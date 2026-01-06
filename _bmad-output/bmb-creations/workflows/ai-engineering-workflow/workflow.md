---
name: AI Engineering Workflow
description: Guide AI/LLM engineering projects from business analysis through operations using the FTI pipeline pattern, with specialized agents at each phase
web_bundle: true
config: 'config.yaml'
version: '1.0.0'
---

# AI Engineering Workflow

**Goal:** Guide AI engineers through building production LLM systems using the Feature-Training-Inference (FTI) pipeline architecture, with specialized agents at each phase and knowledge-grounded decisions throughout.

**Our Partnership:** This workflow uses **11 specialized agents**, each an expert in their domain. As we progress through phases, you'll partner with each agent persona to make decisions grounded in industry best practices. You bring domain knowledge about your AI system; each agent brings specialized expertise. Together, we'll query the Knowledge MCP for guidance and generate implementation stories at each step. This is a collaborative journey, not a command-response process.

---

## WORKFLOW ARCHITECTURE

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file executed one at a time
- **Specialized Agents**: Each step has a dedicated persona with domain expertise
- **Story Generation**: Each phase outputs implementation stories for that domain
- **Just-In-Time Loading**: Only load the current step file - never load future steps until directed
- **Sequential Enforcement**: Complete each phase in order, no skipping or optimization
- **State Tracking**: Progress tracked in `sidecar.yaml` using `stepsCompleted` array
- **Knowledge-Grounded**: Every decision references the Knowledge MCP for best practices
- **Feedback Loops**: Tech Lead can send work back to specific phases when conflicts detected

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **EMBODY PERSONA**: Adopt the agent's persona, communication style, and principles
3. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
4. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
5. **QUERY KNOWLEDGE**: At designated points, query the Knowledge MCP for relevant decisions, patterns, warnings
6. **GENERATE STORIES**: Output implementation stories for the phase before completing
7. **SAVE STATE**: Update `sidecar.yaml` before loading next step
8. **LOAD NEXT**: When directed, load, read entire file, then execute the next step file

### Critical Rules (NO EXCEPTIONS)

- **NEVER** load multiple step files simultaneously
- **ALWAYS** read entire step file before execution
- **NEVER** skip steps or optimize the sequence
- **ALWAYS** update sidecar.yaml when completing a step
- **ALWAYS** follow the exact instructions in the step file
- **ALWAYS** halt at menus and wait for user input
- **ALWAYS** query Knowledge MCP at designated decision points
- **ALWAYS** generate stories before completing a phase

---

## AGENT ROSTER

| Step | Agent | Icon | Focus | Agent File |
|------|-------|------|-------|------------|
| 1 | **Business Analyst** | 📋 | Project init + Stakeholders, use cases, business metrics, success criteria | `agents/business-analyst.md` |
| 2 | **FTI Architect** | 🏗️ | RAG vs Fine-tuning decision, architecture design | `agents/fti-architect.md` |
| 3 | **Data Engineer** | 🔧 | Data sources, ingestion, cleaning, quality | `agents/data-engineer.md` |
| 4 | **Embeddings Engineer** | 🧬 | Chunking strategy, embedding model, vector DB | `agents/embeddings-engineer.md` |
| 5 | **Fine-Tuning Specialist** | 🎯 | SFT/DPO config, dataset prep (CONDITIONAL) | `agents/fine-tuning-specialist.md` |
| 6 | **RAG Specialist** | 🔍 | RAG pipeline, retrieval, reranking, context | `agents/rag-specialist.md` |
| 7 | **Prompt Engineer** | 📝 | System prompts, templates, few-shot examples | `agents/prompt-engineer.md` |
| 8 | **LLM Evaluator** | 📊 | Eval framework, metrics, benchmarks | `agents/llm-evaluator.md` |
| 9 | **MLOps Engineer** | 🔄 | Monitoring, drift detection, alerting | `agents/mlops-engineer.md` |
| 10 | **Tech Lead** | 👨‍💼 | Review all, validate, sequence stories, GO/REVISE | `agents/tech-lead.md` |
| 11 | **Story Elaborator** | - | Transform stories to BMM format, add tasks/dev notes | (embedded) |

### Agents Folder Structure

Agent personas are stored in the `agents/` folder, separate from step workflow logic:

```
agents/
├── business-analyst.md      # Requirements elicitation specialist
├── fti-architect.md         # FTI pipeline architect
├── data-engineer.md         # Data pipeline specialist
├── embeddings-engineer.md   # Vector embeddings specialist
├── fine-tuning-specialist.md # Model customization expert
├── rag-specialist.md        # RAG pipeline specialist
├── prompt-engineer.md       # Prompt design specialist
├── llm-evaluator.md         # Evaluation specialist
├── mlops-engineer.md        # Production ML specialist
└── tech-lead.md             # Technical leadership
```

**Why Separate Files:**
- Agents are reusable across workflows
- Personas can be updated without modifying step logic
- Follows BMAD best practices for agent architecture
- Each agent contains: persona, expertise, principles, activation instructions, outputs, handoff context

