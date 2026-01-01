# Story 4.1: FastAPI Server with MCP Integration

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want a FastAPI server with fastapi-mcp integration,
So that MCP tools can be exposed to Claude Code clients.

## Acceptance Criteria

**Given** the knowledge-mcp package exists
**When** I run `uv run uvicorn src.server:app`
**Then** the FastAPI server starts on the configured port
**And** the `/mcp` endpoint is available via fastapi-mcp mounting
**And** health check endpoint returns server status
**And** server connects to MongoDB and Qdrant on startup

## Dependency Analysis

**Depends On (MUST BE COMPLETE):**
- **Story 1.1:** Initialize Monorepo Structure - Provides `packages/mcp-server/` package with pyproject.toml and uv environment (✅ DONE)
- **Story 1.2:** Docker Compose Infrastructure Setup - Provides local MongoDB (port 27017) and Qdrant (port 6333) for development (✅ IN REVIEW)
- **Story 1.4:** MongoDB Storage Client - Pattern reference for database connection (✅ READY)
- **Story 1.5:** Qdrant Storage Client - Pattern reference for vector database connection (✅ READY)

**Blocks:**
- **Story 4.2:** Semantic Search Tool - Needs server foundation to mount search endpoint
- **Story 4.3:** Extraction Query Tools - Needs server foundation to mount query endpoints
- **Story 4.4-4.6:** All remaining Epic 4 stories - Requires working MCP server

**Context:** This is the FIRST story in Epic 4, establishing the foundation for all MCP tools. All subsequent stories will add endpoints to this server.

## Tasks / Subtasks

- [x] **Task 1: Verify Prerequisites** (AC: All dependencies available)
  - [x] 1.1: Confirm Story 1.1 complete (mcp-server package exists): `ls packages/mcp-server/pyproject.toml`
  - [x] 1.2: Verify uv environment working: `cd packages/mcp-server && uv run python --version`
  - [x] 1.3: Confirm fastapi-mcp installed: `cd packages/mcp-server && uv run python -c "import fastapi_mcp; print(fastapi_mcp.__version__)"`
  - [x] 1.4: Verify Docker infrastructure running: `docker-compose ps` (MongoDB + Qdrant should be up)
  - [x] 1.5: Test MongoDB connection: `mongosh --eval 'db.version()'`
  - [x] 1.6: Test Qdrant connection: `curl http://localhost:6333/health`

- [x] **Task 2: Create Configuration Module** (AC: Server uses Pydantic Settings)
  - [x] 2.1: Create `packages/mcp-server/src/config.py`
  - [x] 2.2: Implement `Settings` class extending `pydantic_settings.BaseSettings`
  - [x] 2.3: Define configuration fields:
    - `environment: str` (default: "local")
    - `mongodb_uri: str` (default: "mongodb://localhost:27017")
    - `mongodb_database: str` (default: "knowledge_db")
    - `qdrant_url: str` (default: "http://localhost:6333")
    - `server_host: str` (default: "0.0.0.0")
    - `server_port: int` (default: 8000)
    - `log_level: str` (default: "INFO")
  - [x] 2.4: Configure `.env` file loading via `Config.env_file = ".env"`
  - [x] 2.5: Export singleton: `settings = Settings()`
  - [x] 2.6: Create `.env.example` with all config variables documented
  - [x] 2.7: Follow project-context.md:59-64 (Configuration pattern)

- [x] **Task 3: Create Exception Classes** (AC: Structured error handling)
  - [x] 3.1: Create `packages/mcp-server/src/exceptions.py`
  - [x] 3.2: Implement base `KnowledgeError(Exception)` with fields: `code`, `message`, `details`
  - [x] 3.3: Implement specific exceptions:
    - `NotFoundError(KnowledgeError)` - For missing resources
    - `ValidationError(KnowledgeError)` - For invalid input
    - `DatabaseError(KnowledgeError)` - For storage failures
    - `RateLimitError(KnowledgeError)` - For tier limits (future)
  - [x] 3.4: Follow project-context.md:66-69 (Error Handling pattern)
  - [x] 3.5: Follow architecture.md:486-496 (Error codes: VALIDATION_ERROR, NOT_FOUND, RATE_LIMITED, INTERNAL_ERROR)

