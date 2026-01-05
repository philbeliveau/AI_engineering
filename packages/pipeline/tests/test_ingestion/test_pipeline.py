"""Unit and integration tests for the ingestion pipeline.

Tests cover:
- Pipeline initialization and configuration
- End-to-end ingestion with sample files
- Error handling for various failure scenarios
- Status tracking through pipeline stages
- Dry run mode
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.ingestion.pipeline import (
    IngestionPipeline,
    IngestionResult,
    IngestionStatus,
    PipelineConfig,
    IngestionError,
    AdapterSelectionError,
    ChunkingError,
    EmbeddingError,
    StorageOrchestrationError,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_markdown(tmp_path: Path) -> Path:
    """Create a sample Markdown file for testing."""
    md_file = tmp_path / "test_document.md"
    md_file.write_text(
        """# Test Document

This is a test document with multiple paragraphs for testing the ingestion pipeline.

## Section 1: Introduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

## Section 2: Details

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident,
sunt in culpa qui officia deserunt mollit anim id est laborum.

### Subsection 2.1: More Details

Additional content for the subsection with more text to ensure we have
enough content for chunking tests.

## Section 3: Conclusion

Final thoughts and conclusions about the test document content.
"""
    )
    return md_file


@pytest.fixture
def unsupported_file(tmp_path: Path) -> Path:
    """Create an unsupported file type for testing."""
    xyz_file = tmp_path / "test.xyz"
    xyz_file.write_text("Unsupported content")
    return xyz_file


@pytest.fixture
def empty_markdown(tmp_path: Path) -> Path:
    """Create an empty Markdown file for testing."""
    md_file = tmp_path / "empty.md"
    md_file.write_text("")
    return md_file


@pytest.fixture
def mock_mongodb():
    """Create a mock MongoDB client."""
    with patch("src.ingestion.pipeline.MongoDBClient") as mock:
        client = MagicMock()
        client.create_source.return_value = "507f1f77bcf86cd799439011"
        client.update_source.return_value = MagicMock()
        client.create_chunks_bulk.return_value = [
            "507f1f77bcf86cd799439012",
            "507f1f77bcf86cd799439013",
        ]
        mock.return_value = client
        yield client


@pytest.fixture
def mock_qdrant():
    """Create a mock Qdrant client."""
    with patch("src.ingestion.pipeline.QdrantStorageClient") as mock:
        client = MagicMock()
        client.ensure_collection.return_value = None
        client.upsert_vectors_batch.return_value = 2
        mock.return_value = client
        yield client


@pytest.fixture
def mock_embedder():
    """Create a mock embedder."""
    with patch("src.ingestion.pipeline.get_embedder") as mock:
        embedder = MagicMock()
        # Return 768-dimensional embeddings
        embedder.embed_batch.return_value = [
            [0.1] * 768,
            [0.2] * 768,
        ]
        mock.return_value = embedder
        yield embedder


# ============================================================================
# Pipeline Configuration Tests
# ============================================================================


class TestPipelineConfig:
    """Tests for PipelineConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PipelineConfig()
        assert config.chunk_size == 512
        assert config.dry_run is False
        assert config.verbose is False

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PipelineConfig(chunk_size=256, dry_run=True, verbose=True)
        assert config.chunk_size == 256
        assert config.dry_run is True
        assert config.verbose is True

    def test_chunk_size_validation_min(self):
        """Test chunk size minimum validation."""
        with pytest.raises(ValueError):
            PipelineConfig(chunk_size=10)  # Below minimum of 50

    def test_chunk_size_validation_max(self):
        """Test chunk size maximum validation."""
        with pytest.raises(ValueError):
            PipelineConfig(chunk_size=5000)  # Above maximum of 2048


# ============================================================================
# Pipeline Initialization Tests
# ============================================================================


class TestPipelineInitialization:
    """Tests for pipeline initialization."""

    def test_pipeline_init_default_config(self):
        """Test pipeline initialization with default config."""
        pipeline = IngestionPipeline()
        assert pipeline.config.chunk_size == 512
        assert pipeline.config.dry_run is False

    def test_pipeline_init_custom_config(self):
        """Test pipeline initialization with custom config."""
        config = PipelineConfig(chunk_size=256, dry_run=True)
        pipeline = IngestionPipeline(config)
        assert pipeline.config.chunk_size == 256
        assert pipeline.config.dry_run is True

    def test_pipeline_context_manager(self, mock_mongodb, mock_qdrant):
        """Test pipeline as context manager."""
        config = PipelineConfig(dry_run=True)
        with IngestionPipeline(config) as pipeline:
            assert pipeline is not None
        # Should close cleanly


