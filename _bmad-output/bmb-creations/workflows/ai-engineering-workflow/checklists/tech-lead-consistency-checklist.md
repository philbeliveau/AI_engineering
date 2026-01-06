# Tech Lead Consistency Validation Checklist

**Project:** {{PROJECT_NAME}}
**Date:** {{DATE}}
**Tech Lead:** Marcus (AI Engineering Workflow)

---

## Purpose

This checklist provides structured validation criteria for the `*validate-consistency` command in Step 10. It identifies BLOCKERS, WARNINGS, and INFO items that must be addressed before the GO/REVISE decision.

---

## How to Use

1. **Load all project artifacts** (see LOAD CONTEXT in step-10-tech-lead.md)
2. **Work through each section** systematically
3. **Categorize findings:**
   - 🔴 **BLOCKER** - Must fix before GO
   - 🟡 **WARNING** - Should address, may proceed with risk
   - 🔵 **INFO** - Noted, no action required
4. **Document findings** in the Notes column
5. **Make GO/REVISE decision** based on blocker count

---

## 1. Architecture Alignment

Verify all phase outputs align with the architecture decision from Step 2.

| Check | Status | Severity | Notes |
|-------|--------|----------|-------|
| [ ] Architecture decision documented | | | ARCH-001 in decision-log.md |
| [ ] All steps reference correct architecture | | | rag-only/fine-tuning/hybrid |
| [ ] Step 5 skip handled correctly (if RAG-only) | | | training-spec.md status |
| [ ] Phase outputs match architecture implications | | | No contradictions |

**Key Files:**
- `phase-0-scoping/architecture-decision.md`
- `sidecar.yaml` → `architecture` field

---

## 2. Decision Consistency

Verify decisions don't contradict each other across steps.

| Check | Status | Severity | Notes |
|-------|--------|----------|-------|
| [ ] No conflicting technology choices | | | Same DB, framework, etc. |
| [ ] Embedding model consistent across steps | | | Step 4 → Step 6 |
| [ ] Vector DB config consistent | | | Step 4 → Step 6 |
| [ ] Latency targets consistent | | | Step 1 → Step 8 → Step 9 |
| [ ] Cost constraints respected | | | Budget vs. chosen tools |
| [ ] Context window limits consistent | | | Chunking → RAG → Prompts |

**Key Files:**
- `decision-log.md` - All ARCH-*, DATA-*, EMB-*, etc.

---

## 3. Dependency Validation

Verify stories have correct dependency chains.

| Check | Status | Severity | Notes |
|-------|--------|----------|-------|
| [ ] Data pipeline stories precede embeddings | | | DATA-S* before EMB-S* |
| [ ] Embeddings stories precede RAG | | | EMB-S* before RAG-S* |
| [ ] RAG stories precede prompts | | | RAG-S* before PROMPT-S* |
| [ ] Training stories properly sequenced (if hybrid) | | | TRAIN-S* timing |
| [ ] Evaluation stories depend on inference | | | EVAL-S* has correct deps |
| [ ] Operations stories are final | | | OPS-S* depend on all others |

**Dependency Map:**
```
ARCH-S* → DATA-S* → EMB-S* → [TRAIN-S* if hybrid] → RAG-S* → PROMPT-S* → EVAL-S* → OPS-S*
```

---

## 4. Completeness Check

Verify no gaps in coverage.

| Check | Status | Severity | Notes |
|-------|--------|----------|-------|
| [ ] All use cases covered by stories | | | Map UC → Stories |
| [ ] All success metrics have evaluation stories | | | Metrics → EVAL-S* |
| [ ] All data sources have pipeline stories | | | Sources → DATA-S* |
| [ ] All constraints addressed | | | Constraints → Decisions |
| [ ] All risks have mitigation in stories | | | Risks → Stories |

**Key Files:**
- `phase-0-scoping/business-requirements.md` (source of truth)
- `sidecar.yaml` → `stories.*` (story inventory)

---

## 5. Quality Gate Prerequisites

Verify Phase 4 (Evaluation) setup is complete.

| Check | Status | Severity | Notes |
|-------|--------|----------|-------|
| [ ] Evaluation criteria defined | | | Thresholds set |
| [ ] Test datasets specified | | | Golden set, edge cases |
| [ ] Quality gate checklist ready | | | quality-gate-checklist.md |
| [ ] Go/No-Go criteria explicit | | | Blocking vs. advisory |

