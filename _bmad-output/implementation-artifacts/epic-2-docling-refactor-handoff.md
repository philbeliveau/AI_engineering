# Epic 2 Course Correction: Docling Refactor Handoff

**Date:** 2025-12-30
**Triggered By:** Philippebeliveau
**Epic:** Epic 2 - Document Ingestion Pipeline
**Change Type:** Architectural Simplification - Library Replacement

---

## Executive Summary

Replace separate PDF/Markdown adapters (pymupdf + markdown-it-py) with IBM's **Docling** library for unified document processing. This simplifies the codebase, improves extraction quality, and adds support for additional formats (DOCX, HTML, PPTX).

**Impact Assessment:**
- Stories Affected: 4 of 6 (2.2, 2.3, 2.4, 2.6)
- Stories Unchanged: 2 (2.1, 2.5)
- Files to Delete: 3 (pdf_adapter.py, markdown_adapter.py, tests)
- Files to Create: 2 (docling_adapter.py, tests)
- Files to Modify: 3 (__init__.py, chunker.py, pyproject.toml)

---

## Current State Analysis

### Sprint Status (Before Correction)

| Story | Status | Notes |
|-------|--------|-------|
| 2.1 - Base Source Adapter Interface | done | Keep as-is |
| 2.2 - PDF Document Adapter | in-progress | 286 lines of PyMuPDF code exists |
| 2.3 - Markdown Document Adapter | ready-for-dev | Not started |
| 2.4 - Text Chunking Processor | ready-for-dev | Manual implementation planned |
| 2.5 - Local Embedding Generator | ready-for-dev | No changes needed |
| 2.6 - End-to-End Pipeline | ready-for-dev | Simpler with Docling |

### Files Currently Existing

```
packages/pipeline/
├── src/
│   └── adapters/
│       ├── __init__.py          # Exports SourceAdapter, PdfAdapter
│       ├── base.py              # SourceAdapter ABC (from 2.1) - KEEP
│       └── pdf_adapter.py       # 286 lines PyMuPDF - DELETE
├── tests/
│   └── test_adapters/
│       ├── conftest.py          # Test fixtures - MODIFY
│       └── test_pdf_adapter.py  # PyMuPDF tests - DELETE
└── pyproject.toml               # Has pymupdf dependency - MODIFY
```

---

## Dependency Changes

### pyproject.toml Modifications

**Add:**
```toml
docling = "^2.66"
transformers = "^4.40"  # Required for HuggingFaceTokenizer in chunking
```

**Remove:**
```toml
# pymupdf - replaced by Docling
# markdown-it-py - replaced by Docling (if added)
```

**Note:** The `transformers` package is required for the `HuggingFaceTokenizer` used by `HybridChunker`. This enables accurate token counting with the same tokenizer used by the embedding model.

### Why Docling?

| Aspect | Before (pymupdf + markdown-it-py) | After (Docling) |
|--------|-----------------------------------|-----------------|
| Libraries | 2 separate libraries | 1 unified library |
| Adapters | 2 separate adapters | 1 unified adapter |
| Formats | PDF, Markdown | PDF, Markdown, DOCX, HTML, PPTX |
| Tables | Basic extraction | Structured table extraction |
| Chunking | Manual implementation | Built-in HybridChunker |
| Tokenizer | Heuristic (~4 chars/token) | Uses actual embedding model tokenizer |

---

## Story-by-Story Changes

### Story 2.1: Base Source Adapter Interface
**Action:** NO CHANGES

The existing `SourceAdapter` ABC, `AdapterResult`, `Section` models, and adapter registry remain valid. Docling adapter will implement this interface.

---

### Story 2.2: PDF Document Adapter -> Docling Document Adapter

**Action:** REWRITE COMPLETELY

**Old Title:** PDF Document Adapter
**New Title:** Docling Document Adapter

**Old Scope:**
- Create PdfAdapter using pymupdf
- Handle PDF-specific extraction
- Multi-column layout handling

**New Scope:**
- Create `DoclingAdapter` extending `SourceAdapter` (from 2.1)
- Support formats: `.pdf`, `.md`, `.docx`, `.html`, `.pptx`
- Use `DocumentConverter` from Docling for extraction
- Map Docling's `DoclingDocument` -> `AdapterResult` model
- Extract sections with hierarchy (headings, tables, lists)
- Handle errors: corrupted files, unsupported formats
- Register in `adapter_registry`

