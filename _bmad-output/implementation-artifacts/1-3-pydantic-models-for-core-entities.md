# Story 1.3: Pydantic Models for Core Entities

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want Pydantic models for Source, Chunk, and Extraction entities,
So that I have type-safe data validation and serialization for all knowledge base operations.

## Acceptance Criteria

**Given** the Pydantic models module exists
**When** I create a Source, Chunk, or Extraction instance
**Then** all required fields are validated according to the architecture schema
**And** `schema_version` field is present on all models
**And** models serialize to JSON with snake_case field names
**And** MongoDB ObjectId fields are properly handled as strings

## Dependency Analysis

**Depends On:**
- **Story 1.1** (Initialize Monorepo Structure) - MUST be completed first
  - Requires `packages/pipeline/` directory structure
  - Requires `pydantic` and `pydantic-settings` dependencies installed
- **Story 1.2** (Docker Compose Infrastructure) - RECOMMENDED for testing
  - MongoDB connection for validation testing (optional but recommended)

**Blocks:**
- **Story 1.4** (MongoDB Storage Client) - needs these Pydantic models
- **Story 1.5** (Qdrant Storage Client) - needs these Pydantic models
- **Story 2.1** (Base Source Adapter Interface) - needs Source model
- **Story 2.4** (Text Chunking Processor) - needs Chunk model
- **Story 3.1** (Base Extractor Interface) - needs Extraction models

## Tasks / Subtasks

- [x] **Task 1: Verify Prerequisites** (AC: Pydantic installed)
  - [x] Confirm Story 1.1 complete: `ls packages/pipeline/pyproject.toml`
  - [x] Confirm pydantic installed: `cd packages/pipeline && uv run python -c "import pydantic; print(pydantic.__version__)"`
  - [x] Confirm pydantic version is >= 2.0

- [x] **Task 2: Create Models Directory Structure** (AC: Module exists)
  - [x] Create `packages/pipeline/src/models/` directory
  - [x] Create `packages/pipeline/src/models/__init__.py`
  - [x] Create `packages/pipeline/src/models/source.py`
  - [x] Create `packages/pipeline/src/models/chunk.py`
  - [x] Create `packages/pipeline/src/models/extraction.py`
  - [x] Create `packages/pipeline/src/__init__.py` if not exists

- [x] **Task 3: Implement Source Model** (AC: Source validation per architecture)
  - [x] Define `Source` Pydantic BaseModel
  - [x] Add `id: str` field (MongoDB ObjectId as string)
  - [x] Add `type: str` field (enum: "book", "paper", "case_study")
  - [x] Add `title: str` field
  - [x] Add `authors: list[str]` field
  - [x] Add `path: str` field
  - [x] Add `ingested_at: datetime` field
  - [x] Add `status: str` field (enum: "pending", "processing", "complete", "failed")
  - [x] Add `metadata: dict` field (arbitrary JSON metadata)
  - [x] Add `schema_version: str` field with default value

- [x] **Task 4: Implement Chunk Model** (AC: Chunk validation per architecture)
  - [x] Define `Chunk` Pydantic BaseModel
  - [x] Add `id: str` field (MongoDB ObjectId as string)
  - [x] Add `source_id: str` field (reference to sources._id)
  - [x] Add `content: str` field (the actual text)
  - [x] Add `position: dict` field with structure `{chapter, section, page}`
  - [x] Add `token_count: int` field
  - [x] Add `schema_version: str` field with default value

- [x] **Task 5: Implement Extraction Base Model** (AC: Extraction validation)
  - [x] Define `Extraction` Pydantic BaseModel (base for all extraction types)
  - [x] Add `id: str` field (MongoDB ObjectId as string)
  - [x] Add `source_id: str` field (reference to sources._id)
  - [x] Add `chunk_id: str` field (reference to chunks._id)
  - [x] Add `type: str` field (enum: "decision", "pattern", "warning", "methodology", "checklist", "persona", "workflow")
  - [x] Add `content: dict` field (type-specific structured data)
  - [x] Add `topics: list[str]` field (topic tags)
  - [x] Add `schema_version: str` field with default value
  - [x] Add `extracted_at: datetime` field

