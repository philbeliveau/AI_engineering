"""Tests for get_methodologies endpoint.

Tests the methodology extraction listing and filtering functionality,
including Registered tier authentication requirement.
"""

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.exceptions import ForbiddenError
from src.middleware.auth import APIKeyValidator, AuthMiddleware
from src.models.auth import APIKey, AuthContext, UserTier
from src.models.responses import MethodologyResponse


class TestGetMethodologiesEndpoint:
    """Tests for get_methodologies endpoint."""

    def test_methodologies_module_import(self):
        """Test that methodologies module can be imported."""
        from src.tools.methodologies import router

        assert router is not None

    def test_get_methodologies_function_exists(self):
        """Test that get_methodologies function exists."""
        from src.tools.methodologies import get_methodologies

        assert get_methodologies is not None
        assert callable(get_methodologies)

    @pytest.mark.asyncio
    async def test_get_methodologies_returns_response_model(self):
        """Test that get_methodologies returns MethodologyResponse."""
        from src.tools.methodologies import get_methodologies

        # Create mock request and auth context
        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            assert isinstance(result, MethodologyResponse)
            assert result.metadata.query == "all"
            assert result.metadata.search_type == "filtered"

    @pytest.mark.asyncio
    async def test_get_methodologies_with_topic_filter(self):
        """Test get_methodologies with topic filter."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic="rag",
                limit=100,
                auth_context=mock_auth,
            )

            assert result.metadata.query == "rag"
            mock_qdrant.list_extractions.assert_called_once_with(
                extraction_type="methodology",
                limit=100,
                topic="rag",
            )

    @pytest.mark.asyncio
    async def test_get_methodologies_with_results(self):
        """Test get_methodologies with actual results."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_results = [
            {
                "id": "meth-1",
                "payload": {
                    "content": {
                        "name": "RAG System Design",
                        "steps": [
                            "Define use case requirements",
                            "Choose embedding model",
                            "Select vector database",
                            "Implement retrieval pipeline",
                            "Add reranking layer",
                        ],
                        "prerequisites": ["Python knowledge", "LLM API access"],
                        "outputs": ["Working RAG system", "API endpoint"],
                    },
                    "topics": ["rag", "architecture"],
                    "source_title": "LLM Engineering Handbook",
                    "source_id": "src-1",
                    "chunk_id": "chunk-1",
                },
            }
        ]

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            assert len(result.results) == 1
            assert result.results[0].id == "meth-1"
            assert result.results[0].name == "RAG System Design"
            assert len(result.results[0].steps) == 5
            assert result.results[0].prerequisites == ["Python knowledge", "LLM API access"]
            assert result.results[0].outputs == ["Working RAG system", "API endpoint"]
            assert result.results[0].source_title == "LLM Engineering Handbook"
            assert "LLM Engineering Handbook" in result.metadata.sources_cited

    @pytest.mark.asyncio
    async def test_get_methodologies_empty_results(self):
        """Test get_methodologies with no results."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic="nonexistent",
                limit=100,
                auth_context=mock_auth,
            )

            assert len(result.results) == 0
            assert result.metadata.result_count == 0
            assert result.metadata.sources_cited == []

    @pytest.mark.asyncio
    async def test_get_methodologies_no_client(self):
        """Test get_methodologies when Qdrant client is unavailable."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        with patch("src.tools.methodologies.get_qdrant_client", return_value=None):
            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            assert len(result.results) == 0
            assert result.metadata.result_count == 0


class TestMethodologiesEndpointRouter:
    """Tests for methodologies endpoint router configuration."""

    def test_router_has_correct_routes(self):
        """Test that router has expected routes."""
        from src.tools.methodologies import router

        assert len(router.routes) > 0

    def test_get_methodologies_has_operation_id(self):
        """Test that get_methodologies endpoint has explicit operation_id."""
        from src.tools.methodologies import router

        route = None
        for r in router.routes:
            if hasattr(r, "operation_id") and r.operation_id == "get_methodologies":
                route = r
                break

        assert route is not None, "get_methodologies route with operation_id not found"


