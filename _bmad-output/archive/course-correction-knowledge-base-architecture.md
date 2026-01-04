# Course Correction: Knowledge Base Architecture (Research-Backed)

**Date:** 2026-01-01
**Status:** Proposed
**Impact:** Medium-High - Schema, storage layer, and payload structure changes
**Supersedes:** `course-correction-multi-project-collections.md` (Option 2 rejected)
**Affected Stories:** 2.6, 3.6, 3.7, Epic 4 (MCP Server), future stories

---

## Problem Statement

The current architecture has two issues:

1. **Single Project Limitation:** Fixed collection names (`sources`, `chunks`, `extractions`) limit the system to one knowledge domain
2. **Poor Metadata:** Insufficient metadata for filtering, browsing, and organizing 10+ books/papers

Our initial proposal (collection-per-project) conflicts with Qdrant best practices.

---

## Research Findings

### Qdrant Official Recommendation

From [Qdrant Multitenancy Guide](https://qdrant.tech/documentation/guides/multitenancy/):

> "In most cases, **a single collection** per embedding model with **payload-based partitioning** for different tenants is recommended. Creating too many collections may result in resource overhead and affect overall performance."

### RAG Metadata Best Practices

From [Unstructured.io](https://unstructured.io/insights/how-to-use-metadata-in-rag-for-better-contextual-results):

> "Metadata filtering narrows the search space, improving retrieval speed and accuracy by pre-selecting documents before applying vector similarity search."

### Taxonomy Design

From [Knowledge Base Taxonomy Best Practices](https://www.matrixflows.com/blog/10-best-practices-for-creating-taxonomy-for-your-company-knowledge-base):

> "Keep hierarchy to 3-4 levels maximum. Implement hybrid categorization—combine hierarchical navigation with faceted filtering."

---

## Proposed Solution: Single Collection + Payload Filtering

### Architecture Overview

```
Qdrant: knowledge_vectors (SINGLE collection for ALL projects)
├── Payload fields for filtering (indexed)
├── Rich metadata for display (not indexed)
└── 384d vectors from all-MiniLM-L6-v2

MongoDB: knowledge_db (SINGLE set of collections)
├── sources      → All sources with project_id field
├── chunks       → All chunks with project_id field
└── extractions  → All extractions with project_id field
```

### Why Single Collection?

| Multi-Collection (Rejected) | Single Collection (Approved) |
|-----------------------------|------------------------------|
| `ai_engineering_extractions` | `knowledge_vectors` with `project_id` filter |
| Physical isolation | Logical isolation via payload |
| Resource overhead per collection | Qdrant optimized for large single collection |
| Cross-project queries = multiple calls | Cross-project = remove filter |
| Delete project = drop collection | Delete = filter by `project_id` |

---

## Schema Changes

### 1. Source Model (`src/models/source.py`)

```python
class Source(BaseModel):
    # Identity
    id: str
    project_id: str = Field(
        default="default",
        description="Project namespace for multi-project isolation"
    )

    # Document Metadata
    title: str
    authors: list[str] = Field(default_factory=list)
    type: Literal["book", "paper", "case_study"]
    year: Optional[int] = Field(default=None, ge=1900, le=2100)

    # Faceted Taxonomy (NEW)
    category: Literal["foundational", "advanced", "reference", "case_study"] = "foundational"
    tags: list[str] = Field(default_factory=list)  # ["rag", "fine-tuning", "agents"]

    # Technical
    path: str
    status: Literal["pending", "processing", "complete", "failed"]
    ingested_at: datetime

    # Flexible Extension
    metadata: dict = Field(default_factory=dict)  # pages, publisher, ISBN
    schema_version: str = "1.1"  # Bump version
```

**New Fields:**
- `project_id` - Multi-project namespace
- `year` - Publication year for recency filtering
- `category` - Faceted classification
- `tags` - Flexible topic tags

### 2. Chunk Model (`src/models/chunk.py`)

```python
class Chunk(BaseModel):
    id: str
    source_id: str
    project_id: str  # NEW: Denormalized for query efficiency

    content: str
    token_count: int

    # Hierarchical Position
    position: ChunkPosition  # chapter, section, page

    # Hierarchy Support (NEW)
    parent_chunk_id: Optional[str] = None  # For hierarchical retrieval
    depth: int = Field(default=0, ge=0, le=4)  # 0=doc, 1=chapter, 2=section

    schema_version: str = "1.1"
```

**New Fields:**
- `project_id` - Denormalized from source
- `parent_chunk_id` - Parent-child hierarchy for context retrieval
- `depth` - Hierarchy level

### 3. Extraction Model (`src/models/extraction.py`)

```python
class Extraction(BaseModel):
    id: str
    source_id: str
    chunk_id: str
    project_id: str  # NEW: Denormalized

    type: ExtractionType
    content: ContentType
    topics: list[str]

    # Enhanced Discoverability (NEW)
    title: str  # Human-readable summary

    # Source Context - Denormalized (NEW)
    source_title: str
    source_type: str
    chapter: Optional[str] = None

    extracted_at: datetime
    schema_version: str = "1.1"
```

**New Fields:**
- `project_id` - Denormalized from source
- `title` - Human-readable extraction title
- `source_title`, `source_type`, `chapter` - Denormalized for Qdrant payload

---

## Qdrant Payload Structure

### Complete Payload Schema

```python
payload = {
    # === INDEXED FIELDS (for filtering) ===

    # Tenant/Project (is_tenant=True for optimized co-location)
    "project_id": "ai_engineering",

    # Content Type
    "content_type": "extraction",  # "chunk" | "extraction"

    # Source Filters
    "source_id": "507f1f77bcf86cd799439011",
    "source_type": "book",  # book | paper | case_study
    "source_category": "foundational",
    "source_year": 2024,
    "source_tags": ["llm-ops", "production"],

    # Extraction Filters (when content_type="extraction")
    "extraction_type": "pattern",  # decision | pattern | warning | etc.
    "topics": ["reliability", "api", "error-handling"],

    # Position Filters
    "chapter": "5",

    # === NON-INDEXED FIELDS (for display) ===

    # IDs for MongoDB lookup
    "chunk_id": "507f1f77bcf86cd799439012",
    "extraction_id": "507f1f77bcf86cd799439013",

    # Display fields (avoid MongoDB lookup for common cases)
    "source_title": "LLM Engineer's Handbook",
    "extraction_title": "Retry with Exponential Backoff",
    "section": "Error Handling",
    "page": 142,
}
```

### Required Payload Indexes

```python
from qdrant_client import models

# Tenant index (co-locates vectors for performance)
client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="project_id",
    field_schema=models.PayloadSchemaType.KEYWORD,
    is_tenant=True,  # v1.11+ optimization
)

# Content type index
client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="content_type",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

# Source filters
client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="source_id",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="source_type",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="source_category",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="source_year",
    field_schema=models.PayloadSchemaType.INTEGER,
)

# Extraction filters
client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="extraction_type",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="topics",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

# Position filter
client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="chapter",
    field_schema=models.PayloadSchemaType.KEYWORD,
)
```

---

## Query Examples

### Find patterns from a specific book

```python
client.query_points(
    collection_name="knowledge_vectors",
    query=embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="project_id",
                match=models.MatchValue(value="ai_engineering")
            ),
            models.FieldCondition(
                key="source_title",
                match=models.MatchValue(value="LLM Engineer's Handbook")
            ),
            models.FieldCondition(
                key="extraction_type",
                match=models.MatchValue(value="pattern")
            ),
        ]
    ),
    limit=10,
)
```

### Find all decisions from 2024+ books

```python
client.query_points(
    collection_name="knowledge_vectors",
    query=embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="project_id",
                match=models.MatchValue(value="ai_engineering")
            ),
            models.FieldCondition(
                key="extraction_type",
                match=models.MatchValue(value="decision")
            ),
            models.FieldCondition(
                key="source_year",
                range=models.Range(gte=2024)
            ),
        ]
    ),
    limit=10,
)
```

### Cross-project search (global knowledge)

```python
# Simply omit project_id filter
client.query_points(
    collection_name="knowledge_vectors",
    query=embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="extraction_type",
                match=models.MatchValue(value="warning")
            ),
        ]
    ),
    limit=10,
)
```

---

## Code Changes Required

### Pipeline Package

| File | Change |
|------|--------|
| `src/models/source.py` | Add `project_id`, `year`, `category`, `tags` fields |
| `src/models/chunk.py` | Add `project_id`, `parent_chunk_id`, `depth` fields |
| `src/models/extraction.py` | Add `project_id`, `title`, `source_title`, `source_type`, `chapter` fields |
| `src/config.py` | Add `project_id` setting with env var |
| `src/storage/mongodb.py` | Add `project_id` to all documents, add compound indexes |
| `src/storage/qdrant.py` | Rename collection to `knowledge_vectors`, add payload indexes |
| `src/storage/extraction_storage.py` | Build rich payload with denormalized fields |
| `src/ingestion/pipeline.py` | Populate `project_id` from settings |
| `src/extraction/pipeline.py` | Populate denormalized fields |
| `scripts/ingest.py` | Accept `--project` flag |
| `scripts/extract.py` | Accept `--project` flag |

### MCP Server Package (Epic 4)

| File | Change |
|------|--------|
| `src/config.py` | Add `project_id` setting |
| `src/storage/qdrant.py` | Use `knowledge_vectors` collection, apply project filter |
| `src/tools/search_*.py` | Add `project_id` filter to all queries |
| `src/tools/filters.py` | NEW: Common filter building utilities |

---

## CLI Changes

### New Usage

```bash
# Set project for session
export PROJECT_ID=ai_engineering
uv run scripts/ingest.py /path/to/book.pdf
uv run scripts/extract.py <source_id>

# Or per-command
PROJECT_ID=time_series uv run scripts/ingest.py /path/to/ts-book.pdf

# Or with flag
uv run scripts/ingest.py --project ai_engineering /path/to/book.pdf
uv run scripts/extract.py --project ai_engineering <source_id>

# Additional metadata via flags
uv run scripts/ingest.py \
    --project ai_engineering \
    --category foundational \
    --tags "rag,embeddings" \
    --year 2024 \
    /path/to/book.pdf
```

---

## Migration Plan

### Phase 1: Schema Update (Non-Breaking)

1. Add new fields with defaults to all models
2. Update storage layer to populate new fields
3. Existing data gets `project_id="default"`, `category="foundational"`
4. Bump `schema_version` to "1.1"

### Phase 2: Qdrant Restructure

1. Create new `knowledge_vectors` collection with proper indexes
2. Migrate existing vectors from `chunks` and `extractions` collections
3. Build rich payload for each vector
4. Verify migration with count checks

```python
# Migration script pseudocode
async def migrate_to_knowledge_vectors():
    # Create new collection
    client.create_collection(
        collection_name="knowledge_vectors",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    # Create all payload indexes
    create_payload_indexes()

    # Migrate chunks
    for chunk in old_chunks_collection:
        source = mongodb.get_source(chunk.source_id)
        client.upsert(
            collection_name="knowledge_vectors",
            points=[PointStruct(
                id=chunk.id,
                vector=chunk.vector,
                payload=build_chunk_payload(chunk, source)
            )]
        )

    # Migrate extractions
    for extraction in old_extractions_collection:
        source = mongodb.get_source(extraction.source_id)
        chunk = mongodb.get_chunk(extraction.chunk_id)
        client.upsert(
            collection_name="knowledge_vectors",
            points=[PointStruct(
                id=extraction.id,
                vector=extraction.vector,
                payload=build_extraction_payload(extraction, source, chunk)
            )]
        )
```

### Phase 3: MongoDB Indexes

```javascript
// Compound indexes for common queries
db.sources.createIndex({ "project_id": 1, "type": 1 })
db.sources.createIndex({ "project_id": 1, "category": 1 })
db.sources.createIndex({ "project_id": 1, "tags": 1 })

db.chunks.createIndex({ "project_id": 1, "source_id": 1 })

db.extractions.createIndex({ "project_id": 1, "source_id": 1 })
db.extractions.createIndex({ "project_id": 1, "type": 1 })
db.extractions.createIndex({ "project_id": 1, "topics": 1 })
```

### Phase 4: Update MCP Server

1. Update storage clients to use new collection/structure
2. Add project_id filter to all search tools
3. Expose new filter options (year, category, tags)

---

## Testing Requirements

### Unit Tests

1. Model validation with new fields
2. Payload builder generates correct structure
3. Filter builder constructs valid Qdrant filters
4. Settings loads PROJECT_ID from env

### Integration Tests

1. **Multi-Project Isolation:**
   - Ingest book to project A
   - Ingest book to project B
   - Query project A returns only A's data
   - Query project B returns only B's data

2. **Rich Filtering:**
   - Filter by source_type
   - Filter by category
   - Filter by year range
   - Filter by tags
   - Combine multiple filters

3. **Cross-Project Query:**
   - Omit project filter
   - Returns data from all projects

4. **Migration Verification:**
   - Count vectors before/after migration
   - Verify payload structure
   - Verify filter functionality

---

## Acceptance Criteria

- [ ] `PROJECT_ID` environment variable configures project namespace
- [ ] Single `knowledge_vectors` collection stores all vectors
- [ ] Payload indexes created for all filterable fields
- [ ] Rich payload includes denormalized source metadata
- [ ] Queries can filter by project, source, type, category, year, tags
- [ ] Cross-project queries work by omitting project filter
- [ ] MCP server applies project filter to all searches
- [ ] Existing data migrated with `project_id="default"`
- [ ] New CLI flags for `--project`, `--category`, `--tags`, `--year`

---

## Estimated Effort

### Pipeline Package

| Task | Estimate |
|------|----------|
| Update Source model | 0.5h |
| Update Chunk model | 0.5h |
| Update Extraction model | 0.5h |
| Update Settings | 0.25h |
| Update MongoDBClient + indexes | 1.5h |
| Update QdrantStorageClient + indexes | 1.5h |
| Update ExtractionStorage (rich payload) | 1h |
| Update pipelines | 0.5h |
| Update CLI scripts | 0.5h |
| Migration script | 2h |
| Update tests | 2h |
| **Subtotal** | **10.75h** |

### MCP Server Package

| Task | Estimate |
|------|----------|
| Update config | 0.25h |
| Update storage clients | 1h |
| Add filter utilities | 0.5h |
| Update all search tools | 1h |
| Update tests | 1h |
| **Subtotal** | **3.75h** |

### **Total Effort: ~14.5h**

---

## References

- [Qdrant Multitenancy Guide](https://qdrant.tech/documentation/guides/multitenancy/)
- [Qdrant Payload Indexes](https://qdrant.tech/documentation/tutorials/multiple-partitions/)
- [RAG Metadata Filtering](https://unstructured.io/insights/how-to-use-metadata-in-rag-for-better-contextual-results)
- [Hierarchical Retrieval Strategies](https://pixion.co/blog/rag-strategies-hierarchical-index-retrieval)
- [Knowledge Base Taxonomy Design](https://www.matrixflows.com/blog/10-best-practices-for-creating-taxonomy-for-your-company-knowledge-base)

---

## Decision

**Approved:** [ ]
**Approved with changes:** [ ]
**Rejected:** [ ]

**Notes:**
_To be filled after review_
