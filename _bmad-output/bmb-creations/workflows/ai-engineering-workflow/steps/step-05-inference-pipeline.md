---
name: 'step-05-inference-pipeline'
description: 'Phase 3: Design the Inference Pipeline - RAG setup, deployment, and serving'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/ai-engineering-workflow'

# File References
thisStepFile: '{workflow_path}/steps/step-05-inference-pipeline.md'
nextStepFile: '{workflow_path}/steps/step-06-evaluation-and-gate.md'
workflowFile: '{workflow_path}/workflow.md'

# Output References
outputFolder: '{output_folder}/{project_name}'
sidecarFile: '{outputFolder}/sidecar.yaml'
projectSpecFile: '{outputFolder}/project-spec.md'
decisionLogFile: '{outputFolder}/decision-log.md'
inferenceFolder: '{outputFolder}/phase-3-inference'
inferenceSpecFile: '{inferenceFolder}/spec.md'
deploymentConfigTemplate: '{inferenceFolder}/templates/deployment-config.template.yaml'
---

# Step 5: Phase 3 - Inference Pipeline

## STEP GOAL:

To design the Inference Pipeline that serves predictions - including RAG setup, model deployment, API design, and serving infrastructure.

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

- 🎯 Focus ONLY on inference and deployment
- 🚫 FORBIDDEN to discuss training (Phase 2) or evaluation details (Phase 4)
- 💬 This is where RAG systems come together
- 🧠 Query Knowledge MCP for deployment patterns and decisions

## EXECUTION PROTOCOLS:

- 🎯 Show your reasoning before making recommendations
- 💾 Update sidecar when completing inference pipeline design
- 📖 Record decisions in decision-log.md
- 🚫 FORBIDDEN to proceed until inference pipeline is fully designed

## CONTEXT BOUNDARIES:

- Architecture from Phase 0 determines if this is RAG-only, fine-tuned model, or hybrid
- Feature Pipeline (Phase 1) provides vectors and retrieval infrastructure
- Training Pipeline (Phase 2) provides fine-tuned model (if applicable)
- This phase brings everything together for serving

## INFERENCE PIPELINE SEQUENCE:

### 1. Welcome to Phase 3

Present the phase introduction based on architecture:

**For RAG-only:**
"**Phase 3: Inference Pipeline - Bringing RAG to Life**

This is where your RAG system comes together. We'll design how queries flow through retrieval, augmentation, and generation.

**Key Components:**
- Query processing and embedding
- Vector retrieval and reranking
- Context assembly and prompting
- LLM generation
- Response post-processing
- API and deployment"

**For Fine-tuning or Hybrid:**
"**Phase 3: Inference Pipeline - Deploying Your Model**

This is where your trained model meets the real world. We'll design the serving infrastructure.

**Key Components:**
- Model serving and optimization
- RAG integration (if hybrid)
- API design
- Scaling and performance
- Deployment infrastructure"

### 2. Query Knowledge MCP for Patterns

**Query 1: RAG Patterns**
```
Endpoint: get_patterns
Topic: RAG retrieval
```

**Query 2: Deployment Patterns**
```
Endpoint: get_patterns
Topic: model deployment
```

**Query 3: Deployment Decisions**
```
Endpoint: get_decisions
Topic: deployment architecture
```

**Query 4: Inference Warnings**
```
Endpoint: get_warnings
Topic: inference pipeline
```

Present relevant patterns and warnings to user.

### 3. RAG Pipeline Design (If RAG-only or Hybrid)

**A. Retrieval Flow**

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐
│  Query  │────▶│   Embed     │────▶│   Search    │
└─────────┘     └─────────────┘     └─────────────┘
                                          │
                                          ▼
