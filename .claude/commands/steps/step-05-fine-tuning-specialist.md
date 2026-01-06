# Step 5: Fine-Tuning Specialist

Execute the Fine-Tuning Specialist step - model customization design.

---

## Phase: 2 - Training Pipeline (CONDITIONAL)

**Note:** This step is SKIPPED for RAG-only architectures.

## Instructions

You are executing **Step 5** of the AI Engineering Workflow.

### Execution Sequence

1. **Check architecture**: Verify sidecar.yaml shows "fine-tuning" or "hybrid"
2. **Load the agent persona**: Read `agents/fine-tuning-specialist.md` completely and embody it
3. **Load the step file**: Read `steps/2-training/step-05-fine-tuning-specialist.md` completely
4. **Execute the step**: Follow ALL instructions in the step file exactly as written

### What This Step Does

| Aspect | Details |
|--------|---------|
| **Agent** | 🎯 Fine-Tuning Specialist |
| **Focus** | SFT/DPO configuration, dataset preparation |
| **Outputs** | Training configuration, TRAIN-prefixed stories |
| **Next Step** | Step 6: RAG Specialist |

### Key Activities

1. Fine-tuning approach selection (SFT, DPO, or combined)
2. Training dataset specification
3. Data format and quality requirements
4. Hyperparameter configuration
5. Validation and checkpointing strategy
6. TRAIN-prefixed story generation

### Knowledge MCP Queries

- `get_methodologies`: SFT/DPO processes
- `get_patterns`: Training data preparation
- `get_warnings`: Fine-tuning pitfalls

### Skip Condition

If `sidecar.yaml` shows `architecture: "rag-only"`:
- Skip this step entirely
- Proceed directly to Step 6: RAG Specialist

---

**BEGIN**: Load `agents/fine-tuning-specialist.md`, then execute `steps/2-training/step-05-fine-tuning-specialist.md`
