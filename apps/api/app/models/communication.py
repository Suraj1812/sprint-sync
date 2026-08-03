"""Communication, notification, and delivery models."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id"),
        index=True,
        nullable=True,
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workspaces.id"),
        index=True,
        nullable=True,
    )
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(20),
        default="normal",
        nullable=False,
    )  # low, normal, high, urgent
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text)
    deep_link: Mapped[str | None] = mapped_column(String(500))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)


class NotificationPreference(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)  # in_app, email, push, sms, webhook
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # * for all
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    frequency: Mapped[str | None] = mapped_column(String(20))  # realtime, daily, weekly
    digest: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quiet_hours_start: Mapped[str | None] = mapped_column(String(5))  # HH:MM
    quiet_hours_end: Mapped[str | None] = mapped_column(String(5))
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)


class EmailTemplate(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "email_templates"

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    html_body: Mapped[str | None] = mapped_column(Text)
    text_body: Mapped[str | None] = mapped_column(Text)
    layout: Mapped[str | None] = mapped_column(String(100))
    variables: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)


class CommunicationEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "communication_events"

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id"),
        index=True,
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, processing, completed, failed
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_retry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DeliveryAttempt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "delivery_attempts"

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("communication_events.id"),
        index=True,
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # sent, delivered, opened, clicked, failed, bounced
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    response: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)


class Device(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "devices"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # web, ios, android
    token: Mapped[str] = mapped_column(Text, nullable=False)
    endpoint: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)
