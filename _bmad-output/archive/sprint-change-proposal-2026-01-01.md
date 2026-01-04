# Sprint Change Proposal: Multi-Project Collection Architecture

**Date:** 2026-01-01
**Status:** Pending Approval
**Change Scope:** Minor
**Estimated Effort:** ~6.5 hours
**Author:** Correct Course Workflow

---

## Section 1: Issue Summary

### Problem Statement

The Knowledge Pipeline architecture uses fixed MongoDB and Qdrant collection names (`sources`, `chunks`, `extractions`), preventing multi-project isolation. Users need to maintain separate knowledge domains (e.g., "AI Engineering", "Time Series", "System Design") without data mixing.

### Discovery Context

Identified during Story 4.2 (Semantic Search Tool - `search_knowledge`) implementation when considering how the MCP server would handle queries across multiple knowledge domains.

### Evidence

- Current architecture diagram shows single-namespace collections
- PRD User Journey 1 (Builder) explicitly mentions multiple book domains
- No mechanism exists to delete/backup individual projects
- Queries must scan all data even when targeting a single domain

---

## Section 2: Impact Analysis

### Epic Impact

| Epic | Status | Impact Level | Changes Required |
|------|--------|--------------|------------------|
| Epic 1: Foundation | Done | Minor Refactor | Update storage clients in Stories 1.4, 1.5 |
| Epic 2: Ingestion | Done | Minor Refactor | Add PROJECT_ID to Story 2.6 CLI |
| Epic 3: Extraction | Done | Minor Refactor | Update extraction storage in Stories 3.6, 3.7 |
| Epic 4: MCP Tools | In-Progress | Natural Fit | Implement pattern in Story 4.2 |
| Epic 5: Deployment | Ready | No Change | Configuration layer already set |

### Story Impact

**Completed Stories Requiring Refactor:**
- 1.4: MongoDB Storage Client - use `settings.*_collection`
- 1.5: Qdrant Storage Client - use `settings.*_collection`
- 2.6: Ingestion Pipeline CLI - support `PROJECT_ID` env var
- 3.6: Extraction Storage - use dynamic collection names
- 3.7: Extraction Pipeline CLI - support `PROJECT_ID` env var

**In-Progress Stories:**
- 4.2: Semantic Search Tool - implement pattern here first

### Artifact Conflicts

| Artifact | Conflict Type | Resolution |
|----------|---------------|------------|
| Architecture.md | Data architecture diagram outdated | Update collection naming section |
| Project-context.md | Missing configuration rule | Add project_id usage rule |
| config.py (both packages) | Missing project_id field | Add field and collection properties |
| mongodb.py (both packages) | Hardcoded collection names | Use settings.*_collection |
| qdrant.py (both packages) | Hardcoded collection names | Use settings.*_collection |
| CLI scripts | No PROJECT_ID support | Document env var usage |

### Technical Impact

- **Code changes:** ~15 files across both packages
- **Infrastructure:** None - databases unaware of collection naming
- **Deployment:** Minor - document PROJECT_ID in deployment config

---

## Section 3: Recommended Approach

### Selected Path: Direct Adjustment (Option 1)

The issue will be addressed by modifying existing stories and establishing the pattern in Story 4.2 (currently in-progress).

### Rationale

1. **Low effort** - 6.5 hours estimated, fits within current sprint
2. **Non-breaking** - Default `project_id="default"` maintains backwards compatibility
3. **Additive** - Enhances architecture without invalidating completed work
4. **Natural insertion point** - Story 4.2 is ideal for establishing the pattern
5. **Cross-package consistency** - Same Settings pattern applies to both packages

### Effort Estimate

| Package | Tasks | Hours |
|---------|-------|-------|
| Pipeline | Settings, storage clients, CLI, tests | 3.5h |
| MCP Server | Settings, storage clients, tests | 1.5h |
| Documentation | Architecture, project-context, README | 1.5h |
| **Total** | | **6.5h** |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missed hardcoded reference | Low | Low | Grep for collection name strings |
| Test failures | Medium | Low | Update test fixtures systematically |
| Backwards compatibility | Low | Medium | Default project_id="default" |

