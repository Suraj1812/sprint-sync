"""Structured logging configuration with correlation and request IDs."""

import logging
import uuid
from contextvars import ContextVar

import structlog

correlation_id_var: ContextVar[str] = ContextVar(
    "correlation_id", default=""
)


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def new_correlation_id() -> str:
    correlation_id = uuid.uuid4().hex
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> str:
    return correlation_id_var.get() or uuid.uuid4().hex
