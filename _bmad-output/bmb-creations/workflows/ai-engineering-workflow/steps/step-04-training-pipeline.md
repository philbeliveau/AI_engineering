---
name: 'step-04-training-pipeline'
description: 'Phase 2: Design the Training Pipeline - SFT, DPO, and model optimization (CONDITIONAL)'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/ai-engineering-workflow'

# File References
thisStepFile: '{workflow_path}/steps/step-04-training-pipeline.md'
nextStepFile: '{workflow_path}/steps/step-05-inference-pipeline.md'
workflowFile: '{workflow_path}/workflow.md'

# Output References
outputFolder: '{output_folder}/{project_name}'
sidecarFile: '{outputFolder}/sidecar.yaml'
projectSpecFile: '{outputFolder}/project-spec.md'
decisionLogFile: '{outputFolder}/decision-log.md'
trainingFolder: '{outputFolder}/phase-2-training'
trainingSpecFile: '{trainingFolder}/spec.md'
trainingConfigTemplate: '{trainingFolder}/templates/training-config.template.yaml'
---

# Step 4: Phase 2 - Training Pipeline

## CONDITIONAL EXECUTION NOTE

⚠️ **This phase is CONDITIONAL:**
- If `architecture: "rag-only"` in sidecar.yaml → **SKIP this phase entirely**
- If `architecture: "fine-tuning"` or `architecture: "hybrid"` → **Execute this phase**

If skipping, create a skip record and proceed directly to Phase 3 (Inference Pipeline).

## STEP GOAL:

To design the Training Pipeline for fine-tuning LLMs using SFT (Supervised Fine-Tuning), DPO (Direct Preference Optimization), or other alignment techniques.

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

- 🎯 Focus ONLY on training pipeline design
- 🚫 FORBIDDEN to discuss deployment (Phase 3) or evaluation details (Phase 4)
- 💬 Query Knowledge MCP for SFT/DPO methodologies
- 🧠 Address common fine-tuning pitfalls proactively

## EXECUTION PROTOCOLS:

- 🎯 Show your reasoning before making recommendations
- 💾 Update sidecar when completing training pipeline design
- 📖 Record decisions in decision-log.md
- 🚫 FORBIDDEN to proceed until training pipeline is fully designed

## CONTEXT BOUNDARIES:

- Feature Pipeline (Phase 1) provides data preparation foundation
- This phase focuses on model training mechanics
- Decisions here impact inference pipeline setup

## SKIP HANDLING:

### If RAG-Only Architecture

Check sidecar.yaml first. If `architecture: "rag-only"`:

**1. Create Skip Record**

Create `{trainingFolder}/spec.md`:
```markdown
# Phase 2: Training Pipeline

**Status:** SKIPPED

**Reason:** RAG-only architecture selected in Phase 0. No fine-tuning required.

**Architecture Decision Reference:** See `phase-0-scoping/architecture-decision.md`

**Implication:** Proceeding directly to Phase 3 (Inference Pipeline) where the RAG system will be configured to use a pre-trained base model.
```

**2. Update Sidecar**
```yaml
stepsCompleted: [1, 2, 3, 4]  # Include 4 even though skipped
phases:
  phase_2_training: "skipped"
```

**3. Proceed to Phase 3**
- Load `{nextStepFile}` immediately

---

## TRAINING PIPELINE SEQUENCE (If Not Skipping):

### 1. Welcome to Phase 2

Present the phase introduction:

"**Phase 2: Training Pipeline - Fine-tuning Your Model**

Based on your **{architecture}** architecture, we'll design a training pipeline for customizing an LLM to your use case.

**Key Decisions:**
- Base model selection
- Training approach (SFT, DPO, or combined)
- Data preparation for training
- Hyperparameter configuration
- Compute requirements

Let's design this systematically."

### 2. Query Knowledge MCP for Methodologies

**MANDATORY QUERIES** - Execute and synthesize:

**Query 1: Fine-tuning Methodologies**
```
Endpoint: search_knowledge
Query: "QLoRA LoRA fine-tuning rank alpha configuration"
```

**Query 2: Training Approach Decision**
```
Endpoint: get_decisions
Topic: "SFT vs DPO"
```

**Query 3: Training Warnings**
```
Endpoint: get_warnings
Topic: "fine-tuning"
```

**Query 4: Dataset Creation**
```
Endpoint: search_knowledge
Query: "instruction dataset creation training data quality"
```

