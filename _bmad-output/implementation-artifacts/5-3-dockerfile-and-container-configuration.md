# Story 5.3: Dockerfile and Container Configuration

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want a Dockerfile for the knowledge-mcp server,
So that the application can be containerized and deployed to Railway.

## Acceptance Criteria

**Given** the Dockerfile exists in knowledge-mcp
**When** I build and run the container
**Then** the server starts and accepts connections
**And** environment variables configure MongoDB/Qdrant connections
**And** the image is optimized for size (multi-stage build)
**And** health check is configured for container orchestration

## Dependency Analysis

**Depends On:**
- **Story 1.1 (Initialize Monorepo Structure)** - ✅ DONE - Provides `packages/mcp-server/` structure
- **Story 1.2 (Docker Compose Infrastructure)** - ✅ DONE - Provides docker-compose.yaml for local dev
- **Epic 4 Stories (MCP Server)** - Server code must exist to containerize
  - Story 4.1 (FastAPI Server with MCP Integration) - Core server.py needed

**Blocks:**
- Story 5.5 (Railway Deployment Pipeline) - Cannot deploy without Dockerfile

**Integration Points:**
- MongoDB connection via `MONGODB_URI` environment variable
- Qdrant connection via `QDRANT_URL` environment variable
- FastAPI server exposed on configurable `PORT` (Railway uses dynamic ports)

## Tasks / Subtasks

- [ ] **Task 1: Create Dockerfile with Multi-Stage Build** (AC: Optimized image size)
  - [ ] Create `packages/mcp-server/Dockerfile`
  - [ ] Use `python:3.11-slim` as base image (matches project Python version)
  - [ ] Implement multi-stage build: builder stage + runtime stage
  - [ ] Install uv in builder stage for dependency resolution
  - [ ] Copy only necessary files to runtime stage (no dev dependencies)
  - [ ] Target final image size < 500MB

- [ ] **Task 2: Configure uv Package Installation in Docker** (AC: Dependencies installed correctly)
  - [ ] Copy `pyproject.toml` and `uv.lock` to builder stage
  - [ ] Run `uv sync --frozen --no-dev` for production dependencies only
  - [ ] Export dependencies to virtualenv in builder stage
  - [ ] Copy virtualenv to runtime stage
  - [ ] Verify all required packages: fastapi, fastapi-mcp, uvicorn, pymongo, qdrant-client, fastembed

- [ ] **Task 3: Configure Application Entry Point** (AC: Server starts correctly)
  - [ ] Copy `src/` directory to container
  - [ ] Set `WORKDIR` to `/app`
  - [ ] Use exec form for CMD: `["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]`
  - [ ] Support `PORT` environment variable override for Railway
  - [ ] Add `--proxy-headers` flag for reverse proxy compatibility

- [ ] **Task 4: Implement Health Check** (AC: Container orchestration compatible)
  - [ ] Add `HEALTHCHECK` instruction to Dockerfile
  - [ ] Check `/health` endpoint (create if not exists in server.py)
  - [ ] Configure interval: 30s, timeout: 10s, retries: 3, start_period: 40s
  - [ ] Ensure health check uses lightweight HTTP client (curl or wget)

- [ ] **Task 5: Configure Environment Variables** (AC: External configuration works)
  - [ ] Document required env vars in Dockerfile comments
  - [ ] Set sensible defaults for local development
  - [ ] Required: `MONGODB_URI`, `QDRANT_URL`
  - [ ] Optional: `PORT` (default 8000), `ENVIRONMENT` (default "production")
  - [ ] Create `.env.example` with all variables documented

- [ ] **Task 6: Add .dockerignore File** (AC: Build context optimized)
  - [ ] Create `packages/mcp-server/.dockerignore`
  - [ ] Exclude `.venv/`, `__pycache__/`, `*.pyc`
  - [ ] Exclude `.git/`, `.gitignore`
  - [ ] Exclude `tests/`, `*.md` (except README if needed)
  - [ ] Exclude `.env` files (secrets protection)
  - [ ] Exclude IDE config: `.vscode/`, `.idea/`

