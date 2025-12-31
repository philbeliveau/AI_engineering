# Story 2.2: Docling Document Adapter

Status: done

<!--
COURSE CORRECTION: 2025-12-30
This story was rewritten from "PDF Document Adapter" to "Docling Document Adapter"
as part of Epic 2 Docling refactor. See: epic-2-sprint-change-proposal.md
-->

## Story

As a **builder**,
I want to ingest documents using Docling,
So that I can extract structured content from PDFs, Markdown, DOCX, HTML, and PPTX files with a unified adapter.

## Acceptance Criteria

**Given** a document file path (PDF, MD, DOCX, HTML, or PPTX)
**When** I use the Docling adapter to process the file
**Then** text is extracted with structure preserved (headings, tables, lists)
**And** source metadata (title, authors if detectable, path) is captured
**And** sections include hierarchy information
**And** position metadata (page numbers for PDF) is tracked
**And** errors are raised for corrupted or unsupported files

## Tasks / Subtasks

- [x] Add `docling = "^2.66"` and `transformers = "^4.40"` to pyproject.toml
- [x] Create `packages/pipeline/src/adapters/docling_adapter.py`
- [x] Implement `DoclingAdapter` class extending `SourceAdapter` (from 2.1)
- [x] Define `SUPPORTED_EXTENSIONS = [".pdf", ".md", ".docx", ".html", ".pptx"]`
- [x] Implement `extract_text()` using `DocumentConverter` from Docling
- [x] Map `DoclingDocument` structure to `AdapterResult` with `Section` list
- [x] Implement `get_metadata()` extracting title, authors, path, type
- [x] Implement `supports_file()` checking extension
- [x] Store `DoclingDocument` in metadata for chunker (required for HybridChunker)
- [x] Add to `adapter_registry` in `__init__.py`
- [x] Create comprehensive tests in `test_docling_adapter.py`
  - [x] PDF extraction with tables
  - [x] Markdown extraction with code blocks
  - [x] DOCX extraction
  - [x] Section hierarchy preservation
  - [x] Error handling (corrupted PDF, missing file)
  - [x] Position metadata (page numbers for PDF)
  - [x] Metadata extraction (title, authors)

## Dev Notes

### Architecture Requirements

**From Architecture.md:**

**Adapter Pattern (FR-1: Source Ingestion):**
- Location: `packages/pipeline/src/adapters/`
- Base class: `SourceAdapter` (ABC) - exists from Story 2.1
- Concrete implementation: `DoclingAdapter` extends `SourceAdapter`
- NFR5 (Extensibility): Abstract adapter pattern enables new source types

**Project Structure:**
```
packages/pipeline/src/adapters/
├── __init__.py           # Add DoclingAdapter export
├── base.py               # SourceAdapter ABC (from Story 2.1)
└── docling_adapter.py    # NEW: DoclingAdapter implementation
```

### Dependencies (Already in pyproject.toml)

```toml
docling = "^2.66"           # Unified document processing
transformers = "^4.40"      # Required for HuggingFaceTokenizer in chunking
```

### Why Docling?

| Aspect | Before (pymupdf + markdown-it-py) | After (Docling) |
|--------|-----------------------------------|-----------------|
| Libraries | 2 separate libraries | 1 unified library |
| Adapters | 2 separate adapters | 1 unified adapter |
| Formats | PDF, Markdown | PDF, Markdown, DOCX, HTML, PPTX |
| Tables | Basic extraction | Structured table extraction |
| Chunking | Manual implementation | Built-in HybridChunker (Story 2.4) |
| Tokenizer | Heuristic (~4 chars/token) | Uses actual embedding model tokenizer |

### Key Implementation Pattern (VERIFIED via Context7)

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

### Important Notes

1. **DoclingDocument is the key object** - The converter returns a result with a `document` attribute that is a `DoclingDocument`. This object gets passed to the chunker.

2. **HybridChunker needs DoclingDocument** - Story 2.4 chunker requires the DoclingDocument, not raw text. That's why we store it in `metadata["_docling_document"]`.

3. **Token counting is now accurate** - Docling's chunker uses the actual tokenizer, so token counts will differ from the old heuristic (~4 chars/token).

