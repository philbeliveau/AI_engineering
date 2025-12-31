"""Response models for Knowledge MCP Server.

Follows architecture.md:464-476 (Success response format) and
architecture.md:478-485 (Error response format).
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseMetadata(BaseModel):
    """Metadata for API responses.

    Attributes:
        query: Original query string
        sources_cited: List of source attributions
        result_count: Number of results returned
        search_type: Type of search performed (semantic, filtered, exact)
    """

    query: str
    sources_cited: list[str]
    result_count: int
    search_type: str


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper.

    All successful API responses are wrapped in this format.

    Attributes:
        results: List of results (always an array)
        metadata: Response metadata
    """

    results: list[T]
    metadata: ResponseMetadata


class ErrorDetail(BaseModel):
    """Details about an error.

    Attributes:
        code: Error code (VALIDATION_ERROR, NOT_FOUND, RATE_LIMITED, INTERNAL_ERROR)
        message: Human-readable error message
        details: Additional error context
    """

    code: str
    message: str
    details: dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response wrapper.

    All error responses are wrapped in this format.

    Attributes:
        error: Error details
    """

    error: ErrorDetail
