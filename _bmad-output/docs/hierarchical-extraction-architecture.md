# Hierarchical Extraction Architecture

This document explains how the Knowledge Pipeline implements hierarchical chunking and extraction to handle documents with varying content scope.

## The Problem

Traditional chunking splits documents into fixed-size pieces (e.g., 512 tokens). This works poorly for knowledge extraction because:

- **Methodologies** span 3-10 pages across multiple chapters
- **Decisions** and **patterns** span 1-3 pages within sections
- **Warnings** are typically single paragraphs

A 512-token chunk cannot capture a methodology that spans 10 pages.

## Solution Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INGESTION PHASE                               │
│                                                                         │
│   PDF/MD → Docling Adapter → DoclingChunker → Chunks with metadata     │
│                                                                         │
│   Each chunk gets:                                                      │
│   - position.chapter: "Chapter 3: RAG Architecture"                     │
│   - position.section: "3.2 Retrieval Strategies"                        │
│   - position.page: 45                                                   │
│   - token_count: ~512                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          EXTRACTION PHASE                               │
│                                                                         │
│   HierarchicalExtractor builds document hierarchy from chunks:          │
│                                                                         │
│   DocumentHierarchy                                                     │
│   ├── Chapter 1 (ChapterNode)                                          │
│   │   ├── Section 1.1 (SectionNode) → [chunk_1, chunk_2, chunk_3]      │
│   │   ├── Section 1.2 (SectionNode) → [chunk_4, chunk_5]               │
│   │   └── uncategorized_chunks → [chunk_6]                             │
│   ├── Chapter 2 (ChapterNode)                                          │
│   │   └── ...                                                          │
│   └── uncategorized_chunks → [chunks without chapter metadata]          │
│                                                                         │
│   Then runs extractors at appropriate context levels:                   │
│   - CHAPTER (8K tokens): methodology, workflow                          │
│   - SECTION (4K tokens): decision, pattern, checklist, persona          │
│   - CHUNK (512 tokens): warning                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Chunking (Ingestion)

### Source Files

- `src/processors/chunker.py` - DoclingChunker class
- `src/models/chunk.py` - Chunk and ChunkPosition models

### How Chunks Are Created

The `DoclingChunker` uses Docling's `HybridChunker` which:

1. Parses document structure (headings, sections, pages)
2. Splits into ~512 token chunks respecting boundaries
3. Contextualizes each chunk (adds relevant headings to text)
4. Extracts position metadata

```python
# ChunkPosition model (src/models/chunk.py)
class ChunkPosition(BaseModel):
    chapter: Optional[str] = None   # "Chapter 3: RAG Architecture"
    section: Optional[str] = None   # "3.2 Retrieval Strategies"
    page: Optional[int] = None      # 45
```

### Metadata Extraction from Headings

```python
# From chunker.py lines 291-304
if hasattr(chunk, "meta") and chunk.meta:
    meta = chunk.meta
    if hasattr(meta, "headings") and meta.headings:
        headings = meta.headings
        # Store full headings array for reference
        position["headings"] = headings
        # Map to architecture-expected chapter/section structure
        if len(headings) >= 1:
            position["chapter"] = headings[0]  # First heading = chapter
        if len(headings) >= 2:
            position["section"] = headings[-1]  # Last heading = section
    if hasattr(meta, "page") and meta.page is not None:
        position["page"] = meta.page
```

### Example Chunk Output

```json
{
  "id": "507f1f77bcf86cd799439012",
  "source_id": "507f1f77bcf86cd799439011",
  "content": "# Chapter 3: RAG Architecture\n\n## 3.2 Retrieval Strategies\n\nVector search is the foundation...",
  "position": {
    "chapter": "Chapter 3: RAG Architecture",
    "section": "3.2 Retrieval Strategies",
    "page": 45,
    "chunk_index": 12,
    "headings": ["Chapter 3: RAG Architecture", "3.2 Retrieval Strategies"]
  },
  "token_count": 487,
  "project_id": "knowledge-pipeline"
}
```

---

## Phase 2: Hierarchy Building (Extraction)

