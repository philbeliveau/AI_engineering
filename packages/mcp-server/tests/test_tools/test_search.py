"""Tests for search_knowledge endpoint.

Tests the full search flow: embed query -> search Qdrant -> enrich from MongoDB.
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestSearchKnowledgeEndpoint:
    """Tests for search_knowledge endpoint."""

    def test_search_module_import(self):
        """Test that search module can be imported."""
        from src.tools.search import router

        assert router is not None

    def test_search_knowledge_function_exists(self):
        """Test that search_knowledge function exists."""
        from src.tools.search import search_knowledge

        assert search_knowledge is not None
        assert callable(search_knowledge)

    @pytest.mark.asyncio
    async def test_search_knowledge_returns_response_model(self):
        """Test that search_knowledge returns SearchKnowledgeResponse."""
        from src.models.responses import SearchKnowledgeResponse
        from src.tools.search import search_knowledge

        # Mock dependencies
        mock_embedding = [0.1] * 384

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=[])
                    mock_qdrant.search_extractions = AsyncMock(return_value=[])
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_mongo.get_source = AsyncMock(return_value=None)
                    mock_get_mongo.return_value = mock_mongo

                    result = await search_knowledge(query="test query", limit=10)

                    assert isinstance(result, SearchKnowledgeResponse)
                    assert result.metadata.query == "test query"
                    assert result.metadata.search_type == "semantic"

    @pytest.mark.asyncio
    async def test_search_knowledge_with_results(self):
        """Test search_knowledge with actual results."""
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384
        mock_chunk_results = [
            {
                "id": "chunk-1",
                "score": 0.95,
                "payload": {
                    "source_id": "src-1",
                    "content": "Test chunk content",
                    "position": {"chapter": "Ch 1", "page": 10},
                },
            }
        ]
        mock_source = {
            "id": "src-1",
            "title": "Test Book",
            "authors": ["Test Author"],
        }

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=mock_chunk_results)
                    mock_qdrant.search_extractions = AsyncMock(return_value=[])
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_mongo.get_source = AsyncMock(return_value=mock_source)
                    mock_get_mongo.return_value = mock_mongo

                    result = await search_knowledge(query="test query", limit=10)

                    assert len(result.results) == 1
                    assert result.results[0].id == "chunk-1"
                    assert result.results[0].score == 0.95
                    assert result.results[0].type == "chunk"
                    assert result.results[0].source.title == "Test Book"

    @pytest.mark.asyncio
    async def test_search_knowledge_merges_chunks_and_extractions(self):
        """Test that chunks and extractions are merged and sorted by score."""
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384
        mock_chunk_results = [
            {
                "id": "chunk-1",
                "score": 0.80,
                "payload": {"source_id": "src-1", "content": "Chunk content"},
            }
        ]
        mock_extraction_results = [
            {
                "id": "ext-1",
                "score": 0.95,  # Higher score should come first
                "payload": {
                    "source_id": "src-1",
                    "chunk_id": "chunk-1",
                    "type": "decision",
                    "content": {"title": "Decision"},
                },
            }
        ]
        mock_source = {"id": "src-1", "title": "Test", "authors": []}

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=mock_chunk_results)
                    mock_qdrant.search_extractions = AsyncMock(
                        return_value=mock_extraction_results
                    )
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_mongo.get_source = AsyncMock(return_value=mock_source)
                    mock_get_mongo.return_value = mock_mongo

                    result = await search_knowledge(query="test", limit=10)

                    # Results should be sorted by score (highest first)
                    assert len(result.results) == 2
                    assert result.results[0].id == "ext-1"  # Higher score
                    assert result.results[0].score == 0.95
                    assert result.results[1].id == "chunk-1"  # Lower score
                    assert result.results[1].score == 0.80

    @pytest.mark.asyncio
    async def test_search_knowledge_empty_results(self):
        """Test search_knowledge with no results."""
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=[])
                    mock_qdrant.search_extractions = AsyncMock(return_value=[])
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_get_mongo.return_value = mock_mongo

                    result = await search_knowledge(query="no results query", limit=10)

                    assert len(result.results) == 0
                    assert result.metadata.result_count == 0
                    assert result.metadata.sources_cited == []

    @pytest.mark.asyncio
    async def test_search_knowledge_respects_limit(self):
        """Test that search_knowledge respects the limit parameter."""
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384
        # Create 20 mock results
        mock_results = [
            {
                "id": f"chunk-{i}",
                "score": 0.9 - (i * 0.01),
                "payload": {"source_id": "src-1", "content": f"Content {i}"},
            }
            for i in range(20)
        ]
        mock_source = {"id": "src-1", "title": "Test", "authors": []}

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=mock_results[:10])
                    mock_qdrant.search_extractions = AsyncMock(return_value=[])
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_mongo.get_source = AsyncMock(return_value=mock_source)
                    mock_get_mongo.return_value = mock_mongo

                    result = await search_knowledge(query="test", limit=5)

                    # Should have at most 5 results
                    assert len(result.results) <= 5

    @pytest.mark.asyncio
    async def test_search_knowledge_includes_source_attribution(self):
        """Test that results include proper source attribution."""
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384
        mock_chunk_results = [
            {
                "id": "chunk-1",
                "score": 0.9,
                "payload": {
                    "source_id": "src-1",
                    "content": "Content",
                    "position": {"chapter": "Chapter 1", "section": "Section 1", "page": 42},
                },
            }
        ]
        mock_source = {
            "id": "src-1",
            "title": "Advanced AI Engineering",
            "authors": ["John Doe", "Jane Smith"],
        }

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=mock_chunk_results)
                    mock_qdrant.search_extractions = AsyncMock(return_value=[])
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_mongo.get_source = AsyncMock(return_value=mock_source)
                    mock_get_mongo.return_value = mock_mongo

                    result = await search_knowledge(query="test", limit=10)

                    assert len(result.results) == 1
                    source = result.results[0].source
                    assert source.source_id == "src-1"
                    assert source.title == "Advanced AI Engineering"
                    assert source.authors == ["John Doe", "Jane Smith"]
                    assert source.position is not None
                    assert source.position.chapter == "Chapter 1"
                    assert source.position.page == 42


class TestSearchEndpointRouter:
    """Tests for search endpoint router configuration."""

    def test_router_has_correct_prefix(self):
        """Test that router is properly configured."""
        from src.tools.search import router

        # Check that router has routes
        assert len(router.routes) > 0

    def test_search_knowledge_has_operation_id(self):
        """Test that search_knowledge endpoint has explicit operation_id."""
        from src.tools.search import router

        # Find the search_knowledge route
        route = None
        for r in router.routes:
            if hasattr(r, "operation_id") and r.operation_id == "search_knowledge":
                route = r
                break

        assert route is not None, "search_knowledge route with operation_id not found"


class TestSearchPerformance:
    """Performance tests for search_knowledge endpoint."""

    @pytest.mark.asyncio
    async def test_search_endpoint_logic_under_100ms(self):
        """Test that endpoint logic (excluding embedding) is fast.

        This test validates the endpoint coordination overhead is minimal.
        Embedding generation is mocked to isolate endpoint logic.

        Note: Full AC6 (<500ms) validation requires integration tests with
        real embedding model. This unit test ensures the endpoint logic
        itself doesn't introduce significant latency.
        """
        import time

        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=[])
                    mock_qdrant.search_extractions = AsyncMock(return_value=[])
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_get_mongo.return_value = mock_mongo

                    start = time.time()
                    await search_knowledge(query="performance test", limit=10)
                    elapsed_ms = (time.time() - start) * 1000

                    # Endpoint logic should be very fast (<100ms) when storage is mocked
                    assert elapsed_ms < 100, f"Endpoint logic took {elapsed_ms:.2f}ms"

    @pytest.mark.asyncio
    async def test_search_with_real_embedding_under_500ms(self):
        """Test full search including embedding generation meets <500ms target.

        This integration test validates AC6 with real embedding generation.
        Requires fastembed model to be available.
        """
        import time

        from src.tools.search import search_knowledge

        with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
            with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                mock_qdrant = AsyncMock()
                mock_qdrant.search_chunks = AsyncMock(return_value=[])
                mock_qdrant.search_extractions = AsyncMock(return_value=[])
                mock_get_qdrant.return_value = mock_qdrant

                mock_mongo = AsyncMock()
                mock_get_mongo.return_value = mock_mongo

                start = time.time()
                await search_knowledge(query="real embedding performance test", limit=10)
                elapsed_ms = (time.time() - start) * 1000

                # Full flow including embedding should be under 500ms
                assert elapsed_ms < 500, f"Response time {elapsed_ms:.2f}ms exceeds 500ms limit"


class TestSearchErrorHandling:
    """Tests for error handling in search_knowledge endpoint."""

    @pytest.mark.asyncio
    async def test_search_handles_embedding_failure(self):
        """Test that embedding failures return proper error response."""
        from fastapi import HTTPException

        from src.tools.search import search_knowledge

        with patch("src.tools.search.asyncio.to_thread", side_effect=Exception("Model load failed")):
            with pytest.raises(HTTPException) as exc_info:
                await search_knowledge(query="test", limit=10)

            assert exc_info.value.status_code == 500
            assert "INTERNAL_ERROR" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_search_handles_no_qdrant_client(self):
        """Test that search works gracefully when Qdrant is unavailable."""
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client", return_value=None):
                with patch("src.tools.search.get_mongodb_client", return_value=None):
                    result = await search_knowledge(query="test", limit=10)

                    # Should return empty results, not crash
                    assert len(result.results) == 0
                    assert result.metadata.result_count == 0

    @pytest.mark.asyncio
    async def test_search_handles_missing_source_id_in_payload(self):
        """Test that results with missing source_id are skipped gracefully."""
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384
        # Result with missing source_id
        mock_chunk_results = [
            {
                "id": "chunk-1",
                "score": 0.95,
                "payload": {"content": "No source_id here"},
            }
        ]

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=mock_chunk_results)
                    mock_qdrant.search_extractions = AsyncMock(return_value=[])
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_mongo.get_source = AsyncMock(return_value=None)
                    mock_get_mongo.return_value = mock_mongo

                    result = await search_knowledge(query="test", limit=10)

                    # Result should be skipped due to missing source_id
                    assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_search_handles_mongodb_unavailable(self):
        """Test that search works when MongoDB is unavailable (minimal results)."""
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384
        mock_chunk_results = [
            {
                "id": "chunk-1",
                "score": 0.95,
                "payload": {"source_id": "src-1", "content": "Test content"},
            }
        ]

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client", return_value=None):
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=mock_chunk_results)
                    mock_qdrant.search_extractions = AsyncMock(return_value=[])
                    mock_get_qdrant.return_value = mock_qdrant

                    result = await search_knowledge(query="test", limit=10)

                    # Should return results with minimal attribution
                    assert len(result.results) == 1
                    assert result.results[0].source.title == "Unknown"


class TestSearchIntegration:
    """Integration tests for search flow."""

    @pytest.mark.asyncio
    async def test_full_search_flow(self):
        """Test the complete search flow: embed -> search -> enrich.

        This is an integration test that validates the full search pipeline
        with mocked external services.
        """
        from src.tools.search import search_knowledge

        mock_embedding = [0.1] * 384

        # Simulate realistic search results
        mock_chunk_results = [
            {
                "id": "chunk-001",
                "score": 0.92,
                "payload": {
                    "source_id": "src-book-1",
                    "content": "AI agents can use tools to interact with external systems.",
                    "position": {"chapter": "3", "section": "3.2", "page": 78},
                },
            },
            {
                "id": "chunk-002",
                "score": 0.87,
                "payload": {
                    "source_id": "src-book-1",
                    "content": "Tool selection is a critical capability for autonomous agents.",
                    "position": {"chapter": "3", "section": "3.3", "page": 82},
                },
            },
        ]

        mock_extraction_results = [
            {
                "id": "ext-001",
                "score": 0.89,
                "payload": {
                    "source_id": "src-book-1",
                    "chunk_id": "chunk-001",
                    "type": "pattern",
                    "content": {"name": "Tool Use Pattern", "description": "How to select tools"},
                },
            }
        ]

        mock_source = {
            "id": "src-book-1",
            "title": "Building AI Agents",
            "authors": ["Jane Developer", "John Researcher"],
        }

        with patch("src.tools.search.asyncio.to_thread", return_value=mock_embedding):
            with patch("src.tools.search.get_qdrant_client") as mock_get_qdrant:
                with patch("src.tools.search.get_mongodb_client") as mock_get_mongo:
                    mock_qdrant = AsyncMock()
                    mock_qdrant.search_chunks = AsyncMock(return_value=mock_chunk_results)
                    mock_qdrant.search_extractions = AsyncMock(
                        return_value=mock_extraction_results
                    )
                    mock_get_qdrant.return_value = mock_qdrant

                    mock_mongo = AsyncMock()
                    mock_mongo.get_source = AsyncMock(return_value=mock_source)
                    mock_get_mongo.return_value = mock_mongo

                    result = await search_knowledge(query="AI agent tools", limit=10)

                    # Verify response structure
                    assert result.metadata.query == "AI agent tools"
                    assert result.metadata.search_type == "semantic"

                    # Verify results are merged and sorted by score
                    assert len(result.results) == 3
                    assert result.results[0].score >= result.results[1].score
                    assert result.results[1].score >= result.results[2].score

                    # Verify source attribution
                    for r in result.results:
                        assert r.source.title == "Building AI Agents"
                        assert r.source.source_id == "src-book-1"

                    # Verify sources_cited in metadata
                    assert "Building AI Agents" in result.metadata.sources_cited
