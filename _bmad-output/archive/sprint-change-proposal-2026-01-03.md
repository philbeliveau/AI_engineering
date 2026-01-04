# Sprint Change Proposal: Knowledge Base Architecture

**Date:** 2026-01-03
**Status:** Proposed
**Change Scope:** Moderate
**Author:** Correct Course Workflow
**Supersedes:** Original multi-collection architecture in `architecture.md`

---

## Section 1: Issue Summary

### Problem Statement

The current architecture uses a **multi-collection pattern** (`{project_id}_chunks`, `{project_id}_extractions`) for Qdrant vector storage. This conflicts with **Qdrant's official best practices** which recommend a single collection with payload-based filtering for multi-tenant scenarios.

### Context

- **Discovered During:** Implementation of Story 4-2 (Semantic Search Tool) and planning for Epic 4 MCP tools
- **Trigger:** Research into Qdrant multitenancy patterns revealed architecture misalignment
- **Already Tracked:** `4-cc-multi-project-collection-architecture` in sprint-status.yaml

### Evidence

1. **Qdrant Multitenancy Guide** states:
   > "In most cases, a single collection per embedding model with payload-based partitioning for different tenants is recommended. Creating too many collections may result in resource overhead and affect overall performance."

2. **Current Implementation Issues:**
   - Pipeline config.py lines 40-53: Uses `{project_id}_{type}` collection naming
   - MCP server config.py lines 46-59: Mirrors same pattern
   - No support for rich metadata filtering (year, category, tags)
   - Cross-project queries require multiple collection searches

---

## Section 2: Impact Analysis

### Epic Impact

| Epic | Status | Impact |
|------|--------|--------|
| Epic 1-3 | Done | Minor - Schema version bump, add `project_id` field to models |
| **Epic 4** | In Progress | **Major** - MCP server storage layer must use new collection structure |
| Epic 5 | Ready | Minor - Deployment unaffected, just config changes |

**Current Epic (4) Assessment:**
- Stories 4-1, 4-2: Done - Will need minor updates to use new collection
- Stories 4-3 to 4-6: Ready-for-dev - Should implement against new architecture
- Epic completion: **Still achievable** with proposed changes

### Story Impact

| Story | Status | Change Needed |
|-------|--------|---------------|
| 3.6 | Done | Add `project_id` to extraction storage, rebuild rich payload |
| 3.7 | Done | Add `--project`, `--category`, `--tags`, `--year` CLI flags |
| 4-3 | Ready | Implement with `project_id` filter and new payload structure |
| 4-4 | Ready | Implement with `project_id` filter |
| 4-5 | Ready | Use payload fields for source browsing |
| 4-6 | Ready | Update response models for rich metadata |

### Artifact Conflicts

#### PRD Conflicts

| Section | Conflict | Resolution |
|---------|----------|------------|
| FR-3.4 | States Qdrant `chunks` collection | Update to `knowledge_vectors` with `content_type="chunk"` |
| FR-3.5 | States Qdrant `extractions` collection | Update to `knowledge_vectors` with `content_type="extraction"` |
| MVP Scope | No change to scope | MVP still achievable |

#### Architecture Conflicts (PRIMARY)

| Section | Current | Proposed |
|---------|---------|----------|
| Data Architecture | `{project_id}_chunks`, `{project_id}_extractions` | Single `knowledge_vectors` collection |
| Qdrant Configuration | Two collections per project | One collection with payload filtering |
| Payload Fields | `{source_id, chunk_id, type, topics}` | Rich payload with 15+ indexed/display fields |
| Project Namespacing | Collection-per-project | Payload field `project_id` with `is_tenant=True` |

**Architecture Document Sections Requiring Update:**
- "Data Architecture" section (lines 265-340)
- "Qdrant Configuration" table (lines 302-310)
- "Project Namespacing" diagram (lines 317-354)

#### Technical Impact

| Component | Current | Change Required |
|-----------|---------|-----------------|
| `packages/pipeline/src/config.py` | Multi-collection properties | Add `knowledge_vectors` constant |
| `packages/pipeline/src/models/source.py` | No `project_id`, `year`, `category`, `tags` | Add 4 new fields |
| `packages/pipeline/src/models/chunk.py` | No `project_id` | Add field (denormalized) |
| `packages/pipeline/src/models/extraction.py` | No `project_id`, `title`, denormalized fields | Add 6 new fields |
| `packages/pipeline/src/storage/qdrant.py` | Uses two collections | Consolidate to single collection |
| `packages/mcp-server/src/config.py` | Multi-collection properties | Mirror pipeline changes |
| `packages/mcp-server/src/storage/qdrant.py` | Searches two collections | Search single collection with filters |

---

## Section 3: Recommended Approach

### Selected Path: Option 1 - Direct Adjustment

**Rationale:**
1. Research is comprehensive and follows vendor best practices
2. Changes are additive (new fields have sensible defaults)
3. Migration path is clear (existing data gets `project_id="default"`)
4. No rollback needed - current data remains valid
5. Course correction story already tracked in sprint

