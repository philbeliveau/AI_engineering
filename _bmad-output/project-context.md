---
project_name: 'AI_engineering'
user_name: 'Philippebeliveau'
date: '2026-01-03'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
rule_count: 92
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

### Runtime & Package Management
- **Python:** >=3.11 (pin with `uv python pin 3.11`)
- **uv:** Package manager - use `uv run` pattern, never manual venv

### API Framework
- **FastAPI:** >=0.115 - all endpoints MUST be async
- **fastapi-mcp:** >=0.4.0 - MCP protocol layer
- **pydantic:** >=2.0 - all models use Pydantic v2 syntax

### Data Storage
- **MongoDB:** 7 - collections: `sources`, `chunks`, `extractions`
- **Qdrant:** latest - 768d vectors, Cosine distance
- **pymongo/qdrant-client:** Use async patterns where available

### Embeddings
- **Model:** nomic-embed-text-v1.5 (768 dimensions, 8K context)
- **Pipeline:** sentence-transformers >=5.0
- **MCP Server:** sentence-transformers (nomic model)

### Development
- **ruff:** line-length 100, target py311
- **pytest-asyncio:** Required for async test functions
- **structlog:** Structured logging only (no print statements)

---

## Critical Implementation Rules

### Python Naming Conventions
- **Files/modules:** `snake_case.py` (e.g., `pdf_adapter.py`)
- **Classes:** `PascalCase` (e.g., `PdfAdapter`, `SearchResult`)
- **Functions/variables:** `snake_case` (e.g., `extract_decisions`, `source_id`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CHUNK_SIZE`)
- **Pydantic models:** `PascalCase` class, `snake_case` fields

### Async Patterns
- FastAPI endpoints: ALWAYS `async def` - no exceptions
- CPU-bound helpers (embeddings): sync OK but add docstring: `"""Sync function - CPU-bound."""`
- Never block async endpoints with sync I/O

### Configuration
- ALWAYS use `pydantic_settings.BaseSettings` for config
- Load from `.env` files via `Config.env_file`
- Never hardcode secrets or connection strings
- Export singleton: `settings = Settings()`

### Project Namespacing (Single Collection Architecture)
- Use `PROJECT_ID` environment variable to isolate knowledge bases
- Default: `"default"` when `PROJECT_ID` not set

**MongoDB:** Uses project-prefixed collections
- Collection naming pattern: `{project_id}_{type}` (e.g., `ai_engineering_sources`)
- Access collections via settings properties, NEVER hardcode names

**Qdrant:** Uses SINGLE `knowledge_vectors` collection with payload filtering
- All vectors (chunks AND extractions) go to `knowledge_vectors`
- Project isolation via `project_id` payload field with `is_tenant=True` index
- Content type discrimination via `content_type` payload: `"chunk"` or `"extraction"`

```python
# CORRECT: MongoDB - Use settings properties
collection = self._db[settings.sources_collection]

# CORRECT: Qdrant - Use single collection constant
from config import KNOWLEDGE_VECTORS_COLLECTION
self._qdrant.ensure_collection(KNOWLEDGE_VECTORS_COLLECTION)

# WRONG: Hardcoded MongoDB collection names
collection = self._db["sources"]  # NEVER DO THIS

# WRONG: Dynamic Qdrant collection names (OLD PATTERN - DEPRECATED)
self._qdrant.ensure_collection(f"{project_id}_chunks")  # NEVER DO THIS
```

### Qdrant Rich Payload Requirements
All vectors stored in `knowledge_vectors` MUST include these payload fields:

**Required Fields (ALL vectors):**
- `project_id`: str - Project namespace (is_tenant=True index)
- `content_type`: str - "chunk" or "extraction"
- `source_id`: str - MongoDB source document ID

**For Chunks:**
- `chunk_id`: str - MongoDB chunk document ID
- `source_title`: str - Human-readable source title
- `source_type`: str - "book", "paper", "case_study"
- `chapter`: Optional[str] - Chapter/section identifier
- `page`: Optional[int] - Page number

**For Extractions:**
- `extraction_id`: str - MongoDB extraction document ID
- `extraction_type`: str - "decision", "pattern", "warning", "methodology"
- `extraction_title`: str - Human-readable extraction title
- `topics`: list[str] - Topic tags
- `source_category`: str - "foundational", "advanced", "reference", "case_study"
- `source_year`: Optional[int] - Publication year
- `source_tags`: list[str] - Custom tags

### LLM Client Configuration
- Use `ANTHROPIC_API_KEY` from environment via pydantic-settings
- Default model: `claude-3-haiku-20240307`
- Never hardcode API keys or model IDs
- Use structured logging for all LLM API calls
- Implement retry logic with exponential backoff (tenacity)

### Error Handling
- Custom exceptions inherit from base `KnowledgeError`
- Always include: `code`, `message`, `details` dict
- Specific exceptions: `NotFoundError`, `ValidationError`
- Never catch bare `Exception` without re-raising

### Framework Rules (FastAPI + MCP)

#### Dual-Package Boundary
- `packages/pipeline`: Batch processing, WRITE to databases
- `packages/mcp-server`: Real-time queries, READ from databases
- NEVER write to databases from mcp-server
- NEVER serve HTTP requests from pipeline

#### API Response Format (MANDATORY)
All endpoints MUST return wrapped responses:
```python
{
    "results": [...],           # Always an array
    "metadata": {
        "query": str,           # Original query
        "sources_cited": [],    # Attribution required
        "result_count": int,
        "search_type": str      # "semantic" | "filtered"
    }
}
```

#### Error Response Format (MANDATORY)
```python
{
    "error": {
        "code": "NOT_FOUND",    # VALIDATION_ERROR | NOT_FOUND | RATE_LIMITED | INTERNAL_ERROR
        "message": str,
        "details": {}
    }
}
```

#### MCP Integration
- Mount MCP after all routes defined: `mcp.mount()`
- MCP endpoint exposed at `/mcp`
- Tools map 1:1 to FastAPI endpoints

### Testing Rules

#### Test Organization
- Tests in separate `tests/` directory (not alongside source)
- Mirror `src/` structure: `src/adapters/` → `tests/test_adapters/`
- Test files prefixed: `test_pdf_adapter.py`
- Integration tests suffixed: `test_*_integration.py`
- Shared fixtures in `conftest.py` at tests root

#### Async Testing
- Use `pytest-asyncio` for all async tests
- Mark async tests: `@pytest.mark.asyncio`
- Async fixtures: `@pytest_asyncio.fixture`

#### Test Patterns
- Unit tests: Mock external dependencies for fast CI runs
- Integration tests: MUST run against real cloud databases (MongoDB Atlas, Qdrant Cloud)
- Credentials stored in `packages/mcp-server/.env` (gitignored)
- Each test function tests ONE behavior

#### Integration Tests (MANDATORY for Code Review)
**Cloud databases are deployed. Code reviewers MUST run integration tests before approving PRs.**

```bash
# Run integration tests against real cloud services
cd packages/mcp-server
uv run pytest -m integration

# Run all tests (unit + integration)
uv run pytest
```

- Integration tests marked with `@pytest.mark.integration`
- Tests verify actual cloud connectivity, not mocked responses
- Mocked tests only prove code logic works with fake data
- Integration tests prove the code works with real infrastructure

#### What Integration Tests Verify
- Real MongoDB Atlas connections and queries
- Real Qdrant Cloud vector operations
- Actual response structures from cloud services
- Connection pooling and timeout behavior
- SSL/TLS and authentication flows

#### Fixture Patterns
```python
# conftest.py
@pytest.fixture
def sample_source() -> Source:
    return Source(id="test-1", title="Test Book", ...)

@pytest_asyncio.fixture
async def mongodb_client():
    # Setup
    client = AsyncIOMotorClient(settings.mongodb_uri)
    yield client
    # Teardown
    await client.close()
```

### Code Quality & Style Rules

#### Linting (Ruff)
- Line length: 100 characters max
- Target: Python 3.11
- Run before commit: `uv run ruff check .`
- Auto-fix: `uv run ruff check --fix .`

#### Logging (MANDATORY)
- Use `structlog` only - never `print()` or `logging` directly
- Always log with context:
```python
import structlog
logger = structlog.get_logger()

# Good
logger.info("search_completed", query=query, result_count=len(results))

# Bad
print(f"Search completed: {query}")
```

#### Code Organization
- One class per file for major components
- ABC base classes in `base.py` within each module
- Pydantic models in `models/` directory
- All exceptions in `exceptions.py`

#### Database Naming (MongoDB)
- Collections: `snake_case` (e.g., `sources`, `chunks`, `extractions`)
- Fields: `snake_case` (e.g., `source_id`, `extracted_at`)
- Indexes: `idx_{collection}_{field}` (e.g., `idx_extractions_type_topics`)
- Dates as ISO 8601 strings: `"2025-12-30T10:30:00Z"`
- IDs as strings (MongoDB ObjectId compatibility)

### Development Workflow Rules

#### Package Management (uv)
- ALWAYS use `uv run` - never `python` or `pip` directly
- Never manually activate venv
- Commit `uv.lock` files for reproducibility
- Add dependencies: `uv add <package>`
- Dev dependencies: `uv add --dev <package>`

#### Local Development Commands
```bash
# Infrastructure
docker-compose up -d              # Start MongoDB + Qdrant

# Pipeline package
cd packages/pipeline
uv run scripts/ingest.py <file>   # Run ingestion
uv run pytest                     # Run tests

# MCP Server package
cd packages/mcp-server
uv run uvicorn src.server:app --reload  # Dev server
```

#### Environment Files
- `.env` for local development (gitignored)
- `.env.example` committed as template
- Never commit secrets or API keys
- Use `pydantic-settings` to load env vars

#### Git Workflow
- Commit lock files (`uv.lock`)
- Gitignore: `.venv/`, `.env`, `data/raw/`, `data/processed/`
- Track: `data/manifests/` (ingestion records)

---

## Critical Don't-Miss Rules

### Anti-Patterns (NEVER DO)
- NEVER write to databases from `packages/mcp-server` (read-only)
- NEVER use `print()` - always `structlog`
- NEVER hardcode connection strings - use Settings
- NEVER return bare results - always wrap in `{results, metadata}`
- NEVER catch bare `Exception` - use specific types
- NEVER use `pip` or manual venv - always `uv run`
- NEVER commit `.env` files or secrets

### Edge Cases to Handle
- Qdrant vectors MUST be exactly 768 dimensions (nomic-embed-text-v1.5)
- MongoDB ObjectIds → convert to strings in API responses
- Every extraction MUST have `source_id` AND `chunk_id` for traceability
- Empty search results → still return `{results: [], metadata: {...}}`

### Security Rules
- API keys in `X-API-Key` header only
- Never log credentials or API keys
- Rate limit public endpoints: 100 req/hr per IP
- Validate all user input at API boundary

### Schema Versioning
- All documents include `schema_version` field
- Check version on read, migrate if needed
- Never break existing document structure without migration

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

---

_Last Updated: 2026-01-03_
