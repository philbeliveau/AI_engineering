# Known Issues & Workarounds

## Docling PDF Parsing Failure with FrameMaker PDFs

**Date Discovered:** 2026-01-05
**Affected Component:** `packages/pipeline/src/adapters/docling_adapter.py`
**Status:** Workaround available

### Problem

Docling fails to extract text from PDFs created with **Adobe FrameMaker** that use hierarchical page tree structures. Only a fraction of pages are processed.

**Example:** A 456-page book yielded only 3,611 characters (should be ~1M characters).

### Root Cause

FrameMaker creates PDFs with nested page tree nodes:

```
/Type /Pages (root)
/Count 6           ← 6 child NODES, not pages
/Kids [node1, node2, ...]

/Type /Pages (node1)
/Count 51          ← 51 actual pages
/Kids [page1, page2, ...]
```

Docling's pypdfium2 backend reads only the root `/Count 6` instead of recursively traversing the tree.

**Evidence:**
- `file` command: Reports "6 pages" (wrong)
- `pdfinfo` (Poppler): Reports "456 pages" (correct)
- `pdftotext` (Poppler): Extracts full content (correct)
- Docling: Extracts only ~6 pages worth of content (bug)

### Affected PDFs

- Created with FrameMaker 16.x
- Modified with iText Core
- Large documents (100+ pages) with nested page trees

### Workaround

Use `pdftotext` to extract content, then ingest the resulting text file:

```bash
# Extract PDF to text/markdown
pdftotext -layout "book.pdf" "book.md"

# Ingest the text file instead
uv run scripts/ingest.py book.md --project ai_engineering
```

### Related Issues

- [Docling Issue #2021](https://github.com/docling-project/docling/issues/2021): No text extraction from certain PDFs
- [Docling Issue #920](https://github.com/docling-project/docling/issues/920): Page numbers excluded from document index
- [qpdf Discussion #10](https://github.com/qpdf/qpdf-dev/discussions/10): Page tree validation and repair

### Potential Fix

Per Issue #2021, switching backends may help:

```python
from docling.backend.pypdfium_backend import PyPdfiumDocumentBackend

# Use alternative backend
converter = DocumentConverter(
    backend=PyPdfiumDocumentBackend
)
```

However, this hasn't been tested with FrameMaker PDFs.

### Recommendation

Report this issue to [docling-project/docling](https://github.com/docling-project/docling/issues) with:
1. Sample PDF created with FrameMaker
2. Output of `pdfinfo` showing correct page count
3. Docling output showing incorrect extraction
