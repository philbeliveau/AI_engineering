"""Tests for Knowledge Pipeline API.

Tests all endpoints:
- GET /health
- POST /ingest (file upload)
- POST /ingest/url
- POST /extract/{source_id}
- GET /sources/{source_id}
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

from api import app, get_project_id


# =============================================================================
# Test Client
# =============================================================================


@pytest.fixture
def client():
    """Create test client for API."""
    # raise_server_exceptions=False allows testing exception handlers
    return TestClient(app, raise_server_exceptions=False)


# =============================================================================
# Test get_project_id Helper
# =============================================================================


class TestGetProjectId:
    """Tests for get_project_id helper function."""

    def test_returns_header_value_when_present(self):
        """Should return X-Project-ID header value when present."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "test-project"

        result = get_project_id(mock_request)

        assert result == "test-project"
        mock_request.headers.get.assert_called_once_with("X-Project-ID", "default")

    def test_returns_default_when_header_missing(self):
        """Should return 'default' when X-Project-ID header is missing."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "default"

        result = get_project_id(mock_request)

        assert result == "default"


# =============================================================================
# Test Health Endpoint
# =============================================================================


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_check_healthy(self, client):
        """Should return healthy status when all services are up."""
        with patch("api.MongoDBClient") as mock_mongo, \
             patch("api.QdrantStorageClient") as mock_qdrant:
            # Mock MongoDB healthy
            mock_mongo_instance = MagicMock()
            mock_mongo_instance.ping.return_value = True
            mock_mongo.return_value = mock_mongo_instance

            # Mock Qdrant healthy
            mock_qdrant_instance = MagicMock()
            mock_qdrant_instance.health_check.return_value = True
            mock_qdrant.return_value = mock_qdrant_instance

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["mongodb"] is True
            assert data["qdrant"] is True

    def test_health_check_degraded_mongodb(self, client):
        """Should return degraded status when MongoDB is down."""
        with patch("api.MongoDBClient") as mock_mongo, \
             patch("api.QdrantStorageClient") as mock_qdrant:
            # Mock MongoDB unhealthy
            mock_mongo.return_value.connect.side_effect = Exception("Connection failed")

            # Mock Qdrant healthy
            mock_qdrant_instance = MagicMock()
            mock_qdrant_instance.health_check.return_value = True
            mock_qdrant.return_value = mock_qdrant_instance

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["mongodb"] is False
            assert data["qdrant"] is True

    def test_health_check_degraded_qdrant(self, client):
        """Should return degraded status when Qdrant is down."""
        with patch("api.MongoDBClient") as mock_mongo, \
             patch("api.QdrantStorageClient") as mock_qdrant:
            # Mock MongoDB healthy
            mock_mongo_instance = MagicMock()
            mock_mongo_instance.ping.return_value = True
            mock_mongo.return_value = mock_mongo_instance

            # Mock Qdrant unhealthy
            mock_qdrant.return_value.health_check.return_value = False

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["mongodb"] is True
            assert data["qdrant"] is False


# =============================================================================
# Test Ingest File Endpoint
# =============================================================================


class TestIngestFileEndpoint:
    """Tests for POST /ingest endpoint."""

    def test_ingest_file_success(self, client, tmp_path):
        """Should successfully ingest a file."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content for ingestion")

        # Mock the IngestionPipeline
        mock_result = MagicMock()
        mock_result.source_id = "abc123"
        mock_result.title = "test.txt"
        mock_result.chunk_count = 5
        mock_result.total_tokens = 100
        mock_result.duration = 1.5

        with patch("api.IngestionPipeline") as mock_pipeline:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.ingest.return_value = mock_result
            mock_pipeline.return_value = mock_instance

            with open(test_file, "rb") as f:
                response = client.post(
                    "/ingest",
                    files={"file": ("test.txt", f, "text/plain")},
                    data={"category": "reference", "tags": "test,demo"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["source_id"] == "abc123"
            assert data["title"] == "test.txt"
            assert data["chunk_count"] == 5
            assert data["project_id"] == "default"
            assert data["status"] == "complete"

    def test_ingest_file_with_project_header(self, client, tmp_path):
        """Should use project ID from X-Project-ID header."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        mock_result = MagicMock()
        mock_result.source_id = "abc123"
        mock_result.title = "test.txt"
        mock_result.chunk_count = 1
        mock_result.total_tokens = 10
        mock_result.duration = 0.5

        with patch("api.IngestionPipeline") as mock_pipeline:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.ingest.return_value = mock_result
            mock_pipeline.return_value = mock_instance

            with open(test_file, "rb") as f:
                response = client.post(
                    "/ingest",
                    files={"file": ("test.txt", f, "text/plain")},
                    headers={"X-Project-ID": "my-custom-project"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["project_id"] == "my-custom-project"


# =============================================================================
# Test Ingest URL Endpoint
# =============================================================================


class TestIngestURLEndpoint:
    """Tests for POST /ingest/url endpoint."""

    def test_ingest_url_success(self, client):
        """Should successfully ingest a URL."""
        mock_result = MagicMock()
        mock_result.source_id = "url123"
        mock_result.title = "Test Document"
        mock_result.chunk_count = 10
        mock_result.total_tokens = 500
        mock_result.duration = 2.5

        with patch("api.IngestionPipeline") as mock_pipeline:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.ingest_url.return_value = mock_result
            mock_pipeline.return_value = mock_instance

            response = client.post(
                "/ingest/url",
                json={
                    "url": "https://example.com/doc.pdf",
                    "category": "reference",
                    "tags": ["test"],
                    "year": 2024,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source_id"] == "url123"
            assert data["title"] == "Test Document"
            assert data["chunk_count"] == 10
            assert data["project_id"] == "default"

    def test_ingest_url_with_project_header(self, client):
        """Should use project ID from X-Project-ID header."""
        mock_result = MagicMock()
        mock_result.source_id = "url123"
        mock_result.title = "Test"
        mock_result.chunk_count = 1
        mock_result.total_tokens = 10
        mock_result.duration = 0.5

        with patch("api.IngestionPipeline") as mock_pipeline:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.ingest_url.return_value = mock_result
            mock_pipeline.return_value = mock_instance

            response = client.post(
                "/ingest/url",
                json={"url": "https://example.com/test.pdf"},
                headers={"X-Project-ID": "custom-project"},
            )

            assert response.status_code == 200
            assert response.json()["project_id"] == "custom-project"


# =============================================================================
# Test Extract Endpoint
# =============================================================================


class TestExtractEndpoint:
    """Tests for POST /extract/{source_id} endpoint."""

    def test_extract_success(self, client):
        """Should successfully run extraction."""
        mock_result = MagicMock()
        mock_result.total_extractions = 15
        mock_result.extraction_counts = {"decision": 5, "pattern": 7, "warning": 3}

        with patch("api.ExtractionPipeline") as mock_pipeline:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.extract_hierarchical.return_value = mock_result
            mock_pipeline.return_value = mock_instance

            response = client.post("/extract/abc123")

            assert response.status_code == 200
            data = response.json()
            assert data["source_id"] == "abc123"
            assert data["total_extractions"] == 15
            assert data["extraction_counts"]["decision"] == 5
            assert data["project_id"] == "default"

    def test_extract_with_project_header(self, client):
        """Should include project ID from header in response."""
        mock_result = MagicMock()
        mock_result.total_extractions = 5
        mock_result.extraction_counts = {"decision": 5}

        with patch("api.ExtractionPipeline") as mock_pipeline:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.extract_hierarchical.return_value = mock_result
            mock_pipeline.return_value = mock_instance

            response = client.post(
                "/extract/abc123",
                headers={"X-Project-ID": "test-project"},
            )

            assert response.status_code == 200
            assert response.json()["project_id"] == "test-project"


# =============================================================================
# Test Source Status Endpoint
# =============================================================================


class TestSourceStatusEndpoint:
    """Tests for GET /sources/{source_id} endpoint."""

    def test_get_source_success(self, client):
        """Should return source status."""
        mock_source = MagicMock()
        mock_source.title = "Test Book"
        mock_source.status = "complete"
        mock_source.project_id = "default"

        with patch("api.MongoDBClient") as mock_mongo:
            mock_instance = MagicMock()
            mock_instance.get_source.return_value = mock_source
            mock_instance.count_chunks_by_source.return_value = 50
            mock_instance.get_extractions_by_source.return_value = [1, 2, 3, 4, 5]
            mock_mongo.return_value = mock_instance

            response = client.get("/sources/abc123")

            assert response.status_code == 200
            data = response.json()
            assert data["source_id"] == "abc123"
            assert data["title"] == "Test Book"
            assert data["status"] == "complete"
            assert data["chunk_count"] == 50
            assert data["extraction_count"] == 5

    def test_get_source_with_project_header(self, client):
        """Should use project ID from source or header."""
        mock_source = MagicMock()
        mock_source.title = "Test"
        mock_source.status = "complete"
        mock_source.project_id = "source-project"

        with patch("api.MongoDBClient") as mock_mongo:
            mock_instance = MagicMock()
            mock_instance.get_source.return_value = mock_source
            mock_instance.count_chunks_by_source.return_value = 1
            mock_instance.get_extractions_by_source.return_value = []
            mock_mongo.return_value = mock_instance

            response = client.get(
                "/sources/abc123",
                headers={"X-Project-ID": "header-project"},
            )

            assert response.status_code == 200
            # Project ID comes from source when available
            assert response.json()["project_id"] == "source-project"


# =============================================================================
# Test Error Handling
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_not_found_error(self, client):
        """Should return 404 for not found errors."""
        from src.exceptions import NotFoundError

        with patch("api.MongoDBClient") as mock_mongo:
            mock_instance = MagicMock()
            mock_instance.get_source.side_effect = NotFoundError("source", "abc123")
            mock_mongo.return_value = mock_instance

            response = client.get("/sources/abc123")

            assert response.status_code == 404
            data = response.json()
            assert data["error"]["code"] == "NOT_FOUND"
            assert "abc123" in data["error"]["message"]

    def test_validation_error(self, client):
        """Should return 400 for validation errors."""
        from src.exceptions import ValidationError

        with patch("api.MongoDBClient") as mock_mongo:
            mock_instance = MagicMock()
            mock_instance.get_source.side_effect = ValidationError(
                "Invalid source ID format",
                details={"id": "invalid"},
            )
            mock_mongo.return_value = mock_instance

            response = client.get("/sources/invalid")

            assert response.status_code == 400
            data = response.json()
            assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_internal_error(self, client):
        """Should return 500 for unexpected errors."""
        with patch("api.MongoDBClient") as mock_mongo:
            mock_instance = MagicMock()
            # The RuntimeError needs to be raised after connect() is called
            mock_instance.connect.return_value = None
            mock_instance.get_source.side_effect = RuntimeError("Unexpected error")
            mock_instance.close.return_value = None
            mock_mongo.return_value = mock_instance

            response = client.get("/sources/abc123")

            assert response.status_code == 500
            data = response.json()
            assert data["error"]["code"] == "INTERNAL_ERROR"


# =============================================================================
# Test Project Isolation
# =============================================================================


class TestProjectIsolation:
    """Tests for project namespace isolation."""

    def test_different_project_headers_passed_to_pipeline(self, client, tmp_path):
        """Should pass different project IDs to pipeline config."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        mock_result = MagicMock()
        mock_result.source_id = "abc"
        mock_result.title = "test"
        mock_result.chunk_count = 1
        mock_result.total_tokens = 10
        mock_result.duration = 0.1

        with patch("api.IngestionPipeline") as mock_pipeline:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.ingest.return_value = mock_result
            mock_pipeline.return_value = mock_instance

            # Test project-a
            with open(test_file, "rb") as f:
                response_a = client.post(
                    "/ingest",
                    files={"file": ("test.txt", f, "text/plain")},
                    headers={"X-Project-ID": "project-a"},
                )

            # Test project-b
            with open(test_file, "rb") as f:
                response_b = client.post(
                    "/ingest",
                    files={"file": ("test.txt", f, "text/plain")},
                    headers={"X-Project-ID": "project-b"},
                )

            assert response_a.json()["project_id"] == "project-a"
            assert response_b.json()["project_id"] == "project-b"

            # Verify PipelineConfig was created with correct project_id
            calls = mock_pipeline.call_args_list
            assert len(calls) == 2
            assert calls[0][1]["config"].project_id == "project-a"
            assert calls[1][1]["config"].project_id == "project-b"
