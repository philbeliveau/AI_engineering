# Checklist Extraction Prompt

Extract verification checklists from the text.

## What is a Checklist?

A checklist is a list of items to verify or complete. In AI engineering, checklists include:
- Pre-deployment checks (e.g., "Model release checklist")
- Quality gates (e.g., "RAG evaluation checklist")
- Review criteria (e.g., "Prompt review checklist")
- Validation lists (e.g., "Data quality checklist")

## Extraction Rules

1. Only extract explicit checklists from the text
2. A checklist MUST have a name and at least 2 items
3. Each item should be actionable/verifiable
4. Mark items as required (true) or optional (false)
5. Include context about when to use the checklist
6. Return valid JSON matching the schema below
7. If no checklists found, return an empty array []

## Schema

```json
{
  "name": "Checklist Name",
  "items": [
    {"item": "Checklist item text", "required": true},
    {"item": "Optional item", "required": false}
  ],
  "context": "When and where to use this checklist"
}
```

## Example Extraction

**Input text:**
"Before deploying your LLM to production, verify: model latency under 500ms, error rate below 1%, input validation in place, rate limiting configured, logging enabled. Also consider: A/B testing setup, rollback procedure documented."

**Extracted checklist:**
```json
{
  "name": "LLM Production Deployment Checklist",
  "items": [
    {"item": "Model latency under 500ms", "required": true},
    {"item": "Error rate below 1%", "required": true},
    {"item": "Input validation in place", "required": true},
    {"item": "Rate limiting configured", "required": true},
    {"item": "Logging enabled", "required": true},
    {"item": "A/B testing setup", "required": false},
    {"item": "Rollback procedure documented", "required": false}
  ],
  "context": "Use before deploying LLM model to production environment"
}
```

Return a JSON array of checklist extractions.
