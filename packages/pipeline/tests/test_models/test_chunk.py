"""Tests for Chunk model."""

import pytest
from pydantic import ValidationError

from src.models import Chunk, ChunkPosition
from src.models.chunk import CURRENT_SCHEMA_VERSION


class TestChunkPositionModel:
    """Tests for the ChunkPosition Pydantic model."""

    def test_position_complete(self) -> None:
        """Test creating a ChunkPosition with all fields."""
        position = ChunkPosition(
            chapter="1",
            section="Introduction",
            page=5,
        )

        assert position.chapter == "1"
        assert position.section == "Introduction"
        assert position.page == 5

    def test_position_partial(self) -> None:
        """Test creating a ChunkPosition with partial fields."""
        position = ChunkPosition(page=10)

        assert position.chapter is None
        assert position.section is None
        assert position.page == 10

    def test_position_empty(self) -> None:
        """Test creating an empty ChunkPosition."""
        position = ChunkPosition()

        assert position.chapter is None
        assert position.section is None
        assert position.page is None

    def test_position_json_serialization(self) -> None:
        """Test JSON serialization of ChunkPosition."""
        position = ChunkPosition(chapter="2", section="Methods", page=15)
        data = position.model_dump()

        assert data["chapter"] == "2"
        assert data["section"] == "Methods"
        assert data["page"] == 15


