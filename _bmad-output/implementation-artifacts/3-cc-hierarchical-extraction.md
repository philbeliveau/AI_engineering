# Story 3.CC: Hierarchical Extraction Architecture + Embedding Model Upgrade

Status: ready-for-dev

## Story

As a **builder**,
I want the extraction pipeline to use hierarchical context (chapter/section/chunk levels) AND a larger-context embedding model,
so that methodologies, workflows, decisions, and patterns are extracted with full context, resulting in higher-quality extractions that capture complete processes rather than fragments.

## Problem Statement

The current extraction system has two coupled limitations:

### Limitation 1: Embedding Model Context Window

| Model | Context | Vectors | Status |
|-------|---------|---------|--------|
| **all-MiniLM-L6-v2** (current) | 512 tokens | 384d | Limited context |
| **nomic-embed-text-v1.5** (new) | **8,192 tokens** | 768d | 16x more context |

### Limitation 2: Flat Chunk-Based Extraction

The current architecture uses **512-token chunks** for LLM extraction, which is **severely insufficient** for meaningful knowledge extraction from educational resources:

| Extraction Type | Typical Content Span | 512 Tokens Covers | Quality Risk |
|-----------------|---------------------|-------------------|--------------|
| **methodology** | 3-10 pages (multi-step process) | One step fragment | **CRITICAL** |
| **workflow** | 2-5 pages (process sequence) | Fragment only | **HIGH** |
| **decision** | 1-3 pages (context → trade-offs → rationale) | ~1 paragraph | **HIGH** |
| **pattern** | 1-2 pages (problem → solution → code) | Half the pattern | **HIGH** |
| **checklist** | 0.5-2 pages | Partial | **MEDIUM** |
| **persona** | 1-2 pages | Partial | **MEDIUM** |
| **warning** | 0.5-1 page (anti-pattern → alternative) | Might fit | **LOW** |

**Core Issue:** The extraction context window is artificially limited to embedding model constraints, despite Claude API supporting 200,000 tokens.

## Solution Overview

This story implements TWO changes:

1. **Embedding Model Upgrade:** Replace `all-MiniLM-L6-v2` (512 tokens) with `nomic-embed-text-v1.5` (8,192 tokens)
2. **Hierarchical Extraction:** Match extraction context to content scope (chapter/section/chunk levels)

```
┌─────────────────────────────────────────────────────────────────┐
│                    BEFORE (Current)                              │
├─────────────────────────────────────────────────────────────────┤
│  all-MiniLM-L6-v2 (512 tokens) ──► Chunks ──► Flat Extraction   │
│                                                                  │
│                    AFTER (This Story)                            │
├─────────────────────────────────────────────────────────────────┤
│  nomic-embed-text (8,192 tokens) ──► Chunks ──► Hierarchical    │
│                                                                  │
│  Chapter Level (8K tokens) → methodology, workflow               │
│  Section Level (4K tokens) → decision, pattern, checklist        │
│  Chunk Level (512 tokens)  → warning                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Embedding Model Decision: nomic-embed-text-v1.5

### Model Specifications

| Property | Value |
|----------|-------|
| **Model ID** | `nomic-ai/nomic-embed-text-v1.5` |
| **Context Window** | 8,192 tokens |
| **Vector Dimensions** | 768 |
| **Model Size** | ~550MB |
| **License** | Apache 2.0 (fully open source) |
| **Architecture** | Custom long-context BERT with RoPE + SwiGLU |
| **Training Data** | ~235M text pairs, multi-stage contrastive |
| **Special Feature** | Instruction prefixes for task specialization |

### Why nomic-embed-text?

| Criteria | all-MiniLM-L6-v2 | nomic-embed-text | Winner |
|----------|------------------|------------------|--------|
| Context window | 512 tokens | 8,192 tokens | nomic (16x) |
| MTEB ranking | ~100+ | Top 20 | nomic |
| Vector size | 384d | 768d | nomic (richer) |
| Cost | Free (local) | Free (local) | Tie |
| Speed | Very fast | Fast | MiniLM (slightly) |
| License | Apache 2.0 | Apache 2.0 | Tie |

### Usage Pattern

```python
from sentence_transformers import SentenceTransformer

