# Story 5.1: Rate Limiting Middleware

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system operator**,
I want rate limiting middleware that enforces request limits by tier,
So that the system is protected from abuse and resources are fairly allocated.

## Acceptance Criteria

**Given** the middleware is configured
**When** requests arrive at the MCP server
**Then** Public tier is limited to 100 requests/hour per IP
**And** Registered tier is limited to 1000 requests/hour per API key
**And** Premium tier has unlimited requests
**And** rate limit errors return 429 status with `retry_after` header
**And** limits are tracked in-memory (Redis optional for future)

## Dependency Analysis

**Depends On:**
- **Epic 4 Stories (MCP Tools)** - Rate limiting applies to MCP tool endpoints
  - Story 4.1 (FastAPI Server with MCP Integration) - Need FastAPI app to add middleware to
  - Story 4.2-4.4 (MCP Tools) - Endpoints that will be rate limited

**Note:** While Epic 4 stories are not marked as "done", this story can be implemented and tested independently. The middleware will be ready when Epic 4 tools are implemented.

**Blocks:**
- Story 5.2 (API Key Authentication) - Authentication middleware will use same tier detection logic
- Story 5.5 (Railway Deployment) - Production deployment requires working rate limiting

**Optional Future Enhancement:**
- Redis backend for distributed rate limiting (when scaling to multiple instances)

## Tasks / Subtasks

- [ ] **Task 1: Install and Configure slowapi** (AC: Library installed)
  - [ ] Add slowapi to mcp-server dependencies: `uv add slowapi`
  - [ ] Verify slowapi is compatible with FastAPI >=0.115
  - [ ] Review slowapi documentation for token bucket algorithm
  - [ ] Understand slowapi error handling and custom handlers

- [ ] **Task 2: Create Rate Limiting Middleware Module** (AC: middleware/rate_limit.py exists)
  - [ ] Create `packages/mcp-server/src/middleware/` directory
  - [ ] Create `packages/mcp-server/src/middleware/__init__.py`
  - [ ] Create `packages/mcp-server/src/middleware/rate_limit.py`
  - [ ] Follow architecture naming conventions (snake_case for files)

- [ ] **Task 3: Implement Tier Detection Logic** (AC: Public/Registered/Premium detection)
  - [ ] Implement `get_rate_limit_key()` function
  - [ ] Extract API key from `X-API-Key` header
  - [ ] Extract real IP from `X-Forwarded-For` header (proxy-aware)
  - [ ] Fall back to `request.client.host` if headers missing
  - [ ] Return key format: `apikey:{key}` or `ip:{address}`
  - [ ] Add structured logging for tier detection

- [ ] **Task 4: Implement Dynamic Rate Limits** (AC: 100/1000/unlimited per tier)
  - [ ] Implement `get_tier_rate_limit()` async function
  - [ ] Return "100/hour" for public tier (no API key)
  - [ ] Return "1000/hour" for registered tier (has API key)
  - [ ] Return "999999/hour" for premium tier (effectively unlimited)
  - [ ] Add TODO comment for MongoDB tier lookup (future Story 5.2)
  - [ ] Add structured logging for rate limit assignment

- [ ] **Task 5: Configure Limiter with Token Bucket Algorithm** (AC: In-memory limiter configured)
  - [ ] Initialize slowapi `Limiter` with `key_func=get_rate_limit_key`
  - [ ] Set `default_limits=[]` (no global limit, per-route only)
  - [ ] Use in-memory storage backend (default)
  - [ ] Export limiter singleton for use in routes
  - [ ] Add docstring explaining token bucket behavior

- [ ] **Task 6: Implement Custom Error Handler** (AC: MCP-compatible 429 responses)
  - [ ] Create `rate_limit_error_handler()` function
  - [ ] Return 429 status code
  - [ ] Add `Retry-After` header with seconds until reset
  - [ ] Add `X-RateLimit-Limit` header
  - [ ] Add `X-RateLimit-Remaining: 0` header
  - [ ] Return error in MCP format: `{error: {code, message, details}}`
  - [ ] Follow project-context.md error response format EXACTLY

- [ ] **Task 7: Add Rate Limiting to Example Endpoints** (AC: Decorator applied to routes)
  - [ ] Create example health endpoint with rate limiting
  - [ ] Apply `@limiter.limit(get_tier_rate_limit)` decorator
  - [ ] Ensure decorator is applied AFTER route decorator
  - [ ] Add structured logging for rate limit checks
  - [ ] Document decorator usage pattern for future tools