### Trade-offs Considered

| Factor | Direct Adjustment | Rollback | MVP Reduction |
|--------|------------------|----------|---------------|
| Effort | Medium (~14.5h) | High (revert + redo) | N/A |
| Risk | Low | Medium | N/A |
| Timeline | +1-2 days | +3-4 days | N/A |
| Technical Debt | Reduces debt | Increases | N/A |

### Effort Estimate

| Package | Work Item | Estimate |
|---------|-----------|----------|
| **Pipeline** | Model updates (Source, Chunk, Extraction) | 1.5h |
| | Config updates | 0.5h |
| | MongoDB storage + indexes | 1.5h |
| | Qdrant storage (single collection + indexes) | 2h |
| | CLI script updates | 0.5h |
| | Migration script | 2h |
| | Test updates | 2h |
| **Pipeline Subtotal** | | **10h** |
| **MCP Server** | Config updates | 0.25h |
| | Storage client updates | 1.5h |
| | Filter utilities | 0.5h |
| | Tool updates (4-3 to 4-6) | 1h |
| | Test updates | 1h |
| **MCP Server Subtotal** | | **4.25h** |
| **Total** | | **~14.5h** |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data migration issues | Low | Medium | Run migration in dev first, verify counts |
| Performance regression | Low | Low | Qdrant optimized for single collection |
| Breaking existing queries | Low | Medium | Payload backward compatible |
| Scope creep | Medium | Low | Strictly follow proposal, no extras |

---

## Section 4: Detailed Change Proposals

### 4.1 Schema Changes

#### Source Model (`packages/pipeline/src/models/source.py`)

```
Story: Schema Update - Source Model
Section: Model Fields

OLD (lines 16-43):
class Source(BaseModel):
    id: str
    type: Literal["book", "paper", "case_study"]
    title: str
    authors: list[str]
    path: str
    ingested_at: datetime
    status: Literal["pending", "processing", "complete", "failed"]
    metadata: dict
    schema_version: str = "1.0"

NEW:
class Source(BaseModel):
    id: str
    project_id: str = Field(default="default", description="Project namespace")
    type: Literal["book", "paper", "case_study"]
    title: str
    authors: list[str]
    path: str
    year: Optional[int] = Field(default=None, ge=1900, le=2100)
    category: Literal["foundational", "advanced", "reference", "case_study"] = "foundational"
    tags: list[str] = Field(default_factory=list)
    ingested_at: datetime
    status: Literal["pending", "processing", "complete", "failed"]
    metadata: dict
    schema_version: str = "1.1"

Rationale: Enable multi-project isolation and rich filtering per Qdrant best practices
```

#### Extraction Model (`packages/pipeline/src/models/extraction.py`)

```
Story: Schema Update - Extraction Model
Section: Model Fields

OLD (lines 188-212):
class Extraction(BaseModel):
    id: str
    source_id: str
    chunk_id: str
    type: ExtractionType
    content: ContentType
    topics: list[str]
    schema_version: str = "1.0"
    extracted_at: datetime

NEW:
class Extraction(BaseModel):
    id: str
    source_id: str
    chunk_id: str
    project_id: str = Field(default="default")  # Denormalized
    type: ExtractionType
    content: ContentType
    topics: list[str]
    title: str = ""  # Human-readable extraction title
    source_title: str = ""  # Denormalized for Qdrant payload
    source_type: str = ""  # Denormalized
    chapter: Optional[str] = None
    schema_version: str = "1.1"
    extracted_at: datetime

Rationale: Rich payload enables display without MongoDB lookup, improves query UX
```

### 4.2 Storage Layer Changes

#### Pipeline Qdrant Storage (`packages/pipeline/src/storage/qdrant.py`)

```
Story: Storage Update - Single Collection Architecture
Section: Collection Constants

OLD (lines 36-40):
CHUNKS_COLLECTION = settings.chunks_collection  # {project_id}_chunks
EXTRACTIONS_COLLECTION = settings.extractions_collection  # {project_id}_extractions

NEW:
KNOWLEDGE_VECTORS_COLLECTION = "knowledge_vectors"  # Single collection for all vectors

Rationale: Follow Qdrant multitenancy best practice - one collection, payload filtering
```

```
Story: Storage Update - Payload Indexes
Section: _create_payload_indexes method

OLD (lines 163-179):
index_fields = ["type", "topics", "source_id"]

NEW:
# Tenant index (co-locates vectors for performance)
client.create_payload_index(
    collection_name="knowledge_vectors",
    field_name="project_id",
    field_schema="keyword",
    is_tenant=True,  # v1.11+ optimization
)
# Content type index
index_fields = [
    "content_type",  # "chunk" | "extraction"
    "source_id",
    "source_type",
    "source_category",
    "source_year",
    "extraction_type",
    "topics",
    "chapter",
]

Rationale: Rich indexes enable all planned filtering use cases
```

### 4.3 Config Changes

