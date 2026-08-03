"""Entitlement and access control service."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import Entitlement, Plan, Subscription, UsageRecord
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self) -> None:
        super().__init__(Subscription)

    async def get_active_for_customer(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
    ) -> Subscription | None:
        stmt = (
            select(Subscription)
            .where(
                Subscription.customer_id == customer_id,
                Subscription.status.in_(["active", "trialing"]),
            )
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


subscription_repository = SubscriptionRepository()


class EntitlementService:
    async def _entitlements_for_plan(
        self,
        db: AsyncSession,
        plan_id: uuid.UUID | None,
    ) -> list[Entitlement]:
        if not plan_id:
            return []
        stmt = select(Entitlement).where(Entitlement.plan_id == plan_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def for_customer(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
    ) -> list[Entitlement]:
        sub = await subscription_repository.get_active_for_customer(db, customer_id)
        if sub:
            return await self._entitlements_for_plan(db, sub.plan_id)

        free = await db.execute(select(Plan).where(Plan.name == "free"))
        plan = free.scalar_one_or_none()
        return await self._entitlements_for_plan(db, plan.id if plan else None)

    async def has_feature(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
        feature: str,
    ) -> bool:
        entitlements = await self.for_customer(db, customer_id)
        return any(e.feature == feature for e in entitlements)

    async def limit_for(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
        feature: str,
    ) -> int | None:
        entitlements = await self.for_customer(db, customer_id)
        for e in entitlements:
            if e.feature == feature:
                return e.limit
        return None

    async def usage_for(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
        metric: str,
        days: int = 30,
    ) -> int:
        from datetime import datetime, timedelta, timezone

        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(func.coalesce(func.sum(UsageRecord.quantity), 0)).where(
            UsageRecord.customer_id == customer_id,
            UsageRecord.metric == metric,
            UsageRecord.recorded_at >= since,
        )
        result = await db.execute(stmt)
        return int(result.scalar() or 0)

    async def can_use(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
        feature: str,
        metric: str,
        quantity: int = 1,
    ) -> bool:
        limit = await self.limit_for(db, customer_id, feature)
        if limit is None:
            return True
        used = await self.usage_for(db, customer_id, metric)
        return used + quantity <= limit

    async def for_user(
        self,
        db: AsyncSession,
        user: object,
    ) -> list[Entitlement]:
        from app.billing.services.customer import customer_repository

        customer = await customer_repository.get_by_user(db, user.id)
        if customer:
            return await self.for_customer(db, customer.id)

        free = await db.execute(select(Plan).where(Plan.name == "free"))
        plan = free.scalar_one_or_none()
        return await self._entitlements_for_plan(db, plan.id if plan else None)


entitlement_service = EntitlementService()
