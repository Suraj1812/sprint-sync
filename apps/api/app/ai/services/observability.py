"""AI observability logging."""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_call import AICallLog
from app.repositories.base import BaseRepository


class AICallLogRepository(BaseRepository[AICallLog]):
    def __init__(self) -> None:
        super().__init__(AICallLog)


ai_call_log_repository = AICallLogRepository()


@asynccontextmanager
async def trace_ai_call(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    provider: str,
    model: str,
    operation: str,
    metadata: dict | None = None,
):
    start = time.monotonic()
    error: str | None = None
    try:
        yield
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        latency_ms = int((time.monotonic() - start) * 1000)
        log = AICallLog(
            user_id=user_id,
            provider=provider,
            model=model,
            operation=operation,
            latency_ms=latency_ms,
            error=error,
            metadata=metadata,
        )
        await ai_call_log_repository.create(db, log)
