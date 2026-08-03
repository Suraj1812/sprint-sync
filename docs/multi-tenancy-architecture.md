# Multi-Tenancy Architecture

## Strategy

**Shared database, shared schema, row-level tenant isolation** is the default. PostgreSQL `organization_id` (and `workspace_id`) columns gate every tenant-scoped query.

## Trade-offs

| Approach | Pros | Cons |
|---|---|---|
| Shared DB / shared schema | Simplest operations, cheapest scaling, easy backups, simplest migrations | Risk of cross-tenant bugs, noisy neighbors, harder per-tenant tuning |
| Shared DB / per-tenant schema | Better data isolation, easier tenant-level dumps | Complex migrations, connection pooling challenges |
| Per-tenant DB | Strongest isolation, per-tenant scaling | Operational overhead, cost, slower onboarding |
| Per-tenant schema + shard | Best of isolation and scale | Maximum complexity |

## Recommendation

Start with **shared schema**. When an enterprise customer requires physical isolation, migrate them to a dedicated database or schema with an ETL path. This mirrors Notion, Figma, and Vercel.

## Tenant Context

`app/tenancy/context.py` provides a `ContextVar` for `tenant_id`. Services can read it to enforce filters, or dependencies can inject the `Organization` into endpoints.

## Request Resolution

1. `X-Organization-Id` header.
2. `organization_id` cookie.
3. User's first active membership.

`get_current_organization` rejects suspended, deleted, or non-member organizations.

## Tenant-Aware Services

Every service that touches tenant data receives the resolved `Organization` or `Workspace` and explicitly filters by `organization_id` / `workspace_id`. No global queries.
