# Tech Stack Selection Decision Tree

**Quick reference for tool selection across AI engineering phases**

---

## Quick Decision Path

```
START: "I'm building an LLM/AI system"
  │
  ├─► Does your use case require frequently-changing external knowledge?
  │   ├─► YES → RAG (Phase 0.5: Information Retrieval)
  │   │   └─► Question: How complex is retrieval logic?
  │   │       ├─► Simple keyword search → LangChain simple retriever
  │   │       ├─► Complex iterative retrieval → Agentic RAG (LangChain/LlamaIndex agents)
  │   │       └─► Multi-step reasoning → Multi-hop RAG with planning
  │   │
  │   └─► NO → Prompt Engineering or Fine-tuning
  │       └─► Question: Is your model too generic for the task?
  │           ├─► YES → Fine-tuning (Phase 2: Training)
  │           └─► NO → Prompt Engineering (Phase 3: Inference only)
  │
  ├─► Question: Do you have production data and infrastructure?
  │   ├─► YES → SageMaker/Vertex AI (full platform)
  │   └─► NO → Start with cloud free tier + open-source
  │
  ├─► Question: What's your team size & operational maturity?
  │   ├─► Startup (1-5 engineers) → Unified cloud platform (SageMaker)
  │   ├─► Scale-up (5-20 engineers) → Cloud + ZenML orchestration
  │   └─► Enterprise (20+ engineers) → Full stack (Airflow + MLflow + cloud)
  │
  └─► Question: Budget constraints?
      ├─► Limited → Open-source (Airflow + PyTorch + self-hosted)
      └─► Adequate → Cloud platform (lower ops overhead)
```

---

## Phase-by-Phase Tool Selection

### PHASE 0: Architecture & Data Strategy

**Key Decision: RAG vs Fine-tuning?**

```
┌──────────────────────────────────────┐
│ Start Here: What's your constraint?  │
└──────────────────────────────────────┘
         │        │           │
         ▼        ▼           ▼
     Speed    Knowledge    Custom
     (days)   (changes     Logic
              often)       (needed)
         │        │           │
    YES │        │ YES    YES │
        │        │            │
        ▼        ▼            ▼
     ┌─────────────────────────────┐
     │ → Use RAG (Default Path)     │
     │ Tools: LangChain/LlamaIndex  │
     │ Vector DB: Qdrant/Pinecone   │
     │ Deployment: Ray Serve/FastAPI │
     └─────────────────────────────┘
              │
         NO   │   (If RAG insufficient)
              ▼
     ┌──────────────────────────────┐
     │ → Add Fine-tuning            │
     │ SFT: Supervised Fine-tuning  │
     │ DPO: Direct Preference Opt.  │
     │ Tools: HuggingFace + ZenML   │
     └──────────────────────────────┘
```

**Tool Selection by Path:**

| Decision | Recommended Tools | Alternative | Cost |
|----------|-------------------|-------------|------|
| **Need RAG** | LangChain + Qdrant | LlamaIndex + Pinecone | $ |
| **Simple Retrieval** | Basic semantic search | BM25 + dense (TwoTower) | $ |
| **Complex Agentic RAG** | LangChain agents + tools | CrewAI or AutoGen | $$ |
| **Need Fine-tuning** | HuggingFace + ZenML | PyTorch + Airflow | $$ |
| **Deployment** | SageMaker Endpoints | Ray Serve on K8s | $$$ |

---

### PHASE 1: Feature & Data Pipeline

**Question Tree:**

```
┌─────────────────────────────────┐
│ Does your data need processing? │
└─────────────────────────────────┘
    ▼
    NO → Store as-is in data warehouse
         Tools: Snowflake / BigQuery / MongoDB

    YES ▼
    ┌──────────────────────────┐
    │ Is processing recurring? │
    └──────────────────────────┘
        ▼
        NO → Script (one-time)
        YES → Automate via orchestration

    ┌────────────────────────────────────┐
    │ Volume & Frequency?                │
    └────────────────────────────────────┘
        ▼
    Small (< 1GB) → Batch script
    Large → Orchestrator needed
        ├─► ZenML (lightweight, ML-focused)
        ├─► Airflow (enterprise)
        └─► Prefect (modern, async)
```

