"""Pydantic schemas for billing."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    is_active: bool
    is_enterprise: bool


class PriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_id: UUID
    provider: str
    provider_price_id: str | None
    billing_interval: str
    amount: Decimal
    currency: str
    usage_type: str | None
    trial_days: int
    is_active: bool


class EntitlementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_id: UUID
    feature: str
    limit: int | None
    value: str | None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    provider_customer_id: str | None
    email: str
    tax_id: str | None
    balance: Decimal
    payment_provider: str


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    plan_id: UUID
    price_id: UUID
    provider: str
    status: str
    current_period_start: datetime | None
    current_period_end: datetime | None
    trial_start: datetime | None
    trial_end: datetime | None
    seats: int


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    subscription_id: UUID | None
    status: str
    number: str | None
    currency: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    paid: Decimal
    pdf_url: str | None
    due_at: datetime | None
    created_at: datetime


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    invoice_id: UUID | None
    amount: Decimal
    currency: str
    status: str
    failure_message: str | None


class UsageRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    metric: str
    quantity: int
    recorded_at: datetime


class CheckoutRequest(BaseModel):
    price_id: UUID
    provider: str | None = None
    success_url: str = Field(default="http://localhost:3000/billing/success")
    cancel_url: str = Field(default="http://localhost:3000/billing/cancel")


class CheckoutResponse(BaseModel):
    url: str
    session_id: str | None = None


class PortalRequest(BaseModel):
    return_url: str = Field(default="http://localhost:3000/billing")


class ChangePlanRequest(BaseModel):
    new_price_id: UUID


class UsageRecordRequest(BaseModel):
    metric: str = Field(..., min_length=1, max_length=50)
    quantity: int = Field(..., ge=0)


class WebhookPayload(BaseModel):
    event: str
    data: dict


class BillingMetrics(BaseModel):
    mrr: float
    arr: float
    active_subscriptions: int
    failed_payments_30d: int
