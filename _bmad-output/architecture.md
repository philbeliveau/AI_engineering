---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - Knowledge-Pipeline-Brief.md
  - AI-Engineering-Workflows-Brief.md
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2025-12-30'
project_name: 'Knowledge Pipeline'
user_name: 'Philippebeliveau'
date: '2025-12-30'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

---

## Project Context Analysis

### System Purpose: Dual-Audience Architecture

This system serves **two distinct audiences** with different needs:

| Audience | Purpose | Primary Extractions |
|----------|---------|---------------------|
| **Builder (Philippebeliveau)** | Create BMAD workflows, agents, prompts | Methodologies, Personas, Checklists, Workflows |
| **End Users (Community)** | Get contextual AI engineering guidance | Decisions, Patterns, Warnings |

```
                        KNOWLEDGE BASE
                    (Books, Papers, Case Studies)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌───────────────────┐       ┌───────────────────┐
    │   BUILDER MODE    │       │   END USER MODE   │
    │                   │       │                   │
    │ Extract:          │       │ Query:            │
    │ - Methodologies   │       │ - Decisions       │
    │ - Personas        │       │ - Patterns        │
    │ - Checklists      │       │ - Warnings        │
    │ - Workflows       │       │                   │
    │                   │       │                   │
    │ Output:           │       │ Output:           │
    │ → BMAD Workflows  │       │ → Guidance        │
    │ → Agent prompts   │       │ → Code examples   │
    └───────────────────┘       └───────────────────┘
```

### Requirements Overview

**Functional Requirements (22 total across 4 domains):**

- **Source Ingestion (FR-1):** Multi-format document intake (PDF, Markdown, arXiv, web) with status tracking
- **Knowledge Extraction (FR-2):** Structured extraction of 7 types (see below)
- **Storage (FR-3):** Dual-store architecture (document + vector) with filtering
- **MCP Interface (FR-4):** Tools for both builder and end-user workflows

**Extraction Types (Expanded):**

| Type | Audience | Purpose |
|------|----------|---------|
| Decision | End User | Choice points with options and considerations |
| Pattern | End User | Reusable code/architecture implementations |
| Warning | End User | Gotchas, anti-patterns, failure modes |
| Methodology | Builder | Step-by-step processes from books |
| Checklist | Builder | Verification criteria for workflow steps |
| Persona | Builder | Role definitions for agent creation |
| Workflow | Builder | Process sequences for BMAD workflow design |

**Non-Functional Requirements:**

- **Performance:** <500ms search, single-session batch ingestion
- **Cost:** Zero external LLM API costs (Claude-as-extractor pattern)
- **Scalability:** 100k+ chunks across multiple sources
- **Extensibility:** Adapter/extractor patterns for new types

### Scale & Complexity

| Indicator | Assessment |
|-----------|------------|
| Primary domain | Backend Data Pipeline + API |
| Complexity level | Medium |
| Architectural components | 10-12 major components |
| Data stores | 2 (MongoDB + Qdrant) |
| MCP tool categories | 2 (builder + end-user) |

### Technical Constraints & Dependencies

| Constraint | Architectural Impact |
|------------|---------------------|
| Zero LLM API costs at query time | Pre-extracted knowledge served from storage |
| Ingestion costs | ~$10/book via Claude Haiku batch extraction |
| Zero embedding costs | Local all-MiniLM-L6-v2 model |
| MCP protocol | All interactions via MCP tools |
| Multi-source synthesis | Claude judges across sources at query time |
| Local-first | Docker Compose required, cloud deployment optional |
| Dual-purpose | Separate tool sets for builder vs end-user |

### Cross-Cutting Concerns

| Concern | Impact |
|---------|--------|
| **Source Attribution** | Every extraction traces back to source → chunk → file |
| **Multi-Source Synthesis** | Claude weighs conflicting recommendations across books |
| **Extraction Quality** | Pre-extracted structure enables exploration; Claude adds judgment |
| **Schema Evolution** | Extraction types may expand; need versioned schemas |
| **Builder vs User Context** | Same data, different query patterns and tools |

### Key Architectural Insight

