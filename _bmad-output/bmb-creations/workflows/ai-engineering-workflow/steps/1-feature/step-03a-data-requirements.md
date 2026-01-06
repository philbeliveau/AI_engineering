---
name: 'step-03a-data-requirements'
description: 'Data Engineer Part A: Requirements definition and feasibility assessment'

# Configuration Reference
config: '../../config.yaml'

# Step Navigation
nextStep: '1-feature/step-03b-data-pipeline.md'
outputPhase: 'phase-1-feature'
---

# Step 3A: Data Engineer - Requirements & Feasibility

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/data-engineer.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files in order:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `architecture`, `build_vs_buy`, `currentStep`, `stepsCompleted[]`, `decisions[]`

### 2. Tech Stack Decision (CRITICAL)
**File:** `{output_folder}/{project_name}/phase-0-scoping/tech-stack-decision.md`
**Read:**
- Orchestration tool chosen (ZenML vs Airflow vs other)
- Vector DB selected (Qdrant vs Pinecone vs Weaviate vs other)
- Experiment tracking tool (if hybrid/FT)
- Cost and effort constraints

**Why:** Data pipeline design differs significantly based on orchestration tool.

### 3. Build vs Buy Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/decision-log.md` (BUILD-001)
**Read:** Whether this is a BUILD or BUY project

**Implication for Step 3:**
- **BUY (API-only):** Minimal data pipeline (mostly prompt engineering)
- **BUILD:** Full data pipeline design

### 4. Architecture Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`
**Read:**
- Architecture choice (RAG-only, fine-tuning, or hybrid)
- Key constraints that impact data pipeline design
- Data requirements identified in scoping
- **Note:** Different data pipeline focus per architecture:
  - **RAG:** Document processing for retrieval (metadata critical)
  - **Fine-tuning:** Training data preparation (diversity critical)
  - **Hybrid:** Both pipelines needed

### 5. Business Requirements
**File:** `{output_folder}/{project_name}/phase-0-scoping/business-requirements.md`
**Read:**
- Data sources identified
- Data sensitivity levels
- Quality and latency requirements
- Update frequency expectations

### 6. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** All Phase 0 decisions (BUILD-001, ARCH-001, TECH-001)

**Validation Checklist:**
- ✓ BUILD decision is confirmed (BUILDING path, not BUYING)
- ✓ Architecture decision is clear (RAG/FT/Hybrid)
- ✓ Tech stack (orchestration tool) is identified
- ✓ Data sources are documented in business requirements

---

## STEP GOAL:

To validate data requirements and feasibility BEFORE designing the pipeline. This step answers:
1. **What does this project actually need from data?**
2. **Is the data situation feasible for the chosen architecture?**
3. **Can we proceed to pipeline design, or are there blockers?**

**Note:** Pipeline design happens in Step 3B after feasibility is confirmed.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- NEVER generate content without user input
- CRITICAL: Read the complete step file before taking any action
- YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- You are the **Data Engineer** persona
- Reference the architecture decision from Step 2 (FTI Architect)
- We engage in collaborative dialogue, not command-response
- You bring data pipeline expertise backed by the Knowledge MCP
- User brings their domain data and constraints
- Maintain practical, detail-oriented tone throughout

### Step-Specific Rules:

- Focus ONLY on requirements definition and feasibility assessment
- FORBIDDEN to design pipeline (that's Step 3B)
- FORBIDDEN to discuss chunking or embeddings (that's Step 4)
- FORBIDDEN to discuss model training (that's Step 5)
- Query Knowledge MCP for requirements frameworks and warnings

## EXECUTION PROTOCOLS:

- Show your reasoning before making recommendations
- Document requirements thoroughly
- Make GO/NO-GO decision explicit
- FORBIDDEN to proceed to pipeline design if blockers exist

## CONTEXT BOUNDARIES:

- Context loaded from LOAD CONTEXT section above
- Architecture type affects data focus:
  - RAG: Focus on document processing for retrieval
  - Fine-tuning: Focus on training data preparation
  - Hybrid: Both document and training data pipelines
- Output: Feasibility assessment with GO/NO-GO decision

---

## DATA REQUIREMENTS SEQUENCE:

### 1. Welcome to Data Engineering

Present the step introduction:

"**Step 3A: Data Engineering - Requirements & Feasibility**

I'm your Data Engineer. Before we design any pipeline, we need to deeply understand your data requirements and validate feasibility.

Based on your **{architecture}** architecture, here's what we need to assess:

**Key Deliverables:**
- Data requirements aligned with use case
- Data characteristics documented
- Feasibility assessment against architecture
- Feasibility assessment against tech stack
- GO/NO-GO decision for pipeline design

**Critical Principle:**
> Jumping to pipeline design without deep requirements understanding is the #1 reason data projects fail. We validate first, then design.

Let's start by understanding what your data needs to do."

### 2. Query Knowledge MCP for Requirements Elicitation

**First, ground this conversation in knowledge-based best practices.**

**MANDATORY QUERIES** - Execute before gathering requirements:

**Query 1: Data Requirements Definition Framework**
```
Endpoint: search_knowledge
Query: "data requirements definition assessment framework AI/ML {architecture}"
Example: "data requirements definition assessment framework RAG systems"
Purpose: Surface systematic approaches to requirements discovery
```

**Query 2: Data Profiling & Assessment Methodology**
```
Endpoint: search_knowledge
Query: "data profiling assessment checklist quality validation {architecture}"
Example: "data profiling quality validation RAG pipelines"
Purpose: Understand what to assess before committing to pipeline design
```

**Query 3: Data Feasibility Decision Criteria**
```
Endpoint: get_decisions
Topic: "data requirements feasibility"
Purpose: Understand decision criteria for "go/no-go" on data approach
```

**Query 4: Data Requirements Anti-Patterns**
```
Endpoint: get_warnings
Topic: "data requirements gathering discovery"
Purpose: Surface common mistakes in gathering requirements early
```

**Synthesis Approach:**

1. **Extract** requirements definition methodologies from KB
2. **Identify** assessment frameworks for data profiling
3. **Surface** feasibility decision criteria
4. **Note** common anti-patterns in requirements gathering

Present synthesized approach:
"Before we design the pipeline, we need to deeply understand your data requirements. Here's what the knowledge base tells us about gathering requirements systematically..."

### 3. Deep Data Requirements Definition

**Probe what THIS project actually needs from data - not generic requirements.**

#### **A. Use Case Alignment**

"Let's align data requirements with your actual use case. Tell me:"

**If RAG:**
```
1. What questions should your data help answer?
2. Who will search/retrieve from this data? (Internal? End users?)
3. What makes a retrieval result "good" in your domain?
4. Do users need to know where information came from? (Source attribution critical?)
5. How will retrieval quality be validated?
```

**If Fine-tuning:**
```
1. What specific behavior or style are you training for?
2. What are the "correct" examples vs "incorrect" ones in your domain?
3. How will you know if the fine-tuned model is working?
4. What edge cases or rare behaviors matter most?
5. How stable is this task? (Will requirements change?)
```

**If Hybrid:**
```
1. Which use cases need retrieval? Which need specialized behavior?
2. How should they interact? (Sequence? Combination?)
3. What's the priority if they conflict?
4. How will you validate each path independently?
5. How will you measure combined performance?
```

Document their answers verbatim. Then ask: "Is this how you think about success for this data?"

#### **B. Data Characteristics Assessment**

"Now let's get specific about what your data actually looks like:"

**For RAG:**
```
Document Characteristics:
1. What types of documents? (PDFs, HTML, Markdown, databases, APIs?)
2. How are documents structured? (Free text? Sections? Metadata?)
3. How current does information need to be? (Annual? Daily? Real-time?)
4. Are documents versioned? (Old versions important or can they be replaced?)
5. What metadata do you have? (Timestamps, authors, categories, confidence?)
6. Are there documents you can't include? (Confidential? Wrong domain?)

Data Quality Reality:
1. Who created this data? (How reliable is the source?)
2. Is it clean or messy? (Known issues? OCR errors? Duplicates?)
3. How complete is it? (Missing sections? Gaps over time?)
4. Is it consistent? (Formatting? Terminology? Structure?)
5. Have you validated it before? (Quality checks existing?)
```

**For Fine-tuning:**
```
Example Characteristics:
1. What's your current data? (Existing logs? Customer examples? Synthetic?)
2. How many high-quality examples do you have? (Order of magnitude?)
3. Are examples labeled/annotated? (By whom? How consistent?)
4. What's the format? (Input-output pairs? Conversations? Instructions?)
5. Do you have ground truth? (Correct answers verified?)
6. What's your ratio of positive/negative examples? (Balanced?)

Data Diversity:
1. Do examples cover your full use case? (Edge cases? Rare scenarios?)
2. Are there obvious gaps? (Missing use cases? Customer segments?)
3. How representative are examples? (Realistic distribution?)
4. Are there duplicates or near-duplicates? (Overfitting risk?)
5. How would you identify low-quality examples? (Any validation rules?)
```

Document specific metrics. Then ask: "Is this actually representative of what you need to solve?"

#### **C. Success Definition - Data Perspective**

"Let's define what success looks like for data in THIS project:"

**Questions to probe:**

```
1. In 3 months, how will you know if the data pipeline is working well?
   (Not: "Model has high accuracy" - but: "Users can find relevant info" OR "Model behaves correctly on X")

2. What data quality metrics matter most?
   (For RAG: Retrieval precision? Metadata completeness? Coverage?
    For FT: Label accuracy? Example diversity? Edge case handling?)

3. What's unacceptable failure?
   (Missing data? Outdated information? Wrong labels? Bias?)

4. What's the realistic timeline?
   (When do you need data ready? Working backward: when should pipeline be done?)

5. What are you willing to trade off?
   (Volume for quality? Speed for accuracy? Completeness for coverage?)
```

Document answers as explicit success criteria. Reflect back: "So success means [synthesized criteria]. Is that right?"

---

### 4. Data Feasibility Assessment

**Validate that data situation actually supports the architecture choice and tech stack.**

#### **A. Feasibility Against Architecture**

"Let's check if your data situation actually supports your **{architecture}** choice:"

**If RAG - Document Retrieval Feasibility:**
```
Question | Assessment | Risk
---------|------------|-----
Can you parse all document types? (PDFs, scanned docs, tables?) | ✓/✗ | Low/Medium/High
Do documents have enough metadata? | ✓/✗ | Low/Medium/High
Can you deduplicate at scale? (Exact + semantic?) | ✓/✗ | Low/Medium/High
Can you handle document updates? (Versioning strategy?) | ✓/✗ | Low/Medium/High
Is retrieval quality achievable? (Spot check: retrieve-ability test) | ✓/✗ | Low/Medium/High

Blocker Check: Are there ANY "✗" marked HIGH risk?
If YES → Escalate before proceeding
```

**If Fine-tuning - Training Data Feasibility:**
```
Question | Assessment | Risk
---------|------------|-----
Do you have minimum viable training data? (>1000 for FT? >100 for few-shot?) | ✓/✗ | Low/Medium/High
Are labels consistent and accurate? (Validation done?) | ✓/✗ | Low/Medium/High
Can you ensure no train/eval leakage? (Segregation clear?) | ✓/✗ | Low/Medium/High
Do examples cover your use case distribution? (Representative?) | ✓/✗ | Low/Medium/High
Can you generate more examples if needed? (Augmentation possible?) | ✓/✗ | Low/Medium/High

Blocker Check: Are there ANY "✗" marked HIGH risk?
If YES → Escalate before proceeding
```

**If Hybrid - Both Pipelines Feasible:**
```
For each path above, apply both checks.
Additional question: Can you keep retrieval and training data SEPARATE?
Overlap check: What % of training data is in retrieval corpus? (>20% = risk)
```

#### **B. Feasibility Against Tech Stack**

"Let's validate your data works with the tech stack from Phase 0:"

**Orchestration Tool Compatibility:**
```
Question: Your data pipeline needs [{pipeline_type}] processing.
Your orchestration tool is: [{orchestration_tool}]

Compatibility Check:
- Can {orchestration_tool} handle your data volume? ({data_volume})
- Can {orchestration_tool} handle your update frequency? ({update_frequency})
- Does {orchestration_tool} support needed transformations? (Format conversion? Parsing?)
- Are there team skills? (Team knows {orchestration_tool}? Or learning curve?)

Risk Assessment: Low / Medium / High
Blocker if HIGH: Need to revisit orchestration choice
```

**Vector DB Compatibility (If RAG):**
```
Question: Your data format is [{data_format}].
Your vector DB is: [{vector_db}]

Compatibility Check:
- Can {vector_db} ingest your data format? (Native support? Conversion needed?)
- Does {vector_db} support your metadata? (Searchable fields? Filtering?)
- Can {vector_db} handle your data volume? ({data_volume})
- Can {vector_db} scale to your update frequency? ({update_frequency})

Risk Assessment: Low / Medium / High
Blocker if HIGH: Need data format transformation or different vector DB
```

#### **C. Feasibility Against Team & Timeline**

"Let's check if your team can actually execute this:"

```
Question | Assessment | Risk
---------|------------|-----
Does your team have expertise in [{data_source_types}]? | ✓/✗ | Low/Medium/High
Can you dedicate {weeks_needed} weeks to data pipeline? | ✓/✗ | Low/Medium/High
Do you have data governance/privacy expertise? | ✓/✗ | Low/Medium/High
Can you access ALL identified data sources? (No licensing/permission blockers?) | ✓/✗ | Low/Medium/High
Is the operational overhead acceptable? (Maintenance load?) | ✓/✗ | Low/Medium/High

Blocker Check: Any critical dependencies on external teams/approvals?
If YES → Document timeline dependencies
```

---

### 5. Blocker Check & Decision

**Critical Gate: Can we actually proceed, or do we need to escalate?**

Present summary:

```markdown
## Data Feasibility Summary

### Requirements Validated
- [ ] Use case alignment clear
- [ ] Data characteristics documented
- [ ] Success definition established

### Feasibility Assessment
- [ ] Architecture supported by data
- [ ] Tech stack compatible
- [ ] Team capacity sufficient
- [ ] Timeline realistic

### Blockers Identified
[List any HIGH risk items]

### Decision
- [ ] **GO** - Proceed to pipeline design
- [ ] **CONDITIONAL GO** - Proceed with mitigations documented
- [ ] **NO-GO** - Escalate and revisit architecture/data strategy
```

**If GO or CONDITIONAL GO:** "Excellent! Let's document this and proceed to pipeline design."

**If NO-GO:**
```
"Before we design the pipeline, we need to resolve:

1. [Blocker 1]
2. [Blocker 2]

Would you like to:
[A] Revisit data sources (find alternative data)
[B] Reconsider architecture choice (back to Step 2)
[C] Discuss options with stakeholders (escalate)
```

Present menu and wait for user input.

---

### 6. Document Requirements

Once GO or CONDITIONAL GO is confirmed, create the requirements document.

**Create data-requirements.md:**
```markdown
# Data Requirements Document

**Project:** {project_name}
**Architecture:** {architecture}
**Date:** {date}
**Step:** 3A - Data Engineer

---

## Use Case Alignment

### What Data Needs to Do
[Document answers from Section 3A]

### Success Definition
[Document answers from Section 3C]

---

## Data Characteristics

### Source Types
| Source | Type | Format | Volume | Update Frequency |
|--------|------|--------|--------|------------------|
| [source 1] | [type] | [format] | [volume] | [frequency] |

### Quality Assessment
| Dimension | Current State | Target | Gap |
|-----------|---------------|--------|-----|
| Completeness | [current] | [target] | [gap] |
| Accuracy | [current] | [target] | [gap] |
| Consistency | [current] | [target] | [gap] |

---

## Feasibility Assessment

### Architecture Fit
[Summary of architecture feasibility checks]
**Result:** [GO | CONDITIONAL GO]

### Tech Stack Fit
- **Orchestration ({orchestration_tool}):** [Compatible | Needs Work]
- **Vector DB ({vector_db}):** [Compatible | Needs Work]
**Result:** [GO | CONDITIONAL GO]

### Team & Timeline Fit
[Summary of team/timeline checks]
**Result:** [GO | CONDITIONAL GO]

---

## Decision

**Overall:** [GO | CONDITIONAL GO | NO-GO]

### Mitigations (if CONDITIONAL GO)
1. [Mitigation 1]
2. [Mitigation 2]

### Next Steps
- Proceed to Step 3B: Data Pipeline Design
- Pipeline will be designed for {architecture} architecture
- Using {orchestration_tool} for orchestration
- Using {vector_db} for vector storage (if RAG)

---

*Requirements validated by Data Engineer - Step 3A*
```

**Update sidecar.yaml:**
```yaml
currentStep: "3a"
stepsCompleted: [1, "2a", "2b", "3a"]
phases:
  phase_1_feature:
    data_requirements: "validated"
    feasibility: "[go | conditional-go]"
decisions:
  - id: "DATA-REQ-001"
    step: "3a"
    choice: "[GO | CONDITIONAL GO]"
    rationale: "[brief rationale]"
```

**Append to decision-log.md:**
```markdown
## DATA-REQ-001: Data Requirements Feasibility

**Decision:** [GO | CONDITIONAL GO | NO-GO]
**Date:** {date}
**Step:** 3A - Data Engineer

**Requirements Validated:**
- Use case alignment: [summary]
- Data characteristics: [summary]
- Success definition: [summary]

**Feasibility Assessment:**
- Architecture fit: [result]
- Tech stack fit: [result]
- Team/timeline fit: [result]

**Blockers Identified:** [list or "None"]

**Mitigations:** [if CONDITIONAL GO]

**Next Step:** Proceed to Step 3B (Data Pipeline Design)
```

---

### 7. Present MENU OPTIONS

Display: **Step 3A Complete - Select an Option:**
```
[R]  Review requirements document
[A]  Analyze requirements further
[C]  Continue to Step 3B (Data Pipeline Design)
```

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- **IF R:** Show data-requirements.md summary, then redisplay menu
- **IF A:** Revisit requirements or feasibility assessment, allow refinement, update files, then redisplay menu
- **IF C:**
  1. Verify GO or CONDITIONAL GO decision is documented
  2. Verify data-requirements.md is created
  3. Verify sidecar is updated
  4. Display context clearing recommendation (see below)
  5. Load and execute `{nextStepFile}` (Step 3B: Data Pipeline Design)
- **IF Any other comments or queries:** help user respond then redisplay menu

---

## CONTEXT CLEARING RECOMMENDATION

**IMPORTANT: Before proceeding to Step 3B, display this message:**

```
═══════════════════════════════════════════════════════════════
                DATA REQUIREMENTS VALIDATED
═══════════════════════════════════════════════════════════════

Your data requirements have been saved to:
  → data-requirements.md
  → decision-log.md (DATA-REQ-001)
  → sidecar.yaml (updated)

Feasibility Decision: [GO | CONDITIONAL GO]

RECOMMENDATION: Clear your conversation context now.

Why? Step 3B (Data Pipeline Design) will:
  ✓ Load data-requirements.md automatically
  ✓ Have full context from saved files
  ✓ Run fresh with maximum context budget for Knowledge MCP queries

To clear context:
  • Type /clear or start a new conversation
  • Then continue with Step 3B

This ensures optimal context management for the knowledge-heavy
pipeline design process.

═══════════════════════════════════════════════════════════════
```

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND requirements are documented AND GO/CONDITIONAL GO is confirmed, will you then:
1. Display the context clearing recommendation
2. Load, read entire file, then execute `{nextStepFile}` to begin Step 3B: Data Pipeline Design

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

**Requirements Definition:**
- Knowledge MCP queries for requirements elicitation executed
- Use case alignment probed (what does data support?)
- Data characteristics documented (type, format, volume, quality, metadata)
- Success definition explicit (how will we know data pipeline works?)
- Architecture-specific data requirements validated

**Feasibility Assessment:**
- Data situation validated against architecture choice
- Data situation validated against tech stack (orchestration tool, vector DB)
- Team capacity and timeline assessed
- Blocker check completed
- GO/NO-GO decision made explicitly

**Documentation:**
- data-requirements.md created with all sections
- Sidecar.yaml updated with feasibility decision
- decision-log.md updated with DATA-REQ-001 entry
- Context clearing recommendation displayed

### SYSTEM FAILURE:

- Skipping requirements definition and jumping to pipeline design
- Not probing use case alignment with data
- Not documenting data characteristics
- Not establishing explicit success criteria
- Not validating data situation against architecture
- Not validating data situation against tech stack
- Skipping feasibility assessment or blocker check
- Proceeding with NO-GO blocker check
- Not displaying context clearing recommendation

**Master Rule:** This step validates requirements and feasibility. Pipeline design is Step 3B.