- [ ] **Task 7: Create docker-compose.dev.yaml for Local Testing** (AC: Easy local container testing)
  - [ ] Create `packages/mcp-server/docker-compose.dev.yaml`
  - [ ] Reference root docker-compose.yaml for MongoDB/Qdrant services
  - [ ] Add mcp-server service building from local Dockerfile
  - [ ] Configure proper networking between services
  - [ ] Mount volumes for hot reload during development (optional)

- [ ] **Task 8: Create Health Endpoint in Server** (AC: Health check works)
  - [ ] Add `/health` GET endpoint to `src/server.py` (if not exists)
  - [ ] Return `{"status": "healthy", "timestamp": "<iso8601>"}` on success
  - [ ] Check MongoDB connection status
  - [ ] Check Qdrant connection status
  - [ ] Return 503 with error details if any dependency unhealthy

- [ ] **Task 9: Write Build and Run Tests** (AC: Container works end-to-end)
  - [ ] Test: `docker build -t knowledge-mcp .` succeeds
  - [ ] Test: Container starts without errors
  - [ ] Test: Health endpoint returns 200
  - [ ] Test: Environment variables are correctly passed
  - [ ] Test: MCP endpoint is accessible
  - [ ] Document test commands in README

- [ ] **Task 10: Document Container Usage** (AC: Clear documentation)
  - [ ] Add "Docker" section to `packages/mcp-server/README.md`
  - [ ] Document build command: `docker build -t knowledge-mcp .`
  - [ ] Document run command with env vars
  - [ ] Document docker-compose usage for local dev
  - [ ] Document Railway-specific considerations

## Dev Notes

### Architecture Compliance

**From architecture.md - Hosting Stack:**
- MCP Server deploys to Railway (~$5/mo)
- Railway auto-deploy on push to `main`
- Environment variables via Railway dashboard

**From architecture.md - Project Structure:**
```
packages/mcp-server/
├── Dockerfile           # <-- This story creates this
├── pyproject.toml       # Already exists
├── src/
│   ├── server.py        # FastAPI + MCP entry point
│   └── ...
```

**From project-context.md - Critical Rules:**
- Use `uv run` pattern - Dockerfile must use uv for dependency management
- FastAPI endpoints MUST be async
- Use `pydantic_settings.BaseSettings` for config
- Use `structlog` for logging (no print statements)

### Technical Requirements

**Python & Dependencies:**
- Python 3.11 (pinned in pyproject.toml)
- uv package manager (NOT pip directly)
- Production dependencies from pyproject.toml (no dev deps in container)

**FastAPI/Uvicorn Configuration:**
- Use uvicorn ASGI server
- Bind to `0.0.0.0` for container networking
- Support dynamic PORT for Railway
- Enable `--proxy-headers` for Railway's reverse proxy

**Container Best Practices (from FastAPI docs):**
- Use exec form for CMD: `CMD ["uvicorn", ...]`
- Multi-stage builds to reduce image size
- Install requirements before copying code (cache optimization)
- Use `--no-cache-dir` with pip/uv to reduce layer size

### Multi-Stage Build Pattern

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
# Install uv, copy deps, sync

# Stage 2: Runtime
FROM python:3.11-slim as runtime
# Copy only virtualenv and app code
```

**Benefits:**
- No build tools in final image
- No uv in final image
- Smaller attack surface
- Faster pulls/deploys

### Environment Variable Pattern

```python
# src/config.py (already follows project-context.md pattern)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    qdrant_url: str = "http://localhost:6333"
    port: int = 8000
    environment: str = "local"

    class Config:
        env_file = ".env"