**Extractions are for NAVIGATION, Claude is for SYNTHESIS.**

- Pre-extracted decisions/patterns/methodologies create a **structured map** of knowledge
- Users can explore: "What decisions exist about X?" "What methodologies cover Y?"
- At query time, Claude **synthesizes across sources**, weighs conflicts, applies user context
- Claude is not limited to extractions—can reason beyond any single source

### Builder Workflow (Book → BMAD)

```
1. Ingest book into knowledge base
2. Query: "What methodologies does this book describe?"
3. Extract methodology steps, decisions, warnings for each step
4. Use extractions to build BMAD workflow structure
5. Query: "What persona handles this domain?"
6. Use persona extraction to define BMAD agent
7. Query: "What should this agent know about X?"
8. Use decisions/patterns/warnings to craft agent prompts
```

---

## Starter Template & Tooling

### Deployment Model: Hosted MCP Server

Community users connect to a **hosted MCP server** - no local setup required:

```
┌──────────────────────────────────────────────────────────────┐
│                      BUILDER HOSTS                            │
│                                                               │
│   server.py ──▶ Deploy to Cloud ──▶ https://aie.app/mcp     │
│                                                               │
│   MongoDB Atlas + Qdrant Cloud + MCP Server (Railway)        │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    COMMUNITY USER                             │
│                                                               │
│   1. Add URL to Claude Code MCP config                       │
│   2. Done - no code, no setup, no server                     │
└──────────────────────────────────────────────────────────────┘
```

### Package Manager: uv

Selected **uv** (Astral) as the Python package manager:
- 10-100x faster than pip for dependency resolution
- Lockfile ensures reproducible environments
- Built-in Python version management
- `uv run` pattern eliminates manual venv management

### MCP Framework: fastapi-mcp

Selected **fastapi-mcp** (tadata-org) for MCP server:
- Native FastAPI extension (not a wrapper)
- Simple mounting: `mcp.mount()` exposes tools at `/mcp`
- Auth support built-in
- Required for Claude Code to connect (MCP protocol)

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()

@app.post("/search_knowledge")
async def search_knowledge(query: str):
    # Business logic here
    return results

mcp = FastApiMCP(app)
mcp.mount()  # Creates /mcp endpoint
```

### No Cookiecutter Template

Custom project structure defined in brief is used directly:
- Dual-repo structure (pipeline + MCP server)
- Specific to knowledge extraction use case
- Already includes all architectural decisions

### Verified Dependency Versions

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.11+ | Runtime |
| fastapi | >=0.115 | API framework |
| fastapi-mcp | >=0.4.0 | MCP protocol layer |
| qdrant-client | >=1.13 | Vector storage |
| sentence-transformers | >=5.0 | Local embeddings |
| pymongo | latest | MongoDB client |
| pymupdf | latest | PDF parsing |
| anthropic | >=0.40.0 | LLM API client for extraction |
| tenacity | >=8.0.0 | Retry logic with backoff |
| pydantic | >=2.0 | Data validation |
| uv | latest | Package management |

### Project Initialization Commands

**packages/pipeline:**
```bash
cd packages/pipeline
uv init && uv python pin 3.11
uv add fastapi uvicorn pymongo qdrant-client sentence-transformers pymupdf pydantic pydantic-settings
uv add --dev pytest pytest-asyncio ruff mypy
```

**packages/mcp-server:**
```bash
cd packages/mcp-server
uv init && uv python pin 3.11
uv add fastapi fastapi-mcp uvicorn qdrant-client pymongo
uv add --dev pytest
```

### Cloud Deployment Stack

| Component | Service | Cost |
|-----------|---------|------|
| MCP Server | Railway | ~$5/mo |
| MongoDB | MongoDB Atlas | Free tier → $9/mo |
| Qdrant | Qdrant Cloud | Free tier → $25/mo |

---

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- MongoDB collection structure (Hybrid)
- Qdrant vector configuration (384d, Cosine)
- MCP tool definitions (Specific granularity)

**Important Decisions (Shape Architecture):**
- Authentication model (Tiered)
- Response format (Annotated with attribution)
- Hosting platform (Railway)

**Deferred Decisions (Post-MVP):**
- Advanced rate limiting (usage-based)
- Premium content gating
- Multi-region deployment

### Data Architecture

**MongoDB Collections (Hybrid Model):**

```
knowledge_db/
├── sources           # Book/paper metadata
│   ├── _id
│   ├── type          # "book", "paper", "case_study"
│   ├── title
│   ├── authors[]
│   ├── path
│   ├── ingested_at
│   ├── status
│   └── metadata{}
│
├── chunks            # Raw text chunks
│   ├── _id
│   ├── source_id     # → sources._id
│   ├── content
│   ├── position      # {chapter, section, page}
│   ├── token_count
│   └── schema_version
│
└── extractions       # Structured knowledge
    ├── _id
    ├── source_id     # → sources._id (for "all from book X")
    ├── chunk_id      # → chunks._id (for context)
    ├── type          # "decision", "pattern", "warning", "methodology"...
    ├── content{}     # Type-specific structured data
    ├── topics[]
    ├── schema_version
    └── extracted_at
