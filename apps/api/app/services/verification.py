"""Verification token service for email and password reset flows."""

import secrets
import uuid
from datetime import timedelta

from app.db.redis import get_redis

EMAIL_VERIFICATION_PREFIX = "email_verification"
PASSWORD_RESET_PREFIX = "password_reset"


class VerificationService:
    async def create_email_verification_token(self, user_id: uuid.UUID) -> str:
        token = secrets.token_urlsafe(32)
        redis = get_redis()
        await redis.setex(
            f"{EMAIL_VERIFICATION_PREFIX}:{token}",
            int(timedelta(hours=24).total_seconds()),
            str(user_id),
        )
        return token

    async def consume_email_verification_token(
        self,
        token: str,
    ) -> str | None:
        redis = get_redis()
        key = f"{EMAIL_VERIFICATION_PREFIX}:{token}"
        user_id = await redis.get(key)
        if user_id:
            await redis.delete(key)
        return user_id

    async def create_password_reset_token(self, user_id: uuid.UUID) -> str:
        token = secrets.token_urlsafe(32)
        redis = get_redis()
        await redis.setex(
            f"{PASSWORD_RESET_PREFIX}:{token}",
            int(timedelta(minutes=30).total_seconds()),
            str(user_id),
        )
        return token

    async def consume_password_reset_token(self, token: str) -> str | None:
        redis = get_redis()
        key = f"{PASSWORD_RESET_PREFIX}:{token}"
        user_id = await redis.get(key)
        if user_id:
            await redis.delete(key)
        return user_id


verification_service = VerificationService()
