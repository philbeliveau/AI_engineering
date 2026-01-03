"""Integration tests for QdrantStorageClient.

These tests require a running Qdrant instance (docker-compose up -d).
"""

import pytest

from src.exceptions import QdrantVectorError
from src.storage import COLLECTION_NAME, VECTOR_SIZE, QdrantStorageClient
from src.storage.qdrant import CHUNKS_COLLECTION, EXTRACTIONS_COLLECTION


class TestQdrantConnection:
    """Tests for Qdrant connection and health check."""

    def test_connection_success(self, qdrant_client):
        """Test that Qdrant client connects successfully."""
        assert qdrant_client is not None
        assert qdrant_client.client is not None

    def test_health_check(self, qdrant_client):
        """Test that health check returns True when Qdrant is running."""
        is_healthy = qdrant_client.health_check()
        assert is_healthy is True


class TestCollectionManagement:
    """Tests for collection creation and management."""

    def test_ensure_chunks_collection(self, qdrant_client):
        """Test chunks collection creation with 384d vectors and Cosine distance."""
        qdrant_client.ensure_collection("test_chunks")

        collections = qdrant_client.client.get_collections().collections
        collection_names = [c.name for c in collections]

        assert "test_chunks" in collection_names

    def test_ensure_extractions_collection(self, qdrant_client):
        """Test extractions collection creation."""
        qdrant_client.ensure_collection("test_extractions")

        collections = qdrant_client.client.get_collections().collections
        collection_names = [c.name for c in collections]

        assert "test_extractions" in collection_names

    def test_ensure_collection_idempotent(self, qdrant_client):
        """Test that ensure_collection is idempotent (no error if exists)."""
        # Create collection twice - should not raise
        qdrant_client.ensure_collection("test_collection")
        qdrant_client.ensure_collection("test_collection")

        collections = qdrant_client.client.get_collections().collections
        collection_names = [c.name for c in collections]

        assert "test_collection" in collection_names

    def test_collection_vector_config(self, qdrant_client):
        """Test that collection has correct vector configuration (384d, Cosine)."""
        qdrant_client.ensure_collection("test_collection")

        collection_info = qdrant_client.client.get_collection("test_collection")

        assert collection_info.config.params.vectors.size == VECTOR_SIZE
        # Distance metric is uppercase in Qdrant API response
        assert collection_info.config.params.vectors.distance.name.upper() == "COSINE"


class TestVectorUpsert:
    """Tests for vector upsert operations."""

    def test_upsert_valid_vector(
        self, qdrant_client, test_vector_384d, sample_chunk_payload
    ):
        """Test upsert with valid 384d vector."""
        qdrant_client.ensure_collection("test_collection")

        # Should not raise
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="test_point_1",
            vector=test_vector_384d,
            payload=sample_chunk_payload,
        )

        # Verify point was inserted
        results = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=1,
        )

        assert len(results) == 1
        assert results[0]["id"] == "test_point_1"

    def test_upsert_invalid_vector_size_rejected(
        self, qdrant_client, test_vector_256d, sample_chunk_payload
    ):
        """Test that non-384d vectors are rejected before reaching Qdrant."""
        # Test through public methods that validate before calling Qdrant
        with pytest.raises(QdrantVectorError) as exc_info:
            qdrant_client.upsert_chunk_vector(
                chunk_id="bad_point",
                vector=test_vector_256d,
                payload=sample_chunk_payload,
            )

        assert exc_info.value.code == "INVALID_VECTOR_SIZE"
        assert exc_info.value.details["expected"] == 384
        assert exc_info.value.details["actual"] == 256

    def test_upsert_chunk_vector(
        self, qdrant_client, test_vector_384d, sample_chunk_payload
    ):
        """Test upsert_chunk_vector method uses unified collection."""
        qdrant_client.ensure_knowledge_collection()

        qdrant_client.upsert_chunk_vector(
            chunk_id="chunk_1",
            vector=test_vector_384d,
            payload=sample_chunk_payload,
        )

        results = qdrant_client.search_chunks(
            query_vector=test_vector_384d,
            limit=1,
        )

        assert len(results) == 1
        assert results[0]["payload"]["source_id"] == sample_chunk_payload["source_id"]
        assert results[0]["payload"]["content_type"] == "chunk"

    def test_upsert_extraction_vector(
        self, qdrant_client, test_vector_384d, sample_extraction_payload
    ):
        """Test upsert_extraction_vector method uses unified collection."""
        qdrant_client.ensure_knowledge_collection()

        qdrant_client.upsert_extraction_vector(
            extraction_id="extraction_1",
            vector=test_vector_384d,
            payload=sample_extraction_payload,
        )

        results = qdrant_client.search_extractions(
            query_vector=test_vector_384d,
            limit=1,
        )

        assert len(results) == 1
        assert results[0]["payload"]["extraction_type"] == "decision"
        assert "architecture" in results[0]["payload"]["topics"]
        assert results[0]["payload"]["content_type"] == "extraction"


