# Story 5.4: Cloud Database Configuration

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system operator**,
I want configuration for MongoDB Atlas and Qdrant Cloud,
So that production data is stored in managed cloud services.

## Acceptance Criteria

**Given** cloud database accounts are set up
**When** I configure the application with cloud connection strings
**Then** the application connects to MongoDB Atlas instead of local MongoDB
**And** the application connects to Qdrant Cloud instead of local Qdrant
**And** connection strings are configured via environment variables
**And** SSL/TLS is enabled for all database connections
**And** the application gracefully handles connection failures

## Dependency Analysis

**Depends On:**
- **Story 1.2 (Docker Compose Infrastructure)** - DONE - Local MongoDB/Qdrant for dev parity testing
- **Story 1.4 (MongoDB Storage Client)** - ready-for-dev - MongoDB client patterns
- **Story 1.5 (Qdrant Storage Client)** - ready-for-dev - Qdrant client patterns
- **Story 5.1 (Rate Limiting Middleware)** - backlog - Production middleware
- **Story 5.2 (API Key Authentication)** - backlog - Production auth
- **Story 5.3 (Dockerfile)** - backlog - Container configuration

**Blocks:**
- **Story 5.5 (Railway Deployment)** - Cannot deploy without cloud database configuration

**Implementation Note:** This story focuses on the **configuration layer** - the actual storage clients (1.4, 1.5) may be implemented separately. This story adds cloud-specific connection handling and environment-based configuration switching.

## Tasks / Subtasks

- [ ] **Task 1: Update Settings Models for Cloud Configuration** (AC: Environment variables configured)
  - [ ] Update `packages/mcp-server/src/config.py` with cloud settings
  - [ ] Add `MONGODB_URI` setting with default local fallback
  - [ ] Add `QDRANT_URL` setting with default local fallback
  - [ ] Add `QDRANT_API_KEY` setting (optional, for Qdrant Cloud)
  - [ ] Add `ENVIRONMENT` setting: `local` | `staging` | `production`
  - [ ] Add `SSL_ENABLED` setting (default True for production)
  - [ ] Add `CONNECTION_TIMEOUT_MS` setting (default 5000)
  - [ ] Add `MAX_POOL_SIZE` setting for MongoDB (default 10)
  - [ ] Use `pydantic_settings.BaseSettings` as per project-context.md
  - [ ] Load from `.env` file with `env_file = ".env"`
  - [ ] Export singleton: `settings = Settings()`

- [ ] **Task 2: Create Environment-Specific Configuration Files** (AC: .env files created)
  - [ ] Create `packages/mcp-server/.env.example` with all settings documented
  - [ ] Create `packages/mcp-server/.env.local.example` for local development
  - [ ] Create `packages/mcp-server/.env.production.example` for production
  - [ ] Document MongoDB Atlas connection string format in comments
  - [ ] Document Qdrant Cloud connection string format in comments
  - [ ] Ensure `.env` is in `.gitignore` (NEVER commit secrets)
  - [ ] Add validation that production environment requires cloud URLs

- [ ] **Task 3: Implement MongoDB Atlas Connection Handler** (AC: SSL/TLS enabled for Atlas)
  - [ ] Create `packages/mcp-server/src/storage/connection.py` module
  - [ ] Implement `create_mongodb_client()` factory function
  - [ ] Parse connection string to detect Atlas (contains `mongodb+srv://`)
  - [ ] Configure SSL/TLS options for Atlas connections
  - [ ] Set appropriate `serverSelectionTimeoutMS` (5 seconds)
  - [ ] Set appropriate `connectTimeoutMS` (10 seconds)
  - [ ] Set `retryWrites=true` for Atlas connections
  - [ ] Set `w=majority` write concern for durability
  - [ ] Use `maxPoolSize` from settings
  - [ ] Add structured logging for connection events

- [ ] **Task 4: Implement Qdrant Cloud Connection Handler** (AC: API key authentication for Qdrant)
  - [ ] Implement `create_qdrant_client()` factory function in `connection.py`
  - [ ] Parse URL to detect Qdrant Cloud (contains `.cloud.qdrant.io`)
  - [ ] Configure API key authentication when `QDRANT_API_KEY` is set
  - [ ] Set HTTPS/TLS for cloud connections
  - [ ] Configure timeout settings (5 second connect, 30 second operation)
  - [ ] Add structured logging for connection events
  - [ ] Return `QdrantClient` instance configured appropriately