**How Agents are Loaded:**
Each step file contains an "Agent Activation" section that references its agent file:
```markdown
## Agent Activation
Load and fully embody the agent persona from `{workflow_path}/agents/[agent-name].md` before proceeding.
```

### Configuration File

All workflow settings are centralized in `config.yaml` at the workflow root:

```
ai-engineering-workflow/
├── config.yaml              # Central configuration
├── workflow.md              # This file
├── agents/                  # Agent personas
├── steps/                   # Step workflow files
├── templates/               # Config templates
└── checklists/              # Quality checklists
```

**config.yaml Contains:**
- **Paths**: `workflow_root`, `output_folder`, relative folder locations
- **Knowledge MCP**: Endpoint URL and available tools
- **Architecture Options**: `rag-only`, `fine-tuning`, `hybrid`
- **Phase Structure**: Folder names and which steps belong to each phase
- **Agent Roster**: Maps step numbers to agent files
- **Step Sequence**: Defines step files, agents, and phases
- **Sidecar Template**: Initial structure for project sidecar.yaml
- **Story Prefixes**: ID prefixes for each step's stories (ARCH, DATA, EMB, etc.)
- **BMM Integration**: Dev agent and workflow for handoff

**Step Files Reference Config:**
Each step file's frontmatter includes a `config` reference:
```yaml
---
name: 'step-02-fti-architect'
description: 'FTI Architect: RAG vs Fine-tuning decision'
config: '../../config.yaml'
nextStep: '1-feature/step-03-data-engineer.md'
outputPhase: 'phase-0-scoping'
---
```

**Benefits:**
- Single source of truth for paths and settings
- Easy to relocate or customize the workflow
- Step files are cleaner and more maintainable
- Changes propagate consistently across all steps

---

## WORKFLOW STRUCTURE

```
Step 1: BUSINESS ANALYST ──────────────────────────────────────────────────────
    │   INIT: Project setup, sidecar creation (if not exists)
    │   WHY: Stakeholders, use cases, business metrics, success criteria
    │   OUTPUT: Business requirements document
    │
    ▼
Step 2: FTI ARCHITECT ─────────────────────────────────────────────────────────
    │   HOW: RAG vs Fine-tuning decision, architecture design
    │   OUTPUT: Architecture decision, technical design + stories
    │
    ▼
Step 3: DATA ENGINEER ─────────────────────────────────────────────────────────
    │   Data sources, ingestion pipelines, cleaning, quality checks
    │   OUTPUT: Data pipeline spec + stories
    │
    ▼
Step 4: EMBEDDINGS ENGINEER ───────────────────────────────────────────────────
    │   Chunking strategy, embedding model selection, vector DB config
    │   OUTPUT: Embedding pipeline spec + stories
    │
    ├── IF RAG-only ──────────────────────────────────────┐
    ▼                                                      │
Step 5: FINE-TUNING SPECIALIST (CONDITIONAL) ──────────────│───────────────────
    │   SFT/DPO configuration, dataset preparation        │
    │   [SKIPPED if RAG-only]                             │
    │   OUTPUT: Training config + stories                  │
    ▼◄────────────────────────────────────────────────────┘
Step 6: RAG SPECIALIST ────────────────────────────────────────────────────────
    │   RAG pipeline design, retrieval optimization, reranking
    │   OUTPUT: RAG pipeline spec + stories
    │
    ▼
Step 7: PROMPT ENGINEER ───────────────────────────────────────────────────────
    │   System prompts, user templates, few-shot examples, chain-of-thought
    │   OUTPUT: Prompt templates + stories
    │
    ▼
Step 8: LLM EVALUATOR ─────────────────────────────────────────────────────────
    │   Evaluation framework, metrics, benchmarks, test sets
    │   OUTPUT: Eval framework spec + stories
    │
    ▼
Step 9: MLOps ENGINEER ────────────────────────────────────────────────────────
    │   Monitoring, drift detection, alerting, runbook
    │   OUTPUT: Operations spec + stories
    │
    ▼
Step 10: TECH LEAD ────────────────────────────────────────────────────────────
    │   Review all outputs, validate consistency, sequence stories
    │
    ├── REVISE ──────► Return to specific step with feedback
    │                       │
    │                       └──► Back to Step 10 after revision
    │
    └── GO ──────────►
                      │
                      ▼
Step 11: STORY ELABORATOR ────────────────────────────────────────────────────
    │   Transform simplified stories → BMM-compliant story files
    │   Add tasks/subtasks, dev notes, architecture context
    │   OUTPUT: Full story files ready for BMM dev agent
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│   HANDOFF TO BMM DEV AGENT (/bmad:bmm:agents:dev)                          │
│   Execute stories via *dev-story workflow                                   │
│   Built-in code review via *code-review                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## KNOWLEDGE MCP INTEGRATION

This workflow queries the Knowledge MCP at key decision points:

| Endpoint | When to Use | Agents |
|----------|-------------|--------|
| `get_decisions` | Architecture choices, trade-offs | FTI Architect, RAG Specialist |
| `get_patterns` | Implementation patterns | Data Engineer, Embeddings, RAG, Prompt |
| `get_warnings` | Anti-patterns to avoid | All agents |
| `get_methodologies` | Step-by-step processes | Fine-Tuning, Evaluator, MLOps |
| `search_knowledge` | General queries | Any agent |

**MCP Endpoint:** `https://knowledge-mcp-production.up.railway.app`

