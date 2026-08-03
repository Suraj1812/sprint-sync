"""Billing platform tables.

Revision ID: 004
Revises: 003
Create Date: 2025-01-23 00:00:00.000000
"""

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone
from decimal import Decimal

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_enterprise", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_plans_name", "plans", ["name"])

    op.create_table(
        "prices",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("plan_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default=sa.text("'stripe'")),
        sa.Column("provider_price_id", sa.String(length=255), nullable=True),
        sa.Column("billing_interval", sa.String(length=20), nullable=False, server_default=sa.text("'month'")),
        sa.Column("amount", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'usd'")),
        sa.Column("usage_type", sa.String(length=50), nullable=True),
        sa.Column("trial_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
    )
    op.create_index("ix_prices_plan_id", "prices", ["plan_id"])

    op.create_table(
        "entitlements",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("plan_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("feature", sa.String(length=100), nullable=False),
        sa.Column("limit", sa.Integer(), nullable=True),
        sa.Column("value", sa.String(length=255), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
    )
    op.create_index("ix_entitlements_plan_id", "entitlements", ["plan_id"])

    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default=sa.text("'stripe'")),
        sa.Column("provider_customer_id", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("tax_id", sa.String(length=100), nullable=True),
        sa.Column("billing_address", sa.JSON(), nullable=True),
        sa.Column("payment_provider", sa.String(length=50), nullable=False, server_default=sa.text("'stripe'")),
        sa.Column("default_payment_method_id", sa.String(length=255), nullable=True),
        sa.Column("balance", sa.DECIMAL(precision=10, scale=2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_customers_user_id", "customers", ["user_id"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("plan_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("price_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default=sa.text("'stripe'")),
        sa.Column("provider_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'incomplete'")),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("seats", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
        sa.ForeignKeyConstraint(["price_id"], ["prices.id"]),
    )
    op.create_index("ix_subscriptions_customer_id", "subscriptions", ["customer_id"])
    op.create_index("ix_subscriptions_plan_id", "subscriptions", ["plan_id"])
    op.create_index("ix_subscriptions_price_id", "subscriptions", ["price_id"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("subscription_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default=sa.text("'stripe'")),
        sa.Column("provider_invoice_id", sa.String(length=255), nullable=True),
        sa.Column("number", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'usd'")),
        sa.Column("subtotal", sa.DECIMAL(precision=10, scale=2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("tax", sa.DECIMAL(precision=10, scale=2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("total", sa.DECIMAL(precision=10, scale=2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("paid", sa.DECIMAL(precision=10, scale=2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("pdf_url", sa.String(length=500), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"]),
    )
    op.create_index("ix_invoices_customer_id", "invoices", ["customer_id"])
    op.create_index("ix_invoices_subscription_id", "invoices", ["subscription_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("invoice_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default=sa.text("'stripe'")),
        sa.Column("provider_payment_id", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'usd'")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
    )
    op.create_index("ix_payments_customer_id", "payments", ["customer_id"])
    op.create_index("ix_payments_invoice_id", "payments", ["invoice_id"])

    op.create_table(
        "usage_records",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("subscription_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("metric", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"]),
    )
    op.create_index("ix_usage_records_customer_id", "usage_records", ["customer_id"])
    op.create_index("ix_usage_records_subscription_id", "usage_records", ["subscription_id"])
    op.create_index("ix_usage_records_recorded_at", "usage_records", ["recorded_at"])

    op.create_table(
        "billing_events",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("provider_event_id", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
    )
    op.create_index("ix_billing_events_customer_id", "billing_events", ["customer_id"])
    op.create_index("ix_billing_events_provider_event_id", "billing_events", ["provider_event_id"])

    op.bulk_insert(
        sa.table(
            "plans",
            sa.column("id", sa.Uuid(as_uuid=True)),
            sa.column("name", sa.String(length=100)),
            sa.column("description", sa.Text()),
            sa.column("is_active", sa.Boolean()),
            sa.column("is_enterprise", sa.Boolean()),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
                "name": "free",
                "description": "Free forever plan",
                "is_active": True,
                "is_enterprise": False,
                "created_at": datetime(2025, 1, 23, tzinfo=timezone.utc),
                "updated_at": datetime(2025, 1, 23, tzinfo=timezone.utc),
            },
            {
                "id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
                "name": "pro",
                "description": "Pro monthly subscription",
                "is_active": True,
                "is_enterprise": False,
                "created_at": datetime(2025, 1, 23, tzinfo=timezone.utc),
                "updated_at": datetime(2025, 1, 23, tzinfo=timezone.utc),
            },
        ],
    )

    op.bulk_insert(
        sa.table(
            "entitlements",
            sa.column("id", sa.Uuid(as_uuid=True)),
            sa.column("plan_id", sa.Uuid(as_uuid=True)),
            sa.column("feature", sa.String(length=100)),
            sa.column("limit", sa.Integer()),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
                "plan_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
                "feature": "ai_tokens",
                "limit": 10000,
                "created_at": datetime(2025, 1, 23, tzinfo=timezone.utc),
                "updated_at": datetime(2025, 1, 23, tzinfo=timezone.utc),
            },
            {
                "id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
                "plan_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
                "feature": "ai_tokens",
                "limit": 100000,
                "created_at": datetime(2025, 1, 23, tzinfo=timezone.utc),
                "updated_at": datetime(2025, 1, 23, tzinfo=timezone.utc),
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("billing_events")
    op.drop_table("usage_records")
    op.drop_table("payments")
    op.drop_table("invoices")
    op.drop_table("subscriptions")
    op.drop_table("customers")
    op.drop_table("entitlements")
    op.drop_table("prices")
    op.drop_table("plans")
