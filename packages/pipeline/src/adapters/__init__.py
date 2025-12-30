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
