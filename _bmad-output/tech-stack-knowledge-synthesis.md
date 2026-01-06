# Tech Stack Selection Guidance: Knowledge MCP Analysis

**Date:** 2026-01-06
**Status:** Complete synthesis from Knowledge MCP database
**Source:** 1,684 extractions across 7 types from AI engineering literature (58 sources)

---

## Executive Summary

The Knowledge MCP contains comprehensive guidance for tech stack selection across the AI/ML engineering workflow. This document synthesizes findings across:

- **Decision Points:** 356 structured decisions with trade-offs
- **Patterns:** 314 reusable implementation patterns
- **Warnings:** 335 anti-patterns and pitfalls
- **Methodologies:** 182 structured approaches
- **Workflows:** 187 orchestration patterns
- **Personas:** 195 role-based perspectives
- **Checklists:** 115 verification templates

**Key Finding:** The knowledge base emphasizes INTEGRATED TOOLING over single-tool optimization. The Unified MLOps, Unified Monitoring, and AgentOps patterns recommend platform-level integration (e.g., Dataiku) rather than best-of-breed point solutions.

---

## 1. Phase-Specific Tool Recommendations

### Phase 0: Architecture Decision (RAG vs Fine-tuning vs Hybrid)

**Key Decision:** "Should you use RAG or fine-tuning?"

| Factor | RAG Recommendation | Fine-tuning Recommendation | Hybrid Consideration |
|--------|-------------------|---------------------------|----------------------|
| **Speed to value** | Fast (days) | Slow (weeks to months) | Balance via hybrid |
| **Knowledge update** | Dynamic (update sources) | Static (requires retraining) | RAG for live data |
| **Model customization** | Low (input control) | High (parameter tuning) | Start with RAG |
| **Infrastructure cost** | Lower (vector DB + retrieval) | Higher (GPU training, monitoring) | Evaluate ROI per phase |
| **Integration complexity** | Medium (retrieval logic) | High (training pipeline, deployment) | RAG first, fine-tune if needed |

**Source:** LLM Engineer's Handbook & Agentic RAG research papers

**When RAG is preferred:**
- Building new features quickly (chatbots, search)
- Knowledge changes frequently (policy updates, new docs)
- Limited training data
- No custom domain logic to encode

**When fine-tuning is preferred:**
- Recurring inference volume justifies training cost
- Task requires specific reasoning patterns
- Need to reduce hallucination on domain concepts
- Have sufficient high-quality training data

**Consideration:**
- Hybrid approaches: Start with prompt engineering → RAG → Fine-tuning based on performance metrics

---

### Phase 1: Feature & Data Pipeline (Infrastructure)

**Key Pattern:** Feature Pipeline + Batch Pipeline

**Recommended Architecture:**
- **Data Collection:** Pipeline-based (not ad-hoc)
- **Processing:** Batch or streaming (decision: sync vs async)
- **Storage:** Data warehouse (NoSQL or SQL based on schema flexibility)
- **Versioning:** Essential for reproducibility

**Infrastructure Components:**

| Component | Pattern | Trade-off |
|-----------|---------|-----------|
| **Data Collection** | ZenML Pipelines (see methodology) | Provides visibility, adds dependency |
| **Orchestration** | Dedicated orchestrator (Airflow/Prefect/ZenML) | Adds complexity but essential for reliability |
| **Storage** | NoSQL if unstructured (MongoDB), SQL if structured | Choose based on query patterns |
| **CI/CD** | Automated CI pipeline (gitleaks, linting, tests) | Non-negotiable for production |

**Tool Decision:** ZenML vs Airflow vs Prefect
- **ZenML:** Lightweight, ML-specific, integrates with model registries (mentioned in knowledge base)
- **Airflow:** Heavy-weight, enterprise standard, large ecosystem
- **Prefect:** Modern async-first, cloud-native

**Checklist for Phase 1:**
- [ ] Data collection pipeline automated
- [ ] Quality checks integrated (data lineage tracking required)
- [ ] CI pipeline with linting, formatting, testing
- [ ] Data versioning strategy defined
- [ ] Compliance and documentation in place

---

### Phase 2: Training Pipeline (If Fine-tuning Chosen)

