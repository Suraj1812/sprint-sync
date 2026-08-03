"""Cost tracking service."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_usage import AIUsage
from app.repositories.base import BaseRepository


class AIUsageRepository(BaseRepository[AIUsage]):
    def __init__(self) -> None:
        super().__init__(AIUsage)

    async def total_cost_for_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        since: datetime | None = None,
    ) -> float:
        since = since or datetime.now(timezone.utc) - timedelta(days=30)
        stmt = (
            select(func.coalesce(func.sum(AIUsage.cost_usd), 0.0))
            .where(
                AIUsage.user_id == user_id,
                AIUsage.created_at >= since,
            )
        )
        result = await db.execute(stmt)
        return float(result.scalar())


ai_usage_repository = AIUsageRepository()


# Approximate per-million-token pricing in USD.
PRICING: dict[str, dict[str, tuple[float, float]]] = {
    "openai": {
        "gpt-4o": (5.0, 15.0),
        "gpt-4o-mini": (0.15, 0.60),
        "text-embedding-3-small": (0.02, 0.0),
    },
    "anthropic": {
        "claude-3-5-sonnet-20241022": (3.0, 15.0),
    },
    "ollama": {
        "default": (0.0, 0.0),
    },
}


class CostService:
    def estimate(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        provider_pricing = PRICING.get(provider, {})
        prompt_price, completion_price = provider_pricing.get(model, (0.0, 0.0))
        return (prompt_tokens * prompt_price + completion_tokens * completion_price) / 1_000_000

    async def log(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID | None,
        conversation_id: uuid.UUID | None,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int,
        status: str = "ok",
        metadata: dict | None = None,
    ) -> AIUsage:
        total_tokens = prompt_tokens + completion_tokens
        cost = self.estimate(provider, model, prompt_tokens, completion_tokens)
        usage = AIUsage(
            user_id=user_id,
            conversation_id=conversation_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            status=status,
            metadata=metadata,
        )
        return await ai_usage_repository.create(db, usage)

    async def dashboard_stats(self, db: AsyncSession) -> dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=30)
        total_cost = (
            await db.execute(
                select(func.coalesce(func.sum(AIUsage.cost_usd), 0.0)).where(
                    AIUsage.created_at >= since
                )
            )
        ).scalar() or 0.0
        total_tokens = (
            await db.execute(
                select(func.coalesce(func.sum(AIUsage.total_tokens), 0)).where(
                    AIUsage.created_at >= since
                )
            )
        ).scalar() or 0
        return {
            "total_cost_30d": float(total_cost),
            "total_tokens_30d": int(total_tokens),
        }


cost_service = CostService()
