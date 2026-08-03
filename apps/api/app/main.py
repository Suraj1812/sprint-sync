"""SprintSync FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.admin import admin_router
from app.api.v1.ai import ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.automation import automation_router
from app.api.v1.billing import billing_router
from app.api.v1.communications import comms_router
from app.api.v1.health import router as health_router
from app.api.v1.tenancy import tenancy_router
from app.api.v1.users import router as users_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.db.redis import get_redis
from app.db.seed import seed_roles
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.utils.responses import error_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    _redis = get_redis()
    try:
        await _redis.ping()
    except Exception:
        pass
    try:
        await seed_roles()
    except Exception:
        pass
    yield
    await _redis.close()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)

allowed_hosts = settings.allowed_host_list
if allowed_hosts != ["*"]:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=settings.cors_method_list,
    allow_headers=settings.cors_header_list,
    expose_headers=["x-correlation-id"],
)


@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    return error_response(exc)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    from app.core.logging import get_logger

    logger = get_logger("api.errors")
    logger.exception("unhandled_exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "internal_error",
            "message": "An unexpected error occurred.",
        },
    )


app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(automation_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(comms_router, prefix="/api/v1")
app.include_router(tenancy_router, prefix="/api/v1")
