# Handoff: Implementation Agents for AI Engineering Workflow

**Date:** 2026-01-06
**From:** BMad Builder Session
**To:** Next Session (BMad Builder)
**Priority:** Configure implementation pipeline (Tech Lead → Story Elaborator → Dev → Code Review)

---

## Executive Summary

The AI Engineering Workflow now has 11 steps for **planning and design**. After Step 11 (Story Elaborator), we need an **implementation pipeline** to execute the stories.

**Key Decision (Updated):** Keep AI Engineering Workflow self-contained - copy agents locally instead of modifying BMM config.

| Role | Approach | Location |
|------|----------|----------|
| **Tech Lead** | New agent (Marcus) | `agents/tech-lead.md` |
| **Dev** | Copied from BMM (Amelia) | `agents/dev.md` |
| **Code Reviewer** | Built-in | `*code-review` in dev agent menu |

**Status:** ✅ COMPLETE - All agents and steps configured. Ready for end-to-end testing.

---

## Architecture Overview

```
AI Engineering Workflow (Steps 1-11)
    │
    │  Step 10: Tech Lead (Marcus) → GO/REVISE
    │  Step 11: Story Elaborator → story files + sprint-status.yaml
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│          AI ENGINEERING IMPLEMENTATION PIPELINE                 │
│          (Self-contained - does NOT modify BMM config)          │
│                                                                 │
│  agents/dev.md (Amelia - local copy)                           │
│      │                                                          │
│      ├── *dev-story                                            │
│      │   - Reads bmm-config.yaml for sprint_artifacts path     │
│      │   - Auto-discovers stories from sprint-status.yaml      │
│      │   - Implements tasks with red-green-refactor            │
│      │   - Marks stories ready-for-review                      │
│      │                                                          │
│      └── *code-review                                          │
│          - Reviews implemented code                             │
│          - Creates action items                                 │
│          - Dev addresses feedback                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent 1: Tech Lead (Step 10)

### Reuse Strategy

The Tech Lead role parallels the **PM (John)** agent from BMM:
- Both make GO/NO-GO decisions
- Both sequence and prioritize work
- Both validate alignment with requirements

**Approach:** Create AI Engineering-specific Tech Lead that inherits patterns from PM.

### Agent Specification

| Field | Value |
|-------|-------|
| **File** | `agents/tech-lead.md` |
| **Role** | Tech Lead |
| **Icon** | 👨‍💼 |
| **Name** | Marcus |
| **Expertise** | System integration, technical leadership, story sequencing, architectural coherence, quality gates |
| **Communication Style** | Strategic and holistic. Sees the big picture while caring about details. Asks hard questions about assumptions and dependencies. Balances perfectionism with pragmatism. Direct like John (PM), but focused on technical delivery. |
| **Principles** | - Integration is where systems succeed or fail<br>- Stories must be sequenced correctly - dependencies matter<br>- Question every assumption - especially your own<br>- Better to revise now than refactor later<br>- Ship when ready, not before<br>- The GO decision is sacred - only give it when truly ready |

### Adaptation from PM (John)

| PM Trait | Tech Lead Adaptation |
|----------|---------------------|
| "Asks WHY relentlessly" | Asks "WHAT DEPENDS ON WHAT" relentlessly |
| "Ruthless prioritization" | Ruthless sequencing |
| "Proactively identify risks" | Proactively identify integration conflicts |
| "Back claims with data" | Back decisions with architectural analysis |

### Menu Commands (Adapted from PM)

```xml
<menu>
  <item cmd="*review-backlog">Review accumulated stories from all steps</item>
  <item cmd="*validate-consistency">Check for conflicts and gaps across stories</item>
  <item cmd="*sequence-stories">Determine implementation order based on dependencies</item>
  <item cmd="*go-decision">Make GO/REVISE decision</item>
  <item cmd="*revise">Send specific step back for revision with feedback</item>
  <item cmd="*dismiss">[D] Dismiss Agent</item>