- [x] **Task 4: Create Response Models** (AC: Standardized API responses)
  - [x] 4.1: Create `packages/mcp-server/src/models/` directory
  - [x] 4.2: Create `packages/mcp-server/src/models/responses.py`
  - [x] 4.3: Implement `ResponseMetadata` Pydantic model:
    - `query: str` - Original query string
    - `sources_cited: list[str]` - Attribution list
    - `result_count: int` - Number of results
    - `search_type: str` - "semantic" | "filtered" | "exact"
  - [x] 4.4: Implement generic `ApiResponse[T]` Pydantic model:
    - `results: list[T]` - Array of results
    - `metadata: ResponseMetadata` - Response metadata
  - [x] 4.5: Implement `ErrorDetail` Pydantic model:
    - `code: str` - Error code (VALIDATION_ERROR, NOT_FOUND, etc.)
    - `message: str` - Human-readable message
    - `details: dict` - Additional error context
  - [x] 4.6: Implement `ErrorResponse` Pydantic model:
    - `error: ErrorDetail`
  - [x] 4.7: Follow architecture.md:464-476 (Success response format)
  - [x] 4.8: Follow architecture.md:478-485 (Error response format)
  - [x] 4.9: Create `packages/mcp-server/src/models/__init__.py` with exports

- [x] **Task 5: Create Storage Clients (Read-Only)** (AC: Connect to databases on startup)
  - [x] 5.1: Create `packages/mcp-server/src/storage/` directory
  - [x] 5.2: Create `packages/mcp-server/src/storage/mongodb.py`
  - [x] 5.3: Implement `MongoDBClient` class (read-only operations):
    - Constructor takes Settings, initializes pymongo client
    - `async def connect()` - Establish connection
    - `async def disconnect()` - Close connection
    - `async def get_source(source_id: str)` - Retrieve source by ID
    - `async def list_sources(limit: int = 100)` - List all sources
    - `async def get_chunks(source_id: str)` - Get chunks for source
    - `async def get_extractions(type: str = None, topics: list[str] = None)` - Query extractions
  - [x] 5.4: Add structured logging with structlog for all database operations
  - [x] 5.5: Create `packages/mcp-server/src/storage/qdrant.py`
  - [x] 5.6: Implement `QdrantClient` class (read-only operations):
    - Constructor takes Settings, initializes qdrant_client
    - `async def connect()` - Establish connection
    - `async def disconnect()` - Close connection
    - `async def search_chunks(query_vector: list[float], limit: int = 10)` - Semantic search on chunks
    - `async def search_extractions(query_vector: list[float], filter: dict = None, limit: int = 10)` - Semantic search on extractions
  - [x] 5.7: Follow project-context.md:71-77 (Dual-Package Boundary: mcp-server is READ-ONLY)
  - [x] 5.8: Follow project-context.md:54-57 (Async patterns for endpoints)
  - [x] 5.9: Create `packages/mcp-server/src/storage/__init__.py` with exports

- [x] **Task 6: Create Health Check Endpoint** (AC: Health check returns server status)
  - [x] 6.1: Create `packages/mcp-server/src/tools/health.py`
  - [x] 6.2: Implement `async def health_check()` endpoint:
    - Returns `{"status": "healthy", "timestamp": <ISO-8601>, "services": {...}}`
  - [x] 6.3: Check MongoDB connection status (ping database)
  - [x] 6.4: Check Qdrant connection status (check cluster health)
  - [x] 6.5: Return HTTP 503 if any service is unavailable
  - [x] 6.6: Include version information from pyproject.toml
  - [x] 6.7: Create `packages/mcp-server/src/tools/__init__.py` with exports

- [x] **Task 7: Create FastAPI Server Application** (AC: Server starts on configured port)
  - [x] 7.1: Create `packages/mcp-server/src/server.py`
  - [x] 7.2: Initialize FastAPI app with metadata:
    - `title="AI Engineering Knowledge MCP Server"`
    - `version` from pyproject.toml
    - `description` from architecture doc
  - [x] 7.3: Configure structured logging with structlog
  - [x] 7.4: Add startup event handler:
    - Load configuration
    - Initialize MongoDB client and connect
    - Initialize Qdrant client and connect
    - Log successful startup
  - [x] 7.5: Add shutdown event handler:
    - Disconnect MongoDB client
    - Disconnect Qdrant client
    - Log graceful shutdown
  - [x] 7.6: Mount health check endpoint at `/health`
  - [x] 7.7: Follow project-context.md:54-57 (All endpoints MUST be async)
  - [x] 7.8: Follow project-context.md:152-164 (Structured logging MANDATORY)

