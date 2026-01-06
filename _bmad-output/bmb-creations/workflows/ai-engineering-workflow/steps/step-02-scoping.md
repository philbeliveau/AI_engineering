---
name: 'step-02-scoping'
description: 'Phase 0: Determine architecture direction through RAG vs Fine-tuning decision'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/ai-engineering-workflow'

# File References
thisStepFile: '{workflow_path}/steps/step-02-scoping.md'
nextStepFile: '{workflow_path}/steps/step-03-feature-pipeline.md'
workflowFile: '{workflow_path}/workflow.md'

# Output References
outputFolder: '{output_folder}/{project_name}'
sidecarFile: '{outputFolder}/sidecar.yaml'
projectSpecFile: '{outputFolder}/project-spec.md'
decisionLogFile: '{outputFolder}/decision-log.md'
scopingFolder: '{outputFolder}/phase-0-scoping'
architectureDecisionFile: '{scopingFolder}/architecture-decision.md'
---

# Step 2: Phase 0 - Scoping

## STEP GOAL:

To determine the foundational architecture direction (RAG-only, Fine-tuning, or Hybrid) through collaborative analysis of use case requirements, constraints, and knowledge-grounded decision criteria.

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

- 🎯 Focus ONLY on the RAG vs Fine-tuning decision
- 🚫 FORBIDDEN to discuss implementation details (that's Phase 1-3)
- 💬 This is the MOST IMPORTANT decision - take time to get it right
- 🧠 Query Knowledge MCP for decision criteria and trade-offs

## EXECUTION PROTOCOLS:

- 🎯 Show your reasoning before making recommendations
- 💾 Update sidecar with `architecture` value when decision is made
- 📖 Record the decision in both decision-log.md and architecture-decision.md
- 🚫 FORBIDDEN to proceed to Phase 1 without clear architecture decision

## CONTEXT BOUNDARIES:

- Previous context = project-spec.md header from Step 1
- Use case requirements gathered fresh in this step
- Architecture decision determines entire workflow path
- RAG-only skips Phase 2 (Training Pipeline)

## SCOPING SEQUENCE:

### 1. Welcome to Phase 0

Present the phase introduction:

"**Phase 0: Scoping - The Most Critical Decision**

Before we build anything, we need to answer one question that determines everything else:

**Should we use RAG, Fine-tuning, or a Hybrid approach?**

This decision impacts:
- Development complexity and timeline
- Infrastructure requirements and cost
- Data requirements and privacy considerations
- Performance characteristics and latency
- Maintenance and update patterns

Let's work through this systematically."

### 2. Query Knowledge MCP for Decision Criteria

Before gathering requirements, query the Knowledge MCP:

**Query 1: Decision Framework**
```
Endpoint: get_decisions
Topic: RAG vs fine-tuning
```

Present the decision criteria to the user:
"Here's what the knowledge base tells us about this decision..."

**Query 2: Common Warnings**
```
Endpoint: get_warnings
Topic: fine-tuning mistakes
```

Surface anti-patterns:
"And here are common pitfalls to avoid..."

### 3. Gather Use Case Requirements

Guide the user through structured requirements gathering:

**A. Use Case Classification**

"Let's classify your use case. Which best describes your project?"

| Category | Description | Typical Direction |
|----------|-------------|-------------------|
| **Knowledge QA** | Answer questions from documents | RAG |
| **Content Generation** | Create new content in specific style | Fine-tuning |
| **Classification/Extraction** | Categorize or extract structured data | Fine-tuning (or prompting) |
| **Conversational Agent** | Multi-turn dialogue with memory | Hybrid |
| **Code Assistant** | Help with programming tasks | Hybrid |
| **Domain Expert** | Deep expertise in specialized field | Depends on data availability |

Ask: "Which category best fits your project? Tell me more about what you're building."

**B. Data Assessment**

"Now let's assess your data situation:"

| Factor | Question | Impact |
|--------|----------|--------|
| **Volume** | How much training data do you have? | <1000 examples → RAG, >10K → FT possible |
| **Quality** | Is the data clean and labeled? | Poor quality → RAG safer |
| **Sensitivity** | Does data contain PII/secrets? | Sensitive → RAG (data stays separate) |
| **Update Frequency** | How often does information change? | Frequent updates → RAG |
| **Proprietary Knowledge** | Do you need custom terminology/reasoning? | Yes → Fine-tuning value |

Ask: "Walk me through your data situation using these factors."

**C. Constraint Analysis**

"Let's understand your constraints:"

| Constraint | Options | Trade-off |
|------------|---------|-----------|
| **Budget** | Limited / Moderate / Flexible | FT has higher upfront cost |
| **Timeline** | Days / Weeks / Months | RAG is faster to implement |
| **Team Skills** | ML-experienced / General devs | FT requires ML expertise |
| **Latency Requirements** | Real-time / Near-real-time / Batch | FT can be faster at inference |
| **Accuracy Requirements** | Good enough / High / Critical | Hybrid for highest accuracy |

Ask: "What are your key constraints?"

### 4. Synthesize and Present Architecture Options

Based on gathered information, present the three options:

**Option A: RAG-Only**
```
Best when:
- Knowledge is in documents that change frequently
- Privacy requires keeping data separate from model
- Need to cite sources for answers
- Limited ML expertise on team
- Quick time-to-market needed

Trade-offs:
+ Faster development, easier updates
+ Source attribution built-in
+ Data stays in your control
- Retrieval quality limits overall quality
- Higher latency (retrieval + generation)
- Context window limits
```

**Option B: Fine-tuning**
```
Best when:
- Need specific style, tone, or behavior
- Have abundant high-quality training data
- Custom terminology or domain reasoning required
- Latency is critical
- Task is well-defined and stable

Trade-offs:
+ Better task-specific performance
+ Lower inference latency
+ Consistent behavior
- Requires ML expertise
- Harder to update knowledge
- Risk of hallucination without grounding
```

**Option C: Hybrid (RAG + Fine-tuning)**
```
Best when:
- Need both current knowledge AND specialized behavior
- Building production system with high accuracy requirements
- Have resources for both approaches
- Complex use case with multiple requirements

Trade-offs:
+ Best of both worlds
+ Highest quality ceiling
- Most complex to build and maintain
- Highest resource requirements
- Longer development timeline
```

### 5. Make the Architecture Decision

Guide to decision:

"Based on our discussion:

**Your Use Case:** [summarize]
**Your Data:** [summarize]
**Your Constraints:** [summarize]

**My Recommendation:** [RAG-only | Fine-tuning | Hybrid]

**Rationale:** [explain why this fits their situation]

Do you agree with this direction, or would you like to discuss further?"

### 6. Document the Decision

Once user confirms, create the architecture decision record.

**Update sidecar.yaml:**
```yaml
architecture: "[rag-only | fine-tuning | hybrid]"
currentPhase: 1
stepsCompleted: [1, 2]
decisions:
  - id: "arch-001"
    choice: "[chosen architecture]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_decisions:rag-vs-fine-tuning"
phases:
  phase_0_scoping: "complete"
```

**Create architecture-decision.md:**
```markdown
# Architecture Decision Record: RAG vs Fine-tuning

## Decision
[Architecture choice]

## Context
[Use case description and requirements]

## Options Considered
1. RAG-only: [pros/cons for this project]
2. Fine-tuning: [pros/cons for this project]
3. Hybrid: [pros/cons for this project]

## Decision Rationale
[Why this option was chosen]

## Knowledge Reference
Query: get_decisions - "RAG vs fine-tuning"
Key insights applied: [list relevant insights]

## Consequences
- [Impact on Phase 1 - Feature Pipeline]
- [Impact on Phase 2 - Training Pipeline (skipped if RAG-only)]
- [Impact on Phase 3 - Inference Pipeline]

## Date
{date}
```

**Append to decision-log.md:**
```markdown
## ARCH-001: Architecture Direction

**Decision:** [RAG-only | Fine-tuning | Hybrid]
**Date:** {date}
**Phase:** 0 - Scoping

**Context:** [Brief use case description]

**Options Evaluated:**
1. RAG-only
2. Fine-tuning
3. Hybrid

**Choice Rationale:** [Why this option]

**Knowledge Reference:** `get_decisions:rag-vs-fine-tuning`

**Consequences:**
- [List key implications]
```

**Update project-spec.md:**
```markdown
## Project Overview

**Use Case:** [Description from discussion]
**Architecture:** [RAG-only | Fine-tuning | Hybrid]
**Key Requirements:**
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

**Constraints:**
- [Constraint 1]
- [Constraint 2]

---
```

### 7. Present MENU OPTIONS

Display: **Phase 0 Complete - Select an Option:** [A] Analyze decision further [P] View progress [C] Continue to Phase 1

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit decision criteria, allow refinement, then redisplay menu
- IF P: Show project-spec.md and decision-log.md summaries, then redisplay menu
- IF C:
  1. Verify sidecar is updated with architecture decision
  2. Load, read entire file, then execute `{nextStepFile}` (Feature Pipeline)
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND architecture decision is documented, will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Phase 1: Feature Pipeline.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Knowledge MCP queried for decision criteria
- Use case thoroughly analyzed with user
- Clear architecture decision made and documented
- Sidecar updated with architecture value
- Architecture-decision.md created
- Decision-log.md updated
- Project-spec.md updated with overview
- User confirmed direction before proceeding

### ❌ SYSTEM FAILURE:

- Making architecture decision without user input
- Skipping Knowledge MCP queries
- Not documenting the decision in all required files
- Proceeding to Phase 1 without confirmed architecture
- Not updating sidecar with architecture value
- Discussing implementation details (belongs in Phase 1-3)

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
