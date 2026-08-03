"""Plan and pricing service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.billing import Entitlement, Plan, Price
from app.repositories.base import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    def __init__(self) -> None:
        super().__init__(Plan)

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> Plan | None:
        stmt = select(Plan).where(Plan.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(
        self,
        db: AsyncSession,
    ) -> list[Plan]:
        stmt = select(Plan).where(Plan.is_active.is_(True))
        result = await db.execute(stmt)
        return result.scalars().all()


class PriceRepository(BaseRepository[Price]):
    def __init__(self) -> None:
        super().__init__(Price)

    async def list_for_plan(
        self,
        db: AsyncSession,
        plan_id: uuid.UUID,
    ) -> list[Price]:
        stmt = select(Price).where(
            Price.plan_id == plan_id,
            Price.is_active.is_(True),
        )
        result = await db.execute(stmt)
        return result.scalars().all()


class EntitlementRepository(BaseRepository[Entitlement]):
    def __init__(self) -> None:
        super().__init__(Entitlement)

    async def list_for_plan(
        self,
        db: AsyncSession,
        plan_id: uuid.UUID,
    ) -> list[Entitlement]:
        stmt = select(Entitlement).where(Entitlement.plan_id == plan_id)
        result = await db.execute(stmt)
        return result.scalars().all()


plan_repository = PlanRepository()
price_repository = PriceRepository()
entitlement_repository = EntitlementRepository()


class PlanService:
    async def list(self, db: AsyncSession) -> list[Plan]:
        return await plan_repository.list_active(db)

    async def get(self, db: AsyncSession, plan_id: uuid.UUID) -> Plan:
        stmt = (
            select(Plan)
            .where(Plan.id == plan_id)
            .options(selectinload(Plan.prices))
        )
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()
        if not plan:
            raise NotFoundError("Plan not found")
        return plan

    async def prices(
        self,
        db: AsyncSession,
        plan_id: uuid.UUID,
    ) -> list[Price]:
        return await price_repository.list_for_plan(db, plan_id)

    async def entitlements(
        self,
        db: AsyncSession,
        plan_id: uuid.UUID,
    ) -> list[Entitlement]:
        return await entitlement_repository.list_for_plan(db, plan_id)

    async def get_price(
        self,
        db: AsyncSession,
        price_id: uuid.UUID,
    ) -> Price:
        price = await price_repository.get(db, price_id)
        if not price:
            raise NotFoundError("Price not found")
        return price


plan_service = PlanService()
