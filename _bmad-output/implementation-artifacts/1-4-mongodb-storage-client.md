# Story 1.4: MongoDB Storage Client

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want a MongoDB client class with CRUD operations for sources, chunks, and extractions,
So that I can persist and retrieve knowledge base data from MongoDB.

## Acceptance Criteria

**Given** MongoDB is running (from Story 1.2)
**When** I use the MongoDB client to create/read/update/delete documents
**Then** documents are properly stored in the correct collections (sources, chunks, extractions)
**And** compound indexes on `extractions.type + extractions.topics` are created
**And** the client uses Pydantic models (from Story 1.3) for validation
**And** errors follow the structured error format from architecture

## Dependency Analysis

**Depends On:**
- **Story 1.1** (Initialize Monorepo Structure) - MUST be completed first
  - Requires `packages/pipeline/` directory structure
  - Requires `pymongo` dependency installed
- **Story 1.2** (Docker Compose Infrastructure) - MUST be completed first
  - Requires MongoDB running on localhost:27017
  - Requires database `knowledge_db` accessible
- **Story 1.3** (Pydantic Models) - MUST be completed first
  - Requires `Source`, `Chunk`, `Extraction` Pydantic models
  - Requires ObjectId validation patterns

**Blocks:**
- **Story 1.5** (Qdrant Storage Client) - can proceed in parallel after this
- **Story 2.1** (Base Source Adapter Interface) - needs storage client for persistence
- **Story 2.6** (End-to-End Ingestion Pipeline) - needs storage client to save documents
- **Story 3.6** (Extraction Storage and Embedding) - needs storage client for extraction persistence

## Tasks / Subtasks

- [ ] **Task 1: Verify Prerequisites** (AC: Dependencies available)
  - [ ] Confirm Story 1.1 complete: `ls packages/pipeline/pyproject.toml`
  - [ ] Confirm Story 1.2 complete: `docker-compose ps` shows mongodb running
  - [ ] Confirm Story 1.3 complete: `from src.models import Source, Chunk, Extraction` works
  - [ ] Confirm pymongo installed: `cd packages/pipeline && uv run python -c "import pymongo; print(pymongo.version)"`

- [ ] **Task 2: Create Storage Module Structure** (AC: Module exists)
  - [ ] Create `packages/pipeline/src/storage/` directory
  - [ ] Create `packages/pipeline/src/storage/__init__.py`
  - [ ] Create `packages/pipeline/src/storage/mongodb.py`

- [ ] **Task 3: Create Exceptions Module** (AC: Error handling)
  - [ ] Create `packages/pipeline/src/exceptions.py`
  - [ ] Define `KnowledgeError` base exception with `code`, `message`, `details`
  - [ ] Define `NotFoundError` for missing resources
  - [ ] Define `StorageError` for database operation failures
  - [ ] Define `ValidationError` for data validation failures

- [ ] **Task 4: Create Configuration Module** (AC: Settings management)
  - [ ] Create `packages/pipeline/src/config.py`
  - [ ] Define `Settings` class using `pydantic_settings.BaseSettings`
  - [ ] Add `mongodb_uri: str = "mongodb://localhost:27017"` field
  - [ ] Add `mongodb_database: str = "knowledge_db"` field
  - [ ] Load from `.env` file
  - [ ] Export singleton: `settings = Settings()`

- [ ] **Task 5: Implement MongoDB Client Base** (AC: Client connects)
  - [ ] Create `MongoDBClient` class in `mongodb.py`
  - [ ] Implement `__init__(self, uri: str, database: str)` constructor
  - [ ] Store `_client: MongoClient` and `_db: Database` as instance variables
  - [ ] Implement `connect()` method to establish connection
  - [ ] Implement `close()` method to close connection
  - [ ] Implement `ping()` method to verify connection health
  - [ ] Implement context manager (`__enter__`, `__exit__`) for connection management

- [ ] **Task 6: Implement Index Creation** (AC: Compound indexes created)
  - [ ] Implement `_ensure_indexes()` private method
  - [ ] Create index on `sources.status` for status filtering
  - [ ] Create index on `chunks.source_id` for source-based queries
  - [ ] Create compound index on `extractions.type + extractions.topics` per architecture
  - [ ] Create index on `extractions.source_id` for source-based queries
  - [ ] Call `_ensure_indexes()` from `connect()` method
  - [ ] Use `create_index()` with `background=True` for non-blocking creation

