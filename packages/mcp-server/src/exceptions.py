"""Exception classes for Knowledge MCP Server.

Follows project-context.md:66-69 error handling pattern and
architecture.md:486-496 error codes.
"""

from typing import Any


class KnowledgeError(Exception):
    """Base exception for all Knowledge MCP Server errors.

    All custom exceptions should inherit from this class.

    Attributes:
        code: Error code string (e.g., NOT_FOUND, VALIDATION_ERROR)
        message: Human-readable error message
        details: Additional context about the error
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize KnowledgeError.

        Args:
            code: Error code string
            message: Human-readable error message
            details: Additional context about the error
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(KnowledgeError):
    """Exception for missing resources.

    Used when a requested resource (source, chunk, extraction) cannot be found.
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize NotFoundError.

        Args:
            message: Human-readable error message
            details: Additional context about what was not found
        """
        super().__init__(code="NOT_FOUND", message=message, details=details)


class ValidationError(KnowledgeError):
    """Exception for invalid input.

    Used when request parameters fail validation.
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize ValidationError.

        Args:
            message: Human-readable error message
            details: Additional context about validation failures
        """
        super().__init__(code="VALIDATION_ERROR", message=message, details=details)


class DatabaseError(KnowledgeError):
    """Exception for storage failures.

    Used when database operations (MongoDB, Qdrant) fail.
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize DatabaseError.

        Args:
            message: Human-readable error message
            details: Additional context about the database failure
        """
        super().__init__(code="INTERNAL_ERROR", message=message, details=details)


class RateLimitError(KnowledgeError):
    """Exception for rate limit violations.

    Used when a client exceeds their API tier limits.
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize RateLimitError.

        Args:
            message: Human-readable error message
            details: Additional context about rate limits
        """
        super().__init__(code="RATE_LIMITED", message=message, details=details)


class AuthError(KnowledgeError):
    """Exception for authentication failures.

    Used when API key validation fails (invalid, malformed, or expired key).
    Returns HTTP 401 Unauthorized.
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize AuthError.

        Args:
            message: Human-readable error message
            details: Additional context about auth failure
        """
        super().__init__(code="UNAUTHORIZED", message=message, details=details)


class ForbiddenError(KnowledgeError):
    """Exception for authorization failures.

    Used when a user's tier is insufficient for the requested resource.
    Returns HTTP 403 Forbidden.
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize ForbiddenError.

        Args:
            message: Human-readable error message
            details: Additional context about required permissions
        """
        super().__init__(code="FORBIDDEN", message=message, details=details)