### Source Files

- `src/extractors/hierarchy.py` - build_hierarchy(), DocumentHierarchy
- `src/extractors/hierarchical.py` - HierarchicalExtractor

### Data Structures

```python
# DocumentHierarchy (hierarchy.py)
@dataclass
class DocumentHierarchy:
    source_id: str
    chapters: dict[str, ChapterNode]        # chapter_name → ChapterNode
    uncategorized_chunks: list[Chunk]        # Chunks without chapter metadata

@dataclass
class ChapterNode:
    chapter_id: str                          # Stable hash ID
    chapter_name: str                        # "Chapter 3: RAG Architecture"
    sections: dict[str, SectionNode]         # section_name → SectionNode
    uncategorized_chunks: list[Chunk]        # Chunks in chapter but no section

@dataclass
class SectionNode:
    section_id: str                          # Stable hash ID
    section_name: str                        # "3.2 Retrieval Strategies"
    chapter_name: str                        # Parent chapter for context
    chunks: list[Chunk]                      # Chunks in this section
```

### How Hierarchy Is Built

```python
# From hierarchy.py lines 171-237
def build_hierarchy(chunks: list[Chunk], source_id: str) -> DocumentHierarchy:
    hierarchy = DocumentHierarchy(source_id=source_id)

    for chunk in chunks:
        chapter_name = chunk.position.chapter if chunk.position else None
        section_name = chunk.position.section if chunk.position else None

        if not chapter_name:
            # No chapter metadata → uncategorized
            hierarchy.uncategorized_chunks.append(chunk)
            continue

        # Ensure chapter exists
        if chapter_name not in hierarchy.chapters:
            chapter_id = _generate_id(source_id, "chapter", chapter_name)
            hierarchy.chapters[chapter_name] = ChapterNode(
                chapter_id=chapter_id,
                chapter_name=chapter_name,
            )

        chapter = hierarchy.chapters[chapter_name]

        if not section_name:
            # Has chapter but no section → chapter's uncategorized
            chapter.uncategorized_chunks.append(chunk)
            continue

        # Ensure section exists within chapter
        if section_name not in chapter.sections:
            section_id = _generate_id(source_id, "section", f"{chapter_name}:{section_name}")
            chapter.sections[section_name] = SectionNode(
                section_id=section_id,
                section_name=section_name,
                chapter_name=chapter_name,
            )

        chapter.sections[section_name].chunks.append(chunk)

    return hierarchy
```

---

## Phase 3: Hierarchical Extraction

### Extraction Level Configuration

```python
# From extraction_levels.py lines 66-85
EXTRACTION_LEVEL_CONFIG = {
    ExtractionLevel.CHAPTER: ExtractionLevelConfig(
        level=ExtractionLevel.CHAPTER,
        extraction_types=["methodology", "workflow"],
        max_tokens=8000,
        combination_strategy="summary_if_exceeded",  # NOT IMPLEMENTED - falls back to truncate
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
        combination_strategy="none",  # No combination needed
    ),
}
```

### Token Budgets Summary

| Level | Max Tokens | Extraction Types | Combination Strategy |
|-------|------------|------------------|---------------------|
| CHAPTER | 8,000 | methodology, workflow | truncate (summary not implemented) |
| SECTION | 4,000 | decision, pattern, checklist, persona | truncate |
| CHUNK | 512 | warning | none |

### How Chunks Are Combined

```python
# From hierarchy.py lines 290-357
def combine_chunks(chunks: list[Chunk], max_tokens: int, strategy: str) -> CombinedContent:
    # Sort chunks by index for proper ordering
    sorted_chunks = sorted(chunks, key=_get_chunk_index)

    # Combine all content with paragraph breaks
    combined_text = "\n\n".join(chunk.content for chunk in sorted_chunks)
    total_tokens = sum(chunk.token_count for chunk in sorted_chunks)

    # If under limit, return as-is
    if strategy == "none" or total_tokens <= max_tokens:
        return CombinedContent(
            content=combined_text,
            chunk_ids=[c.id for c in sorted_chunks],
            total_tokens=total_tokens,
            truncated=False,
        )

    # If over limit, apply strategy
    if strategy == "truncate":
        return _truncate_to_limit(sorted_chunks, max_tokens)

    if strategy == "summary_if_exceeded":
        # NOT IMPLEMENTED - falls back to truncation
        logger.warning("summary_if_exceeded_not_implemented")
        return _truncate_to_limit(sorted_chunks, max_tokens)
```

