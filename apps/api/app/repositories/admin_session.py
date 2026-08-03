"""Admin session repository."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_session import AdminSession
from app.repositories.base import BaseRepository


class AdminSessionRepository(BaseRepository[AdminSession]):
    def __init__(self) -> None:
        super().__init__(AdminSession)

    async def get_by_token(
        self,
        db: AsyncSession,
        token: str,
    ) -> AdminSession | None:
        stmt = select(AdminSession).where(AdminSession.token == token)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active_for_user(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> list[AdminSession]:
        stmt = (
            select(AdminSession)
            .where(
                AdminSession.user_id == user_id,
                AdminSession.is_active.is_(True),
                AdminSession.revoked_at.is_(None),
            )
            .order_by(AdminSession.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def is_active(self, session: AdminSession) -> bool:
        now = datetime.now(timezone.utc)
        return (
            session.is_active
            and session.revoked_at is None
            and session.expires_at > now
        )


admin_session_repository = AdminSessionRepository()
