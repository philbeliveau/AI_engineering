# Story 1.2: Docker Compose Infrastructure Setup

Status: ready-for-dev

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

- [ ] **Task 1: Verify Prerequisites** (AC: Docker installed)
  - [ ] Check Docker installation: `docker --version`
  - [ ] Check Docker Compose installation: `docker compose version`
  - [ ] Verify Docker daemon is running: `docker ps`
  - [ ] Confirm Story 1.1 is complete (check for `packages/` directory structure)

- [ ] **Task 2: Create docker-compose.yaml** (AC: MongoDB port 27017, Qdrant port 6333)
  - [ ] Create `docker-compose.yaml` at monorepo root (NOT in packages/)
  - [ ] Define MongoDB service with image `mongo:7`
  - [ ] Configure MongoDB port mapping `27017:27017`
  - [ ] Set MongoDB environment: `MONGO_INITDB_DATABASE: knowledge_db`
  - [ ] Define Qdrant service with image `qdrant/qdrant:latest`
  - [ ] Configure Qdrant REST port `6333:6333`
  - [ ] Configure Qdrant gRPC port `6334:6334`

- [ ] **Task 3: Configure Volume Persistence** (AC: Data persists across restarts)
  - [ ] Define named volume `mongodb_data` for MongoDB
  - [ ] Mount MongoDB volume to `/data/db`
  - [ ] Define named volume `qdrant_data` for Qdrant
  - [ ] Mount Qdrant volume to `/qdrant/storage`
  - [ ] Declare volumes in top-level `volumes:` section

- [ ] **Task 4: Start and Verify Services** (AC: Both services accessible)
  - [ ] Run `docker-compose up -d`
  - [ ] Verify MongoDB is healthy: `docker-compose ps`
  - [ ] Verify Qdrant is healthy: `docker-compose ps`
  - [ ] Test MongoDB connection: `docker exec -it <container> mongosh --eval "db.stats()"`
  - [ ] Test Qdrant REST API: `curl http://localhost:6333/collections`

- [ ] **Task 5: Test Persistence** (AC: Data persists across restarts)
  - [ ] Create test data in MongoDB
  - [ ] Create test collection in Qdrant
  - [ ] Stop containers: `docker-compose down`
  - [ ] Restart containers: `docker-compose up -d`
  - [ ] Verify test data still exists in both services

- [ ] **Task 6: Test Python Application Access** (AC: Accessible from Python)
  - [ ] Test pymongo connection from `packages/pipeline`
  - [ ] Test qdrant-client connection from `packages/pipeline`
  - [ ] Verify both clients can perform basic operations

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

- [ ] MongoDB image is `mongo:7` (architecture.md:783)
- [ ] MongoDB port is `27017` (architecture.md:783)
- [ ] MongoDB database name is `knowledge_db` (architecture.md:260-291)
- [ ] Qdrant image is `qdrant/qdrant:latest` (architecture.md:784)
- [ ] Qdrant REST port is `6333` (architecture.md:784)
- [ ] Qdrant gRPC port is `6334` (architecture.md:784)
- [ ] Both services use named volumes for persistence
- [ ] docker-compose.yaml is at monorepo root

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
- [ ] `docker-compose.yaml` exists at monorepo root
- [ ] `docker-compose up -d` starts both services without errors
- [ ] `docker-compose ps` shows both services as "Up" or "running"
- [ ] MongoDB accepts connections on port 27017
- [ ] Qdrant responds on port 6333
- [ ] Data persists after `docker-compose down` and `docker-compose up -d`
- [ ] Python pymongo client connects successfully
- [ ] Python qdrant-client connects successfully

### References

- [Source: architecture.md#Docker-Compose-Services] - Docker Compose configuration
- [Source: architecture.md#Data-Architecture] - MongoDB collections structure
- [Source: architecture.md#Qdrant-Configuration] - Qdrant vector configuration
- [Source: epics.md#Story-1.2] - Story acceptance criteria
- [Source: Story 1.1] - Previous story learnings and prerequisites

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

_To be filled by dev agent_

### File List

_To be filled by dev agent - list all files created/modified:_
- docker-compose.yaml (CREATE)
