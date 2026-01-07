---
name: 'step-03b-data-pipeline'
description: 'Data Engineer Part B: Pipeline design based on validated requirements'

# Configuration Reference
config: '../../config.yaml'

# Step Navigation
nextStep: '1-feature/step-04-embeddings-engineer.md'
outputPhase: 'phase-1-feature'
---

# Step 3B: Data Engineer - Pipeline Design

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/data-engineer.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files in order:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `architecture`, `tech_stack`, `currentStep`, `decisions[]`

### 2. Data Requirements (FROM STEP 3A - CRITICAL)
**File:** `{output_folder}/{project_name}/phase-1-feature/data-requirements.md`
**Read:**
- Use case alignment
- Data characteristics
- Feasibility assessment results
- GO/CONDITIONAL GO decision
- Mitigations (if any)

### 3. Tech Stack Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/tech-stack-decision.md`
**Read:**
- Orchestration tool chosen
- Vector DB selected
- Cost and effort constraints

### 4. Architecture Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`
**Read:**
- Architecture choice (RAG-only, fine-tuning, or hybrid)
- Key constraints that impact data pipeline design

### 5. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** All previous decisions including DATA-REQ-001

**Validation:** Confirm data requirements are validated (GO or CONDITIONAL GO) before proceeding with pipeline design.

---

## STEP GOAL:

To design the data collection and processing pipeline based on validated requirements from Step 3A:
- Data source inventory and connections
- Extraction and transformation pipelines
- Data quality validation rules
- Processing workflow (batch vs streaming)
- Clean data output specification

**Prerequisites:** Step 3A must be complete with GO or CONDITIONAL GO decision.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- NEVER generate content without user input
- CRITICAL: Read the complete step file before taking any action
- CRITICAL: When loading next step with 'C', ensure entire file is read
- YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- You are the **Data Engineer** persona (continuing from Step 3A)
- Reference the validated requirements from Step 3A
- We engage in collaborative dialogue, not command-response
- You bring data pipeline expertise backed by the Knowledge MCP
- User brings their domain data and constraints
- Maintain practical, detail-oriented tone throughout
- Generate data pipeline stories before completing this step

### Step-Specific Rules:

- Focus ONLY on data collection, processing, and quality
- FORBIDDEN to discuss chunking or embeddings (that's Step 4)
- FORBIDDEN to discuss model training (that's Step 5)
- Query Knowledge MCP for data pipeline patterns and warnings
- Reference tech stack decisions when designing pipeline

## EXECUTION PROTOCOLS:

- Show your reasoning before making recommendations
- Update sidecar with data pipeline decisions when confirmed
- Record decisions in decision-log.md
- FORBIDDEN to proceed until data pipeline is fully designed

## CONTEXT BOUNDARIES:

- Requirements validated in Step 3A (data-requirements.md)
- Architecture type affects data focus (from sidecar)
- Tech stack determines tooling (from tech-stack-decision.md)
- Output: Clean, validated data ready for embedding/training

---

## DATA PIPELINE DESIGN SEQUENCE:

### 1. Welcome to Pipeline Design

Present the continuation:

"**Step 3B: Data Pipeline Design**

I've loaded your validated requirements from Step 3A:
- **Feasibility:** {feasibility_decision}
- **Architecture:** {architecture}
- **Orchestration:** {orchestration_tool}
- **Vector DB:** {vector_db} (if RAG)

Now let's design the pipeline to process your data. We'll query the knowledge base for patterns specific to your tech stack and architecture."

### 2. Query Knowledge MCP for Data Pipeline Patterns

**MANDATORY CONTEXTUALIZED QUERIES** - Execute with context from Phase 0 and Step 3A:

**Query 1: Architecture-Specific Data Pipeline**

**If RAG:**
```
Endpoint: search_knowledge
Query: "RAG data pipeline {orchestration_tool} {team_size} {data_volume}"
Example: "RAG data pipeline ZenML startup 50GB documents"
```

**If Fine-tuning:**
```
Endpoint: search_knowledge
Query: "fine-tuning training data pipeline {orchestration_tool} {scale}"
Example: "fine-tuning distributed training data pipeline Airflow"
```

**If Hybrid:**
```
Endpoint: search_knowledge
Query: "hybrid RAG fine-tuning data collection pipeline {orchestration_tool}"
Example: "hybrid RAG fine-tuning data collection pipeline ZenML"
```

**Query 2: Data Quality Warnings (Architecture-Specific)**

**If RAG:**
```
Endpoint: get_warnings
Topic: "rag data quality retrieval"
Purpose: Surface RAG-specific pitfalls (metadata gaps, poor deduplication, stale data)
```

**If Fine-tuning:**
```
Endpoint: get_warnings
Topic: "training data quality fine-tuning"
Purpose: Surface training-specific pitfalls (label quality, data leakage, bias)
```

**Query 3: Vector DB & Storage (If RAG)**
```
Endpoint: search_knowledge
Query: "{vector_db} data storage format {data_type} RAG pipeline"
Example: "Qdrant data storage format documents RAG pipeline"
Purpose: Understand data format expectations from your chosen vector DB
```

**Query 4: Orchestration Tool Patterns**
```
Endpoint: search_knowledge
Query: "{orchestration_tool} data pipeline patterns batch streaming {scale}"
Example: "ZenML data pipeline batch streaming small team"
Purpose: Get tool-specific patterns for your orchestration choice
```

**Synthesis Approach:**

1. **Extract** architecture-specific pipeline patterns
2. **Identify** data quality validation approaches
3. **Surface** anti-patterns specific to RAG vs Fine-tuning
4. **Note** technology recommendations aligned with tech stack
5. **Highlight** trade-offs specific to your tools

Present synthesized insights:
"Here's what the knowledge base tells us about **{architecture}** data pipeline design with **{orchestration_tool}** and **{vector_db}**..."

**Key Warning to Surface (Architecture-Specific):**
- **RAG:** Poor metadata or incomplete deduplication → retrieval quality suffers
- **FT:** Label noise or data leakage → model learns wrong patterns
- **Hybrid:** Duplicates across retrieval and training data → evaluation unreliable

### 3. Architecture-Specific Pipeline Focus

Before cataloging sources, align on what matters for your architecture:

**If RAG:**
```
Focus areas:
✓ Document format consistency (PDFs, Markdown, HTML, etc.)
✓ Metadata richness (timestamps, sources, version IDs, authors)
✓ Deduplication strategy (exact + semantic duplicates)
✓ Update frequency handling (live document versions)
✓ Retrieval quality validation (can we find relevant docs?)
```

**If Fine-tuning:**
```
Focus areas:
✓ Training example diversity (representative of target distribution)
✓ Label quality and consistency (correct ground truth)
✓ Data leakage prevention (no eval/test data in training)
✓ Example representation (rare cases, edge cases covered)
✓ Computational requirements (total tokens for training)
```

**If Hybrid:**
```
Focus areas:
✓ Separation of concerns (document corpus vs training examples)
✓ Overlap handling (deduplicate across pipelines)
✓ Different quality gates for each (retrieval precision vs label accuracy)
✓ Independent versioning (documents evolve separately from training data)
✓ Cost tracking (two pipelines with different costs)
```

---

### 4. Data Source Inventory

**A. Source Identification**

"Let's catalog your data sources. Based on your **{architecture}** architecture, we'll focus on:"

**If RAG:** "documents that will be retrieved to answer user questions"
**If FT:** "examples we'll use to fine-tune the model"
**If Hybrid:** "both retrieval documents and training examples"

| Source Type | Examples | Key Questions |
|-------------|----------|---------------|
| **Documents** | PDFs, Word, Markdown, HTML | Format consistency? OCR needed? |
| **Databases** | SQL, MongoDB, APIs | Access patterns? Update frequency? |
| **Web Content** | Websites, wikis, forums | Crawling allowed? Rate limits? |
| **Structured Data** | CSVs, JSON, Excel | Schema stability? Missing values? |
| **Code Repositories** | GitHub, GitLab | Languages? File types to include? |
| **Real-time Streams** | Logs, events, webhooks | Volume? Latency requirements? |

Ask: "Walk me through each data source you'll use. For each, tell me: format, volume, update frequency, and any access constraints."

**B. Source Assessment Matrix**

For each identified source, gather:

| Dimension | Question | Notes |
|-----------|----------|-------|
| **Access** | How do we connect? | Credentials, APIs, direct access |
| **Format** | What's the raw format? | May need parsers/converters |
| **Volume** | How much data? | GB/TB, record counts |
| **Velocity** | How often does it change? | Static, daily, real-time |
| **Veracity** | How reliable is it? | Known quality issues? |
| **Value** | How critical is it? | Primary vs supplementary |

### 5. Extraction Pipeline Design

**A. Extraction Method per Source**

"For each source, we need an extraction strategy:"

| Source | Method | Considerations |
|--------|--------|----------------|
| **PDFs** | Parser (PyMuPDF, pdfplumber, Docling) | Tables, images, OCR needs |
| **Databases** | Query + Incremental loads | Change data capture |
| **APIs** | REST/GraphQL client | Rate limiting, pagination |
| **Web** | Scraper (Scrapy, BeautifulSoup) | robots.txt, legal compliance |
| **Files** | File watcher + readers | Format detection |

Ask: "For your primary data sources, what extraction challenges do you anticipate?"

**B. Extraction Pipeline Architecture**

Query the Knowledge MCP with your constraints:

```
Endpoint: search_knowledge
Query: "{architecture} data pipeline {update_pattern} {team_size} {orchestration_tool}"

Examples:
  - "RAG data pipeline daily updates startup ZenML"
  - "fine-tuning streaming real-time training data Airflow enterprise"
```

**Based on knowledge base patterns, present recommendations for:**
- Batch processing (scheduled extractions, cost-optimized)
- Streaming processing (real-time data ingestion, lower latency)
- Hybrid approach (batch for backfill, streaming for new data)
- Trade-offs for each with your tech stack

**Your constraints to consider:**
- **Data volume:** How much data are we processing?
- **Update frequency:** How often does data change?
- **Latency requirements:** How fresh does data need to be?
- **Team capacity:** Can your team maintain streaming infrastructure?
- **Budget:** Cost difference between batch and streaming?

Present to user:
"Based on your data characteristics, the knowledge base suggests these pipeline patterns. Let me show you the trade-offs specific to your constraints. Which resonates with your situation?"

### 6. Data Transformation Design

**A. Cleaning Operations (Architecture-Specific)**

"What transformations does your data need?"

**For RAG:**
| Operation | Priority | Purpose | Example |
|-----------|----------|---------|---------|
| **Deduplication** | ⭐⭐⭐ CRITICAL | Remove duplicates | Same doc from multiple sources |
| **Metadata Extraction** | ⭐⭐⭐ CRITICAL | Capture retrieval metadata | Source, timestamp, version |
| **Normalization** | ⭐⭐ HIGH | Standardize formats | Date formats, encodings |
| **Filtering** | ⭐⭐ HIGH | Remove boilerplate | Headers, footers, navigation |
| **Enrichment** | ⭐⭐ HIGH | Add context | Category, domain, confidence |
| **Validation** | ⭐ MEDIUM | Check completeness | Metadata present, readable text |

**For Fine-tuning:**
| Operation | Priority | Purpose | Example |
|-----------|----------|---------|---------|
| **Label Validation** | ⭐⭐⭐ CRITICAL | Verify correctness | Labels match examples |
| **Deduplication** | ⭐⭐ HIGH | Remove exact duplicates | Prevent overfitting |
| **Balance Checking** | ⭐⭐ HIGH | Ensure representation | No class imbalance |
| **Filtering** | ⭐⭐ HIGH | Remove corrupted data | Incomplete labels |
| **Normalization** | ⭐ MEDIUM | Standardize format | Consistent structure |
| **Enrichment** | ⭐ MEDIUM | Add context | Example difficulty |

**B. Transformation Pipeline**

```
Raw Data
    ↓
┌─────────────────┐
│  Deduplication  │  → Remove exact and near-duplicates
└────────┬────────┘
         ↓
┌─────────────────┐
│   Validation    │  → Check schema, required fields
└────────┬────────┘
         ↓
┌─────────────────┐
│    Cleaning     │  → Remove noise, normalize formats
└────────┬────────┘
         ↓
┌─────────────────┐
│   Enrichment    │  → Add metadata, timestamps
└────────┬────────┘
         ↓
Clean Data (Ready for Step 4)
```

Ask: "What specific cleaning rules does your data need? Any domain-specific transformations?"

### 7. Data Quality Framework

**A. Quality Dimensions (Architecture-Specific)**

"We'll validate data across dimensions that matter for **{architecture}**:"

**Query Knowledge MCP for Architecture-Specific Quality Thresholds:**

```
Endpoint: get_patterns
Topic: "data quality gates {architecture} validation"
Example: "data quality gates rag-only validation" or "data quality gates fine-tuning validation"
```

```
Endpoint: search_knowledge
Query: "data quality thresholds {architecture} completeness deduplication"
Example: "data quality thresholds rag metadata completeness"
```

**For RAG - Synthesized from Knowledge MCP:**
Present quality dimensions with thresholds from knowledge base queries:

| Dimension | Check | Threshold Source | Why |
|-----------|-------|------------------|-----|
| **Metadata Completeness** | Source, timestamp, version present | Query Knowledge MCP | Required for retrieval traceability |
| **Document Integrity** | No truncated or corrupted text | Query Knowledge MCP | Prevents incomplete retrieval |
| **Deduplication** | No exact or semantic duplicates | Query Knowledge MCP | Prevents redundant retrieval |
| **Format Consistency** | All documents parseable | Query Knowledge MCP | Enables reliable embedding |
| **Freshness** | Documents within acceptable age | Query Knowledge MCP (domain-dependent) | Depends on domain |

**For Fine-tuning - Synthesized from Knowledge MCP:**
Present quality dimensions with thresholds from knowledge base queries:

| Dimension | Check | Threshold Source | Why |
|-----------|-------|------------------|-----|
| **Label Accuracy** | Labels correct per guidelines | Query Knowledge MCP | Wrong labels = wrong behavior |
| **Example Diversity** | No overfitting risk | Query Knowledge MCP (domain-specific) | Poor diversity = poor generalization |
| **Data Leakage** | No eval/test data in training | Query Knowledge MCP | Essential for valid evaluation |
| **Completeness** | All required fields present | Query Knowledge MCP | Prevents training failures |
| **Class Balance** | Fair representation of classes | Query Knowledge MCP (domain-specific) | Prevents model bias |

**B. Quality Gates**

**If RAG - Quality Gates (Thresholds from Knowledge MCP):**
```yaml
quality_gates:
  extraction:
    - name: "Metadata extraction"
      check: "Source, timestamp, version extracted"
      threshold: "[from Knowledge MCP: metadata completeness rag]"
      note: "Query Knowledge MCP: metadata extraction threshold rag"
      action_on_fail: "Block pipeline, review source"

  transformation:
    - name: "Deduplication check"
      check: "No exact or semantic duplicates"
      threshold: "[from Knowledge MCP: deduplication tolerance rag]"
      note: "Query Knowledge MCP: semantic deduplication threshold rag"
      action_on_fail: "Quarantine duplicates, investigate"

  output:
    - name: "Format validation"
      check: "All documents match schema"
      threshold: "[from Knowledge MCP: format consistency threshold rag]"
      note: "Query Knowledge MCP: document format validation rag"
      action_on_fail: "Block pipeline, review"
```

**If Fine-tuning - Quality Gates (Thresholds from Knowledge MCP):**
```yaml
quality_gates:
  extraction:
    - name: "Data completeness"
      check: "All required fields present"
      threshold: "[from Knowledge MCP: completeness threshold fine-tuning]"
      note: "Query Knowledge MCP: data completeness threshold fine-tuning"
      action_on_fail: "Quarantine incomplete records"

  transformation:
    - name: "Label validation"
      check: "Labels match guidelines (sample verified)"
      threshold: "[from Knowledge MCP: label accuracy threshold fine-tuning]"
      note: "Query Knowledge MCP: label validation threshold fine-tuning"
      action_on_fail: "Block pipeline, review labeling"

    - name: "Leakage prevention"
      check: "No eval/test data in training"
      threshold: "[from Knowledge MCP: data leakage tolerance fine-tuning]"
      note: "Query Knowledge MCP: train-eval separation threshold fine-tuning"
      action_on_fail: "Block pipeline, segregate data"
```

Ask: "What quality thresholds are acceptable for your use case? Any critical gates that must block vs. alert?"

### 8. Semantic Caching Decision (IF RAG WITH HIGH VOLUME)

**Query Knowledge MCP for Volume Thresholds:**

Before deciding on semantic caching, query the knowledge base for current best practices on caching thresholds:

```
Endpoint: search_knowledge
Query: "semantic caching volume threshold RAG {orchestration_tool}"
Example: "semantic caching volume threshold RAG ZenML"
```

```
Endpoint: get_patterns
Topic: "semantic caching optimization {data_volume} RAG"
```

**Synthesis Approach:**
1. Extract volume-based caching thresholds from knowledge base
2. Identify cost-benefit trade-offs for your specific data volume
3. Surface warnings about caching complexity and latency impact
4. Present Knowledge MCP recommendation for your data size

**SYNTHESIS APPROACH:**

Based on your data volume and infrastructure:

**Query Knowledge MCP for volume-specific recommendations:**
```
Endpoint: search_knowledge
Query: "semantic caching thresholds {orchestration_tool} {data_volume}"
Example: "semantic caching thresholds ZenML 50GB"
```

```
Endpoint: get_patterns
Topic: "caching cost-benefit {data_volume} {query_frequency}"
Example: "caching cost-benefit 100GB high-frequency"
```

```
Endpoint: get_warnings
Topic: "semantic caching complexity latency trade-offs"
```

**Synthesis:**
1. Extract volume-based thresholds from knowledge base
2. Identify cost-benefit trade-offs specific to your {orchestration_tool}
3. Surface latency and complexity warnings
4. Present recommendation conditioned on actual data volume

**Key Pattern to Surface (from Knowledge MCP):**
> Volume thresholds for caching recommendation vary by orchestration platform and query patterns. The knowledge base will recommend if caching provides ROI for your {data_volume} at {query_frequency}.

**Based on Knowledge MCP recommendations, determine if semantic caching applies:**
- User provides actual data volume from conversation
- Knowledge MCP returns volume-specific recommendation
- Present cost-benefit trade-off for their specific scenario

**Decision (conditioned on Knowledge MCP recommendation):**
- Based on Knowledge MCP patterns for your volume: Implement caching → Adds complexity, saves cost
- Based on Knowledge MCP patterns for your volume: No caching → Simpler pipeline, higher cost
- Evaluate later → Start without, add if costs spike (monitor actual usage patterns first)

### 9. Surface Anti-Patterns & Warnings

**Critical: Pause and surface knowledge-grounded anti-patterns**

Query Knowledge MCP:
```
Endpoint: get_warnings
Topic: "{architecture} data pipeline"
```

**If RAG, surface these:**

⚠️ **Top RAG Data Pipeline Mistakes:**

1. **Missing or incomplete metadata**
   - Prevention: Capture source, timestamp, version in extraction

2. **Poor deduplication strategy**
   - Prevention: De-duplicate exact AND semantic duplicates

3. **No document versioning**
   - Prevention: Track document versions, re-index on updates

4. **Incomplete text extraction from PDFs**
   - Prevention: Use robust PDF parser, validate extracted content

5. **Boilerplate/noise in documents**
   - Prevention: Filter known boilerplate, validate content signal

6. **No retrieval quality validation**
   - Prevention: Test retrieval quality before moving to inference

**If Fine-tuning, surface these:**

⚠️ **Top Fine-tuning Data Pipeline Mistakes:**

1. **Label quality not validated**
   - Prevention: Verify 100% of labels before training

2. **Evaluation data leaks into training**
   - Prevention: Strict separation of train/eval/test sets

3. **Class imbalance**
   - Prevention: Check balance, use sampling strategies

4. **Overfitting on small dataset**
   - Prevention: Audit data diversity, consider augmentation

Ask: "Are you aware of these common pitfalls? Any concerns for your pipeline?"

### 10. Data Storage & Vector DB Specification (IF RAG)

**For RAG systems only - specify where cleaned data goes before embedding**

"Based on your chosen vector DB from Phase 0, we need to specify data format and storage:"

**Query Knowledge MCP:**
```
Endpoint: search_knowledge
Query: "{vector_db} data storage format ingestion {data_type}"
```

**Data specification to document:**

| Aspect | Specification |
|--------|---------------|
| **Format** | [JSON, Parquet, CSV, documents] |
| **Schema** | [Fields: content, metadata.source, etc.] |
| **Storage location** | [Cloud path, local directory, DB URL] |
| **Retention policy** | [How long data is kept] |
| **Access control** | [Who can read/write, encryption] |

"The Embeddings Engineer (Step 4) will ingest this data into {vector_db}."

---

### 11. Document Decisions

Once user confirms data pipeline design, create the specification.

**Create data-pipeline-spec.md:**
```markdown
# Data Pipeline Specification

**Project:** {project_name}
**Architecture:** {architecture}
**Orchestration:** {orchestration_tool}
**Date:** {date}

---

## Sources
| Source | Type | Volume | Update Frequency |
|--------|------|--------|------------------|
| [source 1] | [type] | [volume] | [frequency] |

## Extraction
- **Architecture:** [Batch | Streaming | Hybrid]
- **Tools:** [list extraction tools]
- **Schedule:** [extraction schedule]

## Transformation
1. [transformation 1]
2. [transformation 2]

## Quality Gates
- [gate 1]: [threshold]
- [gate 2]: [threshold]

## Output
- **Format:** [output format]
- **Location:** [storage location]
- **Schema:** [link to schema]

## Pipeline Configuration
[Full YAML config for {orchestration_tool}]
```

**Update sidecar.yaml:**
```yaml
currentStep: "3b"
stepsCompleted: [1, "2a", "2b", "3a", "3b"]
phases:
  phase_1_feature:
    data_requirements: "validated"
    data_pipeline: "designed"
decisions:
  - id: "DATA-001"
    step: "3b"
    choice: "[pipeline architecture]"
    rationale: "[brief rationale]"
```

**Append to decision-log.md:**
```markdown
## DATA-001: Data Pipeline Architecture

**Decision:** [Batch | Streaming | Hybrid]
**Date:** {date}
**Step:** 3B - Data Engineer

**Context:** [Data sources and requirements summary]

**Rationale:** [Why this architecture]

**Tech Stack Integration:**
- Orchestration: {orchestration_tool}
- Vector DB: {vector_db}

**Consequences:**
- [Impact on downstream steps]
```

### 12. Generate Data Pipeline Stories

Based on the pipeline design and tech stack:

```yaml
stories:
  step_3_data:
    - id: "DATA-S01"
      title: "Set up data source connections"
      description: "Configure access to all identified data sources using {orchestration_tool}"
      acceptance_criteria:
        - "All source connections tested and working"
        - "Credentials securely stored in {orchestration_tool} secrets"
        - "Connection retry logic implemented"

    - id: "DATA-S02"
      title: "Implement extraction pipeline"
      description: "Build extraction logic for each source type in {orchestration_tool}"
      acceptance_criteria:
        - "Extractors handle all identified formats"
        - "Incremental extraction where applicable"
        - "Error handling and logging in place"
        - "Scheduling configured"

    - id: "DATA-S03"
      title: "Build transformation pipeline"
      description: "Implement data cleaning and normalization in {orchestration_tool}"
      acceptance_criteria:
        - "[If RAG] Deduplication logic working"
        - "[If RAG] Metadata extraction validated"
        - "[If FT] Label validation implemented"
        - "[If FT] Data leakage checks in place"

    - id: "DATA-S04"
      title: "Implement quality gates"
      description: "Add quality validation checkpoints in {orchestration_tool}"
      acceptance_criteria:
        - "Quality metrics computed"
        - "Thresholds configurable per gate"
        - "Alerts configured on failures"

    - id: "DATA-S05"
      title: "Set up data storage"
      description: "[If RAG] Prepare data format compatible with {vector_db}"
      acceptance_criteria:
        - "Data schema compatible with {vector_db}"
        - "Storage location configured"
        - "Sample data successfully stored"

    - id: "DATA-S06"
      title: "Validate end-to-end pipeline"
      description: "Run complete pipeline with test data"
      acceptance_criteria:
        - "All stages pass"
        - "Quality gates report valid"
        - "Data ready for Step 4"
```

**Update sidecar with stories:**
```yaml
stories:
  step_3_data:
    - "[story list based on pipeline design]"
```

### 12.5 Data Pipeline Design Confirmation

**Before proceeding to Step 4, confirm the pipeline architecture:**

We've designed your data pipeline with:
- **Ingestion Strategy:** {summarize extraction method: batch/streaming/hybrid}
- **Quality Checks:** {list 2-3 key quality gates from conversation}
- **Architecture Fit:** {note which architecture this pipeline serves - RAG/FT/Hybrid}

"This pipeline architecture is designed for **{architecture}** and uses **{orchestration_tool}** for orchestration. Is this approach right for your project?"

**Confirm you're ready to proceed:**
- **[Yes]** The pipeline design aligns with my needs
- **[No]** I need to adjust the pipeline strategy
- **[Questions]** I have concerns we should discuss

Wait for user response and address any adjustments before displaying the menu below.

---

### 13. Present MENU OPTIONS

Display: **Step 3B Complete - Select an Option:**
```
[A] Analyze pipeline further
[Q] Re-query knowledge base with different constraints
[P] View progress
[C] Continue to Step 4 (Embeddings Engineer)
```

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- **IF A:** Revisit pipeline decisions, allow refinement, then redisplay menu
- **IF Q:** Re-query Knowledge MCP with modified constraints, update recommendations, then redisplay menu
- **IF P:** Show data-pipeline-spec.md, decision-log.md, and DATA-001 entry summaries, then redisplay menu
- **IF C:**
  1. Verify sidecar is updated with data pipeline decisions and stories
  2. Verify data-pipeline-spec.md created
  3. Load, read entire file, then execute `{nextStepFile}` (Embeddings Engineer)
- **IF Any other comments or queries:** help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND data pipeline is documented AND stories are generated, will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Step 4: Embeddings Engineer.

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

**Knowledge Grounding:**
- Architecture-specific queries to Knowledge MCP executed
- Vector DB-specific queries executed (if RAG)
- Warnings about anti-patterns surfaced
- User acknowledges risks specific to their architecture

**Pipeline Design:**
- All data sources identified and assessed
- Extraction strategy defined for each source
- Extraction architecture chosen with knowledge-grounded rationale
- Transformation pipeline designed (architecture-aware)
- Quality gates established with architecture-specific thresholds

**Tech Stack Integration:**
- Pipeline designed to work with {orchestration_tool}
- Data format compatible with {vector_db} (if RAG)
- Stories reference tech stack decisions

**Documentation:**
- data-pipeline-spec.md created
- Decision-log.md updated with DATA-001
- Sidecar updated with pipeline decisions
- Stories generated (6+ stories)

### SYSTEM FAILURE:

- Pipeline design without loading requirements from Step 3A
- Not referencing tech stack decisions
- Generic Knowledge MCP queries (not contextualized)
- Same pipeline design for RAG vs FT vs Hybrid
- Discussing chunking or embeddings (Step 4)
- Discussing model training (Step 5)
- Not generating implementation stories

**Master Rule:** This step designs the pipeline based on validated requirements from Step 3A.