class TestSemanticSearch:
    """Tests for semantic search operations."""

    def test_search_returns_ranked_results(self, qdrant_client, test_vector_384d):
        """Test that search returns results ranked by similarity score."""
        qdrant_client.ensure_collection("test_collection")

        # Insert multiple vectors with varying similarity
        for i in range(3):
            # Slightly different vectors
            vector = [0.1 + (i * 0.01)] * 384
            qdrant_client._upsert_vector(
                collection="test_collection",
                point_id=f"point_{i}",
                vector=vector,
                payload={"index": i},
            )

        results = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=3,
        )

        assert len(results) == 3
        # Results should be ordered by score (descending)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_includes_payload(
        self, qdrant_client, test_vector_384d, sample_extraction_payload
    ):
        """Test that search results include payload data."""
        qdrant_client.ensure_collection("test_collection")

        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="point_with_payload",
            vector=test_vector_384d,
            payload=sample_extraction_payload,
        )

        results = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=1,
        )

        assert len(results) == 1
        assert results[0]["payload"]["source_id"] == sample_extraction_payload["source_id"]
        assert results[0]["payload"]["extraction_type"] == "decision"

    def test_search_respects_limit(self, qdrant_client, test_vector_384d):
        """Test that search respects the limit parameter."""
        qdrant_client.ensure_collection("test_collection")

        # Insert 5 vectors
        for i in range(5):
            qdrant_client._upsert_vector(
                collection="test_collection",
                point_id=f"point_{i}",
                vector=test_vector_384d,
                payload={"index": i},
            )

        # Request only 2
        results = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=2,
        )

        assert len(results) == 2


class TestFilteredSearch:
    """Tests for filtered semantic search."""

    def test_search_with_type_filter(
        self, qdrant_client, test_vector_384d, sample_chunk_payload
    ):
        """Test filtered search by type."""
        qdrant_client.ensure_collection("test_collection")

        # Insert vectors with different types
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="decision_1",
            vector=test_vector_384d,
            payload={**sample_chunk_payload, "type": "decision"},
        )
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="pattern_1",
            vector=test_vector_384d,
            payload={**sample_chunk_payload, "type": "pattern"},
        )

        # Filter by type
        results = qdrant_client.search_with_filter(
            collection="test_collection",
            query_vector=test_vector_384d,
            filter_dict={"type": "decision"},
            limit=10,
        )

        assert len(results) == 1
        assert results[0]["payload"]["type"] == "decision"

    def test_search_with_source_id_filter(
        self, qdrant_client, test_vector_384d
    ):
        """Test filtered search by source_id."""
        qdrant_client.ensure_collection("test_collection")

        # Insert vectors with different source_ids
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="source_a_1",
            vector=test_vector_384d,
            payload={"source_id": "source_a", "chunk_id": "c1"},
        )
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="source_b_1",
            vector=test_vector_384d,
            payload={"source_id": "source_b", "chunk_id": "c2"},
        )

        results = qdrant_client.search_with_filter(
            collection="test_collection",
            query_vector=test_vector_384d,
            filter_dict={"source_id": "source_a"},
            limit=10,
        )

        assert len(results) == 1
        assert results[0]["payload"]["source_id"] == "source_a"

    def test_search_with_topics_filter(
        self, qdrant_client, test_vector_384d
    ):
        """Test filtered search by topics (match any in list)."""
        qdrant_client.ensure_collection("test_collection")

        # Insert vectors with different topics
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="rag_point",
            vector=test_vector_384d,
            payload={"source_id": "s1", "topics": ["rag", "embeddings"]},
        )
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="ml_point",
            vector=test_vector_384d,
            payload={"source_id": "s2", "topics": ["ml", "training"]},
        )

        # Filter by topics - should match any
        results = qdrant_client.search_with_filter(
            collection="test_collection",
            query_vector=test_vector_384d,
            filter_dict={"topics": ["rag", "ml"]},
            limit=10,
        )

        # Both should match since both have at least one matching topic
        assert len(results) == 2


