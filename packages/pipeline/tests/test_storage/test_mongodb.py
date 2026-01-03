"""Tests for MongoDB storage client."""

from datetime import datetime

import pytest

from src.config import settings
from src.exceptions import NotFoundError, StorageError
from src.models import Chunk, ChunkPosition, Extraction, Source
from src.storage import MongoDBClient


class TestMongoDBClientConnection:
    """Tests for MongoDB client connection management."""

    def test_connect_and_ping(self, mongodb_client: MongoDBClient):
        """Test that client can connect and ping MongoDB."""
        assert mongodb_client.ping() is True

    def test_context_manager(self):
        """Test that client works as context manager."""
        with MongoDBClient(database="knowledge_db_test") as client:
            assert client.ping() is True
        # After exiting context, client should be closed
        assert client._client is None

    def test_ping_without_connection(self):
        """Test that ping returns False when not connected."""
        client = MongoDBClient()
        assert client.ping() is False

    def test_close_without_connection(self):
        """Test that close works without prior connection."""
        client = MongoDBClient()
        # Should not raise
        client.close()


class TestMongoDBClientSourcesCRUD:
    """Tests for Source CRUD operations."""

    def test_create_source(self, mongodb_client: MongoDBClient, sample_source: Source):
        """Test creating a source document."""
        source_id = mongodb_client.create_source(sample_source)
        assert source_id is not None
        assert len(source_id) == 24  # Valid ObjectId length

    def test_get_source(self, mongodb_client: MongoDBClient, sample_source: Source):
        """Test retrieving a source by ID."""
        source_id = mongodb_client.create_source(sample_source)
        retrieved = mongodb_client.get_source(source_id)

        assert retrieved.title == sample_source.title
        assert retrieved.type == sample_source.type
        assert retrieved.authors == sample_source.authors
        assert retrieved.status == sample_source.status

    def test_get_source_not_found(self, mongodb_client: MongoDBClient):
        """Test that getting non-existent source raises NotFoundError."""
        with pytest.raises(NotFoundError) as exc_info:
            mongodb_client.get_source("507f1f77bcf86cd799439099")
        assert exc_info.value.code == "NOT_FOUND"
        assert "source" in exc_info.value.message

    def test_update_source(self, mongodb_client: MongoDBClient, sample_source: Source):
        """Test updating a source document."""
        source_id = mongodb_client.create_source(sample_source)
        updated = mongodb_client.update_source(source_id, {"status": "complete"})

        assert updated.status == "complete"
        assert updated.title == sample_source.title

    def test_update_source_not_found(self, mongodb_client: MongoDBClient):
        """Test that updating non-existent source raises NotFoundError."""
        with pytest.raises(NotFoundError):
            mongodb_client.update_source("507f1f77bcf86cd799439099", {"status": "complete"})

    def test_delete_source(self, mongodb_client: MongoDBClient, sample_source: Source):
        """Test deleting a source document."""
        source_id = mongodb_client.create_source(sample_source)
        result = mongodb_client.delete_source(source_id)
        assert result is True

        # Verify it's gone
        with pytest.raises(NotFoundError):
            mongodb_client.get_source(source_id)

    def test_delete_source_not_found(self, mongodb_client: MongoDBClient):
        """Test that deleting non-existent source returns False."""
        result = mongodb_client.delete_source("507f1f77bcf86cd799439099")
        assert result is False

    def test_list_sources_empty(self, mongodb_client: MongoDBClient):
        """Test listing sources when none exist."""
        sources = mongodb_client.list_sources()
        assert sources == []

    def test_list_sources(self, mongodb_client: MongoDBClient, sample_source: Source):
        """Test listing all sources."""
        mongodb_client.create_source(sample_source)
        sources = mongodb_client.list_sources()
        assert len(sources) == 1
        assert sources[0].title == sample_source.title

    def test_list_sources_with_status_filter(
        self, mongodb_client: MongoDBClient, sample_source: Source
    ):
        """Test listing sources with status filter."""
        mongodb_client.create_source(sample_source)

        # Create another source with different status
        other_source = Source(
            id="507f1f77bcf86cd799439022",
            type="paper",
            title="Other Source",
            authors=["Other Author"],
            path="/data/raw/other.pdf",
            ingested_at=datetime.now(),
            status="complete",
            schema_version="1.0",
        )
        mongodb_client.create_source(other_source)

        # Filter by pending status
        pending_sources = mongodb_client.list_sources(status="pending")
        assert len(pending_sources) == 1
        assert pending_sources[0].status == "pending"

        # Filter by complete status
        complete_sources = mongodb_client.list_sources(status="complete")
        assert len(complete_sources) == 1
        assert complete_sources[0].status == "complete"