**Key Decision:** "Should you use AWS SageMaker or AWS Bedrock?"

**Recommendation:** AWS SageMaker for full customization

| Aspect | SageMaker | Bedrock |
|--------|-----------|---------|
| **Use Case** | Custom ML logic, full control | Managed LLM API, rapid prototyping |
| **Engineering Focus** | Build, train, deploy your models | Use pre-trained models |
| **Infrastructure Control** | Full (GPU selection, scaling) | None (managed) |
| **Cost Model** | Pay per compute hour | Pay per inference/training token |
| **When to Choose** | Exploring ML engineering aspects | Integrating existing models |

**Infrastructure Patterns for Training:**

1. **Model Registry Pattern**
   - Problem: Tracking versions, sharing models across team
   - Solution: Centralized repository with metadata and versioning
   - Trade-offs:
     - Pro: Single source of truth, team collaboration
     - Pro: Facilitates deployment integration
     - Con: Additional setup and maintenance

2. **Training Framework Selection**
   - **PyTorch:** Dynamic graphs, research-friendly (for fine-tuning exploration)
   - **Transformers (Hugging Face):** Domain-specific, built for NLP/LLMs
   - **Distributed Training:** Required for large models (Ray, distributed PyTorch)

**Checklist for Phase 2:**
- [ ] Training data validation and decontamination complete
- [ ] Model registry set up
- [ ] Training script with error handling
- [ ] GPU resource management and scaling configured
- [ ] Monitoring and metrics tracking enabled
- [ ] Model checkpoint strategy defined

---

### Phase 3: Inference Pipeline (Deployment)

**Key Pattern:** Microservice Architecture for LLM Deployment

**Recommended Architecture:**
```
┌─────────────────────┐
│  Business Logic     │  (RAG, prompt engineering, tool calls)
│  Microservice       │
├─────────────────────┤
│  LLM Microservice   │  (Model serving, batching, caching)
│  (A10G/A100 GPU)    │
└─────────────────────┘
```

**Trade-offs:**
- Pro: Independent scaling of LLM vs business logic
- Pro: Flexible GPU upgrades (A10G → A100)
- Con: Increased microservice complexity and coordination

**Inference Tool Decision Matrix:**

| Tool/Service | Best For | Infrastructure |
|--------------|----------|-----------------|
| **AWS SageMaker Endpoints** | Production ML/LLM serving | Fully managed, real-time |
| **vLLM** | Fast LLM inference (open-source) | Self-hosted, optimized batching |
| **TensorRT** | Optimized inference (Nvidia) | Requires compilation, fastest |
| **Ray Serve** | Distributed serving | Flexible, scales across clusters |
| **FastAPI + Docker** | Custom microservice | Full control, ops responsibility |

**Semantic Caching Pattern** (Critical for inference cost reduction):
- Problem: High API costs from repeated similar queries
- Solution: Cache responses using embedding similarity (not exact match)
- Implementation: Before calling LLM, search embedding cache for similar queries
- Tool: Qdrant + semantic distance (mentioned in patterns)

**Checklist for Phase 3:**
- [ ] Inference latency < 500ms (or SLA defined)
- [ ] Error rate < 1%
- [ ] Input validation in place
- [ ] Rate limiting configured
- [ ] Semantic caching implemented for cost reduction
- [ ] API monitoring and alerting enabled
- [ ] Deployment strategy (canary/blue-green) tested

---

### Phase 4: Evaluation & Quality Gate

**Key Patterns:**

1. **Unified Monitoring Pattern**
   - Single dashboard for deployment health, drift detection, quality metrics
   - Integrates metrics from data pipelines, ML models, and LLM endpoints
   - Trade-off: Requires consolidating disparate monitoring systems

2. **Model Registry for Evaluation**
   - Track evaluation metrics alongside model versions
   - Enable A/B testing and rollback
   - Support decision: Model passed quality gates or not

**Evaluation Tool Checklist:**
- [ ] LLM-as-judge evaluation framework set up
- [ ] Retrieval quality metrics (precision, recall, MRR for RAG)
- [ ] Generation quality metrics (BLEU, ROUGE for summarization, custom for domain)
- [ ] Drift detection thresholds defined
- [ ] Human review process for edge cases
- [ ] Automated quality gate pass/fail criteria

