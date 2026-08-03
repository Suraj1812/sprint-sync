# Security Checklist

## Before shipping

- [ ] `SECRET_KEY` is at least 32 random characters and unique per environment.
- [ ] `HSTS_ENABLED=true` in production.
- [ ] `ALLOWED_HOSTS` is restricted to real domains.
- [ ] `CORS_ORIGINS` does not include `*` in production.
- [ ] Database uses a least-privilege user (not `postgres`).
- [ ] Redis is password-protected and networked only to internal services.
- [ ] TLS certificates are configured and auto-renewed.
- [ ] Container images run as non-root.
- [ ] Audit logs are shipped to a SIEM.
- [ ] `.env` files are not committed.
- [ ] Dependency scans and secret scans are passing in CI.

## Coding

- [ ] No `dangerouslySetInnerHTML` except for sanitized, static JSON.
- [ ] No raw SQL or string concatenation in queries.
- [ ] No hardcoded credentials.
- [ ] Rate limits on mutation and auth endpoints.
- [ ] Audit logging for security-sensitive events.
- [ ] Input validated at the API boundary and again in the service layer.