class TestMongoDBClientChunksCRUD:
    """Tests for Chunk CRUD operations."""

    def test_create_chunk(self, mongodb_client: MongoDBClient, sample_chunk: Chunk):
        """Test creating a chunk document."""
        chunk_id = mongodb_client.create_chunk(sample_chunk)
        assert chunk_id is not None
        assert len(chunk_id) == 24

    def test_get_chunk(self, mongodb_client: MongoDBClient, sample_chunk: Chunk):
        """Test retrieving a chunk by ID."""
        chunk_id = mongodb_client.create_chunk(sample_chunk)
        retrieved = mongodb_client.get_chunk(chunk_id)

        assert retrieved.content == sample_chunk.content
        assert retrieved.source_id == sample_chunk.source_id
        assert retrieved.token_count == sample_chunk.token_count

    def test_get_chunk_not_found(self, mongodb_client: MongoDBClient):
        """Test that getting non-existent chunk raises NotFoundError."""
        with pytest.raises(NotFoundError) as exc_info:
            mongodb_client.get_chunk("507f1f77bcf86cd799439099")
        assert exc_info.value.code == "NOT_FOUND"

    def test_get_chunks_by_source(self, mongodb_client: MongoDBClient, sample_chunk: Chunk):
        """Test getting all chunks for a source."""
        chunk_id = mongodb_client.create_chunk(sample_chunk)
        chunks = mongodb_client.get_chunks_by_source(sample_chunk.source_id)

        assert len(chunks) == 1
        assert chunks[0].id == chunk_id

    def test_get_chunks_by_source_empty(self, mongodb_client: MongoDBClient):
        """Test getting chunks for source with no chunks."""
        chunks = mongodb_client.get_chunks_by_source("507f1f77bcf86cd799439099")
        assert chunks == []

    def test_delete_chunks_by_source(self, mongodb_client: MongoDBClient, sample_chunk: Chunk):
        """Test deleting all chunks for a source."""
        mongodb_client.create_chunk(sample_chunk)
        deleted_count = mongodb_client.delete_chunks_by_source(sample_chunk.source_id)

        assert deleted_count == 1
        # Verify they're gone
        chunks = mongodb_client.get_chunks_by_source(sample_chunk.source_id)
        assert len(chunks) == 0

    def test_count_chunks_by_source(self, mongodb_client: MongoDBClient, sample_chunk: Chunk):
        """Test counting chunks for a source."""
        mongodb_client.create_chunk(sample_chunk)
        count = mongodb_client.count_chunks_by_source(sample_chunk.source_id)
        assert count == 1


class TestMongoDBClientExtractionsCRUD:
    """Tests for Extraction CRUD operations."""

    def test_create_extraction(
        self, mongodb_client: MongoDBClient, sample_extraction: Extraction
    ):
        """Test creating an extraction document."""
        extraction_id = mongodb_client.create_extraction(sample_extraction)
        assert extraction_id is not None
        assert len(extraction_id) == 24

    def test_get_extraction(
        self, mongodb_client: MongoDBClient, sample_extraction: Extraction
    ):
        """Test retrieving an extraction by ID."""
        extraction_id = mongodb_client.create_extraction(sample_extraction)
        retrieved = mongodb_client.get_extraction(extraction_id)

        assert retrieved.type == sample_extraction.type
        assert retrieved.source_id == sample_extraction.source_id
        assert retrieved.topics == sample_extraction.topics

    def test_get_extraction_not_found(self, mongodb_client: MongoDBClient):
        """Test that getting non-existent extraction raises NotFoundError."""
        with pytest.raises(NotFoundError) as exc_info:
            mongodb_client.get_extraction("507f1f77bcf86cd799439099")
        assert exc_info.value.code == "NOT_FOUND"

    def test_get_extractions_by_source(
        self, mongodb_client: MongoDBClient, sample_extraction: Extraction
    ):
        """Test getting all extractions for a source."""
        extraction_id = mongodb_client.create_extraction(sample_extraction)
        extractions = mongodb_client.get_extractions_by_source(sample_extraction.source_id)

        assert len(extractions) == 1
        assert extractions[0].id == extraction_id

    def test_get_extractions_by_type(
        self, mongodb_client: MongoDBClient, sample_extraction: Extraction
    ):
        """Test getting extractions by type."""
        mongodb_client.create_extraction(sample_extraction)
        extractions = mongodb_client.get_extractions_by_type("decision")

        assert len(extractions) == 1
        assert extractions[0].type == "decision"

    def test_get_extractions_by_type_with_topics(
        self, mongodb_client: MongoDBClient, sample_extraction: Extraction
    ):
        """Test getting extractions by type with topic filter."""
        mongodb_client.create_extraction(sample_extraction)

        # Should find with matching topic
        extractions = mongodb_client.get_extractions_by_type(
            "decision", topics=["architecture"]
        )
        assert len(extractions) == 1

        # Should not find with non-matching topic
        extractions = mongodb_client.get_extractions_by_type(
            "decision", topics=["security"]
        )
        assert len(extractions) == 0

    def test_delete_extractions_by_source(
        self, mongodb_client: MongoDBClient, sample_extraction: Extraction
    ):
        """Test deleting all extractions for a source."""
        mongodb_client.create_extraction(sample_extraction)
        deleted_count = mongodb_client.delete_extractions_by_source(
            sample_extraction.source_id
        )

        assert deleted_count == 1
        # Verify they're gone
        extractions = mongodb_client.get_extractions_by_source(sample_extraction.source_id)
        assert len(extractions) == 0


