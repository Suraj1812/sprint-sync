"""Pydantic schemas for multi-tenancy."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class OrganizationCreate(BaseModel):
    name: str
    branding: dict | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    branding: dict | None = None
    billing_email: EmailStr | None = None


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    owner_id: UUID
    is_active: bool
    billing_email: str | None
    branding: dict | None
    created_at: datetime
    updated_at: datetime


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None
    branding: dict | None = None


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    branding: dict | None = None


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: str | None
    is_archived: bool
    branding: dict | None
    created_at: datetime
    updated_at: datetime


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    organization_id: UUID
    role: str
    is_suspended: bool
    created_at: datetime


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = "member"
    workspace_id: UUID | None = None
    expires_days: int = 7


class InvitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    workspace_id: UUID | None
    email: str
    role: str
    expires_at: datetime
    accepted_at: datetime | None
    rejected_at: datetime | None
    is_approved: bool | None


class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    permissions: list[str]


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    permissions: list[str]
    is_default: bool


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_id: str | None
    action: str
    resource: str
    resource_id: str | None
    organization_id: UUID | None
    workspace_id: UUID | None
    details: dict | None
    created_at: datetime
