"""Admin platform unit tests."""

import pytest
from pydantic import ValidationError

from app.schemas.admin import AdminLogin
from app.services.admin import ADMIN_ROLES, _is_admin_role


class TestAdminSecurity:
    def test_admin_roles(self):
        assert "super_admin" in ADMIN_ROLES
        assert "platform_admin" in ADMIN_ROLES
        assert "user" not in ADMIN_ROLES

    def test_is_admin_role(self):
        assert _is_admin_role("super_admin") is True
        assert _is_admin_role("user") is False


class TestAdminSchemas:
    def test_login_valid(self):
        data = AdminLogin(email="admin@example.com", password="correct-horse-battery-staple")
        assert data.email == "admin@example.com"

    def test_login_invalid_email(self):
        with pytest.raises(ValidationError):
            AdminLogin(email="not-an-email", password="correct-horse-battery-staple")

    def test_login_short_password(self):
        with pytest.raises(ValidationError):
            AdminLogin(email="admin@example.com", password="short")
