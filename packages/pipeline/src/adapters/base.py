"""Base adapter interface and supporting classes for document source adapters.

This module defines the abstract base class for all document adapters,
supporting data models, exceptions, and the adapter registry pattern.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Type

import structlog
from pydantic import BaseModel, Field

from src.exceptions import KnowledgeError

logger = structlog.get_logger()


# ============================================================================
# Data Models
# ============================================================================


class Section(BaseModel):
    """Represents a document section with position metadata.

    Attributes:
        title: Section heading text.
        content: Section text content.
        level: Heading level (1-6, like HTML headings).
        position: Position metadata (page, chapter, offset).
    """

    title: str
    content: str
    level: int = Field(default=1, ge=1, le=6)
    position: dict = Field(default_factory=dict)


class AdapterResult(BaseModel):
    """Result of adapter text extraction.

    Attributes:
        text: Extracted raw text content.
        metadata: Source metadata (title, authors, path, type).
        sections: Optional structured sections parsed from document.
    """

    text: str
    metadata: dict
    sections: list[Section] = Field(default_factory=list)


class AdapterConfig(BaseModel):
    """Configuration for adapter behavior.

    Attributes:
        preserve_structure: Whether to preserve document structure.
        include_metadata: Whether to include metadata extraction.
        max_section_depth: Maximum heading level to parse (1-6).
    """

    preserve_structure: bool = True
    include_metadata: bool = True
    max_section_depth: int = Field(default=3, ge=1, le=6)


# ============================================================================
# Exceptions
# ============================================================================


class AdapterError(KnowledgeError):
    """Base exception for adapter errors."""

    pass


class UnsupportedFileError(AdapterError):
    """Raised when file type is not supported by any adapter."""

    def __init__(self, file_path: Path, supported: list[str]):
        super().__init__(
            code="UNSUPPORTED_FILE",
            message=f"File type not supported: {file_path.suffix}",
            details={"path": str(file_path), "supported": supported},
        )


class FileParseError(AdapterError):
    """Raised when file parsing fails."""

    def __init__(self, file_path: Path, reason: str):
        super().__init__(
            code="FILE_PARSE_ERROR",
            message=f"Failed to parse file: {reason}",
            details={"path": str(file_path), "reason": reason},
        )


class MetadataExtractionError(AdapterError):
    """Raised when metadata extraction fails."""

    def __init__(self, file_path: Path, reason: str):
        super().__init__(
            code="METADATA_EXTRACTION_ERROR",
            message=f"Failed to extract metadata: {reason}",
            details={"path": str(file_path), "reason": reason},
        )


# ============================================================================
# Source Adapter ABC
# ============================================================================


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
            extensions=self.SUPPORTED_EXTENSIONS,
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

    # ========================================================================
    # Common Utility Methods
    # ========================================================================

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
        # Collapse multiple spaces/tabs to single space
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse multiple newlines to max 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _extract_title_from_path(self, file_path: Path) -> str:
        """Extract title from filename as fallback.

        Args:
            file_path: Path to extract title from.

        Returns:
            Cleaned filename as title (title-cased).
        """
        # Remove extension and convert underscores/hyphens to spaces
        title = file_path.stem
        title = title.replace("_", " ").replace("-", " ")
        # Title case
        return title.title()

    def _validate_file_exists(self, file_path: Path) -> None:
        """Validate that file exists.

        Args:
            file_path: Path to validate.

        Raises:
            FileNotFoundError: If file does not exist or is not a file.
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


# ============================================================================
# Adapter Registry
# ============================================================================


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
        """
        ext = extension.lower()
        if ext in self._adapters:
            logger.warning(
                "adapter_override",
                extension=ext,
                old=self._adapters[ext].__name__,
                new=adapter_class.__name__,
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
