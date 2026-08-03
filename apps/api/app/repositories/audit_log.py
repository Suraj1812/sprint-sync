"""Audit log repository."""

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self) -> None:
        super().__init__(AuditLog)

    async def search(
        self,
        db: AsyncSession,
        *,
        action: str | None = None,
        resource: str | None = None,
        actor_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:
        stmt = select(AuditLog)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        if resource:
            stmt = stmt.where(AuditLog.resource == resource)
        if actor_id:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        stmt = stmt.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


audit_log_repository = AuditLogRepository()
