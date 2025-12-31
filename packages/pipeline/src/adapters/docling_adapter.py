"""Unified document adapter using IBM Docling for multi-format support.

This module provides a single adapter that handles PDF, Markdown, DOCX,
HTML, and PPTX files using the Docling library.
"""

from pathlib import Path
from typing import Optional

import structlog
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DoclingDocument

from src.adapters.base import (
    AdapterConfig,
    AdapterResult,
    FileParseError,
    Section,
    SourceAdapter,
)

logger = structlog.get_logger()


class DoclingAdapter(SourceAdapter):
    """Unified adapter for document extraction using IBM Docling.

    Supports PDF, Markdown, DOCX, HTML, and PPTX files with a single
    implementation. Extracts text content, document structure, and
    metadata in a unified format.

    Attributes:
        SUPPORTED_EXTENSIONS: List of file extensions this adapter handles.

    Example:
        adapter = DoclingAdapter()
        result = adapter.extract_text(Path("document.pdf"))
        print(result.text)
        print(result.sections)
    """

    SUPPORTED_EXTENSIONS = [".pdf", ".md", ".docx", ".html", ".pptx"]

    def __init__(self, config: Optional[AdapterConfig] = None):
        """Initialize Docling adapter with optional configuration.

        Args:
            config: Adapter configuration. Uses defaults if not provided.
        """
        super().__init__(config)
        self._converter = DocumentConverter()
        logger.debug("docling_adapter_initialized")

    def extract_text(self, file_path: Path) -> AdapterResult:
        """Extract text and structure from document using Docling.

        Args:
            file_path: Path to the document file.

        Returns:
            AdapterResult with extracted text, metadata, and sections.
            The metadata includes a `_docling_document` key containing
            the raw DoclingDocument for downstream processing (e.g., chunking).

        Raises:
            FileNotFoundError: If file does not exist.
            UnsupportedFileError: If file type is not supported.
            FileParseError: If document parsing fails.
        """
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

            # Store DoclingDocument for chunker (HybridChunker needs this)
            metadata["_docling_document"] = doc

            # Try to extract authors from DoclingDocument if available
            extracted_authors = self._extract_authors(doc)
            if extracted_authors:
                metadata["authors"] = extracted_authors

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

        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error("docling_extraction_failed", path=str(file_path), error=str(e))
            raise FileParseError(file_path, f"Docling extraction failed: {e}")

    def get_metadata(self, file_path: Path) -> dict:
        """Extract metadata from a document.

        Args:
            file_path: Path to the document file.

        Returns:
            Dictionary with metadata fields:
            - title: Document title (from metadata or filename).
            - authors: List of authors if detectable.
            - path: Original file path.
            - type: File type based on extension.
            - file_extension: File extension (e.g., ".pdf").

        Raises:
            FileNotFoundError: If file does not exist.
        """
        self._validate_file_exists(file_path)

        # Map extensions to document types
        type_map = {
            ".pdf": "pdf",
            ".md": "markdown",
            ".docx": "docx",
            ".html": "html",
            ".pptx": "presentation",
        }

        return {
            "title": self._extract_title_from_path(file_path),
            "authors": [],  # Docling may extract this; we set default here
            "path": str(file_path),
            "type": type_map.get(file_path.suffix.lower(), "document"),
            "file_extension": file_path.suffix.lower(),
        }

    def supports_file(self, file_path: Path) -> bool:
        """Check if this adapter supports the given file.

        Args:
            file_path: Path to check.

        Returns:
            True if file extension is in SUPPORTED_EXTENSIONS.
        """
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def _extract_sections(self, doc: DoclingDocument) -> list[Section]:
        """Extract sections from DoclingDocument structure.

        Iterates through the document items and creates Section objects
        for each content element with text.

        Args:
            doc: The DoclingDocument from Docling conversion.

        Returns:
            List of Section objects with title, content, level, and position.
        """
        sections = []

        try:
            for item, level in doc.iterate_items():
                if hasattr(item, "text") and item.text:
                    section = Section(
                        title=self._get_item_label(item),
                        content=item.text,
                        level=min(max(level, 1), 6),  # Clamp to 1-6
                        position=self._get_item_position(item),
                    )
                    sections.append(section)
        except Exception as e:
            logger.warning(
                "docling_section_extraction_partial",
                error=str(e),
                sections_extracted=len(sections),
            )

        return sections

    def _get_item_label(self, item) -> str:
        """Get label from a document item.

        Args:
            item: Document item from Docling.

        Returns:
            Label string, or 'content' if no label available.
        """
        if hasattr(item, "label"):
            label = item.label
            # Handle enum-like labels
            if hasattr(label, "value"):
                return str(label.value)
            return str(label)
        return "content"

    def _get_item_position(self, item) -> dict:
        """Extract position metadata from document item.

        Args:
            item: Document item from Docling.

        Returns:
            Dictionary with position info (e.g., page number for PDFs).
        """
        position = {}

        if hasattr(item, "prov") and item.prov:
            # Get page number from provenance
            for prov in item.prov:
                if hasattr(prov, "page_no"):
                    position["page"] = prov.page_no
                    break

        return position

    def _extract_authors(self, doc: DoclingDocument) -> list[str]:
        """Extract authors from DoclingDocument if available.

        Attempts to extract author information from document metadata,
        origin, or properties.

        Args:
            doc: The DoclingDocument from Docling conversion.

        Returns:
            List of author names, or empty list if not detected.
        """
        authors = []

        try:
            # Try to get from document origin metadata
            if hasattr(doc, "origin") and doc.origin:
                origin = doc.origin
                # Check for author in origin metadata
                if hasattr(origin, "author") and origin.author:
                    if isinstance(origin.author, str):
                        authors.append(origin.author)
                    elif isinstance(origin.author, list):
                        authors.extend(origin.author)

            # Try to get from document metadata if available
            if not authors and hasattr(doc, "metadata") and doc.metadata:
                meta = doc.metadata
                if hasattr(meta, "author") and meta.author:
                    if isinstance(meta.author, str):
                        authors.append(meta.author)
                    elif isinstance(meta.author, list):
                        authors.extend(meta.author)
                # Some docs use 'authors' plural
                if hasattr(meta, "authors") and meta.authors:
                    if isinstance(meta.authors, list):
                        authors.extend(meta.authors)

        except Exception as e:
            logger.debug("docling_author_extraction_failed", error=str(e))

        return authors