---

## Section 4: Detailed Change Proposals

### 4.1 Architecture.md Updates

**Data Architecture Section (lines ~267-310):**

```diff
- **MongoDB Collections (Hybrid Model):**
+ **MongoDB Collections (Hybrid Model with Project Namespacing):**

  knowledge_db/
- ├── sources           # Book/paper metadata
- ├── chunks            # Raw text chunks
- └── extractions       # Structured knowledge
+ ├── {project_id}_sources      # e.g., ai_engineering_sources
+ ├── {project_id}_chunks       # e.g., ai_engineering_chunks
+ └── {project_id}_extractions  # e.g., ai_engineering_extractions
+
+ **Project Configuration:**
+ - `PROJECT_ID` environment variable defines the active project
+ - Default: `"default"` for backwards compatibility
+ - Collection names resolved via Settings properties
```

**Qdrant Configuration Section:**

```diff
- | Collection: `chunks` | Semantic search on raw text |
- | Collection: `extractions` | Semantic search on extraction summaries |
+ | Collection: `{project_id}_chunks` | Semantic search on raw text |
+ | Collection: `{project_id}_extractions` | Semantic search on extraction summaries |
```

### 4.2 Project-context.md Update

**Add after Configuration section:**

```markdown
### Project Namespacing
- ALWAYS use `settings.sources_collection`, `settings.chunks_collection`, `settings.extractions_collection`
- NEVER hardcode collection names like `"sources"` or `"chunks"`
- `PROJECT_ID` environment variable configures the active project
- Default project_id is `"default"` for backwards compatibility
```

### 4.3 Config.py Updates (Both Packages)

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Project namespacing
    project_id: str = Field(
        default="default",
        description="Project identifier for collection namespacing"
    )

    @property
    def sources_collection(self) -> str:
        return f"{self.project_id}_sources"

    @property
    def chunks_collection(self) -> str:
        return f"{self.project_id}_chunks"

    @property
    def extractions_collection(self) -> str:
        return f"{self.project_id}_extractions"
```

### 4.4 Storage Client Updates

**MongoDB (both packages):**
```python
# Before
result = await self.db.sources.insert_one(...)

# After
collection = self.db[settings.sources_collection]
result = await collection.insert_one(...)
```

**Qdrant (both packages):**
```python
# Before
CHUNKS_COLLECTION = "chunks"

# After
# Use settings.chunks_collection directly
```

### 4.5 CLI Script Updates

Add usage documentation:
```bash
# Per-command project selection
PROJECT_ID=ai_engineering uv run scripts/ingest.py book.pdf

# Session-wide project selection
export PROJECT_ID=ai_engineering
uv run scripts/ingest.py book.pdf
uv run scripts/extract.py <source_id>
```

---

## Section 5: Implementation Handoff

### Change Scope Classification

**Minor** - Can be implemented directly by development team.

### Handoff Recipients

| Role | Responsibility |
|------|----------------|
| Dev Agent | Implement code changes in both packages |
| SM Agent | Track refactor progress in sprint-status.yaml |

### Implementation Sequence

1. **Update Pipeline Package First**
   - config.py → mongodb.py → qdrant.py → CLI scripts → tests

2. **Update MCP Server Package**
   - config.py → mongodb.py → qdrant.py → tests

3. **Update Documentation**
   - Architecture.md → Project-context.md → README

### Success Criteria

- [ ] `PROJECT_ID` environment variable configures collection names
- [ ] Collections created as `{project_id}_{type}` (e.g., `ai_engineering_sources`)
- [ ] Existing scripts work with `PROJECT_ID=default` for backwards compatibility
- [ ] Can run ingestion for multiple projects without data mixing
- [ ] Can delete all collections for a project easily
- [ ] MCP server queries correct project collections
- [ ] All tests pass with dynamic collection names

---

## Approval

**Decision:** [ ] Approved  [ ] Approved with changes  [ ] Rejected

**Approved by:** _________________

**Date:** _________________

**Notes:**
_To be filled after review_

---

*Generated by Correct Course Workflow*
