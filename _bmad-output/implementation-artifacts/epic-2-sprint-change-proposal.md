# Sprint Change Proposal: Epic 2 Docling Refactor

**Date:** 2025-12-30
**Prepared By:** Correct Course Task (Automated Analysis)
**Status:** Pending Approval
**Change Trigger Document:** `epic-2-docling-refactor-handoff.md`

---

## Executive Summary

### Change Description

Replace separate PDF/Markdown adapters (pymupdf + markdown-it-py) with IBM's **Docling** library for unified document processing in Epic 2: Document Ingestion Pipeline.

### Impact Assessment Summary

| Metric | Value |
|--------|-------|
| Stories Affected | 4 of 6 (67%) |
| Stories Unchanged | 2 (Stories 2.1 and 2.5) |
| Scope Change | Reduction (fewer files, unified approach) |
| Risk Level | Low-Medium (library replacement in early development) |
| MVP Impact | Positive (faster delivery, more formats supported) |
| Architecture Impact | Minimal (same interfaces, different implementation) |

### Recommended Path

**Proceed with Docling refactor.** The change simplifies the codebase, improves extraction quality, and adds support for additional formats (DOCX, HTML, PPTX) with minimal disruption since implementation is early-stage.

---

## Section 1: Change Context Analysis

### 1.1 Original Trigger

**Source:** User-initiated architectural improvement during Story 2.2 (PDF Document Adapter) implementation.

**Trigger Type:** Proactive Optimization - Not a defect, but identification of a superior technical approach before completing the current implementation.

### 1.2 Current Sprint State

**Epic 2 Status:** `in-progress`

| Story | Original Status | Notes |
|-------|-----------------|-------|
| 2.1 - Base Source Adapter Interface | done | Keep unchanged |
| 2.2 - PDF Document Adapter | in-progress | 286 lines PyMuPDF code exists (DELETE) |
| 2.3 - Markdown Document Adapter | ready-for-dev | Not yet started (ARCHIVE) |
| 2.4 - Text Chunking Processor | ready-for-dev | Not yet started (REWRITE) |
| 2.5 - Local Embedding Generator | ready-for-dev | Keep unchanged |
| 2.6 - End-to-End Pipeline | ready-for-dev | Not yet started (UPDATE) |

### 1.3 Existing Implementation

**Files Currently Existing:**
- `packages/pipeline/src/adapters/base.py` - SourceAdapter ABC (Story 2.1) - **KEEP**
- `packages/pipeline/src/adapters/pdf_adapter.py` - 286 lines PyMuPDF - **DELETE**
- `packages/pipeline/src/adapters/__init__.py` - Exports - **MODIFY**
- `packages/pipeline/tests/test_adapters/conftest.py` - Fixtures - **MODIFY**
- `packages/pipeline/tests/test_adapters/test_pdf_adapter.py` - Tests - **DELETE**

### 1.4 Reason for Change

| Aspect | Before (pymupdf + markdown-it-py) | After (Docling) |
|--------|-----------------------------------|-----------------|
| Libraries | 2 separate libraries | 1 unified library |
| Adapters | 2 separate adapters | 1 unified adapter |
| Formats | PDF, Markdown only | PDF, Markdown, DOCX, HTML, PPTX |
| Tables | Basic extraction | Structured table extraction |
| Chunking | Manual implementation (Story 2.4) | Built-in HybridChunker |
| Tokenizer | Heuristic (~4 chars/token) | Uses actual embedding model tokenizer |
| Maintenance | 2 implementations to maintain | 1 implementation |

---

## Section 2: Epic/Story Impact Analysis

### 2.1 Story 2.1: Base Source Adapter Interface

**Action:** NO CHANGES

**Rationale:** The existing `SourceAdapter` ABC, `AdapterResult`, `Section` models, and adapter registry remain valid. The Docling adapter will implement this same interface, preserving the extensibility pattern (NFR5).

**Existing Artifacts Impacted:** None

---

### 2.2 Story 2.2: PDF Document Adapter → Docling Document Adapter

**Action:** COMPLETE REWRITE

**Scope Change:**
- **Old:** Create PdfAdapter using pymupdf for PDF-only extraction
- **New:** Create DoclingAdapter using Docling for multi-format extraction

**Files Impacted:**
| File | Action | Reason |
|------|--------|--------|
| `2-2-pdf-document-adapter.md` | REWRITE | New scope, title, tasks |
| `pdf_adapter.py` | DELETE | Replaced by docling_adapter.py |
| `test_pdf_adapter.py` | DELETE | Replaced by test_docling_adapter.py |
| `docling_adapter.py` | CREATE | New unified adapter |
| `test_docling_adapter.py` | CREATE | New test suite |
| `pyproject.toml` | MODIFY | Replace pymupdf with docling |

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