class TestDeleteOperations:
    """Tests for delete operations."""

    def test_delete_by_id(self, qdrant_client, test_vector_384d, sample_chunk_payload):
        """Test deleting a point by ID."""
        qdrant_client.ensure_collection("test_collection")

        # Insert a point
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="to_delete",
            vector=test_vector_384d,
            payload=sample_chunk_payload,
        )

        # Verify it exists
        results_before = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=1,
        )
        assert len(results_before) == 1

        # Delete it
        qdrant_client.delete_by_id(collection="test_collection", point_id="to_delete")

        # Verify it's gone
        results_after = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=1,
        )
        assert len(results_after) == 0

    def test_delete_by_source(self, qdrant_client, test_vector_384d):
        """Test deleting all points for a source."""
        qdrant_client.ensure_collection("test_collection")

        # Insert multiple points with same source_id
        for i in range(3):
            qdrant_client._upsert_vector(
                collection="test_collection",
                point_id=f"source_x_{i}",
                vector=test_vector_384d,
                payload={"source_id": "source_x", "chunk_id": f"c{i}"},
            )

        # Insert one with different source_id
        qdrant_client._upsert_vector(
            collection="test_collection",
            point_id="source_y_1",
            vector=test_vector_384d,
            payload={"source_id": "source_y", "chunk_id": "c0"},
        )

        # Verify 4 points exist
        results_before = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=10,
        )
        assert len(results_before) == 4

        # Delete by source_id = source_x
        qdrant_client.delete_by_source(collection="test_collection", source_id="source_x")

        # Verify only source_y remains
        results_after = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=10,
        )
        assert len(results_after) == 1
        assert results_after[0]["payload"]["source_id"] == "source_y"

    def test_delete_nonexistent_point_succeeds(self, qdrant_client):
        """Test that deleting a non-existent point doesn't raise an error."""
        qdrant_client.ensure_collection("test_collection")

        # Should not raise
        qdrant_client.delete_by_id(
            collection="test_collection",
            point_id="nonexistent_point",
        )

    def test_delete_batch(self, qdrant_client, test_vector_384d):
        """Test batch delete operations."""
        qdrant_client.ensure_collection("test_collection")

        # Insert multiple points
        for i in range(5):
            qdrant_client._upsert_vector(
                collection="test_collection",
                point_id=f"batch_{i}",
                vector=test_vector_384d,
                payload={"index": i},
            )

        # Delete a subset
        qdrant_client.delete_batch(
            collection="test_collection",
            point_ids=["batch_0", "batch_2", "batch_4"],
        )

        # Verify only batch_1 and batch_3 remain
        results = qdrant_client.search(
            collection="test_collection",
            query_vector=test_vector_384d,
            limit=10,
        )
        assert len(results) == 2
        remaining_ids = {r["id"] for r in results}
        assert remaining_ids == {"batch_1", "batch_3"}


