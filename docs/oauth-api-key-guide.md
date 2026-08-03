# OAuth and API Key Guide

## API Keys

- Prefix: `ssk_`.
- Stored as SHA-256 hashes; preview is the last 10 characters.
- The full key is returned only on creation.
- Scopes support `*` wildcard.
- Expiration and revocation supported.
- Usage count and last-used tracked.

## OAuth 2.0

Supports a minimal Authorization Code flow:

1. `POST /api/v1/automation/oauth/clients` to register.
2. `POST /api/v1/automation/oauth/authorize` with `client_id`, `redirect_uri`, `scope`, `code_challenge`.
3. `POST /api/v1/automation/oauth/token` with `code`, `client_secret`, `redirect_uri`.

PKCE support via `code_challenge`/`code_verifier`.

## Security

- Client secrets are SHA-256 hashed.
- Authorization codes expire in 10 minutes and are single-use.
- Tokens expire in 1 hour by default.
- Always use HTTPS in production.
