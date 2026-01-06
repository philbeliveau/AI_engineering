# Step 03 Data Engineer: Enhancement Summary

**Date:** 2026-01-06
**Status:** ✅ COMPLETE
**Type:** Knowledge Grounding + Architecture Awareness + Tech Stack Integration

---

## 📋 What Was Changed

Step 03 (Data Engineer) has been comprehensively refactored to align with knowledge-grounding principles from CLAUDE.md and integrate Phase 0 decisions. This matches the approach applied to Step 02 (FTI Architect).

---

## 🔄 Major Changes Summary

### 1. ✅ Fixed Hardcoded Pipeline Options

**Before:**
```markdown
**Option 1: Batch Pipeline**
Sources → Scheduled Extract → Transform → Load → Feature Store
Best for: Static or daily-updated data, cost-sensitive scenarios

**Option 2: Streaming Pipeline**
Sources → Event Stream → Transform → Load → Feature Store
Best for: Real-time requirements, continuous updates

**Option 3: Hybrid Pipeline**
Batch for historical data + Streaming for new data
Best for: Large historical corpus with ongoing updates
```

**After:**
```markdown
**IMPORTANT:** We won't hardcode options. Instead, we'll query the knowledge base for patterns specific to your situation.

Query the Knowledge MCP with your constraints:
Endpoint: search_knowledge
Query: "{architecture} data pipeline {update_pattern} {team_size} {orchestration_tool}"

Examples:
  - "RAG data pipeline daily updates startup ZenML"
  - "fine-tuning streaming real-time training data Airflow enterprise"
```

**Why This Matters:**
- Knowledge base is queried with user's actual context
- Recommendations evolve as knowledge base grows
- No static "Option A/B/C" templates
- Aligns with CLAUDE.md principle: "Never hardcode as 'the answer' - query at runtime"

---

### 2. ✅ Contextualized Knowledge MCP Queries

**Before:**
```
Query 1: "data pipeline feature engineering preprocessing" (generic)
Query 2: Topic: "data quality" (generic)
Query 3: Topic: "data" (too broad)
Query 4: Topic: "data pipeline" (generic)
```

**After:**
```
Query 1 (RAG): "RAG data pipeline {orchestration_tool} {team_size} {data_volume}"
Query 1 (FT): "fine-tuning training data pipeline {orchestration_tool} {scale}"
Query 2 (RAG): get_warnings topic="rag data pipeline"
Query 2 (FT): get_warnings topic="training data quality"
Query 3 (RAG): "{vector_db} data storage format {data_type} RAG pipeline"
Query 4: "{orchestration_tool} data pipeline patterns batch streaming {scale}"
```

**Why This Matters:**
- Each query is contextualized with user's architecture
- Different queries for RAG vs Fine-tuning
- Incorporates tech stack (orchestration tool, vector DB) from Phase 0
- Knowledge base returns context-specific recommendations, not generic guidance

---

### 3. ✅ Added Conditional Architecture-Aware Paths

**New Section: 3. Architecture-Specific Data Pipeline Focus**

Before: Generic data pipeline guidance for all architectures
After: Explicit conditional sections showing different focus areas:

**For RAG:**
```
✓ Document format consistency (PDFs, Markdown, HTML, etc.)
✓ Metadata richness (timestamps, sources, version IDs, authors)
✓ Deduplication strategy (exact + semantic duplicates)
✓ Update frequency handling (live document versions)
✓ Retrieval quality validation (can we find relevant docs?)
```

**For Fine-tuning:**
```
✓ Training example diversity (representative of target distribution)
✓ Label quality and consistency (correct ground truth)
✓ Data leakage prevention (no eval/test data in training)
✓ Example representation (rare cases, edge cases covered)
✓ Computational requirements (total tokens for training)
```

**For Hybrid:**
```
✓ Separation of concerns (document corpus vs training examples)
✓ Overlap handling (deduplicate across pipelines)
✓ Different quality gates for each
✓ Independent versioning
✓ Cost tracking (two pipelines)
```

**Why This Matters:**
- RAG and fine-tuning have fundamentally different data requirements
- Users understand which focus areas matter for their architecture
- Prevents over-engineering for the wrong path

