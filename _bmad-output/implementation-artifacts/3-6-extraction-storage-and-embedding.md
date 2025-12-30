# Story 3.6: Extraction Storage and Embedding

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want extractions to be stored in MongoDB and embedded in Qdrant,
So that they can be queried both by type/topic filters and semantic search.

## Acceptance Criteria

**Given** a completed extraction
**When** it is saved
**Then** the extraction document is stored in MongoDB `extractions` collection
**And** an embedding is generated from the extraction summary
**And** the embedding is stored in Qdrant `extractions` collection with payload `{source_id, chunk_id, type, topics}`
**And** source attribution chain is preserved (extraction -> chunk -> source)

## Tasks / Subtasks

- [ ] **Task 1: Verify Prerequisites** (AC: All dependencies available)
  - [ ] 1.1: Confirm Story 1.4 complete (MongoDB client exists): `ls packages/pipeline/src/storage/mongodb.py`
  - [ ] 1.2: Confirm Story 1.5 complete (Qdrant client exists): `ls packages/pipeline/src/storage/qdrant.py`
  - [ ] 1.3: Confirm Story 2.5 complete (Embedding generator exists): `ls packages/pipeline/src/embeddings/local_embedder.py`
  - [ ] 1.4: Confirm Story 3.1 complete (Extraction models exist): `cd packages/pipeline && uv run python -c "from src.extractors import Decision, Pattern, Warning, ExtractionBase; print('OK')"`
  - [ ] 1.5: Verify MongoDB `extractions` collection can be created
  - [ ] 1.6: Verify Qdrant `extractions` collection can be created

