---
stepsCompleted: [1, 2, 3, 4, 5, 6]
---

# Workflow Creation Plan: ai-engineering-workflow

## Initial Project Context

- **Module:** Standalone
- **Target Location:** _bmad-output/bmb-creations/workflows/ai-engineering-workflow
- **Created:** 2026-01-05
- **Approach:** Knowledge-driven design (FTI-aligned)
- **Primary User:** AI engineers, solo devs, or BMAD agents building LLM systems

---

## Requirements Gathered

### Workflow Purpose
Guide AI/LLM engineering projects from scoping through operations, grounded in best practices from the LLM Engineer's Handbook.

### Core Architecture: FTI Pipeline Pattern

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    FEATURE      │     │    TRAINING     │     │   INFERENCE     │
│    PIPELINE     │────▶│    PIPELINE     │────▶│    PIPELINE     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Why FTI:**
- Solves training-serving skew
- Clear separation of concerns
- Each pipeline scales independently
- Different teams can own different pipelines
- Directly aligned with book methodology

### Phase Structure with Conditional Flow

```
Phase 0: SCOPING
    │
    ├── Decision: RAG vs Fine-tuning
    │
    ▼
Phase 1: FEATURE PIPELINE
    │
    ├── If RAG-only ────────────────────┐
    │                                   │
    ▼                                   │
Phase 2: TRAINING PIPELINE              │
    │   (Skip if RAG-only)              │
    │                                   │
    ▼◄──────────────────────────────────┘
Phase 3: INFERENCE PIPELINE
    │
    ▼
Phase 4: EVALUATION
    │
    ├── QUALITY GATE: Ready to Deploy?
    │
    ▼
Phase 5: OPERATIONS
```

### Phase Details with Entry/Exit Criteria

| Phase | Description | Entry Criteria | Exit Criteria |
|-------|-------------|----------------|---------------|
| **0. Scoping** | Use case classification, RAG vs FT decision | Project brief or user requirements | Architecture direction decided, documented |
| **1. Feature Pipeline** | Data collection, processing, vectorization | Data sources identified, storage provisioned | Vectors in DB, retrieval tested |
| **2. Training Pipeline** | SFT, DPO, model optimization | Base model selected, training data prepared | Model trained, metrics logged |
| **3. Inference Pipeline** | RAG setup, deployment, serving | Trained model OR base model + vectors ready | Endpoint deployed, latency acceptable |
| **4. Evaluation** | Testing, benchmarking, QA | Inference pipeline functional | Quality gate passed |
| **5. Operations** | Drift detection, prompt monitoring, scaling | Deployment complete, monitoring configured | Runbook complete, alerts active |

### Quality Gate: Ready to Deploy?

Between Phase 4 and Phase 5, explicit checkpoint:
- Minimum evaluation criteria met?
- Known limitations documented?
- Rollback plan in place?
- Stakeholder sign-off?

### Technology Stack (from LLM Handbook)

| Category | Primary Tools |
|----------|---------------|
| **Cloud** | AWS, SageMaker |
| **Data Storage** | MongoDB (raw), Qdrant (vectors) |
| **ML/LLM** | Hugging Face, llama.cpp |
| **MLOps** | ZenML, GitHub Actions, Comet ML |
| **Monitoring** | Opik (prompt monitoring) |

### Knowledge Inventory

| Type | Count | Coverage | Notes |
|------|-------|----------|-------|
| Methodologies | 7 | MLOps, SFT, PPO, DevOps, Drifts | Strong |
| Decisions | 8 | RAG vs FT, QLoRA vs LoRA, Sync vs Async | Strong |
| Patterns | 15 | RAG, Semantic Caching, FTI, Model Registry | Strong |
| Warnings | 20 | Dataset creation, embedding migration, LLM judge bias | Strong |

**Known Gap:** Phase 4 (Evaluation) has weak coverage - only warnings about LLM judge bias. Mark as evolving; will improve when evaluation frameworks are ingested.

### Workflow Type
- **Type:** Document + Action Workflow (produces architecture docs, executes setup)
- **Interaction:** Collaborative with decision points at each phase
- **Instruction Style:** Intent-based (let AI adapt to context)

### Success Criteria
1. Each phase references specific knowledge queries
2. Decision trees embedded from knowledge base
3. Warnings surfaced proactively at relevant steps
4. Clear entry/exit criteria per phase
5. Conditional flow handles RAG-only vs fine-tuning paths
6. Quality gate enforced before operations
7. Executable by BMAD agents with MCP access

---

## Tools Configuration

### Primary Integration: Knowledge MCP Server

