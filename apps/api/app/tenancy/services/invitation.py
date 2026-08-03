"""Invitation service."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.organization import Invitation, OrganizationMember, WorkspaceMember
from app.models.user import User
from app.repositories.base import BaseRepository
from app.services.audit_log import audit_log_service
from app.tenancy.services.membership import membership_service


class InvitationRepository(BaseRepository[Invitation]):
    def __init__(self) -> None:
        super().__init__(Invitation)

    async def get_by_token(
        self,
        db: AsyncSession,
        token: str,
    ) -> Invitation | None:
        stmt = select(Invitation).where(Invitation.token == token)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_organization(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
    ) -> list[Invitation]:
        stmt = select(Invitation).where(Invitation.organization_id == org_id)
        result = await db.execute(stmt)
        return result.scalars().all()


invitation_repository = InvitationRepository()


class InvitationService:
    async def invite(
        self,
        db: AsyncSession,
        inviter: User,
        org_id: uuid.UUID,
        *,
        email: str,
        role: str = "member",
        workspace_id: uuid.UUID | None = None,
        expires_days: int = 7,
        auto_approve: bool = True,
    ) -> Invitation:
        if not await membership_service.has_permission(
            db, inviter.id, org_id, "organization.invite"
        ):
            raise ValidationError("Cannot invite to this organization")

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        invite = Invitation(
            organization_id=org_id,
            workspace_id=workspace_id,
            email=email,
            token=token,
            role=role,
            invited_by=inviter.id,
            expires_at=expires_at,
            is_approved=auto_approve,
        )
        invite = await invitation_repository.create(db, invite)

        await audit_log_service.log(
            db,
            "organization.invitation.created",
            "invitation",
            actor_id=str(inviter.id),
            actor_email=inviter.email,
            resource_id=str(invite.id),
            organization_id=org_id,
            details={"email": email, "role": role},
        )
        return invite

    async def resend(
        self,
        db: AsyncSession,
        invite_id: uuid.UUID,
        expires_days: int = 7,
    ) -> Invitation:
        invite = await invitation_repository.get(db, invite_id)
        if not invite:
            raise NotFoundError("Invitation not found")
        if invite.accepted_at or invite.rejected_at:
            raise ConflictError("Invitation already resolved")
        invite.token = secrets.token_urlsafe(32)
        invite.expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
        await db.flush()
        return invite

    async def accept(
        self,
        db: AsyncSession,
        token: str,
        user: User,
    ) -> Invitation:
        invite = await invitation_repository.get_by_token(db, token)
        if not invite:
            raise NotFoundError("Invitation not found")
        if invite.accepted_at or invite.rejected_at:
            raise ConflictError("Invitation already resolved")
        if invite.expires_at < datetime.now(timezone.utc):
            raise ValidationError("Invitation expired")
        if invite.is_approved is False:
            raise ValidationError("Invitation not approved")

        invite.accepted_at = datetime.now(timezone.utc)
        org_member = OrganizationMember(
            organization_id=invite.organization_id,
            user_id=user.id,
            role=invite.role,
            invited_by=invite.invited_by,
        )
        db.add(org_member)

        if invite.workspace_id:
            ws_member = WorkspaceMember(
                workspace_id=invite.workspace_id,
                user_id=user.id,
                role="member",
            )
            db.add(ws_member)

        await db.flush()
        await audit_log_service.log(
            db,
            "organization.invitation.accepted",
            "invitation",
            actor_id=str(user.id),
            actor_email=user.email,
            resource_id=str(invite.id),
            organization_id=invite.organization_id,
            workspace_id=invite.workspace_id,
            details={"email": user.email},
        )
        return invite

    async def reject(
        self,
        db: AsyncSession,
        token: str,
        user: User,
    ) -> Invitation:
        invite = await invitation_repository.get_by_token(db, token)
        if not invite:
            raise NotFoundError("Invitation not found")
        if invite.accepted_at or invite.rejected_at:
            raise ConflictError("Invitation already resolved")
        invite.rejected_at = datetime.now(timezone.utc)
        await db.flush()
        return invite

    async def list_for_organization(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
    ) -> list[Invitation]:
        return await invitation_repository.list_for_organization(db, org_id)


invitation_service = InvitationService()
