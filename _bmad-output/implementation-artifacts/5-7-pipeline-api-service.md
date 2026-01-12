# Story 5.7: Pipeline API Service

Status: review

## Story

As a **builder/external system**,
I want a dedicated FastAPI service that exposes ingestion and extraction endpoints with project namespace isolation,
so that I can programmatically ingest documents and trigger knowledge extraction without using CLI commands.

## Acceptance Criteria

1. **Given** the Pipeline API service is running
   **When** I POST to `/ingest` with a file upload and `X-Project-ID: test-project` header
   **Then** the file is ingested and I receive `{source_id, title, chunk_count, total_tokens, duration, project_id, status}` response

2. **Given** the Pipeline API service is running
   **When** I POST to `/ingest/url` with `{url, category, tags, year}` JSON body and `X-Project-ID` header
   **Then** the URL content is ingested and I receive the same response format as file upload

3. **Given** a source has been ingested (chunks exist)
   **When** I POST to `/extract/{source_id}` with `X-Project-ID` header
   **Then** LLM extraction runs and I receive `{source_id, total_extractions, extraction_counts, duration, project_id}` response

4. **Given** a source_id exists in the system
   **When** I GET `/sources/{source_id}` with `X-Project-ID` header
   **Then** I receive `{source_id, title, status, chunk_count, extraction_count, project_id}` response

5. **Given** the Pipeline API service is running
   **When** I GET `/health`
   **Then** I receive `{status: "healthy", mongodb: bool, qdrant: bool}` response

6. **Given** no `X-Project-ID` header is provided
   **When** I make any request to the API
   **Then** the request uses project_id `"default"` as fallback

7. **Given** the API receives a malformed request
   **When** validation fails
   **Then** I receive a structured error response `{error: {code, message, details}}`

## Tasks / Subtasks

- [x] **Task 1: Create FastAPI Application** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] 1.1: Create `packages/pipeline/api.py` with FastAPI app instance
  - [x] 1.2: Add X-Project-ID header extraction middleware
  - [x] 1.3: Create Pydantic request/response models (`IngestResponse`, `ExtractResponse`, `SourceResponse`, `IngestURLRequest`)
  - [x] 1.4: Add global exception handlers returning structured error format

- [x] **Task 2: Implement Ingestion Endpoints** (AC: 1, 2, 6)
  - [x] 2.1: Implement `POST /ingest` with multipart file upload
  - [x] 2.2: Implement `POST /ingest/url` with JSON body
  - [x] 2.3: Pass project_id from header to `PipelineConfig`
  - [x] 2.4: Use existing `IngestionPipeline.ingest()` and `ingest_url()` methods

- [x] **Task 3: Implement Extraction Endpoint** (AC: 3)
  - [x] 3.1: Implement `POST /extract/{source_id}` endpoint
  - [x] 3.2: Use existing `ExtractionPipeline.extract_hierarchical()` method
  - [x] 3.3: Return extraction counts by type from result

- [x] **Task 4: Implement Source Status Endpoint** (AC: 4)
  - [x] 4.1: Implement `GET /sources/{source_id}` endpoint
  - [x] 4.2: Query MongoDB for source metadata and status
  - [x] 4.3: Count chunks and extractions for the source

- [x] **Task 5: Implement Health Check** (AC: 5)
  - [x] 5.1: Implement `GET /health` endpoint
  - [x] 5.2: Test MongoDB connectivity
  - [x] 5.3: Test Qdrant connectivity

- [x] **Task 6: Create Dockerfile** (AC: all)
  - [x] 6.1: Create `packages/pipeline/Dockerfile.api` based on `Dockerfile.streamlit`
  - [x] 6.2: Change CMD to run `uvicorn api:app`
  - [x] 6.3: Ensure same dependencies available

- [x] **Task 7: Create Railway Config** (AC: all)
  - [x] 7.1: Create `packages/pipeline/railway-api.toml`
  - [x] 7.2: Configure health check for `/health`

