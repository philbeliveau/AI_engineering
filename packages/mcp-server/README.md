# Knowledge MCP Server

MCP server providing access to AI engineering knowledge extracted from methodology books.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for MongoDB and Qdrant)

## Quick Start

### 1. Start Infrastructure

```bash
# From project root
docker-compose up -d
```

This starts:
- MongoDB on port 27017
- Qdrant on port 6333

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` as needed. Default values work for local development.

### 3. Install Dependencies

```bash
cd packages/mcp-server
uv sync --all-extras
```

### 4. Run the Server

```bash
uv run uvicorn src.server:app --reload
```

The server starts at http://localhost:8000

## API Endpoints

### Infrastructure

| Endpoint | Description |
|----------|-------------|
| `/health` | Health check - returns server status and service connectivity |
| `/mcp` | MCP protocol endpoint for Claude Code clients |
| `/docs` | Interactive API documentation (Swagger UI) |

### MCP Tools (Knowledge Query)

| Endpoint | Auth | Description |
|----------|------|-------------|
| `/search_knowledge` | Public | Semantic search across all knowledge content |
| `/get_decisions` | Public | List decision extractions with optional topic filter |
| `/get_patterns` | Public | List pattern extractions with optional topic filter |
| `/get_warnings` | Public | List warning extractions with optional topic filter |
| `/get_methodologies` | **Registered** | List methodology extractions (requires API key) |
| `/list_sources` | Public | List all knowledge sources with extraction counts |
| `/compare_sources` | **Registered** | Compare extractions across sources by topic |

**Note:** Registered tier endpoints require an API key in the `X-API-Key` header.

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T12:00:00Z",
  "version": "0.1.0",
  "services": {
    "mongodb": "healthy",
    "qdrant": "healthy"
  }
}
```

## MCP Client Connection

### Connecting to Deployed Server (Production)

Add the Knowledge Pipeline MCP server to your Claude Desktop or Claude Code configuration.

**Location of config file:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

#### Public Access (No API Key)

Access public tier tools (search, decisions, patterns, warnings, list_sources):

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

#### Registered Access (With API Key)

Access all tools including registered tier (methodologies, compare_sources):

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

### Available MCP Tools

| Tool | Tier | Description |
|------|------|-------------|
| `search_knowledge` | Public | Semantic search across all knowledge content |
| `get_decisions` | Public | List architectural decisions with topic filters |
| `get_patterns` | Public | List design patterns with topic filters |
| `get_warnings` | Public | List anti-patterns and pitfalls with topic filters |
| `list_sources` | Public | List all knowledge sources with extraction counts |
| `get_methodologies` | **Registered** | List process methodologies (requires API key) |
| `compare_sources` | **Registered** | Compare extractions across sources (requires API key) |

### Access Tiers

| Tier | Rate Limit | API Key Required | Tools Available |
|------|------------|------------------|-----------------|
| Public | 100 req/hr | No | search, decisions, patterns, warnings, list_sources |
| Registered | 1000 req/hr | Yes | All public + methodologies, compare_sources |
| Premium | Unlimited | Yes | All tools, priority support |

### Connecting to Local Server (Development)

For local development with the server running at `localhost:8000`:

```json
{
  "mcpServers": {
    "knowledge-local": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp"
      ]
    }
  }
}
```

### Verifying Connection

After adding the MCP server to your config:

1. Restart Claude Desktop/Claude Code
2. The server should appear in the MCP servers list
3. Try asking Claude: "What knowledge sources are available?"
4. Claude should use the `list_sources` tool to answer

## Development

### Run Tests

```bash
uv run python -m pytest
```

With verbose output:

```bash
uv run python -m pytest -v
```

### Run Linting

```bash
uv run ruff check .
```

Auto-fix issues:

```bash
uv run ruff check --fix .
```

## Configuration

All configuration is via environment variables. See `.env.example` for available options:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `local` | Environment name (local, development, production) |
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DATABASE` | `knowledge_db` | MongoDB database name |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `QDRANT_API_KEY` | (none) | Qdrant Cloud API key |
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `API_KEYS_FILE` | (none) | Path to JSON file containing API keys |
| `PROJECT_ID` | `default` | Project ID for multi-tenant isolation |

### API Key Configuration

For Registered tier access (e.g., `/get_methodologies`), configure API keys via JSON file:

```json
{
  "keys": [
    {
      "key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
      "tier": "REGISTERED",
      "metadata": {"user": "test-user"}
    }
  ]
}
```

Set the path in `.env`:
```
API_KEYS_FILE=/path/to/api-keys.json
```

Then use the key in requests:
```bash
curl -H "X-API-Key: kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6" http://localhost:8000/get_methodologies
```

## Troubleshooting

### MongoDB Connection Failed

1. Verify MongoDB is running: `docker-compose ps`
2. Check the URI: `mongosh mongodb://localhost:27017`
3. Check firewall settings

### Qdrant Connection Failed

1. Verify Qdrant is running: `docker-compose ps`
2. Check the health endpoint: `curl http://localhost:6333/healthz`
3. Ensure port 6333 is not blocked

### Port 8000 Already in Use

Find and kill the process:

```bash
lsof -ti:8000 | xargs kill -9
```

Or use a different port:

```bash
SERVER_PORT=8001 uv run uvicorn src.server:app --port 8001
```

## Error Handling

All API errors follow a standardized format (Story 4.6):

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {"query.limit": "Input should be greater than or equal to 1"},
    "retry_after": null
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Insufficient access tier |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded (includes `retry_after` in seconds) |
| `INTERNAL_ERROR` | 500 | Server error (includes `correlation_id` for debugging) |

### Response Metadata

All successful responses include latency tracking for NFR1 compliance (<500ms target):