# Load model (requires trust_remote_code for custom architecture)
model = SentenceTransformer(
    "nomic-ai/nomic-embed-text-v1.5",
    trust_remote_code=True
)

# For documents (being embedded for retrieval)
doc_embeddings = model.encode(
    ["search_document: " + text for text in documents]
)

# For queries (searching the documents)
query_embedding = model.encode(
    ["search_query: " + query]
)
```

**Important:** nomic-embed-text uses instruction prefixes:
- `search_document:` for documents being indexed
- `search_query:` for search queries
- `clustering:` for clustering tasks
- `classification:` for classification tasks

### Qdrant Configuration Update

```python
# OLD configuration
QDRANT_CONFIG = {
    "collection_name": "chunks",
    "vector_size": 384,  # all-MiniLM-L6-v2
    "distance": "Cosine",
}

# NEW configuration
QDRANT_CONFIG = {
    "collection_name": "chunks",
    "vector_size": 768,  # nomic-embed-text-v1.5
    "distance": "Cosine",
}
```

### Migration Note

Switching embedding models requires:
1. **Recreate Qdrant collection** with new vector size (768d)
2. **Re-embed all existing chunks** from MongoDB
3. **No MongoDB changes** - chunks collection stays the same

---

## Acceptance Criteria

### Hierarchical Extraction

1. **GIVEN** a document is ingested with chapter/section structure
   **WHEN** the hierarchical extractor processes it
   **THEN** methodology and workflow extractions are run at chapter level (up to 8,000 tokens)

2. **GIVEN** a document with section headings
   **WHEN** the hierarchical extractor processes it
   **THEN** decision, pattern, checklist, and persona extractions are run at section level (up to 4,000 tokens)

3. **GIVEN** individual 512-token chunks
   **WHEN** the warning extractor processes them
   **THEN** warnings are still extracted at chunk level (512 tokens)

4. **GIVEN** any new extraction is saved
   **WHEN** the extraction is stored
   **THEN** it includes `context_level`, `context_id`, and `chunk_ids[]` fields for traceability

5. **GIVEN** existing extractions in MongoDB
   **WHEN** the MCP server queries them
   **THEN** both old (schema_version 1.0.0) and new (schema_version 1.1.0) extractions work correctly

6. **GIVEN** the extraction CLI is run
   **WHEN** a source is processed
   **THEN** the summary shows extraction counts by level (chapter, section, chunk)

### Embedding Model Upgrade

7. **GIVEN** the chunker processes a document
   **WHEN** embeddings are generated
   **THEN** nomic-embed-text-v1.5 is used with `search_document:` prefix

8. **GIVEN** the MCP server receives a search query
   **WHEN** the query is embedded
   **THEN** nomic-embed-text-v1.5 is used with `search_query:` prefix

9. **GIVEN** a new Qdrant collection is created
   **WHEN** the collection is configured
   **THEN** vector_size is 768 (not 384)

10. **GIVEN** existing chunks in MongoDB
    **WHEN** a re-embedding script is run
    **THEN** all chunks are re-embedded with the new model and stored in Qdrant

---

## Tasks / Subtasks

### Part A: Embedding Model Upgrade

- [ ] **Task 0: Update Embedding Configuration** (AC: #7, #8, #9)
  - [ ] 0.1: Update `EMBED_MODEL_ID` constant in `src/processors/chunker.py` to `nomic-ai/nomic-embed-text-v1.5`
  - [ ] 0.2: Update `EMBED_MODEL_ID` in `src/config.py` (if exists) or create centralized config
  - [ ] 0.3: Update Qdrant vector_size from 384 to 768 in storage configuration
  - [ ] 0.4: Add `trust_remote_code=True` to SentenceTransformer initialization
  - [ ] 0.5: Implement instruction prefix handling (`search_document:` / `search_query:`)
  - [ ] 0.6: Update `count_tokens()` to use nomic tokenizer
  - [ ] 0.7: Write unit tests for new embedding model

- [ ] **Task 0.5: Create Re-embedding Script** (AC: #10)
  - [ ] 0.5.1: Create `scripts/reembed.py` to re-embed all chunks with new model
  - [ ] 0.5.2: Delete old Qdrant collection and create new with 768d vectors
  - [ ] 0.5.3: Iterate through MongoDB chunks and generate new embeddings
  - [ ] 0.5.4: Upsert new vectors to Qdrant with existing chunk IDs
  - [ ] 0.5.5: Add progress bar and logging
  - [ ] 0.5.6: Test script with small batch first

- [ ] **Task 0.7: Update MCP Server Embedding** (AC: #8)
  - [ ] 0.7.1: Update `packages/mcp-server/src/config.py` with new model ID
  - [ ] 0.7.2: Ensure query embedding uses `search_query:` prefix
  - [ ] 0.7.3: Update Qdrant client to expect 768d vectors
  - [ ] 0.7.4: Test semantic search with new embeddings

### Part B: Hierarchical Extraction

- [ ] **Task 1: Create Extraction Level Configuration** (AC: #1, #2, #3)
  - [ ] 1.1: Create `src/extractors/config.py` with `ExtractionLevel` enum (CHAPTER, SECTION, CHUNK)
  - [ ] 1.2: Create `ExtractionLevelConfig` Pydantic model (level, extraction_types, max_tokens, combination_strategy)
  - [ ] 1.3: Define `EXTRACTION_LEVEL_CONFIG` mapping each level to its extractors and token budgets
  - [ ] 1.4: Write unit tests for configuration models

- [ ] **Task 2: Create Document Hierarchy Builder** (AC: #1, #2)
  - [ ] 2.1: Create `src/extractors/hierarchy.py` with `DocumentHierarchy`, `ChapterNode`, `SectionNode` dataclasses
  - [ ] 2.2: Implement `build_hierarchy(chunks, source_id)` function that groups chunks by chapter/section using position metadata
  - [ ] 2.3: Implement `_generate_id()` for stable chapter/section IDs
  - [ ] 2.4: Write unit tests for hierarchy building (including edge cases: missing position metadata, unknown chapters)

- [ ] **Task 3: Create Chunk Combiner Utility** (AC: #1, #2)
  - [ ] 3.1: Implement `_combine_chunks(chunks, max_tokens, strategy)` method in hierarchy module
  - [ ] 3.2: Implement "truncate" strategy (cut at token limit)
  - [ ] 3.3: Implement "summary_if_exceeded" strategy (placeholder for future summarization)
  - [ ] 3.4: Sort chunks by chunk_index for proper ordering
  - [ ] 3.5: Write unit tests for chunk combination

- [ ] **Task 4: Update ExtractionBase Model** (AC: #4, #5)
  - [ ] 4.1: Add `context_level: ExtractionLevel = ExtractionLevel.CHUNK` field to `ExtractionBase`
  - [ ] 4.2: Add `context_id: str = ""` field (chapter_id, section_id, or chunk_id)
  - [ ] 4.3: Add `chunk_ids: list[str] = Field(default_factory=list)` field
  - [ ] 4.4: Update `schema_version` to `"1.1.0"` for new extractions
  - [ ] 4.5: Ensure backward compatibility (old extractions default to CHUNK level)
  - [ ] 4.6: Write unit tests for model validation

- [ ] **Task 5: Update BaseExtractor Interface** (AC: #1, #2, #3)
  - [ ] 5.1: Add new async extract signature: `async def extract(content, source_id, context_level, context_id, chunk_ids=None)`
  - [ ] 5.2: Keep old signature as deprecated wrapper for backward compatibility
  - [ ] 5.3: Update `_validate_extraction()` to set context fields
  - [ ] 5.4: Update all 7 existing extractors to use new signature (decision, pattern, warning, methodology, checklist, persona, workflow)
  - [ ] 5.5: Write tests for new interface

- [ ] **Task 6: Create HierarchicalExtractor Orchestrator** (AC: #1, #2, #3, #6)
  - [ ] 6.1: Create `src/extractors/hierarchical.py` with `HierarchicalExtractor` class
  - [ ] 6.2: Implement `extract_document(chunks, source_id)` main entry point
  - [ ] 6.3: Implement `_extract_chapter_level()` for methodology/workflow (8,000 token budget)
  - [ ] 6.4: Implement `_extract_section_level()` for decision/pattern/checklist/persona (4,000 token budget)
  - [ ] 6.5: Implement `_extract_chunk_level()` for warning (512 token budget)
  - [ ] 6.6: Add structured logging for each extraction level
  - [ ] 6.7: Write comprehensive unit tests

- [ ] **Task 7: Update Extraction Pipeline** (AC: #1, #2, #3, #6)
  - [ ] 7.1: Modify `ExtractionPipeline` to use `HierarchicalExtractor` instead of flat chunk iteration
  - [ ] 7.2: Update progress display to show chapter/section/chunk progress
  - [ ] 7.3: Update `ExtractionPipelineResult` to include counts by level
  - [ ] 7.4: Write integration tests against real MongoDB/Qdrant

- [ ] **Task 8: Update Extraction Storage** (AC: #4)
  - [ ] 8.1: Ensure `ExtractionStorage.save_extraction()` handles new fields
  - [ ] 8.2: Update Qdrant payload to include `context_level` for filtering
  - [ ] 8.3: Write tests for storage with new schema

- [ ] **Task 9: Backward Compatibility Verification** (AC: #5)
  - [ ] 9.1: Run MCP server against existing extractions to verify queries work
  - [ ] 9.2: Document migration notes (no data migration required - schema versioning handles it)
  - [ ] 9.3: Write integration test loading old + new extractions

- [ ] **Task 10: Run Full Test Suite & Documentation** (AC: all)
  - [ ] 10.1: Run `uv run pytest` - all tests pass
  - [ ] 10.2: Run `uv run ruff check .` - no linting errors
  - [ ] 10.3: Update CLAUDE.md with new embedding model info
  - [ ] 10.4: Manually test with a real PDF to verify extraction quality improvement

---

## Dev Notes

### Architecture Compliance

This story implements:
1. **Embedding Model Upgrade** - Switch from all-MiniLM-L6-v2 (512 tokens, 384d) to nomic-embed-text-v1.5 (8,192 tokens, 768d)
2. **Hierarchical Extraction** - As described in `_bmad-output/architecture-issue-chunk-context-extraction.md`

Key architectural decisions:
- **Single `chunks` Qdrant collection** - Recreate with 768d vectors
- **MongoDB extractions collection** - New fields added to existing schema with version bump
- **Backward compatible** - Old extractions (1.0.0) continue to work, new extractions (1.1.0) have enhanced metadata

### nomic-embed-text Implementation Details

**Installation:**
```bash
cd packages/pipeline
uv add sentence-transformers
# Model will auto-download on first use (~550MB)
```

**Centralized Embedding Config:**
```python
# packages/pipeline/src/config.py (or similar)

