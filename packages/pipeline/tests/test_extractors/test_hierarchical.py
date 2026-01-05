"""Tests for the hierarchical extractor orchestrator.

Tests cover:
- HierarchicalExtractor initialization
- Document extraction coordination across levels
- Statistics tracking
- Edge cases (empty docs, missing extractors, etc.)
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.extractors.base import (
    Decision,
    ExtractionLevel,
    ExtractionResult,
    ExtractionType,
    Methodology,
    Warning,
)
from src.extractors.hierarchical import (
    HierarchicalExtractor,
    HierarchicalExtractionResult,
    LevelExtractionStats,
)
from src.models.chunk import Chunk, ChunkPosition


# =============================================================================
# Helpers
# =============================================================================


def make_chunk(
    chunk_id: str,
    source_id: str = "507f1f77bcf86cd799439011",
    content: str | None = None,
    chapter: str | None = None,
    section: str | None = None,
    page: int | None = None,
    token_count: int = 100,
) -> Chunk:
    """Factory for creating test chunks with valid IDs.

    Content is auto-generated to be longer than token_count to pass validation.
    """
    # Generate content longer than token_count if not provided
    if content is None:
        content = "x" * (token_count + 50)
    elif len(content) < token_count:
        content = content + "x" * (token_count - len(content) + 50)

    return Chunk(
        id=chunk_id,
        source_id=source_id,
        content=content,
        position=ChunkPosition(chapter=chapter, section=section, page=page),
        token_count=token_count,
    )


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_chunks_with_hierarchy() -> list[Chunk]:
    """Create sample chunks with chapter/section hierarchy."""
    source_id = "507f1f77bcf86cd799439011"
    return [
        make_chunk(
            chunk_id="507f1f77bcf86cd799439001",
            source_id=source_id,
            content="Chapter 1 Section 1 content about RAG methodology steps.",
            chapter="Chapter 1: RAG Architecture",
            section="1.1 Introduction",
            page=1,
            token_count=20,
        ),
        make_chunk(
            chunk_id="507f1f77bcf86cd799439002",
            source_id=source_id,
            content="More content about step 2 of RAG implementation.",
            chapter="Chapter 1: RAG Architecture",
            section="1.1 Introduction",
            page=2,
            token_count=20,
        ),
        make_chunk(
            chunk_id="507f1f77bcf86cd799439003",
            source_id=source_id,
            content="Decision point: choose between vector and keyword search.",
            chapter="Chapter 1: RAG Architecture",
            section="1.2 Retrieval Strategies",
            page=3,
            token_count=20,
        ),
        make_chunk(
            chunk_id="507f1f77bcf86cd799439004",
            source_id=source_id,
            content="Warning: avoid this common embedding mistake.",
            chapter="Chapter 2: Embeddings",
            section="2.1 Common Pitfalls",
            page=10,
            token_count=20,
        ),
    ]


@pytest.fixture
def sample_chunks_no_hierarchy() -> list[Chunk]:
    """Create sample chunks without chapter/section metadata."""
    source_id = "507f1f77bcf86cd799439022"
    return [
        make_chunk(
            chunk_id="507f1f77bcf86cd799439011",
            source_id=source_id,
            content="Content without chapter info.",
            page=1,
            token_count=20,
        ),
        make_chunk(
            chunk_id="507f1f77bcf86cd799439012",
            source_id=source_id,
            content="More content without structure.",
            page=2,
            token_count=20,
        ),
    ]


@pytest.fixture
def mock_decision_result() -> ExtractionResult:
    """Mock successful decision extraction result."""
    decision = Decision(
        source_id="507f1f77bcf86cd799439011",
        chunk_id="507f1f77bcf86cd799439003",
        question="Choose between vector and keyword search?",
        options=["Vector search", "Keyword search"],
        considerations=["Speed", "Accuracy"],
        context_level=ExtractionLevel.SECTION,
        context_id="section-123",
        chunk_ids=["507f1f77bcf86cd799439003"],
    )
    return ExtractionResult(success=True, extraction=decision)


@pytest.fixture
def mock_methodology_result() -> ExtractionResult:
    """Mock successful methodology extraction result."""
    methodology = Methodology(
        source_id="507f1f77bcf86cd799439011",
        chunk_id="507f1f77bcf86cd799439001",
        name="RAG Implementation",
        steps=[],
        context_level=ExtractionLevel.CHAPTER,
        context_id="chapter-123",
        chunk_ids=["507f1f77bcf86cd799439001", "507f1f77bcf86cd799439002"],
    )
    return ExtractionResult(success=True, extraction=methodology)


@pytest.fixture
def mock_warning_result() -> ExtractionResult:
    """Mock successful warning extraction result."""
    warning = Warning(
        source_id="507f1f77bcf86cd799439011",
        chunk_id="507f1f77bcf86cd799439004",
        title="Embedding Mistake",
        description="Common embedding pitfall",
        context_level=ExtractionLevel.CHUNK,
        context_id="507f1f77bcf86cd799439004",
        chunk_ids=["507f1f77bcf86cd799439004"],
    )
    return ExtractionResult(success=True, extraction=warning)


# =============================================================================
# Test: HierarchicalExtractor Initialization
# =============================================================================


class TestHierarchicalExtractorInit:
    """Tests for HierarchicalExtractor initialization."""

    def test_init_with_default_extraction_types(self):
        """Test initialization uses all registered extraction types."""
        extractor = HierarchicalExtractor()
        # Should have at least the core types
        type_values = [et.value for et in extractor.extraction_types]
        assert "decision" in type_values
        assert "warning" in type_values

    def test_init_with_specific_extraction_types(self):
        """Test initialization with specific extraction types."""
        extractor = HierarchicalExtractor(
            extraction_types=[ExtractionType.DECISION, ExtractionType.WARNING]
        )
        assert len(extractor.extraction_types) == 2
        assert ExtractionType.DECISION in extractor.extraction_types
        assert ExtractionType.WARNING in extractor.extraction_types

    def test_init_with_empty_extraction_types(self):
        """Test initialization with empty extraction types list."""
        extractor = HierarchicalExtractor(extraction_types=[])
        assert extractor.extraction_types == []


# =============================================================================
# Test: LevelExtractionStats
# =============================================================================


class TestLevelExtractionStats:
    """Tests for LevelExtractionStats dataclass."""

    def test_stats_defaults(self):
        """Test default values."""
        stats = LevelExtractionStats(level=ExtractionLevel.CHAPTER)
        assert stats.level == ExtractionLevel.CHAPTER
        assert stats.contexts_processed == 0
        assert stats.extractions_attempted == 0
        assert stats.extractions_successful == 0
        assert stats.extractions_failed == 0
        assert stats.total_tokens_processed == 0

    def test_stats_with_values(self):
        """Test stats with custom values."""
        stats = LevelExtractionStats(
            level=ExtractionLevel.SECTION,
            contexts_processed=5,
            extractions_attempted=10,
            extractions_successful=8,
            extractions_failed=2,
            total_tokens_processed=1000,
        )
        assert stats.contexts_processed == 5
        assert stats.extractions_successful == 8


# =============================================================================
# Test: HierarchicalExtractionResult
# =============================================================================


class TestHierarchicalExtractionResult:
    """Tests for HierarchicalExtractionResult dataclass."""

    def test_result_defaults(self):
        """Test default values."""
        result = HierarchicalExtractionResult(source_id="source-1")
        assert result.source_id == "source-1"
        assert result.results == []
        assert result.stats_by_level == {}
        assert result.total_chunks == 0
        assert result.hierarchy_chapters == 0
        assert result.hierarchy_sections == 0

    def test_total_extractions_property(self):
        """Test total_extractions property calculation."""
        result = HierarchicalExtractionResult(source_id="source-1")
        result.stats_by_level[ExtractionLevel.CHAPTER] = LevelExtractionStats(
            level=ExtractionLevel.CHAPTER,
            extractions_attempted=5,
        )
        result.stats_by_level[ExtractionLevel.SECTION] = LevelExtractionStats(
            level=ExtractionLevel.SECTION,
            extractions_attempted=10,
        )
        assert result.total_extractions == 15

    def test_successful_extractions_property(self):
        """Test successful_extractions property calculation."""
        result = HierarchicalExtractionResult(source_id="source-1")
        result.stats_by_level[ExtractionLevel.CHAPTER] = LevelExtractionStats(
            level=ExtractionLevel.CHAPTER,
            extractions_successful=3,
        )
        result.stats_by_level[ExtractionLevel.CHUNK] = LevelExtractionStats(
            level=ExtractionLevel.CHUNK,
            extractions_successful=7,
        )
        assert result.successful_extractions == 10

    def test_failed_extractions_property(self):
        """Test failed_extractions property calculation."""
        result = HierarchicalExtractionResult(source_id="source-1")
        result.stats_by_level[ExtractionLevel.SECTION] = LevelExtractionStats(
            level=ExtractionLevel.SECTION,
            extractions_failed=2,
        )
        assert result.failed_extractions == 2

    def test_get_successful_results(self, mock_decision_result):
        """Test get_successful_results filters correctly."""
        result = HierarchicalExtractionResult(source_id="source-1")
        failed_result = ExtractionResult(success=False, error="Test error")
        result.results = [mock_decision_result, failed_result]

        successful = result.get_successful_results()
        assert len(successful) == 1
        assert successful[0].success is True


# =============================================================================
# Test: HierarchicalExtractor.extract_document
# =============================================================================


class TestHierarchicalExtractorExtractDocument:
    """Tests for HierarchicalExtractor.extract_document method."""

    @pytest.mark.asyncio
    async def test_extract_document_empty_chunks(self):
        """Test extraction with empty chunk list."""
        extractor = HierarchicalExtractor()
        result = await extractor.extract_document([], "source-1")

        assert result.source_id == "source-1"
        assert result.total_chunks == 0
        assert result.results == []

    @pytest.mark.asyncio
    async def test_extract_document_builds_hierarchy(
        self, sample_chunks_with_hierarchy
    ):
        """Test that extraction builds document hierarchy."""
        extractor = HierarchicalExtractor(extraction_types=[])
        result = await extractor.extract_document(
            sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
        )

        assert result.total_chunks == 4
        assert result.hierarchy_chapters == 2  # Chapter 1 and Chapter 2
        assert result.hierarchy_sections >= 2  # Multiple sections

    @pytest.mark.asyncio
    async def test_extract_document_initializes_all_level_stats(
        self, sample_chunks_with_hierarchy
    ):
        """Test that all extraction levels have initialized stats."""
        extractor = HierarchicalExtractor(extraction_types=[])
        result = await extractor.extract_document(
            sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
        )

        assert ExtractionLevel.CHAPTER in result.stats_by_level
        assert ExtractionLevel.SECTION in result.stats_by_level
        assert ExtractionLevel.CHUNK in result.stats_by_level

    @pytest.mark.asyncio
    async def test_extract_document_routes_to_chapter_level(
        self, sample_chunks_with_hierarchy, mock_methodology_result
    ):
        """Test methodology extraction routes to chapter level."""
        with patch(
            "src.extractors.hierarchical.extractor_registry"
        ) as mock_registry:
            # Create mock extractor
            mock_extractor = AsyncMock()
            mock_extractor.extract = AsyncMock(return_value=[mock_methodology_result])
            mock_registry.list_extraction_types.return_value = [
                ExtractionType.METHODOLOGY
            ]
            mock_registry.get_extractor.return_value = mock_extractor

            extractor = HierarchicalExtractor(
                extraction_types=[ExtractionType.METHODOLOGY]
            )
            result = await extractor.extract_document(
                sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
            )

            # Should have called extract with CHAPTER context level
            calls = mock_extractor.extract.call_args_list
            assert len(calls) > 0
            for call in calls:
                assert call.kwargs.get("context_level") == ExtractionLevel.CHAPTER

    @pytest.mark.asyncio
    async def test_extract_document_routes_to_section_level(
        self, sample_chunks_with_hierarchy, mock_decision_result
    ):
        """Test decision extraction routes to section level."""
        with patch(
            "src.extractors.hierarchical.extractor_registry"
        ) as mock_registry:
            mock_extractor = AsyncMock()
            mock_extractor.extract = AsyncMock(return_value=[mock_decision_result])
            mock_registry.list_extraction_types.return_value = [
                ExtractionType.DECISION
            ]
            mock_registry.get_extractor.return_value = mock_extractor

            extractor = HierarchicalExtractor(
                extraction_types=[ExtractionType.DECISION]
            )
            result = await extractor.extract_document(
                sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
            )

            # Should have called extract with SECTION context level
            calls = mock_extractor.extract.call_args_list
            assert len(calls) > 0
            for call in calls:
                assert call.kwargs.get("context_level") == ExtractionLevel.SECTION

    @pytest.mark.asyncio
    async def test_extract_document_routes_to_chunk_level(
        self, sample_chunks_with_hierarchy, mock_warning_result
    ):
        """Test warning extraction routes to chunk level."""
        with patch(
            "src.extractors.hierarchical.extractor_registry"
        ) as mock_registry:
            mock_extractor = AsyncMock()
            mock_extractor.extract = AsyncMock(return_value=[mock_warning_result])
            mock_registry.list_extraction_types.return_value = [
                ExtractionType.WARNING
            ]
            mock_registry.get_extractor.return_value = mock_extractor

            extractor = HierarchicalExtractor(
                extraction_types=[ExtractionType.WARNING]
            )
            result = await extractor.extract_document(
                sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
            )

            # Should have called extract for each chunk with CHUNK context level
            calls = mock_extractor.extract.call_args_list
            assert len(calls) == 4  # One per chunk
            for call in calls:
                assert call.kwargs.get("context_level") == ExtractionLevel.CHUNK

    @pytest.mark.asyncio
    async def test_extract_document_updates_stats(
        self, sample_chunks_with_hierarchy, mock_warning_result
    ):
        """Test that extraction updates statistics correctly."""
        with patch(
            "src.extractors.hierarchical.extractor_registry"
        ) as mock_registry:
            mock_extractor = AsyncMock()
            mock_extractor.extract = AsyncMock(return_value=[mock_warning_result])
            mock_registry.list_extraction_types.return_value = [
                ExtractionType.WARNING
            ]
            mock_registry.get_extractor.return_value = mock_extractor

            extractor = HierarchicalExtractor(
                extraction_types=[ExtractionType.WARNING]
            )
            result = await extractor.extract_document(
                sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
            )

            # Stats should be updated
            chunk_stats = result.stats_by_level[ExtractionLevel.CHUNK]
            assert chunk_stats.extractions_attempted == 4
            assert chunk_stats.extractions_successful == 4

    @pytest.mark.asyncio
    async def test_extract_document_handles_failed_extractions(
        self, sample_chunks_with_hierarchy
    ):
        """Test handling of failed extractions."""
        failed_result = ExtractionResult(success=False, error="LLM error")

        with patch(
            "src.extractors.hierarchical.extractor_registry"
        ) as mock_registry:
            mock_extractor = AsyncMock()
            mock_extractor.extract = AsyncMock(return_value=[failed_result])
            mock_registry.list_extraction_types.return_value = [
                ExtractionType.WARNING
            ]
            mock_registry.get_extractor.return_value = mock_extractor

            extractor = HierarchicalExtractor(
                extraction_types=[ExtractionType.WARNING]
            )
            result = await extractor.extract_document(
                sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
            )

            # Should track failed extractions
            chunk_stats = result.stats_by_level[ExtractionLevel.CHUNK]
            assert chunk_stats.extractions_failed == 4
            assert chunk_stats.extractions_successful == 0


# =============================================================================
# Test: HierarchicalExtractor._get_extractor
# =============================================================================


class TestHierarchicalExtractorGetExtractor:
    """Tests for the _get_extractor helper method."""

    def test_get_extractor_returns_registered_extractor(self):
        """Test getting a registered extractor."""
        extractor = HierarchicalExtractor()
        decision_extractor = extractor._get_extractor(ExtractionType.DECISION)
        assert decision_extractor is not None

    def test_get_extractor_returns_none_for_unregistered(self):
        """Test getting an unregistered extractor returns None."""
        with patch(
            "src.extractors.hierarchical.extractor_registry"
        ) as mock_registry:
            mock_registry.get_extractor.side_effect = Exception("Not found")

            extractor = HierarchicalExtractor(extraction_types=[])
            result = extractor._get_extractor(ExtractionType.DECISION)
            assert result is None


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestHierarchicalExtractorEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_extract_with_chunks_missing_hierarchy(
        self, sample_chunks_no_hierarchy
    ):
        """Test extraction handles chunks without chapter/section metadata."""
        extractor = HierarchicalExtractor(extraction_types=[])
        result = await extractor.extract_document(
            sample_chunks_no_hierarchy, "507f1f77bcf86cd799439022"
        )

        # Should still process (as uncategorized)
        assert result.total_chunks == 2
        assert result.hierarchy_chapters == 0
        assert result.hierarchy_sections == 0

    @pytest.mark.asyncio
    async def test_extract_with_mixed_hierarchy(self):
        """Test extraction with mix of structured and unstructured chunks."""
        source_id = "507f1f77bcf86cd799439033"
        chunks = [
            make_chunk(
                chunk_id="507f1f77bcf86cd799439021",
                source_id=source_id,
                content="Structured content",
                chapter="Chapter 1",
                section="Section 1",
                page=1,
                token_count=20,
            ),
            make_chunk(
                chunk_id="507f1f77bcf86cd799439022",
                source_id=source_id,
                content="Unstructured content",
                page=2,
                token_count=20,
            ),
        ]

        extractor = HierarchicalExtractor(extraction_types=[])
        result = await extractor.extract_document(chunks, source_id)

        assert result.total_chunks == 2
        assert result.hierarchy_chapters == 1
        assert result.hierarchy_sections == 1

    @pytest.mark.asyncio
    async def test_extract_skips_levels_without_matching_types(
        self, sample_chunks_with_hierarchy
    ):
        """Test extraction skips levels when no matching extraction types."""
        # Only use WARNING which runs at CHUNK level
        with patch(
            "src.extractors.hierarchical.extractor_registry"
        ) as mock_registry:
            mock_extractor = AsyncMock()
            mock_extractor.extract = AsyncMock(return_value=[])
            mock_registry.list_extraction_types.return_value = [
                ExtractionType.WARNING
            ]
            mock_registry.get_extractor.return_value = mock_extractor

            extractor = HierarchicalExtractor(
                extraction_types=[ExtractionType.WARNING]
            )
            result = await extractor.extract_document(
                sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
            )

            # Chapter and Section levels should have 0 extractions
            assert result.stats_by_level[ExtractionLevel.CHAPTER].extractions_attempted == 0
            assert result.stats_by_level[ExtractionLevel.SECTION].extractions_attempted == 0

    @pytest.mark.asyncio
    async def test_extract_handles_extractor_exception(
        self, sample_chunks_with_hierarchy
    ):
        """Test graceful handling when extractor raises exception."""
        with patch(
            "src.extractors.hierarchical.extractor_registry"
        ) as mock_registry:
            mock_extractor = AsyncMock()
            mock_extractor.extract = AsyncMock(side_effect=Exception("LLM failed"))
            mock_registry.list_extraction_types.return_value = [
                ExtractionType.WARNING
            ]
            mock_registry.get_extractor.return_value = mock_extractor

            extractor = HierarchicalExtractor(
                extraction_types=[ExtractionType.WARNING]
            )

            # Should raise since we don't handle exceptions in extract calls
            with pytest.raises(Exception, match="LLM failed"):
                await extractor.extract_document(
                    sample_chunks_with_hierarchy, "507f1f77bcf86cd799439011"
                )