### Verified Import Paths (Context7)

```python
# DocumentConverter
from docling.document_converter import DocumentConverter

# DoclingDocument type
from docling_core.types.doc import DoclingDocument

# For Story 2.4 - HybridChunker
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
```

### Testing Requirements

**Test Organization:**
- Tests in: `packages/pipeline/tests/test_adapters/test_docling_adapter.py`
- Mirror src structure (per architecture)
- Shared fixtures in `tests/conftest.py`

**Test Cases Required:**

```python
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

    def test_docling_document_in_metadata(self, sample_pdf):
        """Verify DoclingDocument stored for chunker."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_pdf)
        assert "_docling_document" in result.metadata
        assert result.metadata["_docling_document"] is not None
```

### Project Context Reference

**Critical Rules from project-context.md:**

**Naming:**
- File: `docling_adapter.py` (snake_case)
- Class: `DoclingAdapter` (PascalCase)
- Functions: `extract_text`, `get_metadata` (snake_case)

**Error Handling:**
- Custom exceptions inherit from `AdapterError` (base.py)
- Use `FileParseError` for extraction failures
- Include context in error messages

**Code Quality:**
- No print statements (use structlog)
- Type hints on all functions
- Docstrings for public methods

### Reference Links

**Source Documents:**
- [Sprint Change Proposal](epic-2-sprint-change-proposal.md)
- [Handoff Document](epic-2-docling-refactor-handoff.md)
- [Architecture: Adapter Pattern](../../_bmad-output/architecture.md)
- [Story 2.1: Base Adapter Interface](2-1-base-source-adapter-interface.md)

**External References:**
- [Docling PyPI](https://pypi.org/project/docling/)
- [Docling Documentation](https://ds4sd.github.io/docling/)
- [Docling Chunking Examples](https://ds4sd.github.io/docling/examples/chunking/)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 32 DoclingAdapter tests pass
- Full test suite: 314 tests pass (no regressions)
- Ruff linting: All checks passed

### Completion Notes List

1. **DoclingAdapter Implementation Complete**: Created unified adapter supporting PDF, Markdown, DOCX, HTML, and PPTX using IBM Docling library
2. **Section Extraction**: Implemented `_extract_sections()` that iterates through DoclingDocument items and maps them to Section objects with level clamping (1-6)
3. **Position Metadata**: Implemented `_get_item_position()` to extract page numbers from provenance data
4. **DoclingDocument Storage**: Stored raw DoclingDocument in `metadata["_docling_document"]` for downstream HybridChunker usage (Story 2.4)
5. **Registry Integration**: Registered DoclingAdapter for all 5 extensions (.pdf, .md, .docx, .html, .pptx) in adapter_registry
6. **Error Handling**: Proper FileParseError for corrupted files, FileNotFoundError for missing files, UnsupportedFileError for wrong extensions
7. **Tests**: 32 comprehensive tests covering initialization, file support checks, Markdown/HTML extraction, DoclingDocument storage, section hierarchy, error handling, metadata extraction, and registry integration

### File List

- packages/pipeline/src/adapters/docling_adapter.py (CREATE, MODIFY - added _extract_authors)
- packages/pipeline/src/adapters/__init__.py (MODIFY)
- packages/pipeline/tests/test_adapters/test_docling_adapter.py (CREATE, MODIFY - added PDF/DOCX/PPTX tests)
- packages/pipeline/tests/test_adapters/conftest.py (MODIFY - added PDF/DOCX/PPTX fixtures)

## Change Log

- 2025-12-30: Story implemented - DoclingAdapter with full test coverage
- 2025-12-30: [Code Review] Fixed 4 MEDIUM issues:
  - Added PDF extraction tests with fixtures (sample_pdf_with_table, sample_pdf_with_headings)
  - Added DOCX extraction tests with fixtures (sample_docx)
  - Added PPTX support verification tests (extraction tests skipped - requires full Office Open XML)
  - Implemented _extract_authors() method to extract author metadata from DoclingDocument
  - Test count: 41 passed, 2 skipped (PPTX extraction), full suite: 349 passed
