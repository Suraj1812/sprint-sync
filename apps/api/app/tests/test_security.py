"""Unit tests for security helpers."""

import uuid

import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification() -> None:
    password = "MyStr0ng!Pass123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_jwt_roundtrip() -> None:
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "user")
    payload = decode_token(token, "access")

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert payload["role"] == "user"

    with pytest.raises(AuthenticationError):
        decode_token(token, "refresh")


def test_refresh_token_roundtrip() -> None:
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id, "token-family-1")
    payload = decode_token(token, "refresh")

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"
    assert payload["family"] == "token-family-1"