</menu>
```

---

## Agent 2: Dev (Amelia) - LOCAL COPY

### Why Local Copy Instead of BMM Reuse

**User Decision:** "Why not copy the dev of BMM in the AI Engineering workflow? We don't want to mix the two."

Benefits of local copy:
- AI Engineering Workflow is self-contained
- No need to modify BMM config
- Can evolve independently if needed
- Clear separation of concerns

**Location:** `_bmad-output/bmb-creations/workflows/ai-engineering-workflow/agents/dev.md`

### Key Differences from BMM Dev Agent

| Aspect | BMM Dev | AI Engineering Dev |
|--------|---------|-------------------|
| Config Source | `_bmad/bmm/config.yaml` | `{output_folder}/ai-engineering-workflow/bmm-config.yaml` |
| Sprint Artifacts | BMM sprint_artifacts | AI Engineering stories folder |
| Workflow References | External BMM workflows | Inline prompts |

### Integration Requirements

For the local dev agent to work with AI Engineering Workflow:

**1. Story files must match BMM template:**
```markdown
# Story {epic}.{story}: {title}

Status: ready-for-dev

## Story
As a {role}, I want {action}, so that {benefit}.

## Acceptance Criteria
1. {AC1}

## Tasks / Subtasks
- [ ] Task 1 (AC: #1)
  - [ ] Subtask 1.1

## Dev Notes
- {architecture context}

## Dev Agent Record
### Agent Model Used
### Debug Log References
### Completion Notes List
### File List
```

**2. sprint-status.yaml must exist:**
```yaml
development_status:
  1-1-project-setup: ready-for-dev
  1-2-environment-config: ready-for-dev
```

**3. bmm-config.yaml must exist** (generated by Story Elaborator):
```yaml
sprint_artifacts: "{outputFolder}/stories"
```

**4. project-context.md should exist** (generated by Story Elaborator):
- Coding standards
- Architecture patterns
- File structure conventions

### Invocation

```bash
# After Story Elaborator completes, load the local dev agent:
# agents/dev.md

# Or full path:
# _bmad-output/bmb-creations/workflows/ai-engineering-workflow/agents/dev.md

# Amelia will:
# 1. Read bmm-config.yaml for sprint_artifacts path
# 2. Load sprint-status.yaml
# 3. Find first "ready-for-dev" story
# 4. Implement following TDD
# 5. Mark "review" when complete
```

---

## Agent 3: Code Reviewer - BUILT INTO DEV

### Why No Separate Agent Needed

Code review is **already a menu option** in the BMM dev agent:

```xml
<item cmd="*code-review" workflow="{project-root}/_bmad/bmm/workflows/4-implementation/code-review/workflow.yaml">
  Perform a thorough clean context code review
</item>
```

### How It Works

1. After dev completes a story (status: "review")
2. User invokes `*code-review` from dev agent menu
3. Code review workflow:
   - Analyzes implemented code
   - Creates action items with severity
   - Adds "Review Follow-ups (AI)" section to story
4. Dev agent addresses action items
5. Re-run review until approved

### Best Practice (from dev agent docs)

> 💡 **Tip:** For best results, run `code-review` using a **different** LLM than the one that implemented this story.

---

## Integration Configuration

**The Story Elaborator (Step 11) generates all required files automatically:**

### Generated Files

| File | Purpose |
|------|---------|
| `project-context.md` | Coding standards, architecture patterns (dev agent reads for context) |
| `bmm-config.yaml` | Sprint artifacts path (dev agent reads for story location) |
| `sprint-status.yaml` | Story status tracking (dev agent reads for discovery) |
| `stories/*.md` | BMM-format story files |

### File Locations

All files are output to `{outputFolder}/ai-engineering-workflow/`:

```
{outputFolder}/ai-engineering-workflow/
├── project-context.md      # Coding standards
├── bmm-config.yaml         # Dev agent config
├── sprint-status.yaml      # Story status tracking
└── stories/
    ├── 1-1-project-setup.md
    ├── 1-2-environment-config.md
    └── ...
```

### Dev Agent Configuration

The local dev agent (`agents/dev.md`) reads configuration from:
1. `{project-root}/_bmad/bmb/config.yaml` - User settings (user_name, communication_language)
2. `{output_folder}/ai-engineering-workflow/bmm-config.yaml` - Sprint artifacts path

This approach keeps AI Engineering completely isolated from BMM config.

---

## Execution Flow

### Complete Pipeline

```
1. AI Engineering Workflow (Steps 1-9)
   └── Generate simplified stories in sidecar.yaml

2. Tech Lead (Step 10) - agents/tech-lead.md
   └── Marcus reviews, validates, sequences → GO/REVISE

3. Story Elaborator (Step 11)
   └── Transform to BMM story files
   └── Create sprint-status.yaml
   └── Create project-context.md
   └── Create bmm-config.yaml

4. Local Dev Agent - agents/dev.md
   └── Amelia reads bmm-config.yaml for sprint_artifacts path
   └── *dev-story (implements first ready-for-dev)
   └── Repeats until all stories complete

5. Code Review (per story)
   └── *code-review (in fresh context, different LLM recommended)
   └── Address action items
   └── Re-review until approved

6. Done
   └── All stories status: "done"
```

---

## Progress Status

### Completed

| Task | Status | Location |
|------|--------|----------|
| Tech Lead agent (Marcus) | ✅ DONE | `agents/tech-lead.md` |
| Agent plan documented | ✅ DONE | `_bmad-output/bmb-creations/agent-plan-tech-lead.md` |
| `step-10-tech-lead.md` | ✅ DONE | `steps/6-integration/step-10-tech-lead.md` |
| Local Dev agent (Amelia) | ✅ DONE | `agents/dev.md` |
| `step-11-story-elaborator.md` updates | ✅ DONE | Generates `project-context.md`, `bmm-config.yaml`, references local dev agent |

### Remaining Work

| Task | Priority | Description |
|------|----------|-------------|
| End-to-end testing | MEDIUM | Test full pipeline through local dev agent |

---

## Files Created

All files are relative to `_bmad-output/bmb-creations/workflows/ai-engineering-workflow/`

| File | Description | Status |
|------|-------------|--------|
| `agents/tech-lead.md` | Marcus - Tech Lead agent for GO/REVISE decisions | ✅ Complete |
| `agents/dev.md` | Amelia - Local dev agent (copied from BMM) | ✅ Complete |
| `steps/6-integration/step-10-tech-lead.md` | Loads Tech Lead agent | ✅ Complete |
| `steps/6-integration/step-11-story-elaborator.md` | Generates stories, project-context.md, bmm-config.yaml | ✅ Complete |

---

## How to Continue

**All implementation is complete.** Next step is end-to-end testing:

```bash
# 1. Run AI Engineering Workflow through Step 11
# This generates stories, sprint-status.yaml, project-context.md, bmm-config.yaml

# 2. Load local dev agent
# _bmad-output/bmb-creations/workflows/ai-engineering-workflow/agents/dev.md

# 3. Use *dev-story to implement stories

# 4. Use *code-review for quality checks
```

---

## Success Criteria

1. ~~Tech Lead agent created following BMAD patterns~~ ✅
2. ~~Tech Lead agent includes GO/REVISE decision workflow~~ ✅
3. ~~Step 10 references Tech Lead agent correctly~~ ✅
4. ~~Story Elaborator outputs BMM-compatible files~~ ✅ (project-context.md, bmm-config.yaml, sprint-status.yaml)
5. ~~Local dev agent created (self-contained, no BMM config modification)~~ ✅
6. ~~Step 11 references local dev agent~~ ✅
7. Local dev agent successfully discovers and implements stories (needs testing)
8. Code review workflow functions correctly (needs testing)
9. Full pipeline tested end-to-end (needs testing)

---

## Rationale for Self-Contained Workflow

**Original Party Mode Consensus:** Reuse BMM agents where possible.

**User Feedback:** "Why not copy the dev of BMM in the AI Engineering workflow? We don't want to mix the two."

**Final Decision:** Keep AI Engineering Workflow self-contained with local agent copies.

**Benefits:**
- AI Engineering Workflow is completely independent
- No need to modify BMM config (`_bmad/bmm/config.yaml`)
- Can evolve the dev agent independently for AI-specific needs
- Clear separation between BMM projects and AI Engineering projects

**Key Insight:** The dev agent logic is domain-agnostic (implements any story with tasks/subtasks). Copying it locally preserves this while maintaining isolation.

---

*Handoff created by BMad Builder - 2026-01-06*
*Updated: 2026-01-06 - Changed to local dev agent approach*
