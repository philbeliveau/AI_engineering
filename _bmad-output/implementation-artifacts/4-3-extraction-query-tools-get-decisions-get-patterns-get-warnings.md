# Story 4.3: Extraction Query Tools (get_decisions, get_patterns, get_warnings)

Status: ready-for-dev

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

## Tasks / Subtasks

- [ ] Task 1: Create shared extraction query utilities (AC: #1, #2, #3, #4)
  - [ ] 1.1: Create `packages/mcp-server/src/storage/mongodb.py` with read-only MongoDB client
  - [ ] 1.2: Implement `query_extractions_by_type()` method with topic filtering
  - [ ] 1.3: Add compound index query support for `type + topics`

- [ ] Task 2: Create Pydantic request/response models (AC: #5)
  - [ ] 2.1: Create `packages/mcp-server/src/models/requests.py` with query parameter models
  - [ ] 2.2: Create `packages/mcp-server/src/models/responses.py` with standard response format
  - [ ] 2.3: Create type-specific extraction result models (DecisionResult, PatternResult, WarningResult)

- [ ] Task 3: Implement get_decisions tool (AC: #1, #4, #5, #6)
  - [ ] 3.1: Create `packages/mcp-server/src/tools/decisions.py`
  - [ ] 3.2: Implement FastAPI endpoint with topic filter parameter
  - [ ] 3.3: Map Decision extraction fields to response schema
  - [ ] 3.4: Include source attribution from extraction documents

- [ ] Task 4: Implement get_patterns tool (AC: #2, #4, #5, #6)
  - [ ] 4.1: Create `packages/mcp-server/src/tools/patterns.py`
  - [ ] 4.2: Implement FastAPI endpoint with topic filter parameter
  - [ ] 4.3: Map Pattern extraction fields to response schema
  - [ ] 4.4: Include source attribution from extraction documents

- [ ] Task 5: Implement get_warnings tool (AC: #3, #4, #5, #6)
  - [ ] 5.1: Create `packages/mcp-server/src/tools/warnings.py`
  - [ ] 5.2: Implement FastAPI endpoint with topic filter parameter
  - [ ] 5.3: Map Warning extraction fields to response schema
  - [ ] 5.4: Include source attribution from extraction documents

- [ ] Task 6: Register tools with FastAPI-MCP (AC: #6)
  - [ ] 6.1: Create/update `packages/mcp-server/src/server.py` with FastAPI app
  - [ ] 6.2: Import and register all three tool endpoints
  - [ ] 6.3: Mount MCP server using `mcp.mount_http()`
  - [ ] 6.4: Set explicit `operation_id` for each endpoint

- [ ] Task 7: Write tests (AC: #1-6)
  - [ ] 7.1: Create `packages/mcp-server/tests/test_tools/test_decisions.py`
  - [ ] 7.2: Create `packages/mcp-server/tests/test_tools/test_patterns.py`
  - [ ] 7.3: Create `packages/mcp-server/tests/test_tools/test_warnings.py`
  - [ ] 7.4: Test topic filtering, empty results, and response format

## Dev Notes

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

### MongoDB Query Pattern

For topic filtering with compound index:

```python
async def query_extractions_by_type(
    extraction_type: str,
    topic: Optional[str] = None
) -> list[dict]:
    """Query extractions collection with type and optional topic filter."""
    query = {"type": extraction_type}
    if topic:
        query["topics"] = topic  # MongoDB matches if topic is in array

    cursor = db.extractions.find(query)
    return await cursor.to_list(length=100)  # Limit results
```

**Index used:** `idx_extractions_type_topics` (compound on type + topics)

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

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