**Key Files:**
- `phase-4-evaluation/evaluation-spec.md`
- `checklists/quality-gate-checklist.md`

---

## 6. Operational Readiness Prerequisites

Verify Phase 5 (Operations) can proceed.

| Check | Status | Severity | Notes |
|-------|--------|----------|-------|
| [ ] Monitoring metrics defined | | | Key metrics identified |
| [ ] Alerting strategy outlined | | | Severity levels |
| [ ] Runbook structure planned | | | Procedures identified |
| [ ] Deployment strategy chosen | | | Blue-green/canary/rolling |

**Key Files:**
- `phase-5-operations/operations-spec.md`
- `phase-5-operations/runbook.md`

---

## 7. Story Integrity

Verify all stories are well-formed and complete.

| Check | Status | Severity | Notes |
|-------|--------|----------|-------|
| [ ] All stories have unique IDs | | | No duplicates |
| [ ] All stories have acceptance criteria | | | At least 2-3 ACs |
| [ ] Story IDs follow prefix convention | | | ARCH-S*, DATA-S*, etc. |
| [ ] No orphan stories (unlinked to phase) | | | All categorized |
| [ ] Story count reasonable for scope | | | Not too few, not bloated |

**Story ID Prefix Reference:**
| Step | Prefix |
|------|--------|
| 2 | ARCH-S* |
| 3 | DATA-S* |
| 4 | EMB-S* |
| 5 | TRAIN-S* |
| 6 | RAG-S* |
| 7 | PROMPT-S* |
| 8 | EVAL-S* |
| 9 | OPS-S* |

---

## 8. Knowledge Grounding

Verify Knowledge MCP was queried appropriately.

| Check | Status | Severity | Notes |
|-------|--------|----------|-------|
| [ ] Architecture decision knowledge-grounded | | | get_decisions called |
| [ ] Key patterns referenced | | | get_patterns results |
| [ ] Warnings surfaced | | | get_warnings results |
| [ ] Knowledge gaps noted | | | If queries returned empty |

**Key Queries to Verify:**
- Step 2: `get_decisions` for RAG vs fine-tuning
- Steps 3-9: `get_patterns` and `get_warnings` for each domain

---

## Findings Summary

### 🔴 BLOCKERS (Must Fix)

| ID | Finding | Affected Steps | Resolution |
|----|---------|----------------|------------|
| B1 | | | |
| B2 | | | |
| B3 | | | |

### 🟡 WARNINGS (Should Address)

| ID | Finding | Risk Level | Recommendation |
|----|---------|------------|----------------|
| W1 | | | |
| W2 | | | |
| W3 | | | |

### 🔵 INFO (Noted)

| ID | Finding | Impact |
|----|---------|--------|
| I1 | | |
| I2 | | |
| I3 | | |

---

## GO/REVISE Decision

### Validation Summary

| Category | Items | Passed | Blockers | Warnings |
|----------|-------|--------|----------|----------|
| Architecture Alignment | 4 | | | |
| Decision Consistency | 6 | | | |
| Dependency Validation | 6 | | | |
| Completeness Check | 5 | | | |
| Quality Gate Prerequisites | 4 | | | |
| Operational Readiness | 4 | | | |
| Story Integrity | 5 | | | |
| Knowledge Grounding | 4 | | | |
| **TOTAL** | **38** | | | |

### Decision

**Based on validation results:**

- [ ] **GO** - No blockers, proceed to Story Elaboration (Step 11)
- [ ] **REVISE** - Blockers exist, must return to specified step(s)

### If GO:

- All blockers resolved or none found
- Warnings documented and accepted
- Stories ready for sequencing and elaboration

### If REVISE:

**Return to Step(s):**

| Step | Agent | Issue | Required Fix |
|------|-------|-------|--------------|
| | | | |

**Revision Instructions:**
1.
2.
3.

---

## Integration with Sidecar

When validation complete, update `sidecar.yaml`:

```yaml
integrationReview:
  validated: true
  validated_at: "{date}"
  blockers_found: [count]
  warnings_found: [count]
  decision: "[GO | REVISE]"

  # If REVISE
  revise_steps: [list of step numbers]
  revise_reason: "[brief explanation]"
```

---

*Generated by AI Engineering Workflow v1.0*
