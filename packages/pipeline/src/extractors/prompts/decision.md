# Decision Extraction Prompt

Extract decision points from the text - places where developers need to make choices.

## Schema:
```json
{
  "question": "The decision point question",
  "options": ["Option 1", "Option 2"],
  "considerations": ["Factor to consider 1", "Factor to consider 2"],
  "recommended_approach": "Recommended choice if explicitly stated",
  "context": "Surrounding context for the decision",
  "confidence": 0.85
}
```

## Confidence Scoring for Decisions:
- **0.9-1.0**: Decision is explicitly stated with clear options and trade-offs
- **0.7-0.9**: Decision is clearly implied with identifiable options
- **0.5-0.7**: Decision requires inference but options are reasonable
- **Below 0.5**: Do not extract - insufficient evidence of a real decision point

## Examples of Decision Points:
- "Should you use RAG or fine-tuning?"
- "When to choose synchronous vs asynchronous processing"
- "Trade-offs between accuracy and latency"

## What Makes a Good Decision Extraction:
1. **Clear question** - Phrased as a choice the reader must make
2. **Distinct options** - At least 2 mutually exclusive alternatives
3. **Actionable considerations** - Trade-offs that help the reader decide
4. **Context** - When/where this decision applies

Return a JSON array of decision extractions.
