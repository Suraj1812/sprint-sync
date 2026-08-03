"""Billing webhook processing."""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.providers.registry import payment_provider_registry
from app.billing.services.customer import customer_repository
from app.billing.services.invoice import invoice_service, payment_service
from app.billing.services.subscription import subscription_service
from app.core.logging import get_logger
from app.models.billing import BillingEvent, Customer

logger = get_logger("billing.webhook")


class BillingEventRepository:
    async def get_by_provider_event(
        self,
        db: AsyncSession,
        provider: str,
        event_id: str,
    ) -> BillingEvent | None:
        stmt = (
            select(BillingEvent)
            .where(
                BillingEvent.provider == provider,
                BillingEvent.provider_event_id == event_id,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        event: BillingEvent,
    ) -> BillingEvent:
        db.add(event)
        await db.flush()
        await db.refresh(event)
        return event


billing_event_repository = BillingEventRepository()


class WebhookService:
    async def receive(
        self,
        db: AsyncSession,
        provider_name: str,
        payload: bytes,
        signature: str,
    ) -> bool:
        provider = payment_provider_registry.get(provider_name)
        if not provider.verify_signature(payload, signature):
            logger.warning("Webhook signature verification failed", provider=provider_name)
            return False

        data = json.loads(payload)
        event_id = data.get("id")

        event = await billing_event_repository.get_by_provider_event(
            db, provider_name, event_id
        )
        if event:
            if event.processed:
                return True
            event.attempts += 1
        else:
            event = await billing_event_repository.create(
                db,
                BillingEvent(
                    provider=provider_name,
                    event_type=data.get("type", ""),
                    provider_event_id=event_id,
                    payload=data,
                    signature=signature,
                    attempts=1,
                ),
            )

        try:
            await self._process(db, provider_name, data)
            event.processed = True
            await db.flush()
        except Exception as exc:
            event.error = str(exc)
            await db.flush()
            raise
        return True

    async def _process(
        self,
        db: AsyncSession,
        provider_name: str,
        data: dict,
    ) -> None:
        event_type = data.get("type", "")
        object_data = data.get("data", {}).get("object", {})

        if event_type.startswith("customer.") and not event_type.startswith("customer.subscription"):
            return

        customer = await self._resolve_customer(db, object_data)

        if event_type == "checkout.session.completed":
            checkout_id = object_data.get("id")
            sub = await subscription_service.get_by_provider_id(db, checkout_id)
            if sub:
                sub.provider_subscription_id = object_data.get("subscription") or checkout_id
                await db.flush()
                await subscription_service.update_from_provider_event(
                    db,
                    sub.id,
                    "active",
                    object_data,
                )

        elif event_type == "invoice.payment_succeeded" and customer:
            await invoice_service.from_webhook(db, customer, object_data)

        elif event_type in ("invoice.payment_failed", "payment_intent.payment_failed") and customer:
            await payment_service.from_webhook(db, customer, object_data)

        elif event_type == "customer.subscription.deleted":
            sub = await subscription_service.get_by_provider_id(db, object_data.get("id"))
            if sub:
                await subscription_service.update_from_provider_event(
                    db,
                    sub.id,
                    "canceled",
                    object_data,
                )

        elif event_type == "customer.subscription.updated":
            sub = await subscription_service.get_by_provider_id(db, object_data.get("id"))
            if sub:
                await subscription_service.update_from_provider_event(
                    db,
                    sub.id,
                    object_data.get("status", "active"),
                    object_data,
                )

    async def _resolve_customer(
        self,
        db: AsyncSession,
        object_data: dict,
    ) -> Customer | None:
        customer_id = object_data.get("customer")
        if not customer_id:
            return None

        stmt = select(Customer).where(Customer.provider_customer_id == customer_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


webhook_service = WebhookService()