┌─────────┐     ┌─────────────┐     ┌─────────────┐
│ Response│◀────│   Generate  │◀────│   Rerank    │
└─────────┘     └─────────────┘     └─────────────┘
```

**B. Retrieval Configuration**

| Parameter | Options | Trade-off |
|-----------|---------|-----------|
| **Top-K** | 3-10 documents | More = comprehensive, Less = focused |
| **Similarity Threshold** | 0.7-0.9 | Higher = more relevant, fewer results |
| **Reranking** | None, Cross-encoder, LLM | More accurate, higher latency |
| **Hybrid Search** | Dense-only, BM25+Dense | Better recall, more complex |

**C. Context Assembly**

| Strategy | Description | Best For |
|----------|-------------|----------|
| **Simple Concatenation** | Join retrieved chunks | Single-topic queries |
| **Relevance Ordering** | Most relevant first | Limited context window |
| **Hierarchical** | Summary + details | Complex documents |
| **Interleaved** | Mix sources | Multi-source queries |

Ask: "How should we configure retrieval for your use case? Consider query patterns and accuracy requirements."

### 4. Model Serving Design

**A. Serving Options**

| Option | Latency | Throughput | Cost | Complexity |
|--------|---------|------------|------|------------|
| **API (OpenAI, Anthropic)** | Low | High | Per-token | Low |
| **Self-hosted (vLLM)** | Variable | High | Infrastructure | Medium |
| **Serverless (SageMaker)** | Medium | Auto-scale | Per-request | Medium |
| **Edge (Ollama, llama.cpp)** | Variable | Limited | Hardware | Low |

**Recommended for RAG-only:** API (Claude, GPT-4)
- No model management overhead
- Predictable latency
- Pay-per-use

**Recommended for Fine-tuned:** vLLM or SageMaker
- Serve custom model
- Full control
- Scalable

**Query Knowledge MCP:**
```
Endpoint: get_decisions
Topic: sync vs async inference
```

**B. Model Optimization (For Self-Hosted)**

| Technique | Speed-up | Quality Impact |
|-----------|----------|----------------|
| **Quantization (INT8/INT4)** | 2-4x | Minor |
| **Speculative Decoding** | 2-3x | None |
| **Continuous Batching** | 5-10x throughput | None |
| **KV Cache Optimization** | 1.5-2x | None |

Ask: "What are your latency and throughput requirements? What's your infrastructure budget?"

### 5. Prompt Engineering

**A. System Prompt Design**

"The system prompt defines your AI's behavior and context usage."

```markdown
# System Prompt Template

You are [ROLE] specialized in [DOMAIN].

## Context Usage
When answering questions, use the provided context to ground your responses.
If the context doesn't contain relevant information, say so clearly.

## Response Format
[Define expected output format]

## Constraints
- [List behavioral constraints]
- [List safety guidelines]
```

**B. RAG Prompt Structure**

```markdown
# User Prompt Template

## Context
{retrieved_documents}

## Question
{user_query}

## Instructions
Answer based on the provided context. If the context doesn't contain
sufficient information, acknowledge the limitation.
```

**C. Few-Shot Examples (If Applicable)**

| Use Case | When to Use | Example Count |
|----------|-------------|---------------|
| **Classification** | Ambiguous categories | 3-5 |
| **Extraction** | Specific formats | 2-3 |
| **Generation** | Style matching | 1-2 |

Ask: "Let's design your prompt structure. What behavior and format do you need?"

### 6. API Design

**A. Endpoint Structure**

```yaml
# API Endpoints
endpoints:
  # Main inference endpoint
  - path: /v1/query
    method: POST
    request:
      query: string
      conversation_id: string (optional)
      parameters:
        temperature: float (0-2)
        max_tokens: int
        stream: boolean
    response:
      answer: string
      sources: array
      metadata: object

  # Health check
  - path: /health
    method: GET
    response:
      status: string
      version: string

  # Feedback endpoint (for improvement)
  - path: /v1/feedback
    method: POST
    request:
      query_id: string
      rating: int (1-5)
      comment: string (optional)
```

**B. Authentication & Rate Limiting**

| Component | Options | Recommendation |
|-----------|---------|----------------|
| **Auth** | API Key, OAuth, JWT | API Key for simplicity |
| **Rate Limit** | Per-key, per-IP | Per-key with tiers |
| **Quotas** | Requests, tokens | Both |

### 7. Caching Strategy

**Query Knowledge MCP:**
```
Endpoint: get_patterns
Topic: semantic caching
```

**A. Cache Layers**

| Layer | What to Cache | TTL | Impact |
|-------|---------------|-----|--------|
| **Query Embedding** | Embedded queries | Long | Reduce embedding calls |
| **Retrieval Results** | Search results | Medium | Reduce vector search |
| **Semantic Cache** | Similar query → response | Short | Reduce LLM calls |
| **Response Cache** | Exact query → response | Short | Fastest response |

**B. Cache Configuration**

```yaml
caching:
  embedding_cache:
    enabled: true
    backend: redis
    ttl_hours: 24

  retrieval_cache:
    enabled: true
    backend: redis
    ttl_minutes: 60

  semantic_cache:
    enabled: {{ENABLE_SEMANTIC_CACHE}}
    similarity_threshold: 0.95
    ttl_minutes: 30

  response_cache:
    enabled: {{ENABLE_RESPONSE_CACHE}}
    ttl_minutes: 5
