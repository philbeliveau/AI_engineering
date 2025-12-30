# Story 4.4: Methodology Query Tool (get_methodologies)

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **end user**,
I want to query methodology extractions,
So that I can find step-by-step processes for AI engineering tasks.

## Acceptance Criteria

1. **Given** I am connected to the MCP server with a valid API key
   **When** I call `get_methodologies` with optional topic filter
   **Then** matching methodology extractions are returned

2. **Given** the response contains methodology results
   **When** the data is formatted
   **Then** results include full steps and prerequisites for each methodology

3. **Given** any methodology result
   **When** the source attribution is examined
   **Then** source_id, chunk_id, and source_title are included

4. **Given** the response is formatted
   **When** the structure is validated
   **Then** it follows the annotated format: `{results: [...], metadata: {query, sources_cited, result_count, search_type}}`

5. **Given** the tool is accessed without valid API key
   **When** the request is processed
   **Then** the tool returns 401 Unauthorized (Registered tier required - FR4.5)

6. **Given** the tool is exposed via MCP
   **When** access tier is checked
   **Then** the tool is available at **Registered tier only** (FR4.5)

## Dependency Analysis

**Depends On (MUST BE COMPLETE):**
- **Story 4.1:** FastAPI Server with MCP Integration - Provides server.py base with MCP mounting (ready-for-dev)
- **Story 4.3:** Extraction Query Tools - Provides patterns for MongoDB querying, response models, and tool structure (ready-for-dev)
- **Story 5.2:** API Key Authentication Middleware - Required for Registered tier access enforcement (backlog - may need basic implementation)

**Blocks:**
- **Story 4.5:** Source Management Tools - May share storage client patterns
- **Story 4.6:** Response Models and Error Handling - This story contributes to overall response standardization

**Context:** This story follows the same pattern as Story 4.3 but with TWO key differences:
1. Returns methodology-specific content (steps[], prerequisites, outputs)
2. Requires **Registered tier authentication** (API key required)

## Tasks / Subtasks

- [ ] **Task 1: Verify Prerequisites and Story 4.3 Patterns** (AC: All dependencies available)
  - [ ] 1.1: Confirm Story 4.1 patterns exist (check for `packages/mcp-server/src/server.py` or create minimal version)
  - [ ] 1.2: Review Story 4.3 implementation patterns (if exists) or reference the story file
  - [ ] 1.3: Verify MongoDB client exists or needs creation: `packages/mcp-server/src/storage/mongodb.py`
  - [ ] 1.4: Verify response models exist or need creation: `packages/mcp-server/src/models/responses.py`
  - [ ] 1.5: Check for existing auth middleware: `packages/mcp-server/src/middleware/auth.py`