- [ ] **Task 5: Implement Connection Health Check** (AC: Graceful failure handling)
  - [ ] Create `check_database_health()` async function
  - [ ] Test MongoDB connection with simple ping command
  - [ ] Test Qdrant connection with collection list
  - [ ] Return health status: `{mongodb: bool, qdrant: bool, details: {...}}`
  - [ ] Log connection failures with error details
  - [ ] Don't crash application on connection failure
  - [ ] Add `/health` endpoint that calls this function

- [ ] **Task 6: Implement Connection Retry Logic** (AC: Automatic reconnection)
  - [ ] Implement exponential backoff for connection retries
  - [ ] Maximum 5 retry attempts before giving up
  - [ ] Wait times: 1s, 2s, 4s, 8s, 16s
  - [ ] Log each retry attempt with attempt number
  - [ ] Raise `ConnectionError` with details after max retries
  - [ ] Use `tenacity` library for retry logic (or implement manually)

- [ ] **Task 7: Add Environment Validation** (AC: Startup validation)
  - [ ] Validate MongoDB URI format on startup
  - [ ] Validate Qdrant URL format on startup
  - [ ] Check that production environment has cloud URLs (not localhost)
  - [ ] Warn (not error) if using local databases in development
  - [ ] Log environment and connection targets on startup
  - [ ] Fail fast with clear error if production config is invalid

- [ ] **Task 8: Update Server Startup for Cloud Config** (AC: Server uses factory functions)
  - [ ] Update `packages/mcp-server/src/server.py` lifespan handler
  - [ ] Use factory functions to create database clients
  - [ ] Store clients in application state for route access
  - [ ] Gracefully shut down connections on server stop
  - [ ] Log successful database connections on startup
  - [ ] Include environment name in startup log

- [ ] **Task 9: Write Unit Tests** (AC: Configuration tests pass)
  - [ ] Test Settings model with environment variables
  - [ ] Test cloud URL detection (Atlas vs local)
  - [ ] Test cloud URL detection (Qdrant Cloud vs local)
  - [ ] Test SSL configuration is applied for cloud
  - [ ] Test environment validation (production requires cloud)
  - [ ] Test connection retry logic
  - [ ] Test health check response format
  - [ ] Mock external connections (don't hit real databases)

- [ ] **Task 10: Write Integration Tests** (AC: Real cloud connections work)
  - [ ] Create test MongoDB Atlas cluster (free tier)
  - [ ] Create test Qdrant Cloud cluster (free tier)
  - [ ] Test successful connection to Atlas with SSL
  - [ ] Test successful connection to Qdrant Cloud with API key
  - [ ] Test read/write operations on cloud databases
  - [ ] Test graceful handling of invalid credentials
  - [ ] Test graceful handling of network timeout
  - [ ] Test connection pooling behavior
  - [ ] Mark as `@pytest.mark.integration` (skip in CI by default)

## Dev Notes

### MongoDB Atlas Connection String Format

MongoDB Atlas uses the `mongodb+srv://` protocol which handles DNS-based service discovery:

```bash
# Atlas connection string format
MONGODB_URI="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority"

# Example with actual cluster
MONGODB_URI="mongodb+srv://knowledge_user:secretpassword@knowledge-cluster.abc123.mongodb.net/knowledge_db?retryWrites=true&w=majority"
```

**Atlas-Specific Settings:**
- `retryWrites=true` - Required for Atlas
- `w=majority` - Write concern for durability
- SSL/TLS is automatic with `mongodb+srv://`

### Qdrant Cloud Connection Format

Qdrant Cloud uses HTTPS with API key authentication:

```bash
# Qdrant Cloud URL format
QDRANT_URL="https://<cluster-id>.cloud.qdrant.io:6333"
QDRANT_API_KEY="your-qdrant-cloud-api-key"

# Example
QDRANT_URL="https://abc123.us-east1-0.cloud.qdrant.io:6333"
QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Environment Detection Pattern

```python
def is_cloud_mongodb(uri: str) -> bool:
    """Detect if MongoDB URI points to Atlas."""
    return "mongodb+srv://" in uri or "mongodb.net" in uri

def is_cloud_qdrant(url: str) -> bool:
    """Detect if Qdrant URL points to Qdrant Cloud."""
    return "cloud.qdrant.io" in url
```

### Connection Factory Pattern

Follow the existing architecture pattern for creating database connections:

```python
# packages/mcp-server/src/storage/connection.py
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from qdrant_client import QdrantClient
from src.config import settings
import structlog

logger = structlog.get_logger()

def create_mongodb_client() -> MongoClient:
    """Create MongoDB client configured for environment."""
    if is_cloud_mongodb(settings.mongodb_uri):
        # Atlas-specific configuration
        return MongoClient(
            settings.mongodb_uri,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=settings.connection_timeout_ms,
            maxPoolSize=settings.max_pool_size,
        )
    else:
        # Local configuration
        return MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=settings.connection_timeout_ms,
        )

