# Story 2.4: Text Chunking Processor

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want a chunking processor that splits documents into semantic chunks,
So that extracted text is appropriately sized for embedding and extraction.

## Acceptance Criteria

**Given** extracted text from an adapter
**When** I process it through the chunker
**Then** text is split into chunks of configurable size (default based on architecture)
**And** chunks respect sentence boundaries where possible
**And** each chunk includes position metadata (source location)
**And** chunk token counts are calculated and stored

## Dependency Analysis

**Depends On:**
- **Story 1.1** (Initialize Monorepo Structure) - MUST be completed first
  - Requires `packages/pipeline/src/` directory structure
  - Requires Python 3.11+ environment with uv
- **Story 1.3** (Pydantic Models for Core Entities) - MUST be completed first
  - Requires `Chunk` Pydantic model with fields: `id`, `source_id`, `content`, `position`, `token_count`, `schema_version`
- **Story 2.1** (Base Source Adapter Interface) - MUST be completed first
  - Provides `AdapterResult` with extracted text and sections
  - Provides `Section` model with position metadata
- **Story 2.2** (PDF Document Adapter) - Should be completed first
  - First concrete adapter providing input to chunker
  - Establishes position metadata patterns (chapter, section, page)
- **Story 2.3** (Markdown Document Adapter) - Should be completed first
  - Second concrete adapter providing input to chunker
  - Establishes heading hierarchy patterns

**Blocks:**
- **Story 2.5** (Local Embedding Generator) - Needs chunks to embed
- **Story 2.6** (End-to-End Ingestion Pipeline) - Uses chunker in pipeline
- **Epic 3** (Knowledge Extraction System) - Extractors process chunks

## Tasks / Subtasks

- [ ] **Task 1: Verify Prerequisites** (AC: Dependencies available)
  - [ ] Confirm Story 1.1 complete: `ls packages/pipeline/pyproject.toml`
  - [ ] Confirm Story 1.3 complete: `cd packages/pipeline && uv run python -c "from src.models import Chunk; print('OK')"`
  - [ ] Confirm Story 2.1 complete: `cd packages/pipeline && uv run python -c "from src.adapters import AdapterResult, Section; print('OK')"`
  - [ ] Confirm Python 3.11+: `cd packages/pipeline && uv run python --version`

- [ ] **Task 2: Create Processors Module Structure** (AC: Module exists)
  - [ ] Create `packages/pipeline/src/processors/` directory
  - [ ] Create `packages/pipeline/src/processors/__init__.py`
  - [ ] Create `packages/pipeline/src/processors/chunker.py`

- [ ] **Task 3: Define Chunker Configuration Models** (AC: Type-safe configuration)
  - [ ] Create `ChunkerConfig` Pydantic model with fields:
    - `chunk_size: int = 512` - Target tokens per chunk
    - `chunk_overlap: int = 50` - Overlap tokens between chunks
    - `min_chunk_size: int = 100` - Minimum chunk size in tokens
    - `respect_sentence_boundary: bool = True` - Split at sentences
    - `respect_section_boundary: bool = True` - Preserve section boundaries when possible
  - [ ] Create `ChunkMetadata` Pydantic model with fields:
    - `source_id: str` - Reference to source document
    - `chunk_index: int` - Sequential chunk number
    - `position: dict` - Position info (chapter, section, page, line)
    - `section_title: str | None` - Title of containing section
    - `token_count: int` - Actual token count
    - `char_count: int` - Character count

- [ ] **Task 4: Implement Token Counting** (AC: Accurate token estimation)
  - [ ] Implement `estimate_tokens(text: str) -> int` function
    - Use rough heuristic: ~4 characters per token for English (fast)
  - [ ] Implement `count_tokens_precise(text: str, model: str = "all-MiniLM-L6-v2") -> int` function
    - Use sentence-transformers tokenizer for exact count when needed
  - [ ] Add configurable `use_precise_count: bool = False` to ChunkerConfig
  - [ ] Document tradeoffs: speed vs accuracy

