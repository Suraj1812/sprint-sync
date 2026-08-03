# Role-Based Access Control

## Default Roles

### Organization
- `owner` — wildcard.
- `admin` — manage org, members, workspaces, billing, audit.
- `member` — view and create workspaces.
- `guest` — view only.
- `auditor` — view audit and billing.

### Workspace
- `admin` — wildcard.
- `manager` — update, invite, manage members.
- `member` — view.
- `guest` — view.

## Custom Roles

`CustomRole` stores `name`, `description`, and `permissions` JSON array. If a user's `organization_members.role` is not in the default matrix, the system looks up `CustomRole` by name.

## Permission Format

`resource.action`, e.g. `workspace.create`, `organization.member.manage`. Wildcard `*` grants all.

## Extending

Add new resource actions to `ORG_PERMISSIONS` or `WS_PERMISSIONS`, or create `CustomRole` entries. Avoid hardcoding `if role == "admin"` in endpoint code.

## Checking

```python
if not await membership_service.has_permission(db, user.id, org.id, "workspace.create"):
    raise AuthorizationError("Cannot create workspace")
```
