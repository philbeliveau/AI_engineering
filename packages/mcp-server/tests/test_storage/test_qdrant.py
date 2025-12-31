"""Tests for Qdrant storage client."""

import pytest


class TestQdrantStorageClient:
    """Test cases for QdrantStorageClient."""

    def test_qdrant_client_import(self):
        """Test that QdrantStorageClient can be imported."""
        from src.storage.qdrant import QdrantStorageClient

        assert QdrantStorageClient is not None

    def test_qdrant_client_initialization(self):
        """Test that QdrantStorageClient can be initialized with settings."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        assert client is not None
        assert client._client is None  # Not connected yet

    @pytest.mark.asyncio
    async def test_qdrant_client_has_connect_method(self):
        """Test that QdrantStorageClient has connect method."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        assert hasattr(client, "connect")
        assert callable(client.connect)

    @pytest.mark.asyncio
    async def test_qdrant_client_has_disconnect_method(self):
        """Test that QdrantStorageClient has disconnect method."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        assert hasattr(client, "disconnect")
        assert callable(client.disconnect)

    def test_qdrant_client_has_search_chunks_method(self):
        """Test that QdrantStorageClient has search_chunks method."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        assert hasattr(client, "search_chunks")
        assert callable(client.search_chunks)

    def test_qdrant_client_has_search_extractions_method(self):
        """Test that QdrantStorageClient has search_extractions method."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        assert hasattr(client, "search_extractions")
        assert callable(client.search_extractions)

    def test_qdrant_client_exported_from_storage(self):
        """Test that QdrantStorageClient is exported from storage package."""
        from src.storage import QdrantStorageClient

        assert QdrantStorageClient is not None

    def test_qdrant_client_has_ping_method(self):
        """Test that QdrantStorageClient has ping method for health checks."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        assert hasattr(client, "ping")
        assert callable(client.ping)

    @pytest.mark.asyncio
    async def test_qdrant_ping_returns_false_when_not_connected(self):
        """Test that ping returns False when client is not connected."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        # Client not connected, ping should return False
        result = await client.ping()
        assert result is False


class TestVectorDimensionValidation:
    """Test cases for vector dimension validation."""

    def test_vector_dimensions_constant_is_384(self):
        """Test that VECTOR_DIMENSIONS constant is 384 per project-context.md."""
        from src.storage.qdrant import VECTOR_DIMENSIONS

        assert VECTOR_DIMENSIONS == 384

    def test_validate_vector_accepts_384_dimensions(self):
        """Test that _validate_vector accepts correct 384-dimensional vectors."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        # Should not raise for correct dimensions
        vector = [0.1] * 384
        client._validate_vector(vector)  # Should not raise

    def test_validate_vector_rejects_wrong_dimensions(self):
        """Test that _validate_vector raises ValidationError for wrong dimensions."""
        from src.config import Settings
        from src.exceptions import ValidationError
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        # Test with 100 dimensions (too few)
        vector_100 = [0.1] * 100
        with pytest.raises(ValidationError) as exc_info:
            client._validate_vector(vector_100)
        assert exc_info.value.code == "VALIDATION_ERROR"
        assert exc_info.value.details["expected_dimensions"] == 384
        assert exc_info.value.details["actual_dimensions"] == 100

    def test_validate_vector_rejects_too_many_dimensions(self):
        """Test that _validate_vector raises ValidationError for too many dimensions."""
        from src.config import Settings
        from src.exceptions import ValidationError
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        # Test with 512 dimensions (too many)
        vector_512 = [0.1] * 512
        with pytest.raises(ValidationError) as exc_info:
            client._validate_vector(vector_512)
        assert exc_info.value.details["expected_dimensions"] == 384
        assert exc_info.value.details["actual_dimensions"] == 512

    def test_validate_vector_rejects_empty_vector(self):
        """Test that _validate_vector raises ValidationError for empty vector."""
        from src.config import Settings
        from src.exceptions import ValidationError
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        with pytest.raises(ValidationError) as exc_info:
            client._validate_vector([])
        assert exc_info.value.details["actual_dimensions"] == 0

    @pytest.mark.asyncio
    async def test_search_chunks_validates_vector_dimensions(self):
        """Test that search_chunks validates vector dimensions before search."""
        from unittest.mock import MagicMock

        from src.config import Settings
        from src.exceptions import ValidationError
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        # Mock the client as connected
        client._client = MagicMock()

        # Should raise ValidationError for wrong dimensions
        wrong_vector = [0.1] * 100
        with pytest.raises(ValidationError):
            await client.search_chunks(wrong_vector)

    @pytest.mark.asyncio
    async def test_search_extractions_validates_vector_dimensions(self):
        """Test that search_extractions validates vector dimensions before search."""
        from unittest.mock import MagicMock

        from src.config import Settings
        from src.exceptions import ValidationError
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        # Mock the client as connected
        client._client = MagicMock()

        # Should raise ValidationError for wrong dimensions
        wrong_vector = [0.1] * 500
        with pytest.raises(ValidationError):
            await client.search_extractions(wrong_vector)
