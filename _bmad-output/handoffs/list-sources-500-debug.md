# Handoff: Debug `/list_sources` 500 Internal Error

## Problem Summary

The `/list_sources` endpoint on the production MCP server returns 500 Internal Error, but works perfectly in local tests.

**Production URL:** `https://knowledge-mcp-production.up.railway.app/list_sources`

## What Works

- `/health` - Returns healthy, MongoDB and Qdrant connected
- `/search_knowledge` - POST with query params works fine
- `/get_methodologies` - Works fine
- `/debug/config` - Returns configuration correctly
- All local pytest tests pass (402 passed)

## What Fails

- `/list_sources` - Always returns 500 with correlation_id
- Error format: `{"error":{"code":"INTERNAL_ERROR","message":"An unexpected error occurred","details":{"correlation_id":"..."},"retry_after":null}}`

## Exception Handling Already Added

All of these are in `packages/mcp-server/src/tools/sources.py`:

1. **MongoDB call** (line 200-214): Wrapped in try/except, returns empty response on failure
2. **Qdrant call** (line 220-229): Wrapped in try/except, logs warning and continues with empty counts
3. **SourceResult building** (line 236-255): Individual sources wrapped in try/except, skips malformed sources
4. **Global wrapper** (line 177-197): Entire function wrapped in try/except calling `_list_sources_impl()`

Despite ALL this exception handling, the 500 error still occurs.

## Key Insight

The global exception handler in `src/middleware/error_handlers.py:109-145` (`generic_exception_handler`) is catching an exception that my endpoint code isn't seeing. This means the error is happening:

1. BEFORE my endpoint code runs (route registration, middleware, imports)
2. AFTER my endpoint returns (response serialization, Pydantic validation at framework level)
3. The new code isn't actually deployed (deployment issue)

## Files to Investigate

- `packages/mcp-server/src/tools/sources.py` - The endpoint (heavily modified with exception handling)
- `packages/mcp-server/src/models/responses.py` - SourceResult, SourceListResponse, SourceListMetadata models
- `packages/mcp-server/src/storage/mongodb.py:156-176` - `list_sources()` method
- `packages/mcp-server/src/middleware/error_handlers.py` - Global exception handler logs errors with `exc_info=True`

## Debug Endpoint Added (not yet deployed)

A `/debug/sources` endpoint was added to `src/server.py` to test MongoDB directly:
```python
@app.get("/debug/sources")
async def debug_sources():
    sources = await mongodb_client.list_sources(limit=3)
    return {"status": "ok", "count": len(sources), "sources": [...]}
```

This change is staged but not committed/pushed.

## Next Steps to Try

1. **Deploy the debug endpoint** - Commit and push the staged changes to server.py, then test `/debug/sources`

2. **Check Railway logs** - The error is logged with full stack trace:
   ```bash
   cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering
   railway logs --service knowledge-mcp
   ```
   Look for `internal_error` log entries with the correlation_id

3. **Check response serialization** - The SourceResult model has these required fields:
   - `id`, `title`, `type`, `path`, `ingested_at`, `status` (all strings)
   - `authors` (list[str])
   - `extraction_counts` (dict[str, int])

   If MongoDB returns data that can't be serialized (datetime objects, ObjectId, etc.), Pydantic might fail AFTER the function returns.

4. **Test with minimal response** - Modify `_list_sources_impl` to return immediately after MongoDB call with hardcoded SourceResult to isolate if issue is in data processing or MongoDB call itself.

5. **Check for import errors** - Unused imports in sources.py:
   ```python
   from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
   ```
   These are no longer used but shouldn't cause runtime errors.

## Commands for Testing

```bash
# Test production endpoint
curl -s https://knowledge-mcp-production.up.railway.app/list_sources

# Test debug endpoint (after deploying)
curl -s https://knowledge-mcp-production.up.railway.app/debug/sources

# Run local tests
cd packages/mcp-server && uv run pytest tests/test_tools/test_sources.py -v

# Check Railway deployment
railway status
railway logs --service knowledge-mcp
```

## Git Status

Recent commits related to this issue:
- `6c5c2ea` - Global exception handler wrapper
- `324a14f` - SourceResult building exception handling
- `b6960ea` - MongoDB call exception handling
- `ea70f2a` - Qdrant call exception handling (widened to `except Exception`)

Staged but not committed:
- `packages/mcp-server/src/server.py` - Debug endpoint addition
