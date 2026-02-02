"""Tests for Qdrant multi-tenancy support (Story 11.1).

Tests source_id filter on list_extractions and project_id propagation.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.config import Settings
from src.storage.qdrant import QdrantStorageClient


class TestListExtractionsSourceIdFilter:
    """Tests for source_id filter on list_extractions."""

    def _make_client(self) -> QdrantStorageClient:
        """Create a QdrantStorageClient with a mocked Qdrant client."""
        settings = Settings(project_id="default")
        client = QdrantStorageClient(settings)
        mock_qdrant = MagicMock()
        # Mock scroll to return empty results
        mock_qdrant.scroll.return_value = ([], None)
        client._client = mock_qdrant
        return client

    @pytest.mark.asyncio
    async def test_list_extractions_without_source_id(self):
        """list_extractions without source_id does not add source filter."""
        client = self._make_client()
        await client.list_extractions(extraction_type="decision", limit=10)

        call_args = client._client.scroll.call_args
        scroll_filter = call_args.kwargs.get("scroll_filter") or call_args[1].get("scroll_filter")
        # Should have 3 conditions: project_id, content_type, extraction_type
        assert len(scroll_filter.must) == 3

    @pytest.mark.asyncio
    async def test_list_extractions_with_source_id(self):
        """list_extractions with source_id adds source filter condition."""
        client = self._make_client()
        await client.list_extractions(
            extraction_type="decision", limit=10, source_id="src-123"
        )

        call_args = client._client.scroll.call_args
        scroll_filter = call_args.kwargs.get("scroll_filter") or call_args[1].get("scroll_filter")
        # Should have 4 conditions: project_id, content_type, extraction_type, source_id
        assert len(scroll_filter.must) == 4
        source_conditions = [
            c for c in scroll_filter.must
            if hasattr(c, "key") and c.key == "source_id"
        ]
        assert len(source_conditions) == 1
        assert source_conditions[0].match.value == "src-123"

    @pytest.mark.asyncio
    async def test_list_extractions_with_source_id_and_topic(self):
        """list_extractions with both source_id and topic adds both filters."""
        client = self._make_client()
        await client.list_extractions(
            extraction_type="pattern",
            limit=10,
            source_id="src-456",
            topic="rag",
        )

        call_args = client._client.scroll.call_args
        scroll_filter = call_args.kwargs.get("scroll_filter") or call_args[1].get("scroll_filter")
        # Should have 5 conditions: project_id, content_type, extraction_type, topic, source_id
        assert len(scroll_filter.must) == 5

    @pytest.mark.asyncio
    async def test_list_extractions_project_id_override(self):
        """list_extractions with project_id overrides settings default."""
        client = self._make_client()
        await client.list_extractions(
            extraction_type="warning", limit=10, project_id="org_abc"
        )

        call_args = client._client.scroll.call_args
        scroll_filter = call_args.kwargs.get("scroll_filter") or call_args[1].get("scroll_filter")
        project_conditions = [
            c for c in scroll_filter.must
            if hasattr(c, "key") and c.key == "project_id"
        ]
        assert len(project_conditions) == 1
        assert project_conditions[0].match.value == "org_abc"
