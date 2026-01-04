---
description: Query architectural decisions and trade-offs from knowledge base
argument-hint: [topic or technology]
---

# Get Architectural Decisions

Query the knowledge base for architectural decisions, trade-offs, and technology choices documented in AI engineering literature.

## Examples

- `/knowledge:get-decisions embedding model selection`
- `/knowledge:get-decisions monolith vs microservices`
- `/knowledge:get-decisions caching strategies for LLM apps`
- `/knowledge:get-decisions` (lists all available decisions)

## Task

Use the knowledge-pipeline MCP server's `get_decisions` tool to find decisions about: $ARGUMENTS

If no arguments provided, list all available decisions with brief summaries.

## Output Format

Present each decision with:
- **Decision point** - The question being answered
- **Options considered** - Alternatives evaluated
- **Trade-offs** - Pros/cons of each approach
- **Recommended approach** - What the source suggests (if available)
- **Source** - Book/paper and section
