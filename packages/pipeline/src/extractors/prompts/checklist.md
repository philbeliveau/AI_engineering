# Checklist Extraction Prompt

Extract verification checklists from the text.

## Schema:
```json
{
  "name": "Checklist name",
  "items": [
    {
      "item": "Checklist item text",
      "required": true
    }
  ],
  "context": "When to use this checklist"
}
```

## Examples of Checklists:
- "Production deployment readiness checklist"
- "Model evaluation criteria"
- "Security review checklist"

Return a JSON array of checklist extractions.
