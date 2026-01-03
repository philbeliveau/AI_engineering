"""Get warnings endpoint for MCP Server.

Provides filtered access to warning extractions stored in Qdrant.
Follows project-context.md:54-57 (async endpoints) and architecture.md response format.

Part of Story 4.3: Extraction Query Tools.
"""

from typing import Any

import structlog
from fastapi import APIRouter, Query

from src.exceptions import KnowledgeError
from src.models.responses import (
    ExtractionMetadata,
    WarningResult,
    WarningsResponse,
)
from src.storage.qdrant import QdrantStorageClient
from src.tools.base import get_qdrant_client as _get_shared_client

logger = structlog.get_logger()

router = APIRouter()

# Module-level client reference - can be overridden for testing
_qdrant_client: QdrantStorageClient | None = None


def set_qdrant_client(qdrant: QdrantStorageClient | None) -> None:
    """Set the module-level Qdrant client.

    Called by server.py during application startup.
    Also sets the shared client in base module for consistency.

    Args:
        qdrant: QdrantStorageClient instance
    """
    global _qdrant_client
    _qdrant_client = qdrant


def get_qdrant_client() -> QdrantStorageClient | None:
    """Get the Qdrant client (module-level or shared)."""
    return _qdrant_client or _get_shared_client()


def _map_warning_payload(extraction_id: str, payload: dict[str, Any]) -> WarningResult:
    """Map Qdrant payload to WarningResult model.

    Args:
        extraction_id: The extraction ID from Qdrant
        payload: The payload dict from Qdrant scroll result

    Returns:
        WarningResult with mapped fields
    """
    # Extract content - may be nested dict or flat
    content = payload.get("content", {})
    if isinstance(content, str):
        # If content is a string, treat it as the description
        content = {"title": "Warning", "description": content}

    return WarningResult(
        id=extraction_id,
        title=content.get("title", payload.get("extraction_title", "Warning")),
        description=content.get("description", ""),
        symptoms=content.get("symptoms"),
        consequences=content.get("consequences"),
        prevention=content.get("prevention"),
        topics=payload.get("topics", []),
        source_title=payload.get("source_title", "Unknown"),
        source_id=payload.get("source_id", ""),
        chunk_id=payload.get("chunk_id"),
    )


@router.get(
    "/get_warnings",
    operation_id="get_warnings",
    response_model=WarningsResponse,
    tags=["extractions"],
)
async def get_warnings(
    topic: str | None = Query(
        default=None,
        description="Filter by topic tag (e.g., 'rag', 'embeddings', 'llm-ops')",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Maximum results to return",
    ),
) -> WarningsResponse:
    """Query warning extractions with optional topic filter.

    Returns AI engineering warnings and pitfalls to avoid.
    Available at Public tier - no authentication required.

    Warnings represent common mistakes and pitfalls like:
    - Anti-patterns in LLM application design
    - Common production failures
    - Security and reliability issues
    - Performance bottlenecks

    Args:
        topic: Optional topic filter (returns extractions containing this topic)
        limit: Maximum number of results to return (1-500)

    Returns:
        WarningsResponse with results and metadata
    """
    logger.info("get_warnings_start", topic=topic, limit=limit)

    qdrant = get_qdrant_client()
    if not qdrant:
        logger.warning("get_warnings_no_client")
        return WarningsResponse(
            results=[],
            metadata=ExtractionMetadata(
                query=topic or "all",
                sources_cited=[],
                result_count=0,
                search_type="filtered",
            ),
        )

    # Query Qdrant for warning extractions with error handling
    try:
        raw_results = await qdrant.list_extractions(
            extraction_type="warning",
            limit=limit,
            topic=topic,
        )
    except RuntimeError as e:
        logger.error("get_warnings_qdrant_error", error=str(e), topic=topic)
        raise KnowledgeError(
            code="INTERNAL_ERROR",
            message="Failed to query warning extractions",
            details={"error": str(e)},
        ) from e
    except Exception as e:
        logger.error("get_warnings_unexpected_error", error=str(e), topic=topic)
        raise KnowledgeError(
            code="INTERNAL_ERROR",
            message="Unexpected error querying warnings",
            details={"error_type": type(e).__name__},
        ) from e

    # Map results to response models
    results: list[WarningResult] = []
    sources_cited: set[str] = set()

    for item in raw_results:
        payload = item.get("payload", {})
        warning = _map_warning_payload(item["id"], payload)
        results.append(warning)
        if warning.source_title and warning.source_title != "Unknown":
            sources_cited.add(warning.source_title)

    logger.info(
        "get_warnings_complete",
        topic=topic,
        result_count=len(results),
        sources_count=len(sources_cited),
    )

    return WarningsResponse(
        results=results,
        metadata=ExtractionMetadata(
            query=topic or "all",
            sources_cited=sorted(sources_cited),
            result_count=len(results),
            search_type="filtered",
        ),
    )
