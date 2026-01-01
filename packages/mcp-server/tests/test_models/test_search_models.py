"""Tests for search request/response models.

Tests SearchKnowledgeRequest, SearchResult, SearchMetadata, and SearchKnowledgeResponse models.
"""

import pytest
from pydantic import ValidationError

from src.models.requests import SearchKnowledgeRequest
from src.models.responses import (
    SearchKnowledgeResponse,
    SearchMetadata,
    SearchResult,
    SourceAttribution,
    SourcePosition,
)


class TestSearchKnowledgeRequest:
    """Tests for SearchKnowledgeRequest model."""

    def test_valid_request_minimal(self):
        """Test creating request with required fields only."""
        request = SearchKnowledgeRequest(query="test query")
        assert request.query == "test query"
        assert request.limit == 10  # Default value

    def test_valid_request_with_limit(self):
        """Test creating request with custom limit."""
        request = SearchKnowledgeRequest(query="test query", limit=20)
        assert request.query == "test query"
        assert request.limit == 20

    def test_limit_validation_minimum(self):
        """Test that limit must be at least 1."""
        with pytest.raises(ValidationError):
            SearchKnowledgeRequest(query="test", limit=0)

    def test_limit_validation_maximum(self):
        """Test that limit cannot exceed 100."""
        with pytest.raises(ValidationError):
            SearchKnowledgeRequest(query="test", limit=101)

    def test_empty_query_validation(self):
        """Test that empty query is rejected."""
        with pytest.raises(ValidationError):
            SearchKnowledgeRequest(query="")


class TestSourcePosition:
    """Tests for SourcePosition model."""

    def test_valid_position(self):
        """Test creating valid source position."""
        position = SourcePosition(chapter="Chapter 1", section="Introduction", page=42)
        assert position.chapter == "Chapter 1"
        assert position.section == "Introduction"
        assert position.page == 42

    def test_optional_fields(self):
        """Test that chapter and section are optional."""
        position = SourcePosition(page=10)
        assert position.chapter is None
        assert position.section is None
        assert position.page == 10


class TestSourceAttribution:
    """Tests for SourceAttribution model."""

    def test_valid_attribution(self):
        """Test creating valid source attribution."""
        attribution = SourceAttribution(
            source_id="src-123",
            title="Test Book",
            authors=["Author One", "Author Two"],
            position=SourcePosition(chapter="Ch 1", section="Sec 1", page=5),
        )
        assert attribution.source_id == "src-123"
        assert attribution.title == "Test Book"
        assert len(attribution.authors) == 2
        assert attribution.position.page == 5

    def test_optional_position(self):
        """Test attribution without position."""
        attribution = SourceAttribution(
            source_id="src-456",
            title="Another Book",
            authors=[],
        )
        assert attribution.position is None
        assert attribution.authors == []


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_valid_chunk_result(self):
        """Test creating valid chunk search result."""
        result = SearchResult(
            id="chunk-123",
            score=0.95,
            type="chunk",
            content="This is the chunk content.",
            source=SourceAttribution(
                source_id="src-001",
                title="Test Source",
                authors=["Test Author"],
            ),
        )
        assert result.id == "chunk-123"
        assert result.score == 0.95
        assert result.type == "chunk"
        assert result.content == "This is the chunk content."
        assert result.source.source_id == "src-001"

    def test_valid_extraction_result(self):
        """Test creating valid extraction search result."""
        result = SearchResult(
            id="ext-456",
            score=0.87,
            type="extraction",
            content="This is extracted knowledge.",
            source=SourceAttribution(
                source_id="src-002",
                title="Another Source",
                authors=["Another Author"],
                position=SourcePosition(chapter="Ch 2", page=100),
            ),
        )
        assert result.type == "extraction"
        assert result.source.position.chapter == "Ch 2"


class TestSearchMetadata:
    """Tests for SearchMetadata model."""

    def test_valid_metadata(self):
        """Test creating valid search metadata."""
        metadata = SearchMetadata(
            query="test search query",
            sources_cited=["Source A", "Source B"],
            result_count=5,
            search_type="semantic",
        )
        assert metadata.query == "test search query"
        assert len(metadata.sources_cited) == 2
        assert metadata.result_count == 5
        assert metadata.search_type == "semantic"

    def test_empty_sources(self):
        """Test metadata with no sources."""
        metadata = SearchMetadata(
            query="no results query",
            sources_cited=[],
            result_count=0,
            search_type="semantic",
        )
        assert metadata.sources_cited == []
        assert metadata.result_count == 0


class TestSearchKnowledgeResponse:
    """Tests for SearchKnowledgeResponse model."""

    def test_valid_response(self):
        """Test creating valid search response."""
        response = SearchKnowledgeResponse(
            results=[
                SearchResult(
                    id="res-1",
                    score=0.9,
                    type="chunk",
                    content="Content 1",
                    source=SourceAttribution(
                        source_id="src-1",
                        title="Source 1",
                        authors=["Author"],
                    ),
                ),
            ],
            metadata=SearchMetadata(
                query="test",
                sources_cited=["Source 1"],
                result_count=1,
                search_type="semantic",
            ),
        )
        assert len(response.results) == 1
        assert response.metadata.result_count == 1

    def test_empty_response(self):
        """Test response with no results."""
        response = SearchKnowledgeResponse(
            results=[],
            metadata=SearchMetadata(
                query="empty query",
                sources_cited=[],
                result_count=0,
                search_type="semantic",
            ),
        )
        assert len(response.results) == 0
        assert response.metadata.result_count == 0
