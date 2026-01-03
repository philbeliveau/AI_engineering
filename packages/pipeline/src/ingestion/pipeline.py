"""End-to-end ingestion pipeline orchestrator.

This module provides the IngestionPipeline class that coordinates all steps
of document ingestion: extract, chunk, embed, and store.

Stages:
1. Validate file and select adapter
2. Extract text and metadata using DoclingAdapter
3. Chunk text into semantic units using DoclingChunker
4. Generate embeddings for chunks using LocalEmbedder
5. Store source, chunks (MongoDB), and vectors (Qdrant)
6. Track status throughout (pending -> processing -> complete/failed)

Example:
    from src.ingestion import IngestionPipeline
    from pathlib import Path
    import structlog

    logger = structlog.get_logger()
    pipeline = IngestionPipeline()
    result = pipeline.ingest(Path("book.pdf"))
    logger.info("ingestion_complete", chunk_count=result.chunk_count)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import structlog
from pydantic import BaseModel, Field
from qdrant_client.http.models import PointStruct

from src.adapters import (
    adapter_registry,
    AdapterError,
    UnsupportedFileError,
)
from src.embeddings.local_embedder import get_embedder, EmbeddingError as EmbedError
from src.exceptions import KnowledgeError, StorageError
from src.models.chunk import Chunk, ChunkPosition
from src.models.source import Source
from src.processors.chunker import (
    DoclingChunker,
    ChunkerConfig,
    ChunkerError,
    MissingDoclingDocumentError,
)
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient, CHUNKS_COLLECTION, _string_to_uuid

logger = structlog.get_logger()


# ============================================================================
# Status Enum
# ============================================================================


class IngestionStatus(str, Enum):
    """Status of document ingestion pipeline."""

    PENDING = "pending"  # Created but not started
    PROCESSING = "processing"  # Currently ingesting
    COMPLETE = "complete"  # Successfully ingested
    FAILED = "failed"  # Ingestion failed


# ============================================================================
# Configuration
# ============================================================================


class PipelineConfig(BaseModel):
    """Configuration for ingestion pipeline.

    Attributes:
        chunk_size: Target maximum tokens per chunk.
        dry_run: If True, validate without storing.
        verbose: If True, enable verbose logging.
        project_id: Override PROJECT_ID for this ingestion.
        category: Source category (foundational, advanced, reference, case_study).
        tags: Source tags for filtering (comma-separated in CLI).
        year: Publication year for the source.
    """

    chunk_size: int = Field(default=512, ge=50, le=2048)
    dry_run: bool = False
    verbose: bool = False
    # Source metadata fields (v1.1 schema)
    project_id: Optional[str] = None  # Override PROJECT_ID env var
    category: Optional[str] = None  # foundational, advanced, reference, case_study
    tags: list[str] = Field(default_factory=list)
    year: Optional[int] = Field(default=None, ge=1900, le=2100)


# ============================================================================
# Exceptions
# ============================================================================


class IngestionError(KnowledgeError):
    """Base exception for ingestion pipeline errors."""

    pass


class AdapterSelectionError(IngestionError):
    """Raised when adapter selection fails."""

    def __init__(self, file_path: Path, reason: str):
        super().__init__(
            code="ADAPTER_SELECTION_ERROR",
            message=f"Failed to select adapter for {file_path.name}: {reason}",
            details={"file_path": str(file_path), "reason": reason},
        )


class ChunkingError(IngestionError):
    """Raised when text chunking fails."""

    def __init__(self, source_id: str, reason: str):
        super().__init__(
            code="CHUNKING_ERROR",
            message=f"Failed to chunk document: {reason}",
            details={"source_id": source_id, "reason": reason},
        )


class EmbeddingError(IngestionError):
    """Raised when embedding generation fails."""

    def __init__(self, source_id: str, reason: str, chunk_count: int = 0):
        super().__init__(
            code="EMBEDDING_ERROR",
            message=f"Failed to generate embeddings: {reason}",
            details={
                "source_id": source_id,
                "reason": reason,
                "chunk_count": chunk_count,
            },
        )


class StorageOrchestrationError(IngestionError):
    """Raised when storage operations fail."""

    def __init__(self, source_id: str, stage: str, reason: str):
        super().__init__(
            code="STORAGE_ORCHESTRATION_ERROR",
            message=f"Storage failed at {stage}: {reason}",
            details={"source_id": source_id, "stage": stage, "reason": reason},
        )


# ============================================================================
# Result Models
# ============================================================================


@dataclass
class IngestionResult:
    """Result summary from ingestion pipeline.

    Attributes:
        source_id: MongoDB ObjectId for the ingested source.
        title: Document title.
        file_type: File extension/type.
        chunk_count: Number of chunks created.
        total_tokens: Sum of tokens across all chunks.
        processing_time: Time for extraction and chunking (seconds).
        embedding_time: Time for embedding generation (seconds).
        storage_time: Time for MongoDB/Qdrant storage (seconds).
        duration: Total pipeline duration (seconds).
    """

    source_id: str
    title: str
    file_type: str
    chunk_count: int
    total_tokens: int
    processing_time: float
    embedding_time: float
    storage_time: float
    duration: float


# ============================================================================
# Main Pipeline Class
# ============================================================================


class IngestionPipeline:
    """Orchestrates the complete document ingestion pipeline.

    This class coordinates all steps of document ingestion:
    1. Validate file and select appropriate adapter
    2. Extract text and metadata using the adapter
    3. Chunk text into semantic units
    4. Generate embeddings for chunks
    5. Store source metadata, chunks, and vectors
    6. Track status throughout the process

    The pipeline is synchronous as the underlying libraries (pymongo,
    sentence-transformers) are not async-native.

    Example:
        pipeline = IngestionPipeline()
        result = pipeline.ingest(Path("book.pdf"))
        # Use structlog for output: logger.info("done", chunks=result.chunk_count)
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize pipeline with configuration.

        Args:
            config: Pipeline configuration. Uses defaults if not provided.
        """
        self.config = config or PipelineConfig()

        # Initialize components (lazy loading for embedder)
        self._chunker: Optional[DoclingChunker] = None
        self._mongodb: Optional[MongoDBClient] = None
        self._qdrant: Optional[QdrantStorageClient] = None

        logger.info(
            "pipeline_initialized",
            chunk_size=self.config.chunk_size,
            dry_run=self.config.dry_run,
        )

    @property
    def chunker(self) -> DoclingChunker:
        """Get or create the chunker instance."""
        if self._chunker is None:
            self._chunker = DoclingChunker(
                ChunkerConfig(chunk_size=self.config.chunk_size)
            )
        return self._chunker

    @property
    def mongodb(self) -> MongoDBClient:
        """Get or create the MongoDB client instance."""
        if self._mongodb is None:
            self._mongodb = MongoDBClient()
            self._mongodb.connect()
        return self._mongodb

    @property
    def qdrant(self) -> QdrantStorageClient:
        """Get or create the Qdrant client instance."""
        if self._qdrant is None:
            self._qdrant = QdrantStorageClient()
            self._qdrant.ensure_collection(CHUNKS_COLLECTION)
        return self._qdrant

    def close(self) -> None:
        """Close database connections."""
        if self._mongodb is not None:
            self._mongodb.close()
            self._mongodb = None
        # Qdrant client doesn't need explicit close
        self._qdrant = None

    def __enter__(self) -> "IngestionPipeline":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit."""
        self.close()
        return False

    def ingest(self, file_path: Path) -> IngestionResult:
        """Run complete ingestion pipeline for a document.

        Args:
            file_path: Path to document to ingest.

        Returns:
            IngestionResult with summary statistics.

        Raises:
            IngestionError: If any pipeline stage fails.
            UnsupportedFileError: If file type not supported.
        """
        start_time = time.time()
        source_id: Optional[str] = None
        processing_time = 0.0
        embedding_time = 0.0
        storage_time = 0.0

        # Validate file exists
        if not file_path.exists():
            raise IngestionError(
                code="FILE_NOT_FOUND",
                message=f"File not found: {file_path}",
                details={"file_path": str(file_path)},
            )

        logger.info("ingestion_started", file=str(file_path))

        try:
            # ================================================================
            # Stage 1: Validate and select adapter
            # ================================================================
            logger.info("stage_started", stage="validate", file=str(file_path))
            adapter = self._select_adapter(file_path)
            logger.info(
                "adapter_selected",
                adapter=adapter.__class__.__name__,
                file_type=file_path.suffix,
            )

            # ================================================================
            # Stage 2: Create source with pending status
            # ================================================================
            if not self.config.dry_run:
                # Resolve project_id: CLI flag > env var > default
                from src.config import settings
                resolved_project_id = self.config.project_id or settings.project_id

                source = Source(
                    id="0" * 24,  # Placeholder, will be replaced by MongoDB
                    title=file_path.name,
                    type=self._detect_type(file_path),
                    path=str(file_path.absolute()),
                    ingested_at=datetime.now(),
                    status=IngestionStatus.PENDING.value,
                    metadata={"file_extension": file_path.suffix},
                    # v1.1 schema fields from CLI
                    project_id=resolved_project_id,
                    category=self.config.category or "foundational",
                    tags=self.config.tags,
                    year=self.config.year,
                )
                source_id = self.mongodb.create_source(source)
                logger.info(
                    "source_created",
                    source_id=source_id,
                    project_id=resolved_project_id,
                    category=source.category,
                    status="pending",
                )

                # Update status to processing
                self.mongodb.update_source(
                    source_id, {"status": IngestionStatus.PROCESSING.value}
                )

            # ================================================================
            # Stage 3: Extract text and metadata
            # ================================================================
            logger.info("stage_started", stage="extract")
            extract_start = time.time()

            adapter_result = adapter.extract_text(file_path)
            file_metadata = adapter.get_metadata(file_path)

            # Update source with extracted metadata
            if not self.config.dry_run and source_id:
                self.mongodb.update_source(
                    source_id,
                    {
                        "title": file_metadata.get("title", file_path.name),
                        "authors": file_metadata.get("authors", []),
                        "metadata": file_metadata,
                    },
                )

            # ================================================================
            # Stage 4: Chunk text
            # ================================================================
            logger.info("stage_started", stage="chunk", text_length=len(adapter_result.text))

            chunks = self._chunk_document(
                adapter_result,
                source_id or "dry-run",
            )
            processing_time = time.time() - extract_start

            logger.info(
                "chunking_complete",
                chunk_count=len(chunks),
                total_tokens=sum(c.token_count for c in chunks),
            )

            # ================================================================
            # Stage 5: Generate embeddings
            # ================================================================
            logger.info("stage_started", stage="embed", chunk_count=len(chunks))
            embed_start = time.time()

            embeddings = self._generate_embeddings(chunks, source_id or "dry-run")
            embedding_time = time.time() - embed_start

            logger.info(
                "embedding_complete",
                embedding_count=len(embeddings),
                duration=f"{embedding_time:.2f}s",
            )

            # Validate embedding dimensions
            if embeddings and len(embeddings[0]) != 384:
                raise EmbeddingError(
                    source_id=source_id or "dry-run",
                    reason=f"Expected 384d embeddings, got {len(embeddings[0])}d",
                    chunk_count=len(chunks),
                )

            # ================================================================
            # Stage 6: Store everything
            # ================================================================
            if not self.config.dry_run and source_id:
                logger.info("stage_started", stage="store")
                storage_start = time.time()

                self._store_chunks_and_vectors(
                    chunks=chunks,
                    embeddings=embeddings,
                    source_id=source_id,
                )
                storage_time = time.time() - storage_start

                # Mark source as complete
                self.mongodb.update_source(
                    source_id, {"status": IngestionStatus.COMPLETE.value}
                )

                logger.info(
                    "storage_complete",
                    source_id=source_id,
                    storage_time=f"{storage_time:.2f}s",
                )

            # ================================================================
            # Build result
            # ================================================================
            duration = time.time() - start_time

            logger.info(
                "ingestion_complete",
                source_id=source_id or "dry-run",
                chunk_count=len(chunks),
                duration=f"{duration:.2f}s",
            )

            return IngestionResult(
                source_id=source_id or "dry-run",
                title=file_metadata.get("title", file_path.name),
                file_type=file_path.suffix,
                chunk_count=len(chunks),
                total_tokens=sum(c.token_count for c in chunks),
                processing_time=processing_time,
                embedding_time=embedding_time,
                storage_time=storage_time,
                duration=duration,
            )

        except (UnsupportedFileError, AdapterError) as e:
            # Mark source as failed if it was created
            if source_id and not self.config.dry_run:
                self._mark_failed(source_id, str(e))

            logger.error(
                "ingestion_failed",
                source_id=source_id,
                file=str(file_path),
                error=str(e),
                error_type=type(e).__name__,
            )

            raise AdapterSelectionError(file_path, str(e)) from e

        except (ChunkerError, MissingDoclingDocumentError) as e:
            if source_id and not self.config.dry_run:
                self._mark_failed(source_id, str(e))

            logger.error(
                "ingestion_failed",
                source_id=source_id,
                error=str(e),
                error_type=type(e).__name__,
            )

            raise ChunkingError(source_id or "unknown", str(e)) from e

        except EmbedError as e:
            if source_id and not self.config.dry_run:
                self._mark_failed(source_id, str(e))

            logger.error(
                "ingestion_failed",
                source_id=source_id,
                error=str(e),
                error_type=type(e).__name__,
            )

            raise EmbeddingError(source_id or "unknown", str(e)) from e

        except StorageError as e:
            if source_id and not self.config.dry_run:
                self._mark_failed(source_id, str(e))

            logger.error(
                "ingestion_failed",
                source_id=source_id,
                error=str(e),
                error_type=type(e).__name__,
            )

            raise StorageOrchestrationError(
                source_id or "unknown",
                "storage",
                str(e),
            ) from e

        except IngestionError:
            # Re-raise our own exceptions
            if source_id and not self.config.dry_run:
                self._mark_failed(source_id, "Pipeline error")
            raise

        except Exception as e:
            # Catch-all for unexpected errors
            if source_id and not self.config.dry_run:
                self._mark_failed(source_id, str(e))

            logger.error(
                "ingestion_failed",
                source_id=source_id,
                file=str(file_path),
                error=str(e),
                error_type=type(e).__name__,
            )

            raise IngestionError(
                code="INGESTION_FAILED",
                message=f"Pipeline failed: {str(e)}",
                details={
                    "source_id": source_id,
                    "file": str(file_path),
                    "error_type": type(e).__name__,
                },
            ) from e

    def _select_adapter(self, file_path: Path):
        """Select appropriate adapter for file type.

        Args:
            file_path: Path to the file.

        Returns:
            Instantiated adapter for the file type.

        Raises:
            UnsupportedFileError: If file type not supported.
        """
        return adapter_registry.get_adapter(file_path)

    def _detect_type(self, file_path: Path) -> str:
        """Detect document type from extension.

        Args:
            file_path: Path to the file.

        Returns:
            Document type string (book, paper, or case_study).
        """
        ext = file_path.suffix.lower()
        type_map = {
            ".pdf": "book",
            ".md": "paper",  # Markdown docs are typically papers
            ".markdown": "paper",
            ".docx": "paper",
            ".html": "paper",
            ".pptx": "paper",
        }
        return type_map.get(ext, "book")

    def _chunk_document(self, adapter_result, source_id: str) -> list:
        """Chunk document using DoclingChunker.

        Args:
            adapter_result: Result from adapter.extract_text().
            source_id: Source ID for linking chunks.

        Returns:
            List of ChunkOutput objects.

        Raises:
            ChunkerError: If chunking fails.
        """
        return self.chunker.chunk_from_adapter_result(adapter_result, source_id)

    def _generate_embeddings(
        self, chunks: list, source_id: str
    ) -> list[list[float]]:
        """Generate embeddings for all chunks.

        Args:
            chunks: List of ChunkOutput objects.
            source_id: Source ID for error reporting.

        Returns:
            List of embedding vectors (384 dimensions each).

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        embedder = get_embedder()
        chunk_texts = [chunk.content for chunk in chunks]
        return embedder.embed_batch(chunk_texts)

    def _store_chunks_and_vectors(
        self,
        chunks: list,
        embeddings: list[list[float]],
        source_id: str,
    ) -> list[str]:
        """Store chunks in MongoDB and vectors in Qdrant.

        Args:
            chunks: List of ChunkOutput objects.
            embeddings: List of embedding vectors.
            source_id: Source ID for linking.

        Returns:
            List of chunk IDs.

        Raises:
            StorageOrchestrationError: If storage fails.
        """
        chunk_ids = []

        # Convert ChunkOutput to Chunk model and store in MongoDB
        mongo_chunks = []
        for chunk_output in chunks:
            chunk = Chunk(
                id="0" * 24,  # Placeholder
                source_id=source_id,
                content=chunk_output.content,
                position=ChunkPosition(
                    chapter=chunk_output.position.get("chapter"),
                    section=chunk_output.position.get("section"),
                    page=chunk_output.position.get("page"),
                ),
                token_count=chunk_output.token_count,
            )
            mongo_chunks.append(chunk)

        # Bulk insert chunks to MongoDB
        chunk_ids = self.mongodb.create_chunks_bulk(mongo_chunks)

        logger.info(
            "chunks_stored_mongodb",
            source_id=source_id,
            chunk_count=len(chunk_ids),
        )

        # Prepare Qdrant points with chunk metadata
        points = []
        for chunk_id, chunk_output, embedding in zip(
            chunk_ids, chunks, embeddings
        ):
            qdrant_id = _string_to_uuid(chunk_id)
            payload = {
                "source_id": source_id,
                "chunk_id": chunk_id,
                "position": chunk_output.position,
                "_original_id": chunk_id,
            }
            points.append(
                PointStruct(
                    id=qdrant_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        # Batch upsert to Qdrant
        upserted_count = self.qdrant.upsert_vectors_batch(
            collection=CHUNKS_COLLECTION,
            points=points,
        )

        logger.info(
            "vectors_stored_qdrant",
            source_id=source_id,
            vector_count=upserted_count,
        )

        return chunk_ids

    def _mark_failed(self, source_id: str, error_message: str) -> None:
        """Mark source as failed with error details.

        Args:
            source_id: Source ID to update.
            error_message: Error message to store.
        """
        try:
            self.mongodb.update_source(
                source_id,
                {
                    "status": IngestionStatus.FAILED.value,
                    "metadata.error": error_message,
                },
            )
        except Exception as e:
            logger.error(
                "failed_to_mark_source_failed",
                source_id=source_id,
                error=str(e),
            )