- [ ] **Task 8: Add Rate Limit Headers to Successful Responses** (AC: Headers on 2xx responses)
  - [ ] Implement response middleware to add headers
  - [ ] Add `X-RateLimit-Limit` header
  - [ ] Add `X-RateLimit-Remaining` header
  - [ ] Add `X-RateLimit-Reset` header (Unix timestamp)
  - [ ] Headers present on all successful responses

- [ ] **Task 9: Write Unit Tests** (AC: Test coverage for all functions)
  - [ ] Test `get_rate_limit_key()` with API key
  - [ ] Test `get_rate_limit_key()` with IP only
  - [ ] Test `get_rate_limit_key()` with X-Forwarded-For
  - [ ] Test `get_tier_rate_limit()` for all three tiers
  - [ ] Test rate limit enforcement (100 requests/hour)
  - [ ] Test 429 response format matches project-context.md
  - [ ] Test headers in 429 responses
  - [ ] Use pytest-asyncio for async tests

- [ ] **Task 10: Write Integration Tests** (AC: End-to-end rate limiting works)
  - [ ] Test public tier: 101st request returns 429
  - [ ] Test registered tier: 1001st request returns 429
  - [ ] Test premium tier: no rate limiting up to 10,000 requests
  - [ ] Test rate limit reset after time window
  - [ ] Test concurrent requests from same IP
  - [ ] Test requests from different IPs are independent
  - [ ] Test API key requests from different keys are independent

## Dev Notes

### 🔥 CRITICAL: Why This Story Matters

This is the **FIRST LINE OF DEFENSE** against API abuse in production. Rate limiting protects:
- **Server resources** from being overwhelmed by malicious or buggy clients
- **Database costs** by preventing unlimited MongoDB/Qdrant queries
- **Fair access** for all users by preventing one client from monopolizing the service
- **Revenue** by enforcing tier-based access (public vs registered vs premium)

