"""Methodology query endpoint for MCP Server.

Provides access to methodology extractions (step-by-step processes) from the knowledge base.
Requires Registered tier authentication (API key required).

Follows project-context.md:54-57 (async endpoints), architecture.md response format,
and architecture.md:315-327 tiered authentication model.
"""

import time
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Query, Request

from src.middleware.auth import require_tier
from src.models.auth import AuthContext, UserTier
from src.models.responses import (
    ExtractionMetadata,
    MethodologyResponse,
    MethodologyResult,
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


def _map_methodology_from_mongodb(
    point_id: str,
    extraction: dict[str, Any],
    payload: dict[str, Any],
    source_title: str,
) -> MethodologyResult | None:
    """Convert MongoDB extraction to MethodologyResult.

    Args:
        point_id: Qdrant point ID
        extraction: Full extraction document from MongoDB
        payload: Qdrant point payload (for fallback metadata)
        source_title: Human-readable source title

    Returns:
        MethodologyResult with full content from MongoDB, or None if invalid
    """
    content = extraction.get("content", {})
    if not isinstance(content, dict):
        logger.warning(
            "methodology_invalid_content_format",
            point_id=point_id,
            content_type=type(content).__name__,
        )
        return None

    name = content.get("name", "")
    steps = content.get("steps", [])

    if not name or not steps:
        logger.warning(
            "methodology_missing_required_fields",
            point_id=point_id,
            has_name=bool(name),
            has_steps=bool(steps),
        )
        return None

    return MethodologyResult(
        id=point_id,
        name=name,
        steps=steps,
        prerequisites=content.get("prerequisites"),
        outputs=content.get("outputs"),
        topics=extraction.get("topics", payload.get("topics", [])),
        source_title=source_title,
        source_id=extraction.get("source_id", payload.get("source_id", "")),
        chunk_id=extraction.get("chunk_id", payload.get("chunk_id")),
    )


def _payload_to_methodology_result(
    point_id: str,
    payload: dict[str, Any],
    source_title: str,
) -> MethodologyResult | None:
    """Convert Qdrant payload to MethodologyResult (fallback when MongoDB unavailable).

    Args:
        point_id: Qdrant point ID
        payload: Qdrant point payload
        source_title: Human-readable source title (from MongoDB or payload)

    Returns:
        MethodologyResult with partial data, or None if invalid
    """
    # Fallback returns minimal data since content is not in Qdrant payload
    name = payload.get("extraction_title", "")

    if not name:
        logger.warning(
            "methodology_missing_required_fields",
            point_id=point_id,
            has_name=False,
            has_steps=False,
        )
        return None

    return MethodologyResult(
        id=point_id,
        name=name,
        steps=[],  # Content not available in Qdrant payload
        prerequisites=None,
        outputs=None,
        topics=payload.get("topics", []),
        source_title=source_title,
        source_id=payload.get("source_id", ""),
        chunk_id=payload.get("chunk_id"),
    )


@router.get(
    "/get_methodologies",
    operation_id="get_methodologies",
    response_model=MethodologyResponse,
    tags=["extractions"],
    summary="Query step-by-step AI engineering methodologies and processes",
    description="""Query structured methodologies for AI engineering processes.

## WHEN TO USE
- User asks "what's the process for X?"
- User needs end-to-end guidance (not just a code snippet)
- User is planning a project or workflow
- User asks about evaluation, testing, or deployment flows

## METHODOLOGY STRUCTURE
Each methodology includes:
- Steps: Ordered sequence of actions
- Prerequisites: What you need before starting
- Outputs: What you'll have when done

## WHEN NOT TO USE
- User wants quick code snippet → use get_patterns()
- User needs to make a choice → use get_decisions()
- User has specific implementation question → use search_knowledge()

## SYNTHESIS GUIDANCE
- Present steps in order, don't skip ahead
- Adapt methodology to user's specific context from loaded spec
- Combine with get_patterns() for implementation details of each step
- Check get_warnings() for pitfalls at critical steps

## COMBINE WITH
- get_patterns() → detailed implementation for each step
- get_warnings() → pitfalls to avoid during the process
- get_decisions() → when methodology has choice points""",
)
async def get_methodologies(
    request: Request,
    topic: str = Query(
        "",
        description="Topic filter: 'rag', 'fine-tuning', 'prompt-engineering', 'evaluation', 'deployment'. Include domain from loaded spec.",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Max results. Use 5-10 for specific processes.",
    ),
    auth_context: AuthContext = Depends(require_tier(UserTier.PUBLIC)),
) -> MethodologyResponse:
    """Get step-by-step methodology extractions from the knowledge base.

    Returns methodologies extracted from AI engineering books and papers.
    Each methodology includes steps, prerequisites, and expected outputs.

    Args:
        request: FastAPI request object
        topic: Optional topic filter (matches any methodology with this topic)
        limit: Maximum number of results to return (default 100)
        auth_context: Authentication context (injected by require_tier)

    Returns:
        MethodologyResponse with results and metadata
    """
    start_time = time.time()
    query_str = topic or "all"

    logger.info(
        "get_methodologies_start",
        topic=topic,
        limit=limit,
        user_tier=auth_context.tier.value,
    )

    qdrant = get_qdrant_client()
    mongodb = get_mongodb_client()

    if not qdrant:
        logger.error("qdrant_client_not_available")
        latency_ms = int((time.time() - start_time) * 1000)
        return MethodologyResponse(
            results=[],
            metadata=ExtractionMetadata(
                query=query_str,
                sources_cited=[],
                result_count=0,
                search_type="filtered",
                latency_ms=latency_ms,
            ),
        )

    # Query Qdrant for methodology extractions
    raw_results = await qdrant.list_extractions(
        extraction_type="methodology",
        limit=limit,
        topic=topic,
    )

    # Build source cache for enrichment
    source_cache: dict[str, dict[str, Any] | None] = {}
    results: list[MethodologyResult] = []
    sources_cited: set[str] = set()

    for item in raw_results:
        point_id = item["id"]
        payload = item.get("payload", {})
        source_id = payload.get("source_id", "")
        extraction_id = payload.get("extraction_id")

        # Get source title from MongoDB or payload
        source_title = payload.get("source_title", "Unknown Source")
        if mongodb and source_id and source_title == "Unknown Source":
            if source_id not in source_cache:
                source_cache[source_id] = await mongodb.get_source(source_id)
            source_data = source_cache.get(source_id)
            if source_data:
                source_title = source_data.get("title", "Unknown Source")

        # Try to get full content from MongoDB
        methodology = None
        if mongodb and extraction_id:
            try:
                extraction = await mongodb.get_extraction_by_id(extraction_id)
                if extraction:
                    methodology = _map_methodology_from_mongodb(point_id, extraction, payload, source_title)
                else:
                    logger.debug("methodology_mongodb_not_found", extraction_id=extraction_id)
                    methodology = _payload_to_methodology_result(point_id, payload, source_title)
            except Exception as e:
                logger.warning("methodology_mongodb_lookup_failed", extraction_id=extraction_id, error=str(e))
                methodology = _payload_to_methodology_result(point_id, payload, source_title)
        else:
            methodology = _payload_to_methodology_result(point_id, payload, source_title)

        if methodology:
            results.append(methodology)
            sources_cited.add(source_title)

    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "get_methodologies_complete",
        topic=topic,
        result_count=len(results),
        sources_cited=len(sources_cited),
        latency_ms=latency_ms,
    )

    return MethodologyResponse(
        results=results,
        metadata=ExtractionMetadata(
            query=query_str,
            sources_cited=sorted(sources_cited),
            result_count=len(results),
            search_type="filtered",
            latency_ms=latency_ms,
        ),
    )
