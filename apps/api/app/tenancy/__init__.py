"""Tenant and workspace services."""

from app.tenancy.context import get_current_tenant, tenant_context

__all__ = ["tenant_context", "get_current_tenant"]
