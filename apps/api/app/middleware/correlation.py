"""Request correlation ID and structured request logging middleware."""

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.logging import correlation_id_var, get_logger

logger = get_logger("api.middleware")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        correlation_id = request.headers.get(
            "x-correlation-id",
            uuid.uuid4().hex,
        )
        correlation_id_var.set(correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response: Response | None = None
        try:
            response = await call_next(request)
        finally:
            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=getattr(response, "status_code", 500),
                duration_ms=round(duration, 2),
                correlation_id=correlation_id,
            )
            if response is not None:
                response.headers["x-correlation-id"] = correlation_id

        return response
