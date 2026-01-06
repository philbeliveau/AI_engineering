"""MongoDB storage client for Knowledge MCP Server.

Provides read-only access to MongoDB collections for sources, chunks, and extractions.
Follows project-context.md:71-77 (mcp-server is READ-ONLY).

Note: Uses asyncio.to_thread() to run sync pymongo operations without blocking
the event loop. This is the recommended pattern when using sync drivers in async code.
"""

import asyncio
from typing import Any
from urllib.parse import urlparse, urlunparse

import structlog
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.config import Settings

logger = structlog.get_logger()


def _mask_uri_credentials(uri: str) -> str:
    """Mask credentials in MongoDB URI for safe logging.

    Args:
        uri: MongoDB connection URI

    Returns:
        URI with password masked as ***
    """
    try:
        parsed = urlparse(uri)
        if parsed.password:
            masked = parsed._replace(
                netloc=f"{parsed.username}:***@{parsed.hostname}"
                + (f":{parsed.port}" if parsed.port else "")
            )
            return urlunparse(masked)
        return uri
    except Exception:
        return "mongodb://***"


class MongoDBClient:
    """Read-only MongoDB client for the Knowledge MCP Server.

    Provides methods to query sources, chunks, and extractions from MongoDB.
    All operations are read-only per architecture boundary rules.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize MongoDBClient.

        Args:
            settings: Application settings containing MongoDB configuration
        """
        self._settings = settings
        self._client: MongoClient | None = None
        self._db: Database | None = None

    async def connect(self) -> None:
        """Establish connection to MongoDB.

        Creates a MongoClient and selects the configured database.
        Uses asyncio.to_thread() to avoid blocking the event loop.
        """
        logger.info(
            "mongodb_connecting",
            uri=_mask_uri_credentials(self._settings.mongodb_uri),
            database=self._settings.mongodb_database,
        )

        def _connect_sync() -> None:
            self._client = MongoClient(self._settings.mongodb_uri)
            self._db = self._client[self._settings.mongodb_database]
            # Verify connection
            self._client.admin.command("ping")

        await asyncio.to_thread(_connect_sync)
        logger.info(
            "mongodb_connected",
            database=self._settings.mongodb_database,
        )

    async def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self._client:
            await asyncio.to_thread(self._client.close)
            self._client = None
            self._db = None
            logger.info("mongodb_disconnected")

    async def ping(self) -> bool:
        """Check if MongoDB connection is healthy.

        Returns:
            True if connection is healthy, False otherwise.
        """
        if not self._client:
            return False
        try:
            await asyncio.to_thread(self._client.admin.command, "ping")
            return True
        except Exception:
            return False

    def _get_collection(self, name: str) -> Collection:
        """Get a collection by name.

        Args:
            name: Collection name (sources, chunks, extractions)

        Returns:
            MongoDB collection

        Raises:
            RuntimeError: If not connected
        """
        if self._db is None:
            raise RuntimeError("MongoDB client not connected")
        return self._db[name]

    async def get_source(self, source_id: str) -> dict[str, Any] | None:
        """Retrieve a source by ID.

        Args:
            source_id: The source document ID (hex string)

        Returns:
            Source document or None if not found
        """
        logger.debug("mongodb_get_source", source_id=source_id)

        def _query_sync() -> dict[str, Any] | None:
            collection = self._get_collection(self._settings.sources_collection)

            # Try to convert to ObjectId first (sources use ObjectId as _id)
            try:
                object_id = ObjectId(source_id)
                result = collection.find_one({"_id": object_id})
            except InvalidId:
                # Fall back to string lookup if not a valid ObjectId
                result = collection.find_one({"_id": source_id})

            if result:
                # Convert ObjectId to string for API responses
                result["id"] = str(result.pop("_id"))
            return result

        return await asyncio.to_thread(_query_sync)

    async def list_sources(self, limit: int = 100) -> list[dict[str, Any]]:
        """List all sources.

        Args:
            limit: Maximum number of sources to return

        Returns:
            List of source documents
        """
        logger.debug("mongodb_list_sources", limit=limit)

        def _query_sync() -> list[dict[str, Any]]:
            collection = self._get_collection(self._settings.sources_collection)
            cursor = collection.find({}).limit(limit)
            sources = []
            for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                sources.append(doc)
            return sources

        return await asyncio.to_thread(_query_sync)

    async def get_chunks(self, source_id: str) -> list[dict[str, Any]]:
        """Get all chunks for a source.

        Args:
            source_id: The source document ID

        Returns:
            List of chunk documents
        """
        logger.debug("mongodb_get_chunks", source_id=source_id)

        def _query_sync() -> list[dict[str, Any]]:
            collection = self._get_collection(self._settings.chunks_collection)
            cursor = collection.find({"source_id": source_id})
            chunks = []
            for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                chunks.append(doc)
            return chunks

        return await asyncio.to_thread(_query_sync)

    async def get_extractions(
        self,
        extraction_type: str | None = None,
        topics: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Query extractions with optional filters.

        Args:
            extraction_type: Filter by extraction type (decision, pattern, warning, etc.)
            topics: Filter by topics (documents matching any topic)

        Returns:
            List of extraction documents
        """
        logger.debug(
            "mongodb_get_extractions",
            extraction_type=extraction_type,
            topics=topics,
        )

        def _query_sync() -> list[dict[str, Any]]:
            collection = self._get_collection(self._settings.extractions_collection)
            # Build query filter
            query: dict[str, Any] = {}
            if extraction_type:
                query["type"] = extraction_type
            if topics:
                query["topics"] = {"$in": topics}

            cursor = collection.find(query)
            extractions = []
            for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                extractions.append(doc)
            return extractions

        return await asyncio.to_thread(_query_sync)

    async def get_chunk_by_id(self, chunk_id: str) -> dict[str, Any] | None:
        """Retrieve a single chunk by ID.

        Used for enriching search results with full chunk content.
        Note: Currently unused by search_knowledge (content comes from Qdrant payload).
        Retained for future use cases like get_chunk_details tool.

        Args:
            chunk_id: The chunk document ID

        Returns:
            Chunk document or None if not found
        """
        logger.debug("mongodb_get_chunk_by_id", chunk_id=chunk_id)

        def _query_sync() -> dict[str, Any] | None:
            collection = self._get_collection(self._settings.chunks_collection)
            result = collection.find_one({"_id": chunk_id})
            if result:
                # Convert ObjectId to string for API responses
                result["id"] = str(result.pop("_id"))
            return result

        return await asyncio.to_thread(_query_sync)

    async def get_extraction_by_id(self, extraction_id: str) -> dict[str, Any] | None:
        """Retrieve a single extraction by ID.

        Used for enriching search results with full extraction content.
        Extractions are stored with ObjectId as _id, so we convert the string ID.

        Args:
            extraction_id: The extraction document ID (hex string from Qdrant payload)

        Returns:
            Extraction document or None if not found
        """
        logger.debug("mongodb_get_extraction_by_id", extraction_id=extraction_id)

        def _query_sync() -> dict[str, Any] | None:
            collection = self._get_collection(self._settings.extractions_collection)

            # Try to convert to ObjectId first (extractions use ObjectId as _id)
            try:
                object_id = ObjectId(extraction_id)
                result = collection.find_one({"_id": object_id})
            except InvalidId:
                # Fall back to string lookup if not a valid ObjectId
                result = collection.find_one({"_id": extraction_id})

            if result:
                # Convert ObjectId to string for API responses
                result["id"] = str(result.pop("_id"))
            return result

        return await asyncio.to_thread(_query_sync)
