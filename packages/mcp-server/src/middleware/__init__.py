"""Middleware components for Knowledge MCP Server."""

from src.middleware.auth import (
    APIKeyValidator,
    AuthMiddleware,
    get_auth_context,
    require_tier,
)

__all__ = [
    "APIKeyValidator",
    "AuthMiddleware",
    "get_auth_context",
    "require_tier",
]
