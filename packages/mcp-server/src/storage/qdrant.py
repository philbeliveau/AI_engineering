"""Qdrant storage client for Knowledge MCP Server.

Provides read-only semantic search access to Qdrant vector collections.
Follows project-context.md:71-77 (mcp-server is READ-ONLY).

Note: Uses asyncio.to_thread() to run sync qdrant_client operations without blocking
the event loop. This is the recommended pattern when using sync drivers in async code.
"""

import asyncio
from typing import Any

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from src.config import Settings
from src.exceptions import ValidationError

logger = structlog.get_logger()

# Per project-context.md:228 - vectors MUST be exactly 384 dimensions
VECTOR_DIMENSIONS = 384


class QdrantStorageClient:
    """Read-only Qdrant client for the Knowledge MCP Server.

    Provides semantic search methods for chunks and extractions.
    All operations are read-only per architecture boundary rules.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize QdrantStorageClient.

        Args:
            settings: Application settings containing Qdrant configuration
        """
        self._settings = settings
        self._client: QdrantClient | None = None

    async def connect(self) -> None:
        """Establish connection to Qdrant.

        Creates a QdrantClient connected to the configured URL.
        Uses asyncio.to_thread() to avoid blocking the event loop.
        """
        logger.info("qdrant_connecting", url=self._settings.qdrant_url)

        def _connect_sync() -> int:
            self._client = QdrantClient(url=self._settings.qdrant_url)
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
    ) -> list[dict[str, Any]]:
        """Semantic search on chunks collection.

        Args:
            query_vector: Query embedding vector (384 dimensions)
            limit: Maximum number of results

        Returns:
            List of matching chunks with scores

        Raises:
            ValidationError: If vector has incorrect dimensions
            RuntimeError: If client not connected
        """
        if not self._client:
            raise RuntimeError("Qdrant client not connected")

        self._validate_vector(query_vector)

        logger.debug(
            "qdrant_search_chunks",
            vector_dims=len(query_vector),
            limit=limit,
        )

        def _search_sync() -> list[dict[str, Any]]:
            results = self._client.search(
                collection_name="chunks",
                query_vector=query_vector,
                limit=limit,
            )
            return [
                {
                    "id": str(hit.id),
                    "score": hit.score,
                    "payload": hit.payload or {},
                }
                for hit in results
            ]

        return await asyncio.to_thread(_search_sync)

    async def search_extractions(
        self,
        query_vector: list[float],
        filter_conditions: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Semantic search on extractions collection.

        Args:
            query_vector: Query embedding vector (384 dimensions)
            filter_conditions: Optional filter conditions (e.g., {"type": "decision"})
            limit: Maximum number of results

        Returns:
            List of matching extractions with scores

        Raises:
            ValidationError: If vector has incorrect dimensions
            RuntimeError: If client not connected
        """
        if not self._client:
            raise RuntimeError("Qdrant client not connected")

        self._validate_vector(query_vector)

        logger.debug(
            "qdrant_search_extractions",
            vector_dims=len(query_vector),
            filter_conditions=filter_conditions,
            limit=limit,
        )

        def _search_sync() -> list[dict[str, Any]]:
            # Build Qdrant filter if conditions provided
            qdrant_filter = None
            if filter_conditions:
                must_conditions = []
                for key, value in filter_conditions.items():
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                qdrant_filter = Filter(must=must_conditions)

            results = self._client.search(
                collection_name="extractions",
                query_vector=query_vector,
                query_filter=qdrant_filter,
                limit=limit,
            )
            return [
                {
                    "id": str(hit.id),
                    "score": hit.score,
                    "payload": hit.payload or {},
                }
                for hit in results
            ]

        return await asyncio.to_thread(_search_sync)
