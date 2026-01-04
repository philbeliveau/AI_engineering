# Code Review Handoff: 4-cc-v2-single-collection-architecture

**Date:** 2026-01-03
**Reviewer Requested:** Senior Developer
**Story Status:** Review (Post-Fix)

---

## Context

Story `4-cc-v2-single-collection-architecture` implements a single-collection Qdrant architecture with payload-based multitenancy. An adversarial code review found **3 HIGH** and **4 MEDIUM** issues that have been fixed.

## What Was Fixed

| ID | Severity | Issue | Fix |
|----|----------|-------|-----|
| H1 | HIGH | `is_tenant=True` missing from project_id index | Used `KeywordIndexParams(type="keyword", is_tenant=True)` per Qdrant v1.11+ docs |
| H2 | HIGH | File List incomplete (2 vs 42 files) | Updated story with complete file list |
| H3 | HIGH | AC9 backwards compatibility not tested | Added `test_default_project_id_backwards_compatibility` |
| M1 | MEDIUM | MCP Server using deprecated `.search()` | Updated all 3 methods to `query_points()` API |
| M2 | MEDIUM | No test for is_tenant index | Added `test_tenant_index_is_created` |
| M3 | MEDIUM | extraction_type fallback confusing | Cleaned up logic, added warning log |
| M4 | MEDIUM | MCP missing source_year filter | Added `source_year: int \| None` param |

## Files Modified in This Review

```
packages/pipeline/src/storage/qdrant.py          # KeywordIndexParams with is_tenant=True
packages/mcp-server/src/storage/qdrant.py        # query_points API, source_year filter
packages/pipeline/scripts/ingest.py              # Updated docstring
packages/pipeline/tests/test_storage/test_qdrant.py  # 2 new tests added
```

---

## Review Tasks

### 1. Verify Unit Tests Pass

```bash
cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering/packages/pipeline
uv run pytest tests/test_storage/test_qdrant.py -v
```

**Expected:** 30 tests pass, including:
- `test_tenant_index_is_created`
- `test_default_project_id_backwards_compatibility`

### 2. Test Full Pipeline with Sample PDF

```bash
cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering/packages/pipeline

# Ingest the test PDF with new metadata flags
uv run scripts/ingest.py \
  '/Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/test-files/The3AdvantagesofAIEngineeringOps.pdf' \
  --project ai_engineering \
  --category foundational \
  --tags "ai,engineering,ops" \
  --year 2024 \
  --verbose
```

**Verify:**
- [ ] Ingestion completes without errors
- [ ] Source ID is returned
- [ ] Chunks are created with project_id in payload
- [ ] Log shows `tenant_index_created` with `is_tenant=True`

### 3. Run Extraction on Ingested Source

```bash
# Use the source_id from the ingestion output
uv run scripts/extract.py <SOURCE_ID> --verbose
```

**Verify:**
- [ ] Extractions are saved to MongoDB
- [ ] Vectors upserted to `knowledge_vectors` collection
- [ ] Payload includes: `project_id`, `content_type`, `extraction_type`

### 4. Verify Qdrant Collection Structure

```bash
# Check collection exists with correct indexes
curl -s http://localhost:6333/collections/knowledge_vectors | jq '.result.payload_schema'
```

**Expected payload indexes:**
- `project_id` (keyword, is_tenant should show in index params)
- `content_type` (keyword)
- `extraction_type` (keyword)
- `source_year` (integer)

### 5. Test Search with Filters

```python
# Quick Python test (run in REPL or script)
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# Search with project isolation
results = client.query_points(
    collection_name="knowledge_vectors",
    query=[0.1] * 384,  # dummy vector
    query_filter={
        "must": [
            {"key": "project_id", "match": {"value": "ai_engineering"}},
            {"key": "content_type", "match": {"value": "extraction"}}
        ]
    },
    limit=5,
    with_payload=True
)

print(f"Found {len(results.points)} results")
for p in results.points:
    print(f"  - {p.payload.get('extraction_type')}: {p.payload.get('extraction_title', 'N/A')[:50]}")
```

---

## Acceptance Criteria Checklist

Review against story ACs:

- [ ] **AC1:** Single `knowledge_vectors` collection used for all operations
- [ ] **AC2:** `project_id` has `is_tenant=True` index (verify in Qdrant)
- [ ] **AC3:** `content_type` discriminates chunks vs extractions
- [ ] **AC4:** Rich payload includes indexed and display fields
- [ ] **AC5:** Source model has project_id, year, category, tags
- [ ] **AC6:** Extraction model has denormalized source fields
- [ ] **AC7:** CLI accepts --project, --category, --tags, --year
- [ ] **AC8:** Queries without project_id use default from settings
- [ ] **AC9:** Missing project_id defaults to "default" (tested)
- [ ] **AC10:** MCP server uses single collection with filters

---

## Decision Required

After review, update story status:

- **PASS** → Mark story as `done`
- **FAIL** → Document issues and return to `in-progress`

---

## Related Files

- Story: `_bmad-output/implementation-artifacts/4-cc-v2-single-collection-architecture.md`
- Architecture: `_bmad-output/architecture.md`
- Project Context: `_bmad-output/project-context.md`
