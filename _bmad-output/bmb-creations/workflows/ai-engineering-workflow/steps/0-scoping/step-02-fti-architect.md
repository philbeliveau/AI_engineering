---
name: 'step-02-fti-architect'
description: 'FTI Architect: Determine architecture direction through RAG vs Fine-tuning decision'

# Configuration Reference
# All paths and settings are defined in config.yaml at workflow root
config: '../../config.yaml'

# Step Navigation (resolved from config)
nextStep: '1-feature/step-03-data-engineer.md'
outputPhase: 'phase-0-scoping'
---

# Step 2: FTI Architect

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/fti-architect.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `currentStep`, `stepsCompleted[]`

### 2. Previous Step Output
**File:** `{output_folder}/{project_name}/phase-0-scoping/business-requirements.md`
**Read:**
- Stakeholder map and their needs
- Use cases with priorities
- Success metrics and targets
- Data sources and sensitivity
- Constraints and risks

### 3. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** Any previous decisions (may be empty if this is step 2)

**Validation:** Confirm business requirements are complete before proceeding with architecture decision.

---

## STEP GOAL:

To determine the foundational architecture direction (RAG-only, Fine-tuning, or Hybrid) through collaborative analysis of use case requirements, constraints, and knowledge-grounded decision criteria.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- ✅ You are the **FTI Architect** persona
- ✅ Reference the business requirements from Step 1 (Business Analyst)
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring FTI pipeline expertise backed by the Knowledge MCP
- ✅ User brings their domain requirements and constraints
- ✅ Maintain calm, pragmatic tone throughout
- ✅ Generate architecture stories before completing this step

### Step-Specific Rules:

