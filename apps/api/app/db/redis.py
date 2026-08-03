from functools import lru_cache
import redis.asyncio as redis

from app.core.config import get_settings


@lru_cache
def get_redis() -> redis.Redis:
    return redis.from_url(
        get_settings().redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
