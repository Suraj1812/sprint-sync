"""Authentication API v1 endpoints."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.audit import audit
from app.core.exceptions import AuthenticationError, NotFoundError
from app.core.rate_limit import limiter
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.auth import (
    AuthResponse,
    EmailVerification,
    PasswordResetRequest,
    RefreshToken,
    TokenPair,
    UserLogin,
    UserRegister,
)
from app.schemas.common import APIResponse
from app.schemas.user import UserRead
from app.services.auth import auth_service
from app.services.verification import verification_service
from app.workers.tasks import send_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: UserRegister,
    db: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    user = await auth_service.register(db, data)
    _, tokens = await auth_service.login(
        db,
        UserLogin(email=data.email, password=data.password),
    )
    return AuthResponse(
        user=UserRead(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            email_verified=user.email_verified,
            role=user.role.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
        tokens=tokens,
    )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    user, tokens = await auth_service.login(db, data)
    return AuthResponse(
        user=UserRead(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            email_verified=user.email_verified,
            role=user.role.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
        tokens=tokens,
    )


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    data: RefreshToken,
    db: AsyncSession = Depends(get_db_session),
) -> TokenPair:
    _, tokens = await auth_service.refresh(db, data.refresh_token)
    return tokens


@router.post("/logout", response_model=APIResponse)
@limiter.limit("20/minute")
async def logout(request: Request, data: RefreshToken) -> APIResponse:
    await auth_service.logout(data.refresh_token)
    return APIResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=APIResponse)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    user = await user_repository.get_by_email(db, data.email)
    if user:
        token = await verification_service.create_password_reset_token(user.id)
        send_email.delay(
            to=user.email,
            subject="Reset your SprintSync password",
            body=f"Password reset token: {token}",
        )
        audit(
            "password_reset_requested",
            user_id=str(user.id),
            email=user.email,
            success=True,
        )
    # Always return the same message to prevent email enumeration.
    return APIResponse(
        message="If an account exists, a reset email has been sent."
    )


@router.post("/verify-email", response_model=APIResponse)
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    data: EmailVerification,
    db: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    user_id = await verification_service.consume_email_verification_token(data.token)
    if not user_id:
        raise AuthenticationError("Invalid or expired verification token")

    user = await user_repository.get(db, user_id)
    if not user:
        raise NotFoundError("User not found")

    user.email_verified = True
    await db.commit()
    audit(
        "email_verified",
        user_id=str(user.id),
        email=user.email,
        success=True,
    )
    return APIResponse(message="Email verified successfully")


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        email_verified=current_user.email_verified,
        role=current_user.role.name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
