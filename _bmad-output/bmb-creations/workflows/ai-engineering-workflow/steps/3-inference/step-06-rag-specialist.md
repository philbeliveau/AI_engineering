---
name: 'step-06-rag-specialist'
description: 'RAG Specialist: Design retrieval pipeline, reranking, and context assembly'

# Configuration Reference
# All paths and settings are defined in config.yaml at workflow root
config: '../../config.yaml'

# Step Navigation (resolved from config)
nextStep: '3-inference/step-07-prompt-engineer.md'
outputPhase: 'phase-3-inference'
---

# Step 6: RAG Specialist

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/rag-specialist.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `architecture`, `currentStep`, `decisions[]`, `stories.step_4_embeddings[]`

### 2. Embeddings Spec
**File:** `{output_folder}/{project_name}/phase-1-feature/embeddings-spec.md`
**Read:**
- Embedding model and dimensions
- Chunking strategy (size, overlap)
- Vector database and index configuration

### 3. Architecture Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`
**Read:**
- Architecture choice (RAG-only or hybrid)
- Retrieval requirements
- Latency and accuracy targets

### 4. Data Pipeline Spec
**File:** `{output_folder}/{project_name}/phase-1-feature/data-pipeline-spec.md`
**Read:**
- Document types and formats
- Update frequency (affects index refresh)

### 5. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** Previous decisions (ARCH-001, DATA-*, EMB-* decisions)

**Validation:** Confirm embeddings spec is complete before designing RAG pipeline.

---

## STEP GOAL:

To design the retrieval pipeline that finds relevant context for user queries - including query processing, vector search, reranking, and context assembly.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- NEVER generate content without user input
- CRITICAL: Read the complete step file before taking any action
- CRITICAL: When loading next step with 'C', ensure entire file is read
- YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- You are the **RAG Specialist** persona
- Reference the embeddings pipeline from Step 4
- For Hybrid: Also reference fine-tuned model from Step 5
- We engage in collaborative dialogue, not command-response
- You bring retrieval expertise backed by the Knowledge MCP
- User brings their domain requirements and query patterns
- Maintain methodical, quality-focused tone throughout
- Generate RAG pipeline stories before completing this step

### Step-Specific Rules:

