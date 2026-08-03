"""Organization and tenant lifecycle service."""

import re
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.models.organization import CustomDomain, CustomRole, Organization, OrganizationMember
from app.models.user import User
from app.repositories.base import BaseRepository
from app.services.audit_log import audit_log_service


def _make_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self) -> None:
        super().__init__(Organization)

    async def get_by_slug(
        self,
        db: AsyncSession,
        slug: str,
    ) -> Organization | None:
        stmt = (
            select(Organization)
            .where(Organization.slug == slug, Organization.deleted_at.is_(None))
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


organization_repository = OrganizationRepository()


class OrganizationService:
    async def create(
        self,
        db: AsyncSession,
        user: User,
        name: str,
        *,
        branding: dict | None = None,
    ) -> Organization:
        slug = _make_slug(name)
        existing = await organization_repository.get_by_slug(db, slug)
        if existing:
            raise ConflictError("Organization slug already exists")

        org = Organization(
            name=name,
            slug=slug,
            owner_id=user.id,
            branding=branding,
            billing_email=user.email,
        )
        org = await organization_repository.create(db, org)

        member = OrganizationMember(
            organization_id=org.id,
            user_id=user.id,
            role="owner",
            invited_by=None,
        )
        db.add(member)
        await db.flush()

        await audit_log_service.log(
            db,
            "organization.created",
            "organization",
            actor_id=str(user.id),
            actor_email=user.email,
            resource_id=str(org.id),
            organization_id=org.id,
            details={"name": name},
        )
        return org

    async def get(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
    ) -> Organization:
        org = await organization_repository.get(db, org_id)
        if not org or org.deleted_at:
            raise NotFoundError("Organization not found")
        return org

    async def update(
        self,
        db: AsyncSession,
        user: User,
        org: Organization,
        data: dict[str, Any],
    ) -> Organization:
        if str(org.owner_id) != str(user.id):
            raise AuthorizationError("Only owner can update organization")

        if "name" in data:
            org.name = data["name"]
            org.slug = _make_slug(data["name"])
        if "branding" in data:
            org.branding = data["branding"]
        if "billing_email" in data:
            org.billing_email = data["billing_email"]

        await db.flush()
        await audit_log_service.log(
            db,
            "organization.updated",
            "organization",
            actor_id=str(user.id),
            actor_email=user.email,
            resource_id=str(org.id),
            organization_id=org.id,
            details=data,
        )
        return org

    async def transfer_ownership(
        self,
        db: AsyncSession,
        org: Organization,
        new_owner_id: uuid.UUID,
    ) -> Organization:
        from app.tenancy.services.membership import membership_service

        if not await membership_service.is_member(db, org.id, new_owner_id):
            raise AuthorizationError("New owner is not a member")

        old_owner = org.owner_id
        org.owner_id = new_owner_id
        await db.flush()

        await membership_service.set_role(db, org.id, old_owner, "admin")
        await membership_service.set_role(db, org.id, new_owner_id, "owner")
        return org

    async def suspend(
        self,
        db: AsyncSession,
        org: Organization,
    ) -> Organization:
        org.suspended_at = datetime.now(timezone.utc)
        org.is_active = False
        await db.flush()
        return org

    async def restore(
        self,
        db: AsyncSession,
        org: Organization,
    ) -> Organization:
        org.suspended_at = None
        org.is_active = True
        await db.flush()
        return org

    async def delete(
        self,
        db: AsyncSession,
        org: Organization,
    ) -> Organization:
        org.deleted_at = datetime.now(timezone.utc)
        org.is_active = False
        await db.flush()
        return org


class CustomDomainService:
    async def create(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        domain: str,
    ) -> CustomDomain:
        token = uuid.uuid4().hex[:16]
        domain_obj = CustomDomain(
            organization_id=org_id,
            domain=domain,
            verification_token=token,
        )
        repo = BaseRepository(CustomDomain)
        return await repo.create(db, domain_obj)


class CustomRoleRepository(BaseRepository[CustomRole]):
    def __init__(self) -> None:
        super().__init__(CustomRole)


class CustomRoleService:
    async def create(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        name: str,
        permissions: list[str],
        *,
        description: str | None = None,
    ) -> CustomRole:
        role = CustomRole(
            organization_id=org_id,
            name=name,
            description=description,
            permissions=permissions,
        )
        return await CustomRoleRepository().create(db, role)

    async def list_for_organization(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
    ) -> list[CustomRole]:
        stmt = select(CustomRole).where(CustomRole.organization_id == org_id)
        result = await db.execute(stmt)
        return result.scalars().all()


organization_service = OrganizationService()
custom_domain_service = CustomDomainService()
custom_role_service = CustomRoleService()
