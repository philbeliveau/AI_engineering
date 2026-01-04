# Hierarchical Extraction Architecture

**Status:** Approved for Implementation
**Priority:** High
**Discovered:** 2026-01-04
**Decision:** 2026-01-04
**Component:** Extraction Pipeline (`packages/pipeline/src/extractors/`)

---

## Problem Statement

The current architecture uses **512-token chunks** for both vector embeddings AND LLM extraction. While 512 tokens is appropriate for the embedding model (`all-MiniLM-L6-v2`), it is **severely insufficient** for meaningful knowledge extraction from educational resources and technical books.

**Core Issue:** The extraction context window is artificially limited to embedding model constraints, despite Claude API supporting 200,000 tokens.

### Current Architecture (Flawed)

```
PDF/Markdown → DoclingAdapter → Chunks (512 tokens) → Embeddings → Qdrant
                                       ↓
                               Extractors (see only 512 tokens)
                                       ↓
                               MongoDB (fragmented extractions)
```

### The Constraint Chain

| Layer | Token Limit | Why |
|-------|-------------|-----|
| `all-MiniLM-L6-v2` | 512 | Model's max_position_embeddings |
| `DoclingChunker` | 512 | Matches embedding model |
| `BaseExtractor.extract()` | 512 | Inherits chunk size (**design flaw**) |
| Claude API | 200,000 | **Unused capacity** |

---

## Impact Analysis

### What 512 Tokens Actually Contains

- ~350-400 words
- ~1-2 paragraphs
- Roughly half a book page

### Extraction Type Requirements vs Current Reality

| Extractor | Typical Content Span | 512 Tokens Covers | Quality Risk |
|-----------|---------------------|-------------------|--------------|
| **methodology** | 3-10 pages (multi-step process) | One step fragment | **CRITICAL** |
| **workflow** | 2-5 pages (process sequence) | Fragment only | **HIGH** |
| **decision** | 1-3 pages (context → trade-offs → rationale) | ~1 paragraph | **HIGH** |
| **pattern** | 1-2 pages (problem → solution → code) | Half the pattern | **HIGH** |
| **checklist** | 0.5-2 pages | Partial | **MEDIUM** |
| **persona** | 1-2 pages | Partial | **MEDIUM** |
| **warning** | 0.5-1 page (anti-pattern → alternative) | Might fit | **LOW** |

---

## Solution: Hierarchical Extraction

### Core Concept

**Decouple extraction context from embedding chunk size.** Match each extraction type to its natural document scope:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL EXTRACTION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CHAPTER LEVEL (5,000-10,000 tokens)                            │
│  └── methodology, workflow                                       │
│                                                                  │
│  SECTION LEVEL (2,000-4,000 tokens)                             │
│  └── decision, pattern, checklist, persona                       │
│                                                                  │
│  CHUNK LEVEL (512 tokens)                                        │
│  └── warning                                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      DOCUMENT                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   CHAPTER                                  │  │
│  │                                                            │  │
│  │   HierarchicalExtractor.extract_chapter()                  │  │
│  │   → methodology_extractor (chapter summary)                │  │
│  │   → workflow_extractor (chapter summary)                   │  │
│  │                                                            │  │
│  │  ┌────────────────────┐  ┌────────────────────┐           │  │
│  │  │      SECTION       │  │      SECTION       │           │  │
│  │  │                    │  │                    │           │  │
│  │  │ extract_section()  │  │ extract_section()  │           │  │
│  │  │ → decision_extr    │  │ → pattern_extr     │           │  │
│  │  │ → pattern_extr     │  │ → checklist_extr   │           │  │
│  │  │ → checklist_extr   │  │ → persona_extr     │           │  │
│  │  │ → persona_extr     │  │                    │           │  │
│  │  │                    │  │                    │           │  │
│  │  │ ┌──────┐ ┌──────┐ │  │ ┌──────┐ ┌──────┐ │           │  │
│  │  │ │CHUNK │ │CHUNK │ │  │ │CHUNK │ │CHUNK │ │           │  │
│  │  │ │      │ │      │ │  │ │      │ │      │ │           │  │
│  │  │ │warn_ │ │warn_ │ │  │ │warn_ │ │warn_ │ │           │  │
│  │  │ │extr  │ │extr  │ │  │ │extr  │ │extr  │ │           │  │
│  │  │ └──────┘ └──────┘ │  │ └──────┘ └──────┘ │           │  │
│  │  └────────────────────┘  └────────────────────┘           │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Extraction Level Specifications

