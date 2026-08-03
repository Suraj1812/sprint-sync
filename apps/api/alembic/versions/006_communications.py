"""Communication and notification platform.

Revision ID: 006
Revises: 005
Create Date: 2025-01-25 00:00:00.000000
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("organization_id", sa.Uuid(as_uuid=True), sa.ForeignKey("organizations.id"), index=True, nullable=True),
        sa.Column("workspace_id", sa.Uuid(as_uuid=True), sa.ForeignKey("workspaces.id"), index=True, nullable=True),
        sa.Column("category", sa.String(length=50), index=True, nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default=sa.text("'normal'")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("deep_link", sa.String(length=500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_read", "notifications", ["user_id", "is_read"])

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("frequency", sa.String(length=20), nullable=True),
        sa.Column("digest", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("quiet_hours_start", sa.String(length=5), nullable=True),
        sa.Column("quiet_hours_end", sa.String(length=5), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=False, server_default=sa.text("'en'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "channel", "category"),
    )

    op.create_table(
        "email_templates",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), index=True, nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False, server_default=sa.text("'en'")),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("html_body", sa.Text(), nullable=True),
        sa.Column("text_body", sa.Text(), nullable=True),
        sa.Column("layout", sa.String(length=100), nullable=True),
        sa.Column("variables", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_templates_name_locale", "email_templates", ["name", "locale"])

    op.create_table(
        "communication_events",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), sa.ForeignKey("organizations.id"), index=True, nullable=True),
        sa.Column("event_type", sa.String(length=100), index=True, nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("next_retry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_communication_events_status", "communication_events", ["status"])

    op.create_table(
        "delivery_attempts",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("event_id", sa.Uuid(as_uuid=True), sa.ForeignKey("communication_events.id"), index=True, nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("response", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_delivery_attempts_event_id", "delivery_attempts", ["event_id"])

    op.create_table(
        "devices",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column("endpoint", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_devices_user_id", "devices", ["user_id"])

    # Seed templates
    op.bulk_insert(
        "email_templates",
        [
            {
                "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                "name": "welcome",
                "locale": "en",
                "version": 1,
                "subject": "Welcome to {{ app_name }}",
                "html_body": "<p>Hi {{ name }}, welcome to {{ app_name }}.</p>",
                "text_body": "Hi {{ name }}, welcome to {{ app_name }}.",
                "variables": ["name", "app_name"],
                "is_active": True,
                "created_at": "2025-01-25T00:00:00+00:00",
                "updated_at": "2025-01-25T00:00:00+00:00",
            },
            {
                "id": uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                "name": "password-reset",
                "locale": "en",
                "version": 1,
                "subject": "Reset your {{ app_name }} password",
                "html_body": "<p>Click <a href='{{ link }}'>here</a> to reset your password.</p>",
                "text_body": "Reset your password: {{ link }}",
                "variables": ["link", "app_name"],
                "is_active": True,
                "created_at": "2025-01-25T00:00:00+00:00",
                "updated_at": "2025-01-25T00:00:00+00:00",
            },
            {
                "id": uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
                "name": "invitation",
                "locale": "en",
                "version": 1,
                "subject": "You have been invited to {{ organization }}",
                "html_body": "<p>Join {{ organization }}: {{ link }}</p>",
                "text_body": "Join {{ organization }}: {{ link }}",
                "variables": ["organization", "link"],
                "is_active": True,
                "created_at": "2025-01-25T00:00:00+00:00",
                "updated_at": "2025-01-25T00:00:00+00:00",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("devices")
    op.drop_table("delivery_attempts")
    op.drop_table("communication_events")
    op.drop_table("email_templates")
    op.drop_table("notification_preferences")
    op.drop_table("notifications")