- 🎯 Focus on TWO decisions: (1) RAG vs Fine-tuning, (2) Tech Stack selection
- 🚫 FORBIDDEN to discuss implementation details (that's Phase 1-3)
- 💬 These are FOUNDATIONAL decisions - take time to get both right
- 🧠 Query Knowledge MCP for BOTH architecture criteria AND tool selection guidance
- 🔗 Tech stack must align with architecture (e.g., RAG needs vector DB; FT needs training tools)
- 📋 Document tech stack rationale fully - downstream phases depend on this

## EXECUTION PROTOCOLS:

- 🎯 Show your reasoning before making recommendations
- 💾 Update sidecar with `architecture` value when decision is made
- 📖 Record the decision in both decision-log.md and architecture-decision.md
- 🚫 FORBIDDEN to proceed to Phase 1 without clear architecture decision

## CONTEXT BOUNDARIES:

- Previous context loaded via LOAD CONTEXT section above
- Reference stakeholders, use cases, success metrics, constraints from BA output
- Architecture decision determines entire workflow path
- RAG-only skips Step 5 (Fine-Tuning Specialist)

## SCOPING SEQUENCE:

### 1. Welcome to Phase 0

Present the phase introduction:

"**Phase 0: Scoping - The Most Critical Decisions**

Before we build anything, we need to answer foundational questions that determine everything else:

1. **Build vs Buy:** Should we build a custom LLM, or buy API access to an existing one?
2. **Architecture:** If building/customizing, should we use RAG, Fine-tuning, or Hybrid?
3. **Tech Stack:** What tools do we need for our chosen path?

These decisions impact:
- Development complexity and timeline
- Infrastructure requirements and cost
- Data requirements and privacy considerations
- Performance characteristics and latency
- Maintenance and update patterns

Let's work through this systematically."

### 2. Build vs Buy Decision (LLM Foundation)

**First, determine your LLM strategy:** Are you building a custom/fine-tuned LLM, or buying API access?

Present the framework from "LLMs in Production" (Figure 1.1 - Build vs Buy Decision Tree):

**Three Questions to Ask Yourself:**

```
Q1: Is the LLM going to be critical to your business?
    ↓ YES → Continue to Q2
    ↓ NO  → Go to Buy Decision

Q2: Are you sure? (Validate your answer to Q1)
    ↓ YES → Continue to Q3
    ↓ NO  → Reconsider Q1

Q3: Does your application require strict privacy or security?
    ↓ YES → BUILDING (You need a custom/fine-tuned LLM)
    ↓ NO  → Continue to Build vs Buy trade-off analysis
```

**Decision Outcomes:**

| Outcome | Path | Rationale |
|---------|------|-----------|
| **BUYING** | Use API access (OpenAI, Claude, etc.) | Start by buying/using API access to test concept quickly, fail fast |
| **BUILDING** | Fine-tune or build custom LLM | Critical business need + privacy/security requirements force custom approach |

**Knowledge Base Reference:**
- Source: "LLMs in Production" (Brousseau & Sharp, 2024)
- Decision ID: `695c75fdb2a07918411aca4e`
- Key insight: Start with buying to test concept. Build only if business criticality + privacy/security demands it.

Ask user: "Let's walk through these three questions. Is the LLM critical to your business?"

### 3. Query Knowledge MCP for Architecture Decision (if Building)

If user answered "BUILDING" (needs custom/fine-tuned LLM), proceed to architecture decision.

**MANDATORY QUERIES** - Execute to understand RAG vs Fine-tuning options:

**Query 1: Architecture Decision**
```
Endpoint: get_decisions
Topic: "RAG vs fine-tuning"
```

**Query 2: RAG Patterns**
```
Endpoint: search_knowledge
Query: "RAG retrieval augmented generation when to use"
```

**Query 3: Fine-tuning Considerations**
```
Endpoint: search_knowledge
Query: "fine-tuning LLM when necessary instruction dataset"
```

**Query 4: Common Mistakes**
```
Endpoint: get_warnings
Topic: "fine-tuning"
```

**Synthesis Approach:**
1. Extract **decision criteria** from the knowledge base
2. Identify **use case patterns** that favor each approach
3. Surface **data requirements** for each path
4. Note **common mistakes** to avoid

Present synthesized decision framework:
"Here's what the knowledge base tells us about choosing your architecture..."

**Key Warning to Surface:**
> Creating instruction datasets is the most difficult part of fine-tuning. Natural instruction-answer pairs are rare in raw text. If you don't have high-quality training data, RAG may be the safer path.

**Key Pattern to Surface:**
> RAG combines an LLM with a retrieval mechanism to fetch relevant data from external sources. This prevents hallucinations and provides source attribution - critical for many enterprise use cases.

### 4. Build Path: Gather Use Case Requirements (if BUILDING)

**Only proceed if user chose: BUILDING a custom/fine-tuned LLM**

If user chose: BUYING (API access), skip to Step 9 (Document Buy Decision).

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

### 5. Buy Path: API Provider Selection (if BUYING)

**Only for users who chose: BUYING API access (not building custom)**

"Great! You've decided to buy API access rather than build a custom LLM. Now let's choose the right provider for your needs."

**Query Knowledge MCP:**
```
Endpoint: search_knowledge
Query: "LLM API providers OpenAI Claude Anthropic [your_use_case] [your_constraints]"
```

**Provider Considerations:**

| Provider | Strengths | Best For |
|----------|-----------|----------|
| **Claude (Anthropic)** | Best for complex reasoning, long context | Enterprise, reasoning-heavy tasks |
| **OpenAI GPT-4** | Broad capability, most widely used | General purpose, wide ecosystem |
| **Open Source (Llama)** | Full control, privacy | On-prem, air-gapped environments |

**Document Provider Choice:**

Create `api-provider-decision.md`:
```yaml
path: "buy"
provider: "[OpenAI | Anthropic Claude | Other]"
rationale: "[why this provider for your use case]"
cost_model: "[pay-per-token | subscription | other]"
privacy_considerations: "[data handling, retention]"
```

**Then proceed to: Section 9 (Tech Stack & Documentation)**

### 6. Build Path: Make the Architecture Decision (if BUILDING)

**Only for users who chose: BUILDING a custom/fine-tuned LLM**

Guide to decision:

"Based on our discussion:

**Your Use Case:** [summarize]
**Your Data:** [summarize]
**Your Constraints:** [summarize]

**My Recommendation:** [RAG-only | Fine-tuning | Hybrid]

**Rationale:** [explain why this fits their situation]

Do you agree with this direction, or would you like to discuss further?"

### 7. Gather Tech Stack Constraints

Before querying the knowledge base, understand the user's context (applies to both BUILD and BUY paths):

"Now let's understand your technical constraints for choosing tools. The knowledge base has many tool recommendations - we'll query it with YOUR specific context to surface the right options."

| Factor | Questions | Impact on Selection |
|--------|-----------|-------------------|
| **Cloud Provider** | AWS / GCP / Azure / On-prem / Multicloud? | Affects deployment and managed service options |
| **Team Size** | Solo / 2-5 / 5-10 / 10+ engineers? | Determines complexity tolerance and platform needs |
| **ML Expertise** | Full ML team / mixed / mostly engineers? | Affects tool complexity you can handle |
| **Operational Overhead** | Can manage infrastructure? Want managed services? | Unified platform vs modular tools trade-off |
| **Budget** | <$5K / $5-20K / >$20K annually? | Affects open-source vs commercial tool mix |
| **Iteration Speed** | Experimentation-heavy / stable? | How much experiment tracking matters |
| **Monitoring Needs** | Basic dashboards / advanced observability? | Complexity of monitoring and observability stack |

Ask: "Walk me through these constraints. What's your cloud setup, team structure, and budget?"

### 8. Query Knowledge MCP for Tool Guidance

Based on gathered constraints, guide the user through DYNAMIC queries (applies to both BUILD and BUY paths):

**Query Pattern 1: General Tool Selection Decision Framework**
```
Endpoint: get_decisions
Topic: "tool selection infrastructure deployment"
Context: Synthesize the decision criteria from knowledge base
Question: "What factors should we consider when choosing [orchestration tools | vector databases | experiment tracking | serving platforms]?"
```

**Query Pattern 2: Orchestration Tools**
```
Endpoint: search_knowledge
Query: "[Your context]: orchestration tools pipeline management [your_architecture] [your_constraints]"
Examples:
  - "RAG pipeline orchestration tools for startup team"
  - "fine-tuning pipeline orchestration tools enterprise kubernetes"
  - "lightweight orchestration tools small team"
Context: User's architecture choice + team size + cloud
```

**Query Pattern 3: Vector Database Selection (if RAG)**
```
Endpoint: search_knowledge
Query: "[Your context]: vector database [your_deployment_target]"
Examples:
  - "vector database managed cloud qdrant pinecone"
  - "self-hosted vector database deployment"
  - "vector database latency performance requirements"
Context: User's deployment constraints and performance needs
```

**Query Pattern 4: Experiment Tracking & Monitoring**
```
Endpoint: search_knowledge
Query: "[Your context]: experiment tracking monitoring [LLM | ML] [your_constraints]"
Examples:
  - "LLM experiment tracking evaluation monitoring opik"
  - "MLOps experiment tracking team collaboration"
  - "cost-effective experiment tracking open source"
Context: User's focus (LLM vs general ML) + budget
```

**Query Pattern 5: Inference Serving**
```
Endpoint: search_knowledge
Query: "[Your context]: inference serving deployment [your_cloud] [your_scale]"
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
search_knowledge("MLOps [your_architecture] [your_team_size]")
Context: User's overall architecture and team setup
```

### 9. Synthesis Approach

For EACH query result (applies to both BUILD and BUY paths):
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

### 10. Present Tech Stack Decision Framework

"Based on the knowledge base, here's how tool selection works (applies to both BUILD and BUY paths):

Each tool layer is independent - the right choice depends on YOUR specific constraints. Rather than prescribing one stack, let's let the knowledge base guide us based on your actual needs."

**Tool Selection Happens in Layers:**

| Layer | What It Does | Typical Candidates |
|-------|--------------|-------------------|
| **Orchestration** | Manages data pipelines, training workflows, inference pipelines | Query knowledge base with your architecture + team size |
| **Vector DB** | Stores and retrieves embeddings (if RAG) | Query based on: latency needs, managed vs self-hosted, budget |
| **Experiment Tracking** | Records model versions, metrics, comparisons | Query based on: LLM vs general ML focus, team size, integration needs |
| **Inference Serving** | Deploys models to production | Query based on: cloud choice, scale requirements, latency SLA |
| **Monitoring & Observability** | Tracks system health, drift, performance | Query based on: LLM-specific vs general needs, complexity tolerance |

Ask: "For each layer, we'll query the knowledge base with YOUR constraints. This ensures recommendations fit your specific situation, not a template."

### 11. Execute Dynamic Knowledge MCP Queries

Facilitate the user through each query (applies to both BUILD and BUY paths):

**For Orchestration:**
```
Query to run:
  "[Your_architecture] orchestration tools [your_team_size] [your_constraints]"

Examples (user fills in their context):
  - "RAG orchestration tools 3 engineers startup budget"
  - "fine-tuning orchestration tools enterprise kubernetes AWS"
  - "distributed pipeline orchestration open source"

Then: "What tools does the knowledge base recommend? What are the trade-offs?"
```

**For Vector Database (if RAG):**
```
Query to run:
  "vector database [your_deployment_type] [your_performance_needs]"

Examples:
  - "vector database managed cloud latency requirements"
  - "self-hosted vector database enterprise"
  - "cost-effective vector database single machine"

Then: "What options exist? What are the managed vs self-hosted trade-offs?"
```

**For Experiment Tracking:**
```
Query to run:
  "[LLM | ML] experiment tracking [your_team_size] [your_budget]"

Examples:
  - "LLM experiment tracking evaluation monitoring startup"
  - "MLOps experiment tracking team collaboration enterprise"
  - "open source experiment tracking cost effective"

Then: "What tools does the knowledge base recommend? How do they differ?"
```

**For Inference Serving:**
```
Query to run:
  "inference serving [your_cloud] [your_scale] [your_latency_needs]"

Examples:
  - "inference serving AWS SageMaker production"
  - "lightweight inference serving docker single machine"
  - "kubernetes inference serving auto-scaling"

Then: "What are the options? What are the operational implications?"
```

**For Monitoring/Observability:**
```
Query to run:
  "[LLM | general] monitoring observability [your_constraints]"

Examples:
  - "LLM monitoring observability opik evaluation"
  - "production monitoring drift detection cost"
  - "lightweight monitoring prometheus grafana"

Then: "What tools fit? How do they integrate with orchestration and serving?"
```

### 12. Synthesize Results into Tech Stack Decision

After queries complete, guide synthesis (applies to both BUILD and BUY paths):

"Based on the knowledge base recommendations for YOUR specific constraints:

**Orchestration:** [Tool from query] because [rationale from KB patterns]
**Vector DB:** [Tool from query] because [rationale from KB patterns]
**Experiment Tracking:** [Tool from query] because [rationale from KB patterns]
**Serving:** [Tool from query] because [rationale from KB patterns]
**Monitoring:** [Tool from query] because [rationale from KB patterns]

**Total Cost Estimate:** [from KB patterns] ~[range]
**Setup Effort:** [from KB patterns] ~[weeks]
**Operational Overhead:** [from KB patterns] [low/medium/high]

Does this stack make sense for your team? Would you change anything based on constraints we missed?"

### 13. Confirm Tech Stack Decision

User confirms the synthesized stack from knowledge base queries (applies to both BUILD and BUY paths):

"Based on the knowledge base recommendations and your constraints, we've arrived at:

**Tech Stack:**
- Orchestration: [Tool from KB query]
- Vector DB: [Tool from KB query]
- Experiment Tracking: [Tool from KB query]
- Serving: [Tool from KB query]
- Monitoring: [Tool from KB query]

**Rationale (from knowledge base):**
[Specific patterns and trade-offs from each query]

Do you agree with this direction, or would you like to explore different constraints?"

### 14. Document All Decisions

Once user confirms decisions (BUILD vs BUY, architecture if building, and tech stack), create decision records.

**Use Template:** Load `{workflow_path}/templates/architecture-decision.template.md`
Fill in all `{{VARIABLE}}` placeholders with project-specific values from the discussion.
Save output to `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`

The template includes:
- Decision summary with confidence and reversibility assessment
- Context (problem statement, current state, goals)
- Decision drivers and constraints
- Knowledge MCP query results and synthesis
- Options considered with pros/cons
- Decision matrix with weighted scoring
- Phase implications (Phase 1-4)
- Trade-offs acknowledged and risk assessment
- Anti-patterns to avoid from knowledge base
- **Implementation stories section** (see Section 9 of template)

**Create tech-stack-decision.md:**
```markdown
# Tech Stack Decision

**Date:** {date}
**Step:** 2 - FTI Architect

## Architecture Direction
**Choice:** [RAG-only | Fine-tuning | Hybrid]

## Tech Stack Selection
**Option Chosen:** [Option A | Option B | Option C]

### Orchestration & Workflows
- **Tool:** [ZenML | Airflow | other]
- **Rationale:** [why chosen]
- **Cost:** [estimated annual cost]
- **Setup Time:** [weeks]
- **Alternatives Considered:** [with trade-offs]

### Vector Database
- **Tool:** [Qdrant | Pinecone | Weaviate | other]
- **Rationale:** [why chosen]
- **Managed/Self-hosted:** [decision]
- **Cost:** [estimated annual cost]

### Experiment Tracking & Monitoring
- **Tool:** [Opik | Comet | Weights & Biases | custom]
- **Rationale:** [why chosen]
- **LLM-Specific Needs:** [what Opik provides vs alternatives]
- **Cost:** [estimated annual cost]

### Inference Serving
- **Tool:** [SageMaker | FastAPI | Replicate | other]
- **Rationale:** [why chosen]
- **Auto-scaling:** [yes/no]
- **Cost:** [estimated annual cost]

### Experiment Tracking (for model training)
- **Tool:** [MLflow | Comet | Weights & Biases]
- **Rationale:** [why chosen]
- **Integration with orchestration:** [how it connects]

## Total Cost Estimate
- Annual: [calculated]
- Effort to setup: [weeks]
- Operational overhead: [high/medium/low]

## Knowledge Base References
- Decision Framework: get_decisions:tool-selection
- Orchestration Patterns: search_knowledge results
- Tool Recommendations: LLM Handbook extractions

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
build_vs_buy: "[build | buy]"
api_provider: "[OpenAI | Claude | other | N/A]"  # Only if buying
architecture: "[rag-only | fine-tuning | hybrid | N/A]"  # Only if building
tech_stack:
  orchestration: "[ZenML | Airflow | ...]"
  vector_db: "[Qdrant | Pinecone | ...]"
  monitoring: "[Opik | Comet | ...]"
  serving: "[SageMaker | FastAPI | ...]"
  tracking: "[MLflow | Comet | ...]"
currentPhase: 1
stepsCompleted: [1, 2]
decisions:
  - id: "build-001"
    choice: "[build | buy]"
    rationale: "[brief rationale based on three questions]"
    knowledge_ref: "LLMs in Production, Figure 1.1"
  - id: "arch-001"
    choice: "[rag-only | fine-tuning | hybrid]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_decisions:rag-vs-fine-tuning"
    conditional: "only_if_building"
  - id: "tech-001"
    choice: "[tech stack option]"
    rationale: "[brief rationale]"
    knowledge_ref: "search_knowledge:tool-selection"
phases:
  phase_0_scoping: "complete"
```

**Append to decision-log.md:**
```markdown
## BUILD-001: Build vs Buy LLM Decision

**Decision:** [Build | Buy]
**Date:** {date}
**Step:** 2 - FTI Architect

**Three-Question Framework (from LLMs in Production, Figure 1.1):**
- Q1: Is the LLM going to be critical to your business? [YES | NO]
- Q2: Are you sure? [YES | NO - Validated]
- Q3: Does your application require strict privacy or security? [YES | NO]

**Rationale:**
- Q1 Answer: [explanation]
- Q2 Answer: [confidence assessment]
- Q3 Answer: [privacy/security requirements]
- **Final Decision:** [Build if answered YES to criticality + privacy, else Buy]

**Knowledge Base Reference:**
- Source: "LLMs in Production" (Brousseau & Sharp, 2024), Figure 1.1, Page 14
- Decision ID: `695c75fdb2a07918411aca4e`
- Key Insight: Start by buying API access to test concept quickly. Build only if critical + privacy/security requirements demand it.

**If BUYING:**
- API Provider: [Selected provider from Section 5]
- Cost Model: [pay-per-token | subscription]

**If BUILDING:**
- Architecture Path: See ARCH-001 below

---

## ARCH-001: Architecture Direction (Only if BUILDING)

**Decision:** [RAG-only | Fine-tuning | Hybrid]
**Date:** {date}
**Step:** 2 - FTI Architect

**Rationale:** [from architecture discussion]

---

## TECH-001: Tech Stack Selection

**Decision:** [Option A | Option B | Option C]
**Date:** {date}
**Step:** 2 - FTI Architect

**Rationale:**
- Orchestration: [why chosen]
- Monitoring: [why chosen]
- Serving: [why chosen]
- Cost Considerations: [budget alignment]

**Knowledge Base References:**
- Tool Selection: get_decisions:tool-selection-infrastructure
- ZenML vs Airflow: search_knowledge results
- LLM Monitoring (Opik): search_knowledge results
- Deployment Patterns: get_workflows:deployment-mlops
```

**Update project-spec.md:**
```markdown
## Project Overview

**Use Case:** [Description from discussion]
**Architecture:** [RAG-only | Fine-tuning | Hybrid]
**Tech Stack:** [Option A | Option B | Option C]

### Technology Choices
**Orchestration:** [Tool] - [brief rationale]
**Vector Database:** [Tool] - [brief rationale]
**Monitoring:** [Tool] - [brief rationale]
**Serving:** [Tool] - [brief rationale]

**Key Requirements:**
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

**Constraints:**
- [Constraint 1]
- [Constraint 2]

---
```

### 7. Generate Architecture Stories

The architecture-decision template (Section 9) contains predefined stories for each architecture type. When completing the template:

1. **Select the appropriate story set** based on the chosen architecture (RAG-only vs Fine-tuning/Hybrid)
2. **Fill in the stories section** in the architecture-decision.md output
3. **Update sidecar.yaml** with the generated stories:

```yaml
stories:
  step_2_architect:
    - id: "ARCH-S01"
      title: "[from template]"
      status: "pending"
    - id: "ARCH-S02"
      title: "[from template]"
      status: "pending"
    # ... additional stories based on architecture
```

The template provides complete story definitions with acceptance criteria for both RAG-only and Fine-tuning/Hybrid paths.

### 15. Present MENU OPTIONS

Display: **Step 2 Complete - Select an Option:** [A] Analyze decisions further [Q] Run different queries [P] View progress [C] Continue to Step 3 (Data Engineer)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit architecture OR tech stack decisions, allow refinement, then redisplay menu
- IF Q: "Which layer would you like to re-query? (Orchestration / Vector DB / Experiment Tracking / Serving / Monitoring)" - Allow user to run different knowledge MCP queries with adjusted constraints, then re-synthesize stack, then redisplay menu
- IF P: Show project-spec.md, architecture-decision.md, tech-stack-decision.md, and decision-log.md summaries, then redisplay menu
- IF C:
  1. Verify sidecar is updated with BOTH architecture AND tech stack decisions
  2. Verify architecture-decision.md created
  3. Verify tech-stack-decision.md created with KB query results and synthesis
  4. Verify decision-log.md contains ARCH-001 and TECH-001 entries
  5. Load, read entire file, then execute `{nextStepFile}` (Data Engineer)
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND BOTH architecture AND tech stack decisions are documented with stories generated, will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Step 3: Data Engineer.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

**Build vs Buy Decision:**
- Three-question framework from "LLMs in Production" presented (Figure 1.1)
- User answered Q1: Is LLM critical to business?
- User answered Q2: Are you sure? (Confidence validation)
- User answered Q3: Privacy/security requirements?
- Clear BUILD or BUY decision made based on framework
- Sidecar updated with build_vs_buy value
- Decision-log.md contains BUILD-001 entry with framework details

**Architecture Decision (if BUILDING):**
- Knowledge MCP queried for RAG vs Fine-tuning decision criteria
- Use case thoroughly analyzed with user
- Clear architecture decision made and documented
- Sidecar updated with architecture value
- Decision-log.md contains ARCH-001 entry
- User confirmed direction before proceeding

**Tech Stack Decision:**
- Team constraints gathered (cloud, budget, expertise, overhead, team size)
- Knowledge MCP DYNAMICALLY QUERIED for each tool layer (5+ queries, contextualized with user constraints)
  - Orchestration: Queried with architecture + team size context
  - Vector DB: Queried with deployment + performance needs context
  - Experiment Tracking: Queried with ML focus + budget context
  - Serving: Queried with cloud + scale context
  - Monitoring: Queried with LLM vs general + complexity context
- Query results synthesized to extract patterns, trade-offs, warnings
- Tool stack decision made based on knowledge base recommendations (NOT hardcoded options)
- tech-stack-decision.md created with:
  - Actual KB query text and results
  - Synthesis of patterns and trade-offs per layer
  - Cost and effort estimates from KB patterns
  - Rationale grounded in knowledge base (not personal opinion)
- Sidecar updated with tech_stack values
- Decision-log.md updated with ARCH-001 AND TECH-001 entries (with KB references)

**Documentation & Handoff:**
- architecture-decision.md created
- tech-stack-decision.md created
- project-spec.md updated with overview and tech choices
- decision-log.md updated with both decisions
- Sidecar updated with architecture + tech_stack + decisions
- Architecture stories generated

### ❌ SYSTEM FAILURE:

**Architecture Decision:**
- Making architecture decision without user input
- Skipping Knowledge MCP queries for RAG vs FT
- Not documenting the decision in all required files
- Not updating sidecar with architecture value

**Tech Stack Decision:**
- Skipping Knowledge MCP queries for tool selection (all queries must be contextualized)
- Making tool recommendations without constraint analysis
- **CRITICAL FAILURE:** Presenting hardcoded "Option A/B/C" stacks instead of querying knowledge base
- **CRITICAL FAILURE:** Not showing KB query process to user (synthesis should be visible, not hidden)
- Not documenting actual KB query results and synthesis
- Not creating tech-stack-decision.md
- Not updating sidecar with tech_stack section
- Recommending tools based on "best practices" instead of knowledge base extractions

**General Failures:**
- Proceeding to Phase 1 without confirmed BOTH decisions
- Discussing implementation details (belongs in Phase 1-3)
- Not generating stories based on decisions
- Incomplete sidecar updates

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

## HANDOFF TO DATA ENGINEER (STEP 3)

The tech stack decision becomes THE FOUNDATION for all downstream phases:

**Data Engineer (Phase 1):**
- Uses `{orchestration_tool}` to build feature pipeline
- Uses `{vector_db}` for semantic storage
- Coordinates with `{tracking_tool}` for experiment logging

**Training Specialist (Phase 2 - if fine-tuning):**
- Uses `{orchestration_tool}` for training workflows
- Uses `{tracking_tool}` for experiment tracking
- Follows cost constraints defined in tech-stack-decision.md

**Inference Architect (Phase 3):**
- Uses `{serving_tool}` for model deployment
- Configures `{monitoring_tool}` (Opik) for LLM-specific metrics
- Integrates with `{orchestration_tool}` for inference pipelines

**Evaluator (Phase 4):**
- Uses `{tracking_tool}` for evaluation metrics
- References cost/performance constraints from tech-stack-decision.md
- May recommend tool changes if constraints violated

**MLOps Engineer (Phase 5):**
- Uses `{monitoring_tool}` for production observability
- Uses `{orchestration_tool}` for drift detection pipelines
- Uses `{tracking_tool}` for baseline metrics

**KEY:** Any downstream phase suggesting different tools = BLOCKER until reconciled with Phase 0 tech stack decision. Consistency across phases is CRITICAL.
