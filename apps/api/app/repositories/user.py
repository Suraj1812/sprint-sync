"""User repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        stmt = (
            select(User)
            .offset(skip)
            .limit(limit)
            .options(selectinload(User.role))
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get(self, db: AsyncSession, obj_id: UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == obj_id)
            .options(selectinload(User.role))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
        include_deleted: bool = False,
    ) -> User | None:
        stmt = select(User).where(User.email == email)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_email(self, db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(
            User.email == email,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


user_repository = UserRepository()
