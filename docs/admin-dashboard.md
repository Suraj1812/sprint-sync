# Admin Dashboard

## Layout

The admin dashboard uses a fixed top navigation with global search and notifications, plus a collapsible sidebar for navigation. The main content area is responsive and keyboard-accessible.

## Pages

- `/admin` — dashboard with KPI cards.
- `/admin/users` — user search, suspend/activate, reset password.
- `/admin/organizations` — create and manage organizations.
- `/admin/feature-flags` — create, enable, disable, and roll out flags.
- `/admin/audit` — searchable activity log.
- `/admin/system` — maintenance mode and toggles.

## Widgets

- Total / active users.
- 24-hour new registrations and failed logins.
- Active admin sessions.
- Pending feature flags.
- Uptime and deployment version.

## Accessibility

- `aria-label` on navigation, tables, and controls.
- Skip to main content already provided by the root layout.
- `aria-current="page"` on active sidebar links.
