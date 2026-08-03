# RAG Documentation

## Pipeline

1. **Ingestion** — `POST /api/v1/ai/documents` accepts title, source, and raw text.
2. **Chunking** — text is split into 512-character chunks with 64-character overlap.
3. **Embedding** — chunks are embedded using the configured provider (default OpenAI `text-embedding-3-small`).
4. **Storage** — chunks and embeddings are stored in `document_chunks` and an in-memory vector index (production: pgvector, Pinecone, Qdrant, Weaviate).
5. **Search** — `POST /api/v1/ai/documents/search` embeds the query and returns the top-k chunks by cosine similarity.

## Vector Store Trade-offs

| Option | Pros | Cons |
|---|---|---|
| pgvector | Same DB as app, ACID, easy backups | Scales to ~1M vectors comfortably |
| Pinecone | Managed, high recall, hybrid search | Vendor lock-in, cost |
| Qdrant | Open-source, on-premise, fast | Self-hosted ops |
| Weaviate | Semantic + BM25, GraphQL | Complex deployment |

## Recommendation

Start with **pgvector** to keep operational overhead low. When document counts exceed ~1M or hybrid search is needed, migrate to **Qdrant** or **Pinecone** behind the `VectorStore` interface.
