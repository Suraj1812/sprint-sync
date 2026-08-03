"""Embedding service and in-memory vector store."""

import math
from typing import Any

from app.ai.providers.base import EmbeddingRequest, EmbeddingResponse
from app.ai.providers.registry import provider_registry


class EmbeddingService:
    async def embed(self, provider_name: str, model: str, inputs: list[str]) -> EmbeddingResponse:
        provider = provider_registry.get(provider_name)
        return await provider.embed(EmbeddingRequest(model=model, inputs=inputs))

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
        norm_b = math.sqrt(sum(x * x for x in b)) or 1.0
        return dot / (norm_a * norm_b)


class InMemoryVectorStore:
    """Development vector store. Replace with pgvector/Pinecone in production."""

    def __init__(self) -> None:
        self._index: list[dict[str, Any]] = []

    def add(self, chunk_id: str, content: str, embedding: list[float], metadata: dict) -> None:
        self._index.append({
            "id": chunk_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata,
        })

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        scored = []
        for item in self._index:
            score = EmbeddingService().cosine_similarity(query_embedding, item["embedding"])
            scored.append({**item, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    async def clear(self) -> None:
        self._index.clear()


embedding_service = EmbeddingService()
vector_store = InMemoryVectorStore()