```

**Indexes:**
- `extractions.type` + `extractions.topics` (compound)
- `extractions.source_id`
- `chunks.source_id`

**Qdrant Configuration (Single Collection Architecture):**

Per [Qdrant's multitenancy best practices](https://qdrant.tech/documentation/guides/multitenancy/), all vectors are stored in a **single `knowledge_vectors` collection** with payload-based filtering:

| Setting | Value | Rationale |
|---------|-------|-----------|
| Vector size | 384 | all-MiniLM-L6-v2 output |
| Distance metric | Cosine | Standard for text embeddings |
| Collection | `knowledge_vectors` | Single collection for all vectors |
| Content discrimination | `content_type` payload | "chunk" or "extraction" |
| Project isolation | `project_id` payload | `is_tenant=True` index optimization |

**Rich Payload Schema:**

```python
payload = {
    # === INDEXED FIELDS (for filtering) ===
    "project_id": "ai_engineering",      # is_tenant=True
    "content_type": "extraction",         # "chunk" | "extraction"
    "source_id": "507f1f77...",
    "source_type": "book",
    "source_category": "foundational",
    "source_year": 2024,
    "source_tags": ["llm-ops", "production"],
    "extraction_type": "pattern",         # Only for extractions
    "topics": ["reliability", "api"],
    "chapter": "5",

    # === NON-INDEXED FIELDS (for display) ===
    "chunk_id": "507f1f77...",
    "extraction_id": "507f1f77...",
    "source_title": "LLM Engineer's Handbook",
    "extraction_title": "Retry with Exponential Backoff",
    "section": "Error Handling",
    "page": 142,
}
```

**Payload Indexes:**

```python
# Tenant index (co-locates vectors for performance)
client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="project_id",
    field_schema=models.PayloadSchemaType.KEYWORD,
    is_tenant=True,  # Qdrant v1.11+ optimization
)

# Content type and source filters
for field in ["content_type", "source_id", "source_type", "source_category"]:
    client.create_payload_index(
        collection_name="knowledge_vectors",
        field_name=field,
        field_schema=models.PayloadSchemaType.KEYWORD,
    )

# Integer index for year filtering
client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="source_year",
    field_schema=models.PayloadSchemaType.INTEGER,
)

# Extraction-specific indexes
for field in ["extraction_type", "topics", "chapter"]:
    client.create_payload_index(
        collection_name="knowledge_vectors",
        field_name=field,
        field_schema=models.PayloadSchemaType.KEYWORD,
    )