- [x] **Task 8: Integrate fastapi-mcp** (AC: `/mcp` endpoint available)
  - [x] 8.1: Import `FastApiMCP` from fastapi_mcp
  - [x] 8.2: Initialize MCP after FastAPI app creation: `mcp = FastApiMCP(app)`
  - [x] 8.3: Call `mcp.mount_http()` to create `/mcp` endpoint (using HTTP transport)
  - [x] 8.4: Verify MCP protocol endpoint available
  - [x] 8.5: Follow architecture.md:169-189 (fastapi-mcp integration pattern)
  - [x] 8.6: Follow project-context.md:104-108 (MCP Integration rules)

- [x] **Task 9: Create Server Entry Point** (AC: `uv run uvicorn src.server:app` works)
  - [x] 9.1: Add `if __name__ == "__main__"` block to `server.py`
  - [x] 9.2: Import uvicorn
  - [x] 9.3: Call `uvicorn.run()` with:
    - `app="src.server:app"`
    - `host=settings.server_host`
    - `port=settings.server_port`
    - `reload=True` (for development)
    - `log_level=settings.log_level.lower()`
  - [x] 9.4: Create `main()` function for CLI entry point (matches pyproject.toml script)
  - [x] 9.5: Test server startup: `cd packages/mcp-server && uv run uvicorn src.server:app`
  - [x] 9.6: Verify server accessible at `http://localhost:8000`

- [x] **Task 10: Create Basic Integration Tests** (AC: Server functionality verified)
  - [x] 10.1: Create `packages/mcp-server/tests/test_server.py`
  - [x] 10.2: Use pytest-asyncio for async tests
  - [x] 10.3: Create fixtures in `conftest.py`:
    - `@pytest.fixture` for test app (TestClient)
    - `@pytest_asyncio.fixture` for async database clients
  - [x] 10.4: Test health check endpoint:
    - Returns 200 when services available
    - Returns 503 when services unavailable
    - Includes service status in response
  - [x] 10.5: Test MCP endpoint exists:
    - `/mcp` endpoint is accessible
    - Returns MCP protocol metadata
  - [x] 10.6: Test server startup/shutdown:
    - Database connections established
    - Database connections closed properly
  - [x] 10.7: Follow project-context.md:110-142 (Testing patterns)
  - [x] 10.8: Run tests: `cd packages/mcp-server && uv run pytest`

- [x] **Task 11: Create Documentation** (AC: Developer can run server)
  - [x] 11.1: Create `packages/mcp-server/README.md`
  - [x] 11.2: Document setup instructions:
    - Prerequisites (Docker, uv)
    - Environment configuration
    - Running the server locally
  - [x] 11.3: Document API endpoints:
    - `/health` - Health check
    - `/mcp` - MCP protocol endpoint
  - [x] 11.4: Document MCP client connection:
    - How Claude Code clients connect
    - Example MCP server configuration
  - [x] 11.5: Include troubleshooting section:
    - Common connection errors
    - Database connectivity issues
    - Port conflicts

## Dev Notes

### Epic 4 Foundation Story

This is **Story 4.1** - the foundational story for Epic 4 (Knowledge Query Interface). All subsequent stories in this epic will add MCP tools to this server.

**Epic 4 Context:**
- **Epic Goal:** End users can connect to the MCP server and query knowledge
- **Total Stories:** 6 stories (4.1 through 4.6)
- **FRs Covered:** FR4.1 through FR4.7 (7 MCP tools total)
- **This Story:** Establishes server infrastructure, no tools yet

**Subsequent Epic 4 Stories:**
- 4.2: `search_knowledge` tool (semantic search)
- 4.3: `get_decisions`, `get_patterns`, `get_warnings` tools
- 4.4: `get_methodologies` tool
- 4.5: `list_sources`, `compare_sources` tools
- 4.6: Response models and error handling (cross-cutting)

### Architecture Compliance

**Critical Architecture Decisions:**

1. **Dual-Package Boundary** (architecture.md:730-751, project-context.md:71-77)
   - `packages/pipeline`: Batch processing, WRITE to databases
   - `packages/mcp-server`: Real-time queries, READ from databases
   - **NEVER write to databases from mcp-server** (read-only operations only)

