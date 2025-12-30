# Story 4.6: Response Models and Error Handling

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want standardized response models and error handling for all MCP tools,
So that clients receive consistent, well-structured responses.

## Acceptance Criteria

1. **Given** any MCP tool is called successfully
   **When** the response is returned
   **Then** success responses follow the format: `{results: [...], metadata: {query, sources_cited, result_count, search_type}}`

2. **Given** any MCP tool encounters an error
   **When** the error response is returned
   **Then** error responses follow the format: `{error: {code, message, details}}`

3. **Given** a client sends an invalid request
   **When** the request is processed
   **Then** a 400 VALIDATION_ERROR response is returned with specific field details

4. **Given** a client requests a non-existent resource
   **When** the request is processed
   **Then** a 404 NOT_FOUND response is returned with the resource identifier

5. **Given** a client exceeds rate limits
   **When** the request is processed
   **Then** a 429 RATE_LIMITED response is returned with `retry_after` information

6. **Given** an unexpected server error occurs
   **When** the error is handled
   **Then** a 500 INTERNAL_ERROR response is returned with correlation ID for debugging

7. **Given** any successful search query
   **When** performance is measured
   **Then** NFR1 (<500ms search latency) is achieved

## Dependency Analysis

**Depends On (MUST BE COMPLETE):**
- **Story 4.1:** FastAPI Server with MCP Integration - Provides server.py base with MCP mounting
- **Story 4.2:** Semantic Search Tool - Provides search_knowledge endpoint using these models
- **Story 4.3:** Extraction Query Tools - Uses these response models for get_decisions, get_patterns, get_warnings
- **Story 4.4:** Methodology Query Tool - Uses these response models for get_methodologies
- **Story 4.5:** Source Management Tools - Uses these response models for list_sources, compare_sources

**Blocks:**
- **Epic 5:** Production Deployment - Error handling is prerequisite for rate limiting and auth middleware

**Context:** This story consolidates and standardizes the response models and error handling patterns across ALL MCP tools. It ensures consistency across the entire API surface and provides the foundation for production-ready error handling.

## Tasks / Subtasks

