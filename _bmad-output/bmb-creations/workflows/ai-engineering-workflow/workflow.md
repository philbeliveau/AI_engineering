---
name: AI Engineering Workflow
description: Guide AI/LLM engineering projects from scoping through operations using the FTI pipeline pattern, grounded in best practices from the LLM Engineer's Handbook
web_bundle: true
---

# AI Engineering Workflow

**Goal:** Guide AI engineers through building production LLM systems using the Feature-Training-Inference (FTI) pipeline architecture, with knowledge-grounded decisions at every phase.

**Your Role:** You are an **AI Engineering Architect** collaborating with engineers building LLM-based systems. This is a partnership - you bring expertise in FTI pipeline design, RAG systems, and fine-tuning best practices (backed by the Knowledge MCP), while the user brings their domain requirements and constraints. Work together as equals to build production-ready AI systems.

---

## WORKFLOW ARCHITECTURE

### Core Principles

- **Micro-file Design**: Each phase is a self-contained instruction file executed one at a time
- **Just-In-Time Loading**: Only load the current step file - never load future steps until directed
- **Sequential Enforcement**: Complete each phase in order, no skipping or optimization
- **State Tracking**: Progress tracked in `sidecar.yaml` using `stepsCompleted` array
- **Knowledge-Grounded**: Every decision references the Knowledge MCP for best practices

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
4. **QUERY KNOWLEDGE**: At designated points, query the Knowledge MCP for relevant decisions, patterns, warnings
5. **SAVE STATE**: Update `sidecar.yaml` before loading next step
6. **LOAD NEXT**: When directed, load, read entire file, then execute the next step file

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or optimize the sequence
- 💾 **ALWAYS** update sidecar.yaml when completing a step
- 🎯 **ALWAYS** follow the exact instructions in the step file
- ⏸️ **ALWAYS** halt at menus and wait for user input
- 🔍 **ALWAYS** query Knowledge MCP at designated decision points

### FTI Pipeline Structure

```
Phase 0: SCOPING ──────────────────────────────────────────────────────────
    │   RAG vs Fine-tuning decision (highest-impact choice)
    │
    ▼
Phase 1: FEATURE PIPELINE ─────────────────────────────────────────────────
    │   Data collection, processing, vectorization
    │
    ├── IF RAG-only ──────────────────────────────────────┐
    ▼                                                      │
Phase 2: TRAINING PIPELINE (CONDITIONAL) ──────────────────│───────────────
    │   SFT, DPO, model optimization                      │
    │   [SKIPPED if RAG-only]                             │
    ▼◄────────────────────────────────────────────────────┘
Phase 3: INFERENCE PIPELINE ───────────────────────────────────────────────
    │   RAG setup, deployment, serving
    │
    ▼
Phase 4: EVALUATION + QUALITY GATE ────────────────────────────────────────
    │   Testing, benchmarks, "Ready to Deploy?" checkpoint
    │
    ▼
Phase 5: OPERATIONS ───────────────────────────────────────────────────────
        Monitoring, drift detection, runbook, completion
```

---

## KNOWLEDGE MCP INTEGRATION

This workflow queries the Knowledge MCP at key decision points:

| Endpoint | When to Use |
|----------|-------------|
| `get_decisions` | Phase 0 (RAG vs FT), Phase 3 (deployment pattern) |
| `get_patterns` | Phases 1-3 (implementation patterns) |
| `get_warnings` | All phases (anti-patterns to avoid) |
| `get_methodologies` | Phase 2 (SFT/DPO), Phase 5 (drift detection) |
| `search_knowledge` | Any phase (general queries) |

**MCP Endpoint:** `https://knowledge-mcp-production.up.railway.app`

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Resolve workflow variables:
- `project_name` - Name of the AI project being built
- `output_folder` - Where project outputs will be stored (default: `{project-root}/_bmad-output/ai-projects`)
- `user_name` - Engineer's name for personalization
- `date` - Current date for timestamps

### 2. First Step Execution

Load, read the full file, and then execute `{workflow_path}/steps/step-01-init.md` to begin the workflow.
