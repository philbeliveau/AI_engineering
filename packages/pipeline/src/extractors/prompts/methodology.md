# Methodology Extraction Prompt

Extract step-by-step methodologies and processes from the text.

## What is a Methodology?

A methodology is a structured process with ordered steps. In AI engineering, methodologies include:
- Implementation processes (e.g., "How to build a RAG system")
- Evaluation frameworks (e.g., "LLM output quality assessment")
- Development workflows (e.g., "Fine-tuning preparation steps")
- Design processes (e.g., "Prompt engineering methodology")

## Extraction Rules

1. Only extract methodologies with clear, ordered steps
2. A methodology MUST have a name and at least 2 steps
3. Each step MUST have order, title, and description
4. Capture prerequisites (what must be done/known before starting)
5. Capture outputs (what the methodology produces)
6. Return valid JSON matching the schema below
7. If no methodologies found, return an empty array []

## Schema

```json
{
  "name": "Methodology Name",
  "steps": [
    {
      "order": 1,
      "title": "Step Title",
      "description": "Detailed description of what to do",
      "tips": ["Optional helpful tip"]
    }
  ],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
  "outputs": ["Output/deliverable 1", "Output/deliverable 2"]
}
```

## Example Extraction

**Input text:**
"Building a RAG system requires several key steps. First, prepare your document corpus by collecting and cleaning your source documents. Next, implement chunking - split documents into semantically coherent pieces of 500-1000 tokens. Third, generate embeddings using a model like all-MiniLM-L6-v2. Fourth, store vectors in a database like Qdrant. Finally, implement retrieval with reranking for quality results. Before starting, ensure you have access to your document corpus and have chosen your embedding model. The result is a working retrieval pipeline."

**Extracted methodology:**
```json
{
  "name": "RAG System Implementation",
  "steps": [
    {
      "order": 1,
      "title": "Prepare Document Corpus",
      "description": "Collect and clean source documents for processing",
      "tips": []
    },
    {
      "order": 2,
      "title": "Implement Chunking",
      "description": "Split documents into semantically coherent pieces of 500-1000 tokens",
      "tips": ["Keep chunks semantically coherent"]
    },
    {
      "order": 3,
      "title": "Generate Embeddings",
      "description": "Use embedding model like all-MiniLM-L6-v2 to create vector representations",
      "tips": []
    },
    {
      "order": 4,
      "title": "Store Vectors",
      "description": "Store embeddings in vector database like Qdrant",
      "tips": []
    },
    {
      "order": 5,
      "title": "Implement Retrieval",
      "description": "Build retrieval pipeline with reranking for quality results",
      "tips": ["Add reranking for better quality"]
    }
  ],
  "prerequisites": [
    "Access to document corpus",
    "Embedding model selected"
  ],
  "outputs": [
    "Working retrieval pipeline"
  ]
}
```

Return a JSON array of methodology extractions.
