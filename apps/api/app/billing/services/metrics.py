"""Billing analytics and reporting."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import Invoice, Payment, Subscription


class MetricsService:
    async def mrr(self, db: AsyncSession) -> Decimal:
        stmt = select(func.coalesce(func.sum(Invoice.total), Decimal("0.00"))).where(
            Invoice.status.in_(["paid", "open"]),
            Invoice.created_at >= datetime.now(timezone.utc) - timedelta(days=30),
        )
        result = await db.execute(stmt)
        return Decimal(result.scalar() or 0)

    async def arr(self, db: AsyncSession) -> Decimal:
        return await self.mrr(db) * 12

    async def active_subscriptions(self, db: AsyncSession) -> int:
        stmt = select(func.count(Subscription.id)).where(
            Subscription.status.in_(["active", "trialing"]),
        )
        result = await db.execute(stmt)
        return int(result.scalar() or 0)

    async def failed_payments_30d(self, db: AsyncSession) -> int:
        stmt = select(func.count(Payment.id)).where(
            Payment.status == "failed",
            Payment.created_at >= datetime.now(timezone.utc) - timedelta(days=30),
        )
        result = await db.execute(stmt)
        return int(result.scalar() or 0)

    async def dashboard(self, db: AsyncSession) -> dict:
        return {
            "mrr": float(await self.mrr(db)),
            "arr": float(await self.arr(db)),
            "active_subscriptions": await self.active_subscriptions(db),
            "failed_payments_30d": await self.failed_payments_30d(db),
        }


metrics_service = MetricsService()