- [x] **Task 8: Local Testing** (AC: all)
  - [x] 8.1: Write tests for all endpoints
  - [x] 8.2: Test full workflow: ingest file → check status → extract
  - [x] 8.3: Test project isolation via different X-Project-ID headers

## Dev Notes

### Critical Architecture Patterns

**Response Format (MANDATORY):**
All endpoints MUST return wrapped responses per `project-context.md`:
```python
# Success response
{
    "results": [...],  # or single object for non-list responses
    "metadata": {
        "query": str,
        "sources_cited": [],
        "result_count": int,
        "search_type": str
    }
}

# Error response
{
    "error": {
        "code": "VALIDATION_ERROR" | "NOT_FOUND" | "RATE_LIMITED" | "INTERNAL_ERROR",
        "message": str,
        "details": {}
    }
}
```

**Note:** For this API, the simplified response models in the plan are acceptable as they're direct action responses, not search results. However, error handling MUST follow the structured format.

**Async Patterns:**
- All FastAPI endpoints MUST be `async def`
- CPU-bound operations (embedding, extraction) run in existing sync code - wrap with `run_in_executor` if blocking becomes an issue

**Project Namespacing:**
- Extract `X-Project-ID` header, default to `"default"` if missing
- Pass to `PipelineConfig.project_id` for ingestion
- MongoDB collections are automatically prefixed via `settings.sources_collection` etc.
- Qdrant uses single `knowledge_vectors` collection with `project_id` payload filter

### Existing Code to Use

**IngestionPipeline** (`src/ingestion/pipeline.py:198`):
```python
class IngestionPipeline:
    def __init__(self, config: Optional[PipelineConfig] = None):
        # Already supports PipelineConfig with project_id

    def ingest(self, file_path: Path) -> IngestionResult:
        # Returns IngestionResult dataclass

    def ingest_url(self, url: str) -> IngestionResult:
        # Same return type
```

**PipelineConfig** (`src/ingestion/pipeline.py:79`):
```python
class PipelineConfig(BaseModel):
    project_id: Optional[str] = None  # Override PROJECT_ID env var
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    year: Optional[int] = Field(default=None, ge=1900, le=2100)
```

**ExtractionPipeline** (`src/extraction/pipeline.py`):
- Use `extract_hierarchical()` method for running all extractors on a source

**MongoDBClient** (`src/storage/mongodb.py`):
- Use `get_source_by_id()` for status endpoint
- Collection names via `settings.sources_collection`, `settings.chunks_collection`, `settings.extractions_collection`

### File Structure Requirements

```
packages/pipeline/
├── api.py                    # NEW: FastAPI application
├── Dockerfile.api            # NEW: Docker build for API
├── railway-api.toml          # NEW: Railway deployment config
├── src/
│   ├── ingestion/
│   │   └── pipeline.py       # EXISTING: IngestionPipeline
│   ├── extraction/
│   │   └── pipeline.py       # EXISTING: ExtractionPipeline
│   └── storage/
│       └── mongodb.py        # EXISTING: MongoDBClient
```

### API Implementation Pattern

```python
# api.py skeleton
from fastapi import FastAPI, UploadFile, Form, Request, HTTPException
from pydantic import BaseModel
import structlog

from src.ingestion.pipeline import IngestionPipeline, PipelineConfig, IngestionResult
from src.extraction.pipeline import ExtractionPipeline
from src.storage.mongodb import MongoDBClient
from src.config import settings

logger = structlog.get_logger()

app = FastAPI(title="Knowledge Pipeline API")

# Response models
class IngestResponse(BaseModel):
    source_id: str
    title: str
    chunk_count: int
    total_tokens: int
    duration: float
    project_id: str
    status: str = "complete"

class ExtractResponse(BaseModel):
    source_id: str
    total_extractions: int
    extraction_counts: dict[str, int]
    duration: float
    project_id: str

class SourceResponse(BaseModel):
    source_id: str
    title: str
    status: str
    chunk_count: int
    extraction_count: int
    project_id: str

# Helper to get project_id from header
def get_project_id(request: Request) -> str:
    return request.headers.get("X-Project-ID", "default")

@app.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile,
    category: str = Form(default="reference"),
    tags: str = Form(default=""),
    year: int = Form(default=None),
    request: Request = None,
) -> IngestResponse:
    project_id = get_project_id(request)
    # Save to temp file, run pipeline
    # Return IngestResponse
```

