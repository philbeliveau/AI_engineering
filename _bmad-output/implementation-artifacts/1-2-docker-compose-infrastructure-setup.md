# Story 1.2: Docker Compose Infrastructure Setup

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want to run MongoDB and Qdrant locally via Docker Compose,
So that I have a working development database environment without cloud dependencies.

## Acceptance Criteria

**Given** Docker is installed on my machine
**When** I run `docker-compose up -d`
**Then** MongoDB is running on port 27017
**And** Qdrant is running on port 6333
**And** both services are accessible from the Python application
**And** data persists across container restarts via volumes

## Dependency Analysis

**Depends On:**
- **Story 1.1** (Initialize Monorepo Structure) - MUST be completed first
  - Requires directory restructuring: `packages/pipeline`, `packages/mcp-server`, `data/`
  - Requires uv initialization and dependency installation
  - Docker Compose file goes at monorepo root

**Blocks:**
- Story 1.3 (Pydantic Models) - needs running databases for validation testing
- Story 1.4 (MongoDB Storage Client) - needs MongoDB accessible
- Story 1.5 (Qdrant Storage Client) - needs Qdrant accessible

## Tasks / Subtasks

- [x] **Task 1: Verify Prerequisites** (AC: Docker installed)
  - [x] Check Docker installation: `docker --version`
  - [x] Check Docker Compose installation: `docker compose version`
  - [x] Verify Docker daemon is running: `docker ps`
  - [x] Confirm Story 1.1 is complete (check for `packages/` directory structure)

- [x] **Task 2: Create docker-compose.yaml** (AC: MongoDB port 27017, Qdrant port 6333)
  - [x] Create `docker-compose.yaml` at monorepo root (NOT in packages/)
  - [x] Define MongoDB service with image `mongo:7`
  - [x] Configure MongoDB port mapping `27017:27017`
  - [x] Set MongoDB environment: `MONGO_INITDB_DATABASE: knowledge_db`
  - [x] Define Qdrant service with image `qdrant/qdrant:latest`
  - [x] Configure Qdrant REST port `6333:6333`
  - [x] Configure Qdrant gRPC port `6334:6334`

- [x] **Task 3: Configure Volume Persistence** (AC: Data persists across restarts)
  - [x] Define named volume `mongodb_data` for MongoDB
  - [x] Mount MongoDB volume to `/data/db`
  - [x] Define named volume `qdrant_data` for Qdrant
  - [x] Mount Qdrant volume to `/qdrant/storage`
  - [x] Declare volumes in top-level `volumes:` section

- [x] **Task 4: Start and Verify Services** (AC: Both services accessible)
  - [x] Run `docker-compose up -d`
  - [x] Verify MongoDB is healthy: `docker-compose ps`
  - [x] Verify Qdrant is healthy: `docker-compose ps`
  - [x] Test MongoDB connection: `docker exec -it <container> mongosh --eval "db.stats()"`
  - [x] Test Qdrant REST API: `curl http://localhost:6333/collections`

- [x] **Task 5: Test Persistence** (AC: Data persists across restarts)
  - [x] Create test data in MongoDB
  - [x] Create test collection in Qdrant
  - [x] Stop containers: `docker-compose down`
  - [x] Restart containers: `docker-compose up -d`
  - [x] Verify test data still exists in both services

- [x] **Task 6: Test Python Application Access** (AC: Accessible from Python)
  - [x] Test pymongo connection from `packages/pipeline`
  - [x] Test qdrant-client connection from `packages/pipeline`
  - [x] Verify both clients can perform basic operations

## Dev Notes

### Docker Compose Configuration (EXACT SPECIFICATION)

**From Architecture Document (architecture.md:783-786):**

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

**CRITICAL:** Use this exact configuration. Do NOT deviate without architectural justification.

### MongoDB Configuration Details

**From Architecture Document (architecture.md:260-291):**

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Image | `mongo:7` | MongoDB 7.x (latest stable) |
| Port | `27017` | Default MongoDB port |
| Database | `knowledge_db` | Application database name |
| Volume Mount | `/data/db` | MongoDB data directory |

**Collections to be created (Future Stories):**
- `sources` - Book/paper metadata
- `chunks` - Raw text chunks
- `extractions` - Structured knowledge

**Indexes to be created (Future Stories):**
- `idx_extractions_type_topics` (compound on `type` + `topics`)
- `idx_extractions_source_id`
- `idx_chunks_source_id`

### Qdrant Configuration Details

**From Architecture Document (architecture.md:299-306):**

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Image | `qdrant/qdrant:latest` | Latest Qdrant release |
| REST Port | `6333` | HTTP API access |
| gRPC Port | `6334` | gRPC API access |
| Volume Mount | `/qdrant/storage` | Vector storage directory |

