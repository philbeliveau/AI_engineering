# Step 8: LLM Evaluator

Execute the LLM Evaluator step - evaluation framework design.

---

## Phase: 4 - Evaluation

## Instructions

You are executing **Step 8** of the AI Engineering Workflow.

### Execution Sequence

1. **Load the agent persona**: Read `agents/llm-evaluator.md` completely and embody it
2. **Load the step file**: Read `steps/4-evaluation/step-08-llm-evaluator.md` completely
3. **Execute the step**: Follow ALL instructions in the step file exactly as written
4. **Query Knowledge MCP**: At designated points, query for evaluation patterns

### What This Step Does

| Aspect | Details |
|--------|---------|
| **Agent** | 📊 LLM Evaluator |
| **Focus** | Evaluation framework, metrics, benchmarks |
| **Outputs** | Evaluation specification, EVAL-prefixed stories |
| **Next Step** | Step 9: MLOps Engineer |

### Key Activities

1. Evaluation framework design
2. Metric selection (relevance, faithfulness, coherence, etc.)
3. Benchmark test set creation
4. Quality gate definition
5. Human evaluation protocol
6. EVAL-prefixed story generation

### Knowledge MCP Queries

- `get_patterns`: Evaluation metric patterns
- `get_warnings`: LLM-as-judge limitations
- `get_methodologies`: Evaluation processes

### Quality Gate

This step establishes the **quality gate** that validates system output before deployment:
- Define pass/fail thresholds
- Establish regression detection
- Plan continuous evaluation

---

**BEGIN**: Load `agents/llm-evaluator.md`, then execute `steps/4-evaluation/step-08-llm-evaluator.md`
