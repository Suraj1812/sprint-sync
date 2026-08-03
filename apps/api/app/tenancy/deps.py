"""Tenant and workspace dependencies."""

import uuid

from fastapi import Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.organization import Organization, OrganizationMember
from app.models.user import User


async def get_current_organization(
    request: Request,
    db: AsyncSession,
    user: User = Depends(get_current_user),
    x_organization_id: uuid.UUID | None = Header(None, alias="X-Organization-Id"),
) -> Organization:
    """Resolve the active organization from header, cookie, or user default."""
    org_id = x_organization_id
    if not org_id:
        cookie = request.cookies.get("organization_id")
        if cookie:
            try:
                org_id = uuid.UUID(cookie)
            except ValueError:
                pass

    if not org_id:
        stmt = (
            select(Organization)
            .join(OrganizationMember)
            .where(
                OrganizationMember.user_id == user.id,
                Organization.is_active.is_(True),
                Organization.suspended_at.is_(None),
                Organization.deleted_at.is_(None),
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        org = result.scalar_one_or_none()
        if not org:
            raise NotFoundError("No active organization for user")
        return org

    stmt = (
        select(Organization)
        .join(OrganizationMember)
        .where(
            Organization.id == org_id,
            OrganizationMember.user_id == user.id,
            Organization.is_active.is_(True),
            Organization.suspended_at.is_(None),
            Organization.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    if not org:
        raise AuthorizationError("Organization not accessible")
    return org


async def get_current_workspace(
    request: Request,
    db: AsyncSession,
    user: User = Depends(get_current_user),
    x_workspace_id: uuid.UUID | None = Header(None, alias="X-Workspace-Id"),
):
    """Resolve and validate the active workspace."""
    from app.models.organization import Workspace, WorkspaceMember

    ws_id = x_workspace_id
    if not ws_id:
        cookie = request.cookies.get("workspace_id")
        if cookie:
            try:
                ws_id = uuid.UUID(cookie)
            except ValueError:
                pass

    if not ws_id:
        raise NotFoundError("Workspace not specified")

    stmt = (
        select(Workspace)
        .join(WorkspaceMember)
        .where(
            Workspace.id == ws_id,
            WorkspaceMember.user_id == user.id,
            Workspace.is_archived.is_(False),
            Workspace.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise AuthorizationError("Workspace not accessible")
    return workspace
