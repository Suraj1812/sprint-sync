# Invitation Guide

## Flow

1. An `owner` or `admin` calls `POST /api/v1/tenancy/invitations`.
2. A secure token is generated and an email is queued (email delivery not yet implemented).
3. The invitee calls `POST /tenancy/invitations/{token}/accept`.
4. On acceptance, `organization_members` (and optionally `workspace_members`) rows are created.
5. Audit logs capture the invitation and acceptance.

## Approval Workflow

Set `auto_approve=False` to require admin approval. `is_approved` must be `True` before `accept` succeeds.

## Security

- Tokens are 32-byte URL-safe secrets.
- Invitations expire in 7 days by default.
- Resending creates a new token and resets expiry.
- Used or rejected invitations cannot be re-used.

## Bulk Invitations

Loop over `POST /tenancy/invitations` with the desired list. Future batch endpoint can wrap the same service.
