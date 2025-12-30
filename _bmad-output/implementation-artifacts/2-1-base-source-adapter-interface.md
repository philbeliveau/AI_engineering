# Story 2.1: Base Source Adapter Interface

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want an abstract base class (ABC) for source adapters,
So that all document adapters follow a consistent interface and new adapters can be easily added.

## Acceptance Criteria

**Given** the adapters module exists
**When** I create a new adapter by extending SourceAdapter
**Then** the adapter must implement `extract_text()` and `get_metadata()` methods
**And** the base class provides common utilities for text processing
**And** the pattern follows NFR5 (Extensibility for Adapters)

## Dependency Analysis

**Depends On:**
- **Story 1.1** (Initialize Monorepo Structure) - MUST be completed first
  - Requires `packages/pipeline/src/` directory structure
  - Requires Python 3.11+ environment with uv
- **Story 1.3** (Pydantic Models for Core Entities) - MUST be completed first
  - Requires `Source` Pydantic model for metadata structure
  - Requires schema version pattern for document evolution
- **Story 1.4** (MongoDB Storage Client) - Recommended completed
  - Provides storage patterns that adapters will integrate with

**Blocks:**
- **Story 2.2** (PDF Document Adapter) - Needs base class to extend
- **Story 2.3** (Markdown Document Adapter) - Needs base class to extend
- **Story 2.6** (End-to-End Ingestion Pipeline) - Uses adapters for document processing

## Tasks / Subtasks

- [x] **Task 1: Verify Prerequisites** (AC: Dependencies available)
  - [x] Confirm Story 1.1 complete: `ls packages/pipeline/pyproject.toml`
  - [x] Confirm Story 1.3 complete: `cd packages/pipeline && uv run python -c "from src.models import Source; print('OK')"`
  - [x] Confirm Python 3.11+: `cd packages/pipeline && uv run python --version`

- [x] **Task 2: Create Adapters Module Structure** (AC: Module exists)
  - [x] Create `packages/pipeline/src/adapters/` directory
  - [x] Create `packages/pipeline/src/adapters/__init__.py`
  - [x] Create `packages/pipeline/src/adapters/base.py`

- [x] **Task 3: Define Adapter Data Models** (AC: Type-safe structures)
  - [x] Create `AdapterResult` Pydantic model with fields:
    - `text: str` - Extracted raw text content
    - `metadata: dict` - Source metadata (title, authors, path, type)
    - `sections: list[Section]` - Optional structured sections
  - [x] Create `Section` Pydantic model with fields:
    - `title: str` - Section heading
    - `content: str` - Section text content
    - `level: int` - Heading level (1-6)
    - `position: dict` - Position metadata (page, chapter, offset)
  - [x] Create `AdapterConfig` Pydantic model for adapter settings

- [x] **Task 4: Implement SourceAdapter ABC** (AC: Abstract methods defined)
  - [x] Create `SourceAdapter` abstract base class
  - [x] Define abstract method: `extract_text(file_path: Path) -> AdapterResult`
  - [x] Define abstract method: `get_metadata(file_path: Path) -> dict`
  - [x] Define abstract method: `supports_file(file_path: Path) -> bool`
  - [x] Add `__init__(self, config: AdapterConfig = None)` constructor
  - [x] Add class attribute: `SUPPORTED_EXTENSIONS: list[str]`

- [x] **Task 5: Implement Common Utilities** (AC: Utilities available)
  - [x] Implement `_normalize_whitespace(text: str) -> str` - Clean excess whitespace
  - [x] Implement `_extract_title_from_path(file_path: Path) -> str` - Fallback title extraction
  - [x] Implement `_validate_file_exists(file_path: Path) -> None` - Raises FileNotFoundError
  - [x] Implement `_validate_file_extension(file_path: Path) -> None` - Raises UnsupportedFileError
  - [x] Implement `_calculate_token_estimate(text: str) -> int` - Rough token count

- [x] **Task 6: Implement Adapter Exceptions** (AC: Error handling)
  - [x] Create `AdapterError` base exception inheriting from `KnowledgeError`
  - [x] Create `UnsupportedFileError` for unsupported file types
  - [x] Create `FileParseError` for parsing failures
  - [x] Create `MetadataExtractionError` for metadata extraction failures
  - [x] All exceptions follow structured format: `{code, message, details}`