---

## STORY ACCUMULATION

Each agent (Steps 2-9) generates implementation stories for their domain. Stories accumulate in the sidecar:

```yaml
stories:
  step_2_architect: []      # Architecture setup stories
  step_3_data: []           # Data pipeline stories
  step_4_embeddings: []     # Embedding pipeline stories
  step_5_training: []       # Training stories (if applicable)
  step_6_rag: []            # RAG pipeline stories
  step_7_prompts: []        # Prompt engineering stories
  step_8_evaluation: []     # Evaluation framework stories
  step_9_operations: []     # Operations stories
```

The Tech Lead (Step 10) reviews all stories, validates consistency, identifies gaps, and sequences them into a final implementation backlog.

---

## BMM INTEGRATION

After Tech Lead approval (GO), the Story Elaborator (Step 11) transforms accumulated stories into BMM-compliant format:

### Input (Simplified Story from Sidecar)
```yaml
- id: "DATA-S01"
  title: "Set up data ingestion pipeline"
  description: "Create pipeline to ingest documents from configured sources"
  acceptance_criteria:
    - "Pipeline connects to all data sources"
    - "Documents are parsed and cleaned"
```

### Output (BMM Story File)
```markdown
# Story 3.1: Set up data ingestion pipeline

Status: ready-for-dev

## Story
As a Data Engineer,
I want to set up a data ingestion pipeline,
so that documents from configured sources are available for processing.

## Acceptance Criteria
1. Pipeline connects to all data sources
2. Documents are parsed and cleaned

## Tasks / Subtasks
- [ ] Task 1: Configure data source connections (AC: #1)
  - [ ] Subtask 1.1: Set up MongoDB connection
  - [ ] Subtask 1.2: Configure file system adapters
- [ ] Task 2: Implement document parsing (AC: #2)
  - [ ] Subtask 2.1: Add PDF parser
  - [ ] Subtask 2.2: Add Markdown parser

## Dev Notes
- Architecture: FTI pipeline pattern (see architecture-decision.md)
- Patterns: Use async processing for large documents
- References: [Source: phase-1-feature/spec.md]

## Dev Agent Record
### Agent Model Used
### Debug Log References
### Completion Notes List
### File List
```

### Handoff to BMM Dev Agent

Once stories are elaborated, invoke:
```
/bmad:bmm:agents:dev
→ Select *dev-story
→ Stories auto-discovered from sprint artifacts
```

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Resolve workflow variables:
- `project_name` - Name of the AI project being built
- `output_folder` - Where project outputs will be stored (default: `{project-root}/_bmad-output/ai-projects`)
- `user_name` - Engineer's name for personalization
- `date` - Current date for timestamps

### 2. Project Initialization (Idempotent)

**This logic runs from both workflow.md AND business-analyst.md activation - safe to run multiple times.**

#### A. Get Project Name
Ask the user: "What is your project name?" (e.g., 'customer-support-bot', 'document-qa-system')
Store as `{project_name}`.

#### B. Check for Existing Project
Check if `{output_folder}/{project_name}/sidecar.yaml` exists.

#### C. If Project Does NOT Exist - Create Structure
Create the following folder structure:
```
{output_folder}/{project_name}/
├── sidecar.yaml
├── project-spec.md
├── decision-log.md
├── phase-0-scoping/
├── phase-1-feature/
├── phase-2-training/
├── phase-3-inference/
├── phase-4-evaluation/
└── phase-5-operations/
```

Initialize `sidecar.yaml`:
```yaml
project_name: "{project_name}"
created: "{date}"
user_name: "{user_name}"
architecture: null  # Set in Step 2: "rag-only" | "fine-tuning" | "hybrid"
currentStep: 1
stepsCompleted: []
decisions: []
phases:
  phase_0_scoping: "pending"
  phase_1_feature: "pending"
  phase_2_training: "pending"
  phase_3_inference: "pending"
  phase_4_evaluation: "pending"
  phase_5_operations: "pending"
```

Display: "Project '{project_name}' initialized! Starting with Business Analyst..."

#### D. If Project EXISTS - Offer Continue/Review
Read `sidecar.yaml` to get current state.

Display:
"**Welcome back to '{project_name}'!**

**Progress:** Steps completed: {stepsCompleted}
**Architecture:** {architecture or 'Not yet decided'}
**Last step:** {last completed step name}

Would you like to:
1. **Continue** where you left off
2. **Review** progress so far
3. **Start fresh** (creates new project with different name)"

Handle user choice accordingly.

### 3. First Step Execution

Load, read the full file, and then execute `{workflow_path}/steps/0-scoping/step-01-business-analyst.md` to begin the workflow.
