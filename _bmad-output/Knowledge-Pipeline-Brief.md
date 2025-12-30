# Knowledge Pipeline - Product Brief

**Project:** Knowledge Ingestion & Retrieval Pipeline
**Parent Initiative:** AI Engineering Workflows Framework
**Author:** Philippebeliveau + Claude
**Date:** December 30, 2025
**Status:** Discovery Complete → Ready for Architecture

---

## Executive Summary

A scalable knowledge ingestion pipeline that transforms technical books, research papers, and case studies into a searchable knowledge base accessible via MCP protocol. Claude Code serves as both the extraction engine (during ingestion) and the query interface (during use), eliminating external LLM API costs.

**Core Principle:** The same infrastructure you use to build the knowledge base is what the community uses to query it.

---

## Problem Statement

### The Knowledge Encoding Problem
- Technical books contain valuable decision frameworks, patterns, and warnings
- This knowledge is trapped in PDF format, unsearchable and unstructured
- Manual extraction doesn't scale across multiple sources
- Each new resource (book, paper, case study) requires significant effort to integrate

### The Cost Problem
- Traditional RAG systems require LLM API calls for extraction AND retrieval
- This creates ongoing costs that don't scale
- Embedding APIs add additional per-token charges

### The Integration Problem
- Knowledge bases are typically separate from development workflows
- Context switching between "learning" and "doing" breaks flow
- No standard interface for AI-assisted tools to query domain knowledge

---

## Solution Overview

### What We're Building

A three-component system:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   INGESTION     │     │    STORAGE      │     │   MCP SERVER    │
│   PIPELINE      │────▶│    LAYER        │◀────│   (Interface)   │
│                 │     │                 │     │                 │
│ - PDF parsing   │     │ - MongoDB (raw) │     │ - search_knowledge
│ - Chunking      │     │ - MongoDB (proc)│     │ - get_decisions │
│ - Extraction    │     │ - Qdrant (vec)  │     │ - get_patterns  │
│ - Embedding     │     │                 │     │ - add_source    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                                                │
        │         Claude Code processes                  │
        └────────────────────────────────────────────────┘
```

### Key Innovation: Claude-as-Extractor

During batch ingestion:
1. Pipeline parses and chunks the source document
2. Pipeline presents chunks to Claude Code with extraction prompts
3. Claude Code extracts decisions, patterns, warnings as structured JSON
4. Pipeline stores extractions and generates embeddings locally

**Result:** Zero API costs. Claude Code (already running) does the work.

---

## Target Users

### Primary: You (Philippebeliveau)
- Building the AI Engineering Workflows framework
- Need to encode knowledge from multiple books
- Want to dog-food the same system the community will use

### Secondary: AI Engineering Community
- Engineers learning AI/ML implementation patterns
- Teams building LLM-powered applications
- Practitioners who want decision frameworks, not just documentation

---

## Functional Requirements

### FR-1: Source Ingestion
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Ingest PDF files (books, papers) | Must Have |
| FR-1.2 | Ingest Markdown files (case studies, notes) | Must Have |
| FR-1.3 | Ingest from arXiv by paper ID | Should Have |
| FR-1.4 | Ingest web articles by URL | Could Have |
| FR-1.5 | Track ingestion status and history | Must Have |

### FR-2: Knowledge Extraction
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Extract decision frameworks (question, options, considerations) | Must Have |
| FR-2.2 | Extract code patterns with context | Must Have |
| FR-2.3 | Extract warnings and anti-patterns | Must Have |
| FR-2.4 | Extract benchmarks and performance data | Should Have |
| FR-2.5 | Batch extraction in single Claude session | Must Have |
| FR-2.6 | Preserve source attribution for all extractions | Must Have |

### FR-3: Storage
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Store raw parsed content in MongoDB | Must Have |
| FR-3.2 | Store processed chunks with extractions | Must Have |
| FR-3.3 | Store vector embeddings in Qdrant | Must Have |
| FR-3.4 | Support filtering by source type, topic, date | Must Have |
| FR-3.5 | Local-first with cloud deployment option | Must Have |

### FR-4: MCP Interface
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | `search_knowledge` - semantic search with filters | Must Have |
| FR-4.2 | `get_decisions` - structured decision queries | Must Have |
| FR-4.3 | `get_patterns` - code pattern retrieval | Must Have |
| FR-4.4 | `add_source` - trigger ingestion pipeline | Must Have |
| FR-4.5 | `list_sources` - inventory management | Must Have |
| FR-4.6 | FastAPI-based MCP server | Must Have |

---

## Non-Functional Requirements

### NFR-1: Performance
- Search queries return in <500ms for 10k chunks
- Batch ingestion of 500-page book completes in single session
- Local embedding generation (no external API latency)

### NFR-2: Scalability
- Support 10+ books, 50+ papers, 100+ case studies
- Horizontal scaling via Qdrant clustering (future)
- Stateless MCP server for multiple instances

### NFR-3: Cost
- Zero ongoing LLM API costs for search
- Zero embedding API costs (local models)
- Infrastructure costs: MongoDB Atlas free tier + Qdrant Cloud free tier OR self-hosted

### NFR-4: Developer Experience
- Single command to start local stack (`docker-compose up`)
- Clear CLI for ingestion operations
- MCP server auto-configured in Claude Code settings

### NFR-5: Extensibility
- New source types via adapter pattern
- New extraction types via extractor pattern
- Custom embedding models swappable

---

## Technical Architecture

### Stack Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Language** | Python 3.11+ | ML ecosystem, async support, BMAD tooling |
| **Raw Storage** | MongoDB | Flexible schema for varied source types |
| **Vector DB** | Qdrant | Best DX, hybrid search, filtering, free tier |
| **Embeddings** | sentence-transformers (local) | No API costs, good quality |
| **MCP Server** | FastAPI + fastapi-mcp | Already in your MCP config, proven |
| **Orchestration** | Taskfile | Simple, no ML training = no ZenML needed |
| **Containerization** | Docker Compose | Local dev, easy deployment |

### Data Models

```python
# Core entities

