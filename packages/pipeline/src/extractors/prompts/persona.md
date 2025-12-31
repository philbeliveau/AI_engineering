# Persona Extraction Prompt

Extract role definitions and personas from the text.

## Schema:
```json
{
  "role": "Role title",
  "responsibilities": ["What they do"],
  "expertise": ["Domain expertise areas"],
  "communication_style": "How they communicate"
}
```

## Examples of Personas:
- "ML Engineer responsible for model training"
- "Data Scientist analyzing embeddings"
- "DevOps Engineer managing deployment"

Return a JSON array of persona extractions.
