"""Text processing utilities for knowledge pipeline.

This module provides processors for chunking document text
for embedding and extraction using Docling's HybridChunker.

Example:
    from src.processors import DoclingChunker, ChunkerConfig

    chunker = DoclingChunker(ChunkerConfig(chunk_size=512))
    chunks = chunker.chunk_document(docling_doc, source_id="doc-123")
"""

from src.processors.chunker import (
    # Main class
    DoclingChunker,
    # Configuration models
    ChunkerConfig,
    ChunkOutput,
    # Exceptions
    ChunkerError,
    EmptyContentError,
    ChunkSizeError,
    MissingDoclingDocumentError,
    # Constants
    EMBED_MODEL_ID,
)

__all__ = [
    # Main class
    "DoclingChunker",
    # Configuration models
    "ChunkerConfig",
    "ChunkOutput",
    # Exceptions
    "ChunkerError",
    "EmptyContentError",
    "ChunkSizeError",
    "MissingDoclingDocumentError",
    # Constants
    "EMBED_MODEL_ID",
]