class Source:
    id: str
    type: SourceType  # BOOK, PAPER, CASE_STUDY, ARTICLE
    title: str
    authors: List[str]
    path: str
    ingested_at: datetime
    status: IngestionStatus
    metadata: dict

class Chunk:
    id: str
    source_id: str
    content: str
    position: ChunkPosition  # chapter, section, page
    token_count: int

class ExtractedKnowledge:
    chunk_id: str
    decisions: List[Decision]
    patterns: List[CodePattern]
    warnings: List[Warning]
    topics: List[str]
    extracted_at: datetime

class Decision:
    question: str
    options: List[str]
    considerations: str
    recommendation: Optional[str]
    context: str

class CodePattern:
    name: str
    description: str
    code: str
    language: str
    use_case: str

class Warning:
    issue: str
    consequence: str
    mitigation: str
```

### Project Structure

```
knowledge-pipeline/
├── pyproject.toml
├── Taskfile.yaml
├── docker-compose.yaml
├── .env.example
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── adapters/                 # Source ingestion
│   │   ├── __init__.py
│   │   ├── base.py               # SourceAdapter ABC
│   │   ├── pdf.py                # PDF books/papers
│   │   ├── markdown.py           # MD files
│   │   └── arxiv.py              # arXiv API
│   │
│   ├── processors/               # Content processing
│   │   ├── __init__.py
│   │   ├── chunker.py            # Chunking strategies
│   │   └── cleaner.py            # Text normalization
│   │
│   ├── extractors/               # Knowledge extraction
│   │   ├── __init__.py
│   │   ├── base.py               # Extractor ABC
│   │   ├── decision.py           # Decision framework extraction
│   │   ├── pattern.py            # Code pattern extraction
│   │   ├── warning.py            # Warning extraction
│   │   └── prompts/              # Extraction prompt templates
│   │       ├── decision.md
│   │       ├── pattern.md
│   │       └── warning.md
│   │
│   ├── embeddings/               # Vector generation
│   │   ├── __init__.py
│   │   └── local.py              # sentence-transformers
│   │
│   ├── storage/                  # Data persistence
│   │   ├── __init__.py
│   │   ├── mongodb.py            # Raw + processed storage
│   │   └── qdrant.py             # Vector operations
│   │
│   └── models/                   # Pydantic schemas
│       ├── __init__.py
│       ├── source.py
│       ├── chunk.py
│       ├── knowledge.py
│       └── search.py
│
├── scripts/
│   ├── ingest.py                 # CLI: python scripts/ingest.py book.pdf
│   ├── search.py                 # CLI: test search locally
│   └── export.py                 # Export knowledge to markdown
│
└── tests/
    ├── conftest.py
    ├── test_adapters/
    ├── test_processors/
    └── test_extractors/

knowledge-mcp/
├── pyproject.toml
├── Dockerfile
│
├── src/
│   ├── __init__.py
│   ├── server.py                 # FastAPI + MCP setup
│   ├── config.py
│   │
│   └── tools/                    # MCP tools
│       ├── __init__.py
│       ├── search.py             # search_knowledge
│       ├── decisions.py          # get_decisions
│       ├── patterns.py           # get_patterns
│       ├── ingest.py             # add_source
│       └── manage.py             # list_sources, stats
│
└── tests/
    └── test_tools/

