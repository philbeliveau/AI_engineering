# Get Decisions

Retrieve architectural decisions with trade-offs and recommendations.

---

## Arguments

$ARGUMENTS - Topic for decision guidance (e.g., "RAG vs fine-tuning", "vector database selection")

---

## Instructions

Query the Knowledge MCP for architectural decisions related to: **$ARGUMENTS**

### How to Query

Use the `get_decisions` MCP tool with the topic: **$ARGUMENTS**

### What You'll Get

- **Options**: Available choices for the decision
- **Trade-offs**: Pros/cons of each option
- **Recommendations**: When to choose which option
- **Context factors**: Constraints that influence the decision
- **Source citations**: Where this guidance comes from

### Best For

- Architecture choices (RAG vs fine-tuning, hybrid approaches)
- Technology selection (vector DB, embedding model, LLM)
- Design patterns (chunking strategy, retrieval approach)
- Scale decisions (when to fine-tune vs prompt engineer)

### Follow-Up

After reviewing decisions, consider:
- `get_warnings` - Pitfalls to avoid for your choice
- `get_patterns` - Implementation patterns for your choice

---

**EXECUTE**: Call `get_decisions` tool with topic: "$ARGUMENTS"