- [ ] **Task 7: Implement Sources CRUD Operations** (AC: Sources stored correctly)
  - [ ] Implement `create_source(source: Source) -> str` - returns inserted ObjectId
  - [ ] Implement `get_source(source_id: str) -> Source` - raises NotFoundError if missing
  - [ ] Implement `update_source(source_id: str, updates: dict) -> Source` - partial update
  - [ ] Implement `delete_source(source_id: str) -> bool` - returns success status
  - [ ] Implement `list_sources(status: Optional[str] = None) -> list[Source]` - with optional filter
  - [ ] Use Pydantic `model_dump()` for MongoDB insertion
  - [ ] Use Pydantic `model_validate()` for document-to-model conversion

- [ ] **Task 8: Implement Chunks CRUD Operations** (AC: Chunks stored correctly)
  - [ ] Implement `create_chunk(chunk: Chunk) -> str` - returns inserted ObjectId
  - [ ] Implement `get_chunk(chunk_id: str) -> Chunk` - raises NotFoundError if missing
  - [ ] Implement `get_chunks_by_source(source_id: str) -> list[Chunk]` - all chunks for source
  - [ ] Implement `delete_chunks_by_source(source_id: str) -> int` - returns deleted count
  - [ ] Implement `count_chunks_by_source(source_id: str) -> int` - returns count
  - [ ] Use Pydantic models for validation

- [ ] **Task 9: Implement Extractions CRUD Operations** (AC: Extractions stored correctly)
  - [ ] Implement `create_extraction(extraction: Extraction) -> str` - returns inserted ObjectId
  - [ ] Implement `get_extraction(extraction_id: str) -> Extraction` - raises NotFoundError if missing
  - [ ] Implement `get_extractions_by_source(source_id: str) -> list[Extraction]` - all extractions for source
  - [ ] Implement `get_extractions_by_type(type: str, topics: Optional[list[str]] = None) -> list[Extraction]`
  - [ ] Implement `delete_extractions_by_source(source_id: str) -> int` - returns deleted count
  - [ ] Use Pydantic models for validation

- [ ] **Task 10: Implement Bulk Operations** (AC: Efficient batch processing)
  - [ ] Implement `create_chunks_bulk(chunks: list[Chunk]) -> list[str]` - batch insert
  - [ ] Implement `create_extractions_bulk(extractions: list[Extraction]) -> list[str]` - batch insert
  - [ ] Use `insert_many()` for efficient bulk operations
  - [ ] Handle partial failures appropriately

- [ ] **Task 11: Create Module Exports** (AC: Clean imports)
  - [ ] Export `MongoDBClient` from `packages/pipeline/src/storage/__init__.py`
  - [ ] Verify imports work: `from src.storage import MongoDBClient`

- [ ] **Task 12: Basic Client Tests** (AC: CRUD works)
  - [ ] Create `packages/pipeline/tests/test_storage/` directory
  - [ ] Create `packages/pipeline/tests/test_storage/conftest.py` with MongoDB fixtures
  - [ ] Create `packages/pipeline/tests/test_storage/test_mongodb.py`
  - [ ] Test connection/ping works
  - [ ] Test CRUD operations for each collection
  - [ ] Test error handling (NotFoundError, etc.)
  - [ ] Document test results in completion notes

## Dev Notes

### Architecture-Specified MongoDB Configuration

**From Architecture Document (architecture.md:260-310):**

```
knowledge_db/
├── sources           # Book/paper metadata
│   ├── _id
│   ├── type          # "book", "paper", "case_study"
│   ├── title
│   ├── authors[]
│   ├── path
│   ├── ingested_at
│   ├── status
│   └── metadata{}
│
├── chunks            # Raw text chunks
│   ├── _id
│   ├── source_id     # → sources._id
│   ├── content
│   ├── position      # {chapter, section, page}
│   ├── token_count
│   └── schema_version
│
└── extractions       # Structured knowledge
    ├── _id
    ├── source_id     # → sources._id (for "all from book X")
    ├── chunk_id      # → chunks._id (for context)
    ├── type          # "decision", "pattern", "warning", "methodology"...
    ├── content{}     # Type-specific structured data
    ├── topics[]
    ├── schema_version
    └── extracted_at
```

**CRITICAL:** These collection names and field structures are EXACT requirements.

### Required Indexes