- [x] **Task 6: Implement Type-Specific Extraction Models** (AC: All extraction types)
  - [x] Define `Decision` content model: `question`, `options[]`, `considerations[]`, `recommended_approach`
  - [x] Define `Pattern` content model: `name`, `problem`, `solution`, `code_example`, `context`, `trade_offs`
  - [x] Define `Warning` content model: `title`, `description`, `symptoms`, `consequences`, `prevention`
  - [x] Define `Methodology` content model: `name`, `steps[]`, `prerequisites`, `outputs`
  - [x] Define `Checklist` content model: `name`, `items[]`, `context`
  - [x] Define `Persona` content model: `role`, `responsibilities`, `expertise`, `communication_style`
  - [x] Define `Workflow` content model: `name`, `trigger`, `steps[]`, `decision_points`

- [x] **Task 7: Configure JSON Serialization** (AC: snake_case field names)
  - [x] Verify Pydantic v2 `model_config` uses `alias_generator=None` or snake_case
  - [x] Add `model_config = ConfigDict(populate_by_name=True)` if needed
  - [x] Verify `model_dump()` produces snake_case output
  - [x] Verify `model_dump_json()` produces snake_case JSON

- [x] **Task 8: Handle MongoDB ObjectId** (AC: ObjectId handled as strings)
  - [x] Create custom validator or type for MongoDB ObjectId strings
  - [x] Ensure ObjectId validation (24 hex characters) where applicable
  - [x] Document ObjectId handling pattern for other developers

- [x] **Task 9: Create Model Exports** (AC: Clean imports)
  - [x] Export all models from `packages/pipeline/src/models/__init__.py`
  - [x] Verify imports work: `from src.models import Source, Chunk, Extraction`

- [x] **Task 10: Basic Model Tests** (AC: Validation works)
  - [x] Create test instances of each model with valid data
  - [x] Verify validation fails for invalid data (wrong types, missing required fields)
  - [x] Verify schema_version is present on all serialized output
  - [x] Document test results in completion notes

## Dev Notes

### Architecture-Specified Schema Definitions

**From Architecture Document (architecture.md:260-291):**

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

**CRITICAL:** These field names and types are EXACT requirements from the architecture. Do NOT deviate.

### Pydantic v2 Model Pattern

**From Architecture Document (architecture.md:428-432):**

```python
# Pydantic Models Naming Convention
# Model classes: PascalCase
# Field names: snake_case

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Source(BaseModel):
    id: str = Field(..., description="MongoDB ObjectId as string")
    type: str  # "book", "paper", "case_study"
    title: str
    authors: list[str]
    path: str
    ingested_at: datetime
    status: str  # "pending", "processing", "complete", "failed"
    metadata: dict = Field(default_factory=dict)
    schema_version: str = "1.0"
```

### Extraction Type Content Schemas

**From Architecture Document (architecture.md:62-73) and Epics (epics.md:402-464):**

| Extraction Type | Content Schema Fields |
|-----------------|----------------------|
| **Decision** | `question`, `options[]`, `considerations[]`, `recommended_approach` |
| **Pattern** | `name`, `problem`, `solution`, `code_example`, `context`, `trade_offs` |
| **Warning** | `title`, `description`, `symptoms`, `consequences`, `prevention` |
| **Methodology** | `name`, `steps[]`, `prerequisites`, `outputs` |
| **Checklist** | `name`, `items[]`, `context` |
| **Persona** | `role`, `responsibilities`, `expertise`, `communication_style` |
| **Workflow** | `name`, `trigger`, `steps[]`, `decision_points` |

### File Location and Module Structure

**From Architecture Document (architecture.md:646-651):**

```
packages/pipeline/
├── src/
│   ├── __init__.py
│   ├── models/                # <-- YOUR WORK HERE
│   │   ├── __init__.py
│   │   ├── source.py          # Source model
│   │   ├── chunk.py           # Chunk model
│   │   ├── extraction.py      # Extraction + type-specific models
│   │   └── pipeline.py        # Pipeline-specific models (future)
```

### Python Naming Conventions

**From Architecture Document (architecture.md:418-432):**

