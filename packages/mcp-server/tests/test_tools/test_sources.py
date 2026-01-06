"""Tests for source management endpoints (list_sources, compare_sources).

Tests the source listing and cross-source comparison functionality,
including Public/Registered tier access requirements.
"""

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.exceptions import ForbiddenError, NotFoundError
from src.middleware.auth import APIKeyValidator, AuthMiddleware
from src.models.auth import APIKey, AuthContext, UserTier
from src.models.responses import (
    CompareSourcesResponse,
    SourceListResponse,
)


# ============================================================================
# list_sources Tests (Public Tier)
# ============================================================================


class TestListSourcesEndpoint:
    """Tests for list_sources endpoint."""

    def test_sources_module_import(self):
        """Test that sources module can be imported."""
        from src.tools.sources import router

        assert router is not None

    def test_list_sources_function_exists(self):
        """Test that list_sources function exists."""
        from src.tools.sources import list_sources

        assert list_sources is not None
        assert callable(list_sources)

    @pytest.mark.asyncio
    async def test_list_sources_returns_response_model(self):
        """Test that list_sources returns SourceListResponse."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=[])
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                result = await list_sources(request=mock_request, limit=100)

                assert isinstance(result, SourceListResponse)
                assert result.metadata.query == "all"
                assert result.metadata.search_type == "list"

    @pytest.mark.asyncio
    async def test_list_sources_with_sources(self):
        """Test list_sources with actual sources."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        mock_sources = [
            {
                "id": "src-1",
                "title": "LLM Engineering Handbook",
                "authors": ["John Smith", "Jane Doe"],
                "type": "book",
                "path": "/data/raw/llm-handbook.pdf",
                "ingested_at": "2025-12-28T10:30:00Z",
                "status": "complete",
            },
            {
                "id": "src-2",
                "title": "RAG Survey 2024",
                "authors": ["Alice Brown"],
                "type": "paper",
                "path": "/data/raw/rag-survey.pdf",
                "ingested_at": "2025-12-29T14:00:00Z",
                "status": "complete",
            },
        ]

        # Batch extraction counts for all sources
        mock_all_extraction_counts = {
            "src-1": {"decision": 15, "pattern": 8, "warning": 5},
            "src-2": {"decision": 3, "pattern": 2},
        }

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=mock_sources)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.count_extractions_by_sources = AsyncMock(
                    return_value=mock_all_extraction_counts
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await list_sources(request=mock_request, limit=100)

                assert len(result.results) == 2
                assert result.results[0].id == "src-1"
                assert result.results[0].title == "LLM Engineering Handbook"
                assert result.results[0].authors == ["John Smith", "Jane Doe"]
                assert result.results[0].type == "book"
                assert result.results[0].extraction_counts == {"decision": 15, "pattern": 8, "warning": 5}
                assert result.results[1].extraction_counts == {"decision": 3, "pattern": 2}
                assert result.metadata.result_count == 2

    @pytest.mark.asyncio
    async def test_list_sources_empty_results(self):
        """Test list_sources with no sources."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=[])
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                result = await list_sources(request=mock_request, limit=100)

                assert len(result.results) == 0
                assert result.metadata.result_count == 0
                assert result.metadata.sources_cited == []

    @pytest.mark.asyncio
    async def test_list_sources_no_mongodb_client(self):
        """Test list_sources when MongoDB client is unavailable."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        with patch("src.tools.sources.get_mongodb_client", return_value=None):
            result = await list_sources(request=mock_request, limit=100)

            assert len(result.results) == 0
            assert result.metadata.result_count == 0

    @pytest.mark.asyncio
    async def test_list_sources_handles_qdrant_error(self):
        """Test list_sources handles Qdrant errors gracefully."""
        from qdrant_client.http.exceptions import UnexpectedResponse
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        mock_sources = [{"id": "src-1", "title": "Test Book", "authors": [], "type": "book", "path": "", "ingested_at": "", "status": "complete"}]

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=mock_sources)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.count_extractions_by_sources = AsyncMock(
                    side_effect=UnexpectedResponse(status_code=500, reason_phrase="Internal Error", content=b"", headers={})
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await list_sources(request=mock_request, limit=100)

                # Should still return source, just with empty counts
                assert len(result.results) == 1
                assert result.results[0].extraction_counts == {}

    @pytest.mark.asyncio
    async def test_list_sources_datetime_serialization(self):
        """Test that datetime objects from MongoDB are properly serialized to ISO strings.

        MongoDB returns datetime objects for ingested_at field.
        These must be converted to ISO 8601 strings for JSON serialization.
        This test reproduces the production 500 error where datetime objects
        caused serialization failures.
        """
        from datetime import datetime
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        # Mock MongoDB to return datetime object (as it does in production)
        test_datetime = datetime(2024, 1, 15, 10, 30, 0)
        mock_sources = [
            {
                "id": "test-source",
                "title": "Test Source",
                "type": "book",
                "path": "/test/path",
                "ingested_at": test_datetime,  # datetime object, NOT string
                "status": "complete",
                "authors": ["Test Author"],
            }
        ]

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=mock_sources)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.count_extractions_by_sources = AsyncMock(return_value={})
                mock_get_qdrant.return_value = mock_qdrant

                result = await list_sources(request=mock_request, limit=100)

                # Verify datetime was converted to ISO string
                assert len(result.results) == 1
                assert result.results[0].ingested_at == "2024-01-15T10:30:00"
                assert isinstance(result.results[0].ingested_at, str)

    @pytest.mark.asyncio
    async def test_list_sources_handles_none_datetime(self):
        """Test that None ingested_at values are handled gracefully."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        mock_sources = [
            {
                "id": "test-source",
                "title": "Test Source",
                "type": "book",
                "path": "/test/path",
                "ingested_at": None,  # None value
                "status": "complete",
                "authors": [],
            }
        ]

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=mock_sources)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                result = await list_sources(request=mock_request, limit=100)

                # Should handle None gracefully
                assert len(result.results) == 1
                assert result.results[0].ingested_at == ""

    @pytest.mark.asyncio
    async def test_list_sources_handles_string_datetime(self):
        """Test that string datetime values pass through unchanged."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        mock_sources = [
            {
                "id": "test-source",
                "title": "Test Source",
                "type": "book",
                "path": "/test/path",
                "ingested_at": "2024-01-15T10:30:00Z",  # Already a string
                "status": "complete",
                "authors": [],
            }
        ]

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=mock_sources)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                result = await list_sources(request=mock_request, limit=100)

                # String should pass through
                assert len(result.results) == 1
                assert result.results[0].ingested_at == "2024-01-15T10:30:00Z"


