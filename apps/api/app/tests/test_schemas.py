"""Unit tests for Pydantic schemas and validation."""

import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    EmailVerification,
    PasswordResetRequest,
    UserLogin,
    UserRegister,
)


def test_user_register_password_complexity() -> None:
    with pytest.raises(ValidationError):
        UserRegister(email="test@sprintsync.dev", password="short")

    with pytest.raises(ValidationError):
        UserRegister(email="test@sprintsync.dev", password="lowercase123!")

    with pytest.raises(ValidationError):
        UserRegister(email="test@sprintsync.dev", password="UPPERCASE123!")

    with pytest.raises(ValidationError):
        UserRegister(email="test@sprintsync.dev", password="Uppercase!!!")

    user = UserRegister(email="test@sprintsync.dev", password="MyStr0ng!Pass1")
    assert user.email == "test@sprintsync.dev"


def test_user_login_validation() -> None:
    with pytest.raises(ValidationError):
        UserLogin(email="not-an-email", password="password123")

    login = UserLogin(email="test@sprintsync.dev", password="password123")
    assert login.email == "test@sprintsync.dev"


def test_password_reset_request_email() -> None:
    with pytest.raises(ValidationError):
        PasswordResetRequest(email="invalid")

    request = PasswordResetRequest(email="user@sprintsync.dev")
    assert request.email == "user@sprintsync.dev"


def test_email_verification_token_required() -> None:
    with pytest.raises(ValidationError):
        EmailVerification(token="")

    ev = EmailVerification(token="some-token")
    assert ev.token == "some-token"
