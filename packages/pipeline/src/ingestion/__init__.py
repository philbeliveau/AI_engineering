"""End-to-end ingestion pipeline for knowledge base documents.

This module provides the complete ingestion pipeline that orchestrates:
1. Document extraction via adapters (PDF, Markdown, DOCX, HTML, PPTX)
2. Text chunking with DoclingChunker
3. Embedding generation with local sentence-transformers
4. Storage in MongoDB (sources, chunks) and Qdrant (vectors)

Example:
    from src.ingestion import IngestionPipeline, IngestionResult
    import structlog

    logger = structlog.get_logger()
    pipeline = IngestionPipeline()
    result = pipeline.ingest(Path("book.pdf"))
    logger.info("ingestion_complete", chunk_count=result.chunk_count, source_id=result.source_id)
"""

from src.ingestion.pipeline import (
    # Main classes
    IngestionPipeline,
    IngestionResult,
    # Configuration
    PipelineConfig,
    # Status enum
    IngestionStatus,
    # Exceptions
    IngestionError,
    AdapterSelectionError,
    ChunkingError,
    EmbeddingError,
    StorageOrchestrationError,
)

__all__ = [
    # Main classes
    "IngestionPipeline",
    "IngestionResult",
    # Configuration
    "PipelineConfig",
    # Status enum
    "IngestionStatus",
    # Exceptions
    "IngestionError",
    "AdapterSelectionError",
    "ChunkingError",
    "EmbeddingError",
    "StorageOrchestrationError",
]
