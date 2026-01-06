# Step 7: Prompt Engineer

Execute the Prompt Engineer step - prompt design and templates.

---

## Phase: 3 - Inference Pipeline

## Instructions

You are executing **Step 7** of the AI Engineering Workflow.

### Execution Sequence

1. **Load the agent persona**: Read `agents/prompt-engineer.md` completely and embody it
2. **Load the step file**: Read `steps/3-inference/step-07-prompt-engineer.md` completely
3. **Execute the step**: Follow ALL instructions in the step file exactly as written
4. **Query Knowledge MCP**: At designated points, query for prompt patterns

### What This Step Does

| Aspect | Details |
|--------|---------|
| **Agent** | 📝 Prompt Engineer |
| **Focus** | System prompts, templates, few-shot, CoT |
| **Outputs** | Prompt templates, PROMPT-prefixed stories |
| **Next Step** | Step 8: LLM Evaluator |

### Key Activities

1. System prompt design
2. User message templates
3. Few-shot example development
4. Chain-of-thought patterns (where applicable)
5. Prompt injection mitigations
6. PROMPT-prefixed story generation

### Knowledge MCP Queries

- `get_patterns`: Prompt design patterns
- `get_warnings`: Prompt injection risks
- `get_decisions`: Few-shot vs zero-shot trade-offs

### Handoff

After completion, hands off to **Step 8: LLM Evaluator** with:
- Prompt template library
- System prompt specifications
- PROMPT-prefixed implementation stories

---

**BEGIN**: Load `agents/prompt-engineer.md`, then execute `steps/3-inference/step-07-prompt-engineer.md`
