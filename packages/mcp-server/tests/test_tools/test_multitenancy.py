"""Tests for MCP endpoint multi-tenancy (Story 11.1).

Tests that project_id and source_id query params are correctly propagated
to all 7 endpoints via HTTP requests through the FastAPI test client.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_storage():
    """Mock both Qdrant and MongoDB clients for all tool modules."""
    mock_qdrant = AsyncMock()
    mock_qdrant.list_extractions = AsyncMock(return_value=[])
    mock_qdrant.search_chunks = AsyncMock(return_value=[])
    mock_qdrant.search_extractions = AsyncMock(return_value=[])
    mock_qdrant.count_extractions_by_sources = AsyncMock(return_value={})

    mock_mongodb = AsyncMock()
    mock_mongodb.list_sources = AsyncMock(return_value=[])
    mock_mongodb.get_source = AsyncMock(return_value=None)

    return mock_qdrant, mock_mongodb


class TestProjectIdQueryParam:
    """Tests that project_id query param is accepted on all endpoints."""

    @pytest.mark.asyncio
    async def test_search_knowledge_accepts_project_id(self, mock_storage):
        """search_knowledge accepts ?project_id=org_abc."""
        mock_qdrant, mock_mongodb = mock_storage

        with (
            patch("src.tools.search._qdrant_client", mock_qdrant),
            patch("src.tools.search._mongodb_client", mock_mongodb),
            patch("src.tools.search.embed_query", return_value=[0.1] * 768),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/search_knowledge?query=test&project_id=org_abc"
                )
                assert response.status_code == 200
                # Verify project_id was passed to Qdrant
                mock_qdrant.search_chunks.assert_called_once()
                call_kwargs = mock_qdrant.search_chunks.call_args.kwargs
                assert call_kwargs.get("project_id") == "org_abc"

    @pytest.mark.asyncio
    async def test_get_decisions_accepts_project_id_and_source_id(self, mock_storage):
        """get_decisions accepts ?project_id=org_abc&source_id=src-1."""
        mock_qdrant, mock_mongodb = mock_storage

        with (
            patch("src.tools.decisions._qdrant_client", mock_qdrant),
            patch("src.tools.decisions._mongodb_client", mock_mongodb),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/get_decisions?project_id=org_abc&source_id=src-1"
                )
                assert response.status_code == 200
                mock_qdrant.list_extractions.assert_called_once()
                call_kwargs = mock_qdrant.list_extractions.call_args.kwargs
                assert call_kwargs.get("project_id") == "org_abc"
                assert call_kwargs.get("source_id") == "src-1"

    @pytest.mark.asyncio
    async def test_get_patterns_accepts_project_id_and_source_id(self, mock_storage):
        """get_patterns accepts ?project_id=org_abc&source_id=src-1."""
        mock_qdrant, mock_mongodb = mock_storage

        with (
            patch("src.tools.patterns._qdrant_client", mock_qdrant),
            patch("src.tools.patterns._mongodb_client", mock_mongodb),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/get_patterns?project_id=org_abc&source_id=src-1"
                )
                assert response.status_code == 200
                mock_qdrant.list_extractions.assert_called_once()
                call_kwargs = mock_qdrant.list_extractions.call_args.kwargs
                assert call_kwargs.get("project_id") == "org_abc"
                assert call_kwargs.get("source_id") == "src-1"

    @pytest.mark.asyncio
    async def test_get_warnings_accepts_project_id_and_source_id(self, mock_storage):
        """get_warnings accepts ?project_id=org_abc&source_id=src-1."""
        mock_qdrant, mock_mongodb = mock_storage

        with (
            patch("src.tools.warnings._qdrant_client", mock_qdrant),
            patch("src.tools.warnings._mongodb_client", mock_mongodb),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/get_warnings?project_id=org_abc&source_id=src-1"
                )
                assert response.status_code == 200
                mock_qdrant.list_extractions.assert_called_once()
                call_kwargs = mock_qdrant.list_extractions.call_args.kwargs
                assert call_kwargs.get("project_id") == "org_abc"
                assert call_kwargs.get("source_id") == "src-1"

    @pytest.mark.asyncio
    async def test_get_methodologies_accepts_project_id_and_source_id(self, mock_storage):
        """get_methodologies accepts ?project_id=org_abc&source_id=src-1."""
        mock_qdrant, mock_mongodb = mock_storage

        with (
            patch("src.tools.methodologies._qdrant_client", mock_qdrant),
            patch("src.tools.methodologies._mongodb_client", mock_mongodb),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/get_methodologies?project_id=org_abc&source_id=src-1"
                )
                assert response.status_code == 200
                mock_qdrant.list_extractions.assert_called_once()
                call_kwargs = mock_qdrant.list_extractions.call_args.kwargs
                assert call_kwargs.get("project_id") == "org_abc"
                assert call_kwargs.get("source_id") == "src-1"

    @pytest.mark.asyncio
    async def test_list_sources_accepts_project_id(self, mock_storage):
        """list_sources accepts ?project_id=org_abc."""
        mock_qdrant, mock_mongodb = mock_storage

        with (
            patch("src.tools.sources._qdrant_client", mock_qdrant),
            patch("src.tools.sources._mongodb_client", mock_mongodb),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/list_sources?project_id=org_abc")
                assert response.status_code == 200
                mock_mongodb.list_sources.assert_called_once()
                call_kwargs = mock_mongodb.list_sources.call_args.kwargs
                assert call_kwargs.get("project_id") == "org_abc"

    @pytest.mark.asyncio
    async def test_compare_sources_accepts_project_id(self, mock_storage):
        """compare_sources accepts ?project_id=org_abc."""
        mock_qdrant, mock_mongodb = mock_storage
        # compare_sources requires valid source_ids — mock get_source to return data
        mock_mongodb.get_source = AsyncMock(
            return_value={"id": "src-1", "title": "Test Source"}
        )
        mock_qdrant.get_extractions_for_comparison = AsyncMock(return_value={"src-1": [], "src-2": []})

        with (
            patch("src.tools.sources._qdrant_client", mock_qdrant),
            patch("src.tools.sources._mongodb_client", mock_mongodb),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/compare_sources?topic=rag&source_ids=src-1&source_ids=src-2&project_id=org_abc"
                )
                assert response.status_code == 200
                # Verify project_id was passed to get_source calls
                for call in mock_mongodb.get_source.call_args_list:
                    assert call.kwargs.get("project_id") == "org_abc"


class TestBackwardCompatibility:
    """Tests that requests without project_id work unchanged."""

    @pytest.mark.asyncio
    async def test_get_decisions_without_project_id(self, mock_storage):
        """get_decisions without project_id uses server default."""
        mock_qdrant, mock_mongodb = mock_storage

        with (
            patch("src.tools.decisions._qdrant_client", mock_qdrant),
            patch("src.tools.decisions._mongodb_client", mock_mongodb),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/get_decisions")
                assert response.status_code == 200
                mock_qdrant.list_extractions.assert_called_once()
                call_kwargs = mock_qdrant.list_extractions.call_args.kwargs
                # project_id should be None (letting Qdrant client use default)
                assert call_kwargs.get("project_id") is None
                assert call_kwargs.get("source_id") is None

    @pytest.mark.asyncio
    async def test_list_sources_without_project_id(self, mock_storage):
        """list_sources without project_id uses server default."""
        mock_qdrant, mock_mongodb = mock_storage

        with (
            patch("src.tools.sources._qdrant_client", mock_qdrant),
            patch("src.tools.sources._mongodb_client", mock_mongodb),
        ):
            from src.server import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/list_sources")
                assert response.status_code == 200
                mock_mongodb.list_sources.assert_called_once()
                call_kwargs = mock_mongodb.list_sources.call_args.kwargs
                assert call_kwargs.get("project_id") is None
