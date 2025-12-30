# Story 1.1: Initialize Monorepo Structure

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want to initialize the monorepo with both `packages/pipeline` and `packages/mcp-server` packages using uv,
So that I have a properly structured project with all dependencies installed and ready for development.

## Acceptance Criteria

**Given** a fresh directory for the project
**When** I run the initialization commands from the architecture doc
**Then** both `packages/pipeline` and `packages/mcp-server` directories exist with `pyproject.toml` and `uv.lock`
**And** all dependencies are installed (fastapi, pymongo, qdrant-client, sentence-transformers, etc.)
**AND** the project structure matches the architecture specification

## Current State Analysis

**CRITICAL DISCOVERY:** Partial monorepo structure already exists but needs restructuring!

**Current State (Old Structure):**
- ✅ `knowledge-pipeline/` directory exists with `src/` and `scripts/` subdirectories
- ✅ `knowledge-mcp/` directory exists with `src/` subdirectory
- ✅ `knowledge-mcp/pyproject.toml` exists with dependencies defined
- ✅ `knowledge-store/` directory exists (data directory)

**Required Changes (New Structure):**
- 🔄 Move `knowledge-pipeline/` → `packages/pipeline/`
- 🔄 Move `knowledge-mcp/` → `packages/mcp-server/`
- 🔄 Move `knowledge-store/` → `data/`
- ❌ `packages/pipeline/pyproject.toml` **MISSING**
- ❌ `uv.lock` files **MISSING** in both packages
- ❌ `docker-compose.yaml` **MISSING** at monorepo root
- ❌ Dependencies **NOT INSTALLED** (no lock files)
- ❌ Python version **NOT PINNED** (no uv.lock)

**Git Status:**
- One initial commit: `bc247ce first commit`
- Project is tracked in git

## Tasks / Subtasks

- [x] Verify uv is installed (AC: System-level)
  - [x] Check `uv --version` (minimum version requirement from architecture)
  - [x] If not installed, provide installation guidance

- [x] Restructure directories to match new architecture (AC: Structure matches architecture)
  - [x] Create `packages/` directory at monorepo root
  - [x] Move `knowledge-pipeline/` → `packages/pipeline/`
  - [x] Move `knowledge-mcp/` → `packages/mcp-server/`
  - [x] Move `knowledge-store/` → `data/`
  - [x] Verify all existing files preserved after move

- [x] Create packages/pipeline/pyproject.toml (AC: Both packages exist with pyproject.toml)
  - [x] Match structure of packages/mcp-server/pyproject.toml
  - [x] Include all dependencies from architecture: fastapi, uvicorn, pymongo, qdrant-client, sentence-transformers, pymupdf, pydantic, pydantic-settings
  - [x] Include dev dependencies: pytest, pytest-asyncio, ruff, mypy
  - [x] Set Python version requirement >=3.11

- [x] Initialize uv for packages/pipeline (AC: uv.lock exists)
  - [x] Run `cd packages/pipeline && uv python pin 3.11`
  - [x] Run `uv sync` to generate uv.lock and install dependencies
  - [x] Verify .venv created

- [x] Initialize uv for packages/mcp-server (AC: uv.lock exists)
  - [x] Run `cd packages/mcp-server && uv python pin 3.11`
  - [x] Run `uv sync` to generate uv.lock and install dependencies
  - [x] Verify .venv created

- [x] Create docker-compose.yaml at monorepo root (AC: Docker infrastructure)
  - [x] MongoDB service on port 27017
  - [x] Qdrant service on port 6333
  - [x] Volume persistence for both services
  - [x] Match architecture specification exactly

- [x] Verify complete project structure (AC: Structure matches architecture)
  - [x] Verify all directories from architecture exist
  - [x] Verify both packages are installable
  - [x] Document any deviations from architecture

- [x] Update .gitignore (AC: Clean git status)
  - [x] Add .venv/ (both packages)
  - [x] Add uv.lock (or commit, per team decision)
  - [x] Add .env files
  - [x] Add data/raw/ and data/processed/

## Dev Notes

### Project Structure Context