- [x] **Task 7: Implement Adapter Registry** (AC: Extensibility pattern)
  - [x] Create `AdapterRegistry` class for managing adapters
  - [x] Implement `register(extension: str, adapter_class: Type[SourceAdapter])` method
  - [x] Implement `get_adapter(file_path: Path) -> SourceAdapter` method
  - [x] Implement `list_supported_extensions() -> list[str]` method
  - [x] Create module-level registry instance: `adapter_registry = AdapterRegistry()`

- [x] **Task 8: Create Module Exports** (AC: Clean imports)
  - [x] Export from `packages/pipeline/src/adapters/__init__.py`:
    - `SourceAdapter`
    - `AdapterResult`, `Section`, `AdapterConfig`
    - `AdapterError`, `UnsupportedFileError`, `FileParseError`, `MetadataExtractionError`
    - `AdapterRegistry`, `adapter_registry`
  - [x] Verify imports work: `from src.adapters import SourceAdapter, AdapterResult`

- [x] **Task 9: Create Unit Tests** (AC: ABC works correctly)
  - [x] Create `packages/pipeline/tests/test_adapters/` directory
  - [x] Create `packages/pipeline/tests/test_adapters/conftest.py` with test fixtures
  - [x] Create `packages/pipeline/tests/test_adapters/test_base.py`
  - [x] Test that SourceAdapter cannot be instantiated directly
  - [x] Test that concrete implementation must define abstract methods
  - [x] Test utility methods work correctly
  - [x] Test registry registers and retrieves adapters
  - [x] Test exception hierarchy and structured error format
  - [x] Document test results in completion notes

## Dev Notes

### NFR5 Extensibility Pattern Requirement

**From Architecture Document (architecture.md:80):**

> NFR5: Extensibility (Adapters) - Abstract adapter patterns enabling new source types

This story implements the core adapter pattern that enables easy addition of new document types (PDF, Markdown, arXiv, web scraping, etc.) without modifying existing code.

### Architecture-Specified Directory Structure

**From Architecture Document (architecture.md:612-618):**

```
packages/pipeline/
├── src/
│   ├── __init__.py
│   ├── adapters/              # FR-1: Source Ingestion <-- YOUR WORK HERE
│   │   ├── __init__.py
│   │   ├── base.py            # SourceAdapter ABC
│   │   ├── pdf_adapter.py     # Story 2.2
│   │   ├── markdown_adapter.py # Story 2.3
│   │   └── arxiv_adapter.py   # Post-MVP
```

### Abstract Base Class Pattern

**Reference Implementation:**

