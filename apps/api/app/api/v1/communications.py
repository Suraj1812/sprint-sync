"""Communication and notification API v1."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user, get_db_session
from app.core.exceptions import AuthorizationError
from app.models.communication import (
    CommunicationEvent,
    DeliveryAttempt,
    EmailTemplate,
    Notification,
)
from app.models.user import User
from app.schemas.communication import (
    DeliveryStats,
    EmailTemplateCreate,
    EmailTemplateRead,
    EventPublishRequest,
    NotificationCount,
    NotificationCreate,
    NotificationRead,
    PreferenceRead,
    PreferenceUpdate,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
)
from app.schemas.common import APIResponse
from app.communications.services.email import email_service
from app.communications.services.event_bus import event_bus
from app.communications.services.notification import notification_service
from app.communications.services.preference import preference_service
from app.communications.services.template import template_service

comms_router = APIRouter(prefix="/communications", tags=["communications"])


@comms_router.get("/notifications", response_model=list[NotificationRead])
async def list_notifications(
    unread_only: bool = False,
    category: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await notification_service.list_for_user(
        db,
        user.id,
        unread_only=unread_only,
        category=category,
        skip=skip,
        limit=limit,
    )


@comms_router.get("/notifications/count", response_model=NotificationCount)
async def notification_count(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> NotificationCount:
    return NotificationCount(unread=await notification_service.unread_count(db, user.id))


@comms_router.post("/notifications", response_model=NotificationRead)
async def create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    if data.user_id != user.id and not user.is_admin:
        raise AuthorizationError("Cannot create notification for another user")
    return await notification_service.create(
        db,
        user_id=data.user_id,
        title=data.title,
        category=data.category,
        body=data.body,
        priority=data.priority,
        deep_link=data.deep_link,
    )


@comms_router.post("/notifications/{notification_id}/read")
async def mark_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    await notification_service.mark_read(db, notification_id, user.id)
    return {"ok": True}


@comms_router.post("/notifications/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    count = await notification_service.mark_all_read(db, user.id)
    return {"marked_as_read": count}


@comms_router.post("/notifications/{notification_id}/archive")
async def archive_notification(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    await notification_service.archive(db, notification_id, user.id)
    return {"ok": True}


@comms_router.get("/preferences", response_model=list[PreferenceRead])
async def list_preferences(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await preference_service.get(db, user.id)


@comms_router.post("/preferences", response_model=PreferenceRead)
async def set_preference(
    data: PreferenceUpdate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    return await preference_service.set(
        db,
        user.id,
        channel=data.channel,
        category=data.category,
        enabled=data.enabled,
        frequency=data.frequency,
        digest=data.digest,
        quiet_hours_start=data.quiet_hours_start,
        quiet_hours_end=data.quiet_hours_end,
        language=data.language,
    )


@comms_router.post("/events/publish")
async def publish_event(
    data: EventPublishRequest,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> APIResponse:
    event = await event_bus.publish(db, data.event_type, data.payload, tenant_id=data.tenant_id)
    await event_bus.dispatch(db, event)
    return APIResponse(message="Event published")


@comms_router.get("/admin/templates", response_model=list[EmailTemplateRead])
async def admin_list_templates(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
    name: str | None = None,
    locale: str = "en",
) -> list[Any]:
    stmt = select(EmailTemplate).where(EmailTemplate.locale == locale)
    if name:
        stmt = stmt.where(EmailTemplate.name == name)
    stmt = stmt.order_by(EmailTemplate.name, EmailTemplate.version.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@comms_router.post("/admin/templates", response_model=EmailTemplateRead)
async def admin_create_template(
    data: EmailTemplateCreate,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> Any:
    return await template_service.create(
        db,
        name=data.name,
        subject=data.subject,
        html_body=data.html_body,
        text_body=data.text_body,
        locale=data.locale,
        variables=data.variables,
        layout=data.layout,
    )


@comms_router.post("/admin/templates/preview", response_model=TemplatePreviewResponse)
async def admin_preview_template(
    data: TemplatePreviewRequest,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> Any:
    rendered = await template_service.preview(db, data.name, data.variables, locale=data.locale)
    return TemplatePreviewResponse(**rendered)


@comms_router.post("/admin/send-email")
async def admin_send_email(
    to: str,
    template: str,
    variables: dict,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> Any:
    result = await email_service.send_template(db, to=to, template_name=template, variables=variables)
    return {"success": result.success, "status": result.status}


@comms_router.get("/admin/stats", response_model=DeliveryStats)
async def admin_stats(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> Any:
    total = await db.scalar(select(func.count(CommunicationEvent.id)))
    pending = await db.scalar(select(func.count(CommunicationEvent.id)).where(CommunicationEvent.status == "pending"))
    completed = await db.scalar(select(func.count(CommunicationEvent.id)).where(CommunicationEvent.status == "completed"))
    failed = await db.scalar(select(func.count(CommunicationEvent.id)).where(CommunicationEvent.status == "failed"))

    by_channel = {}
    stmt = select(DeliveryAttempt.channel, func.count(DeliveryAttempt.id)).group_by(DeliveryAttempt.channel)
    result = await db.execute(stmt)
    for row in result.all():
        by_channel[row[0]] = row[1]

    return DeliveryStats(
        total=total or 0,
        pending=pending or 0,
        completed=completed or 0,
        failed=failed or 0,
        by_channel=by_channel,
    )
