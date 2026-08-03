"""Admin API v1 endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db_session
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.schemas.admin import (
    AdminAuthResponse,
    AdminLogin,
    AdminUserRead,
    AuditLogRead,
    DashboardStats,
    FeatureFlagCreate,
    FeatureFlagRead,
    FeatureFlagUpdate,
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    UserListResponse,
    UserStatusUpdate,
)
from app.schemas.auth import UserLogin
from app.schemas.common import APIResponse, PaginatedResponse
from app.services.admin import (
    admin_auth_service,
    admin_dashboard_service,
    admin_user_service,
    feature_flag_service,
    organization_service,
)
from app.services.audit_log import audit_log_service

bearer_scheme = HTTPBearer(auto_error=False)
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.post("/auth/login", response_model=AdminAuthResponse)
async def admin_login(
    data: AdminLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
) -> AdminAuthResponse:
    _, tokens = await admin_auth_service.login(
        db,
        UserLogin(email=data.email, password=data.password),
        request=request,
    )
    from app.core.config import get_settings

    is_prod = get_settings().environment == "production"
    response.set_cookie(
        key="admin_token",
        value=tokens.access_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=tokens.expires_in,
    )
    return tokens


@admin_router.post("/auth/logout", response_model=APIResponse)
async def admin_logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    token = credentials.credentials if credentials else request.cookies.get("admin_token")
    if not token:
        raise AuthenticationError("Missing admin token")
    await admin_auth_service.logout(db, token)
    response.delete_cookie("admin_token")
    return APIResponse(message="Logged out")


@admin_router.get("/auth/me", response_model=APIResponse)
async def admin_me(current_user: User = Depends(get_current_admin)) -> APIResponse:
    return APIResponse(
        data={
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.name,
            "permissions": current_user.role.permissions,
        }
    )


@admin_router.get("/auth/sessions")
async def admin_sessions(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db_session),
):
    sessions = await admin_auth_service.list_sessions(db, current_user.id)
    return [
        {
            "id": str(s.id),
            "ip_address": s.ip_address,
            "user_agent": s.user_agent,
            "created_at": s.created_at,
            "expires_at": s.expires_at,
            "is_active": s.is_active,
        }
        for s in sessions
    ]


@admin_router.post("/auth/sessions/{session_id}/revoke", response_model=APIResponse)
async def admin_revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    await admin_auth_service.revoke_session(db, session_id, current_user)
    return APIResponse(message="Session revoked")


@admin_router.get("/dashboard", response_model=DashboardStats)
async def admin_dashboard(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> DashboardStats:
    return await admin_dashboard_service.stats(db)


@admin_router.get("/users", response_model=UserListResponse)
async def admin_list_users(
    q: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> UserListResponse:
    users, total = await admin_user_service.list_users(
        db,
        skip=skip,
        limit=limit,
        q=q,
        role=role,
        is_active=is_active,
    )
    return UserListResponse(
        data=users,
        total=total,
    )


@admin_router.patch("/users/{user_id}", response_model=APIResponse)
async def admin_update_user(
    user_id: UUID,
    data: UserStatusUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> APIResponse:
    user = await admin_user_service.update_user(db, user_id, data, current_user)
    return APIResponse(
        data=AdminUserRead.model_validate(user).model_dump(),
        message="User updated",
    )


@admin_router.post("/users/{user_id}/reset-password", response_model=APIResponse)
async def admin_reset_password(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> APIResponse:
    temp = await admin_user_service.reset_password(db, user_id, current_user)
    return APIResponse(
        data={"temp_password": temp},  # nosec: placeholder until email delivery
        message="Password reset",
    )


@admin_router.get("/audit-logs", response_model=PaginatedResponse)
async def admin_audit_logs(
    action: str | None = None,
    resource: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> PaginatedResponse:
    logs = await audit_log_service.search(db, action=action, resource=resource, skip=skip, limit=limit)
    data = [AuditLogRead.model_validate(log).model_dump() for log in logs]
    return PaginatedResponse(data=data, total=len(data), page=1, page_size=limit)


@admin_router.get("/feature-flags", response_model=list[FeatureFlagRead])
async def admin_list_feature_flags(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> list[FeatureFlagRead]:
    flags = await feature_flag_service.list(db)
    return [FeatureFlagRead.model_validate(flag) for flag in flags]


@admin_router.post(
    "/feature-flags",
    response_model=FeatureFlagRead,
    status_code=status.HTTP_201_CREATED,
)
async def admin_create_feature_flag(
    data: FeatureFlagCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> FeatureFlagRead:
    flag = await feature_flag_service.create(db, data, current_user)
    return FeatureFlagRead.model_validate(flag)


@admin_router.patch("/feature-flags/{flag_id}", response_model=FeatureFlagRead)
async def admin_update_feature_flag(
    flag_id: UUID,
    data: FeatureFlagUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> FeatureFlagRead:
    flag = await feature_flag_service.update(db, flag_id, data, current_user)
    return FeatureFlagRead.model_validate(flag)


@admin_router.delete("/feature-flags/{flag_id}", response_model=APIResponse)
async def admin_delete_feature_flag(
    flag_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> APIResponse:
    await feature_flag_service.delete(db, flag_id, current_user)
    return APIResponse(message="Feature flag deleted")


@admin_router.get("/organizations", response_model=list[OrganizationRead])
async def admin_list_organizations(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> list[OrganizationRead]:
    orgs = await organization_service.list(db)
    return [OrganizationRead.model_validate(o) for o in orgs]


@admin_router.post(
    "/organizations",
    response_model=OrganizationRead,
    status_code=status.HTTP_201_CREATED,
)
async def admin_create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> OrganizationRead:
    org = await organization_service.create(db, data, current_user)
    return OrganizationRead.model_validate(org)


@admin_router.patch("/organizations/{org_id}", response_model=OrganizationRead)
async def admin_update_organization(
    org_id: UUID,
    data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin),
) -> OrganizationRead:
    org = await organization_service.update(db, org_id, data, current_user)
    return OrganizationRead.model_validate(org)
