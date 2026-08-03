"""Email delivery service."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.communications.providers.base import DeliveryResult, EmailMessage
from app.communications.providers.registry import email_provider_registry
from app.services.audit_log import audit_log_service


class EmailService:
    async def send(
        self,
        db: AsyncSession,
        *,
        to: str,
        subject: str,
        html: str | None = None,
        text: str | None = None,
        from_address: str | None = None,
        tenant_id: uuid.UUID | None = None,
        metadata: dict | None = None,
    ) -> DeliveryResult:
        provider = email_provider_registry.default()
        message = EmailMessage(
            to=to,
            subject=subject,
            html=html,
            text=text,
            from_address=from_address,
            metadata=metadata,
        )
        result = await provider.send(message)

        await audit_log_service.log(
            db,
            "communication.email.sent",
            "delivery",
            organization_id=tenant_id,
            resource_id=to,
            details={
                "to": to,
                "subject": subject,
                "provider": provider.name,
                "success": result.success,
                "status": result.status,
            },
        )
        return result

    async def send_template(
        self,
        db: AsyncSession,
        *,
        to: str,
        template_name: str,
        variables: dict[str, Any],
        tenant_id: uuid.UUID | None = None,
        from_address: str | None = None,
        locale: str = "en",
    ) -> DeliveryResult:
        from app.communications.services.template import template_service

        rendered = await template_service.render(db, template_name, variables, locale=locale)
        return await self.send(
            db,
            to=to,
            subject=str(rendered["subject"]),
            html=rendered.get("html"),
            text=rendered.get("text"),
            from_address=from_address,
            tenant_id=tenant_id,
            metadata={"template": template_name, "variables": variables},
        )

    async def health(self) -> dict[str, Any]:
        provider = email_provider_registry.default()
        return {"provider": provider.name, **await provider.health()}


email_service = EmailService()