### Level 1: Chapter-Level Extraction

**Scope:** Full chapter content or chapter summary
**Token Budget:** 5,000 - 10,000 tokens
**Extraction Types:** `methodology`, `workflow`

**Rationale:** Methodologies and workflows are inherently chapter-spanning. A methodology like "How to implement RAG" includes:
- Prerequisites
- Multiple ordered steps
- Examples for each step
- Expected outputs

This cannot be captured from 512-token fragments.

**Implementation:**

```python
async def extract_chapter_level(
    self,
    source_id: str,
    chapter_id: str,
    chapter_chunks: list[Chunk],
) -> list[ExtractionResult]:
    """Extract methodology and workflow from chapter context."""

    # Combine chapter chunks up to token budget
    chapter_text = self._combine_chunks(
        chunks=chapter_chunks,
        max_tokens=8000,
        strategy="summary_if_exceeded"
    )

    results = []

    # Extract methodologies
    methodology_results = await self.methodology_extractor.extract(
        content=chapter_text,
        source_id=source_id,
        context_level="chapter",
        context_id=chapter_id,
    )
    results.extend(methodology_results)

    # Extract workflows
    workflow_results = await self.workflow_extractor.extract(
        content=chapter_text,
        source_id=source_id,
        context_level="chapter",
        context_id=chapter_id,
    )
    results.extend(workflow_results)

    return results
```

### Level 2: Section-Level Extraction

**Scope:** Full section content (H2 heading scope)
**Token Budget:** 2,000 - 4,000 tokens
**Extraction Types:** `decision`, `pattern`, `checklist`, `persona`

**Rationale:** Decisions and patterns are typically section-scoped. A decision like "RAG vs Fine-tuning" includes:
- Context/problem statement
- Option A with pros/cons
- Option B with pros/cons
- Recommendation with rationale

This fits naturally within a section (2-4 pages).

**Implementation:**

```python
async def extract_section_level(
    self,
    source_id: str,
    section_id: str,
    section_chunks: list[Chunk],
) -> list[ExtractionResult]:
    """Extract decisions, patterns, checklists, personas from section context."""

    # Combine section chunks
    section_text = self._combine_chunks(
        chunks=section_chunks,
        max_tokens=4000,
        strategy="truncate"
    )

    results = []

    # Run section-level extractors
    for extractor in [
        self.decision_extractor,
        self.pattern_extractor,
        self.checklist_extractor,
        self.persona_extractor,
    ]:
        extraction_results = await extractor.extract(
            content=section_text,
            source_id=source_id,
            context_level="section",
            context_id=section_id,
        )
        results.extend(extraction_results)

    return results
```

### Level 3: Chunk-Level Extraction

**Scope:** Individual chunk (512 tokens)
**Token Budget:** 512 tokens
**Extraction Types:** `warning`

**Rationale:** Warnings are often self-contained: "Don't do X because Y. Do Z instead." This typically fits within a single paragraph/chunk.

**Implementation:**

```python
async def extract_chunk_level(
    self,
    source_id: str,
    chunk: Chunk,
) -> list[ExtractionResult]:
    """Extract warnings from individual chunk."""

    return await self.warning_extractor.extract(
        content=chunk.content,
        source_id=source_id,
        chunk_id=chunk.id,
        context_level="chunk",
        context_id=chunk.id,
    )
```

---

## Extraction Level Configuration

