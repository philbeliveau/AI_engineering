---
description: Semantic search across AI engineering knowledge base
argument-hint: [search query]
---

# Search AI Engineering Knowledge

Search the knowledge base for AI engineering insights using semantic search across all extracted content from methodology books, papers, and case studies.

## Examples

- `/knowledge:search-knowledge RAG chunking strategies`
- `/knowledge:search-knowledge when to fine-tune vs prompt engineering`
- `/knowledge:search-knowledge vector database selection criteria`
- `/knowledge:search-knowledge agent orchestration patterns`

## Task

Use the knowledge-pipeline MCP server's `search_knowledge` tool to find relevant information about: $ARGUMENTS

If no arguments provided, ask the user what they want to search for.

## Output Format

Present results with:
- **Key insights** found with relevance to query
- **Source citations** (book/paper title, chapter/section)
- **Actionable takeaways** the user can apply
