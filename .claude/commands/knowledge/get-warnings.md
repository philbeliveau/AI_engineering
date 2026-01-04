---
description: Query anti-patterns and pitfalls to avoid from knowledge base
argument-hint: [topic or technology]
---

# Get Warnings and Anti-Patterns

Query the knowledge base for warnings, pitfalls, anti-patterns, and common mistakes documented in AI engineering literature.

## Examples

- `/knowledge:get-warnings prompt injection vulnerabilities`
- `/knowledge:get-warnings LLM hallucination mitigation`
- `/knowledge:get-warnings embedding model gotchas`
- `/knowledge:get-warnings` (lists all available warnings)

## Task

Use the knowledge-pipeline MCP server's `get_warnings` tool to find warnings about: $ARGUMENTS

If no arguments provided, list all available warnings organized by severity.

## Output Format

Present each warning with:
- **Anti-pattern** - What to avoid
- **Why problematic** - The risks or issues it causes
- **What to do instead** - Recommended alternative
- **Real-world example** - Case where this caused issues (if available)
- **Source** - Book/paper and section
