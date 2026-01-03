"""Authentication models for Knowledge MCP Server.

Defines API key structure, user tiers, and authentication context.
Follows architecture.md:315-327 tiered authentication model.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utc_now() -> datetime:
    """Get current UTC time in a Python 3.12+ compatible way."""
    return datetime.now(timezone.utc)

from pydantic import BaseModel, Field


class UserTier(str, Enum):
    """User access tier levels.

    Hierarchy: PREMIUM > REGISTERED > PUBLIC
    See architecture.md:315-327 for tier definitions.
    """

    PUBLIC = "PUBLIC"
    REGISTERED = "REGISTERED"
    PREMIUM = "PREMIUM"

    def __ge__(self, other: "UserTier") -> bool:
        """Check if this tier is greater than or equal to another."""
        order = {UserTier.PUBLIC: 0, UserTier.REGISTERED: 1, UserTier.PREMIUM: 2}
        return order[self] >= order[other]

    def __gt__(self, other: "UserTier") -> bool:
        """Check if this tier is greater than another."""
        order = {UserTier.PUBLIC: 0, UserTier.REGISTERED: 1, UserTier.PREMIUM: 2}
        return order[self] > order[other]

    def __le__(self, other: "UserTier") -> bool:
        """Check if this tier is less than or equal to another."""
        order = {UserTier.PUBLIC: 0, UserTier.REGISTERED: 1, UserTier.PREMIUM: 2}
        return order[self] <= order[other]

    def __lt__(self, other: "UserTier") -> bool:
        """Check if this tier is less than another."""
        order = {UserTier.PUBLIC: 0, UserTier.REGISTERED: 1, UserTier.PREMIUM: 2}
        return order[self] < order[other]


class APIKey(BaseModel):
    """API key model with tier and metadata.

    Attributes:
        key: The API key string (kp_ prefix + 32 hex chars)
        tier: User tier associated with this key
        created_at: When the key was created
        expires_at: Optional expiration timestamp
        metadata: Additional key metadata (user_id, description, etc.)
    """

    key: str = Field(..., description="API key string")
    tier: UserTier = Field(..., description="User tier for this key")
    created_at: datetime = Field(
        default_factory=_utc_now,
        description="Key creation timestamp",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="Optional expiration timestamp",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional key metadata",
    )

    @property
    def is_expired(self) -> bool:
        """Check if the key has expired."""
        if self.expires_at is None:
            return False
        return _utc_now() > self.expires_at


class AuthContext(BaseModel):
    """Authentication context for a request.

    Attached to request.state.auth_context by AuthMiddleware.

    Attributes:
        tier: The user's access tier
        api_key: The validated API key (if any)
        authenticated: Whether the request has a valid API key
    """

    tier: UserTier = Field(
        default=UserTier.PUBLIC,
        description="User access tier",
    )
    api_key: APIKey | None = Field(
        default=None,
        description="Validated API key (if authenticated)",
    )
    authenticated: bool = Field(
        default=False,
        description="Whether request has valid API key",
    )

    @classmethod
    def public(cls) -> "AuthContext":
        """Create a public (unauthenticated) context."""
        return cls(tier=UserTier.PUBLIC, api_key=None, authenticated=False)

    @classmethod
    def from_api_key(cls, api_key: APIKey) -> "AuthContext":
        """Create an authenticated context from an API key."""
        return cls(tier=api_key.tier, api_key=api_key, authenticated=True)
