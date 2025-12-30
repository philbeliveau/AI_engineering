# Story 4.5: Source Management Tools (list_sources, compare_sources)

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **end user**,
I want to list available knowledge sources and compare extractions across sources,
So that I can understand what knowledge is available and see different perspectives.

## Acceptance Criteria

1. **Given** I am connected to the MCP server
   **When** I call `list_sources`
   **Then** all available sources are returned with metadata (title, authors, type, extraction counts)
   **And** the tool is available at Public tier (FR4.6)

2. **Given** the list_sources response is formatted
   **When** the structure is validated
   **Then** it follows the annotated format: `{results: [...], metadata: {query, sources_cited, result_count, search_type}}`

3. **Given** I am connected to the MCP server with a valid API key
   **When** I call `compare_sources` with a topic and source IDs
   **Then** extractions from specified sources on that topic are returned side-by-side
   **And** Claude can synthesize across conflicting recommendations

4. **Given** the compare_sources response is formatted
   **When** the structure is validated
   **Then** it follows the annotated format with grouped results by source

5. **Given** compare_sources is accessed without valid API key
   **When** the request is processed
   **Then** the tool returns 401 Unauthorized (Registered tier required - FR4.7)

6. **Given** either tool is called with an invalid source_id
   **When** the source lookup fails
   **Then** a proper error response is returned with error code and message

## Dependency Analysis

**Depends On (MUST BE COMPLETE):**
- **Story 4.1:** FastAPI Server with MCP Integration - Provides server.py base with MCP mounting (ready-for-dev)
- **Story 4.3:** Extraction Query Tools - Provides patterns for MongoDB querying, response models, and tool structure (ready-for-dev)
- **Story 4.4:** Methodology Query Tool - Provides API key authentication middleware pattern (ready-for-dev)

**Blocks:**
- **Story 4.6:** Response Models and Error Handling - This story contributes to overall response standardization

**Context:** This story implements TWO tools with DIFFERENT access tiers:
1. `list_sources` - Public tier (no auth required)
2. `compare_sources` - Registered tier (API key required)

## Tasks / Subtasks

- [ ] **Task 1: Verify Prerequisites and Previous Story Patterns** (AC: All dependencies available)
  - [ ] 1.1: Confirm Story 4.1 patterns exist (check for `packages/mcp-server/src/server.py` or create minimal version)
  - [ ] 1.2: Review Story 4.3/4.4 implementation patterns for response models and MongoDB querying
  - [ ] 1.3: Verify MongoDB client exists: `packages/mcp-server/src/storage/mongodb.py`
  - [ ] 1.4: Verify auth middleware exists: `packages/mcp-server/src/middleware/auth.py`
  - [ ] 1.5: Review sources collection schema in MongoDB