---

### 4. ✅ Integrated Tech Stack from Phase 0

**New Section: Enhanced LOAD CONTEXT**

Added mandatory loading of:
1. **Tech Stack Decision** (orchestration tool, vector DB, tracking tool)
2. **Build vs Buy Decision** (confirm this is a BUILD project, not BUY/API-only)
3. **Architecture Decision** (confirms RAG/FT/Hybrid with implications)

**Why This Matters:**
- Data engineer now has full context before designing
- Knows which orchestration tool will run the pipeline
- Knows which vector DB must ingest the data
- Can design pipeline compatible with tech stack
- Prevents misalignment between Phase 0 and Phase 1

---

### 5. ✅ Architecture-Aware Data Transformation

**Before:**
```
Generic cleaning operations list for all architectures
```

**After:**
```
**For RAG:**
| Operation | Priority | Purpose |
| Deduplication | ⭐⭐⭐ CRITICAL | Prevent redundant retrieval |
| Metadata Extraction | ⭐⭐⭐ CRITICAL | Source, timestamp, version |
| Normalization | ⭐⭐ HIGH | Standardize formats |
| Filtering | ⭐⭐ HIGH | Remove boilerplate |
| Enrichment | ⭐⭐ HIGH | Add context |
| Validation | ⭐ MEDIUM | Completeness check |

**For Fine-tuning:**
| Operation | Priority | Purpose |
| Label Validation | ⭐⭐⭐ CRITICAL | Verify correctness |
| Deduplication | ⭐⭐ HIGH | Prevent overfitting |
| Balance Checking | ⭐⭐ HIGH | No class imbalance |
| Filtering | ⭐⭐ HIGH | Remove corrupted data |
| Normalization | ⭐ MEDIUM | Consistent format |
| Enrichment | ⭐ MEDIUM | Add context |
```

**Why This Matters:**
- Different priorities for different architectures
- RAG needs metadata (retrieval depends on it)
- Fine-tuning needs labels (model learns from them)
- Prevents wasting time on irrelevant operations

---

### 6. ✅ Architecture-Aware Quality Frameworks

**Before:**
```yaml
Generic quality gates for all use cases
quality_gates:
  - name: "Completeness check"
    check: "Required fields >99% populated"
    action_on_fail: "Block pipeline, alert"
```

**After:**
```yaml
quality_gates (RAG-specific):
  - name: "Metadata extraction"
    check: "Source, timestamp, version extracted for 100%"
    action_on_fail: "Block pipeline, review source"

  - name: "Deduplication check"
    check: "No exact or semantic duplicates"
    action_on_fail: "Quarantine duplicates, investigate source"

  - name: "Document integrity"
    check: "No truncated/corrupted documents (100%)"
    action_on_fail: "Block pipeline, fix parser"

quality_gates (Fine-tuning-specific):
  - name: "Label validation"
    check: "Labels match guidelines (100% sample verified)"
    action_on_fail: "Block pipeline, review labeling"

  - name: "Leakage prevention"
    check: "No eval/test data in training (>99%)"
    action_on_fail: "Block pipeline, segregate data"
```

**Why This Matters:**
- Quality gates reflect what matters for each architecture
- RAG cares about metadata completeness
- Fine-tuning cares about label correctness and data isolation
- Prevents false positives/negatives in quality validation

---

### 7. ✅ Added Semantic Caching Decision (NEW)

**New Section: 7. Semantic Caching Decision**

For RAG systems with high data volume (>10GB):

```markdown
Query Knowledge MCP:
Endpoint: search_knowledge
Query: "semantic caching RAG optimization {data_volume} {query_frequency}"

Decision Matrix:
| Factor | Supports Caching | Supports No Cache |
| Data volume | >50GB (cost matters) | <50GB (cost not critical) |
| Query volume | High (many similar) | Low (unique queries) |
| Latency SLA | Relaxed (seconds OK) | Strict (milliseconds) |
| Budget | Limited (need cost reduction) | Generous |
| Data freshness | Acceptable delays | Must be real-time |

Decision:
- "Yes, implement caching" → Adds complexity, saves cost
- "No caching" → Simpler pipeline, higher cost
- "Evaluate later" → Start without, add if costs spike
```

