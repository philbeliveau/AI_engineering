"""Response models for Knowledge MCP Server.

Follows architecture.md:464-476 (Success response format) and
architecture.md:478-485 (Error response format).

Story 4.6: Consolidated response models with latency tracking for NFR1 compliance.
"""

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

# Re-export error models from errors.py for backwards compatibility
from src.models.errors import ErrorCode, ErrorDetail, ErrorResponse  # noqa: E402, F401

T = TypeVar("T")


class ResponseMetadata(BaseModel):
    """Metadata for API responses.

    Attributes:
        query: Original query string
        sources_cited: List of source attributions
        result_count: Number of results returned
        search_type: Type of search performed (semantic, filtered, exact, list, comparison)
        latency_ms: Response time in milliseconds for NFR1 tracking (<500ms target)
    """

    query: str
    sources_cited: list[str]
    result_count: int
    search_type: Literal["semantic", "filtered", "list", "comparison"]
    latency_ms: int | None = Field(default=None, description="Response latency in milliseconds")


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper.

    All successful API responses are wrapped in this format.

    Attributes:
        results: List of results (always an array)
        metadata: Response metadata
    """

    results: list[T]
    metadata: ResponseMetadata


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
        latency_ms: Response time in milliseconds for NFR1 tracking
    """

    query: str = Field(..., description="Original search query")
    sources_cited: list[str] = Field(
        default_factory=list, description="List of source titles in results"
    )
    result_count: int = Field(..., description="Total number of results returned")
    search_type: Literal["semantic"] = Field(default="semantic", description='Type of search')
    latency_ms: int | None = Field(default=None, description="Response latency in milliseconds")


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


# Extraction Query Tool Response Models (Story 4.3)


class ExtractionMetadata(BaseModel):
    """Metadata for extraction query responses.

    Attributes:
        query: Topic filter applied or "all" if no filter
        sources_cited: List of source titles in results
        result_count: Total number of results returned
        search_type: Type of search ("filtered")
        latency_ms: Response time in milliseconds for NFR1 tracking
    """

    query: str = Field(..., description="Topic filter applied or 'all'")
    sources_cited: list[str] = Field(
        default_factory=list, description="List of source titles in results"
    )
    result_count: int = Field(..., description="Total number of results returned")
    search_type: Literal["filtered"] = Field(default="filtered", description='Type of search')
    latency_ms: int | None = Field(default=None, description="Response latency in milliseconds")


class DecisionResult(BaseModel):
    """Individual decision extraction result.

    Represents a decision point extracted from source material.

    Attributes:
        id: Unique identifier of the extraction
        question: The decision question or dilemma
        options: List of available options or choices
        considerations: Factors to consider when deciding
        recommended_approach: Suggested approach if available
        topics: Topic tags for categorization
        source_title: Title of the source document
        source_id: Unique identifier of the source
        chunk_id: Unique identifier of the parent chunk
    """

    id: str = Field(..., description="Unique identifier of the extraction")
    question: str = Field(..., description="The decision question or dilemma")
    options: list[str] = Field(default_factory=list, description="Available options")
    considerations: list[str] = Field(default_factory=list, description="Factors to consider")
    recommended_approach: str | None = Field(
        default=None, description="Suggested approach if available"
    )
    topics: list[str] = Field(default_factory=list, description="Topic tags")
    source_title: str = Field(..., description="Title of the source document")
    source_id: str = Field(..., description="Source document ID")
    chunk_id: str | None = Field(default=None, description="Parent chunk ID")


class PatternResult(BaseModel):
    """Individual pattern extraction result.

    Represents a code or design pattern extracted from source material.

    Attributes:
        id: Unique identifier of the extraction
        name: Name of the pattern
        problem: Problem the pattern solves
        solution: How the pattern solves the problem
        code_example: Example code if available
        context: When to use this pattern
        trade_offs: Trade-offs of using this pattern
        topics: Topic tags for categorization
        source_title: Title of the source document
        source_id: Unique identifier of the source
        chunk_id: Unique identifier of the parent chunk
    """

    id: str = Field(..., description="Unique identifier of the extraction")
    name: str = Field(..., description="Name of the pattern")
    problem: str = Field(..., description="Problem the pattern solves")
    solution: str = Field(..., description="How the pattern solves the problem")
    code_example: str | None = Field(default=None, description="Example code if available")
    context: str | None = Field(default=None, description="When to use this pattern")
    trade_offs: list[str] | None = Field(default=None, description="Trade-offs of using pattern")
    topics: list[str] = Field(default_factory=list, description="Topic tags")
    source_title: str = Field(..., description="Title of the source document")
    source_id: str = Field(..., description="Source document ID")
    chunk_id: str | None = Field(default=None, description="Parent chunk ID")


