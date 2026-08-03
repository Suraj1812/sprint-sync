"""Security helpers for password hashing and JWT access/refresh tokens."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hash a plain text password with Argon2id."""
    return ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain text password against an Argon2id hash."""
    try:
        ph.verify(hashed, plain)
        return True
    except VerifyMismatchError:
        return False


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _build_token_payload(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    **extra: str,
) -> dict:
    now = _now()
    return {
        "sub": subject,
        "type": token_type,
        "jti": secrets.token_urlsafe(16),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        **extra,
    }


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    """Issue a short-lived access token."""
    settings = get_settings()
    payload = _build_token_payload(
        str(user_id),
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
        role=role,
    )
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: uuid.UUID, token_family: str) -> str:
    """Issue a long-lived refresh token."""
    settings = get_settings()
    payload = _build_token_payload(
        str(user_id),
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
        family=token_family,
    )
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_admin_token(user_id: uuid.UUID, session_id: uuid.UUID, role: str) -> str:
    """Issue a short-lived admin session token."""
    settings = get_settings()
    payload = _build_token_payload(
        str(user_id),
        "admin",
        timedelta(hours=settings.admin_token_expire_hours),
        session=str(session_id),
        role=role,
    )
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str, expected_type: str) -> dict:
    """Decode and validate a JWT, checking type and signature."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc

    if payload.get("type") != expected_type:
        raise AuthenticationError("Invalid token type")

    return payload
