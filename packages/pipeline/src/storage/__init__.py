"""Storage clients for MongoDB and Qdrant.

This module exports storage clients for both databases:
- MongoDBClient: Document storage for sources, chunks, and extractions
- QdrantStorageClient: Vector storage and semantic search operations
- ExtractionStorage: Orchestration service for extraction persistence
"""

from src.storage.extraction_storage import ExtractionStorage, ExtractionStorageError
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
    # Extraction Storage Service
    "ExtractionStorage",
    "ExtractionStorageError",
]