**New User Story:**
```
As a builder,
I want to ingest documents using Docling,
So that I can extract structured content from PDFs, Markdown, DOCX, HTML, and PPTX files with a unified adapter.
```

**New Acceptance Criteria:**
```
Given a document file path (PDF, MD, DOCX, HTML, or PPTX)
When I use the Docling adapter to process the file
Then text is extracted with structure preserved (headings, tables, lists)
And source metadata (title, authors if detectable, path) is captured
And sections include hierarchy information
And position metadata (page numbers for PDF) is tracked
And errors are raised for corrupted or unsupported files
```

**New Tasks:**
- [ ] Add `docling = "^2.66"` to pyproject.toml
- [ ] Remove `pymupdf` dependency from pyproject.toml
- [ ] Create `packages/pipeline/src/adapters/docling_adapter.py`
- [ ] Implement `DoclingAdapter` class extending `SourceAdapter`
- [ ] Define `SUPPORTED_EXTENSIONS = [".pdf", ".md", ".docx", ".html", ".pptx"]`
- [ ] Implement `extract_text()` using `DocumentConverter`
- [ ] Map `DoclingDocument` structure to `AdapterResult` with `Section` list
- [ ] Implement `get_metadata()` extracting title, authors, path, type
- [ ] Implement `supports_file()` checking extension
- [ ] Add to `adapter_registry` in `__init__.py`
- [ ] Create comprehensive tests in `test_docling_adapter.py`
- [ ] Delete `pdf_adapter.py` and `test_pdf_adapter.py`

**Key Implementation Pattern (VERIFIED via Context7):**
```python
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter
from docling_core.types.doc import DoclingDocument
import structlog

from src.adapters.base import (
    AdapterConfig,
    AdapterResult,
    FileParseError,
    Section,
    SourceAdapter,
)

logger = structlog.get_logger()


class DoclingAdapter(SourceAdapter):
    """Unified adapter for document extraction using IBM Docling."""

    SUPPORTED_EXTENSIONS = [".pdf", ".md", ".docx", ".html", ".pptx"]

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self._converter = DocumentConverter()
        logger.debug("docling_adapter_initialized")

    def extract_text(self, file_path: Path) -> AdapterResult:
        """Extract text and structure from document using Docling."""
        self._validate_file_exists(file_path)
        self._validate_file_extension(file_path)

        try:
            # Convert document - returns ConversionResult
            conv_result = self._converter.convert(str(file_path))
            doc: DoclingDocument = conv_result.document

            # Export to markdown for full text
            full_text = doc.export_to_markdown()

            # Extract sections from document structure
            sections = self._extract_sections(doc)
            metadata = self.get_metadata(file_path)

            # Store DoclingDocument for chunker (important!)
            metadata["_docling_document"] = doc

            result = AdapterResult(
                text=full_text,
                metadata=metadata,
                sections=sections,
            )

            logger.info(
                "docling_extracted",
                path=str(file_path),
                sections=len(sections),
                chars=len(full_text),
            )

            return self._validate_result(result, file_path)

        except Exception as e:
            logger.error("docling_extraction_failed", path=str(file_path), error=str(e))
            raise FileParseError(file_path, f"Docling extraction failed: {e}")

    def _extract_sections(self, doc: DoclingDocument) -> list[Section]:
        """Extract sections from DoclingDocument structure."""
        sections = []
        for item, level in doc.iterate_items():
            if hasattr(item, 'text') and item.text:
                sections.append(Section(
                    title=getattr(item, 'label', 'content'),
                    content=item.text,
                    level=level,
                    position=self._get_item_position(item)
                ))
        return sections

    def _get_item_position(self, item) -> dict:
        """Extract position metadata from document item."""
        position = {}
        if hasattr(item, 'prov') and item.prov:
            # Get page number from provenance
            for prov in item.prov:
                if hasattr(prov, 'page_no'):
                    position['page'] = prov.page_no
                    break
        return position
```

**Important:** The `metadata["_docling_document"]` stores the raw DoclingDocument for the chunker. The HybridChunker requires the DoclingDocument object, not raw text.

**Test Cases Required:**
- PDF extraction with tables
- Markdown extraction with code blocks
- DOCX extraction
- HTML extraction
- Section hierarchy preservation
- Error handling (corrupted PDF, missing file)
- Position metadata (page numbers for PDF)
- Metadata extraction (title, authors)

---

### Story 2.3: Markdown Document Adapter

**Action:** ARCHIVE/REMOVE

