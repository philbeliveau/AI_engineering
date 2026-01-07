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

### 6. Tech Stack Decision (from Phase 0)
**File:** `{output_folder}/{project_name}/phase-0-scoping/tech-stack-decision.md`
**Read:**
- Vector database selected (Qdrant, Pinecone, etc.)
- Orchestration framework (LangChain, LlamaIndex, etc.)
- Serving framework choice
- Reranking model preferences

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

**Context Variables to Use:**
- `{architecture}` from sidecar.yaml
- `{vector_db}` from tech-stack-decision.md
- `{embedding_model}` from embeddings-spec.md
- `{latency_sla}` from business-requirements.md
- `{query_patterns}` gathered from user

**MANDATORY QUERIES** - Execute with context before gathering requirements:

**Query 1: RAG Pipeline Patterns (Contextualized)**
```
Endpoint: get_patterns
Topic: "rag pipeline {vector_db} {orchestration_tool}"
Example: "rag pipeline qdrant langchain"
```

**Query 2: Retrieval Strategies (Contextualized)**
```
Endpoint: search_knowledge
Query: "retrieval {query_complexity} {latency_requirement} {vector_db}"
Example: "retrieval multi-hop-queries 200ms qdrant"
```

**Query 3: RAG Warnings (Contextualized)**
```
Endpoint: get_warnings
Topic: "rag {architecture} {vector_db}"
Example: "rag hybrid pinecone"
```

**Query 4: Context Assembly (Contextualized)**
```
Endpoint: search_knowledge
Query: "context window {llm_context_size} assembly {architecture}"
Example: "context window 128k assembly rag-only"
```

**Synthesis Approach:**
1. Extract **retrieval architecture patterns** compatible with {vector_db}
2. Identify **reranking approaches** that meet {latency_sla}
3. Surface **common RAG failure modes** for {architecture} systems
4. Note **context assembly best practices** for {llm_context_size}

Present synthesized insights:
"Based on your **{architecture}** architecture with **{vector_db}** and **{latency_sla}** requirement, here's what the knowledge base recommends..."

**Key Pattern to Surface (from knowledge - will vary by context):**
> Query patterns for RAG with {vector_db}: [dynamically retrieved]

**Key Warning to Surface (from knowledge - will vary by context):**
> Common pitfall for {architecture} with {vector_db}: [dynamically retrieved]

### 2.5 Architecture-Specific RAG Design

**CRITICAL:** Route based on architecture decision from Phase 0.

**IF architecture == "rag-only":**
- Full RAG pipeline design is required
- Retrieval is the primary intelligence source
- Focus on retrieval quality, reranking, and context assembly
- All sections (3-7) fully apply
- Query: `get_patterns` with topic: "rag-only pipeline end-to-end"

**IF architecture == "hybrid":**
- RAG augments fine-tuned model
- Focus on retrieval for factual grounding only
- Fine-tuned model handles reasoning; RAG provides facts
- Query: `search_knowledge` with: "hybrid rag fine-tuned-model integration"
- Consider: When to retrieve vs. when to rely on model knowledge
- Simpler context assembly (model already has domain knowledge)

**IF architecture == "fine-tuning" (FT-only):**
- Minimal RAG (for evaluation retrieval only)
- May skip this step entirely if no retrieval needed
- OR design lightweight retrieval for eval baselines only
- Query: `get_patterns` with topic: "evaluation retrieval baseline"
- Present option: "Skip to Step 7 if no retrieval component needed"

**Routing Logic:**
```
IF architecture == "fine-tuning" AND user confirms no retrieval:
  → Skip to Step 7 (update sidecar: step_6_skipped: true)
ELSE:
  → Continue with full RAG design (sections 3-9)
```

---

### 2.6 RAG Pipeline Configuration Confirmation

**Before proceeding with full RAG design, confirm your architecture needs retrieval:**

Your architecture is: **{architecture}**

- If your architecture is **rag-only** or **hybrid**: We'll design a full RAG pipeline in this step
- If your architecture is **fine-tuning-only**: You may not need a retrieval-augmented generation component

**Does your system need a RAG (Retrieval-Augmented Generation) component?**
- **[Yes]** Design the full RAG pipeline
- **[No, skip RAG]** Skip to Step 7 (Prompt Engineering)
- **[Unsure]** Let's discuss what retrieval would add to your system

Wait for user response. If "No", update sidecar with `step_6_skipped: true` and proceed directly to Step 7. If "Yes" or "Unsure", continue with Sections 3-9 below.

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

**Query Knowledge MCP (Contextualized):**
Based on your RAG requirements:
- Query patterns: {query_types from user discussion}
- Vector DB: {vector_db from tech-stack-decision}
- Latency SLA: {latency_requirement from business-requirements}

```
Endpoint: get_patterns
Topic: "retrieval strategy {vector_db} {query_complexity}"
Example: "retrieval strategy qdrant multi-facet-queries"
```