2. **API Response Format** (architecture.md:342-354, project-context.md:79-91)
   ```python
   {
     "results": [...],           # Always an array
     "metadata": {
       "query": str,             # Original query
       "sources_cited": [],      # Attribution required
       "result_count": int,
       "search_type": str        # "semantic" | "filtered"
     }
   }
   ```

3. **Error Response Format** (architecture.md:478-485, project-context.md:93-102)
   ```python
   {
     "error": {
       "code": "NOT_FOUND",      # VALIDATION_ERROR | NOT_FOUND | RATE_LIMITED | INTERNAL_ERROR
       "message": str,
       "details": {}
     }
   }
   ```

4. **Configuration Pattern** (project-context.md:59-64)
   - ALWAYS use `pydantic_settings.BaseSettings`
   - Load from `.env` files
   - Never hardcode secrets or connection strings
   - Export singleton: `settings = Settings()`

5. **Async Patterns** (project-context.md:54-57)
   - FastAPI endpoints: ALWAYS `async def` - no exceptions
   - CPU-bound helpers: sync OK but add docstring
   - Never block async endpoints with sync I/O

6. **Structured Logging** (project-context.md:152-164)
   - Use `structlog` only - never `print()` or `logging`
   - Always log with context:
     ```python
     logger.info("server_started", host=host, port=port, environment=env)
     ```

7. **MCP Integration** (architecture.md:169-189, project-context.md:104-108)
   - Mount MCP after all routes defined: `mcp.mount()`
   - MCP endpoint exposed at `/mcp`
   - Tools map 1:1 to FastAPI endpoints

### Technology Stack (Verified Versions)

From architecture.md:198-209 and project-context.md:17-42:

| Package | Version | Purpose |
|---------|---------|---------|
| Python | >=3.11 | Runtime |
| FastAPI | >=0.115 | API framework |
| fastapi-mcp | >=0.4.0 | MCP protocol layer |
| uvicorn | >=0.27.0 | ASGI server |
| pydantic | >=2.0 | Data validation |
| pydantic-settings | >=2.1.0 | Configuration |
| pymongo | >=4.6.0 | MongoDB client |
| qdrant-client | >=1.13 | Vector database client |
| fastembed | >=0.2.0 | Local embeddings (for search) |
| structlog | latest | Structured logging |

All dependencies already installed via Story 1.1 in `packages/mcp-server/pyproject.toml`.

### File Structure Requirements

From architecture.md:667-711:

```
packages/mcp-server/
├── pyproject.toml                  # ✅ EXISTS (Story 1.1)
├── uv.lock                         # ✅ EXISTS (Story 1.1)
├── .env.example                    # ❌ TO CREATE (Task 2)
├── README.md                       # ❌ TO CREATE (Task 11)
│
├── src/
│   ├── __init__.py                 # ✅ EXISTS
│   ├── config.py                   # ❌ TO CREATE (Task 2)
│   ├── server.py                   # ❌ TO CREATE (Task 7)
│   ├── exceptions.py               # ❌ TO CREATE (Task 3)
│   │
│   ├── tools/                      # ✅ EXISTS (minimal)
│   │   ├── __init__.py             # ✅ EXISTS
│   │   └── health.py               # ❌ TO CREATE (Task 6)
│   │
│   ├── storage/                    # ❌ TO CREATE (Task 5)
│   │   ├── __init__.py
│   │   ├── mongodb.py
│   │   └── qdrant.py
│   │
│   └── models/                     # ❌ TO CREATE (Task 4)
│       ├── __init__.py
│       ├── responses.py
│       └── requests.py             # (Future stories)
│
└── tests/                          # ✅ EXISTS (minimal)
    ├── __init__.py                 # ✅ EXISTS
    ├── conftest.py                 # ✅ EXISTS (minimal)
    └── test_server.py              # ❌ TO CREATE (Task 10)
```

### Naming Conventions

From project-context.md:47-60:

| Element | Convention | Example |
|---------|------------|---------|
| Files/modules | `snake_case.py` | `server.py`, `mongodb.py` |
| Classes | `PascalCase` | `MongoDBClient`, `QdrantClient`, `Settings` |
| Functions | `snake_case` | `health_check()`, `connect()` |
| Variables | `snake_case` | `mongodb_uri`, `server_port` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_PORT`, `MAX_RETRIES` |
| Pydantic models | `PascalCase` class, `snake_case` fields | `ResponseMetadata`, `query: str` |

### Previous Story Learnings

**From Story 1.1 (Initialize Monorepo):**
- ✅ Package structure: `packages/mcp-server/` exists with pyproject.toml
- ✅ Dependencies installed via `uv sync`
- ✅ Python 3.11 pinned with `uv python pin 3.11`
- ✅ All fastapi-mcp dependencies available

**From Story 1.2 (Docker Compose):**
- ✅ MongoDB accessible at `mongodb://localhost:27017`
- ✅ Qdrant accessible at `http://localhost:6333`
- ✅ Both services running via `docker-compose up -d`
- ⚠️ Story 1.2 currently in "review" status - verify services are running

**From Epic 3 Stories (Extraction System):**
- Pattern: All modules use structlog for logging
- Pattern: All storage clients use async where possible
- Pattern: Configuration via Pydantic Settings singleton
- Pattern: Exceptions inherit from base `KnowledgeError`

### Git Intelligence

**Recent Commits:**
- `4a59247` - feat(story-1-1): initialize monorepo structure
- `44323de` - Definition of architecture
- `bc247ce` - first commit

**Code Patterns from Recent Work:**
- Monorepo structure established in commit 4a59247
- All Python packages using uv for dependency management
- No server.py implementation exists yet - this story creates it from scratch

### Critical Anti-Patterns to Avoid

From project-context.md:218-225:

**NEVER DO:**
- ❌ Write to databases from `packages/mcp-server` (read-only)
- ❌ Use `print()` - always `structlog`
- ❌ Hardcode connection strings - use Settings
- ❌ Return bare results - always wrap in `{results, metadata}`
- ❌ Catch bare `Exception` - use specific types
- ❌ Use `pip` or manual venv - always `uv run`
- ❌ Commit `.env` files or secrets

### Testing Requirements

From project-context.md:110-142:

**Test Organization:**
- Tests in separate `tests/` directory (not alongside source)
- Mirror `src/` structure: `src/tools/` → `tests/test_tools/`
- Test files prefixed: `test_server.py`
- Shared fixtures in `conftest.py` at tests root

**Async Testing:**
- Use `pytest-asyncio` for all async tests
- Mark async tests: `@pytest.mark.asyncio`
- Async fixtures: `@pytest_asyncio.fixture`

**Test Patterns:**
- Unit tests: Mock external dependencies (MongoDB, Qdrant)
- Integration tests: Use Docker Compose services
- Never test against production databases
- Each test function tests ONE behavior

### Project Context Reference

**CRITICAL:** Read these files before implementation:
- `_bmad-output/project-context.md` - 85+ implementation rules
- `_bmad-output/architecture.md` - All architectural decisions

**Key Sections:**
- project-context.md:17-42 - Technology Stack & Versions
- project-context.md:47-77 - Critical Implementation Rules
- project-context.md:79-108 - Framework Rules (FastAPI + MCP)
- project-context.md:110-142 - Testing Rules
- project-context.md:144-178 - Code Quality & Style Rules
- project-context.md:218-243 - Critical Don't-Miss Rules
- architecture.md:169-189 - MCP Framework (fastapi-mcp)
- architecture.md:314-360 - Authentication & Security
- architecture.md:342-354 - API Response Format
- architecture.md:464-485 - Success/Error Response Formats

### Development Commands

**Start Infrastructure:**
```bash
docker-compose up -d
```

**Verify Services:**
```bash
# MongoDB
mongosh --eval 'db.version()'

# Qdrant
curl http://localhost:6333/health
```

**Run Server (Development):**
```bash
cd packages/mcp-server
uv run uvicorn src.server:app --reload
```

**Run Tests:**
```bash
cd packages/mcp-server
uv run pytest
uv run pytest -v  # Verbose output
uv run pytest tests/test_server.py  # Specific test file
```

**Check Code Quality:**
```bash
cd packages/mcp-server
uv run ruff check .
uv run ruff check --fix .
uv run mypy src/
```

### Success Criteria Summary