This story is now merged into Story 2.2 (Docling Document Adapter). The Docling library handles Markdown natively.

**Sprint Status Update:**
- Change status from `ready-for-dev` to `archived`
- OR remove from sprint tracking entirely
- Add note: "Merged into Story 2.2 - Docling handles Markdown natively"

---

### Story 2.4: Text Chunking Processor

**Action:** REWRITE - Use Docling's HybridChunker

**Old Scope:**
- Manual sentence boundary detection
- Manual sliding window with overlap
- Custom `TextChunker` class
- Token estimation (~4 chars/token)

**New Scope:**
- Use Docling's `HybridChunker` instead of custom implementation
- Configure with `all-MiniLM-L6-v2` tokenizer (matches embedding model)
- `max_tokens=512`, respect section boundaries
- Keep `ChunkOutput` model for storage compatibility
- Keep exception classes (`ChunkerError`, etc.)
- Wrap HybridChunker in thin adapter for consistency

**New User Story:**
```
As a developer,
I want to use Docling's HybridChunker for text chunking,
So that chunks respect document structure and use accurate token counting from the embedding model's tokenizer.
```

**New Acceptance Criteria:**
```
Given extracted content from DoclingAdapter
When I process it through the chunker
Then text is split using Docling's HybridChunker
And chunks respect section boundaries from the document structure
And token counts use the all-MiniLM-L6-v2 tokenizer (accurate, not estimated)
And each chunk includes position metadata
And ChunkOutput models are compatible with MongoDB storage
```

**What to Keep from Original 2.4:**
- `ChunkerConfig` model (for pipeline config)
- `ChunkOutput` model (for storage compatibility)
- Exception classes (`ChunkerError`, `EmptyContentError`, `ChunkSizeError`)
- Module exports pattern in `__init__.py`

**What to Remove:**
- Manual sentence boundary detection (`find_sentence_boundaries()`)
- Manual sliding window logic
- `find_split_point()` function
- Character-based token estimation

**New Implementation Pattern (VERIFIED via Context7):**
```python
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc import DoclingDocument
from transformers import AutoTokenizer

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

class DoclingChunker:
    """Wrapper around Docling's HybridChunker for pipeline integration."""

    def __init__(self, config: Optional[ChunkerConfig] = None):
        self.config = config or ChunkerConfig()

        # Create tokenizer matching the embedding model
        self._tokenizer = HuggingFaceTokenizer(
            tokenizer=AutoTokenizer.from_pretrained(EMBED_MODEL_ID),
            max_tokens=self.config.chunk_size,  # Default 512
        )

        self._chunker = HybridChunker(
            tokenizer=self._tokenizer,
            merge_peers=True,  # Merge peer elements for better context
        )

    def chunk_document(
        self,
        docling_doc: DoclingDocument,
        source_id: str
    ) -> list[ChunkOutput]:
        """Chunk a DoclingDocument into storage-ready chunks."""
        chunk_iter = self._chunker.chunk(dl_doc=docling_doc)
        chunks = list(chunk_iter)

        return [
            ChunkOutput(
                source_id=source_id,
                content=chunk.text,
                position=self._extract_position(chunk),
                token_count=self._tokenizer.count_tokens(chunk.text),
            )
            for i, chunk in enumerate(chunks)
        ]

    def contextualize(self, chunk) -> str:
        """Get chunk text with document context (headings, etc.)."""
        return self._chunker.contextualize(chunk=chunk)
```

**New Tasks:**
- [ ] Rewrite `packages/pipeline/src/processors/chunker.py`
- [ ] Create `DoclingChunker` class wrapping `HybridChunker`
- [ ] Configure with `all-MiniLM-L6-v2` tokenizer
- [ ] Keep `ChunkerConfig`, `ChunkOutput`, exceptions
- [ ] Remove manual sentence boundary detection functions
- [ ] Update tests to use DoclingDocument fixtures
- [ ] Update `__init__.py` exports

---

### Story 2.5: Local Embedding Generator

**Action:** NO CHANGES

The embedding generator using `sentence-transformers/all-MiniLM-L6-v2` remains unchanged. It will receive chunk text from the new Docling-based chunker.

---

### Story 2.6: End-to-End Ingestion Pipeline

**Action:** UPDATE - Simpler Integration

**Changes Required:**
- Import `DoclingAdapter` instead of `PdfAdapter`/`MarkdownAdapter`
- Use Docling's chunker output (with DoclingDocument)
- Fewer adapter registrations needed (1 instead of 2+)
- Same storage flow (MongoDB + Qdrant)

