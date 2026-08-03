"""Tenant context utilities."""

import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.organization import Organization

_tenant: ContextVar[uuid.UUID | None] = ContextVar("tenant_id", default=None)


@asynccontextmanager
async def tenant_context(tenant_id: uuid.UUID):
    token = _tenant.set(tenant_id)
    try:
        yield
    finally:
        _tenant.reset(token)


def get_current_tenant() -> uuid.UUID | None:
    return _tenant.get()


async def get_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> Organization:
    from sqlalchemy import select

    stmt = select(Organization).where(
        Organization.id == tenant_id,
        Organization.is_active.is_(True),
        Organization.suspended_at.is_(None),
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    if not org:
        raise NotFoundError("Organization not found or inactive")
    return org


async def require_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> Organization:
    tenant = await get_tenant(db, tenant_id)
    if not tenant:
        raise AuthorizationError("Organization is not active")
    return tenant
