# Story 5.5: Railway Deployment Pipeline

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system operator**,
I want the MCP server deployed to Railway with auto-deploy,
So that the service is publicly accessible and updates automatically.

## Acceptance Criteria

1. **Given** the Railway project is configured
   **When** I push to the `main` branch
   **Then** Railway automatically builds and deploys the new version

2. **Given** the deployment is complete
   **When** a user connects to the MCP endpoint
   **Then** the MCP endpoint is accessible at the configured URL

3. **Given** the Railway dashboard is open
   **When** I navigate to project settings
   **Then** environment variables are managed via Railway dashboard

4. **Given** an issue occurs in production
   **When** I check Railway
   **Then** logs are accessible for debugging

5. **Given** the service is live
   **When** I measure search latency
   **Then** the deployment achieves NFR1 (<500ms search latency)

6. **Given** the infrastructure is running
   **When** I check the billing
   **Then** estimated cost is ~$5/month for starter tier

## Dependency Analysis

**Depends On:**
- **Story 1.1 (Initialize Monorepo Structure)** - DONE - Base project structure
- **Story 1.2 (Docker Compose Infrastructure)** - DONE - Local dev pattern
- **Story 5.1 (Rate Limiting Middleware)** - ready-for-dev - Production rate limiting
- **Story 5.2 (API Key Authentication)** - ready-for-dev - Production auth
- **Story 5.3 (Dockerfile and Container Configuration)** - ready-for-dev - Container for deployment
- **Story 5.4 (Cloud Database Configuration)** - ready-for-dev - MongoDB Atlas + Qdrant Cloud connection strings

**Blocks:**
- Epic 5 completion - Cannot complete epic without production deployment

**Integration Points:**
- Railway platform for hosting and auto-deployment
- MongoDB Atlas for document storage (connection string from Story 5.4)
- Qdrant Cloud for vector storage (URL and API key from Story 5.4)
- GitHub for source control and auto-deploy trigger

## Tasks / Subtasks

