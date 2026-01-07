# Knowledge Pipeline - Claude Development Notes

## Project Overview

Building an AI engineering knowledge system that extracts structured knowledge from methodology books and serves it via MCP to Claude Code users.

**Core Philosophy:** Extractions are for NAVIGATION, Claude is for SYNTHESIS.

## Knowledge-Grounding Principles (CRITICAL)

When authoring workflows, agents, or any BMAD artifacts that use the Knowledge MCP:

### The Three Principles

1. **Reference knowledge PATTERNS, not copy-paste**
   - Extract principles and methodologies
   - Don't hardcode values from a single source
   - Present as "current recommendation" not "the answer"

2. **Query at RUNTIME**
   - The Knowledge MCP will grow with more sources
   - Design workflows to query dynamically
   - Don't embed static content that becomes stale

3. **Show SYNTHESIS approach**
   - Teach HOW to apply knowledge, not just WHAT it says
   - Include synthesis steps in workflow guidance
   - Example: "Extract patterns → Identify trade-offs → Surface warnings"

### Synthesis Pattern Template

```markdown
### Query Knowledge MCP
**MANDATORY QUERIES** - Execute and synthesize:
- Query 1: [specific endpoint + query]
- Query 2: [specific endpoint + query]

**Synthesis Approach:**
1. Extract [what to look for]
2. Identify [patterns]
3. Surface [warnings]

**Key Pattern/Warning to Surface:**
> [Example from current knowledge - will evolve as more sources added]
```

### Anti-Patterns to Avoid

- NEVER hardcode specific values as "the answer"
- NEVER copy-paste entire sections from one book
- NEVER present knowledge as static/final - it grows
- NEVER skip Knowledge MCP queries when they would add value

## The Two-Layer Architecture

This project serves a dual purpose that is critical to understand:

### Layer 1: Workflow Authoring (Build Time)
The knowledge pipeline enables authoring a comprehensive BMAD AI engineering workflow grounded in best practices from literature. The pipeline had to exist FIRST to build a workflow that follows documented methodologies.

### Layer 2: Workflow Execution (Run Time)
Users run the pre-built workflow. Agents WITHIN the workflow query the knowledge base contextually, with queries conditioned on context accumulated from previous steps.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BUILD TIME (Author, now)                         │
│  Knowledge DB ──► Author ONE comprehensive BMAD AI-Eng Workflow     │
│                   (structure, agents, steps grounded in literature) │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RUN TIME (Users, later)                          │
│                                                                     │
│  Step 1: Gather Requirements ──► Agent queries knowledge with       │
│          (context: chatbot)       current project context           │
│                │                                                    │
│                ▼                                                    │
│  Step 2: Design RAG ──────────► Agent queries: "chunking strategy   │
│          (context: chatbot +      for [doc type] with [constraints]"│
│           eval requirements)                                        │
│                │                                                    │
│                ▼                                                    │
│  Step 3: Select Stack ────────► Agent queries conditioned on ALL    │
│          (context: accumulated)   previous decisions                │
│                                                                     │
│  Each agent's query is CONDITIONAL on accumulated context           │
└─────────────────────────────────────────────────────────────────────┘
```

### Why This Architecture Works

| Factor | Explanation |
|--------|-------------|
| **Structure is fixed** | BMAD provides the skeleton - knowledge fills in best practices |
| **Context accumulates** | Each step knows what came before - queries are targeted |
| **One workflow, deep** | Iterate and refine ONE workflow until excellent |
| **Knowledge as augmentation** | Agents surface relevant info at the right moment |
| **Human-authored structure** | Human expertise structures flow; knowledge grounds details |

### The Chicken-and-Egg Problem Solved

```
Problem:
  "I need a workflow to build AI systems"
    └── But workflows should follow best practices
        └── But best practices are scattered across books
            └── But I can't read everything → STUCK

Solution:
  1. Build pipeline to extract best practices (Epic 1-4) ✅
  2. Use extracted knowledge to author workflow (Epic 6+)
  3. Embed knowledge access INTO the workflow agents
  4. Workflow becomes self-documenting AND contextually intelligent
