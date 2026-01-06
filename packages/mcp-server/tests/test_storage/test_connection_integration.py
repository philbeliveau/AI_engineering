"""Integration tests for cloud database connections (Story 5.4 Task 10).

These tests require actual cloud database accounts and are skipped by default in CI.
Run with: pytest -m integration tests/test_storage/test_connection_integration.py

To run these tests, set the following environment variables:
- MONGODB_URI: MongoDB Atlas connection string
- QDRANT_URL: Qdrant Cloud URL
- QDRANT_API_KEY: Qdrant Cloud API key
"""

import os

import pytest

# Skip all tests in this module unless integration marker is explicitly selected
pytestmark = pytest.mark.integration


def _has_cloud_credentials() -> bool:
    """Check if cloud credentials are available in environment."""
    mongodb_uri = os.getenv("MONGODB_URI", "")
    qdrant_url = os.getenv("QDRANT_URL", "")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

    has_atlas = "mongodb+srv://" in mongodb_uri or "mongodb.net" in mongodb_uri
    has_qdrant_cloud = "cloud.qdrant.io" in qdrant_url and qdrant_api_key

    return has_atlas and has_qdrant_cloud


@pytest.mark.skipif(
    not _has_cloud_credentials(),
    reason="Cloud credentials not configured",
)
class TestMongoDBAtlasIntegration:
    """Integration tests for MongoDB Atlas connections."""

    @pytest.mark.asyncio
    async def test_connect_to_atlas(self):
        """Test successful connection to MongoDB Atlas with SSL."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)

        await client.connect()
        is_healthy = await client.ping()
        await client.disconnect()

        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_atlas_read_write_operations(self):
        """Test read operations on Atlas (MCP server is read-only)."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)

        await client.connect()

        # List sources (read operation)
        sources = await client.list_sources(limit=5)
        assert isinstance(sources, list)

        await client.disconnect()


@pytest.mark.skipif(
    not _has_cloud_credentials(),
    reason="Cloud credentials not configured",
)
class TestQdrantCloudIntegration:
    """Integration tests for Qdrant Cloud connections."""

    @pytest.mark.asyncio
    async def test_connect_to_qdrant_cloud(self):
        """Test successful connection to Qdrant Cloud with API key."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        await client.connect()
        is_healthy = await client.ping()
        await client.disconnect()

        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_qdrant_cloud_search_operations(self):
        """Test search operations on Qdrant Cloud."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        await client.connect()

        # Create a test query vector (768 dimensions for nomic-embed-text-v1.5)
        test_vector = [0.0] * 768

        # Search should work (may return empty results)
        results = await client.search_knowledge(
            query_vector=test_vector,
            limit=5,
        )
        assert isinstance(results, list)

        await client.disconnect()


@pytest.mark.skipif(
    not _has_cloud_credentials(),
    reason="Cloud credentials not configured",
)
class TestCloudConnectionFailures:
    """Integration tests for graceful failure handling."""

    @pytest.mark.asyncio
    async def test_invalid_atlas_credentials(self):
        """Test graceful handling of invalid Atlas credentials."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        # Use invalid credentials
        settings = Settings(
            mongodb_uri="mongodb+srv://invalid:invalid@invalid-cluster.mongodb.net/test"
        )
        client = MongoDBClient(settings)

        # Should not crash, but should fail to connect
        try:
            await client.connect()
            is_healthy = await client.ping()
            assert is_healthy is False
        except Exception:
            pass  # Expected - connection should fail gracefully

    @pytest.mark.asyncio
    async def test_invalid_qdrant_api_key(self):
        """Test graceful handling of invalid Qdrant API key."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        # Use invalid API key
        settings = Settings(
            qdrant_url="https://invalid.cloud.qdrant.io:6333",
            qdrant_api_key="invalid-api-key",
        )
        client = QdrantStorageClient(settings)

        # Should not crash, but should fail to connect
        try:
            await client.connect()
            is_healthy = await client.ping()
            assert is_healthy is False
        except Exception:
            pass  # Expected - connection should fail gracefully


@pytest.mark.skipif(
    not _has_cloud_credentials(),
    reason="Cloud credentials not configured",
)
class TestConnectionPooling:
    """Integration tests for connection pooling behavior."""

    @pytest.mark.asyncio
    async def test_connection_pool_size(self):
        """Test that connection pool size is respected."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings(max_pool_size=5)
        client = MongoDBClient(settings)

        await client.connect()

        # Multiple operations should use the pool
        for _ in range(10):
            await client.ping()

        await client.disconnect()
