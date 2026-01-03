"""Tests for authentication models.

Tests APIKey, UserTier, AuthContext models per story 5.2 AC #1, #2.
"""

from datetime import datetime, timedelta, timezone

import pytest

from src.exceptions import AuthError, ForbiddenError
from src.models.auth import APIKey, AuthContext, UserTier


class TestUserTier:
    """Tests for UserTier enum and comparisons."""

    def test_tier_values(self) -> None:
        """Test UserTier enum has correct values."""
        assert UserTier.PUBLIC.value == "PUBLIC"
        assert UserTier.REGISTERED.value == "REGISTERED"
        assert UserTier.PREMIUM.value == "PREMIUM"

    def test_tier_hierarchy_greater_than(self) -> None:
        """Test tier hierarchy: PREMIUM > REGISTERED > PUBLIC."""
        assert UserTier.PREMIUM > UserTier.REGISTERED
        assert UserTier.PREMIUM > UserTier.PUBLIC
        assert UserTier.REGISTERED > UserTier.PUBLIC

    def test_tier_hierarchy_less_than(self) -> None:
        """Test tier hierarchy: PUBLIC < REGISTERED < PREMIUM."""
        assert UserTier.PUBLIC < UserTier.REGISTERED
        assert UserTier.PUBLIC < UserTier.PREMIUM
        assert UserTier.REGISTERED < UserTier.PREMIUM

    def test_tier_hierarchy_equal(self) -> None:
        """Test tier equality comparisons."""
        assert UserTier.PUBLIC >= UserTier.PUBLIC
        assert UserTier.PUBLIC <= UserTier.PUBLIC
        assert UserTier.REGISTERED >= UserTier.REGISTERED
        assert UserTier.PREMIUM >= UserTier.PREMIUM

    def test_tier_hierarchy_greater_or_equal(self) -> None:
        """Test tier >= comparisons for access checks."""
        assert UserTier.PREMIUM >= UserTier.REGISTERED
        assert UserTier.PREMIUM >= UserTier.PUBLIC
        assert UserTier.REGISTERED >= UserTier.PUBLIC
        assert not (UserTier.PUBLIC >= UserTier.REGISTERED)


class TestAPIKey:
    """Tests for APIKey model."""

    def test_api_key_creation(self) -> None:
        """Test creating an API key with required fields."""
        key = APIKey(
            key="kp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            tier=UserTier.REGISTERED,
        )
        assert key.key == "kp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        assert key.tier == UserTier.REGISTERED
        assert key.expires_at is None
        assert key.metadata == {}
        assert not key.is_expired

    def test_api_key_with_metadata(self) -> None:
        """Test API key with metadata."""
        key = APIKey(
            key="kp_test12345678901234567890123456",
            tier=UserTier.PREMIUM,
            metadata={"user_id": "user_123", "description": "Test key"},
        )
        assert key.metadata["user_id"] == "user_123"
        assert key.metadata["description"] == "Test key"

    def test_api_key_not_expired(self) -> None:
        """Test API key with future expiration is not expired."""
        future = datetime.now(timezone.utc) + timedelta(days=30)
        key = APIKey(
            key="kp_test12345678901234567890123456",
            tier=UserTier.REGISTERED,
            expires_at=future,
        )
        assert not key.is_expired

    def test_api_key_expired(self) -> None:
        """Test API key with past expiration is expired."""
        past = datetime.now(timezone.utc) - timedelta(days=1)
        key = APIKey(
            key="kp_test12345678901234567890123456",
            tier=UserTier.REGISTERED,
            expires_at=past,
        )
        assert key.is_expired

    def test_api_key_no_expiration(self) -> None:
        """Test API key without expiration never expires."""
        key = APIKey(
            key="kp_test12345678901234567890123456",
            tier=UserTier.PREMIUM,
            expires_at=None,
        )
        assert not key.is_expired


class TestAuthContext:
    """Tests for AuthContext model."""

    def test_public_context(self) -> None:
        """Test creating public (unauthenticated) context."""
        ctx = AuthContext.public()
        assert ctx.tier == UserTier.PUBLIC
        assert ctx.api_key is None
        assert ctx.authenticated is False

    def test_from_api_key(self) -> None:
        """Test creating authenticated context from API key."""
        api_key = APIKey(
            key="kp_test12345678901234567890123456",
            tier=UserTier.REGISTERED,
        )
        ctx = AuthContext.from_api_key(api_key)
        assert ctx.tier == UserTier.REGISTERED
        assert ctx.api_key == api_key
        assert ctx.authenticated is True

    def test_from_premium_api_key(self) -> None:
        """Test creating premium context from premium API key."""
        api_key = APIKey(
            key="kp_premium123456789012345678901",
            tier=UserTier.PREMIUM,
        )
        ctx = AuthContext.from_api_key(api_key)
        assert ctx.tier == UserTier.PREMIUM
        assert ctx.authenticated is True

    def test_default_context_is_public(self) -> None:
        """Test default AuthContext is public."""
        ctx = AuthContext()
        assert ctx.tier == UserTier.PUBLIC
        assert ctx.authenticated is False


class TestAuthExceptions:
    """Tests for authentication exceptions."""

    def test_auth_error(self) -> None:
        """Test AuthError exception."""
        error = AuthError(
            message="Invalid API key",
            details={"header": "X-API-Key", "reason": "key_not_found"},
        )
        assert error.code == "UNAUTHORIZED"
        assert error.message == "Invalid API key"
        assert error.details["header"] == "X-API-Key"
        assert error.details["reason"] == "key_not_found"

    def test_forbidden_error(self) -> None:
        """Test ForbiddenError exception."""
        error = ForbiddenError(
            message="Registered tier required",
            details={
                "required_tier": "REGISTERED",
                "current_tier": "PUBLIC",
                "tool": "get_methodologies",
            },
        )
        assert error.code == "FORBIDDEN"
        assert error.message == "Registered tier required"
        assert error.details["required_tier"] == "REGISTERED"
        assert error.details["current_tier"] == "PUBLIC"
