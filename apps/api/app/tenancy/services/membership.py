"""Organization and workspace membership service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.organization import (
    CustomRole,
    OrganizationMember,
    Workspace,
    WorkspaceMember,
)
from app.models.user import User
from app.repositories.base import BaseRepository
from app.services.audit_log import audit_log_service


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    def __init__(self) -> None:
        super().__init__(OrganizationMember)

    async def get(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> OrganizationMember | None:
        stmt = (
            select(OrganizationMember)
            .where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    def __init__(self) -> None:
        super().__init__(WorkspaceMember)

    async def get(
        self,
        db: AsyncSession,
        ws_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WorkspaceMember | None:
        stmt = (
            select(WorkspaceMember)
            .where(
                WorkspaceMember.workspace_id == ws_id,
                WorkspaceMember.user_id == user_id,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


org_member_repository = OrganizationMemberRepository()
ws_member_repository = WorkspaceMemberRepository()

# Ordered permission hierarchy.
ORG_PERMISSIONS = {
    "owner": {"*"},
    "admin": {
        "organization.update",
        "organization.invite",
        "organization.member.manage",
        "workspace.create",
        "workspace.update",
        "workspace.delete",
        "workspace.archive",
        "billing.view",
        "audit.view",
    },
    "member": {
        "workspace.view",
        "workspace.create",
    },
    "guest": {"workspace.view"},
    "auditor": {"audit.view", "billing.view"},
}

WS_PERMISSIONS = {
    "admin": {"*"},
    "manager": {
        "workspace.update",
        "workspace.invite",
        "workspace.member.manage",
    },
    "member": {"workspace.view"},
    "guest": {"workspace.view"},
}


class MembershipService:
    async def is_member(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        m = await org_member_repository.get(db, org_id, user_id)
        return m is not None and not m.is_suspended

    async def get_member(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> OrganizationMember:
        m = await org_member_repository.get(db, org_id, user_id)
        if not m or m.is_suspended:
            raise NotFoundError("Member not found")
        return m

    async def has_permission(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        permission: str,
    ) -> bool:
        member = await org_member_repository.get(db, org_id, user_id)
        if not member or member.is_suspended:
            return False

        # Custom roles override default
        if not ORG_PERMISSIONS.get(member.role):
            custom = await self._custom_role(db, org_id, member.role)
            if custom:
                return permission in custom.permissions or "*" in custom.permissions
            return False

        return self._has_permission(ORG_PERMISSIONS, member.role, permission)

    async def has_workspace_permission(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        ws_id: uuid.UUID,
        permission: str,
    ) -> bool:
        ws_member = await ws_member_repository.get(db, ws_id, user_id)
        if ws_member:
            return self._has_permission(WS_PERMISSIONS, ws_member.role, permission)

        # Check organization role fallback
        stmt = select(Workspace).where(Workspace.id == ws_id)
        result = await db.execute(stmt)
        ws = result.scalar_one_or_none()
        if not ws:
            return False
        return await self.has_permission(db, user_id, ws.organization_id, permission)

    def _has_permission(
        self,
        matrix: dict[str, set[str]],
        role: str,
        permission: str,
    ) -> bool:
        perms = matrix.get(role, set())
        return "*" in perms or permission in perms

    async def _custom_role(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        role_name: str,
    ) -> CustomRole | None:
        stmt = (
            select(CustomRole)
            .where(
                CustomRole.organization_id == org_id,
                CustomRole.name == role_name,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_members(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
    ) -> list[OrganizationMember]:
        stmt = (
            select(OrganizationMember)
            .where(
                OrganizationMember.organization_id == org_id,
            )
            .order_by(OrganizationMember.created_at)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def set_role(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
    ) -> OrganizationMember:
        member = await org_member_repository.get(db, org_id, user_id)
        if not member:
            raise NotFoundError("Member not found")
        member.role = role
        await db.flush()
        return member

    async def suspend(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> OrganizationMember:
        member = await self.get_member(db, org_id, user_id)
        member.is_suspended = True
        await db.flush()
        return member

    async def reactivate(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> OrganizationMember:
        member = await org_member_repository.get(db, org_id, user_id)
        if not member:
            raise NotFoundError("Member not found")
        member.is_suspended = False
        await db.flush()
        return member

    async def remove(
        self,
        db: AsyncSession,
        actor: User,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        member = await org_member_repository.get(db, org_id, user_id)
        if not member:
            raise NotFoundError("Member not found")

        await db.delete(member)
        await audit_log_service.log(
            db,
            "organization.member.removed",
            "organization_member",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(user_id),
            organization_id=org_id,
            details={"removed_user_id": str(user_id)},
        )


membership_service = MembershipService()