- [ ] **Task 2: Create/Extend MongoDB Client for Methodology Queries** (AC: #1, #2, #3)
  - [ ] 2.1: Ensure `packages/mcp-server/src/storage/mongodb.py` exists with read-only client
  - [ ] 2.2: Add `query_methodologies(topic: Optional[str] = None)` method
  - [ ] 2.3: Use compound index query on `type="methodology"` + optional `topics` filter
  - [ ] 2.4: Return methodology documents with all required fields
  - [ ] 2.5: Follow project-context.md:71-77 - MCP server is READ-ONLY

- [ ] **Task 3: Create Methodology Result Model** (AC: #2, #4)
  - [ ] 3.1: Create or extend `packages/mcp-server/src/models/responses.py`
  - [ ] 3.2: Implement `MethodologyResult` Pydantic model:
    - `id: str` - Extraction ID
    - `name: str` - Methodology name
    - `steps: list[str]` - Step-by-step process
    - `prerequisites: Optional[list[str]]` - Required knowledge/setup
    - `outputs: Optional[list[str]]` - Expected outputs/deliverables
    - `topics: list[str]` - Topic tags
    - `source_title: str` - Human-readable source name
    - `source_id: str` - Reference to sources collection
    - `chunk_id: str` - Reference to chunks collection
  - [ ] 3.3: Ensure model follows architecture.md naming conventions (snake_case fields)
  - [ ] 3.4: Create `MethodologyResponse` wrapper with `results` and `metadata`

- [ ] **Task 4: Implement Basic API Key Authentication** (AC: #5, #6)
  - [ ] 4.1: Create `packages/mcp-server/src/middleware/auth.py` if not exists
  - [ ] 4.2: Implement `get_api_key` dependency that extracts `X-API-Key` header
  - [ ] 4.3: Implement `verify_registered_tier` dependency that validates API key
  - [ ] 4.4: For MVP: Use environment variable `REGISTERED_API_KEYS` (comma-separated list)
  - [ ] 4.5: Return 401 Unauthorized if no valid key provided
  - [ ] 4.6: Add `api_keys: list[str]` to Settings in config.py
  - [ ] 4.7: Follow architecture.md:314-328 (Tiered Authentication Model)

- [ ] **Task 5: Implement get_methodologies Tool** (AC: #1, #2, #3, #4, #5, #6)
  - [ ] 5.1: Create `packages/mcp-server/src/tools/methodologies.py`
  - [ ] 5.2: Implement FastAPI endpoint:
    ```python
    @app.get("/get_methodologies", operation_id="get_methodologies")
    async def get_methodologies(
        topic: Optional[str] = Query(None, description="Filter by topic tag"),
        api_key: str = Depends(verify_registered_tier)
    ) -> MethodologyResponse:
    ```
  - [ ] 5.3: Query MongoDB for methodology extractions with optional topic filter
  - [ ] 5.4: Map extraction documents to `MethodologyResult` model
  - [ ] 5.5: Build source attribution from extraction documents (lookup source titles)
  - [ ] 5.6: Construct response with `results` and `metadata` (search_type="filtered")
  - [ ] 5.7: Add structured logging with structlog
  - [ ] 5.8: Handle empty results (return `{results: [], metadata: {...}}`)

- [ ] **Task 6: Register Tool with FastAPI-MCP** (AC: #6)
  - [ ] 6.1: Import methodologies router in `packages/mcp-server/src/server.py`
  - [ ] 6.2: Include router with FastAPI app
  - [ ] 6.3: Verify MCP exposes the tool with `operation_id="get_methodologies"`
  - [ ] 6.4: Add docstring with clear description for LLM context

- [ ] **Task 7: Write Tests** (AC: #1-6)
  - [ ] 7.1: Create `packages/mcp-server/tests/test_tools/test_methodologies.py`
  - [ ] 7.2: Test successful query with valid API key
  - [ ] 7.3: Test 401 response without API key
  - [ ] 7.4: Test 401 response with invalid API key
  - [ ] 7.5: Test topic filtering works correctly
  - [ ] 7.6: Test empty results return proper format
  - [ ] 7.7: Test response matches annotated format
  - [ ] 7.8: Follow project-context.md:110-142 (Testing patterns)

- [ ] **Task 8: Update Documentation** (AC: All)
  - [ ] 8.1: Add `get_methodologies` to README.md API documentation
  - [ ] 8.2: Document Registered tier requirement
  - [ ] 8.3: Add API key configuration to .env.example

## Dev Notes

### Epic 4 Context

This is **Story 4.4** in Epic 4 (Knowledge Query Interface). It follows the pattern established by Story 4.3 but with a critical difference: **Registered tier access** requiring API key authentication.

**Epic 4 Progress:**
- 4.1: FastAPI Server with MCP Integration (ready-for-dev)
- 4.2: Semantic Search Tool (backlog)
- 4.3: get_decisions, get_patterns, get_warnings - Public tier (ready-for-dev)
- **4.4: get_methodologies - Registered tier (THIS STORY)**
- 4.5: list_sources, compare_sources (backlog)
- 4.6: Response Models and Error Handling (backlog)

### Critical Difference: Registered Tier Access

From architecture.md:314-328:

| Tier | Auth Required | Rate Limit | Access |
|------|---------------|------------|--------|
| Public | None | 100 req/hr per IP | Core search, public extractions |
| **Registered** | **API Key** | 1000 req/hr | Full search, **all extractions** |
| Premium | API Key + Subscription | Unlimited | Premium content, priority |

**This tool is Registered tier** because methodologies are considered more valuable content (step-by-step processes from books) intended for users who have registered.

**Implementation:**
- Require `X-API-Key` header
- Validate against configured API keys
- Return 401 Unauthorized if invalid/missing

### Methodology Extraction Document Structure

From the MongoDB `extractions` collection with `type="methodology"`:

```python
{
    "_id": ObjectId,
    "source_id": str,      # Reference to sources._id
    "chunk_id": str,       # Reference to chunks._id
    "type": "methodology", # Fixed for this tool
    "content": {
        "name": str,           # Methodology name
        "steps": [str],        # Step-by-step process
        "prerequisites": [str], # Optional: required knowledge/setup
        "outputs": [str]        # Optional: expected outputs
    },
    "topics": [str],       # Topic tags for filtering
    "schema_version": str,
    "extracted_at": str    # ISO 8601 datetime
}
```

### Response Format (MANDATORY)

From architecture.md:464-476 and project-context.md:79-91:

```python
class MethodologyResponse(BaseModel):
    results: list[MethodologyResult]
    metadata: ResponseMetadata

class ResponseMetadata(BaseModel):
    query: str              # Topic filter or "all"
    sources_cited: list[str]  # e.g., ["LLM Handbook Ch.5", "RAG Survey 2024"]
    result_count: int
    search_type: str = "filtered"  # For topic-based queries

class MethodologyResult(BaseModel):
    id: str
    name: str
    steps: list[str]
    prerequisites: Optional[list[str]] = None
    outputs: Optional[list[str]] = None
    topics: list[str]
    source_title: str
    source_id: str
    chunk_id: str
```

### API Key Authentication Pattern

From architecture.md:323-327:

```python
# packages/mcp-server/src/middleware/auth.py
from fastapi import Header, HTTPException, Depends
from src.config import settings

async def get_api_key(x_api_key: str = Header(None)) -> Optional[str]:
    """Extract API key from header."""
    return x_api_key

async def verify_registered_tier(
    api_key: Optional[str] = Depends(get_api_key)
) -> str:
    """Verify API key is valid for Registered tier access."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "API key required for Registered tier access",
                    "details": {"header": "X-API-Key"}
                }
            }
        )
    if api_key not in settings.registered_api_keys:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid API key",
                    "details": {}
                }
            }
        )
    return api_key
```

### Configuration Update

Add to `packages/mcp-server/src/config.py`:

```python
class Settings(BaseSettings):
    # ... existing fields ...
    registered_api_keys: list[str] = []  # Comma-separated in env

    @validator("registered_api_keys", pre=True)
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v

    class Config:
        env_file = ".env"
```

Add to `.env.example`:
```
# Registered tier API keys (comma-separated)
REGISTERED_API_KEYS=key1,key2,key3
```

### MongoDB Query Pattern

```python
async def query_methodologies(
    self,
    topic: Optional[str] = None,
    limit: int = 100
) -> list[dict]:
    """Query methodology extractions with optional topic filter.

    Uses compound index: idx_extractions_type_topics
    """
    query = {"type": "methodology"}
    if topic:
        query["topics"] = topic  # MongoDB matches if topic is in array

    cursor = self.db.extractions.find(query).limit(limit)
    return await cursor.to_list(length=limit)
```

### File Structure After Implementation

```
packages/mcp-server/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Add registered_api_keys field
│   ├── server.py                 # Register methodologies router
│   ├── exceptions.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py               # NEW: API key authentication
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── responses.py          # Add MethodologyResult, MethodologyResponse
│   │   └── requests.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── mongodb.py            # Add query_methodologies method
│   │
│   └── tools/
│       ├── __init__.py
│       ├── decisions.py          # From Story 4.3
│       ├── patterns.py           # From Story 4.3
│       ├── warnings.py           # From Story 4.3
│       ├── methodologies.py      # NEW: This story
│       └── health.py
│
└── tests/
    ├── conftest.py               # Add API key fixtures
    └── test_tools/
        ├── test_decisions.py
        ├── test_patterns.py
        ├── test_warnings.py
        └── test_methodologies.py # NEW: This story
```

### Testing Pattern for Authenticated Endpoints

```python
# tests/test_tools/test_methodologies.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.server import app

VALID_API_KEY = "test-key-123"
INVALID_API_KEY = "invalid-key"

@pytest.fixture
def mock_api_keys(monkeypatch):
    """Set up test API keys."""
    monkeypatch.setenv("REGISTERED_API_KEYS", VALID_API_KEY)

@pytest.mark.asyncio
async def test_get_methodologies_requires_api_key():
    """Test that endpoint returns 401 without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/get_methodologies")
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.asyncio
async def test_get_methodologies_with_valid_key(mock_api_keys):
    """Test successful query with valid API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/get_methodologies",
            headers={"X-API-Key": VALID_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "metadata" in data
        assert data["metadata"]["search_type"] == "filtered"

@pytest.mark.asyncio
async def test_get_methodologies_with_invalid_key():
    """Test 401 with invalid API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/get_methodologies",
            headers={"X-API-Key": INVALID_API_KEY}
        )
        assert response.status_code == 401
```

### Project Context Reference

**CRITICAL:** Read these files before implementation:
- `_bmad-output/project-context.md` - 85+ implementation rules
- `_bmad-output/architecture.md` - All architectural decisions

**Key Sections:**
- project-context.md:17-42 - Technology Stack & Versions
- project-context.md:47-77 - Critical Implementation Rules
- project-context.md:79-108 - Framework Rules (FastAPI + MCP)
- project-context.md:218-225 - Anti-Patterns (NEVER DO)
- architecture.md:314-328 - Tiered Authentication Model
- architecture.md:330-341 - MCP Tools Tier Access
- architecture.md:464-485 - Success/Error Response Formats

### Critical Anti-Patterns to Avoid

From project-context.md:218-225:

**NEVER DO:**
- Write to databases from `packages/mcp-server` (read-only)
- Use `print()` - always `structlog`
- Hardcode connection strings - use Settings
- Return bare results - always wrap in `{results, metadata}`
- Catch bare `Exception` - use specific types
- Use `pip` or manual venv - always `uv run`
- Commit `.env` files or secrets

### Differences from Story 4.3

| Aspect | Story 4.3 | Story 4.4 |
|--------|-----------|-----------|
| Tools | get_decisions, get_patterns, get_warnings | get_methodologies |
| Access Tier | Public (no auth) | **Registered (API key required)** |
| Content Type | Decision, Pattern, Warning | **Methodology** |
| Content Fields | Type-specific (question/options, name/problem/solution, title/symptoms) | **name, steps[], prerequisites, outputs** |
| Auth Dependency | None | `Depends(verify_registered_tier)` |

### Development Commands

**Start Infrastructure:**
```bash
docker-compose up -d
```

**Run Server (Development):**
```bash
cd packages/mcp-server
uv run uvicorn src.server:app --reload
```

**Test with API Key:**
```bash
# Set API key in .env
echo "REGISTERED_API_KEYS=test-key-123" >> packages/mcp-server/.env

# Test endpoint
curl -H "X-API-Key: test-key-123" http://localhost:8000/get_methodologies
curl -H "X-API-Key: test-key-123" "http://localhost:8000/get_methodologies?topic=rag"
```

**Run Tests:**
```bash
cd packages/mcp-server
uv run pytest tests/test_tools/test_methodologies.py -v
```

### Success Criteria Summary

**Story Complete When:**
1. `get_methodologies` endpoint exists and responds to requests
2. Returns 401 when called without API key
3. Returns 401 when called with invalid API key
4. Returns methodologies when called with valid API key
5. Topic filtering works correctly
6. Response format matches `{results: [...], metadata: {...}}`
7. Results include steps[], prerequisites, outputs
8. Source attribution included (source_id, chunk_id, source_title)
9. All tests passing: `uv run pytest tests/test_tools/test_methodologies.py`
10. No linting errors: `uv run ruff check .`

### References

**Source Documents:**
- [Architecture: MCP Tools Tier Access] architecture.md#L330-341
- [Architecture: Tiered Authentication Model] architecture.md#L314-328
- [Architecture: API Response Format] architecture.md#L464-476
- [Architecture: Error Response Format] architecture.md#L478-485
- [Project Context: Framework Rules] project-context.md#L79-108
- [Project Context: Anti-Patterns] project-context.md#L218-225
- [Epics: Story 4.4 Requirements] epics.md#L563-579
- [Story 4.3: Extraction Query Tools Pattern] 4-3-extraction-query-tools-get-decisions-get-patterns-get-warnings.md

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent during implementation_

### Debug Log References

_To be filled by dev agent during implementation_

### Completion Notes List

_To be filled by dev agent during implementation_

### File List

_To be filled by dev agent during implementation_
