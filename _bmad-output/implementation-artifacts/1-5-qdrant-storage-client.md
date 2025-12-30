# Story 1.5: Qdrant Storage Client

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want a Qdrant client class for vector storage and semantic search operations,
So that I can store embeddings and perform similarity searches on chunks and extractions.

## Acceptance Criteria

**Given** Qdrant is running (from Story 1.2)
**When** I use the Qdrant client to create collections and upsert vectors
**Then** collections are created with 384d vectors and Cosine distance metric
**And** payload fields include `{source_id, chunk_id, type, topics}` for filtering
**And** semantic search returns ranked results with scores
**And** both `chunks` and `extractions` collections are supported

## Dependency Analysis

**Depends On:**
- **Story 1.1** (Initialize Monorepo Structure) - MUST be completed first
  - Requires `packages/pipeline/` directory structure
  - Requires `qdrant-client` dependency installed
- **Story 1.2** (Docker Compose Infrastructure Setup) - MUST be completed first
  - Requires Qdrant running on port 6333
  - Required for integration testing
- **Story 1.3** (Pydantic Models for Core Entities) - MUST be completed first
  - Requires `Chunk` and `Extraction` Pydantic models for type-safe operations
  - Required for validating stored/retrieved data

**Blocks:**
- **Story 2.4** (Text Chunking Processor) - needs Qdrant to store chunk vectors
- **Story 2.5** (Local Embedding Generator) - needs Qdrant collections to store vectors
- **Story 2.6** (End-to-End Ingestion Pipeline) - needs both storage clients
- **Story 3.6** (Extraction Storage and Embedding) - needs Qdrant for extraction vectors
- **Story 4.2** (Semantic Search Tool) - needs Qdrant client for vector search

**Related Story:**
- **Story 1.4** (MongoDB Storage Client) - parallel implementation; follows same pattern

## Tasks / Subtasks

- [x] **Task 1: Verify Prerequisites** (AC: All dependencies available)
  - [x] Confirm Story 1.1 complete: `ls packages/pipeline/pyproject.toml`
  - [x] Confirm Story 1.2 complete: `docker-compose ps` shows Qdrant running
  - [x] Confirm Story 1.3 complete: `from src.models import Chunk, Extraction` works
  - [x] Confirm qdrant-client installed: `cd packages/pipeline && uv run python -c "from qdrant_client import QdrantClient; print('OK')"`
  - [x] Verify Qdrant accessible: `curl http://localhost:6333/collections`

- [x] **Task 2: Create Storage Directory Structure** (AC: Module exists)
  - [x] Create `packages/pipeline/src/storage/` directory (if not exists)
  - [x] Create `packages/pipeline/src/storage/__init__.py`
  - [x] Create `packages/pipeline/src/storage/qdrant.py`

- [x] **Task 3: Implement Configuration** (AC: Settings pattern followed)
  - [x] Add Qdrant settings to config module or `packages/pipeline/src/config.py`
  - [x] Include `qdrant_url: str = "http://localhost:6333"` setting
  - [x] Include `qdrant_grpc_port: int = 6334` setting (optional, for gRPC mode)
  - [x] Use `pydantic_settings.BaseSettings` pattern per architecture

- [x] **Task 4: Implement QdrantClient Wrapper** (AC: Client class exists)
  - [x] Create `QdrantStorageClient` class
  - [x] Implement `__init__` with connection to Qdrant
  - [x] Handle connection errors gracefully with structured error format
  - [x] Implement lazy initialization or connection pooling pattern
  - [x] Add health check method: `async def health_check() -> bool`

- [x] **Task 5: Implement Collection Management** (AC: 384d vectors, Cosine distance)
  - [x] Implement `ensure_collection(collection_name: str)` method
  - [x] Configure vector size: 384 dimensions (all-MiniLM-L6-v2 output)
  - [x] Configure distance metric: Cosine
  - [x] Create `chunks` collection with proper configuration
  - [x] Create `extractions` collection with proper configuration
  - [x] Handle "collection already exists" gracefully (no error, just continue)

- [x] **Task 6: Implement Vector Upsert Operations** (AC: Upsert vectors)
  - [x] Implement `upsert_chunk_vector(chunk_id: str, vector: list[float], payload: dict)` method
  - [x] Implement `upsert_extraction_vector(extraction_id: str, vector: list[float], payload: dict)` method
  - [x] Validate vector dimensionality (must be 384)
  - [x] Payload must include: `{source_id, chunk_id, type, topics}` per architecture
  - [x] Implement batch upsert: `upsert_vectors_batch(collection: str, points: list[PointStruct])`