#### Pipeline Config (`packages/pipeline/src/config.py`)

```
Story: Config Update - Collection Naming
Section: Collection Properties

OLD (lines 40-53):
@property
def sources_collection(self) -> str:
    return f"{self.project_id}_sources"

@property
def chunks_collection(self) -> str:
    return f"{self.project_id}_chunks"

@property
def extractions_collection(self) -> str:
    return f"{self.project_id}_extractions"

NEW:
@property
def sources_collection(self) -> str:
    return f"{self.project_id}_sources"  # MongoDB still per-project

@property
def chunks_collection(self) -> str:
    return f"{self.project_id}_chunks"  # MongoDB still per-project

@property
def extractions_collection(self) -> str:
    return f"{self.project_id}_extractions"  # MongoDB still per-project

# Qdrant uses single collection
KNOWLEDGE_VECTORS_COLLECTION: str = "knowledge_vectors"

Rationale: MongoDB can remain per-project (no multitenancy issue), Qdrant consolidates
```

### 4.4 Architecture Document Updates

#### architecture.md - Data Architecture Section

```
Story: Architecture Update
Section: Data Architecture (lines 265-340)

OLD:
Qdrant Configuration:
| Collection: `chunks` | Semantic search on raw text |
| Collection: `extractions` | Semantic search on extraction summaries |

Project Namespacing:
Collections are dynamically named based on PROJECT_ID:
├── ai_engineering_sources
├── ai_engineering_chunks
└── ai_engineering_extractions

NEW:
Qdrant Configuration:
| Collection: `knowledge_vectors` | Unified semantic search with payload filtering |
| Payload filters: `project_id`, `content_type`, `extraction_type`, `source_*` |

Project Namespacing:
Single Qdrant collection with payload-based isolation (per Qdrant best practices):
knowledge_vectors/
├── project_id="ai_engineering" (payload filter)
├── project_id="bmad_docs" (payload filter)
└── project_id="default" (payload filter)

MongoDB collections remain per-project:
├── ai_engineering_sources
├── ai_engineering_chunks
└── ai_engineering_extractions

Rationale: Follows Qdrant multitenancy guide recommendation for single collection
```

---

## Section 5: Implementation Handoff

### Change Scope Classification

**Scope: MODERATE**
- Requires backlog reorganization (update story 4-cc)
- Architecture document update needed
- Development team can implement with SM coordination

### Handoff Recipients

| Role | Responsibility |
|------|----------------|
| **Developer** | Implement schema, storage, and migration changes |
| **SM (Scrum Master)** | Update sprint-status.yaml, coordinate story sequencing |
| **Architect** | Update architecture.md with approved changes |

### Implementation Sequence

1. **Update architecture.md** (Architect)
   - Document single-collection decision
   - Update Data Architecture section
   - Add rich payload schema

2. **Update schema models** (Developer)
   - Source: +project_id, +year, +category, +tags, bump version
   - Chunk: +project_id (denormalized), bump version
   - Extraction: +project_id, +title, +source_*, bump version

3. **Update pipeline storage** (Developer)
   - Consolidate to single `knowledge_vectors` collection
   - Add all payload indexes with `is_tenant=True` for project_id
   - Build rich payload from denormalized fields

4. **Update MCP server storage** (Developer)
   - Search single collection with project_id filter
   - Support rich filter options

5. **Update CLI scripts** (Developer)
   - Add `--project`, `--category`, `--tags`, `--year` flags
   - Default project_id from environment

6. **Create migration script** (Developer)
   - Migrate existing vectors to new collection with payloads
   - Verify counts and payload structure

7. **Update tests** (Developer)
   - Multi-project isolation tests
   - Rich filtering tests
   - Cross-project query tests

### Success Criteria

- [ ] Single `knowledge_vectors` collection created with all indexes
- [ ] `project_id` payload filter with `is_tenant=True` optimization
- [ ] Rich payload includes all display fields (source_title, etc.)
- [ ] Existing data migrated with `project_id="default"`
- [ ] CLI supports `--project`, `--category`, `--tags`, `--year`
- [ ] MCP tools filter by project_id
- [ ] Cross-project queries work by omitting project filter
- [ ] Architecture.md updated
- [ ] All existing tests still pass
- [ ] New multi-project isolation tests pass

---

## Decision

**Approved:** [x]
**Approved with changes:** [ ]
**Rejected:** [ ]

**Approved By:** Philippebeliveau
**Approval Date:** 2026-01-03

**Conditions/Notes:**
None - approved as proposed.

---

## Checklist Summary

| Section | Status |
|---------|--------|
| 1. Understand Trigger | [x] Done |
| 2. Epic Impact | [x] Done |
| 3. Artifact Conflicts | [x] Done |
| 4. Path Forward | [x] Done - Option 1 Selected |
| 5. Proposal Components | [x] Done |
| 6. Final Review | [x] Done - Approved 2026-01-03 |

---

**Generated by:** Correct Course Workflow
**Reference Document:** `course-correction-knowledge-base-architecture.md`
