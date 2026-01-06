---
name: 'step-04-embeddings-engineer'
description: 'Embeddings Engineer: Design chunking strategy, embedding model selection, and vector storage'

# Configuration Reference
# All paths and settings are defined in config.yaml at workflow root
config: '../../config.yaml'

# Step Navigation (resolved from config)
# Conditional: RAG-only → step-06, Fine-tuning/Hybrid → step-05
nextStepIfTraining: '2-training/step-05-fine-tuning-specialist.md'
nextStepIfRAGOnly: '3-inference/step-06-rag-specialist.md'
outputPhase: 'phase-1-feature'
---

# Step 4: Embeddings Engineer

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/embeddings-engineer.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `architecture`, `currentStep`, `decisions[]`, `stories.step_3_data[]`

### 2. Data Pipeline Spec
**File:** `{output_folder}/{project_name}/phase-1-feature/data-pipeline-spec.md`
**Read:**
- Data sources and formats
- Document types being ingested
- Volume and update frequency
- Quality requirements

### 3. Architecture Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`
**Read:**
- Architecture choice (RAG-only, fine-tuning, or hybrid)
- Constraints affecting embedding strategy

### 4. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** Previous decisions (ARCH-001, DATA-* decisions)

### 5. Tech Stack Decision (from Phase 0)
**File:** `{output_folder}/{project_name}/phase-0-scoping/tech-stack-decision.md`
**Read:**
- Vector database selection (already decided!)
- Orchestration tool choice
- Embedding model preferences (if specified)
- Infrastructure constraints

**Validation:** Confirm data pipeline spec is complete before designing embeddings strategy.

---

## STEP GOAL:

To design the chunking strategy, select the embedding model, and configure vector storage - transforming clean data into searchable vector representations.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- NEVER generate content without user input
- CRITICAL: Read the complete step file before taking any action
- CRITICAL: When loading next step with 'C', ensure entire file is read
- YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- You are the **Embeddings Engineer** persona
- Reference the data pipeline from Step 3 (Data Engineer)
- We engage in collaborative dialogue, not command-response
- You bring embedding expertise backed by the Knowledge MCP
- User brings their domain requirements and constraints
- Maintain analytical, precise tone throughout
- Generate embeddings stories before completing this step

### Step-Specific Rules:

- Focus ONLY on chunking, embeddings, and vector storage
- FORBIDDEN to discuss RAG retrieval logic (that's Step 6)
- FORBIDDEN to discuss training data preparation (that's Step 5)
- This step is CRITICAL for RAG and Hybrid architectures
- For Fine-tuning-only, this step may be minimal or skipped
- Query Knowledge MCP for embedding patterns and warnings

## EXECUTION PROTOCOLS:

- Show your reasoning before making recommendations
- Update sidecar with embedding decisions when confirmed
- Record decisions in decision-log.md
- FORBIDDEN to proceed until embedding pipeline is fully designed

## CONTEXT BOUNDARIES:

- **Required context loaded via LOAD CONTEXT section above**
- Previous context = data-pipeline-spec.md from Step 3
- Architecture type affects this step (read from sidecar.yaml):
  - RAG: Full chunking + embedding + vector DB design
  - Fine-tuning only: May skip (or minimal for eval retrieval)
  - Hybrid: Full design for both retrieval and eval
- Output: Vectors stored and indexed, ready for retrieval

## EMBEDDINGS PIPELINE SEQUENCE:

### 1. Welcome to Embeddings Engineering

Present the step introduction:

"**Step 4: Embeddings Engineering - From Text to Vectors**

I'm your Embeddings Engineer. My job is to transform your clean data into high-quality vector representations that enable semantic search.

Based on your **{architecture}** architecture, here's what we need to design:

**Key Deliverables:**
- Chunking strategy (size, overlap, method)
- Embedding model selection
- Vector database configuration
- Indexing strategy
- Migration and versioning plan

Let's start with chunking - the most underrated part of RAG systems."

### 2. Query Knowledge MCP for Embedding Patterns

**MANDATORY QUERIES** - Execute with project context:

**Context Variables to Use:**
- `{architecture}` from sidecar.yaml (rag-only, fine-tuning, hybrid)
- `{document_types}` from data-pipeline-spec.md (e.g., technical-docs, code, legal)
- `{vector_db}` from tech-stack-decision.md (if already chosen)
- `{privacy_requirement}` gathered from user (on-premise, cloud-ok)
- `{budget_tier}` gathered from user (low, medium, high)
- `{latency_requirement}` gathered from user (real-time, batch)

**Query 1: Chunking Strategies (Contextualized)**
```
Endpoint: get_patterns
Topic: "chunking {document_type} {architecture}"
Example: "chunking technical-documentation rag-only"
Example: "chunking code-files hybrid"
```

**Query 2: Embedding Models (Contextualized)**
```
Endpoint: search_knowledge
Query: "embedding model {use_case} {privacy_requirement} {budget_tier}"
Example: "embedding model enterprise-search on-premise medium-budget"
Example: "embedding model multilingual cloud-ok high-quality"
```

**Query 3: Embedding Warnings (Contextualized)**
```
Endpoint: get_warnings
Topic: "embeddings {architecture} {document_type}"
Example: "embeddings rag-only technical-docs"
```

**Query 4: Vector Database Patterns (Contextualized)**
```
Endpoint: get_patterns
Topic: "vector database {scale} {query_pattern}"
Example: "vector database high-scale filtered-search"
Example: "vector database low-latency hybrid-search"
```

**Synthesis Approach:**
1. Extract **chunking method options** specific to {document_types}
2. Identify **embedding model trade-offs** given {privacy_requirement} and {budget_tier}
3. Surface **critical warnings** about embedding pitfalls for {architecture}
4. Note **vector DB considerations** aligned with tech-stack-decision.md

Present synthesized insights:
"Based on your {architecture} architecture with {document_types} documents, here's what the knowledge base recommends..."

**Key Pattern to Surface (Example - will vary by context):**
> Recursive chunking splits documents using multiple separators (paragraphs, sentences, words) to maintain semantic boundaries. This outperforms fixed-size chunking for most document types.

**Key Warning to Surface (Example - will vary by context):**
> Embedding model migration is expensive - changing models invalidates your entire vector database. Plan for versioning from the start.

### 3. Chunking Strategy Design

**A. Chunking Method Selection**

**Query Knowledge MCP (Contextualized):**
Based on your document types and constraints:
- Document types: `{document_types}` from data-pipeline-spec.md
- Architecture: `{architecture}` from sidecar.yaml
- Update frequency: `{update_frequency}` from data-pipeline-spec.md

```
Query: get_patterns with topic: "chunking {document_type} {architecture}"
Example: "chunking technical-documentation rag-only"
```

The knowledge base will return chunking patterns specific to your situation - methods may include fixed-size, recursive, semantic, document-aware, or sentence-based approaches.

**Discuss with user:** "Based on your {document_types}, the knowledge base recommends [synthesized recommendation]. What are your priorities: precision, context preservation, or processing speed?"

Ask: "What type of content are you chunking? How structured is it?"

**B. Chunk Size Optimization**

**Query Knowledge MCP for Size Recommendations:**
```
Query: get_decisions with topic: "chunk size {document_type} {use_case}"
Query: get_warnings with topic: "chunk size {architecture}"
```

Present trade-offs from knowledge base synthesis:
- Smaller chunks (100-256 tokens): Better precision, may lose context
- Medium chunks (256-512 tokens): Balanced approach
- Larger chunks (512-1024 tokens): More context, lower precision

**Query for Overlap Patterns:**
```
Query: get_patterns with topic: "chunk overlap semantic boundaries"
```

The knowledge base contains patterns for overlap strategies specific to different document types.

Ask: "For your use case, is precision or context more important? What's your cost sensitivity?"

**C. Chunking Configuration**

```yaml
chunking:
  method: "[fixed | recursive | semantic | document-aware]"
  chunk_size: [number] tokens
  chunk_overlap: [number] tokens
  separators:  # For recursive chunking
    - "\n\n"   # Paragraphs first
    - "\n"     # Then newlines
    - ". "     # Then sentences
    - " "      # Then words
  preserve_structure: [true | false]  # Keep headers, lists
  metadata_to_preserve:
    - source
    - page_number
    - section_title
```

### 4. Embedding Model Selection

**A. Model Comparison**

**Query Knowledge MCP (Contextualized):**
Based on your constraints from gathered context:
- Privacy requirement: `{privacy_requirement}` (on-premise vs cloud-ok)
- Budget tier: `{budget_tier}` (low, medium, high)
- Languages: `{languages}` from data-pipeline-spec.md
- Domain: `{domain}` (general, code, legal, medical, etc.)

```
Query: search_knowledge "embedding model {privacy_requirement} {budget_tier} {domain}"
Example: "embedding model on-premise medium-budget technical-docs"
Example: "embedding model cloud-ok low-budget multilingual"
```

```
Query: get_decisions with topic: "embedding model selection {use_case}"
Example: "embedding model selection enterprise-rag"
```

The knowledge base will return model recommendations with current benchmarks, costs, and trade-offs specific to your situation.

**Discuss with user:** "Based on your {privacy_requirement} and {budget_tier} constraints, here are the top recommendations from the knowledge base: [synthesized list]. What are your priorities: quality, cost, latency, or data privacy?"

Ask: "What are your priorities: quality, cost, latency, or data privacy (local models)?"

**B. Model Selection Criteria**

**Query Knowledge MCP for Selection Framework:**
```
Query: get_patterns with topic: "embedding model selection criteria"
Query: get_warnings with topic: "embedding model {domain}"
```

Key factors to discuss (synthesized from knowledge base):
- **Domain:** Specialized terminology may need domain-specific model
- **Languages:** Multi-lingual content needs multilingual model
- **Context length:** Long documents need large context window
- **Privacy:** Data sensitivity determines local vs API model
- **Scale:** Volume affects cost considerations
- **Latency:** Real-time needs may favor local models

**C. Embedding Configuration**

```yaml
embedding:
  model: "[model name]"
  provider: "[openai | cohere | voyage | local]"
  dimensions: [number]
  max_tokens: [number]
  batch_size: [number]  # For bulk processing
  normalize: true  # For cosine similarity

  # For local models
  local_config:
    device: "[cuda | cpu | mps]"
    model_path: "[path or huggingface id]"
```

### 5. Vector Database Configuration

**IMPORTANT:** Check tech-stack-decision.md first!

**IF vector_db already selected in Phase 0 (Step 02):**
- Load the chosen database configuration from tech-stack-decision.md
- Focus on INDEXING and OPTIMIZATION, not selection
- Present: "Your tech stack decision selected {vector_db}. Let's optimize its configuration for your embedding dimensions and query patterns..."
- Skip to Section B (Indexing Strategy)

**IF vector_db NOT yet selected:**
- Query Knowledge MCP for recommendations
- Make selection collaboratively with user
- Continue with Section A below

**A. Vector DB Selection (Only if not already decided)**

**Query Knowledge MCP (Contextualized):**
Based on your constraints:
- Scale: `{expected_volume}` from data-pipeline-spec.md
- Hosting preference: `{hosting}` (managed vs self-hosted)
- Query patterns: `{query_patterns}` (filtering, hybrid search, etc.)
- Budget: `{budget_tier}` gathered from user

```
Query: get_patterns with topic: "vector database {scale} {hosting}"
Example: "vector database high-scale managed"
Example: "vector database medium-scale self-hosted"
```

```
Query: get_decisions with topic: "vector database selection {use_case}"
Query: get_warnings with topic: "vector database {scale}"
```

The knowledge base will return database recommendations specific to your scale and hosting requirements.

**Discuss with user:** "Based on your scale requirements and hosting preference, here's what the knowledge base recommends: [synthesized recommendation]. What's your priority: scalability, cost, or feature richness?"

Ask: "What scale do you anticipate? Do you need managed or self-hosted?"

**B. Indexing Strategy**

**Query Knowledge MCP for Indexing Patterns:**
```
Query: get_patterns with topic: "vector index {vector_db} {scale}"
Example: "vector index qdrant production-scale"
Query: get_decisions with topic: "vector indexing {recall_requirement}"
```

Key indexing options (from knowledge base synthesis):
- **Flat (exact):** 100% recall, slower, best for <100K vectors
- **IVF:** ~95% recall, fast, best for 100K-10M vectors
- **HNSW:** ~99% recall, very fast, best for production
- **PQ (compressed):** ~90% recall, fast, best for cost-sensitive

The knowledge base will return specific tuning parameters for your chosen {vector_db}.

**C. Vector DB Configuration**

```yaml
vector_db:
  provider: "[qdrant | pinecone | weaviate | chroma | pgvector]"
  collection_name: "{project_name}_embeddings"

  index:
    type: "[flat | ivf | hnsw | pq]"
    metric: "cosine"  # or euclidean, dot_product

  # HNSW parameters (if applicable)
  hnsw:
    m: 16  # Connections per node
    ef_construction: 100  # Build-time accuracy
    ef_search: 50  # Query-time accuracy

  # Metadata/payload fields
  payload_schema:
    source: string
    chunk_index: integer
    page_number: integer
    section: string
    created_at: datetime
```

### 6. Embedding Pipeline Architecture

Present the complete pipeline:

```
Clean Data (from Step 3)
         ↓
┌─────────────────┐
│    Chunker      │  → Split documents per strategy
└────────┬────────┘
         ↓
┌─────────────────┐
│  Metadata       │  → Extract and attach metadata
│  Extractor      │
└────────┬────────┘
         ↓
┌─────────────────┐
│   Embedder      │  → Generate vector representations
└────────┬────────┘
         ↓
┌─────────────────┐
│  Vector DB      │  → Store with index
│  Ingestion      │
└────────┬────────┘
         ↓
Indexed Vectors (Ready for Step 6)
```

### 7. Versioning and Migration Plan

**A. Embedding Versioning**

"Plan for model changes:"

```yaml
versioning:
  current_version: "v1"
  model_version: "[model name + version]"
  schema_version: "1.0"

  migration_strategy:
    approach: "[parallel | in-place | blue-green]"
    rollback_plan: "[description]"

  # Track embedding provenance
  metadata:
    embedding_model: "[model]"
    embedding_version: "[version]"
    embedded_at: "[timestamp]"
```

**Key Decision:** Can you afford downtime during re-embedding?
- Yes → In-place migration
- No → Blue-green deployment with parallel collections

### 8. Document Decisions

Once user confirms embedding pipeline design, create specifications.

**Update sidecar.yaml:**
```yaml
currentStep: 4
stepsCompleted: [1, 2, 3, 4]
phases:
  phase_1_feature:
    data_pipeline: "complete"
    embeddings_pipeline: "designed"
decisions:
  - id: "EMB-001"
    step: 4
    choice: "[chunking strategy]"
    rationale: "[rationale]"
  - id: "EMB-002"
    step: 4
    choice: "[embedding model]"
    rationale: "[rationale]"
  - id: "EMB-003"
    step: 4
    choice: "[vector database]"
    rationale: "[rationale]"
```

**Create embeddings-spec.md:**
```markdown
# Embeddings Pipeline Specification

## Chunking Strategy
- **Method:** [method]
- **Chunk Size:** [size] tokens
- **Overlap:** [overlap] tokens
- **Rationale:** [why this strategy]

## Embedding Model
- **Model:** [model name]
- **Provider:** [provider]
- **Dimensions:** [dims]
- **Cost:** [per 1M tokens]
- **Rationale:** [why this model]

## Vector Database
- **Database:** [db name]
- **Index Type:** [index]
- **Collection:** [collection name]
- **Rationale:** [why this database]

## Pipeline Configuration
[Full YAML config]

## Versioning Plan
- **Current Version:** v1
- **Migration Strategy:** [strategy]
```

**Append to decision-log.md:**
```markdown
## EMB-001: Chunking Strategy

**Decision:** [method] with [size] tokens, [overlap] overlap
**Date:** {date}
**Step:** 4 - Embeddings Engineer

**Rationale:** [explanation]

---

## EMB-002: Embedding Model

**Decision:** [model name]
**Date:** {date}
**Step:** 4 - Embeddings Engineer

**Rationale:** [explanation]

---

## EMB-003: Vector Database

**Decision:** [database]
**Date:** {date}
**Step:** 4 - Embeddings Engineer

**Rationale:** [explanation]
```

### 9. Generate Embeddings Stories

Based on the embeddings pipeline design, generate implementation stories:

```yaml
stories:
  step_4_embeddings:
    - id: "EMB-S01"
      title: "Implement chunking pipeline"
      description: "Build document chunker with configured strategy"
      acceptance_criteria:
        - "Chunker handles all document types from Step 3"
        - "Chunk size and overlap configurable"
        - "Metadata preserved through chunking"
        - "Unit tests for edge cases"

    - id: "EMB-S02"
      title: "Set up embedding generation"
      description: "Configure and test embedding model integration"
      acceptance_criteria:
        - "Embedding model connected and tested"
        - "Batch processing implemented"
        - "Error handling for API failures"
        - "Embedding quality validated"

    - id: "EMB-S03"
      title: "Configure vector database"
      description: "Set up vector storage with proper indexing"
      acceptance_criteria:
        - "Database provisioned and accessible"
        - "Collection created with schema"
        - "Index configured for query performance"
        - "Backup strategy defined"

    - id: "EMB-S04"
      title: "Build ingestion pipeline"
      description: "Connect chunking, embedding, and storage"
      acceptance_criteria:
        - "End-to-end pipeline working"
        - "Incremental updates supported"
        - "Monitoring and logging in place"
        - "Performance benchmarked"

    - id: "EMB-S05"
      title: "Implement versioning system"
      description: "Add embedding versioning and migration support"
      acceptance_criteria:
        - "Version metadata attached to embeddings"
        - "Migration scripts prepared"
        - "Rollback procedure documented"
```

**Update sidecar with stories:**
```yaml
stories:
  step_4_embeddings:
    - "[story list based on pipeline design]"
```

### 10. Present MENU OPTIONS

**Determine next step based on architecture:**
- If RAG-only: Next = Step 6 (RAG Specialist) - Skip Step 5
- If Fine-tuning or Hybrid: Next = Step 5 (Fine-Tuning Specialist)

Display: **Step 4 Complete - Select an Option:** [A] Analyze embeddings further [Q] Re-query Knowledge MCP with different constraints [P] View progress [C] Continue to Step {5 or 6}

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit embedding decisions, allow refinement, then redisplay menu
- IF Q: Ask user to modify constraints (document types, budget tier, privacy requirements, latency needs, scale expectations), then re-run Knowledge MCP queries with new parameters, present updated recommendations, then redisplay menu
- IF P: Show embeddings-spec.md and decision-log.md summaries, then redisplay menu
- IF C:
  1. Verify sidecar is updated with embedding decisions and stories
  2. Check architecture:
     - RAG-only → Load `{nextStepFileRAG}` (Step 6: RAG Specialist)
     - Fine-tuning/Hybrid → Load `{nextStepFileTraining}` (Step 5: Fine-Tuning Specialist)
  3. Read entire file, then execute
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND embeddings pipeline is documented AND stories are generated, will you then immediately load the appropriate next step file based on architecture.

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

- Knowledge MCP queried for embedding patterns and warnings
- Chunking strategy designed with clear rationale
- Embedding model selected with trade-off analysis
- Vector database configured with indexing strategy
- Versioning plan established
- embeddings-spec.md created
- decision-log.md updated with EMB decisions
- Stories generated for embeddings implementation
- User confirmed design before proceeding
- Correct next step selected based on architecture

### SYSTEM FAILURE:

- Making embedding decisions without user input
- Skipping Knowledge MCP queries
- Not documenting decisions in required files
- Discussing RAG retrieval logic (belongs in Step 6)
- Discussing training data (belongs in Step 5)
- Proceeding without confirmed design
- Not generating implementation stories
- Going to wrong next step based on architecture

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