This is **Epic 1, Story 1** - the foundational story that establishes the entire development environment. All subsequent stories depend on this setup being correct.

**Target Monorepo Architecture (New Structure):**
```
ai-engineering-knowledge/              # Monorepo root (CURRENT DIRECTORY)
├── docker-compose.yaml                # ❌ TO CREATE
├── packages/                          # ❌ TO CREATE
│   ├── pipeline/                      # 🔄 MOVE from knowledge-pipeline/
│   │   ├── pyproject.toml             # ❌ TO CREATE
│   │   ├── uv.lock                    # ❌ TO CREATE (via uv sync)
│   │   ├── .venv/                     # ❌ TO CREATE (via uv sync)
│   │   ├── src/                       # ✅ EXISTS (empty)
│   │   └── scripts/                   # ✅ EXISTS (empty)
│   └── mcp-server/                    # 🔄 MOVE from knowledge-mcp/
│       ├── pyproject.toml             # ✅ EXISTS (needs move)
│       ├── uv.lock                    # ❌ TO CREATE (via uv sync)
│       ├── .venv/                     # ❌ TO CREATE (via uv sync)
│       └── src/                       # ✅ EXISTS (has some files)
└── data/                              # 🔄 MOVE from knowledge-store/
```

**Reference Template:** `packages/mcp-server/pyproject.toml` (after move) is correctly structured. Use it as a reference for creating `packages/pipeline/pyproject.toml`.

### Critical Architecture Requirements

**From Architecture Document (architecture.md:213-227):**

**packages/pipeline initialization:**
```bash
cd packages/pipeline
uv init && uv python pin 3.11
uv add fastapi uvicorn pymongo qdrant-client sentence-transformers pymupdf pydantic pydantic-settings
uv add --dev pytest pytest-asyncio ruff mypy
```

**packages/mcp-server initialization:**
```bash
cd packages/mcp-server
uv init && uv python pin 3.11
uv add fastapi fastapi-mcp uvicorn qdrant-client pymongo
uv add --dev pytest
```

**⚠️ CRITICAL:** The architecture specifies exact dependencies. Do NOT deviate without architectural justification.

### Dependency Version Requirements

**From Architecture Document (architecture.md:198-209):**

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.11+ | Runtime |
| fastapi | >=0.115 | API framework |
| fastapi-mcp | >=0.4.0 | MCP protocol layer (mcp-server only) |
| qdrant-client | >=1.13 | Vector storage |
| sentence-transformers | >=5.0 | Local embeddings (pipeline only) |
| pymongo | latest | MongoDB client |
| pymupdf | latest | PDF parsing (pipeline only) |
| pydantic | >=2.0 | Data validation |
| uv | latest | Package management |

**⚠️ CRITICAL CONFLICT DETECTED:**
- `packages/mcp-server/pyproject.toml` uses `fastapi-mcp>=0.1.0`
- Architecture specifies `fastapi-mcp>=0.4.0`

**DECISION REQUIRED:** Determine if this is intentional or needs update.

### Docker Compose Configuration

**From Architecture Document (architecture.md:783-786):**

Docker Compose services required:
- `mongodb`: MongoDB 7 on port 27017
- `qdrant`: Qdrant latest on port 6333

**Reference Implementation:**
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: knowledge_db

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  mongodb_data:
  qdrant_data:
```

### Architecture Compliance Checklist

**Python Package Manager (uv):**
- ✅ Use `uv` for all dependency management (architecture.md:160-165)
- ✅ Generate lockfiles for reproducible environments
- ✅ Use `uv run` pattern (eliminates manual venv management)
- ✅ Pin Python 3.11+ with `uv python pin 3.11`

**Project Structure (architecture.md:591-723):**
- ✅ Dual-package pattern: `packages/pipeline` (batch) + `packages/mcp-server` (server)
- ✅ Separate `src/` directories in each package
- ✅ Tests mirror `src/` structure (future stories)
- ✅ Scripts in `packages/pipeline/scripts/`
- ✅ Data directory `data/` at root

**Naming Conventions (architecture.md:408-432):**
- ✅ Files/modules: `snake_case.py`
- ✅ Classes: `PascalCase`
- ✅ Functions/variables: `snake_case`
- ✅ Constants: `UPPER_SNAKE_CASE`

### Package Boundary Understanding

**From Architecture Document (architecture.md:729-748):**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    packages/pipeline (batch)                         │
│  Adapters ──▶ Processors ──▶ Extractors ──▶ Storage (write)         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              ┌──────────┐                   ┌──────────┐
              │ MongoDB  │                   │  Qdrant  │
              └────┬─────┘                   └────┬─────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    │
┌───────────────────────────────────┼─────────────────────────────────┐
│                                   ▼                                  │
│                    packages/mcp-server (server)                      │
│  Middleware ──▶ Tools ──▶ Storage (read) ──▶ FastAPI-MCP            │
└─────────────────────────────────────────────────────────────────────┘
```