```

**Schema Versioning:**
- All documents include `schema_version` field
- Application code handles version differences
- Migration scripts for breaking changes

**Project Namespacing (Payload-Based Isolation):**

Projects are isolated via **payload filtering** rather than separate collections. This follows Qdrant's recommended multitenancy pattern:

```
┌─────────────────────────────────────────────────────────────┐
│             SINGLE COLLECTION ARCHITECTURE                   │
│                                                               │
│  Qdrant: knowledge_vectors (single collection)              │
│    ├── project_id: "ai_engineering" (payload filter)        │
│    ├── project_id: "bmad_docs" (payload filter)             │
│    └── project_id: "default" (when PROJECT_ID not set)      │
│                                                               │
│  MongoDB: Still uses project-prefixed collections           │
│    ├── ai_engineering_sources                                │
│    ├── ai_engineering_chunks                                 │
│    ├── ai_engineering_extractions                            │
│    ├── bmad_docs_sources                                     │
│    └── ...                                                    │
└─────────────────────────────────────────────────────────────┘
```

**Why Single Qdrant Collection:**
- Per Qdrant docs: "Creating too many collections may result in resource overhead"
- `is_tenant=True` on `project_id` index enables optimized co-location
- Cross-project queries are possible by omitting `project_id` filter
- Rich metadata filtering (year, category, tags) without collection proliferation

**Query Examples:**

```python
# Project-scoped search
client.query_points(
    collection_name="knowledge_vectors",
    query=embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="project_id", match=models.MatchValue(value="ai_engineering")),
            models.FieldCondition(key="content_type", match=models.MatchValue(value="extraction")),
        ]
    ),
)

# Cross-project search (omit project_id filter)
client.query_points(
    collection_name="knowledge_vectors",
    query=embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="extraction_type", match=models.MatchValue(value="warning")),
        ]
    ),
)
```

**CLI Usage:**

```bash
# Session-wide project selection
export PROJECT_ID=ai_engineering
uv run scripts/ingest.py book1.pdf

# CLI flags for metadata
uv run scripts/ingest.py \
    --project ai_engineering \
    --category foundational \
    --tags "rag,embeddings" \
    --year 2024 \
    book.pdf
```

### Authentication & Security

**Tiered Authentication Model:**

| Tier | Auth Required | Rate Limit | Access |
|------|---------------|------------|--------|
| Public | None | 100 req/hr per IP | Core search, public extractions |
| Registered | API Key | 1000 req/hr | Full search, all extractions |
| Premium | API Key + Subscription | Unlimited | Premium content, priority |

**Implementation:**
- Public tier: IP-based rate limiting via FastAPI middleware
- API Keys: Simple token in header (`X-API-Key`)
- Premium: Stripe integration (future)

### API & Communication Patterns

**MCP Tools (Specific Granularity):**

| Tool | Purpose | Tier |
|------|---------|------|
| `search_knowledge` | Semantic search across all content | Public |
| `get_decisions` | Query decision extractions by topic | Public |
| `get_patterns` | Query code pattern extractions | Public |
| `get_warnings` | Query warning extractions | Public |
| `get_methodologies` | Query methodology extractions | Registered |
| `list_sources` | List available knowledge sources | Public |
| `compare_sources` | Compare extractions across sources | Registered |

**Response Format (Annotated):**

```json
{
  "results": [...],
  "metadata": {
    "query": "original query",
    "sources_cited": ["LLM Handbook Ch.5", "RAG Survey 2024"],
    "result_count": 5,
    "search_type": "semantic"
  }
}
```

**Error Handling:**
- Standard HTTP status codes
- Structured error responses with `error_code`, `message`, `details`
- Rate limit errors include `retry_after` header

### Infrastructure & Deployment

**Hosting Stack (Confirmed):**

| Component | Service | Tier | Cost |
|-----------|---------|------|------|
| MCP Server | Railway | Starter | ~$5/mo |
| MongoDB | Atlas | M0 Free → M10 | $0 → $57/mo |
| Qdrant | Qdrant Cloud | Free → Starter | $0 → $25/mo |

**CI/CD:**
- Railway auto-deploy on push to `main`
- Preview deployments for PRs
- Environment variables via Railway dashboard

**Environment Configuration:**

| Environment | Purpose | Database |
|-------------|---------|----------|
| `local` | Development | Docker Compose (local) |
| `staging` | Testing | Separate Atlas/Qdrant instances |
| `production` | Live | Production Atlas/Qdrant |

### Decision Impact Analysis

**Implementation Sequence:**
1. Set up MongoDB collections and indexes
2. Configure Qdrant collections
3. Implement core MCP tools (search, get_*)
4. Add rate limiting middleware
5. Deploy to Railway
6. Add API key authentication
7. Implement premium tier (future)

**Cross-Component Dependencies:**
- Extractions reference both `source_id` and `chunk_id` for flexibility
- Qdrant payloads must match MongoDB filter fields
- Rate limiting sits in front of all tools

---

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**12 conflict points identified and resolved** to ensure AI agents and developers write compatible code.

### Naming Patterns

**MongoDB Naming Conventions:**

| Element | Convention | Example |
|---------|------------|---------|
| Collections | `snake_case` | `sources`, `chunks`, `extractions` |
| Fields | `snake_case` | `source_id`, `chunk_id`, `extracted_at` |
| Indexes | `idx_{collection}_{field}` | `idx_extractions_type_topics` |

**Python Naming Conventions:**

| Element | Convention | Example |
|---------|------------|---------|
| Files/modules | `snake_case.py` | `pdf_adapter.py`, `decision_extractor.py` |
| Classes | `PascalCase` | `PdfAdapter`, `DecisionExtractor`, `SearchResult` |
| Functions | `snake_case` | `extract_decisions()`, `search_knowledge()` |
| Variables | `snake_case` | `source_id`, `chunk_content` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_CHUNK_SIZE`, `MAX_RESULTS` |

