"""Integration tests for ExtractionStorage with real MongoDB and Qdrant.

These tests require running Docker containers:
    docker compose up -d mongodb qdrant

Tests verify end-to-end extraction persistence and query capabilities.
"""

import pytest
from bson import ObjectId

from src.embeddings import get_embedder, reset_embedder
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
from src.storage import (
    EXTRACTIONS_COLLECTION,
    ExtractionStorage,
    MongoDBClient,
    QdrantStorageClient,
)


@pytest.fixture(scope="module")
def real_mongodb():
    """Provide a real MongoDB client connected to test database."""
    client = MongoDBClient(database="knowledge_db_test")
    client.connect()
    yield client
    # Cleanup after all tests
    if client._db is not None:
        client._db.extractions.delete_many({})
    client.close()


@pytest.fixture(scope="module")
def real_qdrant():
    """Provide a real Qdrant client."""
    client = QdrantStorageClient()
    # Ensure extractions collection exists
    client.ensure_collection(EXTRACTIONS_COLLECTION)
    yield client
    # Cleanup after all tests
    try:
        client.client.delete_collection(EXTRACTIONS_COLLECTION)
    except Exception:
        pass


@pytest.fixture(scope="module")
def real_embedder():
    """Provide a real embedder instance."""
    reset_embedder()  # Clear singleton for fresh test
    embedder = get_embedder()
    yield embedder
    reset_embedder()


@pytest.fixture
def extraction_storage(real_mongodb, real_qdrant, real_embedder):
    """Provide ExtractionStorage with real dependencies."""
    return ExtractionStorage(
        mongodb_client=real_mongodb,
        qdrant_client=real_qdrant,
        embedder=real_embedder,
    )


@pytest.fixture
def cleanup_extractions(real_mongodb, real_qdrant):
    """Clean up extractions before and after each test."""
    # Cleanup before
    if real_mongodb._db is not None:
        real_mongodb._db.extractions.delete_many({})
    real_qdrant.delete_by_source(EXTRACTIONS_COLLECTION, "test-source-001")

    yield

    # Cleanup after
    if real_mongodb._db is not None:
        real_mongodb._db.extractions.delete_many({})
    real_qdrant.delete_by_source(EXTRACTIONS_COLLECTION, "test-source-001")


class TestSourceAttributionPreservation:
    """Test source attribution chain is preserved through storage."""

    def test_decision_source_attribution(
        self, extraction_storage, real_mongodb, cleanup_extractions
    ):
        """Verify Decision extraction preserves source_id and chunk_id."""
        decision = Decision(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            question="Should I use RAG or fine-tuning?",
            recommended_approach="RAG for most use cases",
            topics=["rag"],
        )

        result = extraction_storage.save_extraction(decision)

        # Verify MongoDB has correct source attribution
        doc = real_mongodb._db.extractions.find_one(
            {"_id": ObjectId(result["extraction_id"])}
        )
        assert doc is not None
        assert doc["source_id"] == "test-source-001"
        assert doc["chunk_id"] == "test-chunk-001"
        assert doc["type"] == "decision"

    def test_pattern_source_attribution(
        self, extraction_storage, real_mongodb, cleanup_extractions
    ):
        """Verify Pattern extraction preserves source_id and chunk_id."""
        pattern = Pattern(
            source_id="test-source-001",
            chunk_id="test-chunk-002",
            name="Semantic Caching",
            problem="High API costs",
            solution="Use embedding-based cache",
            topics=["caching"],
        )

        result = extraction_storage.save_extraction(pattern)

        # Verify MongoDB has correct source attribution
        doc = real_mongodb._db.extractions.find_one(
            {"_id": ObjectId(result["extraction_id"])}
        )
        assert doc is not None
        assert doc["source_id"] == "test-source-001"
        assert doc["chunk_id"] == "test-chunk-002"
        assert doc["type"] == "pattern"

    def test_warning_source_attribution(
        self, extraction_storage, real_mongodb, cleanup_extractions
    ):
        """Verify Warning extraction preserves source_id and chunk_id."""
        warning = Warning(
            source_id="test-source-001",
            chunk_id="test-chunk-003",
            title="Token Overflow",
            description="Context window limits can cause issues",
            topics=["tokens"],
        )

        result = extraction_storage.save_extraction(warning)

        doc = real_mongodb._db.extractions.find_one(
            {"_id": ObjectId(result["extraction_id"])}
        )
        assert doc is not None
        assert doc["source_id"] == "test-source-001"
        assert doc["chunk_id"] == "test-chunk-003"


