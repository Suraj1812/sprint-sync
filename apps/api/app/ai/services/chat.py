"""Chat service coordinating providers, prompts, RAG, tools, cost and guardrails."""

import time
import uuid
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import ChatMessage, ChatRequest, ChatResponse, StreamChunk
from app.ai.providers.registry import provider_registry
from app.ai.services.conversation import conversation_service
from app.ai.services.cost import cost_service
from app.ai.services.guardrails import guardrails
from app.ai.services.prompt import prompt_service
from app.ai.services.retrieval import retrieval_service
from app.ai.services.tool import tool_executor


class ChatService:
    async def chat(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID | None,
        message: str,
        conversation_id: uuid.UUID | None = None,
        provider_name: str | None = None,
        model: str | None = None,
        prompt_name: str | None = None,
        prompt_variables: dict[str, Any] | None = None,
        use_rag: bool = False,
        tools: list[str] | None = None,
        user_permissions: set[str] | None = None,
    ) -> ChatResponse:
        guardrails.validate_input(message)
        provider_name, model = self._resolve(provider_name, model)
        provider = provider_registry.get(provider_name)

        messages = await self._build_messages(
            db,
            user_id,
            message,
            conversation_id,
            prompt_name,
            prompt_variables,
            use_rag,
            provider,
        )

        tool_schemas = None
        if tools:
            tool_schemas = tool_executor.list_schemas(user_permissions)

        start = time.monotonic()
        response = await provider.chat(
            ChatRequest(
                model=model,
                messages=messages,
                tools=tool_schemas or None,
            )
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        if response.tool_calls:
            tool_results = await tool_executor.run_tool_calls(
                response.tool_calls,
                user_permissions=user_permissions,
            )
            # Append tool results as a follow-up assistant message.
            response.content += "\n\n" + "\n".join(
                f"{r['tool']}: {r['result']}" for r in tool_results
            )

        response.content = guardrails.filter_output(response.content)

        conversation = await self._ensure_conversation(
            db,
            user_id,
            conversation_id,
            provider_name,
            model,
            message,
            response,
            latency_ms,
        )

        await cost_service.log(
            db,
            user_id=user_id,
            conversation_id=conversation.id,
            provider=provider_name,
            model=model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            latency_ms=latency_ms,
            status="ok",
        )

        return response

    async def stream(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID | None,
        message: str,
        conversation_id: uuid.UUID | None = None,
        provider_name: str | None = None,
        model: str | None = None,
        prompt_name: str | None = None,
        prompt_variables: dict[str, Any] | None = None,
        use_rag: bool = False,
    ) -> AsyncIterator[StreamChunk]:
        guardrails.validate_input(message)
        provider_name, model = self._resolve(provider_name, model)
        provider = provider_registry.get(provider_name)

        messages = await self._build_messages(
            db,
            user_id,
            message,
            conversation_id,
            prompt_name,
            prompt_variables,
            use_rag,
            provider,
        )

        start = time.monotonic()
        buffer = []
        async for chunk in provider.stream_chat(ChatRequest(model=model, messages=messages)):
            buffer.append(chunk.content)
            yield chunk

        latency_ms = int((time.monotonic() - start) * 1000)
        full = "".join(buffer)
        full = guardrails.filter_output(full)

        conversation = await self._ensure_conversation(
            db,
            user_id,
            conversation_id,
            provider_name,
            model,
            message,
            ChatResponse(
                content=full,
                total_tokens=provider.estimate_tokens(message) + provider.estimate_tokens(full),
                latency_ms=latency_ms,
                model=model,
                provider=provider_name,
            ),
            latency_ms,
        )

        await cost_service.log(
            db,
            user_id=user_id,
            conversation_id=conversation.id,
            provider=provider_name,
            model=model,
            prompt_tokens=provider.estimate_tokens(message),
            completion_tokens=provider.estimate_tokens(full),
            latency_ms=latency_ms,
            status="ok",
        )

    def _resolve(self, provider_name: str | None, model: str | None) -> tuple[str, str]:
        from app.core.config import get_settings

        settings = get_settings()
        provider_name = provider_name or settings.ai_default_provider
        model = model or settings.ai_default_model
        return provider_name, model

    async def _build_messages(
        self,
        db: AsyncSession,
        user_id: uuid.UUID | None,
        message: str,
        conversation_id: uuid.UUID | None,
        prompt_name: str | None,
        prompt_variables: dict[str, Any] | None,
        use_rag: bool,
        provider: Any,
    ) -> list[ChatMessage]:
        messages: list[ChatMessage] = []
        user_text = message

        if prompt_name:
            system, user_text = await prompt_service.render(db, prompt_name, prompt_variables)
            if system:
                messages.append(ChatMessage(role="system", content=system))
            messages.append(ChatMessage(role="user", content=user_text))
        else:
            messages.append(ChatMessage(role="user", content=message))

        if conversation_id:
            history = await conversation_service.history(db, conversation_id)
            for h in history[-10:]:
                messages.insert(-1, ChatMessage(role=h.role, content=h.content))

        if use_rag:
            # Always use the first user message as query.
            chunks = await retrieval_service.search(db, user_text, top_k=3)
            chunks = guardrails.check_rag_context(chunks)
            if chunks:
                context = "\n\n".join(f"[{i+1}] {c['content']}" for i, c in enumerate(chunks))
                messages.append(
                    ChatMessage(
                        role="system",
                        content=f"Use the following context to answer:\n{context}",
                    )
                )

        # Trim to a token budget using the provider's estimator.
        total = sum(provider.estimate_tokens(m.content) for m in messages)
        max_context = 4096
        while total > max_context and len(messages) > 2:
            messages.pop(1)
            total = sum(provider.estimate_tokens(m.content) for m in messages)

        return messages

    async def _ensure_conversation(
        self,
        db: AsyncSession,
        user_id: uuid.UUID | None,
        conversation_id: uuid.UUID | None,
        provider: str,
        model: str,
        user_message: str,
        response: ChatResponse,
        latency_ms: int,
    ) -> Any:
        if conversation_id:
            conversation = await conversation_service.get(db, conversation_id)
        else:
            conversation = await conversation_service.create(
                db,
                user_id=user_id,
                provider=provider,
                model=model,
                title=user_message[:40],
            )

        await conversation_service.add_message(
            db,
            conversation.id,
            "user",
            user_message,
        )
        await conversation_service.add_message(
            db,
            conversation.id,
            "assistant",
            response.content,
            latency_ms=latency_ms,
        )
        return conversation


chat_service = ChatService()
