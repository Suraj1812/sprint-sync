"""Shared API response and pagination schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class APIResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool = True
    error_code: str | None = None
    message: str | None = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(APIResponse):
    data: list = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