EMBEDDING_CONFIG = {
    "model_id": "nomic-ai/nomic-embed-text-v1.5",
    "vector_size": 768,
    "max_tokens": 8192,
    "trust_remote_code": True,
    "prefixes": {
        "document": "search_document: ",
        "query": "search_query: ",
        "clustering": "clustering: ",
        "classification": "classification: ",
    }
}
```

**Embedding Wrapper Class:**
```python
# packages/pipeline/src/processors/embedder.py

from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_CONFIG

class NomicEmbedder:
    """Wrapper for nomic-embed-text-v1.5 with instruction prefixes."""

    def __init__(self):
        self.model = SentenceTransformer(
            EMBEDDING_CONFIG["model_id"],
            trust_remote_code=True
        )
        self.prefixes = EMBEDDING_CONFIG["prefixes"]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents for indexing."""
        prefixed = [self.prefixes["document"] + t for t in texts]
        return self.model.encode(prefixed).tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed query for search."""
        prefixed = self.prefixes["query"] + query
        return self.model.encode([prefixed])[0].tolist()

    def count_tokens(self, text: str) -> int:
        """Count tokens using model's tokenizer."""
        return len(self.model.tokenizer.encode(text))
```

### Files to Create/Modify

**New Files (Embedding):**
| File | Purpose |
|------|---------|
| `src/processors/embedder.py` | NomicEmbedder wrapper class |
| `scripts/reembed.py` | Re-embedding migration script |

**New Files (Hierarchical):**
| File | Purpose |
|------|---------|
| `src/extractors/config.py` | ExtractionLevel enum, ExtractionLevelConfig, EXTRACTION_LEVEL_CONFIG mapping |
| `src/extractors/hierarchy.py` | DocumentHierarchy, ChapterNode, SectionNode, build_hierarchy() |
| `src/extractors/hierarchical.py` | HierarchicalExtractor orchestrator class |
| `tests/test_extractors/test_config.py` | Config tests |
| `tests/test_extractors/test_hierarchy.py` | Hierarchy building tests |
| `tests/test_extractors/test_hierarchical.py` | HierarchicalExtractor tests |
| `tests/test_processors/test_embedder.py` | Embedder tests |

**Files to Modify:**
| File | Changes |
|------|---------|
| `src/config.py` | Add EMBEDDING_CONFIG |
| `src/processors/chunker.py` | Update EMBED_MODEL_ID, use NomicEmbedder |
| `src/storage/qdrant.py` | Update vector_size to 768 |
| `src/extractors/base.py` | Add ExtractionLevel, update ExtractionBase, update BaseExtractor.extract() |
| `src/extractors/decision_extractor.py` | Adapt to new extract() signature |
| `src/extractors/pattern_extractor.py` | Adapt to new extract() signature |
| `src/extractors/warning_extractor.py` | Adapt to new extract() signature |
| `src/extractors/methodology_extractor.py` | Adapt to new extract() signature |
| `src/extractors/checklist_extractor.py` | Adapt to new extract() signature |
| `src/extractors/persona_extractor.py` | Adapt to new extract() signature |
| `src/extractors/workflow_extractor.py` | Adapt to new extract() signature |
| `src/extraction/pipeline.py` | Use HierarchicalExtractor |
| `src/storage/extraction_storage.py` | Handle new context fields |
| `packages/mcp-server/src/config.py` | Update embedding model for queries |
| `packages/mcp-server/src/storage/qdrant.py` | Update vector_size to 768 |

### Token Budget Configuration

```python
EXTRACTION_LEVEL_CONFIG = {
    ExtractionLevel.CHAPTER: ExtractionLevelConfig(
        level=ExtractionLevel.CHAPTER,
        extraction_types=["methodology", "workflow"],
        max_tokens=8000,
        combination_strategy="summary_if_exceeded",
    ),
    ExtractionLevel.SECTION: ExtractionLevelConfig(
        level=ExtractionLevel.SECTION,
        extraction_types=["decision", "pattern", "checklist", "persona"],
        max_tokens=4000,
        combination_strategy="truncate",
    ),
    ExtractionLevel.CHUNK: ExtractionLevelConfig(
        level=ExtractionLevel.CHUNK,
        extraction_types=["warning"],
        max_tokens=512,
        combination_strategy="none",
    ),
}
```

### Position Metadata Already Available

The `DoclingChunker` already extracts position metadata from documents:

```python
position = {
    "chunk_index": 0,
    "headings": ["Chapter 5: RAG Architecture", "5.2 Retrieval Strategies"],
    "chapter": "Chapter 5: RAG Architecture",
    "section": "5.2 Retrieval Strategies",
    "page": 127,
}
```

This is used by `build_hierarchy()` to group chunks.

### Re-embedding Script Template

```python
# packages/pipeline/scripts/reembed.py
"""Re-embed all chunks with nomic-embed-text-v1.5."""