- [ ] **Task 5: Implement Sentence Boundary Detection** (AC: Respects sentence boundaries)
  - [ ] Implement `find_sentence_boundaries(text: str) -> list[int]` function
    - Use regex patterns for common sentence endings (. ! ? followed by space/newline)
    - Handle edge cases: abbreviations (Mr., Dr., etc.), numbers (3.14), URLs
  - [ ] Implement `split_at_sentence(text: str, target_pos: int) -> int` function
    - Find nearest sentence boundary to target position
    - Return position of best split point
  - [ ] Handle edge case: single very long sentence exceeds chunk size

- [ ] **Task 6: Implement Section-Aware Chunking** (AC: Preserves section structure)
  - [ ] Implement `chunk_with_sections(sections: list[Section], config: ChunkerConfig) -> list[Chunk]`
    - Process each section separately when possible
    - Preserve section title in chunk metadata
    - Handle sections smaller than chunk_size (don't split)
    - Handle sections larger than chunk_size (split with overlap)
  - [ ] Maintain section hierarchy in position metadata

- [ ] **Task 7: Implement Core TextChunker Class** (AC: Main chunking logic)
  - [ ] Create `TextChunker` class with `__init__(self, config: ChunkerConfig = None)`
  - [ ] Implement `chunk_text(text: str, source_id: str, position_base: dict = None) -> list[Chunk]`
    - Main method for processing plain text
    - Apply sentence boundary detection
    - Calculate overlap between chunks
    - Generate chunk metadata
  - [ ] Implement `chunk_adapter_result(result: AdapterResult, source_id: str) -> list[Chunk]`
    - Process AdapterResult from adapters
    - Use sections if available, fall back to plain text
    - Preserve position metadata from sections
  - [ ] Implement sliding window with overlap logic

- [ ] **Task 8: Implement Chunk Output Models** (AC: Integration with storage)
  - [ ] Create `ChunkOutput` Pydantic model compatible with Story 1.3 `Chunk` model:
    - `id: str` - Generated unique ID (uuid4)
    - `source_id: str` - Reference to source document
    - `content: str` - Chunk text content
    - `position: dict` - Position metadata
    - `token_count: int` - Token count for this chunk
    - `schema_version: str = "1.0"` - Schema version
  - [ ] Implement `to_chunk_model(chunk_output: ChunkOutput) -> Chunk` converter

- [ ] **Task 9: Implement Chunker Exceptions** (AC: Error handling)
  - [ ] Create `ChunkerError` base exception inheriting from `KnowledgeError`
  - [ ] Create `EmptyContentError` for empty input text
  - [ ] Create `ChunkSizeError` for invalid chunk size configuration
  - [ ] All exceptions follow structured format: `{code, message, details}`

- [ ] **Task 10: Create Module Exports** (AC: Clean imports)
  - [ ] Export from `packages/pipeline/src/processors/__init__.py`:
    - `TextChunker`
    - `ChunkerConfig`, `ChunkMetadata`, `ChunkOutput`
    - `ChunkerError`, `EmptyContentError`, `ChunkSizeError`
    - `estimate_tokens`, `count_tokens_precise`
  - [ ] Verify imports work: `from src.processors import TextChunker, ChunkerConfig`

- [ ] **Task 11: Create Unit Tests** (AC: Comprehensive test coverage)
  - [ ] Create `packages/pipeline/tests/test_processors/` directory
  - [ ] Create `packages/pipeline/tests/test_processors/conftest.py` with test fixtures
  - [ ] Create `packages/pipeline/tests/test_processors/test_chunker.py`
  - [ ] Test basic text chunking (plain text input)
  - [ ] Test sentence boundary detection and splitting
  - [ ] Test section-aware chunking with AdapterResult
  - [ ] Test overlap calculation between chunks
  - [ ] Test token counting (estimate vs precise)
  - [ ] Test edge cases: empty text, very short text, very long sentences
  - [ ] Test configuration variations (different chunk sizes, overlap)
  - [ ] Test position metadata preservation
  - [ ] Document test results in completion notes

## Dev Notes

### Architecture Requirements

**From Architecture Document (architecture.md:619-621):**

```
packages/pipeline/src/
├── processors/              # Chunking, cleaning
│   ├── __init__.py
│   ├── chunker.py
│   └── cleaner.py
```

**From PRD (FR-1.7):**
> Chunking with position tracking (chapter, section, page)

**From Architecture (Data Architecture):**
MongoDB `chunks` collection schema:
- `_id`: Unique chunk ID
- `source_id`: Reference to sources._id
- `content`: Chunk text content
- `position`: {chapter, section, page} position metadata
- `token_count`: Token count for the chunk
- `schema_version`: Schema version string

### Qdrant Configuration Reference

**From Architecture Document (architecture.md:299-306):**
- Vector size: 384 dimensions (all-MiniLM-L6-v2)
- Distance metric: Cosine
- Collection: `chunks` for semantic search on raw text
- Payload: `{source_id, chunk_id, type, topics}` for filtered search

This means chunks need to be appropriately sized for:
1. Embedding with all-MiniLM-L6-v2 (max 256 word pieces, ~512 tokens)
2. Semantic search effectiveness (not too short, not too long)
3. Extraction context windows (chunks feed into LLM extraction)

### Recommended Chunk Configuration

Based on architecture and best practices:

```python
DEFAULT_CONFIG = ChunkerConfig(
    chunk_size=512,           # Tokens - fits embedding model
    chunk_overlap=50,         # ~10% overlap for context
    min_chunk_size=100,       # Don't create tiny chunks
    respect_sentence_boundary=True,
    respect_section_boundary=True,
)
```

**Rationale:**
- `512 tokens`: all-MiniLM-L6-v2 handles up to 256 word pieces, which maps roughly to 512 tokens of content. This ensures full utilization of embedding capacity.
- `50 token overlap`: Provides context continuity between chunks, helping with semantic search and extraction that spans chunk boundaries.
- `100 min tokens`: Prevents fragmentation that would hurt search quality.

### Chunking Algorithm Overview

```python
def chunk_text(text: str, config: ChunkerConfig) -> list[Chunk]:
    """
    Sliding Window Chunking with Sentence Awareness:

    1. Calculate target positions for chunk boundaries
    2. For each boundary, find nearest sentence boundary
    3. Extract chunk from previous boundary to current
    4. Add overlap by including end of previous chunk
    5. Generate metadata and token counts
    """
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        # Calculate target end position
        target_end = start + (config.chunk_size * 4)  # ~4 chars per token

        # Find actual end at sentence boundary
        actual_end = find_sentence_boundary_near(text, target_end)

        # Extract chunk content
        content = text[start:actual_end]

        # Calculate overlap start for next chunk
        overlap_start = max(0, actual_end - (config.chunk_overlap * 4))

        chunks.append(Chunk(
            content=content,
            chunk_index=chunk_index,
            token_count=estimate_tokens(content),
        ))

        # Move to next chunk with overlap
        start = overlap_start
        chunk_index += 1

    return chunks
```

### Section-Aware Chunking

When processing AdapterResult with sections:

```python
def chunk_adapter_result(result: AdapterResult, source_id: str) -> list[Chunk]:
    """
    Section-Aware Chunking Strategy:

    1. If sections available, process each section
    2. Small sections (< min_chunk_size): Combine with next
    3. Medium sections (< chunk_size): Keep as single chunk
    4. Large sections (> chunk_size): Split with overlap
    5. Preserve section title and hierarchy in metadata
    """
    if result.sections:
        return chunk_sections(result.sections, source_id)
    else:
        return chunk_text(result.text, source_id)
```

### Token Estimation vs Precise Counting

**Fast Estimation (default):**
```python
def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 characters per token for English."""
    return len(text) // 4
```

**Precise Counting (optional):**
```python
def count_tokens_precise(text: str) -> int:
    """Use actual tokenizer from sentence-transformers."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return len(model.tokenizer.encode(text))
```

**Tradeoff:** Precise counting adds ~10ms per call due to tokenizer load. Use estimation for chunking, precise for final validation if needed.

### Sentence Boundary Detection

**Regex Pattern for English:**
```python
import re

SENTENCE_END = re.compile(
    r'(?<=[.!?])'           # After . ! ?
    r'(?=\s+[A-Z]|\s*$)'    # Before space+capital or end
    r'|(?<=\n\n)'           # Or after paragraph break
)

# Exceptions to handle:
# - Mr. Mrs. Dr. etc. (abbreviations)
# - Numbers like 3.14
# - URLs like https://example.com
# - Ellipsis ...
```

### Position Metadata Structure

**From adapters (input):**
```python
position = {
    "chapter": "Chapter 5",      # From PDF TOC or MD H1
    "section": "RAG Architecture", # From PDF section or MD H2
    "page": 127,                 # PDF page number
    "line": 45,                  # MD line number
}
```

**In chunk (output):**
```python
chunk.position = {
    "chapter": "Chapter 5",
    "section": "RAG Architecture",
    "page": 127,
    "chunk_index": 3,            # Added by chunker
    "start_char": 5234,          # Character offset in source
    "end_char": 7891,
}
```

### Library/Framework Requirements

**sentence-transformers (for precise token counting):**
- Already a project dependency (from architecture)
- Model: `all-MiniLM-L6-v2`
- Tokenizer provides exact token counts
- Only load model if precise counting requested

**Pydantic v2:**
- All models use Pydantic v2 syntax
- `snake_case` field names
- `schema_version` field on all models

**structlog:**
- All logging via structlog
- No print statements

### File Structure Requirements

**Location:** `packages/pipeline/src/processors/`

**Files to Create:**
1. `packages/pipeline/src/processors/__init__.py` - Module exports
2. `packages/pipeline/src/processors/chunker.py` - TextChunker implementation

**Tests to Create:**
1. `packages/pipeline/tests/test_processors/__init__.py`
2. `packages/pipeline/tests/test_processors/conftest.py` - Test fixtures
3. `packages/pipeline/tests/test_processors/test_chunker.py` - Unit tests

### Integration with Previous Stories

**Story 2.1 (Base Adapter Interface):**
- Input: `AdapterResult` with `text`, `metadata`, `sections`
- Input: `Section` with `title`, `content`, `level`, `position`

**Story 2.2/2.3 (PDF/Markdown Adapters):**
- Receive structured output from adapters
- Position metadata patterns already established
- Follow same error handling patterns

### Testing Requirements

**Test Cases:**

1. **Basic Text Chunking**
   - Plain text split into chunks of target size
   - Verify token counts are within expected range
   - Verify no content lost (concatenated chunks = original)

2. **Sentence Boundary Respect**
   - Chunks should end at sentence boundaries when possible
   - Long sentences that exceed chunk size are split anyway
   - No mid-word splits

3. **Section-Aware Chunking**
   - Sections smaller than chunk_size stay intact
   - Large sections split with overlap
   - Section titles preserved in metadata

4. **Overlap Calculation**
   - Verify overlap tokens present in adjacent chunks
   - Overlap helps with context continuity

5. **Edge Cases**
   - Empty text raises EmptyContentError
   - Very short text (< min_chunk_size) returns single chunk
   - Text with no sentence boundaries still chunks correctly

6. **Configuration Variations**
   - Different chunk_size values
   - Different overlap values
   - Boundary respect on/off

**Test Fixtures:**
```python
@pytest.fixture
def chunker():
    """Default chunker with standard config."""
    return TextChunker()

@pytest.fixture
def sample_text():
    """Multi-paragraph sample text for testing."""
    return """
    Chapter 1: Introduction to RAG

    Retrieval-Augmented Generation (RAG) is a technique that enhances
    large language models by providing relevant context from external
    knowledge sources. This chapter introduces the core concepts.

    ## Key Concepts

    RAG systems combine two main components: a retriever and a generator.
    The retriever finds relevant documents. The generator uses them to
    produce accurate responses.
    """

@pytest.fixture
def sample_adapter_result(sample_text):
    """AdapterResult with sections for testing."""
    return AdapterResult(
        text=sample_text,
        metadata={"title": "RAG Guide", "type": "documentation"},
        sections=[
            Section(title="Introduction", content="...", level=1),
            Section(title="Key Concepts", content="...", level=2),
        ]
    )
```

### Previous Story Intelligence

**From Story 2.1 (Base Source Adapter Interface):**
- `AdapterResult` model: `text`, `metadata`, `sections`
- `Section` model: `title`, `content`, `level`, `position`
- Exception pattern: Inherit from `KnowledgeError`, include `code`, `message`, `details`
- Logging pattern: Use structlog with context

**From Story 2.2 (PDF Document Adapter):**
- Position metadata includes: `chapter`, `section`, `page`
- CPU-bound operations are sync (no async needed)
- PDF-specific position tracking established

**From Story 2.3 (Markdown Document Adapter):**
- Position metadata includes: `line`, heading hierarchy
- Sections map to heading structure (H1=chapter, H2=section)
- markdown-it-py provides token.map for line numbers

**Patterns to Follow:**
- Exception classes inherit from `KnowledgeError`
- All exceptions include `code`, `message`, `details`
- Use structlog for all logging
- Pydantic models for data validation
- Tests mirror src structure
- CPU-bound = sync functions

### Architecture Compliance Checklist

- [ ] File in `packages/pipeline/src/processors/chunker.py` (architecture.md:619-621)
- [ ] `ChunkerConfig` uses Pydantic Settings pattern
- [ ] Default chunk size ~512 tokens (fits all-MiniLM-L6-v2)
- [ ] Overlap between chunks for context continuity
- [ ] Position metadata preserved from adapter input
- [ ] Token counts calculated for each chunk
- [ ] Exceptions inherit from `KnowledgeError` (architecture.md:545-559)
- [ ] Structured error format: `{code, message, details}`
- [ ] Uses structlog for logging (architecture.md:535-542)
- [ ] Tests in `packages/pipeline/tests/test_processors/`

### Reference Implementation

```python
# packages/pipeline/src/processors/chunker.py
"""Text chunking processor for knowledge pipeline.

This module provides semantic text chunking that splits documents
into appropriately sized chunks for embedding and extraction.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
import structlog

from src.adapters import AdapterResult, Section
from src.exceptions import KnowledgeError

logger = structlog.get_logger()


class ChunkerConfig(BaseModel):
    """Configuration for text chunking behavior."""
    chunk_size: int = Field(default=512, ge=50, le=2048)
    chunk_overlap: int = Field(default=50, ge=0)
    min_chunk_size: int = Field(default=100, ge=10)
    respect_sentence_boundary: bool = True
    respect_section_boundary: bool = True
    use_precise_token_count: bool = False


class ChunkMetadata(BaseModel):
    """Metadata for a text chunk."""
    source_id: str
    chunk_index: int
    position: dict = Field(default_factory=dict)
    section_title: Optional[str] = None
    token_count: int
    char_count: int


class ChunkOutput(BaseModel):
    """Output model for a text chunk."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    content: str
    position: dict = Field(default_factory=dict)
    token_count: int
    schema_version: str = "1.0"


class ChunkerError(KnowledgeError):
    """Base exception for chunker errors."""
    pass


class EmptyContentError(ChunkerError):
    """Raised when input text is empty."""
    def __init__(self):
        super().__init__(
            code="EMPTY_CONTENT",
            message="Cannot chunk empty text content",
            details={}
        )


class ChunkSizeError(ChunkerError):
    """Raised when chunk size configuration is invalid."""
    def __init__(self, reason: str, config: ChunkerConfig):
        super().__init__(
            code="INVALID_CHUNK_SIZE",
            message=f"Invalid chunk size configuration: {reason}",
            details={"config": config.model_dump(), "reason": reason}
        )


# Sentence boundary pattern
SENTENCE_END = re.compile(
    r'(?<=[.!?])\s+(?=[A-Z])'  # . ! ? followed by space and capital
    r'|(?<=\n\n)'              # Or paragraph break
)

# Abbreviations that don't end sentences
ABBREVIATIONS = {'Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Sr', 'Jr', 'vs', 'etc', 'eg', 'ie'}


def estimate_tokens(text: str) -> int:
    """Estimate token count using character heuristic.

    Args:
        text: Input text to estimate.

    Returns:
        Estimated token count (~4 chars per token).
    """
    return len(text) // 4


def find_sentence_boundaries(text: str) -> list[int]:
    """Find positions of sentence boundaries in text.

    Args:
        text: Input text to analyze.

    Returns:
        List of character positions where sentences end.
    """
    boundaries = [0]  # Start of text
    for match in SENTENCE_END.finditer(text):
        boundaries.append(match.end())
    boundaries.append(len(text))  # End of text
    return sorted(set(boundaries))


def find_split_point(text: str, target: int, boundaries: list[int]) -> int:
    """Find best split point near target position.

    Args:
        text: Full text being chunked.
        target: Target character position.
        boundaries: List of sentence boundary positions.

    Returns:
        Best split position (sentence boundary nearest to target).
    """
    if not boundaries:
        return min(target, len(text))

    # Binary search for nearest boundary
    import bisect
    idx = bisect.bisect_left(boundaries, target)

    # Check boundaries on either side
    candidates = []
    if idx > 0:
        candidates.append(boundaries[idx - 1])
    if idx < len(boundaries):
        candidates.append(boundaries[idx])

    # Return closest to target
    return min(candidates, key=lambda x: abs(x - target))


class TextChunker:
    """Processor for splitting text into semantic chunks.

    Splits documents into chunks of configurable size while respecting
    sentence and section boundaries where possible.

    Example:
        chunker = TextChunker()
        chunks = chunker.chunk_text(text, source_id="doc-123")
        for chunk in chunks:
            print(f"Chunk {chunk.position['chunk_index']}: {chunk.token_count} tokens")
    """

    def __init__(self, config: Optional[ChunkerConfig] = None):
        """Initialize chunker with configuration.

        Args:
            config: Chunker configuration. Uses defaults if not provided.
        """
        self.config = config or ChunkerConfig()
        self._validate_config()
        logger.debug(
            "chunker_initialized",
            chunk_size=self.config.chunk_size,
            overlap=self.config.chunk_overlap,
        )

    def _validate_config(self) -> None:
        """Validate chunker configuration."""
        if self.config.chunk_overlap >= self.config.chunk_size:
            raise ChunkSizeError(
                "overlap must be less than chunk_size",
                self.config
            )
        if self.config.min_chunk_size > self.config.chunk_size:
            raise ChunkSizeError(
                "min_chunk_size must be <= chunk_size",
                self.config
            )

    def chunk_text(
        self,
        text: str,
        source_id: str,
        position_base: Optional[dict] = None
    ) -> list[ChunkOutput]:
        """Split text into chunks.

        Args:
            text: Text content to chunk.
            source_id: ID of source document.
            position_base: Base position metadata to include.

        Returns:
            List of ChunkOutput objects.

        Raises:
            EmptyContentError: If text is empty.
        """
        text = text.strip()
        if not text:
            raise EmptyContentError()

        position_base = position_base or {}
        chunks = []

        # Find sentence boundaries if respecting them
        boundaries = []
        if self.config.respect_sentence_boundary:
            boundaries = find_sentence_boundaries(text)

        # Calculate character targets from token targets
        chars_per_token = 4
        target_chars = self.config.chunk_size * chars_per_token
        overlap_chars = self.config.chunk_overlap * chars_per_token
        min_chars = self.config.min_chunk_size * chars_per_token

        start = 0
        chunk_index = 0

        while start < len(text):
            # Calculate target end
            target_end = start + target_chars

            # Find actual end at sentence boundary
            if self.config.respect_sentence_boundary and boundaries:
                actual_end = find_split_point(text, target_end, boundaries)
            else:
                actual_end = min(target_end, len(text))

            # Ensure minimum chunk size unless at end
            if actual_end - start < min_chars and actual_end < len(text):
                actual_end = min(start + min_chars, len(text))

            # Extract content
            content = text[start:actual_end].strip()

            if content:  # Only add non-empty chunks
                token_count = estimate_tokens(content)

                chunk = ChunkOutput(
                    source_id=source_id,
                    content=content,
                    position={
                        **position_base,
                        "chunk_index": chunk_index,
                        "start_char": start,
                        "end_char": actual_end,
                    },
                    token_count=token_count,
                )
                chunks.append(chunk)
                chunk_index += 1

                logger.debug(
                    "chunk_created",
                    chunk_index=chunk_index,
                    token_count=token_count,
                    start=start,
                    end=actual_end,
                )

            # Move to next position with overlap
            start = actual_end - overlap_chars
            if start >= actual_end:  # Prevent infinite loop
                start = actual_end

        logger.info(
            "chunking_complete",
            source_id=source_id,
            total_chunks=len(chunks),
            total_tokens=sum(c.token_count for c in chunks),
        )

        return chunks

    def chunk_adapter_result(
        self,
        result: AdapterResult,
        source_id: str
    ) -> list[ChunkOutput]:
        """Chunk an AdapterResult, using sections if available.

        Args:
            result: AdapterResult from a document adapter.
            source_id: ID of source document.

        Returns:
            List of ChunkOutput objects.
        """
        if result.sections and self.config.respect_section_boundary:
            return self._chunk_sections(result.sections, source_id)
        else:
            return self.chunk_text(result.text, source_id, result.metadata)

    def _chunk_sections(
        self,
        sections: list[Section],
        source_id: str
    ) -> list[ChunkOutput]:
        """Chunk document by sections.

        Args:
            sections: List of document sections.
            source_id: ID of source document.

        Returns:
            List of ChunkOutput objects.
        """
        all_chunks = []
        chunk_index = 0

        for section in sections:
            position_base = {
                "section_title": section.title,
                "section_level": section.level,
                **section.position,
            }

            # Check if section fits in single chunk
            section_tokens = estimate_tokens(section.content)

            if section_tokens <= self.config.chunk_size:
                # Small section - keep as single chunk
                chunk = ChunkOutput(
                    source_id=source_id,
                    content=section.content.strip(),
                    position={
                        **position_base,
                        "chunk_index": chunk_index,
                    },
                    token_count=section_tokens,
                )
                all_chunks.append(chunk)
                chunk_index += 1
            else:
                # Large section - split into chunks
                section_chunks = self.chunk_text(
                    section.content,
                    source_id,
                    position_base
                )
                # Update chunk indices
                for chunk in section_chunks:
                    chunk.position["chunk_index"] = chunk_index
                    chunk_index += 1
                all_chunks.extend(section_chunks)

        logger.info(
            "section_chunking_complete",
            source_id=source_id,
            total_sections=len(sections),
            total_chunks=len(all_chunks),
        )

        return all_chunks
```

### Module Exports

```python
# packages/pipeline/src/processors/__init__.py
"""Text processing utilities for knowledge pipeline.

This module provides processors for chunking and cleaning
document text for embedding and extraction.

Example:
    from src.processors import TextChunker, ChunkerConfig

    chunker = TextChunker(ChunkerConfig(chunk_size=512))
    chunks = chunker.chunk_text(text, source_id="doc-123")
"""

from src.processors.chunker import (
    # Main class
    TextChunker,
    # Configuration models
    ChunkerConfig,
    ChunkMetadata,
    ChunkOutput,
    # Exceptions
    ChunkerError,
    EmptyContentError,
    ChunkSizeError,
    # Utility functions
    estimate_tokens,
    find_sentence_boundaries,
)

__all__ = [
    # Main class
    "TextChunker",
    # Configuration models
    "ChunkerConfig",
    "ChunkMetadata",
    "ChunkOutput",
    # Exceptions
    "ChunkerError",
    "EmptyContentError",
    "ChunkSizeError",
    # Utility functions
    "estimate_tokens",
    "find_sentence_boundaries",
]
```

### References

- [Source: epics.md#Story-2.4] - Story acceptance criteria (lines 319-333)
- [Source: architecture.md#Project-Structure-&-Boundaries] - File locations (lines 619-621)
- [Source: architecture.md#Qdrant-Configuration] - Vector size and chunking constraints (lines 299-306)
- [Source: architecture.md#MongoDB-Collections] - Chunk document schema (lines 274-283)
- [Source: architecture.md#Implementation-Patterns-&-Consistency-Rules] - Naming patterns (lines 410-435)
- [Source: architecture.md#Error-Handling-Pattern] - Exception pattern (lines 545-560)
- [Source: project-context.md#Critical-Implementation-Rules] - Error handling, logging rules
- [Source: Story 2.1] - AdapterResult and Section models
- [Source: Story 2.2] - Position metadata patterns from PDF adapter
- [Source: Story 2.3] - Heading hierarchy patterns from Markdown adapter
- [Source: PRD#FR-1.7] - Chunking with position tracking requirement

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

_To be filled by dev agent - list all files created/modified:_
- packages/pipeline/src/processors/__init__.py (CREATE)
- packages/pipeline/src/processors/chunker.py (CREATE)
- packages/pipeline/tests/test_processors/__init__.py (CREATE)
- packages/pipeline/tests/test_processors/conftest.py (CREATE)
- packages/pipeline/tests/test_processors/test_chunker.py (CREATE)