**Synthesis Approach:**
1. Extract **LoRA/QLoRA configuration patterns** (rank, alpha, target modules)
2. Understand **SFT vs DPO decision criteria**
3. Surface **dataset quality requirements** (this is often the hardest part)
4. Note **common fine-tuning mistakes** to avoid

Present synthesized insights:
"Here's what the knowledge base tells us about fine-tuning approaches..."

**Critical Warning to Surface:**
> Creating instruction datasets is often the most difficult part of fine-tuning. Natural instruction-answer pairs are rare - data must be transformed and quality-checked extensively.

### 3. Base Model Selection

**A. Model Selection Criteria**

| Factor | Consideration |
|--------|---------------|
| **Size** | 7B, 13B, 70B - trade-off between capability and cost |
| **License** | Commercial use allowed? (Llama 2, Mistral, Falcon) |
| **Architecture** | Decoder-only (GPT-like) vs Encoder-decoder |
| **Pre-training Data** | Domain relevance of base knowledge |
| **Instruction Tuning** | Already instruction-tuned or base? |
| **Context Length** | Maximum tokens per input |

**B. Recommended Models**

| Model | Size | License | Strengths |
|-------|------|---------|-----------|
| **Llama 2** | 7B-70B | Meta license | Strong general capability |
| **Mistral** | 7B | Apache 2.0 | Efficient, good quality |
| **Qwen** | 7B-72B | Apache 2.0 | Strong reasoning |
| **Falcon** | 7B-180B | Apache 2.0 | Large pre-training corpus |
| **CodeLlama** | 7B-34B | Meta license | Code-specialized |

Ask: "What base model constraints do you have? (Size limits, licensing, domain requirements)"

### 4. Training Approach Selection

**A. SFT (Supervised Fine-Tuning)**

"SFT teaches the model to follow instructions using example pairs."

```
Input: "Summarize this document: [doc]"
Output: "[summary]"
```

**When to use:**
- You have high-quality instruction-response pairs
- Task is well-defined (classification, extraction, generation)
- Need consistent output format

**B. DPO (Direct Preference Optimization)**

"DPO aligns the model using preference data (chosen vs rejected)."

```
Prompt: "Explain quantum computing"
Chosen: [Good, helpful response]
Rejected: [Poor, unhelpful response]
```

**When to use:**
- You have preference data or can generate it
- Need subtle behavior alignment
- Want to reduce harmful outputs

**C. Combined Approach**

"SFT first for capability, then DPO for alignment."

```
Stage 1: SFT → Task capability
Stage 2: DPO → Behavior refinement
```

**Query Knowledge MCP for decision criteria:**
```
Endpoint: get_decisions
Topic: SFT vs DPO
```

Ask: "Based on your data and goals, which approach fits best?"

### 5. Training Data Preparation

**A. Data Requirements**

| Approach | Minimum Data | Ideal Data | Format |
|----------|--------------|------------|--------|
| **SFT** | 1,000 examples | 10,000+ | Instruction-response pairs |
| **DPO** | 1,000 preferences | 5,000+ | Prompt + chosen + rejected |
| **Combined** | Both requirements | Both ideals | Both formats |

**B. Data Quality Checklist**

| Criterion | Description | Why Important |
|-----------|-------------|---------------|
| **Diversity** | Cover all target use cases | Prevent narrow specialization |
| **Quality** | Responses match ideal output | Model learns from examples |
| **Consistency** | Same style/format throughout | Predictable outputs |
| **No Contamination** | Not in eval set | Valid evaluation |
| **No PII** | Remove sensitive data | Compliance |

**Query Warnings:**
```
Endpoint: get_warnings
Topic: training data quality
```

Ask: "Tell me about your training data. How was it collected? What's the quality like?"

### 6. Parameter-Efficient Fine-Tuning

**Query Knowledge MCP for PEFT Patterns:**
```
Endpoint: search_knowledge
Query: "LoRA QLoRA parameter efficient fine-tuning PEFT"
```

```
Endpoint: get_decisions
Topic: "QLoRA vs LoRA"
```

**A. PEFT Method Selection**

Present decision framework from knowledge base:

| Method | Memory | Speed | When Knowledge Base Recommends |
|--------|--------|-------|-------------------------------|
| **Full Fine-tuning** | High | Slow | Small models, unlimited compute |
| **LoRA** | Low | Fast | Training speed is priority, sufficient VRAM |
| **QLoRA** | Very Low | Medium | Memory constraints are primary concern |

**Key Decision from Knowledge Base:**
- **QLoRA**: Use when memory constraints are the primary concern (quantized base model)
- **LoRA**: Use when training speed is crucial AND sufficient memory available