class TestListSourcesNoAuth:
    """Tests for Public tier access (no authentication required)."""

    @pytest.fixture
    def validator(self) -> APIKeyValidator:
        """Create a validator with test keys."""
        v = APIKeyValidator()
        v.register_key(
            APIKey(key="kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6", tier=UserTier.REGISTERED)
        )
        return v

    @pytest.fixture
    def app(self, validator: APIKeyValidator) -> FastAPI:
        """Create test FastAPI app with sources endpoints."""
        from src.tools.sources import router as sources_router

        app = FastAPI()
        app.add_middleware(AuthMiddleware, validator=validator)
        app.include_router(sources_router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create test client."""
        return TestClient(app, raise_server_exceptions=False)

    def test_list_sources_works_without_api_key(self, client: TestClient) -> None:
        """Test that list_sources works without API key (AC #1, Public tier)."""
        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=[])
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                response = client.get("/list_sources")

                assert response.status_code == 200
                data = response.json()
                assert "results" in data
                assert "metadata" in data

    def test_list_sources_also_works_with_api_key(self, client: TestClient) -> None:
        """Test that list_sources also works with API key."""
        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=[])
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                response = client.get(
                    "/list_sources",
                    headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"},
                )

                assert response.status_code == 200


class TestListSourcesResponseFormat:
    """Tests for list_sources response format (AC #2)."""

    @pytest.mark.asyncio
    async def test_response_has_results_array(self):
        """Test that response contains results array."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=[])
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                result = await list_sources(request=mock_request, limit=100)

                assert hasattr(result, "results")
                assert isinstance(result.results, list)

    @pytest.mark.asyncio
    async def test_response_has_metadata(self):
        """Test that response contains metadata with required fields."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=[])
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                result = await list_sources(request=mock_request, limit=100)

                assert hasattr(result, "metadata")
                assert result.metadata.query == "all"
                assert isinstance(result.metadata.sources_cited, list)
                assert result.metadata.result_count == 0
                assert result.metadata.search_type == "list"

    @pytest.mark.asyncio
    async def test_source_result_includes_extraction_counts(self):
        """Test that each source includes extraction_counts (AC #1)."""
        from src.tools.sources import list_sources

        mock_request = MagicMock()

        mock_sources = [
            {
                "id": "src-1",
                "title": "Test Book",
                "authors": [],
                "type": "book",
                "path": "/path",
                "ingested_at": "2025-12-28T10:30:00Z",
                "status": "complete",
            }
        ]

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.list_sources = AsyncMock(return_value=mock_sources)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.count_extractions_by_sources = AsyncMock(
                    return_value={"src-1": {"decision": 5, "pattern": 3}}
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await list_sources(request=mock_request, limit=100)

                assert "extraction_counts" in result.results[0].model_dump()
                assert result.results[0].extraction_counts["decision"] == 5


# ============================================================================
# compare_sources Tests (Registered Tier)
# ============================================================================


class TestCompareSourcesEndpoint:
    """Tests for compare_sources endpoint."""

    def test_compare_sources_function_exists(self):
        """Test that compare_sources function exists."""
        from src.tools.sources import compare_sources

        assert compare_sources is not None
        assert callable(compare_sources)

    @pytest.mark.asyncio
    async def test_compare_sources_returns_response_model(self):
        """Test that compare_sources returns CompareSourcesResponse."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_source = {"id": "src-1", "title": "Test Book"}

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(return_value=mock_source)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value={"src-1": []}
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await compare_sources(
                    request=mock_request,
                    topic="rag",
                    source_ids=["src-1"],
                    limit_per_source=10,
                    auth_context=mock_auth,
                )

                assert isinstance(result, CompareSourcesResponse)
                assert result.metadata.query == "rag"
                assert result.metadata.search_type == "comparison"

    @pytest.mark.asyncio
    async def test_compare_sources_with_extractions(self):
        """Test compare_sources with actual extractions."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_sources = {
            "src-1": {"id": "src-1", "title": "LLM Handbook"},
            "src-2": {"id": "src-2", "title": "RAG Survey 2024"},
        }

        mock_extractions = {
            "src-1": [
                {
                    "id": "ext-1",
                    "payload": {
                        "extraction_type": "decision",
                        "content": {
                            "question": "Which embedding model to use?",
                            "summary": "Recommends all-MiniLM-L6-v2",
                        },
                        "topics": ["embeddings", "rag"],
                    },
                }
            ],
            "src-2": [
                {
                    "id": "ext-2",
                    "payload": {
                        "extraction_type": "decision",
                        "content": {
                            "name": "Embedding model selection",
                            "description": "Suggests BGE-large for accuracy",
                        },
                        "topics": ["embeddings", "rag"],
                    },
                }
            ],
        }

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(side_effect=lambda sid: mock_sources.get(sid))
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value=mock_extractions
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await compare_sources(
                    request=mock_request,
                    topic="embeddings",
                    source_ids=["src-1", "src-2"],
                    limit_per_source=10,
                    auth_context=mock_auth,
                )

                assert len(result.results) == 2
                assert result.results[0].source_id == "src-1"
                assert result.results[0].source_title == "LLM Handbook"
                assert len(result.results[0].extractions) == 1
                assert result.results[1].source_id == "src-2"
                assert "LLM Handbook" in result.metadata.sources_cited
                assert "RAG Survey 2024" in result.metadata.sources_cited

    @pytest.mark.asyncio
    async def test_compare_sources_invalid_source_id(self):
        """Test compare_sources with invalid source_id returns NotFoundError."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(return_value=None)  # Source not found
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_get_qdrant.return_value = mock_qdrant

                with pytest.raises(NotFoundError) as exc_info:
                    await compare_sources(
                        request=mock_request,
                        topic="rag",
                        source_ids=["nonexistent-id"],
                        limit_per_source=10,
                        auth_context=mock_auth,
                    )

                assert "nonexistent-id" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_compare_sources_no_clients(self):
        """Test compare_sources when storage clients are unavailable."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        with patch("src.tools.sources.get_mongodb_client", return_value=None):
            with patch("src.tools.sources.get_qdrant_client", return_value=None):
                result = await compare_sources(
                    request=mock_request,
                    topic="rag",
                    source_ids=["src-1"],
                    limit_per_source=10,
                    auth_context=mock_auth,
                )

                assert len(result.results) == 0
                assert result.metadata.result_count == 0