**Specific Tool Recommendations:**

| Component | Recommended | Alternative | When to Use Alt |
|-----------|-------------|-------------|-----------------|
| **Data Ingestion** | Cloud Data Warehouse | Kafka (if streaming) | Real-time data |
| **Feature Store** | Feast (open) or Tecton | Platform-integrated | Experiment tracking |
| **Orchestration** | ZenML | Airflow | Enterprise gov. required |
| **Data Quality** | Great Expectations | Custom validators | Lightweight projects |
| **Version Control** | DVC (if ML data) | Git LFS | Collaboration needed |

**Infrastructure Checklist:**
```
Phase 1 Readiness Checklist:
- [ ] Data pipeline automated (not manual)
- [ ] CI/CD pipeline with: gitleaks + linting + tests
- [ ] Data quality checks integrated
- [ ] Data lineage tracking enabled
- [ ] Data versioning strategy defined
- [ ] Compliance documentation in place
```

---

### PHASE 2: Training Pipeline (If Fine-tuning Chosen)

**Decision: Platform vs DIY?**

```
┌───────────────────────────┐
│ Budget & Operational Load │
└───────────────────────────┘
    │
    ├─► < 50K samples → SageMaker (managed)
    │   Cost: Predictable | Ops: Low
    │
    ├─► 50K-1M samples → SageMaker or self-hosted
    │   Cost: Compare | Ops: Medium
    │
    └─► > 1M samples → Self-hosted likely cheaper
        Cost: Lower | Ops: High
```

**Detailed Tool Selection:**

| Layer | Recommended | Alternative | Cost |
|-------|-------------|-------------|------|
| **Training Framework** | Hugging Face Transformers | PyTorch raw | $/month |
| **Distributed Training** | FSDP (PyTorch native) | DeepSpeed | $/month |
| **Training Orchestration** | SageMaker Training Jobs | ZenML + custom | $$/month |
| **Model Registry** | MLflow | SageMaker Model Registry | $/month |
| **Experiment Tracking** | Weights & Biases | MLflow | $/month |
| **Infrastructure** | SageMaker managed | EC2 + Docker | Varies |

**Training Stack by Scale:**

**Small Projects (1-2 engineers):**
```
HuggingFace Datasets
    ↓
HuggingFace Trainer (on single GPU)
    ↓
MLflow Model Registry
    ↓
SageMaker Endpoints (for serving)
Cost: ~$500-2000/month
```

**Growing Projects (5-10 engineers):**
```
Hugging Face Hub + DVC
    ↓
ZenML pipeline → SageMaker Training Jobs
    ↓
MLflow + Weights & Biases tracking
    ↓
SageMaker or Ray Serve (deployment)
Cost: ~$2000-5000/month
```

**Enterprise (20+ engineers):**
```
Data Warehouse (Snowflake)
    ↓
Feature Store (Tecton)
    ↓
Airflow → SageMaker Training
    ↓
MLflow + Weights & Biases + Custom metrics
    ↓
Kubernetes (self-hosted serving)
Cost: ~$10,000+/month
```

---

### PHASE 3: Inference & Deployment

**Decision Tree: Inference Serving**

```
┌──────────────────────────┐
│ What are you serving?    │
└──────────────────────────┘
    │
    ├─► LLM with RAG
    │   ├─► Low latency (<100ms)?
    │   │   └─► YES → vLLM (GPU-optimized)
    │   │   └─► NO → Ray Serve
    │   │
    │   └─► API-based access?
    │       └─► YES → SageMaker Endpoints
    │       └─► NO → Self-hosted FastAPI
    │
    └─► Fine-tuned model (traditional ML)
        ├─► Batch predictions?
        │   └─► Airflow/Spark jobs
        │
        └─► Real-time predictions?
            ├─► Scale < 1K req/sec → FastAPI
            ├─► Scale 1K-10K req/sec → Ray Serve
            └─► Scale > 10K req/sec → Kubernetes
```

