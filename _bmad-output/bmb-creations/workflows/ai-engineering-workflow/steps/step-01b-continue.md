---
name: 'step-01b-continue'
description: 'Handle AI Engineering workflow continuation from previous session'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/ai-engineering-workflow'

# File References
thisStepFile: '{workflow_path}/steps/step-01b-continue.md'
workflowFile: '{workflow_path}/workflow.md'

# Output References
outputFolder: '{output_folder}/{project_name}'
sidecarFile: '{outputFolder}/sidecar.yaml'

# Step File References (for determining next step)
step02: '{workflow_path}/steps/step-02-scoping.md'
step03: '{workflow_path}/steps/step-03-feature-pipeline.md'
step04: '{workflow_path}/steps/step-04-training-pipeline.md'
step05: '{workflow_path}/steps/step-05-inference-pipeline.md'
step06: '{workflow_path}/steps/step-06-evaluation-and-gate.md'
step07: '{workflow_path}/steps/step-07-operations-and-complete.md'
---

# Step 1B: Workflow Continuation

## STEP GOAL:

To resume the AI Engineering workflow from where it was left off, ensuring smooth continuation without loss of context or progress.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- ✅ You are an AI Engineering Architect
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring FTI pipeline expertise backed by the Knowledge MCP
- ✅ User brings their domain requirements and constraints
- ✅ Maintain collaborative, technical tone throughout

### Step-Specific Rules:

- 🎯 Focus ONLY on analyzing and resuming workflow state
- 🚫 FORBIDDEN to modify content completed in previous steps
- 💬 Maintain continuity with previous sessions
- 🚪 DETECT exact continuation point from sidecar.yaml

## EXECUTION PROTOCOLS:

- 🎯 Show your analysis of current state before taking action
- 💾 Keep existing sidecar `stepsCompleted` values intact
- 📖 Review the project outputs already generated
- 🚫 FORBIDDEN to modify content that was completed in previous steps
- 📝 Update sidecar with continuation timestamp when resuming

## CONTEXT BOUNDARIES:

- Sidecar.yaml contains the workflow state
- Previous context = project-spec.md + decision-log.md + phase outputs
- Last completed step = last value in `stepsCompleted` array
- Architecture decision may already be made (check sidecar)

## CONTINUATION SEQUENCE:

### 1. Analyze Current State

Read `sidecar.yaml` to understand:

- `stepsCompleted`: Which steps are already done (rightmost value = last completed)
- `currentPhase`: Which FTI phase we're in (0-5)
- `architecture`: Architecture decision if made ("rag-only" | "fine-tuning" | "hybrid")
- `decisions`: Summary of decisions made
- `phases`: Status of each phase

Example: If `stepsCompleted: [1, 2, 3]`, step 3 (Feature Pipeline) was the last completed.

### 2. Map Steps to Phases

| Step | Phase | File |
|------|-------|------|
| 1 | Init | step-01-init.md |
| 2 | Phase 0: Scoping | step-02-scoping.md |
| 3 | Phase 1: Feature Pipeline | step-03-feature-pipeline.md |
| 4 | Phase 2: Training Pipeline | step-04-training-pipeline.md |
| 5 | Phase 3: Inference Pipeline | step-05-inference-pipeline.md |
| 6 | Phase 4: Evaluation + Gate | step-06-evaluation-and-gate.md |
| 7 | Phase 5: Operations | step-07-operations-and-complete.md |

### 3. Determine Next Step

Based on the last value in `stepsCompleted`:

- If last = 1 → Next = step-02-scoping.md (Phase 0)
- If last = 2 → Next = step-03-feature-pipeline.md (Phase 1)
- If last = 3 → Check architecture:
  - If "rag-only" → Next = step-05-inference-pipeline.md (skip training)
  - If "fine-tuning" or "hybrid" → Next = step-04-training-pipeline.md
- If last = 4 → Next = step-05-inference-pipeline.md (Phase 3)
- If last = 5 → Next = step-06-evaluation-and-gate.md (Phase 4)
- If last = 6 → Next = step-07-operations-and-complete.md (Phase 5)
- If last = 7 → Workflow complete!

### 4. Review Previous Output

Read key project files to understand context:

- `project-spec.md` - What's been documented so far
- `decision-log.md` - What decisions have been made
- Phase-specific outputs in `phase-X-*/` folders

### 5. Welcome Back Dialog

Present a warm, context-aware welcome:

"**Welcome back to '{project_name}'!**

**Progress so far:**
- Steps completed: {stepsCompleted}
- Current phase: {currentPhase}
- Architecture: {architecture or 'Not yet decided'}

**Last completed:** [Brief description of last step based on step number]

**Next up:** [Description of next step]

We're ready to continue with [next phase name].

Would you like to:
1. Review what we've accomplished so far?
2. Continue where we left off?
3. See the decisions we've made?"

### 6. Handle User Choice

- **If Review (1):** Summarize project-spec.md content, then return to menu
- **If Continue (2):** Proceed to next step
- **If Decisions (3):** Show decision-log.md summary, then return to menu

### 7. Present MENU OPTIONS

Display: **Resuming workflow - Select an Option:** [R] Review Progress [D] View Decisions [C] Continue to Next Phase

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF R: Show project-spec.md summary, then redisplay menu
- IF D: Show decision-log.md summary, then redisplay menu
- IF C:
  1. Update sidecar: add `lastContinued: {date}`
  2. Determine next step file from section 3 logic
  3. Load, read entire file, then execute the appropriate next step
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN C is selected and continuation analysis is complete, will you then:

1. Update sidecar.yaml with continuation timestamp
2. Load, read entire file, then execute the next step file determined from the analysis

Do NOT modify any other content in the project outputs during this continuation step.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Correctly identified last completed step from `stepsCompleted` array
- Read and understood project context
- User confirmed readiness to continue
- Sidecar updated with continuation timestamp
- Workflow resumed at appropriate next step
- Conditional flow respected (RAG-only skips training)

### ❌ SYSTEM FAILURE:

- Skipping analysis of existing state
- Modifying content from previous steps
- Loading wrong next step file
- Not respecting RAG-only skip logic
- Not updating sidecar with continuation info
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