```

Container overrides via:
```bash
docker run -e MONGODB_URI=mongodb+srv://... -e QDRANT_URL=https://... image
```

### Railway-Specific Considerations

1. **Dynamic Port:** Railway sets `PORT` env var - container must respect it
2. **Proxy Headers:** Railway uses reverse proxy - enable `--proxy-headers`
3. **Health Checks:** Railway uses health checks for zero-downtime deploys
4. **Build Context:** Railway builds from Dockerfile in repo root or package dir
5. **Secrets:** Use Railway dashboard for sensitive env vars (never commit)

### Health Check Pattern

```python
@app.get("/health")
async def health_check():
    # Check MongoDB
    try:
        await mongodb_client.admin.command('ping')
        mongo_status = "healthy"
    except Exception as e:
        mongo_status = f"unhealthy: {e}"

    # Check Qdrant
    try:
        await qdrant_client.get_collections()
        qdrant_status = "healthy"
    except Exception as e:
        qdrant_status = f"unhealthy: {e}"

    overall = "healthy" if mongo_status == "healthy" and qdrant_status == "healthy" else "unhealthy"

    return {
        "status": overall,
        "checks": {
            "mongodb": mongo_status,
            "qdrant": qdrant_status
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

### File Locations

| File | Purpose | Status |
|------|---------|--------|
| `packages/mcp-server/Dockerfile` | Main container definition | **CREATE** |
| `packages/mcp-server/.dockerignore` | Build context optimization | **CREATE** |
| `packages/mcp-server/docker-compose.dev.yaml` | Local container testing | **CREATE** |
| `packages/mcp-server/src/server.py` | Add health endpoint | **MODIFY** |
| `packages/mcp-server/.env.example` | Document env vars | **UPDATE** |
| `packages/mcp-server/README.md` | Add Docker section | **UPDATE** |

### Previous Story Intelligence

**From Story 5.1 (Rate Limiting):**
- Middleware pattern established in `src/middleware/`
- slowapi library used for rate limiting
- Custom error handlers follow MCP format

**Note:** Stories 5.1 and 5.2 are still in backlog status. The Dockerfile can be created independently, but the health endpoint should be added to whatever server.py state exists.

### Git Intelligence

**Recent commits:**
- `c8b7933` - feat(story-1-2): docker compose infrastructure setup
- `4a59247` - feat(story-1-1): initialize monorepo structure

**Existing Docker setup:**
- `docker-compose.yaml` at root with MongoDB and Qdrant services
- MongoDB on port 27017, Qdrant on port 6333
- Volumes configured for data persistence
- Health checks already configured for both services

### Project Structure Notes

**Current `packages/mcp-server/` structure:**
```
packages/mcp-server/
├── pyproject.toml       # ✅ Exists - dependencies defined
├── .venv/               # ✅ Exists - local dev environment
├── src/
│   ├── __init__.py      # ✅ Exists
│   └── tools/
│       └── __init__.py  # ✅ Exists
└── (no Dockerfile yet)
```

**Expected after this story:**
```
packages/mcp-server/
├── Dockerfile           # NEW
├── .dockerignore        # NEW
├── docker-compose.dev.yaml  # NEW
├── pyproject.toml
├── .env.example         # UPDATED
├── README.md            # UPDATED
└── src/
    ├── __init__.py
    ├── server.py        # May need health endpoint
    └── ...
```

### Testing Commands

```bash
# Build image
cd packages/mcp-server
docker build -t knowledge-mcp .

# Run with local MongoDB/Qdrant
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017/knowledge_db \
  -e QDRANT_URL=http://host.docker.internal:6333 \
  knowledge-mcp

# Test health endpoint
curl http://localhost:8000/health

# View logs
docker logs mcp-server

# Cleanup
docker stop mcp-server && docker rm mcp-server
```

### References

- [Source: architecture.md#Hosting-Stack] - Railway deployment config
- [Source: architecture.md#Project-Structure] - Dockerfile location in structure
- [Source: project-context.md#Configuration] - Settings pattern with pydantic-settings
- [Source: project-context.md#Local-Development-Commands] - uv run pattern
- [Source: docker-compose.yaml] - MongoDB/Qdrant service configuration
- [Source: FastAPI Docker Docs] - Multi-stage build pattern, exec form CMD

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

