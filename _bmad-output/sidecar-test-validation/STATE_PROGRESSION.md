# Sidecar.yaml State Progression Through Workflow Steps

This document visualizes how sidecar.yaml evolves as the workflow progresses through Steps 1-4.

---

## Initial State (Before Any Steps)

```yaml
project_name: Test-Knowledge-RAG-System
user_name: test-engineer
created: 2026-01-06

# Empty/Null state
architecture: null
currentStep: 0
stepsCompleted: []
decisions: []

# All pending
step_1_business_analyst: pending
step_2_fti_architect: pending
step_3_data_engineer: pending
step_4_embeddings_engineer: pending
...

phase_0_scoping: pending
phase_1_feature: pending
phase_2_training: pending
...

stories:
  step_2_architect: []
  step_3_data: []
  step_4_embeddings: []
  ...
```

**State Metrics:**
- Current Step: 0
- Steps Completed: 0
- Architecture Decision: Not yet made
- Total Decisions: 0
- Total Stories: 0

---

## After Step 1: Business Analyst Completes

### Changes Made by Step 1

The Business Analyst gathers requirements, documents them, and completes the step.

```yaml
# UPDATED: Current progress
currentStep: 1
stepsCompleted: [1]

# UPDATED: Step 1 marked complete
step_1_business_analyst: complete

# NEW: Phase 0 started
phase_0_scoping: in_progress

# APPENDED: First decision added
decisions:
  - id: req-001
    type: business_requirement
    requirement: Building a knowledge QA system for internal documentation
    phase: 0
    date: 2026-01-06T17:45:37.629429
```