**From Architecture Document (architecture.md:293-297):**

```python
# Indexes to create
indexes = [
    ("extractions", [("type", 1), ("topics", 1)]),  # Compound index
    ("extractions", [("source_id", 1)]),
    ("chunks", [("source_id", 1)]),
]
```

**Index naming convention:** `idx_{collection}_{field}` (e.g., `idx_extractions_type_topics`)

### Configuration Pattern

**From Architecture Document (architecture.md:519-533):**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "knowledge_db"
    qdrant_url: str = "http://localhost:6333"
    embedding_model: str = "all-MiniLM-L6-v2"
    environment: str = "local"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Error Handling Pattern

**From Architecture Document (architecture.md:545-559):**

```python
class KnowledgeError(Exception):
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

class NotFoundError(KnowledgeError):
    def __init__(self, resource: str, id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with id '{id}' not found",
            details={"resource": resource, "id": id}
        )

class StorageError(KnowledgeError):
    def __init__(self, operation: str, details: dict = None):
        super().__init__(
            code="STORAGE_ERROR",
            message=f"Storage operation '{operation}' failed",
            details=details or {}
        )
```

### Async Patterns Note

**From Architecture Document (architecture.md:505-517):**

```python
# FastAPI endpoints: ALWAYS async
# Storage clients: Sync is acceptable for pymongo (CPU-bound pattern)

# Pattern for MongoDB client (sync acceptable):
class MongoDBClient:
    """Sync MongoDB client - pymongo is not async-native."""

    def create_source(self, source: Source) -> str:
        # Sync method is OK for pymongo
        result = self._db.sources.insert_one(source.model_dump())
        return str(result.inserted_id)
```

**NOTE:** pymongo is not async-native. Use sync methods. The MCP server (which is async) will call these sync methods.

### File Location and Module Structure

**From Architecture Document (architecture.md:640-644):**

```
packages/pipeline/
├── src/
│   ├── __init__.py
│   ├── config.py              # <-- Settings class
│   ├── exceptions.py          # <-- Error classes
│   ├── storage/               # <-- YOUR WORK HERE
│   │   ├── __init__.py
│   │   ├── mongodb.py         # MongoDB client
│   │   └── qdrant.py          # Qdrant client (Story 1.5)
│   └── models/                # From Story 1.3
│       ├── source.py
│       ├── chunk.py
│       └── extraction.py
```

### Python Naming Conventions

**From Architecture Document (architecture.md:418-432):**

| Element | Convention | Example |
|---------|------------|---------|
| Files/modules | `snake_case.py` | `mongodb.py`, `config.py` |
| Classes | `PascalCase` | `MongoDBClient`, `Settings` |
| Functions | `snake_case` | `create_source()`, `get_chunk()` |
| Variables | `snake_case` | `source_id`, `chunk_count` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_DATABASE` |

### Logging Pattern

**From Architecture Document (architecture.md:535-542):**

```python
import structlog
logger = structlog.get_logger()

# Good: structured with context
logger.info("source_created", source_id=source_id, type=source.type)
logger.error("storage_failed", operation="create_source", error=str(e))
```

**NOTE:** Use structlog, not print statements.

### Pydantic Model Integration

**From Story 1.3 (Previous Story Intelligence):**

```python
# Converting Pydantic model to MongoDB document
def create_source(self, source: Source) -> str:
    doc = source.model_dump()
    # Handle _id vs id mapping
    doc["_id"] = ObjectId()  # Generate new ObjectId
    del doc["id"]  # Remove string id field
    result = self._db.sources.insert_one(doc)
    return str(result.inserted_id)

# Converting MongoDB document to Pydantic model
def get_source(self, source_id: str) -> Source:
    doc = self._db.sources.find_one({"_id": ObjectId(source_id)})
    if not doc:
        raise NotFoundError("source", source_id)
    # Handle _id vs id mapping
    doc["id"] = str(doc.pop("_id"))
    return Source.model_validate(doc)
```

**CRITICAL:** MongoDB uses `_id` (ObjectId), Pydantic uses `id` (string). Handle conversion.

### Reference Implementation Example

```python
# packages/pipeline/src/storage/mongodb.py
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from bson import ObjectId
import structlog

from src.models import Source, Chunk, Extraction
from src.exceptions import NotFoundError, StorageError
from src.config import settings

logger = structlog.get_logger()

