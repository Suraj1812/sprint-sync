"""Pydantic schemas for the admin platform."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class AdminLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    mfa_code: str | None = None


class AdminAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    email_verified: bool
    role: str
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @field_validator("role", mode="before")
    @classmethod
    def _role_name(cls, value: object) -> str:
        if hasattr(value, "name"):
            return value.name
        if not isinstance(value, str):
            raise ValueError("role must be a string or Role object")
        return value


class UserListResponse(BaseModel):
    data: list[AdminUserRead]
    total: int


class UserStatusUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    email_verified: bool | None = None
    role: str | None = None


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_id: str | None
    actor_email: str | None
    action: str
    resource: str
    resource_id: str | None
    ip_address: str | None
    created_at: datetime


class FeatureFlagCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    enabled: bool = False
    environment: str = "production"
    rollout_percentage: int = Field(100, ge=0, le=100)
    targeting: dict | None = None
    scheduled_at: datetime | None = None


class FeatureFlagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    enabled: bool | None = None
    rollout_percentage: int | None = Field(default=None, ge=0, le=100)
    targeting: dict | None = None
    scheduled_at: datetime | None = None


class FeatureFlagRead(FeatureFlagCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    owner_id: UUID
    settings: dict | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None
    settings: dict | None = None


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    owner_id: UUID
    is_active: bool
    settings: dict | None
    created_at: datetime
    updated_at: datetime


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    new_registrations_24h: int
    failed_logins_24h: int
    admin_sessions: int
    pending_feature_flags: int
    uptime: str
    version: str
