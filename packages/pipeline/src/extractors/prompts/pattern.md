# Pattern Extraction Prompt

Extract reusable patterns from the text - solutions to common problems.

## Schema:
```json
{
  "name": "Pattern name",
  "problem": "Problem it solves",
  "solution": "Solution approach",
  "code_example": "Code snippet if provided",
  "context": "When to use this pattern",
  "trade_offs": ["Pro/con 1", "Pro/con 2"]
}
```

## Examples of Patterns:
- "Retrieval-Augmented Generation"
- "Chain of Thought Prompting"
- "Embedding-based similarity search"

Return a JSON array of pattern extractions.
