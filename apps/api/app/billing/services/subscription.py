"""Subscription lifecycle service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.providers.registry import payment_provider_registry
from app.billing.services.customer import customer_service
from app.billing.services.plan import price_repository
from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.billing import Subscription
from app.models.user import User
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self) -> None:
        super().__init__(Subscription)

    async def get_for_customer(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
    ) -> list[Subscription]:
        from sqlalchemy import desc, select

        stmt = (
            select(Subscription)
            .where(Subscription.customer_id == customer_id)
            .order_by(desc(Subscription.created_at))
        )
        result = await db.execute(stmt)
        return result.scalars().all()


subscription_repository = SubscriptionRepository()


class SubscriptionService:
    async def create(
        self,
        db: AsyncSession,
        user: User,
        price_id: uuid.UUID,
        provider_name: str | None = None,
        *,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        customer = await customer_service.get_or_create(db, user, provider_name)
        price = await price_repository.get(db, price_id)
        if not price:
            raise NotFoundError("Price not found")

        provider = payment_provider_registry.get(provider_name or customer.provider)
        session = await provider.create_checkout_session(
            price_id=price.provider_price_id or str(price.id),
            customer_id=customer.provider_customer_id or str(customer.id),
            success_url=success_url,
            cancel_url=cancel_url,
            mode="subscription" if price.billing_interval in {"month", "year"} else "payment",
        )

        subscription = Subscription(
            customer_id=customer.id,
            plan_id=price.plan_id,
            price_id=price.id,
            provider=provider.name,
            status="incomplete",
            provider_subscription_id=session.get("id"),
        )
        await subscription_repository.create(db, subscription)
        return session

    async def list_for_user(
        self,
        db: AsyncSession,
        user: User,
    ) -> list[Subscription]:
        customer = await customer_service.get_for_user(db, user)
        if not customer:
            return []
        return await subscription_repository.get_for_customer(db, customer.id)

    async def cancel(
        self,
        db: AsyncSession,
        user: User,
        subscription_id: uuid.UUID,
    ) -> Subscription:
        subscription = await self._load_owned(db, user, subscription_id)
        subscription.status = "canceled"
        subscription.canceled_at = datetime.now(timezone.utc)
        await db.flush()
        return subscription

    async def change_plan(
        self,
        db: AsyncSession,
        user: User,
        subscription_id: uuid.UUID,
        new_price_id: uuid.UUID,
    ) -> Subscription:
        subscription = await self._load_owned(db, user, subscription_id)
        new_price = await price_repository.get(db, new_price_id)
        if not new_price:
            raise NotFoundError("Price not found")

        subscription.plan_id = new_price.plan_id
        subscription.price_id = new_price.id
        await db.flush()
        return subscription

    async def get_by_provider_id(
        self,
        db: AsyncSession,
        provider_subscription_id: str | None,
    ) -> Subscription | None:
        if not provider_subscription_id:
            return None
        stmt = select(Subscription).where(
            Subscription.provider_subscription_id == provider_subscription_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _load_owned(
        self,
        db: AsyncSession,
        user: User,
        subscription_id: uuid.UUID,
    ) -> Subscription:
        customer = await customer_service.get_for_user(db, user)
        if not customer:
            raise NotFoundError("Customer not found")
        subscription = await subscription_repository.get(db, subscription_id)
        if not subscription or subscription.customer_id != customer.id:
            raise AuthorizationError("Subscription not found")
        return subscription

    async def update_from_provider_event(
        self,
        db: AsyncSession,
        subscription_id: uuid.UUID | str | None,
        status: str,
        metadata: dict,
    ) -> Subscription | None:
        if not subscription_id:
            return None
        if isinstance(subscription_id, str):
            subscription_id = uuid.UUID(subscription_id)
        subscription = await subscription_repository.get(db, subscription_id)
        if not subscription:
            raise NotFoundError("Subscription not found")
        subscription.status = status
        subscription.metadata = {**(subscription.metadata or {}), **metadata}
        if "current_period_start" in metadata:
            subscription.current_period_start = metadata["current_period_start"]
        if "current_period_end" in metadata:
            subscription.current_period_end = metadata["current_period_end"]
        await db.flush()
        return subscription


subscription_service = SubscriptionService()