- [x] **Task 7: Implement Semantic Search** (AC: Ranked results with scores)
  - [x] Implement `search(collection: str, query_vector: list[float], limit: int = 10)` method
  - [x] Return results ranked by similarity score
  - [x] Include payload data in results
  - [x] Implement filtered search: `search_with_filter(collection, vector, filter_dict, limit)`
  - [x] Support filtering by: `source_id`, `type`, `topics`

- [x] **Task 8: Implement Delete Operations** (AC: Cleanup support)
  - [x] Implement `delete_by_id(collection: str, point_id: str)` method
  - [x] Implement `delete_by_source(collection: str, source_id: str)` method
  - [x] Support batch delete operations
  - [x] Handle non-existent points gracefully

- [x] **Task 9: Implement Error Handling** (AC: Structured errors)
  - [x] Create Qdrant-specific exception classes inheriting from `KnowledgeError`
  - [x] Implement `QdrantConnectionError` for connection failures
  - [x] Implement `QdrantCollectionError` for collection operations
  - [x] Implement `QdrantVectorError` for invalid vector operations
  - [x] All errors follow structured format: `{code, message, details}`

- [x] **Task 10: Create Module Exports** (AC: Clean imports)
  - [x] Export `QdrantStorageClient` from `packages/pipeline/src/storage/__init__.py`
  - [x] Verify imports work: `from src.storage import QdrantStorageClient`
  - [x] Export any helper types/classes needed

- [x] **Task 11: Integration Tests** (AC: Both collections supported)
  - [x] Test connection to local Qdrant
  - [x] Test collection creation for `chunks` and `extractions`
  - [x] Test vector upsert with valid 384d vector
  - [x] Test vector upsert rejects non-384d vectors
  - [x] Test semantic search returns ranked results
  - [x] Test filtered search works correctly
  - [x] Test delete operations work correctly
  - [x] Document test results in completion notes

## Dev Notes

### Qdrant Configuration Requirements

**From Architecture Document (architecture.md:299-306):**

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Vector size | 384 | all-MiniLM-L6-v2 output |
| Distance metric | Cosine | Standard for text embeddings |
| Collection: `chunks` | Semantic search on raw text |
| Collection: `extractions` | Semantic search on extraction summaries |
| Payload | `{source_id, chunk_id, type, topics}` | For filtered search |

**CRITICAL:** These are EXACT requirements from the architecture. Do NOT deviate.

### Qdrant Connection Details

**From Architecture Document (architecture.md:523-533):**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    qdrant_url: str = "http://localhost:6333"
    embedding_model: str = "all-MiniLM-L6-v2"
    environment: str = "local"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Docker Compose (from Story 1.2):**
- Qdrant REST port: `6333`
- Qdrant gRPC port: `6334`
- Volume: `qdrant_data:/qdrant/storage`

### Qdrant Client Pattern

**Reference Implementation (based on architecture patterns):**