- [ ] **Task 2: Create Extraction Summary Generator** (AC: #2)
  - [ ] 2.1: Create utility function `generate_extraction_summary(extraction: ExtractionBase) -> str`
  - [ ] 2.2: Handle Decision extractions: combine question + recommended_approach
  - [ ] 2.3: Handle Pattern extractions: combine name + problem + solution
  - [ ] 2.4: Handle Warning extractions: combine title + description
  - [ ] 2.5: Handle Methodology/Checklist/Persona/Workflow extractions: combine relevant fields
  - [ ] 2.6: Ensure summary is concise (<500 chars) for embedding efficiency
  - [ ] 2.7: Add to `packages/pipeline/src/extractors/utils.py` or similar

- [ ] **Task 3: Extend MongoDB Client for Extractions** (AC: #1, #4)
  - [ ] 3.1: Add `save_extraction(extraction: ExtractionBase)` method to MongoDB client
  - [ ] 3.2: Serialize extraction to dict using Pydantic `.model_dump()`
  - [ ] 3.3: Insert into `extractions` collection
  - [ ] 3.4: Verify `source_id` and `chunk_id` fields are preserved
  - [ ] 3.5: Verify `type`, `topics`, and `schema_version` fields are stored
  - [ ] 3.6: Return inserted extraction ID
  - [ ] 3.7: Handle duplicate extraction prevention (check by chunk_id + type)

- [ ] **Task 4: Extend Qdrant Client for Extraction Embeddings** (AC: #3, #4)
  - [ ] 4.1: Add `upsert_extraction_embedding(extraction_id: str, embedding: list[float], payload: dict)` method
  - [ ] 4.2: Construct payload with fields: `{source_id, chunk_id, type, topics, extraction_id}`
  - [ ] 4.3: Upsert vector to Qdrant `extractions` collection
  - [ ] 4.4: Verify 384-dimensional vector constraint
  - [ ] 4.5: Verify Cosine distance metric is used
  - [ ] 4.6: Handle upsert errors gracefully

- [ ] **Task 5: Create Extraction Storage Service** (AC: All)
  - [ ] 5.1: Create `packages/pipeline/src/storage/extraction_storage.py`
  - [ ] 5.2: Implement `ExtractionStorage` class integrating MongoDB + Qdrant + Embedder
  - [ ] 5.3: Implement `save_extraction(extraction: ExtractionBase)` orchestration method:
    - Generate summary using Task 2 utility
    - Generate embedding using local embedder (Story 2.5)
    - Save to MongoDB (Task 3)
    - Save embedding to Qdrant (Task 4)
    - Return success status with IDs
  - [ ] 5.4: Add error handling for partial failures (MongoDB succeeds, Qdrant fails)
  - [ ] 5.5: Add structured logging for all operations
  - [ ] 5.6: Validate extraction before saving (required fields present)

- [ ] **Task 6: Update Extractor Base Class** (AC: Integration)
  - [ ] 6.1: Add optional `storage: ExtractionStorage` parameter to `BaseExtractor.__init__()`
  - [ ] 6.2: Update `extract()` method to optionally auto-save extractions if storage provided
  - [ ] 6.3: Preserve backward compatibility (storage=None means no auto-save)
  - [ ] 6.4: Log storage operations in structured format

- [ ] **Task 7: Create Integration Tests** (AC: All)
  - [ ] 7.1: Create `packages/pipeline/tests/test_storage/test_extraction_storage.py`
  - [ ] 7.2: Test Decision extraction storage (MongoDB + Qdrant)
  - [ ] 7.3: Test Pattern extraction storage
  - [ ] 7.4: Test Warning extraction storage
  - [ ] 7.5: Test source attribution preservation (query MongoDB by extraction_id, verify source_id and chunk_id)
  - [ ] 7.6: Test Qdrant payload accuracy (query by type, verify results match)
  - [ ] 7.7: Test Qdrant payload filtering (query by topics, verify filtering works)
  - [ ] 7.8: Test summary generation for all extraction types
  - [ ] 7.9: Test embedding dimension validation (384d)
  - [ ] 7.10: Test error handling (MongoDB failure, Qdrant failure)

- [ ] **Task 8: Create Unit Tests** (AC: Individual components)
  - [ ] 8.1: Test extraction summary generator for all types
  - [ ] 8.2: Test MongoDB save_extraction method
  - [ ] 8.3: Test Qdrant upsert_extraction_embedding method
  - [ ] 8.4: Test ExtractionStorage orchestration
  - [ ] 8.5: Test partial failure scenarios

## Dev Notes

### Critical Implementation Context

**Core Philosophy:** Extractions are for NAVIGATION, Claude is for SYNTHESIS. This story creates the dual-store architecture that enables:
1. **Structured querying** via MongoDB (filter by type, topic, source)
2. **Semantic search** via Qdrant (find similar extractions across sources)
3. **Source attribution** for every extraction back to original chunk and source

**Why This Matters:** The MCP server (Epic 4) will use both stores:
- Qdrant finds semantically similar extractions
- MongoDB enriches results with full extraction details and filters by type/topic
- Claude synthesizes across multiple sources at query time

### Architectural Foundation

This story implements the **hybrid storage model** defined in architecture:

```
Extraction Created (Story 3.1-3.5)
         │
         ▼
  ┌──────────────────────────────────────┐
  │   ExtractionStorage (THIS STORY)     │
  │                                       │
  │  1. Generate summary                 │
  │  2. Generate embedding (384d)        │
  │  3. Save to MongoDB (full document)  │
  │  4. Save to Qdrant (vector + payload)│
  └──────────────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│ MongoDB │ │  Qdrant  │
│         │ │          │
│ sources │ │  chunks  │
│ chunks  │ │  ↓       │
│extractions  extractions
└─────────┘ └──────────┘
```

**Data Flow:**
- **Input:** Completed extraction from extractors (Stories 3.1-3.5)
- **Process:** Dual storage with summary generation and embedding
- **Output:** Extraction queryable via both structured filters and semantic search

### MongoDB Extraction Schema

From architecture.md:286-291, the `extractions` collection schema:

```python
{
    "_id": str,                    # MongoDB ObjectId as string
    "source_id": str,              # → sources._id (for "all from book X")
    "chunk_id": str,               # → chunks._id (for context)
    "type": str,                   # "decision", "pattern", "warning", "methodology"...
    "content": dict,               # Type-specific structured data (Decision, Pattern, etc.)
    "topics": list[str],           # Auto-tagged topics
    "schema_version": str,         # "1.0.0"
    "extracted_at": str            # ISO 8601 timestamp
}
```

**Index Requirements (architecture.md:294-296):**
- Compound index: `extractions.type` + `extractions.topics`
- Index: `extractions.source_id`

### Qdrant Extraction Configuration

From architecture.md:298-307:

| Setting | Value | Rationale |
|---------|-------|-----------|
| Vector size | 384 | all-MiniLM-L6-v2 output (Story 2.5) |
| Distance metric | Cosine | Standard for text embeddings |
| Collection | `extractions` | Separate from `chunks` collection |
| Payload | `{source_id, chunk_id, type, topics, extraction_id}` | For filtered search |

**Payload Structure:**
```python
{
    "source_id": str,         # Links to MongoDB sources
    "chunk_id": str,          # Links to MongoDB chunks
    "extraction_id": str,     # Links to MongoDB extractions._id
    "type": str,              # ExtractionType enum value
    "topics": list[str]       # For topic-based filtering
}
```

### Summary Generation Strategy

**Purpose:** Create concise text representation of extraction for embedding.

**Per-Type Strategies:**

**Decision Extraction:**
```python
summary = f"{decision.question} {decision.recommended_approach}"
```

**Pattern Extraction:**
```python
summary = f"{pattern.name}: {pattern.problem}. {pattern.solution[:200]}"
```

**Warning Extraction:**
```python
summary = f"{warning.title}: {warning.description[:200]}"
```

**Methodology Extraction:**
```python
summary = f"{methodology.name}: {' → '.join(methodology.steps[:3])}"
```

**General Rules:**
- Limit to ~500 characters for embedding efficiency
- Include most semantically rich fields first
- Truncate intelligently (word boundaries, not mid-word)
- Preserve key information that makes extraction discoverable

### Extraction Storage Service Architecture

**Component:** `packages/pipeline/src/storage/extraction_storage.py`

**Design Pattern:** Orchestration service coordinating three components:
1. **MongoDB Client** (Story 1.4) - Document storage
2. **Qdrant Client** (Story 1.5) - Vector storage
3. **Local Embedder** (Story 2.5) - Embedding generation

**Key Methods:**

```python
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantClient
from src.embeddings.local_embedder import LocalEmbedder
from src.extractors import ExtractionBase
import structlog

logger = structlog.get_logger()


class ExtractionStorage:
    """Orchestrates extraction storage across MongoDB and Qdrant.

    Handles:
    - Summary generation from extraction content
    - Embedding generation via local embedder
    - Dual storage (MongoDB + Qdrant) with consistency
    - Source attribution preservation
    - Error handling for partial failures
    """

    def __init__(
        self,
        mongodb_client: MongoDBClient,
        qdrant_client: QdrantClient,
        embedder: LocalEmbedder
    ):
        self.mongodb = mongodb_client
        self.qdrant = qdrant_client
        self.embedder = embedder

    def save_extraction(self, extraction: ExtractionBase) -> dict:
        """Save extraction to both MongoDB and Qdrant.

        Args:
            extraction: Validated extraction from extractor

        Returns:
            dict with keys: extraction_id, mongodb_saved, qdrant_saved

        Raises:
            ValidationError: If extraction missing required fields
            StorageError: If both stores fail
        """
        # 1. Validate extraction
        if not extraction.source_id or not extraction.chunk_id:
            raise ValidationError("Missing source_id or chunk_id")

        # 2. Generate summary for embedding
        summary = self._generate_summary(extraction)

        # 3. Generate embedding (384 dimensions)
        embedding = self.embedder.generate_embedding(summary)

        # 4. Save to MongoDB (complete extraction)
        extraction_id = self.mongodb.save_extraction(extraction)

        # 5. Construct Qdrant payload
        payload = {
            "source_id": extraction.source_id,
            "chunk_id": extraction.chunk_id,
            "extraction_id": extraction_id,
            "type": extraction.type.value,  # ExtractionType enum
            "topics": extraction.topics
        }

        # 6. Save to Qdrant (embedding + payload)
        try:
            self.qdrant.upsert_extraction_embedding(
                extraction_id=extraction_id,
                embedding=embedding,
                payload=payload
            )
            qdrant_saved = True
        except QdrantError as e:
            logger.error(
                "qdrant_save_failed",
                extraction_id=extraction_id,
                error=str(e)
            )
            qdrant_saved = False

        logger.info(
            "extraction_saved",
            extraction_id=extraction_id,
            type=extraction.type.value,
            mongodb_saved=True,
            qdrant_saved=qdrant_saved
        )

        return {
            "extraction_id": extraction_id,
            "mongodb_saved": True,
            "qdrant_saved": qdrant_saved
        }

    def _generate_summary(self, extraction: ExtractionBase) -> str:
        """Generate embedding-optimized summary from extraction."""
        # Implementation in Task 2
        pass
```

### MongoDB Client Extension

**Component:** `packages/pipeline/src/storage/mongodb.py` (existing from Story 1.4)

**New Method:**

```python
def save_extraction(self, extraction: ExtractionBase) -> str:
    """Save extraction to MongoDB extractions collection.

    Args:
        extraction: Pydantic extraction model

    Returns:
        str: Inserted extraction ID

    Raises:
        DuplicateExtractionError: If extraction already exists
    """
    # Check for duplicate (same chunk_id + type)
    existing = self.db.extractions.find_one({
        "chunk_id": extraction.chunk_id,
        "type": extraction.type.value
    })

    if existing:
        logger.warning(
            "duplicate_extraction_skipped",
            chunk_id=extraction.chunk_id,
            type=extraction.type.value
        )
        return str(existing["_id"])

    # Serialize with Pydantic
    doc = extraction.model_dump(mode="json")

    # Insert
    result = self.db.extractions.insert_one(doc)

    logger.info(
        "extraction_inserted",
        extraction_id=str(result.inserted_id),
        type=extraction.type.value
    )

    return str(result.inserted_id)
```

**Important:** Use Pydantic v2 `.model_dump(mode="json")` not deprecated `.dict()`

### Qdrant Client Extension

**Component:** `packages/pipeline/src/storage/qdrant.py` (existing from Story 1.5)

**New Method:**

```python
from qdrant_client.models import PointStruct

def upsert_extraction_embedding(
    self,
    extraction_id: str,
    embedding: list[float],
    payload: dict
) -> None:
    """Upsert extraction embedding to Qdrant.

    Args:
        extraction_id: Unique extraction ID (from MongoDB)
        embedding: 384-dimensional vector
        payload: Metadata for filtering {source_id, chunk_id, type, topics, extraction_id}

    Raises:
        VectorDimensionError: If embedding not 384d
        QdrantError: If upsert fails
    """
    # Validate dimension
    if len(embedding) != 384:
        raise VectorDimensionError(
            f"Expected 384 dimensions, got {len(embedding)}"
        )

    # Create point
    point = PointStruct(
        id=extraction_id,  # Use extraction_id as Qdrant point ID
        vector=embedding,
        payload=payload
    )

    # Upsert to extractions collection
    self.client.upsert(
        collection_name="extractions",
        points=[point]
    )

    logger.info(
        "qdrant_extraction_upserted",
        extraction_id=extraction_id,
        type=payload.get("type")
    )
```

### Integration with Extractors (Optional Enhancement)

**Component:** `packages/pipeline/src/extractors/base.py` (existing from Story 3.1)

**Optional Enhancement to BaseExtractor:**

```python
from typing import Optional
from src.storage.extraction_storage import ExtractionStorage

class BaseExtractor(ABC):
    def __init__(self, storage: Optional[ExtractionStorage] = None):
        """Initialize extractor with optional storage.

        Args:
            storage: ExtractionStorage for auto-saving. If None, extractions
                     are returned but not persisted.
        """
        self.storage = storage

    def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str
    ) -> list[ExtractionResult]:
        """Extract knowledge from chunk.

        If storage is configured, extractions are automatically saved.
        """
        # ... existing extraction logic ...

        results = []

        # If storage provided, auto-save each extraction
        if self.storage:
            for extraction in extracted_items:
                save_result = self.storage.save_extraction(extraction)
                results.append(ExtractionResult(
                    extraction=extraction,
                    saved=save_result["mongodb_saved"] and save_result["qdrant_saved"]
                ))

        return results
```

**Rationale:** Allows extractors to optionally auto-save extractions during CLI usage (Story 3.7)

### Project Structure Alignment

```
packages/pipeline/
├── src/
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── mongodb.py           # Story 1.4 + THIS STORY (extend)
│   │   ├── qdrant.py            # Story 1.5 + THIS STORY (extend)
│   │   └── extraction_storage.py  # THIS STORY (new)
│   ├── extractors/
│   │   ├── utils.py             # THIS STORY (new - summary generation)
│   │   └── base.py              # Story 3.1 + THIS STORY (optional extend)
│   └── embeddings/
│       └── local_embedder.py    # Story 2.5 (dependency)
└── tests/
    └── test_storage/
        ├── test_mongodb.py      # Story 1.4 tests
        ├── test_qdrant.py       # Story 1.5 tests
        └── test_extraction_storage.py  # THIS STORY (new)
```

### Dependencies

**Blocked By:**
- Story 1.4: MongoDB Storage Client - Provides `MongoDBClient` with collections
- Story 1.5: Qdrant Storage Client - Provides `QdrantClient` with vector operations
- Story 2.5: Local Embedding Generator - Provides `LocalEmbedder` for 384d vectors
- Story 3.1: Base Extractor Interface - Provides `ExtractionBase` models (Decision, Pattern, Warning, etc.)

**Blocks:**
- Story 3.7: Extraction Pipeline CLI - Uses `ExtractionStorage` to persist extractions
- Epic 4 Stories (MCP Tools) - Query the dual-store architecture created here

### Error Handling Strategy

**Partial Failure Scenarios:**

1. **MongoDB succeeds, Qdrant fails:**
   - Log error with structured logging
   - Return success=false flag
   - DO NOT rollback MongoDB (extraction is saved, just not searchable yet)
   - Qdrant can be backfilled later

2. **MongoDB fails:**
   - Raise exception immediately
   - DO NOT attempt Qdrant save
   - MongoDB is source of truth

3. **Embedding generation fails:**
   - Raise exception immediately
   - DO NOT save to either store
   - Indicates upstream data quality issue

**Idempotency:**
- MongoDB: Check for duplicates by `chunk_id` + `type` before insert
- Qdrant: Use `upsert` (not `insert`) to handle re-runs gracefully

### Testing Strategy

**Unit Tests (`test_extraction_storage.py`):**
- Test summary generation for each extraction type
- Test MongoDB save_extraction method (mock MongoDB)
- Test Qdrant upsert_extraction_embedding (mock Qdrant)
- Test ExtractionStorage orchestration (mock all dependencies)
- Test partial failure handling

**Integration Tests (require Docker Compose MongoDB + Qdrant):**
- Test full cycle: Decision extraction → storage → retrieval
- Test Pattern extraction → storage → retrieval
- Test Warning extraction → storage → retrieval
- Test source attribution preservation across stores
- Test Qdrant payload filtering (query by type, topics)
- Test Qdrant semantic search (query by vector similarity)

**Test Fixtures:**

```python
# conftest.py
@pytest.fixture
def sample_decision() -> Decision:
    return Decision(
        source_id="src-123",
        chunk_id="chunk-456",
        question="Should I use semantic caching?",
        options=["Yes", "No"],
        considerations=["Cost reduction", "Added latency"],
        recommended_approach="Yes for high-traffic apps",
        topics=["caching", "performance"]
    )

@pytest.fixture
def sample_pattern() -> Pattern:
    return Pattern(
        source_id="src-123",
        chunk_id="chunk-789",
        name="Semantic Caching",
        problem="High API costs",
        solution="Cache using embeddings",
        topics=["caching", "embeddings"]
    )
```

### Library & Framework Requirements

**No New Dependencies:** All required packages already specified in Stories 1.4, 1.5, 2.5, 3.1:
- pydantic>=2.0 (model validation)
- pymongo (MongoDB client)
- qdrant-client>=1.13 (Qdrant operations)
- sentence-transformers>=5.0 (embeddings)
- structlog (logging)
- pytest, pytest-asyncio (testing)

### Code Quality Requirements

**From project-context.md - Critical Rules:**

1. **Async Patterns (line 54-57):**
   - Storage operations should be async where possible
   - MongoDB/Qdrant clients: use async clients if available
   - CPU-bound embedding generation can remain sync (documented)

2. **Naming Conventions (lines 47-52):**
   - Files: `extraction_storage.py` (snake_case)
   - Classes: `ExtractionStorage` (PascalCase)
   - Methods: `save_extraction()` (snake_case)
   - Variables: `extraction_id`, `embedding` (snake_case)

3. **Error Handling (lines 65-68):**
   - Custom exceptions: `StorageError`, `VectorDimensionError`
   - Include `code`, `message`, `details` dict
   - Inherit from base `KnowledgeError`

4. **Logging (lines 152-164):**
   - Use `structlog` only - NO print statements
   - Always log with context: `logger.info("extraction_saved", extraction_id=id, type=type)`

5. **Database Naming (lines 172-177):**
   - Collections: `extractions` (snake_case)
   - Fields: `source_id`, `chunk_id`, `extracted_at` (snake_case)
   - Dates as ISO 8601 strings

### Anti-Patterns to Avoid

1. **Don't hardcode connection strings** - Use `pydantic_settings.BaseSettings`
2. **Don't use bare Exception** - Use specific error types
3. **Don't ignore partial failures** - Log them with structured context
4. **Don't skip validation** - Always validate extraction before save
5. **Don't forget indexes** - MongoDB compound index on `type` + `topics` is CRITICAL
6. **Don't use deprecated Pydantic methods** - Use `.model_dump()` not `.dict()`
7. **Don't print debug info** - Use `structlog.get_logger()`

### Architecture Compliance Checklist

- [ ] ExtractionStorage at `packages/pipeline/src/storage/extraction_storage.py`
- [ ] Summary generator at `packages/pipeline/src/extractors/utils.py`
- [ ] MongoDB client extended with `save_extraction()` method
- [ ] Qdrant client extended with `upsert_extraction_embedding()` method
- [ ] All methods use async where I/O-bound (MongoDB, Qdrant)
- [ ] Embedding generation documented as sync/CPU-bound
- [ ] Structured logging with `structlog` (no print statements)
- [ ] Custom exceptions inherit from `KnowledgeError`
- [ ] Pydantic models serialized with `.model_dump(mode="json")`
- [ ] MongoDB compound index created on `extractions.type + topics`
- [ ] Qdrant collection uses 384d vectors, Cosine distance
- [ ] Tests at `packages/pipeline/tests/test_storage/test_extraction_storage.py`
- [ ] All tests pass: `cd packages/pipeline && uv run pytest tests/test_storage/`

### References

**Architecture Decisions:**
- [Architecture: MongoDB Collections Schema] `_bmad-output/architecture.md:262-291`
- [Architecture: Qdrant Configuration] `_bmad-output/architecture.md:298-307`
- [Architecture: Hybrid Storage Model] `_bmad-output/architecture.md:261`
- [Architecture: Source Attribution Chain] `_bmad-output/architecture.md:105`
- [Architecture: Compound Indexes] `_bmad-output/architecture.md:294-296`
- [Architecture: Schema Versioning] `_bmad-output/architecture.md:309-312`

**Requirements:**
- [PRD: FR-2.10 Source Attribution] `_bmad-output/prd.md:263`
- [PRD: FR-3.3 MongoDB extractions collection] `_bmad-output/prd.md:271`
- [PRD: FR-3.5 Qdrant extractions collection] `_bmad-output/prd.md:273`
- [PRD: FR-3.6 Compound Indexes] `_bmad-output/prd.md:274`
- [PRD: FR-3.8 Local Embeddings 384d] `_bmad-output/prd.md:276`

**Epic Context:**
- [Epics: Story 3.6] `_bmad-output/epics.md:467-482`
- [Epics: Epic 3 Goals] `_bmad-output/epics.md:371-376`
- [Epics: Epic 4 Dependencies] `_bmad-output/epics.md:502-506` (this story enables MCP tools)

**Project Rules:**
- [Project Context: All Implementation Rules] `_bmad-output/project-context.md`
- [Project Context: Async Patterns] `_bmad-output/project-context.md:54-57`
- [Project Context: Database Naming] `_bmad-output/project-context.md:172-177`
- [Project Context: Error Handling] `_bmad-output/project-context.md:65-68`
- [Project Context: Logging] `_bmad-output/project-context.md:152-164`

**Story Dependencies:**
- [Story 1.4: MongoDB Storage Client] - Provides base MongoDB client to extend
- [Story 1.5: Qdrant Storage Client] - Provides base Qdrant client to extend
- [Story 2.5: Local Embedding Generator] - Provides 384d embeddings
- [Story 3.1: Base Extractor Interface] - Provides ExtractionBase and all extraction models
- [Story 3.2: Decision Extractor] - Reference for extraction type
- [Story 3.3: Pattern Extractor] - Reference for extraction type (reviewed in Story 3.6 context)

**Previous Story Intelligence:**
From Story 3.3 (Pattern Extractor):
- Follow pattern of extending base class with type-specific logic
- Use `extractor_registry` pattern for type registration
- Implement `get_prompt()` loading from markdown files
- Return `list[ExtractionResult]` from `extract()` method
- Structured logging at start/end of extraction operations

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

_To be filled by dev agent - list all files created/modified:_
- packages/pipeline/src/storage/extraction_storage.py (CREATE)
- packages/pipeline/src/storage/mongodb.py (MODIFY - add save_extraction method)
- packages/pipeline/src/storage/qdrant.py (MODIFY - add upsert_extraction_embedding method)
- packages/pipeline/src/extractors/utils.py (CREATE - summary generation)
- packages/pipeline/src/extractors/base.py (MODIFY - optional storage integration)
- packages/pipeline/tests/test_storage/test_extraction_storage.py (CREATE)
- packages/pipeline/tests/conftest.py (MODIFY - add extraction fixtures)

