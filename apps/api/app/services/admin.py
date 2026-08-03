"""Admin platform services."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import audit
from app.core.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from app.core.security import create_admin_token, decode_token, hash_password
from app.models.admin_session import AdminSession
from app.models.feature_flag import FeatureFlag
from app.models.organization import Organization
from app.models.user import User
from app.repositories.admin_session import admin_session_repository
from app.repositories.feature_flag import feature_flag_repository
from app.repositories.organization import organization_repository
from app.repositories.role import role_repository
from app.services.audit_log import AuditLogService
from app.repositories.user import user_repository
from app.schemas.admin import (
    AdminAuthResponse,
    DashboardStats,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    OrganizationCreate,
    OrganizationUpdate,
    UserStatusUpdate,
)
from app.schemas.auth import UserLogin
from app.services.audit_log import audit_log_service
from app.services.auth import auth_service

ADMIN_ROLES = {
    "super_admin",
    "platform_admin",
    "support",
    "operations",
    "billing",
    "auditor",
}


def _is_admin_role(role_name: str) -> bool:
    return role_name in ADMIN_ROLES


def _has_permission(role_permissions: list[str], permission: str) -> bool:
    if "*" in role_permissions:
        return True
    return permission in role_permissions


def _hash_admin_token() -> str:
    return secrets.token_urlsafe(64)


class AdminAuthService:
    async def login(
        self,
        db: AsyncSession,
        data: UserLogin,
        request: Request | None = None,
    ) -> tuple[User, AdminAuthResponse]:
        user, _ = await auth_service.login(db, data)

        if not _is_admin_role(user.role.name):
            audit(
                "admin_login_denied",
                user_id=str(user.id),
                email=user.email,
                success=False,
                reason="non_admin_role",
            )
            raise AuthorizationError("Admin access required")

        session_id = uuid.uuid4()
        token = _hash_admin_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=8)

        admin_session = AdminSession(
            id=session_id,
            user_id=user.id,
            token=token,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
            expires_at=expires_at,
        )
        await admin_session_repository.create(db, admin_session)

        await audit_log_service.log(
            db,
            action="admin_login",
            resource="admin_session",
            actor_id=str(user.id),
            actor_email=user.email,
            resource_id=str(admin_session.id),
            ip_address=admin_session.ip_address,
            user_agent=admin_session.user_agent,
            details={"role": user.role.name},
        )

        access = create_admin_token(user.id, session_id, user.role.name)
        return user, AdminAuthResponse(
            access_token=access,
            token_type="bearer",
            expires_in=8 * 60 * 60,
        )

    async def logout(self, db: AsyncSession, token: str) -> None:
        payload = decode_token(token, "admin")
        session_id = payload.get("session")
        if not session_id:
            raise AuthenticationError("Invalid admin token")
        session = await admin_session_repository.get(db, uuid.UUID(session_id))
        if session:
            session.revoked_at = datetime.now(timezone.utc)
            session.is_active = False
            await db.flush()
            await audit_log_service.log(
                db,
                action="admin_logout",
                resource="admin_session",
                actor_id=str(session.user_id),
                resource_id=str(session.id),
            )

    async def get_current(
        self,
        db: AsyncSession,
        token: str,
    ) -> User:
        payload = decode_token(token, "admin")
        user_id = payload.get("sub")
        session_id = payload.get("session")
        if not user_id or not session_id:
            raise AuthenticationError("Invalid admin token")

        session = await admin_session_repository.get(db, uuid.UUID(session_id))
        if not session or not await admin_session_repository.is_active(session):
            raise AuthenticationError("Admin session expired or revoked")

        user = await user_repository.get(db, uuid.UUID(user_id))
        if not user or not user.is_active or user.deleted_at is not None:
            raise AuthenticationError("User not found or inactive")

        return user

    async def list_sessions(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[AdminSession]:
        return await admin_session_repository.list_active_for_user(
            db, str(user_id)
        )

    async def revoke_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        actor: User,
    ) -> None:
        session = await admin_session_repository.get(db, session_id)
        if not session:
            raise NotFoundError("Session not found")
        session.revoked_at = datetime.now(timezone.utc)
        session.is_active = False
        await db.flush()
        await audit_log_service.log(
            db,
            action="admin_session_revoke",
            resource="admin_session",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(session.id),
        )


class AdminUserService:
    async def list_users(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        q: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        where = [User.deleted_at.is_(None)]
        if q:
            where.append(
                or_(
                    User.email.ilike(f"%{q}%"),
                    User.first_name.ilike(f"%{q}%"),
                    User.last_name.ilike(f"%{q}%"),
                )
            )
        if role:
            where.append(User.role.has(name=role))
        if is_active is not None:
            where.append(User.is_active.is_(is_active))

        count_stmt = select(func.count(User.id)).where(and_(*where))
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(User)
            .where(and_(*where))
            .options(selectinload(User.role))
            .order_by(desc(User.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all(), total

    async def update_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        data: UserStatusUpdate,
        actor: User,
    ) -> User:
        user = await user_repository.get(db, user_id)
        if not user:
            raise NotFoundError("User not found")

        update = data.model_dump(exclude_unset=True)
        if "role" in update:
            role = await role_repository.get_by_name(db, update["role"])
            if not role:
                raise NotFoundError("Role not found")
            user.role_id = role.id
            del update["role"]

        for key, value in update.items():
            setattr(user, key, value)

        await db.flush()
        await db.refresh(user)

        await audit_log_service.log(
            db,
            action="admin_user_update",
            resource="user",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(user.id),
            details=update,
        )
        return user

    async def reset_password(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        actor: User,
    ) -> str:
        user = await user_repository.get(db, user_id)
        if not user:
            raise NotFoundError("User not found")

        temp_password = secrets.token_urlsafe(12)
        user.hashed_password = hash_password(temp_password)
        await db.flush()

        await audit_log_service.log(
            db,
            action="admin_password_reset",
            resource="user",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(user.id),
        )
        return temp_password


class AdminDashboardService:
    async def stats(self, db: AsyncSession) -> DashboardStats:
        total_users = (
            await db.execute(select(func.count(User.id)).where(User.deleted_at.is_(None)))
        ).scalar() or 0

        active_users = (
            await db.execute(
                select(func.count(User.id)).where(
                    User.is_active.is_(True), User.deleted_at.is_(None)
                )
            )
        ).scalar() or 0

        since = datetime.now(timezone.utc) - timedelta(hours=24)
        new_registrations_24h = (
            await db.execute(
                select(func.count(User.id)).where(User.created_at >= since)
            )
        ).scalar() or 0

        failed_logins_24h = (
            await db.execute(
                select(func.count(AuditLog.id)).where(
                    AuditLog.action == "login_attempt",
                    AuditLog.details.contains({"success": False}),
                    AuditLog.created_at >= since,
                )
            )
        ).scalar() or 0

        admin_sessions = (
            await db.execute(
                select(func.count(AdminSession.id)).where(
                    AdminSession.is_active.is_(True),
                    AdminSession.revoked_at.is_(None),
                    AdminSession.expires_at > datetime.now(timezone.utc),
                )
            )
        ).scalar() or 0

        pending_feature_flags = (
            await db.execute(
                select(func.count(FeatureFlag.id)).where(FeatureFlag.enabled.is_(False))
            )
        ).scalar() or 0

        return DashboardStats(
            total_users=total_users,
            active_users=active_users,
            new_registrations_24h=new_registrations_24h,
            failed_logins_24h=failed_logins_24h,
            admin_sessions=admin_sessions,
            pending_feature_flags=pending_feature_flags,
            uptime="100%",
            version="0.1.0",
        )


class FeatureFlagService:
    async def list(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FeatureFlag]:
        return await feature_flag_repository.get_all(db, skip=skip, limit=limit)

    async def create(
        self,
        db: AsyncSession,
        data: FeatureFlagCreate,
        actor: User,
    ) -> FeatureFlag:
        existing = await feature_flag_repository.get_by_key(
            db, data.key, data.environment
        )
        if existing:
            raise AuthorizationError("Feature flag already exists")

        flag = FeatureFlag(**data.model_dump())
        flag = await feature_flag_repository.create(db, flag)

        await audit_log_service.log(
            db,
            action="feature_flag_create",
            resource="feature_flag",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(flag.id),
            details={"key": flag.key},
        )
        return flag

    async def update(
        self,
        db: AsyncSession,
        flag_id: uuid.UUID,
        data: FeatureFlagUpdate,
        actor: User,
    ) -> FeatureFlag:
        flag = await feature_flag_repository.get(db, flag_id)
        if not flag:
            raise NotFoundError("Feature flag not found")

        update = data.model_dump(exclude_unset=True)
        for key, value in update.items():
            setattr(flag, key, value)
        await db.flush()
        await db.refresh(flag)

        await audit_log_service.log(
            db,
            action="feature_flag_update",
            resource="feature_flag",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(flag.id),
            details=update,
        )
        return flag

    async def delete(
        self,
        db: AsyncSession,
        flag_id: uuid.UUID,
        actor: User,
    ) -> None:
        flag = await feature_flag_repository.get(db, flag_id)
        if not flag:
            raise NotFoundError("Feature flag not found")

        await feature_flag_repository.delete(db, flag)
        await audit_log_service.log(
            db,
            action="feature_flag_delete",
            resource="feature_flag",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(flag.id),
        )


class OrganizationService:
    async def list(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Organization]:
        return await organization_repository.search(db, skip=skip, limit=limit)

    async def create(
        self,
        db: AsyncSession,
        data: OrganizationCreate,
        actor: User,
    ) -> Organization:
        existing = await organization_repository.get_by_slug(db, data.slug)
        if existing:
            raise AuthorizationError("Organization slug already exists")

        org = Organization(**data.model_dump())
        org = await organization_repository.create(db, org)

        await audit_log_service.log(
            db,
            action="organization_create",
            resource="organization",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(org.id),
            details={"slug": org.slug},
        )
        return org

    async def update(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        data: OrganizationUpdate,
        actor: User,
    ) -> Organization:
        org = await organization_repository.get(db, org_id)
        if not org:
            raise NotFoundError("Organization not found")

        update = data.model_dump(exclude_unset=True)
        for key, value in update.items():
            setattr(org, key, value)
        await db.flush()
        await db.refresh(org)

        await audit_log_service.log(
            db,
            action="organization_update",
            resource="organization",
            actor_id=str(actor.id),
            actor_email=actor.email,
            resource_id=str(org.id),
            details=update,
        )
        return org


admin_auth_service = AdminAuthService()
admin_user_service = AdminUserService()
admin_dashboard_service = AdminDashboardService()
feature_flag_service = FeatureFlagService()
organization_service = OrganizationService()
audit_log_service = AuditLogService()
