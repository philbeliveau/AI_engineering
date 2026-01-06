# Workflow Extraction Prompt

Extract process workflows from the text.

## What is a Workflow?

A workflow is a sequence of steps triggered by an event. In AI engineering, workflows include:
- Development workflows (e.g., "Feature implementation flow")
- Operational workflows (e.g., "Model retraining trigger")
- Review workflows (e.g., "PR review process")
- Incident workflows (e.g., "Model degradation response")

## Extraction Rules

1. Only extract workflows with clear triggers and steps
2. A workflow MUST have a name, trigger, and at least 2 steps
3. Each step has order, action, and optional outputs
4. Identify decision points in the workflow
5. Return valid JSON matching the schema below
6. If no workflows found, return ONLY: []

## IMPORTANT

You MUST respond with ONLY valid JSON, nothing else.
- If workflows exist: return a JSON array of workflow objects
- If NO workflows exist: return an empty JSON array: []
- Do NOT add any text before or after the JSON
- Do NOT explain your reasoning
- Just return the JSON array, period.

## Schema

```json
{
  "name": "Workflow Name",
  "trigger": "What initiates this workflow",
  "steps": [
    {
      "order": 1,
      "action": "What to do in this step",
      "outputs": ["Output from this step"]
    }
  ],
  "decision_points": ["Key decision point 1", "Key decision point 2"]
}
```

## Example Extraction

**Input text:**
"When model performance drops below threshold, trigger the retraining workflow. First, collect recent production data. Then, validate data quality - if quality is poor, escalate to data team. Next, fine-tune the model on new data. Run evaluation suite. If metrics improve, deploy to staging. Finally, run A/B test before production rollout."

**Extracted workflow:**
```json
{
  "name": "Model Retraining Workflow",
  "trigger": "Model performance drops below threshold",
  "steps": [
    {
      "order": 1,
      "action": "Collect recent production data",
      "outputs": ["Training dataset"]
    },
    {
      "order": 2,
      "action": "Validate data quality",
      "outputs": ["Quality report"]
    },
    {
      "order": 3,
      "action": "Fine-tune model on new data",
      "outputs": ["Retrained model"]
    },
    {
      "order": 4,
      "action": "Run evaluation suite",
      "outputs": ["Evaluation metrics"]
    },
    {
      "order": 5,
      "action": "Deploy to staging",
      "outputs": ["Staging deployment"]
    },
    {
      "order": 6,
      "action": "Run A/B test before production rollout",
      "outputs": ["A/B test results", "Production deployment"]
    }
  ],
  "decision_points": [
    "Data quality check - escalate if poor",
    "Metrics improvement check before staging deploy"
  ]
}
```

Return a JSON array of workflow extractions.
