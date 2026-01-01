"""Response models for Knowledge MCP Server.

Follows architecture.md:464-476 (Success response format) and
architecture.md:478-485 (Error response format).
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

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


# Search-specific models (Story 4.2)


class SourcePosition(BaseModel):
    """Position of content within a source document.

    Attributes:
        chapter: Chapter name or number
        section: Section name or number
        page: Page number
    """

    chapter: str | None = Field(default=None, description="Chapter name or number")
    section: str | None = Field(default=None, description="Section name or number")
    page: int = Field(..., description="Page number")


class SourceAttribution(BaseModel):
    """Attribution information for a search result.

    Provides traceability back to the original source document.

    Attributes:
        source_id: Unique identifier of the source
        chunk_id: Unique identifier of the chunk (for extractions, references parent chunk)
        title: Title of the source document
        authors: List of author names
        position: Position within the source (chapter, section, page)
    """

    source_id: str = Field(..., description="Unique identifier of the source")
    chunk_id: str | None = Field(default=None, description="Unique identifier of the chunk")
    title: str = Field(..., description="Title of the source document")
    authors: list[str] = Field(default_factory=list, description="List of author names")
    position: SourcePosition | None = Field(
        default=None, description="Position within the source"
    )


class SearchResult(BaseModel):
    """Individual search result.

    Represents either a chunk or extraction result with source attribution.

    Attributes:
        id: Unique identifier of the result
        score: Relevance score (0-1, higher is better)
        type: Result type ("chunk" or "extraction")
        content: Text content of the result
        source: Source attribution information
    """

    id: str = Field(..., description="Unique identifier of the result")
    score: float = Field(..., description="Relevance score (0-1, higher is better)")
    type: str = Field(..., description='Result type ("chunk" or "extraction")')
    content: str = Field(..., description="Text content of the result")
    source: SourceAttribution = Field(..., description="Source attribution information")


class SearchMetadata(BaseModel):
    """Metadata for search responses.

    Extends base ResponseMetadata with search-specific fields.

    Attributes:
        query: Original search query
        sources_cited: List of source titles that appear in results
        result_count: Total number of results returned
        search_type: Type of search ("semantic")
    """

    query: str = Field(..., description="Original search query")
    sources_cited: list[str] = Field(
        default_factory=list, description="List of source titles in results"
    )
    result_count: int = Field(..., description="Total number of results returned")
    search_type: str = Field(default="semantic", description='Type of search ("semantic")')


class SearchKnowledgeResponse(BaseModel):
    """Response model for search_knowledge endpoint.

    Follows the mandatory response format from architecture.md.

    Attributes:
        results: List of search results
        metadata: Search metadata
    """

    results: list[SearchResult] = Field(
        default_factory=list, description="List of search results"
    )
    metadata: SearchMetadata = Field(..., description="Search metadata")
