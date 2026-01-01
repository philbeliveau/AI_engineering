"""Tests for ExtractionStorage service.

Tests cover the orchestration of extraction storage across MongoDB and Qdrant,
including summary generation, embedding, and error handling.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.extractors import (
    Checklist,
    ChecklistItem,
    Decision,
    Methodology,
    MethodologyStep,
    Pattern,
    Persona,
    Warning,
    Workflow,
    WorkflowStep,
)
from src.storage.extraction_storage import ExtractionStorage, ExtractionStorageError


@pytest.fixture
def mock_mongodb_client():
    """Provide a mock MongoDB client."""
    mock = MagicMock()
    mock.save_extraction_from_extractor.return_value = "507f1f77bcf86cd799439013"
    return mock


@pytest.fixture
def mock_qdrant_client():
    """Provide a mock Qdrant client."""
    mock = MagicMock()
    mock.upsert_extraction_vector.return_value = None
    return mock


@pytest.fixture
def mock_embedder():
    """Provide a mock embedder."""
    mock = MagicMock()
    mock.embed_text.return_value = [0.1] * 384
    mock.get_dimension.return_value = 384
    return mock


@pytest.fixture
def extraction_storage(mock_mongodb_client, mock_qdrant_client, mock_embedder):
    """Provide an ExtractionStorage instance with mocked dependencies."""
    return ExtractionStorage(
        mongodb_client=mock_mongodb_client,
        qdrant_client=mock_qdrant_client,
        embedder=mock_embedder,
    )


@pytest.fixture
def sample_decision():
    """Provide a sample Decision extraction for testing."""
    return Decision(
        source_id="507f1f77bcf86cd799439011",
        chunk_id="507f1f77bcf86cd799439012",
        question="Should I use RAG or fine-tuning?",
        options=["RAG", "Fine-tuning", "Both"],
        considerations=["Cost", "Accuracy", "Latency"],
        recommended_approach="RAG for most use cases",
        topics=["rag", "fine-tuning"],
    )


@pytest.fixture
def sample_pattern():
    """Provide a sample Pattern extraction for testing."""
    return Pattern(
        source_id="507f1f77bcf86cd799439011",
        chunk_id="507f1f77bcf86cd799439012",
        name="Semantic Caching",
        problem="High API costs from repeated similar queries",
        solution="Cache responses using embedding similarity matching",
        topics=["caching", "embeddings"],
    )


@pytest.fixture
def sample_warning():
    """Provide a sample Warning extraction for testing."""
    return Warning(
        source_id="507f1f77bcf86cd799439011",
        chunk_id="507f1f77bcf86cd799439012",
        title="Context Window Overflow",
        description="Exceeding token limits causes silent truncation",
        topics=["tokens", "context"],
    )


class TestExtractionStorageSaveExtraction:
    """Test save_extraction method."""

    def test_save_decision_extraction(
        self, extraction_storage, sample_decision, mock_mongodb_client, mock_qdrant_client
    ):
        """Test saving a Decision extraction to both stores."""
        result = extraction_storage.save_extraction(sample_decision)

        # Verify result structure
        assert result["extraction_id"] == "507f1f77bcf86cd799439013"
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

        # Verify MongoDB was called
        mock_mongodb_client.save_extraction_from_extractor.assert_called_once_with(
            sample_decision
        )

        # Verify Qdrant was called with correct payload
        mock_qdrant_client.upsert_extraction_vector.assert_called_once()
        call_args = mock_qdrant_client.upsert_extraction_vector.call_args
        assert call_args.kwargs["extraction_id"] == "507f1f77bcf86cd799439013"
        assert len(call_args.kwargs["vector"]) == 384

        payload = call_args.kwargs["payload"]
        assert payload["source_id"] == sample_decision.source_id
        assert payload["chunk_id"] == sample_decision.chunk_id
        assert payload["extraction_id"] == "507f1f77bcf86cd799439013"
        assert payload["type"] == "decision"
        assert payload["topics"] == ["rag", "fine-tuning"]

    def test_save_pattern_extraction(self, extraction_storage, sample_pattern):
        """Test saving a Pattern extraction."""
        result = extraction_storage.save_extraction(sample_pattern)

        assert result["extraction_id"] == "507f1f77bcf86cd799439013"
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_warning_extraction(self, extraction_storage, sample_warning):
        """Test saving a Warning extraction."""
        result = extraction_storage.save_extraction(sample_warning)

        assert result["extraction_id"] == "507f1f77bcf86cd799439013"
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_summary_generation_called(
        self, extraction_storage, sample_decision, mock_embedder
    ):
        """Test that summary is generated and embedded."""
        extraction_storage.save_extraction(sample_decision)

        # Verify embedder was called with a non-empty summary
        mock_embedder.embed_text.assert_called_once()
        summary_arg = mock_embedder.embed_text.call_args[0][0]
        assert len(summary_arg) > 0
        assert "Should I use RAG or fine-tuning?" in summary_arg


class TestExtractionStorageErrorHandling:
    """Test error handling scenarios."""

    def test_qdrant_failure_returns_partial_success(
        self, extraction_storage, sample_decision, mock_qdrant_client
    ):
        """Test that MongoDB success + Qdrant failure returns partial success."""
        mock_qdrant_client.upsert_extraction_vector.side_effect = Exception("Qdrant down")

        result = extraction_storage.save_extraction(sample_decision)

        assert result["extraction_id"] == "507f1f77bcf86cd799439013"
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is False

    def test_mongodb_failure_raises_error(
        self, extraction_storage, sample_decision, mock_mongodb_client
    ):
        """Test that MongoDB failure raises ExtractionStorageError."""
        mock_mongodb_client.save_extraction_from_extractor.side_effect = Exception(
            "MongoDB down"
        )

        with pytest.raises(ExtractionStorageError) as exc_info:
            extraction_storage.save_extraction(sample_decision)

        assert "mongodb" in str(exc_info.value).lower()

    def test_embedding_failure_raises_error(
        self, extraction_storage, sample_decision, mock_embedder
    ):
        """Test that embedding generation failure raises error."""
        mock_embedder.embed_text.side_effect = Exception("Model not loaded")

        with pytest.raises(ExtractionStorageError) as exc_info:
            extraction_storage.save_extraction(sample_decision)

        assert "embedding" in str(exc_info.value).lower()


class TestExtractionStorageValidation:
    """Test input validation."""

    def test_missing_source_id_raises_error(self, extraction_storage):
        """Test that missing source_id raises validation error."""
        # This should fail at Pydantic level, but test the storage handles it
        decision = Decision(
            source_id="",  # Empty but valid for construction
            chunk_id="507f1f77bcf86cd799439012",
            question="Test question",
        )

        with pytest.raises(ExtractionStorageError) as exc_info:
            extraction_storage.save_extraction(decision)

        assert "source_id" in str(exc_info.value).lower()

    def test_missing_chunk_id_raises_error(self, extraction_storage):
        """Test that missing chunk_id raises validation error."""
        decision = Decision(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="",  # Empty but valid for construction
            question="Test question",
        )

        with pytest.raises(ExtractionStorageError) as exc_info:
            extraction_storage.save_extraction(decision)

        assert "chunk_id" in str(exc_info.value).lower()


class TestExtractionStorageAllTypes:
    """Test saving all extraction types."""

    def test_save_methodology(self, extraction_storage):
        """Test saving Methodology extraction."""
        methodology = Methodology(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439012",
            name="RAG Implementation",
            steps=[
                MethodologyStep(order=1, title="Define requirements", description="..."),
                MethodologyStep(order=2, title="Choose embeddings", description="..."),
            ],
            topics=["rag", "methodology"],
        )

        result = extraction_storage.save_extraction(methodology)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_checklist(self, extraction_storage):
        """Test saving Checklist extraction."""
        checklist = Checklist(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439012",
            name="Pre-deployment Checklist",
            items=[
                ChecklistItem(item="Verify rate limits"),
                ChecklistItem(item="Test with prod data"),
            ],
            topics=["deployment", "checklist"],
        )

        result = extraction_storage.save_extraction(checklist)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_persona(self, extraction_storage):
        """Test saving Persona extraction."""
        persona = Persona(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439012",
            role="ML Engineer",
            responsibilities=["Design ML pipelines", "Optimize models"],
            topics=["roles", "ml"],
        )

        result = extraction_storage.save_extraction(persona)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_workflow(self, extraction_storage):
        """Test saving Workflow extraction."""
        workflow = Workflow(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439012",
            name="Model Deployment",
            trigger="New model version",
            steps=[
                WorkflowStep(order=1, action="Validate metrics"),
                WorkflowStep(order=2, action="Deploy to staging"),
            ],
            topics=["deployment", "workflow"],
        )

        result = extraction_storage.save_extraction(workflow)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True
