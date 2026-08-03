"""Security audit logging helpers.

Never log passwords, tokens, or other sensitive fields.
"""

from app.core.logging import get_logger

logger = get_logger("security.audit")


def audit(
    event: str,
    *,
    user_id: str | None = None,
    email: str | None = None,
    ip: str | None = None,
    success: bool | None = None,
    **kwargs,
) -> None:
    logger.info(
        event,
        user_id=user_id,
        email=email,
        ip=ip,
        success=success,
        **kwargs,
    )
