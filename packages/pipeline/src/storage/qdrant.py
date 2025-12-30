"""Qdrant storage client for vector storage and semantic search operations.

This module provides a client for interacting with Qdrant vector database,
supporting vector upsert, semantic search, and collection management operations.
"""

import uuid
from typing import Any

import structlog
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from src.config import settings
from src.exceptions import (
    QdrantCollectionError,
    QdrantConnectionError,
    QdrantVectorError,
)

logger = structlog.get_logger()

# Constants from architecture requirements
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension
DISTANCE_METRIC = Distance.COSINE

# Collection names from architecture
CHUNKS_COLLECTION = "chunks"
EXTRACTIONS_COLLECTION = "extractions"

# Namespace for generating deterministic UUIDs from string IDs
QDRANT_UUID_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _string_to_uuid(string_id: str) -> str:
    """Convert a string ID to a UUID string for Qdrant.

    Uses UUID5 (SHA-1 based, deterministic) to generate consistent UUIDs
    from arbitrary string IDs (e.g., MongoDB ObjectIds).

    Args:
        string_id: The string ID to convert.

    Returns:
        UUID string compatible with Qdrant.
    """
    return str(uuid.uuid5(QDRANT_UUID_NAMESPACE, string_id))


class QdrantStorageClient:
    """Qdrant client for vector storage and semantic search operations.

    This client provides methods for:
    - Collection management (create, ensure exists)
    - Vector upsert (single and batch)
    - Semantic search with optional filtering
    - Vector deletion by ID or source

    All vectors must be exactly 384 dimensions (all-MiniLM-L6-v2 output).
    Uses Cosine distance metric for similarity search.

    Attributes:
        url: Qdrant server URL.
        client: Underlying QdrantClient instance.
    """

    def __init__(self, url: str | None = None):
        """Initialize Qdrant client with connection to Qdrant server.

        Args:
            url: Qdrant server URL. Defaults to settings.qdrant_url.

        Raises:
            QdrantConnectionError: If connection to Qdrant fails.
        """
        self.url = url or settings.qdrant_url
        try:
            self.client = QdrantClient(url=self.url)
            logger.info("qdrant_client_initialized", url=self.url)
        except Exception as e:
            raise QdrantConnectionError(
                code="QDRANT_CONNECTION_FAILED",
                message=f"Failed to connect to Qdrant at {self.url}",
                details={"url": self.url, "error": str(e)},
            )

    def health_check(self) -> bool:
        """Check if Qdrant is healthy and accessible.

        Sync function - uses sync Qdrant client for consistency with other methods.

        Returns:
            True if Qdrant is accessible, False otherwise.
        """
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

    def ensure_collection(self, collection_name: str, create_indexes: bool = True) -> None:
        """Create collection if it doesn't exist.

        Creates a collection with 384-dimensional vectors and Cosine distance metric.
        If the collection already exists, this method does nothing.

        For the 'extractions' collection, payload indexes are created on 'type' and
        'topics' fields for optimized filtered search performance (NFR1: <500ms).

        Args:
            collection_name: Name of the collection to create/verify.
            create_indexes: Whether to create payload indexes for filtered search.

        Raises:
            QdrantCollectionError: If collection creation fails.
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=DISTANCE_METRIC,
                    ),
                )
                logger.info("qdrant_collection_created", collection=collection_name)

                # Create payload indexes for filtered search performance
                if create_indexes and collection_name == EXTRACTIONS_COLLECTION:
                    self._create_payload_indexes(collection_name)
            else:
                logger.debug("qdrant_collection_exists", collection=collection_name)
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_COLLECTION_ERROR",
                message=f"Failed to ensure collection {collection_name}",
                details={"collection": collection_name, "error": str(e)},
            )

    def _create_payload_indexes(self, collection_name: str) -> None:
        """Create payload indexes for optimized filtered search.

        Creates keyword indexes on 'type', 'topics', and 'source_id' fields
        to improve filtered search performance per NFR1 (<500ms latency).

        Args:
            collection_name: Target collection name.
        """
        index_fields = ["type", "topics", "source_id"]
        for field in index_fields:
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema="keyword",
                )
                logger.debug("payload_index_created", collection=collection_name, field=field)
            except Exception as e:
                # Log but don't fail - index might already exist
                logger.warning(
                    "payload_index_creation_skipped",
                    collection=collection_name,
                    field=field,
                    reason=str(e),
                )

    def _validate_vector_size(self, vector: list[float], context: str = "vector") -> None:
        """Validate that vector has exactly 384 dimensions.

        Args:
            vector: The embedding vector to validate.
            context: Context string for error messages.

        Raises:
            QdrantVectorError: If vector size is not 384.
        """
        if len(vector) != VECTOR_SIZE:
            raise QdrantVectorError(
                code="INVALID_VECTOR_SIZE",
                message=f"{context} must be {VECTOR_SIZE} dimensions, got {len(vector)}",
                details={"expected": VECTOR_SIZE, "actual": len(vector)},
            )

    def upsert_chunk_vector(
        self,
        chunk_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Upsert a chunk vector into the chunks collection.

        Args:
            chunk_id: Unique identifier for the chunk (MongoDB ObjectId format).
            vector: 384-dimensional embedding vector.
            payload: Metadata payload (must include source_id, chunk_id).

        Raises:
            QdrantVectorError: If vector size is not 384.
            QdrantCollectionError: If upsert operation fails.
        """
        self._validate_vector_size(vector, "Chunk vector")
        self._upsert_vector(CHUNKS_COLLECTION, chunk_id, vector, payload)

    def upsert_extraction_vector(
        self,
        extraction_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Upsert an extraction vector into the extractions collection.

        Args:
            extraction_id: Unique identifier for the extraction (MongoDB ObjectId format).
            vector: 384-dimensional embedding vector.
            payload: Metadata payload (must include source_id, chunk_id, type, topics).

        Raises:
            QdrantVectorError: If vector size is not 384.
            QdrantCollectionError: If upsert operation fails.
        """
        self._validate_vector_size(vector, "Extraction vector")
        self._upsert_vector(EXTRACTIONS_COLLECTION, extraction_id, vector, payload)

    def _upsert_vector(
        self,
        collection: str,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Internal method to upsert a single vector into a collection.

        Args:
            collection: Target collection name.
            point_id: Unique identifier for the point (will be converted to UUID).
            vector: 384-dimensional embedding vector.
            payload: Metadata payload.

        Raises:
            QdrantCollectionError: If upsert operation fails.
        """
        # Convert string ID to UUID for Qdrant compatibility
        qdrant_id = _string_to_uuid(point_id)
        # Store original ID in payload for retrieval
        payload_with_id = {**payload, "_original_id": point_id}

        try:
            self.client.upsert(
                collection_name=collection,
                points=[
                    PointStruct(
                        id=qdrant_id,
                        vector=vector,
                        payload=payload_with_id,
                    )
                ],
            )
            logger.debug("vector_upserted", collection=collection, point_id=point_id)
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_UPSERT_ERROR",
                message=f"Failed to upsert vector to {collection}",
                details={"collection": collection, "point_id": point_id, "error": str(e)},
            )

    def upsert_vectors_batch(
        self,
        collection: str,
        points: list[PointStruct],
        batch_size: int = 100,
    ) -> int:
        """Upsert multiple vectors in batches.

        Args:
            collection: Target collection name.
            points: List of PointStruct objects to upsert.
            batch_size: Number of points to upsert per batch (default 100).

        Returns:
            Number of points successfully upserted.

        Raises:
            QdrantVectorError: If any vector has invalid dimensions.
            QdrantCollectionError: If batch upsert fails.
        """
        # Validate all vectors first
        for point in points:
            self._validate_vector_size(point.vector, f"Vector for point {point.id}")

        total_upserted = 0
        try:
            for i in range(0, len(points), batch_size):
                batch = points[i : i + batch_size]
                self.client.upsert(
                    collection_name=collection,
                    points=batch,
                )
                total_upserted += len(batch)
                logger.debug(
                    "batch_upserted",
                    collection=collection,
                    batch_size=len(batch),
                    total=total_upserted,
                )
            return total_upserted
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_BATCH_UPSERT_ERROR",
                message=f"Failed to batch upsert vectors to {collection}",
                details={
                    "collection": collection,
                    "total_points": len(points),
                    "upserted_before_error": total_upserted,
                    "error": str(e),
                },
            )

    def search(
        self,
        collection: str,
        query_vector: list[float],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Perform semantic search on a collection.

        Args:
            collection: Target collection name.
            query_vector: 384-dimensional query embedding.
            limit: Maximum number of results to return (default 10).

        Returns:
            List of results with id, score, and payload.

        Raises:
            QdrantVectorError: If query vector size is not 384.
            QdrantCollectionError: If search operation fails.
        """
        self._validate_vector_size(query_vector, "Query vector")

        try:
            # Use query_points (newer API) instead of deprecated search
            response = self.client.query_points(
                collection_name=collection,
                query=query_vector,
                limit=limit,
                with_payload=True,
            )

            return [
                {
                    # Return original ID from payload if available, else UUID
                    "id": result.payload.get("_original_id", result.id),
                    "score": result.score,
                    # Remove internal _original_id from returned payload
                    "payload": {
                        k: v for k, v in result.payload.items() if k != "_original_id"
                    },
                }
                for result in response.points
            ]
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_SEARCH_ERROR",
                message=f"Failed to search collection {collection}",
                details={"collection": collection, "limit": limit, "error": str(e)},
            )

    def search_with_filter(
        self,
        collection: str,
        query_vector: list[float],
        filter_dict: dict[str, Any],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Perform filtered semantic search on a collection.

        Supports filtering by source_id, type, and topics.

        Args:
            collection: Target collection name.
            query_vector: 384-dimensional query embedding.
            filter_dict: Filter conditions (e.g., {"type": "decision", "source_id": "abc123"}).
            limit: Maximum number of results to return (default 10).

        Returns:
            List of results with id, score, and payload.

        Raises:
            QdrantVectorError: If query vector size is not 384.
            QdrantCollectionError: If search operation fails.
        """
        self._validate_vector_size(query_vector, "Query vector")

        # Build Qdrant filter from dict
        must_conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, list):
                # For list values (e.g., topics), match any in the list
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchAny(any=value),
                    )
                )
            else:
                # For scalar values, exact match
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )

        qdrant_filter = Filter(must=must_conditions) if must_conditions else None

        try:
            # Use query_points (newer API) instead of deprecated search
            response = self.client.query_points(
                collection_name=collection,
                query=query_vector,
                limit=limit,
                query_filter=qdrant_filter,
                with_payload=True,
            )

            return [
                {
                    # Return original ID from payload if available, else UUID
                    "id": result.payload.get("_original_id", result.id),
                    "score": result.score,
                    # Remove internal _original_id from returned payload
                    "payload": {
                        k: v for k, v in result.payload.items() if k != "_original_id"
                    },
                }
                for result in response.points
            ]
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_FILTERED_SEARCH_ERROR",
                message=f"Failed to perform filtered search on {collection}",
                details={
                    "collection": collection,
                    "filter": filter_dict,
                    "limit": limit,
                    "error": str(e),
                },
            )

    def delete_by_id(self, collection: str, point_id: str) -> None:
        """Delete a point by ID.

        Args:
            collection: Target collection name.
            point_id: ID of the point to delete (will be converted to UUID).

        Note:
            If the point doesn't exist, this operation succeeds silently.
        """
        # Convert string ID to UUID for Qdrant compatibility
        qdrant_id = _string_to_uuid(point_id)

        try:
            self.client.delete(
                collection_name=collection,
                points_selector=PointIdsList(points=[qdrant_id]),
            )
            logger.debug("point_deleted", collection=collection, point_id=point_id)
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_DELETE_ERROR",
                message=f"Failed to delete point from {collection}",
                details={"collection": collection, "point_id": point_id, "error": str(e)},
            )

    def delete_by_source(self, collection: str, source_id: str) -> None:
        """Delete all points for a given source.

        Args:
            collection: Target collection name.
            source_id: Source ID to filter and delete all matching points.
        """
        try:
            self.client.delete(
                collection_name=collection,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="source_id",
                            match=MatchValue(value=source_id),
                        )
                    ]
                ),
            )
            logger.info("points_deleted_by_source", collection=collection, source_id=source_id)
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_DELETE_BY_SOURCE_ERROR",
                message=f"Failed to delete points by source from {collection}",
                details={"collection": collection, "source_id": source_id, "error": str(e)},
            )

    def delete_batch(self, collection: str, point_ids: list[str]) -> None:
        """Delete multiple points by their IDs.

        Args:
            collection: Target collection name.
            point_ids: List of point IDs to delete (will be converted to UUIDs).

        Note:
            Non-existent points are silently ignored.
        """
        if not point_ids:
            return

        # Convert string IDs to UUIDs for Qdrant compatibility
        qdrant_ids = [_string_to_uuid(pid) for pid in point_ids]

        try:
            self.client.delete(
                collection_name=collection,
                points_selector=PointIdsList(points=qdrant_ids),
            )
            logger.debug(
                "points_batch_deleted",
                collection=collection,
                count=len(point_ids),
            )
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_BATCH_DELETE_ERROR",
                message=f"Failed to batch delete points from {collection}",
                details={
                    "collection": collection,
                    "point_count": len(point_ids),
                    "error": str(e),
                },
            )