**Recommended Metrics by Phase:**

| Metric Type | Tools/Frameworks | Phase |
|-------------|------------------|-------|
| **Data Quality** | Great Expectations, custom validators | Phase 1 |
| **Model Performance** | Hugging Face Evaluate, TorchMetrics | Phase 2 |
| **Inference Quality** | LLM-as-judge, human review, BLEU/ROUGE | Phase 3-4 |
| **Drift Detection** | Evidentlyai, custom thresholds | Ongoing |
| **Production Health** | Prometheus, DataDog, custom dashboards | Ongoing |

---

### Phase 5: Operations & Continuous Improvement

**Key Pattern:** Model Retraining Workflow

**Trigger:** Model performance drops below threshold

**Steps:**
1. Collect recent production data
2. Validate quality
3. Retrain model
4. Evaluate against current model
5. Update model registry
6. Deploy if performance improved

**Infrastructure Patterns:**

1. **Orchestrator Pattern**
   - Problem: Automating, scheduling, coordinating complex ML pipelines
   - Solution: Dedicated orchestrator managing pipeline execution, dependencies, failures
   - Tools: ZenML, Airflow, Prefect, Kubeflow
   - Trade-offs:
     - Pro: Reliability and scalability
     - Pro: Simplified management and monitoring
     - Con: System complexity
     - Con: Upfront setup investment

2. **AgentOps Pattern** (For autonomous systems)
   - Brings together DataOps, MLOps, LLMOps, and AgentOps
   - Unified metrics and visibility across all operational layers
   - Example implementation: Dataiku Universal AI Platform

**Checklist for Phase 5:**
- [ ] Retraining pipeline automated and tested
- [ ] Performance degradation detection active
- [ ] Model registry integration for easy rollback
- [ ] Monitoring dashboards for all metrics
- [ ] Data collection strategy for continuous improvement
- [ ] Documentation and runbooks for incident response

---

## 2. Infrastructure & Tool Stack Overview

### Core Infrastructure Decisions

**Key Finding:** The knowledge base emphasizes UNIFIED PLATFORMS over point solutions.

**Decision Framework for Infrastructure:**

| Layer | Consideration | Recommended Approach |
|-------|---------------|----------------------|
| **Orchestration** | Complex pipelines with dependencies → Dedicated orchestrator | ZenML (lightweight ML-specific) or Airflow (enterprise) |
| **Model Management** | Track versions, enable team collaboration → Model Registry | MLflow, Dataiku, or platform-integrated |
| **Monitoring** | Single source of truth for metrics → Unified dashboard | Dataiku, custom (Prometheus + Grafana), or cloud provider |
| **Experimentation** | Track model variants and metrics → Experiment tracking | Weights & Biases, MLflow, Dataiku |
| **Feature Management** | Version and reuse features → Feature store | Tecton, Feast (open-source), or platform-integrated |
| **Model Serving** | Production-grade inference → Managed service or custom | AWS SageMaker, Ray Serve, or FastAPI + Docker |

### Platform Options

**Unified Platforms (Recommended):**
- **Dataiku:** Brings DataOps, MLOps, LLMOps, AgentOps in one system
- **AWS SageMaker:** Full ML lifecycle management
- **Azure ML:** Enterprise ML platform
- **Google Vertex AI:** Integrated ML lifecycle

**Best-of-Breed (Requires Integration):**
- **Orchestration:** Airflow or Prefect
- **Experiment Tracking:** Weights & Biases or MLflow
- **Model Registry:** MLflow or custom
- **Monitoring:** Prometheus + Grafana or Datadog
- **Feature Store:** Tecton or Feast

### Technology Stack by Language/Framework

**For LLM/RAG Systems (Recommended):**
- **LLM Framework:** Hugging Face Transformers, LiteLLM (abstraction layer)
- **RAG Framework:** LangChain, LlamaIndex (mentioned implicitly in patterns)
- **Vector Database:** Qdrant (mentioned in patterns), Pinecone, Milvus
- **Orchestration:** ZenML or Airflow
- **Model Serving:** vLLM (optimized), Ray Serve (distributed)
- **Monitoring:** Prometheus + custom LLM-specific dashboards

