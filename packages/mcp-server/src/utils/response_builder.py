"""Response builder utilities for Knowledge MCP Server.

Provides helper functions to build standardized API responses with
latency tracking for NFR1 compliance (<500ms target).

Story 4.6: Response builder utilities for DRY code.
"""

import time
from typing import Literal, TypeVar

from src.models.responses import ApiResponse, ResponseMetadata

T = TypeVar("T")


def build_response(
    results: list[T],
    query: str,
    sources: list[str],
    search_type: Literal["semantic", "filtered", "list", "comparison"],
    start_time: float,
) -> ApiResponse[T]:
    """Build standardized API response with timing.

    Automatically calculates latency_ms from start_time for NFR1 tracking.

    Args:
        results: List of result objects (type-safe)
        query: Original query string or filter description
        sources: List of source titles cited in results
        search_type: Type of search performed
        start_time: Start time from time.time() call

    Returns:
        ApiResponse with results and metadata including latency

    Example:
        start_time = time.time()
        results = await perform_search(query)
        return build_response(
            results=results,
            query=query,
            sources=extract_sources(results),
            search_type="semantic",
            start_time=start_time
        )
    """
    latency_ms = int((time.time() - start_time) * 1000)

    return ApiResponse(
        results=results,
        metadata=ResponseMetadata(
            query=query,
            sources_cited=sources,
            result_count=len(results),
            search_type=search_type,
            latency_ms=latency_ms,
        ),
    )


def build_empty_response(
    query: str,
    search_type: Literal["semantic", "filtered", "list", "comparison"],
    start_time: float,
) -> ApiResponse:
    """Build response for empty result sets.

    Convenience function for returning empty results while maintaining
    the standard response format and latency tracking.

    Args:
        query: Original query string or filter description
        search_type: Type of search performed
        start_time: Start time from time.time() call

    Returns:
        ApiResponse with empty results and metadata including latency
    """
    return build_response(
        results=[],
        query=query,
        sources=[],
        search_type=search_type,
        start_time=start_time,
    )
