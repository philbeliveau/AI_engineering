# AI Engineering Workflow - Checklist Design Documentation

**Date:** 2026-01-06
**Author:** BMad Builder (Checklist Design Task)
**Workflow:** AI Engineering Workflow v1.0

---

## Summary

This document describes the checklist design decisions for the AI Engineering Workflow.

---

## Checklist Inventory

### Final Checklist Set (3 files)

| Checklist | Purpose | Integration Point | Status |
|-----------|---------|-------------------|--------|
| `quality-gate-checklist.md` | Deployment readiness validation | Step 8 (LLM Evaluator) | **EXISTS** - No changes needed |
| `step-01-completion-checklist.md` | Business requirements completeness | Step 1 (Business Analyst) | **NEW** - Created |
| `tech-lead-consistency-checklist.md` | Cross-step consistency validation | Step 10 (Tech Lead) | **NEW** - Created |

---

## Design Rationale

### Why Only 3 Checklists?

1. **Avoid checkbox fatigue** - Too many checklists burden users without adding value
2. **DRY principle** - Steps 2-9 have inline SUCCESS/FAILURE criteria that are sufficient
3. **Strategic placement** - Checklists are placed at key decision points:
   - **Step 1** → Start of workflow (requirements complete?)
   - **Step 8** → Quality gate (ready for production?)
   - **Step 10** → Final review (all work consistent?)

### What Was NOT Created (And Why)

| Proposed Checklist | Reason NOT Created |
|--------------------|-------------------|
| Per-step completion checklists | Steps 2-9 have inline SUCCESS/FAILURE criteria that are actionable |
| Phase-level checklists | Each step validates its prerequisites; no aggregate needed |
| Prerequisites validation checklists | "LOAD CONTEXT" sections are explicit and sufficient |
| Story validation checklists | Story Elaborator (Step 11) has BMM compliance rules inline |

---

## Checklist Structure Pattern

All checklists follow this pattern (aligned with `quality-gate-checklist.md`):

```markdown
# [Checklist Name]

**Project:** {{PROJECT_NAME}}
**Date:** {{DATE}}
**[Role]:** [Who fills this out]

---

## Purpose
[1-2 sentences on when/why to use]

---

## [Category 1]
| Item | Status | Evidence/Notes |
|------|--------|----------------|
| [ ] Check item | | |

---

## Summary
[Aggregated pass/fail counts]

---

## Decision
[GO/NO-GO or similar decision with options]

---

## Integration with Sidecar
[YAML snippet showing what to update in sidecar.yaml]
```

---

## Integration Points

### Step 1: Business Analyst

**File Changed:** `steps/0-scoping/step-01-business-analyst.md`
**Location:** Menu Handling Logic → [R] Review Requirements Summary
**Change:** Added `**Use Checklist:** Load {workflow_path}/checklists/step-01-completion-checklist.md`

**When Used:**
- User selects [R] to review requirements
- Agent loads checklist and works through 8 categories with user
- Checklist items map to the 8 completion criteria from CRITICAL STEP COMPLETION NOTE

### Step 8: LLM Evaluator

**File Changed:** `steps/4-evaluation/step-08-llm-evaluator.md`
**Location:** Section 7. Quality Gate Design → A. Quality Gate Checklist
**Change:** Replaced inline simplified checklist with reference to comprehensive external file

**When Used:**
- After evaluation framework is designed
- Before GO/NO-GO decision
- Agent loads `{workflow_path}/checklists/quality-gate-checklist.md`
- Works through 8 categories (46+ items) with user

### Step 10: Tech Lead

**Files Changed:**
1. `steps/6-integration/step-10-tech-lead.md` - Added "Command Details" subsection
2. `agents/tech-lead.md` - Updated `validate-consistency` prompt with checklist reference and 8 categories

**Changes:**
- Step file: Added checklist reference for `*validate-consistency` command
- Agent file: Updated `<prompt id="validate-consistency">` with explicit checklist loading and 8 validation categories
- Agent file: Updated `<prompt id="go-decision">` pre-decision checklist with reference

**When Used:**
- User invokes `*validate-consistency` command
- Marcus loads `{workflow_path}/checklists/tech-lead-consistency-checklist.md`
- Works through 8 validation categories (38 items)
- Findings categorized as BLOCKER (🔴), WARNING (🟡), INFO (🔵)
- Results feed into GO/REVISE decision in `*go-decision`

---

## Sidecar Integration

### Step 1 Completion Updates
```yaml
business_analysis:
  checklist_validated: true
  validated_at: "{date}"
```

### Step 8 Quality Gate Updates
```yaml
quality_gate:
  decision: "[GO | NO-GO | CONDITIONAL]"
  validated_at: "{date}"
```

### Step 10 Consistency Validation Updates
```yaml
integrationReview:
  validated: true
  blockers_found: [count]
  warnings_found: [count]
  decision: "[GO | REVISE]"
```

---

## Variable Naming Convention

All checklists use `{{UPPERCASE_FORMAT}}` for variables:

| Variable | Description |
|----------|-------------|
| `{{PROJECT_NAME}}` | Project name from sidecar.yaml |
| `{{DATE}}` | Current date when checklist is used |
| `{{REVIEWER}}` | Name/role of person completing checklist |

---

## Validation Traceability

### Step 1 Checklist → Business Requirements
| Checklist Category | Source Criteria |
|--------------------|-----------------|
| Stakeholder Identification | CRITICAL STEP COMPLETION NOTE item 1 |
| Use Case Documentation | CRITICAL STEP COMPLETION NOTE item 2 |
| Success Metrics | CRITICAL STEP COMPLETION NOTE item 3 |
| Data Landscape | CRITICAL STEP COMPLETION NOTE item 4 |
| Constraints | CRITICAL STEP COMPLETION NOTE item 5 |
| Risk Assessment | CRITICAL STEP COMPLETION NOTE item 6 |
| Artifacts | CRITICAL STEP COMPLETION NOTE item 7 |
| User Confirmation | CRITICAL STEP COMPLETION NOTE item 8 |

### Tech Lead Checklist → Step Success Criteria
| Checklist Category | Validates Steps |
|--------------------|-----------------|
| Architecture Alignment | Step 2 output |
| Decision Consistency | Steps 2-9 decision-log entries |
| Dependency Validation | Story relationships |
| Completeness Check | Requirements → Stories mapping |
| Quality Gate Prerequisites | Step 8 output |
| Operational Readiness | Step 9 output |
| Story Integrity | All step story outputs |
| Knowledge Grounding | Knowledge MCP usage |

---

## Testing Recommendations

1. **Step 1 Checklist Test:**
   - Run through Step 1 with a sample project
   - When selecting [R], verify checklist loads and categories display
   - Verify sidecar updates correctly when complete

2. **Tech Lead Checklist Test:**
   - Complete Steps 1-9 with a sample project
   - Invoke `*validate-consistency`
   - Verify all 8 categories can be evaluated
   - Test BLOCKER/WARNING/INFO categorization
   - Test GO/REVISE decision flow

3. **Quality Gate Checklist Test:**
   - Already in use - verify no regressions

---

## Future Considerations

If the workflow grows, consider:

1. **Checklist Templates** - Move to `templates/` folder if more checklists needed
2. **Dynamic Checklists** - Generate checklist items from sidecar.yaml content
3. **Checklist Automation** - Script to auto-check certain items (file existence, etc.)

---

*Generated by BMad Builder - AI Engineering Workflow Checklist Design Task*
