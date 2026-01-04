---
description: List all knowledge sources in the database
---

# List Knowledge Sources

List all available knowledge sources (books, papers, case studies) in the knowledge base with extraction statistics.

## Examples

- `/knowledge:list-sources`

## Task

Use the knowledge-pipeline MCP server's `list_sources` tool to display all ingested sources.

## Output Format

Present each source with:
- **Title** and author(s)
- **Type** - Book, paper, or case study
- **Extraction counts** by type:
  - Decisions extracted
  - Patterns extracted
  - Warnings extracted
  - Methodologies extracted (if applicable)
- **Topics covered** - Key subject areas
