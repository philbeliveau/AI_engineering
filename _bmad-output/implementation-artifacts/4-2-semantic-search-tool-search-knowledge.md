# Story 4.2: Semantic Search Tool (search_knowledge)

Status: ready-for-dev

## Story

As an **end user**,
I want to search across all knowledge content semantically,
so that I can find relevant information using natural language queries.

## Acceptance Criteria

1. **Given** I am connected to the MCP server
   **When** I call `search_knowledge` with a query string
   **Then** semantically similar chunks and extractions are returned

2. **Given** a valid query is submitted
   **When** the search executes
   **Then** results are ranked by relevance score (descending)

3. **Given** search results are returned
   **When** I inspect each result
   **Then** source attribution is included (source_id, chunk_id, title, position)

4. **Given** any `search_knowledge` call
   **When** the response is returned
   **Then** it follows the annotated format with `results` and `metadata`

5. **Given** the tool's tier requirements
   **When** accessed without authentication
   **Then** the tool is available at Public tier (FR4.1)

6. **Given** the performance requirements
   **When** a search query executes
   **Then** response time is <500ms (NFR1)

## Tasks / Subtasks

- [ ] **Task 1: Create request/response models** (AC: 3, 4)
  - [ ] 1.1 Create `SearchKnowledgeRequest` Pydantic model in `src/models/requests.py`
  - [ ] 1.2 Create `SearchResult` model with source attribution fields
  - [ ] 1.3 Create `SearchKnowledgeResponse` model with `results` array and `metadata` dict
  - [ ] 1.4 Add `SearchMetadata` model (query, sources_cited, result_count, search_type)

- [ ] **Task 2: Implement Qdrant search client** (AC: 1, 2)
  - [ ] 2.1 Create `QdrantClient` wrapper in `src/storage/qdrant.py`
  - [ ] 2.2 Implement `search_vectors()` method for semantic search
  - [ ] 2.3 Add payload filtering support for `type` and `topics` fields
  - [ ] 2.4 Ensure 384-dimension vector compatibility (all-MiniLM-L6-v2)

- [ ] **Task 3: Implement embedding generation** (AC: 1)
  - [ ] 3.1 Create `EmbeddingService` in `src/embeddings/` using fastembed
  - [ ] 3.2 Implement `embed_query(text: str) -> list[float]` method
  - [ ] 3.3 Ensure model loads once and is reused (singleton pattern)
  - [ ] 3.4 Document as sync function (CPU-bound per project-context.md)

- [ ] **Task 4: Implement MongoDB enrichment client** (AC: 3)
  - [ ] 4.1 Create `MongoDBClient` wrapper in `src/storage/mongodb.py`
  - [ ] 4.2 Implement `get_source_by_id()` for source metadata enrichment
  - [ ] 4.3 Implement `get_chunk_by_id()` for chunk content retrieval
  - [ ] 4.4 Implement `get_extraction_by_id()` for extraction details

- [ ] **Task 5: Create search_knowledge endpoint** (AC: 1, 2, 3, 4)
  - [ ] 5.1 Create `src/tools/search.py` with FastAPI route
  - [ ] 5.2 Implement endpoint logic: embed query → search Qdrant → enrich from MongoDB
  - [ ] 5.3 Add explicit `operation_id="search_knowledge"` to endpoint decorator
  - [ ] 5.4 Return wrapped response with `results` and `metadata`

- [ ] **Task 6: Register endpoint with MCP** (AC: 5)
  - [ ] 6.1 Import search router in `src/server.py`
  - [ ] 6.2 Include router with appropriate tag (e.g., `tags=["search"]`)
  - [ ] 6.3 Verify MCP exposes the tool after `mcp.mount_http()`

- [ ] **Task 7: Write tests** (AC: all)
  - [ ] 7.1 Create `tests/test_tools/test_search.py`
  - [ ] 7.2 Write unit tests for embedding generation
  - [ ] 7.3 Write unit tests for Qdrant search with mocked client
  - [ ] 7.4 Write integration test for full search flow
  - [ ] 7.5 Add performance test validating <500ms response time