**Pydantic Models:**

| Element | Convention | Example |
|---------|------------|---------|
| Model classes | `PascalCase` | `Source`, `Chunk`, `Decision` |
| Field names | `snake_case` | `source_id: str`, `extracted_at: datetime` |

### Structure Patterns

**Project Organization:**
```
packages/pipeline/             # (same pattern for mcp-server/)
├── src/
│   ├── __init__.py
│   ├── config.py              # Pydantic Settings
│   ├── adapters/              # Source type handlers
│   ├── processors/            # Chunking, cleaning
│   ├── extractors/            # Knowledge extraction
│   ├── embeddings/            # Vector generation
│   ├── storage/               # DB clients
│   └── models/                # Pydantic schemas
├── tests/                     # Mirror src/ structure
│   ├── test_adapters/
│   ├── test_processors/
│   └── conftest.py
├── scripts/                   # CLI utilities
└── pyproject.toml
```

**Test Organization:**
- Tests in separate `tests/` directory
- Mirror `src/` structure: `src/adapters/` → `tests/test_adapters/`
- Test files prefixed: `test_pdf_adapter.py`
- Shared fixtures in `conftest.py`

### Format Patterns

**API Response Format (Success):**
```json
{
  "results": [...],
  "metadata": {
    "query": "original query string",
    "sources_cited": ["LLM Handbook Ch.5", "RAG Survey 2024"],
    "result_count": 5,
    "search_type": "semantic"
  }
}
```

**API Response Format (Error):**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Source with id 'xyz' not found",
    "details": {"source_id": "xyz"}
  }
}
```

**Error Codes:**

| Code | HTTP Status | Usage |
|------|-------------|-------|
| `VALIDATION_ERROR` | 400 | Invalid input parameters |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

**JSON Field Naming:**
- Always `snake_case` in JSON (matches Python/MongoDB)
- Dates as ISO 8601 strings: `"2025-12-30T10:30:00Z"`
- IDs as strings (MongoDB ObjectId compatibility)

### Process Patterns

**Async Patterns:**
```python
# FastAPI endpoints: ALWAYS async
@app.post("/search_knowledge")
async def search_knowledge(query: str) -> SearchResponse:
    results = await qdrant_client.search(...)
    return SearchResponse(results=results)

# CPU-bound helpers: sync is OK (documented)
def generate_embedding(text: str) -> List[float]:
    """Sync function - CPU-bound embedding generation."""
    return model.encode(text).tolist()
```

**Configuration Pattern:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    qdrant_url: str = "http://localhost:6333"
    embedding_model: str = "all-MiniLM-L6-v2"
    environment: str = "local"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Logging Pattern:**
```python
import structlog
logger = structlog.get_logger()

