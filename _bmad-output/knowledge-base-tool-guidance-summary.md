# Tool Guidance Found in Knowledge Base - Quick Reference

## What's Available for Step 02 (Infrastructure Decisions)

### LLM Handbook: 257 Deployment-Specific Extractions

**10 Tools Recommended:**
- **ZenML** (54 mentions) - Pipeline orchestration, reproducibility
- **SageMaker** (54 mentions) - AWS-native training/deployment
- **MLOps frameworks** (24 mentions) - Governance, lifecycle
- **Weights & Biases** (16 mentions) - Experiment tracking, visualization
- **Comet** (10 mentions) - ML experiment platform
- **Airflow** (6 mentions) - DAG orchestration
- **Opik** (5 mentions) - LLM monitoring & evaluation
- **MLFlow** (4 mentions) - Model registry, versioning
- **Databricks** (1 mention) - Unified analytics
- **LangChain** (2 mentions) - Framework usage

### Extraction Types Available

| Type | Count | Use Case |
|------|-------|----------|
| **Workflow** | 60 | Step-by-step processes (Model Retraining, Inference Pipelines) |
| **Checklist** | 62 | Quality gates (Production Deployment, Data Validation) |
| **Pattern** | 19 | Architecture patterns (Batch Pipeline, Model Registry) |
| **Decision** | 18 | Tool selection frameworks, approach decisions |
| **Methodology** | 26 | ZenML orchestration, training/inference patterns |
| **Warning** | 57 | Common deployment pitfalls |
| **Persona** | 15 | Role definitions (DevOps, ML Engineers) |

## Specific Extraction IDs to Reference

### Workflow Templates (Copy as Examples)
```
695c3c5b7909f0f2702ef17e - Model Retraining Workflow (6 steps)
695c3c5c7909f0f2702ef185 - Content Generation Workflow (5 steps)
695c3c627909f0f2702ef196 - Training Pipeline (3 steps)
695c3c5e7909f0f2702ef18d - Inference Pipeline
```

### Production Checklists
```
695c3cc47909f0f2702ef305 - LLM Production Deployment Checklist
695c3cc27909f0f2702ef302 - Data Collection & Preparation Checklist
695c3cc67909f0f2702ef30b - Production Candidate Evaluation Checklist
```

### Infrastructure Patterns
```
695c3cbf7909f0f2702ef2f8 - Monolithic Batch Pipeline Architecture
695c3cc07909f0f2702ef2fd - Feature Pipeline Pattern
695c3ccd7909f0f2702ef320 - Model Registry Pattern
```

## How to Query for Step 02

### Get All Deployment Guidance (257 extractions)
```python
# Query the Knowledge MCP
query_params = {
    "source_id": "695c177a9ff569ca95527f62",  # LLM Handbook
    "topics": ["deployment"]
}
# Returns: Workflows, checklists, patterns, decisions, warnings
```

### Get Tool Decision Frameworks
```python
# Get decisions about tool selection
query_params = {
    "source_id": "695c177a9ff569ca95527f62",
    "type": "decision",
    "topics": ["deployment"]
}
# Returns: 18 decision frameworks for architectural choices
```

### Get Workflow Templates
```python
# Get structured workflows with steps
query_params = {
    "source_id": "695c177a9ff569ca95527f62",
    "type": "workflow",
    "topics": ["deployment", "training", "inference"]
}
# Returns: Retraining workflows, inference pipelines, etc.
```

## What's NOT in LLM Handbook (Gaps)

These areas need supplementary sources:
- Kubernetes/container orchestration details
- Cloud platform comparisons (AWS vs GCP vs Azure)
- CI/CD pipeline configuration
- Advanced monitoring/observability
- Cost optimization
- Multi-region deployment

**Supplementary sources available:**
- "LLMs in Production" (445 extractions, 20 deployment-related)
- "The3 Advantages of AI Engineering Ops" (21 extractions, focus on monitoring)

## Synthesis Approach for Step 02

1. **Show Tool Decision Tree** - Use 18 decision extractions to help users choose ZenML vs SageMaker vs Airflow
2. **Provide Workflow Templates** - Embed 3-5 deployment workflow examples from LLM Handbook
3. **Surface Quality Gates** - Link to 62 deployment checklists for validation
4. **Highlight Pitfalls** - Surface 57 warnings about common deployment mistakes
5. **Define Roles** - Use 15 persona extractions for team structure guidance

## Key Statistics

- **LLM Handbook extractions:** 1,137 (67% of entire knowledge base)
- **Deployment-specific:** 257
- **Tools mentioned:** 10
- **Extraction types:** 7 (all represented)
- **Workflow examples:** 60 structured processes
- **Decision frameworks:** 18
- **Quality checklists:** 62

## Next Steps

1. Decide which tool(s) to feature (ZenML and SageMaker have equal coverage)
2. Extract 3-5 workflow templates as examples
3. Pull deployment checklists for quality gates
4. Create decision tree using 18 decision extractions
5. Synthesize pitfalls and warnings into guidance text

---

**Data source:** MongoDB knowledge-pipeline_extractions
**Query date:** 2026-01-06
**Full report:** See knowledge-base-query-results.md for detailed breakdown