**B. LoRA Configuration - Knowledge-Grounded Values**

Query for current best practices:
```
Endpoint: search_knowledge
Query: "LoRA rank alpha dropout target modules configuration"
```

**Configuration Pattern from Knowledge Base:**

| Parameter | Starting Point | Guidance |
|-----------|---------------|----------|
| **rank (r)** | r=4 | Can increase up to 256 for complex tasks |
| **alpha (α)** | α = 2r | Common heuristic: if r=4, then α=8 |
| **dropout** | 0 to 0.1 | Optional regularization factor |

**Target Modules Pattern:**
- **Attention layers**: q_proj, v_proj, k_proj, o_proj (standard)
- **MLP layers**: gate_proj, up_proj, down_proj (for extended adaptation)
- Query knowledge base for model-specific recommendations

**C. Decision Capture**

Document the PEFT choice with rationale:
- Method chosen (LoRA/QLoRA/Full)
- Rank and alpha values with justification
- Target modules selected
- Link to knowledge base query that informed decision

Ask: "What compute resources do you have? Let me query the knowledge base for appropriate PEFT configuration."

### 7. Hyperparameter Configuration

**Query Knowledge MCP:**
```
Endpoint: search_knowledge
Query: "fine-tuning hyperparameters learning rate epochs batch size"
```

```
Endpoint: get_warnings
Topic: "training hyperparameters"
```

**A. Key Hyperparameters - Query for Current Recommendations**

Present ranges from knowledge base, noting they evolve with research:

| Parameter | Typical Range | Knowledge Base Guidance |
|-----------|---------------|------------------------|
| **Learning Rate** | 1e-5 to 2e-4 (SFT) | Lower for larger models |
| **Epochs** | 1-5 | Knowledge base warns: 2-5 often optimal, watch for overfitting |
| **Batch Size** | 4-32 | Limited by memory, use gradient accumulation |
| **Warmup** | 3-10% of steps | Stabilizes early training |

**Key Warning from Knowledge Base:**
> Too few epochs → underfitting. Too many epochs → overfitting (model memorizes training data). Monitor validation performance and implement early stopping.

**B. Training Approach-Specific Configuration**

Query for approach-specific guidance:
```
Endpoint: get_methodologies
Topic: "DPO alignment"
```

**For DPO (if applicable):**
- **Beta parameter**: Controls KL penalty (query knowledge base for current recommendations)
- **Reference model**: Usually needed unless using reference-free variants
- Query for latest DPO variants and their trade-offs

**C. Monitoring Training**

Knowledge base recommends tracking:
- Training/validation loss curves
- Gradient norms
- Early stopping based on validation performance

Ask: "What's your training budget (time, compute)? This affects hyperparameter choices."

### 8. Training Infrastructure

**A. Compute Options**

| Platform | Cost Model | Best For |
|----------|------------|----------|
| **Local GPU** | CapEx | Iteration, privacy |
| **Cloud GPU** | Per-hour | Scale, flexibility |
| **SageMaker** | Managed | Enterprise, integration |
| **Lambda Labs** | Simple pricing | Cost-effective |
| **Vast.ai** | Marketplace | Budget training |

**Recommended (from Knowledge Base):** AWS SageMaker
- Managed training jobs
- Spot instances for cost savings
- Integrated with feature pipeline (MongoDB, Qdrant)

**B. Experiment Tracking**

| Tool | Features | Integration |
|------|----------|-------------|
| **Comet ML** | Full MLOps | Recommended by knowledge base |
| **Weights & Biases** | Popular | Good ecosystem |
| **MLflow** | Open source | Self-hosted |

Ask: "What's your preference for training infrastructure and experiment tracking?"

### 9. Create Training Pipeline Spec

**Create spec.md in phase-2-training/:**

