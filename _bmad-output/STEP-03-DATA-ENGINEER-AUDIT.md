# Step 03 Data Engineer: Knowledge Integration Audit

**Date:** 2026-01-06
**Status:** AUDIT COMPLETE - GAPS IDENTIFIED
**Comparison:** Similar exercise as Step 02 (FTI Architect)

---

## 📊 EXECUTIVE SUMMARY

### Current State of Step 03
Step 03 (Data Engineer) has solid **structural workflow** with sections for:
- Data source inventory ✓
- Extraction pipeline design ✓
- Transformation operations ✓
- Quality framework ✓
- Story generation ✓

### Critical Gaps Identified
- ❌ **Hardcoded pipeline options** (Batch/Streaming/Hybrid) without knowledge grounding
- ❌ **Static Knowledge MCP queries** (not contextualized with architecture or constraints)
- ❌ **Missing conditional paths** (different flows for RAG vs Fine-tuning vs Hybrid)
- ❌ **No tech stack integration** (doesn't reference orchestration tools from Phase 0)
- ❌ **Missing RAG-specific data pipeline patterns** (despite strong RAG coverage in KB)
- ❌ **Missing semantic caching decision** (optimization pattern not surfaced)
- ❌ **Generic data quality framework** (not grounded in knowledge warnings)
- ❌ **Missing anti-patterns** (RAG pitfalls specific to data pipeline stage)

---

## 🔍 DETAILED GAP ANALYSIS

### Gap 1: Hardcoded Pipeline Architecture Options (Lines 213-231)

**Current Code:**
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

Ask: "Based on your update patterns, which architecture fits best?"
```

**Problem:** This is a HARDCODED TEMPLATE, not a knowledge-grounded recommendation.

**What Knowledge Base Has:**
- 42 data collection workflows
- Multiple RAG pipeline patterns (IDs: 695be858d66d1f78593b23b9, 695be859d66d1f78593b23bc)
- 176 RAG decisions
- Semantic caching patterns (IDs: 69596ba2eb005e20ace7ecaf)

**Fix Pattern (Similar to Step 02 Correction):**
```markdown
### Query Knowledge MCP for Pipeline Architecture

Based on your data characteristics, we'll query knowledge for guidance:

**Query Pattern: Data Pipeline Architecture**
Endpoint: search_knowledge
Query (contextualized): "[Architecture: {user_architecture}] + [Volume: {data_volume}] + [Update Frequency: {frequency}] + [Requirements: {latency_requirements}]"

Examples:
- "RAG pipeline batch processing large document corpus"
- "fine-tuning streaming real-time training data"
- "hybrid RAG+FT continuous updates with historical data"
```

**Knowledge-Grounded Approach:**
- Query with user's specific architecture from Phase 0
- Query with their data constraints
- Knowledge base returns RAG-specific patterns vs Fine-tuning patterns
- Surface trade-offs from extracted decisions

---

### Gap 2: Static Knowledge MCP Queries (Lines 124-146)

**Current Queries:**
```
Query 1: "data pipeline feature engineering preprocessing"
Query 2: Topic: "data quality"
Query 3: Topic: "data"
Query 4: Topic: "data pipeline"
```

**Problems:**
1. Generic/too broad - not contextualized with user's architecture
2. Not leveraging that they already made BUILD/BUY and ARCHITECTURE decisions in Phase 0
3. Queries don't specify RAG vs Fine-tuning constraints
4. Don't reference tech stack choices for orchestration tool

**What's Missing:**
Should have **CONDITIONAL QUERIES** based on:
- Architecture choice from Phase 0 (RAG vs FT vs Hybrid)
- Build vs Buy decision (different data pipelines for API-only vs custom)
- Tech stack orchestration tool chosen (different patterns for Airflow vs ZenML)

**Example Dynamic Query Pattern:**
```
If RAG:
  "RAG data pipeline patterns with [orchestration_tool] [team_size] constraints"
If Fine-tuning:
  "fine-tuning data pipeline workflows [orchestration_tool] distributed training"
If Hybrid:
  "hybrid RAG fine-tuning data collection strategy"
```

---

### Gap 3: Missing Conditional Paths (Architecture-Aware)

**Current Issue:**
Step 03 treats all architectures the same. But RAG vs Fine-tuning vs Hybrid have VERY different data pipeline concerns:

| Concern | RAG | Fine-tuning | Hybrid |
|---------|-----|-------------|--------|
| **Document Format** | Critical (retrieval) | May vary (training) | Both matter |
| **Deduplication** | Exact + semantic | Minimal (diversity) | Both strategies |
| **Versioning** | Ongoing (live docs) | Fixed (training set) | Different strategies |
| **Quality Gates** | Retrieval precision | Training diversity | Dual gates |
| **Semantic Caching** | Highly relevant | Not applicable | Partial |

**What's Missing:**
Section 3 should branch:
```
### 3. Data Source Inventory [CONDITIONAL ON ARCHITECTURE]

If RAG:
  - Focus on document format consistency
  - Emphasize metadata for retrieval (timestamps, sources)
  - Plan for versioning/updates

If Fine-tuning:
  - Focus on example diversity
  - Emphasize label quality
  - Plan for fixed training set

If Hybrid:
  - Design dual pipelines (retrieval docs + training examples)
  - Different quality gates for each
```

---

### Gap 4: No Tech Stack Integration

**Current Issue:**
Step 03 doesn't reference the `tech-stack-decision.md` created in Phase 0.

**What's Missing:**
After loading context, should load and reference:
```yaml
# Load from Phase 0
tech_stack_decision.orchestration  # e.g., "ZenML" or "Airflow"
tech_stack_decision.vector_db      # e.g., "Qdrant" or "Pinecone"
```

Then use this context in queries:
```
"RAG data pipeline with ZenML orchestration for small team"
(not just "data pipeline" generically)
```

**Why It Matters:**
- ZenML vs Airflow have different data pipeline patterns
- Vector DB choice affects data format/transformation steps
- Orchestration tool determines batch/streaming/hybrid feasibility

---

### Gap 5: Missing RAG-Specific Data Pipeline Patterns

**Knowledge Base Has:**
- 636 RAG extractions
- 176 RAG decisions
- 129 RAG warnings (anti-patterns!)
- Specific RAG workflow patterns

**Currently Step 03:**
- Generic data pipeline guidance
- No mention of RAG concerns (retrieval quality, metadata, versioning)

**Example RAG-Specific Patterns to Surface:**
1. **Semantic Caching** (ID: 69596ba2eb005e20ace7ecaf)
   - Surface when data volume is high
   - Trade-off: latency vs cost

2. **Retrieval Quality** patterns
   - What metadata matters for retrieval?
   - How to validate retrieval precision early?
   - When to do semantic chunking vs size chunking?

3. **Document Versioning**
   - How to handle document updates?
   - When to re-index?
   - How to track lineage?

4. **RAG Anti-Patterns** (129 warnings)
   - Missing metadata
   - Poor chunking strategy
   - No retrieval validation
   - Stale data pipeline

---

### Gap 6: Generic Data Quality Framework

**Current (Lines 273-307):**
```yaml
quality_gates:
  extraction:
    - name: "Source connectivity"
  transformation:
    - name: "Schema validation"
  output:
    - name: "Completeness check"
```

**Problem:**
Generic quality gates, not grounded in knowledge warnings about data pipeline pitfalls.

**What Knowledge Base Says:**
- 337 warnings about data/training/inference issues
- 129 specific RAG warnings
- Patterns for data validation in RAG systems

**Should Be:**
Different quality gates for RAG vs Fine-tuning:

```
If RAG:
  - Retrieval metadata completeness (source, timestamp, version)
  - Document format consistency
  - No low-quality or incomplete chunks

If Fine-tuning:
  - Label accuracy and consistency
  - Training example diversity
  - No data leakage to evaluation set
```

---

### Gap 7: Missing Semantic Caching Decision

**Knowledge Has:**
- ID: 69596ba2eb005e20ace7ecaf - "Semantic Caching"
- Multiple caching optimization patterns

**Currently:**
No mention of semantic caching in Step 03.

**Should Be Added:**
New section after pipeline architecture decision:

```markdown
### Optimization Consideration: Semantic Caching

For RAG systems with high data volume:

Query: "semantic caching RAG [data_volume] [budget_constraints]"

Trade-off:
- Reduces embedding cost (cached semantically similar queries)
- Adds latency (similarity matching before vector DB lookup)
- Useful when: Large document corpus + repeated similar queries
- Not useful when: Real-time requirements, rapidly changing data
```

---

### Gap 8: Missing Anti-Pattern Warnings

**What Step 03 Currently Does:**
Generic workflow, no warnings about common pitfalls.

**What Knowledge Base Offers:**
- 129 RAG-specific warnings
- 337 total data/training warnings
- Extraction-specific pitfalls
- Transformation mistakes

**Should Surface:**
At start of each section:

```markdown
⚠️ **Common Data Pipeline Pitfalls (from knowledge base):**

In RAG systems:
- Insufficient metadata captured → retrieval fails
- Poor deduplication strategy → hallucination amplification
- No versioning for document updates → stale responses
- Skipping quality validation → garbage in, garbage out

Before proceeding, ask: "Are you aware of these risks?"
```

---

## 🎯 RECOMMENDED CHANGES TO STEP 03

### Priority 1: CRITICAL (Mirrors Step 02 Fixes)

1. **Replace hardcoded options with dynamic queries**
   - Lines 213-231: Rewrite extraction pipeline architecture section
   - Use knowledge MCP contextualized queries instead
   - Add [Q] menu option to re-query with different constraints

2. **Add conditional paths based on architecture**
   - Data source inventory differs for RAG vs FT
   - Transformation operations differ
   - Quality gates differ
   - Add conditional sections marked "Only if RAG", "Only if FT", "If Hybrid"

3. **Integrate tech stack from Phase 0**
   - Load tech-stack-decision.md
   - Reference orchestration tool in queries
   - Acknowledge vector DB choice in transformation section

### Priority 2: HIGH

4. **Add semantic caching decision**
   - New section after pipeline architecture
   - Query knowledge for caching patterns
   - Present trade-off analysis

5. **Surface RAG-specific anti-patterns**
   - Add warnings section referencing knowledge base
   - Highlight common RAG data pipeline mistakes
   - Ask user to confirm they understand before proceeding

6. **Make quality gates knowledge-grounded**
   - Different thresholds for RAG vs FT
   - Use warnings from knowledge base
   - Surface criticality of metadata for retrieval

### Priority 3: MEDIUM

7. **Add data storage specification**
   - Reference vector DB choice from tech stack
   - Specify data format expectations
   - Add schema validation details

8. **Enhance story generation**
   - Stories should reference orchestration tool
   - Stories should account for architecture-specific tasks
   - Add stories for data quality monitoring (Phase 5 handoff)

---

## 📋 SPECIFIC KNOWLEDGE BASE ITEMS TO INTEGRATE

### Must-Query Items:
```
1. RAG Pipeline Patterns
   ID: 695be858d66d1f78593b23b9 - "Retrieval Augmented Generation (RAG) Pipeline"
   ID: 695be858d66d1f78593b23ba - "Concatenative Retrieval for RAG"
   ID: 695be859d66d1f78593b23bc - "Iterative/Agentic RAG"

2. Data Collection Workflows
   - 42 available workflows for data collection
   - Query: "data collection workflow [architecture]"

3. Semantic Caching
   ID: 69596ba2eb005e20ace7ecaf - "Semantic Caching"
   ID: 69596ba2eb005e20ace7ecb9 - "Semantic Caching"

4. RAG Warnings (129 total)
   - Query: "get_warnings topic=rag" → Anti-patterns
   - Surface before proceeding

5. Embedding Pipeline Patterns
   ID: 695c3c687909f0f2702ef1b3 - "Storing data in Qdrant"
   ID: 695c3c5d7909f0f2702ef187 - "LLM Twin Data Collection Workflow"

6. Training Data Collection (if hybrid)
   ID: 695bf6bf8b4ecee92efe83e9 - "Dataset Generation Workflow"
   ID: 695bf6be8b4ecee92efe83e6 - "Data Collecting Workflow"
```

### Query Patterns to Implement:

```markdown
# Query 1: Architecture-Specific Data Pipeline (CONDITIONAL)
If RAG:
  search_knowledge("RAG data pipeline [orchestration_tool] [team_size]")
If FT:
  search_knowledge("fine-tuning training data pipeline [orchestration_tool]")
If Hybrid:
  search_knowledge("hybrid RAG fine-tuning data collection")

# Query 2: Data Quality Patterns
get_warnings(topic="rag_data_pipeline")
get_warnings(topic="training_data_quality")

# Query 3: Semantic Caching (if RAG with volume > 10GB)
If applicable:
  search_knowledge("semantic caching RAG optimization [budget]")

# Query 4: Data Storage & Format
If RAG:
  search_knowledge("Qdrant vector storage data format [data_type]")
If FT:
  search_knowledge("training data storage distributed [orchestration_tool]")
```

---

## 🔄 WORKFLOW RESTRUCTURING

### Current Flow:
```
1. Welcome
2. Query Knowledge MCP (generic)
3. Data Source Inventory
4. Extraction Pipeline Design
5. Data Transformation
6. Quality Framework
7. Document Decisions
8. Generate Stories
9. Menu
```

### Recommended New Flow:
```
1. Welcome
2. Load Phase 0 Context (Architecture, Tech Stack)
3. Query Knowledge MCP (CONDITIONAL ON ARCHITECTURE)
   - If RAG: Query RAG data pipeline patterns
   - If FT: Query training data collection
   - If Hybrid: Both
4. Data Source Inventory (CONDITIONAL - different focus)
5. Extraction Pipeline Design (dynamic queries, not hardcoded)
   - Includes semantic caching decision
   - References orchestration tool from tech stack
6. Data Transformation (architecture-specific operations)
7. Quality Framework (conditional thresholds)
8. Data Storage Specification (NEW - vector DB integration)
9. Surface Warnings (RAG anti-patterns if applicable)
10. Document Decisions
11. Generate Stories
12. Menu
```

---

## ✅ SUCCESS CRITERIA FOR UPDATED STEP 03

- [ ] Load tech-stack-decision.md from Phase 0
- [ ] Load architecture decision from Phase 0
- [ ] Knowledge MCP queries are contextualized (not generic)
- [ ] Conditional sections for RAG vs FT vs Hybrid
- [ ] No hardcoded pipeline options (use knowledge instead)
- [ ] Semantic caching decision if RAG + volume > threshold
- [ ] RAG-specific anti-patterns surfaced before proceeding
- [ ] Quality gates differentiated by architecture
- [ ] Data storage specification references vector DB choice
- [ ] Stories include tech stack context (orchestration tool)
- [ ] Menu includes [Q] option to re-query with different constraints

---

## 📁 FILES TO MODIFY

1. **`step-03-data-engineer.md`** - Core step file
   - Restructure sections (add conditional paths)
   - Replace hardcoded options with dynamic queries
   - Add semantic caching decision
   - Add anti-pattern warnings
   - Integrate tech stack from Phase 0
   - Update story generation

2. **`agents/data-engineer.md`** - Agent persona
   - Enhance identity for knowledge-grounded decisions
   - Add expertise in RAG-specific data pipelines
   - Add expertise in tech stack integration

---

## 📊 IMPACT ANALYSIS

### Similarities to Step 02 Fixes:
- **Hardcoded options** → Same issue, same solution
- **Static queries** → Same issue, same solution
- **Missing context integration** → Same issue, same solution

### Step 03 Specific Issues:
- **Conditional architecture paths** → More critical here (RAG vs FT very different)
- **Tech stack integration** → New (Phase 0 → Phase 1 linkage)
- **Semantic caching** → Optimization pattern specific to high-volume RAG

### Why This Matters:
Step 03 is the **DATA FOUNDATION** for entire project:
- RAG projects need retrieval-ready data (metadata critical)
- Fine-tuning projects need diversity (different quality gates)
- Hybrid needs both (dual pipelines)

Getting this wrong cascades to Phases 2-5. Knowledge base has strong RAG coverage - should use it.

---

## 🎓 KNOWLEDGE GROUNDING PRINCIPLES (From CLAUDE.md)

Step 03 currently violates these:

❌ **"NEVER hardcode specific values as 'the answer'"** - Batch/Streaming/Hybrid are hardcoded

❌ **"Query at RUNTIME"** - Queries are static, not contextualized with user's actual data

❌ **"Show SYNTHESIS approach"** - Generic guidance, not teaching HOW to apply knowledge to their situation

✅ **Once fixed**, Step 03 will embody all three principles:
- Reference knowledge PATTERNS for pipeline architecture
- Query at RUNTIME with user's constraints
- Show SYNTHESIS of architecture choice → data pipeline implications

---

**Recommendation**: Proceed with Priority 1 changes to align Step 03 with the knowledge-grounding fixes made to Step 02. The fixes are similar in nature and will significantly improve the workflow's contextual intelligence.

*Analysis complete: 2026-01-06*
