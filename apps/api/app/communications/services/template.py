"""Email template service."""

import uuid
from string import Template
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.models.communication import EmailTemplate
from app.repositories.base import BaseRepository


class EmailTemplateRepository(BaseRepository[EmailTemplate]):
    def __init__(self) -> None:
        super().__init__(EmailTemplate)

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
        *,
        locale: str = "en",
    ) -> EmailTemplate | None:
        stmt = (
            select(EmailTemplate)
            .where(
                EmailTemplate.name == name,
                EmailTemplate.locale == locale,
                EmailTemplate.is_active.is_(True),
            )
            .order_by(desc(EmailTemplate.version))
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


email_template_repository = EmailTemplateRepository()


class TemplateService:
    async def get(
        self,
        db: AsyncSession,
        name: str,
        *,
        locale: str = "en",
    ) -> EmailTemplate:
        template = await email_template_repository.get_by_name(db, name, locale=locale)
        if not template:
            raise NotFoundError("Template not found")
        return template

    async def create(
        self,
        db: AsyncSession,
        *,
        name: str,
        subject: str,
        html_body: str | None = None,
        text_body: str | None = None,
        locale: str = "en",
        variables: list[str] | None = None,
        layout: str | None = None,
        metadata: dict | None = None,
    ) -> EmailTemplate:
        template = EmailTemplate(
            name=name,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            locale=locale,
            variables=variables or [],
            layout=layout,
            metadata=metadata,
        )
        return await email_template_repository.create(db, template)

    async def render(
        self,
        db: AsyncSession,
        template_name: str,
        variables: dict[str, Any],
        *,
        locale: str = "en",
    ) -> dict[str, str | None]:
        template = await self.get(db, template_name, locale=locale)
        app_name = (await get_settings()).app_name
        context = {"app_name": app_name, **variables}
        subject = Template(template.subject).safe_substitute(context)
        html = Template(template.html_body or "").safe_substitute(context) if template.html_body else None
        text = Template(template.text_body or "").safe_substitute(context) if template.text_body else None
        return {"subject": subject, "html": html, "text": text}

    async def preview(
        self,
        db: AsyncSession,
        template_name: str,
        variables: dict[str, Any],
        *,
        locale: str = "en",
    ) -> dict[str, str | None]:
        return await self.render(db, template_name, variables, locale=locale)


template_service = TemplateService()