class TestMongoDBClientBulkOperations:
    """Tests for bulk insert operations."""

    def test_create_chunks_bulk(self, mongodb_client: MongoDBClient, sample_chunk: Chunk):
        """Test bulk inserting chunks."""
        # Create multiple chunks
        chunks = []
        for i in range(3):
            chunk = Chunk(
                id=f"507f1f77bcf86cd79943901{i}",
                source_id=sample_chunk.source_id,
                content=f"Test content {i} with enough characters to be valid.",
                position=ChunkPosition(page=i + 1),
                token_count=10,
                schema_version="1.0",
            )
            chunks.append(chunk)

        chunk_ids = mongodb_client.create_chunks_bulk(chunks)

        assert len(chunk_ids) == 3
        assert all(len(cid) == 24 for cid in chunk_ids)

        # Verify they were all inserted
        count = mongodb_client.count_chunks_by_source(sample_chunk.source_id)
        assert count == 3

    def test_create_chunks_bulk_empty(self, mongodb_client: MongoDBClient):
        """Test bulk inserting empty list returns empty list."""
        chunk_ids = mongodb_client.create_chunks_bulk([])
        assert chunk_ids == []

    def test_create_extractions_bulk(
        self, mongodb_client: MongoDBClient, sample_extraction: Extraction
    ):
        """Test bulk inserting extractions."""
        # Create multiple extractions
        extractions = []
        for i in range(3):
            extraction = Extraction(
                id=f"507f1f77bcf86cd79943902{i}",
                source_id=sample_extraction.source_id,
                chunk_id=sample_extraction.chunk_id,
                type="pattern",
                content={
                    "name": f"Pattern {i}",
                    "problem": f"Problem {i}",
                    "solution": f"Solution {i}",
                },
                topics=[f"topic{i}"],
                schema_version="1.0",
                extracted_at=datetime.now(),
            )
            extractions.append(extraction)

        extraction_ids = mongodb_client.create_extractions_bulk(extractions)

        assert len(extraction_ids) == 3
        assert all(len(eid) == 24 for eid in extraction_ids)

        # Verify they were all inserted
        results = mongodb_client.get_extractions_by_type("pattern")
        assert len(results) == 3

    def test_create_extractions_bulk_empty(self, mongodb_client: MongoDBClient):
        """Test bulk inserting empty list returns empty list."""
        extraction_ids = mongodb_client.create_extractions_bulk([])
        assert extraction_ids == []


class TestMongoDBClientIndexes:
    """Tests for index creation."""

    def test_indexes_created(self, mongodb_client: MongoDBClient):
        """Test that required indexes are created on connect."""
        # Check indexes exist on collections
        source_indexes = list(mongodb_client._db[settings.sources_collection].list_indexes())
        chunk_indexes = list(mongodb_client._db[settings.chunks_collection].list_indexes())
        extraction_indexes = list(mongodb_client._db[settings.extractions_collection].list_indexes())

        # Check for expected index names
        source_index_names = [idx["name"] for idx in source_indexes]
        assert "idx_sources_status" in source_index_names

        chunk_index_names = [idx["name"] for idx in chunk_indexes]
        assert "idx_chunks_source_id" in chunk_index_names

        extraction_index_names = [idx["name"] for idx in extraction_indexes]
        assert "idx_extractions_type_topics" in extraction_index_names
        assert "idx_extractions_source_id" in extraction_index_names


