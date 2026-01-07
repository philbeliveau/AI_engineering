# AI Engineering Workflow - Architecture Overview

**Version:** 1.0.0
**Last Updated:** January 6, 2026
**Status:** Production Ready

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [The 13-Step Workflow](#the-13-step-workflow)
3. [Knowledge MCP Integration](#knowledge-mcp-integration)
4. [Conditional Routing Logic](#conditional-routing-logic)
5. [State Machine Progression](#state-machine-progression)
6. [Component Interactions](#component-interactions)
7. [Data Flow](#data-flow)

---

## System Architecture

### Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI ENGINEERING WORKFLOW                              │
│                       (13-Step FTI Pipeline Pattern)                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ PHASE 1      │  Step 1: Business Analyst
│ DISCOVERY    │  - Project initialization
│              │  - Stakeholder analysis
│              │  - Business metrics definition
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PHASE 2      │  Step 2A: FTI Architect (Part 1)
│ ARCHITECTURE │  - Build vs Buy decision
│              │  - RAG vs Fine-tuning decision
│              │  - Architecture options selection
└──────┬───────┘
       │
       ▼
┌──────────────┐
│              │  Step 2B: FTI Architect (Part 2)
│              │  - Tech stack selection
│              │  - Conditional routing based on Step 2A
│              │  - Architecture confirmation
└──────┬───────┘
       │
    ┌──┴──────────────────────────────┐
    │                                  │
    ▼                                  ▼
┌─────────────────────┐      ┌──────────────────────┐
│ PHASE 3A: DATA      │      │ BRANCH A: RAG-ONLY   │
│ ENGINEERING         │      │ Path                 │
│                     │      │ (Steps 3-9)          │
│ Step 3A: Data       │      │                      │
│ Requirements        │      └──────────────────────┘
│                     │
│ Step 3B: Data       │      ┌──────────────────────┐
│ Pipeline Design     │      │ BRANCH B: FINE-      │
└─────────┬───────────┘      │ TUNING Path          │
          │                  │ (Steps 3-9 +         │
          │                  │  Step 5: Fine-       │
          │                  │  Tuning)             │
          │                  └──────────────────────┘
          │
          ▼
┌──────────────┐
│ PHASE 3B     │  Step 4: Embeddings Engineer
│ EMBEDDINGS   │  - Chunking strategy
│              │  - Embedding model selection
│              │  - Vector database setup
└──────┬───────┘
       │
       ├─── (Conditional on Step 2A output)
       │
       ▼
┌──────────────────────────────────────────┐
│ PHASE 4 (CONDITIONAL)                    │
│ Step 5: Fine-Tuning Specialist           │
│ (Only if "fine-tuning" path selected)    │
│ - SFT/DPO configuration                  │
│ - Dataset preparation                    │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ PHASE 5      │  Step 6: RAG Specialist
│ RETRIEVAL    │  - RAG pipeline design
│              │  - Retrieval strategy
│              │  - Reranking configuration
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PHASE 6      │  Step 7: Prompt Engineer
│ PROMPTING    │  - System prompt design
│              │  - Few-shot examples
│              │  - Template creation
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PHASE 7      │  Step 8: LLM Evaluator
│ EVALUATION   │  - Evaluation framework
│              │  - Benchmark selection
│              │  - Metrics definition
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PHASE 8      │  Step 9: MLOps Engineer
│ OPERATIONS   │  - Monitoring setup
│              │  - Drift detection
│              │  - Alerting configuration
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PHASE 9      │  Step 10: Tech Lead (Review & Validation)
│ REVIEW       │  - Cross-step validation
│              │  - Conflict detection
│              │  - GO/REVISE decision
└──────┬───────┘
       │
       ├─── (If conflicts found, send back to specific phases)
       │
       ▼
┌──────────────┐
│ PHASE 10     │  Step 11: Story Elaboration
│ ELABORATION  │  - Transform raw stories to BMM format
│              │  - Add tasks and subtasks
│              │  - Add developer notes
└──────┬───────┘
       │
       ▼
┌──────────────┐
│              │  Step 12: Story Sequencing
│ PHASE 11     │  - Organize stories by priority
│ SEQUENCING   │  - Identify dependencies
│              │  - Create sprint roadmap
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PHASE 12     │  Step 13: Handoff
│ HANDOFF      │  - Generate final deliverables
│              │  - Create implementation guide
│              │  - Archive project state
└──────────────┘
```

### Architecture Tiers

#### Tier 1: Input Processing
- **Step 1 (Business Analyst)**: Gathers requirements and business context
- **Step 2A-2B (FTI Architect)**: Makes critical architectural decisions

#### Tier 2: Technical Design
- **Steps 3-4**: Data and embeddings engineering
- **Step 5** (Conditional): Fine-tuning design
- **Steps 6-7**: RAG and prompting strategies

#### Tier 3: Validation & Operations
- **Step 8**: Evaluation framework design
- **Step 9**: MLOps and monitoring setup
- **Step 10**: Cross-step validation by Tech Lead

#### Tier 4: Story Generation
- **Steps 11-13**: Transform designs into implementation stories

---

## The 13-Step Workflow

### Step 1: Business Analyst - Requirements Elicitation

**Input:** User's AI project description
**Output:** `requirements.md`, updated `sidecar.yaml`

```
Phase: DISCOVERY
Duration: 15-20 minutes
Agent: Business Analyst (persona-driven)

Process:
1. Load agent persona (business-analyst.md)
2. Present discovery interview framework
3. Ask structured questions about:
   - Problem domain
   - Stakeholders
   - Success metrics
   - Constraints
4. Document answers in requirements.md
5. Update sidecar.yaml with discovery phase status
```

**Key Outputs:**
- Clear problem statement
- Stakeholder identification
- Success metrics and KPIs
- Initial constraints

---

### Step 2A: FTI Architect (Part 1) - Architecture Decision

**Input:** requirements.md
**Output:** `architecture-decision.md`, updated `sidecar.yaml`

```
Phase: ARCHITECTURE (Part 1)
Duration: 20-25 minutes
Agent: FTI Architect (persona-driven)

Critical Decisions:
1. Build vs Buy
   - Query Knowledge MCP for framework recommendations
   - Compare options: Build, Buy, Hybrid
   - Record decision rationale

2. RAG vs Fine-tuning
   - Query Knowledge MCP for architecture patterns
   - Evaluate trade-offs
   - Determine feasibility based on data availability

3. Hybrid Approaches
   - Query Knowledge MCP for hybrid patterns
   - Document combined strategy if selected

Knowledge MCP Queries (MANDATORY):
- get_decisions: "framework selection approaches"
- get_patterns: "RAG implementation patterns"
- get_warnings: "fine-tuning pitfalls"
- get_methodologies: "AI system architecture"

Process:
1. Load FTI Architect persona (fti-architect.md)
2. Review requirements.md
3. Execute architecture decision framework
4. Query Knowledge MCP at decision points
5. Present 3 architecture options:
   - RAG-only approach
   - Fine-tuning approach
   - Hybrid approach
6. Record selected option
7. Update sidecar.yaml with architecture decisions
8. Generate architecture-decision.md
```

**Key Outputs:**
- Build vs Buy decision (recorded)
- RAG vs Fine-tuning decision (recorded)
- Selected architecture option
- Rationale for each decision

---

### Step 2B: FTI Architect (Part 2) - Tech Stack Selection

**Input:** architecture-decision.md, requirements.md
**Output:** `tech-stack.md`, updated `sidecar.yaml`

```
Phase: ARCHITECTURE (Part 2)
Duration: 25-30 minutes
Agent: FTI Architect (persona-driven)

Conditional Logic:
- If Step 2A selected "RAG-only":
  - Skip fine-tuning-specific components
  - Focus on RAG stack

- If Step 2A selected "Fine-tuning":
  - Include training infrastructure
  - Include fine-tuning frameworks

- If Step 2A selected "Hybrid":
  - Include both RAG and fine-tuning stacks

Knowledge MCP Queries (Dynamic, based on Step 2A):
- get_decisions: "vector database selection"
- get_patterns: "embedding model selection patterns"
- get_decisions: "LLM framework choices"
- get_patterns: "prompt framework patterns"
- get_warnings: "common stack pitfalls"
- get_methodologies: "production deployment patterns"

Process:
1. Load architecture-decision.md
2. Query Knowledge MCP (conditional on Step 2A output)
3. Present tech stack options for:
   - Vector database (Pinecone, Qdrant, Milvus, Weaviate)
   - Embedding model (OpenAI, Hugging Face, etc.)
   - LLM framework (LangChain, LlamaIndex, etc.)
   - Fine-tuning framework (if applicable)
4. Record selected technologies
5. Document trade-offs and constraints
6. Architecture Confirmation Checkpoint (CRITICAL)
   - Present complete architecture summary
   - User confirms or requests revisions
7. Update sidecar.yaml with tech stack selections
8. Generate tech-stack.md
```

**Key Outputs:**
- Selected tech stack (vector DB, embedding model, framework)
- Trade-off documentation
- Architecture confirmation from user

---

### Step 3A: Data Engineer - Requirements Definition

**Input:** architecture-decision.md, tech-stack.md
**Output:** `data-requirements.md`, updated `sidecar.yaml`

```
Phase: DATA ENGINEERING (Part 1)
Duration: 15-20 minutes
Agent: Data Engineer (persona-driven)

Conditional Logic:
- If "RAG-only" path:
  - Focus on ingestion data sources
  - Document embedding requirements

- If "Fine-tuning" path:
  - Include training data requirements
  - Document labeling strategy

- If "Hybrid" path:
  - Include both ingestion and training data

Knowledge MCP Queries:
- get_patterns: "data ingestion patterns"
- get_warnings: "data quality issues"
- get_decisions: "data source evaluation"

Process:
1. Load Data Engineer persona (data-engineer.md)
2. Review architecture decisions
3. Assess data requirements:
   - Data availability
   - Data format and structure
   - Quality metrics
   - Scale estimates
4. Document feasibility assessment
5. Update sidecar.yaml
```

**Key Outputs:**
- Data availability assessment
- Format and structure documentation
- Quality requirements
- Feasibility report

---

### Step 3B: Data Engineer - Pipeline Design

**Input:** data-requirements.md, requirements.md
**Output:** `data-pipeline.md`, updated `sidecar.yaml`

```
Phase: DATA ENGINEERING (Part 2)
Duration: 20-25 minutes
Agent: Data Engineer (persona-driven)

Knowledge MCP Queries:
- get_patterns: "data pipeline design"
- get_methodologies: "data processing workflows"
- get_warnings: "data pipeline pitfalls"

Process:
1. Design data pipeline architecture
2. Document ingestion strategy
3. Define quality checks
4. Specify monitoring points
5. Generate data-pipeline.md
6. Update sidecar.yaml
```

**Key Outputs:**
- Data pipeline architecture
- Ingestion procedures
- Quality assurance processes
- Monitoring strategy

---

### Step 4: Embeddings Engineer - Embeddings Strategy

**Input:** data-pipeline.md, tech-stack.md
**Output:** `embeddings-strategy.md`, updated `sidecar.yaml`

```
Phase: EMBEDDINGS & VECTORIZATION
Duration: 20-25 minutes
Agent: Embeddings Engineer (persona-driven)

Knowledge MCP Queries:
- get_decisions: "embedding model selection"
- get_patterns: "chunking strategy patterns"
- get_warnings: "embedding pitfalls"
- get_methodologies: "vector database setup"

Process:
1. Load Embeddings Engineer persona
2. Define chunking strategy:
   - Chunk size (tokens)
   - Overlap strategy
   - Document structure handling
3. Select embedding model:
   - Dimensionality
   - Training data compatibility
   - Cost considerations
4. Configure vector database:
   - Indexing strategy
   - Search parameters
   - Storage requirements
5. Document metadata handling
6. Generate embeddings-strategy.md
7. Update sidecar.yaml
```

**Key Outputs:**
- Chunking strategy with parameters
- Embedding model selection and rationale
- Vector database configuration
- Metadata handling strategy

---

### Step 5: Fine-Tuning Specialist - Fine-Tuning Design (CONDITIONAL)

**Input:** data-pipeline.md, tech-stack.md, Step 2A decision
**Output:** `fine-tuning-config.md`, updated `sidecar.yaml`
**Condition:** Only executed if Step 2A selected fine-tuning or hybrid approach

```
Phase: FINE-TUNING (CONDITIONAL)
Duration: 25-30 minutes
Agent: Fine-Tuning Specialist (persona-driven)

Knowledge MCP Queries:
- get_decisions: "SFT vs DPO approaches"
- get_patterns: "fine-tuning data preparation"
- get_warnings: "fine-tuning pitfalls"
- get_methodologies: "fine-tuning workflows"

Process:
1. Load Fine-Tuning Specialist persona
2. Determine fine-tuning approach:
   - Supervised Fine-Tuning (SFT)
   - Reinforcement Learning from Human Feedback (RLHF)
   - Direct Preference Optimization (DPO)
3. Define training data requirements:
   - Format specification
   - Quality standards
   - Size estimates
4. Configure training parameters:
   - Learning rate
   - Batch size
   - Epochs
   - Validation strategy
5. Define evaluation criteria
6. Document cost estimates
7. Generate fine-tuning-config.md
8. Update sidecar.yaml

Note: Skipped entirely if Step 2A = "RAG-only"
```

**Key Outputs:**
- Fine-tuning approach selection
- Training data specifications
- Hyperparameter configuration
- Cost and resource estimates

---

### Step 6: RAG Specialist - RAG Pipeline Design

**Input:** embeddings-strategy.md, data-pipeline.md, fine-tuning-config.md (if applicable)
**Output:** `rag-design.md`, updated `sidecar.yaml`

```
Phase: RETRIEVAL-AUGMENTED GENERATION
Duration: 25-30 minutes
Agent: RAG Specialist (persona-driven)

Knowledge MCP Queries:
- get_patterns: "RAG pipeline architectures"
- get_decisions: "retrieval strategy selection"
- get_warnings: "RAG pitfalls and failures"
- get_methodologies: "context window optimization"

Process:
1. Load RAG Specialist persona
2. Design retrieval pipeline:
   - Similarity search strategy
   - Ranking approach
   - Context windowing
3. Configure reranking:
   - Reranker selection
   - Ranking criteria
   - Cutoff thresholds
4. Define context assembly:
   - Context template
   - Metadata inclusion
   - Ordering strategy
5. Plan chunking post-processing:
   - De-duplication
   - Context merging
   - Formatting
6. Document integration points
7. Generate rag-design.md
8. Update sidecar.yaml
```

**Key Outputs:**
- Retrieval strategy documentation
- Reranking configuration
- Context assembly pipeline
- Integration architecture

---

### Step 7: Prompt Engineer - Prompt Design

**Input:** rag-design.md, requirements.md, architecture-decision.md
**Output:** `prompt-design.md`, updated `sidecar.yaml`

```
Phase: PROMPTING & TEMPLATES
Duration: 20-25 minutes
Agent: Prompt Engineer (persona-driven)

Knowledge MCP Queries:
- get_patterns: "system prompt patterns"
- get_patterns: "few-shot examples"
- get_warnings: "prompt engineering pitfalls"
- get_methodologies: "prompt design processes"

Process:
1. Load Prompt Engineer persona
2. Design system prompt:
   - Role and context
   - Instructions and constraints
   - Output format specification
3. Create prompt templates:
   - User query template
   - Context integration points
   - Response formatting
4. Develop few-shot examples:
   - Quality levels
   - Domain variation
   - Edge cases
5. Document prompt versioning strategy
6. Plan A/B testing approach
7. Generate prompt-design.md
8. Update sidecar.yaml
```

**Key Outputs:**
- System prompt template
- User query templates
- Few-shot example set
- Prompt versioning strategy

---

### Step 8: LLM Evaluator - Evaluation Framework

**Input:** prompt-design.md, requirements.md, rag-design.md
**Output:** `evaluation-framework.md`, updated `sidecar.yaml`

```
Phase: EVALUATION & METRICS
Duration: 20-25 minutes
Agent: LLM Evaluator (persona-driven)

Knowledge MCP Queries:
- get_decisions: "evaluation metric selection"
- get_patterns: "evaluation framework patterns"
- get_warnings: "evaluation pitfalls"
- get_methodologies: "benchmark design"

Process:
1. Load LLM Evaluator persona
2. Define success metrics:
   - Business metrics (from Step 1)
   - Technical metrics
   - User satisfaction metrics
3. Select evaluation approaches:
   - Automated metrics (BLEU, ROUGE, etc.)
   - Human evaluation
   - Real-world testing
4. Create benchmark dataset:
   - Test set composition
   - Size requirements
   - Diversity considerations
5. Define evaluation process:
   - Frequency
   - Threshold decision criteria
   - Failure investigation protocol
6. Document cost estimates
7. Generate evaluation-framework.md
8. Update sidecar.yaml
```

**Key Outputs:**
- Evaluation metrics specification
- Benchmark dataset definition
- Evaluation process documentation
- Success criteria thresholds

---

### Step 9: MLOps Engineer - Operations & Monitoring

**Input:** evaluation-framework.md, rag-design.md, fine-tuning-config.md (if applicable)
**Output:** `operations-plan.md`, updated `sidecar.yaml`

```
Phase: OPERATIONS & MONITORING
Duration: 20-25 minutes
Agent: MLOps Engineer (persona-driven)

Knowledge MCP Queries:
- get_patterns: "monitoring architectures"
- get_decisions: "alert strategy selection"
- get_warnings: "production ML pitfalls"
- get_methodologies: "drift detection approaches"

Process:
1. Load MLOps Engineer persona
2. Design monitoring strategy:
   - Metrics to track
   - Collection points
   - Storage approach
3. Define alerting:
   - Alert thresholds
   - Notification channels
   - Escalation procedures
4. Plan drift detection:
   - Input drift detection
   - Model performance drift detection
   - Response to drift
5. Document incident response:
   - Detection procedures
   - Rollback strategy
   - Recovery steps
6. Specify logging requirements
7. Generate operations-plan.md
8. Update sidecar.yaml
```

**Key Outputs:**
- Monitoring architecture
- Alert configuration
- Drift detection strategy
- Incident response procedures

---

### Step 10: Tech Lead - Review & Validation

**Input:** All previous outputs (stories from Steps 1-9)
**Output:** `validation-report.md`, decision to proceed or revise

```
Phase: CROSS-STEP VALIDATION
Duration: 30-40 minutes
Agent: Tech Lead (persona-driven)

Process:
1. Load Tech Lead persona
2. Review all generated stories/outputs:
   - Architecture consistency
   - Technical stack alignment
   - Data strategy feasibility
   - Deployment readiness
3. Validate handoff points:
   - Step 1 → Step 2 context
   - Step 2A → Step 2B context
   - Step 2B → Steps 3+ context
   - Each technical step to next
4. Check for conflicts:
   - Technology mismatches
   - Data assumptions violations
   - Architectural inconsistencies
5. Generate validation report:
   - Issues found (if any)
   - Recommendations for revision
   - Risk assessment
6. Decision point:
   - GO: Proceed to story elaboration
   - REVISE: Send work back to specific phases
   - NEEDS_CLARIFICATION: Request more info

If REVISE:
- Identify which steps need rework
- Provide specific feedback
- Return to those steps
- Restart from Tech Lead review

If GO:
- Update sidecar.yaml with approval
- Proceed to Step 11
```

**Key Outputs:**
- Validation report
- Conflict identification (if any)
- GO/REVISE decision
- Feedback for revisions (if needed)

---

### Step 11: Story Elaboration - BMM Transformation

**Input:** All validated design outputs
**Output:** Implementation-ready stories in BMM format

```
Phase: STORY ELABORATION
Duration: 30-40 minutes
Agent: Story Elaborator (embedded in workflow)

Process:
1. Transform design outputs to user stories:
   - Step 1 → Discovery epic
   - Step 2 → Architecture epic
   - Step 3 → Data Engineering epic
   - Step 4 → Embeddings epic
   - Step 5 → Fine-tuning epic (if applicable)
   - Step 6 → RAG epic
   - Step 7 → Prompting epic
   - Step 8 → Evaluation epic
   - Step 9 → Operations epic

2. For each story, add:
   - User story format (As a... I want... So that...)
   - Acceptance criteria
   - Tasks and subtasks
   - Developer implementation notes
   - Testing requirements
   - Dependencies

3. Add technical context:
   - Architecture references
   - Knowledge MCP queries to run
   - Code patterns to follow
   - Quality standards
```

**Key Outputs:**
- Implementation-ready user stories (9 epics)
- Detailed acceptance criteria
- Task breakdowns
- Developer guidance

---

### Step 12: Story Sequencing - Roadmap Creation

**Input:** Elaborated stories from Step 11
**Output:** Implementation roadmap and sprint plan

```
Phase: STORY SEQUENCING & ROADMAP
Duration: 15-20 minutes

Process:
1. Organize stories by execution phase:
   - Foundational phase (infrastructure setup)
   - Feature development phase
   - Integration phase
   - Testing and refinement phase
   - Deployment phase

2. Identify dependencies:
   - Hard dependencies (must complete before)
   - Soft dependencies (should complete before)
   - Parallel work opportunities

3. Create sprint roadmap:
   - Story point estimation
   - Sprint assignments (2-week sprints typical)
   - Resource allocation
   - Risk mitigation

4. Generate roadmap documentation
```

**Key Outputs:**
- Implementation roadmap (3-6 months typical)
- Sprint planning (first 2-3 sprints detailed)
- Dependency graph
- Risk timeline

---

### Step 13: Handoff - Final Deliverables

**Input:** Complete workflow outputs and roadmap
**Output:** Implementation guide, project archive

```
Phase: HANDOFF & DELIVERY
Duration: 10-15 minutes

Process:
1. Generate final deliverables package:
   - Complete design documentation
   - Implementation roadmap
   - Story backlog
   - Architecture validation report

2. Create implementation guide:
   - Setup instructions
   - Development environment setup
   - First story walkthrough
   - Knowledge MCP integration instructions

3. Archive project state:
   - Save all sidecar.yaml values
   - Package all outputs
   - Create reference index

4. Provide next steps:
   - How to start implementation
   - Where to access resources
   - Who to contact for questions
```

**Key Outputs:**
- Implementation guide
- Complete deliverables package
- Project reference index
- Next steps checklist

---

## Knowledge MCP Integration

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW EXECUTION                       │
│                                                              │
│  Step 1 → Step 2A → Step 2B → Steps 3-9 → Step 10 → ...    │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   KNOWLEDGE MCP QUERIES       │
        │   (Runtime at each step)      │
        └───────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    ┌────────┐   ┌────────┐   ┌──────────────┐
    │Decisions│   │Patterns│   │Warnings      │
    └────────┘   └────────┘   └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
        ┌───────────────────────────────┐
        │   AI AGENT SYNTHESIS          │
        │   (Contextual application)    │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   STEP OUTPUT GENERATION      │
        │   (Informed by knowledge)     │
        └───────────────────────────────┘
```

### Query Points by Step

#### Step 2A: FTI Architect
```
Mandatory Queries:
1. get_decisions("framework selection approaches")
2. get_patterns("RAG implementation patterns")
3. get_warnings("fine-tuning pitfalls")
4. get_methodologies("AI system architecture")

Synthesis Approach:
1. Extract decision alternatives with trade-offs
2. Identify architectural patterns for each approach
3. Surface critical warnings and failure modes
4. Connect to documented methodologies for validation
```

#### Step 2B: Tech Stack
```
Conditional Queries (based on Step 2A output):
1. get_decisions("vector database selection")
2. get_patterns("embedding model selection patterns")
3. get_decisions("LLM framework choices")
4. get_patterns("prompt framework patterns")
5. get_warnings("common stack pitfalls")
6. get_methodologies("production deployment patterns")

Synthesis Approach:
1. Extract decisions with trade-offs for each component
2. Identify patterns matching project constraints
3. Surface warnings specific to selected architecture
4. Validate against deployment methodologies
```

#### Step 3A: Data Requirements
```
Knowledge MCP Queries:
1. get_patterns("data ingestion patterns")
2. get_warnings("data quality issues")
3. get_decisions("data source evaluation")

Synthesis Approach:
1. Extract patterns for data ingestion matching format
2. Surface quality issues relevant to domain
3. Connect to decision frameworks for source evaluation
```

#### Step 3B: Data Pipeline
```
Knowledge MCP Queries:
1. get_patterns("data pipeline design")
2. get_methodologies("data processing workflows")
3. get_warnings("data pipeline pitfalls")

Synthesis Approach:
1. Extract pipeline patterns matching architecture
2. Follow documented workflows for design approach
3. Identify and mitigate common pitfalls
```

#### Step 4: Embeddings
```
Knowledge MCP Queries:
1. get_decisions("embedding model selection")
2. get_patterns("chunking strategy patterns")
3. get_warnings("embedding pitfalls")
4. get_methodologies("vector database setup")

Synthesis Approach:
1. Extract embedding decisions with comparison matrices
2. Identify chunking patterns for data type
3. Surface embedding-specific pitfalls
4. Follow documented vector DB setup procedures
```

#### Step 5: Fine-Tuning (Conditional)
```
Knowledge MCP Queries:
1. get_decisions("SFT vs DPO approaches")
2. get_patterns("fine-tuning data preparation")
3. get_warnings("fine-tuning pitfalls")
4. get_methodologies("fine-tuning workflows")

Synthesis Approach:
1. Extract approach decisions with trade-off analysis
2. Identify data prep patterns for approach
3. Surface fine-tuning-specific failure modes
4. Follow documented workflows for configuration
```

#### Step 6: RAG Pipeline
```
Knowledge MCP Queries:
1. get_patterns("RAG pipeline architectures")
2. get_decisions("retrieval strategy selection")
3. get_warnings("RAG pitfalls and failures")
4. get_methodologies("context window optimization")

Synthesis Approach:
1. Extract patterns matching project architecture
2. Extract decisions for retrieval strategy selection
3. Surface RAG-specific failure modes with mitigations
4. Apply documented optimization methodologies
```

#### Step 7: Prompting
```
Knowledge MCP Queries:
1. get_patterns("system prompt patterns")
2. get_patterns("few-shot examples")
3. get_warnings("prompt engineering pitfalls")
4. get_methodologies("prompt design processes")

Synthesis Approach:
1. Extract system prompt patterns for domain
2. Surface few-shot design patterns
3. Identify prompt-specific failure modes
4. Follow documented design methodologies
```

#### Step 8: Evaluation
```
Knowledge MCP Queries:
1. get_decisions("evaluation metric selection")
2. get_patterns("evaluation framework patterns")
3. get_warnings("evaluation pitfalls")
4. get_methodologies("benchmark design")

Synthesis Approach:
1. Extract metric decisions matched to business goals
2. Identify framework patterns for project type
3. Surface evaluation-specific pitfalls
4. Follow documented benchmark design methodology
```

#### Step 9: Operations
```
Knowledge MCP Queries:
1. get_patterns("monitoring architectures")
2. get_decisions("alert strategy selection")
3. get_warnings("production ML pitfalls")
4. get_methodologies("drift detection approaches")

Synthesis Approach:
1. Extract patterns for monitoring architecture
2. Extract decisions for alert strategy selection
3. Surface production-specific failure modes
4. Apply documented drift detection methodologies
```

### Knowledge-Grounding Principles

When agents query the Knowledge MCP:

#### Principle 1: Reference Patterns, Don't Copy-Paste
- Extract methodologies and principles
- Don't hardcode values from a single source
- Present as "current recommendations" not "the answer"
- Allow knowledge to evolve as more sources are added

#### Principle 2: Query at Runtime
- The Knowledge MCP grows with more sources
- Design queries to be dynamic
- Don't embed static content that becomes stale
- Condition queries on accumulated project context

#### Principle 3: Show Synthesis Approach
- Teach HOW to apply knowledge, not just WHAT it says
- Include synthesis steps in workflow guidance
- Example: "Extract patterns → Identify trade-offs → Surface warnings"
- Validate recommendations against multiple sources

---

## Conditional Routing Logic

### Primary Branching: Step 2A Output

Step 2A produces a critical decision that controls the entire downstream workflow:

```
Step 2A Decision: Architecture Type
├── RAG-Only
│   └── Path: Steps 3-9 (RAG-focused)
│       └── Step 5 (Fine-Tuning): SKIPPED
│       └── Step 6 (RAG): FULLY EXECUTED
│
├── Fine-Tuning
│   └── Path: Steps 3-9 (Training-focused)
│       └── Step 5 (Fine-Tuning): FULLY EXECUTED
│       └── Step 6 (RAG): Minimal/Optional
│
└── Hybrid (RAG + Fine-Tuning)
    └── Path: Steps 3-9 (Both strategies)
        └── Step 5 (Fine-Tuning): FULLY EXECUTED
        └── Step 6 (RAG): FULLY EXECUTED
```

### Conditional Execution: Step 5

```
Condition: IF Step 2A Output = "Fine-Tuning" OR "Hybrid"
THEN Execute Step 5
ELSE Skip Step 5

Rationale:
- RAG-only projects don't need fine-tuning specialist
- Saves 25-30 minutes for non-training projects
- Reduces unnecessary stories in final backlog
```

### Context-Dependent Knowledge MCP Queries: Step 2B

```
Condition: Step 2A Output
├── IF "RAG-Only":
│   └── Focus tech stack queries on:
│       - RAG frameworks
│       - Retrieval databases
│       - Embedding models
│       - Prompt frameworks
│
├── IF "Fine-Tuning":
│   └── Focus tech stack queries on:
│       - Fine-tuning frameworks
│       - Training infrastructure
│       - Distributed training
│       - Model optimization
│
└── IF "Hybrid":
    └── Focus tech stack queries on:
        - RAG frameworks
        - Fine-tuning frameworks
        - Integration patterns
        - Infrastructure scaling
```

### Adaptive Tech Stack Selection: Steps 3-9

```
Each step's output adapts based on Step 2A and Step 2B selections:

Data Engineer (Step 3):
├── IF "Fine-Tuning" path:
│   └── Include training data requirements
└── IF "RAG" path:
    └── Include ingestion data requirements

Embeddings Engineer (Step 4):
├── IF "Fine-Tuning" path:
│   └── Consider embedding model fine-tunability
└── IF "RAG" path:
    └── Focus on retrieval embedding quality

RAG Specialist (Step 6):
├── IF "RAG" path:
│   └── Full RAG pipeline design
├── IF "Fine-Tuning" path:
│   └── Optional RAG for hybrid retrieval
└── IF "Hybrid" path:
    └── RAG as secondary retrieval layer
```

---

## State Machine Progression

### State Variables in `sidecar.yaml`

```yaml
# Phase Tracking
phase: "string"  # Current workflow phase
phaseCompleted: ["step-01", "step-02a", ...]

# Step Tracking
currentStep: "01" | "02a" | "02b" | "03a" | ...
stepsCompleted: [1, 2, 3, ...]  # Completed step numbers

# Decision Tracking
decisions:
  build_vs_buy: "build" | "buy" | "hybrid" | null
  rag_vs_finetuning: "rag" | "finetuning" | "hybrid" | null
  architecture_type: "rag-only" | "finetuning" | "hybrid" | null

# Tech Stack Tracking
techStack:
  vectorDatabase: "string"
  embeddingModel: "string"
  framework: "string"
  finetuningFramework: "string" | null

# Context Tracking
currentContext: {}  # Accumulated context from previous steps
lastContextClearance: "step-02b" | "step-03b" | ...

# Approval Tracking
techLeadApproval: true | false | null
approvalDate: "YYYY-MM-DD" | null
revisionsRequired: []

# Overall Status
status: "in-progress" | "paused" | "revision" | "approved" | "complete"
completedAt: "YYYY-MM-DD HH:MM" | null
```

### State Transitions

```
INITIAL STATE
└── sidecar.yaml created with default values

STEP COMPLETION TRANSITION
├── Execute step fully
├── Update sidecar:
│   - Increment stepsCompleted array
│   - Update currentStep
│   - Record step-specific decisions/outputs
│   - Update phase
└── Signal ready for next step

CONDITIONAL BRANCH TRANSITION (at Step 2A)
├── Record Step 2A decision
├── Update architecture_type
├── Skip or include Step 5 based on decision
└── Adapt Steps 3-9 queries/outputs accordingly

REVISION TRANSITION (at Step 10)
├── Tech Lead validation identifies issues
├── Record revisionsRequired list
├── Update status to "revision"
├── Return to specific step
├── Restart validation at Step 10
└── Clear intermediate decisions if needed

COMPLETION TRANSITION (at Step 13)
├── All steps completed successfully
├── Generate final deliverables
├── Update sidecar:
│   - status = "complete"
│   - completedAt = timestamp
│   - Archive all decisions
└── Project ready for implementation
```

### Example State Progression: RAG-Only Project

```
Step 1 (Complete):
├── stepsCompleted: [1]
├── phase: "discovery"
├── currentStep: "02a"
└── status: "in-progress"

Step 2A (Complete, RAG path):
├── stepsCompleted: [1, 2, 3]  # Note: 2A and 2B counted as 2 and 3
├── decisions.architecture_type: "rag-only"
├── phase: "architecture"
├── currentStep: "02b"
└── status: "in-progress"

Step 2B (Complete):
├── stepsCompleted: [1, 2, 3]
├── techStack: {vectorDatabase: "Qdrant", embeddingModel: "...", ...}
├── phase: "architecture"
├── currentStep: "03a"
└── status: "in-progress"

Step 3A (Complete):
├── stepsCompleted: [1, 2, 3, 4]
├── phase: "data-engineering"
├── currentStep: "03b"
└── status: "in-progress"

Step 3B (Complete):
├── stepsCompleted: [1, 2, 3, 4, 5]
├── phase: "data-engineering"
├── currentStep: "04"
└── status: "in-progress"

Step 4 (Complete):
├── stepsCompleted: [1, 2, 3, 4, 5, 6]
├── phase: "embeddings"
├── currentStep: "05"  # But Step 5 skipped due to rag-only
└── status: "in-progress"

NOTE: Step 5 is skipped, currentStep jumps from "04" to "06"

Step 6 (Complete):
├── stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
├── phase: "retrieval"
├── currentStep: "07"
└── status: "in-progress"

Steps 7-9 (Complete):
├── stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
├── phase: "operations"
├── currentStep: "10"
└── status: "in-progress"

Step 10 (Complete, approved):
├── stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
├── techLeadApproval: true
├── phase: "review"
├── currentStep: "11"
└── status: "in-progress"

Steps 11-13 (Complete):
├── stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
├── phase: "handoff"
├── status: "complete"
├── completedAt: "2026-01-07 15:30"
└── currentStep: "13"
```

---

## Component Interactions

### Agent Coordination

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT HANDOFF PATTERN                    │
└─────────────────────────────────────────────────────────────┘

Agent N (Current Step)
├── Read step file completely
├── Load agent persona from agents/ folder
├── Accept input from previous agent:
│   └── {previous_step_output_file}
├── Execute step:
│   ├── Follow numbered instructions
│   ├── Query Knowledge MCP at decision points
│   ├── Query sidecar.yaml for accumulated context
│   └── Generate step-specific outputs
├── Update sidecar.yaml:
│   └── stepsCompleted += [current_step_num]
├── Create output files:
│   ├── {step_name}-output.md
│   ├── {step_name}-stories.md (if generating stories)
│   └── Any supporting files
├── Signal to next agent:
│   └── "{step_name}_complete" flag in sidecar
└── STOP - Wait for next step instruction

Agent N+1 (Next Step)
├── Read {step_name_current}-output.md
├── Load own agent persona
├── Query sidecar.yaml for context and decisions
├── Adapt behavior based on accumulated context
└── Execute own step
```

### File Handoff Pattern

```
Step 1 Outputs:
├── requirements.md
└── sidecar.yaml (updated with step 1 metadata)
        │
        ▼
Step 2A Input:
├── requirements.md (read from output folder)
├── sidecar.yaml (read for context)
└── agent persona (from agents/fti-architect.md)
        │
Step 2A Outputs:
├── architecture-decision.md
└── sidecar.yaml (updated with architecture decisions)
        │
        ▼
Step 2B Input:
├── architecture-decision.md (read from output folder)
├── requirements.md (read from output folder)
├── sidecar.yaml (read for decisions)
└── agent persona (from agents/fti-architect.md)
        │
Step 2B Outputs:
├── tech-stack.md
└── sidecar.yaml (updated with tech stack + branching info)
        │
        ▼
Steps 3-9 Input:
├── All previous output files (conditional read)
├── sidecar.yaml (read for accumulated context)
├── Agent persona (specific to current step)
└── Knowledge MCP (dynamic queries based on sidecar values)
        │
        ├─────────────────────────────────────┐
        │                                     │
        ▼                                     ▼
Step 10 (Tech Lead):                Step 11-13:
├── Read ALL previous outputs       ├── Read ALL validated outputs
├── Cross-validate consistency      ├── Transform to BMM stories
└── GO/REVISE decision              ├── Create roadmap
                                    └── Generate final deliverables
```

### Context Management

#### Context Accumulation (Steps 1-10)

```
Step 1: requirements.md
├── Problem domain
├── Stakeholders
├── Success metrics
└── Constraints

Step 2A: + architecture-decision.md
├── Build vs Buy decision
├── RAG vs Fine-tuning decision
├── Architectural trade-offs
└── Conditional path selected

Step 2B: + tech-stack.md
├── Vector database choice
├── Embedding model choice
├── Framework choices
└── Deployment constraints

Step 3A: + data-requirements.md
├── Data availability
├── Data format
├── Quality requirements
└── Scale estimates

Step 3B: + data-pipeline.md
├── Ingestion strategy
├── Quality checks
├── Monitoring points
└── Processing approach

Step 4: + embeddings-strategy.md
├── Chunking strategy
├── Embedding model details
├── Vector DB configuration
└── Metadata handling

Step 5 (conditional): + fine-tuning-config.md
├── Fine-tuning approach
├── Training data specs
├── Hyperparameters
└── Resource requirements

Step 6: + rag-design.md
├── Retrieval strategy
├── Reranking approach
├── Context assembly
└── Integration points

Step 7: + prompt-design.md
├── System prompt
├── User templates
├── Few-shot examples
└── Versioning strategy

Step 8: + evaluation-framework.md
├── Success metrics
├── Benchmark dataset
├── Evaluation approach
└── Threshold criteria

Step 9: + operations-plan.md
├── Monitoring architecture
├── Alert configuration
├── Drift detection
└── Incident response

Step 10: validation-report.md
├── Cross-step validation
├── Consistency checks
├── Conflict detection
└── GO/REVISE decision
```

#### Context Clearing Between Steps

```
Recommended clearing points (to manage token context):

1. After Step 2B
   - Keep: sidecar.yaml, requirements.md, architecture-decision.md
   - Clear: Business analyst persona details
   - Reason: Move from discovery to technical phases

2. After Step 3B
   - Keep: Data requirements and pipeline designs
   - Clear: General architecture discussion context
   - Reason: Move to specialized technical domains

3. Optional: Between Steps 4-6
   - If context is large, clear non-embeddings discussion
   - Keep: embeddings-strategy.md and relevant architecture
   - Reason: Focus on RAG/Fine-tuning specializations
```

---

## Data Flow

### Complete System Data Flow Diagram

```
┌─────────────────┐
│ USER INPUT      │
│ (Project Desc)  │
└────────┬────────┘
         │
         ▼
    ┌────────────────────────┐
    │ STEP 1: BUSINESS       │
    │ ANALYST                │
    │                        │
    │ Input: Project desc    │
    │ Output:                │
    │ - requirements.md      │
    │ - sidecar.yaml         │
    └────────┬───────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ STEP 2A: FTI ARCHITECT │
    │ (Architecture Decision)│
    │                        │
    │ Input:                 │
    │ - requirements.md      │
    │                        │
    │ Knowledge MCP Queries: │
    │ - get_decisions        │
    │ - get_patterns         │
    │ - get_warnings         │
    │ - get_methodologies    │
    │                        │
    │ Output:                │
    │ - architecture-        │
    │   decision.md          │
    │ - sidecar.yaml         │
    └────────┬───────────────┘
             │
             ├─── CRITICAL BRANCH ───┐
             │                       │
        RAG-Only     Fine-Tuning    Hybrid
             │            │          │
             ▼            ▼          ▼
    ┌────────────────────────┐
    │ STEP 2B: FTI ARCHITECT │
    │ (Tech Stack)           │
    │                        │
    │ Conditional Queries:   │
    │ - Vector DB decision   │
    │ - Embedding model      │
    │ - Framework selection  │
    │ - Stack pitfalls       │
    │                        │
    │ Output:                │
    │ - tech-stack.md        │
    │ - sidecar.yaml         │
    └────────┬───────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ STEP 3A: DATA          │
    │ ENGINEER               │
    │ (Data Requirements)    │
    │                        │
    │ Knowledge MCP Queries: │
    │ - Data patterns        │
    │ - Quality issues       │
    │ - Source evaluation    │
    │                        │
    │ Output:                │
    │ - data-requirements.md │
    │ - sidecar.yaml         │
    └────────┬───────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ STEP 3B: DATA          │
    │ ENGINEER               │
    │ (Data Pipeline)        │
    │                        │
    │ Knowledge MCP Queries: │
    │ - Pipeline patterns    │
    │ - Processing methods   │
    │ - Pipeline pitfalls    │
    │                        │
    │ Output:                │
    │ - data-pipeline.md     │
    │ - sidecar.yaml         │
    └────────┬───────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ STEP 4: EMBEDDINGS     │
    │ ENGINEER               │
    │                        │
    │ Knowledge MCP Queries: │
    │ - Embedding selection  │
    │ - Chunking patterns    │
    │ - Embedding pitfalls   │
    │ - Vector DB setup      │
    │                        │
    │ Output:                │
    │ - embeddings-          │
    │   strategy.md          │
    │ - sidecar.yaml         │
    └────────┬───────────────┘
             │
             ├──── CONDITIONAL ────┐
             │    (based on 2A)    │
             │                     │
        RAG-Only/Hybrid        Fine-Tuning
             │                     │
             │                     ▼
             │            ┌────────────────────────┐
             │            │ STEP 5: FINE-TUNING    │
             │            │ SPECIALIST             │
             │            │ (Only if needed)       │
             │            │                        │
             │            │ Knowledge MCP Queries: │
             │            │ - SFT vs DPO           │
             │            │ - Data prep patterns   │
             │            │ - FT pitfalls          │
             │            │ - FT workflows         │
             │            │                        │
             │            │ Output:                │
             │            │ - fine-tuning-         │
             │            │   config.md            │
             │            │ - sidecar.yaml         │
             │            └────────┬───────────────┘
             │                     │
             └─────────┬───────────┘
                       │
                       ▼
            ┌────────────────────────┐
            │ STEP 6: RAG SPECIALIST │
            │                        │
            │ Knowledge MCP Queries: │
            │ - RAG architectures    │
            │ - Retrieval strategies │
            │ - RAG pitfalls         │
            │ - Context optimization │
            │                        │
            │ Output:                │
            │ - rag-design.md        │
            │ - sidecar.yaml         │
            └────────┬───────────────┘
                     │
                     ▼
            ┌────────────────────────┐
            │ STEP 7: PROMPT         │
            │ ENGINEER               │
            │                        │
            │ Knowledge MCP Queries: │
            │ - System prompts       │
            │ - Few-shot patterns    │
            │ - Prompt pitfalls      │
            │ - Design processes     │
            │                        │
            │ Output:                │
            │ - prompt-design.md     │
            │ - sidecar.yaml         │
            └────────┬───────────────┘
                     │
                     ▼
            ┌────────────────────────┐
            │ STEP 8: LLM EVALUATOR  │
            │                        │
            │ Knowledge MCP Queries: │
            │ - Metric selection     │
            │ - Eval frameworks      │
            │ - Eval pitfalls        │
            │ - Benchmark design     │
            │                        │
            │ Output:                │
            │ - evaluation-          │
            │   framework.md         │
            │ - sidecar.yaml         │
            └────────┬───────────────┘
                     │
                     ▼
            ┌────────────────────────┐
            │ STEP 9: MLOPS ENGINEER │
            │                        │
            │ Knowledge MCP Queries: │
            │ - Monitoring patterns  │
            │ - Alert strategies     │
            │ - Prod ML pitfalls     │
            │ - Drift detection      │
            │                        │
            │ Output:                │
            │ - operations-plan.md   │
            │ - sidecar.yaml         │
            └────────┬───────────────┘
                     │
                     ▼
            ┌────────────────────────┐
            │ STEP 10: TECH LEAD     │
            │ (Validation)           │
            │                        │
            │ Validation Process:    │
            │ - Read all outputs     │
            │ - Check consistency    │
            │ - Detect conflicts     │
            │ - Generate validation  │
            │   report               │
            │                        │
            │ Output:                │
            │ - validation-report.md │
            │ - sidecar.yaml         │
            │ - GO/REVISE decision   │
            └────────┬───────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
      REVISE (rare)          GO
          │                     │
    (back to specific          ▼
     step for rework)   ┌────────────────────────┐
                        │ STEP 11: STORY         │
                        │ ELABORATION            │
                        │                        │
                        │ Transform to:          │
                        │ - BMM format           │
                        │ - User stories         │
                        │ - Acceptance criteria  │
                        │ - Task breakdowns      │
                        │                        │
                        │ Output:                │
                        │ - stories.md           │
                        │ - tasks.md             │
                        │ - sidecar.yaml         │
                        └────────┬───────────────┘
                                 │
                                 ▼
                        ┌────────────────────────┐
                        │ STEP 12: STORY         │
                        │ SEQUENCING             │
                        │                        │
                        │ Organize stories by:   │
                        │ - Phase                │
                        │ - Dependencies         │
                        │ - Sprint allocation    │
                        │                        │
                        │ Output:                │
                        │ - roadmap.md           │
                        │ - sprint-plan.md       │
                        │ - sidecar.yaml         │
                        └────────┬───────────────┘
                                 │
                                 ▼
                        ┌────────────────────────┐
                        │ STEP 13: HANDOFF       │
                        │                        │
                        │ Deliver:               │
                        │ - All design docs      │
                        │ - Implementation guide │
                        │ - Story backlog        │
                        │ - Project archive      │
                        │                        │
                        │ Output:                │
                        │ - implementation-      │
                        │   guide.md             │
                        │ - deliverables/        │
                        │ - sidecar.yaml         │
                        │   (status=complete)    │
                        └────────────────────────┘
```

### Context Flow in sidecar.yaml

```yaml
# Initial state (Step 1 complete)
phase: "discovery"
stepsCompleted: [1]
decisions: {}

# After Step 2A (Critical decision point)
phase: "architecture-1"
stepsCompleted: [1, 2]
decisions:
  build_vs_buy: "buy"
  rag_vs_finetuning: "rag"
  architecture_type: "rag-only"

# After Step 2B (Tech stack selected, path confirmed)
phase: "architecture-2"
stepsCompleted: [1, 2, 3]
decisions:
  # ... same as above, plus:
techStack:
  vectorDatabase: "qdrant"
  embeddingModel: "all-MiniLM-L6-v2"
  framework: "llamaindex"
conditionalPath: "rag-only"

# After Steps 3-9 (All technical specialists complete)
phase: "operations"
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
decisions: {...}
techStack: {...}
outputs:
  dataRequirements: "data-requirements.md"
  dataPipeline: "data-pipeline.md"
  embeddingsStrategy: "embeddings-strategy.md"
  ragDesign: "rag-design.md"
  promptDesign: "prompt-design.md"
  evaluationFramework: "evaluation-framework.md"
  operationsPlan: "operations-plan.md"

# After Step 10 (Tech Lead approval)
phase: "review"
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
techLeadApproval: true
approvalDate: "2026-01-07"
revisionsRequired: []

# After Steps 11-13 (Handoff complete)
phase: "handoff"
status: "complete"
completedAt: "2026-01-07 16:45"
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
deliverables:
  - "implementation-guide.md"
  - "stories/"
  - "roadmap.md"
```

---

## Summary

The AI Engineering Workflow is a comprehensive, 13-step process that:

1. **Gathers requirements** through discovery (Step 1)
2. **Makes critical architecture decisions** with knowledge grounding (Steps 2A-2B)
3. **Designs technical implementation** through specialized agents (Steps 3-9)
4. **Validates consistency** and resolves conflicts (Step 10)
5. **Transforms outputs** to implementation-ready format (Steps 11-13)

The workflow uses **conditional routing** based on architecture decisions to skip unnecessary steps, **Knowledge MCP integration** to ground decisions in best practices, and **state management** via sidecar.yaml to track progress and context.

This architecture ensures that complex AI engineering projects are designed systematically, with all decisions documented, validated, and grounded in established methodologies before implementation begins.
