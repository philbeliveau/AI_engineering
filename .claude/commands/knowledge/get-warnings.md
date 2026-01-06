# Get Warnings

Retrieve anti-patterns and pitfalls to avoid.

---

## Arguments

$ARGUMENTS - Topic or technology (e.g., "RAG pipeline", "fine-tuning", "prompt injection")

---

## Instructions

Query the Knowledge MCP for warnings and anti-patterns related to: **$ARGUMENTS**

### How to Query

Use the `get_warnings` MCP tool with the topic: **$ARGUMENTS**

### What You'll Get

- **Warning**: What can go wrong
- **Symptoms**: How to recognize the problem
- **Impact**: Consequences of ignoring
- **Prevention**: How to avoid it
- **Mitigation**: How to fix if it happens
- **Source citations**: Where this warning comes from

### CRITICAL: Always Check Warnings Before Implementing

Before recommending any implementation approach:
1. Query warnings for that approach
2. Surface top 2-3 relevant warnings
3. Frame as: "To avoid X, ensure you Y"

### Common Warning Categories

- Data quality pitfalls
- Chunking mistakes
- Embedding failures
- RAG anti-patterns
- Fine-tuning traps
- Prompt injection risks
- Evaluation blind spots
- Production failure modes

---

**EXECUTE**: Call `get_warnings` tool with topic: "$ARGUMENTS"
