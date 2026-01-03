# Story 4.3: Extraction Query Tools (get_decisions, get_patterns, get_warnings)

Status: done

## Story

As an **end user**,
I want to query specific extraction types by topic,
So that I can find decisions, patterns, or warnings relevant to my current problem.

## Acceptance Criteria

1. **Given** I am connected to the MCP server
   **When** I call `get_decisions` with optional topic filter
   **Then** matching decision extractions are returned with source attribution

2. **Given** I am connected to the MCP server
   **When** I call `get_patterns` with optional topic filter
   **Then** matching pattern extractions are returned with source attribution

3. **Given** I am connected to the MCP server
   **When** I call `get_warnings` with optional topic filter
   **Then** matching warning extractions are returned with source attribution

4. **Given** any of the three tools is called
   **When** results can be filtered by topic tags
   **Then** only extractions matching the topic filter are returned

5. **Given** any of the three tools returns results
   **When** the response is formatted
   **Then** it follows the annotated format: `{results: [...], metadata: {query, sources_cited, result_count, search_type}}`

6. **Given** the tools are exposed via MCP
   **When** access tier is checked
   **Then** all three tools are available at Public tier (FR4.2, FR4.3, FR4.4)

## Dependency Analysis

**Depends On (MUST BE COMPLETE):**
- **Story 4-CC-V2:** Single Collection Architecture - Provides `KNOWLEDGE_VECTORS_COLLECTION` constant and payload-based filtering for all Qdrant operations
- **Story 4.1:** FastAPI Server with MCP Integration - Provides server.py base with MCP mounting

**Implementation Note:** Story 4-CC-V2 must be complete before implementing Task 1 (storage client creation). Qdrant queries MUST use the single `knowledge_vectors` collection with payload filtering (`content_type="extraction"`, `extraction_type`, `project_id`).

## Tasks / Subtasks

