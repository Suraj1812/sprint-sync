"""Domain event bus."""

import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.automation import DomainEvent
from app.repositories.base import BaseRepository
from app.services.audit_log import audit_log_service

Handler = Callable[[AsyncSession, DomainEvent], Coroutine[Any, Any, None]]


class DomainEventRepository(BaseRepository[DomainEvent]):
    def __init__(self) -> None:
        super().__init__(DomainEvent)


class DomainEventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = {}
        self._event_repository = DomainEventRepository()

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    async def publish(
        self,
        db: AsyncSession,
        event_type: str,
        payload: dict[str, Any],
        *,
        tenant_id: uuid.UUID | None = None,
        correlation_id: str | None = None,
        source: str | None = None,
    ) -> DomainEvent:
        if not correlation_id:
            correlation_id = uuid.uuid4().hex

        event = DomainEvent(
            tenant_id=tenant_id,
            event_type=event_type,
            payload=payload,
            correlation_id=correlation_id,
            source=source,
            status="pending",
        )
        event = await self._event_repository.create(db, event)

        await audit_log_service.log(
            db,
            "event.published",
            "domain_event",
            organization_id=tenant_id,
            resource_id=str(event.id),
            details={"event_type": event_type, "correlation_id": correlation_id},
        )

        # Dispatch synchronously for now. Could be moved to Celery.
        await self.dispatch(db, event)
        return event

    async def dispatch(
        self,
        db: AsyncSession,
        event: DomainEvent,
    ) -> None:
        handlers = self._subscribers.get(event.event_type, [])
        event.status = "processing"
        event.processed_at = datetime.now(timezone.utc)
        await db.flush()

        for handler in handlers:
            try:
                await handler(db, event)
            except Exception:
                event.status = "failed"
                await db.flush()
                raise

        event.status = "processed"
        await db.flush()

    async def get(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
    ) -> DomainEvent:
        event = await self._event_repository.get(db, event_id)
        if not event:
            raise NotFoundError("Event not found")
        return event

    async def list_recent(
        self,
        db: AsyncSession,
        *,
        status: str | None = None,
        tenant_id: uuid.UUID | None = None,
        limit: int = 100,
    ) -> list[DomainEvent]:
        stmt = select(DomainEvent)
        if status:
            stmt = stmt.where(DomainEvent.status == status)
        if tenant_id:
            stmt = stmt.where(DomainEvent.tenant_id == tenant_id)
        stmt = stmt.order_by(DomainEvent.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


domain_event_bus = DomainEventBus()