**Vector Configuration (Future Stories):**
- Vector size: 384 dimensions (all-MiniLM-L6-v2 output)
- Distance metric: Cosine
- Collections: `chunks`, `extractions`
- Payload fields: `{source_id, chunk_id, type, topics}`

### File Location

**CRITICAL:** `docker-compose.yaml` MUST be placed at monorepo root:

```
ai-engineering-knowledge/              # Monorepo root
├── docker-compose.yaml                # <-- HERE
├── packages/
│   ├── pipeline/
│   └── mcp-server/
└── data/
```

**DO NOT place in:**
- `packages/pipeline/docker-compose.yaml` (WRONG)
- `packages/mcp-server/docker-compose.yaml` (WRONG)
- `.docker/docker-compose.yaml` (WRONG)

### Previous Story Intelligence (Story 1.1)

**Key Learnings from Story 1.1:**
- Directory restructuring required: `knowledge-pipeline` → `packages/pipeline`
- Directory restructuring required: `knowledge-mcp` → `packages/mcp-server`
- Directory restructuring required: `knowledge-store` → `data`
- Python version must be pinned to 3.11 via `uv python pin 3.11`
- Lock files (uv.lock) should be committed for reproducibility

**PREREQUISITE CHECK:** Verify Story 1.1 is complete before starting:
```bash
# All of these should exist:
ls packages/pipeline/pyproject.toml
ls packages/mcp-server/pyproject.toml
ls packages/pipeline/uv.lock
ls packages/mcp-server/uv.lock
```

If any are missing, Story 1.1 is not complete.

### Connection Testing Scripts

**MongoDB Connection Test (Python):**
```python
# Run from packages/pipeline directory
# uv run python -c "..."
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.knowledge_db
print(f"Connected to MongoDB: {db.name}")
print(f"Collections: {db.list_collection_names()}")
```

**Qdrant Connection Test (Python):**
```python
# Run from packages/pipeline directory
# uv run python -c "..."
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
collections = client.get_collections()
print(f"Connected to Qdrant")
print(f"Collections: {collections}")
```

**Qdrant REST API Test (curl):**
```bash
# Health check
curl http://localhost:6333/

# List collections
curl http://localhost:6333/collections
```

### Architecture Compliance Checklist

**From Architecture Document:**

- [x] MongoDB image is `mongo:7` (architecture.md:783)
- [x] MongoDB port is `27017` (architecture.md:783)
- [x] MongoDB database name is `knowledge_db` (architecture.md:260-291)
- [x] Qdrant image is `qdrant/qdrant:latest` (architecture.md:784)
- [x] Qdrant REST port is `6333` (architecture.md:784)
- [x] Qdrant gRPC port is `6334` (architecture.md:784)
- [x] Both services use named volumes for persistence
- [x] docker-compose.yaml is at monorepo root
- [x] Healthchecks configured for both services (added in code review)
- [x] Container names explicitly set for debugging

### Environment Variables

**For Local Development (default):**
```
MONGODB_URI=mongodb://localhost:27017
QDRANT_URL=http://localhost:6333
QDRANT_GRPC_PORT=6334
```

These values are already the defaults in the architecture. No `.env` file is required for local Docker Compose development.

**For Production (Future - Story 5.4):**
- MongoDB Atlas connection string
- Qdrant Cloud connection string
- SSL/TLS configurations

### Common Issues & Solutions

**Issue 1: Port Already in Use**
```bash
# Check what's using port 27017 or 6333
lsof -i :27017
lsof -i :6333

# Solution: Stop conflicting service or change ports
```

**Issue 2: Docker Daemon Not Running**
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

**Issue 3: Permission Denied on Volumes**
```bash
# Fix volume permissions
docker-compose down -v  # Remove volumes
docker-compose up -d    # Recreate with correct permissions
```

**Issue 4: Qdrant Not Responding**
```bash
# Check Qdrant logs
docker-compose logs qdrant

# Qdrant needs a few seconds to initialize
sleep 5 && curl http://localhost:6333/
```

### Success Validation

**Story is COMPLETE when:**
- [x] `docker-compose.yaml` exists at monorepo root
- [x] `docker-compose up -d` starts both services without errors
- [x] `docker-compose ps` shows both services as "Up" or "running" (healthy)
- [x] MongoDB accepts connections on port 27017
- [x] Qdrant responds on port 6333
- [x] Data persists after `docker-compose down` and `docker-compose up -d`
- [x] Python pymongo client connects successfully
- [x] Python qdrant-client connects successfully
- [x] `.env.example` template exists (added in code review)

### References

