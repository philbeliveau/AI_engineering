---
project_name: 'AI_engineering'
user_name: 'Philippebeliveau'
date: '2025-12-30'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality']
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
- **Qdrant:** latest - 384d vectors, Cosine distance
- **pymongo/qdrant-client:** Use async patterns where available

### Embeddings
- **Model:** all-MiniLM-L6-v2 (384 dimensions)
- **Pipeline:** sentence-transformers >=5.0
- **MCP Server:** fastembed >=0.2.0

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
- Shared fixtures in `conftest.py` at tests root

#### Async Testing
- Use `pytest-asyncio` for all async tests
- Mark async tests: `@pytest.mark.asyncio`
- Async fixtures: `@pytest_asyncio.fixture`

#### Test Patterns
- Unit tests: Mock external dependencies (MongoDB, Qdrant)
- Integration tests: Use Docker Compose services
- Never test against production databases
- Each test function tests ONE behavior

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

