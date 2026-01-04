---
description: Compare how different sources address the same topic (Registered tier)
argument-hint: [topic to compare]
---

# Compare Sources

Compare how different knowledge sources (books, papers, case studies) address the same topic, revealing areas of agreement and different perspectives.

## Access Note

This is a **Registered tier** endpoint - requires API key configuration.

## Examples

- `/knowledge:compare-sources chunking strategies for RAG`
- `/knowledge:compare-sources LLM evaluation approaches`
- `/knowledge:compare-sources vector database selection`

## Task

1. First call `list_sources` to identify available source IDs
2. Use the knowledge-pipeline MCP server's `compare_sources` tool to compare 2-4 sources on: $ARGUMENTS

## Output Format

Present comparison with:
- **Topic** - What's being compared
- **Sources compared** - Which books/papers included
- **Per-source summary** - What each source says
- **Areas of agreement** - Common recommendations
- **Areas of disagreement** - Different perspectives or emphasis
- **Synthesis** - Balanced recommendation considering all viewpoints
- **Citations** - Specific references for each perspective
