from functools import lru_cache

from pydantic import EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SprintSync API"
    environment: str = "development"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sprintsync"
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = "change-me-in-production-immediately"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    admin_token_expire_hours: int = 8
    password_hash_time_cost: int = 2
    password_hash_memory_cost: int = 65536
    password_hash_parallelism: int = 4

    # CORS
    cors_origins: str = "http://localhost:3000"
    cors_methods: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    cors_headers: str = "*"

    # Hosts
    allowed_hosts: str = "*"
    hsts_enabled: bool = False

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Email (architecture-only; provider injected in tasks)
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    email_from: EmailStr = "noreply@sprintsync.dev"

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # AI providers
    ai_default_provider: str = "openai"
    ai_default_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_api_key: str | None = None
    anthropic_base_url: str = "https://api.anthropic.com/v1"
    azure_openai_key: str | None = None
    azure_openai_endpoint: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # Billing
    billing_provider: str = "stripe"
    stripe_secret_key: str | None = None
    stripe_publishable_key: str | None = None
    stripe_webhook_secret: str | None = None
    paddle_api_key: str | None = None
    paddle_webhook_secret: str | None = None
    razorpay_key_id: str | None = None
    razorpay_key_secret: str | None = None
    razorpay_webhook_secret: str | None = None
    billing_currency: str = "usd"

    # Communications
    email_provider: str = "console"
    resend_api_key: str | None = None
    sendgrid_api_key: str | None = None
    ses_access_key_id: str | None = None
    ses_secret_access_key: str | None = None
    ses_region: str = "us-east-1"
    postmark_api_key: str | None = None
    push_provider: str = "none"
    vapid_public_key: str | None = None
    vapid_private_key: str | None = None
    default_locale: str = "en"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def cors_method_list(self) -> list[str]:
        return [
            method.strip().upper()
            for method in self.cors_methods.split(",")
            if method.strip()
        ]

    @property
    def cors_header_list(self) -> list[str]:
        return [
            header.strip()
            for header in self.cors_headers.split(",")
            if header.strip()
        ]

    @property
    def allowed_host_list(self) -> list[str]:
        return [
            host.strip()
            for host in self.allowed_hosts.split(",")
            if host.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
