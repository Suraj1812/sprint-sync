# Admin Platform Architecture

## Goals

The internal admin platform gives operators, support, and platform administrators a secure, single-pane view to manage users, organizations, feature flags, audit logs, and system configuration.

## Architecture

- **Frontend**: `apps/web/app/admin` is a sub-application of the marketing Next.js app. It reuses `@sprint-sync/ui`, the design system, and the same CSP/security middleware.
- **Backend**: `app/api/v1/admin` is a dedicated FastAPI sub-router with its own dependencies, schemas, services, repositories, and models.
- **Authentication**: Admin sessions are short-lived JWTs (8 hours) with `HttpOnly` cookies. They are tracked in the `admin_sessions` table for revocation and login history.
- **Authorization**: Fine-grained RBAC using the existing `Role` model. Each admin role has an explicit permission list.
- **Audit**: Every admin action, login, and flag change is persisted to the `audit_logs` table.
- **Data**: `organizations`, `feature_flags`, and `audit_logs` live alongside `users` and `roles` in PostgreSQL.

## Security

- Admin endpoints require both a valid JWT and an active database session.
- Failed admin login attempts are rate-limited and tracked.
- Sessions can be listed and revoked individually.
- `HttpOnly`, `Secure` (production), `SameSite=Lax` cookies.
