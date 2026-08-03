"""Outgoing webhook service."""

import hmac
import hashlib
import json
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.automation import WebhookDelivery, WebhookSubscription
from app.repositories.base import BaseRepository
from app.services.audit_log import audit_log_service


class WebhookSubscriptionRepository(BaseRepository[WebhookSubscription]):
    def __init__(self) -> None:
        super().__init__(WebhookSubscription)

    async def list_active(
        self,
        db: AsyncSession,
        event_type: str,
        tenant_id: uuid.UUID | None = None,
    ) -> list[WebhookSubscription]:
        stmt = select(WebhookSubscription).where(
            WebhookSubscription.is_active.is_(True),
        )
        if tenant_id:
            stmt = stmt.where(WebhookSubscription.tenant_id == tenant_id)
        result = await db.execute(stmt)
        subs = result.scalars().all()
        return [s for s in subs if event_type in (s.events or [])]


webhook_subscription_repository = WebhookSubscriptionRepository()


class WebhookService:
    async def create(
        self,
        db: AsyncSession,
        *,
        name: str,
        url: str,
        events: list[str],
        tenant_id: uuid.UUID | None = None,
    ) -> tuple[WebhookSubscription, str]:
        secret = "whsec_" + secrets.token_urlsafe(32)
        sub = WebhookSubscription(
            tenant_id=tenant_id,
            name=name,
            url=url,
            events=events,
            secret=secret,
        )
        db.add(sub)
        await db.flush()
        await db.refresh(sub)
        return sub, secret

    async def deliver(
        self,
        db: AsyncSession,
        event: Any,  # DomainEvent
    ) -> None:
        subs = await webhook_subscription_repository.list_active(
            db,
            event.event_type,
            tenant_id=event.tenant_id,
        )
        for sub in subs:
            await self._send(db, sub, event)

    async def _send(
        self,
        db: AsyncSession,
        sub: WebhookSubscription,
        event: Any,
    ) -> None:
        payload = {
            "event_type": event.event_type,
            "id": str(event.id),
            "tenant_id": str(event.tenant_id) if event.tenant_id else None,
            "correlation_id": event.correlation_id,
            "payload": event.payload,
            "occurred_at": event.created_at.isoformat() if event.created_at else None,
        }
        body = json.dumps(payload, default=str).encode()
        signature = hmac.new(
            sub.secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()

        delivery = WebhookDelivery(
            subscription_id=sub.id,
            event_id=event.id,
            status="sent",
            signature=signature,
        )
        db.add(delivery)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    sub.url,
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event.event_type,
                    },
                )
            delivery.response_status = response.status_code
            delivery.response_body = response.text[:2000]
            if 200 <= response.status_code < 300:
                delivery.status = "delivered"
                sub.failure_count = 0
                sub.last_delivery_at = datetime.now(timezone.utc)
            else:
                delivery.status = "failed"
                sub.failure_count += 1
        except Exception as exc:
            delivery.status = "failed"
            delivery.error = str(exc)[:2000]
            sub.failure_count += 1

        if sub.failure_count >= 5:
            sub.is_active = False

        await db.flush()

    async def list_deliveries(
        self,
        db: AsyncSession,
        sub_id: uuid.UUID,
    ) -> list[WebhookDelivery]:
        stmt = select(WebhookDelivery).where(WebhookDelivery.subscription_id == sub_id)
        stmt = stmt.order_by(WebhookDelivery.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()


webhook_service = WebhookService()