class TestMongoDBClientErrorHandling:
    """Tests for error handling."""

    def test_storage_error_not_connected(self):
        """Test that operations fail properly when not connected."""
        client = MongoDBClient()
        sample_source = Source(
            id="507f1f77bcf86cd799439011",
            type="book",
            title="Test",
            authors=[],
            path="/test",
            ingested_at=datetime.now(),
            status="pending",
            schema_version="1.0",
        )

        with pytest.raises(StorageError) as exc_info:
            client.create_source(sample_source)
        assert exc_info.value.code == "STORAGE_ERROR"
        assert "Not connected" in str(exc_info.value.details)

    def test_connection_failure_bad_uri(self):
        """Test that connection to invalid URI fails gracefully."""
        # Use localhost with unlikely port and short timeout to avoid long waits
        client = MongoDBClient(uri="mongodb://localhost:59999/?serverSelectionTimeoutMS=100")
        with pytest.raises(StorageError) as exc_info:
            client.connect()
        assert exc_info.value.code == "STORAGE_ERROR"
        # Error occurs during index creation which triggers actual connection
        assert "Connection refused" in str(exc_info.value.details.get("error", ""))


class TestMongoDBClientValidation:
    """Tests for input validation."""

    def test_get_source_invalid_objectid(self, mongodb_client: MongoDBClient):
        """Test that invalid ObjectId raises ValidationError."""
        from src.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            mongodb_client.get_source("invalid-id")
        assert exc_info.value.code == "VALIDATION_ERROR"
        assert "Invalid source ID format" in exc_info.value.message

    def test_get_chunk_invalid_objectid(self, mongodb_client: MongoDBClient):
        """Test that invalid chunk ObjectId raises ValidationError."""
        from src.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            mongodb_client.get_chunk("not-an-objectid")
        assert exc_info.value.code == "VALIDATION_ERROR"
        assert "Invalid chunk ID format" in exc_info.value.message

    def test_get_extraction_invalid_objectid(self, mongodb_client: MongoDBClient):
        """Test that invalid extraction ObjectId raises ValidationError."""
        from src.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            mongodb_client.get_extraction("bad-id-123")
        assert exc_info.value.code == "VALIDATION_ERROR"
        assert "Invalid extraction ID format" in exc_info.value.message

    def test_update_source_empty_updates(
        self, mongodb_client: MongoDBClient, sample_source: Source
    ):
        """Test that empty updates dict raises ValidationError."""
        from src.exceptions import ValidationError

        source_id = mongodb_client.create_source(sample_source)

        with pytest.raises(ValidationError) as exc_info:
            mongodb_client.update_source(source_id, {})
        assert exc_info.value.code == "VALIDATION_ERROR"
        assert "cannot be empty" in exc_info.value.message

    def test_update_source_only_protected_fields(
        self, mongodb_client: MongoDBClient, sample_source: Source
    ):
        """Test that updates with only _id/id fields raises ValidationError."""
        from src.exceptions import ValidationError

        source_id = mongodb_client.create_source(sample_source)

        with pytest.raises(ValidationError) as exc_info:
            mongodb_client.update_source(source_id, {"_id": "test", "id": "test2"})
        assert exc_info.value.code == "VALIDATION_ERROR"

    def test_delete_source_invalid_objectid(self, mongodb_client: MongoDBClient):
        """Test that invalid ObjectId on delete raises ValidationError."""
        from src.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            mongodb_client.delete_source("12345")
        assert exc_info.value.code == "VALIDATION_ERROR"


