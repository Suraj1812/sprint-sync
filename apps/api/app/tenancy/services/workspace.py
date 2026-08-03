"""Workspace lifecycle and switching service."""

import re
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.models.organization import Workspace, WorkspaceMember
from app.models.user import User
from app.repositories.base import BaseRepository
from app.services.audit_log import audit_log_service
from app.tenancy.services.membership import membership_service


def _make_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self) -> None:
        super().__init__(Workspace)

    async def get_by_slug(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        slug: str,
    ) -> Workspace | None:
        stmt = (
            select(Workspace)
            .where(
                Workspace.organization_id == organization_id,
                Workspace.slug == slug,
                Workspace.deleted_at.is_(None),
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


workspace_repository = WorkspaceRepository()


class WorkspaceService:
    async def create(
        self,
        db: AsyncSession,
        user: User,
        org_id: uuid.UUID,
        name: str,
        *,
        description: str | None = None,
        branding: dict | None = None,
    ) -> Workspace:
        slug = _make_slug(name)
        existing = await workspace_repository.get_by_slug(db, org_id, slug)
        if existing:
            raise ConflictError("Workspace slug already exists in organization")

        if not await membership_service.has_permission(
            db, user.id, org_id, "workspace.create"
        ):
            raise AuthorizationError("Cannot create workspace")

        ws = Workspace(
            organization_id=org_id,
            name=name,
            slug=slug,
            description=description,
            branding=branding,
        )
        ws = await workspace_repository.create(db, ws)

        member = WorkspaceMember(
            workspace_id=ws.id,
            user_id=user.id,
            role="admin",
        )
        db.add(member)
        await db.flush()

        await audit_log_service.log(
            db,
            "workspace.created",
            "workspace",
            actor_id=str(user.id),
            actor_email=user.email,
            resource_id=str(ws.id),
            organization_id=org_id,
            workspace_id=ws.id,
            details={"name": name},
        )
        return ws

    async def list_for_organization(
        self,
        db: AsyncSession,
        user: User,
        org_id: uuid.UUID,
    ) -> list[Workspace]:
        stmt = (
            select(Workspace)
            .join(WorkspaceMember)
            .where(
                Workspace.organization_id == org_id,
                WorkspaceMember.user_id == user.id,
                Workspace.is_archived.is_(False),
                Workspace.deleted_at.is_(None),
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get(
        self,
        db: AsyncSession,
        ws_id: uuid.UUID,
    ) -> Workspace:
        ws = await workspace_repository.get(db, ws_id)
        if not ws or ws.deleted_at:
            raise NotFoundError("Workspace not found")
        return ws

    async def update(
        self,
        db: AsyncSession,
        user: User,
        ws: Workspace,
        data: dict[str, Any],
    ) -> Workspace:
        if not await membership_service.has_workspace_permission(
            db, user.id, ws.id, "workspace.update"
        ):
            raise AuthorizationError("Cannot update workspace")

        if "name" in data:
            ws.name = data["name"]
            ws.slug = _make_slug(data["name"])
        if "description" in data:
            ws.description = data["description"]
        if "branding" in data:
            ws.branding = data["branding"]

        await db.flush()
        await audit_log_service.log(
            db,
            "workspace.updated",
            "workspace",
            actor_id=str(user.id),
            actor_email=user.email,
            resource_id=str(ws.id),
            organization_id=ws.organization_id,
            workspace_id=ws.id,
            details=data,
        )
        return ws

    async def archive(
        self,
        db: AsyncSession,
        ws: Workspace,
    ) -> Workspace:
        ws.is_archived = True
        ws.archived_at = datetime.now(timezone.utc)
        await db.flush()
        return ws

    async def restore(
        self,
        db: AsyncSession,
        ws: Workspace,
    ) -> Workspace:
        ws.is_archived = False
        ws.archived_at = None
        await db.flush()
        return ws

    async def delete(
        self,
        db: AsyncSession,
        ws: Workspace,
    ) -> Workspace:
        ws.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return ws


workspace_service = WorkspaceService()