### Truncation Logic

```python
# From hierarchy.py lines 360-404
def _truncate_to_limit(chunks: list[Chunk], max_tokens: int) -> CombinedContent:
    included_chunks = []
    current_tokens = 0

    for chunk in chunks:
        if current_tokens + chunk.token_count > max_tokens:
            break  # Adding this chunk would exceed limit
        included_chunks.append(chunk)
        current_tokens += chunk.token_count

    return CombinedContent(
        content="\n\n".join(c.content for c in included_chunks),
        chunk_ids=[c.id for c in included_chunks],
        total_tokens=current_tokens,
        truncated=len(included_chunks) < len(chunks),
    )
```

---

## Extraction Flow

### HierarchicalExtractor.extract_document()

```python
# From hierarchical.py lines 152-223
async def extract_document(self, chunks: list[Chunk], source_id: str):
    # Build document hierarchy
    hierarchy = build_hierarchy(chunks, source_id)

    # Extract at each level
    chapter_results = await self._extract_chapter_level(hierarchy, source_id)
    section_results = await self._extract_section_level(hierarchy, source_id)
    chunk_results = await self._extract_chunk_level(hierarchy, source_id)

    # Combine results
    result.results.extend(chapter_results)
    result.results.extend(section_results)
    result.results.extend(chunk_results)

    return result
```

### Chapter-Level Extraction

```python
# From hierarchical.py lines 225-279
async def _extract_chapter_level(self, hierarchy, source_id):
    config = EXTRACTION_LEVEL_CONFIG[ExtractionLevel.CHAPTER]
    chapter_types = [et for et in self.extraction_types if et.value in config.extraction_types]

    for chapter in hierarchy.get_chapter_nodes():
        # Combine chapter chunks (up to 8K tokens)
        combined = combine_chunks(chapter.all_chunks, config.max_tokens, config.combination_strategy)

        # Run extractors (methodology, workflow)
        for extraction_type in chapter_types:
            extractor = self._get_extractor(extraction_type)
            results = await extractor.extract(
                content=combined.content,
                source_id=source_id,
                context_level=ExtractionLevel.CHAPTER,
                context_id=chapter.chapter_id,
                chunk_ids=combined.chunk_ids,
            )
```

---

## Current Limitations

### 1. Token Truncation for Large Chapters

**Problem:** If a chapter has 100,000 tokens but max_tokens is 8,000, only the first ~8K tokens are used for methodology extraction.

**What happens:**
```
Chapter: "Complete RAG Implementation Guide" (100K tokens)
    ↓
combine_chunks() with max_tokens=8000
    ↓
Only first ~16 pages extracted, rest is LOST for methodology extraction
```

**Impact:** Methodologies appearing later in long chapters are missed.

**Planned solution:** The `summary_if_exceeded` strategy is defined but not implemented. It would:
1. Summarize chunks before combining
2. Or use sliding window extraction with multiple passes

### 2. Missing Section Metadata

**Problem:** If a PDF has poor heading structure, chunks may lack chapter/section metadata.

**What happens:**
- Chunks go into `uncategorized_chunks`
- Still extracted, but without hierarchical context benefits

### 3. Section-Level Extractors on Long Sections

**Problem:** Sections are limited to 4K tokens. Long sections (e.g., 20K tokens) are truncated.

**Impact:** Decisions or patterns appearing late in long sections may be missed.

---

## File Reference

