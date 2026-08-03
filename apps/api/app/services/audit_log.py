"""Persisted audit log service for admin and security events."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.audit_log import audit_log_repository


class AuditLogService:
    async def log(
        self,
        db: AsyncSession,
        action: str,
        resource: str,
        *,
        actor_id: str | None = None,
        actor_email: str | None = None,
        resource_id: str | None = None,
        organization_id: uuid.UUID | None = None,
        workspace_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            resource=resource,
            resource_id=resource_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )
        return await audit_log_repository.create(db, log)


audit_log_service = AuditLogService()