```python
# packages/pipeline/src/storage/qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from typing import Optional
import structlog

from src.config import settings
from src.exceptions import QdrantConnectionError, QdrantVectorError

logger = structlog.get_logger()

# Constants from architecture
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension
DISTANCE_METRIC = Distance.COSINE

# Collection names from architecture
CHUNKS_COLLECTION = "chunks"
EXTRACTIONS_COLLECTION = "extractions"


class QdrantStorageClient:
    """Qdrant client for vector storage and semantic search operations."""

    def __init__(self, url: str = None):
        """Initialize Qdrant client with connection to Qdrant server.

        Args:
            url: Qdrant server URL. Defaults to settings.qdrant_url.
        """
        self.url = url or settings.qdrant_url
        try:
            self.client = QdrantClient(url=self.url)
            logger.info("qdrant_client_initialized", url=self.url)
        except Exception as e:
            raise QdrantConnectionError(
                code="QDRANT_CONNECTION_FAILED",
                message=f"Failed to connect to Qdrant at {self.url}",
                details={"url": self.url, "error": str(e)}
            )

    def ensure_collection(self, collection_name: str) -> None:
        """Create collection if it doesn't exist.

        Args:
            collection_name: Name of the collection to create/verify.
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=DISTANCE_METRIC,
                    ),
                )
                logger.info("qdrant_collection_created", collection=collection_name)
            else:
                logger.debug("qdrant_collection_exists", collection=collection_name)
        except Exception as e:
            raise QdrantConnectionError(
                code="QDRANT_COLLECTION_ERROR",
                message=f"Failed to ensure collection {collection_name}",
                details={"collection": collection_name, "error": str(e)}
            )

    def upsert_vector(
        self,
        collection: str,
        point_id: str,
        vector: list[float],
        payload: dict,
    ) -> None:
        """Upsert a single vector into a collection.

        Args:
            collection: Target collection name.
            point_id: Unique identifier for the point.
            vector: 384-dimensional embedding vector.
            payload: Metadata payload (source_id, chunk_id, type, topics).
        """
        if len(vector) != VECTOR_SIZE:
            raise QdrantVectorError(
                code="INVALID_VECTOR_SIZE",
                message=f"Vector must be {VECTOR_SIZE} dimensions, got {len(vector)}",
                details={"expected": VECTOR_SIZE, "actual": len(vector)}
            )

        self.client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        logger.debug("vector_upserted", collection=collection, point_id=point_id)

    def search(
        self,
        collection: str,
        query_vector: list[float],
        limit: int = 10,
        filter_conditions: Optional[dict] = None,
    ) -> list[dict]:
        """Perform semantic search on a collection.

        Args:
            collection: Target collection name.
            query_vector: 384-dimensional query embedding.
            limit: Maximum number of results to return.
            filter_conditions: Optional filter dict (e.g., {"type": "decision"}).

        Returns:
            List of results with scores and payloads.
        """
        if len(query_vector) != VECTOR_SIZE:
            raise QdrantVectorError(
                code="INVALID_VECTOR_SIZE",
                message=f"Query vector must be {VECTOR_SIZE} dimensions",
                details={"expected": VECTOR_SIZE, "actual": len(query_vector)}
            )

        # Build filter if conditions provided
        qdrant_filter = None
        if filter_conditions:
            must_conditions = []
            for key, value in filter_conditions.items():
                if isinstance(value, list):
                    # Handle topics[] - match any in list
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                else:
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
            qdrant_filter = Filter(must=must_conditions)

        results = self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit,
            query_filter=qdrant_filter,
        )

        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload,
            }
            for result in results
        ]

    def delete_by_id(self, collection: str, point_id: str) -> None:
        """Delete a point by ID."""
        self.client.delete(
            collection_name=collection,
            points_selector=[point_id],
        )
        logger.debug("point_deleted", collection=collection, point_id=point_id)

    def delete_by_source(self, collection: str, source_id: str) -> None:
        """Delete all points for a given source."""
        self.client.delete(
            collection_name=collection,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source_id",
                        match=MatchValue(value=source_id),
                    )
                ]
            ),
        )
        logger.info("points_deleted_by_source", collection=collection, source_id=source_id)

    async def health_check(self) -> bool:
        """Check if Qdrant is healthy and accessible."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
```

### Payload Schema Requirements

**From Architecture Document (architecture.md:306):**

All vectors MUST include these payload fields:

| Field | Type | Purpose |
|-------|------|---------|
| `source_id` | str | Reference to MongoDB sources._id |
| `chunk_id` | str | Reference to MongoDB chunks._id (for chunks) |
| `type` | str | Extraction type (for extractions only) |
| `topics` | list[str] | Topic tags for filtering |

**For chunks collection:**
```python
payload = {
    "source_id": "507f1f77bcf86cd799439011",
    "chunk_id": "507f1f77bcf86cd799439012",  # Same as point_id
}
```

**For extractions collection:**
```python
payload = {
    "source_id": "507f1f77bcf86cd799439011",
    "chunk_id": "507f1f77bcf86cd799439012",
    "type": "decision",  # or pattern, warning, methodology, etc.
    "topics": ["rag", "embeddings", "vector-search"],
}
```

### Exception Classes Pattern

**From Architecture Document (architecture.md:550-560):**

```python
# packages/pipeline/src/exceptions.py (add to existing file)

class KnowledgeError(Exception):
    """Base exception for all knowledge pipeline errors."""
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class QdrantConnectionError(KnowledgeError):
    """Raised when Qdrant connection fails."""
    pass


class QdrantVectorError(KnowledgeError):
    """Raised when vector operations fail (wrong dimensions, etc.)."""
    pass


class QdrantCollectionError(KnowledgeError):
    """Raised when collection operations fail."""
    pass
```

