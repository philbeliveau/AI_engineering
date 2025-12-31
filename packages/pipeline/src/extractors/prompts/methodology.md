# Methodology Extraction Prompt

Extract step-by-step methodologies and processes from the text.

## Schema:
```json
{
  "name": "Methodology name",
  "steps": [
    {
      "order": 1,
      "title": "Step title",
      "description": "Step details",
      "tips": ["Optional tips"]
    }
  ],
  "prerequisites": ["Required before starting"],
  "outputs": ["Expected deliverables"]
}
```

## Examples of Methodologies:
- "RAG system implementation process"
- "Prompt engineering workflow"
- "Model evaluation pipeline"

Return a JSON array of methodology extractions.
