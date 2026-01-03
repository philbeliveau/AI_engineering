"""Qdrant storage client for Knowledge MCP Server.

Provides read-only semantic search access to Qdrant vector collections.
Follows project-context.md:71-77 (mcp-server is READ-ONLY).

Uses single-collection architecture with payload-based filtering:
- All vectors (chunks and extractions) stored in 'knowledge_vectors' collection
- content_type field discriminates between 'chunk' and 'extraction'
- project_id field enables multi-project isolation
- extraction_type field filters extraction types (decision, pattern, etc.)

Note: Uses asyncio.to_thread() to run sync qdrant_client operations without blocking
the event loop. This is the recommended pattern when using sync drivers in async code.
"""

import asyncio
from typing import Any

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

from src.config import KNOWLEDGE_VECTORS_COLLECTION, Settings
from src.exceptions import ValidationError

logger = structlog.get_logger()

# Per project-context.md:228 - vectors MUST be exactly 384 dimensions
VECTOR_DIMENSIONS = 384

# Content type discriminator values for single-collection architecture
CONTENT_TYPE_CHUNK = "chunk"
CONTENT_TYPE_EXTRACTION = "extraction"


class QdrantStorageClient:
    """Read-only Qdrant client for the Knowledge MCP Server.

    Provides semantic search methods for chunks and extractions using
    single-collection architecture with payload-based filtering.

    All operations are read-only per architecture boundary rules.
    All queries are scoped by project_id for multi-project isolation.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize QdrantStorageClient.

        Args:
            settings: Application settings containing Qdrant configuration
        """
        self._settings = settings
        self._client: QdrantClient | None = None
        self._collection = KNOWLEDGE_VECTORS_COLLECTION

    async def connect(self) -> None:
        """Establish connection to Qdrant.

        Creates a QdrantClient connected to the configured URL.
        Uses asyncio.to_thread() to avoid blocking the event loop.
        """
        logger.info("qdrant_connecting", url=self._settings.qdrant_url)

        def _connect_sync() -> int:
            # Configure client with API key for Qdrant Cloud
            self._client = QdrantClient(
                url=self._settings.qdrant_url,
                api_key=self._settings.qdrant_api_key,
                timeout=30,
            )
            # Verify connection by checking cluster health
            info = self._client.get_collections()
            return len(info.collections)

        collection_count = await asyncio.to_thread(_connect_sync)
        logger.info("qdrant_connected", collection_count=collection_count)

    async def disconnect(self) -> None:
        """Close the Qdrant connection."""
        if self._client:
            await asyncio.to_thread(self._client.close)
            self._client = None
            logger.info("qdrant_disconnected")

    async def ping(self) -> bool:
        """Check if Qdrant connection is healthy.

        Returns:
            True if connection is healthy, False otherwise.
        """
        if not self._client:
            return False
        try:
            await asyncio.to_thread(self._client.get_collections)
            return True
        except Exception:
            return False

    def _validate_vector(self, query_vector: list[float]) -> None:
        """Validate vector dimensions.

        Args:
            query_vector: Vector to validate

        Raises:
            ValidationError: If vector has incorrect dimensions
        """
        if len(query_vector) != VECTOR_DIMENSIONS:
            raise ValidationError(
                message=f"Vector must have exactly {VECTOR_DIMENSIONS} dimensions",
                details={
                    "expected_dimensions": VECTOR_DIMENSIONS,
                    "actual_dimensions": len(query_vector),
                },
            )

    async def search_chunks(
        self,
        query_vector: list[float],
        limit: int = 10,
        project_id: str | None = None,
        source_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic search for chunks in unified collection.

        Uses content_type filter to return only chunk vectors.

        Args:
            query_vector: Query embedding vector (384 dimensions)
            limit: Maximum number of results
            project_id: Override project filter (defaults to settings.project_id)
            source_id: Optional source_id filter

        Returns:
            List of matching chunks with scores

        Raises:
            ValidationError: If vector has incorrect dimensions
            RuntimeError: If client not connected
        """
        if not self._client:
            raise RuntimeError("Qdrant client not connected")

        self._validate_vector(query_vector)

        effective_project_id = project_id or self._settings.project_id

        logger.debug(
            "qdrant_search_chunks",
            vector_dims=len(query_vector),
            limit=limit,
            project_id=effective_project_id,
        )

        def _search_sync() -> list[dict[str, Any]]:
            # Build filter for chunks with project isolation
            must_conditions = [
                FieldCondition(key="project_id", match=MatchValue(value=effective_project_id)),
                FieldCondition(key="content_type", match=MatchValue(value=CONTENT_TYPE_CHUNK)),
            ]
            if source_id:
                must_conditions.append(
                    FieldCondition(key="source_id", match=MatchValue(value=source_id))
                )

            qdrant_filter = Filter(must=must_conditions)

            # Use query_points (newer API) instead of deprecated search
            response = self._client.query_points(
                collection_name=self._collection,
                query=query_vector,
                query_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
            )
            return [
                {
                    "id": str(point.id),
                    "score": point.score,
                    "payload": point.payload or {},
                }
                for point in response.points
            ]

        return await asyncio.to_thread(_search_sync)

    async def search_extractions(
        self,
        query_vector: list[float],
        limit: int = 10,
        project_id: str | None = None,
        extraction_type: str | None = None,
        source_id: str | None = None,
        topics: list[str] | None = None,
        source_type: str | None = None,
        source_category: str | None = None,
        source_year: int | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic search for extractions in unified collection.

        Uses content_type filter to return only extraction vectors.
        Supports filtering by extraction_type, topics, and source metadata.

        Args:
            query_vector: Query embedding vector (384 dimensions)
            limit: Maximum number of results
            project_id: Override project filter (defaults to settings.project_id)
            extraction_type: Filter by type (decision, pattern, warning, etc.)
            source_id: Optional source_id filter
            topics: Filter by topics (match any)
            source_type: Filter by source type (book, paper, case_study)
            source_category: Filter by category (foundational, advanced, etc.)
            source_year: Filter by publication year

        Returns:
            List of matching extractions with scores

        Raises:
            ValidationError: If vector has incorrect dimensions
            RuntimeError: If client not connected
        """
        if not self._client:
            raise RuntimeError("Qdrant client not connected")

        self._validate_vector(query_vector)

        effective_project_id = project_id or self._settings.project_id

        logger.debug(
            "qdrant_search_extractions",
            vector_dims=len(query_vector),
            limit=limit,
            project_id=effective_project_id,
            extraction_type=extraction_type,
            source_year=source_year,
        )

        def _search_sync() -> list[dict[str, Any]]:
            # Build filter for extractions with project isolation
            must_conditions = [
                FieldCondition(key="project_id", match=MatchValue(value=effective_project_id)),
                FieldCondition(key="content_type", match=MatchValue(value=CONTENT_TYPE_EXTRACTION)),
            ]

            if extraction_type:
                must_conditions.append(
                    FieldCondition(key="extraction_type", match=MatchValue(value=extraction_type))
                )
            if source_id:
                must_conditions.append(
                    FieldCondition(key="source_id", match=MatchValue(value=source_id))
                )
            if topics:
                must_conditions.append(
                    FieldCondition(key="topics", match=MatchAny(any=topics))
                )
            if source_type:
                must_conditions.append(
                    FieldCondition(key="source_type", match=MatchValue(value=source_type))
                )
            if source_category:
                must_conditions.append(
                    FieldCondition(key="source_category", match=MatchValue(value=source_category))
                )
            if source_year:
                must_conditions.append(
                    FieldCondition(key="source_year", match=MatchValue(value=source_year))
                )

            qdrant_filter = Filter(must=must_conditions)

            # Use query_points (newer API) instead of deprecated search
            response = self._client.query_points(
                collection_name=self._collection,
                query=query_vector,
                query_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
            )
            return [
                {
                    "id": str(point.id),
                    "score": point.score,
                    "payload": point.payload or {},
                }
                for point in response.points
            ]

        return await asyncio.to_thread(_search_sync)

    async def search_knowledge(
        self,
        query_vector: list[float],
        limit: int = 10,
        project_id: str | None = None,
        content_type: str | None = None,
        extraction_type: str | None = None,
        source_id: str | None = None,
        topics: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """General-purpose semantic search on unified collection.

        Returns both chunks and extractions by default, or filtered by content_type.

        Args:
            query_vector: Query embedding vector (384 dimensions)
            limit: Maximum number of results
            project_id: Override project filter (defaults to settings.project_id)
            content_type: Filter by 'chunk' or 'extraction' (optional)
            extraction_type: Filter by extraction type (only applies to extractions)
            source_id: Optional source_id filter
            topics: Filter by topics (match any)

        Returns:
            List of matching results with scores

        Raises:
            ValidationError: If vector has incorrect dimensions
            RuntimeError: If client not connected
        """
        if not self._client:
            raise RuntimeError("Qdrant client not connected")

        self._validate_vector(query_vector)

        effective_project_id = project_id or self._settings.project_id

        logger.debug(
            "qdrant_search_knowledge",
            vector_dims=len(query_vector),
            limit=limit,
            project_id=effective_project_id,
            content_type=content_type,
        )

        def _search_sync() -> list[dict[str, Any]]:
            # Build filter with project isolation
            must_conditions = [
                FieldCondition(key="project_id", match=MatchValue(value=effective_project_id)),
            ]

            if content_type:
                must_conditions.append(
                    FieldCondition(key="content_type", match=MatchValue(value=content_type))
                )
            if extraction_type:
                must_conditions.append(
                    FieldCondition(key="extraction_type", match=MatchValue(value=extraction_type))
                )
            if source_id:
                must_conditions.append(
                    FieldCondition(key="source_id", match=MatchValue(value=source_id))
                )
            if topics:
                must_conditions.append(
                    FieldCondition(key="topics", match=MatchAny(any=topics))
                )

            qdrant_filter = Filter(must=must_conditions)

            # Use query_points (newer API) instead of deprecated search
            response = self._client.query_points(
                collection_name=self._collection,
                query=query_vector,
                query_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
            )
            return [
                {
                    "id": str(point.id),
                    "score": point.score,
                    "payload": point.payload or {},
                }
                for point in response.points
            ]

        return await asyncio.to_thread(_search_sync)

    async def list_extractions(
        self,
        extraction_type: str,
        limit: int = 100,
        project_id: str | None = None,
        topic: str | None = None,
    ) -> list[dict[str, Any]]:
        """List extractions by type without semantic search.

        Uses Qdrant scroll API to list extractions filtered by type and optional topic.
        No embedding required - returns all matching extractions up to limit.

        Args:
            extraction_type: Type of extraction (decision, pattern, warning, etc.)
            limit: Maximum number of results to return
            project_id: Override project filter (defaults to settings.project_id)
            topic: Optional topic filter (returns extractions containing this topic)

        Returns:
            List of extraction payloads from Qdrant

        Raises:
            RuntimeError: If client not connected
        """
        if not self._client:
            raise RuntimeError("Qdrant client not connected")

        effective_project_id = project_id or self._settings.project_id

        logger.debug(
            "qdrant_list_extractions",
            extraction_type=extraction_type,
            limit=limit,
            project_id=effective_project_id,
            topic=topic,
        )

        def _scroll_sync() -> list[dict[str, Any]]:
            # Build filter for extractions with project isolation
            must_conditions = [
                FieldCondition(key="project_id", match=MatchValue(value=effective_project_id)),
                FieldCondition(key="content_type", match=MatchValue(value=CONTENT_TYPE_EXTRACTION)),
                FieldCondition(key="extraction_type", match=MatchValue(value=extraction_type)),
            ]

            if topic:
                must_conditions.append(
                    FieldCondition(key="topics", match=MatchAny(any=[topic]))
                )

            qdrant_filter = Filter(must=must_conditions)

            # Use scroll for non-semantic listing
            results, _next_offset = self._client.scroll(
                collection_name=self._collection,
                scroll_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,  # Don't need vectors for listing
            )

            return [
                {
                    "id": str(point.id),
                    "payload": point.payload or {},
                }
                for point in results
            ]

        return await asyncio.to_thread(_scroll_sync)