### File Location and Module Structure

**From Architecture Document (architecture.md:640-645):**

```
packages/pipeline/
├── src/
│   ├── __init__.py
│   ├── config.py              # Settings (add qdrant_url here)
│   ├── exceptions.py          # Add Qdrant exceptions
│   ├── models/                # From Story 1.3
│   │   ├── __init__.py
│   │   ├── source.py
│   │   ├── chunk.py
│   │   └── extraction.py
│   └── storage/               # <-- YOUR WORK HERE
│       ├── __init__.py
│       ├── mongodb.py         # From Story 1.4
│       └── qdrant.py          # CREATE THIS
```

### Previous Story Intelligence

**From Story 1.1 (Monorepo Structure):**
- Directory structure: `packages/pipeline/src/`
- `qdrant-client` dependency installed
- Python version: 3.11+
- Package manager: `uv`

**From Story 1.2 (Docker Compose):**
- Qdrant available at `http://localhost:6333`
- gRPC port at `6334`
- Volume persists data at `/qdrant/storage`

**From Story 1.3 (Pydantic Models):**
- `Chunk` model with fields: `id`, `source_id`, `content`, `position`, `token_count`, `schema_version`
- `Extraction` model with fields: `id`, `source_id`, `chunk_id`, `type`, `content`, `topics`, `schema_version`, `extracted_at`
- MongoDB ObjectId validation: 24 hex character pattern
- All models serialize to snake_case JSON

**From Story 1.4 (MongoDB Storage Client - parallel story):**
- Same pattern: Storage client class with CRUD operations
- Same exception pattern: Inherit from `KnowledgeError`
- Same config pattern: `pydantic_settings.BaseSettings`
- Same logging pattern: `structlog`

### Architecture Compliance Checklist

**From Architecture Document:**

- [ ] Vector size is exactly 384 dimensions (architecture.md:299)
- [ ] Distance metric is Cosine (architecture.md:300)
- [ ] Collections named `chunks` and `extractions` (architecture.md:303-304)
- [ ] Payload includes `{source_id, chunk_id, type, topics}` (architecture.md:306)
- [ ] Uses `pydantic_settings.BaseSettings` for config (architecture.md:520-533)
- [ ] Uses structured logging with structlog (architecture.md:536-541)
- [ ] Exceptions inherit from `KnowledgeError` (architecture.md:546-560)
- [ ] Error format: `{code, message, details}` (architecture.md:478-488)
- [ ] Files in `packages/pipeline/src/storage/` (architecture.md:644)
- [ ] Class naming: PascalCase `QdrantStorageClient` (architecture.md:424)
- [ ] File naming: snake_case `qdrant.py` (architecture.md:419)

### Testing Pattern

**From Architecture Document (architecture.md:456-462):**

Tests mirror src/ structure:
```
packages/pipeline/
├── src/
│   └── storage/
│       └── qdrant.py
└── tests/
    └── test_storage/
        ├── conftest.py
        └── test_qdrant.py
```

**Test file naming:** `test_qdrant.py`