| Element | Convention | Example |
|---------|------------|---------|
| Files/modules | `snake_case.py` | `source.py`, `extraction.py` |
| Classes | `PascalCase` | `Source`, `Chunk`, `Decision` |
| Functions | `snake_case` | `validate_object_id()` |
| Variables | `snake_case` | `source_id`, `schema_version` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_SCHEMA_VERSION` |

### MongoDB ObjectId Handling

**CRITICAL PATTERN:** MongoDB ObjectIds must be handled as strings in Pydantic:

```python
from pydantic import BaseModel, field_validator
import re

OBJECTID_PATTERN = re.compile(r'^[a-f0-9]{24}$')

class MongoModel(BaseModel):
    id: str

    @field_validator('id')
    @classmethod
    def validate_object_id(cls, v: str) -> str:
        if not OBJECTID_PATTERN.match(v):
            raise ValueError('Invalid MongoDB ObjectId format')
        return v
```

**Alternative - Use Pydantic's built-in pattern:**
```python
from pydantic import BaseModel, Field

class MongoModel(BaseModel):
    id: str = Field(..., pattern=r'^[a-f0-9]{24}$')
```

### Schema Versioning Strategy

**From Architecture Document (architecture.md:307-310):**

- All documents include `schema_version` field
- Application code handles version differences
- Migration scripts for breaking changes

**Implementation:**
```python
CURRENT_SCHEMA_VERSION = "1.0"

class BaseDocument(BaseModel):
    schema_version: str = CURRENT_SCHEMA_VERSION
```

### Previous Story Intelligence

**From Story 1.1 (Monorepo Structure):**
- Directory structure: `packages/pipeline/src/`
- Pydantic dependency: `pydantic>=2.0`, `pydantic-settings`
- Python version: 3.11+
- Package manager: `uv`

**From Story 1.2 (Docker Compose):**
- MongoDB available at `localhost:27017`
- Database name: `knowledge_db`
- Collections to be created: `sources`, `chunks`, `extractions`

### Reference Implementation Example

```python
# packages/pipeline/src/models/source.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal
import re

OBJECTID_PATTERN = re.compile(r'^[a-f0-9]{24}$')
CURRENT_SCHEMA_VERSION = "1.0"

class Source(BaseModel):
    """Source document model for books, papers, and case studies."""

    id: str = Field(..., description="MongoDB ObjectId as string")
    type: Literal["book", "paper", "case_study"]
    title: str
    authors: list[str] = Field(default_factory=list)
    path: str
    ingested_at: datetime
    status: Literal["pending", "processing", "complete", "failed"]
    metadata: dict = Field(default_factory=dict)
    schema_version: str = CURRENT_SCHEMA_VERSION

    @field_validator('id')
    @classmethod
    def validate_object_id(cls, v: str) -> str:
        if not OBJECTID_PATTERN.match(v):
            raise ValueError('Invalid MongoDB ObjectId format')
        return v

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "type": "book",
                "title": "LLM Engineer's Handbook",
                "authors": ["Paul Iusztin", "Maxime Labonne"],
                "path": "/data/raw/llm-handbook.pdf",
                "ingested_at": "2025-12-30T10:30:00Z",
                "status": "complete",
                "metadata": {"pages": 800},
                "schema_version": "1.0"
            }
        }
    }
```

### Testing Pattern

**From Architecture Document (architecture.md:456-462):**

Tests mirror src/ structure:
```
packages/pipeline/
├── src/
│   └── models/
│       ├── source.py
│       └── chunk.py
└── tests/
    └── test_models/
        ├── conftest.py
        ├── test_source.py
        └── test_chunk.py
```

**Test file naming:** `test_source.py`, `test_chunk.py`

**Basic test example:**
```python
# packages/pipeline/tests/test_models/test_source.py
import pytest
from datetime import datetime
from src.models import Source

def test_source_valid():
    source = Source(
        id="507f1f77bcf86cd799439011",
        type="book",
        title="Test Book",
        authors=["Author"],
        path="/test/path.pdf",
        ingested_at=datetime.now(),
        status="pending"
    )
    assert source.schema_version == "1.0"
    assert source.type == "book"