def create_qdrant_client() -> QdrantClient:
    """Create Qdrant client configured for environment."""
    if is_cloud_qdrant(settings.qdrant_url):
        # Qdrant Cloud configuration
        return QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )
    else:
        # Local configuration
        return QdrantClient(
            url=settings.qdrant_url,
            timeout=30,
        )
```

### Project Structure Notes

**Files to Create/Modify:**
- `packages/mcp-server/src/config.py` - Update Settings model
- `packages/mcp-server/src/storage/connection.py` - NEW: Connection factories
- `packages/mcp-server/src/storage/__init__.py` - Export connection functions
- `packages/mcp-server/src/server.py` - Update to use factories
- `packages/mcp-server/.env.example` - NEW: Environment template
- `packages/mcp-server/tests/test_storage/test_connection.py` - NEW: Tests

**Alignment with Architecture:**
- Uses `pydantic_settings.BaseSettings` per architecture.md:519-533
- Uses `structlog` for logging per project-context.md:153-164
- Connection strings via environment variables per architecture.md:375-382
- Error handling follows project-context.md:66-69

### SSL/TLS Requirements

**MongoDB Atlas:**
- SSL is automatic when using `mongodb+srv://` protocol
- No additional configuration needed
- Certificate verification is enabled by default

**Qdrant Cloud:**
- HTTPS is automatic when URL contains `https://`
- API key is passed in request headers
- TLS 1.2+ required

### Cost Considerations

Per architecture.md:235-236 and 365-369:

| Service | Free Tier | Starter Tier |
|---------|-----------|--------------|
| MongoDB Atlas | M0 (512MB) | M10 ($57/mo) |
| Qdrant Cloud | Free (1GB) | Starter ($25/mo) |

**Recommendation:** Start with free tiers for initial deployment, upgrade based on usage.

### References

- [Source: _bmad-output/architecture.md#Infrastructure-Deployment] - Cloud deployment stack
- [Source: _bmad-output/architecture.md#Core-Architectural-Decisions] - Database configuration
- [Source: _bmad-output/project-context.md#Configuration] - Settings patterns
- [Source: _bmad-output/project-context.md#Error-Handling] - Error format requirements
- [Source: _bmad-output/epics.md#Story-5.4] - Original story requirements
- [Source: packages/mcp-server/pyproject.toml] - Current dependencies

### Security Considerations

**CRITICAL:**
- NEVER commit `.env` files with credentials
- NEVER log connection strings (contains passwords)
- ALWAYS use environment variables for secrets
- API keys should be rotated periodically

**Logging Safe Connection Info:**
```python
# Good - log sanitized info
logger.info("connecting_mongodb", cluster="knowledge-cluster.mongodb.net", database="knowledge_db")

# Bad - exposes credentials
logger.info("connecting", uri=settings.mongodb_uri)  # NEVER DO THIS
```

### Railway Deployment Notes

For Story 5.5 compatibility, environment variables will be set via Railway dashboard:
- `MONGODB_URI` - From MongoDB Atlas connection string
- `QDRANT_URL` - From Qdrant Cloud dashboard
- `QDRANT_API_KEY` - From Qdrant Cloud API keys
- `ENVIRONMENT=production` - Must be set for production validation

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