class TestQdrantPayloadAccuracy:
    """Test Qdrant payload contains correct metadata for filtering."""

    def test_qdrant_payload_contains_type(
        self, extraction_storage, real_qdrant, real_embedder, cleanup_extractions
    ):
        """Verify Qdrant payload contains extraction type."""
        decision = Decision(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            question="What embedding model to use?",
            recommended_approach="all-MiniLM-L6-v2 for local",
            topics=["embeddings"],
        )

        result = extraction_storage.save_extraction(decision)
        assert result["qdrant_saved"] is True

        # Search with type filter
        query_vector = real_embedder.embed_text("embedding model selection")
        results = real_qdrant.search_with_filter(
            collection=EXTRACTIONS_COLLECTION,
            query_vector=query_vector,
            filter_dict={"type": "decision"},
            limit=10,
        )

        assert len(results) >= 1
        # Find our extraction
        found = any(r["payload"]["chunk_id"] == "test-chunk-001" for r in results)
        assert found

    def test_qdrant_payload_contains_topics(
        self, extraction_storage, real_qdrant, real_embedder, cleanup_extractions
    ):
        """Verify Qdrant payload contains topics for filtering."""
        pattern = Pattern(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            name="RAG Pattern",
            problem="Need context-aware responses",
            solution="Retrieve then generate",
            topics=["rag", "retrieval"],
        )

        result = extraction_storage.save_extraction(pattern)
        assert result["qdrant_saved"] is True

        # Search with topic filter
        query_vector = real_embedder.embed_text("retrieval augmented generation")
        results = real_qdrant.search_with_filter(
            collection=EXTRACTIONS_COLLECTION,
            query_vector=query_vector,
            filter_dict={"topics": ["rag"]},
            limit=10,
        )

        assert len(results) >= 1
        found = any(r["payload"]["chunk_id"] == "test-chunk-001" for r in results)
        assert found


class TestEmbeddingDimensionValidation:
    """Test that embeddings are validated to 384 dimensions."""

    def test_embedding_is_384_dimensions(
        self, extraction_storage, real_embedder, cleanup_extractions
    ):
        """Verify generated embeddings are exactly 384 dimensions."""
        decision = Decision(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            question="Test question for dimension check",
            topics=["test"],
        )

        # Generate embedding directly to check dimension
        from src.extractors.utils import generate_extraction_summary

        summary = generate_extraction_summary(decision)
        embedding = real_embedder.embed_text(summary)

        assert len(embedding) == 384

    def test_storage_uses_384d_embeddings(
        self, extraction_storage, real_qdrant, cleanup_extractions
    ):
        """Verify storage service uses 384d embeddings for Qdrant."""
        decision = Decision(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            question="Another test for embedding dimensions",
            topics=["test"],
        )

        result = extraction_storage.save_extraction(decision)

        # If Qdrant saved successfully, embeddings must be correct dimension
        assert result["qdrant_saved"] is True


class TestAllExtractionTypes:
    """Test all extraction types save correctly to both stores."""

    def test_save_decision(self, extraction_storage, cleanup_extractions):
        """Test Decision saves to MongoDB and Qdrant."""
        decision = Decision(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            question="RAG or fine-tuning?",
            topics=["rag"],
        )
        result = extraction_storage.save_extraction(decision)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_pattern(self, extraction_storage, cleanup_extractions):
        """Test Pattern saves to MongoDB and Qdrant."""
        pattern = Pattern(
            source_id="test-source-001",
            chunk_id="test-chunk-002",
            name="Test Pattern",
            problem="Test problem",
            solution="Test solution",
            topics=["patterns"],
        )
        result = extraction_storage.save_extraction(pattern)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_warning(self, extraction_storage, cleanup_extractions):
        """Test Warning saves to MongoDB and Qdrant."""
        warning = Warning(
            source_id="test-source-001",
            chunk_id="test-chunk-003",
            title="Test Warning",
            description="Test description",
            topics=["warnings"],
        )
        result = extraction_storage.save_extraction(warning)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_methodology(self, extraction_storage, cleanup_extractions):
        """Test Methodology saves to MongoDB and Qdrant."""
        methodology = Methodology(
            source_id="test-source-001",
            chunk_id="test-chunk-004",
            name="Test Methodology",
            steps=[MethodologyStep(order=1, title="Step 1", description="Do this")],
            topics=["methodology"],
        )
        result = extraction_storage.save_extraction(methodology)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_checklist(self, extraction_storage, cleanup_extractions):
        """Test Checklist saves to MongoDB and Qdrant."""
        checklist = Checklist(
            source_id="test-source-001",
            chunk_id="test-chunk-005",
            name="Test Checklist",
            items=[ChecklistItem(item="Check this")],
            topics=["checklist"],
        )
        result = extraction_storage.save_extraction(checklist)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_persona(self, extraction_storage, cleanup_extractions):
        """Test Persona saves to MongoDB and Qdrant."""
        persona = Persona(
            source_id="test-source-001",
            chunk_id="test-chunk-006",
            role="Test Engineer",
            responsibilities=["Test things"],
            topics=["personas"],
        )
        result = extraction_storage.save_extraction(persona)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True

    def test_save_workflow(self, extraction_storage, cleanup_extractions):
        """Test Workflow saves to MongoDB and Qdrant."""
        workflow = Workflow(
            source_id="test-source-001",
            chunk_id="test-chunk-007",
            name="Test Workflow",
            trigger="User action",
            steps=[WorkflowStep(order=1, action="Do action")],
            topics=["workflow"],
        )
        result = extraction_storage.save_extraction(workflow)
        assert result["mongodb_saved"] is True
        assert result["qdrant_saved"] is True
