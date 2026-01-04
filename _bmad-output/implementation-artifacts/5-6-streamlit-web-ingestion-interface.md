# Story 5.6: Streamlit Web Ingestion Interface

Status: in-progress

## Story

As a **builder**,
I want a web-based drag-and-drop interface for ingesting documents into the knowledge pipeline,
so that I can easily upload files and monitor database status without using CLI commands.

## Acceptance Criteria

1. **Given** the Streamlit app is running
   **When** I navigate to the web interface
   **Then** I see a drag-and-drop file upload area, metadata input fields, and database status sidebar

2. **Given** the sidebar displays database status
   **When** I view the MongoDB section
   **Then** I see connection status, source count, chunk count, and extraction count for the current project

3. **Given** the sidebar displays database status
   **When** I view the Qdrant section
   **Then** I see connection status, vector count, dimension (384d), and collection status

4. **Given** I upload a supported file (PDF, MD, DOCX, HTML, PPTX)
   **When** I click the "Ingest Document" button
   **Then** the ingestion pipeline runs and displays real-time output with success/error feedback

5. **Given** I provide optional metadata (category, tags, year)
   **When** the document is ingested
   **Then** the metadata is stored with the source record in MongoDB

6. **Given** the ingestion completes successfully
   **When** I view the "Recent Sources" table
   **Then** I see the newly ingested document with title, type, status, and ingestion date

7. **Given** I click the "Refresh Status" button
   **When** the status updates
   **Then** MongoDB and Qdrant statistics refresh to show current counts

8. **Given** the Streamlit app is deployed to Railway
   **When** I access the production URL
   **Then** the web interface is publicly accessible and connects to cloud databases (MongoDB Atlas, Qdrant Cloud)

## Tasks / Subtasks

