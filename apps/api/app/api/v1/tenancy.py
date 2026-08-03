"""Tenant, organization, workspace, and collaboration API v1."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user, get_db_session
from app.core.exceptions import AuthorizationError
from app.models.audit_log import AuditLog
from app.models.organization import (
    Organization,
    Workspace,
)
from app.models.user import User
from app.schemas.tenancy import (
    AuditLogRead,
    InvitationCreate,
    InvitationRead,
    MemberRead,
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    RoleCreate,
    RoleRead,
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from app.tenancy.deps import get_current_organization, get_current_workspace
from app.tenancy.services.invitation import invitation_service
from app.tenancy.services.membership import membership_service
from app.tenancy.services.organization import (
    custom_role_service,
    organization_service,
)
from app.tenancy.services.workspace import workspace_service

tenancy_router = APIRouter(prefix="/tenancy", tags=["tenancy"])


@tenancy_router.post("/organizations", response_model=OrganizationRead)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    return await organization_service.create(db, user, data.name, branding=data.branding)


@tenancy_router.get("/organizations", response_model=list[OrganizationRead])
async def list_organizations(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    stmt = (
        select(Organization)
        .join(OrganizationMember)
        .where(
            OrganizationMember.user_id == user.id,
            Organization.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@tenancy_router.get("/organizations/{org_id}", response_model=OrganizationRead)
async def get_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if org.id != org_id:
        raise AuthorizationError("Organization not accessible")
    return org


@tenancy_router.patch("/organizations/{org_id}", response_model=OrganizationRead)
async def update_organization(
    org_id: uuid.UUID,
    data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if org.id != org_id:
        raise AuthorizationError("Organization not accessible")
    return await organization_service.update(db, user, org, data.model_dump(exclude_unset=True))


@tenancy_router.post("/organizations/{org_id}/transfer")
async def transfer_ownership(
    org_id: uuid.UUID,
    new_owner_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if org.id != org_id or str(org.owner_id) != str(user.id):
        raise AuthorizationError("Only owner can transfer ownership")
    return await organization_service.transfer_ownership(db, org, new_owner_id)


@tenancy_router.post("/organizations/{org_id}/suspend")
async def suspend_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if org.id != org_id:
        raise AuthorizationError("Organization not accessible")
    if str(org.owner_id) != str(user.id):
        raise AuthorizationError("Only owner can suspend")
    return await organization_service.suspend(db, org)


@tenancy_router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if org.id != org_id:
        raise AuthorizationError("Organization not accessible")
    if str(org.owner_id) != str(user.id):
        raise AuthorizationError("Only owner can delete")
    await organization_service.delete(db, org)
    return {"deleted": True}


@tenancy_router.post("/workspaces", response_model=WorkspaceRead)
async def create_workspace(
    data: WorkspaceCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    return await workspace_service.create(
        db,
        user,
        org.id,
        data.name,
        description=data.description,
        branding=data.branding,
    )


@tenancy_router.get("/workspaces", response_model=list[WorkspaceRead])
async def list_workspaces(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> list[Any]:
    return await workspace_service.list_for_organization(db, user, org.id)


@tenancy_router.get("/workspaces/{ws_id}", response_model=WorkspaceRead)
async def get_workspace(
    ws_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    ws: Workspace = Depends(get_current_workspace),
) -> Any:
    if ws.id != ws_id or ws.organization_id != org.id:
        raise AuthorizationError("Workspace not accessible")
    return ws


@tenancy_router.patch("/workspaces/{ws_id}", response_model=WorkspaceRead)
async def update_workspace(
    ws_id: uuid.UUID,
    data: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    ws: Workspace = Depends(get_current_workspace),
) -> Any:
    if ws.id != ws_id:
        raise AuthorizationError("Workspace not accessible")
    return await workspace_service.update(db, user, ws, data.model_dump(exclude_unset=True))


@tenancy_router.post("/workspaces/{ws_id}/archive")
async def archive_workspace(
    ws_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    ws: Workspace = Depends(get_current_workspace),
) -> Any:
    if ws.id != ws_id:
        raise AuthorizationError("Workspace not accessible")
    return await workspace_service.archive(db, ws)


@tenancy_router.post("/workspaces/{ws_id}/restore")
async def restore_workspace(
    ws_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    ws: Workspace = Depends(get_current_workspace),
) -> Any:
    if ws.id != ws_id:
        raise AuthorizationError("Workspace not accessible")
    return await workspace_service.restore(db, ws)


@tenancy_router.get("/members", response_model=list[MemberRead])
async def list_members(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> list[Any]:
    members = await membership_service.list_members(db, org.id)
    return members


@tenancy_router.post("/members/{user_id}/suspend")
async def suspend_member(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if not await membership_service.has_permission(db, user.id, org.id, "organization.member.manage"):
        raise AuthorizationError("Cannot manage members")
    return await membership_service.suspend(db, org.id, user_id)


@tenancy_router.post("/members/{user_id}/reactivate")
async def reactivate_member(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if not await membership_service.has_permission(db, user.id, org.id, "organization.member.manage"):
        raise AuthorizationError("Cannot manage members")
    return await membership_service.reactivate(db, org.id, user_id)


@tenancy_router.delete("/members/{user_id}")
async def remove_member(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if not await membership_service.has_permission(db, user.id, org.id, "organization.member.manage"):
        raise AuthorizationError("Cannot manage members")
    await membership_service.remove(db, user, org.id, user_id)
    return {"removed": True}


@tenancy_router.post("/invitations", response_model=InvitationRead)
async def create_invitation(
    data: InvitationCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    return await invitation_service.invite(
        db,
        user,
        org.id,
        email=str(data.email),
        role=data.role,
        workspace_id=data.workspace_id,
        expires_days=data.expires_days,
    )


@tenancy_router.get("/invitations", response_model=list[InvitationRead])
async def list_invitations(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> list[Any]:
    return await invitation_service.list_for_organization(db, org.id)


@tenancy_router.post("/invitations/{token}/accept")
async def accept_invitation(
    token: str,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    return await invitation_service.accept(db, token, user)


@tenancy_router.post("/invitations/{token}/reject")
async def reject_invitation(
    token: str,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    return await invitation_service.reject(db, token, user)


@tenancy_router.post("/roles", response_model=RoleRead)
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> Any:
    if not await membership_service.has_permission(db, user.id, org.id, "organization.member.manage"):
        raise AuthorizationError("Cannot manage roles")
    return await custom_role_service.create(db, org.id, data.name, data.permissions, description=data.description)


@tenancy_router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
) -> list[Any]:
    return await custom_role_service.list_for_organization(db, org.id)


@tenancy_router.get("/audit-logs", response_model=list[AuditLogRead])
async def list_audit_logs(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    ws_id: uuid.UUID | None = Header(None, alias="X-Workspace-Id"),
) -> list[Any]:
    if not await membership_service.has_permission(db, user.id, org.id, "audit.view"):
        raise AuthorizationError("Cannot view audit logs")

    stmt = select(AuditLog).where(AuditLog.organization_id == org.id)
    if ws_id:
        stmt = stmt.where(AuditLog.workspace_id == ws_id)
    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(100)
    result = await db.execute(stmt)
    return result.scalars().all()


@tenancy_router.get("/admin/organizations", response_model=list[OrganizationRead])
async def admin_list_organizations(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    stmt = select(Organization).where(Organization.deleted_at.is_(None))
    result = await db.execute(stmt)
    return result.scalars().all()


@tenancy_router.get("/admin/workspaces", response_model=list[WorkspaceRead])
async def admin_list_workspaces(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    stmt = select(Workspace).where(Workspace.deleted_at.is_(None))
    result = await db.execute(stmt)
    return result.scalars().all()


@tenancy_router.get("/admin/invitations", response_model=list[InvitationRead])
async def admin_list_invitations(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    stmt = select(Invitation).limit(100)
    result = await db.execute(stmt)
    return result.scalars().all()


@tenancy_router.post("/admin/organizations/{org_id}/suspend")
async def admin_suspend_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> Any:
    org = await organization_service.get(db, org_id)
    return await organization_service.suspend(db, org)