knowledge-store/                  # Data directory (mostly gitignored)
├── raw/                          # Original files (gitignored)
├── processed/                    # Intermediate (gitignored)
├── manifests/                    # Ingestion records (tracked)
│   └── sources.json
└── .gitkeep
```

---

## Implementation Stages

### Stage 1: Foundation (MVP)
**Goal:** Ingest one PDF, search it via MCP

**Deliverables:**
- [ ] Project scaffolding (both repos)
- [ ] Pydantic models for Source, Chunk, ExtractedKnowledge
- [ ] PDF adapter (basic text extraction)
- [ ] Simple chunker (by section/page)
- [ ] MongoDB storage (local Docker)
- [ ] Qdrant storage (local Docker)
- [ ] Local embedding generation
- [ ] MCP server with `search_knowledge` tool
- [ ] Docker Compose for local stack

**Validation:**
- Ingest one chapter from "LLM Engineer's Handbook"
- Search returns relevant chunks
- MCP tool works in Claude Code

### Stage 2: Extraction Engine
**Goal:** Extract structured knowledge, not just text

**Deliverables:**
- [ ] Decision extractor with prompts
- [ ] Pattern extractor with prompts
- [ ] Warning extractor with prompts
- [ ] Batch extraction CLI
- [ ] Extraction storage in MongoDB
- [ ] `get_decisions` MCP tool
- [ ] `get_patterns` MCP tool

**Validation:**
- Extract decisions from RAG chapter
- Query "what embedding model should I use" returns decision framework
- Code patterns are retrievable with context

### Stage 3: Full Pipeline
**Goal:** Production-ready ingestion for multiple sources

**Deliverables:**
- [ ] `add_source` MCP tool (trigger ingestion)
- [ ] Markdown adapter
- [ ] arXiv adapter
- [ ] Ingestion manifests (tracking)
- [ ] `list_sources` MCP tool
- [ ] Error handling and retry logic
- [ ] Progress reporting

**Validation:**
- Ingest both books fully
- Ingest 5 research papers
- Add case study markdown files
- All searchable via MCP

### Stage 4: Polish & Deploy
**Goal:** Community-ready deployment

**Deliverables:**
- [ ] Qdrant Cloud deployment
- [ ] MongoDB Atlas deployment
- [ ] MCP server containerization
- [ ] MCP server deployment (Railway/Fly.io)
- [ ] Authentication for premium content
- [ ] Rate limiting
- [ ] Documentation

**Validation:**
- Community member can add MCP server to their config
- Search works against hosted knowledge base
- No API keys required for basic use

---

## Success Metrics

### Stage 1 Success
- Single book searchable via MCP
- Search latency <1s locally
- Zero external API calls

### Stage 2 Success
- 50+ decisions extracted from one book
- 20+ code patterns extracted
- Structured queries return relevant results

### Stage 3 Success
- 2 books + 10 papers + 5 case studies ingested
- Batch ingestion completes without manual intervention
- Cross-source search works

### Stage 4 Success
- Public MCP server accessible
- 10+ community users connected
- <500ms search latency on hosted version

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| PDF parsing quality varies | Extraction errors | Medium | Test with multiple PDF types, add cleaning |
| Batch extraction too slow | Bad UX | Low | Chunk batching, progress indicators |
| Embedding quality insufficient | Poor search results | Medium | Test multiple models, hybrid search |
| Qdrant free tier limits | Scaling issues | Low | Self-host option, optimize chunk count |
| MongoDB schema changes | Migration pain | Medium | Versioned schemas, migration scripts |

---

## Open Questions

1. **Chunk size strategy?**
   - Fixed token count vs. semantic boundaries
   - Recommendation: Start with ~512 tokens, adjust based on retrieval quality

2. **Multi-book deduplication?**
   - Same concepts in multiple books
   - Recommendation: Keep all, rank by source recency/authority

3. **Extraction prompt iteration?**
   - How to improve prompts over time
   - Recommendation: Version prompts, track extraction quality

4. **Premium content separation?**
   - How to gate enterprise case studies
   - Recommendation: Metadata flag + MCP auth layer

---

## Next Steps

1. **Review this brief** - Confirm scope and priorities
2. **Create Architecture doc** - Detail the technical design
3. **Set up project scaffolding** - Both repos with structure
4. **Implement Stage 1** - MVP end-to-end

---

## Appendix: Extraction Prompt Examples

### Decision Extraction Prompt
```markdown
You are extracting decision frameworks from technical content.

Given this text chunk, identify any decision points where an engineer
must choose between options. For each decision found, extract:

- question: The decision to be made (as a question)
- options: The available choices
- considerations: Factors that affect the choice
- recommendation: Default/common choice if mentioned

Text:
---
{chunk_content}
---

Return as JSON array. If no decisions found, return empty array.
```

### Pattern Extraction Prompt
```markdown
You are extracting reusable code patterns from technical content.

Given this text chunk, identify any code patterns, implementations,
or architectural patterns that could be reused. For each pattern:

- name: Short descriptive name
- description: What it does and when to use it
- code: The code snippet (if present)
- language: Programming language
- use_case: When this pattern applies

Text:
---
{chunk_content}
---

Return as JSON array. If no patterns found, return empty array.
```

---

**Brief Status:** Complete - Ready for Architecture Phase