```json
{
  "results": [...],
  "metadata": {
    "query": "test query",
    "sources_cited": ["Book 1"],
    "result_count": 5,
    "search_type": "semantic",
    "latency_ms": 42
  }
}
```

## Docker

### Build the Image

```bash
cd packages/mcp-server
docker build -t knowledge-mcp .
```

### Run the Container

**With local MongoDB/Qdrant (started via docker-compose):**

```bash
# Start infrastructure first
docker-compose up -d

# Run the MCP server container
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017/knowledge_db \
  -e QDRANT_URL=http://host.docker.internal:6333 \
  -e ENVIRONMENT=local \
  --add-host=host.docker.internal:host-gateway \
  knowledge-mcp
```

**With cloud databases (production):**

```bash
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -e MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/knowledge_db \
  -e QDRANT_URL=https://xxx.cloud.qdrant.io:6333 \
  -e QDRANT_API_KEY=your-qdrant-api-key \
  -e ENVIRONMENT=production \
  knowledge-mcp
```

### Using docker-compose for Local Development

A convenience docker-compose file is included for local container testing:

```bash
# From packages/mcp-server directory
docker-compose -f ../../docker-compose.yaml -f docker-compose.dev.yaml up -d --build
```

This builds the container and runs it alongside the infrastructure services.

### Container Health Check

The container includes a built-in health check:

```bash
# Check container health status
docker inspect mcp-server --format "{{.State.Health.Status}}"

# Manual health check
curl http://localhost:8000/health
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGODB_URI` | Yes | - | MongoDB connection string |
| `QDRANT_URL` | Yes | - | Qdrant server URL |
| `QDRANT_API_KEY` | No | - | Qdrant Cloud API key |
| `PORT` | No | `8000` | Server port (Railway sets dynamically) |
| `ENVIRONMENT` | No | `production` | Deployment environment |
| `PROJECT_ID` | No | `default` | Multi-tenant project ID |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `API_KEYS_FILE` | No | - | Path to API keys JSON file |

## Railway Deployment

The MCP server is designed for deployment to [Railway](https://railway.app), a platform-as-a-service that simplifies containerized app deployment.

### Prerequisites

Before deploying to Railway, ensure:

1. **Cloud Databases Configured** (Story 5.4):
   - MongoDB Atlas cluster created with connection string
   - Qdrant Cloud cluster created with URL and API key

2. **Dockerfile Ready** (Story 5.3):
   - `packages/mcp-server/Dockerfile` exists and builds successfully

### Quick Start

1. **Create Railway Project:**
   - Sign up at [railway.app](https://railway.app)
   - Create new project → "Deploy from GitHub repo"
   - Connect your repository
   - Set **Root Directory** to `/packages/mcp-server` (critical for monorepo)

2. **Configure Environment Variables:**

   | Variable | Required | Description |
   |----------|----------|-------------|
   | `MONGODB_URI` | Yes | MongoDB Atlas connection string |
   | `MONGODB_DATABASE` | Yes | Database name (e.g., `knowledge_db`) |
   | `QDRANT_URL` | Yes | Qdrant Cloud URL |
   | `QDRANT_API_KEY` | Yes | Qdrant Cloud API key |
   | `ENVIRONMENT` | No | Set to `production` |
   | `PORT` | No | Railway sets automatically |
   | `PROJECT_ID` | No | Multi-tenant project ID |
   | `LOG_LEVEL` | No | `INFO` (default) |

3. **Deploy:**
   - Railway auto-deploys on push to `main` branch
   - Or trigger manual deploy from Railway dashboard

### Configuration as Code

The `railway.json` file provides declarative configuration:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile",
    "watchPatterns": ["src/**", "pyproject.toml", "Dockerfile"]
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Verifying Deployment

After deployment, verify the service is healthy:

```bash
# Health check
curl https://<your-app>.up.railway.app/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2026-01-04T12:00:00Z",
  "version": "0.1.0",
  "services": {
    "mongodb": "healthy",
    "qdrant": "healthy"
  }
}
```

### Troubleshooting

**Build fails with "Dockerfile not found"**
- Ensure Root Directory is set to `/packages/mcp-server` in Railway settings

**Health check fails**
- Check Railway logs for MongoDB/Qdrant connection errors
- Verify environment variables are set correctly
- Ensure cloud database services allow Railway IP ranges

**Port binding error**
- Don't hardcode port - Railway sets `PORT` dynamically
- The Dockerfile uses `${PORT}` environment variable

**Cold start timeout**
- First request after deploy may be slow (embedding model initialization)
- Subsequent requests should be <500ms

### Monitoring

- **Logs:** Railway dashboard → Deployments → View Logs
- **Metrics:** Railway provides basic CPU/memory metrics
- **Health:** `/health` endpoint for uptime monitoring

### Cost Estimate

| Component | Tier | Monthly Cost |
|-----------|------|--------------|
| Railway MCP Server | Hobby | ~$5 |
| MongoDB Atlas | M0 Free | $0 |
| Qdrant Cloud | Free | $0 |
| **Total** | | **~$5/month** |

### Rollback

If deployment fails:
1. Railway dashboard → Deployments tab
2. Find previous successful deployment
3. Click "Redeploy" to restore

## Architecture

This package is the READ-ONLY query layer of the Knowledge Pipeline:

```
packages/pipeline (WRITE)     packages/mcp-server (READ)
         │                            │
         ▼                            ▼
    ┌─────────┐                 ┌─────────┐
    │ MongoDB │ ◄───────────────│   MCP   │
    │ Qdrant  │                 │ Server  │
    └─────────┘                 └─────────┘
```

The server NEVER writes to databases - all write operations are handled by the pipeline package.
