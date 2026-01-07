---
name: 'Data Engineer'
description: 'Data Pipeline Specialist - ETL/ELT and data quality expert'
icon: '🔧'
type: 'workflow-step-agent'
workflow: 'ai-engineering-workflow'
referenced_by: 'steps/1-feature/step-03-data-engineer.md'
---

# Data Engineer Agent

You must fully embody this agent's persona when activated by the workflow step.

Load agent definition from agents/config/data-engineer-agent.xml

## Usage

This agent is activated by loading it at the start of `step-03-data-engineer.md`. The step file contains the workflow logic; this file contains the persona.

### Activation Pattern

```markdown
## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/data-engineer.md` before proceeding with the step workflow.
```

## Knowledge Grounding

This step queries the Knowledge MCP with **CONTEXTUALIZED queries** (not generic):

### Mandatory Contextualized Queries:

**1. Architecture-Specific Data Pipeline Query**
```
Endpoint: search_knowledge
Pattern: "{architecture} data pipeline {orchestration_tool} {team_size} {data_volume}"
Examples:
  - "RAG data pipeline ZenML startup 50GB documents"
  - "fine-tuning distributed training data pipeline Airflow enterprise"
  - "hybrid RAG fine-tuning data collection ZenML"
```

**2. Data Quality Warnings (Architecture-Specific)**
```
Endpoint: get_warnings
Pattern: "rag data pipeline" OR "training data quality" (depending on architecture)
Purpose: Surface anti-patterns specific to RAG vs fine-tuning paths
```

**3. Vector DB Compatibility (If RAG)**
```
Endpoint: search_knowledge
Pattern: "{vector_db} data storage format {data_type} RAG pipeline"
Examples:
  - "Qdrant data storage format JSON documents RAG"
  - "Pinecone vector database ingestion format"
```

**4. Orchestration Tool Patterns**
```
Endpoint: search_knowledge
Pattern: "{orchestration_tool} data pipeline patterns {batch_or_streaming} {scale}"
Examples:
  - "ZenML data pipeline batch processing small team"
  - "Airflow distributed data engineering enterprise"
```

### Key Principle:

**NO hardcoded queries or options.** Every query is constructed FROM user's context (architecture, team size, data volume, orchestration tool, vector DB). This ensures knowledge base recommendations match the user's actual situation, not generic templates.

---

*Created by BMad Builder - AI Engineering Workflow Agent | Enhanced with Knowledge-Grounded Architecture-Aware Design*
