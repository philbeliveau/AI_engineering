---
name: 'step-03-feature-pipeline'
description: 'Phase 1: Design the Feature Pipeline - data collection, processing, and vectorization'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/ai-engineering-workflow'

# File References
thisStepFile: '{workflow_path}/steps/step-03-feature-pipeline.md'
nextStepFileTraining: '{workflow_path}/steps/step-04-training-pipeline.md'
nextStepFileInference: '{workflow_path}/steps/step-05-inference-pipeline.md'
workflowFile: '{workflow_path}/workflow.md'

# Output References
outputFolder: '{output_folder}/{project_name}'
sidecarFile: '{outputFolder}/sidecar.yaml'
projectSpecFile: '{outputFolder}/project-spec.md'
decisionLogFile: '{outputFolder}/decision-log.md'
featureFolder: '{outputFolder}/phase-1-feature'
featureSpecFile: '{featureFolder}/spec.md'
chunkingConfigTemplate: '{featureFolder}/templates/chunking-config.template.yaml'
embeddingConfigTemplate: '{featureFolder}/templates/embedding-config.template.yaml'
---

# Step 3: Phase 1 - Feature Pipeline

## STEP GOAL:

To design the Feature Pipeline that handles data collection, processing, chunking, and vectorization - the foundation of any LLM system.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- ✅ You are an AI Engineering Architect
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring FTI pipeline expertise backed by the Knowledge MCP
- ✅ User brings their domain requirements and constraints
- ✅ Maintain collaborative, technical tone throughout

### Step-Specific Rules:

- 🎯 Focus ONLY on data and feature engineering
- 🚫 FORBIDDEN to discuss model training (Phase 2) or deployment (Phase 3)
- 💬 This phase is critical for both RAG and fine-tuning paths
- 🧠 Query Knowledge MCP for patterns and warnings

## EXECUTION PROTOCOLS:

- 🎯 Show your reasoning before making recommendations
- 💾 Update sidecar when completing feature pipeline design
- 📖 Record decisions in decision-log.md
- 🚫 FORBIDDEN to proceed until feature pipeline is fully designed

## CONTEXT BOUNDARIES:

- Architecture decision from Phase 0 determines focus areas
- RAG-only: Heavy focus on chunking and embedding for retrieval
- Fine-tuning: Focus on data preparation for training
- Hybrid: Both concerns must be addressed

## FEATURE PIPELINE SEQUENCE:

### 1. Welcome to Phase 1

Present the phase introduction:

"**Phase 1: Feature Pipeline - The Data Foundation**

The Feature Pipeline is responsible for transforming raw data into features that your LLM system can use. Based on your **{architecture}** architecture:

**Key Tasks:**
- Identify and connect to data sources
- Design data processing workflows
- Define chunking strategy (critical for RAG)
- Select embedding model and configuration
- Set up vector storage

Let's design this systematically."

### 2. Query Knowledge MCP for Patterns

**MANDATORY QUERIES** - Execute these and synthesize results:

**Query 1: Feature Pipeline Patterns**
```
Endpoint: search_knowledge
Query: "feature pipeline data processing chunking embedding"
```

**Query 2: Data Processing Warnings**
```
Endpoint: get_warnings
Topic: "data processing"
```

**Query 3: Storage Patterns**
```
Endpoint: get_patterns
Topic: "vector database"
```

**Synthesis Approach:**
1. Extract the **pipeline steps** pattern (typically: Clean → Chunk → Embed → Store)
2. Identify **data type considerations** (different content types need different handling)
3. Surface **technology recommendations** with trade-offs
4. Note any **warnings** about common mistakes

Present synthesized insights to user:
"Here's what the knowledge base tells us about feature pipeline design..."

**Key Pattern to Surface:** The FTI (Feature-Training-Inference) architecture separates concerns - the feature pipeline's job is to produce **reusable features** consumed by both training and inference.

### 3. Data Source Identification

**A. Source Types**

"Let's identify your data sources:"