```python
# packages/pipeline/src/extractors/config.py

from enum import Enum
from pydantic import BaseModel, Field

class ExtractionLevel(str, Enum):
    """Document hierarchy level for extraction."""
    CHAPTER = "chapter"
    SECTION = "section"
    CHUNK = "chunk"

class ExtractionLevelConfig(BaseModel):
    """Configuration for extraction at each level."""
    level: ExtractionLevel
    extraction_types: list[str]
    max_tokens: int
    combination_strategy: str  # "truncate", "summary_if_exceeded", "sliding_window"

# Default configuration mapping
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

---

## Interface Changes

### BaseExtractor Changes

Current signature (to be deprecated):

```python
# OLD - packages/pipeline/src/extractors/base.py
@abstractmethod
def extract(
    self,
    chunk_content: str,
    chunk_id: str,
    source_id: str,
) -> list[ExtractionResult]:
```

New signature:

```python
# NEW - packages/pipeline/src/extractors/base.py
@abstractmethod
async def extract(
    self,
    content: str,
    source_id: str,
    context_level: ExtractionLevel,
    context_id: str,  # chapter_id, section_id, or chunk_id
    chunk_ids: list[str] | None = None,  # For attribution to original chunks
) -> list[ExtractionResult]:
```

### ExtractionBase Model Changes

Add context tracking fields:

```python
class ExtractionBase(BaseModel):
    # Existing fields
    id: str = ""
    source_id: str
    chunk_id: str  # Keep for backward compatibility
    type: ExtractionType
    topics: list[str] = Field(default_factory=list)
    schema_version: str = "1.1.0"  # Bump version
    extracted_at: datetime
    confidence: float

    # NEW: Hierarchical context fields
    context_level: ExtractionLevel = ExtractionLevel.CHUNK
    context_id: str = ""  # chapter_id, section_id, or chunk_id
    chunk_ids: list[str] = Field(default_factory=list)  # All chunks used for extraction
```

---

## Document Structure Detection

### Leveraging Existing Position Metadata

The `DoclingChunker` already extracts position metadata:

```python
position = {
    "chunk_index": 0,
    "headings": ["Chapter 5: RAG Architecture", "5.2 Retrieval Strategies"],
    "chapter": "Chapter 5: RAG Architecture",
    "section": "5.2 Retrieval Strategies",
    "page": 127,
}
```

### Building Document Hierarchy

```python
# packages/pipeline/src/extractors/hierarchy.py

from collections import defaultdict
from dataclasses import dataclass

@dataclass
class DocumentHierarchy:
    """Represents document structure for hierarchical extraction."""
    source_id: str
    chapters: dict[str, "ChapterNode"]

@dataclass
class ChapterNode:
    """Chapter in document hierarchy."""
    chapter_id: str
    title: str
    sections: dict[str, "SectionNode"]
    chunks: list[Chunk]

@dataclass
class SectionNode:
    """Section within a chapter."""
    section_id: str
    title: str
    chunks: list[Chunk]

def build_hierarchy(chunks: list[Chunk], source_id: str) -> DocumentHierarchy:
    """Build document hierarchy from chunks using position metadata."""

    chapters: dict[str, ChapterNode] = defaultdict(
        lambda: ChapterNode(chapter_id="", title="", sections={}, chunks=[])
    )

    for chunk in chunks:
        position = chunk.position or {}
        chapter_title = position.get("chapter", "Unknown Chapter")
        section_title = position.get("section", "Unknown Section")

        # Generate stable IDs
        chapter_id = _generate_id(source_id, chapter_title)
        section_id = _generate_id(source_id, chapter_title, section_title)

        # Build hierarchy
        if chapter_id not in chapters:
            chapters[chapter_id] = ChapterNode(
                chapter_id=chapter_id,
                title=chapter_title,
                sections={},
                chunks=[],
            )

        chapters[chapter_id].chunks.append(chunk)

        if section_id not in chapters[chapter_id].sections:
            chapters[chapter_id].sections[section_id] = SectionNode(
                section_id=section_id,
                title=section_title,
                chunks=[],
            )

        chapters[chapter_id].sections[section_id].chunks.append(chunk)

    return DocumentHierarchy(source_id=source_id, chapters=dict(chapters))