**Specific Serving Tool Recommendations:**

| Use Case | Tool | GPU Required | Latency | Ops Load |
|----------|------|--------------|---------|----------|
| **LLM RAG** | vLLM | A100/A10 | <500ms | Medium |
| **Managed Simplicity** | SageMaker | Managed | <1s | Low |
| **Distributed Scaling** | Ray Serve | Auto-scaled | <2s | Medium |
| **Custom Microservice** | FastAPI | Optional | <200ms | High |
| **Batch Processing** | Spark/Airflow | CPU ok | Hours | Low |

**Microservice Architecture Template:**

```yaml
# Business Logic Service (CPU, can be modest)
service: business_logic
runtime: FastAPI + Python
scaling: Auto (based on req/sec)
deployment: Container / Kubernetes

# LLM Service (GPU, resource-heavy)
service: llm_inference
runtime: vLLM or TensorRT
scaling: Auto (based on GPU utilization)
deployment: Kubernetes with GPU nodes

# Coordination
framework: ZenML or custom FastAPI
communication: gRPC or REST
caching: Semantic caching (Qdrant) for cost reduction
```

**Cost Optimization Pattern: Semantic Caching**
```
User Query
    ↓
Embed query using embedding model
    ↓
Search Qdrant for semantically similar cached responses
    ↓
If similar match found (>0.95 similarity):
    ├─► Return cached response (NO LLM CALL)
    ├─► Save cost: ~95% reduction if high hit rate
    └─► Risk: May return stale response

If no match:
    ├─► Call LLM normally
    ├─► Cache response
    └─► Return to user
```

**Phase 3 Checklist:**
```
- [ ] Inference latency < 500ms (or SLA met)
- [ ] Error rate < 1%
- [ ] Input validation implemented
- [ ] Rate limiting configured
- [ ] Semantic caching for LLM cost reduction
- [ ] Monitoring and alerting enabled
- [ ] Canary deployment tested
- [ ] Rollback plan documented
```

---

### PHASE 4: Evaluation & Quality Gates

**Evaluation Framework Decision:**

```
┌────────────────────────────────┐
│ What are you evaluating?       │
└────────────────────────────────┘
    │
    ├─► LLM Output Quality
    │   ├─► Fully automated?
    │   │   ├─► BLEU/ROUGE → HuggingFace Evaluate
    │   │   ├─► Semantic similarity → Sentence Transformers
    │   │   └─► Task-specific → Custom metrics
    │   │
    │   └─► Human-in-loop?
    │       ├─► LLM-as-judge → GPT-4 evaluation (cost!)
    │       └─► Human review → Annotation tools
    │
    ├─► Retrieval Quality (for RAG)
    │   ├─► Precision/Recall → TREC eval
    │   ├─► MRR/NDCG → IR metrics
    │   └─► Semantic relevance → BERTScore
    │
    ├─► Production Metrics
    │   ├─► Drift detection → EvidentlyAI
    │   ├─► Distribution shift → Custom thresholds
    │   └─► Cost tracking → Token counting
    │
    └─► Automated Quality Gate
        ├─► Pass threshold → Deploy
        └─► Fail threshold → Block (needs investigation)
```

**Tool Selection Matrix:**

| Metric Type | Tool | Cost | Effort |
|-------------|------|------|--------|
| **BLEU/ROUGE** | HuggingFace Evaluate | Free | Low |
| **LLM-as-judge** | GPT-4 via API | $$ | Low |
| **Drift Detection** | EvidentlyAI | $ | Medium |
| **Custom Metrics** | Python + validation | Free | High |
| **Human Review** | Annotation tool | $ | High |

---

### PHASE 5: Operations & Monitoring

**Monitoring & Operations Architecture:**

