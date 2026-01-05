# Knowledge Pipeline - Claude Development Notes

## Project Overview

Building an AI engineering knowledge system that extracts structured knowledge from methodology books and serves it via MCP to Claude Code users.

**Core Philosophy:** Extractions are for NAVIGATION, Claude is for SYNTHESIS.

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

**Phase:** Epic 5 - Production Deployment
**Deployed:** MCP Server live on Railway
**Completed:** Epics 1-4, Stories 5.2-5.5

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

---

**Full architecture:** `_bmad-output/architecture.md`
**Implementation rules:** `_bmad-output/project-context.md`