| Source Type | Examples | Considerations |
|-------------|----------|----------------|
| **Documents** | PDFs, Word, Markdown | Need parsing strategy |
| **Databases** | SQL, MongoDB, APIs | Connection management |
| **Web Content** | Websites, wikis | Crawling and updates |
| **Structured Data** | CSVs, JSON, Excel | Schema handling |
| **Code Repositories** | GitHub, GitLab | Code-aware processing |
| **Real-time Streams** | Logs, events | Incremental processing |

Ask: "What data sources will feed your system? List them with approximate volumes."

**B. Data Characteristics**

For each source, gather:

| Characteristic | Question | Impact |
|----------------|----------|--------|
| **Format** | What file/data formats? | Determines parser needed |
| **Volume** | How much data initially? | Affects infrastructure |
| **Update Pattern** | Static, periodic, or streaming? | Determines pipeline type |
| **Quality** | Clean, noisy, or mixed? | Pre-processing needs |
| **Structure** | Highly structured or free-form? | Chunking approach |

### 4. Data Processing Design

**A. Ingestion Pipeline**

"Based on your sources, let's design the ingestion flow:"

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sources   │────▶│   Parsers   │────▶│   Cleaners  │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Storage   │◀────│   Chunkers  │◀────│ Transformers│
└─────────────┘     └─────────────┘     └─────────────┘
```

**Recommended Stack (from Knowledge Base):**
- Storage: MongoDB (raw documents), Qdrant (vectors)
- Processing: Python with async patterns
- Orchestration: ZenML for pipeline management

**B. Pre-processing Steps**

| Step | Purpose | Tools |
|------|---------|-------|
| **Parsing** | Extract text from formats | Docling, pypdf, unstructured |
| **Cleaning** | Remove noise, normalize | Custom rules, regex |
| **Deduplication** | Remove duplicates | MinHash, exact matching |
| **Enrichment** | Add metadata | Entity extraction, classification |

Ask: "What pre-processing challenges do you anticipate with your data?"

### 5. Chunking Strategy Design

**CRITICAL FOR RAG SYSTEMS**

"Chunking is one of the most impactful decisions for retrieval quality."

**Query Knowledge MCP:**
```
Endpoint: search_knowledge
Query: "chunking strategy document splitting text segmentation"
```

**Key Principle from Knowledge Base:**
Different data types require different chunking strategies. The knowledge base emphasizes:
- **Articles/Documents**: Respect structure (headers, paragraphs)
- **Social Content**: Handle formatting, URLs, special characters
- **Code**: Preserve syntax boundaries, function definitions

**A. Chunking Approaches**

Present options and let knowledge base inform the recommendation:

| Strategy | Description | When Knowledge Base Recommends |
|----------|-------------|-------------------------------|
| **Fixed Size** | Split by token count | Uniform content, simple documents |
| **Semantic** | Split by meaning boundaries | Complex documents, varied content |
| **Recursive** | Hierarchical with fallbacks | Mixed content types |
| **Document-Aware** | Respect document structure | Structured docs (code, legal, technical) |

**B. Configuration - Query for Current Best Practices**

```
Endpoint: search_knowledge
Query: "chunk size overlap embedding model context window"
```

**Synthesis Pattern:**
1. What chunk sizes do sources recommend? (typically 512-1024 tokens)
2. What overlap ratios work well? (typically 10-20%)
3. How does embedding model context window affect this?

**C. Two-Snapshot Pattern**

If doing hybrid (RAG + fine-tuning), the knowledge base recommends creating **two data snapshots**:
1. **After cleaning** → Used for fine-tuning training data
2. **After embedding** → Used for RAG retrieval

This affects chunking decisions - fine-tuning may need different granularity than retrieval.

**Query Warnings:**
```
Endpoint: get_warnings
Topic: "chunking"
```

Ask: "Given your document types and use case, what chunking approach makes sense? Let's discuss what the knowledge base recommends for your specific content types."

### 6. Embedding Strategy

**Query Knowledge MCP for Current Recommendations:**
```
Endpoint: search_knowledge
Query: "embedding model selection dimensions context window"
```

```
Endpoint: get_warnings
Topic: "embedding migration"
```

**A. Embedding Model Selection**

Present options based on knowledge base patterns. Key factors to query:
- **Dimensions**: Affects storage cost and search speed
- **Context Window**: Must accommodate your chunk size
- **Deployment**: Local vs API (cost implications)

**Critical Warning from Knowledge Base:**
> Changing embedding models invalidates ALL existing vectors. Different models produce incompatible vector spaces. Plan migration windows carefully.

**Decision Framework:**
| Factor | Question to User | Impact |
|--------|------------------|--------|
| **Cost** | API budget vs local compute? | Determines model hosting |
| **Scale** | How many documents? | Affects dimension choice |
| **Latency** | Real-time or batch? | Local may be faster |
| **Quality** | Precision requirements? | Higher dims = better quality |

**B. Embedding Configuration Pattern**

Query for current best practices:
```
Endpoint: search_knowledge
Query: "embedding batch size normalization prefixes"
```

Key configuration decisions:
- **Batch size**: Balance throughput vs memory
- **Normalization**: Required for cosine similarity
- **Prefixes**: Some models use query/document prefixes (check model docs)

**C. Version Your Choice**

Per knowledge base warnings:
- Store raw text alongside vectors (enables re-embedding)
- Document embedding model version in sidecar
- Plan for migration if model changes

Ask: "What are your constraints for embedding? (Local vs API, cost, latency, scale)"

### 7. Vector Storage Design

**Query Knowledge MCP:**
```
Endpoint: search_knowledge
Query: "vector database storage retrieval filtering"
```

```
Endpoint: get_patterns
Topic: "vector database"
```

**A. Vector Database Selection**

Present options from knowledge base. Key decision factors:
- **Filtering needs**: Do you need metadata filtering during search?
- **Hybrid search**: Need keyword + semantic combined?
- **Scale**: Expected vector count and query load
- **Deployment**: Managed vs self-hosted preference

**Decision Framework:**
| Factor | Self-Hosted | Managed |
|--------|-------------|---------|
| **Control** | Full | Limited |
| **Cost at Scale** | Lower | Higher |
| **Ops Burden** | Higher | Lower |
| **Features** | Varies | Usually complete |

**B. Index Configuration Pattern**

Query for configuration best practices:
```
Endpoint: search_knowledge
Query: "vector index configuration distance metric"
```

Key decisions:
- **Distance Metric**: Cosine (normalized), Dot (unnormalized), Euclidean (spatial)
- **Payload Indexing**: Which metadata fields to index for filtering
- **Sharding**: How to partition large collections

**C. Storage Architecture Pattern**

The FTI pattern from knowledge base recommends:
- **Raw Storage** (e.g., MongoDB): Keep original documents
- **Vector Storage** (e.g., Qdrant): Keep embedded vectors
- **Sync Strategy**: How to keep them synchronized

Ask: "What vector storage requirements do you have? (Filtering, scale, deployment preference)"

### 8. Create Feature Pipeline Spec

Document the complete design:

**Create spec.md in phase-1-feature/:**

```markdown
# Phase 1: Feature Pipeline Spec

