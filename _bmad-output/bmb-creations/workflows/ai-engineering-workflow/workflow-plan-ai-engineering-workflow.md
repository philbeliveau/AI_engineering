---
stepsCompleted: [1, 2, 3, 4, 5]
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
├── phase-2-training/               ← (empty if RAG-only)
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

---

## Refinements Applied

1. ✅ **Conditional flow** - RAG-only path skips Phase 2
2. ✅ **Entry/exit criteria** - Prerequisites and completion conditions per phase
3. ✅ **Quality gate** - "Ready to Deploy?" checkpoint after Phase 4
4. ✅ **Gap acknowledgment** - Phase 4 marked as evolving (weak knowledge coverage)
5. ✅ **Tiered output model** - Docs + templates for v1, code gen deferred
6. ✅ **Structured folder output** - Organized by phase with consistent structure

---

## Next Steps

Proceed to workflow step design - define the detailed steps within each phase.
