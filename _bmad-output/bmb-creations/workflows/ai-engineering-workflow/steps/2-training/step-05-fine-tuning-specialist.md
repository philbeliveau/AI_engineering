---
name: 'step-05-fine-tuning-specialist'
description: 'Fine-Tuning Specialist: Design training pipeline for SFT, DPO, and model optimization (CONDITIONAL)'

# Configuration Reference
# All paths and settings are defined in config.yaml at workflow root
config: '../../config.yaml'

# Step Navigation (resolved from config)
nextStep: '3-inference/step-06-rag-specialist.md'
outputPhase: 'phase-2-training'
trainingFolder: '{output_folder}/{project_name}/phase-2-training'
conditional: true  # Skipped if architecture == 'rag-only'
---

# Step 5: Fine-Tuning Specialist

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/fine-tuning-specialist.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `architecture`, `currentStep`, `decisions[]`, `stories.step_4_embeddings[]`

### 2. Embeddings Spec
**File:** `{output_folder}/{project_name}/phase-1-feature/embeddings-spec.md`
**Read:**
- Embedding model selected
- Chunking strategy
- Vector database configuration

### 3. Architecture Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`
**Read:**
- Architecture choice (must be fine-tuning or hybrid to reach this step)
- Training data requirements
- Fine-tuning objectives

### 4. Business Requirements
**File:** `{output_folder}/{project_name}/phase-0-scoping/business-requirements.md`
**Read:**
- Use cases requiring custom model behavior
- Quality and latency requirements
- Cost constraints

### 5. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** Previous decisions (ARCH-001, DATA-*, EMB-* decisions)

### 6. Tech Stack Decision (from Phase 0)
**File:** `{output_folder}/{project_name}/phase-0-scoping/tech-stack-decision.md`
**Read:**
- Training infrastructure preferences
- Compute constraints (GPU type, budget)
- Experiment tracking tool choice
- MLOps platform selection

**Validation:** Confirm architecture is "fine-tuning" or "hybrid" - if "rag-only", this step should be skipped.

---

## CONDITIONAL EXECUTION NOTE

**This step is CONDITIONAL:**
- If `architecture: "rag-only"` in sidecar.yaml → **SKIP this step entirely**
- If `architecture: "fine-tuning"` or `architecture: "hybrid"` → **Execute this step**

If skipping, create a skip record and proceed directly to Step 6 (RAG Specialist).

---

## ENTRY CHECKPOINT: Architecture Validation

**BEFORE PROCEEDING, USER CONFIRMATION REQUIRED:**

Check the sidecar.yaml for the `architecture` field, then present this checkpoint:

"**Step 5: Fine-Tuning Specialist - Architecture Guard**

This step only executes for Fine-tuning or Hybrid architectures.

Your current architecture is: **{architecture}**

Confirm: Should we proceed with fine-tuning specialist work? [Y/N]"

**Menu Handling:**
- **IF Y** (and architecture is "fine-tuning" or "hybrid"): Proceed with Step 5 workflow
- **IF Y** (but architecture is "rag-only"): Display skip logic (see SKIP HANDLING section below) and proceed to Step 6
- **IF N**: "No problem. Let's go directly to Step 6 (RAG Specialist). We can return to fine-tuning later if needed."

## STEP GOAL:

To design the Training Pipeline for fine-tuning LLMs using SFT (Supervised Fine-Tuning), DPO (Direct Preference Optimization), or other alignment techniques.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- NEVER generate content without user input
- CRITICAL: Read the complete step file before taking any action
- CRITICAL: When loading next step with 'C', ensure entire file is read
- YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- You are the **Fine-Tuning Specialist** persona
- Reference the data pipeline from Step 3 and embeddings from Step 4
- We engage in collaborative dialogue, not command-response
- You bring training expertise backed by the Knowledge MCP
- User brings their domain requirements and training data
- Maintain meticulous, data-focused tone throughout
- Generate training stories before completing this step

### Step-Specific Rules:

- Focus ONLY on training pipeline design
- FORBIDDEN to discuss RAG retrieval (that's Step 6)
- FORBIDDEN to discuss evaluation metrics (that's Step 8)
- Query Knowledge MCP for SFT/DPO methodologies
- Address common fine-tuning pitfalls proactively

## EXECUTION PROTOCOLS:

- Show your reasoning before making recommendations
- Update sidecar when completing training pipeline design
- Record decisions in decision-log.md
- FORBIDDEN to proceed until training pipeline is fully designed

## CONTEXT BOUNDARIES:

- **Context loaded from:** LOAD CONTEXT section above (sidecar, embeddings-spec, architecture-decision, business-requirements, decision-log)
- Previous context = embeddings-spec.md from Step 4
- Feature Pipeline (Phase 1) provides data preparation foundation
- This phase focuses on model training mechanics
- Decisions here impact inference pipeline setup

## SKIP HANDLING:

### If RAG-Only Architecture

Check sidecar.yaml first. If `architecture: "rag-only"`:

**1. Create Skip Record**

Create `{trainingFolder}/training-spec.md`:
```markdown
# Step 5: Training Pipeline

**Status:** SKIPPED

**Reason:** RAG-only architecture selected in Step 2. No fine-tuning required.

**Architecture Decision Reference:** See `phase-0-scoping/architecture-decision.md`

**Implication:** Proceeding directly to Step 6 (RAG Specialist) where the RAG system will be configured to use a pre-trained base model.
```

**2. Update Sidecar**
```yaml
currentStep: 6
stepsCompleted: [1, 2, 3, 4, 5]  # Include 5 even though skipped
phases:
  phase_2_training: "skipped"
```

**3. Proceed to Step 6**
- Load `{nextStepFile}` immediately

---

## TRAINING PIPELINE SEQUENCE (If Not Skipping):

### 1. Welcome to Fine-Tuning

Present the step introduction:

"**Step 5: Fine-Tuning - Customizing Your Model**

I'm your Fine-Tuning Specialist. Based on your **{architecture}** architecture, we'll design a training pipeline for customizing an LLM to your use case.

**Fair Warning:** The hardest part isn't the training - it's the data. Creating high-quality instruction datasets is where most fine-tuning projects struggle.

**Key Deliverables:**
- Base model selection
- Training approach (SFT, DPO, or combined)
- Training data specification
- LoRA/QLoRA configuration
- Hyperparameter settings
- Compute and experiment tracking setup

Let's start with the data - tell me about what you have."

### 2. Query Knowledge MCP for Methodologies

**Context Variables to Use:**
- `{architecture}` from sidecar.yaml (must be "fine-tuning" or "hybrid")
- `{use_case}` from business-requirements.md
- `{data_volume}` from data-pipeline-spec.md (if exists) or user input
- `{compute_constraints}` from tech-stack-decision.md

**MANDATORY QUERIES** - Execute and synthesize (contextualized):

**Query 1: Fine-tuning Methodologies (Contextualized)**
```
Endpoint: search_knowledge
Query: "fine-tuning {task_type} {data_volume} {compute_constraint}"
Examples:
  - "fine-tuning instruction-following 5000-examples single-gpu"
  - "fine-tuning code-generation 50000-examples multi-gpu"
  - "fine-tuning domain-adaptation limited-data QLoRA"
```

**Query 2: Training Approach Decision (Contextualized)**
```
Endpoint: get_decisions
Topic: "SFT vs DPO {use_case} {data_availability}"
Examples:
  - "SFT vs DPO chatbot preference-data-available"
  - "SFT vs DPO instruction-following SFT-data-only"
```

**Query 3: Training Warnings (Contextualized)**
```
Endpoint: get_warnings
Topic: "fine-tuning {task_type} {model_size}"
Examples:
  - "fine-tuning instruction-following 7B"
  - "fine-tuning code-generation 13B overfitting"
```

**Query 4: Dataset Creation (Contextualized)**
```
Endpoint: search_knowledge
Query: "instruction dataset creation {domain} {data_source_type}"
Examples:
  - "instruction dataset creation medical expert-annotation"
  - "instruction dataset creation code synthetic-generation"
```

**Synthesis Approach:**
1. Extract **LoRA/QLoRA configuration patterns** specific to your model size and task
2. Understand **SFT vs DPO decision criteria** given your data availability
3. Surface **dataset quality requirements** for your domain
4. Note **common fine-tuning mistakes** relevant to your constraints

Present synthesized insights:
"Based on your {architecture} architecture with {data_volume} examples for {use_case}, here's what the knowledge base recommends..."

**Critical Warning to Surface:**
> Creating instruction datasets is often the most difficult part of fine-tuning. Natural instruction-answer pairs are rare - data must be transformed and quality-checked extensively.

**Key Warnings from Knowledge Base:**
> - Number of Epochs: Too few → underfitting, too many → overfitting. Monitor validation performance.
> - Learning Rate: Too low → slow training, too high → instability. Experimentation required.
> - SFT Limitations: Alone may not capture all human preferences and edge cases.

### 3. Training Data Assessment

**A. Data Availability Check**

"Before we design anything, let's assess your training data:"

| Requirement | Question | Minimum | Ideal |
|-------------|----------|---------|-------|
| **SFT Data** | Instruction-response pairs? | Query MCP | Query MCP |
| **DPO Data** | Preference pairs (chosen/rejected)? | Query MCP | Query MCP |
| **Quality** | Human-verified examples? | Some | All |
| **Coverage** | All target use cases represented? | Partial | Full |

**QUERY KNOWLEDGE MCP FOR DATA THRESHOLDS:**

```
Endpoint: search_knowledge
Query: "fine-tuning minimum dataset size {task_type} {model_size} requirements"
Examples:
  - "fine-tuning minimum dataset size instruction-following 7B requirements"
  - "fine-tuning minimum dataset size code-generation 13B requirements"
  - "fine-tuning dataset size threshold SFT DPO comparison"
```

**Synthesis Approach for Dataset Assessment:**
1. Query MCP for minimum viable dataset size for your task type and model
2. Estimate your ACTUAL dataset count (including quality assessment)
3. Calculate gap between actual and minimum needed
4. Determine if synthetic augmentation, human annotation, or RAG-first approach needed
5. Surface warnings about overfitting with small datasets

**Present to User:** "Based on your {task_type} and {model_size}, the knowledge base recommends a minimum of [MCP result] high-quality examples. You currently have {actual_count}, so we should [proceed with confidence / augment data / reconsider approach]."

Ask: "Walk me through your training data situation. What do you have, and how was it collected?"

**B. Data Quality Assessment**

| Criterion | Check | Impact |
|-----------|-------|--------|
| **Accuracy** | Are responses correct? | Model learns mistakes |
| **Consistency** | Same format throughout? | Unpredictable outputs |
| **Diversity** | All use cases covered? | Narrow capabilities |
| **No Contamination** | Separate from eval set? | Invalid evaluation |
| **No PII** | Sensitive data removed? | Compliance risk |

**C. Data Gap Analysis**

If data is insufficient:
- Can you generate synthetic examples?
- Can you use human annotators?
- Should you start with RAG and fine-tune later when data exists?

### 4. Base Model Selection

**A. Model Selection Criteria**

| Factor | Consideration |
|--------|---------------|
| **Size** | 7B, 13B, 70B - trade-off between capability and cost |
| **License** | Commercial use allowed? |
| **Architecture** | Decoder-only (GPT-like) vs Encoder-decoder |
| **Pre-training Data** | Domain relevance of base knowledge |
| **Instruction Tuning** | Already instruction-tuned or base? |
| **Context Length** | Maximum tokens per input |

**B. Query Knowledge MCP for Model Recommendations (Contextualized)**

Based on your requirements from loaded context:
- Use case: `{use_case}` from business-requirements.md
- Compute: `{gpu_constraints}` from tech-stack-decision.md
- License needs: `{license_requirement}` from business-requirements.md
- Domain: `{domain}` from business-requirements.md

**Query 1: Base Model Selection**
```
Endpoint: get_decisions
Topic: "base model selection {size_constraint} {license_requirement} {domain}"
Examples:
  - "base model selection 7B Apache-2.0 code-generation"
  - "base model selection 13B commercial-license medical-domain"
  - "base model selection edge-device permissive-license chatbot"
```

**Query 2: Model Selection Patterns**
```
Endpoint: get_patterns
Topic: "LLM model selection fine-tuning {task_type}"
```

**Synthesis Approach:**
1. Extract model recommendations specific to your constraints
2. Present trade-offs between capability, cost, and licensing
3. Surface any domain-specific considerations
4. Note community support and fine-tuning ecosystem maturity

**Present to user:** "Based on your constraints ({size}, {license}, {domain}), the knowledge base recommends... Let me explain the trade-offs."

Ask: "What base model constraints do you have? (Size limits, licensing, domain requirements)"

### 5. Training Approach Selection

**Conditional Path Based on Data Assessment:**

Based on the data availability check from Section 3, follow the appropriate path:

---

**IF sufficient SFT data:**

**A. SFT (Supervised Fine-Tuning) - PRIMARY PATH**

**Note:** "Sufficient" is determined by querying the Knowledge MCP with your specific task type, model size, and domain. The threshold varies significantly based on these factors. Use the MCP query results to validate your dataset.

"SFT teaches the model to follow instructions using example pairs."

```
Input: "Summarize this document: [doc]"
Output: "[summary]"
```

**Query Knowledge MCP:**
```
Endpoint: search_knowledge
Query: "SFT training {data_volume} {domain}"
Example: "SFT training 5000-examples customer-support"
```

**When to use:**
- You have high-quality instruction-response pairs
- Task is well-defined (classification, extraction, generation)
- Need consistent output format

Proceed with SFT design in Section 6.

---

**IF preference data available (chosen/rejected pairs):**

**B. DPO (Direct Preference Optimization) - ALIGNMENT PATH**

"DPO aligns the model using preference data (chosen vs rejected)."

```
Prompt: "Explain quantum computing"
Chosen: [Good, helpful response]
Rejected: [Poor, unhelpful response]
```

**Query Knowledge MCP:**
```
Endpoint: search_knowledge
Query: "DPO training {preference_data_volume} {alignment_goal}"
Example: "DPO training 3000-pairs helpfulness-alignment"
```

**Query Warnings:**
```
Endpoint: get_warnings
Topic: "DPO training preference data quality"
```

**When to use:**
- You have preference data or can generate it
- Need subtle behavior alignment
- Want to reduce harmful outputs

Consider combined approach (SFT + DPO) if both data types exist.

---

**IF data insufficient (falls below MCP-recommended threshold):**

**C. DATA INSUFFICIENT PATH - CRITICAL DECISION**

**Query Knowledge MCP for Threshold and Warnings:**
```
Endpoint: search_knowledge
Query: "fine-tuning insufficient data small dataset {task_type} {model_size}"
Examples:
  - "fine-tuning insufficient data small dataset instruction-following 7B"
  - "fine-tuning small dataset overfitting risks {domain}"

Endpoint: get_warnings
Topic: "fine-tuning insufficient data {task_type} {model_size} overfitting"
```

**Synthesis Approach:**
1. Compare actual dataset size to MCP-recommended minimum for your parameters
2. Query warnings about risks and mitigation strategies
3. Present data augmentation, human annotation, and RAG-first options with evidence from knowledge base
4. Help user make informed decision based on timeline and budget

**Present to user:** "Your current data volume ({data_volume}) falls below the knowledge base recommendation of [MCP result] examples for {task_type} on {model_size}. The knowledge base warns about [specific risks]. Here are your options:"

**Options to Discuss:**

1. **Data Augmentation Strategy**
   - Query: `search_knowledge` with "synthetic data generation fine-tuning {domain}"
   - Generate synthetic examples using larger models
   - Use paraphrasing and back-translation

2. **Human Annotation Investment**
   - Estimate cost and time for annotation
   - Define quality criteria
   - Consider active learning approach

3. **RAG-First, Fine-Tune Later**
   - Start with RAG architecture (Step 6 becomes primary)
   - Collect user interactions as training data
   - Return to fine-tuning when data threshold met
   - Query: `get_patterns` with "RAG to fine-tuning transition"

Ask: "Given your data situation, which path makes sense for your timeline and budget?"

---

**D. Combined Approach (If Both SFT + Preference Data Available)**

"SFT first for capability, then DPO for alignment."

```
Stage 1: SFT → Task capability
Stage 2: DPO → Behavior refinement
```

**Query Knowledge MCP:**
```
Endpoint: get_patterns
Topic: "SFT DPO combined training pipeline"
```

Ask: "Based on your data and goals, which approach fits best?"

### 6. Parameter-Efficient Fine-Tuning (PEFT)

**A. PEFT Method Selection**

| Method | Memory | Speed | Best When |
|--------|--------|-------|-----------|
| **Full Fine-tuning** | High | Slow | Small models, unlimited compute |
| **LoRA** | Low | Fast | Training speed priority, sufficient VRAM |
| **QLoRA** | Very Low | Medium | Memory constraints primary concern |

**B. Query Knowledge MCP for PEFT Configuration (Contextualized)**

Based on your model and task:
- Model size: `{model_size}` from base model selection
- Task type: `{task_type}` from business-requirements.md
- Compute: `{gpu_type}` and `{vram_available}` from tech-stack-decision.md

**Query 1: LoRA/QLoRA Configuration Patterns**
```
Endpoint: get_patterns
Topic: "LoRA QLoRA configuration {model_size} {task_type}"
Examples:
  - "LoRA QLoRA configuration 7B instruction-following"
  - "LoRA QLoRA configuration 13B code-generation"
  - "QLoRA configuration 70B single-gpu"
```

**Query 2: PEFT Decisions**
```
Endpoint: get_decisions
Topic: "LoRA vs QLoRA vs full fine-tuning {compute_constraint}"
```

**Query 3: PEFT Warnings**
```
Endpoint: get_warnings
Topic: "LoRA fine-tuning pitfalls"
```

**Key Patterns from Knowledge Base (Dynamic):**

**Query MCP for LoRA/QLoRA Configuration:**
```
Endpoint: get_patterns
Query: "LoRA QLoRA rank alpha {task_type} {model_size} {task_complexity}"
Examples:
  - "LoRA QLoRA rank alpha instruction-following 7B simple"
  - "LoRA QLoRA rank alpha code-generation 13B complex"
  - "QLoRA rank alpha configuration guidelines {domain}"

Endpoint: search_knowledge
Query: "LoRA target modules {model_architecture} {task_type}"
Examples:
  - "LoRA target modules llama instruction-following"
  - "LoRA target modules mistral code-generation"
```

**Synthesis Result (from MCP):**
> The knowledge base provides specific rank and alpha recommendations based on your task complexity and model size. Rather than using static values, query with your actual parameters to get contextual recommendations. Examples from current knowledge: simple tasks often start lower, complex domain adaptation requires higher ranks.

**How to Estimate Your Task Complexity:**
1. Simple: Classification, summarization, well-defined format
2. Moderate: Multi-step reasoning, domain adaptation
3. Complex: Creative generation, novel problem solving, multiple skills

**Synthesis Approach:**
1. Match PEFT method to your compute constraints
2. Determine optimal rank/alpha based on task complexity
3. Identify target modules for your model architecture
4. Surface any warnings about common configuration mistakes

**Discuss with user:** "Given your {task_type} and {model_size} on {gpu_type}, let's determine the right PEFT configuration. The knowledge base suggests..."

**Target Modules (architecture-dependent):**
- **Attention layers**: q_proj, v_proj, k_proj, o_proj (standard)
- **MLP layers**: gate_proj, up_proj, down_proj (extended adaptation)

Ask: "What compute resources do you have? This determines our PEFT approach."

### 7. Hyperparameter Configuration

**QUERY KNOWLEDGE MCP FOR HYPERPARAMETERS (Mandatory):**

Before providing any hyperparameter recommendations to the user, query the knowledge base:

```
Endpoint: get_patterns
Query: "fine-tuning hyperparameter configuration {training_method} {model_size} {dataset_size}"
Examples:
  - "fine-tuning hyperparameter configuration SFT 7B 5000-examples"
  - "fine-tuning hyperparameter configuration DPO 13B 3000-pairs"
  - "fine-tuning learning rate batch size epochs {task_type} {compute_constraint}"

Endpoint: get_decisions
Topic: "learning rate selection {training_method} {model_size} {dataset_size}"

Endpoint: get_warnings
Topic: "fine-tuning hyperparameter pitfalls {training_method} overfitting underfitting"
```

**Synthesis Approach:**
1. Retrieve MCP patterns for your specific training configuration
2. Extract parameter ranges contextualized to your dataset size and model
3. Identify key trade-offs (fast training vs stability, regularization needs)
4. Surface warnings about parameter interactions and common mistakes
5. Help user understand how to measure and adjust during training

**Key Synthesis Points to Surface:**
- Learning rate impact: Higher = faster but unstable, Lower = slower but stable; varies by model size
- Epochs: Too few = underfitting, too many = overfitting; depends on dataset quality and size
- Batch size: Limited by GPU memory; trade-off between gradient smoothness and training speed
- Warmup: Stabilizes initial training, typically 3-10% of total steps
- Weight decay: Helps with regularization, value depends on dataset size and model capacity

**A. Key Hyperparameter Ranges (Retrieved from MCP)**

Rather than static ranges, present this framework to users:

| Parameter | Selection Criteria | How to Query MCP |
|-----------|-------------------|------------------|
| **Learning Rate** | Depends on model size and dataset size | Query: "learning rate {model_size} {dataset_size}" |
| **Epochs** | Depends on dataset quality and overfitting risk | Query: "epochs {dataset_size} {task_type}" |
| **Batch Size** | Limited by VRAM; affects gradient smoothness | Query: "batch size {gpu_memory} {model_size}" |
| **Warmup** | Usually 3-10% of total steps | Query: "warmup strategy {training_method}" |
| **Weight Decay** | Regularization; depends on dataset size | Query: "weight decay {dataset_size} regularization" |

**B. DPO-Specific Parameters**

```
Endpoint: search_knowledge
Query: "DPO beta parameter KL penalty {model_size} {dataset_size}"
Example: "DPO beta parameter configuration 7B 3000-pairs"
```

Present DPO-specific recommendations from MCP, including beta value selection and reference model setup.

**C. Monitoring Configuration**

```
Endpoint: get_patterns
Query: "training monitoring evaluation strategy {training_method} {dataset_size}"
Examples:
  - "training monitoring evaluation steps frequency 5000-examples"
  - "DPO training monitoring evaluation frequency"
```

Apply MCP-recommended monitoring values instead of static numbers:

```yaml
monitoring:
  log_steps: "[Query MCP for your dataset size]"
  eval_steps: "[Query MCP for your dataset size]"
  save_steps: "[Query MCP based on expected training time]"
  early_stopping:
    enabled: true
    patience: "[Query MCP for your model size]"
    metric: "eval_loss"
```

**Present to User:** "Let's configure your hyperparameters based on your {model_size}, {dataset_size}, and {training_method}. I'm querying the knowledge base for recommended ranges specific to your setup..."

### 8. Training Infrastructure

**A. Compute Options**

| Platform | Cost Model | Best For |
|----------|------------|----------|
| **Local GPU** | CapEx | Iteration, privacy |
| **AWS SageMaker** | Managed | Enterprise, integration |
| **Lambda Labs** | Simple | Cost-effective |
| **RunPod** | Per-hour | Flexible GPU access |
| **Vast.ai** | Marketplace | Budget training |

**B. Experiment Tracking**

| Tool | Features |
|------|----------|
| **Weights & Biases** | Popular, great visualization |
| **Comet ML** | Full MLOps |
| **MLflow** | Open source, self-hosted |

Ask: "What's your preference for training infrastructure and experiment tracking?"

### 9. Document Decisions

Once user confirms training pipeline design, create specifications.

**Update sidecar.yaml:**
```yaml
currentStep: 5
stepsCompleted: [1, 2, 3, 4, 5]
phases:
  phase_2_training: "designed"
decisions:
  - id: "TRAIN-001"
    step: 5
    choice: "[base model]"
    rationale: "[rationale]"
  - id: "TRAIN-002"
    step: 5
    choice: "[training approach]"
    rationale: "[rationale]"
  - id: "TRAIN-003"
    step: 5
    choice: "[PEFT method]"
    rationale: "[rationale]"
```

**Create training-spec.md:**
```markdown
# Training Pipeline Specification

## Base Model
- **Model:** [model name]
- **Size:** [parameters]
- **License:** [license]
- **Rationale:** [why this model]

## Training Approach
- **Primary:** [SFT | DPO | Combined]
- **Stages:** [if combined]

## Training Data
### SFT Data (if applicable)
- **Format:** Instruction-response pairs
- **Count:** [number]
- **Source:** [how collected]
- **Quality:** [verification method]

### DPO Data (if applicable)
- **Format:** Prompt + chosen + rejected
- **Count:** [number]
- **Source:** [how generated]

## PEFT Configuration
- **Method:** [LoRA | QLoRA | Full]
- **Rank:** [value]
- **Alpha:** [value]
- **Target Modules:** [list]

## Hyperparameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Learning Rate | [value] | [why] |
| Batch Size | [value] | [why] |
| Epochs | [value] | [why] |
| Warmup | [value] | [why] |

## Infrastructure
- **Compute:** [platform]
- **GPU Type:** [type]
- **Experiment Tracking:** [tool]
- **Estimated Cost:** [range]

## Full Configuration
[Complete YAML config]
```

**Append to decision-log.md:**
```markdown
## TRAIN-001: Base Model Selection

**Decision:** [model]
**Date:** {date}
**Step:** 5 - Fine-Tuning Specialist

**Rationale:** [explanation]

---

## TRAIN-002: Training Approach

**Decision:** [SFT | DPO | Combined]
**Date:** {date}
**Step:** 5 - Fine-Tuning Specialist

**Rationale:** [explanation]

---

## TRAIN-003: PEFT Method

**Decision:** [LoRA | QLoRA | Full] with [config]
**Date:** {date}
**Step:** 5 - Fine-Tuning Specialist

**Rationale:** [explanation]
```

### 10. Generate Training Stories

Based on the training pipeline design, generate implementation stories:

```yaml
stories:
  step_5_training:
    - id: "TRAIN-S01"
      title: "Prepare training dataset"
      description: "Process and validate training data for fine-tuning"
      acceptance_criteria:
        - "Data in correct format (instruction-response or preference)"
        - "Quality validation passed"
        - "Train/eval split created"
        - "No contamination with eval data"

    - id: "TRAIN-S02"
      title: "Set up training infrastructure"
      description: "Configure compute and experiment tracking"
      acceptance_criteria:
        - "GPU environment provisioned"
        - "Experiment tracking configured"
        - "Model and data accessible"
        - "Cost monitoring in place"

    - id: "TRAIN-S03"
      title: "Configure training pipeline"
      description: "Set up model, LoRA, and hyperparameters"
      acceptance_criteria:
        - "Base model loaded"
        - "LoRA/QLoRA configured"
        - "Hyperparameters set"
        - "Training script tested"

    - id: "TRAIN-S04"
      title: "Execute training run"
      description: "Run fine-tuning with monitoring"
      acceptance_criteria:
        - "Training completed successfully"
        - "Loss curves logged"
        - "Checkpoints saved"
        - "No divergence or instability"

    - id: "TRAIN-S05"
      title: "Evaluate fine-tuned model"
      description: "Validate model quality before deployment"
      acceptance_criteria:
        - "Benchmark scores computed"
        - "Qualitative review completed"
        - "Comparison with base model"
        - "Model artifacts saved"
```

**Update sidecar with stories:**
```yaml
stories:
  step_5_training:
    - "[story list based on training design]"
```

### 11. Present MENU OPTIONS

Display: **Step 5 Complete - Select an Option:** [A] Analyze training decisions further [Q] Re-query Knowledge MCP with different constraints [P] View progress [C] Continue to Step 6 (RAG Specialist)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit training decisions, allow refinement, then redisplay menu
- IF Q: **Re-query with Modified Constraints**
  1. Ask user which constraints to modify:
     - Compute budget (GPU type, training time)
     - Data volume assumptions
     - Quality vs speed trade-offs
     - Model size constraints
  2. Re-run Knowledge MCP queries with updated constraints
  3. Present updated recommendations with explanation of what changed
  4. Allow user to revise training decisions based on new insights
  5. Redisplay menu
- IF P: Show training-spec.md and decision-log.md summaries, then redisplay menu
- IF C:
  1. Verify sidecar is updated with training decisions and stories
  2. Load, read entire file, then execute `{nextStepFile}` (RAG Specialist)
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND training pipeline is documented (OR step is properly skipped) AND stories are generated, will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Step 6: RAG Specialist.

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

- Correctly handled skip logic for RAG-only
- Knowledge MCP queried for methodologies and warnings
- Training data assessed thoroughly
- Base model selected with rationale
- Training approach defined with data requirements
- PEFT configuration documented
- Hyperparameters justified
- Infrastructure planned
- training-spec.md complete
- Stories generated for training implementation
- User confirmed design before proceeding

### SYSTEM FAILURE:

- Not checking architecture for skip condition
- Making decisions without user input
- Skipping Knowledge MCP queries
- Not creating skip record when RAG-only
- Discussing RAG retrieval (belongs in Step 6)
- Discussing evaluation metrics (belongs in Step 8)
- Not generating implementation stories
- Proceeding without confirmed design

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
