"""Tests for MongoDB multi-tenancy support (Story 11.1).

Tests _collection_name() helper and project_id parameter propagation
through all MongoDB query methods.
"""

import pytest
from unittest.mock import MagicMock

from src.config import Settings
from src.storage.mongodb import MongoDBClient


class TestCollectionNameHelper:
    """Tests for _collection_name() method."""

    def test_collection_name_with_default_project_id(self):
        """When project_id is None, uses settings.project_id."""
        settings = Settings(project_id="default")
        client = MongoDBClient(settings)
        assert client._collection_name("sources") == "default_sources"
        assert client._collection_name("chunks") == "default_chunks"
        assert client._collection_name("extractions") == "default_extractions"

    def test_collection_name_with_explicit_project_id(self):
        """When project_id is provided, uses it instead of settings."""
        settings = Settings(project_id="default")
        client = MongoDBClient(settings)
        assert client._collection_name("sources", "org_abc") == "org_abc_sources"
        assert client._collection_name("chunks", "org_abc") == "org_abc_chunks"
        assert client._collection_name("extractions", "org_abc") == "org_abc_extractions"

    def test_collection_name_none_falls_back_to_settings(self):
        """Explicitly passing None uses settings.project_id."""
        settings = Settings(project_id="my_project")
        client = MongoDBClient(settings)
        assert client._collection_name("sources", None) == "my_project_sources"

    def test_backward_compat_matches_old_properties(self):
        """_collection_name(base, None) produces same result as old settings properties."""
        settings = Settings(project_id="knowledge-pipeline")
        client = MongoDBClient(settings)
        # Old pattern: settings.sources_collection == "knowledge-pipeline_sources"
        assert client._collection_name("sources") == settings.sources_collection
        assert client._collection_name("chunks") == settings.chunks_collection
        assert client._collection_name("extractions") == settings.extractions_collection


class TestValidateProjectId:
    """Tests for _validate_project_id() security validation."""

    def test_valid_alphanumeric(self):
        """Accept standard alphanumeric project IDs."""
        # Should not raise
        MongoDBClient._validate_project_id("org_abc")
        MongoDBClient._validate_project_id("my-project")
        MongoDBClient._validate_project_id("Project123")
        MongoDBClient._validate_project_id("a")

    def test_rejects_empty_string(self):
        """Reject empty string."""
        from src.exceptions import ValidationError

        with pytest.raises(ValidationError):
            MongoDBClient._validate_project_id("")

    def test_rejects_whitespace_only(self):
        """Reject whitespace-only string."""
        from src.exceptions import ValidationError

        with pytest.raises(ValidationError):
            MongoDBClient._validate_project_id("   ")

    def test_rejects_special_characters(self):
        """Reject project IDs with dots, slashes, spaces, or other special chars."""
        from src.exceptions import ValidationError

        with pytest.raises(ValidationError):
            MongoDBClient._validate_project_id("org.abc")
        with pytest.raises(ValidationError):
            MongoDBClient._validate_project_id("../../admin")
        with pytest.raises(ValidationError):
            MongoDBClient._validate_project_id("org abc")
        with pytest.raises(ValidationError):
            MongoDBClient._validate_project_id("org$abc")

    def test_rejects_dollar_prefix(self):
        """Reject MongoDB operator injection attempts."""
        from src.exceptions import ValidationError

        with pytest.raises(ValidationError):
            MongoDBClient._validate_project_id("$where")

    def test_collection_name_validates(self):
        """_collection_name() calls _validate_project_id, so invalid IDs are rejected."""
        from src.exceptions import ValidationError

        settings = Settings(project_id="default")
        client = MongoDBClient(settings)
        with pytest.raises(ValidationError):
            client._collection_name("sources", "../../hack")


class TestProjectIdPropagation:
    """Tests that project_id is correctly propagated to collection resolution."""

    def _make_client_with_mock_db(self, project_id: str = "default") -> MongoDBClient:
        """Create a MongoDBClient with a mocked database."""
        settings = Settings(project_id=project_id)
        client = MongoDBClient(settings)
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_collection.find.return_value = iter([])
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        client._db = mock_db
        return client

    @pytest.mark.asyncio
    async def test_get_source_uses_project_id(self):
        """get_source with project_id accesses correct collection."""
        client = self._make_client_with_mock_db("default")
        await client.get_source("src-1", project_id="org_abc")
        client._db.__getitem__.assert_called_with("org_abc_sources")

    @pytest.mark.asyncio
    async def test_get_source_default_project_id(self):
        """get_source without project_id uses settings default."""
        client = self._make_client_with_mock_db("default")
        await client.get_source("src-1")
        client._db.__getitem__.assert_called_with("default_sources")

    @pytest.mark.asyncio
    async def test_list_sources_uses_project_id(self):
        """list_sources with project_id accesses correct collection."""
        client = self._make_client_with_mock_db("default")
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = iter([])
        client._db.__getitem__.return_value.find.return_value = mock_cursor
        await client.list_sources(project_id="org_abc")
        client._db.__getitem__.assert_called_with("org_abc_sources")

    @pytest.mark.asyncio
    async def test_get_chunks_uses_project_id(self):
        """get_chunks with project_id accesses correct collection."""
        client = self._make_client_with_mock_db("default")
        await client.get_chunks("src-1", project_id="org_abc")
        client._db.__getitem__.assert_called_with("org_abc_chunks")

    @pytest.mark.asyncio
    async def test_get_extractions_uses_project_id(self):
        """get_extractions with project_id accesses correct collection."""
        client = self._make_client_with_mock_db("default")
        await client.get_extractions(project_id="org_abc")
        client._db.__getitem__.assert_called_with("org_abc_extractions")

    @pytest.mark.asyncio
    async def test_get_chunk_by_id_uses_project_id(self):
        """get_chunk_by_id with project_id accesses correct collection."""
        client = self._make_client_with_mock_db("default")
        await client.get_chunk_by_id("chunk-1", project_id="org_abc")
        client._db.__getitem__.assert_called_with("org_abc_chunks")

    @pytest.mark.asyncio
    async def test_get_extraction_by_id_uses_project_id(self):
        """get_extraction_by_id with project_id accesses correct collection."""
        client = self._make_client_with_mock_db("default")
        await client.get_extraction_by_id("ext-1", project_id="org_abc")
        client._db.__getitem__.assert_called_with("org_abc_extractions")
