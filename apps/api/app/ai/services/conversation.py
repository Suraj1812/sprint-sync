"""Conversation service."""

import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.conversation import Conversation, Message
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self) -> None:
        super().__init__(Conversation)

    async def list_for_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()


class MessageRepository(BaseRepository[Message]):
    def __init__(self) -> None:
        super().__init__(Message)

    async def list_for_conversation(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        result = await db.execute(stmt)
        return result.scalars().all()


conversation_repository = ConversationRepository()
message_repository = MessageRepository()


class ConversationService:
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID | None,
        provider: str,
        model: str,
        title: str | None = None,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            provider=provider,
            model=model,
            title=title,
        )
        return await conversation_repository.create(db, conversation)

    async def get(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
    ) -> Conversation:
        conversation = await conversation_repository.get(db, conversation_id)
        if not conversation:
            raise NotFoundError("Conversation not found")
        return conversation

    async def list(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Conversation]:
        return await conversation_repository.list_for_user(db, user_id, skip, limit)

    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        *,
        tool_calls: dict | None = None,
        latency_ms: int | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            latency_ms=latency_ms,
        )
        return await message_repository.create(db, message)

    async def history(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
    ) -> list[Message]:
        return await message_repository.list_for_conversation(db, conversation_id)

    async def summarize_title(
        self, db: AsyncSession, conversation_id: uuid.UUID, title: str) -> None:
        conversation = await self.get(db, conversation_id)
        conversation.title = title
        await db.flush()


conversation_service = ConversationService()