**Story Complete When:**
1. ✅ Server starts successfully: `uv run uvicorn src.server:app`
2. ✅ Health check returns 200: `curl http://localhost:8000/health`
3. ✅ MCP endpoint accessible: `curl http://localhost:8000/mcp`
4. ✅ MongoDB connection established on startup (logs confirm)
5. ✅ Qdrant connection established on startup (logs confirm)
6. ✅ All tests passing: `uv run pytest`
7. ✅ No linting errors: `uv run ruff check .`
8. ✅ README.md documents how to run server
9. ✅ .env.example exists with all config variables
10. ✅ Sprint status updated to "ready-for-dev" → stays "ready-for-dev" until dev-story completes

### References

**Source Documents:**
- [Architecture: MCP Framework] architecture.md#L169-189
- [Architecture: API Response Format] architecture.md#L342-354
- [Architecture: Error Response Format] architecture.md#L478-485
- [Architecture: Project Structure] architecture.md#L667-711
- [Architecture: Authentication Model] architecture.md#L314-360
- [Project Context: Technology Stack] project-context.md#L17-42
- [Project Context: Framework Rules] project-context.md#L79-108
- [Project Context: Testing Rules] project-context.md#L110-142
- [Project Context: Anti-Patterns] project-context.md#L218-225
- [Epics: Story 4.1 Requirements] epics.md#L510-524

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- **structlog issue**: ModuleNotFoundError for structlog - fixed by adding `uv add structlog`
- **pytest wrong Python**: Tests failed due to system pytest - fixed by using `uv run python -m pytest`
- **Dev deps missing**: Tests not found initially - fixed with `uv sync --all-extras`
- **MCP mount() hanging**: Default `mcp.mount()` caused tests to hang - fixed by using `mcp.mount_http()` per fastapi-mcp docs for HTTP transport
- **Linting errors**: 6 unused pytest imports - fixed with `uv run ruff check --fix .`
- **Port conflicts**: Server processes left running - fixed with `pkill -f "uvicorn"`
- **Pydantic deprecation**: Old `class Config` syntax - fixed by using `model_config = SettingsConfigDict(...)`

### Completion Notes List

1. **All 11 tasks completed successfully** following TDD (Red-Green-Refactor) approach
2. **93 tests pass** with `uv run python -m pytest` (expanded after code review)
3. **All linting checks pass** with `uv run ruff check .`
4. **Server starts successfully** and connects to MongoDB and Qdrant on startup
5. **Routes available**: `/openapi.json`, `/docs`, `/docs/oauth2-redirect`, `/redoc`, `/mcp`, `/health`
6. **MCP Integration**: Using `mount_http()` for HTTP transport (not SSE)
7. **Read-only clients**: Both MongoDBClient and QdrantStorageClient implement read-only operations per dual-package boundary
8. **Structured logging**: All modules use structlog (no print statements)
9. **Configuration**: Pydantic Settings with `.env` file support
10. **Exception hierarchy**: Base `KnowledgeError` with specialized exceptions (NotFoundError, ValidationError, DatabaseError, RateLimitError)

### File List

**Source Files Created:**
- `packages/mcp-server/src/config.py` - Configuration module with Pydantic Settings
- `packages/mcp-server/src/exceptions.py` - Exception hierarchy (KnowledgeError, NotFoundError, etc.)
- `packages/mcp-server/src/models/__init__.py` - Model exports
- `packages/mcp-server/src/models/responses.py` - Response models (ApiResponse, ResponseMetadata, ErrorDetail, ErrorResponse)
- `packages/mcp-server/src/storage/__init__.py` - Storage client exports
- `packages/mcp-server/src/storage/mongodb.py` - Read-only MongoDB client
- `packages/mcp-server/src/storage/qdrant.py` - Read-only Qdrant storage client
- `packages/mcp-server/src/tools/health.py` - Health check function
- `packages/mcp-server/src/tools/__init__.py` - Updated with health export
- `packages/mcp-server/src/server.py` - FastAPI application with MCP integration

**Configuration Files Created:**
- `packages/mcp-server/.env.example` - Environment configuration template

**Documentation Created:**
- `packages/mcp-server/README.md` - Setup, usage, and troubleshooting guide