---

### 2.3 Story 2.3: Markdown Document Adapter

**Action:** ARCHIVE/REMOVE FROM SPRINT

**Rationale:** Docling handles Markdown natively. Story 2.2 (Docling Adapter) now covers this functionality.

**Files Impacted:**
| File | Action | Reason |
|------|--------|--------|
| `2-3-markdown-document-adapter.md` | ARCHIVE | Merged into Story 2.2 |
| `markdown_adapter.py` | SKIP | Never created, not needed |
| `test_markdown_adapter.py` | SKIP | Never created, not needed |

---

### 2.4 Story 2.4: Text Chunking Processor

**Action:** REWRITE APPROACH

**Scope Change:**
- **Old:** Manual sentence boundary detection, sliding window with overlap, custom TextChunker class, token estimation (~4 chars/token)
- **New:** Use Docling's `HybridChunker`, configure with `all-MiniLM-L6-v2` tokenizer, accurate token counting

**Files Impacted:**
| File | Action | Reason |
|------|--------|--------|
| `2-4-text-chunking-processor.md` | REWRITE | New implementation approach |
| `chunker.py` | REWRITE | Wrap HybridChunker instead of manual |
| `test_chunker.py` | MODIFY | Update for DoclingDocument fixtures |

**What to Keep:**
- `ChunkerConfig` model (for pipeline configuration)
- `ChunkOutput` model (for storage compatibility)
- Exception classes (`ChunkerError`, `EmptyContentError`, `ChunkSizeError`)
- Module exports pattern

**What to Remove:**
- Manual sentence boundary detection functions
- Sliding window logic
- Character-based token estimation

---

### 2.5 Story 2.5: Local Embedding Generator

**Action:** NO CHANGES

**Rationale:** The embedding generator using `sentence-transformers/all-MiniLM-L6-v2` remains unchanged. It receives chunk text from the new Docling-based chunker.

---

### 2.6 Story 2.6: End-to-End Ingestion Pipeline

**Action:** UPDATE REFERENCES

**Scope Change:**
- **Old:** Import PdfAdapter + MarkdownAdapter, separate adapter registrations
- **New:** Import DoclingAdapter only, single adapter handles all formats

**Files Impacted:**
| File | Action | Reason |
|------|--------|--------|
| `2-6-end-to-end-ingestion-pipeline.md` | UPDATE | Update references and imports |
| `pipeline.py` | MODIFY | Update imports when implemented |
| CLI help text | MODIFY | Reflect supported formats |

**Updated Pipeline Flow:**
```
1. Validate file exists
2. Get DoclingAdapter from registry (handles .pdf, .md, .docx, .html, .pptx)
3. adapter.extract_text() -> AdapterResult with DoclingDocument
4. DoclingChunker.chunk_document() -> list[ChunkOutput]
5. LocalEmbedder.embed_batch() -> 384d vectors
6. Store: MongoDB (sources, chunks), Qdrant (vectors)
```

---

## Section 3: Artifact Conflict Resolution

### 3.1 Dependency Changes (pyproject.toml)

**Add:**
```toml
docling = "^2.66"           # Unified document processing
transformers = "^4.40"      # Required for HuggingFaceTokenizer in chunking
```

**Remove:**
```toml
pymupdf                     # Replaced by Docling
markdown-it-py              # Replaced by Docling (if added)
```

### 3.2 Module Exports (__init__.py)

**Before:**
```python
from .base import SourceAdapter, AdapterResult, Section
from .pdf_adapter import PdfAdapter

__all__ = ["SourceAdapter", "AdapterResult", "Section", "PdfAdapter"]
```

**After:**
```python
from .base import SourceAdapter, AdapterResult, Section
from .docling_adapter import DoclingAdapter

__all__ = ["SourceAdapter", "AdapterResult", "Section", "DoclingAdapter"]
```

### 3.3 Adapter Registry

**Before:** Would register PdfAdapter and MarkdownAdapter separately
**After:** Single DoclingAdapter registration handles all formats

---

## Section 4: Path Evaluation & Recommendation

### 4.1 Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A: Full Docling Refactor** | Replace all adapters with unified Docling | Simpler codebase, better extraction, more formats | Learning curve for Docling API |
| B: Hybrid Approach | Keep PdfAdapter, add Docling for new formats | Less code deletion | Inconsistent patterns, 2 libraries to maintain |
| C: Continue Original Plan | Complete pymupdf + markdown-it-py | No rework | Technical debt, worse extraction, fewer formats |

### 4.2 Recommendation

**Option A: Full Docling Refactor**