**Integration test example:**
```python
# packages/pipeline/tests/test_storage/test_qdrant.py
import pytest
from src.storage import QdrantStorageClient

# Requires running Qdrant instance (docker-compose up -d)
@pytest.fixture
def qdrant_client():
    return QdrantStorageClient()

def test_connection(qdrant_client):
    """Test Qdrant connection is successful."""
    assert qdrant_client.health_check() is True

def test_ensure_chunks_collection(qdrant_client):
    """Test chunks collection creation."""
    qdrant_client.ensure_collection("chunks")
    collections = qdrant_client.client.get_collections().collections
    assert any(c.name == "chunks" for c in collections)

def test_upsert_and_search(qdrant_client):
    """Test vector upsert and semantic search."""
    # Create collection
    qdrant_client.ensure_collection("test_collection")

    # Create a 384d test vector
    test_vector = [0.1] * 384
    test_payload = {
        "source_id": "507f1f77bcf86cd799439011",
        "chunk_id": "507f1f77bcf86cd799439012",
    }

    # Upsert
    qdrant_client.upsert_vector(
        collection="test_collection",
        point_id="test_point_1",
        vector=test_vector,
        payload=test_payload,
    )

    # Search
    results = qdrant_client.search(
        collection="test_collection",
        query_vector=test_vector,
        limit=1,
    )

    assert len(results) == 1
    assert results[0]["id"] == "test_point_1"
    assert results[0]["score"] > 0.99  # Should be very similar
    assert results[0]["payload"]["source_id"] == "507f1f77bcf86cd799439011"

def test_invalid_vector_size_rejected(qdrant_client):
    """Test that non-384d vectors are rejected."""
    from src.exceptions import QdrantVectorError

    qdrant_client.ensure_collection("test_collection")

    wrong_size_vector = [0.1] * 256  # Wrong size

    with pytest.raises(QdrantVectorError) as exc_info:
        qdrant_client.upsert_vector(
            collection="test_collection",
            point_id="bad_point",
            vector=wrong_size_vector,
            payload={"source_id": "test"},
        )

    assert exc_info.value.code == "INVALID_VECTOR_SIZE"
    assert exc_info.value.details["expected"] == 384
    assert exc_info.value.details["actual"] == 256
```

### Success Validation

**Story is COMPLETE when:**
- [ ] `packages/pipeline/src/storage/__init__.py` exists and exports `QdrantStorageClient`
- [ ] `packages/pipeline/src/storage/qdrant.py` implements all required methods
- [ ] `ensure_collection()` creates 384d Cosine collections
- [ ] `upsert_vector()` stores vectors with proper payload
- [ ] `upsert_vector()` rejects non-384d vectors with `QdrantVectorError`
- [ ] `search()` returns ranked results with scores and payloads
- [ ] `search()` supports filtering by source_id, type, topics
- [ ] `delete_by_id()` removes individual points
- [ ] `delete_by_source()` removes all points for a source
- [ ] Exception classes created: `QdrantConnectionError`, `QdrantVectorError`, `QdrantCollectionError`
- [ ] All exceptions follow structured error format
- [ ] Config uses `pydantic_settings.BaseSettings` pattern
- [ ] Logging uses `structlog` (no print statements)
- [ ] Integration tests pass with running Qdrant

### Known Issues & Decisions

**Issue 1: Sync vs Async Client**
- **Impact:** Qdrant client has both sync and async modes
- **Decision:** Use sync client for pipeline (batch operations); MCP server may use async
- **Validation:** Document sync usage in docstrings

**Issue 2: Point ID Format**
- **Impact:** Qdrant accepts string or int IDs
- **Decision:** Use string IDs (MongoDB ObjectId format) for consistency
- **Validation:** Use UUID or ObjectId-compatible strings

**Issue 3: Batch Upsert Size**
- **Impact:** Large batches may timeout or fail
- **Decision:** Implement optional batching with configurable batch size
- **Validation:** Default to 100 points per batch, configurable via settings

**Issue 4: Collection Recreation**
- **Impact:** Changing vector config requires collection deletion
- **Decision:** `ensure_collection` only creates if missing; manual migration for config changes
- **Validation:** Document in error message if config mismatch detected

### Performance Considerations

**From Architecture NFR1 (<500ms search latency):**
- Keep collections indexed properly
- Use payload indexes for frequently filtered fields
- Consider gRPC port (6334) for high-throughput operations
- Batch upserts for ingestion efficiency

**Payload Index Recommendation:**
```python
# Create payload index for filtered search performance
self.client.create_payload_index(
    collection_name="extractions",
    field_name="type",
    field_schema="keyword",
)
self.client.create_payload_index(
    collection_name="extractions",
    field_name="topics",
    field_schema="keyword",
)
```

### Project Structure Notes

- File location: `packages/pipeline/src/storage/qdrant.py`
- Aligned with architecture: `packages/pipeline/` contains all batch processing code
- Storage module: Contains both MongoDB (1.4) and Qdrant (this story) clients
- Shared exceptions: `packages/pipeline/src/exceptions.py`

### References

