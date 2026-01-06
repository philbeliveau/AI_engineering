# Step 4: Embeddings Engineer

Execute the Embeddings Engineer step - vectorization pipeline design.

---

## Phase: 1 - Feature Pipeline

## Instructions

You are executing **Step 4** of the AI Engineering Workflow.

### Execution Sequence

1. **Load the agent persona**: Read `agents/embeddings-engineer.md` completely and embody it
2. **Load the step file**: Read `steps/1-feature/step-04-embeddings-engineer.md` completely
3. **Execute the step**: Follow ALL instructions in the step file exactly as written
4. **Query Knowledge MCP**: At designated points, query for embedding patterns

### What This Step Does

| Aspect | Details |
|--------|---------|
| **Agent** | 🧬 Embeddings Engineer |
| **Focus** | Chunking strategy, embedding model, vector DB |
| **Outputs** | Embedding pipeline specification, EMB-prefixed stories |
| **Next Step** | Step 5 (if fine-tuning) or Step 6 (if RAG-only) |

### Key Activities

1. Chunking strategy selection (fixed, semantic, hierarchical)
2. Chunk size and overlap optimization
3. Embedding model selection
4. Vector database configuration
5. Indexing strategy design
6. EMB-prefixed story generation

### Knowledge MCP Queries

- `get_patterns`: Chunking strategies, embedding patterns
- `get_decisions`: Embedding model trade-offs
- `get_warnings`: Chunking pitfalls

### Conditional Routing

| Architecture | Next Step |
|--------------|-----------|
| **RAG-only** | Skip to Step 6: RAG Specialist |
| **Fine-tuning / Hybrid** | Step 5: Fine-Tuning Specialist |

---

**BEGIN**: Load `agents/embeddings-engineer.md`, then execute `steps/1-feature/step-04-embeddings-engineer.md`
