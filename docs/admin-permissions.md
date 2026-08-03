# Admin Permission Model

## Roles

- `super_admin` — full platform access (`*`).
- `platform_admin` — users, orgs, flags, settings, audit logs.
- `support` — read and limited user metadata updates.
- `operations` — flags and settings.
- `billing` — billing and audit logs.
- `auditor` — read-only across the platform.

## Permissions

Permissions are resource-action strings. Examples:

- `read` — read any resource.
- `write:users` — create, update, suspend users.
- `write:users:metadata` — update only non-sensitive user fields.
- `write:orgs` — manage organizations.
- `write:flags` — manage feature flags.
- `write:settings` — update system settings.
- `read:audit` — view audit logs.
- `write:billing` — billing operations.

## Enforcement

- `require_admin` checks that the user has an admin role.
- `require_permission(permission)` checks the role's permission list for the specific string or `*`.
- All admin endpoints are protected with one of these dependencies.
