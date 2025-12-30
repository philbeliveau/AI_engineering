# Story 4.1: FastAPI Server with MCP Integration

Status: ready-for-dev

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

- [ ] **Task 1: Verify Prerequisites** (AC: All dependencies available)
  - [ ] 1.1: Confirm Story 1.1 complete (mcp-server package exists): `ls packages/mcp-server/pyproject.toml`
  - [ ] 1.2: Verify uv environment working: `cd packages/mcp-server && uv run python --version`
  - [ ] 1.3: Confirm fastapi-mcp installed: `cd packages/mcp-server && uv run python -c "import fastapi_mcp; print(fastapi_mcp.__version__)"`
  - [ ] 1.4: Verify Docker infrastructure running: `docker-compose ps` (MongoDB + Qdrant should be up)
  - [ ] 1.5: Test MongoDB connection: `mongosh --eval 'db.version()'`
  - [ ] 1.6: Test Qdrant connection: `curl http://localhost:6333/health`

- [ ] **Task 2: Create Configuration Module** (AC: Server uses Pydantic Settings)
  - [ ] 2.1: Create `packages/mcp-server/src/config.py`
  - [ ] 2.2: Implement `Settings` class extending `pydantic_settings.BaseSettings`
  - [ ] 2.3: Define configuration fields:
    - `environment: str` (default: "local")
    - `mongodb_uri: str` (default: "mongodb://localhost:27017")
    - `mongodb_database: str` (default: "knowledge_db")
    - `qdrant_url: str` (default: "http://localhost:6333")
    - `server_host: str` (default: "0.0.0.0")
    - `server_port: int` (default: 8000)
    - `log_level: str` (default: "INFO")
  - [ ] 2.4: Configure `.env` file loading via `Config.env_file = ".env"`
  - [ ] 2.5: Export singleton: `settings = Settings()`
  - [ ] 2.6: Create `.env.example` with all config variables documented
  - [ ] 2.7: Follow project-context.md:59-64 (Configuration pattern)

- [ ] **Task 3: Create Exception Classes** (AC: Structured error handling)
  - [ ] 3.1: Create `packages/mcp-server/src/exceptions.py`
  - [ ] 3.2: Implement base `KnowledgeError(Exception)` with fields: `code`, `message`, `details`
  - [ ] 3.3: Implement specific exceptions:
    - `NotFoundError(KnowledgeError)` - For missing resources
    - `ValidationError(KnowledgeError)` - For invalid input
    - `DatabaseError(KnowledgeError)` - For storage failures
    - `RateLimitError(KnowledgeError)` - For tier limits (future)
  - [ ] 3.4: Follow project-context.md:66-69 (Error Handling pattern)
  - [ ] 3.5: Follow architecture.md:486-496 (Error codes: VALIDATION_ERROR, NOT_FOUND, RATE_LIMITED, INTERNAL_ERROR)

- [ ] **Task 4: Create Response Models** (AC: Standardized API responses)
  - [ ] 4.1: Create `packages/mcp-server/src/models/` directory
  - [ ] 4.2: Create `packages/mcp-server/src/models/responses.py`
  - [ ] 4.3: Implement `ResponseMetadata` Pydantic model:
    - `query: str` - Original query string
    - `sources_cited: list[str]` - Attribution list
    - `result_count: int` - Number of results
    - `search_type: str` - "semantic" | "filtered" | "exact"
  - [ ] 4.4: Implement generic `ApiResponse[T]` Pydantic model:
    - `results: list[T]` - Array of results
    - `metadata: ResponseMetadata` - Response metadata
  - [ ] 4.5: Implement `ErrorDetail` Pydantic model:
    - `code: str` - Error code (VALIDATION_ERROR, NOT_FOUND, etc.)
    - `message: str` - Human-readable message
    - `details: dict` - Additional error context
  - [ ] 4.6: Implement `ErrorResponse` Pydantic model:
    - `error: ErrorDetail`
  - [ ] 4.7: Follow architecture.md:464-476 (Success response format)
  - [ ] 4.8: Follow architecture.md:478-485 (Error response format)
  - [ ] 4.9: Create `packages/mcp-server/src/models/__init__.py` with exports

- [ ] **Task 5: Create Storage Clients (Read-Only)** (AC: Connect to databases on startup)
  - [ ] 5.1: Create `packages/mcp-server/src/storage/` directory
  - [ ] 5.2: Create `packages/mcp-server/src/storage/mongodb.py`
  - [ ] 5.3: Implement `MongoDBClient` class (read-only operations):
    - Constructor takes Settings, initializes pymongo client
    - `async def connect()` - Establish connection
    - `async def disconnect()` - Close connection
    - `async def get_source(source_id: str)` - Retrieve source by ID
    - `async def list_sources(limit: int = 100)` - List all sources
    - `async def get_chunks(source_id: str)` - Get chunks for source
    - `async def get_extractions(type: str = None, topics: list[str] = None)` - Query extractions
  - [ ] 5.4: Add structured logging with structlog for all database operations
  - [ ] 5.5: Create `packages/mcp-server/src/storage/qdrant.py`
  - [ ] 5.6: Implement `QdrantClient` class (read-only operations):
    - Constructor takes Settings, initializes qdrant_client
    - `async def connect()` - Establish connection
    - `async def disconnect()` - Close connection
    - `async def search_chunks(query_vector: list[float], limit: int = 10)` - Semantic search on chunks
    - `async def search_extractions(query_vector: list[float], filter: dict = None, limit: int = 10)` - Semantic search on extractions
  - [ ] 5.7: Follow project-context.md:71-77 (Dual-Package Boundary: mcp-server is READ-ONLY)
  - [ ] 5.8: Follow project-context.md:54-57 (Async patterns for endpoints)
  - [ ] 5.9: Create `packages/mcp-server/src/storage/__init__.py` with exports

- [ ] **Task 6: Create Health Check Endpoint** (AC: Health check returns server status)
  - [ ] 6.1: Create `packages/mcp-server/src/tools/health.py`
  - [ ] 6.2: Implement `async def health_check()` endpoint:
    - Returns `{"status": "healthy", "timestamp": <ISO-8601>, "services": {...}}`
  - [ ] 6.3: Check MongoDB connection status (ping database)
  - [ ] 6.4: Check Qdrant connection status (check cluster health)
  - [ ] 6.5: Return HTTP 503 if any service is unavailable
  - [ ] 6.6: Include version information from pyproject.toml
  - [ ] 6.7: Create `packages/mcp-server/src/tools/__init__.py` with exports

- [ ] **Task 7: Create FastAPI Server Application** (AC: Server starts on configured port)
  - [ ] 7.1: Create `packages/mcp-server/src/server.py`
  - [ ] 7.2: Initialize FastAPI app with metadata:
    - `title="AI Engineering Knowledge MCP Server"`
    - `version` from pyproject.toml
    - `description` from architecture doc
  - [ ] 7.3: Configure structured logging with structlog
  - [ ] 7.4: Add startup event handler:
    - Load configuration
    - Initialize MongoDB client and connect
    - Initialize Qdrant client and connect
    - Log successful startup
  - [ ] 7.5: Add shutdown event handler:
    - Disconnect MongoDB client
    - Disconnect Qdrant client
    - Log graceful shutdown
  - [ ] 7.6: Mount health check endpoint at `/health`
  - [ ] 7.7: Follow project-context.md:54-57 (All endpoints MUST be async)
  - [ ] 7.8: Follow project-context.md:152-164 (Structured logging MANDATORY)

- [ ] **Task 8: Integrate fastapi-mcp** (AC: `/mcp` endpoint available)
  - [ ] 8.1: Import `FastApiMCP` from fastapi_mcp
  - [ ] 8.2: Initialize MCP after FastAPI app creation: `mcp = FastApiMCP(app)`
  - [ ] 8.3: Call `mcp.mount()` to create `/mcp` endpoint
  - [ ] 8.4: Verify MCP protocol endpoint available
  - [ ] 8.5: Follow architecture.md:169-189 (fastapi-mcp integration pattern)
  - [ ] 8.6: Follow project-context.md:104-108 (MCP Integration rules)

- [ ] **Task 9: Create Server Entry Point** (AC: `uv run uvicorn src.server:app` works)
  - [ ] 9.1: Add `if __name__ == "__main__"` block to `server.py`
  - [ ] 9.2: Import uvicorn
  - [ ] 9.3: Call `uvicorn.run()` with:
    - `app="src.server:app"`
    - `host=settings.server_host`
    - `port=settings.server_port`
    - `reload=True` (for development)
    - `log_level=settings.log_level.lower()`
  - [ ] 9.4: Create `main()` function for CLI entry point (matches pyproject.toml script)
  - [ ] 9.5: Test server startup: `cd packages/mcp-server && uv run uvicorn src.server:app`
  - [ ] 9.6: Verify server accessible at `http://localhost:8000`

- [ ] **Task 10: Create Basic Integration Tests** (AC: Server functionality verified)
  - [ ] 10.1: Create `packages/mcp-server/tests/test_server.py`
  - [ ] 10.2: Use pytest-asyncio for async tests
  - [ ] 10.3: Create fixtures in `conftest.py`:
    - `@pytest.fixture` for test app (TestClient)
    - `@pytest_asyncio.fixture` for async database clients
  - [ ] 10.4: Test health check endpoint:
    - Returns 200 when services available
    - Returns 503 when services unavailable
    - Includes service status in response
  - [ ] 10.5: Test MCP endpoint exists:
    - `/mcp` endpoint is accessible
    - Returns MCP protocol metadata
  - [ ] 10.6: Test server startup/shutdown:
    - Database connections established
    - Database connections closed properly
  - [ ] 10.7: Follow project-context.md:110-142 (Testing patterns)
  - [ ] 10.8: Run tests: `cd packages/mcp-server && uv run pytest`

- [ ] **Task 11: Create Documentation** (AC: Developer can run server)
  - [ ] 11.1: Create `packages/mcp-server/README.md`
  - [ ] 11.2: Document setup instructions:
    - Prerequisites (Docker, uv)
    - Environment configuration
    - Running the server locally
  - [ ] 11.3: Document API endpoints:
    - `/health` - Health check
    - `/mcp` - MCP protocol endpoint
  - [ ] 11.4: Document MCP client connection:
    - How Claude Code clients connect
    - Example MCP server configuration
  - [ ] 11.5: Include troubleshooting section:
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

_To be filled by dev agent during implementation_

### Debug Log References

_To be filled by dev agent during implementation_

### Completion Notes List

_To be filled by dev agent during implementation_

### File List

_To be filled by dev agent during implementation_