**State Metrics:**
- Current Step: 1
- Steps Completed: [1]
- Architecture Decision: Still null (Step 2's job)
- Total Decisions: 1
- Total Stories: 0

**What Can Happen Next:**
- Proceed to Step 2 (FTI Architect) to make architecture decision
- Step 2 will read requirements from Step 1's decision

---

## After Step 2: FTI Architect Makes Architecture Decision

### Changes Made by Step 2

The FTI Architect analyzes requirements and decides the architecture approach.

```yaml
# UPDATED: Current progress
currentStep: 2
stepsCompleted: [1, 2]

# UPDATED: Step 2 marked complete
step_2_fti_architect: complete

# NEW: Architecture decision made
architecture: rag-only

# APPENDED: Architecture decision to decisions array
decisions:
  - id: req-001
    type: business_requirement
    ...

  - id: arch-001
    choice: rag-only
    rationale: Knowledge QA with frequent updates, RAG pattern optimal
    knowledge_ref: get_decisions:rag-vs-fine-tuning
    phase: 0
    date: 2026-01-06T17:45:37.636065

# IMPORTANT: phase_0_scoping still in_progress
# (Will be marked complete after Step 2B - Tech Stack selection)
phase_0_scoping: in_progress
```

**State Metrics:**
- Current Step: 2
- Steps Completed: [1, 2]
- Architecture Decision: **rag-only** (Critical for workflow routing)
- Total Decisions: 2
- Total Stories: 0

**What Can Happen Next:**
- Step 3 can now read the architecture decision
- Subsequent steps can use `if architecture == 'rag-only'` to skip Step 5
- Step 2B will select tech stack, then Phase 0 will be marked complete

---

## After Step 3: Data Engineer Begins Adding Stories

### Changes Made by Step 3

The Data Engineer adds implementation stories for the data pipeline.

```yaml
# UPDATED: Current progress
currentStep: 3
stepsCompleted: [1, 2, 3]

# UPDATED: Step 3 marked complete
step_3_data_engineer: complete

# NEW: Phase 1 started
phase_1_feature: in_progress

# APPENDED: Data engineer's decision
decisions:
  - id: req-001
    ...
  - id: arch-001
    ...
  - id: data-001
    choice: semantic-chunking
    rationale: Preserves context for better retrieval
    phase: 1
    date: 2026-01-06T17:45:37.643567

# CRITICAL: Architecture persists (still accessible)
architecture: rag-only

# NEW: Stories begin accumulating
stories:
  step_2_architect: []                          # Empty (no Step 2 stories)

  step_3_data:                                  # Filled by Step 3
    - id: DATA-S01
      title: Design document ingestion pipeline
      description: Build ETL for PDF/Markdown documents with metadata extraction
      acceptance_criteria:
        - Supports PDF and Markdown formats
        - Extracts document metadata (title, author, date)
        - Handles 100+ document batch processing
        - Logs errors to monitoring system

    - id: DATA-S02
      title: Implement document chunking strategy
      description: Smart chunking preserving semantic boundaries
      acceptance_criteria:
        - Respects document structure (sections, paragraphs)
        - Maintains cross-references
        - Generates chunk metadata

  step_4_embeddings: []                         # Still empty
  step_5_training: []                           # Still empty
  ...
```

**State Metrics:**
- Current Step: 3
- Steps Completed: [1, 2, 3]
- Architecture Decision: **rag-only** (Persists and used for routing)
- Total Decisions: 3
- Total Stories: 2 (in step_3_data)

**Key Observations:**
- Architecture set in Step 2 is still accessible
- Stories organized by step (DATA-S01, DATA-S02)
- Other story arrays remain empty (no spillover)
- Each story has complete structure: id, title, description, acceptance criteria

**What Can Happen Next:**
- Step 4 reads architecture to design embeddings
- Step 4 adds its own stories to step_4_embeddings
- Step 3 stories NOT overwritten or removed

---

## After Step 4: Embeddings Engineer Adds More Stories

### Changes Made by Step 4

The Embeddings Engineer adds stories for embedding infrastructure.

```yaml
# UPDATED: Current progress
currentStep: 4
stepsCompleted: [1, 2, 3, 4]

# UPDATED: Step 4 marked complete
step_4_embeddings_engineer: complete

# PERSISTED: Phase 1 still in_progress
phase_1_feature: in_progress

# APPENDED: Embedding and tech decisions
decisions:
  - id: req-001
    ...
  - id: arch-001
    ...
  - id: data-001
    ...
  - id: emb-001
    choice: text-embedding-3-small
    rationale: Good performance-to-cost ratio, 1536 dimensions suitable for domain
    phase: 1
    date: 2026-01-06T17:45:37.651596

  - id: tech-001
    choice: pinecone
    rationale: Managed service, no infrastructure overhead, good for MVP
    phase: 0
    date: 2026-01-06T17:45:37.651605

# PERSISTED: Architecture still rag-only
architecture: rag-only

# CONDITIONAL: Can determine Step 5 should be skipped
# Based on: architecture == 'rag-only'
phase_2_training: skipped
step_5_fine_tuning_specialist: skipped

# UPDATED: Stories now have entries for Steps 3 and 4
stories:
  step_2_architect: []                          # Empty

  step_3_data:                                  # Persists from Step 3
    - id: DATA-S01
      title: Design document ingestion pipeline
      ...
    - id: DATA-S02
      title: Implement document chunking strategy
      ...

  step_4_embeddings:                            # New from Step 4
    - id: EMB-S01
      title: Select and fine-tune embedding model
      description: Choose embedding model based on domain and evaluate performance
      acceptance_criteria:
        - Model selected: text-embedding-3-small
        - Evaluation metrics calculated
        - Performance meets retrieval targets

    - id: EMB-S02
      title: Build embedding pipeline with caching
      description: Efficient batch embedding generation with Redis caching
      acceptance_criteria:
        - Batch processing for 1000+ vectors
        - Cache hit rate > 90%
        - Latency < 100ms per chunk

    - id: EMB-S03
      title: Setup vector database (Pinecone)
      description: Initialize and configure Pinecone index
      acceptance_criteria:
        - Index created with correct dimensions
        - Metadata filtering configured
        - Backup strategy implemented

  step_5_training: []                           # Skipped (not filled)
  step_6_rag: []                                # Pending
  ...
```

**State Metrics:**
- Current Step: 4
- Steps Completed: [1, 2, 3, 4]
- Architecture Decision: **rag-only** (Used to skip Step 5)
- Total Decisions: 5
- Total Stories: 5 (2 from Step 3, 3 from Step 4)

**Key Observations:**
1. **Story Separation**: Each step has its own story array
   - DATA-S01, DATA-S02 in step_3_data
   - EMB-S01, EMB-S02, EMB-S03 in step_4_embeddings

2. **Architecture Driven Routing**: Based on `architecture == 'rag-only'`:
   - phase_2_training marked as "skipped"
   - step_5_fine_tuning_specialist marked as "skipped"
   - Workflow automatically routes to Step 6 instead

3. **Decision Context**: Decisions include rationale tied to architecture
   - tech-001 (Pinecone) fits RAG pattern
   - emb-001 (embedding model) selected for retrieval task

4. **Story Structure**: Each story is implementation-ready with acceptance criteria
   - Developers can take these directly to sprint backlog

---

## Decision Routing Flow

Based on accumulated state at Step 4:

```
                    ┌─────────────────────────┐
                    │   Step 1: BA            │
                    │ Gathers Requirements    │
                    │ → req-001 decision      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Step 2: Architect     │
                    │ Makes Arch Decision     │
                    │ → arch-001: rag-only    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Step 3: Data Eng      │
                    │ Designs Data Pipeline   │
                    │ → data-001: chunking    │
                    │ → DATA-S01, S02         │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Step 4: Embeddings    │
                    │ Selects Embedding Arch  │
                    │ → emb-001: OpenAI      │
                    │ → tech-001: Pinecone   │
                    │ → EMB-S01, S02, S03    │
                    └────────────┬────────────┘
                                 │
                   ┌─────────────┴──────────────────┐
                   │                                │
                   │  architecture == 'rag-only'?   │
                   │  YES → Skip Step 5             │
                   │                                │
                   └─────────────┬──────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Step 6: RAG Specialist │
                    │ Designs RAG Pipeline     │
                    │ (Training step skipped)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Step 7: Prompt Eng    │
                    │ Optimizes Prompts       │
                    └────────────┬────────────┘
                                 │
                               ...

State checkpoint at Step 4:
├─ currentStep: 4
├─ stepsCompleted: [1, 2, 3, 4]
├─ architecture: rag-only ◄── Used to skip Step 5
├─ phase_2_training: skipped ◄── Result of architecture decision
├─ Decisions: 5 (req, arch, data, emb, tech)
└─ Stories: 5 (DATA×2, EMB×3)
```

---

## State Availability for Conditional Logic

### Step 5 Decision Logic (Uses State from Step 4)

```python
# Pseudo-code showing how Step 5 logic uses accumulated state

sidecar = load_sidecar()

# Can Step 5 execute?
if sidecar['architecture'] == 'rag-only':
    # Skip fine-tuning entirely
    sidecar['steps']['step_5_fine_tuning_specialist'] = 'skipped'
    sidecar['phases']['phase_2_training'] = 'skipped'
    next_step = 6  # Skip to RAG specialist

elif sidecar['architecture'] == 'fine-tuning':
    # Execute full fine-tuning
    sidecar['currentStep'] = 5
    next_step = 6

elif sidecar['architecture'] == 'hybrid':
    # Execute fine-tuning then RAG
    sidecar['currentStep'] = 5
    next_step = 6

save_sidecar(sidecar)
proceed_to_step(next_step)
```

### Checkpointing/Resumption Logic (Uses State from Step 4)

```python
# Pseudo-code showing resumption from saved checkpoint

sidecar = load_sidecar()

# Where did we leave off?
current = sidecar['currentStep']  # 4
completed = sidecar['stepsCompleted']  # [1, 2, 3, 4]
arch = sidecar['architecture']  # 'rag-only'

print(f"Last completed: Step {current}")
print(f"All steps: {completed}")
print(f"Architecture: {arch}")

# What was decided?
for decision in sidecar['decisions']:
    print(f"- {decision['id']}: {decision['choice']}")

# What stories were created?
for step_key, stories in sidecar['stories'].items():
    if stories:
        print(f"- {step_key}: {len(stories)} stories")
        for story in stories:
            print(f"  * {story['id']}: {story['title']}")

# Resume workflow
if arch == 'rag-only':
    print("Proceeding to Step 6 (RAG Specialist)")
else:
    print("Proceeding to Step 5 (Fine-tuning Specialist)")
```

---

## Accumulation Pattern

### How Decisions Accumulate

```
Step 1 → decisions: [req-001]
Step 2 → decisions: [req-001, arch-001]
Step 3 → decisions: [req-001, arch-001, data-001]
Step 4 → decisions: [req-001, arch-001, data-001, emb-001, tech-001]
Step 5 → decisions: [..., training-001]
...
```

Each step APPENDS to the decisions array (never overwrites).

### How Stories Accumulate

```
Step 2 → stories: {step_2_architect: [], ...}
Step 3 → stories: {step_2_architect: [], step_3_data: [DATA-S01, DATA-S02], ...}
Step 4 → stories: {
           step_2_architect: [],
           step_3_data: [DATA-S01, DATA-S02],
           step_4_embeddings: [EMB-S01, EMB-S02, EMB-S03],
           ...
         }
```

Each step fills its own story array. Previous arrays persist.

---

## Summary of State Transitions

| Metric | Initial | After Step 1 | After Step 2 | After Step 3 | After Step 4 |
|--------|---------|--------------|--------------|--------------|--------------|
| currentStep | 0 | 1 | 2 | 3 | 4 |
| stepsCompleted | [] | [1] | [1,2] | [1,2,3] | [1,2,3,4] |
| architecture | null | null | rag-only | rag-only | rag-only |
| Decisions | 0 | 1 | 2 | 3 | 5 |
| Stories | 0 | 0 | 0 | 2 | 5 |
| Phase 0 | pending | in_progress | in_progress | in_progress | in_progress |
| Phase 1 | pending | pending | pending | in_progress | in_progress |
| Phase 2 | pending | pending | pending | pending | skipped |
| Phase 3 | pending | pending | pending | pending | pending |

---

## Critical Values for Routing

At Step 4, these values determine subsequent workflow:

1. **architecture = 'rag-only'**
   - Skip Step 5 (Fine-tuning)
   - Mark Phase 2 as skipped
   - Proceed directly to Step 6 (RAG Specialist)

2. **currentStep = 4, stepsCompleted = [1,2,3,4]**
   - Workflow can resume from this checkpoint
   - All prerequisites complete
   - Ready for Step 5 or 6

3. **decisions array has 5 entries**
   - All major architectural decisions made
   - Sufficient context for subsequent steps
   - Tech stack determined (Pinecone, OpenAI embeddings)

4. **stories array has 5 total**
   - Data pipeline tasks identified (2 stories)
   - Embedding infrastructure tasks identified (3 stories)
   - Ready for developer implementation

---

## Persistence Across Sessions

If workflow pauses after Step 4 and resumes later:

```yaml
# User: "Continue project 'Test-Knowledge-RAG-System'"
sidecar = load_sidecar('Test-Knowledge-RAG-System/sidecar.yaml')

# Everything is available:
print(sidecar['currentStep'])                 # 4
print(sidecar['architecture'])                # 'rag-only'
print(sidecar['stepsCompleted'])              # [1, 2, 3, 4]
print(len(sidecar['decisions']))              # 5
print(len(sidecar['stories']['step_3_data'])) # 2
print(len(sidecar['stories']['step_4_embeddings'])) # 3

# Can determine next step
if sidecar['architecture'] == 'rag-only':
    next_step = 6
else:
    next_step = 5

# Can display progress
print("Completed: %s" % sidecar['stepsCompleted'])
print("Architecture: %s" % sidecar['architecture'])
print("Ready to continue to Step %d" % next_step)
```

All context is preserved - workflow continues seamlessly.
