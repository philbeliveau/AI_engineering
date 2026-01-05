"""Unit tests for ExtractionPipeline."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.exceptions import NotFoundError
from src.extraction.pipeline import (
    ExtractionPipeline,
    ExtractionPipelineError,
    ExtractionPipelineResult,
)
from src.extractors import ExtractionType
from src.models import Chunk, Source


# Test constants - valid MongoDB ObjectId format (24 hex characters)
TEST_SOURCE_ID = "507f1f77bcf86cd799439011"
TEST_CHUNK_ID_1 = "507f1f77bcf86cd799439012"
TEST_CHUNK_ID_2 = "507f1f77bcf86cd799439013"


class TestExtractionPipelineResult:
    """Tests for ExtractionPipelineResult dataclass."""

    def test_total_extractions_empty(self):
        """Test total_extractions when no extractions."""
        result = ExtractionPipelineResult(
            source_id="src-123",
            source_title="Test",
            chunk_count=10,
            extraction_counts={},
            storage_counts={"saved": 0, "failed": 0},
            duration=1.5,
        )
        assert result.total_extractions == 0

    def test_total_extractions_with_counts(self):
        """Test total extraction count calculation."""
        result = ExtractionPipelineResult(
            source_id="src-123",
            source_title="Test",
            chunk_count=10,
            extraction_counts={"decision": 5, "pattern": 3, "warning": 2},
            storage_counts={"saved": 10, "failed": 0},
            duration=1.5,
        )
        assert result.total_extractions == 10

    def test_format_summary_empty(self):
        """Test summary formatting with no extractions."""
        result = ExtractionPipelineResult(
            source_id="src-123",
            source_title="Test",
            chunk_count=10,
            extraction_counts={},
            storage_counts={"saved": 0, "failed": 0},
            duration=1.5,
        )
        summary = result.format_summary()
        assert "TOTAL" in summary
        assert "0" in summary

    def test_format_summary_with_extractions(self):
        """Test summary table formatting."""
        result = ExtractionPipelineResult(
            source_id="src-123",
            source_title="Test",
            chunk_count=10,
            extraction_counts={"decision": 5, "pattern": 3},
            storage_counts={"saved": 8, "failed": 0},
            duration=1.5,
        )
        summary = result.format_summary()
        assert "decision" in summary
        assert "pattern" in summary
        assert "5" in summary
        assert "3" in summary
        assert "TOTAL" in summary


class TestExtractionPipeline:
    """Unit tests for ExtractionPipeline."""

    @pytest.fixture
    def mock_mongodb(self):
        """Create mock MongoDB client."""
        mock = MagicMock()
        mock.get_source.return_value = Source(
            id=TEST_SOURCE_ID,
            title="Test Book",
            type="book",
            path="/path/to/book.pdf",
            status="complete",
            ingested_at=datetime.now(),
        )
        mock.get_chunks_by_source.return_value = [
            Chunk(
                id=TEST_CHUNK_ID_1,
                source_id=TEST_SOURCE_ID,
                content="Test content for extraction",
                token_count=5,
            ),
            Chunk(
                id=TEST_CHUNK_ID_2,
                source_id=TEST_SOURCE_ID,
                content="More test content",
                token_count=4,
            ),
        ]
        return mock

    @pytest.fixture
    def mock_qdrant(self):
        """Create mock Qdrant client."""
        mock = MagicMock()
        mock.ensure_collection.return_value = None
        return mock

    @pytest.fixture
    def mock_embedder(self):
        """Create mock embedder."""
        mock = MagicMock()
        mock.embed_text.return_value = [0.1] * 768
        mock.get_dimension.return_value = 768
        return mock

    @pytest.fixture
    def mock_storage(self):
        """Create mock extraction storage."""
        mock = MagicMock()
        mock.save_extraction.return_value = {
            "extraction_id": "ext-123",
            "mongodb_saved": True,
            "qdrant_saved": True,
        }
        return mock

    def test_pipeline_init(self):
        """Test pipeline initialization."""
        pipeline = ExtractionPipeline()
        assert pipeline._mongodb is None
        assert pipeline._qdrant is None
        assert pipeline._connected is False

    @patch("src.extraction.pipeline.MongoDBClient")
    @patch("src.extraction.pipeline.QdrantStorageClient")
    @patch("src.extraction.pipeline.LocalEmbedder")
    @patch("src.extraction.pipeline.ExtractionStorage")
    def test_connect(
        self,
        mock_storage_cls,
        mock_embedder_cls,
        mock_qdrant_cls,
        mock_mongodb_cls,
    ):
        """Test pipeline connection."""
        pipeline = ExtractionPipeline()
        pipeline._connect()

        assert pipeline._connected is True
        mock_mongodb_cls.assert_called_once()
        mock_qdrant_cls.assert_called_once()
        mock_embedder_cls.assert_called_once()

    @patch("src.extraction.pipeline.MongoDBClient")
    @patch("src.extraction.pipeline.QdrantStorageClient")
    @patch("src.extraction.pipeline.LocalEmbedder")
    @patch("src.extraction.pipeline.ExtractionStorage")
    def test_context_manager(
        self,
        mock_storage_cls,
        mock_embedder_cls,
        mock_qdrant_cls,
        mock_mongodb_cls,
    ):
        """Test context manager pattern."""
        with ExtractionPipeline() as pipeline:
            assert pipeline._connected is True

        mock_mongodb_cls.return_value.close.assert_called_once()

    @patch("src.extraction.pipeline.MongoDBClient")
    @patch("src.extraction.pipeline.QdrantStorageClient")
    @patch("src.extraction.pipeline.LocalEmbedder")
    @patch("src.extraction.pipeline.ExtractionStorage")
    def test_validate_source_exists(
        self,
        mock_storage_cls,
        mock_embedder_cls,
        mock_qdrant_cls,
        mock_mongodb_cls,
        mock_mongodb,
    ):
        """Test source validation when source exists."""
        mock_mongodb_cls.return_value = mock_mongodb

        pipeline = ExtractionPipeline()
        pipeline._connect()
        source = pipeline._validate_source(TEST_SOURCE_ID)

        assert source.title == "Test Book"
        mock_mongodb.get_source.assert_called_once_with(TEST_SOURCE_ID)

    @patch("src.extraction.pipeline.MongoDBClient")
    @patch("src.extraction.pipeline.QdrantStorageClient")
    @patch("src.extraction.pipeline.LocalEmbedder")
    @patch("src.extraction.pipeline.ExtractionStorage")
    def test_validate_source_not_found(
        self,
        mock_storage_cls,
        mock_embedder_cls,
        mock_qdrant_cls,
        mock_mongodb_cls,
    ):
        """Test NotFoundError raised when source missing."""
        mock_mongodb_cls.return_value.get_source.side_effect = NotFoundError(
            "source", "src-missing"
        )

        pipeline = ExtractionPipeline()
        pipeline._connect()

        with pytest.raises(NotFoundError):
            pipeline._validate_source("src-missing")

    @patch("src.extraction.pipeline.MongoDBClient")
    @patch("src.extraction.pipeline.QdrantStorageClient")
    @patch("src.extraction.pipeline.LocalEmbedder")
    @patch("src.extraction.pipeline.ExtractionStorage")
    def test_get_chunks_for_source(
        self,
        mock_storage_cls,
        mock_embedder_cls,
        mock_qdrant_cls,
        mock_mongodb_cls,
        mock_mongodb,
    ):
        """Test chunk retrieval by source ID."""
        mock_mongodb_cls.return_value = mock_mongodb

        pipeline = ExtractionPipeline()
        pipeline._connect()
        chunks = pipeline._get_chunks_for_source(TEST_SOURCE_ID)

        assert len(chunks) == 2
        mock_mongodb.get_chunks_by_source.assert_called_once_with(TEST_SOURCE_ID)

    def test_get_all_extractors(self):
        """Test getting all registered extractors."""
        pipeline = ExtractionPipeline()
        extractors = pipeline._get_extractors(None)

        # Should get all 7 registered extractor types
        assert len(extractors) == 7

    def test_get_filtered_extractors(self):
        """Test getting specific extractor types."""
        pipeline = ExtractionPipeline()
        extractors = pipeline._get_extractors([
            ExtractionType.DECISION,
            ExtractionType.PATTERN,
        ])

        assert len(extractors) == 2
        types = {e.extraction_type for e in extractors}
        assert ExtractionType.DECISION in types
        assert ExtractionType.PATTERN in types

    @patch("src.extraction.pipeline.MongoDBClient")
    @patch("src.extraction.pipeline.QdrantStorageClient")
    @patch("src.extraction.pipeline.LocalEmbedder")
    @patch("src.extraction.pipeline.ExtractionStorage")
    def test_dry_run(
        self,
        mock_storage_cls,
        mock_embedder_cls,
        mock_qdrant_cls,
        mock_mongodb_cls,
        mock_mongodb,
    ):
        """Test dry run validation."""
        mock_mongodb_cls.return_value = mock_mongodb

        with ExtractionPipeline() as pipeline:
            result = pipeline.dry_run(TEST_SOURCE_ID)

        assert result["source_id"] == TEST_SOURCE_ID
        assert result["source_title"] == "Test Book"
        assert result["chunk_count"] == 2
        assert result["extractor_count"] == 7

    @patch("src.extraction.pipeline.MongoDBClient")
    @patch("src.extraction.pipeline.QdrantStorageClient")
    @patch("src.extraction.pipeline.LocalEmbedder")
    @patch("src.extraction.pipeline.ExtractionStorage")
    def test_extract_no_chunks(
        self,
        mock_storage_cls,
        mock_embedder_cls,
        mock_qdrant_cls,
        mock_mongodb_cls,
    ):
        """Test extraction when no chunks exist."""
        mock_mongodb = MagicMock()
        mock_mongodb.get_source.return_value = Source(
            id=TEST_SOURCE_ID,
            title="Empty Book",
            type="book",
            path="/path/to/book.pdf",
            status="complete",
            ingested_at=datetime.now(),
        )
        mock_mongodb.get_chunks_by_source.return_value = []
        mock_mongodb_cls.return_value = mock_mongodb

        with ExtractionPipeline() as pipeline:
            result = pipeline.extract(TEST_SOURCE_ID, quiet=True)

        assert result.chunk_count == 0
        assert result.total_extractions == 0


class TestExtractionPipelineError:
    """Tests for ExtractionPipelineError exception."""

    def test_error_creation(self):
        """Test error creation with message and details."""
        error = ExtractionPipelineError(
            message="Test error",
            details={"key": "value"},
        )

        assert error.code == "EXTRACTION_PIPELINE_ERROR"
        assert error.message == "Test error"
        assert error.details == {"key": "value"}

    def test_error_string(self):
        """Test error string representation."""
        error = ExtractionPipelineError(message="Test error")
        assert "EXTRACTION_PIPELINE_ERROR" in str(error)
        assert "Test error" in str(error)

    def test_error_to_dict(self):
        """Test error to dict conversion."""
        error = ExtractionPipelineError(
            message="Test error",
            details={"key": "value"},
        )
        result = error.to_dict()

        assert result["error"]["code"] == "EXTRACTION_PIPELINE_ERROR"
        assert result["error"]["message"] == "Test error"
        assert result["error"]["details"] == {"key": "value"}
