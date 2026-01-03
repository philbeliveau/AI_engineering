"""Authentication middleware for Knowledge MCP Server.

Implements API key validation and tier-based access control.
Follows architecture.md:315-327 tiered authentication model.
"""

import re
import secrets
from typing import Callable

import structlog
from fastapi import Depends, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.exceptions import ForbiddenError
from src.models.auth import APIKey, AuthContext, UserTier

logger = structlog.get_logger()

# API key format: kp_ prefix + 32 hex characters
API_KEY_PATTERN = re.compile(r"^kp_[a-fA-F0-9]{32}$")


class APIKeyValidator:
    """Validates API keys and returns associated metadata.

    Uses in-memory storage for MVP. Production should use database.
    Uses secrets.compare_digest() for constant-time string comparison
    to prevent timing attacks during key validation.

    Attributes:
        _keys: In-memory dictionary mapping key strings to APIKey objects.
    """

    def __init__(self) -> None:
        """Initialize the validator with empty key storage."""
        self._keys: dict[str, APIKey] = {}

    def register_key(self, api_key: APIKey) -> None:
        """Register an API key for validation.

        Args:
            api_key: The APIKey object to register.
        """
        self._keys[api_key.key] = api_key
        logger.debug(
            "api_key_registered",
            key_prefix=api_key.key[:8] + "...",
            tier=api_key.tier.value,
        )

    def register_keys(self, api_keys: list[APIKey]) -> None:
        """Register multiple API keys.

        Args:
            api_keys: List of APIKey objects to register.
        """
        for key in api_keys:
            self.register_key(key)

    def validate_format(self, key: str) -> bool:
        """Validate API key format.

        Args:
            key: The API key string to validate.

        Returns:
            True if the format is valid (kp_ prefix + 32 hex chars).
        """
        return bool(API_KEY_PATTERN.match(key))

    def _find_key_constant_time(self, key: str) -> APIKey | None:
        """Find a matching API key using constant-time comparison.

        Iterates through all registered keys and uses secrets.compare_digest()
        for timing-attack-resistant string comparison.

        Args:
            key: The API key string to find.

        Returns:
            The matching APIKey object, or None if not found.
        """
        matched_key: APIKey | None = None

        # Iterate through all keys to prevent timing leaks
        # about which keys exist
        for stored_key, api_key in self._keys.items():
            # Use constant-time comparison to prevent timing attacks
            if secrets.compare_digest(key, stored_key):
                matched_key = api_key

        return matched_key

    def validate(self, key: str) -> APIKey | None:
        """Validate an API key and return associated metadata.

        Uses constant-time comparison via secrets.compare_digest()
        to prevent timing attacks.

        Args:
            key: The API key string to validate.

        Returns:
            The APIKey object if valid and not expired, None otherwise.
        """
        # Check format first
        if not self.validate_format(key):
            logger.debug("api_key_invalid_format", key_prefix=key[:8] + "..." if len(key) > 8 else key)
            return None

        # Find key using constant-time comparison
        api_key = self._find_key_constant_time(key)

        if api_key is None:
            logger.debug("api_key_not_found", key_prefix=key[:8] + "...")
            return None

        # Check expiration
        if api_key.is_expired:
            logger.debug(
                "api_key_expired",
                key_prefix=key[:8] + "...",
                expired_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
            )
            return None

        logger.debug(
            "api_key_validated",
            key_prefix=key[:8] + "...",
            tier=api_key.tier.value,
        )
        return api_key

    def clear(self) -> None:
        """Clear all registered keys. Useful for testing."""
        self._keys.clear()


# Global validator instance
_validator: APIKeyValidator | None = None


def get_validator() -> APIKeyValidator:
    """Get the global API key validator instance.

    Returns:
        The global APIKeyValidator instance.
    """
    global _validator
    if _validator is None:
        _validator = APIKeyValidator()
    return _validator