**Key Integration Changes:**
```python
# OLD (Story 2.6 as written)
from src.adapters import adapter_registry  # Would have PdfAdapter, MarkdownAdapter

# NEW (After Docling refactor)
from src.adapters import adapter_registry  # Only DoclingAdapter needed
from src.adapters.docling_adapter import DoclingAdapter

# The adapter_registry.get_adapter(file_path) will now return DoclingAdapter
# for ALL supported file types: .pdf, .md, .docx, .html, .pptx
```

**Pipeline Flow (Updated):**
```
1. Validate file exists
2. Get DoclingAdapter from registry (handles all formats)
3. adapter.extract_text() -> AdapterResult with DoclingDocument
4. DoclingChunker.chunk_document() -> list[ChunkOutput]
5. LocalEmbedder.embed_batch() -> 384d vectors
6. Store: MongoDB (sources, chunks), Qdrant (vectors)
```

**Updated Tasks:**
- [ ] Update imports to use `DoclingAdapter`
- [ ] Update pipeline to pass DoclingDocument to chunker
- [ ] Remove references to `MarkdownAdapter`
- [ ] Test with all supported formats (.pdf, .md, .docx)
- [ ] Update CLI help text to reflect supported formats

---

## Files to Create/Modify/Delete

| File | Action | Notes |
|------|--------|-------|
| `packages/pipeline/pyproject.toml` | MODIFY | Add docling, remove pymupdf/markdown-it-py |
| `src/adapters/docling_adapter.py` | CREATE | New unified adapter |
| `src/adapters/__init__.py` | MODIFY | Export DoclingAdapter, remove PdfAdapter |
| `src/adapters/pdf_adapter.py` | DELETE | Replaced by DoclingAdapter |
| `src/adapters/markdown_adapter.py` | DELETE | Never created, now not needed |
| `src/processors/chunker.py` | REWRITE | Wrap HybridChunker |
| `tests/test_adapters/test_docling_adapter.py` | CREATE | New tests |
| `tests/test_adapters/test_pdf_adapter.py` | DELETE | Replaced |
| `tests/test_adapters/test_markdown_adapter.py` | DELETE | Never needed |

---

## Testing Requirements

### DoclingAdapter Tests