- [x] Task 1: Add Streamlit dependency (AC: #1)
  - [x] 1.1: Add `streamlit` to `packages/pipeline/pyproject.toml`
  - [x] 1.2: Run `uv sync` to install

- [x] Task 2: Implement database status functions (AC: #2, #3)
  - [x] 2.1: Create `get_mongodb_stats()` function returning sources/chunks/extractions counts
  - [x] 2.2: Create `get_qdrant_stats()` function returning vector count and collection info
  - [x] 2.3: Handle connection errors gracefully with error display

- [x] Task 3: Build Streamlit UI layout (AC: #1, #6)
  - [x] 3.1: Configure page with title, icon, and wide layout
  - [x] 3.2: Create sidebar with MongoDB and Qdrant status sections
  - [x] 3.3: Add refresh button to clear cache and update stats
  - [x] 3.4: Create main content area with two columns (upload + metadata)
  - [x] 3.5: Add "Recent Sources" table at bottom

- [x] Task 4: Implement file upload and metadata inputs (AC: #4, #5)
  - [x] 4.1: Add `st.file_uploader` with accepted types: pdf, md, markdown, docx, html, pptx
  - [x] 4.2: Add category dropdown: foundational, advanced, reference, case_study
  - [x] 4.3: Add tags text input (comma-separated)
  - [x] 4.4: Add year number input (1900-2100, default 2024)

- [x] Task 5: Implement ingestion execution (AC: #4)
  - [x] 5.1: Create `run_ingestion()` function that calls `uv run scripts/ingest.py`
  - [x] 5.2: Save uploaded file to temp location before ingestion
  - [x] 5.3: Pass metadata flags (--category, --tags, --year) to CLI
  - [x] 5.4: Display stdout/stderr in code block
  - [x] 5.5: Show success (balloons) or error state
  - [x] 5.6: Clean up temp file after ingestion

- [x] Task 6: Test and document (AC: all)
  - [x] 6.1: Test with PDF, Markdown, and DOCX files
  - [x] 6.2: Verify database counts update after ingestion
  - [x] 6.3: Add run instructions to `_bmad-output/data-ingestion-guide.md`

- [ ] Task 7: Railway deployment (AC: #8)
  - [ ] 7.1: Create `Dockerfile.streamlit` in `packages/pipeline/`
  - [ ] 7.2: Configure Railway service (GitHub repo, root directory, Dockerfile path)
  - [ ] 7.3: Set environment variables (MONGODB_URI, QDRANT_URL, QDRANT_API_KEY, PROJECT_ID)
  - [ ] 7.4: Deploy and verify production URL is accessible
  - [ ] 7.5: Test ingestion works with cloud databases

## Dev Notes

### Architecture Compliance

- **Location:** `packages/pipeline/web_app.py` (already created as prototype)
- **Dependencies:** Reuse existing `src/config.py`, `src/storage/mongodb.py`, `src/storage/qdrant.py`
- **No new API endpoints:** This is a standalone Streamlit app, not part of the MCP server
- **Subprocess pattern:** Uses `subprocess.run()` to call existing `scripts/ingest.py` CLI

### Technical Requirements

- **Streamlit version:** Latest stable (add via `uv add streamlit`)
- **Python:** 3.11+ (matches project)
- **No authentication:** Local development tool only
- **State management:** Use `st.cache_data` for database stats with manual refresh

### Metadata Schema (v1.1)

User provides 3 optional fields (everything else is auto-extracted):

| Field | Type | Values | Auto-filled |
|-------|------|--------|-------------|
| `category` | enum | `foundational`, `advanced`, `reference`, `case_study` | No |
| `tags` | list[str] | User-defined | No |
| `year` | int | 1900-2100 | No |
| `title` | str | - | Yes (from document) |
| `authors` | list[str] | - | Yes (from PDF metadata) |
| `type` | enum | `book`, `paper`, `case_study` | Yes (detected) |
| `project_id` | str | - | Yes (from env/config) |

### File Structure

```
packages/pipeline/
├── web_app.py              # Streamlit application (this story)
├── Dockerfile.streamlit    # Railway deployment (Task 7)
├── scripts/
│   └── ingest.py           # Existing CLI (called via subprocess)
└── src/
    ├── config.py           # Settings (reuse)
    └── storage/
        ├── mongodb.py      # MongoDBClient (reuse)
        └── qdrant.py       # QdrantStorageClient (reuse)
```

### UI Layout Reference

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

### Run Command (Local)

```bash
cd packages/pipeline
uv add streamlit
uv run streamlit run web_app.py
```

Opens at `http://localhost:8501`

### Railway Deployment

**Dockerfile:** `packages/pipeline/Dockerfile.streamlit`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pipeline package
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY web_app.py ./

# Install dependencies
RUN uv sync --frozen

# Streamlit config
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "web_app.py"]
```

**Railway Configuration:**

| Setting | Value |
|---------|-------|
| **Railway Project** | `knowledge-mcp` |
| **Service Name** | `streamlite` |
| **Service Type** | GitHub Repo |
| **Root Directory** | `packages/pipeline` |
| **Dockerfile Path** | `Dockerfile.streamlit` |

**Environment Variables:**

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `QDRANT_URL` | Qdrant Cloud URL |
| `QDRANT_API_KEY` | Qdrant Cloud API key |
| `PROJECT_ID` | `ai_engineering` |
| `PORT` | Auto-set by Railway (optional override) |

### Project Structure Notes

- Aligns with existing `packages/pipeline` structure
- Reuses storage clients without modification
- No changes to `packages/mcp-server`

### References

- [Source: packages/pipeline/src/storage/mongodb.py] - MongoDBClient for stats
- [Source: packages/pipeline/src/storage/qdrant.py] - QdrantStorageClient for vector stats
- [Source: packages/pipeline/src/models/source.py] - Source schema v1.1 with category, tags, year
- [Source: packages/pipeline/scripts/ingest.py] - CLI interface called via subprocess
- [Source: _bmad-output/architecture.md] - Overall system architecture

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Completion Notes List

- **Task 1:** Added `streamlit>=1.40.0` to `packages/pipeline/pyproject.toml` and ran `uv sync` - installed Streamlit 1.52.2 with dependencies (altair, pyarrow, pydeck, etc.)
- **Task 2:** Fixed import from `get_settings` to `settings` singleton. Added `@st.cache_data(ttl=60)` decorators for performance. Both `get_mongodb_stats()` and `get_qdrant_stats()` handle connection errors gracefully.
- **Task 3:** UI verified complete - page config (title, icon, wide layout), sidebar with MongoDB/Qdrant status, refresh button, two-column layout, Recent Sources table.
- **Task 4:** File uploader accepts pdf, md, markdown, docx, html, pptx. Category dropdown with empty + 4 options. Tags text input. Year number input (1900-2100, default 2024).
- **Task 5:** `run_ingestion()` calls `uv run scripts/ingest.py` via subprocess. Temp file handling with cleanup in finally block. Stdout/stderr display. Balloons on success.
- **Task 6:** 716/718 tests pass (2 pre-existing failures unrelated to this story). Added Web Interface section to data-ingestion-guide.md with run instructions and UI layout diagram.
- **Code Review Fix 1:** Fixed Docling/OpenCV `libGL.so.1` error using Context7 docs preferred solution - replaced `opencv-python` with `opencv-python-headless` in builder stage (no system deps needed).
- **Code Review Fix 2:** Fixed MongoDB connection leak in `get_mongodb_stats()` - added `finally` block to close connection after use.
- **Code Review Fix 3:** Replaced hardcoded collection names with `settings.sources_collection`, `settings.chunks_collection`, `settings.extractions_collection` per project-context.md rules.

### Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-01-04 | Story created | New feature request for web-based ingestion |
| 2026-01-04 | Implemented Tasks 1-6 | Complete Streamlit web interface for document ingestion |
| 2026-01-04 | Added Task 7: Railway deployment | Deploy Streamlit to Railway (service: streamlite in knowledge-mcp project) |
| 2026-01-04 | Code review fixes | Fixed Dockerfile libGL error, MongoDB connection leak, hardcoded collection names |

### File List

- `packages/pipeline/pyproject.toml` - Added streamlit>=1.40.0 dependency
- `packages/pipeline/web_app.py` - Fixed imports, caching, connection management, collection naming
- `packages/pipeline/Dockerfile.streamlit` - Added libgl1-mesa-glx and libglib2.0-0 system dependencies
- `_bmad-output/data-ingestion-guide.md` - Added Web Interface (Streamlit) section with run instructions
