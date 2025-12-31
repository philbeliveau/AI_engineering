# Workflow Extraction Prompt

Extract process workflows from the text.

## Schema:
```json
{
  "name": "Workflow name",
  "trigger": "What starts the workflow",
  "steps": [
    {
      "order": 1,
      "action": "What to do",
      "outputs": ["Step outputs"]
    }
  ],
  "decision_points": ["Key decision points in the workflow"]
}
```

## Examples of Workflows:
- "Document ingestion workflow"
- "Query processing workflow"
- "Model fine-tuning workflow"

Return a JSON array of workflow extractions.
