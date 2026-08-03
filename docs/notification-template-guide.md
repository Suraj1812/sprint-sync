# Email Template Authoring Guide

## Storage

Templates are stored in `email_templates` with `name`, `locale`, `version`, `subject`, `html_body`, `text_body`, `variables`, and `layout`.

## Variables

Use `{{ variable_name }}` syntax. The renderer uses Python `string.Template.safe_substitute`, so missing variables are left unchanged.

Default context includes `{{ app_name }}`.

## Versioning

Create a new template with `version` incremented. The system selects the highest `version` for `(name, locale)` where `is_active` is true.

## Preview

Use `POST /api/v1/communications/admin/templates/preview` to render a template with sample variables.

## Built-in Templates

Seeded on migration:
- `welcome`
- `password-reset`
- `invitation`

## Localization

Set `locale` on the template and pass `locale` when rendering. Fallback is `en`.
