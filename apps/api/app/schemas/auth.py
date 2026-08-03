"""Pydantic schemas for authentication."""

import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user import UserRead

PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128
SPECIAL_CHARACTERS = r"!@#$%^&*()-_=+[]{};:'\",.<>/?`~|\\"


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )
    first_name: str | None = None
    last_name: str | None = None

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(rf"[{re.escape(SPECIAL_CHARACTERS)}]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)


class TokenPair(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class EmailVerification(BaseModel):
    token: str


class AuthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserRead
    tokens: TokenPair
