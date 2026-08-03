"""User notification preferences service."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communication import NotificationPreference
from app.repositories.base import BaseRepository


class NotificationPreferenceRepository(BaseRepository[NotificationPreference]):
    def __init__(self) -> None:
        super().__init__(NotificationPreference)

    async def get_for_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[NotificationPreference]:
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()


preference_repository = NotificationPreferenceRepository()


class PreferenceService:
    async def get(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[NotificationPreference]:
        return await preference_repository.get_for_user(db, user_id)

    async def set(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        *,
        channel: str,
        category: str,
        enabled: bool,
        frequency: str | None = None,
        digest: bool = False,
        quiet_hours_start: str | None = None,
        quiet_hours_end: str | None = None,
        language: str = "en",
    ) -> NotificationPreference:
        stmt = (
            select(NotificationPreference)
            .where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.channel == channel,
                NotificationPreference.category == category,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        pref = result.scalar_one_or_none()

        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                channel=channel,
                category=category,
            )
            db.add(pref)

        pref.enabled = enabled
        if frequency:
            pref.frequency = frequency
        pref.digest = digest
        if quiet_hours_start:
            pref.quiet_hours_start = quiet_hours_start
        if quiet_hours_end:
            pref.quiet_hours_end = quiet_hours_end
        pref.language = language
        await db.flush()
        await db.refresh(pref)
        return pref

    async def is_enabled(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        channel: str,
        category: str = "*",
    ) -> bool:
        # A specific preference that disables this channel/category wins.
        disabled = (
            select(NotificationPreference)
            .where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.channel == channel,
                NotificationPreference.category.in_([category, "*"]),
                NotificationPreference.enabled.is_(False),
            )
            .limit(1)
        )
        result = await db.execute(disabled)
        if result.scalar_one_or_none():
            return False
        return True

    async def reset(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> None:
        prefs = await preference_repository.get_for_user(db, user_id)
        for p in prefs:
            await db.delete(p)
        await db.flush()


preference_service = PreferenceService()
