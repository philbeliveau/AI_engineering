# Step 11: Story Elaborator

Execute the Story Elaborator step - transform stories to BMM format for development handoff.

---

## Phase: 6 - Integration & Handoff

## Instructions

You are executing **Step 11** (final step) of the AI Engineering Workflow.

### Execution Sequence

1. **Load the step file**: Read `steps/6-integration/step-11-story-elaborator.md` completely
2. **Execute the step**: Follow ALL instructions in the step file exactly as written
3. **Generate BMM stories**: Transform all accumulated stories to BMM format

### What This Step Does

| Aspect | Details |
|--------|---------|
| **Agent** | 📚 Story Elaborator (embedded) |
| **Focus** | BMM format transformation, task breakdown |
| **Outputs** | Full BMM story files ready for dev agent |
| **Next Step** | Handoff to BMM Dev Agent |

### Key Activities

1. Read all stories from sidecar.yaml
2. Transform each story to BMM format:
   - Story statement (As a... I want... So that...)
   - Acceptance criteria
   - Tasks and subtasks
   - Dev notes with architecture context
3. Save stories to sprint artifacts folder
4. Prepare for dev agent handoff

### BMM Story Format

```markdown
# Story X.Y: [Title]

Status: ready-for-dev

## Story
As a [role],
I want to [action],
So that [benefit].

## Acceptance Criteria
1. [Criterion 1]
2. [Criterion 2]

## Tasks / Subtasks
- [ ] Task 1 (AC: #1)
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2

## Dev Notes
- Architecture: [reference]
- Patterns: [from knowledge base]
```

### Handoff to Development

After story elaboration:
```
/bmad:bmm:agents:dev
→ Select *dev-story
→ Stories auto-discovered from sprint artifacts
```

---

**BEGIN**: Execute `steps/6-integration/step-11-story-elaborator.md`
