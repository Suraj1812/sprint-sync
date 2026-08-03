"""Usage tracking service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import UsageRecord
from app.repositories.base import BaseRepository


class UsageRepository(BaseRepository[UsageRecord]):
    def __init__(self) -> None:
        super().__init__(UsageRecord)

    async def sum_for_customer_metric(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
        metric: str,
        since: datetime,
    ) -> int:
        stmt = select(func.coalesce(func.sum(UsageRecord.quantity), 0)).where(
            UsageRecord.customer_id == customer_id,
            UsageRecord.metric == metric,
            UsageRecord.recorded_at >= since,
        )
        result = await db.execute(stmt)
        return int(result.scalar() or 0)


usage_repository = UsageRepository()


class UsageService:
    async def record(
        self,
        db: AsyncSession,
        *,
        customer_id: uuid.UUID | None,
        subscription_id: uuid.UUID | None,
        metric: str,
        quantity: int,
        recorded_at: datetime | None = None,
        metadata: dict | None = None,
    ) -> UsageRecord:
        record = UsageRecord(
            customer_id=customer_id,
            subscription_id=subscription_id,
            metric=metric,
            quantity=quantity,
            recorded_at=recorded_at or datetime.now(timezone.utc),
            metadata=metadata,
        )
        return await usage_repository.create(db, record)

    async def total(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
        metric: str,
        days: int = 30,
    ) -> int:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        return await usage_repository.sum_for_customer_metric(db, customer_id, metric, since)

    async def record_event(
        self,
        db: AsyncSession,
        metric: str,
        quantity: int = 1,
        customer_id: uuid.UUID | None = None,
    ) -> UsageRecord | None:
        if not customer_id:
            return None
        return await self.record(
            db,
            customer_id=customer_id,
            metric=metric,
            quantity=quantity,
        )


usage_service = UsageService()