**Test Files Created:**
- `packages/mcp-server/tests/test_config.py` - Configuration tests
- `packages/mcp-server/tests/test_exceptions.py` - Exception class tests
- `packages/mcp-server/tests/test_models/__init__.py` - Test package init
- `packages/mcp-server/tests/test_models/test_responses.py` - Response model tests
- `packages/mcp-server/tests/test_storage/__init__.py` - Test package init
- `packages/mcp-server/tests/test_storage/test_mongodb.py` - MongoDB client tests (+ URI masking, ping tests)
- `packages/mcp-server/tests/test_storage/test_qdrant.py` - Qdrant client tests (+ vector validation tests)
- `packages/mcp-server/tests/test_tools/__init__.py` - Test package init
- `packages/mcp-server/tests/test_tools/test_health.py` - Health check tests
- `packages/mcp-server/tests/test_server.py` - Server application tests
- `packages/mcp-server/tests/test_mcp_integration.py` - MCP integration tests

**Files Modified (during development):**
- `packages/mcp-server/pyproject.toml` - Added structlog dependency
- `packages/mcp-server/uv.lock` - Lock file updated

---

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.5
**Date:** 2025-12-30
**Outcome:** APPROVED (after fixes)

### Issues Found and Fixed

| # | Severity | Issue | Fix Applied |
|---|----------|-------|-------------|
| 1 | HIGH | MongoDB client methods declared `async def` but called sync pymongo (blocking event loop) | Wrapped all sync operations in `asyncio.to_thread()` |
| 2 | HIGH | Qdrant client methods declared `async def` but called sync qdrant_client (blocking event loop) | Wrapped all sync operations in `asyncio.to_thread()` |
| 3 | HIGH | Tests only verified methods exist, not actual behavior | Added 16 new meaningful tests (ping, validation, URI masking) |
| 4 | MEDIUM | Private `_client` attribute accessed in health.py | Added public `ping()` methods to both storage clients |
| 5 | MEDIUM | No vector dimension validation per project-context.md:228 | Added `_validate_vector()` and `VECTOR_DIMENSIONS=384` constant |
| 6 | MEDIUM | Modified files (pyproject.toml, uv.lock) not in File List | Updated File List |
| 7 | LOW | MongoDB URI logged in plain text (potential credential leak) | Added `_mask_uri_credentials()` helper |

### Test Count
- **Before Review:** 77 tests
- **After Review:** 93 tests (+16 meaningful behavior tests)

### Architecture Compliance
- ✅ All sync database operations now properly offloaded via `asyncio.to_thread()`
- ✅ Vector dimensions validated before Qdrant search (384d required)
- ✅ Public `ping()` methods replace private attribute access
- ✅ Credentials masked in logging per project-context.md:236

---

## Second Code Review (AI)

**Reviewer:** Claude Opus 4.5
**Date:** 2026-01-01
**Outcome:** APPROVED (after fixes)
**Context:** User asked "Do we actually have the MCP server working?"

### Verification Results

| Check | Result | Evidence |
|-------|--------|----------|
| Server starts | ✅ PASS | `mongodb_connected=True qdrant_connected=True` |
| `/health` endpoint | ✅ PASS | Returns `{"status":"healthy","services":{"mongodb":"healthy","qdrant":"healthy"}}` |
| `/mcp` endpoint | ✅ PASS | Returns MCP protocol response (406 without SSE = correct behavior) |
| All tests pass | ✅ PASS | 97/97 tests pass |
| Linting clean | ✅ PASS | `ruff check .` returns no errors |

### Issues Found and Fixed

| # | Severity | Issue | Fix Applied |
|---|----------|-------|-------------|
| 1 | MEDIUM | Health endpoint defined AFTER `mcp.mount_http()` causing confusing code flow | Moved health endpoint definition BEFORE MCP mount |
| 2 | MEDIUM | Health endpoint not excluded from MCP tools (per context7 best practices) | Added `tags=["infrastructure"]` and `exclude_tags=["infrastructure"]` to MCP config |
| 3 | LOW | MCP integration tests only checked existence, not configuration | Added 4 new tests for MCP configuration (exclude_tags, name, tag verification) |

### Test Count
- **Before Review:** 93 tests
- **After Review:** 97 tests (+4 MCP configuration tests)

### Files Modified
- `packages/mcp-server/src/server.py` - Reordered health endpoint before MCP mount, added infrastructure tag and exclude_tags
- `packages/mcp-server/tests/test_mcp_integration.py` - Added 4 new tests for MCP configuration verification

### Context7 Documentation References
- fastapi-mcp `exclude_tags` parameter: Excludes tagged endpoints from MCP tools
- fastapi-mcp endpoint ordering: Endpoints defined before `mount_http()` are automatically captured
- MCP best practices: Infrastructure endpoints should not be exposed as tools