def _generate_id(*parts: str) -> str:
    """Generate stable ID from parts."""
    import hashlib
    combined = "|".join(parts)
    return hashlib.sha256(combined.encode()).hexdigest()[:24]
```

---

## HierarchicalExtractor Implementation

```python
# packages/pipeline/src/extractors/hierarchical.py

from typing import Optional
import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionResult,
    ExtractionLevel,
    ExtractorConfig,
)
from src.extractors.hierarchy import DocumentHierarchy, build_hierarchy
from src.extractors.config import EXTRACTION_LEVEL_CONFIG
from src.models.chunk import Chunk

logger = structlog.get_logger()

class HierarchicalExtractor:
    """Orchestrates extraction at appropriate document hierarchy levels.

    This class coordinates multiple extractors, running each at its
    optimal context level (chapter, section, or chunk).

    Example:
        extractor = HierarchicalExtractor(extractors={
            "methodology": methodology_extractor,
            "decision": decision_extractor,
            "warning": warning_extractor,
            ...
        })

        results = await extractor.extract_document(
            chunks=chunks,
            source_id="source-123",
        )
    """

    def __init__(
        self,
        extractors: dict[str, BaseExtractor],
        config: Optional[dict[ExtractionLevel, ExtractionLevelConfig]] = None,
    ):
        self.extractors = extractors
        self.config = config or EXTRACTION_LEVEL_CONFIG

        logger.info(
            "hierarchical_extractor_initialized",
            extractors=list(extractors.keys()),
            levels=list(self.config.keys()),
        )

    async def extract_document(
        self,
        chunks: list[Chunk],
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract knowledge from document using hierarchical approach.

        Args:
            chunks: All chunks from the document, ordered by position.
            source_id: Source document ID.

        Returns:
            All extraction results from all levels.
        """
        # Build document hierarchy
        hierarchy = build_hierarchy(chunks, source_id)

        all_results: list[ExtractionResult] = []

        # Level 1: Chapter-level extraction
        chapter_results = await self._extract_chapter_level(hierarchy)
        all_results.extend(chapter_results)

        # Level 2: Section-level extraction
        section_results = await self._extract_section_level(hierarchy)
        all_results.extend(section_results)

        # Level 3: Chunk-level extraction
        chunk_results = await self._extract_chunk_level(chunks, source_id)
        all_results.extend(chunk_results)

        logger.info(
            "hierarchical_extraction_complete",
            source_id=source_id,
            total_results=len(all_results),
            chapter_results=len(chapter_results),
            section_results=len(section_results),
            chunk_results=len(chunk_results),
        )

        return all_results

    async def _extract_chapter_level(
        self,
        hierarchy: DocumentHierarchy,
    ) -> list[ExtractionResult]:
        """Extract at chapter level (methodology, workflow)."""
        config = self.config[ExtractionLevel.CHAPTER]
        results = []

        for chapter_id, chapter in hierarchy.chapters.items():
            # Combine chapter chunks
            chapter_text = self._combine_chunks(
                chapter.chunks,
                config.max_tokens,
                config.combination_strategy,
            )

            chunk_ids = [c.id for c in chapter.chunks]

            for extraction_type in config.extraction_types:
                if extraction_type not in self.extractors:
                    continue

                extractor = self.extractors[extraction_type]
                extraction_results = await extractor.extract(
                    content=chapter_text,
                    source_id=hierarchy.source_id,
                    context_level=ExtractionLevel.CHAPTER,
                    context_id=chapter_id,
                    chunk_ids=chunk_ids,
                )
                results.extend(extraction_results)

                logger.debug(
                    "chapter_extraction_complete",
                    chapter=chapter.title,
                    extraction_type=extraction_type,
                    results_count=len(extraction_results),
                )

        return results

    async def _extract_section_level(
        self,
        hierarchy: DocumentHierarchy,
    ) -> list[ExtractionResult]:
        """Extract at section level (decision, pattern, checklist, persona)."""
        config = self.config[ExtractionLevel.SECTION]
        results = []

        for chapter in hierarchy.chapters.values():
            for section_id, section in chapter.sections.items():
                # Combine section chunks
                section_text = self._combine_chunks(
                    section.chunks,
                    config.max_tokens,
                    config.combination_strategy,
                )

                chunk_ids = [c.id for c in section.chunks]

                for extraction_type in config.extraction_types:
                    if extraction_type not in self.extractors:
                        continue

                    extractor = self.extractors[extraction_type]
                    extraction_results = await extractor.extract(
                        content=section_text,
                        source_id=hierarchy.source_id,
                        context_level=ExtractionLevel.SECTION,
                        context_id=section_id,
                        chunk_ids=chunk_ids,
                    )
                    results.extend(extraction_results)

                    logger.debug(
                        "section_extraction_complete",
                        section=section.title,
                        extraction_type=extraction_type,
                        results_count=len(extraction_results),
                    )

        return results

    async def _extract_chunk_level(
        self,
        chunks: list[Chunk],
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract at chunk level (warning)."""
        config = self.config[ExtractionLevel.CHUNK]
        results = []

        for chunk in chunks:
            for extraction_type in config.extraction_types:
                if extraction_type not in self.extractors:
                    continue

                extractor = self.extractors[extraction_type]
                extraction_results = await extractor.extract(
                    content=chunk.content,
                    source_id=source_id,
                    context_level=ExtractionLevel.CHUNK,
                    context_id=chunk.id,
                    chunk_ids=[chunk.id],
                )
                results.extend(extraction_results)

        logger.debug(
            "chunk_extraction_complete",
            chunks_processed=len(chunks),
            results_count=len(results),
        )

        return results

    def _combine_chunks(
        self,
        chunks: list[Chunk],
        max_tokens: int,
        strategy: str,
    ) -> str:
        """Combine chunks into single text within token budget.

        Strategies:
        - truncate: Simply truncate at max_tokens
        - summary_if_exceeded: Summarize if over budget
        - sliding_window: Not implemented yet
        """
        # Sort by chunk_index for proper ordering
        sorted_chunks = sorted(
            chunks,
            key=lambda c: c.position.get("chunk_index", 0) if c.position else 0
        )

        combined_parts = []
        total_tokens = 0

        for chunk in sorted_chunks:
            if total_tokens + chunk.token_count > max_tokens:
                if strategy == "truncate":
                    break
                elif strategy == "summary_if_exceeded":
                    # TODO: Implement summarization fallback
                    break

            combined_parts.append(chunk.content)
            total_tokens += chunk.token_count

        return "\n\n".join(combined_parts)
```

---

## Migration & Compatibility

### Backward Compatibility

The new system maintains backward compatibility:

1. **Existing extractions:** Schema version tracks old vs new extractions
2. **chunk_id field:** Kept for backward compatibility, populated with first chunk in context
3. **MCP tools:** Continue to work - they query extractions, not extraction method

### Migration Path

```python
# No migration required for existing data
# New extractions will have:
#   - schema_version: "1.1.0"
#   - context_level: set appropriately
#   - chunk_ids: list of all chunks used

# Old extractions remain valid with:
#   - schema_version: "1.0.0"
#   - context_level: defaults to "chunk"
#   - chunk_ids: [chunk_id]
```

### Re-extraction Option

If desired, existing sources can be re-extracted:

```python
async def reextract_source(source_id: str):
    """Re-extract a source using hierarchical extraction."""
    # 1. Load chunks from MongoDB
    chunks = await mongodb.chunks.find({"source_id": source_id})

    # 2. Delete old extractions
    await mongodb.extractions.delete_many({"source_id": source_id})
    await qdrant.delete(collection="extractions", filter={"source_id": source_id})

    # 3. Run hierarchical extraction
    results = await hierarchical_extractor.extract_document(chunks, source_id)

    # 4. Save new extractions
    for result in results:
        if result.success:
            await storage.save_extraction(result.extraction)
```

---

## Cost Analysis

### Token Usage Comparison

| Approach | Tokens per Source (est.) | API Cost (Claude) |
|----------|-------------------------|-------------------|
| Current (chunk-level) | ~500 tokens × N chunks | $X |
| Hierarchical | ~8000 × chapters + ~4000 × sections + ~500 × chunks | ~10X |

### Justification

**Extraction is a one-time cost.** The knowledge base is:
- Built once during ingestion
- Queried thousands of times via MCP (zero API cost)
- Quality directly impacts user experience

**ROI calculation:**
- 10x extraction cost
- 90% quality improvement
- Amortized over lifetime of queries = negligible per-query cost

---

## Testing Requirements

### Unit Tests

1. **DocumentHierarchy building**
   - Correctly groups chunks by chapter/section
   - Handles missing position metadata
   - Generates stable IDs

2. **Chunk combination**
   - Respects token budgets
   - Maintains chunk order
   - Truncation strategy works

3. **Level routing**
   - Methodology goes to chapter level
   - Decision goes to section level
   - Warning goes to chunk level

### Integration Tests

1. **End-to-end extraction**
   - Full document → hierarchical extraction → storage
   - Verify extractions have correct context_level
   - Verify chunk_ids attribution

2. **Backward compatibility**
   - Old extraction queries still work
   - MCP tools return both old and new extractions

### Quality Tests

1. **Extraction completeness**
   - Methodology has all steps
   - Decision has all options and trade-offs
   - Pattern has problem, solution, and code

---

## Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `src/extractors/config.py` | Extraction level configuration |
| `src/extractors/hierarchy.py` | Document hierarchy building |
| `src/extractors/hierarchical.py` | HierarchicalExtractor orchestrator |
| `tests/test_extractors/test_hierarchy.py` | Hierarchy tests |
| `tests/test_extractors/test_hierarchical.py` | HierarchicalExtractor tests |

### Modified Files

| File | Changes |
|------|---------|
| `src/extractors/base.py` | New extract() signature, ExtractionLevel enum, updated ExtractionBase |
| `src/extractors/decision_extractor.py` | Adapt to new signature |
| `src/extractors/pattern_extractor.py` | Adapt to new signature |
| `src/extractors/warning_extractor.py` | Adapt to new signature |
| `src/extractors/methodology_extractor.py` | Adapt to new signature |
| `src/extractors/checklist_extractor.py` | Adapt to new signature |
| `src/extractors/persona_extractor.py` | Adapt to new signature |
| `src/extractors/workflow_extractor.py` | Adapt to new signature |
| `src/extraction/pipeline.py` | Use HierarchicalExtractor |

---

## Acceptance Criteria

1. **Hierarchical extraction orchestrator exists** that routes extraction types to appropriate context levels
2. **Document hierarchy is built** from chunk position metadata (chapter, section)
3. **Chapter-level extraction** combines chapter chunks (up to 8000 tokens) for methodology and workflow extraction
4. **Section-level extraction** combines section chunks (up to 4000 tokens) for decision, pattern, checklist, persona extraction
5. **Chunk-level extraction** processes individual chunks for warning extraction
6. **Extractions include context metadata** (context_level, context_id, chunk_ids)
7. **Backward compatibility maintained** - existing extractions and MCP tools continue to work
8. **All existing tests pass** plus new tests for hierarchical extraction
9. **Extraction quality visibly improved** - methodology has complete steps, decisions have full trade-offs

---

## References

- `packages/pipeline/src/processors/chunker.py` - DoclingChunker (produces position metadata)
- `packages/pipeline/src/extractors/base.py` - Current BaseExtractor interface
- `packages/pipeline/src/extraction/pipeline.py` - Current extraction orchestration
- `_bmad-output/architecture.md` - Original architecture decisions
- `_bmad-output/project-context.md` - Implementation rules