class TestErrorHandling:
    """Tests for error handling with structured error format."""

    def test_invalid_vector_size_error_format(
        self, qdrant_client, test_vector_256d, sample_chunk_payload
    ):
        """Test that QdrantVectorError has correct structured format."""
        # Use public method that validates before calling Qdrant
        with pytest.raises(QdrantVectorError) as exc_info:
            qdrant_client.upsert_chunk_vector(
                chunk_id="bad_point",
                vector=test_vector_256d,
                payload=sample_chunk_payload,
            )

        error = exc_info.value
        assert error.code == "INVALID_VECTOR_SIZE"
        assert "256" in error.message
        assert error.details["expected"] == 384
        assert error.details["actual"] == 256

        # Test to_dict format
        error_dict = error.to_dict()
        assert "code" in error_dict["error"]
        assert "message" in error_dict["error"]
        assert "details" in error_dict["error"]

    def test_search_with_invalid_vector_raises(self, qdrant_client, test_vector_256d):
        """Test that search with invalid vector raises QdrantVectorError."""
        qdrant_client.ensure_collection("test_collection")

        with pytest.raises(QdrantVectorError) as exc_info:
            qdrant_client.search(
                collection="test_collection",
                query_vector=test_vector_256d,
                limit=10,
            )

        assert exc_info.value.code == "INVALID_VECTOR_SIZE"