```python
# packages/pipeline/src/adapters/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Type
from pydantic import BaseModel
import structlog

from src.exceptions import KnowledgeError

logger = structlog.get_logger()


class Section(BaseModel):
    """Represents a document section with position metadata."""
    title: str
    content: str
    level: int = 1
    position: dict = {}  # {page, chapter, offset}


class AdapterResult(BaseModel):
    """Result of adapter text extraction."""
    text: str
    metadata: dict
    sections: list[Section] = []


class AdapterConfig(BaseModel):
    """Configuration for adapter behavior."""
    preserve_structure: bool = True
    include_metadata: bool = True
    max_section_depth: int = 3


class AdapterError(KnowledgeError):
    """Base exception for adapter errors."""
    pass


class UnsupportedFileError(AdapterError):
    """Raised when file type is not supported."""
    def __init__(self, file_path: Path, supported: list[str]):
        super().__init__(
            code="UNSUPPORTED_FILE",
            message=f"File type not supported: {file_path.suffix}",
            details={"path": str(file_path), "supported": supported}
        )


class FileParseError(AdapterError):
    """Raised when file parsing fails."""
    def __init__(self, file_path: Path, reason: str):
        super().__init__(
            code="FILE_PARSE_ERROR",
            message=f"Failed to parse file: {reason}",
            details={"path": str(file_path), "reason": reason}
        )


class MetadataExtractionError(AdapterError):
    """Raised when metadata extraction fails."""
    def __init__(self, file_path: Path, reason: str):
        super().__init__(
            code="METADATA_EXTRACTION_ERROR",
            message=f"Failed to extract metadata: {reason}",
            details={"path": str(file_path), "reason": reason}
        )


class SourceAdapter(ABC):
    """Abstract base class for document source adapters.

    All document adapters must extend this class and implement
    the abstract methods for text extraction and metadata retrieval.

    Attributes:
        SUPPORTED_EXTENSIONS: List of file extensions this adapter handles.
        config: Adapter configuration settings.

    Example:
        class PdfAdapter(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".pdf"]

            def extract_text(self, file_path: Path) -> AdapterResult:
                # Implementation here
                pass

            def get_metadata(self, file_path: Path) -> dict:
                # Implementation here
                pass

            def supports_file(self, file_path: Path) -> bool:
                return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    """

    SUPPORTED_EXTENSIONS: list[str] = []

    def __init__(self, config: Optional[AdapterConfig] = None):
        """Initialize adapter with optional configuration.

        Args:
            config: Adapter configuration. Uses defaults if not provided.
        """
        self.config = config or AdapterConfig()
        logger.debug(
            "adapter_initialized",
            adapter=self.__class__.__name__,
            extensions=self.SUPPORTED_EXTENSIONS
        )

    @abstractmethod
    def extract_text(self, file_path: Path) -> AdapterResult:
        """Extract text content from a document.

        Args:
            file_path: Path to the document file.

        Returns:
            AdapterResult with extracted text, metadata, and sections.

        Raises:
            FileNotFoundError: If file does not exist.
            UnsupportedFileError: If file type is not supported.
            FileParseError: If file parsing fails.
        """
        pass

    @abstractmethod
    def get_metadata(self, file_path: Path) -> dict:
        """Extract metadata from a document.

        Args:
            file_path: Path to the document file.

        Returns:
            Dictionary with metadata fields:
            - title: str
            - authors: list[str] (optional)
            - path: str
            - type: str (e.g., "book", "paper", "documentation")
            - page_count: int (optional)
            - created_at: datetime (optional)

        Raises:
            FileNotFoundError: If file does not exist.
            MetadataExtractionError: If metadata extraction fails.
        """
        pass

    @abstractmethod
    def supports_file(self, file_path: Path) -> bool:
        """Check if this adapter supports the given file.

        Args:
            file_path: Path to check.

        Returns:
            True if this adapter can process the file, False otherwise.
        """
        pass

    # Common utility methods

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text.

        - Collapses multiple spaces to single space
        - Collapses multiple newlines to double newline (paragraph break)
        - Strips leading/trailing whitespace

        Args:
            text: Raw text to normalize.

        Returns:
            Normalized text.
        """
        import re
        # Collapse multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        # Collapse multiple newlines to max 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _extract_title_from_path(self, file_path: Path) -> str:
        """Extract title from filename as fallback.

        Args:
            file_path: Path to extract title from.

        Returns:
            Cleaned filename as title.
        """
        # Remove extension and convert underscores/hyphens to spaces
        title = file_path.stem
        title = title.replace('_', ' ').replace('-', ' ')
        # Title case
        return title.title()

    def _validate_file_exists(self, file_path: Path) -> None:
        """Validate that file exists.

        Args:
            file_path: Path to validate.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise FileNotFoundError(f"Path is not a file: {file_path}")

    def _validate_file_extension(self, file_path: Path) -> None:
        """Validate that file extension is supported.

        Args:
            file_path: Path to validate.

        Raises:
            UnsupportedFileError: If file extension is not supported.
        """
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileError(file_path, self.SUPPORTED_EXTENSIONS)

    def _calculate_token_estimate(self, text: str) -> int:
        """Estimate token count for text.

        Uses rough heuristic: ~4 characters per token for English text.

        Args:
            text: Text to estimate tokens for.

        Returns:
            Estimated token count.
        """
        # Rough estimate: 4 chars per token for English
        return len(text) // 4
```

### Adapter Registry Pattern

