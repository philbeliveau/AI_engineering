# Story 2.2: PDF Document Adapter

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **builder**,
I want to ingest PDF documents using pymupdf,
So that I can extract text content from AI engineering books for knowledge extraction.

## Acceptance Criteria

**Given** a PDF file path is provided
**When** I use the PDF adapter to process the file
**Then** text is extracted from all pages with position metadata (chapter, section, page)
**And** source metadata (title, authors if detectable, path) is captured
**AND** the adapter handles multi-column layouts gracefully
**AND** errors are raised for corrupted or password-protected PDFs

## Tasks / Subtasks

- [ ] Create base SourceAdapter ABC interface (AC: #1)
  - [ ] Define abstract methods: `extract_text()` and `get_metadata()`
  - [ ] Add common text processing utilities
  - [ ] Document extensibility pattern (NFR5)
- [ ] Implement PdfAdapter class extending SourceAdapter (AC: #2, #3)
  - [ ] Initialize pymupdf (fitz) document handler
  - [ ] Extract text from all pages with position tracking
  - [ ] Parse PDF metadata (title, authors from document properties)
  - [ ] Handle multi-column layouts gracefully
  - [ ] Implement error handling for corrupted/encrypted PDFs
- [ ] Create Pydantic models for adapter outputs (AC: #1, #2)
  - [ ] Source model with metadata fields
  - [ ] Position model with chapter/section/page tracking
- [ ] Add comprehensive tests for PDF adapter (AC: #1-4)
  - [ ] Unit tests with sample PDFs
  - [ ] Test multi-column layout handling
  - [ ] Test metadata extraction
  - [ ] Test error cases (corrupted, encrypted PDFs)

## Dev Notes

### Architecture Requirements

**From Architecture.md:**

**Adapter Pattern (FR-1: Source Ingestion):**
- Location: `packages/pipeline/src/adapters/`
- Base class: `SourceAdapter` (ABC) with abstract methods
- Concrete implementation: `PdfAdapter` extends `SourceAdapter`
- NFR5 (Extensibility): Abstract adapter pattern enables new source types

**Project Structure:**
```
packages/pipeline/src/adapters/
├── __init__.py
├── base.py              # SourceAdapter ABC
├── pdf_adapter.py       # PdfAdapter implementation
└── markdown_adapter.py  # (separate story)
```

**Pydantic Models Required:**
- `Source` model (location: `packages/pipeline/src/models/source.py`)
- Fields: `id`, `type`, `title`, `authors[]`, `path`, `ingested_at`, `status`, `metadata{}`, `schema_version`

**Dependencies:**
- `pymupdf` (PyMuPDF/fitz): PDF parsing library
- Already specified in architecture: `uv add pymupdf`

**Naming Conventions (MANDATORY):**
- File: `pdf_adapter.py` (snake_case)
- Class: `PdfAdapter` (PascalCase)
- Methods: `extract_text()`, `get_metadata()` (snake_case)
- Module exports: `from .base import SourceAdapter`

### Technical Implementation Details

**PDF Text Extraction with pymupdf:**
```python
import fitz  # PyMuPDF

# Open PDF document
doc = fitz.open(pdf_path)

# Extract text page by page with position metadata
for page_num, page in enumerate(doc, start=1):
    text = page.get_text("text")  # Simple text extraction
    # For multi-column: page.get_text("blocks") returns positioned blocks
```

**Metadata Extraction:**
- PDF metadata available via `doc.metadata` dict
- Common fields: `title`, `author`, `subject`, `creator`
- Fallback: derive title from filename if metadata missing

**Multi-Column Layout Handling:**
- Use `page.get_text("blocks")` for positioned text blocks
- Sort blocks by (y, x) coordinates to preserve reading order
- Detect columns by analyzing x-coordinate clusters

**Error Handling:**
- Corrupted PDFs: `fitz.open()` raises exceptions
- Encrypted PDFs: Check `doc.is_encrypted` before processing
- Raise custom `KnowledgeError` subclass with structured error format

### Library/Framework Requirements

**pymupdf (PyMuPDF) - Latest Stable:**
- Primary PDF processing library
- Alias: `import fitz` (MuPDF Python binding)
- Features used: text extraction, metadata parsing, page iteration
- Error handling: raises exceptions for corrupted/encrypted files

**Pydantic v2:**
- All models use Pydantic v2 syntax
- `snake_case` field names
- `schema_version` field on all models

**Python 3.11+:**
- Type hints required for all function signatures
- Use modern syntax (match/case, improved type annotations)

### File Structure Requirements

**Location:** `packages/pipeline/src/adapters/`

**Files to Create/Modify:**
1. `packages/pipeline/src/adapters/base.py` - SourceAdapter ABC
2. `packages/pipeline/src/adapters/pdf_adapter.py` - PdfAdapter implementation
3. `packages/pipeline/src/models/source.py` - Source Pydantic model
4. `tests/test_adapters/test_pdf_adapter.py` - Unit tests

**Module Initialization:**
```python
# packages/pipeline/src/adapters/__init__.py
from .base import SourceAdapter
from .pdf_adapter import PdfAdapter

__all__ = ["SourceAdapter", "PdfAdapter"]
```

### Testing Requirements

**Test Organization:**
- Tests in: `packages/pipeline/tests/test_adapters/test_pdf_adapter.py`
- Mirror src structure (per architecture)
- Shared fixtures in `tests/conftest.py`

**Test Cases Required:**
1. **Test successful PDF text extraction**
   - Use sample PDF file
   - Verify text content extracted
   - Verify position metadata (page numbers)
2. **Test metadata extraction**
   - PDF with metadata present
   - PDF with missing metadata (filename fallback)
3. **Test multi-column layout**
   - Sample multi-column PDF
   - Verify reading order preserved
4. **Test error handling**
   - Corrupted PDF file
   - Encrypted/password-protected PDF
   - Verify structured error responses

**Test Fixtures:**
```python
# conftest.py
@pytest.fixture
def sample_pdf_path(tmp_path):
    # Create or use sample PDF for testing
    return Path("tests/fixtures/sample.pdf")
```

### Previous Story Intelligence

**Story 2.1: Base Source Adapter Interface** (Previous story in this epic)
- If Story 2.1 exists, the `SourceAdapter` ABC should already be implemented
- If not, this story must create it as a prerequisite
- Check for existing `packages/pipeline/src/adapters/base.py`

**Expected from Story 2.1:**
- Abstract base class with `extract_text()` and `get_metadata()` methods
- Common text processing utilities
- Extensibility documentation (NFR5)

**Integration Point:**
This story implements the first concrete adapter extending the base interface.

### Latest Technical Information

**pymupdf (PyMuPDF) - Current Best Practices (2025):**

**Installation:**
```bash
uv add pymupdf  # Alias: fitz
```

**Key APIs:**
- `fitz.open(path)`: Open PDF document
- `doc.page_count`: Total pages
- `doc.metadata`: Dict of PDF metadata
- `doc.is_encrypted`: Check if password-protected
- `page.get_text("text")`: Extract plain text
- `page.get_text("blocks")`: Extract positioned text blocks

**Multi-Column Handling:**
```python
blocks = page.get_text("blocks")
# blocks format: (x0, y0, x1, y1, text, block_no, block_type)
# Sort by (y, x) to maintain reading order
sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
```

**Error Patterns:**
- `RuntimeError`: Corrupted PDF
- `fitz.fitz.FileDataError`: Invalid PDF structure
- Encrypted check: `if doc.is_encrypted: raise EncryptedError()`

**Performance Considerations:**
- pymupdf is C-based, very fast
- No need for async (CPU-bound)
- Process page-by-page to manage memory

### Project Context Reference

**Critical Rules from project-context.md:**

**Naming:**
- File: `pdf_adapter.py` (snake_case)
- Class: `PdfAdapter` (PascalCase)
- Functions: `extract_text`, `get_metadata` (snake_case)

**Error Handling:**
- Custom exceptions inherit from `KnowledgeError`
- Include: `code`, `message`, `details` dict
- Specific exception: Create `PdfProcessingError` or similar

**Code Quality:**
- No print statements (use structlog)
- Type hints on all functions
- Docstrings for public methods

**Testing:**
- Tests in separate `tests/` directory
- Mirror src structure
- Use pytest fixtures

**Package Boundary:**
- This is `packages/pipeline` - batch processing
- WRITE-only operations
- No HTTP serving

### Reference Links

**Source Documents:**
- [Epic 2 Context: epics.md#262-368](file:///Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/epics.md)
- [Architecture: Adapter Pattern](file:///Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/architecture.md#612-621)
- [Architecture: Project Structure](file:///Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/architecture.md#592-727)
- [PRD: Source Ingestion Requirements](file:///Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/prd.md#23-27)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