**Rationale:**
1. **Early Stage:** Story 2.2 is in-progress but not merged/deployed. Minimal sunk cost.
2. **Simplification:** One library instead of two reduces maintenance burden.
3. **Quality Improvement:** Docling provides better table extraction and document structure.
4. **Format Expansion:** Gains DOCX, HTML, PPTX support at no additional cost.
5. **Chunking Integration:** HybridChunker uses actual tokenizer, improving chunk quality.
6. **Verified API:** Handoff document includes Context7-verified implementation patterns.

**Risks & Mitigations:**
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Docling API breaking changes | Low | Medium | Pin to ^2.66, test thoroughly |
| Performance regression | Low | Medium | Benchmark against current code |
| Missing edge case handling | Medium | Low | Comprehensive test suite |

---

## Section 5: Specific Proposed Edits

### 5.1 Sprint Status File (sprint-status.yaml)

**Change From:**
```yaml
development_status:
  # Epic 2: Document Ingestion Pipeline
  epic-2: in-progress
  2-1-base-source-adapter-interface: done
  2-2-pdf-document-adapter: in-progress
  2-3-markdown-document-adapter: ready-for-dev
  2-4-text-chunking-processor: ready-for-dev
  2-5-local-embedding-generator: ready-for-dev
  2-6-end-to-end-ingestion-pipeline: ready-for-dev
```

**Change To:**
```yaml
development_status:
  # Epic 2: Document Ingestion Pipeline
  epic-2: in-progress
  2-1-base-source-adapter-interface: done
  2-2-docling-document-adapter: ready-for-dev    # RENAMED & RESET
  2-3-markdown-document-adapter: archived        # MERGED INTO 2.2
  2-4-text-chunking-processor: ready-for-dev     # REWRITE NEEDED
  2-5-local-embedding-generator: ready-for-dev   # NO CHANGE
  2-6-end-to-end-ingestion-pipeline: ready-for-dev # UPDATE NEEDED
```

---

### 5.2 Story 2.2 File (2-2-pdf-document-adapter.md → 2-2-docling-document-adapter.md)

**Action:** RENAME file and REPLACE entire contents

**New Filename:** `2-2-docling-document-adapter.md`

**New Contents:** (Summary - full content in handoff document)

```markdown
# Story 2.2: Docling Document Adapter

Status: ready-for-dev

## Story

As a **builder**,
I want to ingest documents using Docling,
So that I can extract structured content from PDFs, Markdown, DOCX, HTML, and PPTX files with a unified adapter.

## Acceptance Criteria

Given a document file path (PDF, MD, DOCX, HTML, or PPTX)
When I use the Docling adapter to process the file
Then text is extracted with structure preserved (headings, tables, lists)
And source metadata (title, authors if detectable, path) is captured
And sections include hierarchy information
And position metadata (page numbers for PDF) is tracked
And errors are raised for corrupted or unsupported files

## Tasks / Subtasks

- [ ] Add `docling = "^2.66"` and `transformers = "^4.40"` to pyproject.toml
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

## Dev Notes

[Include implementation patterns from handoff document]
```

---

### 5.3 Story 2.3 File (2-3-markdown-document-adapter.md)

**Action:** Add ARCHIVED notice at top of file

**Add to Line 1-10:**
```markdown
---
status: archived
archived_date: 2025-12-30
archived_reason: Merged into Story 2.2 (Docling Document Adapter)
note: Docling library handles Markdown natively, no separate adapter needed
---

# Story 2.3: Markdown Document Adapter [ARCHIVED]

**STATUS: ARCHIVED - Merged into Story 2.2**

This story has been archived as part of the Docling refactor. The Docling library
handles Markdown documents natively, so no separate adapter is required.

See: `epic-2-sprint-change-proposal.md` for details.

---

[Original content preserved below for reference]
```

---

### 5.4 Story 2.4 File (2-4-text-chunking-processor.md)

**Action:** UPDATE sections to reflect HybridChunker approach

**Changes Required:**

**1. Update Story Description:**
```markdown
## Story

As a **developer**,
I want to use Docling's HybridChunker for text chunking,
So that chunks respect document structure and use accurate token counting from the embedding model's tokenizer.
```

**2. Update Acceptance Criteria:**
```markdown
## Acceptance Criteria

Given extracted content from DoclingAdapter
When I process it through the chunker
Then text is split using Docling's HybridChunker
And chunks respect section boundaries from the document structure
And token counts use the all-MiniLM-L6-v2 tokenizer (accurate, not estimated)
And each chunk includes position metadata
And ChunkOutput models are compatible with MongoDB storage
```

**3. Update Tasks:**
- Remove tasks for manual sentence boundary detection
- Remove tasks for sliding window implementation
- Add tasks for HybridChunker wrapper implementation
- Add task for HuggingFaceTokenizer configuration
- Update test tasks for DoclingDocument fixtures

**4. Update Dev Notes:**
Add new implementation pattern from handoff document.

---

