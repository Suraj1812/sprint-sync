"""AI platform API v1."""

import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.services.chat import chat_service
from app.ai.services.conversation import conversation_service
from app.ai.services.cost import cost_service
from app.ai.services.embedding import embedding_service
from app.ai.services.prompt import prompt_repository, prompt_service
from app.ai.services.retrieval import retrieval_service
from app.ai.services.tool import tool_executor
from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ConversationRead,
    DocumentCreate,
    DocumentRead,
    EmbedRequest,
    MessageRead,
    PromptCreate,
    PromptRead,
    SearchRequest,
    SearchResult,
    StreamChunk,
    ToolList,
    UsageStats,
)
from app.schemas.common import APIResponse

ai_router = APIRouter(prefix="/ai", tags=["ai"])


async def _sse_content(lines: AsyncIterator[str]):
    async for chunk in lines:
        yield _sse_line(f"data: {chunk}")


def _sse_line(text: str) -> bytes:
    return (text + "\n\n").encode("utf-8")


def _sse(lines: AsyncIterator[str]) -> StreamingResponse:
    return StreamingResponse(
        _sse_content(lines),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@ai_router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> ChatResponse:
    response = await chat_service.chat(
        db,
        user_id=user.id,
        message=request.message,
        conversation_id=request.conversation_id,
        provider_name=request.provider,
        model=request.model,
        prompt_name=request.prompt,
        prompt_variables=request.prompt_variables,
        use_rag=request.use_rag,
        tools=request.tools,
        user_permissions=set(user.role.permissions),
    )
    return ChatResponse(
        content=response.content,
        finish_reason=response.finish_reason,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        total_tokens=response.total_tokens,
        latency_ms=response.latency_ms,
        provider=response.provider,
        model=response.model,
    )


@ai_router.post("/chat/stream")
async def ai_chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    async def stream() -> AsyncIterator[str]:
        async for chunk in chat_service.stream(
            db,
            user_id=user.id,
            message=request.message,
            conversation_id=request.conversation_id,
            provider_name=request.provider,
            model=request.model,
            prompt_name=request.prompt,
            prompt_variables=request.prompt_variables,
            use_rag=request.use_rag,
        ):
            yield json.dumps(StreamChunk(
                content=chunk.content,
                finish_reason=chunk.finish_reason,
            ).model_dump())

    return _sse(stream())


@ai_router.post("/prompts", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    data: PromptCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    prompt = await prompt_service.get_or_create(
        db,
        name=data.name,
        user_template=data.user_template,
        system=data.system,
        description=data.description,
        variables=data.variables,
    )
    return prompt


@ai_router.get("/prompts", response_model=list[PromptRead])
async def list_prompts(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await prompt_repository.get_all(db, skip=skip, limit=limit)


@ai_router.post("/conversations", response_model=ConversationRead)
async def create_conversation(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    # TODO: accept provider/model in body
    conversation = await conversation_service.create(
        db,
        user_id=user.id,
        provider="openai",
        model="gpt-4o-mini",
    )
    return conversation


@ai_router.get("/conversations", response_model=list[ConversationRead])
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await conversation_service.list(db, user.id, skip=skip, limit=limit)


@ai_router.get("/conversations/{conversation_id}/messages", response_model=list[MessageRead])
async def get_messages(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    conversation = await conversation_service.get(db, conversation_id)
    return await conversation_service.history(db, conversation.id)


@ai_router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    document = await retrieval_service.ingest(
        db,
        title=data.title,
        source=data.source,
        text=data.text,
        provider=data.provider,
        model=data.model,
    )
    return document


@ai_router.post("/documents/search", response_model=list[SearchResult])
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[SearchResult]:
    results = await retrieval_service.search(db, request.query, top_k=request.top_k)
    return [SearchResult(**r) for r in results]


@ai_router.post("/embeddings")
async def create_embeddings(
    request: EmbedRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> APIResponse:
    embeddings = await embedding_service.embed(request.provider, request.model, request.inputs)
    return APIResponse(data={"embeddings": embeddings.embeddings})


@ai_router.get("/usage", response_model=UsageStats)
async def usage_stats(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> UsageStats:
    stats = await cost_service.dashboard_stats(db)
    return UsageStats(**stats)


@ai_router.get("/tools", response_model=ToolList)
async def list_tools(
    user: User = Depends(get_current_user),
) -> ToolList:
    return ToolList(tools=tool_executor.list_schemas(set(user.role.permissions)))


@ai_router.get("/providers")
async def list_providers(
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    result = []
    for name in provider_registry.list():
        provider = provider_registry.get(name)
        result.append({"name": name, **await provider.health()})
    return result
