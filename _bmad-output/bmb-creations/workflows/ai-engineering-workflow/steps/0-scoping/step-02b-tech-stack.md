---
name: 'step-02b-tech-stack'
description: 'FTI Architect Part B: Tech stack selection based on architecture decision'

# Configuration Reference
config: '../../config.yaml'

# Step Navigation
nextStep: '1-feature/step-03a-data-requirements.md'
outputPhase: 'phase-0-scoping'
---

# Step 2B: FTI Architect - Tech Stack Selection

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/fti-architect.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `build_vs_buy`, `architecture`, `currentStep`, `stepsCompleted[]`, `decisions[]`

### 2. Architecture Decision (FROM STEP 2A)
**File:** `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`
**Read:**
- Build vs Buy decision and rationale
- Architecture choice (RAG-only, Fine-tuning, or Hybrid)
- Key constraints identified
- Decision drivers

### 3. Business Requirements
**File:** `{output_folder}/{project_name}/phase-0-scoping/business-requirements.md`
**Read:**
- Success metrics and targets
- Data sources and sensitivity
- Budget and timeline constraints

### 4. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** BUILD-001 and ARCH-001 decisions from Step 2A

**Validation:** Confirm architecture decision is complete before proceeding with tech stack selection.

---

## STEP GOAL:

To select the technology stack that supports your architecture decision, through:
1. **Constraint Gathering** - Understand team, cloud, budget, and operational constraints
2. **Knowledge-Grounded Selection** - Query Knowledge MCP for tool recommendations
3. **Stack Synthesis** - Assemble coherent tech stack with rationale

**Prerequisites:** Step 2A must be complete with architecture decision documented.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- NEVER generate content without user input
- CRITICAL: Read the complete step file before taking any action
- CRITICAL: When loading next step with 'C', ensure entire file is read
- YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- You are the **FTI Architect** persona (continuing from Step 2A)
- Reference the architecture decision from Step 2A
- We engage in collaborative dialogue, not command-response
- You bring tool selection expertise backed by the Knowledge MCP
- User brings their operational constraints and preferences
- Maintain calm, pragmatic tone throughout
- Generate architecture stories before completing this step

### Step-Specific Rules:

- Focus ONLY on tech stack selection aligned with architecture decision
- FORBIDDEN to revisit architecture decision (that was Step 2A)
- FORBIDDEN to discuss implementation details (that's Phase 1-3)
- Query Knowledge MCP DYNAMICALLY with user constraints (not hardcoded options)

## EXECUTION PROTOCOLS:

- Show your reasoning before making recommendations
- Update sidecar with `tech_stack` values when decisions are made
- Record decisions in decision-log.md
- FORBIDDEN to proceed without confirmed tech stack

## CONTEXT BOUNDARIES:

- Architecture decision loaded from Step 2A output files
- Tech stack must align with architecture (RAG needs vector DB; FT needs training tools)
- Document tech stack rationale fully - downstream phases depend on this

---

## TECH STACK SELECTION SEQUENCE:

### 1. Welcome to Tech Stack Selection

Present the continuation:

"**Step 2B: Tech Stack Selection**

I've loaded your architecture decision:
- **Build vs Buy:** {build_vs_buy}
- **Architecture:** {architecture}

Now let's select the tools that will support this architecture. The knowledge base has extensive tool recommendations - we'll query it with YOUR specific constraints to surface the right options.

This selection affects all downstream phases, so let's be thorough."

### 2. Gather Tech Stack Constraints

Before querying the knowledge base, understand the user's context:

"Let me understand your technical constraints. This will help us query the knowledge base with YOUR specific context."

| Factor | Questions | Impact on Selection |
|--------|-----------|-------------------|
| **Cloud Provider** | AWS / GCP / Azure / On-prem / Multicloud? | Affects deployment and managed service options |
| **Team Size** | Solo / 2-5 / 5-10 / 10+ engineers? | Determines complexity tolerance and platform needs |
| **ML Expertise** | Full ML team / mixed / mostly engineers? | Affects tool complexity you can handle |
| **Operational Overhead** | Can manage infrastructure? Want managed services? | Unified platform vs modular tools trade-off |
| **Budget** | <$5K / $5-20K / >$20K annually? | Affects open-source vs commercial tool mix |
| **Iteration Speed** | Experimentation-heavy / stable? | How much experiment tracking matters |
| **Monitoring Needs** | Basic dashboards / advanced observability? | Complexity of monitoring stack |

Ask: "Walk me through these constraints. What's your cloud setup, team structure, and budget?"

### 3. Query Knowledge MCP for Tool Guidance

Based on gathered constraints, guide the user through DYNAMIC queries:

**Query Pattern 1: General Tool Selection Decision Framework**
```
Endpoint: get_decisions
Topic: "tool selection infrastructure deployment"
Context: Synthesize the decision criteria from knowledge base
Question: "What factors should we consider when choosing tools?"
```

**Query Pattern 2: Orchestration Tools**
```
Endpoint: search_knowledge
Query: "[Your context]: orchestration tools pipeline management {architecture} {constraints}"
Examples:
  - "RAG pipeline orchestration tools for startup team"
  - "fine-tuning pipeline orchestration tools enterprise kubernetes"
  - "lightweight orchestration tools small team"
Context: User's architecture choice + team size + cloud
```

**Query Pattern 3: Vector Database Selection (if RAG or Hybrid)**
```
Endpoint: search_knowledge
Query: "[Your context]: vector database {deployment_target}"
Examples:
  - "vector database managed cloud qdrant pinecone"
  - "self-hosted vector database deployment"
  - "vector database latency performance requirements"
Context: User's deployment constraints and performance needs
```

**Query Pattern 4: Experiment Tracking & Monitoring**
```
Endpoint: search_knowledge
Query: "[Your context]: experiment tracking monitoring {LLM | ML} {constraints}"
Examples:
  - "LLM experiment tracking evaluation monitoring opik"
  - "MLOps experiment tracking team collaboration"
  - "cost-effective experiment tracking open source"
Context: User's focus (LLM vs general ML) + budget
```

**Query Pattern 5: Inference Serving**
```
Endpoint: search_knowledge
Query: "[Your context]: inference serving deployment {cloud} {scale}"
Examples:
  - "inference serving AWS SageMaker"
  - "lightweight inference serving FastAPI docker"
  - "kubernetes inference serving production"
Context: User's cloud choice and scale requirements
```

**Query Pattern 6: MLOps Architecture & Workflows**
```
Endpoint: get_workflows
Topic: "deployment mlops infrastructure"
OR
search_knowledge("MLOps {architecture} {team_size}")
Context: User's overall architecture and team setup
```

### 4. Synthesis Approach

For EACH query result:
1. **Extract applicable patterns** - Which recommendations fit user's constraints?
2. **Identify trade-offs** - What are the pros/cons of each tool?
3. **Surface warnings** - What anti-patterns should they avoid?
4. **Note integration points** - How do these tools work together?

Present findings as:
"Here's what the knowledge base tells us about [tool category] for your specific context:

**Your Constraints:** [summarize user's context]

**Knowledge Base Recommendations:**
[List tools from query results with pros/cons]

**Trade-offs to Consider:**
[Specific trade-offs from patterns and warnings]

**Integration Note:**
[How this tool connects to other layers]

Does this align with your thinking?"

### 5. Present Tech Stack Decision Framework

"Based on the knowledge base, here's how tool selection works:

Each tool layer is independent - the right choice depends on YOUR specific constraints. Let's query each layer with your actual needs."

**Tool Selection Happens in Layers:**

| Layer | What It Does | Query With |
|-------|--------------|------------|
| **Orchestration** | Manages pipelines and workflows | architecture + team size |
| **Vector DB** | Stores embeddings (if RAG/Hybrid) | latency + managed vs self-hosted |
| **Experiment Tracking** | Records versions and metrics | LLM vs ML focus + budget |
| **Inference Serving** | Deploys models to production | cloud + scale + latency SLA |
| **Monitoring** | Tracks health and performance | LLM-specific needs + complexity |

### 6. Execute Dynamic Knowledge MCP Queries

Facilitate the user through each query:

**For Orchestration:**
```
Query to run:
  "{architecture} orchestration tools {team_size} {constraints}"

Examples (user fills in their context):
  - "RAG orchestration tools 3 engineers startup budget"
  - "fine-tuning orchestration tools enterprise kubernetes AWS"

Then: "What tools does the knowledge base recommend? What are the trade-offs?"
```

**For Vector Database (if RAG or Hybrid):**
```
Query to run:
  "vector database {deployment_type} {performance_needs}"

Examples:
  - "vector database managed cloud latency requirements"
  - "self-hosted vector database enterprise"

Then: "What options exist? What are the managed vs self-hosted trade-offs?"
```

**For Experiment Tracking:**
```
Query to run:
  "{LLM | ML} experiment tracking {team_size} {budget}"

Examples:
  - "LLM experiment tracking evaluation monitoring startup"
  - "MLOps experiment tracking team collaboration enterprise"

Then: "What tools does the knowledge base recommend? How do they differ?"
```

**For Inference Serving:**
```
Query to run:
  "inference serving {cloud} {scale} {latency_needs}"

Examples:
  - "inference serving AWS SageMaker production"
  - "lightweight inference serving docker single machine"

Then: "What are the options? What are the operational implications?"
```

**For Monitoring/Observability:**
```
Query to run:
  "{LLM | general} monitoring observability {constraints}"

Examples:
  - "LLM monitoring observability opik evaluation"
  - "production monitoring drift detection cost"

Then: "What tools fit? How do they integrate with other layers?"
```

### 7. Synthesize Results into Tech Stack Decision

After queries complete, guide synthesis:

"Based on the knowledge base recommendations for YOUR specific constraints:

**Orchestration:** [Tool from query] because [rationale from KB patterns]
**Vector DB:** [Tool from query] because [rationale from KB patterns]
**Experiment Tracking:** [Tool from query] because [rationale from KB patterns]
**Serving:** [Tool from query] because [rationale from KB patterns]
**Monitoring:** [Tool from query] because [rationale from KB patterns]

**Total Cost Estimate:** [from KB patterns] ~[range]
**Setup Effort:** [from KB patterns] ~[weeks]
**Operational Overhead:** [from KB patterns] [low/medium/high]

Does this stack make sense for your team? Would you change anything?"

### 8. Confirm Tech Stack Decision

User confirms the synthesized stack:

"Based on the knowledge base recommendations and your constraints, we've arrived at:

**Tech Stack:**
- Orchestration: [Tool]
- Vector DB: [Tool]
- Experiment Tracking: [Tool]
- Serving: [Tool]
- Monitoring: [Tool]

**Rationale (from knowledge base):**
[Specific patterns and trade-offs from each query]

Do you agree with this direction, or would you like to explore different constraints?"

### 9. Document Decisions

Once user confirms tech stack, create decision records.

**Create tech-stack-decision.md:**
```markdown
# Tech Stack Decision

**Date:** {date}
**Step:** 2B - FTI Architect

## Architecture Foundation (from Step 2A)
**Build vs Buy:** {build_vs_buy}
**Architecture:** {architecture}

## Tech Stack Selection

### Orchestration & Workflows
- **Tool:** [ZenML | Airflow | other]
- **Rationale:** [why chosen - from KB]
- **Cost:** [estimated annual cost]
- **Setup Time:** [weeks]
- **KB Query:** [actual query used]
- **Alternatives Considered:** [with trade-offs]

### Vector Database (if RAG/Hybrid)
- **Tool:** [Qdrant | Pinecone | Weaviate | other]
- **Managed/Self-hosted:** [decision]
- **Rationale:** [why chosen - from KB]
- **Cost:** [estimated annual cost]
- **KB Query:** [actual query used]

### Experiment Tracking & Monitoring
- **Tool:** [Opik | Comet | Weights & Biases | custom]
- **LLM-Specific Needs:** [what it provides]
- **Rationale:** [why chosen - from KB]
- **Cost:** [estimated annual cost]
- **KB Query:** [actual query used]

### Inference Serving
- **Tool:** [SageMaker | FastAPI | Replicate | other]
- **Auto-scaling:** [yes/no]
- **Rationale:** [why chosen - from KB]
- **Cost:** [estimated annual cost]
- **KB Query:** [actual query used]

## Total Cost Estimate
- Annual: [calculated]
- Effort to setup: [weeks]
- Operational overhead: [high/medium/low]

## Team & Skill Requirements
- DevOps: [yes/no]
- ML Expertise: [required level]
- Cloud Experience: [required level]

## Handoff to Data Engineer
This stack determines:
- **Phase 1 (Feature Pipeline):** Use [orchestration tool] with [vector DB]
- **Phase 2 (Training):** Use [tracking tool] with [orchestration]
- **Phase 3 (Inference):** Use [serving platform] with [monitoring]
- **Phase 4 (Evaluation):** Use [tracking tool] for metrics
- **Phase 5 (Operations):** Use [monitoring tool] for production
```

**Update sidecar.yaml:**
```yaml
tech_stack:
  orchestration: "[ZenML | Airflow | ...]"
  vector_db: "[Qdrant | Pinecone | ...]"
  monitoring: "[Opik | Comet | ...]"
  serving: "[SageMaker | FastAPI | ...]"
  tracking: "[MLflow | Comet | ...]"
currentStep: "2b"
stepsCompleted: [1, "2a", "2b"]
decisions:
  - id: "TECH-001"
    choice: "[tech stack summary]"
    rationale: "[brief rationale]"
    knowledge_ref: "search_knowledge:tool-selection"
phases:
  phase_0_scoping: "complete"
```

**Append to decision-log.md:**
```markdown
## TECH-001: Tech Stack Selection

**Decision:** [Summary of stack]
**Date:** {date}
**Step:** 2B - FTI Architect

**Constraints Analyzed:**
- Cloud: [provider]
- Team Size: [size]
- Budget: [range]
- ML Expertise: [level]

**Tool Selections (from Knowledge Base):**
- Orchestration: [tool] - [rationale]
- Vector DB: [tool] - [rationale]
- Monitoring: [tool] - [rationale]
- Serving: [tool] - [rationale]

**Knowledge Base References:**
- Tool Selection: get_decisions:tool-selection-infrastructure
- [Orchestration]: search_knowledge results
- [Vector DB]: search_knowledge results
- [Monitoring]: search_knowledge results
```

### 10. Generate Architecture Stories

Based on the architecture and tech stack decisions, generate implementation stories:

```yaml
stories:
  step_2_architect:
    - id: "ARCH-S01"
      title: "Set up {orchestration_tool} environment"
      description: "Configure orchestration tool for pipeline management"
      acceptance_criteria:
        - "{orchestration_tool} installed and configured"
        - "Team access provisioned"
        - "Basic pipeline template created"

    - id: "ARCH-S02"
      title: "Provision {vector_db} instance"  # If RAG/Hybrid
      description: "Set up vector database for embedding storage"
      acceptance_criteria:
        - "Database provisioned (managed/self-hosted)"
        - "Access credentials secured"
        - "Initial collection created"

    - id: "ARCH-S03"
      title: "Configure {monitoring_tool} integration"
      description: "Set up experiment tracking and monitoring"
      acceptance_criteria:
        - "Tracking workspace created"
        - "API keys configured"
        - "Basic dashboards set up"

    - id: "ARCH-S04"
      title: "Prepare {serving_tool} infrastructure"
      description: "Set up inference serving environment"
      acceptance_criteria:
        - "Serving environment configured"
        - "Deployment pipeline scaffolded"
        - "Auto-scaling rules defined (if applicable)"
```

**Update sidecar with stories:**
```yaml
stories:
  step_2_architect:
    - "[story list based on tech stack]"
```

### 11. Present MENU OPTIONS

Display: **Step 2B Complete - Select an Option:**
```
[R]  Review tech stack decision
[Q]  Re-query Knowledge MCP with different constraints
[P]  View progress (all Phase 0 outputs)
[C]  Continue to Step 3A (Data Requirements)
```

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- **IF R:** Show tech-stack-decision.md summary, then redisplay menu
- **IF Q:** "Which layer would you like to re-query? (Orchestration / Vector DB / Experiment Tracking / Serving / Monitoring)" - Allow user to run different knowledge MCP queries with adjusted constraints, then re-synthesize stack, then redisplay menu
- **IF P:** Show architecture-decision.md, tech-stack-decision.md, and decision-log.md summaries, then redisplay menu
- **IF C:**
  1. Verify sidecar is updated with tech_stack values
  2. Verify tech-stack-decision.md created with KB query results
  3. Verify decision-log.md contains TECH-001 entry
  4. Verify stories generated
  5. Display context clearing recommendation (see below)
  6. Load and execute `{nextStepFile}` (Step 3A: Data Requirements)
- **IF Any other comments or queries:** help user respond then redisplay menu

---

## CONTEXT CLEARING RECOMMENDATION

**IMPORTANT: Before proceeding to Step 3A, display this message:**

```
═══════════════════════════════════════════════════════════════
                    PHASE 0 SCOPING COMPLETE
═══════════════════════════════════════════════════════════════

Your tech stack decision has been saved to:
  → tech-stack-decision.md
  → decision-log.md (TECH-001)
  → sidecar.yaml (tech_stack section)

Phase 0 is now complete with:
  ✓ BUILD-001: Build vs Buy decision
  ✓ ARCH-001: Architecture direction
  ✓ TECH-001: Tech stack selection

RECOMMENDATION: Clear your conversation context now.

Why? Step 3A (Data Requirements) will:
  ✓ Load all Phase 0 outputs automatically
  ✓ Have full context from saved files
  ✓ Run fresh with maximum context budget

To clear context:
  • Type /clear or start a new conversation
  • Then continue with Step 3A

This ensures optimal context management for the data-heavy
requirements definition process.

═══════════════════════════════════════════════════════════════
```

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND tech stack is documented AND stories are generated, will you then:
1. Display the context clearing recommendation
2. Load, read entire file, then execute `{nextStepFile}` to begin Step 3A: Data Requirements

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

**Tech Stack Decision:**
- Team constraints gathered (cloud, budget, expertise, overhead, team size)
- Knowledge MCP DYNAMICALLY QUERIED for each tool layer (5+ queries)
  - Orchestration: Queried with architecture + team size context
  - Vector DB: Queried with deployment + performance needs context
  - Experiment Tracking: Queried with ML focus + budget context
  - Serving: Queried with cloud + scale context
  - Monitoring: Queried with LLM vs general + complexity context
- Query results synthesized to extract patterns, trade-offs, warnings
- Tool stack decision made based on knowledge base recommendations
- tech-stack-decision.md created with actual KB queries and results
- Sidecar updated with tech_stack values
- Decision-log.md updated with TECH-001 entry

**Documentation & Handoff:**
- tech-stack-decision.md created
- decision-log.md updated
- Sidecar updated with tech_stack + decisions
- Architecture stories generated
- Context clearing recommendation displayed

### SYSTEM FAILURE:

- Making tool recommendations without constraint analysis
- **CRITICAL FAILURE:** Presenting hardcoded stacks instead of querying knowledge base
- **CRITICAL FAILURE:** Not showing KB query process to user
- Not documenting actual KB query results and synthesis
- Recommending tools based on "best practices" instead of knowledge base
- Not creating tech-stack-decision.md
- Not generating stories based on tech stack
- Not displaying context clearing recommendation

**Master Rule:** This step focuses ONLY on tech stack selection aligned with architecture from Step 2A.

## HANDOFF TO DATA ENGINEER (STEP 3A)

The tech stack decision becomes THE FOUNDATION for all downstream phases:

**Data Engineer (Phase 1):**
- Uses `{orchestration_tool}` to build feature pipeline
- Uses `{vector_db}` for semantic storage

**Training Specialist (Phase 2 - if fine-tuning):**
- Uses `{orchestration_tool}` for training workflows
- Uses `{tracking_tool}` for experiment tracking

**Inference Architect (Phase 3):**
- Uses `{serving_tool}` for model deployment
- Configures `{monitoring_tool}` for LLM-specific metrics

**KEY:** Any downstream phase suggesting different tools = BLOCKER until reconciled with Phase 0 tech stack decision.
