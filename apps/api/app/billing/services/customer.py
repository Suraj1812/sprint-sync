"""Customer billing service."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.providers.registry import payment_provider_registry
from app.core.exceptions import NotFoundError
from app.models.billing import Customer
from app.models.user import User
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self) -> None:
        super().__init__(Customer)

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> Customer | None:
        stmt = select(Customer).where(Customer.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> Customer | None:
        stmt = select(Customer).where(Customer.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


customer_repository = CustomerRepository()


class CustomerService:
    async def get_or_create(
        self,
        db: AsyncSession,
        user: User,
        provider_name: str | None = None,
    ) -> Customer:
        customer = await customer_repository.get_by_user(db, user.id)
        if customer:
            return customer

        provider = payment_provider_registry.get(provider_name or "stripe")
        remote = await provider.create_customer(user.email)

        customer = Customer(
            user_id=user.id,
            provider=provider.name,
            provider_customer_id=remote.get("id"),
            email=user.email,
            payment_provider=provider.name,
        )
        customer = await customer_repository.create(db, customer)
        return customer

    async def get_for_user(
        self,
        db: AsyncSession,
        user: User,
    ) -> Customer | None:
        return await customer_repository.get_by_user(db, user.id)

    async def get(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
    ) -> Customer:
        customer = await customer_repository.get(db, customer_id)
        if not customer:
            raise NotFoundError("Customer not found")
        return customer


customer_service = CustomerService()
