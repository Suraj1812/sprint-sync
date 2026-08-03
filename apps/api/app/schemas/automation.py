"""Pydantic schemas for automation and integrations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DomainEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID | None
    event_type: str
    version: int
    payload: dict | None
    correlation_id: str | None
    source: str | None
    status: str
    processed_at: datetime | None
    created_at: datetime


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    trigger: dict
    steps: list[dict] = []
    tenant_id: UUID | None = None


class WorkflowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID | None
    name: str
    description: str | None
    trigger: dict
    steps: list[dict]
    is_active: bool
    status: str
    version: int
    created_at: datetime


class WorkflowRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    result: dict | None
    error: str | None


class WebhookSubscriptionCreate(BaseModel):
    name: str
    url: str
    events: list[str]
    tenant_id: UUID | None = None


class WebhookSubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID | None
    name: str
    url: str
    events: list[str]
    is_active: bool
    last_delivery_at: datetime | None
    failure_count: int
    created_at: datetime


class WebhookDeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subscription_id: UUID
    event_id: UUID
    status: str
    response_status: int | None
    error: str | None
    created_at: datetime


class ApiKeyCreate(BaseModel):
    name: str
    scopes: list[str] = []
    expires_days: int | None = None


class ApiKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key_preview: str
    scopes: list[str]
    expires_at: datetime | None
    last_used_at: datetime | None
    usage_count: int


class ApiKeyCreateResponse(ApiKeyRead):
    key: str


class OAuthClientCreate(BaseModel):
    name: str
    redirect_uris: list[str]
    allowed_scopes: list[str]
    tenant_id: UUID | None = None


class OAuthClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID | None
    name: str
    client_id: str
    redirect_uris: list[str]
    allowed_scopes: list[str]
    is_active: bool
    created_at: datetime


class OAuthClientCreateResponse(OAuthClientRead):
    client_secret: str


class OAuthAuthorizeRequest(BaseModel):
    client_id: str
    redirect_uri: str
    scope: str = ""
    state: str | None = None
    code_challenge: str | None = None
    code_challenge_method: str | None = "S256"


class OAuthTokenRequest(BaseModel):
    client_id: str
    client_secret: str
    code: str
    redirect_uri: str
    code_verifier: str | None = None


class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    refresh_token: str | None = None
    scope: str = ""