- [Source: architecture.md#Docker-Compose-Services] - Docker Compose configuration
- [Source: architecture.md#Data-Architecture] - MongoDB collections structure
- [Source: architecture.md#Qdrant-Configuration] - Qdrant vector configuration
- [Source: epics.md#Story-1.2] - Story acceptance criteria
- [Source: Story 1.1] - Previous story learnings and prerequisites

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Docker version 20.10.21 confirmed
- Docker Compose version v2.13.0 confirmed
- Story 1.1 structure verified: `packages/pipeline/`, `packages/mcp-server/` exist with pyproject.toml and uv.lock files
- `docker-compose.yaml` already existed at monorepo root with correct architecture-compliant configuration
- MongoDB container: `ai_engineering-mongodb-1` running on port 27017
- Qdrant container: `ai_engineering-qdrant-1` running on ports 6333, 6334

### Completion Notes List

- **Task 1 Complete:** All prerequisites verified - Docker 20.10.21, Docker Compose v2.13.0, Story 1.1 structure in place
- **Task 2 Complete:** `docker-compose.yaml` exists at monorepo root with exact architecture specification (mongo:7, qdrant/qdrant:latest)
- **Task 3 Complete:** Named volumes configured: `mongodb_data:/data/db`, `qdrant_data:/qdrant/storage`
- **Task 4 Complete:** Both services running and responding:
  - MongoDB: `mongosh --eval "db.stats()"` returns valid JSON
  - Qdrant: `curl http://localhost:6333/collections` returns `{"status":"ok"}`
- **Task 5 Complete:** Persistence verified - test data survived container restart cycle (`docker-compose down` → `docker-compose up -d`)
- **Task 6 Complete:** Python clients from `packages/pipeline` successfully connect and perform CRUD operations:
  - `pymongo.MongoClient("mongodb://localhost:27017")` - insert/find/drop operations work
  - `qdrant_client.QdrantClient(host="localhost", port=6333)` - create_collection/get_collections/delete_collection work

### Change Log

- 2025-12-30: Story implemented and verified - all acceptance criteria satisfied
- 2025-12-30: **Code Review Fixes Applied** (Adversarial Senior Developer Review):
  - Added healthchecks to docker-compose.yaml for both MongoDB and Qdrant
  - Removed deprecated `version: '3.8'` key (Docker Compose V2 doesn't need it)
  - Added explicit container names (`knowledge-mongodb`, `knowledge-qdrant`)
  - Created `.env.example` template file per project-context.md requirements
  - Created `packages/pipeline/tests/` and `packages/mcp-server/tests/` directories with conftest.py
  - Added `__init__.py` files to empty source directories for proper Python packaging
  - Completed Architecture Compliance and Success Validation checklists

### File List

**Modified:**
- docker-compose.yaml (added healthchecks, container names, removed deprecated version key)

**Created (Code Review):**
- .env.example (environment configuration template)
- packages/pipeline/tests/__init__.py
- packages/pipeline/tests/conftest.py
- packages/mcp-server/tests/__init__.py
- packages/mcp-server/tests/conftest.py
- packages/pipeline/src/adapters/__init__.py
- packages/pipeline/src/storage/__init__.py
- packages/pipeline/src/models/__init__.py
- packages/pipeline/src/processors/__init__.py
- packages/mcp-server/src/tools/__init__.py

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.5 (Adversarial Code Review)
**Date:** 2025-12-30

### Review Summary

| Category | Issues Found | Issues Fixed |
|----------|--------------|--------------|
| HIGH | 3 | 3 |
| MEDIUM | 4 | 4 |
| LOW | 2 | 2 |

### Issues Fixed

1. **HIGH-1:** Story claimed credit for docker-compose.yaml created in Story 1.1 → Clarified in File List as verification story
2. **HIGH-2:** Missing `.env.example` file → Created with MongoDB/Qdrant configuration template
3. **HIGH-3:** No healthchecks in docker-compose.yaml → Added MongoDB mongosh ping and Qdrant TCP port check
4. **MEDIUM-1:** No `tests/` directories → Created with __init__.py and conftest.py fixtures
5. **MEDIUM-2:** Empty source directories without __init__.py → Added to all subdirectories
6. **MEDIUM-3/4:** Incomplete checklists → All items verified and marked complete
7. **LOW-1:** Deprecated `version: '3.8'` key → Removed
8. **LOW-2:** Auto-generated container names → Set explicit names for debugging

### Verification Results

```
$ docker compose ps
NAME                STATUS
knowledge-mongodb   running (healthy)
knowledge-qdrant    running (healthy)
```

**Verdict:** ✅ APPROVED - All issues fixed, story ready for done status
