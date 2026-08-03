"""Pydantic schemas for communications."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    category: str
    priority: str
    body: str | None
    deep_link: str | None
    is_read: bool
    read_at: datetime | None
    created_at: datetime


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str
    category: str = "general"
    body: str | None = None
    priority: str = "normal"
    deep_link: str | None = None


class NotificationCount(BaseModel):
    unread: int


class PreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    channel: str
    category: str
    enabled: bool
    frequency: str | None
    digest: bool
    quiet_hours_start: str | None
    quiet_hours_end: str | None
    language: str


class PreferenceUpdate(BaseModel):
    channel: str
    category: str
    enabled: bool
    frequency: str | None = None
    digest: bool = False
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    language: str = "en"


class EmailTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    locale: str
    version: int
    subject: str
    html_body: str | None
    text_body: str | None
    variables: list[str]
    is_active: bool


class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    html_body: str | None = None
    text_body: str | None = None
    locale: str = "en"
    variables: list[str] = []
    layout: str | None = None


class TemplatePreviewRequest(BaseModel):
    name: str
    variables: dict = {}
    locale: str = "en"


class TemplatePreviewResponse(BaseModel):
    subject: str
    html: str | None
    text: str | None


class EventPublishRequest(BaseModel):
    event_type: str
    payload: dict = {}
    tenant_id: UUID | None = None


class DeliveryStats(BaseModel):
    total: int
    pending: int
    completed: int
    failed: int
    by_channel: dict