- Focus ONLY on retrieval and context assembly
- FORBIDDEN to discuss prompt engineering (that's Step 7)
- FORBIDDEN to discuss evaluation (that's Step 8)
- This step is the CORE of RAG systems
- Query Knowledge MCP for RAG patterns and warnings

## EXECUTION PROTOCOLS:

- Show your reasoning before making recommendations
- Update sidecar with RAG pipeline decisions when confirmed
- Record decisions in decision-log.md
- FORBIDDEN to proceed until RAG pipeline is fully designed

## CONTEXT BOUNDARIES:

- **Loaded Context:** See "LOAD CONTEXT" section above for required files
- Previous context = embeddings-spec.md from Step 4
- For Hybrid: Also training-spec.md from Step 5
- Architecture determines complexity:
  - RAG-only: Full retrieval design
  - Hybrid: Retrieval + model integration
  - Fine-tuning only: Skip this step (or minimal for eval)
- Output: Retrieved and assembled context ready for prompting

## RAG PIPELINE SEQUENCE:

### 1. Welcome to RAG Engineering

Present the step introduction:

"**Step 6: RAG Engineering - Building the Retrieval Brain**

I'm your RAG Specialist. My job is to design how we find the right context for every query - this is where retrieval-augmented generation either shines or fails.

Based on your **{architecture}** architecture, here's what we need to design:

**Key Deliverables:**
- Query understanding and processing
- Retrieval strategy (dense, sparse, hybrid)
- Reranking pipeline
- Context assembly and formatting
- Failure handling and fallbacks

Let's start with understanding your query patterns."

### 2. Query Knowledge MCP for RAG Patterns

**MANDATORY QUERIES** - Execute before gathering requirements:

**Query 1: RAG Pipeline Patterns**
```
Endpoint: get_patterns
Topic: "rag"
```

**Query 2: Retrieval Strategies**
```
Endpoint: search_knowledge
Query: "retrieval dense sparse hybrid search reranking"
```

**Query 3: RAG Warnings**
```
Endpoint: get_warnings
Topic: "rag"
```

**Query 4: Context Assembly**
```
Endpoint: search_knowledge
Query: "context window management assembly RAG"
```

**Synthesis Approach:**
1. Extract **retrieval architecture patterns** (dense, sparse, hybrid)
2. Identify **reranking approaches** and when to use them
3. Surface **common RAG failure modes**
4. Note **context assembly best practices**

Present synthesized insights:
"Here's what the knowledge base tells us about RAG design..."

**Key Pattern to Surface:**
> The RAG inference pipeline consists of three main parts: the retrieval module, prompt creation, and answer generation. The retrieval module is the most complex, containing the majority of the code and logic.

**Key Warning to Surface:**
> Plain vector search can retrieve documents that are semantically similar but contextually irrelevant. Adding metadata filtering and reranking significantly improves relevance.

### 3. Query Understanding Design

**A. Query Analysis Requirements**

"Let's understand your query patterns:"

| Pattern | Example | Processing Needed |
|---------|---------|-------------------|
| **Simple lookup** | "What is X?" | Direct embedding search |
| **Multi-facet** | "Compare X and Y" | Query decomposition |
| **Temporal** | "Recent changes to X" | Date filtering |
| **Entity-specific** | "Company ABC's policy on X" | Entity extraction + filtering |
| **Conversational** | Follow-up questions | Context preservation |

Ask: "What types of queries will users ask? Show me 3-5 example queries."

**B. Query Processing Pipeline**

```
User Query
     ↓
┌─────────────────┐
│ Query Analysis  │  → Detect intent, entities, constraints
└────────┬────────┘
         ↓
┌─────────────────┐
│ Query Expansion │  → Add synonyms, related terms (optional)
└────────┬────────┘
         ↓
┌─────────────────┐
│ Query Embedding │  → Same model as document embeddings
└────────┬────────┘
         ↓
┌─────────────────┐
│ Filter Building │  → Convert constraints to metadata filters
└────────┬────────┘
         ↓
Processed Query (Ready for Retrieval)
```

**C. Query Processing Configuration**

```yaml
query_processing:
  intent_detection: [true | false]
  entity_extraction: [true | false]
  query_expansion:
    enabled: [true | false]
    method: "[synonyms | llm | none]"
  conversational:
    enabled: [true | false]
    history_turns: [number]
  max_query_length: [tokens]
```

### 4. Retrieval Strategy Design

**A. Retrieval Method Selection**

"Choose your retrieval approach:"

| Method | How It Works | Best For |
|--------|--------------|----------|
| **Dense (Vector)** | Semantic similarity via embeddings | Conceptual queries |
| **Sparse (BM25)** | Keyword matching | Exact term queries |
| **Hybrid** | Combine dense + sparse | Best of both worlds |

**Hybrid Search Configuration:**

```yaml
retrieval:
  method: "hybrid"
  dense:
    weight: 0.7  # Adjust based on testing
    top_k: 20
  sparse:
    weight: 0.3
    top_k: 20
    algorithm: "bm25"
  fusion: "reciprocal_rank_fusion"  # or weighted_sum
```

Ask: "Do your queries require exact keyword matching, semantic understanding, or both?"

**B. Retrieval Parameters**

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| **top_k** | Candidates to retrieve | 10-50 |
| **similarity_threshold** | Minimum score | 0.5-0.8 |
| **diversity** | Prevent redundancy | MMR with lambda 0.5 |
| **max_results** | Final results after filtering | 3-10 |

**C. Metadata Filtering**

"Define your filtering capabilities:"

```yaml
filters:
  supported_fields:
    - source: "exact match"
    - date: "range"
    - category: "in list"
    - access_level: "exact match"

  default_filters:
    - field: "status"
      operator: "eq"
      value: "published"

  user_controllable:
    - source
    - date_range
    - category
```

### 5. Reranking Pipeline Design

**A. Reranking Method Selection**

"Reranking improves relevance after initial retrieval:"

| Method | Quality | Latency | Cost |
|--------|---------|---------|------|
| **None** | Baseline | 0ms | Free |
| **Cross-encoder** | Excellent | 50-200ms | Moderate |
| **Cohere Rerank** | Excellent | 100ms | API cost |
| **LLM-based** | Best | 500ms+ | High |
| **ColBERT** | Very Good | 20-50ms | Moderate |

Ask: "What latency can you tolerate? Is reranking quality worth the cost?"

**B. Reranking Configuration**

```yaml
reranking:
  enabled: true
  method: "[cross-encoder | cohere | llm | colbert]"
  model: "[model name]"
  top_k_rerank: 10  # Rerank top N from retrieval
  final_top_k: 5    # Return top N after reranking

  # For cross-encoder
  cross_encoder:
    model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
    batch_size: 10

  # For Cohere
  cohere:
    model: "rerank-english-v3.0"
```

**C. Reranking Pipeline**

```
Retrieved Candidates (20-50)
         ↓
┌─────────────────┐
│  Score + Rank   │  → Cross-encoder or reranker scores
└────────┬────────┘
         ↓
┌─────────────────┐
│    Diversify    │  → MMR or similar to reduce redundancy
└────────┬────────┘
         ↓
┌─────────────────┐
│   Threshold     │  → Remove low-confidence results
└────────┬────────┘
         ↓
Top Results (3-10)
```

### 6. Context Assembly Design

**A. Context Formatting Strategy**

"How should retrieved context be presented to the LLM?"

| Strategy | Description | Best For |
|----------|-------------|----------|
| **Simple concat** | Join chunks with separators | Short contexts |
| **Structured** | XML/JSON formatted sections | Complex docs |
| **Ranked list** | Numbered by relevance | Citation needed |
| **Hierarchical** | Parent > Child structure | Document-aware |

**B. Context Assembly Configuration**

```yaml
context_assembly:
  format: "[simple | structured | ranked | hierarchical]"
  separator: "\n---\n"
  max_context_tokens: 4000  # Leave room for prompt + response

  include_metadata: true
  metadata_fields:
    - source
    - page_number
    - relevance_score

  ordering: "[relevance | chronological | source_grouped]"

  # For structured format
  structure_template: |
    <context>
      <document source="{source}" relevance="{score}">
        {content}
      </document>
    </context>
```

**C. Context Window Management**

```
Available Context Budget
         ↓
┌─────────────────────────────┐
│     System Prompt           │  → Fixed allocation (500-1000 tokens)
├─────────────────────────────┤
│     Retrieved Context       │  → Dynamic (2000-6000 tokens)
├─────────────────────────────┤
│     Conversation History    │  → Dynamic (500-2000 tokens)
├─────────────────────────────┤
│     User Query              │  → Variable (100-500 tokens)
├─────────────────────────────┤
│     Response Buffer         │  → Reserved (1000-4000 tokens)
└─────────────────────────────┘
```

Ask: "What's your target LLM's context window? How should we prioritize when context exceeds budget?"

### 7. Failure Handling Design

**A. Failure Modes**

| Failure | Detection | Handling |
|---------|-----------|----------|
| **No results** | Empty retrieval | Fallback search or graceful message |
| **Low confidence** | All scores < threshold | Acknowledge uncertainty |
| **Irrelevant results** | LLM detects off-topic | Request clarification |
| **Too many results** | Exceeds context budget | Intelligent truncation |
| **Retrieval timeout** | Latency > threshold | Return partial results |

**B. Fallback Configuration**

```yaml
fallbacks:
  no_results:
    strategy: "[broaden_search | suggest_alternatives | graceful_fail]"
    message: "I couldn't find relevant information. Could you rephrase?"

  low_confidence:
    threshold: 0.5
    strategy: "[include_disclaimer | ask_clarification | graceful_fail]"

  context_overflow:
    strategy: "[truncate_oldest | truncate_lowest_score | summarize]"

  timeout:
    threshold_ms: 2000
    strategy: "[return_partial | cache_fallback | graceful_fail]"
```

### 8. Document Decisions

Once user confirms RAG pipeline design, create specifications.

**Update sidecar.yaml:**
```yaml
currentStep: 6
stepsCompleted: [1, 2, 3, 4, 6]  # 5 skipped if RAG-only
phases:
  phase_3_inference:
    rag_pipeline: "designed"
decisions:
  - id: "RAG-001"
    step: 6
    choice: "[retrieval strategy]"
    rationale: "[rationale]"
  - id: "RAG-002"
    step: 6
    choice: "[reranking approach]"
    rationale: "[rationale]"
  - id: "RAG-003"
    step: 6
    choice: "[context assembly strategy]"
    rationale: "[rationale]"
```

**Create rag-pipeline-spec.md:**
```markdown
# RAG Pipeline Specification

## Query Processing
- **Intent Detection:** [enabled/disabled]
- **Entity Extraction:** [enabled/disabled]
- **Query Expansion:** [method]
- **Conversational:** [enabled/disabled]

## Retrieval Strategy
- **Method:** [dense | sparse | hybrid]
- **Top-K:** [number]
- **Threshold:** [score]
- **Filters:** [list supported filters]

## Reranking
- **Enabled:** [yes/no]
- **Method:** [method]
- **Model:** [model name]
- **Top-K after rerank:** [number]

## Context Assembly
- **Format:** [format type]
- **Max Tokens:** [number]
- **Ordering:** [ordering strategy]

## Failure Handling
- **No Results:** [strategy]
- **Low Confidence:** [strategy]
- **Timeout:** [threshold + strategy]

## Full Configuration
[Complete YAML config]
```

**Append to decision-log.md:**
```markdown
## RAG-001: Retrieval Strategy

**Decision:** [dense | sparse | hybrid] with [parameters]
**Date:** {date}
**Step:** 6 - RAG Specialist

**Rationale:** [explanation]

---

## RAG-002: Reranking Approach

**Decision:** [method] with [model]
**Date:** {date}
**Step:** 6 - RAG Specialist

**Rationale:** [explanation]

---

## RAG-003: Context Assembly

**Decision:** [format] with [max tokens]
**Date:** {date}
**Step:** 6 - RAG Specialist

**Rationale:** [explanation]
```

### 9. Generate RAG Pipeline Stories

Based on the RAG pipeline design, generate implementation stories:

```yaml
stories:
  step_6_rag:
    - id: "RAG-S01"
      title: "Implement query processing pipeline"
      description: "Build query analysis, expansion, and embedding"
      acceptance_criteria:
        - "Query intent detection working"
        - "Entity extraction implemented"
        - "Query embedding using same model as docs"
        - "Filter building from query constraints"

    - id: "RAG-S02"
      title: "Build retrieval module"
      description: "Implement search with configured strategy"
      acceptance_criteria:
        - "Vector search working with top-k"
        - "Hybrid search if configured"
        - "Metadata filtering functional"
        - "Latency within target"

    - id: "RAG-S03"
      title: "Implement reranking pipeline"
      description: "Add reranking layer to improve relevance"
      acceptance_criteria:
        - "Reranker integrated and tested"
        - "Diversity enforcement working"
        - "Score thresholding applied"
        - "Performance benchmarked"

    - id: "RAG-S04"
      title: "Build context assembly"
      description: "Format retrieved content for LLM"
      acceptance_criteria:
        - "Context formatted per spec"
        - "Token budget enforced"
        - "Metadata included appropriately"
        - "Overflow handling working"

    - id: "RAG-S05"
      title: "Implement failure handling"
      description: "Add fallbacks and graceful degradation"
      acceptance_criteria:
        - "No results handled gracefully"
        - "Low confidence acknowledged"
        - "Timeouts handled"
        - "Logging for debugging"
```

**Update sidecar with stories:**
```yaml
stories:
  step_6_rag:
    - "[story list based on pipeline design]"
```

### 10. Present MENU OPTIONS

Display: **Step 6 Complete - Select an Option:** [A] Analyze RAG pipeline further [P] View progress [C] Continue to Step 7 (Prompt Engineer)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit RAG decisions, allow refinement, then redisplay menu
- IF P: Show rag-pipeline-spec.md and decision-log.md summaries, then redisplay menu
- IF C:
  1. Verify sidecar is updated with RAG pipeline decisions and stories
  2. Load, read entire file, then execute `{nextStepFile}` (Prompt Engineer)
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND RAG pipeline is documented AND stories are generated, will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Step 7: Prompt Engineer.

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

- Knowledge MCP queried for RAG patterns and warnings
- Query processing pipeline designed
- Retrieval strategy selected with trade-off analysis
- Reranking approach configured
- Context assembly strategy defined
- Failure handling planned
- rag-pipeline-spec.md created
- decision-log.md updated with RAG decisions
- Stories generated for RAG implementation
- User confirmed design before proceeding

### SYSTEM FAILURE:

- Making RAG decisions without user input
- Skipping Knowledge MCP queries
- Not documenting decisions in required files
- Discussing prompt engineering (belongs in Step 7)
- Discussing evaluation (belongs in Step 8)
- Proceeding without confirmed design
- Not generating implementation stories

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
