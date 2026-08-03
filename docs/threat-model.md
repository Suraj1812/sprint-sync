# Threat Model

## Assets

- User credentials and tokens.
- PII (email, names).
- Workspaces, projects, tasks (future business data).
- Infrastructure secrets.

## Threats and Mitigations

| Threat | Mitigation |
|--------|------------|
| XSS | Strict CSP with nonce, `X-Content-Type-Options`, typed React components, `dangerouslySetInnerHTML` only for static JSON-LD. |
| CSRF | JWT in `Authorization` header, `SameSite` cookies, CORS allowlist. |
| SQL Injection | SQLAlchemy ORM with parameterized queries; no raw SQL. |
| Broken Authentication | Argon2id, account lockout, refresh-token rotation, token revocation in Redis. |
| Sensitive Data Exposure | TLS, HSTS, `Referrer-Policy`, no passwords/tokens in logs. |
| IDOR | Service-layer authorization checks, RBAC, UUIDs instead of sequential IDs. |
| Brute-force | SlowAPI rate limits on auth endpoints; account lockout via Redis. |
| SSRF | Input validation; no open redirects or outbound URL from user input. |
| Container Escape | Non-root users, minimal images, no `sudo`. |

## Trust Boundaries

- Untrusted client → Next.js middleware → FastAPI API → Database/Redis/Celery.
- Each boundary validates and sanitizes input before passing it downstream.
