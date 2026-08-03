# ADR-002: Identity and Access Architecture

## Status

Accepted

## Context

SprintSync requires secure, scalable authentication that satisfies enterprise non-functional requirements:

- short-lived access tokens
- rotated, single-use refresh tokens
- role-based access control
- rate-limited authentication endpoints
- testable, stateless dependency injection
- no duplicate security logic

## Decision

- Implement the identity domain with a `User` SQLAlchemy model, `IUserRepository` / `SQLUserRepository`, `TokenService`, and `AuthService`.
- Hash passwords with Argon2id; never return the password hash in any DTO.
- Issue JWT access tokens (15-minute TTL) and opaque, hashed, single-use refresh tokens stored in Redis (7-day TTL).
- Validate tokens in FastAPI dependencies and map errors to HTTP 401/403.
- Add `slowapi` rate limits on `register` (5/min) and `login` (10/min).
- Expose versioned routes at `/api/v1/auth`.
- Implement the Next.js 15 login and register pages as client components that submit to Server Actions, which set HTTP-only, `SameSite=Lax` cookies and redirect to the dashboard.
- Gate client-side routes with `middleware.ts` using the access-token cookie presence.

## Consequences

- The service layer can be unit-tested without a database or HTTP server.
- Refresh-token rotation limits the window for token replay.
- FastAPI dependencies provide a clean, reusable `get_current_user` and `require_role` mechanism.
- Server Actions keep credential handling on the server and avoid exposing tokens to client JavaScript.
- The middleware performs a lightweight presence check; actual token validation is performed by the backend.
