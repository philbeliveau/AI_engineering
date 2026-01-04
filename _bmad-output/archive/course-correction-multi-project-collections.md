# Course Correction: Multi-Project Collection Architecture

> **SUPERSEDED** - This document has been replaced by `course-correction-knowledge-base-architecture.md`
>
> Research showed that Qdrant recommends **single collection with payload filtering** over multiple collections. The new document implements the research-backed approach.

**Date:** 2026-01-01
**Status:** ~~Proposed~~ **SUPERSEDED**
**Impact:** Medium - Schema and storage layer changes
**Affected Stories:** Future stories, minor refactor of 2.6, 3.6, 3.7, **Epic 4 (MCP Server)**

---

## Problem Statement

The current architecture uses fixed collection names (`sources`, `chunks`, `extractions`) which limits the system to a single knowledge domain. Users need to build workflows for multiple domains (e.g., "AI Engineering", "Time Series", "System Design") without mixing data.

---

## Current State

```
MongoDB: knowledge_db
├── sources      → All sources mixed
├── chunks       → All chunks mixed
└── extractions  → All extractions mixed

Qdrant:
├── chunks       → All chunk vectors mixed
└── extractions  → All extraction vectors mixed
```

**Limitations:**
- Cannot easily separate projects
- Cannot delete one project without affecting others
- Cannot backup/restore individual projects
- Queries must scan all data even for single project

---

## Proposed Solution: Option 2 - Collection-per-Project

```
MongoDB: knowledge_db
├── {project}_sources      → e.g., ai_engineering_sources
├── {project}_chunks       → e.g., ai_engineering_chunks
└── {project}_extractions  → e.g., ai_engineering_extractions

Qdrant:
├── {project}_chunks       → e.g., ai_engineering_chunks
└── {project}_extractions  → e.g., ai_engineering_extractions
```

### Example for Two Projects

```
MongoDB: knowledge_db
├── ai_engineering_sources
├── ai_engineering_chunks
├── ai_engineering_extractions
├── time_series_sources
├── time_series_chunks
└── time_series_extractions

Qdrant:
├── ai_engineering_chunks
├── ai_engineering_extractions
├── time_series_chunks
└── time_series_extractions
```

---

## Configuration Changes

### 1. Add Project ID to Config

**File:** `packages/pipeline/src/config.py`

```python
class Settings(BaseSettings):
    # Existing settings...

    # NEW: Project identification
    project_id: str = Field(
        default="default",
        description="Project identifier for collection namespacing"
    )

    @property
    def sources_collection(self) -> str:
        return f"{self.project_id}_sources"

    @property
    def chunks_collection(self) -> str:
        return f"{self.project_id}_chunks"

    @property
    def extractions_collection(self) -> str:
        return f"{self.project_id}_extractions"
```

### 2. Environment Variable

```bash
# .env
PROJECT_ID=ai_engineering

# Or per-command (prefered)
PROJECT_ID=time_series uv run scripts/ingest.py book.pdf
```

---

## Code Changes Required

### Storage Layer Updates

| File | Change |
|------|--------|
| `src/storage/mongodb.py` | Use `settings.sources_collection` instead of hardcoded `"sources"` |
| `src/storage/qdrant.py` | Use `settings.chunks_collection` instead of hardcoded `"chunks"` |
| `src/storage/extraction_storage.py` | Use `settings.extractions_collection` |
| `src/ingestion/pipeline.py` | Pass collection names from settings |
| `src/extraction/pipeline.py` | Pass collection names from settings |

### Affected Methods

**MongoDBClient:**
- `create_source()` → use `self.db[settings.sources_collection]`
- `get_source()` → use `self.db[settings.sources_collection]`
- `create_chunks_bulk()` → use `self.db[settings.chunks_collection]`
- `get_chunks_by_source()` → use `self.db[settings.chunks_collection]`
- `save_extraction()` → use `self.db[settings.extractions_collection]`
- `get_extractions_by_source()` → use `self.db[settings.extractions_collection]`

**QdrantStorageClient:**
- `ensure_collection()` → accept dynamic collection name
- `upsert_chunk_vector()` → use `settings.chunks_collection`
- `upsert_extraction_vector()` → use `settings.extractions_collection`

---

## CLI Changes

