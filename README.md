# Knowledge Pipeline

AI Engineering knowledge extraction system that serves structured insights via MCP (Model Context Protocol) to Claude Code and Claude Desktop users.

## Quick Start - Connect to the MCP Server

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

## What's Inside

The knowledge base contains structured extractions from AI engineering methodology books:

- **Decisions** - When to choose X over Y, with trade-offs
- **Patterns** - Reusable solutions with implementation guidance
- **Warnings** - Anti-patterns and mistakes to avoid
- **Methodologies** - Step-by-step processes for AI engineering tasks

## Architecture

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
        │  Atlas   │                   │  Cloud   │
        └──────────┘                   └──────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                packages/mcp-server (server)                  │
│     FastAPI + MCP → Semantic Search → Structured Results    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Claude Desktop / Code
```

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