def set_validator(validator: APIKeyValidator) -> None:
    """Set the global API key validator instance.

    Useful for testing and dependency injection.

    Args:
        validator: The APIKeyValidator instance to use.
    """
    global _validator
    _validator = validator


class AuthMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for API key authentication.

    Extracts X-API-Key header, validates the key, and sets
    request.state.auth_context with tier information.

    Missing or invalid keys default to PUBLIC tier (no error).
    """

    def __init__(self, app: ASGIApp, validator: APIKeyValidator | None = None) -> None:
        """Initialize the middleware.

        Args:
            app: The ASGI application.
            validator: Optional APIKeyValidator instance. Uses global if not provided.
        """
        super().__init__(app)
        self._validator = validator or get_validator()

    async def dispatch(self, request: Request, call_next: Callable) -> None:
        """Process the request and set auth context.

        Args:
            request: The incoming request.
            call_next: The next middleware/handler in the chain.

        Returns:
            The response from the next handler.
        """
        # Extract API key from header (case-insensitive)
        api_key_header = request.headers.get("x-api-key") or request.headers.get("X-API-Key")

        if api_key_header:
            # Validate the key
            api_key = self._validator.validate(api_key_header)

            if api_key:
                # Valid key - set authenticated context
                request.state.auth_context = AuthContext.from_api_key(api_key)
                logger.info(
                    "request_authenticated",
                    tier=api_key.tier.value,
                    path=request.url.path,
                )
            else:
                # Invalid key - default to public (per AC #5, no error)
                # But if a key was provided and it's invalid, we might want to return 401
                # Per story: "Given no API key is provided... defaults to Public tier (no error)"
                # But AC #4: "Given invalid key... returns 401"
                # So: invalid key = 401, missing key = public
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    status_code=401,
                    content={
                        "error": {
                            "code": "UNAUTHORIZED",
                            "message": "Invalid or expired API key",
                            "details": {
                                "header": "X-API-Key",
                                "reason": "key_invalid_or_expired",
                            },
                        }
                    },
                )
        else:
            # No key provided - default to public tier (AC #5)
            request.state.auth_context = AuthContext.public()
            logger.debug("request_public", path=request.url.path)

        return await call_next(request)


def get_auth_context(request: Request) -> AuthContext:
    """FastAPI dependency to get auth context from request.

    Args:
        request: The FastAPI request object.

    Returns:
        The AuthContext from request.state, or public context if not set.
    """
    return getattr(request.state, "auth_context", AuthContext.public())


def require_tier(minimum_tier: UserTier) -> Callable:
    """Create a FastAPI dependency that requires a minimum tier.

    Args:
        minimum_tier: The minimum tier required to access the endpoint.

    Returns:
        A FastAPI dependency function that checks tier access.

    Raises:
        ForbiddenError: If the user's tier is insufficient.

    Example:
        @app.get("/premium-feature")
        async def premium_feature(
            auth: AuthContext = Depends(require_tier(UserTier.REGISTERED))
        ):
            return {"message": "Welcome, registered user!"}
    """

    def tier_checker(
        request: Request,
        auth_context: AuthContext = Depends(get_auth_context),
    ) -> AuthContext:
        """Check if the user's tier meets the minimum requirement.

        Args:
            request: The FastAPI request (for path info in error).
            auth_context: The current authentication context.

        Returns:
            The auth context if tier is sufficient.

        Raises:
            ForbiddenError: If tier is insufficient.
        """
        if not (auth_context.tier >= minimum_tier):
            logger.warning(
                "tier_access_denied",
                required_tier=minimum_tier.value,
                current_tier=auth_context.tier.value,
                path=request.url.path,
            )
            raise ForbiddenError(
                message=f"{minimum_tier.value} tier required for this resource",
                details={
                    "required_tier": minimum_tier.value,
                    "current_tier": auth_context.tier.value,
                    "path": request.url.path,
                },
            )
        return auth_context

    return tier_checker
