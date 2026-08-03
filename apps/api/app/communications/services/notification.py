"""In-app notification center service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.communication import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self) -> None:
        super().__init__(Notification)

    async def unread_count(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> int:
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
            Notification.archived_at.is_(None),
        )
        result = await db.execute(stmt)
        return int(result.scalar() or 0)


notification_repository = NotificationRepository()


class NotificationService:
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        title: str,
        category: str,
        body: str | None = None,
        priority: str = "normal",
        deep_link: str | None = None,
        organization_id: uuid.UUID | None = None,
        workspace_id: uuid.UUID | None = None,
        metadata: dict | None = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            category=category,
            body=body,
            priority=priority,
            deep_link=deep_link,
            organization_id=organization_id,
            workspace_id=workspace_id,
            metadata=metadata,
        )
        return await notification_repository.create(db, notif)

    async def list_for_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        *,
        unread_only: bool = False,
        category: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Notification]:
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.archived_at.is_(None),
        )
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        if category:
            stmt = stmt.where(Notification.category == category)
        stmt = stmt.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def mark_read(
        self,
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Notification:
        notif = await notification_repository.get(db, notification_id)
        if not notif or notif.user_id != user_id:
            raise NotFoundError("Notification not found")
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await db.flush()
        return notif

    async def mark_all_read(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> int:
        stmt = (
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        result = await db.execute(stmt)
        count = 0
        for n in result.scalars().all():
            n.is_read = True
            n.read_at = datetime.now(timezone.utc)
            count += 1
        if count:
            await db.flush()
        return count

    async def archive(
        self,
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Notification:
        notif = await notification_repository.get(db, notification_id)
        if not notif or notif.user_id != user_id:
            raise NotFoundError("Notification not found")
        notif.archived_at = datetime.now(timezone.utc)
        await db.flush()
        return notif

    async def unread_count(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> int:
        return await notification_repository.unread_count(db, user_id)


notification_service = NotificationService()
