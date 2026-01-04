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

__all__ = [
    "APIKeyValidator",
    "AuthMiddleware",
    "generic_exception_handler",
    "get_auth_context",
    "knowledge_error_handler",
    "require_tier",
    "validation_exception_handler",
]
