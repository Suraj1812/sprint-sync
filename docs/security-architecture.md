# Security Architecture

## Principles

SprintSync is built with a defense-in-depth, zero-trust mindset:

- **Secure by default** — strong headers, rate limits, and least-privilege access out of the box.
- **Least privilege** — services and users only get the minimum permissions required.
- **Assume breach** — every layer (network, container, API, database) is independently hardened.
- **Privacy by design** — sensitive data is encrypted at rest and in transit; PII is minimized.

## Layers

### 1. Network

- TLS 1.2+ in production.
- HSTS and secure cookie flags.
- CORS origin and method allowlists.
- `TrustedHostMiddleware` in FastAPI.

### 2. Container

- Non-root `nextjs` and `appuser` accounts.
- Multi-stage builds.
- Minimal `python:3.13-slim` and `node:22-alpine` images.
- Read-only application files where possible.

### 3. Application

- **Frontend**: strict CSP with nonce, X-Frame-Options, Referrer-Policy, Permissions-Policy.
- **API**: rate limiting, input validation, parameterized SQLAlchemy queries, structured audit logs.
- **Authentication**: Argon2id, short-lived JWTs, refresh-token rotation, Redis revocation, account lockout.

### 4. Data

- PostgreSQL with least-privilege users.
- Encrypted backups and TLS in transit.
- Soft-delete audit fields.

## Secret Management

- Secrets are read from environment variables.
- `SECRET_KEY` is validated to be ≥ 32 characters.
- `.env` files are git-ignored; `.env.example` is committed as a template.
- Production should use a dedicated secret manager (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, 1Password, HashiCorp Vault).
