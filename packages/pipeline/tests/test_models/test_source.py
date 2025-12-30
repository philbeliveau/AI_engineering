"""Tests for Source model."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models import Source
from src.models.source import CURRENT_SCHEMA_VERSION


class TestSourceModel:
    """Tests for the Source Pydantic model."""

    def test_source_valid_complete(self, valid_object_id: str, sample_datetime: datetime) -> None:
        """Test creating a valid Source with all fields."""
        source = Source(
            id=valid_object_id,
            type="book",
            title="LLM Engineer's Handbook",
            authors=["Paul Iusztin", "Maxime Labonne"],
            path="/data/raw/llm-handbook.pdf",
            ingested_at=sample_datetime,
            status="complete",
            metadata={"pages": 800},
        )

        assert source.id == valid_object_id
        assert source.type == "book"
        assert source.title == "LLM Engineer's Handbook"
        assert source.authors == ["Paul Iusztin", "Maxime Labonne"]
        assert source.path == "/data/raw/llm-handbook.pdf"
        assert source.ingested_at == sample_datetime
        assert source.status == "complete"
        assert source.metadata == {"pages": 800}
        assert source.schema_version == CURRENT_SCHEMA_VERSION

    def test_source_valid_minimal(self, valid_object_id: str, sample_datetime: datetime) -> None:
        """Test creating a valid Source with minimal required fields."""
        source = Source(
            id=valid_object_id,
            type="paper",
            title="Attention Is All You Need",
            path="/data/raw/attention.pdf",
            ingested_at=sample_datetime,
            status="pending",
        )

        assert source.id == valid_object_id
        assert source.type == "paper"
        assert source.authors == []  # Default empty list
        assert source.metadata == {}  # Default empty dict
        assert source.schema_version == CURRENT_SCHEMA_VERSION

    def test_source_all_types(self, valid_object_id: str, sample_datetime: datetime) -> None:
        """Test all valid source types."""
        for source_type in ["book", "paper", "case_study"]:
            source = Source(
                id=valid_object_id,
                type=source_type,
                title="Test",
                path="/test",
                ingested_at=sample_datetime,
                status="pending",
            )
            assert source.type == source_type

    def test_source_all_statuses(self, valid_object_id: str, sample_datetime: datetime) -> None:
        """Test all valid source statuses."""
        for status in ["pending", "processing", "complete", "failed"]:
            source = Source(
                id=valid_object_id,
                type="book",
                title="Test",
                path="/test",
                ingested_at=sample_datetime,
                status=status,
            )
            assert source.status == status

    def test_source_invalid_object_id(self, sample_datetime: datetime) -> None:
        """Test that invalid ObjectId is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Source(
                id="invalid-id",
                type="book",
                title="Test",
                path="/test",
                ingested_at=sample_datetime,
                status="pending",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "id" in str(errors[0]["loc"])
        assert "ObjectId" in errors[0]["msg"]

    def test_source_invalid_object_id_too_short(self, sample_datetime: datetime) -> None:
        """Test that too-short ObjectId is rejected."""
        with pytest.raises(ValidationError):
            Source(
                id="507f1f77bcf86cd7994390",  # 22 chars instead of 24
                type="book",
                title="Test",
                path="/test",
                ingested_at=sample_datetime,
                status="pending",
            )

    def test_source_invalid_object_id_uppercase(self, sample_datetime: datetime) -> None:
        """Test that uppercase hex ObjectId is rejected."""
        with pytest.raises(ValidationError):
            Source(
                id="507F1F77BCF86CD799439011",  # Uppercase
                type="book",
                title="Test",
                path="/test",
                ingested_at=sample_datetime,
                status="pending",
            )

    def test_source_invalid_type(self, valid_object_id: str, sample_datetime: datetime) -> None:
        """Test that invalid source type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Source(
                id=valid_object_id,
                type="article",  # Invalid type
                title="Test",
                path="/test",
                ingested_at=sample_datetime,
                status="pending",
            )

        errors = exc_info.value.errors()
        assert "type" in str(errors[0]["loc"])

    def test_source_invalid_status(self, valid_object_id: str, sample_datetime: datetime) -> None:
        """Test that invalid status is rejected."""
        with pytest.raises(ValidationError):
            Source(
                id=valid_object_id,
                type="book",
                title="Test",
                path="/test",
                ingested_at=sample_datetime,
                status="unknown",  # Invalid status
            )

    def test_source_empty_title(self, valid_object_id: str, sample_datetime: datetime) -> None:
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError):
            Source(
                id=valid_object_id,
                type="book",
                title="",  # Empty title
                path="/test",
                ingested_at=sample_datetime,
                status="pending",
            )

    def test_source_empty_path(self, valid_object_id: str, sample_datetime: datetime) -> None:
        """Test that empty path is rejected."""
        with pytest.raises(ValidationError):
            Source(
                id=valid_object_id,
                type="book",
                title="Test",
                path="",  # Empty path
                ingested_at=sample_datetime,
                status="pending",
            )

    def test_source_json_serialization(
        self, valid_object_id: str, sample_datetime: datetime
    ) -> None:
        """Test JSON serialization produces snake_case output."""
        source = Source(
            id=valid_object_id,
            type="book",
            title="Test Book",
            authors=["Author One"],
            path="/test/path.pdf",
            ingested_at=sample_datetime,
            status="complete",
            metadata={"key": "value"},
        )

        # Test model_dump()
        data = source.model_dump()
        assert "schema_version" in data
        assert "ingested_at" in data
        assert data["schema_version"] == CURRENT_SCHEMA_VERSION

        # Test model_dump_json()
        json_str = source.model_dump_json()
        assert "schema_version" in json_str
        assert "ingested_at" in json_str
        # Ensure snake_case (not camelCase)
        assert "schemaVersion" not in json_str
        assert "ingestedAt" not in json_str

    def test_source_schema_version_default(
        self, valid_object_id: str, sample_datetime: datetime
    ) -> None:
        """Test that schema_version is present with default value."""
        source = Source(
            id=valid_object_id,
            type="book",
            title="Test",
            path="/test",
            ingested_at=sample_datetime,
            status="pending",
        )

        assert source.schema_version == CURRENT_SCHEMA_VERSION
        assert source.schema_version == "1.0"

    def test_source_schema_version_in_serialized_output(
        self, valid_object_id: str, sample_datetime: datetime
    ) -> None:
        """Test that schema_version appears in all serialized output."""
        source = Source(
            id=valid_object_id,
            type="book",
            title="Test",
            path="/test",
            ingested_at=sample_datetime,
            status="pending",
        )

        # In dict output
        data = source.model_dump()
        assert "schema_version" in data

        # In JSON output
        json_str = source.model_dump_json()
        assert "schema_version" in json_str

    def test_source_empty_authors_filtered(
        self, valid_object_id: str, sample_datetime: datetime
    ) -> None:
        """Test that empty and whitespace-only authors are filtered out."""
        source = Source(
            id=valid_object_id,
            type="book",
            title="Test",
            path="/test",
            authors=["", "Valid Author", "   ", "Another Author", "  "],
            ingested_at=sample_datetime,
            status="pending",
        )

        assert source.authors == ["Valid Author", "Another Author"]

    def test_source_authors_whitespace_trimmed(
        self, valid_object_id: str, sample_datetime: datetime
    ) -> None:
        """Test that author names have whitespace trimmed."""
        source = Source(
            id=valid_object_id,
            type="book",
            title="Test",
            path="/test",
            authors=["  Padded Author  ", "Normal Author"],
            ingested_at=sample_datetime,
            status="pending",
        )

        assert source.authors == ["Padded Author", "Normal Author"]

    def test_source_title_max_length(
        self, valid_object_id: str, sample_datetime: datetime
    ) -> None:
        """Test that title exceeding max_length is rejected."""
        with pytest.raises(ValidationError):
            Source(
                id=valid_object_id,
                type="book",
                title="x" * 501,  # Exceeds 500 char limit
                path="/test",
                ingested_at=sample_datetime,
                status="pending",
            )

    def test_source_path_max_length(
        self, valid_object_id: str, sample_datetime: datetime
    ) -> None:
        """Test that path exceeding max_length is rejected."""
        with pytest.raises(ValidationError):
            Source(
                id=valid_object_id,
                type="book",
                title="Test",
                path="/" + "x" * 1001,  # Exceeds 1000 char limit
                ingested_at=sample_datetime,
                status="pending",
            )

    def test_source_future_date_rejected(self, valid_object_id: str) -> None:
        """Test that future ingested_at dates are rejected."""
        from datetime import timedelta

        future_date = datetime.now() + timedelta(days=1)

        with pytest.raises(ValidationError) as exc_info:
            Source(
                id=valid_object_id,
                type="book",
                title="Test",
                path="/test",
                ingested_at=future_date,
                status="pending",
            )

        errors = exc_info.value.errors()
        assert any("future" in str(e["msg"]).lower() for e in errors)