- [ ] **Task 2: Create Source Result Models** (AC: #1, #2)
  - [ ] 2.1: Create or extend `packages/mcp-server/src/models/responses.py`
  - [ ] 2.2: Implement `SourceResult` Pydantic model:
    - `id: str` - Source ID
    - `title: str` - Source title (e.g., "LLM Handbook")
    - `authors: list[str]` - Author names
    - `type: str` - Source type ("book", "paper", "case_study")
    - `path: str` - Original file path
    - `ingested_at: str` - ISO 8601 datetime
    - `status: str` - Ingestion status ("complete", "processing", "failed")
    - `extraction_counts: dict[str, int]` - Count by extraction type (e.g., {"decision": 15, "pattern": 8})
  - [ ] 2.3: Create `SourceListResponse` wrapper with `results` and `metadata`
  - [ ] 2.4: Ensure model follows architecture.md naming conventions (snake_case fields)

- [ ] **Task 3: Create Comparison Result Models** (AC: #3, #4)
  - [ ] 3.1: Implement `ComparisonResult` Pydantic model:
    - `source_id: str` - Source being compared
    - `source_title: str` - Human-readable source name
    - `extractions: list[ExtractionSummary]` - Extractions on the topic from this source
  - [ ] 3.2: Implement `ExtractionSummary` Pydantic model:
    - `id: str` - Extraction ID
    - `type: str` - Extraction type (decision, pattern, warning, methodology)
    - `title: str` - Extraction title/name/question
    - `summary: str` - Brief summary of the extraction content
    - `topics: list[str]` - Topic tags
  - [ ] 3.3: Create `CompareSourcesResponse` wrapper with grouped results and metadata

- [ ] **Task 4: Extend MongoDB Client for Source Operations** (AC: #1, #3, #6)
  - [ ] 4.1: Ensure `packages/mcp-server/src/storage/mongodb.py` exists with read-only client
  - [ ] 4.2: Add `list_sources()` method to fetch all sources with metadata
  - [ ] 4.3: Add `get_source_by_id(source_id: str)` method for source lookups
  - [ ] 4.4: Add `count_extractions_by_source(source_id: str)` method to get extraction counts
  - [ ] 4.5: Add `get_extractions_for_comparison(source_ids: list[str], topic: str)` method
  - [ ] 4.6: Follow project-context.md:71-77 - MCP server is READ-ONLY

- [ ] **Task 5: Implement list_sources Tool** (AC: #1, #2, #6)
  - [ ] 5.1: Create `packages/mcp-server/src/tools/sources.py`
  - [ ] 5.2: Implement FastAPI endpoint:
    ```python
    @app.get("/list_sources", operation_id="list_sources")
    async def list_sources() -> SourceListResponse:
    ```
  - [ ] 5.3: Query MongoDB sources collection for all sources
  - [ ] 5.4: For each source, count extractions by type using aggregation
  - [ ] 5.5: Map source documents to `SourceResult` model
  - [ ] 5.6: Construct response with `results` and `metadata` (search_type="list")
  - [ ] 5.7: Add structured logging with structlog
  - [ ] 5.8: Handle empty sources case (return `{results: [], metadata: {...}}`)
  - [ ] 5.9: No authentication required (Public tier)

- [ ] **Task 6: Implement compare_sources Tool** (AC: #3, #4, #5, #6)
  - [ ] 6.1: Add to `packages/mcp-server/src/tools/sources.py`
  - [ ] 6.2: Implement FastAPI endpoint:
    ```python
    @app.get("/compare_sources", operation_id="compare_sources")
    async def compare_sources(
        topic: str = Query(..., description="Topic to compare across sources"),
        source_ids: list[str] = Query(..., description="Source IDs to compare"),
        api_key: str = Depends(verify_registered_tier)
    ) -> CompareSourcesResponse:
    ```
  - [ ] 6.3: Validate all source_ids exist (return 404 for invalid IDs)
  - [ ] 6.4: Query extractions for each source filtered by topic
  - [ ] 6.5: Group results by source for side-by-side comparison
  - [ ] 6.6: Create extraction summaries with key fields highlighted
  - [ ] 6.7: Construct response with grouped results and metadata
  - [ ] 6.8: Add structured logging with structlog
  - [ ] 6.9: Handle no extractions found (return empty arrays per source)

- [ ] **Task 7: Register Tools with FastAPI-MCP** (AC: #1, #3)
  - [ ] 7.1: Import sources router in `packages/mcp-server/src/server.py`
  - [ ] 7.2: Include router with FastAPI app
  - [ ] 7.3: Verify MCP exposes both tools with correct `operation_id`
  - [ ] 7.4: Add docstrings with clear descriptions for LLM context

- [ ] **Task 8: Write Tests** (AC: #1-6)
  - [ ] 8.1: Create `packages/mcp-server/tests/test_tools/test_sources.py`
  - [ ] 8.2: Test list_sources returns all sources with extraction counts
  - [ ] 8.3: Test list_sources response format matches annotated structure
  - [ ] 8.4: Test list_sources works without authentication (Public tier)
  - [ ] 8.5: Test compare_sources with valid API key returns grouped results
  - [ ] 8.6: Test compare_sources without API key returns 401
  - [ ] 8.7: Test compare_sources with invalid API key returns 401
  - [ ] 8.8: Test compare_sources with invalid source_id returns 404
  - [ ] 8.9: Test compare_sources response format matches annotated structure
  - [ ] 8.10: Follow project-context.md:110-142 (Testing patterns)

- [ ] **Task 9: Update Documentation** (AC: All)
  - [ ] 9.1: Add `list_sources` and `compare_sources` to README.md API documentation
  - [ ] 9.2: Document tier requirements for each tool
  - [ ] 9.3: Add usage examples showing comparison workflow

## Dev Notes

### Epic 4 Context

This is **Story 4.5** in Epic 4 (Knowledge Query Interface). It implements the final two tools that enable source exploration and cross-source comparison.

**Epic 4 Progress:**
- 4.1: FastAPI Server with MCP Integration (ready-for-dev)
- 4.2: Semantic Search Tool (ready-for-dev)
- 4.3: get_decisions, get_patterns, get_warnings - Public tier (ready-for-dev)
- 4.4: get_methodologies - Registered tier (ready-for-dev)
- **4.5: list_sources (Public), compare_sources (Registered) - THIS STORY**
- 4.6: Response Models and Error Handling (backlog)

### Mixed Access Tiers

From architecture.md:330-341 - MCP Tools Tier Access:

| Tool | Purpose | Tier |
|------|---------|------|
| `list_sources` | List available knowledge sources | **Public** |
| `compare_sources` | Compare extractions across sources | **Registered** |

**Implementation:**
- `list_sources`: No authentication, 100 req/hr per IP
- `compare_sources`: Requires `X-API-Key` header, 1000 req/hr

### Source Document Structure

From MongoDB `sources` collection (architecture.md:260-280):

```python
{
    "_id": ObjectId,
    "type": str,           # "book", "paper", "case_study"
    "title": str,          # Human-readable title
    "authors": [str],      # Author names
    "path": str,           # Original file path
    "ingested_at": str,    # ISO 8601 datetime
    "status": str,         # "pending", "processing", "complete", "failed"
    "metadata": {}         # Additional metadata
}
```

### Extraction Aggregation for Counts

To get extraction counts per source, use MongoDB aggregation:

```python
async def count_extractions_by_source(self, source_id: str) -> dict[str, int]:
    """Count extractions grouped by type for a source.

    Returns: {"decision": 5, "pattern": 3, "warning": 2, ...}
    """
    pipeline = [
        {"$match": {"source_id": source_id}},
        {"$group": {"_id": "$type", "count": {"$sum": 1}}}
    ]
    cursor = self.db.extractions.aggregate(pipeline)
    results = await cursor.to_list(length=None)
    return {doc["_id"]: doc["count"] for doc in results}
```

### Response Format: list_sources

```python
class SourceResult(BaseModel):
    id: str
    title: str
    authors: list[str]
    type: str
    path: str
    ingested_at: str
    status: str
    extraction_counts: dict[str, int]  # {"decision": 15, "pattern": 8, ...}

class SourceListResponse(BaseModel):
    results: list[SourceResult]
    metadata: ResponseMetadata

# Example response:
{
    "results": [
        {
            "id": "507f1f77bcf86cd799439011",
            "title": "LLM Handbook",
            "authors": ["John Smith", "Jane Doe"],
            "type": "book",
            "path": "/data/raw/llm-handbook.pdf",
            "ingested_at": "2025-12-28T10:30:00Z",
            "status": "complete",
            "extraction_counts": {
                "decision": 45,
                "pattern": 23,
                "warning": 18,
                "methodology": 12
            }
        }
    ],
    "metadata": {
        "query": "all",
        "sources_cited": [],
        "result_count": 1,
        "search_type": "list"
    }
}
```

### Response Format: compare_sources

```python
class ExtractionSummary(BaseModel):
    id: str
    type: str              # "decision", "pattern", "warning", "methodology"
    title: str             # Name/question/title from extraction
    summary: str           # Brief summary for comparison
    topics: list[str]

class ComparisonResult(BaseModel):
    source_id: str
    source_title: str
    extractions: list[ExtractionSummary]

class CompareSourcesResponse(BaseModel):
    results: list[ComparisonResult]  # Grouped by source
    metadata: ResponseMetadata

# Example response:
{
    "results": [
        {
            "source_id": "507f1f77bcf86cd799439011",
            "source_title": "LLM Handbook",
            "extractions": [
                {
                    "id": "ext-001",
                    "type": "decision",
                    "title": "Which embedding model to use?",
                    "summary": "Recommends all-MiniLM-L6-v2 for balance of speed and quality",
                    "topics": ["embeddings", "rag"]
                }
            ]
        },
        {
            "source_id": "507f1f77bcf86cd799439012",
            "source_title": "RAG Survey 2024",
            "extractions": [
                {
                    "id": "ext-002",
                    "type": "decision",
                    "title": "Embedding model selection",
                    "summary": "Suggests BGE-large for highest accuracy despite slower speed",
                    "topics": ["embeddings", "rag"]
                }
            ]
        }
    ],
    "metadata": {
        "query": "embeddings",
        "sources_cited": ["LLM Handbook", "RAG Survey 2024"],
        "result_count": 2,
        "search_type": "comparison"
    }
}
```

### Comparison Query Pattern

```python
async def get_extractions_for_comparison(
    self,
    source_ids: list[str],
    topic: str,
    limit_per_source: int = 10
) -> dict[str, list[dict]]:
    """Get extractions from multiple sources for a topic.

    Returns: {source_id: [extraction1, extraction2, ...], ...}
    """
    results = {}
    for source_id in source_ids:
        query = {
            "source_id": source_id,
            "topics": topic
        }
        cursor = self.db.extractions.find(query).limit(limit_per_source)
        extractions = await cursor.to_list(length=limit_per_source)
        results[source_id] = extractions
    return results
```

### Core Architectural Insight

From architecture.md Key Insight:

**"Extractions are for NAVIGATION, Claude is for SYNTHESIS."**

The `compare_sources` tool enables Claude to:
1. See extractions from multiple sources on the same topic
2. Identify conflicting recommendations
3. Synthesize across sources with source attribution
4. Provide nuanced guidance acknowledging different perspectives

Example user query:
> "What do different books say about chunk size for RAG?"

Claude calls `compare_sources(topic="chunking", source_ids=[...])` and receives grouped extractions, then synthesizes: "The LLM Handbook recommends 512 tokens while RAG Survey 2024 suggests 256-1024 depending on use case..."

### File Structure After Implementation

```
packages/mcp-server/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── server.py                 # Register sources router
│   ├── exceptions.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py               # verify_registered_tier (from Story 4.4)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── responses.py          # Add SourceResult, ComparisonResult, etc.
│   │   └── requests.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── mongodb.py            # Add list_sources, get_extractions_for_comparison
│   │
│   └── tools/
│       ├── __init__.py
│       ├── decisions.py          # From Story 4.3
│       ├── patterns.py           # From Story 4.3
│       ├── warnings.py           # From Story 4.3
│       ├── methodologies.py      # From Story 4.4
│       ├── sources.py            # NEW: list_sources, compare_sources
│       └── health.py
│
└── tests/
    ├── conftest.py               # Add source fixtures
    └── test_tools/
        ├── test_decisions.py
        ├── test_patterns.py
        ├── test_warnings.py
        ├── test_methodologies.py
        └── test_sources.py       # NEW: This story
```

### Testing Patterns

```python
# tests/test_tools/test_sources.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.server import app

VALID_API_KEY = "test-key-123"

@pytest.fixture
def mock_api_keys(monkeypatch):
    """Set up test API keys."""
    monkeypatch.setenv("REGISTERED_API_KEYS", VALID_API_KEY)

# list_sources tests (Public tier - no auth)

@pytest.mark.asyncio
async def test_list_sources_no_auth_required():
    """Test that list_sources works without authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/list_sources")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "metadata" in data
        assert data["metadata"]["search_type"] == "list"

@pytest.mark.asyncio
async def test_list_sources_includes_extraction_counts():
    """Test that each source includes extraction counts by type."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/list_sources")
        assert response.status_code == 200
        data = response.json()
        for source in data["results"]:
            assert "extraction_counts" in source
            assert isinstance(source["extraction_counts"], dict)

# compare_sources tests (Registered tier - auth required)

@pytest.mark.asyncio
async def test_compare_sources_requires_api_key():
    """Test that endpoint returns 401 without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/compare_sources",
            params={"topic": "rag", "source_ids": ["id1", "id2"]}
        )
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.asyncio
async def test_compare_sources_with_valid_key(mock_api_keys):
    """Test successful comparison with valid API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/compare_sources",
            params={"topic": "rag", "source_ids": ["id1", "id2"]},
            headers={"X-API-Key": VALID_API_KEY}
        )
        # May return 200 or 404 depending on mock data
        assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_compare_sources_invalid_source_id(mock_api_keys):
    """Test 404 response for invalid source_id."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/compare_sources",
            params={"topic": "rag", "source_ids": ["nonexistent-id"]},
            headers={"X-API-Key": VALID_API_KEY}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"

@pytest.mark.asyncio
async def test_compare_sources_response_format(mock_api_keys, mock_sources):
    """Test response is grouped by source."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/compare_sources",
            params={"topic": "rag", "source_ids": mock_sources},
            headers={"X-API-Key": VALID_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        for result in data["results"]:
            assert "source_id" in result
            assert "source_title" in result
            assert "extractions" in result
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
- architecture.md:260-280 - MongoDB Sources Collection Schema
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

### Error Handling for Invalid Source IDs

```python
from fastapi import HTTPException
from src.exceptions import NotFoundError

async def validate_source_ids(self, source_ids: list[str]) -> list[dict]:
    """Validate all source IDs exist and return source documents.

    Raises NotFoundError if any source_id is invalid.
    """
    sources = []
    for source_id in source_ids:
        source = await self.db.sources.find_one({"_id": ObjectId(source_id)})
        if not source:
            raise NotFoundError(
                resource="source",
                id=source_id
            )
        sources.append(source)
    return sources
```

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

**Test Endpoints:**
```bash
# list_sources - Public (no auth)
curl http://localhost:8000/list_sources

# compare_sources - Registered (requires API key)
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/compare_sources?topic=rag&source_ids=id1&source_ids=id2"
```

**Run Tests:**
```bash
cd packages/mcp-server
uv run pytest tests/test_tools/test_sources.py -v
```

### Success Criteria Summary

**Story Complete When:**
1. `list_sources` endpoint exists and returns all sources
2. `list_sources` includes extraction_counts per source
3. `list_sources` works without authentication (Public tier)
4. `compare_sources` endpoint exists and groups results by source
5. `compare_sources` returns 401 without API key
6. `compare_sources` returns 401 with invalid API key
7. `compare_sources` returns 404 for invalid source_ids
8. Both responses follow annotated format `{results: [...], metadata: {...}}`
9. All tests passing: `uv run pytest tests/test_tools/test_sources.py`
10. No linting errors: `uv run ruff check .`

### References

**Source Documents:**
- [Architecture: MCP Tools Tier Access] architecture.md#L330-341
- [Architecture: Tiered Authentication Model] architecture.md#L314-328
- [Architecture: MongoDB Sources Collection] architecture.md#L260-280
- [Architecture: API Response Format] architecture.md#L464-476
- [Architecture: Error Response Format] architecture.md#L478-485
- [Architecture: Key Insight - Navigation vs Synthesis] architecture.md#L113-119
- [Project Context: Framework Rules] project-context.md#L79-108
- [Project Context: Anti-Patterns] project-context.md#L218-225
- [Epics: Story 4.5 Requirements] epics.md#L580-599
- [Story 4.4: Methodology Query Tool Pattern] 4-4-methodology-query-tool-get-methodologies.md
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
