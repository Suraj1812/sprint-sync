"""Prompt management models."""

import uuid

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class Prompt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "prompts"

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    default_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("prompt_versions.id"),
        nullable=True,
    )
    variables: Mapped[list[str] | None] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class PromptVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "prompt_versions"

    prompt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prompts.id"),
        index=True,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    system: Mapped[str | None] = mapped_column(Text)
    user_template: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