| File | Purpose |
|------|---------|
| `src/models/chunk.py` | Chunk and ChunkPosition models |
| `src/processors/chunker.py` | DoclingChunker for creating chunks |
| `src/extractors/hierarchy.py` | DocumentHierarchy, build_hierarchy(), combine_chunks() |
| `src/extractors/hierarchical.py` | HierarchicalExtractor orchestrator |
| `src/extractors/extraction_levels.py` | ExtractionLevelConfig, token limits |
| `src/extraction/pipeline.py` | ExtractionPipeline.extract_hierarchical() |

---

## Example: End-to-End Flow

### Input: RAG Survey PDF (100 pages)

1. **Ingestion:**
   ```
   PDF → DoclingAdapter → 61 chunks with chapter/section metadata
   ```

2. **Hierarchy Building:**
   ```
   61 chunks → DocumentHierarchy with:
   - 8 chapters
   - 24 sections
   - 0 uncategorized
   ```

3. **Chapter-Level Extraction (methodology, workflow):**
   ```
   For each chapter:
   - Combine chunks (up to 8K tokens)
   - Run methodology extractor
   - Run workflow extractor
   ```

4. **Section-Level Extraction (decision, pattern, checklist, persona):**
   ```
   For each section:
   - Combine chunks (up to 4K tokens)
   - Run decision extractor
   - Run pattern extractor
   - Run checklist extractor
   - Run persona extractor
   ```

5. **Chunk-Level Extraction (warning):**
   ```
   For each individual chunk:
   - Run warning extractor
   ```

6. **Output:**
   ```
   87 extractions stored in MongoDB + Qdrant
   - methodologies: 12
   - workflows: 8
   - decisions: 25
   - patterns: 18
   - warnings: 24
   ```

---

## Diagram: Complete Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              DOCUMENT                                       │
│                         (100 pages, 50K tokens)                            │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           DoclingChunker                                    │
│                                                                            │
│  - Splits into ~512 token chunks                                           │
│  - Extracts chapter/section from headings                                  │
│  - Uses nomic tokenizer for accurate counts                                │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                              CHUNKS                                         │
│                                                                            │
│  [Chunk 1] chapter="Ch1", section="1.1", tokens=487                        │
│  [Chunk 2] chapter="Ch1", section="1.1", tokens=512                        │
│  [Chunk 3] chapter="Ch1", section="1.2", tokens=498                        │
│  [Chunk 4] chapter="Ch2", section="2.1", tokens=501                        │
│  ...                                                                       │
│  [Chunk 61] chapter="Ch8", section="8.3", tokens=423                       │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                          build_hierarchy()                                  │
│                                                                            │
│  Groups chunks by chapter → section → chunk                                │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         DocumentHierarchy                                   │
│                                                                            │
│  Chapter 1 (15 chunks, 7200 tokens)                                        │
│  ├── Section 1.1 (6 chunks, 2900 tokens)                                   │
│  ├── Section 1.2 (5 chunks, 2400 tokens)                                   │
│  └── Section 1.3 (4 chunks, 1900 tokens)                                   │
│  Chapter 2 (12 chunks, 5800 tokens)                                        │
│  └── ...                                                                   │
│  ...                                                                       │
│  Chapter 8 (8 chunks, 3900 tokens)                                         │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │ CHAPTER      │ │ SECTION      │ │ CHUNK        │
           │ LEVEL        │ │ LEVEL        │ │ LEVEL        │
           │              │ │              │ │              │
           │ max: 8K      │ │ max: 4K      │ │ max: 512     │
           │ types:       │ │ types:       │ │ types:       │
           │ - methodology│ │ - decision   │ │ - warning    │
           │ - workflow   │ │ - pattern    │ │              │
           │              │ │ - checklist  │ │              │
           │              │ │ - persona    │ │              │
           └──────────────┘ └──────────────┘ └──────────────┘
                    │               │               │
                    ▼               ▼               ▼
           ┌──────────────────────────────────────────────┐
           │              EXTRACTIONS                      │
           │                                              │
           │  Stored in MongoDB + Qdrant with:           │
           │  - context_level (chapter/section/chunk)     │
           │  - context_id (stable hash)                  │
           │  - chunk_ids (traceability)                  │
           │  - embedding (768d vector)                   │
           └──────────────────────────────────────────────┘
```
