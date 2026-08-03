"""Centralized event bus for communications."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.communication import CommunicationEvent
from app.repositories.base import BaseRepository


class CommunicationEventRepository(BaseRepository[CommunicationEvent]):
    def __init__(self) -> None:
        super().__init__(CommunicationEvent)


class EventBusService:
    async def publish(
        self,
        db: AsyncSession,
        event_type: str,
        payload: dict[str, Any],
        *,
        tenant_id: uuid.UUID | None = None,
    ) -> CommunicationEvent:
        event = CommunicationEvent(
            tenant_id=tenant_id,
            event_type=event_type,
            payload=payload,
            status="pending",
            next_retry=datetime.now(timezone.utc),
        )
        repo = CommunicationEventRepository()
        return await repo.create(db, event)

    async def dispatch(
        self,
        db: AsyncSession,
        event: CommunicationEvent,
    ) -> None:
        from app.communications.services.email import email_service
        from app.communications.services.notification import notification_service
        from app.communications.services.preference import preference_service

        handlers = self._handlers(event.event_type)
        event.status = "processing"
        await db.flush()

        for handler in handlers:
            channel = handler["channel"]
            user_id = event.payload.get("user_id")
            tenant_id = event.tenant_id

            if user_id and not await preference_service.is_enabled(
                db, uuid.UUID(user_id), channel, event.payload.get("category", "*")
            ):
                continue

            try:
                if channel == "email":
                    await email_service.send_template(
                        db,
                        to=event.payload["to"],
                        template_name=handler["template"],
                        variables=event.payload.get("variables", {}),
                        tenant_id=tenant_id,
                        locale=event.payload.get("locale", get_settings().default_locale),
                    )
                elif channel == "in_app":
                    await notification_service.create(
                        db,
                        user_id=uuid.UUID(user_id),
                        title=event.payload["title"],
                        category=event.payload.get("category", "general"),
                        body=event.payload.get("body"),
                        priority=event.payload.get("priority", "normal"),
                        deep_link=event.payload.get("deep_link"),
                        organization_id=tenant_id,
                    )
            except Exception as exc:
                event.status = "failed"
                event.retry_count += 1
                event.next_retry = datetime.now(timezone.utc) + timedelta(
                    minutes=2 ** min(event.retry_count, 5)
                )
                await db.flush()
                raise

        event.status = "completed"
        event.processed_at = datetime.now(timezone.utc)
        await db.flush()

    def _handlers(self, event_type: str) -> list[dict[str, Any]]:
        default = [
            {"channel": "in_app", "template": None},
            {"channel": "email", "template": event_type},
        ]
        overrides = {
            "user.registered": [
                {"channel": "in_app", "template": None},
                {"channel": "email", "template": "welcome"},
            ],
            "password.reset": [
                {"channel": "email", "template": "password-reset"},
            ],
            "invitation.created": [
                {"channel": "email", "template": "invitation"},
            ],
            "billing.invoice": [
                {"channel": "email", "template": "billing-invoice"},
                {"channel": "in_app", "template": None},
            ],
            "security.alert": [
                {"channel": "email", "template": "security-alert"},
                {"channel": "in_app", "template": None},
            ],
        }
        return overrides.get(event_type, default)

    async def retry_failed(
        self,
        db: AsyncSession,
    ) -> list[CommunicationEvent]:
        from sqlalchemy import select

        stmt = select(CommunicationEvent).where(
            CommunicationEvent.status == "failed",
            CommunicationEvent.next_retry <= datetime.now(timezone.utc),
            CommunicationEvent.retry_count < 10,
        )
        result = await db.execute(stmt)
        events = result.scalars().all()
        for event in events:
            await self.dispatch(db, event)
        return list(events)


event_bus = EventBusService()