- [ ] **Task 1: Create Base Response Models** (AC: #1, #7)
  - [ ] 1.1: Create/verify `packages/mcp-server/src/models/responses.py` exists
  - [ ] 1.2: Implement `ResponseMetadata` Pydantic model:
    - `query: str` - Original query or filter
    - `sources_cited: list[str]` - Human-readable source references
    - `result_count: int` - Number of results returned
    - `search_type: Literal["semantic", "filtered"]` - Query type
    - `latency_ms: Optional[int]` - Response time for NFR1 tracking
  - [ ] 1.3: Implement generic `ApiResponse[T]` wrapper model:
    - `results: list[T]` - Type-safe results array
    - `metadata: ResponseMetadata` - Standard metadata
  - [ ] 1.4: Ensure all models use `snake_case` field names (project-context.md:52)

- [ ] **Task 2: Create Type-Specific Result Models** (AC: #1)
  - [ ] 2.1: Implement `SearchResult` for semantic search:
    - `id: str`, `content: str`, `score: float`, `source_title: str`, `source_id: str`, `chunk_id: str`, `extraction_type: Optional[str]`
  - [ ] 2.2: Implement `DecisionResult` for decisions:
    - `id: str`, `question: str`, `options: list[str]`, `considerations: list[str]`, `recommended_approach: Optional[str]`, `topics: list[str]`, `source_title: str`, `source_id: str`, `chunk_id: str`
  - [ ] 2.3: Implement `PatternResult` for patterns:
    - `id: str`, `name: str`, `problem: str`, `solution: str`, `code_example: Optional[str]`, `context: Optional[str]`, `trade_offs: Optional[list[str]]`, `topics: list[str]`, `source_title: str`, `source_id: str`, `chunk_id: str`
  - [ ] 2.4: Implement `WarningResult` for warnings:
    - `id: str`, `title: str`, `description: str`, `symptoms: Optional[list[str]]`, `consequences: Optional[list[str]]`, `prevention: Optional[str]`, `topics: list[str]`, `source_title: str`, `source_id: str`, `chunk_id: str`
  - [ ] 2.5: Implement `MethodologyResult` for methodologies:
    - `id: str`, `name: str`, `steps: list[str]`, `prerequisites: Optional[list[str]]`, `outputs: Optional[list[str]]`, `topics: list[str]`, `source_title: str`, `source_id: str`, `chunk_id: str`
  - [ ] 2.6: Implement `SourceResult` for list_sources:
    - `id: str`, `title: str`, `authors: list[str]`, `type: str`, `extraction_counts: dict[str, int]`, `ingested_at: str`

- [ ] **Task 3: Create Error Response Models** (AC: #2, #3, #4, #5, #6)
  - [ ] 3.1: Create `packages/mcp-server/src/models/errors.py`
  - [ ] 3.2: Implement `ErrorCode` Enum:
    - `VALIDATION_ERROR` (400), `NOT_FOUND` (404), `UNAUTHORIZED` (401), `RATE_LIMITED` (429), `INTERNAL_ERROR` (500)
  - [ ] 3.3: Implement `ErrorDetail` Pydantic model:
    - `code: ErrorCode` - Standard error code
    - `message: str` - Human-readable error message
    - `details: dict[str, Any]` - Additional context (field errors, resource ID, etc.)
  - [ ] 3.4: Implement `ErrorResponse` wrapper:
    - `error: ErrorDetail` - Single error object
  - [ ] 3.5: Add `retry_after: Optional[int]` field for rate limit errors

- [ ] **Task 4: Create Custom Exception Hierarchy** (AC: #2, #3, #4, #5, #6)
  - [ ] 4.1: Create/update `packages/mcp-server/src/exceptions.py`
  - [ ] 4.2: Implement base `KnowledgeError` exception:
    - `code: ErrorCode`, `message: str`, `details: dict`, `status_code: int`
  - [ ] 4.3: Implement `ValidationError(KnowledgeError)`:
    - status_code=400, code=VALIDATION_ERROR
  - [ ] 4.4: Implement `NotFoundError(KnowledgeError)`:
    - status_code=404, code=NOT_FOUND
    - Constructor: `(resource: str, id: str)`
  - [ ] 4.5: Implement `UnauthorizedError(KnowledgeError)`:
    - status_code=401, code=UNAUTHORIZED
  - [ ] 4.6: Implement `RateLimitedError(KnowledgeError)`:
    - status_code=429, code=RATE_LIMITED
    - Constructor includes `retry_after: int`
  - [ ] 4.7: Implement `InternalError(KnowledgeError)`:
    - status_code=500, code=INTERNAL_ERROR
    - Auto-generates `correlation_id` for debugging

- [ ] **Task 5: Create Global Exception Handlers** (AC: #2, #3, #4, #5, #6)
  - [ ] 5.1: Create `packages/mcp-server/src/middleware/error_handlers.py`
  - [ ] 5.2: Implement `knowledge_error_handler` for `KnowledgeError` exceptions:
    - Returns `JSONResponse` with `ErrorResponse` body
    - Sets appropriate HTTP status code
  - [ ] 5.3: Implement `validation_exception_handler` for Pydantic `ValidationError`:
    - Maps Pydantic errors to VALIDATION_ERROR format
    - Includes field-level error details
  - [ ] 5.4: Implement `generic_exception_handler` for uncaught exceptions:
    - Logs error with structlog including stack trace
    - Returns generic INTERNAL_ERROR response (no sensitive info)
    - Generates correlation_id for log correlation
  - [ ] 5.5: Add rate limit header `Retry-After` for RATE_LIMITED errors

- [ ] **Task 6: Register Exception Handlers with FastAPI** (AC: #2-6)
  - [ ] 6.1: Update `packages/mcp-server/src/server.py`
  - [ ] 6.2: Import exception handlers from middleware
  - [ ] 6.3: Register handlers using `app.add_exception_handler()`
  - [ ] 6.4: Ensure handlers are registered before MCP mounting

- [ ] **Task 7: Create Response Builder Utilities** (AC: #1, #7)
  - [ ] 7.1: Create `packages/mcp-server/src/utils/response_builder.py`
  - [ ] 7.2: Implement `build_response()` function:
    ```python
    def build_response(
        results: list[T],
        query: str,
        sources: list[str],
        search_type: str,
        start_time: float
    ) -> ApiResponse[T]
    ```
  - [ ] 7.3: Automatically calculate `latency_ms` from `start_time`
  - [ ] 7.4: Validate results are list (never return bare results)
  - [ ] 7.5: Add `build_empty_response()` for empty result sets

- [ ] **Task 8: Update All Existing Tools to Use Standard Models** (AC: #1, #2)
  - [ ] 8.1: Update `tools/search.py` to use `ApiResponse[SearchResult]` and `build_response()`
  - [ ] 8.2: Update `tools/decisions.py` to use `ApiResponse[DecisionResult]`
  - [ ] 8.3: Update `tools/patterns.py` to use `ApiResponse[PatternResult]`
  - [ ] 8.4: Update `tools/warnings.py` to use `ApiResponse[WarningResult]`
  - [ ] 8.5: Update `tools/methodologies.py` to use `ApiResponse[MethodologyResult]`
  - [ ] 8.6: Update `tools/sources.py` to use `ApiResponse[SourceResult]`
  - [ ] 8.7: Replace any custom error handling with `KnowledgeError` exceptions

- [ ] **Task 9: Write Comprehensive Tests** (AC: #1-7)
  - [ ] 9.1: Create `packages/mcp-server/tests/test_models/test_responses.py`
  - [ ] 9.2: Create `packages/mcp-server/tests/test_models/test_errors.py`
  - [ ] 9.3: Create `packages/mcp-server/tests/test_middleware/test_error_handlers.py`
  - [ ] 9.4: Test success response format for each result type
  - [ ] 9.5: Test error response format for each error code
  - [ ] 9.6: Test exception handler converts KnowledgeError correctly
  - [ ] 9.7: Test Pydantic validation errors are properly formatted
  - [ ] 9.8: Test uncaught exceptions return safe INTERNAL_ERROR
  - [ ] 9.9: Test latency_ms calculation is accurate

- [ ] **Task 10: Update Documentation** (AC: All)
  - [ ] 10.1: Add response format documentation to README.md
  - [ ] 10.2: Add error code reference table
  - [ ] 10.3: Add example responses for each tool
  - [ ] 10.4: Document retry_after behavior for rate limiting

## Dev Notes

### Epic 4 Context

This is **Story 4.6** in Epic 4 (Knowledge Query Interface). It provides the **foundational response models and error handling** that all other tools in Epic 4 depend on for consistency.

**Epic 4 Progress:**
- 4.1: FastAPI Server with MCP Integration (ready-for-dev)
- 4.2: Semantic Search Tool - search_knowledge (ready-for-dev)
- 4.3: get_decisions, get_patterns, get_warnings - Public tier (ready-for-dev)
- 4.4: get_methodologies - Registered tier (ready-for-dev)
- 4.5: list_sources, compare_sources (backlog)
- **4.6: Response Models and Error Handling (THIS STORY)**

### Architecture Compliance

This story implements the **API & Communication Patterns** from architecture.md:330-359:

**MCP Tools Tier Access:**
| Tool | Purpose | Tier |
|------|---------|------|
| `search_knowledge` | Semantic search across all content | Public |
| `get_decisions` | Query decision extractions by topic | Public |
| `get_patterns` | Query code pattern extractions | Public |
| `get_warnings` | Query warning extractions | Public |
| `get_methodologies` | Query methodology extractions | Registered |
| `list_sources` | List available knowledge sources | Public |
| `compare_sources` | Compare extractions across sources | Registered |

**Critical Boundary:** The MCP server is READ-ONLY. Never write to databases from `packages/mcp-server`.

### Response Format (MANDATORY)

From architecture.md:342-358 and project-context.md:79-102:

**Success Response Format:**
```python
class ApiResponse(BaseModel, Generic[T]):
    results: list[T]
    metadata: ResponseMetadata

class ResponseMetadata(BaseModel):
    query: str              # Original query or filter
    sources_cited: list[str]  # e.g., ["LLM Handbook Ch.5", "RAG Survey 2024"]
    result_count: int       # Number of results
    search_type: Literal["semantic", "filtered"]
    latency_ms: Optional[int] = None  # For NFR1 tracking
```

**Example Success Response:**
```json
{
  "results": [
    {
      "id": "decision-123",
      "question": "Which chunking strategy to use?",
      "options": ["fixed-size", "semantic", "recursive"],
      "considerations": ["Document type", "Query patterns"],
      "recommended_approach": "Semantic for technical docs",
      "topics": ["rag", "chunking"],
      "source_title": "LLM Engineer's Handbook",
      "source_id": "src-001",
      "chunk_id": "chunk-042"
    }
  ],
  "metadata": {
    "query": "chunking",
    "sources_cited": ["LLM Engineer's Handbook Ch.5"],
    "result_count": 1,
    "search_type": "filtered",
    "latency_ms": 45
  }
}
```

### Error Response Format (MANDATORY)

From architecture.md:478-497 and project-context.md:93-102:

**Error Response Format:**
```python
class ErrorResponse(BaseModel):
    error: ErrorDetail

class ErrorDetail(BaseModel):
    code: ErrorCode  # "VALIDATION_ERROR" | "NOT_FOUND" | "UNAUTHORIZED" | "RATE_LIMITED" | "INTERNAL_ERROR"
    message: str
    details: dict[str, Any] = {}
    retry_after: Optional[int] = None  # Only for RATE_LIMITED
```

**Error Codes:**
| Code | HTTP Status | Usage |
|------|-------------|-------|
| `VALIDATION_ERROR` | 400 | Invalid input parameters |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

**Example Error Responses:**

**Validation Error (400):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "topic": "Topic must be at least 2 characters"
    }
  }
}
```

**Not Found Error (404):**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Source with id 'xyz' not found",
    "details": {
      "resource": "source",
      "id": "xyz"
    }
  }
}
```

**Rate Limited Error (429):**
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Please retry after 60 seconds.",
    "details": {
      "limit": 100,
      "window": "hour"
    },
    "retry_after": 60
  }
}
```

**Internal Error (500):**
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "correlation_id": "abc123-def456"
    }
  }
}
```

### Exception Hierarchy Pattern

From architecture.md:544-560:

```python
# packages/mcp-server/src/exceptions.py
from enum import Enum
from typing import Any, Optional

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class KnowledgeError(Exception):
    """Base exception for all Knowledge Pipeline errors."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class NotFoundError(KnowledgeError):
    """Resource not found error."""

    def __init__(self, resource: str, id: str):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=f"{resource} with id '{id}' not found",
            status_code=404,
            details={"resource": resource, "id": id}
        )

class ValidationError(KnowledgeError):
    """Request validation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            status_code=400,
            details=details
        )

class UnauthorizedError(KnowledgeError):
    """Authentication/authorization error."""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=401
        )

class RateLimitedError(KnowledgeError):
    """Rate limit exceeded error."""

    def __init__(self, retry_after: int, limit: int, window: str):
        super().__init__(
            code=ErrorCode.RATE_LIMITED,
            message=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
            status_code=429,
            details={"limit": limit, "window": window, "retry_after": retry_after}
        )
        self.retry_after = retry_after

class InternalError(KnowledgeError):
    """Internal server error with correlation ID."""

    def __init__(self, correlation_id: str):
        super().__init__(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred",
            status_code=500,
            details={"correlation_id": correlation_id}
        )
```

### Global Exception Handler Pattern

```python
# packages/mcp-server/src/middleware/error_handlers.py
import uuid
import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from src.exceptions import KnowledgeError, InternalError, ErrorCode
from src.models.errors import ErrorResponse, ErrorDetail

logger = structlog.get_logger()

async def knowledge_error_handler(request: Request, exc: KnowledgeError) -> JSONResponse:
    """Handle KnowledgeError exceptions."""
    logger.warning(
        "knowledge_error",
        code=exc.code.value,
        message=exc.message,
        path=request.url.path
    )

    response = ErrorResponse(
        error=ErrorDetail(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            retry_after=getattr(exc, "retry_after", None)
        )
    )

    headers = {}
    if exc.code == ErrorCode.RATE_LIMITED and hasattr(exc, "retry_after"):
        headers["Retry-After"] = str(exc.retry_after)

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
        headers=headers
    )

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic/FastAPI validation errors."""
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors[field] = error["msg"]

    logger.warning(
        "validation_error",
        errors=errors,
        path=request.url.path
    )

    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid request parameters",
            details=errors
        )
    )

    return JSONResponse(status_code=400, content=response.model_dump())

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions safely."""
    correlation_id = str(uuid.uuid4())

    logger.error(
        "internal_error",
        correlation_id=correlation_id,
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        exc_info=True  # Include stack trace in logs
    )

    # Return safe error without sensitive details
    error = InternalError(correlation_id=correlation_id)
    response = ErrorResponse(
        error=ErrorDetail(
            code=error.code,
            message=error.message,
            details=error.details
        )
    )

    return JSONResponse(status_code=500, content=response.model_dump())
```

### Register Handlers in server.py

```python
# packages/mcp-server/src/server.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_mcp import FastApiMCP

from src.exceptions import KnowledgeError
from src.middleware.error_handlers import (
    knowledge_error_handler,
    validation_exception_handler,
    generic_exception_handler
)

app = FastAPI(
    title="Knowledge Pipeline MCP Server",
    description="MCP server providing AI engineering knowledge tools"
)

# Register exception handlers BEFORE adding routes
app.add_exception_handler(KnowledgeError, knowledge_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Import and include routers
from src.tools import search, decisions, patterns, warnings, methodologies, sources

app.include_router(search.router)
app.include_router(decisions.router)
# ... etc

# Mount MCP AFTER all routes are defined
mcp = FastApiMCP(app, name="Knowledge Pipeline MCP")
mcp.mount_http()
```

### Response Builder Utility

```python
# packages/mcp-server/src/utils/response_builder.py
import time
from typing import TypeVar, Generic
from src.models.responses import ApiResponse, ResponseMetadata

T = TypeVar("T")

def build_response(
    results: list[T],
    query: str,
    sources: list[str],
    search_type: str,
    start_time: float
) -> ApiResponse[T]:
    """Build standardized API response with timing."""
    latency_ms = int((time.time() - start_time) * 1000)

    return ApiResponse(
        results=results,
        metadata=ResponseMetadata(
            query=query,
            sources_cited=sources,
            result_count=len(results),
            search_type=search_type,
            latency_ms=latency_ms
        )
    )

def build_empty_response(
    query: str,
    search_type: str,
    start_time: float
) -> ApiResponse:
    """Build response for empty result sets."""
    return build_response(
        results=[],
        query=query,
        sources=[],
        search_type=search_type,
        start_time=start_time
    )
```

### File Structure After Implementation

```
packages/mcp-server/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── server.py                   # Register exception handlers
│   ├── exceptions.py               # KnowledgeError hierarchy
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── responses.py            # ApiResponse, ResponseMetadata, *Result
│   │   ├── errors.py               # ErrorCode, ErrorDetail, ErrorResponse
│   │   ├── requests.py
│   │   └── shared.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handlers.py       # Global exception handlers
│   │   ├── rate_limit.py
│   │   ├── auth.py
│   │   └── logging.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── mongodb.py
│   │   └── qdrant.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py               # Uses ApiResponse[SearchResult]
│   │   ├── decisions.py            # Uses ApiResponse[DecisionResult]
│   │   ├── patterns.py             # Uses ApiResponse[PatternResult]
│   │   ├── warnings.py             # Uses ApiResponse[WarningResult]
│   │   ├── methodologies.py        # Uses ApiResponse[MethodologyResult]
│   │   ├── sources.py              # Uses ApiResponse[SourceResult]
│   │   └── health.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── response_builder.py     # build_response(), build_empty_response()
│
└── tests/
    ├── conftest.py
    ├── test_models/
    │   ├── test_responses.py       # Test response model serialization
    │   └── test_errors.py          # Test error model serialization
    └── test_middleware/
        └── test_error_handlers.py  # Test exception handler behavior
```

### NFR1 Performance Tracking

From architecture.md:294 and PRD NFR-1:

**Target:** <500ms search latency for all MCP tool queries

**Implementation:**
1. Track `start_time = time.time()` at endpoint entry
2. Calculate `latency_ms` in `build_response()` utility
3. Include in response metadata for client visibility
4. Log latency via structlog for monitoring

```python
@app.get("/search_knowledge", operation_id="search_knowledge")
async def search_knowledge(query: str) -> ApiResponse[SearchResult]:
    """Semantic search across all content."""
    start_time = time.time()  # Start timing

    results = await perform_search(query)

    return build_response(
        results=results,
        query=query,
        sources=extract_sources(results),
        search_type="semantic",
        start_time=start_time  # Calculate latency
    )
```

### Testing Pattern

```python
# tests/test_models/test_responses.py
import pytest
from src.models.responses import ApiResponse, ResponseMetadata, DecisionResult

def test_api_response_format():
    """Test ApiResponse follows required format."""
    result = DecisionResult(
        id="test-1",
        question="Which approach?",
        options=["A", "B"],
        considerations=["Speed", "Cost"],
        recommended_approach="A",
        topics=["testing"],
        source_title="Test Book",
        source_id="src-1",
        chunk_id="chunk-1"
    )

    response = ApiResponse(
        results=[result],
        metadata=ResponseMetadata(
            query="test",
            sources_cited=["Test Book"],
            result_count=1,
            search_type="filtered",
            latency_ms=42
        )
    )

    data = response.model_dump()
    assert "results" in data
    assert "metadata" in data
    assert data["metadata"]["result_count"] == 1
    assert data["metadata"]["latency_ms"] == 42

# tests/test_models/test_errors.py
import pytest
from src.models.errors import ErrorResponse, ErrorDetail, ErrorCode

def test_error_response_format():
    """Test ErrorResponse follows required format."""
    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.NOT_FOUND,
            message="Source with id 'xyz' not found",
            details={"resource": "source", "id": "xyz"}
        )
    )

    data = response.model_dump()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "resource" in data["error"]["details"]

# tests/test_middleware/test_error_handlers.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.server import app
from src.exceptions import NotFoundError

@pytest.mark.asyncio
async def test_not_found_error_response():
    """Test NotFoundError returns proper JSON response."""
    # Add test endpoint that raises NotFoundError
    @app.get("/test-not-found")
    async def test_endpoint():
        raise NotFoundError(resource="source", id="test-123")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/test-not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
        assert "test-123" in data["error"]["message"]
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
- architecture.md:342-358 - API Response Format
- architecture.md:478-497 - Error Response Format
- architecture.md:544-560 - Error Handling Pattern

### Critical Anti-Patterns to Avoid

From project-context.md:218-225:

**NEVER DO:**
- Write to databases from `packages/mcp-server` (read-only)
- Use `print()` - always `structlog`
- Hardcode connection strings - use Settings
- Return bare results - always wrap in `{results, metadata}`
- Catch bare `Exception` - use specific types (except in generic_exception_handler)
- Use `pip` or manual venv - always `uv run`
- Commit `.env` files or secrets
- Expose stack traces in API responses - use correlation_id

### Previous Story Intelligence

**From Stories 4.3 and 4.4:**
- Response models already partially defined for DecisionResult, PatternResult, WarningResult, MethodologyResult
- Authentication pattern established in Story 4.4 for Registered tier
- MongoDB query patterns established for extraction queries
- FastAPI-MCP integration pattern with `operation_id` established

**What This Story Adds:**
- Centralizes all response models in one location
- Adds proper Generic[T] typing for type-safe responses
- Implements complete error handling hierarchy
- Adds global exception handlers for consistent error responses
- Adds latency tracking for NFR1 compliance
- Adds response builder utilities for DRY code

### Git Intelligence

**Recent Commits:**
- `c8b7933` feat(story-1-2): docker compose infrastructure setup
- `4a59247` feat(story-1-1): initialize monorepo structure
- `44323de` Definition of architecture
- `bc247ce` first commit

**Patterns Observed:**
- Conventional commit format: `feat(story-X-X): description`
- Stories 1.1 and 1.2 completed - foundation is ready
- Epic 4 stories are all in ready-for-dev or backlog status

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

**Test Error Handling:**
```bash
# Test validation error
curl -X GET "http://localhost:8000/get_decisions?topic=" | jq .

# Test not found (will need test endpoint)
curl -X GET "http://localhost:8000/sources/nonexistent" | jq .

# Test successful response
curl -X GET "http://localhost:8000/get_decisions?topic=rag" | jq .
```

**Run Tests:**
```bash
cd packages/mcp-server
uv run pytest tests/test_models/ tests/test_middleware/ -v
```

**Lint:**
```bash
cd packages/mcp-server
uv run ruff check .
uv run ruff check --fix .
```

### Success Criteria Summary

**Story Complete When:**
1. All response models centralized in `models/responses.py`
2. All error models defined in `models/errors.py`
3. Exception hierarchy implemented in `exceptions.py`
4. Global exception handlers registered in `server.py`
5. Response builder utility created in `utils/response_builder.py`
6. All existing tools updated to use standardized models
7. Latency tracking implemented for NFR1 compliance
8. All tests passing: `uv run pytest tests/test_models/ tests/test_middleware/`
9. No linting errors: `uv run ruff check .`
10. Error responses match documented format exactly

### References

**Source Documents:**
- [Architecture: API Response Format] architecture.md#L342-358
- [Architecture: Error Response Format] architecture.md#L478-497
- [Architecture: Error Handling Pattern] architecture.md#L544-560
- [Architecture: MCP Tools] architecture.md#L330-341
- [Project Context: Framework Rules] project-context.md#L79-108
- [Project Context: Anti-Patterns] project-context.md#L218-225
- [Epics: Story 4.6 Requirements] epics.md#L600-618
- [Story 4.3: Extraction Query Tools] 4-3-extraction-query-tools-get-decisions-get-patterns-get-warnings.md
- [Story 4.4: Methodology Query Tool] 4-4-methodology-query-tool-get-methodologies.md

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent during implementation_

### Debug Log References

_To be filled by dev agent during implementation_

### Completion Notes List

_To be filled by dev agent during implementation_

### File List

_To be filled by dev agent during implementation_
