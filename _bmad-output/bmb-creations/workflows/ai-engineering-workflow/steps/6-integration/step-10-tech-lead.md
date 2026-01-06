---
name: 'step-10-tech-lead'
description: 'Tech Lead: Final integration review, consistency check, and GO/REVISE decision'

# Configuration Reference
config: '../../config.yaml'

# Step Navigation
nextStep: 'step-11-story-elaborator.md'
outputPhase: null  # Integration review spans all phases
# Note: Agent reference is in the Agent Activation section below, not duplicated here
---

# Step 10: Tech Lead Review

## Agent Activation

**CRITICAL:** Load and fully activate the **Marcus** agent from `{workflow_path}/agents/tech-lead.md`.

This step is driven by Marcus via his menu commands. The agent file contains:
- Full persona (role, identity, communication_style, principles)
- Activation sequence with config loading
- 5 core menu commands for review workflow
- Prompt definitions for each command

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read ALL project files:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** Complete sidecar including all `stories.*` sections from Steps 2-9

### 2. Phase 0 - Scoping
**Files:**
- `{output_folder}/{project_name}/phase-0-scoping/business-requirements.md`
- `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`

### 3. Phase 1 - Feature Pipeline
**Files:**
- `{output_folder}/{project_name}/phase-1-feature/data-pipeline-spec.md`
- `{output_folder}/{project_name}/phase-1-feature/embeddings-spec.md`

### 4. Phase 2 - Training (if applicable)
**Files:** (only if architecture is "fine-tuning" or "hybrid")
- `{output_folder}/{project_name}/phase-2-training/training-spec.md`

### 5. Phase 3 - Inference
**Files:**
- `{output_folder}/{project_name}/phase-3-inference/rag-pipeline-spec.md`
- `{output_folder}/{project_name}/phase-3-inference/prompt-engineering-spec.md`

### 6. Phase 4 - Evaluation
**Files:**
- `{output_folder}/{project_name}/phase-4-evaluation/evaluation-spec.md`

### 7. Phase 5 - Operations
**Files:**
- `{output_folder}/{project_name}/phase-5-operations/operations-spec.md`

### 8. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** All decisions (ARCH-*, DATA-*, EMB-*, RAG-*, PROMPT-*, EVAL-*, OPS-*)

**Validation:** ALL phase specs must be complete before Tech Lead review can proceed.

---

## STEP GOAL

Marcus serves as the **quality gate** between planning/design phases (Steps 1-9) and implementation (Step 11+). He reviews all accumulated stories, validates consistency, sequences dependencies, and makes the sacred GO/REVISE decision.

---

## HOW THIS STEP WORKS

Unlike other steps with inline workflow logic, Step 10 is **agent-driven**:

1. **Load Marcus** - The Tech Lead agent activates with full menu
2. **Marcus greets user** - Shows available commands
3. **User drives review** - Using Marcus's menu commands
4. **Marcus makes recommendation** - GO or REVISE with rationale
5. **Continue or Revise** - Based on decision

---

## MARCUS'S MENU COMMANDS

| Command | Purpose |
|---------|---------|
| `*review-backlog` | Load and summarize all stories from Steps 1-9 |
| `*validate-consistency` | Check for conflicts, gaps, and inconsistencies |
| `*sequence-stories` | Determine implementation order based on dependencies |
| `*go-decision` | Make the sacred GO/REVISE verdict |
| `*revise` | Send specific step back for revision with feedback |
| `*party-mode` | Bring in other agents for discussion |
| `*advanced-elicitation` | Deep dive techniques |
| `*dismiss` | Exit agent |

### Command Details

#### `*validate-consistency`
**Use Checklist:** Load `{workflow_path}/checklists/tech-lead-consistency-checklist.md`

Work through the 8 validation categories:
1. Architecture Alignment
2. Decision Consistency
3. Dependency Validation
4. Completeness Check
5. Quality Gate Prerequisites
6. Operational Readiness Prerequisites
7. Story Integrity
8. Knowledge Grounding

Categorize each finding as:
- 🔴 **BLOCKER** - Must fix before GO
- 🟡 **WARNING** - Should address, may proceed with risk
- 🔵 **INFO** - Noted, no action required

---

## EXPECTED WORKFLOW

### Typical Session:

```
1. Marcus activates, loads sidecar.yaml
2. User: *review-backlog
   → Marcus presents story inventory by phase

3. User: *validate-consistency
   → Marcus reports BLOCKERS, WARNINGS, INFO

4. User: *sequence-stories
   → Marcus maps dependencies, presents implementation waves

5. User: *go-decision
   → Marcus renders GO or REVISE verdict with rationale

6. If GO: Proceed to Step 11 (Story Elaborator)
   If REVISE: Marcus specifies which step(s) need work
```

---

## CONTEXT FOR MARCUS

**Reference:** See the **LOAD CONTEXT (MANDATORY)** section above for the complete list of files Marcus must load.

When Marcus loads the project files, he has access to all accumulated context:

| Step | Agent | Artifacts | Story Prefix |
|------|-------|-----------|--------------|
| Step 1 | Business Analyst | `business-requirements.md` | (requirements only) |
| Step 2 | FTI Architect | `architecture-decision.md` | ARCH-S* |
| Step 3 | Data Engineer | `data-pipeline-spec.md` | DATA-S* |
| Step 4 | Embeddings Engineer | `embeddings-spec.md` | EMB-S* |
| Step 5 | Fine-Tuning Specialist | `training-spec.md` (if applicable) | TRAIN-S* |
| Step 6 | RAG Specialist | `rag-pipeline-spec.md` | RAG-S* |
| Step 7 | Prompt Engineer | `prompt-engineering-spec.md` | PROMPT-S* |
| Step 8 | LLM Evaluator | `evaluation-spec.md` | EVAL-S* |
| Step 9 | MLOps Engineer | `operations-spec.md` | OPS-S* |

**Additionally:** The `decision-log.md` contains all architectural and design decisions made throughout the workflow.

---

## DELIVERABLES (Created by Marcus)

When GO is decided:

| Deliverable | Description |
|-------------|-------------|
| `integration-review.md` | Marcus's review findings |
| `implementation-stories.md` | Consolidated, sequenced story backlog |
| Updated `sidecar.yaml` | Status: "go-approved", stories sequenced |

When REVISE is decided:

| Deliverable | Description |
|-------------|-------------|
| `revision-request.md` | Which steps need work and why |
| Updated `sidecar.yaml` | Status: "needs-revision", step(s) to revisit |

---

## TRANSITION TO STEP 11

When Marcus approves GO:

1. `sidecar.yaml` updated with `integrationReview.decision: "GO"`
2. Stories sequenced and ready for elaboration
3. User proceeds to Step 11: Story Elaborator
4. Story Elaborator transforms stories into BMM-compatible format

---

## SUCCESS CRITERIA

- All stories from Steps 1-9 reviewed
- Consistency validated (no unresolved BLOCKERS)
- Dependencies mapped and sequenced
- Clear GO or REVISE decision with rationale
- Deliverables created based on decision
- Sidecar updated with review status

---

## SYSTEM FAILURE CONDITIONS

- Approving GO when BLOCKERS exist
- Not reviewing all step outputs
- Making decision without user confirmation
- Not creating required deliverables
- Skipping dependency analysis

---

*Step 10 is the quality gate. Marcus takes this responsibility seriously.*
