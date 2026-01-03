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


def _extract_title_from_payload(payload: dict[str, Any]) -> str:
    """Extract a title or name from extraction payload.

    Tries various common fields to find an appropriate title.

    Args:
        payload: Extraction payload from Qdrant

    Returns:
        Extracted title or fallback
    """
    content = payload.get("content", {})
    if isinstance(content, dict):
        # Try common fields
        for field in ["name", "title", "question"]:
            if field in content and content[field]:
                return str(content[field])
    return "Untitled extraction"


def _extract_summary_from_payload(payload: dict[str, Any]) -> str:
    """Extract a summary from extraction payload.

    Creates a brief summary from the extraction content.

    Args:
        payload: Extraction payload from Qdrant

    Returns:
        Brief summary string
    """
    content = payload.get("content", {})
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
            return f"Step 1: {content['steps'][0]}"
    return "No summary available"


@router.get(
    "/list_sources",
    operation_id="list_sources",
    response_model=SourceListResponse,
    tags=["sources"],
)
async def list_sources(
    request: Request,
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of sources to return"
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
        return SourceListResponse(
            results=[],
            metadata=SourceListMetadata(
                query="all",
                sources_cited=[],
                result_count=0,
                search_type="list",
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

    latency_ms = (time.time() - start_time) * 1000

    logger.info(
        "list_sources_complete",
        result_count=len(results),
        latency_ms=round(latency_ms, 2),
    )

    return SourceListResponse(
        results=results,
        metadata=SourceListMetadata(
            query="all",
            sources_cited=[],
            result_count=len(results),
            search_type="list",
        ),
    )


@router.get(
    "/compare_sources",
    operation_id="compare_sources",
    response_model=CompareSourcesResponse,
    tags=["sources"],
)
async def compare_sources(
    request: Request,
    topic: str = Query(
        ...,
        description="Topic to compare across sources (e.g., 'rag', 'embeddings', 'chunking')",
    ),
    source_ids: list[str] = Query(
        ...,
        min_length=2,
        description="Source IDs to compare (minimum 2 required for comparison)",
    ),
    limit_per_source: int = Query(
        10, ge=1, le=50, description="Maximum extractions per source"
    ),
    auth_context: AuthContext = Depends(require_tier(UserTier.REGISTERED)),
) -> CompareSourcesResponse:
    """Compare extractions across multiple sources for a topic.

    Returns extractions from specified sources grouped by source for side-by-side
    comparison. Enables Claude to synthesize across different perspectives.

    Requires Registered tier access (valid API key in X-API-Key header).

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
        return CompareSourcesResponse(
            results=[],
            metadata=ComparisonMetadata(
                query=topic,
                sources_cited=[],
                result_count=0,
                search_type="comparison",
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
                message=f"Source not found: {source_id}",
                details={"source_id": source_id},
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

        # Convert extractions to summaries
        extraction_summaries: list[ExtractionSummary] = []
        for extraction in extractions_by_source.get(source_id, []):
            payload = extraction.get("payload", {})

            extraction_summaries.append(
                ExtractionSummary(
                    id=extraction.get("id", ""),
                    type=payload.get("extraction_type", "unknown"),
                    title=_extract_title_from_payload(payload),
                    summary=_extract_summary_from_payload(payload),
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

    latency_ms = (time.time() - start_time) * 1000

    logger.info(
        "compare_sources_complete",
        topic=topic,
        sources_compared=len(results),
        total_extractions=sum(len(r.extractions) for r in results),
        latency_ms=round(latency_ms, 2),
    )

    return CompareSourcesResponse(
        results=results,
        metadata=ComparisonMetadata(
            query=topic,
            sources_cited=sources_cited,
            result_count=len(results),
            search_type="comparison",
        ),
    )