class TestMongoDBClientSaveExtractionFromExtractor:
    """Tests for save_extraction_from_extractor method.

    This method handles extractions from the extractor system (Decision,
    Pattern, Warning, etc.) and converts them to MongoDB format.
    """

    def test_save_decision_extraction(self, mongodb_client: MongoDBClient):
        """Test saving a Decision extraction from extractor system."""
        from src.extractors import Decision

        decision = Decision(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439012",
            question="Should I use RAG or fine-tuning?",
            options=["RAG", "Fine-tuning"],
            recommended_approach="RAG for most cases",
            topics=["rag", "fine-tuning"],
        )

        extraction_id = mongodb_client.save_extraction_from_extractor(decision)

        assert extraction_id is not None
        assert len(extraction_id) == 24  # Valid ObjectId length

        # Verify document structure in MongoDB
        from bson import ObjectId

        doc = mongodb_client._db[settings.extractions_collection].find_one({"_id": ObjectId(extraction_id)})
        assert doc is not None
        assert doc["source_id"] == "507f1f77bcf86cd799439011"
        assert doc["chunk_id"] == "507f1f77bcf86cd799439012"
        assert doc["type"] == "decision"
        assert doc["topics"] == ["rag", "fine-tuning"]
        assert "content" in doc
        assert doc["content"]["question"] == "Should I use RAG or fine-tuning?"

    def test_save_pattern_extraction(self, mongodb_client: MongoDBClient):
        """Test saving a Pattern extraction from extractor system."""
        from src.extractors import Pattern

        pattern = Pattern(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439012",
            name="Semantic Caching",
            problem="High API costs",
            solution="Use embedding-based cache",
            topics=["caching", "embeddings"],
        )

        extraction_id = mongodb_client.save_extraction_from_extractor(pattern)

        assert extraction_id is not None

        from bson import ObjectId

        doc = mongodb_client._db[settings.extractions_collection].find_one({"_id": ObjectId(extraction_id)})
        assert doc["type"] == "pattern"
        assert doc["content"]["name"] == "Semantic Caching"
        assert doc["content"]["solution"] == "Use embedding-based cache"

    def test_save_warning_extraction(self, mongodb_client: MongoDBClient):
        """Test saving a Warning extraction from extractor system."""
        from src.extractors import Warning

        warning = Warning(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439012",
            title="Token Overflow",
            description="Context window limits cause truncation",
            topics=["tokens"],
        )

        extraction_id = mongodb_client.save_extraction_from_extractor(warning)

        assert extraction_id is not None

        from bson import ObjectId

        doc = mongodb_client._db[settings.extractions_collection].find_one({"_id": ObjectId(extraction_id)})
        assert doc["type"] == "warning"
        assert doc["content"]["title"] == "Token Overflow"

    def test_duplicate_detection_returns_existing_id(self, mongodb_client: MongoDBClient):
        """Test that duplicate extractions return existing ID."""
        from src.extractors import Decision

        decision = Decision(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439014",  # Unique chunk_id for this test
            question="Duplicate test question",
            topics=["test"],
        )

        # First save
        first_id = mongodb_client.save_extraction_from_extractor(decision)

        # Second save with same chunk_id + type should return existing ID
        second_id = mongodb_client.save_extraction_from_extractor(decision)

        assert first_id == second_id

        # Verify only one document exists
        count = mongodb_client._db[settings.extractions_collection].count_documents({
            "chunk_id": "507f1f77bcf86cd799439014",
            "type": "decision",
        })
        assert count == 1

    def test_different_chunk_creates_new_extraction(self, mongodb_client: MongoDBClient):
        """Test that different chunk_id creates new extraction."""
        from src.extractors import Decision

        decision1 = Decision(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439015",
            question="First question",
            topics=["test"],
        )

        decision2 = Decision(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439016",
            question="Second question",
            topics=["test"],
        )

        first_id = mongodb_client.save_extraction_from_extractor(decision1)
        second_id = mongodb_client.save_extraction_from_extractor(decision2)

        assert first_id != second_id

    def test_different_type_creates_new_extraction(self, mongodb_client: MongoDBClient):
        """Test that different type on same chunk creates new extraction."""
        from src.extractors import Decision, Pattern

        decision = Decision(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439017",
            question="Test question",
            topics=["test"],
        )

        pattern = Pattern(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439017",  # Same chunk
            name="Test Pattern",
            problem="Test problem",
            solution="Test solution",
            topics=["test"],
        )

        first_id = mongodb_client.save_extraction_from_extractor(decision)
        second_id = mongodb_client.save_extraction_from_extractor(pattern)

        # Different types should create different extractions
        assert first_id != second_id

    def test_content_fields_extracted_correctly(self, mongodb_client: MongoDBClient):
        """Test that content fields are properly extracted from flat model."""
        from src.extractors import Methodology, MethodologyStep

        methodology = Methodology(
            source_id="507f1f77bcf86cd799439011",
            chunk_id="507f1f77bcf86cd799439018",
            name="Test Methodology",
            steps=[
                MethodologyStep(order=1, title="Step 1", description="Do this"),
                MethodologyStep(order=2, title="Step 2", description="Then this"),
            ],
            prerequisites=["Pre 1", "Pre 2"],
            outputs=["Output 1"],
            topics=["methodology"],
        )

        extraction_id = mongodb_client.save_extraction_from_extractor(methodology)

        from bson import ObjectId

        doc = mongodb_client._db[settings.extractions_collection].find_one({"_id": ObjectId(extraction_id)})

        # Verify content structure
        content = doc["content"]
        assert content["name"] == "Test Methodology"
        assert len(content["steps"]) == 2
        assert content["prerequisites"] == ["Pre 1", "Pre 2"]
        assert content["outputs"] == ["Output 1"]

        # Verify base fields are NOT in content
        assert "source_id" not in content
        assert "chunk_id" not in content
        assert "type" not in content
        assert "topics" not in content