# ============================================================================
# Dry Run Tests
# ============================================================================


class TestDryRun:
    """Tests for dry run mode."""

    def test_dry_run_no_database_calls(self, sample_markdown, mock_embedder):
        """Test that dry run mode doesn't make database calls."""
        config = PipelineConfig(dry_run=True)

        with patch("src.ingestion.pipeline.MongoDBClient") as mongo_mock:
            with patch("src.ingestion.pipeline.QdrantStorageClient") as qdrant_mock:
                pipeline = IngestionPipeline(config)
                result = pipeline.ingest(sample_markdown)

                # Verify no database calls were made
                mongo_mock.return_value.create_source.assert_not_called()
                mongo_mock.return_value.create_chunks_bulk.assert_not_called()
                qdrant_mock.return_value.upsert_vectors_batch.assert_not_called()

                # Result should still have data
                assert result.source_id == "dry-run"
                assert result.chunk_count > 0
                assert result.total_tokens > 0

    def test_dry_run_result_structure(self, sample_markdown, mock_embedder):
        """Test dry run result has complete structure."""
        config = PipelineConfig(dry_run=True)
        pipeline = IngestionPipeline(config)
        result = pipeline.ingest(sample_markdown)

        assert isinstance(result, IngestionResult)
        assert result.source_id == "dry-run"
        assert result.title is not None
        assert result.file_type == ".md"
        assert result.chunk_count > 0
        assert result.total_tokens > 0
        assert result.processing_time >= 0
        assert result.embedding_time >= 0
        assert result.storage_time == 0  # No storage in dry run
        assert result.duration > 0


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_file_not_found(self):
        """Test error when file doesn't exist."""
        pipeline = IngestionPipeline()
        nonexistent = Path("/nonexistent/file.pdf")

        with pytest.raises(IngestionError) as exc_info:
            pipeline.ingest(nonexistent)

        assert exc_info.value.code == "FILE_NOT_FOUND"
        assert str(nonexistent) in exc_info.value.message

    def test_unsupported_file_type(self, unsupported_file):
        """Test error for unsupported file type."""
        config = PipelineConfig(dry_run=True)
        pipeline = IngestionPipeline(config)

        with pytest.raises(AdapterSelectionError) as exc_info:
            pipeline.ingest(unsupported_file)

        assert exc_info.value.code == "ADAPTER_SELECTION_ERROR"

    def test_adapter_error_marks_source_failed(
        self, sample_markdown, mock_mongodb, mock_qdrant, mock_embedder
    ):
        """Test that adapter errors mark source as failed."""
        # Make extract_text succeed but chunking fail so source is created first
        with patch("src.ingestion.pipeline.adapter_registry") as mock_registry:
            adapter = MagicMock()
            # extract_text returns a mock result
            adapter.extract_text.return_value = MagicMock(
                text="test content",
                metadata={},  # No _docling_document, will cause chunking error
            )
            adapter.get_metadata.return_value = {"title": "Test"}
            mock_registry.get_adapter.return_value = adapter

            pipeline = IngestionPipeline()
            # Inject mock clients
            pipeline._mongodb = mock_mongodb
            pipeline._qdrant = mock_qdrant

            with pytest.raises(ChunkingError):
                pipeline.ingest(sample_markdown)

            # Source should be marked as failed via update_source
            mock_mongodb.update_source.assert_called()


# ============================================================================
# Status Tracking Tests
# ============================================================================


class TestStatusTracking:
    """Tests for ingestion status tracking."""

    def test_status_enum_values(self):
        """Test IngestionStatus enum values."""
        assert IngestionStatus.PENDING.value == "pending"
        assert IngestionStatus.PROCESSING.value == "processing"
        assert IngestionStatus.COMPLETE.value == "complete"
        assert IngestionStatus.FAILED.value == "failed"

    def test_status_transitions(
        self, sample_markdown, mock_mongodb, mock_qdrant, mock_embedder
    ):
        """Test status transitions during ingestion."""
        pipeline = IngestionPipeline()
        pipeline._mongodb = mock_mongodb
        pipeline._qdrant = mock_qdrant

        # Track update calls
        update_calls = []
        mock_mongodb.update_source.side_effect = lambda sid, updates: update_calls.append(
            updates
        )

        pipeline.ingest(sample_markdown)

        # Should have status updates: pending->processing, then final complete
        status_updates = [
            call.get("status")
            for call in update_calls
            if call.get("status") is not None
        ]

        assert IngestionStatus.PROCESSING.value in status_updates
        assert IngestionStatus.COMPLETE.value in status_updates


