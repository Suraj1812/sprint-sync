"""Feature flag repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature_flag import FeatureFlag
from app.repositories.base import BaseRepository


class FeatureFlagRepository(BaseRepository[FeatureFlag]):
    def __init__(self) -> None:
        super().__init__(FeatureFlag)

    async def get_by_key(
        self,
        db: AsyncSession,
        key: str,
        environment: str = "production",
    ) -> FeatureFlag | None:
        stmt = select(FeatureFlag).where(
            FeatureFlag.key == key,
            FeatureFlag.environment == environment,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def search(
        self,
        db: AsyncSession,
        environment: str | None = None,
        enabled: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FeatureFlag]:
        stmt = select(FeatureFlag)
        if environment:
            stmt = stmt.where(FeatureFlag.environment == environment)
        if enabled is not None:
            stmt = stmt.where(FeatureFlag.enabled.is_(enabled))
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


feature_flag_repository = FeatureFlagRepository()
