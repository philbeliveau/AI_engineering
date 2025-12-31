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

| Endpoint | Description |
|----------|-------------|
| `/health` | Health check - returns server status and service connectivity |
| `/mcp` | MCP protocol endpoint for Claude Code clients |
| `/docs` | Interactive API documentation (Swagger UI) |

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
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

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