```markdown
# Phase 2: Training Pipeline Spec

## Objective
Design the training pipeline for fine-tuning the base model to project requirements.

## Knowledge Consulted
- `get_methodologies: supervised fine-tuning` - [key insights]
- `get_methodologies: DPO alignment` - [key insights]
- `get_patterns: model training` - [key insights]
- `get_warnings: fine-tuning mistakes` - [warnings to avoid]

## Base Model

**Model:** [selected model]
**Size:** [parameters]
**License:** [license type]
**Rationale:** [why this model]

## Training Approach

**Primary:** [SFT | DPO | Combined]

### SFT Configuration (if applicable)
- Data format: [instruction-response]
- Examples: [count]
- Quality verification: [method]

### DPO Configuration (if applicable)
- Data format: [prompt + chosen + rejected]
- Preference pairs: [count]
- Source: [how preferences were obtained]

## Parameter-Efficient Training

**Method:** [LoRA | QLoRA | Full]
**Configuration:**
- Rank: [value]
- Alpha: [value]
- Target modules: [list]

## Hyperparameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Learning Rate | [value] | [why] |
| Batch Size | [value] | [why] |
| Epochs | [value] | [why] |

## Infrastructure

**Compute:** [platform]
**Tracking:** [tool]
**Estimated Cost:** [range]

## Decisions Made

| ID | Decision | Rationale |
|----|----------|-----------|
| TP-001 | [Base model] | [Why] |
| TP-002 | [Training approach] | [Why] |
| TP-003 | [PEFT method] | [Why] |

## Exit Criteria
- [ ] Base model selected
- [ ] Training approach defined
- [ ] Data requirements documented
- [ ] Hyperparameters configured
- [ ] Infrastructure planned
- [ ] Templates generated
```

### 10. Generate Training Config Template

**training-config.template.yaml:**
```yaml
# Training Configuration
# Decision reference: See decision-log.md#TP-xxx

# Base Model
model:
  name: "{{BASE_MODEL}}"
  revision: "{{MODEL_REVISION}}"
  quantization: "{{QUANTIZATION}}"  # none | 4bit | 8bit

# LoRA Configuration
lora:
  r: {{LORA_RANK}}
  alpha: {{LORA_ALPHA}}
  dropout: {{LORA_DROPOUT}}
  target_modules:
    - q_proj
    - v_proj
    - k_proj
    - o_proj

# Training Parameters
training:
  approach: "{{TRAINING_APPROACH}}"  # sft | dpo | combined

  # Common parameters
  learning_rate: {{LEARNING_RATE}}
  batch_size: {{BATCH_SIZE}}
  gradient_accumulation_steps: {{GRAD_ACCUM}}
  num_epochs: {{NUM_EPOCHS}}
  warmup_ratio: {{WARMUP_RATIO}}
  weight_decay: {{WEIGHT_DECAY}}

  # DPO-specific (if applicable)
  dpo:
    beta: {{DPO_BETA}}
    reference_free: {{REF_FREE}}

# Data
data:
  train_path: "{{TRAIN_DATA_PATH}}"
  eval_path: "{{EVAL_DATA_PATH}}"
  max_length: {{MAX_LENGTH}}

# Infrastructure
infrastructure:
  platform: "{{PLATFORM}}"
  instance_type: "{{INSTANCE_TYPE}}"
  spot_instances: {{USE_SPOT}}

# Tracking
tracking:
  tool: "{{TRACKING_TOOL}}"
  project: "{{PROJECT_NAME}}"
  experiment: "{{EXPERIMENT_NAME}}"
```

### 11. Update Project Files

**Update sidecar.yaml:**
```yaml
currentPhase: 3
stepsCompleted: [1, 2, 3, 4]
decisions:
  # ... previous decisions ...
  - id: "tp-001"
    choice: "[base model]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_patterns:model-selection"
  - id: "tp-002"
    choice: "[training approach]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_methodologies:sft"
phases:
  phase_2_training: "complete"
```

**Append to decision-log.md:** (all TP decisions)

**Update project-spec.md:** (add Training Pipeline section)

### 12. Present MENU OPTIONS

Display: **Phase 2 Complete - Select an Option:** [A] Analyze decisions further [P] View progress [C] Continue to Phase 3

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit any decision, allow refinement, then redisplay menu
- IF P: Show spec.md summary, then redisplay menu
- IF C:
  1. Verify sidecar is updated
  2. Load, read entire file, then execute `{nextStepFile}` (Inference Pipeline)
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND all training pipeline decisions are documented (OR phase is properly skipped), will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Phase 3: Inference Pipeline.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Correctly handled skip logic for RAG-only
- Knowledge MCP queried for methodologies and patterns
- Base model selected with rationale
- Training approach defined with data requirements
- PEFT configuration documented
- Hyperparameters justified
- Infrastructure planned
- Config templates generated
- Spec.md complete

### ❌ SYSTEM FAILURE:

- Not checking architecture for skip condition
- Making decisions without user input
- Skipping Knowledge MCP queries
- Not creating skip record when RAG-only
- Discussing inference/deployment (belongs in Phase 3)
- Not generating config templates

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