class WarningResult(BaseModel):
    """Individual warning extraction result.

    Represents a warning or pitfall extracted from source material.

    Attributes:
        id: Unique identifier of the extraction
        title: Short title for the warning
        description: Detailed description of the warning
        symptoms: Signs that indicate this problem
        consequences: What happens if ignored
        prevention: How to avoid this problem
        topics: Topic tags for categorization
        source_title: Title of the source document
        source_id: Unique identifier of the source
        chunk_id: Unique identifier of the parent chunk
    """

    id: str = Field(..., description="Unique identifier of the extraction")
    title: str = Field(..., description="Short title for the warning")
    description: str = Field(..., description="Detailed description of the warning")
    symptoms: list[str] | None = Field(default=None, description="Signs of this problem")
    consequences: list[str] | None = Field(default=None, description="What happens if ignored")
    prevention: str | None = Field(default=None, description="How to avoid this problem")
    topics: list[str] = Field(default_factory=list, description="Topic tags")
    source_title: str = Field(..., description="Title of the source document")
    source_id: str = Field(..., description="Source document ID")
    chunk_id: str | None = Field(default=None, description="Parent chunk ID")


class DecisionsResponse(BaseModel):
    """Response model for get_decisions endpoint.

    Follows the mandatory response format from architecture.md.

    Attributes:
        results: List of decision extractions
        metadata: Response metadata
    """

    results: list[DecisionResult] = Field(
        default_factory=list, description="List of decision extractions"
    )
    metadata: ExtractionMetadata = Field(..., description="Response metadata")


class PatternsResponse(BaseModel):
    """Response model for get_patterns endpoint.

    Follows the mandatory response format from architecture.md.

    Attributes:
        results: List of pattern extractions
        metadata: Response metadata
    """

    results: list[PatternResult] = Field(
        default_factory=list, description="List of pattern extractions"
    )
    metadata: ExtractionMetadata = Field(..., description="Response metadata")


class WarningsResponse(BaseModel):
    """Response model for get_warnings endpoint.

    Follows the mandatory response format from architecture.md.

    Attributes:
        results: List of warning extractions
        metadata: Response metadata
    """

    results: list[WarningResult] = Field(
        default_factory=list, description="List of warning extractions"
    )
    metadata: ExtractionMetadata = Field(..., description="Response metadata")


# Methodology Query Tool Response Models (Story 4.4)


class MethodologyResult(BaseModel):
    """Individual methodology extraction result.

    Represents a step-by-step process extracted from source material.

    Attributes:
        id: Unique identifier of the extraction
        name: Name of the methodology
        steps: Step-by-step process instructions
        prerequisites: Required knowledge or setup (optional)
        outputs: Expected outputs or deliverables (optional)
        topics: Topic tags for categorization
        source_title: Human-readable source document title
        source_id: Reference to sources collection
        chunk_id: Reference to chunks collection
    """

    id: str = Field(..., description="Unique identifier of the extraction")
    name: str = Field(..., description="Name of the methodology")
    steps: list[str] = Field(..., description="Step-by-step process instructions")
    prerequisites: list[str] | None = Field(
        default=None, description="Required knowledge or setup"
    )
    outputs: list[str] | None = Field(
        default=None, description="Expected outputs or deliverables"
    )
    topics: list[str] = Field(default_factory=list, description="Topic tags")
    source_title: str = Field(..., description="Human-readable source document title")
    source_id: str = Field(..., description="Reference to sources collection")
    chunk_id: str | None = Field(default=None, description="Reference to chunks collection")


class MethodologyResponse(BaseModel):
    """Response model for get_methodologies endpoint.

    Follows the mandatory response format from architecture.md.
    Requires Registered tier access (API key authentication).

    Attributes:
        results: List of methodology results
        metadata: Response metadata
    """

    results: list[MethodologyResult] = Field(
        default_factory=list, description="List of methodology results"
    )
    metadata: ExtractionMetadata = Field(..., description="Response metadata")


# Source Management Response Models (Story 4.5)