class TestMethodologyPayloadMapping:
    """Tests for payload mapping edge cases."""

    @pytest.mark.asyncio
    async def test_handles_missing_optional_fields(self):
        """Test mapping when optional fields are missing."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_results = [
            {
                "id": "meth-2",
                "payload": {
                    "content": {
                        "name": "Basic Methodology",
                        "steps": ["Step 1", "Step 2"],
                    },
                    "source_title": "Source Book",
                    "source_id": "src-2",
                },
            }
        ]

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            methodology = result.results[0]
            assert methodology.name == "Basic Methodology"
            assert methodology.steps == ["Step 1", "Step 2"]
            assert methodology.prerequisites is None
            assert methodology.outputs is None
            assert methodology.topics == []

    @pytest.mark.asyncio
    async def test_skips_invalid_content_format(self):
        """Test that string content (instead of dict) is skipped."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_results = [
            {
                "id": "meth-3",
                "payload": {
                    "content": "This is a string, not a dict",
                    "source_title": "Source",
                    "source_id": "src-3",
                },
            }
        ]

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_skips_missing_required_fields(self):
        """Test that content missing name or steps is skipped."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_results = [
            {
                "id": "meth-4",
                "payload": {
                    "content": {
                        "name": "Has name but no steps",
                    },
                    "source_title": "Source",
                    "source_id": "src-4",
                },
            },
            {
                "id": "meth-5",
                "payload": {
                    "content": {
                        "steps": ["Has steps but no name"],
                    },
                    "source_title": "Source",
                    "source_id": "src-5",
                },
            },
        ]

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            assert len(result.results) == 0


class TestMethodologiesAuthentication:
    """Tests for Registered tier authentication requirement (AC #5, #6)."""

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
        """Create test FastAPI app with methodologies endpoint."""
        from src.tools.methodologies import router as methodologies_router

        app = FastAPI()

        # Add ForbiddenError handler
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

        app.add_middleware(AuthMiddleware, validator=validator)
        app.include_router(methodologies_router)

        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create test client."""
        return TestClient(app, raise_server_exceptions=False)

    def test_returns_403_without_api_key(self, client: TestClient) -> None:
        """Test that endpoint returns 403 without API key (AC #5)."""
        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            response = client.get("/get_methodologies")

            assert response.status_code == 403
            data = response.json()
            assert data["error"]["code"] == "FORBIDDEN"
            assert data["error"]["details"]["current_tier"] == "PUBLIC"

    def test_returns_403_with_public_tier(self, client: TestClient) -> None:
        """Test that PUBLIC tier gets 403 Forbidden (AC #6)."""
        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            # No API key = PUBLIC tier
            response = client.get("/get_methodologies")

            assert response.status_code == 403
            data = response.json()
            assert data["error"]["code"] == "FORBIDDEN"
            assert "REGISTERED" in data["error"]["message"]

    def test_returns_200_with_registered_key(self, client: TestClient) -> None:
        """Test that Registered tier key returns 200 (AC #1)."""
        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            response = client.get(
                "/get_methodologies",
                headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert "metadata" in data

    def test_returns_200_with_premium_key(self, client: TestClient) -> None:
        """Test that Premium tier key also works (tier hierarchy)."""
        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            response = client.get(
                "/get_methodologies",
                headers={"X-API-Key": "kp_11111111111111111111111111111111"},
            )

            assert response.status_code == 200

    def test_returns_401_with_invalid_key(self, client: TestClient) -> None:
        """Test that invalid API key returns 401 Unauthorized."""
        response = client.get(
            "/get_methodologies",
            headers={"X-API-Key": "kp_00000000000000000000000000000000"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"


class TestMethodologiesResponseFormat:
    """Tests for response format (AC #4)."""

    @pytest.mark.asyncio
    async def test_response_has_results_array(self):
        """Test that response contains results array."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            assert hasattr(result, "results")
            assert isinstance(result.results, list)

    @pytest.mark.asyncio
    async def test_response_has_metadata(self):
        """Test that response contains metadata with required fields."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic="rag",
                limit=100,
                auth_context=mock_auth,
            )

            assert hasattr(result, "metadata")
            assert result.metadata.query == "rag"
            assert isinstance(result.metadata.sources_cited, list)
            assert result.metadata.result_count == 0
            assert result.metadata.search_type == "filtered"


class TestMethodologiesSourceAttribution:
    """Tests for source attribution (AC #3)."""

    @pytest.mark.asyncio
    async def test_results_include_source_attribution(self):
        """Test that results include source_id, chunk_id, and source_title."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_results = [
            {
                "id": "meth-6",
                "payload": {
                    "content": {
                        "name": "Test Methodology",
                        "steps": ["Step 1"],
                    },
                    "topics": ["testing"],
                    "source_title": "Testing Handbook",
                    "source_id": "src-test",
                    "chunk_id": "chunk-test",
                },
            }
        ]

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            methodology = result.results[0]
            assert methodology.source_id == "src-test"
            assert methodology.chunk_id == "chunk-test"
            assert methodology.source_title == "Testing Handbook"

    @pytest.mark.asyncio
    async def test_sources_cited_in_metadata(self):
        """Test that sources are listed in metadata.sources_cited."""
        from src.tools.methodologies import get_methodologies

        mock_request = MagicMock()
        mock_auth = AuthContext(tier=UserTier.REGISTERED, authenticated=True)

        mock_results = [
            {
                "id": "meth-7",
                "payload": {
                    "content": {"name": "Method 1", "steps": ["Step"]},
                    "source_title": "Book A",
                    "source_id": "src-a",
                },
            },
            {
                "id": "meth-8",
                "payload": {
                    "content": {"name": "Method 2", "steps": ["Step"]},
                    "source_title": "Book B",
                    "source_id": "src-b",
                },
            },
            {
                "id": "meth-9",
                "payload": {
                    "content": {"name": "Method 3", "steps": ["Step"]},
                    "source_title": "Book A",
                    "source_id": "src-a",
                },
            },
        ]

        with patch("src.tools.methodologies.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_methodologies(
                request=mock_request,
                topic=None,
                limit=100,
                auth_context=mock_auth,
            )

            assert len(result.metadata.sources_cited) == 2
            assert "Book A" in result.metadata.sources_cited
            assert "Book B" in result.metadata.sources_cited


class TestServerIntegration:
    """Integration tests for get_methodologies in actual server."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for actual server app."""
        from src.server import app

        return TestClient(app, raise_server_exceptions=False)

    def test_methodologies_endpoint_registered_in_server(self, client: TestClient) -> None:
        """Test that get_methodologies endpoint exists in server."""
        # Without API key, should get 403 (Registered tier required)
        response = client.get("/get_methodologies")
        # 403 = endpoint exists but requires auth
        assert response.status_code == 403

    def test_methodologies_returns_401_for_invalid_key(self, client: TestClient) -> None:
        """Test that invalid API key returns 401."""
        response = client.get(
            "/get_methodologies",
            headers={"X-API-Key": "kp_00000000000000000000000000000000"},
        )
        assert response.status_code == 401

    def test_methodologies_available_in_mcp(self) -> None:
        """Test that get_methodologies is available as MCP tool."""
        from src.server import app

        # Check that the route exists with correct operation_id
        route_found = False
        for route in app.routes:
            if hasattr(route, "operation_id") and route.operation_id == "get_methodologies":
                route_found = True
                break

        assert route_found, "get_methodologies should be registered in app"