```

Ask: "What caching strategy makes sense for your query patterns?"

### 8. Deployment Infrastructure

**A. Architecture Pattern**

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
         │ API Pod │    │ API Pod │    │ API Pod │
         └────┬────┘    └────┬────┘    └────┬────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐        ┌─────▼─────┐       ┌─────▼─────┐
    │  Redis  │        │  Qdrant   │       │ LLM API   │
    │ (Cache) │        │ (Vectors) │       │ (or vLLM) │
    └─────────┘        └───────────┘       └───────────┘
```

**B. Deployment Options**

| Platform | Best For | Complexity |
|----------|----------|------------|
| **Docker Compose** | Development, small scale | Low |
| **Kubernetes** | Production, scaling | High |
| **AWS ECS/Fargate** | Managed containers | Medium |
| **Railway/Render** | Quick deployment | Low |
| **SageMaker Endpoints** | ML-specific | Medium |

**Recommended (from Knowledge Base):**
- Development: Docker Compose
- Production: Kubernetes or AWS ECS

Ask: "What's your deployment target? (Cloud provider, scale requirements)"

### 9. Performance Requirements

**A. Latency Targets**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **P50 Latency** | < 2s | Median response time |
| **P99 Latency** | < 5s | Worst case |
| **Time to First Token** | < 500ms | For streaming |
| **Retrieval Latency** | < 200ms | Vector search |

**B. Throughput Targets**

| Metric | Target | Notes |
|--------|--------|-------|
| **Concurrent Users** | [define] | Active simultaneous |
| **Requests/Minute** | [define] | Peak load |
| **Tokens/Second** | [define] | Generation speed |

Ask: "What are your performance requirements? (latency, throughput, scale)"

### 10. Create Inference Pipeline Spec

**Create spec.md in phase-3-inference/:**

```markdown
# Phase 3: Inference Pipeline Spec

## Objective
Design the serving infrastructure that brings the AI system to users.

## Knowledge Consulted
- `get_patterns: RAG retrieval` - [key insights]
- `get_patterns: model deployment` - [key insights]
- `get_decisions: deployment architecture` - [key insights]
- `get_warnings: inference pipeline` - [warnings to avoid]

## Architecture Summary

**Type:** [RAG-only | Fine-tuned | Hybrid]
**Model:** [Model being served]
**Serving Method:** [API | Self-hosted | Hybrid]

## RAG Configuration (if applicable)

### Retrieval
- Top-K: [value]
- Similarity Threshold: [value]
- Reranking: [method or none]
- Hybrid Search: [yes/no]

### Context Assembly
- Strategy: [method]
- Max Context Tokens: [value]

## Model Serving

### Infrastructure
- Platform: [Docker/K8s/ECS/etc]
- Instance Type: [if applicable]
- Auto-scaling: [config]

### Optimization
- Quantization: [method or none]
- Batching: [config]

## Prompt Design

### System Prompt
[Include actual system prompt]

### User Prompt Template
[Include actual template]

## API Design

### Endpoints
[List with request/response formats]

### Authentication
- Method: [API Key/OAuth/etc]
- Rate Limiting: [config]

## Caching Strategy

[Describe caching layers and config]

## Performance Targets

| Metric | Target |
|--------|--------|
| P50 Latency | [value] |
| P99 Latency | [value] |
| Throughput | [value] |

## Decisions Made

| ID | Decision | Rationale |
|----|----------|-----------|
| IP-001 | [Serving method] | [Why] |
| IP-002 | [Caching strategy] | [Why] |
| IP-003 | [Deployment platform] | [Why] |

## Exit Criteria
- [ ] RAG flow designed (if applicable)
- [ ] Model serving configured
- [ ] Prompts designed
- [ ] API defined
- [ ] Caching strategy set
- [ ] Performance targets defined
- [ ] Deployment config ready
```

