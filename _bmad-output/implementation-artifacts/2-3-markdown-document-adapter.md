---
status: archived
archived_date: 2025-12-30
archived_reason: Merged into Story 2.2 (Docling Document Adapter)
note: Docling library handles Markdown natively, no separate adapter needed
see: epic-2-sprint-change-proposal.md
---

# Story 2.3: Markdown Document Adapter [ARCHIVED]

Status: archived

<!--
COURSE CORRECTION: 2025-12-30
This story has been ARCHIVED as part of the Epic 2 Docling refactor.
The Docling library handles Markdown documents natively, so no separate adapter is required.
See: epic-2-sprint-change-proposal.md for details.

The original story content is preserved below for historical reference.
-->

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **builder**,
I want to ingest Markdown documents,
So that I can extract content from markdown-based documentation and notes.

## Acceptance Criteria

**Given** a Markdown file path is provided
**When** I use the Markdown adapter to process the file
**Then** text is extracted with structure preserved (headings become section markers)
**And** source metadata (title from H1, path) is captured
**And** code blocks are preserved with language annotations
**And** links and images are handled appropriately

## Tasks / Subtasks

- [ ] Create MarkdownAdapter class extending SourceAdapter (AC: #1, #2, #3, #4)
  - [ ] Implement `extract_text()` method using markdown-it-py parser
  - [ ] Parse heading hierarchy to create section markers (H1=chapter, H2=section, H3=subsection)
  - [ ] Extract metadata: title from first H1, path from input
  - [ ] Preserve code blocks with language annotations for later processing
  - [ ] Handle inline links: extract href, preserve text
  - [ ] Handle images: extract alt text and path for later reference
  - [ ] Implement position tracking (line numbers, heading hierarchy)
- [ ] Add MarkdownAdapter to adapters module (AC: #1)
  - [ ] Export from `__init__.py`
  - [ ] Follow existing PdfAdapter pattern from Story 2.2
- [ ] Create Pydantic models for markdown-specific outputs (AC: #1, #2)
  - [ ] `MarkdownSection` model with heading level, title, content, position
  - [ ] `CodeBlock` model with language, content, line numbers
  - [ ] `Link` model with text, href, type (inline/reference)
- [ ] Add comprehensive tests for Markdown adapter (AC: #1-4)
  - [ ] Unit tests with sample markdown files
  - [ ] Test heading hierarchy extraction
  - [ ] Test code block preservation with language tags
  - [ ] Test link and image handling
  - [ ] Test metadata extraction (title from H1)
  - [ ] Test error cases (empty file, invalid encoding)

## Dev Notes

### Architecture Requirements

**From Architecture.md:**

**Adapter Pattern (FR-1: Source Ingestion):**
- Location: `packages/pipeline/src/adapters/`
- Base class: `SourceAdapter` (ABC) - should exist from Story 2.1/2.2
- Concrete implementation: `MarkdownAdapter` extends `SourceAdapter`
- NFR5 (Extensibility): Abstract adapter pattern enables new source types

**Project Structure:**
```
packages/pipeline/src/adapters/
├── __init__.py           # Add MarkdownAdapter export
├── base.py               # SourceAdapter ABC (from Story 2.1)
├── pdf_adapter.py        # PdfAdapter (from Story 2.2)
└── markdown_adapter.py   # NEW: MarkdownAdapter implementation
```

**Pydantic Models Required:**
- Use existing `Source` model (location: `packages/pipeline/src/models/source.py`)
- Fields: `id`, `type`, `title`, `authors[]`, `path`, `ingested_at`, `status`, `metadata{}`, `schema_version`
- For markdown: `type="markdown"`, `authors=[]` (empty unless specified in frontmatter)

**Dependencies:**
- `markdown-it-py`: Selected markdown parsing library (CommonMark compliant, fast, extensible)
- Add via: `uv add markdown-it-py`

**Naming Conventions (MANDATORY):**
- File: `markdown_adapter.py` (snake_case)
- Class: `MarkdownAdapter` (PascalCase)
- Methods: `extract_text()`, `get_metadata()` (snake_case)
- Module exports: `from .markdown_adapter import MarkdownAdapter`

### Technical Implementation Details

**Why markdown-it-py (over alternatives):**

| Library | Speed | CommonMark | Notes |
|---------|-------|------------|-------|
| mistune | Fastest | No | Edge-case inconsistencies |
| **markdown-it-py** | Fast | Yes | Best balance of speed + compliance |
| mistletoe | Medium | Yes | Less extensible |
| commonmark-py | Slow | Yes | Spec compliance > speed |

**markdown-it-py provides:**
- 100% CommonMark specification compliance
- Token-based parsing (access to AST)
- Extensible with plugins (tables, strikethrough, etc.)
- 2.33x slower than mistune but handles edge cases correctly

**Markdown Parsing with markdown-it-py:**
```python
from markdown_it import MarkdownIt

# Initialize with GFM (GitHub Flavored Markdown) support
md = MarkdownIt("gfm-like")

# Parse to tokens (AST-like structure)
tokens = md.parse(markdown_text)

# Process tokens to extract structure
for token in tokens:
    if token.type == "heading_open":
        level = int(token.tag[1])  # h1 -> 1, h2 -> 2
    elif token.type == "fence":
        # Code block
        language = token.info  # e.g., "python"
        code = token.content
```

**Token Types to Handle:**
- `heading_open/heading_close`: Section markers (H1-H6)
- `paragraph_open/paragraph_close`: Text paragraphs
- `fence`: Fenced code blocks (```language ... ```)
- `code_inline`: Inline code
- `link_open/link_close`: Links with `href` attribute
- `image`: Images with `src` and `alt` attributes
- `bullet_list_open/ordered_list_open`: Lists

**Structure Extraction Pattern:**
```python
def extract_structure(tokens: list) -> list[Section]:
    """Convert token stream to hierarchical sections."""
    sections = []
    current_section = None
    heading_stack = []  # Track heading hierarchy

    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            level = int(token.tag[1])
            # Next token contains heading text
            title = tokens[i + 1].content

            # Update heading stack for hierarchy tracking
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))

            # Create section with position info
            current_section = Section(
                level=level,
                title=title,
                hierarchy=[h[1] for h in heading_stack],
                line=token.map[0] if token.map else 0
            )
            sections.append(current_section)
```

**Metadata Extraction:**
- Title: First H1 heading content OR filename (fallback)
- Path: Input file path
- YAML frontmatter (optional): Parse if present for additional metadata

**Frontmatter Handling (Optional Enhancement):**
```python
import re

FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter if present."""
    match = FRONTMATTER_PATTERN.match(content)
    if match:
        import yaml
        frontmatter = yaml.safe_load(match.group(1))
        remaining_content = content[match.end():]
        return frontmatter, remaining_content
    return {}, content
```

**Code Block Preservation:**
- Store language annotation from fence info
- Preserve exact content including whitespace
- Track line numbers for source attribution

**Link/Image Handling:**
- Extract href/src for reference
- Preserve visible text/alt text for content
- Track relative vs absolute URLs

### Library/Framework Requirements

**markdown-it-py - Latest Stable:**
- CommonMark compliant markdown parser
- Token-based parsing provides AST access
- Install: `uv add markdown-it-py`
- GFM support via `MarkdownIt("gfm-like")`

**Pydantic v2:**
- All models use Pydantic v2 syntax
- `snake_case` field names
- `schema_version` field on all models

**Python 3.11+:**
- Type hints required for all function signatures
- Use modern syntax (match/case, improved type annotations)

**structlog:**
- All logging via structlog
- No print statements

### File Structure Requirements

**Location:** `packages/pipeline/src/adapters/`

**Files to Create/Modify:**
1. `packages/pipeline/src/adapters/markdown_adapter.py` - NEW: MarkdownAdapter implementation
2. `packages/pipeline/src/adapters/__init__.py` - ADD: MarkdownAdapter export
3. `tests/test_adapters/test_markdown_adapter.py` - NEW: Unit tests

**Module Initialization Update:**
```python
# packages/pipeline/src/adapters/__init__.py
from .base import SourceAdapter
from .pdf_adapter import PdfAdapter
from .markdown_adapter import MarkdownAdapter  # ADD

__all__ = ["SourceAdapter", "PdfAdapter", "MarkdownAdapter"]  # UPDATE
```

### Testing Requirements

**Test Organization:**
- Tests in: `packages/pipeline/tests/test_adapters/test_markdown_adapter.py`
- Mirror src structure (per architecture)
- Shared fixtures in `tests/conftest.py`

**Test Cases Required:**

1. **Test successful markdown text extraction**
   - Use sample markdown file with mixed content
   - Verify text content extracted correctly
   - Verify structure (headings, paragraphs) preserved

2. **Test heading hierarchy extraction**
   - Markdown with H1, H2, H3 headings
   - Verify section markers created correctly
   - Verify hierarchy tracking (H1 > H2 > H3)

3. **Test code block preservation**
   - Code blocks with language annotation
   - Code blocks without language annotation
   - Inline code preservation
   - Verify language tags captured

4. **Test metadata extraction**
   - Title from first H1
   - Title from filename (no H1 fallback)
   - Optional: frontmatter parsing

5. **Test link and image handling**
   - Inline links `[text](url)`
   - Reference links
   - Images with alt text
   - Relative vs absolute paths

6. **Test error handling**
   - Empty markdown file
   - File with only frontmatter
   - Invalid encoding (non-UTF-8)
   - Verify structured error responses

**Sample Test Fixtures:**
```python
# tests/fixtures/sample.md
---
title: Sample Document
author: Test Author
---

# Main Title

Introduction paragraph.

## Section 1

Content with **bold** and *italic*.

### Subsection 1.1

```python
def hello():
    print("Hello, World!")
```

## Section 2

A [link](https://example.com) and an ![image](./img.png).
```

**Test Fixtures Setup:**
```python
# conftest.py
@pytest.fixture
def sample_markdown_path(tmp_path):
    """Create sample markdown file for testing."""
    md_file = tmp_path / "sample.md"
    md_file.write_text(SAMPLE_MARKDOWN_CONTENT)
    return md_file

@pytest.fixture
def markdown_adapter():
    """Return MarkdownAdapter instance."""
    return MarkdownAdapter()
```

### Previous Story Intelligence

**Story 2.2: PDF Document Adapter** (Previous story in this epic)
- The `SourceAdapter` ABC should already be implemented
- `PdfAdapter` pattern established - follow same structure
- Existing file: `packages/pipeline/src/adapters/base.py`
- Existing file: `packages/pipeline/src/adapters/pdf_adapter.py`

**Expected from Story 2.2:**
- Abstract base class with `extract_text()` and `get_metadata()` methods
- Common text processing utilities
- Error handling pattern with `KnowledgeError` subclasses
- Source model with metadata fields

**Key Patterns from PDF Adapter to Follow:**
1. Same interface: `extract_text(file_path: Path) -> ExtractedContent`
2. Same metadata structure: `get_metadata(file_path: Path) -> SourceMetadata`
3. Same error handling: Raise structured `KnowledgeError` subclasses
4. Same logging: Use structlog for all logging

**Differences from PDF Adapter:**
- No multi-column layout concerns (markdown is linear)
- Has heading hierarchy (PDF has chapter/section from position)
- Has code blocks with language annotations
- May have YAML frontmatter metadata
- No password protection concerns

### Latest Technical Information

**markdown-it-py - Current Best Practices (2025):**

**Installation:**
```bash
uv add markdown-it-py
```

**Key APIs:**
```python
from markdown_it import MarkdownIt

# Initialize with presets
md = MarkdownIt()  # CommonMark
md = MarkdownIt("gfm-like")  # GitHub Flavored Markdown

# Parse to tokens (AST)
tokens = md.parse(content)

# Render to HTML (if needed)
html = md.render(content)
```

**Token Properties:**
- `token.type`: Token type (heading_open, paragraph_open, fence, etc.)
- `token.tag`: HTML tag (h1, h2, p, code, etc.)
- `token.content`: Text content
- `token.info`: Additional info (e.g., language for code fence)
- `token.map`: Line mapping [start, end] for source tracking
- `token.attrs`: Attributes (e.g., href for links)

**GFM Extensions (gfm-like preset includes):**
- Tables
- Strikethrough
- Task lists
- Autolinks

**Performance Considerations:**
- markdown-it-py is pure Python, fast enough for batch processing
- No need for async (CPU-bound)
- Process file-by-file for memory management
- Token parsing is faster than full HTML rendering (use parse() not render())

### Project Context Reference

**Critical Rules from project-context.md:**

**Naming:**
- File: `markdown_adapter.py` (snake_case)
- Class: `MarkdownAdapter` (PascalCase)
- Functions: `extract_text`, `get_metadata` (snake_case)

**Error Handling:**
- Custom exceptions inherit from `KnowledgeError`
- Include: `code`, `message`, `details` dict
- Specific exception: Create `MarkdownProcessingError` or similar

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
- [Epic 2 Context: epics.md#262-368](epics.md) - Story 2.3 acceptance criteria
- [Architecture: Adapter Pattern](architecture.md#612-621) - Adapter ABC pattern
- [Architecture: Project Structure](architecture.md#592-727) - Directory layout
- [PRD: Source Ingestion Requirements](prd.md#238-249) - FR-1.2 Markdown adapter

**External References:**
- [markdown-it-py GitHub](https://github.com/executablebooks/markdown-it-py) - Library documentation
- [CommonMark Spec](https://commonmark.org/) - Markdown specification

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