def test_source_invalid_id():
    with pytest.raises(ValueError):
        Source(
            id="invalid-id",
            type="book",
            title="Test",
            authors=[],
            path="/test",
            ingested_at=datetime.now(),
            status="pending"
        )
```

### Architecture Compliance Checklist

**From Architecture Document:**

- [ ] All models use PascalCase class names (architecture.md:424)
- [ ] All fields use snake_case (architecture.md:425)
- [ ] `schema_version` present on all document models (architecture.md:307)
- [ ] MongoDB ObjectIds handled as strings (architecture.md:308)
- [ ] JSON serialization uses snake_case (architecture.md:500)
- [ ] Files in `packages/pipeline/src/models/` (architecture.md:646)
- [ ] Pydantic v2 patterns used (architecture.md:198)

### Success Validation

**Story is COMPLETE when:**
- [ ] `packages/pipeline/src/models/__init__.py` exists and exports all models
- [ ] `Source` model validates all fields per architecture schema
- [ ] `Chunk` model validates all fields per architecture schema
- [ ] `Extraction` base model validates all fields per architecture schema
- [ ] Type-specific content models exist (Decision, Pattern, Warning, etc.)
- [ ] `schema_version` field present on all models
- [ ] MongoDB ObjectId validation works (24 hex character strings)
- [ ] JSON serialization produces snake_case output
- [ ] Basic instantiation tests pass for all models

### Known Issues & Decisions

**Issue 1: ObjectId vs String Trade-off**
- **Impact:** MongoDB uses ObjectId internally, but JSON/API needs strings
- **Decision:** Use string type with regex validation for ObjectId fields
- **Validation:** `^[a-f0-9]{24}$` pattern

**Issue 2: Optional vs Required Fields**
- **Impact:** Some fields may be optional during creation but required after save
- **Decision:** Use `Optional[]` for fields that can be None initially
- **Validation:** Document which fields are optional in model docstrings

**Issue 3: Extraction Content Type Safety**
- **Impact:** `content` field varies by extraction type
- **Decision:** Create specific content models for each extraction type
- **Validation:** Use Union types or discriminated unions if needed

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 51 tests passing (0.18s)
- Ruff linting: All checks passed
- Pydantic version: 2.12.5

### Completion Notes List

**Implementation Summary:**

1. **Source Model** (`source.py`):
   - Full Pydantic v2 implementation with Literal types for `type` and `status` enums
   - MongoDB ObjectId validation via `@field_validator` using regex pattern `^[a-f0-9]{24}$`
   - Default `schema_version = "1.0"` on all instances
   - `ConfigDict(populate_by_name=True)` for JSON serialization

2. **Chunk Model** (`chunk.py`):
   - `ChunkPosition` nested model for `{chapter, section, page}` structure
   - ObjectId validation on both `id` and `source_id` fields
   - Model validator to ensure `token_count` doesn't exceed content length
   - Schema version and JSON config matching Source model

3. **Extraction Model** (`extraction.py`):
   - Base `Extraction` model with Union content type supporting all 7 extraction types
   - 7 type-specific content models: `DecisionContent`, `PatternContent`, `WarningContent`, `MethodologyContent`, `ChecklistContent`, `PersonaContent`, `WorkflowContent`
   - 7 typed extraction convenience classes: `DecisionExtraction`, `PatternExtraction`, etc.
   - ObjectId validation on `id`, `source_id`, and `chunk_id` fields

4. **Testing:**
   - 51 comprehensive tests covering:
     - Valid model creation with complete and minimal fields
     - All enum variations (types, statuses)
     - Invalid ObjectId rejection (wrong format, too short, uppercase)
     - Invalid enum value rejection
     - Empty required field rejection
     - JSON serialization snake_case verification
     - Schema version presence in all outputs
     - All 7 content models and typed extractions

5. **Architecture Compliance:**
   - All models use PascalCase class names ✓
   - All fields use snake_case ✓
   - schema_version present on Source, Chunk, Extraction ✓
   - MongoDB ObjectIds as validated strings ✓
   - JSON serialization produces snake_case ✓
   - Files in packages/pipeline/src/models/ ✓
   - Pydantic v2 patterns (BaseModel, ConfigDict, field_validator) ✓

### File List

**Created:**
- packages/pipeline/src/models/__init__.py (MODIFIED - added exports)
- packages/pipeline/src/models/source.py (CREATE)
- packages/pipeline/src/models/chunk.py (CREATE)
- packages/pipeline/src/models/extraction.py (CREATE)
- packages/pipeline/tests/test_models/__init__.py (CREATE)
- packages/pipeline/tests/test_models/conftest.py (CREATE)
- packages/pipeline/tests/test_models/test_source.py (CREATE)
- packages/pipeline/tests/test_models/test_chunk.py (CREATE)
- packages/pipeline/tests/test_models/test_extraction.py (CREATE)

## Senior Developer Review (AI)

### Review Date: 2025-12-30
### Reviewer: Claude Opus 4.5 (Adversarial Code Review)

**Review Outcome: APPROVED (after fixes applied)**

### Issues Found and Fixed

**HIGH Severity (2 issues - FIXED):**

1. **H1: Content-Type Mismatch in Base Extraction Model** (`extraction.py:222-249`)
   - **Issue:** Base `Extraction` class allowed type/content schema mismatches
   - **Fix:** Added `model_validator` to verify content structure matches extraction type
   - **Impact:** Prevents data integrity issues when querying by type

2. **H2: ChunkPosition Allows Negative Page Numbers** (`chunk.py:26`)
   - **Issue:** `page` field accepted negative values
   - **Fix:** Added `Field(default=None, ge=1)` constraint
   - **Impact:** Prevents invalid position data

**MEDIUM Severity (4 issues - 3 FIXED, 1 SKIPPED):**

1. **M1: Empty/Whitespace Strings in Authors List** (`source.py:52-56`)
   - **Fix:** Added `validate_authors` field validator to filter and trim

2. **M2: No Maximum Length on String Fields** (`source.py:36-38`, `chunk.py:48`)
   - **Fix:** Added `max_length=500` for title, `max_length=1000` for path, `max_length=50000` for content

3. **M3: Module `__all__` Export Mismatch** - SKIPPED
   - **Reason:** Intentional design - submodules not meant for direct import

4. **M4: Future Dates Allowed for `ingested_at`** (`source.py:58-67`)
   - **Fix:** Added validator rejecting future dates (5-minute tolerance for clock skew)

**LOW Severity (3 issues - NOT FIXED, documented):**

1. **L1:** Duplicate `CURRENT_SCHEMA_VERSION` constants (maintenance burden)
2. **L2:** No docs for raw dict content in Union type
3. **L3:** Missing edge case test for same ObjectId reuse

### Test Coverage Update

- **Before review:** 51 tests passing
- **After review:** 61 tests passing (+10 new tests)
- **New tests added:**
  - `test_source_empty_authors_filtered`
  - `test_source_authors_whitespace_trimmed`
  - `test_source_title_max_length`
  - `test_source_path_max_length`
  - `test_source_future_date_rejected`
  - `test_chunk_content_max_length`
  - `test_position_negative_page_rejected`
  - `test_position_zero_page_rejected`
  - `test_position_valid_page`
  - `test_extraction_content_type_mismatch_rejected`

### Files Modified in Review

- `packages/pipeline/src/models/source.py` - Added author validation, future date validation, max_length constraints
- `packages/pipeline/src/models/chunk.py` - Added page >=1 constraint, content max_length
- `packages/pipeline/src/models/extraction.py` - Added content-type mismatch validator
- `packages/pipeline/tests/test_models/test_source.py` - Added 5 new tests
- `packages/pipeline/tests/test_models/test_chunk.py` - Added 4 new tests
- `packages/pipeline/tests/test_models/test_extraction.py` - Added 1 new test, fixed existing test

### Verification

```
$ uv run pytest tests/test_models -v
61 passed in 0.21s

$ uv run ruff check src/models/ tests/test_models/
All checks passed!
```

## Change Log

- 2025-12-30: Implemented Pydantic models for Source, Chunk, and Extraction entities with full validation, type-specific content models, and comprehensive test suite (51 tests passing)
- 2025-12-30: Code review completed - 5 issues fixed, 10 new tests added, all 61 tests passing