```python
# packages/pipeline/src/adapters/base.py (continued)

class AdapterRegistry:
    """Registry for managing document adapters.

    Provides a central location for registering and retrieving
    adapters based on file extensions.

    Example:
        registry = AdapterRegistry()
        registry.register(".pdf", PdfAdapter)
        registry.register(".md", MarkdownAdapter)

        adapter = registry.get_adapter(Path("document.pdf"))
        result = adapter.extract_text(Path("document.pdf"))
    """

    def __init__(self):
        """Initialize empty registry."""
        self._adapters: dict[str, Type[SourceAdapter]] = {}
        logger.debug("adapter_registry_initialized")

    def register(self, extension: str, adapter_class: Type[SourceAdapter]) -> None:
        """Register an adapter for a file extension.

        Args:
            extension: File extension including dot (e.g., ".pdf")
            adapter_class: Adapter class to register.

        Raises:
            ValueError: If extension already registered.
        """
        ext = extension.lower()
        if ext in self._adapters:
            logger.warning(
                "adapter_override",
                extension=ext,
                old=self._adapters[ext].__name__,
                new=adapter_class.__name__
            )
        self._adapters[ext] = adapter_class
        logger.info("adapter_registered", extension=ext, adapter=adapter_class.__name__)

    def get_adapter(self, file_path: Path) -> SourceAdapter:
        """Get an adapter instance for a file.

        Args:
            file_path: Path to get adapter for.

        Returns:
            Instantiated adapter for the file type.

        Raises:
            UnsupportedFileError: If no adapter registered for extension.
        """
        ext = file_path.suffix.lower()
        if ext not in self._adapters:
            raise UnsupportedFileError(file_path, list(self._adapters.keys()))
        return self._adapters[ext]()

    def list_supported_extensions(self) -> list[str]:
        """List all registered file extensions.

        Returns:
            List of supported file extensions.
        """
        return list(self._adapters.keys())

    def is_supported(self, file_path: Path) -> bool:
        """Check if a file is supported by any registered adapter.

        Args:
            file_path: Path to check.

        Returns:
            True if file is supported, False otherwise.
        """
        return file_path.suffix.lower() in self._adapters


# Module-level registry instance
adapter_registry = AdapterRegistry()
```

### Module Exports

```python
# packages/pipeline/src/adapters/__init__.py
"""Document source adapters for knowledge pipeline ingestion.

This module provides the base adapter interface and registry
for processing different document types (PDF, Markdown, etc.).

Example:
    from src.adapters import SourceAdapter, AdapterResult, adapter_registry

    class MyAdapter(SourceAdapter):
        SUPPORTED_EXTENSIONS = [".txt"]

        def extract_text(self, file_path):
            # Implementation
            pass

        def get_metadata(self, file_path):
            # Implementation
            pass

        def supports_file(self, file_path):
            return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    adapter_registry.register(".txt", MyAdapter)
"""

from src.adapters.base import (
    # Base class
    SourceAdapter,
    # Data models
    AdapterResult,
    Section,
    AdapterConfig,
    # Exceptions
    AdapterError,
    UnsupportedFileError,
    FileParseError,
    MetadataExtractionError,
    # Registry
    AdapterRegistry,
    adapter_registry,
)

__all__ = [
    # Base class
    "SourceAdapter",
    # Data models
    "AdapterResult",
    "Section",
    "AdapterConfig",
    # Exceptions
    "AdapterError",
    "UnsupportedFileError",
    "FileParseError",
    "MetadataExtractionError",
    # Registry
    "AdapterRegistry",
    "adapter_registry",
]
```

### Python Naming Conventions

**From Architecture Document (architecture.md:418-432):**

| Element | Convention | Example |
|---------|------------|---------|
| Files/modules | `snake_case.py` | `base.py`, `pdf_adapter.py` |
| Classes | `PascalCase` | `SourceAdapter`, `AdapterResult` |
| Functions | `snake_case` | `extract_text()`, `get_metadata()` |
| Variables | `snake_case` | `file_path`, `adapter_class` |
| Constants | `UPPER_SNAKE_CASE` | `SUPPORTED_EXTENSIONS` |

### Exception Pattern