# Good: structured with context
logger.info("search_completed", query=query, result_count=len(results))
```

**Error Handling Pattern:**
```python
class KnowledgeError(Exception):
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

class NotFoundError(KnowledgeError):
    def __init__(self, resource: str, id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with id '{id}' not found",
            details={"resource": resource, "id": id}
        )
```

### Enforcement Guidelines

**All AI Agents MUST:**
1. Use `snake_case` for all Python identifiers except classes
2. Use `PascalCase` for all class names
3. Return wrapped responses with `results` and `metadata`
4. Use structured error format with `code`, `message`, `details`
5. Use Pydantic Settings for all configuration
6. Use structured logging (no print statements in production code)
7. Place tests in `tests/` directory mirroring `src/` structure

**Pattern Verification:**
- Ruff linter enforces Python naming conventions
- Pydantic validates response structures
- PR reviews check pattern compliance

---

## Project Structure & Boundaries

### Requirements to Component Mapping

| Requirement Category | Component Location |
|---------------------|-------------------|
| **FR-1: Source Ingestion** | `packages/pipeline/src/adapters/` |
| **FR-2: Knowledge Extraction** | `packages/pipeline/src/extractors/` |
| **FR-3: Storage** | `packages/pipeline/src/storage/`, `packages/mcp-server/src/storage/` |
| **FR-4: MCP Interface** | `packages/mcp-server/src/tools/` |

### Complete Project Directory Structure

```
ai-engineering-knowledge/              # Monorepo root
├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yaml                # Local dev: MongoDB + Qdrant
├── Taskfile.yaml                      # Task runner
│
├── packages/                          # All code packages
│   │
│   ├── pipeline/                      # Ingestion & extraction
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   ├── .env.example
│   │   │
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Pydantic Settings
│   │   │   ├── main.py                # CLI entry point
│   │   │   │
│   │   │   ├── adapters/              # FR-1: Source Ingestion
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py            # SourceAdapter ABC
│   │   │   │   ├── pdf_adapter.py
│   │   │   │   ├── markdown_adapter.py
│   │   │   │   └── arxiv_adapter.py
│   │   │   │
│   │   │   ├── processors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chunker.py
│   │   │   │   └── cleaner.py
│   │   │   │
│   │   │   ├── extractors/            # FR-2: Knowledge Extraction
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── llm_client.py      # LLM API wrapper for batch extraction
│   │   │   │   ├── decision_extractor.py
│   │   │   │   ├── pattern_extractor.py
│   │   │   │   ├── warning_extractor.py
│   │   │   │   ├── methodology_extractor.py
│   │   │   │   └── prompts/
│   │   │   │       ├── decision.md
│   │   │   │       ├── pattern.md
│   │   │   │       ├── warning.md
│   │   │   │       └── methodology.md
│   │   │   │
│   │   │   ├── embeddings/
│   │   │   │   ├── __init__.py
│   │   │   │   └── local_embedder.py
│   │   │   │
│   │   │   ├── storage/               # FR-3: Storage (write)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mongodb.py
│   │   │   │   └── qdrant.py
│   │   │   │
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── source.py
│   │   │   │   ├── chunk.py
│   │   │   │   ├── extraction.py
│   │   │   │   └── pipeline.py
│   │   │   │
│   │   │   └── exceptions.py
│   │   │
│   │   ├── scripts/
│   │   │   ├── ingest.py
│   │   │   ├── extract.py
│   │   │   └── export.py
│   │   │
│   │   └── tests/
│   │       ├── conftest.py
│   │       ├── test_adapters/
│   │       ├── test_processors/
│   │       ├── test_extractors/
│   │       └── test_storage/
│   │
│   └── mcp-server/                    # MCP Server
│       ├── pyproject.toml
│       ├── uv.lock
│       ├── .env.example
│       ├── Dockerfile
│       │
│       ├── src/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── server.py              # FastAPI + MCP
│       │   │
│       │   ├── tools/                 # FR-4: MCP Tools
│       │   │   ├── __init__.py
│       │   │   ├── search.py          # search_knowledge
│       │   │   ├── decisions.py       # get_decisions
│       │   │   ├── patterns.py        # get_patterns
│       │   │   ├── warnings.py        # get_warnings
│       │   │   ├── methodologies.py   # get_methodologies
│       │   │   ├── sources.py         # list_sources
│       │   │   └── health.py
│       │   │
│       │   ├── storage/               # FR-3: Storage (read)
│       │   │   ├── __init__.py
│       │   │   ├── mongodb.py
│       │   │   └── qdrant.py
│       │   │
│       │   ├── models/
│       │   │   ├── __init__.py
│       │   │   ├── requests.py
│       │   │   ├── responses.py
│       │   │   └── shared.py
│       │   │
│       │   ├── middleware/
│       │   │   ├── __init__.py
│       │   │   ├── rate_limit.py
│       │   │   ├── auth.py
│       │   │   └── logging.py
│       │   │
│       │   └── exceptions.py
│       │
│       └── tests/
│           ├── conftest.py
│           ├── test_tools/
│           └── test_middleware/
│
├── data/                              # Data directory (renamed from knowledge-store)
│   ├── raw/                           # Original files (gitignored)
│   ├── processed/                     # Intermediate (gitignored)
│   └── manifests/                     # Ingestion records (tracked)
│       └── sources.json
│
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── api.md
│   └── development.md
│
└── .github/
    └── workflows/
        └── ci.yml
