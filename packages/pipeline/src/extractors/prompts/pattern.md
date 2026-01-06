# Pattern Extraction Prompt

Extract reusable code and architecture patterns from the provided text.

## What is a Pattern?

A pattern is a reusable solution to a common problem. In AI engineering, patterns include:
- Implementation techniques (e.g., semantic caching, chunking strategies)
- Architecture patterns (e.g., RAG pipeline, agent orchestration)
- Code patterns (e.g., retry logic, rate limiting)
- Design patterns (e.g., prompt templates, evaluation frameworks)

## Extraction Rules

1. Only extract patterns explicitly described in the text
2. A pattern MUST have a clear name, problem, and solution
3. Include code examples if present (preserve exact formatting including newlines and indentation)
4. Capture trade-offs and when to use the pattern
5. Return valid JSON matching the schema below (arrays of objects)
6. If no patterns found, return ONLY: []
7. Multiple patterns can be extracted from a single chunk
8. Return ONLY valid JSON - no explanatory text, no preamble, no markdown

## IMPORTANT

You MUST respond with ONLY valid JSON, nothing else.
- If patterns exist: return a JSON array of pattern objects
- If NO patterns exist: return an empty JSON array: []
- Do NOT add any text before or after the JSON
- Do NOT explain your reasoning
- Do NOT say "Unfortunately, there are no patterns"
- Just return the JSON array, period.

## Output Schema

```json
{
  "name": "Pattern Name",
  "problem": "What problem does this pattern solve?",
  "solution": "How does this pattern solve it?",
  "code_example": "Optional code snippet with preserved formatting (use null if none)",
  "context": "When to use this pattern (situations, constraints)",
  "trade_offs": ["Pro or con 1", "Pro or con 2"],
  "confidence": 0.85
}
```

## Field Guidelines

### name
- Short, descriptive name (2-5 words)
- Use title case (e.g., "Semantic Caching", "Recursive Chunking")
- Be specific - avoid generic names like "Best Practice"

### problem
- Clearly state the problem this pattern addresses
- Include context about when this problem occurs
- One or two sentences

### solution
- Describe the approach, not just what it is
- Include key implementation details
- Can be multiple sentences for complex patterns

### code_example
- Preserve exact formatting (newlines, indentation)
- Include only if code is explicitly provided in the text
- Set to null if no code example present
- Prefer complete, runnable examples over fragments

### context
- When should this pattern be used?
- What constraints or requirements apply?
- What type of project/system benefits?

### trade_offs
- List both pros and cons
- Prefix with "Pro:" or "Con:" for clarity
- Include performance, complexity, cost considerations
- At least 1-2 trade-offs if discussed in the text

## Example Extractions

**Example 1: Pattern with code**
```json
{
  "name": "Semantic Caching",
  "problem": "High API costs from repeated similar queries to LLM endpoints",
  "solution": "Cache responses using embedding similarity instead of exact match. Compare query embeddings against cache entries to find semantically similar previous queries and return cached responses.",
  "code_example": "def get_cached_response(query, cache, threshold=0.9):\n    embedding = model.encode(query)\n    for key, value in cache.items():\n        if cosine_similarity(embedding, key) > threshold:\n            return value\n    return None",
  "context": "High-traffic LLM applications where users ask similar questions. Works best when queries have semantic overlap rather than exact duplicates.",
  "trade_offs": [
    "Pro: 40-60% cost reduction in typical workloads",
    "Con: Added latency for embedding and similarity computation",
    "Con: Cache invalidation complexity when knowledge updates"
  ],
  "confidence": 0.9
}
```

**Example 2: Pattern without code**
```json
{
  "name": "Recursive Chunking",
  "problem": "Fixed-size chunking splits content at arbitrary boundaries, losing semantic context",
  "solution": "Recursively split documents using multiple separators (paragraphs, sentences, words) to respect natural boundaries while staying within size limits.",
  "code_example": null,
  "context": "Document processing for RAG systems with structured documents containing headers, paragraphs, and lists.",
  "trade_offs": [
    "Pro: Preserves semantic coherence within chunks",
    "Pro: Respects document structure",
    "Con: More complex implementation than fixed-size",
    "Con: Variable chunk sizes may complicate batching"
  ],
  "confidence": 0.85
}
```

## Now extract patterns from this text:
