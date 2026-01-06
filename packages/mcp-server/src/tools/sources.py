"""Source management endpoints for MCP Server.

Provides access to knowledge sources and cross-source comparison:
- list_sources: Public tier - list all available knowledge sources
- compare_sources: Registered tier - compare extractions across sources

Follows project-context.md:54-57 (async endpoints), architecture.md response format,
and architecture.md:315-327 tiered authentication model.
"""

import time
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Query, Request
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

from src.exceptions import NotFoundError
from src.middleware.auth import require_tier
from src.models.auth import AuthContext, UserTier
from src.models.responses import (
    CompareSourcesResponse,
    ComparisonMetadata,
    ComparisonResult,
    ExtractionSummary,
    SourceListMetadata,
    SourceListResponse,
    SourceResult,
)
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient

logger = structlog.get_logger()

router = APIRouter()

# Global clients - set by server.py during startup
_qdrant_client: QdrantStorageClient | None = None
_mongodb_client: MongoDBClient | None = None


def set_clients(
    qdrant: QdrantStorageClient | None, mongodb: MongoDBClient | None
) -> None:
    """Set the global storage clients.

    Called by server.py during application startup.

    Args:
        qdrant: QdrantStorageClient instance
        mongodb: MongoDBClient instance
    """
    global _qdrant_client, _mongodb_client
    _qdrant_client = qdrant
    _mongodb_client = mongodb


def get_qdrant_client() -> QdrantStorageClient | None:
    """Get the Qdrant client."""
    return _qdrant_client


def get_mongodb_client() -> MongoDBClient | None:
    """Get the MongoDB client."""
    return _mongodb_client


def _extract_title_from_content(content: dict[str, Any], payload: dict[str, Any]) -> str:
    """Extract a title or name from extraction content.

    Tries various common fields to find an appropriate title.

    Args:
        content: Extraction content from MongoDB
        payload: Qdrant payload (for fallback to extraction_title)

    Returns:
        Extracted title or fallback
    """
    if isinstance(content, dict):
        # Try common fields
        for field in ["name", "title", "question"]:
            if field in content and content[field]:
                return str(content[field])
    # Fallback to extraction_title from Qdrant payload
    return payload.get("extraction_title", "Untitled extraction")


def _extract_summary_from_content(content: dict[str, Any], extraction_type: str) -> str:
    """Extract a summary from extraction content.

    Creates a brief summary from the extraction content.

    Args:
        content: Extraction content from MongoDB
        extraction_type: Type of extraction for type-specific handling

    Returns:
        Brief summary string
    """
    if isinstance(content, dict):
        # Try common summary fields
        for field in ["summary", "description", "problem", "solution"]:
            if field in content and content[field]:
                text = str(content[field])
                # Truncate if too long
                if len(text) > 200:
                    return text[:197] + "..."
                return text
        # For methodologies, show first step
        if "steps" in content and content["steps"]:
            first_step = content["steps"][0]
            return f"Step 1: {first_step[:150]}" if len(str(first_step)) > 150 else f"Step 1: {first_step}"
        # For decisions, show options
        if "options" in content and content["options"]:
            options = content["options"][:3]
            return f"Options: {', '.join(options)}"
        # For warnings, show consequences
        if "consequences" in content and content["consequences"]:
            return f"Consequences: {content['consequences'][:150]}"
    return "No summary available"


