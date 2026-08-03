"""Rate limiting configuration."""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.exceptions import RateLimitError
from app.utils.responses import error_response

limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request, exc: RateLimitExceeded):  # noqa: ARG001
    """Convert SlowAPI rate-limit errors into the standard response format."""
    return error_response(RateLimitError("Too many requests. Please slow down."))