**Why This Matters:**
- Introduces optimization pattern from knowledge base
- Prevents over-engineering (caching not needed for small volumes)
- Prevents under-optimization (caching could save significant cost)
- Explicit trade-off analysis

---

### 8. ✅ Surfaced Anti-Patterns & Knowledge Warnings (NEW)

**New Section: 8. Surface RAG Anti-Patterns & Data Pipeline Warnings**

Queries knowledge base for warnings and surfaces common pitfalls:

**RAG Anti-Patterns:**
1. Missing/incomplete metadata → retrieval fails → hallucination
2. Poor deduplication → same info multiple times → confusion
3. No document versioning → stale data → contradictions
4. Incomplete PDF extraction → partial results → misleading
5. Boilerplate noise → wasted tokens → poor responses
6. No retrieval validation → discovered late → too late

**Fine-tuning Anti-Patterns:**
1. Unvalidated labels → wrong learning → poor generalization
2. Eval data leaking to training → false metrics → poor test performance
3. Class imbalance → majority class bias → poor minority performance
4. Overfitting on small data → memorization → no generalization

**Why This Matters:**
- Surfaces common mistakes BEFORE they happen
- Users understand risks specific to their architecture
- Prevention strategies documented
- Aligns with "warnings" extraction type from knowledge base (337 warnings available)

---

### 9. ✅ Added Data Storage & Vector DB Specification (NEW)

**New Section: 9. Data Storage & Vector DB Specification (IF RAG)**

For RAG systems, specifies where data goes before embedding:

```markdown
Load from Phase 0:
- Vector DB chosen: {vector_db}
- Data volume: {estimated_volume}
- Update frequency: {update_frequency}

Query Knowledge MCP for DB-specific patterns:
Query: "{vector_db} data storage format ingestion {data_type}"

Data specification to document:
| Aspect | Specification |
| Format | [JSON, Parquet, CSV, documents] |
| Schema | [Fields: content, metadata.source, metadata.timestamp] |
| Serialization | [How documents are serialized] |
| Indexing | [What fields are indexed] |
| Storage location | [Cloud path, database URL] |
| Retention policy | [How long kept, versioning] |
| Access control | [Who can read/write, encryption] |
```

**Why This Matters:**
- Data Engineer understands downstream requirements
- Ensures compatibility with chosen vector DB
- Prevents format incompatibility issues
- Embeddings Engineer has everything needed to ingest

---

### 10. ✅ Tech-Stack-Aware Story Generation

**Before:**
```yaml
- id: "DATA-S01"
  title: "Set up data source connections"
  description: "Configure access to all identified data sources"
  acceptance_criteria:
    - "All source connections tested and working"
    - "Credentials securely stored"
```

**After:**
```yaml
- id: "DATA-S01"
  title: "Set up data source connections"
  description: "Configure access to all identified data sources using {orchestration_tool}"
  acceptance_criteria:
    - "All source connections tested and working"
    - "Credentials securely stored in {orchestration_tool} secrets"
    - "Connection retry logic implemented with exponential backoff"
    - "Connection tests pass for all sources"

- id: "DATA-S05"
  title: "Set up data storage and schema"
  description: "[If RAG] Prepare data format compatible with {vector_db} ingestion"
  acceptance_criteria:
    - "[If RAG] Data schema compatible with {vector_db}"
    - "[If RAG] Storage location configured and access tested"
    - "[If RAG] Sample data successfully stored"
    - "[If RAG] Retention and versioning policies documented"

- id: "DATA-S06"
  title: "Validate end-to-end pipeline"
  description: "Run complete pipeline end-to-end with test data"
  acceptance_criteria:
    - "[If RAG] Data ready for Embeddings Engineer (Step 4)"
    - "[If FT] Data ready for Training Specialist (Step 5)"
```

**Why This Matters:**
- Stories reference actual orchestration tool (ZenML, Airflow, etc.)
- Stories reference vector DB choice (Qdrant, Pinecone, etc.)
- Architecture-specific acceptance criteria
- Downstream step expectations are clear

