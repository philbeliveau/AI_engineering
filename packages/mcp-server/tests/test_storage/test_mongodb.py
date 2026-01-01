"""Tests for MongoDB storage client."""

import pytest


class TestMongoDBClient:
    """Test cases for MongoDBClient."""

    def test_mongodb_client_import(self):
        """Test that MongoDBClient can be imported."""
        from src.storage.mongodb import MongoDBClient

        assert MongoDBClient is not None

    def test_mongodb_client_initialization(self):
        """Test that MongoDBClient can be initialized with settings."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert client is not None
        assert client._client is None  # Not connected yet
        assert client._db is None

    @pytest.mark.asyncio
    async def test_mongodb_client_has_connect_method(self):
        """Test that MongoDBClient has connect method."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "connect")
        assert callable(client.connect)

    @pytest.mark.asyncio
    async def test_mongodb_client_has_disconnect_method(self):
        """Test that MongoDBClient has disconnect method."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "disconnect")
        assert callable(client.disconnect)

    def test_mongodb_client_has_get_source_method(self):
        """Test that MongoDBClient has get_source method."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "get_source")
        assert callable(client.get_source)

    def test_mongodb_client_has_list_sources_method(self):
        """Test that MongoDBClient has list_sources method."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "list_sources")
        assert callable(client.list_sources)

    def test_mongodb_client_has_get_chunks_method(self):
        """Test that MongoDBClient has get_chunks method."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "get_chunks")
        assert callable(client.get_chunks)

    def test_mongodb_client_has_get_extractions_method(self):
        """Test that MongoDBClient has get_extractions method."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "get_extractions")
        assert callable(client.get_extractions)

    def test_mongodb_client_exported_from_storage(self):
        """Test that MongoDBClient is exported from storage package."""
        from src.storage import MongoDBClient

        assert MongoDBClient is not None

    def test_mongodb_client_has_ping_method(self):
        """Test that MongoDBClient has ping method for health checks."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "ping")
        assert callable(client.ping)

    @pytest.mark.asyncio
    async def test_mongodb_ping_returns_false_when_not_connected(self):
        """Test that ping returns False when client is not connected."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        # Client not connected, ping should return False
        result = await client.ping()
        assert result is False

    def test_get_collection_raises_when_not_connected(self):
        """Test that _get_collection raises RuntimeError when not connected."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        with pytest.raises(RuntimeError, match="MongoDB client not connected"):
            client._get_collection("sources")


class TestMaskUriCredentials:
    """Test cases for URI credential masking helper."""

    def test_mask_uri_without_credentials(self):
        """Test that URI without credentials is returned unchanged."""
        from src.storage.mongodb import _mask_uri_credentials

        uri = "mongodb://localhost:27017"
        result = _mask_uri_credentials(uri)
        assert result == uri

    def test_mask_uri_with_password(self):
        """Test that password is masked in URI."""
        from src.storage.mongodb import _mask_uri_credentials

        uri = "mongodb://user:secretpassword@localhost:27017"
        result = _mask_uri_credentials(uri)
        assert "secretpassword" not in result
        assert "***" in result
        assert "user" in result

    def test_mask_uri_with_password_and_port(self):
        """Test that password is masked and port is preserved."""
        from src.storage.mongodb import _mask_uri_credentials

        uri = "mongodb://admin:mysecret@db.example.com:27017"
        result = _mask_uri_credentials(uri)
        assert "mysecret" not in result
        assert ":27017" in result
        assert "admin" in result

    def test_mask_uri_handles_invalid_uri(self):
        """Test that invalid URI returns masked placeholder."""
        from src.storage.mongodb import _mask_uri_credentials

        # The function should handle any edge cases gracefully
        result = _mask_uri_credentials("")
        # Empty string has no password, returns as-is
        assert result == ""


class TestMongoDBEnrichmentMethods:
    """Test cases for MongoDB enrichment methods (Story 4.2)."""

    def test_mongodb_client_has_get_chunk_by_id_method(self):
        """Test that MongoDBClient has get_chunk_by_id method."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "get_chunk_by_id")
        assert callable(client.get_chunk_by_id)

    def test_mongodb_client_has_get_extraction_by_id_method(self):
        """Test that MongoDBClient has get_extraction_by_id method."""
        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)
        assert hasattr(client, "get_extraction_by_id")
        assert callable(client.get_extraction_by_id)

    @pytest.mark.asyncio
    async def test_get_chunk_by_id_with_mock(self):
        """Test get_chunk_by_id with mocked database."""
        from unittest.mock import MagicMock

        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)

        # Mock the database and collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {
            "_id": "chunk-123",
            "source_id": "src-001",
            "content": "Test chunk content",
            "position": {"chapter": "Ch 1", "section": "Sec 1", "page": 42},
        }
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        client._db = mock_db

        result = await client.get_chunk_by_id("chunk-123")
        assert result is not None
        assert result["id"] == "chunk-123"
        assert result["content"] == "Test chunk content"
        assert result["position"]["page"] == 42

    @pytest.mark.asyncio
    async def test_get_chunk_by_id_not_found(self):
        """Test get_chunk_by_id returns None when not found."""
        from unittest.mock import MagicMock

        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)

        # Mock the database returning None
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        client._db = mock_db

        result = await client.get_chunk_by_id("nonexistent-chunk")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_extraction_by_id_with_mock(self):
        """Test get_extraction_by_id with mocked database."""
        from unittest.mock import MagicMock

        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)

        # Mock the database and collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {
            "_id": "ext-456",
            "source_id": "src-001",
            "chunk_id": "chunk-123",
            "type": "decision",
            "content": {"title": "Test Decision"},
            "topics": ["architecture", "testing"],
        }
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        client._db = mock_db

        result = await client.get_extraction_by_id("ext-456")
        assert result is not None
        assert result["id"] == "ext-456"
        assert result["type"] == "decision"
        assert result["topics"] == ["architecture", "testing"]

    @pytest.mark.asyncio
    async def test_get_extraction_by_id_not_found(self):
        """Test get_extraction_by_id returns None when not found."""
        from unittest.mock import MagicMock

        from src.config import Settings
        from src.storage.mongodb import MongoDBClient

        settings = Settings()
        client = MongoDBClient(settings)

        # Mock the database returning None
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        client._db = mock_db

        result = await client.get_extraction_by_id("nonexistent-ext")
        assert result is None