**Common LLM Developer Mistakes to PREVENT:**
1. ❌ Implementing rate limiting AFTER routes are defined (slowapi won't work)
2. ❌ Forgetting to handle `X-Forwarded-For` header (all requests appear from same IP behind proxy)
3. ❌ Not returning MCP-compatible error format (breaks Claude Code client)
4. ❌ Using global middleware instead of decorators (less flexible, harder to test)
5. ❌ Hardcoding rate limits instead of tier-based dynamic limits
6. ❌ Not including rate limit headers in successful responses (poor UX)
7. ❌ Testing with sleep() instead of mocking time (slow tests)

### Technology Selection: slowapi

**Why slowapi?** (From Web Research)

| Criterion | slowapi | fastapi-limiter | Custom Middleware |
|-----------|---------|-----------------|-------------------|
| **Maturity** | ✅ Battle-tested (millions of req/month in production) | ⚠️ Less adoption | ❌ Untested |
| **FastAPI Integration** | ✅ Native decorator support | ✅ Native dependency injection | ⚠️ Requires custom work |
| **In-Memory Backend** | ✅ Built-in | ❌ Redis-only | ✅ Custom implementation |
| **Redis Migration** | ✅ Simple config change | ✅ Built-in | ❌ Major refactor |
| **Algorithm** | ✅ Token bucket (best for APIs) | ✅ Multiple algorithms | ❌ Must implement |
| **Error Handling** | ✅ Automatic 429 responses | ✅ Automatic | ❌ Must implement |
| **Headers** | ✅ Retry-After automatic | ✅ Automatic | ❌ Must implement |
| **Maintenance** | ✅ Active | ✅ Active | ❌ Our responsibility |

**Decision:** Use **slowapi** because:
1. In-memory backend with Redis migration path (matches architecture.md:86 "Redis optional for future")
2. Token bucket algorithm handles bursts naturally (good for Claude Code's request patterns)
3. Decorator-based approach (per-route control, easier testing)
4. Battle-tested in production environments
5. Simple integration with FastAPI's request object

### Rate Limiting Algorithm: Token Bucket

**How Token Bucket Works:**
```
Bucket = 100 tokens (for public tier)
Refill rate = 100 tokens/hour

Request 1:  Consume 1 token → 99 tokens remain → ✅ Allow
Request 2:  Consume 1 token → 98 tokens remain → ✅ Allow
...
Request 100: Consume 1 token → 0 tokens remain → ✅ Allow
Request 101: Need 1 token, 0 available → ❌ REJECT (429)

After 36 seconds (1/100 of an hour):
  Bucket refills by 1 token → 1 token available
  Request 102: Consume 1 token → 0 tokens remain → ✅ Allow
```

**Why Token Bucket?**
- ✅ Allows bursts (user can make 100 requests immediately if needed)
- ✅ Smooth long-term enforcement (averages to 100 req/hr over time)
- ✅ Low memory (only stores token count + timestamp per key)
- ✅ Natural API behavior (feels responsive to users)

**Alternative: Fixed Window** (NOT RECOMMENDED)
```
Window 1:00-2:00: 100 requests allowed
Window 2:00-3:00: 100 requests allowed

Problem: User can make 200 requests in 2 seconds:
  1:59:59 → Make 100 requests → ✅ Allowed (Window 1)
  2:00:01 → Make 100 requests → ✅ Allowed (Window 2)
  Total: 200 requests in 2 seconds! (Burst vulnerability)
```

### Architecture Compliance

**From architecture.md:315-327 (Tiered Authentication Model):**

| Tier | Auth Required | Rate Limit | Access |
|------|---------------|------------|--------|
| **Public** | None | **100 req/hr per IP** | Core search, public extractions |
| **Registered** | API Key (`X-API-Key`) | **1000 req/hr per key** | Full search, all extractions |
| **Premium** | API Key + Subscription | **Unlimited** | Premium content, priority |

**From architecture.md:86 (Infrastructure):**
> "Tiered authentication model with three tiers:
>   - Public: No auth, 100 req/hr per IP, core search access
>   - Registered: API Key (`X-API-Key` header), 1000 req/hr, full access
>   - Premium: API Key + Subscription, unlimited access (future implementation)"

**Implementation Mapping:**
- `get_rate_limit_key()` → Determines tier from `X-API-Key` header presence
- `get_tier_rate_limit()` → Returns "100/hour", "1000/hour", or "999999/hour"
- Token bucket → Enforces limits smoothly with burst tolerance

### File Structure & Module Organization

**From architecture.md:699-704:**
```
packages/mcp-server/
└── src/
    ├── middleware/
    │   ├── __init__.py
    │   ├── rate_limit.py      # ← THIS STORY
    │   ├── auth.py             # Story 5.2
    │   └── logging.py
```

**Rate Limit Module Exports:**
```python
# packages/mcp-server/src/middleware/rate_limit.py

# Public API for other modules
__all__ = [
    "limiter",                    # slowapi Limiter instance
    "get_rate_limit_key",         # Key function for tier detection
    "get_tier_rate_limit",        # Dynamic limit function
    "rate_limit_error_handler"    # Custom 429 error handler
]
```

**Usage in MCP Tools (Future Stories):**
```python
# packages/mcp-server/src/tools/search_knowledge.py

from fastapi import Request
from ..middleware.rate_limit import limiter, get_tier_rate_limit

@app.post("/tools/search_knowledge")
@limiter.limit(get_tier_rate_limit)  # ← Apply rate limiting
async def search_knowledge(request: Request, query: str):
    """Search knowledge base with tier-based rate limiting"""
    # Tool implementation...
    return {"results": [...], "metadata": {...}}
```

### Critical Implementation Details

#### 1. Proxy-Aware IP Detection

**Problem:** When deployed behind Railway/load balancer, all requests appear from same IP
**Solution:** Check `X-Forwarded-For` header first

```python
def get_rate_limit_key(request: Request) -> str:
    """Extract rate limit key with proxy awareness"""
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key}"

    # CRITICAL: Check X-Forwarded-For BEFORE request.client.host
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # First IP in comma-separated list is real client
        ip = forwarded.split(",")[0].strip()
        return f"ip:{ip}"

    # Fallback for local development (no proxy)
    return f"ip:{request.client.host or 'unknown'}"
```

**Why this matters:**
- Railway/cloud deployments use reverse proxies
- Without `X-Forwarded-For`, all public tier users share one limit
- `X-Forwarded-For: client_ip, proxy1_ip, proxy2_ip` format
- ALWAYS take first IP (real client), not last (proxy)

#### 2. MCP-Compatible Error Response Format

**From project-context.md:94-102 (Error Response Format - MANDATORY):**

```python
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",  # or NOT_FOUND, VALIDATION_ERROR, etc.
        "message": str,
        "details": {}
    }
}
```

**CRITICAL: slowapi Default vs MCP Format**

slowapi default response (❌ WRONG):
```python
{
    "error": "Rate limit exceeded: 100 per 1 hour"
}
```

MCP-compatible response (✅ CORRECT):
```python
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Rate limit of 100 requests per hour exceeded",
        "details": {
            "limit": 100,
            "window_seconds": 3600,
            "retry_after": 2847,
            "tier": "public"
        }
    }
}
```

**Implementation:**
```python
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

async def rate_limit_error_handler(
    request: Request,
    exc: RateLimitExceeded
) -> JSONResponse:
    """Return MCP-compatible error response for rate limit exceeded"""

    # Extract retry_after from exception detail string
    # slowapi format: "Rate limit exceeded: 100 per 1 hour"
    # Parse to get seconds until reset

    return JSONResponse(
        status_code=429,
        headers={
            "Retry-After": str(retry_after_seconds),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_timestamp)
        },
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit of {limit} requests per hour exceeded",
                "details": {
                    "limit": limit,
                    "window_seconds": 3600,
                    "retry_after": retry_after_seconds,
                    "tier": get_tier_from_request(request)
                }
            }
        }
    )

# Register handler in FastAPI app
app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)
```

#### 3. Rate Limit Headers on Successful Responses

**Best Practice:** Include rate limit headers on ALL responses (not just 429s)

**Headers to Add:**

| Header | Type | Example | Purpose |
|--------|------|---------|---------|
| `X-RateLimit-Limit` | int | `100` | Max requests in window |
| `X-RateLimit-Remaining` | int | `73` | Requests left in current window |
| `X-RateLimit-Reset` | int | `1735641600` | Unix timestamp when limit resets |
| `Retry-After` | int | `2847` | Seconds until reset (429 only) |

**Why this matters:**
- Clients can track their usage without hitting 429
- Claude Code can show "23 requests remaining" to user
- Enables exponential backoff strategies
- Better developer experience

**Implementation Options:**

Option 1: Response middleware (adds to all responses)
```python
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add headers from slowapi state
        # (slowapi stores this in request.state)
        if hasattr(request.state, "view_rate_limit"):
            limit_info = request.state.view_rate_limit
            response.headers["X-RateLimit-Limit"] = str(limit_info.limit)
            response.headers["X-RateLimit-Remaining"] = str(limit_info.remaining)
            response.headers["X-RateLimit-Reset"] = str(limit_info.reset_time)

        return response
```

Option 2: Decorator wrapper (per-route control)
```python
from functools import wraps

def add_rate_limit_headers(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        response = await func(request, *args, **kwargs)
        # Add headers from slowapi...
        return response
    return wrapper
```

**Recommendation:** Use middleware for consistency across all endpoints.

#### 4. Dynamic Tier Detection (Future-Proof)

**Current Implementation (Story 5.1):**
```python
async def get_tier_rate_limit(request: Request) -> str:
    """Return rate limit based on API key presence"""
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return "100/hour"  # Public tier

    # Placeholder: Detect premium by key prefix
    if api_key.startswith("premium_"):
        return "999999/hour"  # Unlimited
    else:
        return "1000/hour"  # Registered tier
```

**Future Enhancement (Story 5.2 - API Key Authentication):**
```python
from ..storage.mongodb import get_user_tier

async def get_tier_rate_limit(request: Request) -> str:
    """Return rate limit based on user tier from database"""
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return "100/hour"

    # Query MongoDB for user tier
    tier = await get_user_tier(api_key)

    tier_limits = {
        "public": "100/hour",
        "registered": "1000/hour",
        "premium": "999999/hour"
    }

    return tier_limits.get(tier, "100/hour")
```

**TODO Comments to Add:**
```python
# TODO(Story 5.2): Replace key prefix detection with MongoDB tier lookup
# TODO(Story 5.2): Cache tier lookups to avoid repeated database queries
# TODO(Story 5.2): Add tier to request.state for use in logging/analytics
```

### Testing Strategy

#### Unit Tests (`tests/test_middleware/test_rate_limit.py`)

**Test Tier Detection:**
```python
import pytest
from fastapi import Request
from src.middleware.rate_limit import get_rate_limit_key

def test_get_rate_limit_key_with_api_key():
    """API key should be used as rate limit key"""
    request = create_mock_request(
        headers={"X-API-Key": "test_key_123"}
    )
    assert get_rate_limit_key(request) == "apikey:test_key_123"

def test_get_rate_limit_key_with_x_forwarded_for():
    """Should extract real IP from X-Forwarded-For"""
    request = create_mock_request(
        headers={"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
    )
    assert get_rate_limit_key(request) == "ip:203.0.113.1"

def test_get_rate_limit_key_fallback_to_client_host():
    """Should fall back to client.host if no headers"""
    request = create_mock_request(client_host="192.168.1.1")
    assert get_rate_limit_key(request) == "ip:192.168.1.1"
```

**Test Dynamic Limits:**
```python
@pytest.mark.asyncio
async def test_get_tier_rate_limit_public():
    """Public tier (no API key) should get 100/hour"""
    request = create_mock_request()
    limit = await get_tier_rate_limit(request)
    assert limit == "100/hour"

@pytest.mark.asyncio
async def test_get_tier_rate_limit_registered():
    """Registered tier should get 1000/hour"""
    request = create_mock_request(
        headers={"X-API-Key": "reg_test_key"}
    )
    limit = await get_tier_rate_limit(request)
    assert limit == "1000/hour"

@pytest.mark.asyncio
async def test_get_tier_rate_limit_premium():
    """Premium tier should get unlimited (999999/hour)"""
    request = create_mock_request(
        headers={"X-API-Key": "premium_test_key"}
    )
    limit = await get_tier_rate_limit(request)
    assert limit == "999999/hour"
```

**Test Error Response Format:**
```python
@pytest.mark.asyncio
async def test_rate_limit_error_response_format():
    """429 response should match MCP error format"""
    exc = RateLimitExceeded("Rate limit exceeded: 100 per 1 hour")
    request = create_mock_request()

    response = await rate_limit_error_handler(request, exc)

    assert response.status_code == 429
    assert "Retry-After" in response.headers

    body = json.loads(response.body)
    assert "error" in body
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "message" in body["error"]
    assert "details" in body["error"]
```

#### Integration Tests (`tests/test_middleware/test_rate_limit_integration.py`)

**Test Rate Limit Enforcement:**
```python
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_public_tier_rate_limit_enforcement():
    """Public tier should be limited to 100 requests/hour"""
    client = TestClient(app)

    # Make 100 requests - all should succeed
    for i in range(100):
        response = client.get("/health")
        assert response.status_code == 200

    # 101st request should be rate limited
    response = client.get("/health")
    assert response.status_code == 429
    assert "error" in response.json()
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

@pytest.mark.asyncio
async def test_registered_tier_rate_limit():
    """Registered tier should be limited to 1000 requests/hour"""
    client = TestClient(app)
    headers = {"X-API-Key": "reg_test_key"}

    # Make 1000 requests - all should succeed
    for i in range(1000):
        response = client.get("/health", headers=headers)
        assert response.status_code == 200

    # 1001st request should be rate limited
    response = client.get("/health", headers=headers)
    assert response.status_code == 429
```

**CRITICAL: Test Performance**
```python
import time

def test_rate_limit_does_not_slow_requests():
    """Rate limiting should add <10ms latency"""
    client = TestClient(app)

    start = time.time()
    for i in range(10):
        client.get("/health")
    duration = time.time() - start

    # Each request should take <100ms (10 requests in 1 second)
    assert duration < 1.0
```

### Structured Logging Requirements

**From project-context.md:153-164 (Logging - MANDATORY):**

```python
import structlog
logger = structlog.get_logger()

# ✅ GOOD: Structured with context
logger.info(
    "rate_limit_check",
    key="ip:203.0.113.1",
    tier="public",
    limit=100,
    remaining=73
)

# ✅ GOOD: Rate limit exceeded
logger.warning(
    "rate_limit_exceeded",
    key="apikey:test_123",
    tier="registered",
    limit=1000,
    retry_after=2847
)

# ❌ BAD: Never use print
print(f"Rate limit exceeded for {key}")  # NEVER DO THIS
```

### Migration Path to Redis (Future)

**When to Migrate:**
- Deploying multiple MCP server instances
- Rate limit state must be shared across servers
- Need persistent state (survive restarts)

**Migration Steps (Future Story):**
```python
# Current (In-Memory):
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[]
)

# Future (Redis):
limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri="redis://localhost:6379",  # Or cloud Redis URL
    default_limits=[]
)
```

**Dependencies to Add:**
```bash
uv add redis        # For Redis backend
# OR
uv add redis-py     # Alternative Redis client
```

**Zero Code Changes Required:**
- slowapi abstracts storage backend
- Same decorators work with Redis
- Same error handling
- Same headers

### Common Pitfalls & Solutions

| Pitfall | Why It's Bad | Solution |
|---------|--------------|----------|
| **Hardcoding limits in decorators** | Can't support tiers | Use `get_tier_rate_limit()` function |
| **Not handling X-Forwarded-For** | All users share one limit | Check header before `client.host` |
| **Using middleware instead of decorators** | Less flexible, harder to test | Use `@limiter.limit()` decorator |
| **Not returning MCP error format** | Breaks Claude Code client | Custom error handler with exact format |
| **Forgetting headers on 2xx responses** | Poor UX, no usage tracking | Response middleware adds headers |
| **Testing with sleep()** | Slow tests (hours!) | Mock time or use small windows for testing |
| **Not logging tier decisions** | Hard to debug tier issues | Structured logging for all tier detections |

### Security Considerations

**From project-context.md:234-238 (Security Rules):**

1. **API keys in headers only** - Never accept keys in query params (logged in URLs)
2. **Never log credentials** - Log `api_key[:10]` not full key
3. **Rate limit public endpoints** - 100 req/hr default for unauthenticated
4. **Validate all input** - slowapi handles this, but verify error responses

**IP Spoofing Protection:**
```python
# ONLY trust X-Forwarded-For in controlled environments
# For Railway deployment, this is safe (Railway sets header)
# For open internet, could be spoofed

# Future enhancement: Verify X-Forwarded-For against trusted proxy list
TRUSTED_PROXIES = ["10.0.0.0/8"]  # Railway internal IPs

def get_real_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded and is_from_trusted_proxy(request):
        return forwarded.split(",")[0].strip()
    return request.client.host or "unknown"
```

### Project Structure Notes

**File Locations:**
```
packages/mcp-server/
├── src/
│   ├── middleware/
│   │   ├── __init__.py          # Export public API
│   │   ├── rate_limit.py        # THIS STORY
│   │   ├── auth.py              # Story 5.2 (future)
│   │   └── logging.py           # Future enhancement
│   ├── tools/                    # Will use rate_limit
│   └── server.py                 # Registers error handler
└── tests/
    └── test_middleware/
        ├── __init__.py
        ├── test_rate_limit.py           # Unit tests
        └── test_rate_limit_integration.py  # Integration tests
```

**Import Structure:**
```python
# In server.py (register error handler)
from src.middleware.rate_limit import rate_limit_error_handler
app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)

# In tools/search_knowledge.py (apply rate limiting)
from ..middleware.rate_limit import limiter, get_tier_rate_limit

@app.post("/tools/search_knowledge")
@limiter.limit(get_tier_rate_limit)
async def search_knowledge(request: Request, query: str):
    ...
```

### References

- [Source: architecture.md#Authentication-&-Security (lines 315-327)] - Tiered authentication model with rate limits
- [Source: architecture.md#Infrastructure-&-Deployment (lines 86-88)] - In-memory with Redis optional
- [Source: project-context.md#Error-Response-Format (lines 94-102)] - MANDATORY error format
- [Source: project-context.md#Security-Rules (lines 234-238)] - API key and rate limiting security
- [Source: epics.md#Story-5.1 (lines 628-643)] - Story acceptance criteria
- [Source: Web Research: FastAPI Rate Limiting Best Practices 2025] - slowapi selection, token bucket algorithm
- [Source: Story 1.2 (docker-compose-infrastructure-setup.md)] - Project structure and patterns

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent during implementation_

### Debug Log References

_To be filled by dev agent during implementation_

### Completion Notes List

_To be filled by dev agent during implementation_

### File List

_To be filled by dev agent during implementation_