```
┌──────────────────────────────┐
│ What's your monitoring need? │
└──────────────────────────────┘
    │
    ├─► Unified view (recommended)
    │   └─► Dataiku or SageMaker Dashboard
    │       Shows: Data health + Model perf + Inference quality
    │
    ├─► Best-of-breed monitoring
    │   ├─► Infrastructure → Prometheus + Grafana
    │   ├─► Models → MLflow + Custom
    │   ├─► LLM-specific → Custom dashboards
    │   └─► Drift → EvidentlyAI
    │
    └─► Automated Retraining
        ├─► Trigger: Performance drops > 5%
        ├─► Pipeline: Orchestrator (Airflow/ZenML)
        ├─► Validation: Compare to current model
        └─► Deploy: If performance improved
```

**Tool Stack for Operations:**

| Layer | Tool | Alternative | When to Use Alt |
|-------|------|-------------|-----------------|
| **Infrastructure Monitoring** | Prometheus + Grafana | Datadog | Cloud-native preference |
| **Model Metrics** | MLflow UI | Weights & Biases | Experiment tracking needed |
| **Drift Detection** | EvidentlyAI | Custom rules | Simple scenarios |
| **Retraining Orchestration** | Airflow or ZenML | SageMaker Pipelines | Full managed |
| **Alerts** | PagerDuty | Slack webhooks | Just alerts vs incidents |
| **Dashboards** | Grafana | Dataiku | Unified view vs specialized |

**Operations Checklist:**
```
- [ ] Retraining pipeline automated
- [ ] Performance degradation detection active
- [ ] Model registry integration for rollback
- [ ] Unified monitoring dashboard deployed
- [ ] Data collection for continuous improvement
- [ ] Incident response runbooks documented
- [ ] Backup and disaster recovery tested
- [ ] Compliance monitoring (if needed)
```

---

## Quick Reference: Tool Comparison

### Orchestration Tools

| Tool | Complexity | ML-Focus | Enterprise | Learn Time | Cost |
|------|-----------|----------|-----------|-----------|------|
| **ZenML** | Low | High | Medium | 1-2 weeks | Free ($) |
| **Airflow** | High | Low | High | 2-4 weeks | Free ($) |
| **Prefect** | Medium | Medium | Medium | 2 weeks | Free ($) |
| **SageMaker Pipelines** | Low | High | High | 1 week | Included in SageMaker |
| **Kubeflow** | High | High | Enterprise | 4+ weeks | Free (infrastructure $) |

**Recommendation:** Start with ZenML for ML-specific needs; graduate to Airflow if enterprise governance required.

---

### Model Registry & Experiment Tracking

| Tool | Scope | UI Quality | Cloud Support | Cost |
|------|-------|-----------|---------------|------|
| **MLflow** | Both | Basic | Limited | Free |
| **Weights & Biases** | Tracking | Excellent | Native | Free/$$ |
| **SageMaker Model Registry** | Registry only | Good | Native | Included |
| **Dataiku Model Registry** | Platform | Excellent | Native | Included |
| **Neptune.ai** | Tracking | Good | Native | Free/$$ |

**Recommendation:** MLflow for open-source; Weights & Biases for tracking features; cloud platform registries if using managed service.

---

### Vector Databases (for RAG)

| Database | Scalability | Filtering | Ease | Cost |
|----------|-------------|-----------|------|------|
| **Qdrant** | Medium-High | Excellent | Easy | $ (self-hosted) |
| **Pinecone** | High | Good | Easy | $$ (managed) |
| **Weaviate** | Medium | Good | Medium | $ or $$ |
| **Milvus** | High | Excellent | Hard | $ (self-hosted) |
| **Chroma** | Low | None | Very easy | Free (in-memory) |

**Recommendation:** Qdrant for serious projects (mentioned in knowledge base); Pinecone for rapid prototyping.

---

## Decision Template for Your Project

**Fill this out before selecting tools:**

