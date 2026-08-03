"""User service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.user import user_repository
from app.schemas.user import UserRead, UserUpdate


class UserService:
    async def get_user(self, db: AsyncSession, user_id: UUID) -> UserRead:
        user = await user_repository.get(db, user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserRead(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            email_verified=user.email_verified,
            role=user.role.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def list_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UserRead]:
        users = await user_repository.get_all(db, skip=skip, limit=limit)
        return [
            UserRead(
                id=u.id,
                email=u.email,
                first_name=u.first_name,
                last_name=u.last_name,
                is_active=u.is_active,
                email_verified=u.email_verified,
                role=u.role.name,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ]

    async def update_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: UserUpdate,
    ) -> UserRead:
        user = await user_repository.get(db, user_id)
        if not user:
            raise NotFoundError("User not found")

        update = data.model_dump(exclude_unset=True)
        await user_repository.update(db, user, update)
        return await self.get_user(db, user_id)


user_service = UserService()
