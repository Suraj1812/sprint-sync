# Audit Logging

## Events

The `audit_logs` table records:

- `admin_login` / `admin_logout`
- `admin_session_revoke`
- `admin_user_update`
- `admin_password_reset`
- `feature_flag_create` / `feature_flag_update` / `feature_flag_delete`
- `organization_create` / `organization_update`
- `login_attempt` (all user logins, success and failure)

## Fields

- `actor_id` / `actor_email`
- `action`
- `resource` / `resource_id`
- `ip_address`
- `user_agent`
- `details` (JSON)
- `created_at`

## Retention

Recommended production retention: 90 days in PostgreSQL, then archive to cold storage (S3/ClickHouse) and retain for one year.