### Testing Requirements

**Integration Tests Required:**
```bash
# Test full workflow
curl -X POST http://localhost:8000/ingest \
  -H "X-Project-ID: test-project" \
  -F "file=@test.pdf" \
  -F "category=reference"

curl http://localhost:8000/sources/{source_id} \
  -H "X-Project-ID: test-project"

curl -X POST http://localhost:8000/extract/{source_id} \
  -H "X-Project-ID: test-project"
```

**Project Isolation Test:**
- Ingest with `X-Project-ID: project-a`
- Verify MongoDB collections are `project-a_sources`, `project-a_chunks`
- Verify Qdrant vectors have `project_id: "project-a"` payload

### Library/Framework Requirements

**Already in pyproject.toml:**
- `fastapi>=0.115` - API framework
- `uvicorn` - ASGI server
- `pydantic>=2.0` - Request/response models
- `python-multipart` - File upload support (verify this is present, add if not)

**Verify dependency:**
```bash
cd packages/pipeline
uv add python-multipart  # Required for file uploads
```

### Security Considerations

- **No API key required** (public access per plan)
- Rate limiting NOT in scope for this story (MCP server handles that)
- Input validation via Pydantic models
- File type validation via existing adapter registry

### Project Structure Notes

- Alignment with existing monorepo structure in `packages/pipeline/`
- API is a new entry point alongside existing Streamlit app
- Shares all `src/` modules with Streamlit
- Separate Docker image but same dependencies

### References

- [Source: _bmad-output/architecture.md#Data-Architecture] - MongoDB/Qdrant patterns
- [Source: _bmad-output/architecture.md#API-Response-Format] - Response structure requirements
- [Source: _bmad-output/project-context.md#Framework-Rules] - FastAPI async patterns
- [Source: packages/pipeline/src/ingestion/pipeline.py] - IngestionPipeline implementation
- [Source: packages/pipeline/src/config.py] - Settings and collection naming
- [Source: User plan provided in workflow args] - Complete API specification

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 17 unit tests passing: `uv run pytest tests/test_api/test_api.py -v`

### Completion Notes List

**Files Created:**
- `packages/pipeline/api.py` - FastAPI application with all endpoints
- `packages/pipeline/Dockerfile.api` - Docker build for API service
- `packages/pipeline/railway-api.toml` - Railway deployment configuration
- `packages/pipeline/tests/test_api/__init__.py` - Test package init
- `packages/pipeline/tests/test_api/test_api.py` - 17 comprehensive unit tests

**Files Modified:**
- `packages/pipeline/pyproject.toml` - Added `python-multipart>=0.0.9` dependency

**Deployment:**
- Deployed to Railway with PROJECT_ID=enact
- Environment variables: MONGODB_URI, QDRANT_URL, QDRANT_API_KEY, ANTHROPIC_API_KEY

**Endpoints Implemented:**
- `POST /ingest` - File upload ingestion with multipart form
- `POST /ingest/url` - URL-based ingestion with JSON body
- `POST /extract/{source_id}` - Run hierarchical extraction
- `GET /sources/{source_id}` - Get source status and counts
- `GET /health` - Health check with MongoDB/Qdrant status

**Test Coverage:**
- Helper function tests (get_project_id)
- Health endpoint tests (healthy, degraded states)
- Ingest file endpoint tests (success, project header)
- Ingest URL endpoint tests (success, project header)
- Extract endpoint tests (success, project header)
- Source status endpoint tests (success, project header)
- Error handling tests (404, 400, 500)
- Project isolation tests

### Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-12 | Story created from user plan via create-story workflow | Claude Opus 4.5 |
| 2026-01-12 | Implementation complete - all 8 tasks done, deployed to Railway | Claude Opus 4.5 |