```

### Architectural Boundaries

**Service Boundaries:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    packages/pipeline (batch)                         │
│  Adapters ──▶ Processors ──▶ Extractors ──▶ Storage (write)         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              ┌──────────┐                   ┌──────────┐
              │ MongoDB  │                   │  Qdrant  │
              └────┬─────┘                   └────┬─────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    │
┌───────────────────────────────────┼─────────────────────────────────┐
│                                   ▼                                  │
│                    packages/mcp-server (server)                      │
│  Middleware ──▶ Tools ──▶ Storage (read) ──▶ FastAPI-MCP            │
└─────────────────────────────────────────────────────────────────────┘
```

**Data Boundaries:**

| Store | Pipeline (Write) | MCP Server (Read) |
|-------|-----------------|-------------------|
| MongoDB `{project}_sources` | ✓ | ✓ |
| MongoDB `{project}_chunks` | ✓ | ✓ |
| MongoDB `{project}_extractions` | ✓ | ✓ |
| Qdrant `knowledge_vectors` | ✓ | ✓ |

*Note: MongoDB uses project-prefixed collections. Qdrant uses a single `knowledge_vectors` collection with `project_id` payload filtering.*

### Integration Points

**Data Flow:**
```
Source File → Adapter → Chunker → Extractor → Storage (MongoDB + Qdrant)
                                                        ↓
Claude Code → MCP Server → Search (Qdrant) → Enrich (MongoDB) → Response
```

### Development Workflow

**Local Development:**
```bash
# Start infrastructure
docker-compose up -d

# Run pipeline
cd packages/pipeline && uv run scripts/ingest.py <file>

# Run MCP server
cd packages/mcp-server && uv run uvicorn src.server:app --reload
```

**Docker Compose Services:**
- `mongodb`: MongoDB 7 on port 27017
- `qdrant`: Qdrant latest on port 6333

---

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:** All technology choices (Python 3.11, FastAPI, MongoDB, Qdrant, fastapi-mcp, sentence-transformers) are compatible and work together without conflicts.

**Pattern Consistency:** Implementation patterns (Pydantic models, async FastAPI, structured logging) align with chosen stack.

**Structure Alignment:** Project structure supports all architectural decisions with clear boundaries between pipeline and MCP server.

### Requirements Coverage Validation ✅

**Functional Requirements:**
- FR-1 (Source Ingestion): Fully supported by adapters module
- FR-2 (Knowledge Extraction): Fully supported by extractors module
- FR-3 (Storage): Fully supported by storage modules in both repos
- FR-4 (MCP Interface): Fully supported by tools module with 7 defined tools

**Non-Functional Requirements:**
- Performance: Qdrant + indexed MongoDB ensures <500ms search
- Cost: Zero LLM API costs via local embeddings and Claude-as-extractor
- Scalability: Stateless server, Qdrant clustering ready
- Extensibility: ABC patterns for adapters and extractors

