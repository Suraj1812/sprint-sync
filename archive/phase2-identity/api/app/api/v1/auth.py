from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import (
    LogoutRequest,
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserRegister,
)
from app.schemas.user import UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: UserRegister,
    auth: AuthService = Depends(get_auth_service),
) -> TokenPair:
    return await auth.register(
        payload.email,
        payload.password,
        payload.full_name,
    )


@router.post("/login", response_model=TokenPair)
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: UserLogin,
    auth: AuthService = Depends(get_auth_service),
) -> TokenPair:
    return await auth.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    auth: AuthService = Depends(get_auth_service),
) -> TokenPair:
    return await auth.refresh(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest,
    auth: AuthService = Depends(get_auth_service),
) -> None:
    await auth.logout(payload.refresh_token)


@router.get("/me", response_model=UserRead)
async def me(
    user: User = Depends(get_current_user),
) -> User:
    return user
