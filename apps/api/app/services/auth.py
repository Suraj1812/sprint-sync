"""Authentication service for registration, login, and token refresh."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.redis import get_redis
from app.models.user import User
from app.repositories.role import role_repository
from app.repositories.user import user_repository
from app.schemas.auth import TokenPair, UserLogin, UserRegister
from app.services.audit_log import audit_log_service
from app.services.verification import verification_service
from app.workers.tasks import send_email

logger = get_logger("services.auth")

REFRESH_PREFIX = "refresh_token"
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 900


def _lockout_key(email: str) -> str:
    return f"login_attempts:{email.lower()}"


class AuthService:
    async def _record_failed_login(self, email: str) -> None:
        redis = get_redis()
        key = _lockout_key(email)
        attempts = await redis.incr(key)
        if attempts == 1:
            await redis.expire(key, LOGIN_LOCKOUT_SECONDS)

    async def _reset_login_attempts(self, email: str) -> None:
        redis = get_redis()
        await redis.delete(_lockout_key(email))

    async def _is_locked_out(self, email: str) -> bool:
        redis = get_redis()
        attempts = await redis.get(_lockout_key(email))
        return attempts is not None and int(attempts) >= MAX_LOGIN_ATTEMPTS

    async def _queue_verification_email(self, user: User) -> None:
        token = await verification_service.create_email_verification_token(user.id)
        send_email.delay(
            to=user.email,
            subject="Verify your SprintSync email",
            body=f"Verification token: {token}",
        )

    async def register(
        self,
        db: AsyncSession,
        data: UserRegister,
    ) -> User:
        existing = await user_repository.get_by_email(db, data.email)
        if existing:
            raise ConflictError("An account with this email already exists")

        role = await role_repository.get_by_name(db, "user")
        if not role:
            raise NotFoundError("Default user role not found")

        user = User(
            email=str(data.email),
            hashed_password=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role_id=role.id,
        )
        user = await user_repository.create(db, user)
        audit("user_registered", user_id=str(user.id), email=user.email)
        await self._queue_verification_email(user)
        return user

    async def login(
        self,
        db: AsyncSession,
        data: UserLogin,
    ) -> tuple[User, TokenPair]:
        email = str(data.email)

        if await self._is_locked_out(email):
            audit(
                "login_attempt",
                email=email,
                success=False,
                reason="account_locked",
            )
            await audit_log_service.log(
                db,
                "login_attempt",
                "user",
                actor_email=email,
                details={"success": False, "reason": "account_locked"},
            )
            raise AuthenticationError(
                "Account temporarily locked. Please try again later."
            )

        user = await user_repository.get_active_by_email(db, email)
        if not user or not verify_password(data.password, user.hashed_password):
            await self._record_failed_login(email)
            audit("login_attempt", email=email, success=False, reason="bad_credentials")
            await audit_log_service.log(
                db,
                "login_attempt",
                "user",
                actor_email=email,
                details={"success": False, "reason": "bad_credentials"},
            )
            raise AuthenticationError("Invalid email or password")

        await self._reset_login_attempts(email)

        token_family = uuid.uuid4().hex
        access = create_access_token(user.id, user.role.name)
        refresh = create_refresh_token(user.id, token_family)

        redis = get_redis()
        await redis.setex(
            f"{REFRESH_PREFIX}:{user.id}:{refresh}",
            int(timedelta(days=7).total_seconds()),
            "1",
        )

        audit(
            "login_attempt",
            user_id=str(user.id),
            email=user.email,
            success=True,
        )
        user.last_login_at = datetime.now(timezone.utc)
        await db.flush()

        await audit_log_service.log(
            db,
            "login_attempt",
            "user",
            actor_id=str(user.id),
            actor_email=user.email,
            details={"success": True},
        )
        return user, TokenPair(access_token=access, refresh_token=refresh)

    async def refresh(
        self,
        db: AsyncSession,
        token: str,
    ) -> tuple[User, TokenPair]:
        payload = decode_token(token, "refresh")
        try:
            user_id = uuid.UUID(payload["sub"])
        except (KeyError, ValueError) as exc:
            raise AuthenticationError("Invalid refresh token") from exc

        family = payload.get("family")
        if not family:
            raise AuthenticationError("Invalid refresh token")

        redis = get_redis()
        stored = await redis.get(f"{REFRESH_PREFIX}:{user_id}:{token}")
        if stored is None:
            raise AuthenticationError("Refresh token has been revoked")

        user = await user_repository.get(db, user_id)
        if not user or not user.is_active or user.deleted_at is not None:
            raise AuthenticationError("User not found or inactive")

        await redis.delete(f"{REFRESH_PREFIX}:{user_id}:{token}")

        new_access = create_access_token(user.id, user.role.name)
        new_refresh = create_refresh_token(user.id, family)
        await redis.setex(
            f"{REFRESH_PREFIX}:{user_id}:{new_refresh}",
            int(timedelta(days=7).total_seconds()),
            "1",
        )

        audit("token_refreshed", user_id=str(user.id), success=True)
        return user, TokenPair(access_token=new_access, refresh_token=new_refresh)

    async def logout(self, token: str) -> None:
        payload = decode_token(token, "refresh")
        user_id = payload.get("sub")
        if user_id:
            redis = get_redis()
            await redis.delete(f"{REFRESH_PREFIX}:{user_id}:{token}")
            audit("logout", user_id=user_id, success=True)


auth_service = AuthService()