### 11. Generate Deployment Config Template

**deployment-config.template.yaml:**
```yaml
# Deployment Configuration
# Decision reference: See decision-log.md#IP-xxx

# Service Configuration
service:
  name: "{{SERVICE_NAME}}"
  version: "{{VERSION}}"
  replicas: {{REPLICAS}}

# Model Configuration
model:
  provider: "{{MODEL_PROVIDER}}"  # openai | anthropic | self-hosted
  name: "{{MODEL_NAME}}"

  # Self-hosted specific
  self_hosted:
    image: "{{MODEL_IMAGE}}"
    quantization: "{{QUANTIZATION}}"
    gpu_memory: "{{GPU_MEMORY}}"

# RAG Configuration
rag:
  enabled: {{RAG_ENABLED}}

  retrieval:
    top_k: {{TOP_K}}
    similarity_threshold: {{SIMILARITY_THRESHOLD}}
    reranking: {{RERANKING_ENABLED}}
    reranker_model: "{{RERANKER_MODEL}}"

  context:
    strategy: "{{CONTEXT_STRATEGY}}"
    max_tokens: {{MAX_CONTEXT_TOKENS}}

# Vector Database
vector_db:
  provider: "{{VECTOR_DB}}"  # qdrant | pinecone | etc
  host: "{{VECTOR_HOST}}"
  collection: "{{COLLECTION_NAME}}"

# Caching
cache:
  redis_url: "{{REDIS_URL}}"

  embedding_cache:
    enabled: {{EMBEDDING_CACHE}}
    ttl_hours: {{EMBEDDING_TTL}}

  semantic_cache:
    enabled: {{SEMANTIC_CACHE}}
    threshold: {{SEMANTIC_THRESHOLD}}
    ttl_minutes: {{SEMANTIC_TTL}}

# API Configuration
api:
  host: "0.0.0.0"
  port: {{API_PORT}}

  auth:
    enabled: {{AUTH_ENABLED}}
    method: "{{AUTH_METHOD}}"

  rate_limit:
    requests_per_minute: {{RATE_LIMIT}}

# Performance
performance:
  timeout_seconds: {{TIMEOUT}}
  max_concurrent: {{MAX_CONCURRENT}}

# Monitoring
monitoring:
  metrics_enabled: true
  traces_enabled: {{TRACING_ENABLED}}
  log_level: "{{LOG_LEVEL}}"
```

### 12. Update Project Files

**Update sidecar.yaml:**
```yaml
currentPhase: 4
stepsCompleted: [1, 2, 3, 4, 5]  # or [1, 2, 3, 5] if RAG-only
decisions:
  # ... previous decisions ...
  - id: "ip-001"
    choice: "[serving method]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_patterns:deployment"
  - id: "ip-002"
    choice: "[caching strategy]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_patterns:semantic-caching"
phases:
  phase_3_inference: "complete"
```

**Append to decision-log.md:** (all IP decisions)

**Update project-spec.md:** (add Inference Pipeline section)

### 13. Present MENU OPTIONS

Display: **Phase 3 Complete - Select an Option:** [A] Analyze decisions further [P] View progress [C] Continue to Phase 4

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit any decision, allow refinement, then redisplay menu
- IF P: Show spec.md summary, then redisplay menu
- IF C:
  1. Verify sidecar is updated
  2. Load, read entire file, then execute `{nextStepFile}` (Evaluation + Gate)
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND all inference pipeline decisions are documented, will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Phase 4: Evaluation and Quality Gate.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Knowledge MCP queried for patterns and decisions
- RAG flow designed (if applicable)
- Model serving method selected with rationale
- Prompts designed and documented
- API structure defined
- Caching strategy set
- Performance targets established
- Deployment config template generated
- Spec.md complete

### ❌ SYSTEM FAILURE:

- Making decisions without user input
- Skipping Knowledge MCP queries
- Not addressing RAG configuration for RAG/hybrid architectures
- Not creating deployment config template
- Discussing training (belongs in Phase 2)
- Discussing detailed evaluation (belongs in Phase 4)

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
