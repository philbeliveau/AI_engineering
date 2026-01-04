# Knowledge Pipeline

**An AI-powered knowledge system that gives developers instant access to best practices, patterns, and pitfalls from the AI engineering literature.**

---

## Why This Exists

Building AI applications is hard. The best practices are scattered across books, research papers, and case studies. Developers waste hours searching for answers to questions like:

- *"Should I use RAG or fine-tuning for my use case?"*
- *"What's the best chunking strategy for legal documents?"*
- *"What are common production pitfalls with LLM APIs?"*

**Knowledge Pipeline solves this** by extracting structured knowledge from authoritative sources and making it instantly accessible through Claude Code and Claude Desktop via MCP.

---

## What It Does

| Capability | Description |
|------------|-------------|
| **Instant Answers** | Ask Claude about AI engineering and get answers grounded in expert sources |
| **Structured Knowledge** | Decisions, patterns, warnings, and methodologies — not just raw text |
| **Multi-Source Synthesis** | Combines insights from multiple books and papers for balanced perspective |
| **Contextual Guidance** | Recommendations adapt to your specific domain, scale, and constraints |

---

## Who It's For

- **AI/ML Engineers** building LLM applications, RAG systems, or AI agents
- **Software Developers** adding AI capabilities to existing products
- **Technical Leaders** making architectural decisions about AI infrastructure
- **Researchers** exploring practical implementation of AI concepts

---

## Knowledge Sources

The system extracts structured knowledge from:

| Source Type | Examples |
|-------------|----------|
| **Books** | AI engineering methodology books, LLM application guides |
| **Research Papers** | RAG techniques, embedding strategies, evaluation methods |
| **Case Studies** | Production deployments, failure analyses, optimization stories |

Each source is processed to extract:
- **Decisions** — Architectural choices with trade-offs and recommendations
- **Patterns** — Reusable solutions with implementation code
- **Warnings** — Anti-patterns and pitfalls to avoid
- **Methodologies** — Step-by-step processes for complex tasks

---

## How It Works

```
┌──────────────────────────────────────────────────────────────────────┐
│  1. INGESTION PIPELINE (One-time)                                    │
│                                                                      │
│  Books/Papers/Cases → Chunking → LLM Extraction → Structured Data   │
│                                                                      │
│  Extracts: decisions, patterns, warnings, methodologies              │
└──────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│  2. VECTOR STORAGE                                                   │
│                                                                      │
│  MongoDB (metadata) + Qdrant (384d embeddings)                       │
│                                                                      │
│  Enables semantic search across all extracted knowledge              │
└──────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│  3. MCP SERVER (Real-time)                                           │
│                                                                      │
│  FastAPI + MCP Protocol → Claude Desktop / Claude Code               │
│                                                                      │
│  7 tools for search, decisions, patterns, warnings, methodologies    │
└──────────────────────────────────────────────────────────────────────┘
```

**Key Design Choice:** Extractions are for *navigation*, Claude is for *synthesis*. The MCP tools return structured results; Claude synthesizes them into actionable advice.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Runtime** | Python 3.11, uv package manager |
| **API** | FastAPI + fastapi-mcp |
| **Vector DB** | Qdrant Cloud (384d embeddings) |
| **Document DB** | MongoDB Atlas |
| **Embeddings** | all-MiniLM-L6-v2 (local, no API costs) |
| **Extraction** | Claude API (one-time ingestion only) |
| **Deployment** | Railway (server), Docker |

---

## Quick Start — Connect to the MCP Server

Add the Knowledge Pipeline to your Claude configuration to get AI engineering knowledge directly in your conversations.

### Claude Desktop / Claude Code

Add to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

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

Then restart Claude Desktop/Claude Code.

## Available MCP Tools

Once connected, Claude can use these tools to answer your AI engineering questions:

| Tool | Description |
|------|-------------|
| `search_knowledge` | Semantic search across all AI engineering knowledge |
| `get_decisions` | Architectural decisions with trade-offs and recommendations |
| `get_patterns` | Reusable implementation patterns with code examples |
| `get_warnings` | Anti-patterns and pitfalls to avoid |
| `list_sources` | List all knowledge sources (books, papers, case studies) |

### Example Questions

After connecting, try asking Claude:

- "What are best practices for LLM API retry logic?"
- "Show me patterns for semantic caching"
- "What decisions should I consider for RAG vs fine-tuning?"
- "What are common pitfalls when building AI agents?"

## Project Structure

```
packages/
├── pipeline/      # Batch ingestion & extraction (PDF → Knowledge)
└── mcp-server/    # Real-time MCP query server (Knowledge → Claude)
```

## Development

See individual package READMEs for development setup:

- [MCP Server Development](packages/mcp-server/README.md)
- Pipeline Development (coming soon)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check (MongoDB + Qdrant status) |
| `GET /docs` | Interactive API documentation |
| `/mcp` | MCP protocol endpoint for Claude clients |

## Status

**Production:** https://knowledge-mcp-production.up.railway.app

| Service | Status |
|---------|--------|
| MCP Server | Deployed on Railway |
| MongoDB | Atlas M0 (Free) |
| Qdrant | Cloud (Free) |

## License

MIT
