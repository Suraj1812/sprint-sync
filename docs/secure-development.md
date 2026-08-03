# Secure Development Guidelines

## Secrets

- Never commit `.env`, keys, or certificates.
- Use `SECRET_KEY` from environment variables only.
- Rotate secrets quarterly and on employee/offboarding.
- Use a secrets manager in production.

## Authentication & Authorization

- Always validate user identity in dependencies, not inside services.
- Use `require_admin` or permission checks for admin routes.
- Never return password hashes or tokens in `UserRead`.

## Input

- Validate all request payloads with Pydantic.
- Escape output where user content is rendered.
- Never trust client-provided IDs; validate ownership.

## Logging

- Log security events: logins, failed logins, permission denials, admin actions.
- Never log passwords, tokens, or full request bodies.
- Use correlation IDs for traceability.

## Dependencies

- Pin versions in `pyproject.toml` and `package.json`.
- Run `pnpm audit` and `pip-audit` before merging.
- Review CI security job results.

## Review

- All code must pass static analysis (Ruff, ESLint, mypy) and security scans.
- Treat security review as a non-negotiable part of every PR.
