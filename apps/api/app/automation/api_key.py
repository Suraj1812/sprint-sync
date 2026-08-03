"""API key service."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, NotFoundError
from app.models.automation import ApiKey
from app.models.user import User
from app.repositories.base import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKey]):
    def __init__(self) -> None:
        super().__init__(ApiKey)

    async def get_by_hash(
        self,
        db: AsyncSession,
        key_hash: str,
    ) -> ApiKey | None:
        stmt = (
            select(ApiKey)
            .where(
                ApiKey.key_hash == key_hash,
                ApiKey.revoked_at.is_(None),
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


api_key_repository = ApiKeyRepository()


class ApiKeyService:
    def _hash(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    async def create(
        self,
        db: AsyncSession,
        *,
        user: User,
        name: str,
        scopes: list[str],
        tenant_id: uuid.UUID | None = None,
        expires_days: int | None = None,
    ) -> tuple[ApiKey, str]:
        raw = "ssk_" + secrets.token_urlsafe(32)
        key_hash = self._hash(raw)
        preview = raw[-10:]

        expires_at = None
        if expires_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        key = ApiKey(
            tenant_id=tenant_id,
            user_id=user.id,
            name=name,
            key_hash=key_hash,
            key_preview=preview,
            scopes=scopes,
            expires_at=expires_at,
        )
        await api_key_repository.create(db, key)
        return key, raw

    async def verify(
        self,
        db: AsyncSession,
        key: str,
    ) -> ApiKey:
        key_hash = self._hash(key)
        record = await api_key_repository.get_by_hash(db, key_hash)
        if not record:
            raise AuthenticationError("Invalid API key")
        if record.expires_at and record.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError("API key expired")
        record.last_used_at = datetime.now(timezone.utc)
        record.usage_count += 1
        await db.flush()
        return record

    async def has_scope(
        self,
        key: ApiKey,
        required: str,
    ) -> bool:
        return required in key.scopes or "*" in key.scopes

    async def revoke(
        self,
        db: AsyncSession,
        key_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ApiKey:
        record = await api_key_repository.get(db, key_id)
        if not record:
            raise NotFoundError("API key not found")
        if str(record.user_id) != str(user_id):
            raise AuthenticationError("Cannot revoke this key")
        record.revoked_at = datetime.now(timezone.utc)
        await db.flush()
        return record

    async def list_for_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[ApiKey]:
        stmt = (
            select(ApiKey)
            .where(ApiKey.user_id == user_id)
            .order_by(ApiKey.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()


api_key_service = ApiKeyService()