**From Architecture Document (architecture.md:545-559) and project-context.md:**

All exceptions must:
1. Inherit from `KnowledgeError` base class
2. Include `code`, `message`, `details` fields
3. Follow structured error format

### Logging Pattern

**From Architecture Document (architecture.md:535-542):**

```python
import structlog
logger = structlog.get_logger()

# Good: structured with context
logger.info("adapter_registered", extension=".pdf", adapter="PdfAdapter")
logger.debug("adapter_initialized", adapter="SourceAdapter", extensions=[])
logger.error("file_parse_failed", path=str(file_path), error=str(e))
```

**CRITICAL:** Use structlog, no print statements.

### Testing Pattern

**From Architecture Document (architecture.md:456-462):**

```
packages/pipeline/
├── src/
│   └── adapters/
│       └── base.py
└── tests/
    └── test_adapters/
        ├── conftest.py
        └── test_base.py
```

**Test file example:**

```python
# packages/pipeline/tests/test_adapters/test_base.py
import pytest
from pathlib import Path
from abc import ABC

from src.adapters import (
    SourceAdapter,
    AdapterResult,
    Section,
    AdapterConfig,
    AdapterError,
    UnsupportedFileError,
    FileParseError,
    AdapterRegistry,
)


class TestSourceAdapterABC:
    """Test that SourceAdapter is properly abstract."""

    def test_cannot_instantiate_directly(self):
        """SourceAdapter cannot be instantiated without implementing abstract methods."""
        with pytest.raises(TypeError) as exc_info:
            SourceAdapter()
        assert "abstract" in str(exc_info.value).lower()

    def test_concrete_class_must_implement_abstract_methods(self):
        """Concrete class must implement all abstract methods."""
        class IncompleteAdapter(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".txt"]
            # Missing extract_text, get_metadata, supports_file

        with pytest.raises(TypeError):
            IncompleteAdapter()


class TestConcreteAdapter:
    """Test a concrete adapter implementation."""

    @pytest.fixture
    def concrete_adapter(self):
        """Create a minimal concrete adapter for testing."""
        class TestAdapter(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".txt", ".text"]

            def extract_text(self, file_path: Path) -> AdapterResult:
                self._validate_file_exists(file_path)
                self._validate_file_extension(file_path)
                return AdapterResult(
                    text=file_path.read_text(),
                    metadata=self.get_metadata(file_path),
                )

            def get_metadata(self, file_path: Path) -> dict:
                return {
                    "title": self._extract_title_from_path(file_path),
                    "path": str(file_path),
                    "type": "text",
                }

            def supports_file(self, file_path: Path) -> bool:
                return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

        return TestAdapter()

    def test_extract_text_file_not_found(self, concrete_adapter, tmp_path):
        """Should raise FileNotFoundError for missing file."""
        fake_path = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            concrete_adapter.extract_text(fake_path)

    def test_extract_text_unsupported_extension(self, concrete_adapter, tmp_path):
        """Should raise UnsupportedFileError for wrong extension."""
        wrong_file = tmp_path / "file.pdf"
        wrong_file.touch()
        with pytest.raises(UnsupportedFileError) as exc_info:
            concrete_adapter.extract_text(wrong_file)
        assert exc_info.value.code == "UNSUPPORTED_FILE"

    def test_extract_text_success(self, concrete_adapter, tmp_path):
        """Should extract text from valid file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        result = concrete_adapter.extract_text(test_file)

        assert isinstance(result, AdapterResult)
        assert result.text == "Hello, World!"
        assert result.metadata["title"] == "Test"
        assert result.metadata["type"] == "text"

    def test_supports_file(self, concrete_adapter, tmp_path):
        """Should correctly identify supported files."""
        assert concrete_adapter.supports_file(Path("doc.txt")) is True
        assert concrete_adapter.supports_file(Path("doc.text")) is True
        assert concrete_adapter.supports_file(Path("doc.pdf")) is False


class TestUtilityMethods:
    """Test utility methods on SourceAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create adapter for utility testing."""
        class MinimalAdapter(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".txt"]
            def extract_text(self, file_path): pass
            def get_metadata(self, file_path): pass
            def supports_file(self, file_path): return True
        return MinimalAdapter()

    def test_normalize_whitespace(self, adapter):
        """Should normalize excessive whitespace."""
        input_text = "Hello   World\n\n\n\nTest"
        result = adapter._normalize_whitespace(input_text)
        assert result == "Hello World\n\nTest"

    def test_extract_title_from_path(self, adapter):
        """Should extract clean title from filename."""
        path = Path("my-document_file.txt")
        title = adapter._extract_title_from_path(path)
        assert title == "My Document File"

    def test_calculate_token_estimate(self, adapter):
        """Should estimate token count."""
        text = "Hello World"  # 11 chars
        estimate = adapter._calculate_token_estimate(text)
        assert estimate == 2  # 11 // 4 = 2


class TestAdapterRegistry:
    """Test adapter registry functionality."""

    def test_register_and_get_adapter(self):
        """Should register and retrieve adapters."""
        class DummyAdapter(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".dummy"]
            def extract_text(self, fp): pass
            def get_metadata(self, fp): pass
            def supports_file(self, fp): return True

        registry = AdapterRegistry()
        registry.register(".dummy", DummyAdapter)

        adapter = registry.get_adapter(Path("test.dummy"))
        assert isinstance(adapter, DummyAdapter)

    def test_get_adapter_unsupported_raises(self):
        """Should raise UnsupportedFileError for unregistered extension."""
        registry = AdapterRegistry()

        with pytest.raises(UnsupportedFileError) as exc_info:
            registry.get_adapter(Path("file.xyz"))
        assert exc_info.value.code == "UNSUPPORTED_FILE"

    def test_list_supported_extensions(self):
        """Should list all registered extensions."""
        class Adapter1(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".one"]
            def extract_text(self, fp): pass
            def get_metadata(self, fp): pass
            def supports_file(self, fp): return True

        registry = AdapterRegistry()
        registry.register(".one", Adapter1)
        registry.register(".two", Adapter1)

        extensions = registry.list_supported_extensions()
        assert ".one" in extensions
        assert ".two" in extensions

    def test_is_supported(self):
        """Should check if file is supported."""
        class Adapter(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".sup"]
            def extract_text(self, fp): pass
            def get_metadata(self, fp): pass
            def supports_file(self, fp): return True

        registry = AdapterRegistry()
        registry.register(".sup", Adapter)

        assert registry.is_supported(Path("file.sup")) is True
        assert registry.is_supported(Path("file.unsup")) is False


class TestExceptions:
    """Test exception classes."""

    def test_unsupported_file_error(self):
        """Should have structured error format."""
        error = UnsupportedFileError(Path("test.xyz"), [".pdf", ".md"])
        assert error.code == "UNSUPPORTED_FILE"
        assert "test.xyz" in error.message
        assert error.details["supported"] == [".pdf", ".md"]

    def test_file_parse_error(self):
        """Should have structured error format."""
        error = FileParseError(Path("corrupt.pdf"), "Invalid PDF structure")
        assert error.code == "FILE_PARSE_ERROR"
        assert "corrupt.pdf" in str(error.details["path"])
        assert error.details["reason"] == "Invalid PDF structure"

    def test_exception_hierarchy(self):
        """Exceptions should inherit from AdapterError."""
        assert issubclass(UnsupportedFileError, AdapterError)
        assert issubclass(FileParseError, AdapterError)
        assert issubclass(MetadataExtractionError, AdapterError)
```

