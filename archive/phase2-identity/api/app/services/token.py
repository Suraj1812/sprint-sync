from __future__ import annotations

import hashlib
import json
import secrets
from datetime import timedelta

import redis.asyncio as redis

from app.core.config import get_settings


class TokenService:
    def __init__(self, client: redis.Redis) -> None:
        self._client = client
        self._ttl = timedelta(days=get_settings().refresh_token_expire_days)

    async def create_refresh_token(self, user_id: str) -> str:
        token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"refresh:{token_hash}"
        payload = json.dumps({"user_id": user_id})
        await self._client.setex(
            key,
            int(self._ttl.total_seconds()),
            payload,
        )
        return token

    async def consume_refresh_token(self, token: str) -> str | None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"refresh:{token_hash}"
        data = await self._client.getdel(key)
        if not data:
            return None
        payload = json.loads(data)
        return payload.get("user_id")

    async def revoke_refresh_token(self, token: str) -> None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"refresh:{token_hash}"
        await self._client.delete(key)
