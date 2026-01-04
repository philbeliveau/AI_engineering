# Data Ingestion Pipeline Guide

## Overview

The Knowledge Pipeline transforms raw documents (PDFs, Markdown, etc.) into a searchable knowledge base. Documents are chunked, embedded, and stored in MongoDB + Qdrant for semantic search via MCP tools.

```
Document → Adapter → Chunks → Embeddings → Storage → MCP Query
```

**Cost Model:** Ingestion uses local embeddings (zero API costs). Only extraction uses Claude API.

---

## Quick Start

```bash
cd packages/pipeline

# Basic ingestion
uv run scripts/ingest.py /path/to/document.pdf

# With metadata
uv run scripts/ingest.py book.pdf \
  --category foundational \
  --tags "rag,llm" \
  --year 2024

# Extract structured knowledge (optional)
uv run scripts/extract.py <source_id>
```

---

## Supported Formats

| Format | Extension |
|--------|-----------|
| PDF | `.pdf` |
| Markdown | `.md` |
| Word | `.docx` |
| HTML | `.html` |
| PowerPoint | `.pptx` |

---

## Configuration

Create `.env` in `packages/pipeline/`:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=knowledge_db
QDRANT_URL=http://localhost:6333
PROJECT_ID=ai_engineering
```

---

## Pipeline Stages

### 1. Adapter (DoclingAdapter)
Extracts text and structure from any supported format.

### 2. Chunking (HybridChunker)
Splits into ~512 token chunks respecting semantic boundaries.

### 3. Embedding (LocalEmbedder)
Generates 384-dimensional vectors using `all-MiniLM-L6-v2`.

### 4. Storage
- **MongoDB:** Sources and chunks (metadata + text)
- **Qdrant:** Vectors (semantic search)

---

## CLI Options

```
uv run scripts/ingest.py <file> [options]

Options:
  --chunk-size N      Tokens per chunk (default: 512)
  --category TYPE     foundational|advanced|reference|case_study
  --tags TAG1,TAG2    Comma-separated tags
  --year YYYY         Publication year
  --project ID        Project namespace
  --dry-run           Validate only
  --verbose           Debug logging
```

---

## Web Interface (Streamlit)

A drag-and-drop web UI for ingesting documents without CLI commands.

### Starting the Web App

```bash
cd packages/pipeline
uv run streamlit run web_app.py
```

Opens at `http://localhost:8501`

### Features

- **Drag & Drop Upload:** PDF, Markdown, DOCX, HTML, PPTX
- **Metadata Input:** Category, tags, publication year
- **Database Status:** Real-time MongoDB and Qdrant connection status
- **Recent Sources:** View recently ingested documents
- **Refresh Button:** Update database statistics

### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  📚 Knowledge Pipeline Ingestion                             │
├──────────────┬──────────────────────────────────────────────┤
│  SIDEBAR     │  MAIN CONTENT                                │
│              │                                              │
│  MongoDB     │  ┌────────────────────┐  ┌───────────────┐  │
│  ✅ Connected │  │  Drag & Drop File  │  │  Category ▼   │  │
│  Sources: 12 │  │  [    📄    ]      │  │  Tags: ___    │  │
│  Chunks: 847 │  │                    │  │  Year: 2024   │  │
│  Extrs: 156  │  └────────────────────┘  └───────────────┘  │
│              │                                              │
│  Qdrant      │  [🚀 Ingest Document]                        │
│  ✅ Connected │                                              │
│  Vectors: 847│  ─────────────────────────────────────────   │
│  Dim: 384d   │  Recent Sources                              │
│              │  | Title          | Type | Status | Date   | │
│  [🔄 Refresh]│  | Building LLM   | book | done   | 12/22  | │
└──────────────┴──────────────────────────────────────────────┘
```

### Requirements

- MongoDB running (local or cloud)
- Qdrant running (local or cloud)
- `.env` file configured with connection strings

---

## Example Workflow

```bash
# 1. Ingest a book
uv run scripts/ingest.py data/building-llm-apps.pdf \
  --category foundational \
  --tags "rag,production" \
  --year 2024
# Output: Source ID: 507f1f77bcf86cd799439011

# 2. Extract knowledge
uv run scripts/extract.py 507f1f77bcf86cd799439011

# 3. Query via MCP (from Claude Code)
# Documents now searchable via knowledge-pipeline MCP server
```

---

## Production MCP Server

Add to `claude_desktop_config.json`:

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

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| File not found | Use absolute path |
| Connection error | Check MongoDB/Qdrant running |
| Slow ingestion | Normal - embedding is bottleneck |

---

## Architecture Reference

Full details: `_bmad-output/architecture.md`
Implementation rules: `_bmad-output/project-context.md`