### Integration with Source Model

**From Story 1.3 (Pydantic Models):**

The `Source` model from Story 1.3 will receive metadata from adapters:

```python
# Expected Source model fields that adapters populate
metadata = {
    "title": str,         # Extracted or fallback from filename
    "authors": list[str], # Optional, from document metadata
    "path": str,          # Original file path
    "type": str,          # "book", "paper", "documentation"
    "page_count": int,    # Optional, for PDFs
}
```

The adapter's `get_metadata()` output maps directly to `Source` model fields.

### Project Structure Notes

- File location: `packages/pipeline/src/adapters/base.py`
- Module exports: `packages/pipeline/src/adapters/__init__.py`
- Tests: `packages/pipeline/tests/test_adapters/test_base.py`
- Aligned with architecture: All source ingestion code in `packages/pipeline/`
- Follow NFR5 extensibility pattern: ABC enables easy addition of new adapters

### Story Predecessor Intelligence

**From Epic 1 Stories (Foundation):**
- Story 1.1 established monorepo structure at `packages/pipeline/`
- Story 1.3 established Pydantic model patterns and `Source` model
- Story 1.4 established exception patterns with `KnowledgeError` base
- Story 1.5 established logging with structlog pattern

**Patterns to Follow:**
- Exception classes inherit from `KnowledgeError`
- All exceptions include `code`, `message`, `details`
- Use structlog for all logging
- Pydantic models for data validation
- Tests mirror src structure

