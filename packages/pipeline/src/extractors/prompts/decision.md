# Decision Extraction Prompt

Extract decision points from the text - places where developers need to make choices.

## Schema:
```json
{
  "question": "The decision point question",
  "options": ["Option 1", "Option 2"],
  "considerations": ["Factor to consider 1", "Factor to consider 2"],
  "recommended_approach": "Recommended choice if explicitly stated",
  "context": "Surrounding context for the decision"
}
```

## Examples of Decision Points:
- "Should you use RAG or fine-tuning?"
- "When to choose synchronous vs asynchronous processing"
- "Trade-offs between accuracy and latency"

Return a JSON array of decision extractions.