@router.get(
    "/list_sources",
    operation_id="list_sources",
    response_model=SourceListResponse,
    tags=["sources"],
    summary="List all knowledge sources available in the database",
    description="""List all books, papers, and case studies in the knowledge base.

## WHEN TO USE
- User asks "what sources do you have on X?"
- User wants to know what's in the knowledge base
- Before compare_sources() to get valid source IDs
- When user asks about credibility or references

## WHEN NOT TO USE
- User wants to search content → use search_knowledge()
- User has a specific question → use specialized tools first

## USE FOR TRANSPARENCY
When synthesizing answers, you can reference:
- Which sources informed your answer
- How many sources cover a topic
- Authority/type of sources (books vs papers vs case studies)

## COMBINE WITH
- compare_sources() → after getting source IDs to compare perspectives
- search_knowledge() → to find content within specific sources""",
)
async def list_sources(
    request: Request,
    limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Max sources to return. Use default for full inventory.",
    ),
) -> SourceListResponse:
    """List all available knowledge sources.

    Returns all sources (books, papers, case studies) in the knowledge base
    along with extraction counts for each source.

    Public tier access - no authentication required.

    Args:
        request: FastAPI request object
        limit: Maximum number of sources to return (default 100)

    Returns:
        SourceListResponse with results and metadata
    """
    start_time = time.time()

    logger.info(
        "list_sources_start",
        limit=limit,
    )

    mongodb = get_mongodb_client()
    qdrant = get_qdrant_client()

    if not mongodb:
        logger.error("mongodb_client_not_available")
        latency_ms = int((time.time() - start_time) * 1000)
        return SourceListResponse(
            results=[],
            metadata=SourceListMetadata(
                query="all",
                sources_cited=[],
                result_count=0,
                search_type="list",
                latency_ms=latency_ms,
            ),
        )

    # Get all sources from MongoDB
    sources = await mongodb.list_sources(limit=limit)

    # Batch fetch extraction counts from Qdrant (avoids N+1 queries)
    source_ids = [s.get("id", "") for s in sources if s.get("id")]
    all_extraction_counts: dict[str, dict[str, int]] = {}
    if qdrant and source_ids:
        try:
            all_extraction_counts = await qdrant.count_extractions_by_sources(source_ids)
        except (UnexpectedResponse, ResponseHandlingException, RuntimeError) as e:
            # Graceful degradation: return empty counts on Qdrant errors
            logger.warning(
                "extraction_counts_batch_failed",
                source_count=len(source_ids),
                error=str(e),
                error_type=type(e).__name__,
            )

    results: list[SourceResult] = []
    for source in sources:
        source_id = source.get("id", "")
        extraction_counts = all_extraction_counts.get(source_id, {})

        results.append(
            SourceResult(
                id=source_id,
                title=source.get("title", "Unknown"),
                authors=source.get("authors", []),
                type=source.get("type", "unknown"),
                path=source.get("path", ""),
                ingested_at=source.get("ingested_at", ""),
                status=source.get("status", "unknown"),
                extraction_counts=extraction_counts,
            )
        )

    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "list_sources_complete",
        result_count=len(results),
        latency_ms=latency_ms,
    )

    return SourceListResponse(
        results=results,
        metadata=SourceListMetadata(
            query="all",
            sources_cited=[],
            result_count=len(results),
            search_type="list",
            latency_ms=latency_ms,
        ),
    )


