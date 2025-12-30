# Story 1.3: Pydantic Models for Core Entities

Status: ready-for-dev

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

- [ ] **Task 1: Verify Prerequisites** (AC: Pydantic installed)
  - [ ] Confirm Story 1.1 complete: `ls packages/pipeline/pyproject.toml`
  - [ ] Confirm pydantic installed: `cd packages/pipeline && uv run python -c "import pydantic; print(pydantic.__version__)"`
  - [ ] Confirm pydantic version is >= 2.0

- [ ] **Task 2: Create Models Directory Structure** (AC: Module exists)
  - [ ] Create `packages/pipeline/src/models/` directory
  - [ ] Create `packages/pipeline/src/models/__init__.py`
  - [ ] Create `packages/pipeline/src/models/source.py`
  - [ ] Create `packages/pipeline/src/models/chunk.py`
  - [ ] Create `packages/pipeline/src/models/extraction.py`
  - [ ] Create `packages/pipeline/src/__init__.py` if not exists

- [ ] **Task 3: Implement Source Model** (AC: Source validation per architecture)
  - [ ] Define `Source` Pydantic BaseModel
  - [ ] Add `id: str` field (MongoDB ObjectId as string)
  - [ ] Add `type: str` field (enum: "book", "paper", "case_study")
  - [ ] Add `title: str` field
  - [ ] Add `authors: list[str]` field
  - [ ] Add `path: str` field
  - [ ] Add `ingested_at: datetime` field
  - [ ] Add `status: str` field (enum: "pending", "processing", "complete", "failed")
  - [ ] Add `metadata: dict` field (arbitrary JSON metadata)
  - [ ] Add `schema_version: str` field with default value

- [ ] **Task 4: Implement Chunk Model** (AC: Chunk validation per architecture)
  - [ ] Define `Chunk` Pydantic BaseModel
  - [ ] Add `id: str` field (MongoDB ObjectId as string)
  - [ ] Add `source_id: str` field (reference to sources._id)
  - [ ] Add `content: str` field (the actual text)
  - [ ] Add `position: dict` field with structure `{chapter, section, page}`
  - [ ] Add `token_count: int` field
  - [ ] Add `schema_version: str` field with default value

- [ ] **Task 5: Implement Extraction Base Model** (AC: Extraction validation)
  - [ ] Define `Extraction` Pydantic BaseModel (base for all extraction types)
  - [ ] Add `id: str` field (MongoDB ObjectId as string)
  - [ ] Add `source_id: str` field (reference to sources._id)
  - [ ] Add `chunk_id: str` field (reference to chunks._id)
  - [ ] Add `type: str` field (enum: "decision", "pattern", "warning", "methodology", "checklist", "persona", "workflow")
  - [ ] Add `content: dict` field (type-specific structured data)
  - [ ] Add `topics: list[str]` field (topic tags)
  - [ ] Add `schema_version: str` field with default value
  - [ ] Add `extracted_at: datetime` field

- [ ] **Task 6: Implement Type-Specific Extraction Models** (AC: All extraction types)
  - [ ] Define `Decision` content model: `question`, `options[]`, `considerations[]`, `recommended_approach`
  - [ ] Define `Pattern` content model: `name`, `problem`, `solution`, `code_example`, `context`, `trade_offs`
  - [ ] Define `Warning` content model: `title`, `description`, `symptoms`, `consequences`, `prevention`
  - [ ] Define `Methodology` content model: `name`, `steps[]`, `prerequisites`, `outputs`
  - [ ] Define `Checklist` content model: `name`, `items[]`, `context`
  - [ ] Define `Persona` content model: `role`, `responsibilities`, `expertise`, `communication_style`
  - [ ] Define `Workflow` content model: `name`, `trigger`, `steps[]`, `decision_points`

- [ ] **Task 7: Configure JSON Serialization** (AC: snake_case field names)
  - [ ] Verify Pydantic v2 `model_config` uses `alias_generator=None` or snake_case
  - [ ] Add `model_config = ConfigDict(populate_by_name=True)` if needed
  - [ ] Verify `model_dump()` produces snake_case output
  - [ ] Verify `model_dump_json()` produces snake_case JSON

- [ ] **Task 8: Handle MongoDB ObjectId** (AC: ObjectId handled as strings)
  - [ ] Create custom validator or type for MongoDB ObjectId strings
  - [ ] Ensure ObjectId validation (24 hex characters) where applicable
  - [ ] Document ObjectId handling pattern for other developers

- [ ] **Task 9: Create Model Exports** (AC: Clean imports)
  - [ ] Export all models from `packages/pipeline/src/models/__init__.py`
  - [ ] Verify imports work: `from src.models import Source, Chunk, Extraction`

- [ ] **Task 10: Basic Model Tests** (AC: Validation works)
  - [ ] Create test instances of each model with valid data
  - [ ] Verify validation fails for invalid data (wrong types, missing required fields)
  - [ ] Verify schema_version is present on all serialized output
  - [ ] Document test results in completion notes

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

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

_To be filled by dev agent_

### File List

_To be filled by dev agent - list all files created/modified:_
- packages/pipeline/src/__init__.py (CREATE if not exists)
- packages/pipeline/src/models/__init__.py (CREATE)
- packages/pipeline/src/models/source.py (CREATE)
- packages/pipeline/src/models/chunk.py (CREATE)
- packages/pipeline/src/models/extraction.py (CREATE)
- packages/pipeline/tests/test_models/ (CREATE directory - optional)
- packages/pipeline/tests/test_models/test_source.py (CREATE - optional)
- packages/pipeline/tests/test_models/test_chunk.py (CREATE - optional)
- packages/pipeline/tests/test_models/test_extraction.py (CREATE - optional)