class TestChunkModel:
    """Tests for the Chunk Pydantic model."""

    def test_chunk_valid_complete(self, valid_object_id: str, valid_object_id_2: str) -> None:
        """Test creating a valid Chunk with all fields."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Large Language Models (LLMs) are neural networks trained on massive text corpora.",
            position=ChunkPosition(chapter="1", section="Introduction", page=5),
            token_count=15,
        )

        assert chunk.id == valid_object_id
        assert chunk.source_id == valid_object_id_2
        assert "Large Language Models" in chunk.content
        assert chunk.position.chapter == "1"
        assert chunk.position.page == 5
        assert chunk.token_count == 15
        assert chunk.schema_version == CURRENT_SCHEMA_VERSION

    def test_chunk_valid_minimal(self, valid_object_id: str, valid_object_id_2: str) -> None:
        """Test creating a valid Chunk with minimal required fields."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Simple text content",
            token_count=3,
        )

        assert chunk.id == valid_object_id
        assert chunk.source_id == valid_object_id_2
        assert chunk.content == "Simple text content"
        assert chunk.position.chapter is None
        assert chunk.position.section is None
        assert chunk.position.page is None
        assert chunk.token_count == 3
        assert chunk.schema_version == CURRENT_SCHEMA_VERSION

    def test_chunk_position_dict(self, valid_object_id: str, valid_object_id_2: str) -> None:
        """Test creating a Chunk with position as dict."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Test content",
            position={"chapter": "3", "section": "Results", "page": 42},
            token_count=2,
        )

        assert chunk.position.chapter == "3"
        assert chunk.position.section == "Results"
        assert chunk.position.page == 42

    def test_chunk_invalid_id(self, valid_object_id_2: str) -> None:
        """Test that invalid chunk id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Chunk(
                id="invalid-id",
                source_id=valid_object_id_2,
                content="Test",
                token_count=1,
            )

        errors = exc_info.value.errors()
        assert any("id" in str(e["loc"]) for e in errors)

    def test_chunk_invalid_source_id(self, valid_object_id: str) -> None:
        """Test that invalid source_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Chunk(
                id=valid_object_id,
                source_id="invalid-source-id",
                content="Test",
                token_count=1,
            )

        errors = exc_info.value.errors()
        assert any("source_id" in str(e["loc"]) for e in errors)

    def test_chunk_empty_content(self, valid_object_id: str, valid_object_id_2: str) -> None:
        """Test that empty content is rejected."""
        with pytest.raises(ValidationError):
            Chunk(
                id=valid_object_id,
                source_id=valid_object_id_2,
                content="",
                token_count=0,
            )

    def test_chunk_negative_token_count(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that negative token_count is rejected."""
        with pytest.raises(ValidationError):
            Chunk(
                id=valid_object_id,
                source_id=valid_object_id_2,
                content="Test",
                token_count=-1,
            )

    def test_chunk_token_count_exceeds_content_length(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that token_count cannot exceed content length."""
        with pytest.raises(ValidationError) as exc_info:
            Chunk(
                id=valid_object_id,
                source_id=valid_object_id_2,
                content="Hi",  # 2 characters
                token_count=100,  # Way more than content length
            )

        errors = exc_info.value.errors()
        assert any("token_count" in str(e["msg"]) for e in errors)

    def test_chunk_json_serialization(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test JSON serialization produces snake_case output."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Test content for serialization",
            position=ChunkPosition(chapter="1", page=1),
            token_count=5,
        )

        # Test model_dump()
        data = chunk.model_dump()
        assert "schema_version" in data
        assert "source_id" in data
        assert "token_count" in data
        assert data["schema_version"] == CURRENT_SCHEMA_VERSION

        # Test model_dump_json()
        json_str = chunk.model_dump_json()
        assert "schema_version" in json_str
        assert "source_id" in json_str
        assert "token_count" in json_str
        # Ensure snake_case (not camelCase)
        assert "schemaVersion" not in json_str
        assert "sourceId" not in json_str
        assert "tokenCount" not in json_str

    def test_chunk_schema_version_default(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that schema_version is present with default value."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Test",
            token_count=1,
        )

        assert chunk.schema_version == CURRENT_SCHEMA_VERSION
        assert chunk.schema_version == "1.1"

    def test_chunk_schema_version_in_serialized_output(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that schema_version appears in all serialized output."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Test",
            token_count=1,
        )

        # In dict output
        data = chunk.model_dump()
        assert "schema_version" in data

        # In JSON output
        json_str = chunk.model_dump_json()
        assert "schema_version" in json_str

    def test_chunk_content_max_length(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that content exceeding max_length is rejected."""
        with pytest.raises(ValidationError):
            Chunk(
                id=valid_object_id,
                source_id=valid_object_id_2,
                content="x" * 50001,  # Exceeds 50000 char limit
                token_count=1,
            )


class TestChunkPositionValidation:
    """Tests for ChunkPosition validation rules."""

    def test_position_negative_page_rejected(self) -> None:
        """Test that negative page numbers are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkPosition(page=-1)

        errors = exc_info.value.errors()
        assert any("page" in str(e["loc"]) for e in errors)

    def test_position_zero_page_rejected(self) -> None:
        """Test that zero page number is rejected (pages start at 1)."""
        with pytest.raises(ValidationError):
            ChunkPosition(page=0)

    def test_position_valid_page(self) -> None:
        """Test that valid positive page numbers are accepted."""
        pos = ChunkPosition(page=1)
        assert pos.page == 1

        pos = ChunkPosition(page=999)
        assert pos.page == 999


class TestChunkV11Fields:
    """Tests for Chunk v1.1 schema fields (project_id)."""

    def test_chunk_project_id_default(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that project_id defaults to 'default'."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Test content",
            token_count=2,
        )

        assert chunk.project_id == "default"

    def test_chunk_project_id_custom(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that project_id can be set to custom value."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Test content",
            token_count=2,
            project_id="ai_engineering",
        )

        assert chunk.project_id == "ai_engineering"

    def test_chunk_schema_version_v11(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that schema_version is '1.1'."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Test",
            token_count=1,
        )

        assert chunk.schema_version == "1.1"

    def test_chunk_v11_fields_in_serialization(
        self, valid_object_id: str, valid_object_id_2: str
    ) -> None:
        """Test that v1.1 fields appear in serialized output."""
        chunk = Chunk(
            id=valid_object_id,
            source_id=valid_object_id_2,
            content="Test",
            token_count=1,
            project_id="my_project",
        )

        data = chunk.model_dump()
        assert "project_id" in data
        assert data["project_id"] == "my_project"
