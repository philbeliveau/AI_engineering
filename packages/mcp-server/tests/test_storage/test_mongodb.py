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
