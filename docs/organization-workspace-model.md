# Organization and Workspace Model

## Organization

The top-level tenant. Owns billing, custom domains, custom roles, and members.

**Fields:**
- `name`, `slug` (unique)
- `owner_id`
- `suspended_at`
- `branding`
- `billing_email`
- `settings`

**Lifecycle:**
- Create → owner becomes `organization_members` with `owner`.
- Update → owner or admin.
- Transfer ownership → owner.
- Suspend / restore.
- Soft delete.

## Workspace

A project or team container inside an organization. Users can belong to multiple workspaces.

**Fields:**
- `organization_id`
- `name`, `slug`
- `is_archived`, `archived_at`
- `branding`
- `settings`

**Lifecycle:**
- Create → requires `workspace.create`.
- Archive / restore.
- Soft delete.

## Membership

`organization_members` and `workspace_members` link users to tenants with roles.

- Users can be in multiple organizations.
- Users can be in multiple workspaces.
- Workspace permissions fall back to organization permissions.