class TestCompareSourcesAuthentication:
    """Tests for Registered tier authentication requirement (AC #5)."""

    @pytest.fixture
    def validator(self) -> APIKeyValidator:
        """Create a validator with test keys."""
        v = APIKeyValidator()
        v.register_key(
            APIKey(key="kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6", tier=UserTier.REGISTERED)
        )
        v.register_key(
            APIKey(key="kp_11111111111111111111111111111111", tier=UserTier.PREMIUM)
        )
        return v

    @pytest.fixture
    def app(self, validator: APIKeyValidator) -> FastAPI:
        """Create test FastAPI app with sources endpoints."""
        from src.tools.sources import router as sources_router

        app = FastAPI()

        @app.exception_handler(ForbiddenError)
        async def forbidden_handler(request, exc: ForbiddenError):
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                        "details": exc.details,
                    }
                },
            )

        @app.exception_handler(NotFoundError)
        async def not_found_handler(request, exc: NotFoundError):
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                        "details": exc.details,
                    }
                },
            )

        app.add_middleware(AuthMiddleware, validator=validator)
        app.include_router(sources_router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create test client."""
        return TestClient(app, raise_server_exceptions=False)

    def test_returns_403_without_api_key(self, client: TestClient) -> None:
        """Test that compare_sources returns 403 without API key (AC #5)."""
        response = client.get(
            "/compare_sources",
            params={"topic": "rag", "source_ids": ["id1", "id2"]},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"
        assert data["error"]["details"]["current_tier"] == "PUBLIC"

    def test_returns_401_with_invalid_key(self, client: TestClient) -> None:
        """Test that invalid API key returns 401 Unauthorized."""
        response = client.get(
            "/compare_sources",
            params={"topic": "rag", "source_ids": ["id1", "id2"]},
            headers={"X-API-Key": "kp_00000000000000000000000000000000"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_returns_200_or_404_with_registered_key(self, client: TestClient) -> None:
        """Test that Registered tier key is accepted."""
        mock_source = {"id": "src-1", "title": "Test"}

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(return_value=mock_source)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value={"src-1": [], "src-2": []}
                )
                mock_get_qdrant.return_value = mock_qdrant

                response = client.get(
                    "/compare_sources",
                    params={"topic": "rag", "source_ids": ["src-1", "src-2"]},
                    headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"},
                )

                assert response.status_code == 200

    def test_returns_200_with_premium_key(self, client: TestClient) -> None:
        """Test that Premium tier key also works (tier hierarchy)."""
        mock_source = {"id": "src-1", "title": "Test"}

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(return_value=mock_source)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value={"src-1": [], "src-2": []}
                )
                mock_get_qdrant.return_value = mock_qdrant

                response = client.get(
                    "/compare_sources",
                    params={"topic": "rag", "source_ids": ["src-1", "src-2"]},
                    headers={"X-API-Key": "kp_11111111111111111111111111111111"},
                )

                assert response.status_code == 200

    def test_returns_404_for_invalid_source_id(self, client: TestClient) -> None:
        """Test 404 response for invalid source_id (AC #6)."""
        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            # Return None for invalid source, simulating not found
            mock_mongo.get_source = AsyncMock(return_value=None)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_get_qdrant.return_value = mock_qdrant

                response = client.get(
                    "/compare_sources",
                    params={"topic": "rag", "source_ids": ["nonexistent-id-1", "nonexistent-id-2"]},
                    headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"},
                )

                assert response.status_code == 404
                data = response.json()
                assert data["error"]["code"] == "NOT_FOUND"

    def test_returns_422_for_single_source_id(self, client: TestClient) -> None:
        """Test 422 response when fewer than 2 source_ids provided."""
        response = client.get(
            "/compare_sources",
            params={"topic": "rag", "source_ids": ["only-one"]},
            headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"},
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_returns_422_for_empty_source_ids(self, client: TestClient) -> None:
        """Test 422 response when no source_ids provided."""
        response = client.get(
            "/compare_sources",
            params={"topic": "rag"},  # No source_ids
            headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"},
        )

        assert response.status_code == 422  # Validation error


class TestCompareSourcesResponseFormat:
    """Tests for compare_sources response format (AC #4)."""

    @pytest.mark.asyncio
    async def test_response_has_results_grouped_by_source(self):
        """Test that response contains results grouped by source."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_sources = {
            "src-1": {"id": "src-1", "title": "Book A"},
            "src-2": {"id": "src-2", "title": "Book B"},
        }

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(side_effect=lambda sid: mock_sources.get(sid))
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value={"src-1": [], "src-2": []}
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await compare_sources(
                    request=mock_request,
                    topic="rag",
                    source_ids=["src-1", "src-2"],
                    limit_per_source=10,
                    auth_context=mock_auth,
                )

                assert len(result.results) == 2
                assert result.results[0].source_id == "src-1"
                assert result.results[1].source_id == "src-2"

    @pytest.mark.asyncio
    async def test_response_has_metadata(self):
        """Test that response contains metadata with required fields."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_source = {"id": "src-1", "title": "Test Book"}

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(return_value=mock_source)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value={"src-1": []}
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await compare_sources(
                    request=mock_request,
                    topic="embeddings",
                    source_ids=["src-1"],
                    limit_per_source=10,
                    auth_context=mock_auth,
                )

                assert hasattr(result, "metadata")
                assert result.metadata.query == "embeddings"
                assert "Test Book" in result.metadata.sources_cited
                assert result.metadata.result_count == 1
                assert result.metadata.search_type == "comparison"


class TestExtractionSummaryExtraction:
    """Tests for extraction summary extraction helpers."""

    @pytest.mark.asyncio
    async def test_extracts_title_from_name_field(self):
        """Test title extraction from name field."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_source = {"id": "src-1", "title": "Book"}

        mock_extractions = {
            "src-1": [
                {
                    "id": "ext-1",
                    "payload": {
                        "extraction_type": "pattern",
                        "content": {"name": "Retry Pattern"},
                        "topics": [],
                    },
                }
            ]
        }

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(return_value=mock_source)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value=mock_extractions
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await compare_sources(
                    request=mock_request,
                    topic="test",
                    source_ids=["src-1"],
                    limit_per_source=10,
                    auth_context=mock_auth,
                )

                assert result.results[0].extractions[0].title == "Retry Pattern"

    @pytest.mark.asyncio
    async def test_extracts_title_from_question_field(self):
        """Test title extraction from question field."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_source = {"id": "src-1", "title": "Book"}

        mock_extractions = {
            "src-1": [
                {
                    "id": "ext-1",
                    "payload": {
                        "extraction_type": "decision",
                        "content": {"question": "Which model to use?"},
                        "topics": [],
                    },
                }
            ]
        }

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(return_value=mock_source)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value=mock_extractions
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await compare_sources(
                    request=mock_request,
                    topic="test",
                    source_ids=["src-1"],
                    limit_per_source=10,
                    auth_context=mock_auth,
                )

                assert result.results[0].extractions[0].title == "Which model to use?"

    @pytest.mark.asyncio
    async def test_extracts_summary_from_description(self):
        """Test summary extraction from description field."""
        from src.tools.sources import compare_sources

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_source = {"id": "src-1", "title": "Book"}

        mock_extractions = {
            "src-1": [
                {
                    "id": "ext-1",
                    "payload": {
                        "extraction_type": "warning",
                        "content": {"title": "Warning", "description": "Watch out for this!"},
                        "topics": [],
                    },
                }
            ]
        }

        with patch("src.tools.sources.get_mongodb_client") as mock_get_mongo:
            mock_mongo = AsyncMock()
            mock_mongo.get_source = AsyncMock(return_value=mock_source)
            mock_get_mongo.return_value = mock_mongo

            with patch("src.tools.sources.get_qdrant_client") as mock_get_qdrant:
                mock_qdrant = AsyncMock()
                mock_qdrant.get_extractions_for_comparison = AsyncMock(
                    return_value=mock_extractions
                )
                mock_get_qdrant.return_value = mock_qdrant

                result = await compare_sources(
                    request=mock_request,
                    topic="test",
                    source_ids=["src-1"],
                    limit_per_source=10,
                    auth_context=mock_auth,
                )

                assert result.results[0].extractions[0].summary == "Watch out for this!"


# ============================================================================
# Server Integration Tests
# ============================================================================


class TestServerIntegration:
    """Integration tests for sources endpoints in actual server."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for actual server app."""
        from src.server import app

        return TestClient(app, raise_server_exceptions=False)

    def test_list_sources_endpoint_registered_in_server(self, client: TestClient) -> None:
        """Test that list_sources endpoint exists in server."""
        response = client.get("/list_sources")
        # Should get 200 (Public tier - no auth required)
        assert response.status_code == 200

    def test_compare_sources_requires_auth_in_server(self, client: TestClient) -> None:
        """Test that compare_sources requires auth in server."""
        response = client.get(
            "/compare_sources",
            params={"topic": "rag", "source_ids": ["id1"]},
        )
        # Should get 403 (Registered tier required)
        assert response.status_code == 403

    def test_list_sources_available_in_mcp(self) -> None:
        """Test that list_sources is available as MCP tool."""
        from src.server import app

        route_found = False
        for route in app.routes:
            if hasattr(route, "operation_id") and route.operation_id == "list_sources":
                route_found = True
                break

        assert route_found, "list_sources should be registered in app"

    def test_compare_sources_available_in_mcp(self) -> None:
        """Test that compare_sources is available as MCP tool."""
        from src.server import app

        route_found = False
        for route in app.routes:
            if hasattr(route, "operation_id") and route.operation_id == "compare_sources":
                route_found = True
                break

        assert route_found, "compare_sources should be registered in app"


# ============================================================================
# Router Configuration Tests
# ============================================================================


class TestSourcesRouterConfiguration:
    """Tests for sources router configuration."""

    def test_router_has_correct_routes(self):
        """Test that router has expected routes."""
        from src.tools.sources import router

        assert len(router.routes) >= 2  # list_sources and compare_sources

    def test_list_sources_has_operation_id(self):
        """Test that list_sources endpoint has explicit operation_id."""
        from src.tools.sources import router

        route = None
        for r in router.routes:
            if hasattr(r, "operation_id") and r.operation_id == "list_sources":
                route = r
                break

        assert route is not None, "list_sources route with operation_id not found"

    def test_compare_sources_has_operation_id(self):
        """Test that compare_sources endpoint has explicit operation_id."""
        from src.tools.sources import router

        route = None
        for r in router.routes:
            if hasattr(r, "operation_id") and r.operation_id == "compare_sources":
                route = r
                break

        assert route is not None, "compare_sources route with operation_id not found"


# ============================================================================
# Integration Tests (require real databases)
# ============================================================================


@pytest.mark.integration
class TestSourcesIntegration:
    """Integration tests for sources endpoints against real MongoDB and Qdrant.

    These tests require:
    - MONGODB_URI pointing to real MongoDB (Atlas or local)
    - QDRANT_URL pointing to real Qdrant (Cloud or local)

    Run with: pytest -m integration
    Skip with: pytest -m "not integration"
    """

    @pytest.fixture
    def integration_client(self):
        """Create client with real database connections."""
        import os

        # Skip if not in integration test mode
        if not os.getenv("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled (set RUN_INTEGRATION_TESTS=1)")

        from src.server import app
        from starlette.testclient import TestClient

        return TestClient(app)

    @pytest.mark.asyncio
    async def test_list_sources_returns_real_data(self, integration_client):
        """Test list_sources against real databases."""
        response = integration_client.get("/list_sources")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "results" in data
        assert "metadata" in data
        assert data["metadata"]["search_type"] == "list"

        # Each source should have required fields
        for source in data["results"]:
            assert "id" in source
            assert "title" in source
            assert "type" in source
            assert "extraction_counts" in source

    @pytest.mark.asyncio
    async def test_compare_sources_with_real_data(self, integration_client):
        """Test compare_sources against real databases with valid sources."""
        import os

        api_key = os.getenv("TEST_API_KEY")
        if not api_key:
            pytest.skip("TEST_API_KEY not set for integration tests")

        # First get some real source IDs
        list_response = integration_client.get("/list_sources")
        sources = list_response.json().get("results", [])

        if len(sources) < 2:
            pytest.skip("Need at least 2 sources for comparison test")

        source_ids = [s["id"] for s in sources[:2]]

        response = integration_client.get(
            "/compare_sources",
            params={"topic": "testing", "source_ids": source_ids},
            headers={"X-API-Key": api_key},
        )

        assert response.status_code in [200, 404]  # 404 if no extractions for topic

        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "metadata" in data
            assert data["metadata"]["search_type"] == "comparison"