### Implementation Readiness Validation ✅

**Decision Completeness:** All critical decisions documented with specific versions.

**Structure Completeness:** Full project tree with 80+ files/directories defined.

**Pattern Completeness:** 12 potential conflict points identified and resolved with concrete examples.

### Gap Analysis Results

**Critical Gaps:** None

**Deferred to Post-MVP:**
- Premium authentication (Stage 4)
- arXiv adapter (Stage 3)
- Multi-region deployment (Future)

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Dual-audience (builder + end-user) identified
- [x] Technical constraints identified (zero API cost)
- [x] Cross-cutting concerns mapped

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Tiered authentication model defined
- [x] Deployment model (hosted MCP) confirmed

**✅ Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Response patterns specified
- [x] Error handling patterns documented

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
- Clear separation of concerns (pipeline vs server)
- Zero external API dependency
- Comprehensive pattern documentation
- Staged implementation roadmap

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure and boundaries
- Refer to this document for all architectural questions

**First Implementation Priority:**
1. Create monorepo structure with docker-compose
2. Implement Pydantic models (shared foundation)
3. Build MongoDB/Qdrant storage clients
4. Create basic PDF adapter and chunker
5. Implement `search_knowledge` MCP tool

---

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2025-12-30
**Document Location:** _bmad-output/architecture.md

### Final Architecture Deliverables

**📋 Complete Architecture Document**

- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**🏗️ Implementation Ready Foundation**

- 12+ architectural decisions made across technology stack, data architecture, authentication, and deployment
- 12+ implementation patterns defined (naming, structure, format, and process patterns)
- 10-12 architectural components specified (adapters, processors, extractors, storage, tools, middleware)
- 22 functional requirements fully supported across 4 domains

**📚 AI Agent Implementation Guide**

- Technology stack with verified versions (Python 3.11, FastAPI, MongoDB, Qdrant, fastapi-mcp)
- Consistency rules that prevent implementation conflicts
- Project structure with clear boundaries (pipeline vs MCP server)
- Integration patterns and communication standards

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing Knowledge Pipeline. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**

```bash
# packages/pipeline
cd packages/pipeline
uv init && uv python pin 3.11
uv add fastapi uvicorn pymongo qdrant-client sentence-transformers pymupdf pydantic pydantic-settings
uv add --dev pytest pytest-asyncio ruff mypy

# packages/mcp-server
cd packages/mcp-server
uv init && uv python pin 3.11
uv add fastapi fastapi-mcp uvicorn qdrant-client pymongo
uv add --dev pytest
```

**Development Sequence:**

1. Initialize project using documented starter template
2. Set up development environment per architecture
3. Implement core architectural foundations (Pydantic models, storage clients)
4. Build features following established patterns
5. Maintain consistency with documented rules

### Quality Assurance Checklist

**✅ Architecture Coherence**

- [x] All decisions work together without conflicts
- [x] Technology choices are compatible
- [x] Patterns support the architectural decisions
- [x] Structure aligns with all choices

**✅ Requirements Coverage**

- [x] All functional requirements are supported
- [x] All non-functional requirements are addressed
- [x] Cross-cutting concerns are handled
- [x] Integration points are defined

**✅ Implementation Readiness**

- [x] Decisions are specific and actionable
- [x] Patterns prevent agent conflicts
- [x] Structure is complete and unambiguous
- [x] Examples are provided for clarity

### Project Success Factors

**🎯 Clear Decision Framework**
Every technology choice was made collaboratively with clear rationale, ensuring all stakeholders understand the architectural direction.

**🔧 Consistency Guarantee**
Implementation patterns and rules ensure that multiple AI agents will produce compatible, consistent code that works together seamlessly.

**📋 Complete Coverage**
All project requirements are architecturally supported, with clear mapping from business needs to technical implementation.

**🏗️ Solid Foundation**
The chosen technology stack and architectural patterns provide a production-ready foundation following current best practices.

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein.

**Document Maintenance:** Update this architecture when major technical decisions are made during implementation.