## Objective
Design and document the data pipeline that transforms raw sources into queryable features.

## Knowledge Consulted
- `get_patterns: feature pipeline` - [key insights]
- `get_patterns: chunking strategy` - [key insights]
- `get_warnings: data processing` - [warnings to avoid]

## Data Sources

| Source | Type | Volume | Update Pattern |
|--------|------|--------|----------------|
| [Source 1] | [Type] | [Volume] | [Pattern] |
| [Source 2] | [Type] | [Volume] | [Pattern] |

## Processing Pipeline

### Ingestion Flow
[Description of pipeline stages]

### Pre-processing
- Parsing: [approach]
- Cleaning: [rules]
- Enrichment: [metadata added]

## Chunking Strategy

**Approach:** [Fixed/Semantic/Recursive/Document-Aware]
**Configuration:**
- Chunk Size: [value]
- Overlap: [value]
- Separators: [priority list]

**Rationale:** [Why this approach]

## Embedding Configuration

**Model:** [selected model]
**Dimensions:** [value]
**Deployment:** [Local/API]

## Vector Storage

**Database:** [selected database]
**Index Configuration:** [key settings]

## Decisions Made

| ID | Decision | Rationale |
|----|----------|-----------|
| FP-001 | [Chunking choice] | [Why] |
| FP-002 | [Embedding choice] | [Why] |
| FP-003 | [Storage choice] | [Why] |

