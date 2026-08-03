"""Shared API response helpers."""

from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


def error_response(exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.detail,
        },
    )
