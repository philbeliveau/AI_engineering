# Knowledge Pipeline - Claude Development Notes

## Project Overview

Building an AI engineering knowledge system that extracts structured knowledge from methodology books and serves it via MCP to Claude Code users.

**Core Philosophy:** Extractions are for NAVIGATION, Claude is for SYNTHESIS.

## Current Status

**Phase:** Implementation Ready
**Current Work:** Epic 1 - Foundation Setup
**Next Story:** 1.1 - Initialize Monorepo Structure (ready-for-dev)

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
- **Storage:** MongoDB 7 + Qdrant (384d vectors)
- **Embeddings:** all-MiniLM-L6-v2 (local)

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

## Current Priority

**Story 1.1: Initialize Monorepo Structure**
- Restructure directories to `packages/` layout
- Create pyproject.toml for both packages
- Set up docker-compose (MongoDB + Qdrant)
- Initialize uv with all dependencies

See: `_bmad-output/implementation-artifacts/1-1-initialize-monorepo-structure.md`

---

**Full architecture:** `_bmad-output/architecture.md`
**Implementation rules:** `_bmad-output/project-context.md`