**For Traditional ML:**
- **Training:** PyTorch, Scikit-learn
- **Feature Management:** Feast or Tecton
- **Orchestration:** Airflow, Prefect
- **Model Registry:** MLflow
- **Monitoring:** Evidently.ai for drift detection

---

## 3. Decision Frameworks & Tool Selection Patterns

### Decision Matrix: When to Use Each Tool

**Orchestration Tool Selection:**

| Requirement | ZenML | Airflow | Prefect | Kubeflow |
|-------------|-------|---------|---------|----------|
| **ML-Specific** | Yes | No | No | Yes |
| **Easy to Learn** | Yes | No | Yes | No |
| **Enterprise Scale** | Medium | Yes | Medium | Yes |
| **Cloud Native** | Yes | Yes | Yes | Yes |
| **Community Size** | Growing | Large | Growing | Large |

**Recommendation:** Start with ZenML for lightweight projects; migrate to Airflow if enterprise governance becomes critical.

---

**Monitoring & Observability Tool Selection:**

| Requirement | Unified Platform | Best-of-Breed |
|-------------|------------------|---------------|
| **All metrics in one place** | Dataiku, SageMaker | Prometheus + custom UI |
| **Low operational overhead** | Cloud provider (Vertex, SageMaker) | Datadog |
| **Cost control** | Open-source stacks | Cloud provider |
| **Customization** | Limited | High |
| **Integration complexity** | Low | Medium to High |

**Knowledge Base Position:** Unified monitoring is critical. The pattern emphasizes: "Provides a unified dashboard that allows ML engineers and IT to track all relevant metrics and health indicators from a single view."

---

### Golden Path Stack Recommendations

#### Option A: Cloud-First (Recommended for most teams)

```
Data Ingestion    → Cloud Data Warehouse (Snowflake, BigQuery)
                     ↓
Feature Pipeline  → Feature Store (platform-integrated) or Feast
                     ↓
Training          → Cloud ML Platform (SageMaker, Vertex AI)
                     ↓
Model Registry    → Platform-integrated
                     ↓
Serving           → Platform endpoints (SageMaker, Vertex AI)
                     ↓
Monitoring        → Platform-integrated dashboard
                     ↓
Orchestration     → Cloud orchestration (SageMaker Pipelines, Vertex Pipelines)
```

**Cost:** Medium-High
**Operational Overhead:** Low
**Scalability:** Automatic

---

#### Option B: Open-Source + Self-Hosted (For cost-sensitive or customization-heavy)

```
Data Ingestion    → Apache Kafka or batch scripts
                     ↓
Feature Pipeline  → Feast (open-source)
                     ↓
Orchestration     → Airflow + ZenML
                     ↓
Training          → PyTorch + Hugging Face on VM clusters
                     ↓
Model Registry    → MLflow
                     ↓
Serving           → Ray Serve or vLLM (for LLMs)
                     ↓
Monitoring        → Prometheus + Grafana + custom dashboards
```

**Cost:** Low-Medium (infrastructure + DevOps)
**Operational Overhead:** High
**Scalability:** Requires manual tuning

---

#### Option C: Hybrid (Recommended for LLM-specific projects)

```
Data Management   → Cloud DW (Snowflake) + DVC for ML data versioning
                     ↓
Orchestration     → ZenML (lightweight ML focus)
                     ↓
LLM Fine-tuning   → Hugging Face + AWS SageMaker Training
                     ↓
RAG Pipeline      → LangChain/LlamaIndex + Qdrant (self-hosted or cloud)
                     ↓
Model Serving     → vLLM (self-hosted, GPU-optimized) or SageMaker endpoints
                     ↓
Monitoring        → Custom (Prometheus) + LLM-specific metrics
```

**Cost:** Medium
**Operational Overhead:** Medium
**Scalability:** Good for LLM workloads

---

## 4. Implementation Patterns & Anti-Patterns

### Recommended Patterns

**1. Unified MLOps Workflows**
- **Benefit:** 10x faster model operations vs fragmented approaches
- **Implementation:** Use integrated MLOps platform or carefully orchestrate best-of-breed tools
- **Key:** Unified deployment and monitoring workflows

