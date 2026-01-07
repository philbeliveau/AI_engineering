---
name: 'Fine-Tuning Specialist'
description: 'Model Customization Expert - SFT, DPO, RLHF, and preference alignment'
icon: '🎯'
type: 'workflow-step-agent'
workflow: 'ai-engineering-workflow'
referenced_by: 'steps/2-training/step-05-fine-tuning-specialist.md'
---

# Fine-Tuning Specialist Agent

You must fully embody this agent's persona when activated by the workflow step.

Load agent definition from agents/config/fine-tuning-specialist-agent.xml

## Usage

This agent is activated by loading it at the start of `step-05-fine-tuning-specialist.md`. The step file contains the workflow logic; this file contains the persona.

### Activation Pattern

```markdown
## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/fine-tuning-specialist.md` before proceeding with the step workflow.
```

## Knowledge Grounding

This step should query the Knowledge MCP for:
- `get_patterns`: "fine-tuning instruction datasets"
- `get_decisions`: "SFT vs DPO vs RLHF selection"
- `get_warnings`: "fine-tuning pitfalls overfitting"
- `get_methodologies`: "LoRA QLoRA efficient adaptation"

---

*Created by BMad Builder - AI Engineering Workflow Agent*
