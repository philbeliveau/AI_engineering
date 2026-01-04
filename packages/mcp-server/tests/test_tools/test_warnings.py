"""Tests for get_warnings endpoint.

Tests the warning extraction listing and filtering functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestGetWarningsEndpoint:
    """Tests for get_warnings endpoint."""

    def test_warnings_module_import(self):
        """Test that warnings module can be imported."""
        from src.tools.warnings import router

        assert router is not None

    def test_get_warnings_function_exists(self):
        """Test that get_warnings function exists."""
        from src.tools.warnings import get_warnings

        assert get_warnings is not None
        assert callable(get_warnings)

    @pytest.mark.asyncio
    async def test_get_warnings_returns_response_model(self):
        """Test that get_warnings returns WarningsResponse."""
        from src.models.responses import WarningsResponse
        from src.tools.warnings import get_warnings

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_warnings(topic=None, limit=100)

            assert isinstance(result, WarningsResponse)
            assert result.metadata.query == "all"
            assert result.metadata.search_type == "filtered"

    @pytest.mark.asyncio
    async def test_get_warnings_with_topic_filter(self):
        """Test get_warnings with topic filter."""
        from src.tools.warnings import get_warnings

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_warnings(topic="security", limit=100)

            assert result.metadata.query == "security"
            mock_qdrant.list_extractions.assert_called_once_with(
                extraction_type="warning",
                limit=100,
                topic="security",
            )

    @pytest.mark.asyncio
    async def test_get_warnings_with_results(self):
        """Test get_warnings with actual results."""
        from src.tools.warnings import get_warnings

        mock_results = [
            {
                "id": "warn-1",
                "payload": {
                    "content": {
                        "title": "Prompt Injection Vulnerability",
                        "description": "User input can manipulate LLM behavior",
                        "symptoms": ["Unexpected outputs", "Ignored instructions"],
                        "consequences": ["Data leakage", "Unauthorized actions"],
                        "prevention": "Use input validation and output filtering",
                    },
                    "topics": ["security", "prompt-engineering"],
                    "source_title": "LLM Security Best Practices",
                    "source_id": "src-1",
                    "chunk_id": "chunk-1",
                },
            }
        ]

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_warnings(topic=None, limit=100)

            assert len(result.results) == 1
            assert result.results[0].id == "warn-1"
            assert result.results[0].title == "Prompt Injection Vulnerability"
            assert "Data leakage" in result.results[0].consequences
            assert result.results[0].source_title == "LLM Security Best Practices"
            assert "LLM Security Best Practices" in result.metadata.sources_cited

    @pytest.mark.asyncio
    async def test_get_warnings_empty_results(self):
        """Test get_warnings with no results."""
        from src.tools.warnings import get_warnings

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_warnings(topic="nonexistent", limit=100)

            assert len(result.results) == 0
            assert result.metadata.result_count == 0
            assert result.metadata.sources_cited == []

    @pytest.mark.asyncio
    async def test_get_warnings_no_client(self):
        """Test get_warnings when Qdrant client is unavailable."""
        from src.tools.warnings import get_warnings

        with patch("src.tools.warnings.get_qdrant_client", return_value=None):
            result = await get_warnings(topic=None, limit=100)

            assert len(result.results) == 0
            assert result.metadata.result_count == 0

    @pytest.mark.asyncio
    async def test_get_warnings_maps_content_correctly(self):
        """Test that warning payload fields are mapped correctly."""
        from src.tools.warnings import get_warnings

        mock_results = [
            {
                "id": "warn-2",
                "payload": {
                    "content": {
                        "title": "Token Limit Exceeded",
                        "description": "Context window overflow causes truncation",
                        "symptoms": ["Incomplete responses", "Missing context"],
                        "consequences": ["Poor quality answers", "Lost information"],
                        "prevention": "Implement chunking and summarization",
                    },
                    "topics": ["context-window", "rag"],
                    "source_title": "RAG Implementation Guide",
                    "source_id": "src-2",
                    "chunk_id": "chunk-2",
                },
            }
        ]

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_warnings(topic=None, limit=100)

            warning = result.results[0]
            assert warning.title == "Token Limit Exceeded"
            assert warning.description == "Context window overflow causes truncation"
            assert warning.symptoms == ["Incomplete responses", "Missing context"]
            assert warning.prevention == "Implement chunking and summarization"
            assert warning.topics == ["context-window", "rag"]


class TestWarningsEndpointRouter:
    """Tests for warnings endpoint router configuration."""

    def test_router_has_correct_routes(self):
        """Test that router has expected routes."""
        from src.tools.warnings import router

        assert len(router.routes) > 0

    def test_get_warnings_has_operation_id(self):
        """Test that get_warnings endpoint has explicit operation_id."""
        from src.tools.warnings import router

        route = None
        for r in router.routes:
            if hasattr(r, "operation_id") and r.operation_id == "get_warnings":
                route = r
                break

        assert route is not None, "get_warnings route with operation_id not found"


class TestWarningPayloadMapping:
    """Tests for payload mapping edge cases."""

    @pytest.mark.asyncio
    async def test_handles_string_content(self):
        """Test mapping when content is a string instead of dict."""
        from src.tools.warnings import get_warnings

        mock_results = [
            {
                "id": "warn-3",
                "payload": {
                    "content": "Simple warning description",
                    "extraction_title": "Warning Title",
                    "topics": [],
                    "source_title": "Source",
                    "source_id": "src-3",
                },
            }
        ]

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_warnings(topic=None, limit=100)

            assert len(result.results) == 1
            assert result.results[0].description == "Simple warning description"

    @pytest.mark.asyncio
    async def test_handles_missing_optional_fields(self):
        """Test mapping when optional fields are missing."""
        from src.tools.warnings import get_warnings

        mock_results = [
            {
                "id": "warn-4",
                "payload": {
                    "content": {
                        "title": "Minimal Warning",
                        "description": "A warning description",
                    },
                    "source_title": "Source",
                    "source_id": "src-4",
                },
            }
        ]

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_warnings(topic=None, limit=100)

            warning = result.results[0]
            assert warning.title == "Minimal Warning"
            assert warning.description == "A warning description"
            assert warning.symptoms is None
            assert warning.consequences is None
            assert warning.prevention is None
            assert warning.topics == []

    @pytest.mark.asyncio
    async def test_handles_dict_content_missing_title(self):
        """Test mapping when content is dict but title key is missing - uses extraction_title fallback."""
        from src.tools.warnings import get_warnings

        mock_results = [
            {
                "id": "warn-5",
                "payload": {
                    "content": {
                        "description": "A warning without title",
                    },
                    "extraction_title": "Fallback Warning Title",
                    "source_title": "Source",
                    "source_id": "src-5",
                },
            }
        ]

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_warnings(topic=None, limit=100)

            warning = result.results[0]
            assert warning.title == "Fallback Warning Title"


class TestWarningsHTTPIntegration:
    """HTTP integration tests for get_warnings endpoint."""

    @pytest.mark.asyncio
    async def test_get_warnings_via_http(self):
        """Test get_warnings endpoint via HTTP client."""
        from httpx import ASGITransport, AsyncClient
        from unittest.mock import AsyncMock, patch

        from src.server import app

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/get_warnings")

                assert response.status_code == 200
                data = response.json()
                assert "results" in data
                assert "metadata" in data
                assert data["metadata"]["search_type"] == "filtered"

    @pytest.mark.asyncio
    async def test_get_warnings_with_topic_via_http(self):
        """Test get_warnings with topic parameter via HTTP."""
        from httpx import ASGITransport, AsyncClient
        from unittest.mock import AsyncMock, patch

        from src.server import app

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/get_warnings", params={"topic": "security"})

                assert response.status_code == 200
                data = response.json()
                assert data["metadata"]["query"] == "security"

    @pytest.mark.asyncio
    async def test_get_warnings_limit_validation_too_low(self):
        """Test that limit=0 is rejected."""
        from httpx import ASGITransport, AsyncClient

        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/get_warnings", params={"limit": 0})

            # Story 4.6: Validation errors now return 400 (VALIDATION_ERROR) per architecture.md
            assert response.status_code == 400
            data = response.json()
            assert data["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_get_warnings_limit_validation_too_high(self):
        """Test that limit=501 is rejected."""
        from httpx import ASGITransport, AsyncClient

        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/get_warnings", params={"limit": 501})

            # Story 4.6: Validation errors now return 400 (VALIDATION_ERROR) per architecture.md
            assert response.status_code == 400
            data = response.json()
            assert data["error"]["code"] == "VALIDATION_ERROR"


class TestWarningsErrorHandling:
    """Tests for error handling in get_warnings endpoint."""

    @pytest.mark.asyncio
    async def test_get_warnings_handles_runtime_error(self):
        """Test that RuntimeError from Qdrant is converted to KnowledgeError."""
        from src.exceptions import KnowledgeError
        from src.tools.warnings import get_warnings

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(
                side_effect=RuntimeError("Qdrant client not connected")
            )
            mock_get_qdrant.return_value = mock_qdrant

            with pytest.raises(KnowledgeError) as exc_info:
                await get_warnings(topic=None, limit=100)

            assert exc_info.value.code == "INTERNAL_ERROR"
            assert "warning" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_get_warnings_handles_unexpected_error(self):
        """Test that unexpected exceptions are converted to KnowledgeError."""
        from src.exceptions import KnowledgeError
        from src.tools.warnings import get_warnings

        with patch("src.tools.warnings.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(
                side_effect=ValueError("Unexpected error")
            )
            mock_get_qdrant.return_value = mock_qdrant

            with pytest.raises(KnowledgeError) as exc_info:
                await get_warnings(topic=None, limit=100)

            assert exc_info.value.code == "INTERNAL_ERROR"
            assert "error_type" in exc_info.value.details