**2. Semantic Caching**
- **Problem:** High API costs from repeated similar queries
- **Solution:** Cache responses using embedding similarity
- **Implementation:** Before LLM call, search embedding cache for similar queries
- **Tool:** Qdrant or similar vector DB for semantic search

**3. Iterative/Agentic RAG**
- **Problem:** Single retrieval insufficient for complex queries
- **Solution:** Let model drive iterative retrieval (agent decides if more info needed)
- **Benefits:** Better accuracy than single-pass RAG
- **Implementation:** ReAct pattern with retrieval tool

**4. Model Registry Pattern**
- **Purpose:** Centralized version management and team collaboration
- **Integration:** With deployment pipeline and experiment tracking
- **Tools:** MLflow, Dataiku, or cloud provider

**5. Microservice Architecture for LLM Deployment**
- **Separation:** LLM service (GPU-optimized) + Business logic service
- **Scaling:** Independent scaling of components
- **Flexibility:** Easy GPU upgrades (A10G → A100)

### Anti-Patterns to Avoid

**Warning: Poetry Dependency Management**
- Use Poetry for modern Python dependency management
- But ensure it's integrated with CI/CD for reproducible builds

**Warning: Monolithic Batch Pipeline Architecture**
- Problem: Couples feature creation, model training, and inference
- Consequence: Training-serving skew, difficult to scale
- Solution: Separate feature pipeline from inference pipeline

**Warning: Asynchronous Processing Pitfalls**
- Common question: "When to choose synchronous vs asynchronous processing?"
- Context: Async improves throughput but adds complexity
- Decision: Use async for I/O-bound tasks (API calls, DB queries), not compute-bound

**Warning: Version Mismatches**
- **Embedding Model Migration:** Incompatibility when changing embedding models
- **Solution:** Maintain backward compatibility or re-index all embeddings
- **Cost:** Significant; plan embedding model selection carefully

---

## 5. Knowledge Gap Analysis

### Well-Covered Areas (High Extraction Count)

| Topic | Extractions | Confidence |
|-------|-------------|------------|
| RAG vs Fine-tuning Decision | 5+ patterns + decisions | High |
| Inference Optimization | 5+ patterns (semantic caching) | High |
| Evaluation Frameworks | Multiple patterns + checklists | High |
| Data Quality & Lineage | Multiple patterns + checklists | High |
| Microservice Deployment | Multiple patterns | High |
| Orchestration | Implicit (ZenML mentioned) | Medium |

### Gaps in Knowledge Base

**Missing or Minimal Coverage:**

1. **Specific Tool Recommendations**
   - No detailed comparisons of Weights & Biases vs Dataiku vs MLflow
   - No zenML vs Airflow detailed comparison (zenML mentioned in methodology only)
   - No opik or cometML mentions found

2. **Cost Analysis**
   - No clear cost-benefit analysis per tool
   - No infrastructure cost breakdowns by phase

3. **Team Size Scaling**
   - Guidance for startups (1-2 engineers) vs enterprises (50+ engineers)
   - Limited on tool selection based on team maturity

4. **Integration Patterns**
   - Limited guidance on integrating multiple tools
   - No explicit "best-of-breed stack" walkthrough

---

## 6. Synthesis Approach for Workflow Agents

### Query Strategy (When Building Workflow Steps)

**For Phase 1: Feature Pipeline Decision**
1. Query: `search_knowledge("feature pipeline architecture orchestration tools")`
2. Query: `get_patterns("Feature Pipeline, Orchestrator")`
3. Query: `get_decisions("data processing synchronous asynchronous")`
4. Query: `get_warnings("pipeline performance data quality")`

**For Phase 2: Training Decision**
1. Query: `get_decisions("fine-tuning vs RAG when to use")`
2. Query: `get_patterns("model registry, training framework")`
3. Query: `get_warnings("training infrastructure, distributed training")`

**For Phase 3: Inference Decision**
1. Query: `get_patterns("microservice architecture LLM, semantic caching")`
2. Query: `search_knowledge("model serving inference optimization deployment")`
3. Query: `get_decisions("inference latency trade-offs")`

