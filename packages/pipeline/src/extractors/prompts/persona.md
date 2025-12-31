# Persona Extraction Prompt

Extract role definitions and personas from the text.

## What is a Persona?

A persona is a role definition that can be used to create AI agents. In AI engineering, personas include:
- Technical roles (e.g., "ML Engineer", "Data Scientist")
- Domain experts (e.g., "RAG Specialist", "Prompt Engineer")
- Process roles (e.g., "Code Reviewer", "QA Engineer")
- Stakeholder views (e.g., "End User", "Product Owner")

## Extraction Rules

1. Only extract personas explicitly described in the text
2. A persona MUST have a clear role title
3. Include responsibilities (what they do)
4. Include expertise areas (what they know)
5. Include communication style if described
6. Return valid JSON matching the schema below
7. If no personas found, return an empty array []

## Schema

```json
{
  "role": "Role Title",
  "responsibilities": ["Responsibility 1", "Responsibility 2"],
  "expertise": ["Domain expertise 1", "Domain expertise 2"],
  "communication_style": "How they communicate (formal, technical, etc.)"
}
```

## Example Extraction

**Input text:**
"The RAG Specialist is responsible for designing and implementing retrieval-augmented generation systems. They need deep expertise in embedding models, vector databases, and chunking strategies. They should also understand query optimization and reranking techniques. They communicate technically with development teams and translate complex concepts for stakeholders."

**Extracted persona:**
```json
{
  "role": "RAG Specialist",
  "responsibilities": [
    "Design retrieval-augmented generation systems",
    "Implement RAG pipelines",
    "Optimize query and retrieval performance"
  ],
  "expertise": [
    "Embedding models",
    "Vector databases",
    "Chunking strategies",
    "Query optimization",
    "Reranking techniques"
  ],
  "communication_style": "Technical with development teams, translates complex concepts for stakeholders"
}
```

Return a JSON array of persona extractions.