### 5.5 Story 2.6 File (2-6-end-to-end-ingestion-pipeline.md)

**Action:** UPDATE references and imports

**Changes Required:**

**1. Update Dependency Analysis:**
```markdown
## Dependency Analysis

**Depends On:**
- **Story 2.1** (Base Source Adapter Interface) - MUST be completed
- **Story 2.2** (Docling Document Adapter) - MUST be completed
  - Provides unified DoclingAdapter for all document types
  - Supports: PDF, Markdown, DOCX, HTML, PPTX
- ~~**Story 2.3** (Markdown Document Adapter)~~ - ARCHIVED: Merged into Story 2.2
- **Story 2.4** (Text Chunking Processor) - MUST be completed
  - Uses DoclingChunker wrapper around HybridChunker
```

**2. Update Task 3 (Adapter Selection):**
```markdown
- [ ] **Task 3: Integrate Adapter Selection** (AC: Multi-format support)
  - [ ] Use `adapter_registry.get_adapter(file_path)` from Story 2.1
  - [ ] DoclingAdapter handles all formats: .pdf, .md, .docx, .html, .pptx
  - [ ] Raise `UnsupportedFileError` for unsupported types
  - [ ] Log adapter selection: `logger.info("adapter_selected", type="docling")`
```

**3. Update Acceptance Criteria line 1:**
```markdown
Given a document path (PDF, Markdown, DOCX, HTML, or PPTX)
```

---

### 5.6 Epics File (epics.md)

**Action:** No immediate changes required.

The epics.md file contains the original story definitions. Since we're using story files for implementation, we can either:
1. Leave epics.md as historical reference
2. Add a note referencing the sprint change proposal

**Recommended:** Add note after Story 2.2 and 2.3 definitions pointing to the change proposal.

---

### 5.7 Files to Create/Delete

| Action | File Path | Reason |
|--------|-----------|--------|
| DELETE | `packages/pipeline/src/adapters/pdf_adapter.py` | Replaced by docling_adapter.py |
| DELETE | `packages/pipeline/tests/test_adapters/test_pdf_adapter.py` | Replaced |
| CREATE | `packages/pipeline/src/adapters/docling_adapter.py` | New unified adapter |
| CREATE | `packages/pipeline/tests/test_adapters/test_docling_adapter.py` | New tests |
| RENAME | `2-2-pdf-document-adapter.md` → `2-2-docling-document-adapter.md` | New scope |
| MODIFY | `packages/pipeline/pyproject.toml` | Dependency changes |
| MODIFY | `packages/pipeline/src/adapters/__init__.py` | Export changes |
| MODIFY | `packages/pipeline/src/processors/chunker.py` | HybridChunker approach |

---

## Section 6: Implementation Order

### Phase 1: Cleanup & Setup
1. Delete `pdf_adapter.py` and `test_pdf_adapter.py`
2. Update `pyproject.toml` (add docling, remove pymupdf)
3. Run `uv sync` to update lock file
4. Update sprint-status.yaml

### Phase 2: Story 2.2 (Docling Adapter)
1. Rename story file to `2-2-docling-document-adapter.md`
2. Update story content with new scope
3. Implement DoclingAdapter
4. Create test suite
5. Update adapter registry exports

### Phase 3: Story 2.4 (Chunking Refactor)
1. Update story file with HybridChunker approach
2. Implement DoclingChunker wrapper
3. Update test fixtures for DoclingDocument
4. Verify integration with adapter

### Phase 4: Story 2.6 (Pipeline Updates)
1. Update story file references
2. Implementation uses new adapter/chunker (when Story 2.6 is developed)

---

## Section 7: Success Criteria

| Criterion | Verification Method |
|-----------|-------------------|
| Story 2.2 rewritten | File renamed and content updated |
| Story 2.3 archived | Status marked as archived |
| Story 2.4 updated | Reflects HybridChunker approach |
| Story 2.6 updated | References DoclingAdapter |
| Sprint status updated | New story states reflected |
| Dependencies updated | pyproject.toml has docling, not pymupdf |
| Old code deleted | pdf_adapter.py removed |
| Tests pass | New DoclingAdapter test suite passes |

---

## Approval

**This Sprint Change Proposal requires user approval before implementation.**

Upon approval:
1. Story files will be updated as specified
2. Sprint status will be modified
3. Existing pdf_adapter.py code will be deleted
4. Development can proceed with the new Docling-based approach

---

## References

- **Handoff Document:** `_bmad-output/implementation-artifacts/epic-2-docling-refactor-handoff.md`
- **Architecture:** `_bmad-output/architecture.md`
- **Epics:** `_bmad-output/epics.md`
- **PRD:** `_bmad-output/prd.md`
- **Project Context:** `_bmad-output/project-context.md`
- **Docling Documentation:** https://ds4sd.github.io/docling/
