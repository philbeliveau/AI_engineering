"""Get patterns endpoint for MCP Server.

Provides filtered access to pattern extractions stored in Qdrant.
Follows project-context.md:54-57 (async endpoints) and architecture.md response format.

Part of Story 4.3: Extraction Query Tools.
"""

import time
from typing import Any

import structlog
from fastapi import APIRouter, Query

from src.exceptions import KnowledgeError
from src.models.responses import (
    ExtractionMetadata,
    PatternResult,
    PatternsResponse,
)
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient
from src.tools.base import get_qdrant_client as _get_shared_client

logger = structlog.get_logger()

router = APIRouter()

# Module-level client references - can be overridden for testing
_qdrant_client: QdrantStorageClient | None = None
_mongodb_client: MongoDBClient | None = None


def set_clients(
    qdrant: QdrantStorageClient | None, mongodb: MongoDBClient | None
) -> None:
    """Set the module-level storage clients.

    Called by server.py during application startup.

    Args:
        qdrant: QdrantStorageClient instance
        mongodb: MongoDBClient instance
    """
    global _qdrant_client, _mongodb_client
    _qdrant_client = qdrant
    _mongodb_client = mongodb


def set_qdrant_client(qdrant: QdrantStorageClient | None) -> None:
    """Set the module-level Qdrant client (legacy, use set_clients instead)."""
    global _qdrant_client
    _qdrant_client = qdrant


def get_qdrant_client() -> QdrantStorageClient | None:
    """Get the Qdrant client (module-level or shared)."""
    return _qdrant_client or _get_shared_client()


def get_mongodb_client() -> MongoDBClient | None:
    """Get the MongoDB client."""
    return _mongodb_client


def _map_pattern_from_mongodb(
    extraction_id: str, extraction: dict[str, Any], payload: dict[str, Any]
) -> PatternResult:
    """Map MongoDB extraction to PatternResult model.

    Args:
        extraction_id: The extraction ID
        extraction: Full extraction document from MongoDB
        payload: The payload dict from Qdrant (for fallback metadata)

    Returns:
        PatternResult with full content from MongoDB
    """
    content = extraction.get("content", {})
    if isinstance(content, str):
        content = {"name": "Pattern", "problem": "", "solution": content}

    return PatternResult(
        id=extraction_id,
        name=content.get("name", payload.get("extraction_title", "Unknown Pattern")),
        problem=content.get("problem", ""),
        solution=content.get("solution", ""),
        code_example=content.get("code_example"),
        context=content.get("context"),
        trade_offs=content.get("trade_offs"),
        topics=extraction.get("topics", payload.get("topics", [])),
        source_title=payload.get("source_title", "Unknown"),
        source_id=extraction.get("source_id", payload.get("source_id", "")),
        chunk_id=extraction.get("chunk_id", payload.get("chunk_id")),
    )


def _map_pattern_payload(extraction_id: str, payload: dict[str, Any]) -> PatternResult:
    """Map Qdrant payload to PatternResult model (fallback when MongoDB unavailable).

    Args:
        extraction_id: The extraction ID from Qdrant
        payload: The payload dict from Qdrant scroll result

    Returns:
        PatternResult with partial data from Qdrant payload
    """
    return PatternResult(
        id=extraction_id,
        name=payload.get("extraction_title", "Unknown Pattern"),
        problem="",
        solution="",
        code_example=None,
        context=None,
        trade_offs=None,
        topics=payload.get("topics", []),
        source_title=payload.get("source_title", "Unknown"),
        source_id=payload.get("source_id", ""),
        chunk_id=payload.get("chunk_id"),
    )


