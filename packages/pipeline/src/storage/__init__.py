"""Storage clients for MongoDB and Qdrant.

This module exports storage clients for both databases:
- MongoDBClient: Document storage for sources, chunks, and extractions
- QdrantStorageClient: Vector storage and semantic search operations
"""

from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import (
    CHUNKS_COLLECTION,
    DISTANCE_METRIC,
    EXTRACTIONS_COLLECTION,
    VECTOR_SIZE,
    QdrantStorageClient,
)

__all__ = [
    # MongoDB
    "MongoDBClient",
    # Qdrant
    "QdrantStorageClient",
    "VECTOR_SIZE",
    "DISTANCE_METRIC",
    "CHUNKS_COLLECTION",
    "EXTRACTIONS_COLLECTION",
]
