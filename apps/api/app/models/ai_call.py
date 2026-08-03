"""AI call observability logs."""

import uuid

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class AICallLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_call_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    operation: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    record_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
