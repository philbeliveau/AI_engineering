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

    def test_vector_dimensions_constant_is_768(self):
        """Test that VECTOR_DIMENSIONS constant is 768 for nomic-embed-text-v1.5."""
        from src.storage.qdrant import VECTOR_DIMENSIONS

        assert VECTOR_DIMENSIONS == 768

    def test_validate_vector_accepts_768_dimensions(self):
        """Test that _validate_vector accepts correct 768-dimensional vectors."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        # Should not raise for correct dimensions
        vector = [0.1] * 768
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
        assert exc_info.value.details["expected_dimensions"] == 768
        assert exc_info.value.details["actual_dimensions"] == 100

    def test_validate_vector_rejects_too_many_dimensions(self):
        """Test that _validate_vector raises ValidationError for too many dimensions."""
        from src.config import Settings
        from src.exceptions import ValidationError
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        # Test with 1024 dimensions (too many)
        vector_1024 = [0.1] * 1024
        with pytest.raises(ValidationError) as exc_info:
            client._validate_vector(vector_1024)
        assert exc_info.value.details["expected_dimensions"] == 768
        assert exc_info.value.details["actual_dimensions"] == 1024

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


class TestListExtractions:
    """Tests for list_extractions method (Story 4.3)."""

    def test_list_extractions_method_exists(self):
        """Test that list_extractions method exists."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)
        assert hasattr(client, "list_extractions")
        assert callable(client.list_extractions)

    @pytest.mark.asyncio
    async def test_list_extractions_raises_when_not_connected(self):
        """Test that list_extractions raises RuntimeError when not connected."""
        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        with pytest.raises(RuntimeError, match="not connected"):
            await client.list_extractions(extraction_type="decision")

    @pytest.mark.asyncio
    async def test_list_extractions_calls_scroll(self):
        """Test that list_extractions uses scroll API."""
        from unittest.mock import MagicMock

        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        # Mock the Qdrant client
        mock_qdrant = MagicMock()
        mock_qdrant.scroll.return_value = ([], None)  # Empty results
        client._client = mock_qdrant

        await client.list_extractions(
            extraction_type="decision",
            limit=50,
            topic="rag",
        )

        # Verify scroll was called
        mock_qdrant.scroll.assert_called_once()
        call_kwargs = mock_qdrant.scroll.call_args.kwargs
        assert call_kwargs["limit"] == 50
        assert call_kwargs["with_payload"] is True
        assert call_kwargs["with_vectors"] is False

    @pytest.mark.asyncio
    async def test_list_extractions_returns_correct_format(self):
        """Test that list_extractions returns list of dicts with id and payload."""
        from unittest.mock import MagicMock

        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings()
        client = QdrantStorageClient(settings)

        # Mock result
        mock_point = MagicMock()
        mock_point.id = "ext-123"
        mock_point.payload = {"content": {"title": "Test"}, "topics": ["rag"]}

        mock_qdrant = MagicMock()
        mock_qdrant.scroll.return_value = ([mock_point], None)
        client._client = mock_qdrant

        results = await client.list_extractions(extraction_type="decision")

        assert len(results) == 1
        assert results[0]["id"] == "ext-123"
        assert results[0]["payload"]["topics"] == ["rag"]

    @pytest.mark.asyncio
    async def test_list_extractions_uses_project_id(self):
        """Test that list_extractions filters by project_id."""
        from unittest.mock import MagicMock

        from qdrant_client.models import FieldCondition, Filter

        from src.config import Settings
        from src.storage.qdrant import QdrantStorageClient

        settings = Settings(project_id="test-project")
        client = QdrantStorageClient(settings)

        mock_qdrant = MagicMock()
        mock_qdrant.scroll.return_value = ([], None)
        client._client = mock_qdrant

        await client.list_extractions(extraction_type="pattern")

        # Verify filter includes project_id
        call_kwargs = mock_qdrant.scroll.call_args.kwargs
        scroll_filter = call_kwargs["scroll_filter"]
        assert isinstance(scroll_filter, Filter)

        # Check that project_id is in the filter conditions
        project_id_found = False
        for cond in scroll_filter.must:
            if isinstance(cond, FieldCondition) and cond.key == "project_id":
                project_id_found = True
                assert cond.match.value == "test-project"
        assert project_id_found, "project_id filter not found"