- [x] **Task 1: Create Railway Project** (AC: #1, #3)
  - [x] Sign up/login to Railway at railway.app
  - [x] Create new project named `knowledge-mcp`
  - [x] Connect GitHub repository to Railway project
  - [x] Select the `packages/mcp-server` directory as the root (important for monorepo)
  - [x] Verify Railway detects the Dockerfile from Story 5.3
  - [x] Enable auto-deploy on push to `main` branch

- [x] **Task 2: Configure railway.json for Deployment Settings** (AC: #1, #5)
  - [x] Create `packages/mcp-server/railway.json` for config-as-code
  - [x] Set build configuration to use Dockerfile
  - [x] Configure healthcheck path: `/health`
  - [x] Set healthcheck timeout: 120s (increased from 30s for cold start)
  - [x] Set startup timeout: 60s (allow embedding model load)
  - [x] Configure restart policy: `on-failure` with max 3 retries
  - [x] Add watch patterns for relevant source files

- [x] **Task 3: Configure Environment Variables in Railway** (AC: #3)
  - [x] Add `MONGODB_URI` from MongoDB Atlas (from Story 5.4)
  - [x] Add `QDRANT_URL` from Qdrant Cloud (from Story 5.4)
  - [x] Add `QDRANT_API_KEY` from Qdrant Cloud dashboard
  - [x] Set `ENVIRONMENT=production` for production validation
  - [x] Set `PORT` to Railway-provided dynamic port (Railway sets this automatically)
  - [x] Verify environment variables are marked as sensitive (hidden in logs)

- [x] **Task 4: Configure Custom Domain (Optional)** (AC: #2)
  - [x] Railway provides default `*.up.railway.app` domain
  - [x] Using default domain: `https://knowledge-mcp-production.up.railway.app`
  - [x] Document the public MCP endpoint URL in README
  - [x] Verify SSL/TLS is automatically configured by Railway

- [x] **Task 5: Trigger Initial Deployment** (AC: #1, #2)
  - [x] Push latest changes to `main` branch
  - [x] Monitor Railway build logs for any errors
  - [x] Verify container starts successfully
  - [x] Check health endpoint is responding: `GET https://knowledge-mcp-production.up.railway.app/health`
  - [x] Verify MCP endpoint is accessible: `https://knowledge-mcp-production.up.railway.app/mcp`

- [x] **Task 6: Verify Database Connections in Production** (AC: #5)
  - [x] Check Railway logs for successful MongoDB Atlas connection
  - [x] Check Railway logs for successful Qdrant Cloud connection
  - [x] Run health check that verifies both connections
  - [x] Test a simple query to verify data flow

- [x] **Task 7: Configure Logging and Monitoring** (AC: #4)
  - [x] Verify Railway captures stdout/stderr logs
  - [x] Check logs are accessible via Railway dashboard
  - [x] Verify structlog output is readable in Railway log viewer
  - [x] Document log access procedure in deployment docs

- [x] **Task 8: Performance Validation** (AC: #5)
  - [x] Run latency test against production endpoint
  - [x] Measure `search_knowledge` response time: **17ms** (target: <500ms) ✅
  - [x] Measure cold start time: ~915ms (first request after deploy)
  - [x] Document performance baseline for future comparison

- [x] **Task 9: Create Deployment Documentation** (AC: all)
  - [x] Update `packages/mcp-server/README.md` with Railway deployment section
  - [x] Document environment variables required
  - [x] Document Railway project setup steps
  - [x] Document troubleshooting common deployment issues
  - [x] Add deployment architecture diagram to docs

- [x] **Task 10: Create User Connection Documentation** (AC: #2)
  - [x] Document how users add MCP server to Claude Code config
  - [x] Create example `claude_desktop_config.json` snippet
  - [x] Document available MCP tools and their tiers
  - [x] Add to project README for community users

## Dev Notes

### Railway Platform Overview

Railway is a platform-as-a-service (PaaS) that simplifies deployment of containerized applications. Key features for this project:

- **Auto-deploy from GitHub:** Push to `main` triggers automatic build and deploy
- **Dockerfile detection:** Railway automatically uses Dockerfile if present
- **Environment variables:** Managed via dashboard, injected at runtime
- **Dynamic PORT:** Railway sets `PORT` env var; container must listen on it
- **Free tier:** $5/month hobby plan, sufficient for MVP

### Railway Configuration File (railway.json)

Per Railway's Config-as-Code documentation, create `railway.json` for declarative configuration:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile",
    "watchPatterns": [
      "src/**",
      "pyproject.toml",
      "Dockerfile"
    ]
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "startCommand": null,
    "startupTimeout": 60,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Monorepo Deployment Consideration

**CRITICAL:** This is a monorepo with `packages/pipeline/` and `packages/mcp-server/`. Railway needs to know which directory to deploy:

**Option 1: Railway Root Directory Setting**
- In Railway project settings, set "Root Directory" to `packages/mcp-server`
- Railway will use the Dockerfile from that directory

**Option 2: Root-level Dockerfile (Alternative)**
- Create `Dockerfile.railway` at repo root that references `packages/mcp-server`
- Configure Railway to use this Dockerfile

**Recommended:** Use Option 1 (Root Directory setting) for simplicity.

### Environment Variables Required

| Variable | Source | Purpose | Secret |
|----------|--------|---------|--------|
| `MONGODB_URI` | MongoDB Atlas connection string | Document database | Yes |
| `QDRANT_URL` | Qdrant Cloud URL | Vector database | No |
| `QDRANT_API_KEY` | Qdrant Cloud dashboard | Qdrant auth | Yes |
| `ENVIRONMENT` | Set to `production` | Config validation | No |
| `PORT` | Railway-provided | Dynamic port binding | No (auto) |

**Note:** Railway automatically sets `PORT`. The Dockerfile and server.py must respect this:

```dockerfile
# In Dockerfile (from Story 5.3)
ENV PORT=8000
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "${PORT}"]
```

Actually, for proper variable substitution, use a shell command:

```dockerfile
CMD sh -c "uvicorn src.server:app --host 0.0.0.0 --port ${PORT:-8000}"
```

Or configure in the FastAPI app:

```python
# src/server.py
import os
port = int(os.environ.get("PORT", 8000))
```

### Claude Code MCP Configuration

Users will add the deployed server to their Claude Code configuration. Example `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "knowledge-pipeline": {
      "type": "sse",
      "url": "https://knowledge-mcp.up.railway.app/mcp"
    }
  }
}
```

For authenticated (Registered/Premium) access:

```json
{
  "mcpServers": {
    "knowledge-pipeline": {
      "type": "sse",
      "url": "https://knowledge-mcp.up.railway.app/mcp",
      "headers": {
        "X-API-Key": "kp_your_api_key_here"
      }
    }
  }
}
```

### Cost Analysis

Per architecture.md and PRD, target cost is ~$5/month:

| Component | Tier | Monthly Cost |
|-----------|------|--------------|
| Railway MCP Server | Hobby | ~$5 |
| MongoDB Atlas | M0 Free | $0 |
| Qdrant Cloud | Free | $0 |
| **Total** | | **~$5/month** |

**Scaling path:**
- Railway: $5 → $20 (Pro) when traffic increases
- MongoDB Atlas: $0 → $9 (Shared) → $57 (M10 Dedicated)
- Qdrant Cloud: $0 → $25 (Starter)

### Health Check Endpoint

From Story 5.3, the health endpoint must be available:

```python
@app.get("/health")
async def health_check():
    """Health check for Railway deployment."""
    mongo_healthy = await check_mongodb_connection()
    qdrant_healthy = await check_qdrant_connection()

    overall = "healthy" if mongo_healthy and qdrant_healthy else "unhealthy"

    return {
        "status": overall,
        "checks": {
            "mongodb": "healthy" if mongo_healthy else "unhealthy",
            "qdrant": "healthy" if qdrant_healthy else "unhealthy"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

Railway uses this endpoint for:
- Zero-downtime deployments (waits for health before routing traffic)
- Container restart decisions
- Dashboard health indicators

### Troubleshooting Common Issues

**Issue: Build fails with "Dockerfile not found"**
- Ensure Root Directory is set to `packages/mcp-server` in Railway settings
- Verify Dockerfile exists at `packages/mcp-server/Dockerfile`

**Issue: Container starts but health check fails**
- Check startup timeout is sufficient (60s recommended for embedding model)
- Verify health endpoint path is correct (`/health`)
- Check MongoDB/Qdrant connection strings are valid

**Issue: Environment variables not visible**
- Railway injects env vars at runtime, not build time
- Use `os.environ.get()` in Python, not build-time substitution
- Check variables are set in Railway dashboard (not just railway.json)

**Issue: Port binding error**
- Ensure server binds to `0.0.0.0`, not `127.0.0.1`
- Ensure server reads `PORT` from environment variable
- Railway assigns dynamic ports; don't hardcode

**Issue: Cold start timeout**
- Embedding model download takes time on first request
- Increase `startupTimeout` in railway.json to 120s if needed
- Consider pre-loading model in Dockerfile or startup

### SSL/TLS

Railway automatically provides:
- Free SSL certificate for all `*.up.railway.app` domains
- Automatic certificate renewal
- HTTPS enforcement (HTTP redirects to HTTPS)

No additional SSL configuration needed.

### Rollback Procedure

If deployment fails or causes issues:

1. Railway dashboard → Deployments tab
2. Find previous successful deployment
3. Click "Redeploy" on that version
4. Previous version is restored immediately

Or use Railway CLI:
```bash
railway redeploy <deployment-id>
```

### Logging Best Practices

Per project-context.md, use structlog with context:

```python
import structlog
logger = structlog.get_logger()

# Good - appears cleanly in Railway logs
logger.info("server_started", port=port, environment=settings.environment)
logger.info("search_completed", query=query[:50], result_count=len(results), latency_ms=latency)
logger.error("database_connection_failed", database="mongodb", error=str(e))

# Bad - hard to parse in Railway
print(f"Server started on port {port}")
```

Railway log viewer supports:
- Text search across all logs
- Time-range filtering
- Log level filtering (if using standard levels)

### Project Structure Notes

**Files to Create/Modify:**

| File | Action | Purpose |
|------|--------|---------|
| `packages/mcp-server/railway.json` | CREATE | Railway config-as-code |
| `packages/mcp-server/README.md` | UPDATE | Deployment documentation |
| `docs/deployment.md` | CREATE | Comprehensive deployment guide |
| `.github/workflows/` | OPTIONAL | CI checks before Railway deploy |

**Alignment with Architecture:**
- Uses Railway as specified in architecture.md:363-369
- Respects monorepo structure from architecture.md:593-726
- Uses environment variables per project-context.md:207
- Follows logging patterns per project-context.md:153-164

### Previous Story Intelligence

**From Story 5.3 (Dockerfile):**
- Multi-stage build pattern for optimized images
- `python:3.11-slim` base image
- Health check configured in Dockerfile
- PORT environment variable support
- uv for dependency management

**From Story 5.4 (Cloud Database Configuration):**
- MongoDB Atlas connection string format: `mongodb+srv://...`
- Qdrant Cloud URL format: `https://<cluster>.cloud.qdrant.io:6333`
- Connection validation at startup
- Environment-based configuration switching

**From Story 5.1 (Rate Limiting):**
- slowapi middleware configured
- Public: 100 req/hr, Registered: 1000 req/hr, Premium: unlimited
- 429 responses with MCP-compatible format

**From Story 5.2 (API Key Authentication):**
- X-API-Key header for auth
- Tier detection (PUBLIC/REGISTERED/PREMIUM)
- 401/403 error responses in MCP format

### Git Intelligence

**Recent commits:**
```
c8b7933 feat(story-1-2): docker compose infrastructure setup
4a59247 feat(story-1-1): initialize monorepo structure
44323de Definition of architecture
bc247ce first commit
```

**Current project state:**
- Monorepo structure established
- Docker Compose for local dev working
- Stories 1.1, 1.2 complete
- Stories 5.1-5.4 ready-for-dev (must be implemented before this story is fully functional)

### Security Considerations

**CRITICAL:**
1. **NEVER commit secrets** - Use Railway dashboard for all credentials
2. **Mark variables as sensitive** - Railway hides sensitive vars in logs
3. **Validate production config** - Fail fast if cloud URLs missing
4. **Use HTTPS only** - Railway enforces this automatically

**Environment Variable Security:**
- MongoDB URI contains password → MUST be secret
- Qdrant API key → MUST be secret
- Other config values can be non-secret

### Testing the Deployment

**Pre-deployment checklist:**
- [ ] All Story 5.1-5.4 changes committed
- [ ] Dockerfile builds locally: `docker build -t test .`
- [ ] Container runs locally with cloud env vars
- [ ] Health endpoint returns 200

**Post-deployment verification:**
- [ ] Health check: `curl https://<app>.up.railway.app/health`
- [ ] MCP tools discoverable via Claude Code
- [ ] Public tier rate limiting works
- [ ] Authenticated tier works with valid API key
- [ ] Latency <500ms for search operations

### References

- [Source: _bmad-output/architecture.md#Infrastructure & Deployment (lines 363-376)] - Railway hosting stack
- [Source: _bmad-output/architecture.md#Project Structure (lines 593-726)] - Monorepo structure
- [Source: _bmad-output/project-context.md#Configuration (lines 59-63)] - Settings pattern
- [Source: _bmad-output/project-context.md#Development Workflow Rules (lines 182-211)] - uv patterns
- [Source: _bmad-output/epics.md#Story 5.5 (lines 698-714)] - Original story definition
- [Source: _bmad-output/prd.md#NFR-1 Performance (lines 292-299)] - <500ms latency requirement
- [Source: _bmad-output/prd.md#Cloud Dependencies (lines 394-400)] - Cost estimates
- [Source: 5-3-dockerfile-and-container-configuration.md] - Dockerfile patterns
- [Source: 5-4-cloud-database-configuration.md] - Cloud database connection
- [Source: Railway Docs - FastAPI Deployment](https://docs.railway.com/guides/fastapi) - Official Railway FastAPI guide
- [Source: Railway Config-as-Code](https://blog.railway.com/p/comparing-deployment-methods-in-railway) - railway.json configuration

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Initial deployment failed: healthcheck timeout (30s too short for cold start)
- Fixed by increasing healthcheckTimeout to 120s in railway.json
- Root directory issue resolved: must be set to `packages/mcp-server` in Railway settings

### Completion Notes List

- ✅ Railway project `knowledge-mcp` created and configured
- ✅ Created `railway.json` with Dockerfile build config, health checks, restart policy
- ✅ Environment variables configured: MONGODB_URI, QDRANT_URL, QDRANT_API_KEY, ENVIRONMENT, MONGODB_DATABASE
- ✅ Deployment successful at: `https://knowledge-mcp-production.up.railway.app`
- ✅ Health check passing: MongoDB healthy, Qdrant healthy
- ✅ Performance validated: warm latency **17ms** (target: <500ms)
- ✅ Cold start latency: ~915ms (acceptable for serverless-like deployment)
- ✅ README updated with comprehensive Railway deployment and MCP client connection docs

### File List

- `packages/mcp-server/railway.json` - NEW - Railway config-as-code
- `packages/mcp-server/README.md` - MODIFIED - Added Railway deployment section, MCP client connection docs
- `_bmad-output/implementation-artifacts/sprint-status.yaml` - MODIFIED - Story status updated

### Change Log

- 2026-01-04: Story implementation complete - Railway deployment pipeline operational

