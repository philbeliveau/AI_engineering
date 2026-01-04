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

### Using Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "knowledge": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp"
      ]
    }
  }
}
```

### Using Claude Code

The server exposes MCP tools that can be queried directly via the `/mcp` endpoint.

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

### Railway Deployment

The Dockerfile is optimized for Railway deployment:

1. **Dynamic Port:** Railway sets `PORT` env var - container respects it
2. **Proxy Headers:** `--proxy-headers` flag trusts Railway's reverse proxy
3. **Health Checks:** Railway uses `/health` for zero-downtime deploys
4. **Multi-Stage Build:** Optimized image size (~660MB with ML dependencies)

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
