"""Integration tests for ExtractionStorage with real MongoDB and Qdrant.

These tests require running Docker containers:
    docker compose up -d mongodb qdrant

Tests verify end-to-end extraction persistence and query capabilities.
"""

import pytest
from bson import ObjectId

from src.config import KNOWLEDGE_VECTORS_COLLECTION, settings
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
    COLLECTION_NAME,
    CONTENT_TYPE_EXTRACTION,
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
        client._db[settings.extractions_collection].delete_many({})
    client.close()


@pytest.fixture(scope="module")
def real_qdrant():
    """Provide a real Qdrant client."""
    client = QdrantStorageClient()
    # Ensure unified knowledge collection exists
    client.ensure_knowledge_collection()
    yield client
    # Cleanup after all tests - delete all points but keep collection
    try:
        from qdrant_client import models
        client.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source_id",
                            match=models.MatchValue(value="test-source-001"),
                        )
                    ]
                )
            ),
        )
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
        real_mongodb._db[settings.extractions_collection].delete_many({})
    real_qdrant.delete_by_source(COLLECTION_NAME, "test-source-001")

    yield

    # Cleanup after
    if real_mongodb._db is not None:
        real_mongodb._db[settings.extractions_collection].delete_many({})
    real_qdrant.delete_by_source(COLLECTION_NAME, "test-source-001")


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
        doc = real_mongodb._db[settings.extractions_collection].find_one(
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
        doc = real_mongodb._db[settings.extractions_collection].find_one(
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

        doc = real_mongodb._db[settings.extractions_collection].find_one(
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
        """Verify Qdrant payload contains extraction type in unified collection."""
        # Use unique chunk_id to avoid conflicts with other tests
        unique_chunk_id = "test-chunk-type-filter"
        decision = Decision(
            source_id="test-source-001",
            chunk_id=unique_chunk_id,
            question="What embedding model to use?",
            recommended_approach="all-MiniLM-L6-v2 for local",
            topics=["embeddings"],
        )

        result = extraction_storage.save_extraction(decision)
        assert result["qdrant_saved"] is True

        # Search with extraction_type filter in unified collection
        query_vector = real_embedder.embed_text("embedding model selection")
        results = real_qdrant.search_with_filter(
            collection=COLLECTION_NAME,  # Use unified collection
            query_vector=query_vector,
            filter_dict={
                "extraction_type": "decision",  # New payload field name
                "content_type": CONTENT_TYPE_EXTRACTION,
            },
            limit=10,
        )

        assert len(results) >= 1
        # Find our extraction by unique chunk_id
        found = any(r["payload"]["chunk_id"] == unique_chunk_id for r in results)
        assert found

    def test_qdrant_payload_contains_topics(
        self, extraction_storage, real_qdrant, real_embedder, cleanup_extractions
    ):
        """Verify Qdrant payload contains topics for filtering."""
        # Use unique chunk_id to avoid conflicts with other tests
        unique_chunk_id = "test-chunk-topic-filter"
        pattern = Pattern(
            source_id="test-source-001",
            chunk_id=unique_chunk_id,
            name="RAG Pattern",
            problem="Need context-aware responses",
            solution="Retrieve then generate",
            topics=["rag", "retrieval"],
        )

        result = extraction_storage.save_extraction(pattern)
        assert result["qdrant_saved"] is True

        # Search with topic filter in unified collection
        query_vector = real_embedder.embed_text("retrieval augmented generation")
        results = real_qdrant.search_with_filter(
            collection=COLLECTION_NAME,  # Use unified collection
            query_vector=query_vector,
            filter_dict={
                "topics": ["rag"],
                "content_type": CONTENT_TYPE_EXTRACTION,
            },
            limit=10,
        )

        assert len(results) >= 1
        # Find our extraction by unique chunk_id
        found = any(r["payload"]["chunk_id"] == unique_chunk_id for r in results)
        assert found


class TestEmbeddingDimensionValidation:
    """Test that embeddings are validated to 768 dimensions."""

    def test_embedding_is_768_dimensions(
        self, extraction_storage, real_embedder, cleanup_extractions
    ):
        """Verify generated embeddings are exactly 768 dimensions."""
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

        assert len(embedding) == 768

    def test_storage_uses_768d_embeddings(
        self, extraction_storage, real_qdrant, cleanup_extractions
    ):
        """Verify storage service uses 768d embeddings for Qdrant."""
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


class TestRichPayloadGeneration:
    """Test rich payload generation for unified collection architecture."""

    def test_extraction_title_from_pattern(self, extraction_storage):
        """Test _get_extraction_title extracts name from Pattern."""
        pattern = Pattern(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            name="Semantic Caching Pattern",
            problem="High API costs",
            solution="Use embedding cache",
        )
        title = extraction_storage._get_extraction_title(pattern)
        assert title == "Semantic Caching Pattern"

    def test_extraction_title_from_warning(self, extraction_storage):
        """Test _get_extraction_title extracts title from Warning."""
        warning = Warning(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            title="Token Overflow Risk",
            description="Context window limits",
        )
        title = extraction_storage._get_extraction_title(warning)
        assert title == "Token Overflow Risk"

    def test_extraction_title_from_decision(self, extraction_storage):
        """Test _get_extraction_title extracts question from Decision."""
        decision = Decision(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            question="Should I use RAG or fine-tuning for my use case?",
        )
        title = extraction_storage._get_extraction_title(decision)
        assert title == "Should I use RAG or fine-tuning for my use case?"

    def test_extraction_title_from_methodology(self, extraction_storage):
        """Test _get_extraction_title extracts name from Methodology."""
        methodology = Methodology(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            name="RAG Evaluation Methodology",
        )
        title = extraction_storage._get_extraction_title(methodology)
        assert title == "RAG Evaluation Methodology"

    def test_extraction_title_from_persona(self, extraction_storage):
        """Test _get_extraction_title extracts role from Persona."""
        persona = Persona(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            role="AI Solutions Architect",
        )
        title = extraction_storage._get_extraction_title(persona)
        assert title == "AI Solutions Architect"

    def test_rich_payload_contains_required_fields(
        self, extraction_storage, real_mongodb, cleanup_extractions
    ):
        """Test _build_rich_payload includes all required indexed fields."""
        pattern = Pattern(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            name="Test Pattern",
            problem="Test problem",
            solution="Test solution",
            topics=["rag", "caching"],
        )

        # Build payload (without MongoDB lookup - source/chunk not in DB)
        payload = extraction_storage._build_rich_payload(
            pattern,
            extraction_id="507f1f77bcf86cd799439013",
            project_id="test_project",
        )

        # Verify indexed fields
        assert payload["project_id"] == "test_project"
        assert payload["content_type"] == CONTENT_TYPE_EXTRACTION
        assert payload["source_id"] == "test-source-001"
        assert payload["extraction_type"] == "pattern"
        assert payload["topics"] == ["rag", "caching"]

        # Verify display fields
        assert payload["chunk_id"] == "test-chunk-001"
        assert payload["extraction_id"] == "507f1f77bcf86cd799439013"
        assert payload["extraction_title"] == "Test Pattern"
        assert payload["_original_id"] == "507f1f77bcf86cd799439013"

    def test_rich_payload_defaults_project_from_settings(self, extraction_storage):
        """Test _build_rich_payload uses settings.project_id when not specified."""
        pattern = Pattern(
            source_id="test-source-001",
            chunk_id="test-chunk-001",
            name="Test Pattern",
            problem="Test",
            solution="Test",
        )

        payload = extraction_storage._build_rich_payload(
            pattern,
            extraction_id="507f1f77bcf86cd799439013",
        )

        # Should use settings.project_id (default is "default")
        assert payload["project_id"] == settings.project_id

    def test_rich_payload_gracefully_handles_missing_source(self, extraction_storage):
        """Test _build_rich_payload provides defaults when source lookup fails."""
        pattern = Pattern(
            source_id="nonexistent-source-id-000",
            chunk_id="nonexistent-chunk-id-000",
            name="Test Pattern",
            problem="Test",
            solution="Test",
        )

        payload = extraction_storage._build_rich_payload(
            pattern,
            extraction_id="507f1f77bcf86cd799439013",
        )

        # Should have empty/default values for source metadata
        assert payload["source_type"] == ""
        assert payload["source_category"] == "foundational"
        assert payload["source_year"] is None
        assert payload["source_tags"] == []
        assert payload["source_title"] == ""

    def test_rich_payload_gracefully_handles_missing_chunk(self, extraction_storage):
        """Test _build_rich_payload provides defaults when chunk lookup fails."""
        pattern = Pattern(
            source_id="nonexistent-source-id-000",
            chunk_id="nonexistent-chunk-id-000",
            name="Test Pattern",
            problem="Test",
            solution="Test",
        )

        payload = extraction_storage._build_rich_payload(
            pattern,
            extraction_id="507f1f77bcf86cd799439013",
        )

        # Should have None values for chunk position
        assert payload["chapter"] is None
        assert payload["section"] is None
        assert payload["page"] is None