```

**The pipeline is not overhead - it's the prerequisite for building a knowledge-grounded workflow.**

## Cost Model Clarification

**One-time extraction (Epic 2 & 3):** Uses `LLMClient` with Anthropic API to extract structured knowledge from raw chunks. This incurs API costs during database population.

**MCP server queries (Epic 4+):** Zero LLM API costs. The server performs vector search and returns pre-extracted data. No API calls are made.

**Workflow building (post-MVP):** Builder uses Claude Code + MCP tools to query the pre-built database. Claude Code synthesizes results locally - no additional extraction costs.

```
ONE-TIME EXTRACTION ($$$ API costs)
PDF/MD → Chunks → LLMClient → Claude API → Extractions → DB + Qdrant
                                                              │
                                                              ▼
RUNTIME QUERIES (Zero API costs)
Builder → Claude Code → MCP Tools → Vector Search → Pre-extracted Data → Synthesis
```

## Production MCP Server

**Live:** https://knowledge-mcp-production.up.railway.app

Add to your Claude config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "knowledge-pipeline": {
      "type": "sse",
      "url": "https://knowledge-mcp-production.up.railway.app/mcp"
    }
  }
}
```

## Database Overview (CRITICAL - READ THIS)

**Connection String:** Set via `MONGODB_URI` environment variable (see `.env.example`)

**Important:** MongoDB contains BOTH collections. Always query `knowledge-pipeline_extractions` (NOT `ai_engineering_extractions` which is empty).

### Collections in knowledge_db
- `knowledge-pipeline_chunks` - Document chunks ingested from sources
- `knowledge-pipeline_sources` - Source metadata (books, papers, etc.)
- `knowledge-pipeline_extractions` - **MAIN COLLECTION** Contains all structured extractions (1,684+ total)
- `ai_engineering_chunks`, `ai_engineering_sources`, `ai_engineering_extractions` - Legacy/unused collections

### Extraction Counts (knowledge-pipeline_extractions) CHanges all the time 
| Type | Count | Status |
|------|-------|--------|
| **decision** | 356 | ✅ Complete |
| **warning** | 335 | ✅ Complete |
| **pattern** | 314 | ✅ Complete |
| **methodology** | 182 | ✅ Complete |
| **checklist** | 115 | ✅ Complete |
| **workflow** | 187 | ✅ Complete (recently added) |
| **persona** | 195 | ✅ Complete (recently added) |
| **TOTAL** | **1,684** | Ready for MCP serving |

**All extractions are from diverse sources across the knowledge base, providing comprehensive AI engineering reference material.**

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `search_knowledge` | Semantic search across all AI engineering knowledge |
| `get_decisions` | Architectural decisions with trade-offs |
| `get_patterns` | Reusable implementation patterns |
| `get_warnings` | Anti-patterns and pitfalls to avoid |
| `list_sources` | List all knowledge sources |

## Extraction Process

### How to Run Extractions

All 7 extractors are defined in:
- `packages/pipeline/src/extractors/` - Base and specific extractor classes
- `packages/pipeline/src/extractors/prompts/` - LLM prompts for each extraction type

**Extraction script locations:**
- `packages/pipeline/extract_llms_book.py` - Script for batch extraction from sources
- Run via: `.venv/bin/python extract_llms_book.py`

### Extraction Method
1. **Input:** Document chunks from MongoDB (`knowledge-pipeline_chunks`)
2. **Processing:** Each chunk passed through extractor with context
3. **LLM Call:** Claude 3 Haiku generates structured JSON for each chunk
4. **Validation:** Pydantic models validate extraction structure
5. **Storage:** Valid extractions saved to `knowledge-pipeline_extractions` with:
   - `type`: extraction type (decision, pattern, warning, etc.)
   - `source_id`: reference to source document
   - `chunk_id`: which chunk generated it
   - `topics`: auto-tagged categories (rag, evaluation, llm, training, etc.)
   - `extracted_at`: timestamp

**Key Implementation Files:**
- `src/extractors/base.py:ExtractorRegistry` - Manages all extractors
- `src/extractors/llm_client.py:LLMClient` - Handles Claude API calls
- Each extractor inherits from `BaseExtractor` and implements custom extraction logic

## Known Issues

See `_bmad-output/docs/known-issues.md` for documented bugs and workarounds, including:

- **Docling PDF parsing failure** with FrameMaker PDFs (hierarchical page tree bug)
  - Workaround: Use `pdftotext` to extract, then ingest the text file
- **MongoDB collection confusion** - Always use `knowledge-pipeline_extractions`, NOT `ai_engineering_extractions`

---

**Full architecture:** `_bmad-output/architecture.md`
**Implementation rules:** `_bmad-output/project-context.md`
**Known issues:** `_bmad-output/docs/known-issues.md`