- [ ] **Task 8: Add structured logging** (AC: 6)
  - [ ] 8.1 Add structlog logging for search operations
  - [ ] 8.2 Log query, result_count, and latency_ms for each search

## Dev Notes

### Critical Architecture Patterns

**Dual-Package Boundary (CRITICAL):**
- `packages/mcp-server` is READ-ONLY from databases
- NEVER write to MongoDB or Qdrant from this package
- All data originates from `packages/pipeline`

**Response Format (MANDATORY):**
```python
{
    "results": [
        {
            "id": str,
            "score": float,
            "type": str,  # "chunk" | "extraction"
            "content": str,
            "source": {
                "source_id": str,
                "title": str,
                "authors": list[str],
                "position": {"chapter": str, "section": str, "page": int}
            }
        }
    ],
    "metadata": {
        "query": str,
        "sources_cited": list[str],
        "result_count": int,
        "search_type": "semantic"
    }
}
```

**Error Response Format:**
```python
{
    "error": {
        "code": "VALIDATION_ERROR" | "NOT_FOUND" | "RATE_LIMITED" | "INTERNAL_ERROR",
        "message": str,
        "details": {}
    }
}
```

### Qdrant Configuration

| Setting | Value | Source |
|---------|-------|--------|
| Vector dimensions | 384 | all-MiniLM-L6-v2 |
| Distance metric | Cosine | architecture.md |
| Collections | `chunks`, `extractions` | architecture.md |
| Payload fields | `source_id`, `chunk_id`, `type`, `topics` | architecture.md |

**Search both collections and merge results:**
```python
# Search chunks collection
chunk_results = qdrant.search("chunks", query_vector, limit=10)

# Search extractions collection
extraction_results = qdrant.search("extractions", query_vector, limit=10)

# Merge and re-rank by score
all_results = sorted(chunk_results + extraction_results, key=lambda x: x.score, reverse=True)
```

### Embedding Configuration

**Model:** all-MiniLM-L6-v2 via fastembed
**Dimensions:** 384
**Library for MCP Server:** fastembed (NOT sentence-transformers - see pyproject.toml)

```python
from fastembed import TextEmbedding

# Singleton pattern - load once
_embedding_model: TextEmbedding | None = None

def get_embedding_model() -> TextEmbedding:
    """Get or create the embedding model singleton."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embedding_model

def embed_query(text: str) -> list[float]:
    """Sync function - CPU-bound embedding generation."""
    model = get_embedding_model()
    # fastembed returns generator, convert to list
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()
```

### FastAPI + MCP Integration

**Explicit operation_id is REQUIRED** for clean MCP tool naming:
```python
from fastapi import APIRouter, Query
from src.models.requests import SearchKnowledgeRequest
from src.models.responses import SearchKnowledgeResponse

router = APIRouter()

@router.post(
    "/search_knowledge",
    operation_id="search_knowledge",  # REQUIRED - explicit tool name
    response_model=SearchKnowledgeResponse,
    tags=["search"]
)
async def search_knowledge(
    query: str = Query(..., description="Natural language search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results to return")
) -> SearchKnowledgeResponse:
    """
    Search across all knowledge content semantically.

    Returns chunks and extractions ranked by relevance to your query.
    Available at Public tier - no authentication required.
    """
    # Implementation here
    pass
```

**Server setup (src/server.py):**
```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from src.tools.search import router as search_router

app = FastAPI(
    title="Knowledge MCP Server",
    version="0.1.0"
)

# Include routers BEFORE creating MCP
app.include_router(search_router)

# Create and mount MCP AFTER all routes defined
mcp = FastApiMCP(app)
mcp.mount_http()  # Exposes at /mcp
```

### MongoDB Collections Reference

```python
# sources collection
{
    "_id": ObjectId,
    "type": str,  # "book", "paper", "case_study"
    "title": str,
    "authors": list[str],
    "path": str,
    "ingested_at": str,  # ISO 8601
    "status": str,
    "metadata": dict,
    "schema_version": int
}

# chunks collection
{
    "_id": ObjectId,
    "source_id": str,
    "content": str,
    "position": {"chapter": str, "section": str, "page": int},
    "token_count": int,
    "schema_version": int
}

# extractions collection
{
    "_id": ObjectId,
    "source_id": str,
    "chunk_id": str,
    "type": str,  # "decision", "pattern", "warning", etc.
    "content": dict,
    "topics": list[str],
    "schema_version": int,
    "extracted_at": str
}
```