- [x] Task 1: Create shared extraction query utilities (AC: #1, #2, #3, #4)
  - [x] 1.1: Added `list_extractions()` method to `QdrantStorageClient` using scroll API
  - [x] 1.2: Implement extraction filtering by type with optional topic filter
  - [x] 1.3: Uses single-collection architecture with payload-based filtering

- [x] Task 2: Create Pydantic request/response models (AC: #5)
  - [x] 2.1: Query parameters handled inline in endpoint definitions
  - [x] 2.2: Added `ExtractionMetadata` response model to responses.py
  - [x] 2.3: Added `DecisionResult`, `PatternResult`, `WarningResult`, and response models

- [x] Task 3: Implement get_decisions tool (AC: #1, #4, #5, #6)
  - [x] 3.1: Created `packages/mcp-server/src/tools/decisions.py`
  - [x] 3.2: Implemented FastAPI endpoint with topic filter parameter
  - [x] 3.3: Map Decision extraction fields to response schema
  - [x] 3.4: Include source attribution from extraction documents

- [x] Task 4: Implement get_patterns tool (AC: #2, #4, #5, #6)
  - [x] 4.1: Created `packages/mcp-server/src/tools/patterns.py`
  - [x] 4.2: Implemented FastAPI endpoint with topic filter parameter
  - [x] 4.3: Map Pattern extraction fields to response schema
  - [x] 4.4: Include source attribution from extraction documents

- [x] Task 5: Implement get_warnings tool (AC: #3, #4, #5, #6)
  - [x] 5.1: Created `packages/mcp-server/src/tools/warnings.py`
  - [x] 5.2: Implemented FastAPI endpoint with topic filter parameter
  - [x] 5.3: Map Warning extraction fields to response schema
  - [x] 5.4: Include source attribution from extraction documents

- [x] Task 6: Register tools with FastAPI-MCP (AC: #6)
  - [x] 6.1: Updated `packages/mcp-server/src/server.py` with router imports
  - [x] 6.2: Imported and registered all three tool routers with "extractions" tag
  - [x] 6.3: Tools exposed via existing MCP mount
  - [x] 6.4: Each endpoint has explicit `operation_id`

- [x] Task 7: Write tests (AC: #1-6)
  - [x] 7.1: Created `packages/mcp-server/tests/test_tools/test_decisions.py` (12 tests)
  - [x] 7.2: Created `packages/mcp-server/tests/test_tools/test_patterns.py` (12 tests)
  - [x] 7.3: Created `packages/mcp-server/tests/test_tools/test_warnings.py` (12 tests)
  - [x] 7.4: Added `TestListExtractions` tests to test_qdrant.py (5 tests)

## Dev Notes

### Single Collection Architecture (Course Correction 2026-01-03)

**CRITICAL:** This story must implement the single-collection architecture from Story 4-CC-V2.

All Qdrant operations use a single `knowledge_vectors` collection with payload-based filtering:

```python
# packages/mcp-server/src/config.py
from src.config import KNOWLEDGE_VECTORS_COLLECTION  # = "knowledge_vectors"

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "knowledge_db"
    qdrant_url: str = "http://localhost:6333"

    # Project namespacing - used for payload filtering
    project_id: str = Field(
        default="default",
        description="Project identifier for payload filtering"
    )
```

**Qdrant queries MUST use single collection with payload filters:**
```python
from qdrant_client import models

# CORRECT - Single collection with payload filters
client.query_points(
    collection_name=KNOWLEDGE_VECTORS_COLLECTION,  # "knowledge_vectors"
    query=embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="project_id", match=models.MatchValue(value=settings.project_id)),
            models.FieldCondition(key="content_type", match=models.MatchValue(value="extraction")),
            models.FieldCondition(key="extraction_type", match=models.MatchValue(value="decision")),
        ]
    ),
    limit=100,
)

# WRONG - Never use multiple collections
client.query_points(collection_name=f"{project_id}_extractions", ...)  # ❌ NEVER DO THIS
```

**Rich Payload Fields Available for Filtering:**
- `project_id` (indexed, is_tenant=True)
- `content_type` ("chunk" | "extraction")
- `extraction_type` ("decision" | "pattern" | "warning" | "methodology" | ...)
- `source_id`, `source_type`, `source_category`, `source_year`
- `topics` (array of strings)

**Environment Variable:**
```bash
PROJECT_ID=ai_engineering uv run uvicorn src.server:app
```

See: `_bmad-output/implementation-artifacts/4-cc-v2-single-collection-architecture.md` for full details.

---

### Architecture Compliance

This story implements **FR4.2, FR4.3, FR4.4** from the requirements:
- `get_decisions` - Query decision extractions by topic (Public tier)
- `get_patterns` - Query code pattern extractions (Public tier)
- `get_warnings` - Query warning extractions (Public tier)

**Critical Boundary:** The MCP server is READ-ONLY. Never write to databases from `packages/mcp-server`.

### Extraction Document Structure

From the MongoDB `extractions` collection (see architecture.md):

```python
{
    "_id": ObjectId,
    "source_id": str,      # Reference to sources._id
    "chunk_id": str,       # Reference to chunks._id
    "type": str,           # "decision" | "pattern" | "warning" | ...
    "content": {           # Type-specific structured data
        # Decision: question, options[], considerations[], recommended_approach
        # Pattern: name, problem, solution, code_example, context, trade_offs
        # Warning: title, description, symptoms, consequences, prevention
    },
    "topics": [str],       # Topic tags for filtering
    "schema_version": str,
    "extracted_at": str    # ISO 8601 datetime
}
```

### FastAPI-MCP Integration Pattern

From fastapi-mcp documentation, use this pattern:

```python
from fastapi import FastAPI, Query
from fastapi_mcp import FastApiMCP
from typing import Optional

app = FastAPI()

@app.get("/get_decisions", operation_id="get_decisions")
async def get_decisions(
    topic: Optional[str] = Query(None, description="Filter by topic tag")
) -> ExtractionResponse:
    """Query decision extractions by topic.

    Returns AI engineering decision points with options and considerations.
    """
    # Implementation here
    pass

mcp = FastApiMCP(app, name="Knowledge Pipeline MCP")
mcp.mount_http()
```

**Key Points:**
- Use explicit `operation_id` parameter for clear tool names
- All endpoints MUST be `async def`
- Use Query parameters with descriptions for LLM context
- Mount using `mount_http()` (recommended over SSE)

### Response Format (MANDATORY)

All tools must return this exact structure:

```python
class ExtractionResponse(BaseModel):
    results: list[DecisionResult | PatternResult | WarningResult]
    metadata: ResponseMetadata

class ResponseMetadata(BaseModel):
    query: str              # Topic filter or "all"
    sources_cited: list[str]  # e.g., ["LLM Handbook Ch.5", "RAG Survey 2024"]
    result_count: int
    search_type: str = "filtered"  # For topic-based queries
```

**Error Response Format:**
```python
{
    "error": {
        "code": "NOT_FOUND" | "VALIDATION_ERROR" | "INTERNAL_ERROR",
        "message": str,
        "details": {}
    }
}
```

### Type-Specific Result Models

**DecisionResult:**
```python
class DecisionResult(BaseModel):
    id: str
    question: str
    options: list[str]
    considerations: list[str]
    recommended_approach: Optional[str]
    topics: list[str]
    source_title: str
    source_id: str
    chunk_id: str
```

**PatternResult:**
```python
class PatternResult(BaseModel):
    id: str
    name: str
    problem: str
    solution: str
    code_example: Optional[str]
    context: Optional[str]
    trade_offs: Optional[list[str]]
    topics: list[str]
    source_title: str
    source_id: str
    chunk_id: str
```

**WarningResult:**
```python
class WarningResult(BaseModel):
    id: str
    title: str
    description: str
    symptoms: Optional[list[str]]
    consequences: Optional[list[str]]
    prevention: Optional[str]
    topics: list[str]
    source_title: str
    source_id: str
    chunk_id: str
```

### Qdrant Query Pattern

For extraction filtering using single collection with payload filters:

```python
from qdrant_client import models
from src.config import KNOWLEDGE_VECTORS_COLLECTION, settings

async def query_extractions_by_type(
    self,
    extraction_type: str,
    topic: Optional[str] = None,
    limit: int = 100
) -> list[dict]:
    """Query extractions using Qdrant single collection with payload filters.

    Uses KNOWLEDGE_VECTORS_COLLECTION with content_type and extraction_type filters.
    """
    must_conditions = [
        models.FieldCondition(key="project_id", match=models.MatchValue(value=settings.project_id)),
        models.FieldCondition(key="content_type", match=models.MatchValue(value="extraction")),
        models.FieldCondition(key="extraction_type", match=models.MatchValue(value=extraction_type)),
    ]

    if topic:
        must_conditions.append(
            models.FieldCondition(key="topics", match=models.MatchAny(any=[topic]))
        )

    results = self.client.scroll(
        collection_name=KNOWLEDGE_VECTORS_COLLECTION,
        scroll_filter=models.Filter(must=must_conditions),
        limit=limit,
        with_payload=True,
    )
    return [point.payload for point, _ in results]
```

**Payload indexes used:** `project_id` (is_tenant=True), `content_type`, `extraction_type`, `topics`

### Configuration Pattern

Use pydantic-settings for all configuration:

```python
# packages/mcp-server/src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "knowledge_db"
    environment: str = "local"

    class Config:
        env_file = ".env"

settings = Settings()
```

### File Structure

```
packages/mcp-server/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Settings with pydantic-settings
│   ├── server.py                 # FastAPI app + MCP mounting
│   ├── exceptions.py             # KnowledgeError, NotFoundError
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py           # Query parameter models
│   │   ├── responses.py          # Response format models
│   │   └── shared.py             # Shared types
│   ├── storage/
│   │   ├── __init__.py
│   │   └── mongodb.py            # Read-only MongoDB client
│   └── tools/
│       ├── __init__.py
│       ├── decisions.py          # get_decisions endpoint
│       ├── patterns.py           # get_patterns endpoint
│       └── warnings.py           # get_warnings endpoint
└── tests/
    ├── conftest.py               # Shared fixtures
    └── test_tools/
        ├── test_decisions.py
        ├── test_patterns.py
        └── test_warnings.py
```

### Dependencies

Story 4.3 depends on:
- **Story 4.1:** FastAPI Server with MCP Integration (provides server.py base)
- **Story 4.2:** Semantic Search Tool (may share storage clients)

Verify these are complete or implement minimal versions:
- MongoDB connection and client
- FastAPI app with MCP mounting
- Basic response models

### Testing Pattern

```python
# tests/test_tools/test_decisions.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.server import app

@pytest.mark.asyncio
async def test_get_decisions_returns_wrapped_response():
    """Test that get_decisions returns proper response format."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/get_decisions")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "metadata" in data
        assert data["metadata"]["search_type"] == "filtered"

@pytest.mark.asyncio
async def test_get_decisions_with_topic_filter():
    """Test topic filtering works correctly."""
    # Mock MongoDB or use test database
    pass
```

### Project Structure Notes

- All files go in `packages/mcp-server/` following the architecture
- Tests mirror src structure: `src/tools/` → `tests/test_tools/`
- Use `conftest.py` for shared fixtures (MongoDB mock, sample extractions)

### References

- [Source: _bmad-output/architecture.md#MCP Tools] - Tool definitions and tier access
- [Source: _bmad-output/architecture.md#Data Architecture] - MongoDB collection structure
- [Source: _bmad-output/architecture.md#Implementation Patterns] - Response format
- [Source: _bmad-output/project-context.md#Framework Rules] - FastAPI + MCP rules
- [Source: _bmad-output/epics.md#Story 4.3] - Acceptance criteria

### Critical Rules from project-context.md

1. **NEVER write to databases from mcp-server** (read-only)
2. **All endpoints MUST be async def** - no exceptions
3. **Use structlog only** - never print()
4. **Always return wrapped responses** with results and metadata
5. **Use pydantic-settings for config** - never hardcode connection strings
6. **Tests in separate tests/ directory** mirroring src/ structure

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A

### Completion Notes List

- Implemented all 7 tasks with 41 new tests (all passing)
- Total test count for MCP server: 300 tests passing
- Used Qdrant `scroll()` API for non-semantic listing (no embedding required)
- Each tool uses single-collection architecture with payload-based filtering
- Response models follow mandatory format from architecture.md

### File List

**New Files Created:**
- `packages/mcp-server/src/tools/decisions.py` - get_decisions endpoint
- `packages/mcp-server/src/tools/patterns.py` - get_patterns endpoint
- `packages/mcp-server/src/tools/warnings.py` - get_warnings endpoint
- `packages/mcp-server/src/tools/base.py` - Shared extraction tool infrastructure (Code Review Fix)
- `packages/mcp-server/tests/test_tools/test_decisions.py` - 19 tests (7 added in code review)
- `packages/mcp-server/tests/test_tools/test_patterns.py` - 19 tests (7 added in code review)
- `packages/mcp-server/tests/test_tools/test_warnings.py` - 19 tests (7 added in code review)

**Modified Files:**
- `packages/mcp-server/src/storage/qdrant.py` - Added `list_extractions()` method
- `packages/mcp-server/src/models/responses.py` - Added ExtractionMetadata, DecisionResult, PatternResult, WarningResult, and response models
- `packages/mcp-server/src/server.py` - Added router imports and registrations
- `packages/mcp-server/tests/test_storage/test_qdrant.py` - Added TestListExtractions class (5 tests)

## Senior Developer Review (AI)

**Review Date:** 2026-01-03
**Reviewer:** Claude Opus 4.5 (code-review workflow)
**Outcome:** Changes Requested → Fixed

### Issues Found and Fixed

| Severity | Issue | Resolution |
|----------|-------|------------|
| HIGH | Missing HTTP integration tests - endpoints not tested via actual HTTP | Added 12 HTTP tests (4 per endpoint) including limit validation |
| HIGH | No error handling for Qdrant failures - unhandled 500 errors | Added try/except with KnowledgeError conversion in all 3 endpoints |
| HIGH | Duplicate global state pattern across 3 modules | Created `src/tools/base.py` with shared infrastructure |
| MEDIUM | No tests for limit parameter validation (ge=1, le=500) | Added HTTP tests verifying 422 for limit=0 and limit=501 |
| MEDIUM | extraction_title fallback untested for dict content | Added 3 tests for dict content with missing primary key |
| MEDIUM | Error handling tests missing | Added 6 error handling tests (2 per endpoint) |

### Tests Added (Code Review)

**test_decisions.py:** +7 tests
- `test_handles_dict_content_missing_question` - extraction_title fallback
- `test_get_decisions_via_http` - HTTP integration
- `test_get_decisions_with_topic_via_http` - HTTP with params
- `test_get_decisions_limit_validation_too_low` - limit=0 rejected
- `test_get_decisions_limit_validation_too_high` - limit=501 rejected
- `test_get_decisions_handles_runtime_error` - Qdrant error handling
- `test_get_decisions_handles_unexpected_error` - Generic error handling

**test_patterns.py:** +7 tests (same pattern)

**test_warnings.py:** +7 tests (same pattern)

### Code Changes

1. **Error Handling:** All three tool endpoints now catch `RuntimeError` and generic `Exception`, converting them to `KnowledgeError` with proper error codes and logging.

2. **Shared Infrastructure:** Created `src/tools/base.py` with `set_extraction_clients()` and `get_qdrant_client()` functions. Individual modules can still override for testing while sharing the base implementation.

3. **Test Coverage:** Total tests for Story 4.3 increased from 41 to 62 (57 in tool tests + 5 in Qdrant tests).

### Final Test Results

```
57 passed in 1.72s
```

All acceptance criteria verified via both unit tests and HTTP integration tests.
