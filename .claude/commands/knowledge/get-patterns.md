---
description: Query reusable implementation patterns from knowledge base
argument-hint: [pattern type or problem]
---

# Get Implementation Patterns

Query the knowledge base for reusable implementation patterns, design solutions, and proven approaches from AI engineering literature.

## Examples

- `/knowledge:get-patterns retry with exponential backoff`
- `/knowledge:get-patterns RAG retrieval patterns`
- `/knowledge:get-patterns prompt template management`
- `/knowledge:get-patterns` (lists all available patterns)

## Task

Use the knowledge-pipeline MCP server's `get_patterns` tool to find patterns about: $ARGUMENTS

If no arguments provided, list all available patterns organized by category.

## Output Format

Present each pattern with:
- **Pattern name** - Identifier for the pattern
- **Problem** - What situation this solves
- **Solution** - How to implement it
- **Code example** - Sample implementation (if available)
- **Trade-offs** - When to use vs. alternatives
- **Source** - Book/paper and section
