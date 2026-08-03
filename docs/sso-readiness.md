# SSO and Enterprise Identity Readiness

## Interfaces

Design should support:

- **SAML 2.0** — `IdentityProvider` model for metadata, ACS, and SP-initiated login.
- **OAuth 2.0 / OIDC** — `SSOConnection` model for client_id, client_secret, discovery URL.
- **SCIM provisioning** — `SCIMUser`/`SCIMGroup` endpoints and push events.

## Extensible Provider Pattern

Following the billing and AI provider abstractions:

```
app/enterprise/providers/base.py    → SSOProvider
app/enterprise/providers/saml.py    → SAMLProvider
app/enterprise/providers/oidc.py    → OIDCProvider
app/enterprise/providers/scim.py    → SCIMProvider
```

## Current State

The `CustomDomain` model and organization-level settings are ready. Add `SSOConnection` when implementing a provider.

## Security

- Force SAML for an organization.
- JIT provisioning for invited domains.
- SCIM deactivation must suspend `organization_members`.
- Map IdP groups to `CustomRole`.
