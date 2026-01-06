# Handoff: Add Extraction Button to Streamlit App

## Goal

Add a button to the Streamlit web app that allows users to trigger knowledge extraction directly from the UI, without needing to use the command line.

## Context

The Knowledge Pipeline has two main stages:
1. **Ingestion** - Upload a document, chunk it, store in MongoDB + Qdrant (already in UI)
2. **Extraction** - Run LLM-based extraction on chunks to create structured knowledge (CLI only)

Currently, after ingesting a document via the Streamlit app, users must run extraction manually:
```bash
uv run scripts/extract.py <source_id> --hierarchical
```

We want extraction to be triggerable from the UI.

## Current State

- **Streamlit app:** `packages/pipeline/web_app.py`
- **Extraction CLI:** `packages/pipeline/scripts/extract.py`
- **Recent Sources table:** Shows ingested sources with editable titles
- **Source status field:** Available in MongoDB (`status: "complete"` after ingestion)

## Desired Behavior

1. In the Recent Sources table (or near it), add an "Extract" action for each source
2. Clicking "Extract" should:
   - Run hierarchical extraction on that source
   - Show progress/status while running
   - Display results (number of extractions created)
3. Add an "Extractions" count column to the table so that we know this source was extracted
4. Optionally allow choosing extraction types (decisions, patterns, warnings, methodology)

## Key Files

| File | Purpose |
|------|---------|
| `packages/pipeline/web_app.py` | Streamlit app to modify |
| `packages/pipeline/scripts/extract.py` | CLI that shows how to call extraction |
| `packages/pipeline/src/pipelines/extraction.py` | `ExtractionPipeline` class with `extract_hierarchical()` |
| `packages/pipeline/src/config.py` | Settings for MongoDB/Qdrant connections |

## Technical Notes

- The extraction pipeline uses `ExtractionPipeline` from `src/pipelines/extraction.py`
- Hierarchical extraction is preferred (combines chunks by chapter/section for better context)
- Extraction requires Anthropic API key (already in `.env`)
- Each extraction run can take 30-60 seconds per source depending on size

## Success Criteria

- User can trigger extraction from the Streamlit UI
- Progress feedback during extraction
- Results displayed after completion
- No CLI needed for the complete ingest → extract workflow