@router.get(
    "/compare_sources",
    operation_id="compare_sources",
    response_model=CompareSourcesResponse,
    tags=["sources"],
    summary="Compare how different sources address the same topic",
    description="""Compare extractions across multiple sources for side-by-side analysis.

## WHEN TO USE
- User asks "what do different experts say about X?"
- User wants multiple perspectives on a topic
- After search_knowledge() shows results from multiple sources
- When there's known disagreement in the field

## WORKFLOW
1. Call list_sources() to get available source IDs
2. Call compare_sources() with 2-4 source IDs + topic
3. Synthesize: agreements, disagreements, unique insights

## SYNTHESIS GUIDANCE
- Highlight consensus across sources (strong signal)
- Note disagreements and explain different contexts
- Don't favor any single source unless clearly more authoritative
- Present as "Source A emphasizes X, while Source B focuses on Y"
- If spec is loaded, weight perspectives by relevance to domain/constraints

## COMBINE WITH
- list_sources() → get valid source IDs first
- get_decisions() → when comparing decision-making approaches
- search_knowledge() → to dive deeper into specific source content""",
)
async def compare_sources(
    request: Request,
    topic: str = Query(
        ...,
        description="Topic to compare: 'rag', 'embeddings', 'chunking', 'fine-tuning'. Use domain terms from loaded spec.",
    ),
    source_ids: list[str] = Query(
        ...,
        min_length=2,
        description="Source IDs to compare (get from list_sources). Use 2-4 sources for balanced comparison.",
    ),
    limit_per_source: int = Query(
        10,
        ge=1,
        le=50,
        description="Extractions per source. Use 5-10 for focused comparison.",
    ),
    auth_context: AuthContext = Depends(require_tier(UserTier.PUBLIC)),
) -> CompareSourcesResponse:
    """Compare extractions across multiple sources for a topic.

    Returns extractions from specified sources grouped by source for side-by-side
    comparison. Enables Claude to synthesize across different perspectives.

    Args:
        request: FastAPI request object
        topic: Topic to compare (matches any in topics array)
        source_ids: List of source IDs to compare (must be valid)
        limit_per_source: Maximum extractions per source (default 10)
        auth_context: Authentication context (injected by require_tier)

    Returns:
        CompareSourcesResponse with grouped results and metadata

    Raises:
        NotFoundError: If any source_id is invalid
    """
    start_time = time.time()

    logger.info(
        "compare_sources_start",
        topic=topic,
        source_ids=source_ids,
        limit_per_source=limit_per_source,
        user_tier=auth_context.tier.value,
    )

    mongodb = get_mongodb_client()
    qdrant = get_qdrant_client()

    if not mongodb or not qdrant:
        logger.error("storage_clients_not_available")
        latency_ms = int((time.time() - start_time) * 1000)
        return CompareSourcesResponse(
            results=[],
            metadata=ComparisonMetadata(
                query=topic,
                sources_cited=[],
                result_count=0,
                search_type="comparison",
                latency_ms=latency_ms,
            ),
        )

    # Validate all source IDs exist and build source cache
    source_cache: dict[str, dict[str, Any]] = {}
    for source_id in source_ids:
        source = await mongodb.get_source(source_id)
        if not source:
            logger.warning(
                "source_not_found",
                source_id=source_id,
            )
            raise NotFoundError(
                resource="source",
                resource_id=source_id,
            )
        source_cache[source_id] = source

    # Get extractions for comparison
    extractions_by_source = await qdrant.get_extractions_for_comparison(
        source_ids=source_ids,
        topic=topic,
        limit_per_source=limit_per_source,
    )

    # Build comparison results
    results: list[ComparisonResult] = []
    sources_cited: list[str] = []

    for source_id in source_ids:
        source = source_cache[source_id]
        source_title = source.get("title", "Unknown Source")
        sources_cited.append(source_title)

        # Convert extractions to summaries with MongoDB lookup
        extraction_summaries: list[ExtractionSummary] = []
        for extraction_item in extractions_by_source.get(source_id, []):
            payload = extraction_item.get("payload", {})
            extraction_id = payload.get("extraction_id")
            extraction_type = payload.get("extraction_type", "unknown")

            # Fetch full content from MongoDB
            content: dict[str, Any] = {}
            if mongodb and extraction_id:
                try:
                    extraction_doc = await mongodb.get_extraction_by_id(extraction_id)
                    if extraction_doc:
                        content = extraction_doc.get("content", {})
                except Exception as e:
                    logger.warning("compare_sources_mongodb_lookup_failed", extraction_id=extraction_id, error=str(e))

            extraction_summaries.append(
                ExtractionSummary(
                    id=extraction_item.get("id", ""),
                    type=extraction_type,
                    title=_extract_title_from_content(content, payload),
                    summary=_extract_summary_from_content(content, extraction_type),
                    topics=payload.get("topics", []),
                )
            )

        results.append(
            ComparisonResult(
                source_id=source_id,
                source_title=source_title,
                extractions=extraction_summaries,
            )
        )

    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "compare_sources_complete",
        topic=topic,
        sources_compared=len(results),
        total_extractions=sum(len(r.extractions) for r in results),
        latency_ms=latency_ms,
    )

    return CompareSourcesResponse(
        results=results,
        metadata=ComparisonMetadata(
            query=topic,
            sources_cited=sources_cited,
            result_count=len(results),
            search_type="comparison",
            latency_ms=latency_ms,
        ),
    )
