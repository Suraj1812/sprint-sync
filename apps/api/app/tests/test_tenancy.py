"""Multi-tenancy unit tests."""

import pytest

from app.tenancy.services.membership import MembershipService
from app.tenancy.services.organization import _make_slug


class TestSlug:
    def test_make_slug(self):
        assert _make_slug("Acme Corp") == "acme-corp"
        assert _make_slug("Two  Words") == "two-words"


class TestPermissionMatrix:
    def test_owner_has_wildcard(self):
        service = MembershipService()
        assert service._has_permission(service.ORG_PERMISSIONS, "owner", "anything")

    def test_member_limited(self):
        service = MembershipService()
        assert service._has_permission(service.ORG_PERMISSIONS, "member", "workspace.view")
        assert not service._has_permission(service.ORG_PERMISSIONS, "member", "organization.update")