```
Endpoint: get_decisions
Topic: "hybrid search dense sparse {vector_db}"
Example: "hybrid search dense sparse pinecone"
```

**Synthesis:** Present retrieval options that are compatible with the chosen vector DB and meet latency requirements.

"Based on your **{vector_db}** choice and **{latency_sla}** requirement, here are the retrieval strategies that apply:"

| Method | Compatibility with {vector_db} | Trade-offs |
|--------|-------------------------------|------------|
| **Dense (Vector)** | Check native support | Query knowledge for latency characteristics |
| **Sparse (BM25)** | Check if supported or needs external | Query knowledge for integration patterns |
| **Hybrid** | Check fusion support | Query knowledge for RRF vs weighted patterns |

**Configuration Template (adapt based on knowledge queries):**

```yaml
retrieval:
  method: "[dense | sparse | hybrid]"  # From knowledge-grounded recommendation
  vector_db: "{vector_db}"  # From tech-stack-decision
  dense:
    weight: "[from knowledge patterns]"
    top_k: "[from knowledge patterns]"
  sparse:
    weight: "[from knowledge patterns]"
    top_k: "[from knowledge patterns]"
    algorithm: "[from knowledge patterns]"
  fusion: "[from knowledge patterns]"
```

Ask: "Do your queries require exact keyword matching, semantic understanding, or both? Let me query the knowledge base for patterns specific to your {vector_db} choice."

**B. Retrieval Parameters (Knowledge-Grounded)**

Query Knowledge MCP for architecture and vector DB-specific parameter recommendations:

```
Endpoint: get_patterns
Topic: "retrieval parameters top-k threshold {vector_db} {query_complexity}"
Example: "retrieval parameters top-k threshold qdrant multi-facet-queries"
```

```
Endpoint: search_knowledge
Query: "retrieval configuration {vector_db} {latency_requirement}"
Example: "retrieval configuration qdrant 200ms latency"
```

| Parameter | Description | Value Source |
|-----------|-------------|---------------|
| **top_k** | Candidates to retrieve | From Knowledge MCP for {query_complexity} |
| **similarity_threshold** | Minimum score | From Knowledge MCP for {vector_db} and {quality_tier} |
| **diversity** | Prevent redundancy | From Knowledge MCP (MMR method and lambda) |
| **max_results** | Final results after filtering | From Knowledge MCP for {context_window_size} |

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

### 5. Reranking & LLM-as-Judge Evaluation Design

**A. Reranking Method Selection**

**Query Knowledge MCP for Reranking (Contextualized):**
```
Endpoint: get_patterns
Topic: "reranking {latency_budget} {quality_requirement}"
Example: "reranking 100ms-budget high-precision"
```

```
Endpoint: get_warnings
Topic: "reranking latency quality tradeoffs"
```

```
Endpoint: get_decisions
Topic: "reranking cross-encoder cohere colbert"
```

**Query for LLM-as-Judge Bias Patterns (if using LLM-based reranking):**
```
Endpoint: get_patterns
Topic: "llm judge bias evaluation reranking"
Example: "llm judge bias evaluation reranking"
```

```
Endpoint: get_warnings
Topic: "llm-as-judge limitations reranking {architecture}"
Example: "llm-as-judge limitations reranking rag-only"
```

**Conditional Logic (Knowledge-Grounded):**

Query Knowledge MCP for latency-specific recommendations:
```
Endpoint: get_patterns
Topic: "reranking latency-budget {latency_sla} {vector_db}"
Example: "reranking latency-budget 50ms qdrant" or "reranking latency-budget 200ms pinecone"
```

Based on Knowledge MCP response:
- IF knowledge base indicates latency_budget is constrained:
  - Surface warning about reranking latency trade-off
  - Query: "low-latency reranking alternatives"
- IF quality requirements are paramount:
  - Query: "high-precision reranking models {vector_db}"
- IF cost-sensitive:
  - Query: "cost-effective reranking local-models"

**Synthesis:** Present reranking options based on:
1. Your latency budget: {latency_sla from business-requirements}
2. Quality requirements: {quality_tier from user discussion}
3. Budget constraints: {budget from business-requirements}
4. LLM-as-judge biases (if applicable): Current patterns from Knowledge MCP

"Based on your **{latency_budget}ms** latency budget and **{quality_requirement}** priority, here are the reranking approaches from the knowledge base:"

**Key Reranking & LLM-as-Judge Bias Patterns to Surface (from Knowledge MCP):**

Query Knowledge MCP for current LLM judge bias patterns:
```
Endpoint: get_patterns
Topic: "llm-judge bias types detection mitigation reranking"
Example: "llm-judge bias types detection mitigation reranking"
```

```
Endpoint: get_warnings
Topic: "llm-as-judge reranking sole-quality-signal risks"
Example: "llm-as-judge reranking sole-quality-signal risks"
```