**Package Purpose:**
- `packages/pipeline`: Batch ingestion and extraction (WRITE to databases)
- `packages/mcp-server`: Real-time query server (READ from databases)
- Shared infrastructure: MongoDB + Qdrant

**Dependency Differences:**
- `packages/pipeline`: Needs `sentence-transformers` (local embeddings), `pymupdf` (PDF parsing)
- `packages/mcp-server`: Needs `fastapi-mcp` (MCP protocol), `fastembed` (search)

### Testing Standards

**From Architecture Document (architecture.md:456-462):**

Test organization for FUTURE stories (not this story):
- Tests in separate `tests/` directory
- Mirror `src/` structure
- Test files prefixed: `test_*.py`
- Shared fixtures in `conftest.py`

**This story:** No tests required (infrastructure setup only)

### Implementation Sequence

**CRITICAL ORDER:**

1. **First:** Verify uv installation
2. **Second:** Restructure directories (`packages/pipeline`, `packages/mcp-server`, `data/`)
3. **Third:** Create `packages/pipeline/pyproject.toml` (modeled after mcp-server)
4. **Fourth:** Initialize both packages with `uv python pin 3.11` + `uv sync`
5. **Fifth:** Create `docker-compose.yaml`
6. **Sixth:** Update `.gitignore`
7. **Finally:** Verify complete structure