import asyncio
from rich.progress import Progress
from src.processors.embedder import NomicEmbedder
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantClient
from src.config import EMBEDDING_CONFIG

async def reembed_all():
    mongo = MongoDBClient()
    qdrant = QdrantClient()
    embedder = NomicEmbedder()

    # 1. Recreate Qdrant collection with new vector size
    await qdrant.delete_collection("chunks")
    await qdrant.create_collection(
        name="chunks",
        vector_size=EMBEDDING_CONFIG["vector_size"],  # 768
    )

    # 2. Load all chunks from MongoDB
    chunks = list(mongo.chunks.find({}))

    # 3. Re-embed in batches
    batch_size = 100
    with Progress() as progress:
        task = progress.add_task("Re-embedding...", total=len(chunks))

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c["content"] for c in batch]
            ids = [str(c["_id"]) for c in batch]

            # Embed with document prefix
            vectors = embedder.embed_documents(texts)

            # Upsert to Qdrant
            await qdrant.upsert_batch(
                collection="chunks",
                ids=ids,
                vectors=vectors,
                payloads=[{"source_id": c["source_id"]} for c in batch]
            )

            progress.update(task, advance=len(batch))

    print(f"Re-embedded {len(chunks)} chunks with nomic-embed-text-v1.5")

if __name__ == "__main__":
    asyncio.run(reembed_all())