---

### 11. ✅ Added Menu Option [Q] for Re-Querying

**Before:**
```
[A] Analyze pipeline further
[P] View progress
[C] Continue to Step 4
```

**After:**
```
[A] Analyze pipeline further
[Q] Re-query knowledge base with different constraints
[P] View progress
[C] Continue to Step 4
```

**Why This Matters:**
- Users can explore different trade-offs
- If constraints change, can re-query and get different recommendations
- Knowledge base grows → re-querying gets better results over time
- Matches approach from Step 02

---

### 12. ✅ Enhanced Success/Failure Metrics

**Before:**
Simple checklist of ~10 items

**After:**
Comprehensive checklist with categories:
- Context Loading (4 items)
- Knowledge Grounding (5 items)
- Architecture-Aware Design (4 items)
- Data Pipeline Design (4 items)
- Optimization & Risk Management (4 items)
- Documentation (4 items)
- Completion (3 items)

Plus detailed failure metrics with 20+ critical blockers

**Why This Matters:**
- Clear success criteria that prevent mistakes
- Mirrors Step 02 approach
- Helps agents understand what "done" looks like
- Highlights critical areas that can't be skipped

---

### 13. ✅ Enhanced Data Engineer Agent

**Updated agent file: `agents/data-engineer.md`**

**Enhanced Identity:**
Added:
- "Understands architecture implications - RAG pipelines need different focus than fine-tuning"
- "Knowledge-grounded - queries knowledge base for patterns specific to user's context"
- "Tech-stack aware - designs pipelines compatible with orchestration tool and vector DB from Phase 0"
- "Risk-conscious - surfaces common pitfalls and anti-patterns"

**Enhanced Expertise:**
Added domains:
- RAG-specific data requirements
- Fine-tuning data requirements
- Orchestration tool integration patterns
- Vector database compatibility
- Semantic caching optimization

**Enhanced Activation Instructions:**
Added:
- Load tech-stack-decision.md
- Load build-vs-buy decision
- Tailor pipeline to RAG vs FT vs Hybrid
- Use contextualized Knowledge MCP queries
- Surface architecture-specific anti-patterns
- Design stories with tech stack references

**Enhanced Outputs:**
Added:
- Architecture-specific pipeline design
- Semantic caching decision (if applicable)
- Vector DB data format specification
- Implementation stories with tech stack references
- Data pipeline specification with rationale

**Enhanced Handoff:**
Now specifies:
- Conditional routing (Step 4 if RAG, Step 5 if FT)
- Complete data pipeline design artifacts
- Anti-patterns acknowledged
- Tech stack context preserved

---

## 📊 Section Restructuring

### Old Flow (12 sections):
1. Welcome
2. Query Knowledge MCP (generic)
3. Data Source Inventory
4. Extraction Pipeline Design (hardcoded options)
5. Data Transformation (generic)
6. Data Quality Framework (generic)
7. Document Decisions
8. Generate Stories
9. Menu
10. Completion Note
11. Success/Failure Metrics

### New Flow (12 sections, restructured):
1. Welcome
2. Query Knowledge MCP (contextualized, architecture-aware)
3. Architecture-Specific Data Pipeline Focus (NEW)
4. Data Source Inventory (architecture-aware)
5. Extraction Pipeline Design (dynamic queries, no hardcoding)
6. Data Transformation Design (architecture-aware priorities)
7. Semantic Caching Decision (NEW, if applicable)
8. Surface Anti-Patterns & Warnings (NEW)
9. Data Storage & Vector DB Spec (NEW, if RAG)
10. Document Decisions
11. Generate Stories (tech-stack aware)
12. Menu (with [Q] option)

---

## 🔗 Knowledge Base Integration

### Queries Grounded in KB Content:

**RAG Patterns Available (636 total):**
- 42 data collection workflows
- 176 RAG decisions
- 129 RAG warnings
- Multiple semantic caching patterns
- Retrieval optimization patterns

**Fine-tuning Content (338 total):**
- 54 training workflows
- 180 fine-tuning decisions
- Training data quality patterns