## Exit Criteria
- [ ] Data sources documented
- [ ] Processing pipeline designed
- [ ] Chunking strategy defined
- [ ] Embedding model selected
- [ ] Vector storage configured
- [ ] Templates generated
```

### 9. Generate Config Templates

Create configuration templates for implementation:

**chunking-config.template.yaml:**
```yaml
# Chunking Configuration
# Decision reference: See decision-log.md#FP-001

chunking:
  strategy: "{{CHUNKING_STRATEGY}}"  # semantic | fixed | recursive | document-aware
  chunk_size: {{CHUNK_SIZE}}          # tokens (recommended: 512-1024)
  overlap: {{OVERLAP}}                # tokens (recommended: 50-100)

  separators:
    - "\n\n"    # Paragraphs first
    - "\n"      # Then lines
    - ". "      # Then sentences
    - " "       # Then words (fallback)

  # Document-aware settings
  respect_headers: {{RESPECT_HEADERS}}
  max_header_depth: {{MAX_HEADER_DEPTH}}

  # Metadata to preserve
  metadata_fields:
    - source
    - document_type
    - created_at
```

**embedding-config.template.yaml:**
```yaml
# Embedding Configuration
# Decision reference: See decision-log.md#FP-002

embedding:
  model: "{{EMBEDDING_MODEL}}"
  dimensions: {{DIMENSIONS}}
  batch_size: {{BATCH_SIZE}}
  normalize: true

  # Model-specific prefixes (if applicable)
  query_prefix: "{{QUERY_PREFIX}}"
  document_prefix: "{{DOC_PREFIX}}"

  # Performance settings
  max_retries: 3
  timeout_seconds: 30
```

### 10. Update Project Files

**Update sidecar.yaml:**
```yaml
currentPhase: 2  # or 3 if RAG-only
stepsCompleted: [1, 2, 3]
decisions:
  # ... previous decisions ...
  - id: "fp-001"
    choice: "[chunking strategy]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_patterns:chunking"
  - id: "fp-002"
    choice: "[embedding model]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_patterns:embedding"
phases:
  phase_1_feature: "complete"
```

**Append to decision-log.md:** (all FP decisions)

**Update project-spec.md:** (add Feature Pipeline section)

### 11. Present MENU OPTIONS

Display: **Phase 1 Complete - Select an Option:** [A] Analyze decisions further [P] View progress [C] Continue to next phase

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit any decision, allow refinement, then redisplay menu
- IF P: Show spec.md summary, then redisplay menu
- IF C:
  1. Verify sidecar is updated
  2. Check architecture:
     - If "rag-only" → Load `{nextStepFileInference}` (skip training)
     - If "fine-tuning" or "hybrid" → Load `{nextStepFileTraining}`
  3. Load, read entire file, then execute appropriate next step
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND all feature pipeline decisions are documented, will you then:

1. Check `architecture` in sidecar.yaml
2. If "rag-only": Load step-05-inference-pipeline.md (SKIP Phase 2)
3. If "fine-tuning" or "hybrid": Load step-04-training-pipeline.md

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Knowledge MCP queried for patterns and warnings
- Data sources documented with volumes and patterns
- Chunking strategy selected with clear rationale
- Embedding model chosen based on requirements
- Vector storage configured
- All config templates generated
- Spec.md created with complete design
- Correct next step loaded based on architecture

### ❌ SYSTEM FAILURE:

- Making decisions without user input
- Skipping Knowledge MCP queries
- Not respecting architecture-based routing (RAG-only skip)
- Not creating config templates
- Discussing model training (belongs in Phase 2)
- Discussing deployment (belongs in Phase 3)

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