### Current Usage
```bash
uv run scripts/ingest.py /path/to/book.pdf
uv run scripts/extract.py <source_id>
```

### New Usage
```bash
# Set project for session
export PROJECT_ID=ai_engineering
uv run scripts/ingest.py /path/to/book.pdf
uv run scripts/extract.py <source_id>

# Or per-command
PROJECT_ID=time_series uv run scripts/ingest.py /path/to/ts-book.pdf
```

### Optional: Add --project flag
```bash
uv run scripts/ingest.py --project ai_engineering /path/to/book.pdf
uv run scripts/extract.py --project ai_engineering <source_id>
```

---

## Migration Plan

### Phase 1: Update Schema (Non-Breaking)
1. Add `project_id` to Settings with default value `"default"`
2. Update storage layer to use dynamic collection names
3. Existing data stays in `default_sources`, `default_chunks`, `default_extractions`

### Phase 2: Migrate Existing Data (Optional)
```bash
# Rename existing collections to ai_engineering_*
db.sources.renameCollection("ai_engineering_sources")
db.chunks.renameCollection("ai_engineering_chunks")
db.extractions.renameCollection("ai_engineering_extractions")
```

### Phase 3: Update MCP Server (Epic 4)

**Option A: Single Project per Server Instance**
```bash
# Start server for specific project
PROJECT_ID=ai_engineering uv run mcp-server
```
- Simplest approach
- Server reads `settings.project_id` on startup
- All tools query that project's collections
- Run multiple server instances for multiple projects

**Option B: Multi-Project via Tool Parameter**
```python
# Tool signature
async def search_extractions(
    query: str,
    project_id: str = "default",  # NEW parameter
    extraction_type: Optional[str] = None,
) -> list[dict]:
    ...
```
- More flexible
- Single server can query any project
- Requires tool signature changes

**Recommended:** Start with Option A, migrate to Option B if needed.

---

## Epic 4 (MCP Server) Changes

### Affected Files

| File | Change |
|------|--------|
| `packages/mcp-server/src/config.py` | Add `project_id` setting (same as pipeline) |
| `packages/mcp-server/src/storage/mongodb.py` | Use dynamic collection names |
| `packages/mcp-server/src/storage/qdrant.py` | Use dynamic collection names |
| `packages/mcp-server/src/tools/*.py` | All search tools use settings collections |

### Tool Changes

All MCP tools that query storage will automatically use the correct collections:
- `search_decisions`
- `search_patterns`
- `search_warnings`
- `search_methodologies`
- `search_checklists`
- `search_personas`
- `search_workflows`
- `get_source`
- `get_chunk`

---

## Testing Requirements

1. **Unit Tests:** Mock collection names, verify dynamic resolution
2. **Integration Tests:**
   - Create project A, ingest, extract
   - Create project B, ingest, extract
   - Verify isolation (project A queries don't return project B data)
3. **CLI Tests:** Verify `PROJECT_ID` env var works

---

## Acceptance Criteria

- [ ] `PROJECT_ID` environment variable configures collection names
- [ ] Collections are created as `{project_id}_{type}` (e.g., `ai_engineering_sources`)
- [ ] Existing scripts work with `PROJECT_ID=default` for backwards compatibility
- [ ] Can run ingestion for multiple projects without data mixing
- [ ] Can delete all collections for a project easily
- [ ] MCP server can query specific project

---

## Estimated Effort

### Pipeline Package (Epic 2-3)

| Task | Estimate |
|------|----------|
| Update Settings with project_id | 0.5h |
| Update MongoDBClient | 1h |
| Update QdrantStorageClient | 1h |
| Update pipelines | 0.5h |
| Update CLI scripts | 0.5h |
| Update tests | 1h |
| Documentation | 0.5h |
| **Subtotal** | **5h** |

### MCP Server Package (Epic 4)

| Task | Estimate |
|------|----------|
| Copy project_id to mcp-server Settings | 0.25h |
| Update mcp-server storage clients | 0.5h |
| Update MCP tools | 0.25h |
| Update mcp-server tests | 0.5h |
| **Subtotal** | **1.5h** |

### **Total Effort: ~6.5h**

---

## Decision

**Approved:** [ ]
**Approved with changes:** [ ]
**Rejected:** [ ]

**Notes:**
_To be filled after review_