- [Source: architecture.md#Qdrant-Configuration] - Vector configuration (lines 299-306)
- [Source: architecture.md#Settings-Pattern] - Configuration pattern (lines 520-533)
- [Source: architecture.md#Error-Handling-Pattern] - Exception pattern (lines 546-560)
- [Source: architecture.md#Logging-Pattern] - Structured logging (lines 536-541)
- [Source: epics.md#Story-1.5] - Story acceptance criteria (lines 244-258)
- [Source: project-context.md#Technology-Stack] - Qdrant version requirements
- [Source: Story 1.3] - Pydantic models for Chunk and Extraction
- [Source: Story 1.4] - MongoDB client pattern reference

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Initial implementation had to handle Qdrant point ID format requirements (UUIDs or integers only)
- Implemented deterministic UUID conversion using `uuid.uuid5()` for string IDs
- Updated search API from deprecated `search()` to `query_points()` method in newer qdrant-client

### Completion Notes List

**All 11 tasks completed successfully:**

1. ✅ Prerequisites verified: Story 1.1, 1.2, 1.3 complete; qdrant-client installed; Qdrant accessible
2. ✅ Storage directory structure exists (from Story 1.4)
3. ✅ Configuration added: `qdrant_grpc_port: int = 6334` to settings
4. ✅ QdrantStorageClient class implemented with connection handling
5. ✅ Collection management: `ensure_collection()` creates 384d Cosine collections, idempotent
6. ✅ Vector upsert: `upsert_chunk_vector()`, `upsert_extraction_vector()`, batch upsert with validation
7. ✅ Semantic search: `search()` and `search_with_filter()` with ranked results and payload filtering
8. ✅ Delete operations: `delete_by_id()`, `delete_by_source()`, `delete_batch()`
9. ✅ Error handling: `QdrantConnectionError`, `QdrantCollectionError`, `QdrantVectorError` exceptions
10. ✅ Module exports: `QdrantStorageClient`, `VECTOR_SIZE`, `DISTANCE_METRIC`, `CHUNKS_COLLECTION`, `EXTRACTIONS_COLLECTION`
11. ✅ Integration tests: 22 tests covering all functionality, all passing

**Test Results:**
```
tests/test_storage/test_qdrant.py ...................... [100%]
======================== 22 passed, 1 warning in 2.11s ========================
```

**Full Suite Regression:**
```
======================== 117 passed, 1 warning in 2.60s ========================
```

**Key Implementation Details:**
- Used UUID5 (deterministic) for point ID conversion to ensure consistent mapping between string IDs and Qdrant UUIDs
- Original string IDs stored in `_original_id` payload field for retrieval
- Updated to use `query_points()` API (newer qdrant-client replaces deprecated `search()`)
- Vector validation before Qdrant API calls to provide clear error messages
- Structured error format: `{code, message, details}` as per architecture

### File List

**Created:**
- `packages/pipeline/src/storage/qdrant.py` - QdrantStorageClient implementation (~517 lines)
- `packages/pipeline/tests/test_storage/test_qdrant.py` - Integration tests (486 lines, 22 tests)

**Updated:**
- `packages/pipeline/src/storage/__init__.py` - Added Qdrant exports
- `packages/pipeline/src/exceptions.py` - Added QdrantConnectionError, QdrantCollectionError, QdrantVectorError
- `packages/pipeline/src/config.py` - Added qdrant_grpc_port setting, fixed Pydantic v2 deprecation
- `packages/pipeline/tests/test_storage/conftest.py` - Added Qdrant fixtures, improved cleanup

### Code Review Record

**Reviewer:** Claude Opus 4.5 (Adversarial Code Review)
**Date:** 2025-12-30
**Issues Found:** 2 HIGH, 4 MEDIUM, 2 LOW

**Fixes Applied:**

| Issue | Severity | Fix |
|-------|----------|-----|
| Redundant `UnexpectedResponse` exception handling | HIGH | Removed duplicate catch block in `ensure_collection` |
| Pydantic `class Config` deprecation | HIGH | Updated to `SettingsConfigDict` pattern |
| Missing payload indexes for NFR1 | MEDIUM | Added `_create_payload_indexes()` for type/topics/source_id |
| Async `health_check` with sync call | MEDIUM | Changed to sync method for consistency |
| Test fixture missing real collection cleanup | MEDIUM | Added chunks/extractions to cleanup list |

**Post-Review Test Results:**
```
tests/test_storage/test_qdrant.py ...................... [100%]
======================== 22 passed in 2.11s ========================
```

**Not Fixed (LOW priority):**
- Tests use `_upsert_vector` private method directly (refactoring risk)
- Completion notes 117 vs 22 test count clarification (documentation only)
