"""Centralized application exceptions.

All service-layer errors derive from AppError and are converted into consistent
HTTP responses by the global exception handler.
"""


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    error_code: str = "internal_error"
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str | None = None) -> None:
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class AuthenticationError(AppError):
    status_code = 401
    error_code = "authentication_error"
    detail = "Authentication failed."


class AuthorizationError(AppError):
    status_code = 403
    error_code = "authorization_error"
    detail = "You do not have permission to perform this action."


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"
    detail = "Resource not found."


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"
    detail = "Resource already exists."


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"
    detail = "Request validation failed."


class RateLimitError(AppError):
    status_code = 429
    error_code = "rate_limit_exceeded"
    detail = "Rate limit exceeded. Please try again later."


class ServiceUnavailableError(AppError):
    status_code = 503
    error_code = "service_unavailable"
    detail = "The requested AI provider is currently unavailable."
