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
    KeywordIndexParams,
    MatchAny,
    MatchValue,
    PayloadSchemaType,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from src.config import KNOWLEDGE_VECTORS_COLLECTION, VECTOR_SIZE, settings
from src.exceptions import (
    QdrantCollectionError,
    QdrantConnectionError,
    QdrantVectorError,
)

logger = structlog.get_logger()

# Constants from config (nomic-embed-text-v1.5: 768 dimensions)
# VECTOR_SIZE imported from src.config
DISTANCE_METRIC = Distance.COSINE

# Single collection for all vectors (following Qdrant multitenancy best practices)
# Uses payload-based filtering with project_id as tenant identifier
COLLECTION_NAME = KNOWLEDGE_VECTORS_COLLECTION

# Legacy collection names - kept for backwards compatibility during migration
# These are DEPRECATED and will be removed in future versions
CHUNKS_COLLECTION = settings.chunks_collection
EXTRACTIONS_COLLECTION = settings.extractions_collection

# Content type discriminator values
CONTENT_TYPE_CHUNK = "chunk"
CONTENT_TYPE_EXTRACTION = "extraction"

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

    def __init__(self, url: str | None = None, api_key: str | None = None):
        """Initialize Qdrant client with connection to Qdrant server.

        Args:
            url: Qdrant server URL. Defaults to settings.qdrant_url.
            api_key: Qdrant API key for cloud authentication. Defaults to settings.qdrant_api_key.

        Raises:
            QdrantConnectionError: If connection to Qdrant fails.
        """
        self.url = url or settings.qdrant_url
        self.api_key = api_key if api_key is not None else settings.qdrant_api_key
        try:
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
                timeout=30,
            )
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

        For the unified 'knowledge_vectors' collection, comprehensive payload indexes
        are created for optimized filtered search performance (NFR1: <500ms).

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
                if create_indexes:
                    self._create_payload_indexes(collection_name)
            else:
                logger.debug("qdrant_collection_exists", collection=collection_name)
        except Exception as e:
            raise QdrantCollectionError(
                code="QDRANT_COLLECTION_ERROR",
                message=f"Failed to ensure collection {collection_name}",
                details={"collection": collection_name, "error": str(e)},
            )

    def ensure_knowledge_collection(self) -> None:
        """Create the unified knowledge_vectors collection if it doesn't exist.

        Convenience method that ensures the single collection architecture is set up
        with all required payload indexes for multitenancy and filtering.
        """
        self.ensure_collection(COLLECTION_NAME, create_indexes=True)

    def _create_payload_indexes(self, collection_name: str) -> None:
        """Create payload indexes for optimized filtered search.

        Creates comprehensive indexes for the unified knowledge_vectors collection:
        - project_id: Tenant index for multitenancy with is_tenant=True optimization
        - content_type: Discriminator between chunks and extractions
        - source_id: Filter by source document
        - extraction_type: Filter extractions by type (decision, pattern, etc.)
        - topics: Filter by topic tags
        - source_type: Filter by source type (book, paper, case_study)
        - source_category: Filter by category (foundational, advanced, etc.)
        - source_year: Filter by publication year

        Args:
            collection_name: Target collection name.
        """
        # Create project_id index with is_tenant=True for optimized co-location (Qdrant v1.11+)
        # This enables efficient multi-tenant queries by grouping vectors by project
        # Uses KeywordIndexParams per Qdrant documentation for multitenancy
        try:
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="project_id",
                field_schema=KeywordIndexParams(
                    type="keyword",
                    is_tenant=True,
                ),
            )
            logger.debug(
                "tenant_index_created",
                collection=collection_name,
                field="project_id",
                is_tenant=True,
            )
        except Exception as e:
            # Log but don't fail - index might already exist
            logger.warning(
                "tenant_index_creation_skipped",
                collection=collection_name,
                field="project_id",
                reason=str(e),
            )

        # Keyword indexes for exact match filtering (non-tenant fields)
        keyword_fields = [
            "content_type",
            "source_id",
            "chunk_id",
            "extraction_type",
            "topics",
            "source_type",
            "source_category",
        ]

        for field in keyword_fields:
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
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

        # Integer index for year filtering
        try:
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="source_year",
                field_schema=PayloadSchemaType.INTEGER,
            )
            logger.debug("payload_index_created", collection=collection_name, field="source_year")
        except Exception as e:
            logger.warning(
                "payload_index_creation_skipped",
                collection=collection_name,
                field="source_year",
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
        project_id: str | None = None,
    ) -> None:
        """Upsert a chunk vector into the unified knowledge collection.

        Args:
            chunk_id: Unique identifier for the chunk (MongoDB ObjectId format).
            vector: 384-dimensional embedding vector.
            payload: Metadata payload (must include source_id).
            project_id: Project identifier for multitenancy (defaults to settings.project_id).

        Raises:
            QdrantVectorError: If vector size is not 384.
            QdrantCollectionError: If upsert operation fails.
        """
        self._validate_vector_size(vector, "Chunk vector")

        # Build rich payload with content_type discriminator
        rich_payload = {
            **payload,
            "content_type": CONTENT_TYPE_CHUNK,
            "project_id": project_id or settings.project_id,
            "chunk_id": chunk_id,
        }

        self._upsert_vector(COLLECTION_NAME, chunk_id, vector, rich_payload)

    def upsert_extraction_vector(
        self,
        extraction_id: str,
        vector: list[float],
        payload: dict[str, Any],
        project_id: str | None = None,
    ) -> None:
        """Upsert an extraction vector into the unified knowledge collection.

        Args:
            extraction_id: Unique identifier for the extraction (MongoDB ObjectId format).
            vector: 384-dimensional embedding vector.
            payload: Metadata payload containing:
                - source_id: Reference to source document
                - chunk_id: Reference to source chunk
                - type: Extraction type (decision, pattern, warning, etc.)
                - topics: Topic tags
                - title: Human-readable extraction title (optional)
                - source_title: Source document title (optional, denormalized)
                - source_type: Source document type (optional, denormalized)
                - source_category: Source category (optional, denormalized)
                - source_year: Publication year (optional, denormalized)
                - chapter: Chapter from source (optional, denormalized)
            project_id: Project identifier for multitenancy (defaults to settings.project_id).

        Raises:
            QdrantVectorError: If vector size is not 384.
            QdrantCollectionError: If upsert operation fails.
        """
        self._validate_vector_size(vector, "Extraction vector")

        # Build rich payload with content_type discriminator
        # extraction_type is set by ExtractionStorage._build_rich_payload()
        rich_payload = {
            **payload,
            "content_type": CONTENT_TYPE_EXTRACTION,
            "project_id": project_id or settings.project_id,
            "extraction_id": extraction_id,
        }

        # Ensure extraction_type is always set for proper filtering
        if "extraction_type" not in rich_payload:
            logger.warning(
                "extraction_type_missing",
                extraction_id=extraction_id,
                hint="payload should include extraction_type from _build_rich_payload",
            )
            rich_payload["extraction_type"] = ""

        self._upsert_vector(COLLECTION_NAME, extraction_id, vector, rich_payload)

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

    def search_knowledge(
        self,
        query_vector: list[float],
        limit: int = 10,
        project_id: str | None = None,
        content_type: str | None = None,
        extraction_type: str | None = None,
        source_id: str | None = None,
        topics: list[str] | None = None,
        source_type: str | None = None,
        source_category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search the unified knowledge collection with project isolation.

        This is the primary search method for the single-collection architecture.
        Always filters by project_id for proper multitenancy.

        Args:
            query_vector: 384-dimensional query embedding.
            limit: Maximum number of results to return (default 10).
            project_id: Project identifier (defaults to settings.project_id).
            content_type: Filter by content type ('chunk' or 'extraction').
            extraction_type: Filter extractions by type (decision, pattern, etc.).
            source_id: Filter by source document.
            topics: Filter by topic tags (match any).
            source_type: Filter by source type (book, paper, case_study).
            source_category: Filter by category (foundational, advanced, etc.).

        Returns:
            List of results with id, score, and payload.

        Raises:
            QdrantVectorError: If query vector size is not 384.
            QdrantCollectionError: If search operation fails.
        """
        # Build filter dict with project isolation
        filter_dict: dict[str, Any] = {
            "project_id": project_id or settings.project_id,
        }

        if content_type:
            filter_dict["content_type"] = content_type
        if extraction_type:
            filter_dict["extraction_type"] = extraction_type
        if source_id:
            filter_dict["source_id"] = source_id
        if topics:
            filter_dict["topics"] = topics
        if source_type:
            filter_dict["source_type"] = source_type
        if source_category:
            filter_dict["source_category"] = source_category

        return self.search_with_filter(
            collection=COLLECTION_NAME,
            query_vector=query_vector,
            filter_dict=filter_dict,
            limit=limit,
        )

    def search_chunks(
        self,
        query_vector: list[float],
        limit: int = 10,
        project_id: str | None = None,
        source_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for chunks in the unified collection.

        Convenience method that filters by content_type='chunk'.

        Args:
            query_vector: 384-dimensional query embedding.
            limit: Maximum number of results to return (default 10).
            project_id: Project identifier (defaults to settings.project_id).
            source_id: Filter by source document.

        Returns:
            List of chunk results with id, score, and payload.
        """
        return self.search_knowledge(
            query_vector=query_vector,
            limit=limit,
            project_id=project_id,
            content_type=CONTENT_TYPE_CHUNK,
            source_id=source_id,
        )

    def search_extractions(
        self,
        query_vector: list[float],
        limit: int = 10,
        project_id: str | None = None,
        extraction_type: str | None = None,
        source_id: str | None = None,
        topics: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for extractions in the unified collection.

        Convenience method that filters by content_type='extraction'.

        Args:
            query_vector: 384-dimensional query embedding.
            limit: Maximum number of results to return (default 10).
            project_id: Project identifier (defaults to settings.project_id).
            extraction_type: Filter by extraction type (decision, pattern, etc.).
            source_id: Filter by source document.
            topics: Filter by topic tags (match any).

        Returns:
            List of extraction results with id, score, and payload.
        """
        return self.search_knowledge(
            query_vector=query_vector,
            limit=limit,
            project_id=project_id,
            content_type=CONTENT_TYPE_EXTRACTION,
            extraction_type=extraction_type,
            source_id=source_id,
            topics=topics,
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
