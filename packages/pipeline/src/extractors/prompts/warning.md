# Warning Extraction Prompt

Extract warnings, gotchas, and anti-patterns from the text.

## Schema:
```json
{
  "title": "Warning title",
  "description": "What the warning is about",
  "symptoms": ["How to recognize the problem"],
  "consequences": ["What happens if ignored"],
  "prevention": "How to avoid the issue"
}
```

## Examples of Warnings:
- "Context window overflow causing truncation"
- "Prompt injection vulnerabilities"
- "Embedding dimension mismatch"

Return a JSON array of warning extractions.