```python
# tests/test_adapters/test_docling_adapter.py

class TestDoclingAdapter:
    """Tests for unified Docling document adapter."""

    def test_extract_pdf_with_tables(self, sample_pdf_with_table):
        """Verify table extraction from PDF."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_pdf_with_table)
        assert "table content" in result.text.lower()

    def test_extract_markdown_with_code(self, sample_markdown_with_code):
        """Verify code block extraction from Markdown."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_markdown_with_code)
        assert "```python" in result.text or "def " in result.text

    def test_extract_docx(self, sample_docx):
        """Verify DOCX extraction."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_docx)
        assert result.text
        assert result.sections

    def test_section_hierarchy_preserved(self, sample_pdf_with_headings):
        """Verify heading hierarchy in sections."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_pdf_with_headings)
        levels = [s.level for s in result.sections]
        assert 1 in levels  # H1
        assert 2 in levels  # H2

    def test_error_on_corrupted_pdf(self, corrupted_pdf):
        """Verify error handling for corrupted files."""
        adapter = DoclingAdapter()
        with pytest.raises(FileParseError):
            adapter.extract_text(corrupted_pdf)

    def test_position_metadata_pdf(self, sample_pdf):
        """Verify page numbers in position metadata."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_pdf)
        page_positions = [s.position.get("page") for s in result.sections if s.position]
        assert any(p is not None for p in page_positions)
```

### DoclingChunker Tests

```python
# tests/test_processors/test_chunker.py

class TestDoclingChunker:
    """Tests for Docling-based chunker."""

    def test_chunks_respect_section_boundaries(self, docling_doc_with_sections):
        """Verify chunks align with document sections."""
        chunker = DoclingChunker()
        chunks = chunker.chunk_document(docling_doc_with_sections, "test-source")
        # Chunks should not split mid-section when possible

    def test_token_counts_accurate(self, sample_docling_doc):
        """Verify token counts use actual tokenizer."""
        chunker = DoclingChunker()
        chunks = chunker.chunk_document(sample_docling_doc, "test-source")
        for chunk in chunks:
            assert chunk.token_count <= 512  # max_tokens
            assert chunk.token_count > 0

    def test_chunk_output_model_compatible(self, sample_docling_doc):
        """Verify ChunkOutput works with MongoDB storage."""
        chunker = DoclingChunker()
        chunks = chunker.chunk_document(sample_docling_doc, "test-source")
        for chunk in chunks:
            assert chunk.id  # UUID generated
            assert chunk.source_id == "test-source"
            assert chunk.content
            assert chunk.schema_version == "1.0"
```

---

## Sprint Status Updates Required

After implementing changes, update `sprint-status.yaml`:

```yaml
development_status:
  # Epic 2: Document Ingestion Pipeline
  epic-2: in-progress
  2-1-base-source-adapter-interface: done          # NO CHANGE
  2-2-docling-document-adapter: ready-for-dev      # RENAMED, reset to ready-for-dev
  2-3-markdown-document-adapter: archived          # MERGED INTO 2.2
  2-4-text-chunking-processor: ready-for-dev       # REWRITE NEEDED
  2-5-local-embedding-generator: ready-for-dev     # NO CHANGE
  2-6-end-to-end-ingestion-pipeline: ready-for-dev # UPDATE NEEDED
```

---

## References

### External Documentation
- Docling PyPI: https://pypi.org/project/docling/
- Docling Docs: https://ds4sd.github.io/docling/
- Docling Chunking: https://ds4sd.github.io/docling/examples/chunking/
- LangChain Integration: https://docs.langchain.com/oss/python/integrations/document_loaders/docling

### Internal Documents
- Architecture: `_bmad-output/architecture.md`
- PRD: `_bmad-output/prd.md`
- Project Context: `_bmad-output/project-context.md`
- Story 2.1 (Adapter Interface): `_bmad-output/implementation-artifacts/2-1-base-source-adapter-interface.md`

---

## Success Criteria for Course Correction

1. **Story 2.2 Rewritten:** New story file reflects DoclingAdapter scope
2. **Story 2.3 Archived:** Clearly marked as merged into 2.2
3. **Story 2.4 Updated:** Reflects HybridChunker usage, not manual implementation
4. **Story 2.6 Updated:** References DoclingAdapter, simpler integration
5. **Sprint Status Updated:** Reflects new story states
6. **Dependencies Updated:** pyproject.toml has docling, not pymupdf
7. **Old Code Deleted:** pdf_adapter.py removed
8. **Tests Pass:** New test suite for DoclingAdapter passes

---

## Notes for Implementation Agent

1. **Read Docling documentation first** - The library has specific patterns for document iteration and chunking.

2. **DoclingDocument is the key object** - The converter returns a result with a `document` attribute that is a `DoclingDocument`. This is what gets passed to the chunker.

3. **HybridChunker needs a DoclingDocument** - It doesn't work on raw text. The chunker and adapter are tightly coupled through this object.

4. **Token counting is now accurate** - Docling's chunker uses the actual tokenizer, so token counts will differ from the old heuristic (~4 chars/token).

5. **Test fixtures need updating** - Create fixtures that produce DoclingDocument objects for chunker tests.

---

## Context7 Verification Summary (2025-12-30)

**Verified Dependencies:**
```toml
docling = "^2.66"          # Latest: 2.66.0 (confirmed via PyPI)
transformers = "^4.40"     # Required for HuggingFaceTokenizer
```

**Verified Import Paths:**
```python
# DocumentConverter
from docling.document_converter import DocumentConverter

# HybridChunker
from docling.chunking import HybridChunker

# HuggingFaceTokenizer (required for chunker)
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

# DoclingDocument type
from docling_core.types.doc import DoclingDocument
```

**Key API Patterns (from Context7 code snippets):**
```python
# Document conversion
converter = DocumentConverter()
result = converter.convert(source)  # source can be Path or URL
doc = result.document  # DoclingDocument

# Export formats
doc.export_to_markdown()
doc.export_to_dict()  # JSON
doc.export_to_html()

# Chunking setup
tokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2"),
    max_tokens=512,
)
chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)
chunks = list(chunker.chunk(dl_doc=doc))

# Token counting
token_count = tokenizer.count_tokens(chunk.text)

# Contextualization (adds headings/context to chunk text)
contextualized_text = chunker.contextualize(chunk=chunk)
```

**Context7 Sources Used:**
- `/docling-project/docling` (1753 snippets, score: 87.8)
- Topics: installation, HybridChunker, DocumentConverter
