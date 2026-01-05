"""MongoDB storage client for knowledge base operations.

This module provides a sync MongoDB client for the knowledge pipeline.
pymongo is not async-native, so sync methods are used.
"""

from typing import TYPE_CHECKING, Optional

import structlog

if TYPE_CHECKING:
    from src.extractors.base import ExtractionBase as ExtractorExtractionBase
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from src.config import settings
from src.exceptions import NotFoundError, StorageError, ValidationError
from src.models import Chunk, Extraction, Source

logger = structlog.get_logger()


class MongoDBClient:
    """MongoDB client for knowledge base storage operations.

    Sync MongoDB client - pymongo is not async-native.

    Provides CRUD operations for sources, chunks, and extractions collections.
    """

    @staticmethod
    def _validate_object_id(id_str: str, resource: str) -> ObjectId:
        """Validate and convert string to ObjectId.

        Args:
            id_str: The string to convert to ObjectId.
            resource: Resource name for error messages (e.g., 'source', 'chunk').

        Returns:
            Valid ObjectId.

        Raises:
            ValidationError: If id_str is not a valid 24-character hex string.
        """
        try:
            return ObjectId(id_str)
        except InvalidId as e:
            raise ValidationError(
                f"Invalid {resource} ID format: '{id_str}'",
                details={"id": id_str, "resource": resource, "error": str(e)},
            ) from e

    def __init__(self, uri: str | None = None, database: str | None = None):
        """Initialize MongoDB client.

        Args:
            uri: MongoDB connection URI. Defaults to settings.mongodb_uri.
            database: Database name. Defaults to settings.mongodb_database.
        """
        self._uri = uri or settings.mongodb_uri
        self._database_name = database or settings.mongodb_database
        self._client: MongoClient | None = None
        self._db: Database | None = None

    def connect(self) -> None:
        """Establish connection to MongoDB and ensure indexes."""
        try:
            self._client = MongoClient(self._uri)
            self._db = self._client[self._database_name]
            self._ensure_indexes()
            logger.info("mongodb_connected", database=self._database_name)
        except PyMongoError as e:
            logger.error("mongodb_connection_failed", error=str(e))
            raise StorageError("connect", {"error": str(e)}) from e

    def close(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("mongodb_disconnected")

    def ping(self) -> bool:
        """Verify connection health.

        Returns:
            True if connection is healthy, False otherwise.
        """
        try:
            if self._client is None:
                return False
            self._client.admin.command("ping")
            return True
        except PyMongoError:
            return False

    def __enter__(self) -> "MongoDBClient":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit."""
        self.close()
        return False

    # =========================================================================
    # Index Management
    # =========================================================================

    def _ensure_indexes(self) -> None:
        """Create required indexes for all collections.

        Creates indexes with background=True for non-blocking creation.
        Index naming convention: idx_{collection}_{field}

        Indexes support multi-project architecture with project_id filtering.
        """
        if self._db is None:
            raise StorageError("_ensure_indexes", {"error": "Not connected"})

        try:
            # Sources indexes
            sources_col = self._db[settings.sources_collection]
            sources_col.create_index(
                [("status", ASCENDING)],
                name="idx_sources_status",
                background=True,
            )
            # Multi-project indexes for sources
            sources_col.create_index(
                [("project_id", ASCENDING), ("type", ASCENDING)],
                name="idx_sources_project_type",
                background=True,
            )
            sources_col.create_index(
                [("project_id", ASCENDING), ("category", ASCENDING)],
                name="idx_sources_project_category",
                background=True,
            )
            sources_col.create_index(
                [("project_id", ASCENDING), ("tags", ASCENDING)],
                name="idx_sources_project_tags",
                background=True,
            )

            # Chunks indexes
            chunks_col = self._db[settings.chunks_collection]
            chunks_col.create_index(
                [("source_id", ASCENDING)],
                name="idx_chunks_source_id",
                background=True,
            )
            chunks_col.create_index(
                [("project_id", ASCENDING), ("source_id", ASCENDING)],
                name="idx_chunks_project_source",
                background=True,
            )

            # Extractions indexes
            extractions_col = self._db[settings.extractions_collection]
            extractions_col.create_index(
                [("type", ASCENDING), ("topics", ASCENDING)],
                name="idx_extractions_type_topics",
                background=True,
            )
            extractions_col.create_index(
                [("source_id", ASCENDING)],
                name="idx_extractions_source_id",
                background=True,
            )
            # Multi-project indexes for extractions
            extractions_col.create_index(
                [("project_id", ASCENDING), ("source_id", ASCENDING)],
                name="idx_extractions_project_source",
                background=True,
            )
            extractions_col.create_index(
                [("project_id", ASCENDING), ("type", ASCENDING)],
                name="idx_extractions_project_type",
                background=True,
            )

            logger.info("mongodb_indexes_ensured")
        except PyMongoError as e:
            logger.error("mongodb_index_creation_failed", error=str(e))
            raise StorageError("_ensure_indexes", {"error": str(e)}) from e

    # =========================================================================
    # Sources CRUD Operations
    # =========================================================================

    def create_source(self, source: Source) -> str:
        """Create a new source document.

        Args:
            source: Source model to insert.

        Returns:
            The inserted document's ObjectId as string.

        Raises:
            StorageError: If insertion fails.
        """
        if self._db is None:
            raise StorageError("create_source", {"error": "Not connected"})

        try:
            doc = source.model_dump()
            # Generate new ObjectId if not provided or replace the string id
            doc["_id"] = ObjectId()
            if "id" in doc:
                del doc["id"]

            result = self._db[settings.sources_collection].insert_one(doc)
            source_id = str(result.inserted_id)
            logger.info("source_created", source_id=source_id, type=source.type)
            return source_id
        except PyMongoError as e:
            logger.error("source_creation_failed", error=str(e))
            raise StorageError("create_source", {"error": str(e)}) from e

    def get_source(self, source_id: str) -> Source:
        """Get a source by ID.

        Args:
            source_id: The source ObjectId as string.

        Returns:
            The Source model.

        Raises:
            ValidationError: If source_id is not a valid ObjectId format.
            NotFoundError: If source not found.
            StorageError: If query fails.
        """
        if self._db is None:
            raise StorageError("get_source", {"error": "Not connected"})

        oid = self._validate_object_id(source_id, "source")

        try:
            doc = self._db[settings.sources_collection].find_one({"_id": oid})
            if not doc:
                raise NotFoundError("source", source_id)
            # Convert MongoDB _id to string id for Pydantic model
            doc["id"] = str(doc.pop("_id"))
            return Source.model_validate(doc)
        except NotFoundError:
            raise
        except PyMongoError as e:
            logger.error("source_get_failed", source_id=source_id, error=str(e))
            raise StorageError("get_source", {"error": str(e)}) from e

    def update_source(self, source_id: str, updates: dict) -> Source:
        """Update a source document.

        Args:
            source_id: The source ObjectId as string.
            updates: Dictionary of fields to update (must not be empty).

        Returns:
            The updated Source model.

        Raises:
            ValidationError: If source_id is invalid or updates is empty.
            NotFoundError: If source not found.
            StorageError: If update fails.
        """
        if self._db is None:
            raise StorageError("update_source", {"error": "Not connected"})

        oid = self._validate_object_id(source_id, "source")

        # Don't allow updating _id or id
        updates.pop("_id", None)
        updates.pop("id", None)

        # Validate updates is not empty after removing protected fields
        if not updates:
            raise ValidationError(
                "Updates dictionary cannot be empty",
                details={"source_id": source_id},
            )

        try:
            result = self._db[settings.sources_collection].update_one(
                {"_id": oid},
                {"$set": updates},
            )
            if result.matched_count == 0:
                raise NotFoundError("source", source_id)

            logger.info("source_updated", source_id=source_id, fields=list(updates.keys()))
            return self.get_source(source_id)
        except NotFoundError:
            raise
        except PyMongoError as e:
            logger.error("source_update_failed", source_id=source_id, error=str(e))
            raise StorageError("update_source", {"error": str(e)}) from e

    def delete_source(self, source_id: str) -> bool:
        """Delete a source document.

        Args:
            source_id: The source ObjectId as string.

        Returns:
            True if deleted, False if not found.

        Raises:
            ValidationError: If source_id is not a valid ObjectId format.
            StorageError: If deletion fails.
        """
        if self._db is None:
            raise StorageError("delete_source", {"error": "Not connected"})

        oid = self._validate_object_id(source_id, "source")

        try:
            result = self._db[settings.sources_collection].delete_one({"_id": oid})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info("source_deleted", source_id=source_id)
            return deleted
        except PyMongoError as e:
            logger.error("source_delete_failed", source_id=source_id, error=str(e))
            raise StorageError("delete_source", {"error": str(e)}) from e

    def list_sources(self, status: Optional[str] = None) -> list[Source]:
        """List all sources with optional status filter.

        Args:
            status: Optional status to filter by.

        Returns:
            List of Source models.

        Raises:
            StorageError: If query fails.
        """
        if self._db is None:
            raise StorageError("list_sources", {"error": "Not connected"})

        try:
            query = {}
            if status:
                query["status"] = status

            sources = []
            for doc in self._db[settings.sources_collection].find(query):
                doc["id"] = str(doc.pop("_id"))
                sources.append(Source.model_validate(doc))
            return sources
        except PyMongoError as e:
            logger.error("sources_list_failed", error=str(e))
            raise StorageError("list_sources", {"error": str(e)}) from e

    # =========================================================================
    # Chunks CRUD Operations
    # =========================================================================

    def create_chunk(self, chunk: Chunk) -> str:
        """Create a new chunk document.

        Args:
            chunk: Chunk model to insert.

        Returns:
            The inserted document's ObjectId as string.

        Raises:
            StorageError: If insertion fails.
        """
        if self._db is None:
            raise StorageError("create_chunk", {"error": "Not connected"})

        try:
            doc = chunk.model_dump()
            doc["_id"] = ObjectId()
            if "id" in doc:
                del doc["id"]

            result = self._db[settings.chunks_collection].insert_one(doc)
            chunk_id = str(result.inserted_id)
            logger.info("chunk_created", chunk_id=chunk_id, source_id=chunk.source_id)
            return chunk_id
        except PyMongoError as e:
            logger.error("chunk_creation_failed", error=str(e))
            raise StorageError("create_chunk", {"error": str(e)}) from e

    def get_chunk(self, chunk_id: str) -> Chunk:
        """Get a chunk by ID.

        Args:
            chunk_id: The chunk ObjectId as string.

        Returns:
            The Chunk model.

        Raises:
            ValidationError: If chunk_id is not a valid ObjectId format.
            NotFoundError: If chunk not found.
            StorageError: If query fails.
        """
        if self._db is None:
            raise StorageError("get_chunk", {"error": "Not connected"})

        oid = self._validate_object_id(chunk_id, "chunk")

        try:
            doc = self._db[settings.chunks_collection].find_one({"_id": oid})
            if not doc:
                raise NotFoundError("chunk", chunk_id)
            doc["id"] = str(doc.pop("_id"))
            return Chunk.model_validate(doc)
        except NotFoundError:
            raise
        except PyMongoError as e:
            logger.error("chunk_get_failed", chunk_id=chunk_id, error=str(e))
            raise StorageError("get_chunk", {"error": str(e)}) from e

    def get_chunks_by_source(self, source_id: str) -> list[Chunk]:
        """Get all chunks for a source.

        Args:
            source_id: The source ObjectId as string.

        Returns:
            List of Chunk models.

        Raises:
            StorageError: If query fails.
        """
        if self._db is None:
            raise StorageError("get_chunks_by_source", {"error": "Not connected"})

        try:
            chunks = []
            for doc in self._db[settings.chunks_collection].find({"source_id": source_id}):
                doc["id"] = str(doc.pop("_id"))
                chunks.append(Chunk.model_validate(doc))
            return chunks
        except PyMongoError as e:
            logger.error("chunks_by_source_failed", source_id=source_id, error=str(e))
            raise StorageError("get_chunks_by_source", {"error": str(e)}) from e

    def delete_chunks_by_source(self, source_id: str) -> int:
        """Delete all chunks for a source.

        Args:
            source_id: The source ObjectId as string.

        Returns:
            Number of chunks deleted.

        Raises:
            StorageError: If deletion fails.
        """
        if self._db is None:
            raise StorageError("delete_chunks_by_source", {"error": "Not connected"})

        try:
            result = self._db[settings.chunks_collection].delete_many({"source_id": source_id})
            deleted_count = result.deleted_count
            logger.info("chunks_deleted_by_source", source_id=source_id, count=deleted_count)
            return deleted_count
        except PyMongoError as e:
            logger.error("chunks_delete_by_source_failed", source_id=source_id, error=str(e))
            raise StorageError("delete_chunks_by_source", {"error": str(e)}) from e

    def count_chunks_by_source(self, source_id: str) -> int:
        """Count chunks for a source.

        Args:
            source_id: The source ObjectId as string.

        Returns:
            Number of chunks for the source.

        Raises:
            StorageError: If count fails.
        """
        if self._db is None:
            raise StorageError("count_chunks_by_source", {"error": "Not connected"})

        try:
            return self._db[settings.chunks_collection].count_documents({"source_id": source_id})
        except PyMongoError as e:
            logger.error("chunks_count_by_source_failed", source_id=source_id, error=str(e))
            raise StorageError("count_chunks_by_source", {"error": str(e)}) from e

    # =========================================================================
    # Extractions CRUD Operations
    # =========================================================================

    def create_extraction(self, extraction: Extraction) -> str:
        """Create a new extraction document.

        Args:
            extraction: Extraction model to insert.

        Returns:
            The inserted document's ObjectId as string.

        Raises:
            StorageError: If insertion fails.
        """
        if self._db is None:
            raise StorageError("create_extraction", {"error": "Not connected"})

        try:
            doc = extraction.model_dump()
            doc["_id"] = ObjectId()
            if "id" in doc:
                del doc["id"]

            result = self._db[settings.extractions_collection].insert_one(doc)
            extraction_id = str(result.inserted_id)
            logger.info(
                "extraction_created",
                extraction_id=extraction_id,
                type=extraction.type,
                source_id=extraction.source_id,
            )
            return extraction_id
        except PyMongoError as e:
            logger.error("extraction_creation_failed", error=str(e))
            raise StorageError("create_extraction", {"error": str(e)}) from e

    def get_extraction(self, extraction_id: str) -> Extraction:
        """Get an extraction by ID.

        Args:
            extraction_id: The extraction ObjectId as string.

        Returns:
            The Extraction model.

        Raises:
            ValidationError: If extraction_id is not a valid ObjectId format.
            NotFoundError: If extraction not found.
            StorageError: If query fails.
        """
        if self._db is None:
            raise StorageError("get_extraction", {"error": "Not connected"})

        oid = self._validate_object_id(extraction_id, "extraction")

        try:
            doc = self._db[settings.extractions_collection].find_one({"_id": oid})
            if not doc:
                raise NotFoundError("extraction", extraction_id)
            doc["id"] = str(doc.pop("_id"))
            return Extraction.model_validate(doc)
        except NotFoundError:
            raise
        except PyMongoError as e:
            logger.error("extraction_get_failed", extraction_id=extraction_id, error=str(e))
            raise StorageError("get_extraction", {"error": str(e)}) from e

    def get_extractions_by_source(self, source_id: str) -> list[Extraction]:
        """Get all extractions for a source.

        Args:
            source_id: The source ObjectId as string.

        Returns:
            List of Extraction models.

        Raises:
            StorageError: If query fails.
        """
        if self._db is None:
            raise StorageError("get_extractions_by_source", {"error": "Not connected"})

        try:
            extractions = []
            for doc in self._db[settings.extractions_collection].find({"source_id": source_id}):
                doc["id"] = str(doc.pop("_id"))
                extractions.append(Extraction.model_validate(doc))
            return extractions
        except PyMongoError as e:
            logger.error("extractions_by_source_failed", source_id=source_id, error=str(e))
            raise StorageError("get_extractions_by_source", {"error": str(e)}) from e

    def get_extractions_by_type(
        self, extraction_type: str, topics: Optional[list[str]] = None
    ) -> list[Extraction]:
        """Get extractions by type with optional topic filter.

        Uses compound index on (type, topics) for efficient querying.

        Args:
            extraction_type: Type of extraction (decision, pattern, warning, etc.).
            topics: Optional list of topics to filter by (matches any).

        Returns:
            List of Extraction models.

        Raises:
            StorageError: If query fails.
        """
        if self._db is None:
            raise StorageError("get_extractions_by_type", {"error": "Not connected"})

        try:
            query = {"type": extraction_type}
            if topics:
                query["topics"] = {"$in": topics}

            extractions = []
            for doc in self._db[settings.extractions_collection].find(query):
                doc["id"] = str(doc.pop("_id"))
                extractions.append(Extraction.model_validate(doc))
            return extractions
        except PyMongoError as e:
            logger.error(
                "extractions_by_type_failed",
                type=extraction_type,
                topics=topics,
                error=str(e),
            )
            raise StorageError("get_extractions_by_type", {"error": str(e)}) from e

    def delete_extractions_by_source(self, source_id: str) -> int:
        """Delete all extractions for a source.

        Args:
            source_id: The source ObjectId as string.

        Returns:
            Number of extractions deleted.

        Raises:
            StorageError: If deletion fails.
        """
        if self._db is None:
            raise StorageError("delete_extractions_by_source", {"error": "Not connected"})

        try:
            result = self._db[settings.extractions_collection].delete_many({"source_id": source_id})
            deleted_count = result.deleted_count
            logger.info(
                "extractions_deleted_by_source", source_id=source_id, count=deleted_count
            )
            return deleted_count
        except PyMongoError as e:
            logger.error(
                "extractions_delete_by_source_failed", source_id=source_id, error=str(e)
            )
            raise StorageError("delete_extractions_by_source", {"error": str(e)}) from e

    def save_extraction_from_extractor(
        self,
        extraction: "ExtractorExtractionBase",
    ) -> str:
        """Save an extraction from the extractor system to MongoDB.

        This method handles the conversion from extractor ExtractionBase models
        to the MongoDB storage format, with duplicate detection based on
        chunk_id + type combination.

        Args:
            extraction: ExtractionBase model from extractors (Decision, Pattern, etc.)

        Returns:
            The extraction ID (new or existing if duplicate).

        Raises:
            StorageError: If save operation fails.
        """
        if self._db is None:
            raise StorageError("save_extraction_from_extractor", {"error": "Not connected"})

        # Check for duplicate (same chunk_id + type)
        try:
            existing = self._db[settings.extractions_collection].find_one({
                "chunk_id": extraction.chunk_id,
                "type": extraction.type.value,
            })

            if existing:
                existing_id = str(existing["_id"])
                logger.warning(
                    "duplicate_extraction_skipped",
                    chunk_id=extraction.chunk_id,
                    type=extraction.type.value,
                    existing_id=existing_id,
                )
                return existing_id

            # Serialize extraction using Pydantic model_dump
            # This converts the extractor model to a dict suitable for MongoDB
            extraction_data = extraction.model_dump(mode="json")

            # Convert type enum to string value if needed
            if hasattr(extraction_data.get("type"), "value"):
                extraction_data["type"] = extraction_data["type"].value

            # Build MongoDB document structure
            # The extractor model is flat, but MongoDB expects specific structure
            doc = {
                "_id": ObjectId(),
                "source_id": extraction_data.get("source_id"),
                "chunk_id": extraction_data.get("chunk_id"),
                "type": extraction_data.get("type"),
                "content": self._extract_content_from_extraction(extraction_data),
                "topics": extraction_data.get("topics", []),
                "schema_version": extraction_data.get("schema_version", "1.0.0"),
                "extracted_at": extraction_data.get("extracted_at"),
                # Hierarchical context fields (v1.1.0)
                "context_level": extraction_data.get("context_level", "chunk"),
                "context_id": extraction_data.get("context_id", extraction_data.get("chunk_id", "")),
                "chunk_ids": extraction_data.get("chunk_ids", []),
            }

            result = self._db[settings.extractions_collection].insert_one(doc)
            extraction_id = str(result.inserted_id)

            logger.info(
                "extraction_saved_from_extractor",
                extraction_id=extraction_id,
                type=extraction.type.value,
                source_id=extraction.source_id,
                chunk_id=extraction.chunk_id,
            )

            return extraction_id

        except PyMongoError as e:
            logger.error(
                "extraction_save_failed",
                chunk_id=extraction.chunk_id,
                type=extraction.type.value,
                error=str(e),
            )
            raise StorageError("save_extraction_from_extractor", {"error": str(e)}) from e

    def _extract_content_from_extraction(self, extraction_data: dict) -> dict:
        """Extract content fields from flat extraction data.

        The extractor models are flat (all fields at top level), but MongoDB
        expects a nested 'content' structure. This method extracts the
        type-specific fields into a content dict.

        Args:
            extraction_data: Flat extraction dict from model_dump.

        Returns:
            Content dict with type-specific fields.
        """
        # Base fields that are NOT content (they are metadata)
        base_fields = {
            "id", "source_id", "chunk_id", "type", "topics",
            "schema_version", "extracted_at", "confidence",
        }

        # Extract all fields that are not base metadata as content
        content = {}
        for key, value in extraction_data.items():
            if key not in base_fields:
                content[key] = value

        return content

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    def create_chunks_bulk(self, chunks: list[Chunk]) -> list[str]:
        """Bulk insert multiple chunks.

        Uses insert_many for efficient batch insertion.

        Args:
            chunks: List of Chunk models to insert.

        Returns:
            List of inserted ObjectIds as strings.

        Raises:
            StorageError: If bulk insertion fails.
        """
        if self._db is None:
            raise StorageError("create_chunks_bulk", {"error": "Not connected"})

        if not chunks:
            return []

        try:
            docs = []
            for chunk in chunks:
                doc = chunk.model_dump()
                doc["_id"] = ObjectId()
                if "id" in doc:
                    del doc["id"]
                docs.append(doc)

            result = self._db[settings.chunks_collection].insert_many(docs, ordered=False)
            chunk_ids = [str(oid) for oid in result.inserted_ids]
            logger.info("chunks_bulk_created", count=len(chunk_ids))
            return chunk_ids
        except PyMongoError as e:
            logger.error("chunks_bulk_creation_failed", error=str(e))
            raise StorageError("create_chunks_bulk", {"error": str(e)}) from e

    def create_extractions_bulk(self, extractions: list[Extraction]) -> list[str]:
        """Bulk insert multiple extractions.

        Uses insert_many for efficient batch insertion.

        Args:
            extractions: List of Extraction models to insert.

        Returns:
            List of inserted ObjectIds as strings.

        Raises:
            StorageError: If bulk insertion fails.
        """
        if self._db is None:
            raise StorageError("create_extractions_bulk", {"error": "Not connected"})

        if not extractions:
            return []

        try:
            docs = []
            for extraction in extractions:
                doc = extraction.model_dump()
                doc["_id"] = ObjectId()
                if "id" in doc:
                    del doc["id"]
                docs.append(doc)

            result = self._db[settings.extractions_collection].insert_many(docs, ordered=False)
            extraction_ids = [str(oid) for oid in result.inserted_ids]
            logger.info("extractions_bulk_created", count=len(extraction_ids))
            return extraction_ids
        except PyMongoError as e:
            logger.error("extractions_bulk_creation_failed", error=str(e))
            raise StorageError("create_extractions_bulk", {"error": str(e)}) from e