**Orchestration & Tools (110+ total):**
- ZenML patterns (54 extractions)
- Airflow patterns (6 extractions)
- Vector DB patterns (available for Qdrant, Pinecone, Weaviate)

---

## ✅ Verification Checklist

Step 03 now includes:
- ✅ Tech stack integration (Phase 0 decisions loaded)
- ✅ Architecture-aware design (RAG vs FT vs Hybrid)
- ✅ Knowledge-grounded queries (contextualized, not generic)
- ✅ Hardcoding removed (dynamic queries instead)
- ✅ Conditional paths (different flows for different architectures)
- ✅ Anti-pattern warnings (surfaced before proceeding)
- ✅ Semantic caching decision (optimization consideration)
- ✅ Vector DB specification (IF RAG)
- ✅ Tech-stack-aware stories (orchestration tool references)
- ✅ [Q] menu option (re-query with different constraints)
- ✅ Comprehensive success criteria (20+ items)
- ✅ Enhanced agent persona (knowledge-grounded, architecture-aware)

---

## 🎯 Principles Enforced

**Knowledge Grounding (from CLAUDE.md):**
✅ Reference knowledge PATTERNS, not copy-paste
✅ Query at RUNTIME with user context
✅ Show SYNTHESIS approach (HOW to apply knowledge)

**Architecture Awareness:**
✅ Different pipelines for RAG vs FT vs Hybrid
✅ Architecture-specific quality gates
✅ Architecture-specific transformation priorities

**Tech Stack Integration:**
✅ Load decisions from Phase 0
✅ Design compatible with orchestration tool
✅ Ensure vector DB compatibility

**Risk Management:**
✅ Surface anti-patterns before proceeding
✅ Semantic caching decision for optimization
✅ Prevention strategies documented

---

## 📁 Files Modified

1. **`step-03-data-engineer.md`**
   - 12 comprehensive sections (restructured)
   - 1000+ lines of guidance
   - Architecture-aware content throughout
   - Knowledge-grounded queries
   - Removed all hardcoded options

2. **`agents/data-engineer.md`**
   - Enhanced identity (architecture-aware, knowledge-grounded)
   - Enhanced expertise (RAG, FT, orchestration, vector DB)
   - Enhanced activation instructions
   - Enhanced outputs and handoff
   - New knowledge grounding section

---

## 🔄 Consistency with Step 02

This refactoring of Step 03 uses the **same patterns and principles** applied to Step 02 (FTI Architect):

| Principle | Step 02 | Step 03 |
|-----------|---------|---------|
| Hardcoded options | ❌ Fixed | ✅ Fixed |
| Generic queries | ❌ Fixed | ✅ Fixed |
| Tech stack integration | ✅ Integrated | ✅ Integrated |
| Architecture awareness | ✅ Added | ✅ Added |
| Anti-pattern warnings | ✅ Added | ✅ Added |
| [Q] re-query option | ✅ Added | ✅ Added |
| Enhanced agent | ✅ Updated | ✅ Updated |
| Comprehensive success criteria | ✅ Added | ✅ Added |

**Next steps:** Apply same pattern to Steps 04-09

---

## 🎓 Why This Matters

**Before (Gap):**
- Step 03 was generic ETL/ELT guidance
- Didn't know which architecture (RAG vs FT)
- Didn't know which tech stack (orchestration, vector DB)
- Didn't surface architecture-specific risks
- Had hardcoded "Batch/Streaming/Hybrid" options

**After (Knowledge-Grounded):**
- Step 03 is context-aware data engineering
- Explicitly tailored to RAG vs FT vs Hybrid
- Integrated with Phase 0 tech stack decisions
- Surfaces architecture-specific anti-patterns
- Knowledge base drives recommendations, not hardcoded templates

**Impact:**
- Users get data pipelines designed for their actual situation
- Prevents common mistakes specific to their architecture
- Ensures compatibility with tech stack chosen in Phase 0
- Knowledge base growth automatically improves recommendations

---

*Enhancement Complete: 2026-01-06*
*Pattern Aligned with Step 02 Knowledge-Grounding Approach*
*Ready for Steps 04-09 Application*
