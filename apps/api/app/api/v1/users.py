"""User management API v1 endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session, require_admin
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.user import UserRead, UserUpdate
from app.services.user import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse)
async def list_users(
    params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> PaginatedResponse:
    users = await user_service.list_users(
        db,
        skip=(params.page - 1) * params.page_size,
        limit=params.page_size,
    )
    return PaginatedResponse(
        data=users,
        page=params.page,
        page_size=params.page_size,
        total=len(users),
    )


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    user = await user_service.get_user(db, user_id)
    if user.id != current_user.id and current_user.role.name != "admin":
        from app.core.exceptions import AuthorizationError

        raise AuthorizationError("You can only view your own profile")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    if user_id != current_user.id and current_user.role.name != "admin":
        from app.core.exceptions import AuthorizationError

        raise AuthorizationError("You can only update your own profile")
    return await user_service.update_user(db, user_id, data)