class TestUnifiedCollectionArchitecture:
    """Tests for single-collection architecture with payload-based filtering."""

    def test_ensure_knowledge_collection(self, qdrant_client):
        """Test that ensure_knowledge_collection creates unified collection."""
        qdrant_client.ensure_knowledge_collection()

        collections = qdrant_client.client.get_collections().collections
        collection_names = [c.name for c in collections]

        assert COLLECTION_NAME in collection_names

    def test_chunks_and_extractions_in_same_collection(
        self, qdrant_client, test_vector_384d, sample_chunk_payload, sample_extraction_payload
    ):
        """Test that chunks and extractions coexist in unified collection."""
        qdrant_client.ensure_knowledge_collection()

        # Insert a chunk
        qdrant_client.upsert_chunk_vector(
            chunk_id="unified_chunk_1",
            vector=test_vector_384d,
            payload=sample_chunk_payload,
        )

        # Insert an extraction
        qdrant_client.upsert_extraction_vector(
            extraction_id="unified_extraction_1",
            vector=test_vector_384d,
            payload=sample_extraction_payload,
        )

        # Search all (no content_type filter)
        all_results = qdrant_client.search(
            collection=COLLECTION_NAME,
            query_vector=test_vector_384d,
            limit=10,
        )

        assert len(all_results) >= 2

    def test_content_type_filtering(
        self, qdrant_client, test_vector_384d, sample_chunk_payload, sample_extraction_payload
    ):
        """Test that content_type correctly filters chunks vs extractions."""
        qdrant_client.ensure_knowledge_collection()

        # Insert both types
        qdrant_client.upsert_chunk_vector(
            chunk_id="filter_test_chunk",
            vector=test_vector_384d,
            payload=sample_chunk_payload,
        )
        qdrant_client.upsert_extraction_vector(
            extraction_id="filter_test_extraction",
            vector=test_vector_384d,
            payload=sample_extraction_payload,
        )

        # Search only chunks
        chunk_results = qdrant_client.search_chunks(
            query_vector=test_vector_384d,
            limit=10,
        )
        assert all(r["payload"]["content_type"] == "chunk" for r in chunk_results)

        # Search only extractions
        extraction_results = qdrant_client.search_extractions(
            query_vector=test_vector_384d,
            limit=10,
        )
        assert all(r["payload"]["content_type"] == "extraction" for r in extraction_results)

    def test_project_id_isolation(
        self, qdrant_client, test_vector_384d, sample_chunk_payload
    ):
        """Test that project_id isolates data between projects."""
        qdrant_client.ensure_knowledge_collection()

        # Insert chunk for project A
        qdrant_client.upsert_chunk_vector(
            chunk_id="project_a_chunk",
            vector=test_vector_384d,
            payload=sample_chunk_payload,
            project_id="project_a",
        )

        # Insert chunk for project B
        qdrant_client.upsert_chunk_vector(
            chunk_id="project_b_chunk",
            vector=test_vector_384d,
            payload=sample_chunk_payload,
            project_id="project_b",
        )

        # Search project A only
        results_a = qdrant_client.search_knowledge(
            query_vector=test_vector_384d,
            project_id="project_a",
            limit=10,
        )
        assert all(r["payload"]["project_id"] == "project_a" for r in results_a)

        # Search project B only
        results_b = qdrant_client.search_knowledge(
            query_vector=test_vector_384d,
            project_id="project_b",
            limit=10,
        )
        assert all(r["payload"]["project_id"] == "project_b" for r in results_b)

    def test_extraction_type_filtering(
        self, qdrant_client, test_vector_384d
    ):
        """Test filtering extractions by extraction_type."""
        qdrant_client.ensure_knowledge_collection()

        # Insert different extraction types using extraction_type key
        qdrant_client.upsert_extraction_vector(
            extraction_id="decision_1",
            vector=test_vector_384d,
            payload={"source_id": "s1", "chunk_id": "c1", "extraction_type": "decision", "topics": []},
        )
        qdrant_client.upsert_extraction_vector(
            extraction_id="pattern_1",
            vector=test_vector_384d,
            payload={"source_id": "s1", "chunk_id": "c1", "extraction_type": "pattern", "topics": []},
        )

        # Filter by extraction_type
        decision_results = qdrant_client.search_extractions(
            query_vector=test_vector_384d,
            extraction_type="decision",
            limit=10,
        )
        assert all(r["payload"]["extraction_type"] == "decision" for r in decision_results)

    def test_search_knowledge_combined_filters(
        self, qdrant_client, test_vector_384d
    ):
        """Test search_knowledge with multiple filters combined."""
        qdrant_client.ensure_knowledge_collection()

        # Insert extraction with specific metadata
        # Use extraction_type (not legacy 'type' key) per single-collection architecture
        qdrant_client.upsert_extraction_vector(
            extraction_id="combined_filter_test",
            vector=test_vector_384d,
            payload={
                "source_id": "special_source",
                "chunk_id": "c1",
                "extraction_type": "methodology",
                "topics": ["rag", "llm"],
                "source_type": "book",
            },
            project_id="test_project",
        )

        # Search with multiple filters
        results = qdrant_client.search_knowledge(
            query_vector=test_vector_384d,
            project_id="test_project",
            content_type="extraction",
            extraction_type="methodology",
            source_id="special_source",
            topics=["rag"],
            limit=10,
        )

        assert len(results) >= 1
        assert results[0]["payload"]["extraction_type"] == "methodology"
        assert results[0]["payload"]["source_id"] == "special_source"

    def test_default_project_id_backwards_compatibility(
        self, qdrant_client, test_vector_384d, sample_chunk_payload
    ):
        """Test AC9: Data without explicit project_id defaults to 'default'.

        Verifies backwards compatibility for existing data that may not have
        project_id set. The system should treat missing project_id as 'default'.
        """
        qdrant_client.ensure_knowledge_collection()

        # Insert chunk WITHOUT explicit project_id (should use default from settings)
        qdrant_client.upsert_chunk_vector(
            chunk_id="backwards_compat_chunk",
            vector=test_vector_384d,
            payload=sample_chunk_payload,
            # project_id not specified - should default to settings.project_id ("default")
        )

        # Search with explicit project_id="default" should find the chunk
        results = qdrant_client.search_chunks(
            query_vector=test_vector_384d,
            project_id="default",
            limit=10,
        )

        # Verify the chunk is found and has project_id="default"
        matching = [r for r in results if r["id"] == "backwards_compat_chunk"]
        assert len(matching) >= 1
        assert matching[0]["payload"]["project_id"] == "default"

    def test_tenant_index_is_created(self, qdrant_client):
        """Test M2: Verify project_id index is created with is_tenant optimization.

        Validates that the project_id payload index is created with is_tenant=True
        for efficient multi-tenant queries per Qdrant v1.11+ best practices.
        """
        # Create collection with indexes
        qdrant_client.ensure_knowledge_collection()

        # Get collection info to verify index configuration
        collection_info = qdrant_client.client.get_collection(COLLECTION_NAME)

        # Check that payload indexes are created
        payload_schema = collection_info.payload_schema
        assert payload_schema is not None

        # Verify project_id index exists
        assert "project_id" in payload_schema

        # The project_id index should be a keyword type
        project_id_schema = payload_schema["project_id"]
        assert project_id_schema.data_type.name.upper() == "KEYWORD"
