"""Search knowledge endpoint for MCP Server.

Provides semantic search across chunks and extractions using vector similarity.
Follows project-context.md:54-57 (async endpoints) and architecture.md response format.
"""

import asyncio
import time
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, Query

from src.embeddings.embedding_service import embed_query
from src.models.responses import (
    SearchKnowledgeResponse,
    SearchMetadata,
    SearchResult,
    SourceAttribution,
    SourcePosition,
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


async def _enrich_result(
    hit: dict[str, Any],
    result_type: str,
    mongodb: MongoDBClient,
    source_cache: dict[str, dict[str, Any] | None],
) -> SearchResult | None:
    """Enrich a search hit with source metadata.

    Args:
        hit: Qdrant search hit
        result_type: "chunk" or "extraction"
        mongodb: MongoDB client for enrichment
        source_cache: Cache of source lookups

    Returns:
        SearchResult with source attribution, or None if source not found
    """
    payload = hit.get("payload", {})
    source_id = payload.get("source_id")
    # For chunks, chunk_id is the hit id; for extractions, it's in the payload
    chunk_id = payload.get("chunk_id") if result_type == "extraction" else hit["id"]

    if not source_id:
        logger.warning("search_result_missing_source_id", hit_id=hit["id"])
        return None

    # Get source from cache or fetch
    if source_id not in source_cache:
        source_cache[source_id] = await mongodb.get_source(source_id)

    source_data = source_cache[source_id]
    if not source_data:
        logger.debug("search_result_source_not_found", source_id=source_id)
        # Create minimal source attribution
        source = SourceAttribution(
            source_id=source_id,
            chunk_id=chunk_id,
            title="Unknown Source",
            authors=[],
        )
    else:
        # Build position from payload if available
        position = None
        pos_data = payload.get("position")
        if pos_data and isinstance(pos_data, dict) and "page" in pos_data:
            position = SourcePosition(
                chapter=pos_data.get("chapter"),
                section=pos_data.get("section"),
                page=pos_data.get("page", 0),
            )

        source = SourceAttribution(
            source_id=source_id,
            chunk_id=chunk_id,
            title=source_data.get("title", "Unknown"),
            authors=source_data.get("authors", []),
            position=position,
        )

    # Get content based on type
    if result_type == "chunk":
        content = payload.get("content", "")
    else:
        # For extractions, fetch full content from MongoDB using extraction_id
        extraction_id = payload.get("extraction_id")
        content = ""
        if extraction_id:
            try:
                extraction = await mongodb.get_extraction_by_id(extraction_id)
                if extraction:
                    content_data = extraction.get("content", {})
                    if isinstance(content_data, dict):
                        # Format extraction content for readability
                        content = _format_extraction_content(content_data, payload.get("extraction_type", ""))
                    else:
                        content = str(content_data)
                else:
                    logger.debug("search_extraction_mongodb_not_found", extraction_id=extraction_id)
                    content = payload.get("extraction_title", "")
            except Exception as e:
                logger.warning("search_extraction_mongodb_lookup_failed", extraction_id=extraction_id, error=str(e))
                content = payload.get("extraction_title", "")
        else:
            content = payload.get("extraction_title", "")

    return SearchResult(
        id=hit["id"],
        score=hit["score"],
        type=result_type,
        content=content,
        source=source,
    )


def _format_extraction_content(content: dict[str, Any], extraction_type: str) -> str:
    """Format extraction content dict to readable string.

    Args:
        content: Content dict from MongoDB extraction
        extraction_type: Type of extraction (decision, pattern, warning, methodology)

    Returns:
        Formatted string representation of the content
    """
    parts = []

    # Handle different extraction types
    if extraction_type == "decision":
        if content.get("question"):
            parts.append(f"Question: {content['question']}")
        if content.get("options"):
            parts.append(f"Options: {', '.join(str(o) for o in content['options'])}")
        if content.get("considerations"):
            parts.append(f"Considerations: {', '.join(str(c) for c in content['considerations'])}")
        if content.get("recommended_approach"):
            parts.append(f"Recommended: {content['recommended_approach']}")
    elif extraction_type == "pattern":
        if content.get("name"):
            parts.append(f"Pattern: {content['name']}")
        if content.get("problem"):
            parts.append(f"Problem: {content['problem']}")
        if content.get("solution"):
            parts.append(f"Solution: {content['solution']}")
        if content.get("code_example"):
            parts.append(f"Code: {str(content['code_example'])[:500]}")
    elif extraction_type == "warning":
        if content.get("title"):
            parts.append(f"Warning: {content['title']}")
        if content.get("description"):
            parts.append(f"Description: {content['description']}")
        if content.get("prevention"):
            parts.append(f"Prevention: {content['prevention']}")
    elif extraction_type == "methodology":
        if content.get("name"):
            parts.append(f"Methodology: {content['name']}")
        if content.get("steps"):
            # Steps can be list of dicts with title/description or list of strings
            steps = content["steps"][:5]
            step_strs = []
            for step in steps:
                if isinstance(step, dict):
                    title = step.get("title", step.get("description", str(step)))
                    step_strs.append(str(title))
                else:
                    step_strs.append(str(step))
            parts.append(f"Steps: {'; '.join(step_strs)}")
    else:
        # Generic handling for other extraction types
        for key, value in content.items():
            if value and key not in ["_id", "context_level", "context_id", "chunk_ids"]:
                if isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        # List of dicts - extract main field
                        items = [str(v.get("title", v.get("name", str(v)))) for v in value[:3]]
                        parts.append(f"{key}: {', '.join(items)}")
                    else:
                        parts.append(f"{key}: {', '.join(str(v) for v in value[:5])}")
                else:
                    parts.append(f"{key}: {str(value)[:200]}")

    return " | ".join(parts) if parts else str(content)


@router.post(
    "/search_knowledge",
    operation_id="search_knowledge",
    response_model=SearchKnowledgeResponse,
    tags=["search"],
    summary="Semantic search across all AI engineering knowledge",
    description="""Search across AI engineering knowledge from multiple sources (books, papers, case studies).

## WHEN TO USE
- User asks a general question about AI/ML engineering
- You need to find relevant context before answering
- Starting point for most knowledge queries

## MULTI-QUERY STRATEGY
For comprehensive answers, call this tool 2-3 times with varied queries:
1. User's original phrasing
2. Technical synonyms (e.g., "RAG" → "retrieval augmented generation")
3. Related concepts (e.g., "chunking" → "document splitting", "text segmentation")

## QUERY OPTIMIZATION
- Be specific: "embedding dimension trade-offs" not just "embeddings"
- Include domain context: "RAG chunking" not just "chunking"
- Use technical terms: "vector similarity" not "finding similar things"
- If spec/context is loaded, ALWAYS include domain terms in query

## COMBINE WITH OTHER TOOLS
- After search, call get_decisions() if results mention trade-offs or choices
- Call get_warnings() if implementing something to avoid pitfalls
- Call get_patterns() if looking for implementation examples

## RESULT INTERPRETATION
- Results from multiple sources = synthesize across perspectives
- Low scores (< 0.5) = consider rephrasing query
- Single source dominates = search with different angle for diversity
- If < 3 relevant results, try synonyms or related concepts""",
)
async def search_knowledge(
    query: str = Query(
        ...,
        min_length=1,
        description="Semantic search query. Be specific and use technical terms. Include domain context if spec is loaded. For broad topics, make multiple calls with different phrasings.",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Results to return. Use 10-15 for exploration, 5 for focused queries.",
    ),
) -> SearchKnowledgeResponse:
    """Search across all knowledge content semantically.

    Returns chunks and extractions ranked by relevance to your query.
    Available at Public tier - no authentication required.

    Args:
        query: Natural language search query
        limit: Maximum number of results to return (1-100)

    Returns:
        SearchKnowledgeResponse with results and metadata
    """
    start_time = time.time()
    logger.info("search_knowledge_start", query=query, limit=limit)

    qdrant = get_qdrant_client()
    mongodb = get_mongodb_client()

    # Generate query embedding (CPU-bound, run in thread pool to avoid blocking)
    try:
        query_vector = await asyncio.to_thread(embed_query, query)
    except Exception as e:
        logger.error("embedding_generation_failed", query=query, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to generate query embedding"},
        )

    # Search both collections in parallel for better performance
    chunk_results: list[dict[str, Any]] = []
    extraction_results: list[dict[str, Any]] = []

    if qdrant:
        # Parallel search of chunks and extractions collections
        chunk_results, extraction_results = await asyncio.gather(
            qdrant.search_chunks(query_vector=query_vector, limit=limit),
            qdrant.search_extractions(query_vector=query_vector, limit=limit),
        )

    # Merge and sort by score (descending)
    all_hits = []
    for hit in chunk_results:
        all_hits.append({"hit": hit, "type": "chunk"})
    for hit in extraction_results:
        all_hits.append({"hit": hit, "type": "extraction"})

    all_hits.sort(key=lambda x: x["hit"]["score"], reverse=True)

    # Enrich results with source metadata
    results: list[SearchResult] = []
    sources_cited: set[str] = set()
    source_cache: dict[str, dict[str, Any] | None] = {}

    for item in all_hits[:limit]:
        hit = item["hit"]
        result_type = item["type"]

        if mongodb:
            enriched = await _enrich_result(hit, result_type, mongodb, source_cache)
            if enriched:
                results.append(enriched)
                sources_cited.add(enriched.source.title)
        else:
            # Without MongoDB, create minimal result
            payload = hit.get("payload", {})
            # For chunks, chunk_id is the hit id; for extractions, it's in the payload
            chunk_id = payload.get("chunk_id") if result_type == "extraction" else hit["id"]
            source = SourceAttribution(
                source_id=payload.get("source_id", "unknown"),
                chunk_id=chunk_id,
                title="Unknown",
                authors=[],
            )
            content = payload.get("content", "")
            if isinstance(content, dict):
                content = str(content)
            results.append(
                SearchResult(
                    id=hit["id"],
                    score=hit["score"],
                    type=result_type,
                    content=content,
                    source=source,
                )
            )

    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "search_knowledge_complete",
        query=query,
        result_count=len(results),
        latency_ms=latency_ms,
    )

    return SearchKnowledgeResponse(
        results=results,
        metadata=SearchMetadata(
            query=query,
            sources_cited=sorted(sources_cited),
            result_count=len(results),
            search_type="semantic",
            latency_ms=latency_ms,
        ),
    )