# ============================================================================
# Result Model Tests
# ============================================================================


class TestIngestionResult:
    """Tests for IngestionResult dataclass."""

    def test_result_fields(self):
        """Test IngestionResult has all required fields."""
        result = IngestionResult(
            source_id="507f1f77bcf86cd799439011",
            title="Test Document",
            file_type=".pdf",
            chunk_count=10,
            total_tokens=5000,
            processing_time=1.5,
            embedding_time=2.0,
            storage_time=0.5,
            duration=4.0,
        )

        assert result.source_id == "507f1f77bcf86cd799439011"
        assert result.title == "Test Document"
        assert result.file_type == ".pdf"
        assert result.chunk_count == 10
        assert result.total_tokens == 5000
        assert result.processing_time == 1.5
        assert result.embedding_time == 2.0
        assert result.storage_time == 0.5
        assert result.duration == 4.0


# ============================================================================
# Exception Tests
# ============================================================================


class TestExceptions:
    """Tests for custom exceptions."""

    def test_ingestion_error_base(self):
        """Test IngestionError base class."""
        error = IngestionError(
            code="TEST_ERROR",
            message="Test error message",
            details={"key": "value"},
        )
        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details == {"key": "value"}

    def test_adapter_selection_error(self):
        """Test AdapterSelectionError."""
        error = AdapterSelectionError(
            file_path=Path("/test/file.xyz"),
            reason="Unsupported file type",
        )
        assert error.code == "ADAPTER_SELECTION_ERROR"
        assert "file.xyz" in error.message
        assert error.details["file_path"] == "/test/file.xyz"

    def test_chunking_error(self):
        """Test ChunkingError."""
        error = ChunkingError(
            source_id="507f1f77bcf86cd799439011",
            reason="Empty content",
        )
        assert error.code == "CHUNKING_ERROR"
        assert error.details["source_id"] == "507f1f77bcf86cd799439011"

    def test_embedding_error(self):
        """Test EmbeddingError."""
        error = EmbeddingError(
            source_id="507f1f77bcf86cd799439011",
            reason="Model failed",
            chunk_count=10,
        )
        assert error.code == "EMBEDDING_ERROR"
        assert error.details["chunk_count"] == 10

    def test_storage_orchestration_error(self):
        """Test StorageOrchestrationError."""
        error = StorageOrchestrationError(
            source_id="507f1f77bcf86cd799439011",
            stage="mongodb",
            reason="Connection failed",
        )
        assert error.code == "STORAGE_ORCHESTRATION_ERROR"
        assert error.details["stage"] == "mongodb"


# ============================================================================
# Integration Tests (require Docker services)
# ============================================================================


@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring MongoDB and Qdrant.

    These tests require Docker services to be running:
        docker-compose up -d
    """

    @pytest.fixture
    def pipeline(self):
        """Create pipeline for integration tests."""
        pipeline = IngestionPipeline()
        yield pipeline
        pipeline.close()

    @pytest.mark.skip(reason="Requires Docker services")
    def test_end_to_end_markdown(self, pipeline, sample_markdown):
        """Test complete pipeline with Markdown input."""
        result = pipeline.ingest(sample_markdown)

        assert result.source_id is not None
        assert len(result.source_id) == 24  # MongoDB ObjectId
        assert result.chunk_count > 0
        assert result.total_tokens > 0
        assert result.duration > 0

    @pytest.mark.skip(reason="Requires Docker services")
    def test_storage_verification(self, pipeline, sample_markdown):
        """Test that data is actually stored in databases."""
        result = pipeline.ingest(sample_markdown)

        # Verify MongoDB storage
        source = pipeline.mongodb.get_source(result.source_id)
        assert source.status == IngestionStatus.COMPLETE.value
        assert source.title is not None

        chunks = pipeline.mongodb.get_chunks_by_source(result.source_id)
        assert len(chunks) == result.chunk_count
        assert all(chunk.source_id == result.source_id for chunk in chunks)

    @pytest.mark.skip(reason="Requires Docker services")
    def test_status_tracking_integration(self, pipeline, sample_markdown):
        """Test status tracking in actual database."""
        result = pipeline.ingest(sample_markdown)

        # Verify final status
        source = pipeline.mongodb.get_source(result.source_id)
        assert source.status == IngestionStatus.COMPLETE.value