| Endpoint | Purpose | Phases |
|----------|---------|--------|
| `search_knowledge` | General semantic queries | All |
| `get_decisions` | Architectural choices with trade-offs | 0, 1, 3 |
| `get_patterns` | Implementation patterns | 1, 2, 3 |
| `get_warnings` | Anti-patterns to avoid | All |
| `get_methodologies` | Step-by-step processes | 2, 4, 5 |

**MCP Endpoint:** `https://knowledge-mcp-production.up.railway.app`

### Core BMAD Tools

| Tool | Included | Integration Points |
|------|----------|-------------------|
| **Advanced Elicitation** | Yes | Phase 0 (RAG vs FT decision validation) |
| **Brainstorming** | No | Deferred - add if needed |
| **Party-Mode** | No | Deferred - add if needed |

### LLM Features

| Feature | Included | Use Case |
|---------|----------|----------|
| **File I/O** | Yes | Output architecture docs, configs, specs |
| **Web-Browsing** | Optional | Research when needed |
| **Sub-Agents** | No | Premature - add if complexity requires |
| **Sub-Processes** | No | Premature - add if complexity requires |

### External Integrations

| Tool | Included | Purpose |
|------|----------|---------|
| **Context7** | Yes | Verify framework/library documentation |

### Memory Systems

| Tool | Included | Purpose |
|------|----------|---------|
| **Sidecar File** | Yes | Track decisions across phases, maintain project context |

### Installation Requirements

- **Knowledge MCP:** Already deployed (no install needed)
- **Context7:** MCP server (requires install if not present)
- **User Preference:** Willing to install as needed

---

## Output Format Design

### Output Philosophy

> "Document decisions, provide templates, let humans/agents generate the actual artifacts."

### Tiered Output Model

| Tier | What | Format | v1 Scope |
|------|------|--------|----------|
| **Tier 1: Essential** | Project spec, decision log, knowledge refs | Markdown | ✅ Yes |
| **Tier 2: Structured** | Phase specs, config templates, checklists | Markdown + YAML templates | ✅ Yes |
| **Tier 3: Generated** | Actual configs, code, IaC | YAML, Python, Terraform | ❌ Future |

### Output Folder Structure

```
project-output/
├── sidecar.yaml                    ← State tracking across phases
├── project-spec.md                 ← Single growing narrative
├── decision-log.md                 ← All decisions + rationale + knowledge refs
│
├── phase-0-scoping/
│   └── architecture-decision.md    ← ADR format
│
├── phase-1-feature/
│   ├── spec.md                     ← What to build
│   └── templates/
│       ├── chunking-config.template.yaml
│       └── embedding-config.template.yaml
│
├── phase-2-training/               ← (SKIPPED output if RAG-only)
│   ├── spec.md
│   └── templates/
│       └── training-config.template.yaml
│
├── phase-3-inference/
│   ├── spec.md
│   └── templates/
│       └── deployment-config.template.yaml
│
├── phase-4-evaluation/
│   ├── report.md
│   └── checklists/
│       └── quality-gate-checklist.md
│
└── phase-5-operations/
    ├── runbook.md
    └── templates/
        └── alerts-config.template.yaml
```

### Document Formats

**Format Type:** Structured (required sections, flexible content)

**Primary Documents:**
- `project-spec.md` - Growing narrative, one section per phase
- `decision-log.md` - ADR-style entries with knowledge references

**Phase Specs:** Each follows consistent structure:
```markdown
# Phase X: [Name] Spec

## Objective
[What this phase achieves]

## Knowledge Consulted
[MCP queries made, key insights]

## Decisions Made
[Choices with rationale]

## Implementation Guidance
[What to build, how to configure]

## Templates Provided
[List of config templates]

## Exit Criteria
[How to know this phase is complete]
```

**Config Templates:** YAML with placeholders
```yaml
# chunking-config.template.yaml
chunking:
  strategy: "{{CHUNKING_STRATEGY}}"  # semantic | fixed | recursive
  chunk_size: {{CHUNK_SIZE}}          # recommended: 512-1024
  overlap: {{OVERLAP}}                # recommended: 50-100
  # Decision reference: See decision-log.md#chunking-strategy
```

**Conditional Skip Output:** When Phase 2 is skipped (RAG-only):
```markdown
## Phase 2: Training Pipeline
**Status:** SKIPPED (RAG-only architecture selected in Phase 0)
**Reason:** No fine-tuning required for this use case.
```

---

## Workflow Step Design

### Step Structure (7 Steps)

```
step-01-init
    │
    ├─── (existing project?) ───▶ step-01b-continue
    │
    ▼
step-02-scoping (Phase 0)
    │
    ▼
step-03-feature-pipeline (Phase 1)
    │
    ├─── IF RAG-only ──────────────────┐
    ▼                                  │
step-04-training-pipeline (Phase 2)    │
    │   [or SKIPPED output]            │
    ▼◄─────────────────────────────────┘
step-05-inference-pipeline (Phase 3)
    │
    ▼
step-06-evaluation-and-gate (Phase 4 + Quality Gate)
    │
    ▼
step-07-operations-and-complete (Phase 5 + Finalize)
```

### Step Details

| Step | File | Purpose | Knowledge Queries | Menu |
|------|------|---------|-------------------|------|
| 01 | `step-01-init.md` | Create project folder, sidecar, detect continuation | - | Auto-proceed |
| 01b | `step-01b-continue.md` | Resume existing project, jump to last step | - | Jump menu |
| 02 | `step-02-scoping.md` | RAG vs FT decision, use case analysis, constraints | `get_decisions` | A/P/C |
| 03 | `step-03-feature-pipeline.md` | Data sources, chunking strategy, embedding config | `get_patterns`, `get_warnings` | A/P/C |
| 04 | `step-04-training-pipeline.md` | SFT/DPO setup, hyperparams (CONDITIONAL) | `get_methodologies`, `get_patterns` | A/P/C or SKIP |
| 05 | `step-05-inference-pipeline.md` | RAG setup, deployment pattern, scaling | `get_patterns`, `get_decisions` | A/P/C |
| 06 | `step-06-evaluation-and-gate.md` | Test plan, benchmarks, quality gate checklist | `get_warnings` | A/P/C + Gate |
| 07 | `step-07-operations-and-complete.md` | Monitoring, drift, runbook, finalize | `get_methodologies` | Complete |

### Continuation Support

- `step-01-init.md` checks for existing `sidecar.yaml`
- `step-01b-continue.md` reads state and jumps to appropriate step
- Every step updates `currentPhase` and `stepsCompleted` in sidecar

### Sidecar Schema

```yaml
# sidecar.yaml
project_name: "{{PROJECT_NAME}}"
created: "{{DATE}}"
architecture: "rag-only" | "fine-tuning" | "hybrid"
currentPhase: 0-5
stepsCompleted: [1, 2, 3...]
decisions:
  - id: "rag-vs-ft"
    choice: "rag-only"
    rationale: "..."
    knowledge_ref: "get_decisions:rag-vs-fine-tuning"
warnings_acknowledged: []
```

### Interaction Patterns

| Step | Interaction Style |
|------|-------------------|
| 01/01b | Automated (setup/resume) |
| 02 | High collaboration (critical decision) + Advanced Elicitation |
| 03-05 | Guided design with knowledge queries |
| 06 | Checklist-driven + quality gate decision |
| 07 | Summary review + completion |

### Role Definition

**AI Role:** AI Engineering Architect
- Expertise in FTI pipeline design, RAG systems, fine-tuning
- Queries Knowledge MCP to ground recommendations
- Collaborative tone, surfaces trade-offs clearly
- Proactively warns about anti-patterns

---

## Refinements Applied

1. ✅ **Conditional flow** - RAG-only path skips Phase 2
2. ✅ **Entry/exit criteria** - Prerequisites and completion conditions per phase
3. ✅ **Quality gate** - "Ready to Deploy?" checkpoint after Phase 4
4. ✅ **Gap acknowledgment** - Phase 4 marked as evolving (weak knowledge coverage)
5. ✅ **Tiered output model** - Docs + templates for v1, code gen deferred
6. ✅ **Structured folder output** - Organized by phase with consistent structure
7. ✅ **7-step design** - Merged eval+gate, operations+finalize for efficiency
8. ✅ **Explicit SKIPPED output** - Conditional phases produce clear skip documentation
9. ✅ **Continuation support** - Multi-session via sidecar state tracking

---

## Files to Create

### Workflow Files
```
ai-engineering-workflow/
├── workflow.md                      ← Main workflow config
├── steps/
│   ├── step-01-init.md
│   ├── step-01b-continue.md
│   ├── step-02-scoping.md
│   ├── step-03-feature-pipeline.md
│   ├── step-04-training-pipeline.md
│   ├── step-05-inference-pipeline.md
│   ├── step-06-evaluation-and-gate.md
│   └── step-07-operations-and-complete.md
├── templates/
│   ├── sidecar.template.yaml
│   ├── project-spec.template.md
│   ├── decision-log.template.md
│   ├── phase-spec.template.md
│   └── config-templates/
│       ├── chunking-config.template.yaml
│       ├── embedding-config.template.yaml
│       ├── training-config.template.yaml
│       ├── deployment-config.template.yaml
│       └── alerts-config.template.yaml
└── checklists/
    └── quality-gate-checklist.md
```

---

## Next Steps

Proceed to build phase - create the actual workflow files.