**⚠️ DO NOT:**
- Skip directory restructuring (old paths will break architecture compliance)
- Skip dependency installation (no lock files = incomplete setup)
- Modify `packages/mcp-server/pyproject.toml` without justification
- Add dependencies not in architecture
- Create source code files (that's future stories)

### Success Validation

**Story is COMPLETE when:**
- ✅ Directory structure matches architecture (`packages/pipeline`, `packages/mcp-server`, `data/`)
- ✅ Both `pyproject.toml` files exist with correct dependencies
- ✅ Both `uv.lock` files exist
- ✅ Both `.venv/` directories exist with installed dependencies
- ✅ `docker-compose.yaml` exists at monorepo root
- ✅ `docker-compose up -d` successfully starts MongoDB + Qdrant
- ✅ Can run `cd packages/pipeline && uv run python --version` (shows Python 3.11+)
- ✅ Can run `cd packages/mcp-server && uv run python --version` (shows Python 3.11+)
- ✅ Project structure matches architecture specification

### Known Issues & Decisions

**Issue 1: Directory Restructuring Required**
- **Impact:** Old structure (`knowledge-pipeline/`, `knowledge-mcp/`, `knowledge-store/`) needs migration
- **Decision:** Move directories to new structure (`packages/pipeline/`, `packages/mcp-server/`, `data/`)
- **Validation:** Ensure all existing files preserved after move

**Issue 2: fastapi-mcp Version Mismatch** ✅ RESOLVED
- **Previous:** `packages/mcp-server/pyproject.toml` had `fastapi-mcp>=0.1.0`
- **Architecture:** Specifies `fastapi-mcp>=0.4.0`
- **Resolution:** Fixed during code review - pyproject.toml now specifies correct versions per architecture.md:198-209

**Issue 3: Git Tracking**
- **Decision Needed:** Should `uv.lock` be committed or gitignored?
- **Recommendation:** Commit lock files for reproducibility (per uv best practices)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- uv version verified: 0.8.5
- Both packages sync successfully with Python 3.11.13
- docker-compose.yaml validates successfully
- Docker daemon not running during test (expected on this system)

### Completion Notes List

1. **Directory Restructuring Complete**: Moved `knowledge-pipeline/` → `packages/pipeline/`, `knowledge-mcp/` → `packages/mcp-server/`, `knowledge-store/` → `data/`. All files preserved.

2. **Pipeline Package Initialized**: Created `pyproject.toml` with all architecture-specified dependencies (fastapi>=0.115, sentence-transformers>=5.0, pymupdf, qdrant-client>=1.13, etc.). uv.lock generated with 60 packages installed.

3. **MCP Server Package Initialized**: Existing `pyproject.toml` used. Created README.md (required by hatchling). uv.lock generated with 77 packages installed. Note: fastapi-mcp resolved to 0.4.0 (matching architecture spec) despite pyproject.toml specifying >=0.1.0.

4. **Docker Compose Created**: MongoDB 7 on port 27017, Qdrant latest on ports 6333/6334, with volume persistence. Config validates successfully.

5. **Gitignore Updated**: Added .venv/, __pycache__/, .env files, data subdirectories.

6. **Issue 2 FIXED (Code Review)**: Updated `packages/mcp-server/pyproject.toml` with correct version constraints per architecture.md:198-209:
   - `fastapi>=0.115` (was >=0.109.0)
   - `fastapi-mcp>=0.4.0` (was >=0.1.0)
   - `qdrant-client>=1.13` (was >=1.7.0)
   - `pydantic>=2.0` (was >=2.5.0, relaxed to match architecture)
   - Re-ran `uv sync` to regenerate lock file with correct constraints.

7. **Decision on Issue 3 (uv.lock tracking)**: Lock files NOT gitignored - they should be committed for reproducibility per uv best practices.

8. **Git State Cleaned (Code Review)**: Staged all changes properly so git recognizes renames instead of separate delete+add operations.

9. **Note on data/embeddings/ directory**: This directory exists but is NOT in architecture.md. It's gitignored so no immediate issue, but should be added to architecture if intentional.

### Change Log

- 2025-12-30: Story implementation completed. All 8 tasks/subtasks marked complete. Directory restructured, both packages initialized with uv, docker-compose created, .gitignore updated.
- 2025-12-30: **Code Review Fixes Applied** - Fixed mcp-server dependency versions, cleaned git state, verified docker-compose config.

### File List

**Created:**
- packages/ (directory)
- packages/pipeline/pyproject.toml
- packages/pipeline/uv.lock
- packages/pipeline/.python-version
- packages/pipeline/.venv/ (directory with installed packages)
- packages/pipeline/README.md
- packages/mcp-server/uv.lock
- packages/mcp-server/.python-version
- packages/mcp-server/.venv/ (directory with installed packages)
- packages/mcp-server/README.md
- docker-compose.yaml
- data/embeddings/ (directory - not in architecture, gitignored)
- data/manifests/ (directory)
- data/raw/ (directory, gitignored)
- data/processed/ (directory, gitignored)

**Moved (git tracks as renames):**
- knowledge-pipeline/src/__init__.py → packages/pipeline/src/__init__.py
- knowledge-pipeline/src/adapters/ → packages/pipeline/src/adapters/
- knowledge-pipeline/src/extractors/ → packages/pipeline/src/extractors/
- knowledge-pipeline/src/models/ → packages/pipeline/src/models/
- knowledge-pipeline/src/processors/ → packages/pipeline/src/processors/
- knowledge-pipeline/src/storage/ → packages/pipeline/src/storage/
- knowledge-pipeline/scripts/ → packages/pipeline/scripts/
- knowledge-mcp/pyproject.toml → packages/mcp-server/pyproject.toml
- knowledge-mcp/src/__init__.py → packages/mcp-server/src/__init__.py
- knowledge-mcp/src/tools/ → packages/mcp-server/src/tools/
- knowledge-store/ → data/

**Modified:**
- .gitignore (added Python, env, and data patterns)
- packages/mcp-server/pyproject.toml (fixed dependency versions during code review)
