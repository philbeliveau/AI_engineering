# Handoff: Build AI Engineering Workflow from Knowledge Base

## Mission

Build a comprehensive **AI Engineering Workflow** by extracting and organizing knowledge from the LLM Handbook (already ingested in the knowledge MCP). This workflow will guide AI engineering projects from requirements through deployment.

---

## Context

### What We Have

1. **Knowledge MCP Server** (live and healthy):
   - URL: `https://knowledge-mcp-production.up.railway.app`
   - Contains extracted knowledge from the **LLM Engineer's Handbook**
   - 15+ architectural decisions
   - 40+ implementation patterns
   - 20+ warnings/anti-patterns
   - 13+ methodologies

2. **Available Endpoints** (GET requests):
   | Endpoint | Returns |
   |----------|---------|
   | `/get_methodologies` | Step-by-step processes |
   | `/get_decisions` | Architectural choices with trade-offs |
   | `/get_patterns` | Implementation patterns with examples |
   | `/get_warnings` | Anti-patterns and pitfalls to avoid |
   | `/search_knowledge?query=<topic>` | Semantic search across all knowledge |

3. **Target Workflow Structure**: **SUBJECT TO CHANGE DEPENDING ON WHAT WE FIND THROUGH THE SEARCH**
   ```
   AI Engineering Workflow
   ├── Phase 1: Requirements & Scoping
   ├── Phase 2: Architecture Design
   ├── Phase 3: Data Preparation
   ├── Phase 4: Model/RAG Development
   ├── Phase 5: Evaluation
   ├── Phase 6: Deployment
   └── Phase 7: Operations & Monitoring
   ```

---

## Task: Knowledge Extraction & Organization

### Step 1: Query Each Endpoint

Use WebFetch to query each endpoint and extract content:

```
GET https://knowledge-mcp-production.up.railway.app/get_methodologies
GET https://knowledge-mcp-production.up.railway.app/get_decisions
GET https://knowledge-mcp-production.up.railway.app/get_patterns
GET https://knowledge-mcp-production.up.railway.app/get_warnings
```

### Step 2: Map Knowledge to Workflow Phases

Organize extracted knowledge by workflow phase: (**CREATE NEW PHASE IF. NECESSARY, THESE ARE SUBJECT TO CHANGE**)

| Phase | Relevant Decisions | Relevant Patterns | Relevant Warnings | Methodologies |
|-------|-------------------|-------------------|-------------------|---------------|
| Requirements | Use case classification | - | - | - |
| Architecture | RAG vs Fine-tuning, Batch vs Streaming, Monolithic vs Microservices | FTI Pipeline, Microservices | - | MLOps principles |
| Data Prep | Training data scope, Deduplication strategy | Chunking, Deduplication, Synthetic data | Instruction dataset creation | Data curation |
| Development | QLoRA vs LoRA, Sequence truncation | SFT, DPO, Gradient checkpointing | Learning rate, Epochs | SFT, PPO methodologies |
| Evaluation | Benchmark selection | Drift monitoring, Black-box testing | LLM judge bias, Position bias | Evaluation methodology |
| Deployment | Online vs Batch inference, Sync vs Async | SageMaker, Model registry, Quantization | Static replicas, Unversioned deps | DevOps methodology |
| Operations | Monitoring vs Observability | Drift detection, Logging | Unmonitored calls, Missing orchestration | Drifts methodology |

### Step 3: Identify Gaps

Note which phases have:
- **Strong coverage** (3+ pieces of knowledge)
- **Weak coverage** (1-2 pieces)
- **No coverage** (need additional sources)

Expected gaps (to be filled later):
- RAG-specific patterns (need RAG survey ingestion)
- Detailed evaluation frameworks
- Agent patterns (if building agentic systems)
- ++++

---

## Deliverable: Workflow Specification

Create a workflow file at: `_bmad-output/workflows/ai-engineering-workflow.md`

### Workflow Format

```markdown
# AI Engineering Workflow

## Overview
[Purpose and when to use this workflow]

## Prerequisites
[What must be in place before starting]

---

## Phase 1: Requirements & Scoping

### Objective
[What this phase achieves]

### Steps
1. Step description
   - Knowledge query: `get_decisions?topic=use-case-classification`
   - Expected output: [what agent produces]

### Decision Points
- [Key decisions to make with options from knowledge base]

### Warnings
- [Anti-patterns to avoid from knowledge base]

### Exit Criteria
- [How to know this phase is complete]

---

## Phase 2: Architecture Design
[Same structure...]

---
[Continue for all phases]
```

### Workflow Design Principles

1. **Each step should reference knowledge queries** - Agents executing this workflow will query the MCP at each step
2. **Include decision trees** - When the knowledge base has decision points, embed them
3. **Surface warnings proactively** - Don't let agents hit anti-patterns
4. **Define clear exit criteria** - Each phase needs completion conditions
5. **Allow for iteration** - Build in feedback loops

---

## Knowledge Already Extracted (Reference)

### Key Decisions Available
- RAG vs Fine-tuning
- Synchronous vs Asynchronous Processing
- Online vs Batch Inference
- QLoRA vs LoRA
- Monolithic vs Microservices
- Batch vs Streaming Pipelines
- Monitoring vs Observability

### Key Patterns Available
- Semantic Caching (40-60% cost reduction)
- FTI Pipeline (Feature, Training, Inference)
- Supervised Fine-Tuning
- Direct Preference Optimization
- Microservice Architecture for LLM
- Model Registry
- Drift Detection

### Key Warnings Available
- Instruction dataset creation is "the most difficult part"
- Embedding model changes invalidate all vectors ("thousands of dollars")
- LLM judges "favor the first answer presented"
- Static replica config = "wasted resources"
- Missing orchestration = "unreliable ML pipelines"

### Key Methodologies Available
- Supervised Finetuning (SFT)
- PPO for RLHF
- MLOps Principles
- DevOps Methodology
- Drift Monitoring
- Advanced RAG Framework

---

## Success Criteria

The workflow is complete when:
1. All 7 phases are defined with steps
2. Each phase references relevant knowledge queries
3. Decision points include options and trade-offs from knowledge base
4. Warnings are embedded at relevant steps
5. Gaps are documented for future knowledge ingestion
6. Workflow can be executed by a BMAD agent

---

## Next Steps After Workflow Creation

1. **Test** the workflow with a sample project: "Build a RAG chatbot for internal docs"
2. **Identify gaps** where knowledge was insufficient
3. **Ingest additional sources** to fill gaps:
   - RAG Survey → Phase 4 (RAG Development)
   - Evaluation papers → Phase 5
   - MLOps books → Phases 6-7
4. **Iterate** on the workflow with enriched knowledge

---

## Commands to Use

```bash
# Create the workflow using BMAD Builder
/bmad:bmb:workflows:create-workflow

# Query knowledge as needed
/knowledge:get-methodologies <topic>
/knowledge:get-decisions <topic>
/knowledge:get-patterns <topic>
/knowledge:get-warnings <topic>
/knowledge:search-knowledge <query>
```