@router.get(
    "/get_patterns",
    operation_id="get_patterns",
    response_model=PatternsResponse,
    tags=["extractions"],
    summary="Query reusable AI engineering patterns with code examples",
    description="""Query implementation patterns extracted from AI engineering sources.

## WHEN TO USE
- User asks "how do I implement X?"
- User wants code examples or templates
- User is ready to build (decision already made)
- After get_decisions() when user has chosen an approach

## WHEN NOT TO USE
- User is still deciding between approaches → use get_decisions()
- User asks about risks or pitfalls → use get_warnings()
- User has a vague question → use search_knowledge() first

## PATTERN STRUCTURE
Each pattern includes:
- Problem: What situation this solves
- Solution: How to implement it
- Code example: Working code snippet (when available)
- Trade-offs: What you gain/lose with this approach

## MULTI-PATTERN STRATEGY
For complex implementations, retrieve patterns for:
1. Main concept (e.g., "semantic chunking")
2. Supporting concerns (e.g., "chunk overlap", "metadata extraction")
3. Error handling (e.g., "chunking edge cases")

## SYNTHESIS GUIDANCE
- Adapt code examples to user's stack (Python/JS/etc.)
- Combine multiple patterns for complete solution
- If spec is loaded, prioritize patterns matching domain/scale
- ALWAYS pair with get_warnings() before implementation""",
)
async def get_patterns(
    topic: str | None = Query(
        default=None,
        description="Topic filter: 'rag', 'embeddings', 'chunking', 'prompt-engineering', 'evaluation'. Include domain from loaded spec if available.",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Max results. Use 10-20 for specific implementations.",
    ),
) -> PatternsResponse:
    """Query pattern extractions with optional topic filter.

    Returns AI engineering patterns with problem, solution, and code examples.
    Available at Public tier - no authentication required.

    Patterns represent reusable solutions like:
    - RAG implementation patterns
    - Prompt engineering techniques
    - Error handling strategies
    - Caching and optimization patterns

    Args:
        topic: Optional topic filter (returns extractions containing this topic)
        limit: Maximum number of results to return (1-500)

    Returns:
        PatternsResponse with results and metadata
    """
    start_time = time.time()
    logger.info("get_patterns_start", topic=topic, limit=limit)

    qdrant = get_qdrant_client()
    if not qdrant:
        logger.warning("get_patterns_no_client")
        latency_ms = int((time.time() - start_time) * 1000)
        return PatternsResponse(
            results=[],
            metadata=ExtractionMetadata(
                query=topic or "all",
                sources_cited=[],
                result_count=0,
                search_type="filtered",
                latency_ms=latency_ms,
            ),
        )

    # Query Qdrant for pattern extractions with error handling
    try:
        raw_results = await qdrant.list_extractions(
            extraction_type="pattern",
            limit=limit,
            topic=topic,
        )
    except RuntimeError as e:
        logger.error("get_patterns_qdrant_error", error=str(e), topic=topic)
        raise KnowledgeError(
            code="INTERNAL_ERROR",
            message="Failed to query pattern extractions",
            details={"error": str(e)},
        ) from e
    except Exception as e:
        logger.error("get_patterns_unexpected_error", error=str(e), topic=topic)
        raise KnowledgeError(
            code="INTERNAL_ERROR",
            message="Unexpected error querying patterns",
            details={"error_type": type(e).__name__},
        ) from e

    # Map results to response models with MongoDB enrichment
    results: list[PatternResult] = []
    sources_cited: set[str] = set()
    mongodb = get_mongodb_client()

    for item in raw_results:
        payload = item.get("payload", {})
        extraction_id = payload.get("extraction_id")

        # Try to get full content from MongoDB
        if mongodb and extraction_id:
            try:
                extraction = await mongodb.get_extraction_by_id(extraction_id)
                if extraction:
                    pattern = _map_pattern_from_mongodb(item["id"], extraction, payload)
                else:
                    logger.debug("pattern_mongodb_not_found", extraction_id=extraction_id)
                    pattern = _map_pattern_payload(item["id"], payload)
            except Exception as e:
                logger.warning("pattern_mongodb_lookup_failed", extraction_id=extraction_id, error=str(e))
                pattern = _map_pattern_payload(item["id"], payload)
        else:
            pattern = _map_pattern_payload(item["id"], payload)

        results.append(pattern)
        if pattern.source_title and pattern.source_title != "Unknown":
            sources_cited.add(pattern.source_title)

    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "get_patterns_complete",
        topic=topic,
        result_count=len(results),
        sources_count=len(sources_cited),
        latency_ms=latency_ms,
    )

    return PatternsResponse(
        results=results,
        metadata=ExtractionMetadata(
            query=topic or "all",
            sources_cited=sorted(sources_cited),
            result_count=len(results),
            search_type="filtered",
            latency_ms=latency_ms,
        ),
    )
