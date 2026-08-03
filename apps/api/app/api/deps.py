"""Shared API dependencies."""

from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import user_repository
from app.services.admin import ADMIN_ROLES, admin_auth_service

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get("access_token")

    if not token:
        raise AuthenticationError("Missing authentication token")

    payload = decode_token(token, "access")
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    user = await user_repository.get(db, UUID(user_id))
    if not user or not user.is_active or user.deleted_at is not None:
        raise AuthenticationError("User not found or inactive")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role.name not in ADMIN_ROLES:
        raise AuthorizationError("Admin access required")
    return user


def require_permission(permission: str):
    def checker(user: User = Depends(require_admin)) -> User:
        if "*" in user.role.permissions or permission in user.role.permissions:
            return user
        raise AuthorizationError(f"Permission '{permission}' required")
    return checker


async def get_current_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get("admin_token")

    if not token:
        raise AuthenticationError("Missing admin token")

    return await admin_auth_service.get_current(db, token)