class MongoDBClient:
    """MongoDB client for knowledge base storage operations."""

    def __init__(self, uri: str = None, database: str = None):
        self._uri = uri or settings.mongodb_uri
        self._database_name = database or settings.mongodb_database
        self._client: MongoClient = None
        self._db: Database = None

    def connect(self) -> None:
        """Establish connection to MongoDB and ensure indexes."""
        self._client = MongoClient(self._uri)
        self._db = self._client[self._database_name]
        self._ensure_indexes()
        logger.info("mongodb_connected", database=self._database_name)

    def close(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            logger.info("mongodb_disconnected")

    def ping(self) -> bool:
        """Verify connection health."""
        try:
            self._client.admin.command('ping')
            return True
        except Exception:
            return False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def _ensure_indexes(self) -> None:
        """Create required indexes for all collections."""
        # Sources indexes
        self._db.sources.create_index(
            [("status", ASCENDING)],
            name="idx_sources_status",
            background=True
        )

        # Chunks indexes
        self._db.chunks.create_index(
            [("source_id", ASCENDING)],
            name="idx_chunks_source_id",
            background=True
        )

        # Extractions indexes
        self._db.extractions.create_index(
            [("type", ASCENDING), ("topics", ASCENDING)],
            name="idx_extractions_type_topics",
            background=True
        )
        self._db.extractions.create_index(
            [("source_id", ASCENDING)],
            name="idx_extractions_source_id",
            background=True
        )
        logger.info("mongodb_indexes_ensured")

    # Sources CRUD
    def create_source(self, source: Source) -> str:
        """Create a new source document."""
        doc = source.model_dump()
        doc["_id"] = ObjectId()
        if "id" in doc:
            del doc["id"]
        result = self._db.sources.insert_one(doc)
        source_id = str(result.inserted_id)
        logger.info("source_created", source_id=source_id, type=source.type)
        return source_id

    def get_source(self, source_id: str) -> Source:
        """Get a source by ID."""
        doc = self._db.sources.find_one({"_id": ObjectId(source_id)})
        if not doc:
            raise NotFoundError("source", source_id)
        doc["id"] = str(doc.pop("_id"))
        return Source.model_validate(doc)

    # ... more methods following same pattern
```

### Testing Pattern

**From Architecture Document (architecture.md:456-462):**

```
packages/pipeline/
├── src/
│   └── storage/
│       └── mongodb.py
└── tests/
    └── test_storage/
        ├── conftest.py
        └── test_mongodb.py
```

**Test fixtures example:**
```python
# packages/pipeline/tests/test_storage/conftest.py
import pytest
from src.storage import MongoDBClient

@pytest.fixture
def mongodb_client():
    """Provide a MongoDB client for testing."""
    client = MongoDBClient()
    client.connect()
    yield client
    # Cleanup: drop test collections
    client._db.sources.delete_many({})
    client._db.chunks.delete_many({})
    client._db.extractions.delete_many({})
    client.close()
```

### Docker Compose Reference

**From Story 1.2 (Previous Story Intelligence):**

MongoDB is available at:
- Host: `localhost`
- Port: `27017`
- Database: `knowledge_db`
- No authentication (local development)

### Project Structure Notes

- Alignment with unified project structure: Files go in `packages/pipeline/src/storage/`
- Naming follows `snake_case.py` convention
- Classes follow `PascalCase` convention
- Tests mirror src structure in `tests/test_storage/`

### References

- [Source: architecture.md#Data-Architecture] - MongoDB collection structure
- [Source: architecture.md#Implementation-Patterns-&-Consistency-Rules] - Naming and patterns
- [Source: architecture.md#Project-Structure-&-Boundaries] - File locations
- [Source: 1-3-pydantic-models-for-core-entities.md] - Pydantic model patterns
- [Source: project-context.md#Technology-Stack-&-Versions] - pymongo version
- [Source: project-context.md#Critical-Implementation-Rules] - Error handling pattern

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

_To be filled by dev agent - list all files created/modified:_
- packages/pipeline/src/config.py (CREATE)
- packages/pipeline/src/exceptions.py (CREATE)
- packages/pipeline/src/storage/__init__.py (CREATE)
- packages/pipeline/src/storage/mongodb.py (CREATE)
- packages/pipeline/tests/test_storage/conftest.py (CREATE)
- packages/pipeline/tests/test_storage/test_mongodb.py (CREATE)
