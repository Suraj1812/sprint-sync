"""RAG retrieval service."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.services.embedding import embedding_service, vector_store
from app.core.exceptions import NotFoundError
from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self) -> None:
        super().__init__(Document)


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self) -> None:
        super().__init__(DocumentChunk)


document_repository = DocumentRepository()
document_chunk_repository = DocumentChunkRepository()


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    return chunks


class RetrievalService:
    async def ingest(
        self,
        db: AsyncSession,
        title: str,
        source: str,
        text: str,
        provider: str = "openai",
        model: str = "text-embedding-3-small",
    ) -> Document:
        document = Document(
            title=title,
            source=source,
            content_hash=str(hash(text)),
        )
        document = await document_repository.create(db, document)

        chunks = _chunk_text(text)
        embeddings = await embedding_service.embed(provider, model, chunks)

        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings.embeddings)):
            chunk = DocumentChunk(
                document_id=document.id,
                content=chunk_text,
                embedding=embedding,
                chunk_index=idx,
            )
            await document_chunk_repository.create(db, chunk)
            vector_store.add(
                chunk_id=str(chunk.id),
                content=chunk_text,
                embedding=embedding,
                metadata={"document_id": str(document.id), "chunk_index": idx},
            )

        return document

    async def search(
        self,
        db: AsyncSession,
        query: str,
        provider: str = "openai",
        model: str = "text-embedding-3-small",
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        embeddings = await embedding_service.embed(provider, model, [query])
        return vector_store.search(embeddings.embeddings[0], top_k=top_k)

    async def get_document(
        self,
        db: AsyncSession,
        document_id: Any,
    ) -> Document:
        document = await document_repository.get(db, document_id)
        if not document:
            raise NotFoundError("Document not found")
        return document


retrieval_service = RetrievalService()