**Synthesis Approach:**
1. Retrieve current bias types from knowledge base (evolves as research updates)
2. Identify detection methods specific to {vector_db} and {latency_sla}
3. Surface mitigation strategies from literature
4. Present warning about cross-validation necessity

**Key Pattern to Surface (from Knowledge MCP):**
> LLM-as-judge introduces systematic biases that vary by model and reranking context. Current knowledge base identifies [specific bias types and frequencies].

**Key Warning to Surface:**
> The knowledge base strongly recommends avoiding LLM-based reranking as your sole quality signal. Cross-validate with human judgment or classical methods (BM25, cross-encoder models). Different reranking methods can have conflicting preferences - this is documented in [current knowledge sources].

Ask: "What latency can you tolerate for reranking? Is reranking quality worth the cost? If using LLM-based reranking, are you aware of potential biases? Let me query for patterns that match your constraints."

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

**B. Context Assembly Configuration (Knowledge-Grounded)**

Query Knowledge MCP for context assembly best practices:

```
Endpoint: get_patterns
Topic: "context assembly formatting {llm_model} {context_window_size}"
Example: "context assembly formatting claude-opus 200k"
```

```yaml
context_assembly:
  format: "[from Knowledge MCP: simple | structured | ranked | hierarchical]"
  separator: "\n---\n"
  max_context_tokens: "[from Knowledge MCP for {llm_model}]"
  note: "Query Knowledge MCP: context budget allocation {llm_context_window}"

  include_metadata: true
  metadata_fields:
    - source
    - page_number
    - relevance_score

  ordering: "[from Knowledge MCP: relevance | chronological | source_grouped]"

  # For structured format
  structure_template: |
    <context>
      <document source="{source}" relevance="{score}">
        {content}
      </document>
    </context>
```

**C. Context Window Management (Knowledge-Grounded)**

Query Knowledge MCP for context budget allocation:

```
Endpoint: search_knowledge
Query: "context window budget allocation {llm_model} {architecture}"
Example: "context window budget allocation claude-opus rag-only"
```

**Context Budget Allocation (Dynamically determined):**
```
Available Context Budget ({llm_context_window} tokens)
         ↓
┌─────────────────────────────┐
│     System Prompt           │  → [from Knowledge MCP for {llm_model}]
├─────────────────────────────┤
│     Retrieved Context       │  → [from Knowledge MCP for {architecture}]
├─────────────────────────────┤
│     Conversation History    │  → [from Knowledge MCP based on use case]
├─────────────────────────────┤
│     User Query              │  → [from Knowledge MCP estimate]
├─────────────────────────────┤
│     Response Buffer         │  → [from Knowledge MCP safety margin]
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

**B. Fallback Configuration (Knowledge-Grounded)**

Query Knowledge MCP for failure handling strategies:

```
Endpoint: get_patterns
Topic: "rag failure handling timeout thresholds {latency_sla}"
Example: "rag failure handling timeout thresholds 200ms"
```

```
Endpoint: get_warnings
Topic: "rag retrieval failure modes handling {architecture}"
Example: "rag retrieval failure modes handling rag-only"
```

```yaml
fallbacks:
  no_results:
    strategy: "[from Knowledge MCP: broaden_search | suggest_alternatives | graceful_fail]"
    message: "I couldn't find relevant information. Could you rephrase?"
    note: "Query Knowledge MCP: no-results fallback strategy {domain}"

  low_confidence:
    threshold: "[from Knowledge MCP for {vector_db} and {quality_tier}]"
    note: "Query Knowledge MCP: confidence threshold {vector_db}"
    strategy: "[from Knowledge MCP: include_disclaimer | ask_clarification | graceful_fail]"

  context_overflow:
    strategy: "[from Knowledge MCP: truncate_oldest | truncate_lowest_score | summarize]"
    note: "Query Knowledge MCP: context overflow handling {llm_model}"

  timeout:
    threshold_ms: "[from Knowledge MCP for {latency_sla}]"
    note: "Query Knowledge MCP: retrieval timeout threshold {latency_sla}"
    strategy: "[from Knowledge MCP: return_partial | cache_fallback | graceful_fail]"
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

Display: **Step 6 Complete - Select an Option:** [A] Analyze RAG pipeline further [Q] Re-query Knowledge MCP with different constraints [P] View progress [C] Continue to Step 7 (Prompt Engineer)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit RAG decisions, allow refinement, then redisplay menu
- IF Q:
  1. Ask user to modify constraints:
     - "What constraints would you like to change?"
     - Options: latency budget, quality priority, cost limits, vector DB, reranking preference
  2. Re-run Knowledge MCP queries with new parameters:
     - `get_patterns` with updated topic
     - `get_decisions` with updated constraints
     - `get_warnings` for new constraint combination
  3. Present updated recommendations based on new query results
  4. Allow user to update decisions if desired
  5. Redisplay menu
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
