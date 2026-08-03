# Tenant Isolation

## Rules

1. Every tenant-scoped table has `organization_id`.
2. Workspace-scoped tables also have `workspace_id`.
3. Queries must always include `WHERE organization_id = :org_id`.
4. Dependencies resolve the tenant before business logic runs.
5. No endpoints may accept a raw `organization_id` and use it without membership validation.

## Implementation

- `get_current_organization` validates the user is a member.
- `get_current_workspace` validates workspace membership inside the organization.
- `MembershipService.has_permission` checks organization-level RBAC.
- `MembershipService.has_workspace_permission` checks workspace-level RBAC.

## Cross-Tenant Prevention

- `select` filters by `organization_id`.
- `update`/`delete` also verify the resource belongs to the tenant.
- Admin endpoints use `get_current_admin` and do not leak tenant data without filtering.

## Caching, Logging, Search

- Cache keys should include `tenant:{org_id}`.
- Audit logs include `organization_id` and `workspace_id`.
- Search indexes must be scoped by `organization_id`.
- Background jobs must run with `tenant_context(org_id)`.