### Async Patterns

**All FastAPI endpoints MUST be async:**
```python
# CORRECT
@router.post("/search_knowledge")
async def search_knowledge(...):
    results = await qdrant_client.search(...)
    return response

# WRONG - never use sync endpoints
@router.post("/search_knowledge")
def search_knowledge(...):  # Missing async!
    ...
```

**CPU-bound helpers can be sync (documented):**
```python
def embed_query(text: str) -> list[float]:
    """Sync function - CPU-bound embedding generation."""
    return model.embed(text).tolist()
```

### Configuration Pattern

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    qdrant_url: str = "http://localhost:6333"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    environment: str = "local"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Test Organization

```
packages/mcp-server/tests/
├── conftest.py              # Shared fixtures
├── test_tools/
│   └── test_search.py       # search_knowledge tests
├── test_storage/
│   ├── test_qdrant.py
│   └── test_mongodb.py
└── test_embeddings/
    └── test_embedding_service.py
```

**Test patterns:**
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_search_knowledge_returns_results():
    """Test that search returns properly formatted results."""
    # Mock Qdrant client
    mock_qdrant = AsyncMock()
    mock_qdrant.search.return_value = [
        {"id": "1", "score": 0.95, "payload": {...}}
    ]

    # Test endpoint
    response = await search_knowledge(query="test", limit=10)

    assert "results" in response
    assert "metadata" in response
    assert response["metadata"]["search_type"] == "semantic"
```

### Project Structure Notes

**File locations for this story:**
```
packages/mcp-server/
├── src/
│   ├── config.py                    # Settings (if not exists)
│   ├── server.py                    # FastAPI app + MCP mount
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding_service.py     # NEW: fastembed wrapper
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── qdrant.py                # NEW: Qdrant client
│   │   └── mongodb.py               # NEW: MongoDB client
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py              # NEW: SearchKnowledgeRequest
│   │   └── responses.py             # NEW: SearchKnowledgeResponse
│   └── tools/
│       ├── __init__.py
│       └── search.py                # NEW: search_knowledge endpoint
└── tests/
    ├── conftest.py                  # NEW: shared fixtures
    └── test_tools/
        └── test_search.py           # NEW: search tests
```

### Dependencies Already Installed

From `packages/mcp-server/pyproject.toml`:
- `fastapi>=0.115`
- `fastapi-mcp>=0.4.0`
- `qdrant-client>=1.13`
- `pymongo>=4.6.0`
- `fastembed>=0.2.0`
- `pydantic>=2.0`
- `pydantic-settings>=2.1.0`

**No additional dependencies needed.**

### References

- [Source: _bmad-output/architecture.md#Data-Architecture] - MongoDB collections and Qdrant configuration
- [Source: _bmad-output/architecture.md#API-Communication-Patterns] - Response format specifications
- [Source: _bmad-output/architecture.md#MCP-Tools] - Tool definitions and tier requirements
- [Source: _bmad-output/project-context.md#API-Response-Format] - Mandatory response wrapper
- [Source: _bmad-output/project-context.md#Async-Patterns] - Async/sync function guidelines
- [Source: _bmad-output/project-context.md#Testing-Rules] - Test organization and patterns
- [Source: _bmad-output/epics.md#Story-4.2] - Original story requirements

### Dependency on Story 4.1

**IMPORTANT:** This story depends on Story 4.1 (FastAPI Server with MCP Integration) being completed first.

If 4.1 is not done, you must first:
1. Create `src/server.py` with FastAPI app
2. Mount fastapi-mcp
3. Create `src/config.py` with Settings class
4. Verify the server starts with `uv run uvicorn src.server:app`

Check if `src/server.py` exists before starting. If not, complete the minimal 4.1 setup first.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### Change Log
| Task | Status | Notes |
|------|--------|-------|