```

### Testing Standards Summary

- Unit tests: Mock LLM client and embedding model, use sample chunks
- Integration tests: Run against real MongoDB Atlas + Qdrant Cloud
- Mark integration tests with `@pytest.mark.integration`
- All async tests require `@pytest.mark.asyncio`

### Cost Analysis

| Change | One-Time Cost | Runtime Cost |
|--------|---------------|--------------|
| Embedding model upgrade | Re-embed all chunks (~minutes) | Slightly slower embedding |
| Hierarchical extraction | Re-extract all sources (~$$) | No change |
| MCP queries | None | Zero API cost (unchanged) |

**Note:** Both embedding and extraction are ONE-TIME costs during ingestion. MCP queries remain ZERO API cost.

---

## References

- [Source: _bmad-output/architecture-issue-chunk-context-extraction.md] - Full hierarchical extraction architecture
- [Source: nomic-ai/nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) - Embedding model documentation
- [Source: _bmad-output/architecture.md#Data-Architecture] - MongoDB/Qdrant collection patterns
- [Source: _bmad-output/project-context.md#Qdrant-Rich-Payload-Requirements] - Payload field requirements
- [Source: packages/pipeline/src/extractors/base.py] - Current BaseExtractor interface
- [Source: packages/pipeline/src/processors/chunker.py] - DoclingChunker with position metadata
- [Source: packages/pipeline/src/extraction/pipeline.py] - Current extraction orchestration

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### Change Log

- 2026-01-04: Added embedding model upgrade (nomic-embed-text-v1.5) to story scope
- 2026-01-04: Added Tasks 0, 0.5, 0.7 for embedding model changes
- 2026-01-04: Added acceptance criteria #7-#10 for embedding model
- 2026-01-04: Added NomicEmbedder wrapper class specification
- 2026-01-04: Added re-embedding script template

### File List