```
PROJECT CONTEXT
─────────────────
Team size: _____ engineers
Timeline to production: _____ weeks
Budget: $_____ / month
Infrastructure preference: (Cloud / Self-hosted / Hybrid)
Data volume: _____ GB/month
Inference QPS: _____ requests/sec


ARCHITECTURE DECISIONS
──────────────────────
[ ] RAG sufficient for use case?
[ ] Fine-tuning required?
[ ] Production data in warehouse?
[ ] Real-time inference needed?


TOOL SELECTIONS
───────────────
Data Pipeline:
  Warehouse: ________________
  Orchestration: ________________

Training (if fine-tuning):
  Framework: ________________
  Model Registry: ________________

Inference:
  Serving: ________________
  Deployment: ________________

Operations:
  Monitoring: ________________
  Retraining: ________________


ESTIMATED COSTS
───────────────
Infrastructure: $____ / month
Tools/SaaS: $____ / month
People (if applicable): $____ / month
Total: $____ / month


CONFIDENCE & RISK
─────────────────
Confidence in selections: (Low / Medium / High)
Riskiest assumption: ________________
Validation plan: ________________
```

---

## Example Stacks for Different Projects

### Example 1: Startup Building RAG Chatbot (3 engineers, $2K/month budget)

```yaml
Phase 1 (Data):
  Source: Simple JSON/CSV
  Warehouse: Supabase PostgreSQL
  Orchestration: Prefect Cloud free tier

Phase 2: N/A (RAG only, no fine-tuning)

Phase 3 (Inference):
  Framework: LangChain + Qdrant (self-hosted)
  Serving: FastAPI on AWS ECS
  Deployment: Docker

Phase 4 (Evaluation):
  Metrics: Custom (user ratings + manual review)
  Framework: Python + spreadsheet

Phase 5 (Operations):
  Monitoring: Basic CloudWatch + custom logs
  Alerting: Slack webhooks

Estimated Cost: $500 infrastructure + $1500 team ops = $2K/month
```

### Example 2: Scale-up Fine-tuning LLM for Domain Task (10 engineers, $10K/month budget)

```yaml
Phase 1 (Data):
  Source: Production database
  Warehouse: Snowflake
  Orchestration: ZenML + Airflow

Phase 2 (Training):
  Framework: Hugging Face Transformers
  Platform: AWS SageMaker Training
  Registry: MLflow
  Tracking: Weights & Biases

Phase 3 (Inference):
  Framework: LangChain + fine-tuned model + RAG
  Serving: SageMaker Endpoints
  Optimization: Semantic caching with Qdrant

Phase 4 (Evaluation):
  Metrics: BLEU/ROUGE + LLM-as-judge + human review
  Framework: Hugging Face Evaluate + custom

Phase 5 (Operations):
  Monitoring: Prometheus + Grafana + W&B dashboard
  Retraining: Airflow pipeline + quality gates
  Incident: PagerDuty + runbooks

Estimated Cost: $4K infrastructure + $6K tooling = $10K/month
```

### Example 3: Enterprise Multi-Team ML Platform (50+ engineers, $50K+/month budget)

```yaml
Phase 1 (Data):
  Warehouse: Snowflake + Data Lake
  Feature Store: Tecton
  Orchestration: Airflow + in-house tools

Phase 2 (Training):
  Framework: PyTorch + Hugging Face
  Platform: Kubernetes + custom scheduler
  Registry: Internal + MLflow
  Tracking: Databricks + custom logging

Phase 3 (Inference):
  Frameworks: Multiple (LLM, traditional ML, etc.)
  Serving: Kubernetes + KServe or Seldon Core
  Infrastructure: Dedicated GPU nodes + autoscaling

Phase 4 (Evaluation):
  Metrics: Comprehensive automated + manual review
  Framework: Internal testing platform
  A/B Testing: Dedicated framework

Phase 5 (Operations):
  Monitoring: Prometheus + Grafana + internal dashboards
  Logging: ELK stack or Datadog
  Incident Management: PagerDuty + Slack integration
  Retraining: Airflow with approval workflows

Estimated Cost: $40K infrastructure + $10K tooling = $50K+/month
```

---

## Next Steps

1. **Fill out decision template** above for your specific project
2. **Start with Phase 1** and validate data pipeline
3. **Query Knowledge MCP** for specific tool guidance as needed
4. **Validate with team** before finalizing selections
5. **Plan onboarding** for selected tools (2-4 weeks per major tool)

---

**Last Updated:** 2026-01-06
**Status:** Ready for workflow agent implementation