**For Phase 4: Evaluation Decision**
1. Query: `get_patterns("unified monitoring, model evaluation")`
2. Query: `search_knowledge("evaluation metrics LLM quality benchmarks")`
3. Query: `get_checklists("evaluation production deployment")`

**For Phase 5: Operations**
1. Query: `get_patterns("model retraining, drift detection")`
2. Query: `get_workflows("model retraining orchestration")`
3. Query: `get_decisions("when to retrain models")`

---

## 7. Key Takeaways for Tech Stack Selection

### Principles from Knowledge Base

1. **Integration Over Point Solutions**
   - Unified MLOps platforms (Dataiku) preferred over best-of-breed fragmentation
   - 10x faster operations with unified workflows

2. **Phase-Based Tool Selection**
   - Different phases require different tools (data tools ≠ training tools ≠ serving tools)
   - Not one tool for entire workflow

3. **RAG as Default Starting Point**
   - RAG > Fine-tuning > Prompt Engineering hierarchy
   - Only fine-tune if RAG performance insufficient
   - Hybrid approaches acceptable

4. **Infrastructure as Prerequisite**
   - Data quality, versioning, and lineage tracking non-negotiable
   - Orchestration required for reliability
   - Monitoring essential for production LLM systems

5. **Cost Reduction Through Intelligence**
   - Semantic caching critical for LLM cost control
   - Smart retrieval (agentic RAG) reduces hallucination
   - Model registry enables efficient reuse

### Decision Checklist for Your Project

**Before selecting tools, answer:**

- [ ] RAG sufficient, or fine-tuning required?
- [ ] Team size and operational maturity?
- [ ] Budget for infrastructure (cloud vs self-hosted)?
- [ ] Specific compliance/data residency requirements?
- [ ] Real-time vs batch processing preference?
- [ ] Multi-team or single team project?
- [ ] Custom domain logic needed (justifying fine-tuning)?

**Recommended Approach:**
1. Start with cloud-first (SageMaker/Vertex) + RAG
2. Add fine-tuning only if RAG performance insufficient
3. Implement unified monitoring from day 1
4. Scale to self-hosted only if cost becomes prohibitive
5. Invest in orchestration early (ZenML or Airflow)

---

## Appendix: Sources & Extraction Coverage

### Primary Source: LLM Engineer's Handbook
- 721 LLM-related extractions
- 635 RAG-specific extractions
- 465 embedding/inference extractions
- Tools mentioned: ZenML, Poetry, Dataiku
- Patterns: Unified MLOps, Microservice Architecture, Semantic Caching

### Secondary Sources (58 total)
- Agentic RAG research papers (335+ retrieval extractions)
- "Designing ML Systems" patterns
- MLOps/LLMOps methodology guides
- Production deployment case studies
- Safety & evaluation frameworks

### Extraction Type Distribution

| Type | Count | Reliability |
|------|-------|-------------|
| Decision | 356 | High (structured Q&A format) |
| Warning | 335 | High (clear anti-patterns) |
| Pattern | 314 | High (problem-solution pairs) |
| Methodology | 182 | Medium (steps-based) |
| Workflow | 187 | Medium (orchestration patterns) |
| Persona | 195 | Low (role-based, implicit) |
| Checklist | 115 | High (verification items) |

---

## Next Steps for Workflow Implementation

1. **Create Phase-Specific Templates**
   - Use this analysis as basis for step configs
   - Reference decision points from knowledge base
   - Include tool selection checklists

2. **Embed Knowledge Queries**
   - Each workflow step queries MCP with phase-specific context
   - Agents synthesize patterns, decisions, warnings
   - Show trade-offs and considerations to user

3. **Validate Against Real Projects**
   - Run workflow on sample AI engineering projects
   - Verify tool recommendations align with team experience
   - Update patterns based on feedback

4. **Expand Knowledge Base**
   - Ingest more recent LLMOps tooling literature
   - Add cost analysis benchmarks
   - Include team-size scaling guidelines

---

**Document prepared for AI Engineering Workflow implementation.**
**Ready for use in workflow agent guidance and tool selection decisions.**