### Architecture Compliance Checklist

- [x] File in `packages/pipeline/src/adapters/base.py` (architecture.md:612-618)
- [x] ABC with abstract methods `extract_text()`, `get_metadata()` (NFR5)
- [x] Common utilities provided as protected methods
- [x] Exceptions inherit from `KnowledgeError` (architecture.md:545-559)
- [x] Structured error format: `{code, message, details}`
- [x] Uses structlog for logging (architecture.md:535-542)
- [x] Pydantic models for `AdapterResult`, `Section`, `AdapterConfig`
- [x] Registry pattern for extensibility
- [x] Tests in `packages/pipeline/tests/test_adapters/`

### References

- [Source: epics.md#Story-2.1] - Story acceptance criteria (lines 268-282)
- [Source: architecture.md#Project-Structure-&-Boundaries] - File locations (lines 612-618)
- [Source: architecture.md#NFR5] - Extensibility requirement (line 80)
- [Source: architecture.md#Implementation-Patterns-&-Consistency-Rules] - Naming patterns (lines 410-435)
- [Source: architecture.md#Error-Handling-Pattern] - Exception pattern (lines 545-560)
- [Source: project-context.md#Critical-Implementation-Rules] - Error handling rules
- [Source: Story 1.3] - Pydantic model patterns
- [Source: Story 1.4] - Exception patterns from MongoDB client

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All tests pass: 46 adapter tests + 170 total tests in full suite
- Linting passes: `ruff check src/adapters/ tests/test_adapters/` - All checks passed

### Completion Notes List

- **Task 1**: Verified all prerequisites - Story 1.1 complete (pyproject.toml exists), Story 1.3 complete (Source model imports), Python 3.11.13 confirmed
- **Task 2**: Created adapters module structure with `__init__.py` and `base.py`
- **Task 3**: Implemented Pydantic models: `Section` (with level validation 1-6), `AdapterResult`, `AdapterConfig`
- **Task 4**: Implemented `SourceAdapter` ABC with three abstract methods and SUPPORTED_EXTENSIONS class attribute
- **Task 5**: Implemented 5 utility methods: `_normalize_whitespace`, `_extract_title_from_path`, `_validate_file_exists`, `_validate_file_extension`, `_calculate_token_estimate`
- **Task 6**: Implemented exception hierarchy: `AdapterError` (base), `UnsupportedFileError`, `FileParseError`, `MetadataExtractionError` - all follow structured error format with code/message/details
- **Task 7**: Implemented `AdapterRegistry` with `register()`, `get_adapter()`, `list_supported_extensions()`, `is_supported()` methods and module-level `adapter_registry` instance
- **Task 8**: Created module exports in `__init__.py` with all classes, exceptions, and registry
- **Task 9**: Created comprehensive test suite with 46 tests covering ABC behavior, concrete implementations, utilities, registry, exceptions, and data models

### Change Log

- 2025-12-30: Implemented base source adapter interface per NFR5 extensibility pattern

### File List

- packages/pipeline/src/adapters/__init__.py (MODIFIED - was empty placeholder)
- packages/pipeline/src/adapters/base.py (CREATE)
- packages/pipeline/tests/test_adapters/__init__.py (CREATE)
- packages/pipeline/tests/test_adapters/conftest.py (CREATE)
- packages/pipeline/tests/test_adapters/test_base.py (CREATE)
