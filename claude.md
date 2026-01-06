# Knowledge Pipeline - Claude Development Notes

## Project Overview

Building an AI engineering knowledge system that extracts structured knowledge from methodology books and serves it via MCP to Claude Code users.

**Core Philosophy:** Extractions are for NAVIGATION, Claude is for SYNTHESIS.

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

## Current Status

**Phase:** Epic 5 - Production Deployment (Pipeline Complete)
**Next Phase:** Epic 6 - AI Engineering Workflow Authoring
**Deployed:** MCP Server live on Railway
**Completed:** Epics 1-4, Stories 5.2-5.5

### Upcoming: Knowledge Ingestion & Workflow Creation

With the pipeline infrastructure complete, the next phase involves:
1. **Ingesting AI engineering literature** - MLOps books, RAG papers, agent patterns, evaluation frameworks
2. **Authoring the BMAD AI-Eng workflow** - Using extracted knowledge to ground each step
3. **Embedding MCP queries into workflow agents** - Contextual knowledge access at runtime

## Key Artifacts

| Document | Purpose | Status |
|----------|---------|--------|
| `_bmad-output/architecture.md` | All technical decisions | Complete |
| `_bmad-output/prd.md` | Product requirements | Complete |
| `_bmad-output/epics.md` | Implementation roadmap | Complete |
| `_bmad-output/project-context.md` | AI agent implementation rules | Complete |
| `_bmad-output/implementation-artifacts/` | Story files | In Progress |

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                 packages/pipeline (batch)                    │
│   Adapters → Processors → Extractors → Storage (WRITE)      │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
        ┌──────────┐                   ┌──────────┐
        │ MongoDB  │                   │  Qdrant  │
        └──────────┘                   └──────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                             ▼                                │
│                packages/mcp-server (server)                  │
│     Middleware → Tools → Storage (READ) → FastAPI-MCP       │
└─────────────────────────────────────────────────────────────┘
```

## Technical Stack

- **Runtime:** Python 3.11, uv package manager
- **API:** FastAPI + fastapi-mcp
- **Storage:** MongoDB 7 + Qdrant (768d vectors)
- **Embeddings:** nomic-embed-text-v1.5 (local, 8K context)

## For AI Agents

**Before implementing any code, read:**
`_bmad-output/project-context.md`

This contains 85+ critical implementation rules covering:
- Naming conventions and async patterns
- API response formats (MANDATORY)
- Testing and code quality rules
- Anti-patterns to avoid

## Project Structure (Target)

```
packages/
├── pipeline/          # Batch ingestion & extraction (WRITE)
│   ├── src/
│   │   ├── adapters/  # PDF, Markdown, arXiv
│   │   ├── extractors/# Decision, Pattern, Warning, Methodology
│   │   └── storage/   # MongoDB, Qdrant clients
│   └── scripts/
└── mcp-server/        # Real-time query server (READ)
    └── src/
        ├── tools/     # MCP tools (search, get_decisions, etc.)
        └── middleware/# Rate limiting, auth
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `search_knowledge` | Semantic search across all AI engineering knowledge |
| `get_decisions` | Architectural decisions with trade-offs |
| `get_patterns` | Reusable implementation patterns |
| `get_warnings` | Anti-patterns and pitfalls to avoid |
| `list_sources` | List all knowledge sources |

## Knowledge Resource Categories

The following categories of AI engineering literature will be ingested to ground the workflow:

| Category | Content Type | Purpose in Workflow |
|----------|--------------|---------------------|
| **MLOps/LLMOps Methodology** | Maturity models, lifecycle stages | Structure workflow phases |
| **RAG Architecture** | Chunking, retrieval, reranking patterns | Design retrieval systems |
| **Agent Patterns** | ReAct, multi-agent, tool use | Build agentic features |
| **Evaluation Frameworks** | Metrics, benchmarks, LLM-as-judge | Quality assurance steps |
| **Fine-tuning Decision Trees** | When to customize vs prompt vs RAG | Model selection guidance |
| **Production Infrastructure** | Serving, caching, scaling | Deployment decisions |
| **Data Engineering** | Pipelines, versioning, quality | Data preparation steps |
| **Safety & Governance** | Compliance, bias, guardrails | Risk management |

### Key Source Materials

- **Books:** "Designing ML Systems", "LLM Engineer's Handbook", "Building LLM Apps", "Practical MLOps"
- **Papers:** RAG surveys, agent architecture papers, evaluation benchmarks
- **Guides:** Anthropic cookbook, framework documentation (LangChain, LlamaIndex)
- **Standards:** NIST AI RMF, ML Model Cards

## Known Issues

See `_bmad-output/docs/known-issues.md` for documented bugs and workarounds, including:

- **Docling PDF parsing failure** with FrameMaker PDFs (hierarchical page tree bug)
  - Workaround: Use `pdftotext` to extract, then ingest the text file

---

**Full architecture:** `_bmad-output/architecture.md`
**Implementation rules:** `_bmad-output/project-context.md`
**Known issues:** `_bmad-output/docs/known-issues.md`
