"""Billing and subscription models."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Numeric as SQLDecimal,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Plan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_enterprise: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)
    prices: Mapped[list["Price"]] = relationship(
        "Price",
        order_by="Price.created_at",
        back_populates="plan",
    )
    entitlements: Mapped[list["Entitlement"]] = relationship(
        "Entitlement",
        back_populates="plan",
    )


class Price(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "prices"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plans.id"),
        index=True,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), default="stripe", nullable=False)
    provider_price_id: Mapped[str | None] = mapped_column(String(255))
    billing_interval: Mapped[str] = mapped_column(
        String(20),
        default="month",
        nullable=False,
    )  # month, year, one_time, usage
    amount: Mapped[Decimal] = mapped_column(
        SQLDecimal(precision=10, scale=2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    usage_type: Mapped[str | None] = mapped_column(String(50))  # seat, token, api_call, storage
    trial_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="prices")


class Customer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customers"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        unique=True,
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(50), default="stripe", nullable=False)
    provider_customer_id: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(100))
    billing_address: Mapped[dict | None] = mapped_column(JSON)
    payment_provider: Mapped[str] = mapped_column(String(50), default="stripe", nullable=False)
    default_payment_method_id: Mapped[str | None] = mapped_column(String(255))
    balance: Mapped[Decimal] = mapped_column(
        SQLDecimal(precision=10, scale=2),
        default=Decimal("0.00"),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Subscription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=False,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plans.id"),
        index=True,
        nullable=False,
    )
    price_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prices.id"),
        index=True,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), default="stripe", nullable=False)
    provider_subscription_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(20),
        default="incomplete",
        nullable=False,
    )  # incomplete, active, trialing, past_due, canceled, paused
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trial_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    seats: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)


class Invoice(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "invoices"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=False,
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subscriptions.id"),
        index=True,
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(50), default="stripe", nullable=False)
    provider_invoice_id: Mapped[str | None] = mapped_column(String(255))
    number: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        nullable=False,
    )  # draft, open, paid, uncollectible, void, refunded
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(
        SQLDecimal(precision=10, scale=2),
        default=Decimal("0.00"),
        nullable=False,
    )
    tax: Mapped[Decimal] = mapped_column(
        SQLDecimal(precision=10, scale=2),
        default=Decimal("0.00"),
        nullable=False,
    )
    total: Mapped[Decimal] = mapped_column(
        SQLDecimal(precision=10, scale=2),
        default=Decimal("0.00"),
        nullable=False,
    )
    paid: Mapped[Decimal] = mapped_column(
        SQLDecimal(precision=10, scale=2),
        default=Decimal("0.00"),
        nullable=False,
    )
    pdf_url: Mapped[str | None] = mapped_column(String(500))
    record_metadata: Mapped[dict | None] = mapped_column(JSON)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=False,
    )
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("invoices.id"),
        index=True,
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(50), default="stripe", nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(
        SQLDecimal(precision=10, scale=2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    failure_message: Mapped[str | None] = mapped_column(Text)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)


class UsageRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "usage_records"

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=True,
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subscriptions.id"),
        index=True,
        nullable=True,
    )
    metric: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)


class Entitlement(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "entitlements"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plans.id"),
        index=True,
        nullable=False,
    )
    feature: Mapped[str] = mapped_column(String(100), nullable=False)
    limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    record_metadata: Mapped[dict | None] = mapped_column(JSON)
    plan: Mapped["Plan"] = relationship("Plan", back_populates="entitlements")


class BillingEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "billing_events"

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_event_id: Mapped[str | None] = mapped_column(String(255))
    payload: Mapped[dict | None] = mapped_column(JSON)
    signature: Mapped[str | None] = mapped_column(Text)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
