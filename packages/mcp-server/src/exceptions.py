"""Exception classes for Knowledge MCP Server.

Follows project-context.md:66-69 error handling pattern and
architecture.md:486-496 error codes.

Story 4.6: Enhanced exception hierarchy with status_code and correlation_id.
"""

import uuid
from typing import Any

from src.models.errors import ErrorCode


class KnowledgeError(Exception):
    """Base exception for all Knowledge MCP Server errors.

    All custom exceptions should inherit from this class.

    Attributes:
        code: Error code from ErrorCode enum
        message: Human-readable error message
        details: Additional context about the error
        status_code: HTTP status code for the error
    """

    def __init__(
        self,
        code: str | ErrorCode,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize KnowledgeError.

        Args:
            code: Error code string or ErrorCode enum
            message: Human-readable error message
            status_code: HTTP status code (default 500)
            details: Additional context about the error
        """
        # Support both string and ErrorCode enum for backwards compatibility
        self.code = code.value if isinstance(code, ErrorCode) else code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(KnowledgeError):
    """Exception for missing resources.

    Used when a requested resource (source, chunk, extraction) cannot be found.
    Returns HTTP 404 Not Found.
    """

    def __init__(
        self,
        resource: str,
        resource_id: str,
        message: str | None = None,
    ) -> None:
        """Initialize NotFoundError.

        Args:
            resource: Type of resource not found (e.g., "source", "extraction")
            resource_id: ID of the missing resource
            message: Optional custom message (auto-generated if not provided)
        """
        default_message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=message or default_message,
            status_code=404,
            details={"resource": resource, "id": resource_id},
        )


class ValidationError(KnowledgeError):
    """Exception for invalid input.

    Used when request parameters fail validation.
    Returns HTTP 400 Bad Request.
    """

    def __init__(
        self,
        message: str = "Invalid request parameters",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize ValidationError.

        Args:
            message: Human-readable error message
            details: Additional context about validation failures (e.g., field errors)
        """
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            status_code=400,
            details=details,
        )


class DatabaseError(KnowledgeError):
    """Exception for storage failures.

    Used when database operations (MongoDB, Qdrant) fail.
    Returns HTTP 500 Internal Server Error (no details exposed).
    """

    def __init__(
        self,
        message: str = "Database operation failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize DatabaseError.

        Args:
            message: Human-readable error message
            details: Additional context about the database failure
        """
        super().__init__(
            code=ErrorCode.INTERNAL_ERROR,
            message=message,
            status_code=500,
            details=details,
        )


class RateLimitError(KnowledgeError):
    """Exception for rate limit violations.

    Used when a client exceeds their API tier limits.
    Returns HTTP 429 Too Many Requests with Retry-After header.
    """

    def __init__(
        self,
        retry_after: int,
        limit: int,
        window: str,
        message: str | None = None,
    ) -> None:
        """Initialize RateLimitError.

        Args:
            retry_after: Seconds until client can retry
            limit: The rate limit that was exceeded
            window: The time window for the limit (e.g., "hour", "minute")
            message: Optional custom message
        """
        default_message = f"Rate limit exceeded. Please retry after {retry_after} seconds."
        super().__init__(
            code=ErrorCode.RATE_LIMITED,
            message=message or default_message,
            status_code=429,
            details={"limit": limit, "window": window, "retry_after": retry_after},
        )
        self.retry_after = retry_after


class AuthError(KnowledgeError):
    """Exception for authentication failures.

    Used when API key validation fails (invalid, malformed, or expired key).
    Returns HTTP 401 Unauthorized.
    """

    def __init__(
        self,
        message: str = "Unauthorized access",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize AuthError.

        Args:
            message: Human-readable error message
            details: Additional context about auth failure
        """
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=401,
            details=details,
        )


class ForbiddenError(KnowledgeError):
    """Exception for authorization failures.

    Used when a user's tier is insufficient for the requested resource.
    Returns HTTP 403 Forbidden.
    """

    def __init__(
        self,
        message: str = "Access forbidden",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize ForbiddenError.

        Args:
            message: Human-readable error message
            details: Additional context about required permissions
        """
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            status_code=403,
            details=details,
        )


class InternalError(KnowledgeError):
    """Exception for unexpected internal errors.

    Auto-generates a correlation_id for log correlation and debugging.
    Returns HTTP 500 Internal Server Error with correlation ID only.
    """

    def __init__(
        self,
        correlation_id: str | None = None,
        message: str = "An unexpected error occurred",
    ) -> None:
        """Initialize InternalError.

        Args:
            correlation_id: Optional correlation ID (auto-generated if not provided)
            message: Human-readable error message (safe for client)
        """
        self.correlation_id = correlation_id or str(uuid.uuid4())
        super().__init__(
            code=ErrorCode.INTERNAL_ERROR,
            message=message,
            status_code=500,
            details={"correlation_id": self.correlation_id},
        )
