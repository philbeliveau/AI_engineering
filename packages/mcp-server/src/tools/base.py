"""Shared infrastructure for extraction query tools.

Provides common functionality for get_decisions, get_patterns, get_warnings, and get_methodologies.
Eliminates code duplication across extraction tool modules (Story 4.3 Code Review Fix).
"""

import structlog

from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient

logger = structlog.get_logger()

# Global clients - set by server.py during startup
_qdrant_client: QdrantStorageClient | None = None
_mongodb_client: MongoDBClient | None = None


def set_extraction_clients(
    qdrant: QdrantStorageClient | None = None,
    mongodb: MongoDBClient | None = None,
) -> None:
    """Set the global storage clients for all extraction tools.

    Called by server.py during application startup. Provides a single
    entry point for initializing all extraction tool dependencies.

    Args:
        qdrant: QdrantStorageClient instance for vector queries
        mongodb: MongoDBClient instance for document queries (optional)
    """
    global _qdrant_client, _mongodb_client
    _qdrant_client = qdrant
    _mongodb_client = mongodb
    logger.debug(
        "extraction_clients_set",
        qdrant_available=qdrant is not None,
        mongodb_available=mongodb is not None,
    )


def get_qdrant_client() -> QdrantStorageClient | None:
    """Get the Qdrant client for extraction queries.

    Returns:
        QdrantStorageClient instance or None if not initialized.
    """
    return _qdrant_client


def get_mongodb_client() -> MongoDBClient | None:
    """Get the MongoDB client for extraction queries.

    Returns:
        MongoDBClient instance or None if not initialized.
    """
    return _mongodb_client
