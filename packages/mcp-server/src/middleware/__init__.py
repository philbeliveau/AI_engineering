"""Middleware components for Knowledge MCP Server."""

from src.middleware.auth import (
    APIKeyValidator,
    AuthMiddleware,
    get_auth_context,
    require_tier,
)
from src.middleware.error_handlers import (
    generic_exception_handler,
    knowledge_error_handler,
    validation_exception_handler,
)
from src.middleware.rate_limit import (
    RateLimitHeaderMiddleware,
    TIER_LIMITS,
    get_rate_limit_key,
    get_tier_rate_limit,
    limiter,
    rate_limit_error_handler,
)

__all__ = [
    "APIKeyValidator",
    "AuthMiddleware",
    "RateLimitHeaderMiddleware",
    "TIER_LIMITS",
    "generic_exception_handler",
    "get_auth_context",
    "get_rate_limit_key",
    "get_tier_rate_limit",
    "knowledge_error_handler",
    "limiter",
    "rate_limit_error_handler",
    "require_tier",
    "validation_exception_handler",
]
