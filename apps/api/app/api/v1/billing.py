"""Billing and subscription API v1."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user, get_db_session
from app.billing.providers.registry import payment_provider_registry
from app.billing.services.customer import customer_repository, customer_service
from app.billing.services.entitlement import entitlement_service
from app.billing.services.invoice import invoice_service
from app.billing.services.metrics import metrics_service
from app.billing.services.plan import plan_service
from app.billing.services.subscription import subscription_service
from app.billing.services.usage import usage_service
from app.billing.services.webhook import webhook_service
from app.models.user import User
from app.models.billing import Subscription, UsageRecord
from app.schemas.billing import (
    BillingMetrics,
    ChangePlanRequest,
    CheckoutRequest,
    CheckoutResponse,
    CustomerRead,
    EntitlementRead,
    InvoiceRead,
    PlanRead,
    PortalRequest,
    SubscriptionRead,
    UsageRecordRead,
    UsageRecordRequest,
)
from app.schemas.common import APIResponse

billing_router = APIRouter(prefix="/billing", tags=["billing"])


@billing_router.get("/plans", response_model=list[PlanRead])
async def list_plans(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await plan_service.list(db)


@billing_router.get("/plans/{plan_id}", response_model=PlanRead)
async def get_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    plan = await plan_service.get(db, plan_id)
    return plan


@billing_router.get("/plans/{plan_id}/entitlements", response_model=list[EntitlementRead])
async def plan_entitlements(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await plan_service.entitlements(db, plan_id)


@billing_router.get("/customer", response_model=CustomerRead)
async def get_customer(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    customer = await customer_service.get_for_user(db, user)
    if not customer:
        customer = await customer_service.get_or_create(db, user)
    return customer


@billing_router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    data: CheckoutRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> CheckoutResponse:
    session = await subscription_service.create(
        db,
        user,
        data.price_id,
        data.provider,
        success_url=data.success_url,
        cancel_url=data.cancel_url,
    )
    return CheckoutResponse(
        url=session.get("url", ""),
        session_id=session.get("id"),
    )


@billing_router.post("/portal", response_model=CheckoutResponse)
async def create_portal(
    data: PortalRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> CheckoutResponse:
    customer = await customer_service.get_or_create(db, user)
    provider = payment_provider_registry.get(customer.provider)
    session = await provider.create_portal_session(
        customer.provider_customer_id or str(customer.id),
        return_url=data.return_url,
    )
    return CheckoutResponse(url=session.get("url", ""), session_id=session.get("id"))


@billing_router.get("/subscriptions", response_model=list[SubscriptionRead])
async def list_subscriptions(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await subscription_service.list_for_user(db, user)


@billing_router.post("/subscriptions/{subscription_id}/cancel", response_model=SubscriptionRead)
async def cancel_subscription(
    subscription_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    return await subscription_service.cancel(db, user, subscription_id)


@billing_router.post(
    "/subscriptions/{subscription_id}/change",
    response_model=SubscriptionRead,
)
async def change_subscription(
    subscription_id: uuid.UUID,
    data: ChangePlanRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    return await subscription_service.change_plan(db, user, subscription_id, data.new_price_id)


@billing_router.get("/invoices", response_model=list[InvoiceRead])
async def list_invoices(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    customer = await customer_service.get_for_user(db, user)
    if not customer:
        return []
    return await invoice_service.list_for_user(db, customer)


@billing_router.get("/entitlements", response_model=list[EntitlementRead])
async def get_entitlements(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await entitlement_service.for_user(db, user)


@billing_router.post("/usage", response_model=UsageRecordRead)
async def record_usage(
    data: UsageRecordRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    customer = await customer_service.get_or_create(db, user)
    record = await usage_service.record(
        db,
        customer_id=customer.id,
        metric=data.metric,
        quantity=data.quantity,
    )
    return record


@billing_router.get("/usage", response_model=list[UsageRecordRead])
async def get_usage(
    metric: str | None = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    customer = await customer_service.get_for_user(db, user)
    if not customer:
        return []
    from datetime import datetime, timedelta, timezone

    since = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = select(UsageRecord).where(
        UsageRecord.customer_id == customer.id,
        UsageRecord.recorded_at >= since,
    )
    if metric:
        stmt = stmt.where(UsageRecord.metric == metric)
    result = await db.execute(stmt)
    return result.scalars().all()


@billing_router.post("/webhooks/{provider}")
async def receive_webhook(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    payload = await request.body()
    signature = (
        request.headers.get("Stripe-Signature")
        or request.headers.get("Paddle-Signature")
        or request.headers.get("X-Razorpay-Signature")
        or ""
    )
    ok = await webhook_service.receive(db, provider, payload, signature)
    if not ok:
        return APIResponse(
            success=False,
            message="Invalid webhook signature",
        )
    return APIResponse(message="Webhook processed")


@billing_router.get("/admin/metrics", response_model=BillingMetrics)
async def admin_metrics(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> BillingMetrics:
    stats = await metrics_service.dashboard(db)
    return BillingMetrics(**stats)


@billing_router.get("/admin/subscriptions", response_model=list[SubscriptionRead])
async def admin_subscriptions(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    from sqlalchemy import select
    result = await db.execute(select(Subscription))
    return result.scalars().all()


@billing_router.get("/admin/invoices", response_model=list[InvoiceRead])
async def admin_invoices(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    from sqlalchemy import select
    result = await db.execute(select(Invoice))
    return result.scalars().all()


@billing_router.get("/admin/events", response_model=list[dict])
async def admin_billing_events(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    from sqlalchemy import select
    from app.models.billing import BillingEvent
    result = await db.execute(select(BillingEvent).order_by(BillingEvent.created_at.desc()).limit(100))
    return result.scalars().all()