class SourceResult(BaseModel):
    """Individual source result.

    Represents a knowledge source (book, paper, case study) in the knowledge base.

    Attributes:
        id: Unique identifier of the source
        title: Human-readable source title
        authors: List of author names
        type: Source type (book, paper, case_study)
        path: Original file path
        ingested_at: ISO 8601 datetime when ingested
        status: Ingestion status (pending, processing, complete, failed)
        extraction_counts: Count of extractions by type
    """

    id: str = Field(..., description="Unique identifier of the source")
    title: str = Field(..., description="Human-readable source title")
    authors: list[str] = Field(default_factory=list, description="List of author names")
    type: str = Field(..., description="Source type (book, paper, case_study)")
    path: str = Field(..., description="Original file path")
    ingested_at: str = Field(..., description="ISO 8601 datetime when ingested")
    status: str = Field(..., description="Ingestion status")
    extraction_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Count of extractions by type (e.g., {decision: 15, pattern: 8})",
    )


class SourceListMetadata(BaseModel):
    """Metadata for source list responses.

    Attributes:
        query: Query description (always "all" for list_sources)
        sources_cited: Empty for source listing
        result_count: Total number of sources returned
        search_type: Type of search ("list")
        latency_ms: Response time in milliseconds for NFR1 tracking
    """

    query: str = Field(default="all", description="Query description")
    sources_cited: list[str] = Field(default_factory=list, description="Empty for source listing")
    result_count: int = Field(..., description="Total number of sources returned")
    search_type: Literal["list"] = Field(default="list", description='Type of search')
    latency_ms: int | None = Field(default=None, description="Response latency in milliseconds")


class SourceListResponse(BaseModel):
    """Response model for list_sources endpoint.

    Follows the mandatory response format from architecture.md.
    Public tier access (no authentication required).

    Attributes:
        results: List of source results
        metadata: Response metadata
    """

    results: list[SourceResult] = Field(
        default_factory=list, description="List of source results"
    )
    metadata: SourceListMetadata = Field(..., description="Response metadata")


class ExtractionSummary(BaseModel):
    """Summary of an extraction for comparison.

    Provides a condensed view of an extraction for cross-source comparison.

    Attributes:
        id: Unique identifier of the extraction
        type: Extraction type (decision, pattern, warning, methodology)
        title: Title or name from extraction
        summary: Brief summary of the extraction content
        topics: Topic tags for categorization
    """

    id: str = Field(..., description="Unique identifier of the extraction")
    type: str = Field(..., description="Extraction type")
    title: str = Field(..., description="Title or name from extraction")
    summary: str = Field(..., description="Brief summary of the extraction content")
    topics: list[str] = Field(default_factory=list, description="Topic tags")


class ComparisonResult(BaseModel):
    """Extractions from a single source for comparison.

    Groups extractions by source for side-by-side comparison.

    Attributes:
        source_id: Unique identifier of the source
        source_title: Human-readable source name
        extractions: List of extraction summaries from this source
    """

    source_id: str = Field(..., description="Unique identifier of the source")
    source_title: str = Field(..., description="Human-readable source name")
    extractions: list[ExtractionSummary] = Field(
        default_factory=list, description="Extraction summaries from this source"
    )


class ComparisonMetadata(BaseModel):
    """Metadata for comparison responses.

    Attributes:
        query: Topic used for comparison
        sources_cited: List of source titles included in comparison
        result_count: Total number of sources compared
        search_type: Type of search ("comparison")
        latency_ms: Response time in milliseconds for NFR1 tracking
    """

    query: str = Field(..., description="Topic used for comparison")
    sources_cited: list[str] = Field(
        default_factory=list, description="List of source titles in comparison"
    )
    result_count: int = Field(..., description="Total number of sources compared")
    search_type: Literal["comparison"] = Field(default="comparison", description='Type of search')
    latency_ms: int | None = Field(default=None, description="Response latency in milliseconds")


class CompareSourcesResponse(BaseModel):
    """Response model for compare_sources endpoint.

    Follows the mandatory response format from architecture.md.
    Requires Registered tier access (API key authentication).

    Attributes:
        results: List of comparison results grouped by source
        metadata: Response metadata
    """

    results: list[ComparisonResult] = Field(
        default_factory=list, description="Comparison results grouped by source"
    )
    metadata: ComparisonMetadata = Field(..., description="Response metadata")
