"""Fixtures for storage client tests."""

from datetime import datetime

import pytest

from src.config import settings
from src.models import Chunk, ChunkPosition, Extraction, Source
from src.storage import MongoDBClient, QdrantStorageClient


@pytest.fixture
def mongodb_client():
    """Provide a MongoDB client for testing.

    Uses the default test database and cleans up after tests.
    """
    client = MongoDBClient(database="knowledge_db_test")
    client.connect()
    # Cleanup before test to ensure clean state
    if client._db is not None:
        client._db[settings.sources_collection].delete_many({})
        client._db[settings.chunks_collection].delete_many({})
        client._db[settings.extractions_collection].delete_many({})
    yield client
    # Cleanup after test
    if client._db is not None:
        client._db[settings.sources_collection].delete_many({})
        client._db[settings.chunks_collection].delete_many({})
        client._db[settings.extractions_collection].delete_many({})
    client.close()


@pytest.fixture
def sample_source() -> Source:
    """Provide a sample Source for testing."""
    return Source(
        id="507f1f77bcf86cd799439011",
        type="book",
        title="Test Book",
        authors=["Test Author"],
        path="/data/raw/test-book.pdf",
        ingested_at=datetime.now(),
        status="pending",
        metadata={"pages": 100},
        schema_version="1.0",
    )


@pytest.fixture
def sample_chunk(sample_source) -> Chunk:
    """Provide a sample Chunk for testing."""
    return Chunk(
        id="507f1f77bcf86cd799439012",
        source_id=sample_source.id,
        content="This is test content for a chunk. It contains enough text to be valid.",
        position=ChunkPosition(chapter="1", section="Introduction", page=1),
        token_count=15,
        schema_version="1.0",
    )


@pytest.fixture
def sample_extraction(sample_source, sample_chunk) -> Extraction:
    """Provide a sample Extraction for testing."""
    return Extraction(
        id="507f1f77bcf86cd799439013",
        source_id=sample_source.id,
        chunk_id=sample_chunk.id,
        type="decision",
        content={
            "question": "Which database should we use?",
            "options": ["MongoDB", "PostgreSQL"],
            "considerations": ["Flexibility", "Performance"],
            "recommended_approach": "MongoDB for document storage",
        },
        topics=["architecture", "database"],
        schema_version="1.0",
        extracted_at=datetime.now(),
    )


# ============================================================================
# Qdrant Fixtures
# ============================================================================


@pytest.fixture
def qdrant_client():
    """Provide a Qdrant client for testing.

    Creates test collections and cleans up before and after tests.
    Requires Qdrant to be running (docker-compose up -d).
    """
    from src.config import KNOWLEDGE_VECTORS_COLLECTION

    client = QdrantStorageClient()

    # Cleanup collections before test to ensure clean state
    collections_to_cleanup = [
        "test_chunks",
        "test_extractions",
        "test_collection",
        settings.chunks_collection,
        settings.extractions_collection,
        KNOWLEDGE_VECTORS_COLLECTION,  # Unified collection
    ]
    for collection in collections_to_cleanup:
        try:
            client.client.delete_collection(collection)
        except Exception:
            pass

    yield client

    # Cleanup: delete all test and real collections created during tests
    for collection in collections_to_cleanup:
        try:
            client.client.delete_collection(collection)
        except Exception:
            pass


@pytest.fixture
def test_vector_384d() -> list[float]:
    """Provide a valid 384-dimensional test vector."""
    return [0.1] * 384


@pytest.fixture
def test_vector_256d() -> list[float]:
    """Provide an invalid 256-dimensional test vector for rejection tests."""
    return [0.1] * 256


@pytest.fixture
def sample_chunk_payload(sample_source, sample_chunk) -> dict:
    """Provide a sample chunk payload for Qdrant."""
    return {
        "source_id": sample_source.id,
        "chunk_id": sample_chunk.id,
    }


@pytest.fixture
def sample_extraction_payload(sample_source, sample_chunk) -> dict:
    """Provide a sample extraction payload for Qdrant.

    Uses the new unified collection schema with:
    - extraction_type: The type of extraction (decision, pattern, etc.)
    - topics: Topic tags for filtering
    """
    return {
        "source_id": sample_source.id,
        "chunk_id": sample_chunk.id,
        "extraction_type": "decision",  # New schema uses extraction_type
        "topics": ["architecture", "database"],
    }
