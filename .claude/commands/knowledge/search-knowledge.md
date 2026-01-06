# Search Knowledge

Semantic search across all AI engineering knowledge.

---

## Arguments

$ARGUMENTS - Your search query (e.g., "chunking strategies for legal documents")

---

## Instructions

Execute a semantic search against the Knowledge MCP to find relevant AI engineering information.

### How to Search

Use the `search_knowledge` MCP tool with the query: **$ARGUMENTS**

### Search Tips

- **Be specific**: "RAG chunking for code documentation" > "chunking"
- **Include domain context**: "embedding model for multilingual support"
- **Try synonyms**: If few results, try related terms

### Multi-Query Strategy

For comprehensive answers, search 2-3 times with varied queries:
1. User's original phrasing
2. Technical synonyms (e.g., "RAG" → "retrieval augmented generation")
3. Related concepts (e.g., "chunking" → "document splitting")

### What You'll Get

- Relevant patterns, decisions, warnings, and methodologies
- Source citations (books, papers, case studies)
- Synthesized recommendations from multiple sources

---

**EXECUTE**: Call `search_knowledge` tool with query: "$ARGUMENTS"
