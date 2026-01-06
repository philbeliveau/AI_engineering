# Step 2: FTI Architect

Execute the FTI Architect step - architecture decision and system design.

---

## Phase: 0 - Scoping

## Instructions

You are executing **Step 2** of the AI Engineering Workflow.

### Execution Sequence

1. **Load the agent persona**: Read `agents/fti-architect.md` completely and embody it
2. **Load the step file**: Read `steps/0-scoping/step-02-fti-architect.md` completely
3. **Execute the step**: Follow ALL instructions in the step file exactly as written
4. **Query Knowledge MCP**: At designated points, query for architectural decisions

### What This Step Does

| Aspect | Details |
|--------|---------|
| **Agent** | 🏗️ FTI Architect |
| **Focus** | RAG vs Fine-tuning decision, FTI pipeline design |
| **Outputs** | Architecture decision document, ARCH-prefixed stories |
| **Next Step** | Step 3: Data Engineer |

### Critical Decision Point

This step makes the **routing decision** that affects the entire workflow:

| Decision | Path |
|----------|------|
| **RAG-only** | Skip Step 5 (Fine-Tuning), go directly to Step 6 |
| **Fine-tuning** | Include Step 5, then continue |
| **Hybrid** | Include both Step 5 and Step 6 with integration |

### Knowledge MCP Queries

- `get_decisions`: RAG vs fine-tuning trade-offs
- `get_warnings`: Architecture anti-patterns

### Handoff

After completion, hands off to **Step 3: Data Engineer** with:
- Architecture decision (rag-only / fine-tuning / hybrid)
- Technical design document
- ARCH-prefixed implementation stories

---

**BEGIN**: Load `agents/fti-architect.md`, then execute `steps/0-scoping/step-02-fti-architect.md`
