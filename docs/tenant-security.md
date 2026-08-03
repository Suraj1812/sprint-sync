# Tenant Security

## Goals

- Zero cross-tenant data leakage.
- Defense in depth for membership, workspace, and role changes.
- Full audit trail.

## Controls

- **Tenant resolution** happens before any business logic.
- **Membership validation** on every request.
- **RBAC** for all mutations.
- **Audit logs** include `organization_id`, `workspace_id`, actor, and IP.
- **Soft deletes** preserve data and allow recovery.
- **Suspension** disables all access without data loss.

## Custom Domains

`CustomDomain` supports:
- Domain name
- TXT verification token
- Verified flag
- Certificate ARN for SSL/TLS (via ACM / cert-manager)

## Background Jobs

Always wrap with `tenant_context(org_id)` and use the `X-Organization-Id` or database `organization_id` filter.

## Search

If using Elasticsearch, OpenSearch, or pgvector, prefix indexes with `tenant-{org_id}`.
