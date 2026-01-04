"""Tests for get_patterns endpoint.

Tests the pattern extraction listing and filtering functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestGetPatternsEndpoint:
    """Tests for get_patterns endpoint."""

    def test_patterns_module_import(self):
        """Test that patterns module can be imported."""
        from src.tools.patterns import router

        assert router is not None

    def test_get_patterns_function_exists(self):
        """Test that get_patterns function exists."""
        from src.tools.patterns import get_patterns

        assert get_patterns is not None
        assert callable(get_patterns)

    @pytest.mark.asyncio
    async def test_get_patterns_returns_response_model(self):
        """Test that get_patterns returns PatternsResponse."""
        from src.models.responses import PatternsResponse
        from src.tools.patterns import get_patterns

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_patterns(topic=None, limit=100)

            assert isinstance(result, PatternsResponse)
            assert result.metadata.query == "all"
            assert result.metadata.search_type == "filtered"

    @pytest.mark.asyncio
    async def test_get_patterns_with_topic_filter(self):
        """Test get_patterns with topic filter."""
        from src.tools.patterns import get_patterns

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_patterns(topic="embeddings", limit=100)

            assert result.metadata.query == "embeddings"
            mock_qdrant.list_extractions.assert_called_once_with(
                extraction_type="pattern",
                limit=100,
                topic="embeddings",
            )

    @pytest.mark.asyncio
    async def test_get_patterns_with_results(self):
        """Test get_patterns with actual results."""
        from src.tools.patterns import get_patterns

        mock_results = [
            {
                "id": "pat-1",
                "payload": {
                    "content": {
                        "name": "Retry with Exponential Backoff",
                        "problem": "API calls can fail temporarily",
                        "solution": "Implement retry logic with increasing delays",
                        "code_example": "async def retry(fn, max_retries=3): ...",
                        "context": "When calling external LLM APIs",
                        "trade_offs": ["Increased latency", "More complex code"],
                    },
                    "topics": ["reliability", "api"],
                    "source_title": "Production LLM Systems",
                    "source_id": "src-1",
                    "chunk_id": "chunk-1",
                },
            }
        ]

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_patterns(topic=None, limit=100)

            assert len(result.results) == 1
            assert result.results[0].id == "pat-1"
            assert result.results[0].name == "Retry with Exponential Backoff"
            assert result.results[0].code_example == "async def retry(fn, max_retries=3): ..."
            assert result.results[0].source_title == "Production LLM Systems"
            assert "Production LLM Systems" in result.metadata.sources_cited

    @pytest.mark.asyncio
    async def test_get_patterns_empty_results(self):
        """Test get_patterns with no results."""
        from src.tools.patterns import get_patterns

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_patterns(topic="nonexistent", limit=100)

            assert len(result.results) == 0
            assert result.metadata.result_count == 0
            assert result.metadata.sources_cited == []

    @pytest.mark.asyncio
    async def test_get_patterns_no_client(self):
        """Test get_patterns when Qdrant client is unavailable."""
        from src.tools.patterns import get_patterns

        with patch("src.tools.patterns.get_qdrant_client", return_value=None):
            result = await get_patterns(topic=None, limit=100)

            assert len(result.results) == 0
            assert result.metadata.result_count == 0

    @pytest.mark.asyncio
    async def test_get_patterns_maps_content_correctly(self):
        """Test that pattern payload fields are mapped correctly."""
        from src.tools.patterns import get_patterns

        mock_results = [
            {
                "id": "pat-2",
                "payload": {
                    "content": {
                        "name": "Semantic Caching",
                        "problem": "Repeated similar queries are expensive",
                        "solution": "Cache responses keyed by embedding similarity",
                        "code_example": None,
                        "context": "High-traffic LLM applications",
                        "trade_offs": ["Memory usage", "Cache invalidation"],
                    },
                    "topics": ["caching", "performance"],
                    "source_title": "LLM Optimization Guide",
                    "source_id": "src-2",
                    "chunk_id": "chunk-2",
                },
            }
        ]

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_patterns(topic=None, limit=100)

            pattern = result.results[0]
            assert pattern.name == "Semantic Caching"
            assert pattern.problem == "Repeated similar queries are expensive"
            assert pattern.solution == "Cache responses keyed by embedding similarity"
            assert pattern.code_example is None
            assert pattern.context == "High-traffic LLM applications"
            assert pattern.trade_offs == ["Memory usage", "Cache invalidation"]


class TestPatternsEndpointRouter:
    """Tests for patterns endpoint router configuration."""

    def test_router_has_correct_routes(self):
        """Test that router has expected routes."""
        from src.tools.patterns import router

        assert len(router.routes) > 0

    def test_get_patterns_has_operation_id(self):
        """Test that get_patterns endpoint has explicit operation_id."""
        from src.tools.patterns import router

        route = None
        for r in router.routes:
            if hasattr(r, "operation_id") and r.operation_id == "get_patterns":
                route = r
                break

        assert route is not None, "get_patterns route with operation_id not found"


class TestPatternPayloadMapping:
    """Tests for payload mapping edge cases."""

    @pytest.mark.asyncio
    async def test_handles_string_content(self):
        """Test mapping when content is a string instead of dict."""
        from src.tools.patterns import get_patterns

        mock_results = [
            {
                "id": "pat-3",
                "payload": {
                    "content": "Simple solution text",
                    "extraction_title": "Pattern Title",
                    "topics": [],
                    "source_title": "Source",
                    "source_id": "src-3",
                },
            }
        ]

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_patterns(topic=None, limit=100)

            assert len(result.results) == 1
            assert result.results[0].solution == "Simple solution text"

    @pytest.mark.asyncio
    async def test_handles_missing_optional_fields(self):
        """Test mapping when optional fields are missing."""
        from src.tools.patterns import get_patterns

        mock_results = [
            {
                "id": "pat-4",
                "payload": {
                    "content": {
                        "name": "Minimal Pattern",
                        "problem": "A problem",
                        "solution": "A solution",
                    },
                    "source_title": "Source",
                    "source_id": "src-4",
                },
            }
        ]

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_patterns(topic=None, limit=100)

            pattern = result.results[0]
            assert pattern.name == "Minimal Pattern"
            assert pattern.code_example is None
            assert pattern.context is None
            assert pattern.trade_offs is None
            assert pattern.topics == []

    @pytest.mark.asyncio
    async def test_handles_dict_content_missing_name(self):
        """Test mapping when content is dict but name key is missing - uses extraction_title fallback."""
        from src.tools.patterns import get_patterns

        mock_results = [
            {
                "id": "pat-5",
                "payload": {
                    "content": {
                        "problem": "A problem without name",
                        "solution": "A solution",
                    },
                    "extraction_title": "Fallback Pattern Name",
                    "source_title": "Source",
                    "source_id": "src-5",
                },
            }
        ]

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_patterns(topic=None, limit=100)

            pattern = result.results[0]
            assert pattern.name == "Fallback Pattern Name"


class TestPatternsHTTPIntegration:
    """HTTP integration tests for get_patterns endpoint."""

    @pytest.mark.asyncio
    async def test_get_patterns_via_http(self):
        """Test get_patterns endpoint via HTTP client."""
        from httpx import ASGITransport, AsyncClient
        from unittest.mock import AsyncMock, patch

        from src.server import app

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/get_patterns")

                assert response.status_code == 200
                data = response.json()
                assert "results" in data
                assert "metadata" in data
                assert data["metadata"]["search_type"] == "filtered"

    @pytest.mark.asyncio
    async def test_get_patterns_with_topic_via_http(self):
        """Test get_patterns with topic parameter via HTTP."""
        from httpx import ASGITransport, AsyncClient
        from unittest.mock import AsyncMock, patch

        from src.server import app

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/get_patterns", params={"topic": "caching"})

                assert response.status_code == 200
                data = response.json()
                assert data["metadata"]["query"] == "caching"

    @pytest.mark.asyncio
    async def test_get_patterns_limit_validation_too_low(self):
        """Test that limit=0 is rejected."""
        from httpx import ASGITransport, AsyncClient

        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/get_patterns", params={"limit": 0})

            # Story 4.6: Validation errors now return 400 (VALIDATION_ERROR) per architecture.md
            assert response.status_code == 400
            data = response.json()
            assert data["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_get_patterns_limit_validation_too_high(self):
        """Test that limit=501 is rejected."""
        from httpx import ASGITransport, AsyncClient

        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/get_patterns", params={"limit": 501})

            # Story 4.6: Validation errors now return 400 (VALIDATION_ERROR) per architecture.md
            assert response.status_code == 400
            data = response.json()
            assert data["error"]["code"] == "VALIDATION_ERROR"


class TestPatternsErrorHandling:
    """Tests for error handling in get_patterns endpoint."""

    @pytest.mark.asyncio
    async def test_get_patterns_handles_runtime_error(self):
        """Test that RuntimeError from Qdrant is converted to KnowledgeError."""
        from src.exceptions import KnowledgeError
        from src.tools.patterns import get_patterns

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(
                side_effect=RuntimeError("Qdrant client not connected")
            )
            mock_get_qdrant.return_value = mock_qdrant

            with pytest.raises(KnowledgeError) as exc_info:
                await get_patterns(topic=None, limit=100)

            assert exc_info.value.code == "INTERNAL_ERROR"
            assert "pattern" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_get_patterns_handles_unexpected_error(self):
        """Test that unexpected exceptions are converted to KnowledgeError."""
        from src.exceptions import KnowledgeError
        from src.tools.patterns import get_patterns

        with patch("src.tools.patterns.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(
                side_effect=ValueError("Unexpected error")
            )
            mock_get_qdrant.return_value = mock_qdrant

            with pytest.raises(KnowledgeError) as exc_info:
                await get_patterns(topic=None, limit=100)

            assert exc_info.value.code == "INTERNAL_ERROR"
            assert "error_type" in exc_info.value.details
