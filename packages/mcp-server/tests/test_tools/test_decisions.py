"""Tests for get_decisions endpoint.

Tests the decision extraction listing and filtering functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestGetDecisionsEndpoint:
    """Tests for get_decisions endpoint."""

    def test_decisions_module_import(self):
        """Test that decisions module can be imported."""
        from src.tools.decisions import router

        assert router is not None

    def test_get_decisions_function_exists(self):
        """Test that get_decisions function exists."""
        from src.tools.decisions import get_decisions

        assert get_decisions is not None
        assert callable(get_decisions)

    @pytest.mark.asyncio
    async def test_get_decisions_returns_response_model(self):
        """Test that get_decisions returns DecisionsResponse."""
        from src.models.responses import DecisionsResponse
        from src.tools.decisions import get_decisions

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_decisions(topic=None, limit=100)

            assert isinstance(result, DecisionsResponse)
            assert result.metadata.query == "all"
            assert result.metadata.search_type == "filtered"

    @pytest.mark.asyncio
    async def test_get_decisions_with_topic_filter(self):
        """Test get_decisions with topic filter."""
        from src.tools.decisions import get_decisions

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_decisions(topic="rag", limit=100)

            assert result.metadata.query == "rag"
            mock_qdrant.list_extractions.assert_called_once_with(
                extraction_type="decision",
                limit=100,
                topic="rag",
            )

    @pytest.mark.asyncio
    async def test_get_decisions_with_results(self):
        """Test get_decisions with actual results."""
        from src.tools.decisions import get_decisions

        mock_results = [
            {
                "id": "dec-1",
                "payload": {
                    "content": {
                        "question": "Should we use RAG or fine-tuning?",
                        "options": ["RAG", "Fine-tuning", "Hybrid"],
                        "considerations": ["Cost", "Latency", "Quality"],
                        "recommended_approach": "RAG for most use cases",
                    },
                    "topics": ["rag", "fine-tuning"],
                    "source_title": "LLM Engineering Handbook",
                    "source_id": "src-1",
                    "chunk_id": "chunk-1",
                },
            }
        ]

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_decisions(topic=None, limit=100)

            assert len(result.results) == 1
            assert result.results[0].id == "dec-1"
            assert result.results[0].question == "Should we use RAG or fine-tuning?"
            assert result.results[0].options == ["RAG", "Fine-tuning", "Hybrid"]
            assert result.results[0].source_title == "LLM Engineering Handbook"
            assert "LLM Engineering Handbook" in result.metadata.sources_cited

    @pytest.mark.asyncio
    async def test_get_decisions_empty_results(self):
        """Test get_decisions with no results."""
        from src.tools.decisions import get_decisions

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_decisions(topic="nonexistent", limit=100)

            assert len(result.results) == 0
            assert result.metadata.result_count == 0
            assert result.metadata.sources_cited == []

    @pytest.mark.asyncio
    async def test_get_decisions_no_client(self):
        """Test get_decisions when Qdrant client is unavailable."""
        from src.tools.decisions import get_decisions

        with patch("src.tools.decisions.get_qdrant_client", return_value=None):
            result = await get_decisions(topic=None, limit=100)

            assert len(result.results) == 0
            assert result.metadata.result_count == 0

    @pytest.mark.asyncio
    async def test_get_decisions_maps_content_correctly(self):
        """Test that decision payload fields are mapped correctly."""
        from src.tools.decisions import get_decisions

        mock_results = [
            {
                "id": "dec-2",
                "payload": {
                    "content": {
                        "question": "Which vector database?",
                        "options": ["Qdrant", "Pinecone", "Weaviate"],
                        "considerations": ["Performance", "Cost", "Features"],
                        "recommended_approach": "Qdrant for self-hosted",
                    },
                    "topics": ["vector-db", "infrastructure"],
                    "source_title": "Building RAG Systems",
                    "source_id": "src-2",
                    "chunk_id": "chunk-2",
                },
            }
        ]

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_decisions(topic=None, limit=100)

            decision = result.results[0]
            assert decision.question == "Which vector database?"
            assert decision.recommended_approach == "Qdrant for self-hosted"
            assert decision.topics == ["vector-db", "infrastructure"]
            assert decision.source_id == "src-2"
            assert decision.chunk_id == "chunk-2"


class TestDecisionsEndpointRouter:
    """Tests for decisions endpoint router configuration."""

    def test_router_has_correct_routes(self):
        """Test that router has expected routes."""
        from src.tools.decisions import router

        assert len(router.routes) > 0

    def test_get_decisions_has_operation_id(self):
        """Test that get_decisions endpoint has explicit operation_id."""
        from src.tools.decisions import router

        route = None
        for r in router.routes:
            if hasattr(r, "operation_id") and r.operation_id == "get_decisions":
                route = r
                break

        assert route is not None, "get_decisions route with operation_id not found"


class TestDecisionPayloadMapping:
    """Tests for payload mapping edge cases."""

    @pytest.mark.asyncio
    async def test_handles_string_content(self):
        """Test mapping when content is a string instead of dict."""
        from src.tools.decisions import get_decisions

        mock_results = [
            {
                "id": "dec-3",
                "payload": {
                    "content": "Simple question text",
                    "extraction_title": "Decision Title",
                    "topics": [],
                    "source_title": "Source",
                    "source_id": "src-3",
                },
            }
        ]

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_decisions(topic=None, limit=100)

            assert len(result.results) == 1
            assert result.results[0].question == "Simple question text"

    @pytest.mark.asyncio
    async def test_handles_missing_optional_fields(self):
        """Test mapping when optional fields are missing."""
        from src.tools.decisions import get_decisions

        mock_results = [
            {
                "id": "dec-4",
                "payload": {
                    "content": {
                        "question": "Minimal decision",
                    },
                    "source_title": "Source",
                    "source_id": "src-4",
                },
            }
        ]

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_decisions(topic=None, limit=100)

            decision = result.results[0]
            assert decision.question == "Minimal decision"
            assert decision.options == []
            assert decision.considerations == []
            assert decision.recommended_approach is None
            assert decision.topics == []

    @pytest.mark.asyncio
    async def test_handles_dict_content_missing_question(self):
        """Test mapping when content is dict but question key is missing - uses extraction_title fallback."""
        from src.tools.decisions import get_decisions

        mock_results = [
            {
                "id": "dec-5",
                "payload": {
                    "content": {
                        "options": ["Option A", "Option B"],
                    },
                    "extraction_title": "Fallback Decision Question",
                    "source_title": "Source",
                    "source_id": "src-5",
                },
            }
        ]

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=mock_results)
            mock_get_qdrant.return_value = mock_qdrant

            result = await get_decisions(topic=None, limit=100)

            decision = result.results[0]
            assert decision.question == "Fallback Decision Question"


class TestDecisionsHTTPIntegration:
    """HTTP integration tests for get_decisions endpoint."""

    @pytest.mark.asyncio
    async def test_get_decisions_via_http(self):
        """Test get_decisions endpoint via HTTP client."""
        from httpx import ASGITransport, AsyncClient
        from unittest.mock import AsyncMock, patch

        from src.server import app

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/get_decisions")

                assert response.status_code == 200
                data = response.json()
                assert "results" in data
                assert "metadata" in data
                assert data["metadata"]["search_type"] == "filtered"

    @pytest.mark.asyncio
    async def test_get_decisions_with_topic_via_http(self):
        """Test get_decisions with topic parameter via HTTP."""
        from httpx import ASGITransport, AsyncClient
        from unittest.mock import AsyncMock, patch

        from src.server import app

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(return_value=[])
            mock_get_qdrant.return_value = mock_qdrant

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/get_decisions", params={"topic": "rag"})

                assert response.status_code == 200
                data = response.json()
                assert data["metadata"]["query"] == "rag"

    @pytest.mark.asyncio
    async def test_get_decisions_limit_validation_too_low(self):
        """Test that limit=0 is rejected."""
        from httpx import ASGITransport, AsyncClient

        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/get_decisions", params={"limit": 0})

            # Story 4.6: Validation errors now return 400 (VALIDATION_ERROR) per architecture.md
            assert response.status_code == 400
            data = response.json()
            assert data["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_get_decisions_limit_validation_too_high(self):
        """Test that limit=501 is rejected."""
        from httpx import ASGITransport, AsyncClient

        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/get_decisions", params={"limit": 501})

            # Story 4.6: Validation errors now return 400 (VALIDATION_ERROR) per architecture.md
            assert response.status_code == 400
            data = response.json()
            assert data["error"]["code"] == "VALIDATION_ERROR"


class TestDecisionsErrorHandling:
    """Tests for error handling in get_decisions endpoint."""

    @pytest.mark.asyncio
    async def test_get_decisions_handles_runtime_error(self):
        """Test that RuntimeError from Qdrant is converted to KnowledgeError."""
        from src.exceptions import KnowledgeError
        from src.tools.decisions import get_decisions

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(
                side_effect=RuntimeError("Qdrant client not connected")
            )
            mock_get_qdrant.return_value = mock_qdrant

            with pytest.raises(KnowledgeError) as exc_info:
                await get_decisions(topic=None, limit=100)

            assert exc_info.value.code == "INTERNAL_ERROR"
            assert "decision" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_get_decisions_handles_unexpected_error(self):
        """Test that unexpected exceptions are converted to KnowledgeError."""
        from src.exceptions import KnowledgeError
        from src.tools.decisions import get_decisions

        with patch("src.tools.decisions.get_qdrant_client") as mock_get_qdrant:
            mock_qdrant = AsyncMock()
            mock_qdrant.list_extractions = AsyncMock(
                side_effect=ValueError("Unexpected error")
            )
            mock_get_qdrant.return_value = mock_qdrant

            with pytest.raises(KnowledgeError) as exc_info:
                await get_decisions(topic=None, limit=100)

            assert exc_info.value.code == "INTERNAL_ERROR"
            assert "error_type" in exc_info.value.details
