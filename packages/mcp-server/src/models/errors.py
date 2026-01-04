"""Error response models for Knowledge MCP Server.

Follows architecture.md:478-497 (Error response format) and
project-context.md:152-160 (Error response format).

Story 4.6: Centralized error models with ErrorCode enum.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Standard error codes for API responses.

    Maps to HTTP status codes:
    - VALIDATION_ERROR: 400 Bad Request
    - UNAUTHORIZED: 401 Unauthorized
    - FORBIDDEN: 403 Forbidden
    - NOT_FOUND: 404 Not Found
    - RATE_LIMITED: 429 Too Many Requests
    - INTERNAL_ERROR: 500 Internal Server Error
    """

    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# Map error codes to HTTP status codes
ERROR_CODE_TO_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.INTERNAL_ERROR: 500,
}


class ErrorDetail(BaseModel):
    """Details about an error.

    Attributes:
        code: Standard error code from ErrorCode enum
        message: Human-readable error message
        details: Additional error context (field errors, resource ID, etc.)
        retry_after: Seconds until client can retry (only for RATE_LIMITED)
    """

    code: ErrorCode = Field(..., description="Standard error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    retry_after: int | None = Field(
        default=None, description="Seconds until retry allowed (RATE_LIMITED only)"
    )


class ErrorResponse(BaseModel):
    """Error response wrapper.

    All error responses are wrapped in this format per architecture.md.

    Attributes:
        error: Error details object
    """

    error: ErrorDetail = Field(..., description="Error details")
