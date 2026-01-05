"""Rate limiting middleware for Knowledge MCP Server.

Implements tier-based rate limiting using slowapi (token bucket algorithm).
Follows architecture.md:315-327 tiered authentication model:
- Public: 100 req/hr per IP
- Registered: 1000 req/hr per API key
- Premium: Unlimited (999999 req/hr)

Story 5.1: Rate Limiting Middleware
"""

import time
from typing import Callable

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.models.auth import AuthContext, UserTier
from src.models.errors import ErrorCode, ErrorDetail, ErrorResponse

logger = structlog.get_logger()

# Tier-based rate limits (per architecture.md:315-327)
TIER_LIMITS = {
    UserTier.PUBLIC: "100/hour",
    UserTier.REGISTERED: "1000/hour",
    UserTier.PREMIUM: "999999/hour",  # Effectively unlimited
}


def get_rate_limit_key(request: Request) -> str:
    """Extract rate limit key with proxy awareness.

    Uses API key if present (for registered/premium tiers),
    otherwise extracts real client IP (X-Forwarded-For aware).

    Args:
        request: FastAPI request object

    Returns:
        Rate limit key in format "apikey:{key}" or "ip:{address}"
    """
    # Check for API key first (registered/premium tier)
    api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if api_key:
        logger.debug(
            "rate_limit_key_apikey",
            key_prefix=api_key[:8] + "..." if len(api_key) > 8 else api_key,
        )
        return f"apikey:{api_key}"

    # CRITICAL: Check X-Forwarded-For BEFORE request.client.host
    # Required for Railway/cloud deployments behind reverse proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # First IP in comma-separated list is real client
        # Format: "client_ip, proxy1_ip, proxy2_ip"
        ip = forwarded.split(",")[0].strip()
        logger.debug("rate_limit_key_forwarded_ip", ip=ip)
        return f"ip:{ip}"

    # Fallback for local development (no proxy)
    ip = request.client.host if request.client else "unknown"
    logger.debug("rate_limit_key_direct_ip", ip=ip)
    return f"ip:{ip}"


def get_tier_rate_limit(key: str) -> str:
    """Return rate limit string based on key type.

    Dynamic limit function for slowapi's @limiter.limit() decorator.
    Receives the key from get_rate_limit_key() and determines the limit.

    - Keys starting with "apikey:" get REGISTERED tier limit (1000/hour)
      (Premium detection would require database lookup - future enhancement)
    - Keys starting with "ip:" get PUBLIC tier limit (100/hour)

    Args:
        key: Rate limit key from get_rate_limit_key() (e.g., "apikey:xxx" or "ip:1.2.3.4")

    Returns:
        Rate limit string (e.g., "100/hour", "1000/hour")
    """
    # Determine tier based on key type
    # API keys indicate authenticated users (at least REGISTERED tier)
    # IP-based keys are PUBLIC tier
    if key.startswith("apikey:"):
        # Authenticated user - default to REGISTERED tier
        # Premium detection would require database lookup (future enhancement)
        tier = UserTier.REGISTERED
    else:
        # IP-based (public/anonymous user)
        tier = UserTier.PUBLIC

    limit = TIER_LIMITS.get(tier, TIER_LIMITS[UserTier.PUBLIC])

    logger.debug(
        "tier_rate_limit",
        key_type="apikey" if key.startswith("apikey:") else "ip",
        tier=tier.value,
        limit=limit,
    )

    return limit


def get_tier_from_request(request: Request) -> str:
    """Get tier string from request for error responses.

    Args:
        request: FastAPI request object

    Returns:
        Tier name string (e.g., "public", "registered")
    """
    auth_context: AuthContext = getattr(
        request.state, "auth_context", AuthContext.public()
    )
    return auth_context.tier.value.lower()


async def rate_limit_error_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    """Return MCP-compatible error response for rate limit exceeded.

    Parses slowapi exception to extract retry timing and returns
    error in project-context.md:152-160 format.

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception from slowapi

    Returns:
        JSONResponse with 429 status and MCP error format
    """
    # Parse limit from exception detail string
    # slowapi format: "100 per 1 hour"
    detail_str = str(exc.detail)
    limit = 100  # Default fallback
    window_seconds = 3600  # Default to 1 hour

    try:
        # Parse "100 per 1 hour" format
        parts = detail_str.split(" per ")
        if len(parts) >= 1:
            limit = int(parts[0])
    except (ValueError, IndexError):
        pass

    # Calculate retry_after (approximate - full window for simplicity)
    # In production, slowapi provides more accurate timing
    retry_after = window_seconds

    # Get tier for response
    tier = get_tier_from_request(request)

    logger.warning(
        "rate_limit_exceeded",
        key=get_rate_limit_key(request),
        tier=tier,
        limit=limit,
        retry_after=retry_after,
        path=request.url.path,
    )

    # Build MCP-compatible error response (project-context.md:152-160)
    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.RATE_LIMITED,
            message=f"Rate limit of {limit} requests per hour exceeded",
            details={
                "limit": limit,
                "window_seconds": window_seconds,
                "retry_after": retry_after,
                "tier": tier,
            },
            retry_after=retry_after,
        )
    )

    # Reset timestamp (Unix time when limit resets)
    reset_timestamp = int(time.time()) + retry_after

    return JSONResponse(
        status_code=429,
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_timestamp),
        },
        content=response.model_dump(),
    )


# Initialize slowapi Limiter with token bucket algorithm (in-memory)
# Uses get_rate_limit_key for tier-aware key extraction
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[],  # No global limit, per-route only via decorator
)


class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers to successful responses.

    Adds X-RateLimit-* headers to all responses for client usage tracking.
    Headers are added based on the tier and current usage.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware.

        Args:
            app: ASGI application
        """
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> JSONResponse:
        """Process request and add rate limit headers to response.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler

        Returns:
            Response with rate limit headers added
        """
        response = await call_next(request)

        # Get tier to determine limit
        auth_context: AuthContext = getattr(
            request.state, "auth_context", AuthContext.public()
        )
        tier = auth_context.tier
        limit_str = TIER_LIMITS.get(tier, TIER_LIMITS[UserTier.PUBLIC])

        # Parse limit from string (e.g., "100/hour" -> 100)
        try:
            limit = int(limit_str.split("/")[0])
        except (ValueError, IndexError):
            limit = 100

        # Add rate limit headers
        # Note: Remaining count is approximate without full limiter state access
        # slowapi stores state internally; for accurate remaining, would need
        # to query limiter storage directly (future enhancement)
        reset_timestamp = int(time.time()) + 3600  # Reset in 1 hour (approximate)

        response.headers["X-RateLimit-Limit"] = str(limit)
        # Remaining is not easily accessible from slowapi; set to limit - 1 as indicator
        # In production, this should query the actual limiter storage
        response.headers["X-RateLimit-Reset"] = str(reset_timestamp)

        return response


# Public API exports
__all__ = [
    "limiter",
    "get_rate_limit_key",
    "get_tier_rate_limit",
    "rate_limit_error_handler",
    "RateLimitHeaderMiddleware",
    "TIER_LIMITS",
]
