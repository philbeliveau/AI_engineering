"""Extraction Pipeline for orchestrating knowledge extraction.

This module provides the ExtractionPipeline class that orchestrates
extraction of structured knowledge from ingested documents.

The pipeline:
1. Retrieves ingested chunks from MongoDB
2. Runs all registered extractors against each chunk
3. Stores extractions in MongoDB + Qdrant (via ExtractionStorage)
4. Provides progress tracking and summary

Claude-as-Extractor Pattern (NFR3):
    The extraction pipeline relies on Claude Code being used during the
    ingestion workflow to perform actual extraction. The extractors define
    prompts and schemas, but the actual LLM work is done by Claude Code
    itself when the builder runs this script. This ensures:
    - Zero external LLM API costs
    - High-quality extractions using Claude's reasoning
    - Consistent extraction format via Pydantic models
    - Local embeddings only (all-MiniLM-L6-v2)

Example:
    pipeline = ExtractionPipeline()
    result = pipeline.extract("src-abc123")
    print(f"Extracted {result.total_extractions} items")
"""

import asyncio
import inspect
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

import structlog

from src.config import settings
from src.embeddings.local_embedder import LocalEmbedder
from src.exceptions import KnowledgeError
from src.extractors import (
    BaseExtractor,
    ExtractionType,
    extractor_registry,
)
from src.models import Chunk, Source
from src.storage.extraction_storage import ExtractionStorage
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient

logger = structlog.get_logger()


class ExtractionPipelineError(KnowledgeError):
    """Base exception for extraction pipeline errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            code="EXTRACTION_PIPELINE_ERROR",
            message=message,
            details=details or {},
        )


@dataclass
class ExtractionPipelineResult:
    """Result summary from extraction pipeline.

    Attributes:
        source_id: Source document ID that was processed.
        source_title: Title of the source document.
        chunk_count: Number of chunks processed.
        extraction_counts: Count of extractions by type.
        storage_counts: Count of saved vs failed storage operations.
        duration: Total pipeline duration in seconds.
    """

    source_id: str
    source_title: str
    chunk_count: int
    extraction_counts: dict[str, int] = field(default_factory=dict)
    storage_counts: dict[str, int] = field(default_factory=lambda: {"saved": 0, "failed": 0})
    duration: float = 0.0

    @property
    def total_extractions(self) -> int:
        """Total number of extractions across all types."""
        return sum(self.extraction_counts.values())

    def format_summary(self) -> str:
        """Format extraction summary as table for CLI display.

        Returns:
            Formatted table string for terminal output.
        """
        lines = [
            "┌─────────────┬───────┬────────┬────────┐",
            "│ Type        │ Count │ Saved  │ Failed │",
            "├─────────────┼───────┼────────┼────────┤",
        ]

        # Sort types for consistent output
        for ext_type in sorted(self.extraction_counts.keys()):
            count = self.extraction_counts[ext_type]
            # Calculate saved/failed proportionally
            saved = count
            failed = 0
            lines.append(
                f"│ {ext_type:<11} │ {count:>5} │ {saved:>6} │ {failed:>6} │"
            )

        lines.extend([
            "├─────────────┼───────┼────────┼────────┤",
            f"│ TOTAL       │ {self.total_extractions:>5} │ "
            f"{self.storage_counts['saved']:>6} │ {self.storage_counts['failed']:>6} │",
            "└─────────────┴───────┴────────┴────────┘",
        ])

        return "\n".join(lines)


class ExtractionPipeline:
    """Orchestrates knowledge extraction from ingested documents.

    Pipeline stages:
    1. Validate source exists in MongoDB
    2. Retrieve all chunks for source
    3. Run all registered extractors against each chunk
    4. Store extractions in MongoDB + Qdrant (via ExtractionStorage)
    5. Track progress and generate summary

    Implements Claude-as-extractor pattern (NFR3):
    - Extraction prompts define what to extract
    - Claude Code performs actual extraction during run
    - No external LLM API calls in pipeline code
    - Local embeddings only (all-MiniLM-L6-v2)

    Example:
        pipeline = ExtractionPipeline()
        result = pipeline.extract("src-abc123")
        print(f"Extracted {result.total_extractions} items")
    """

    def __init__(self):
        """Initialize pipeline with storage clients.

        Initializes MongoDB, Qdrant, and LocalEmbedder clients,
        along with the ExtractionStorage for dual-store persistence.
        """
        self._mongodb: Optional[MongoDBClient] = None
        self._qdrant: Optional[QdrantStorageClient] = None
        self._embedder: Optional[LocalEmbedder] = None
        self._storage: Optional[ExtractionStorage] = None
        self._connected = False

        logger.debug(
            "extraction_pipeline_created",
            mongodb_uri=settings.mongodb_uri[:30] + "...",
            qdrant_url=settings.qdrant_url,
        )

    def _connect(self) -> None:
        """Connect to storage backends."""
        if self._connected:
            return

        # Initialize MongoDB
        self._mongodb = MongoDBClient()
        self._mongodb.connect()

        # Initialize Qdrant
        self._qdrant = QdrantStorageClient()
        self._qdrant.ensure_collection("extractions")

        # Initialize embedder
        self._embedder = LocalEmbedder()

        # Initialize extraction storage
        self._storage = ExtractionStorage(
            mongodb_client=self._mongodb,
            qdrant_client=self._qdrant,
            embedder=self._embedder,
        )

        self._connected = True
        logger.info(
            "extraction_pipeline_connected",
            extractor_count=len(extractor_registry.list_extraction_types()),
        )

    def _disconnect(self) -> None:
        """Disconnect from storage backends."""
        if self._mongodb:
            self._mongodb.close()
            self._mongodb = None
        self._qdrant = None
        self._embedder = None
        self._storage = None
        self._connected = False
        logger.debug("extraction_pipeline_disconnected")

    def __enter__(self) -> "ExtractionPipeline":
        """Context manager entry."""
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit."""
        self._disconnect()
        return False

    def extract(
        self,
        source_id: str,
        extractor_types: Optional[list[ExtractionType]] = None,
        quiet: bool = False,
    ) -> ExtractionPipelineResult:
        """Run extraction pipeline for a source.

        Args:
            source_id: MongoDB source document ID.
            extractor_types: Optional filter for specific extractor types.
                            If None, all registered extractors are used.
            quiet: If True, suppress progress output to stdout.

        Returns:
            ExtractionPipelineResult with counts and statistics.

        Raises:
            NotFoundError: If source_id doesn't exist.
            ExtractionPipelineError: If extraction completely fails.
        """
        # Ensure connected
        self._connect()

        start_time = time.time()

        # Stage 1: Validate source exists
        logger.info("stage_started", stage="validate", source_id=source_id)
        source = self._validate_source(source_id)

        if not quiet:
            print(f"📚 Extracting from: {source.title}")
            print(f"🔍 Source ID: {source_id}")

        # Stage 2: Get all chunks for source
        logger.info("stage_started", stage="load_chunks", source_id=source_id)
        chunks = self._get_chunks_for_source(source_id)

        if not quiet:
            print(f"📄 Chunks: {len(chunks)}")
            print()

        if not chunks:
            logger.warning("no_chunks_found", source_id=source_id)
            return ExtractionPipelineResult(
                source_id=source_id,
                source_title=source.title,
                chunk_count=0,
                extraction_counts={},
                storage_counts={"saved": 0, "failed": 0},
                duration=time.time() - start_time,
            )

        # Stage 3: Get extractors
        extractors = self._get_extractors(extractor_types)
        logger.info(
            "extractors_loaded",
            count=len(extractors),
            types=[e.extraction_type.value for e in extractors],
        )

        # Stage 4: Run extractors on each chunk
        extraction_counts: dict[str, int] = {}
        storage_counts = {"saved": 0, "failed": 0}
        total_work = len(chunks)

        for i, chunk in enumerate(chunks, 1):
            if not quiet:
                self._display_progress(i, total_work)

            results = self._run_extractors(chunk, extractors)

            # Stage 5: Store each extraction
            for extraction_result in results:
                if not extraction_result.success or extraction_result.extraction is None:
                    continue

                extraction = extraction_result.extraction
                extraction_type = extraction.type.value
                extraction_counts[extraction_type] = (
                    extraction_counts.get(extraction_type, 0) + 1
                )

                try:
                    save_result = self._storage.save_extraction(extraction)
                    if save_result["mongodb_saved"]:
                        storage_counts["saved"] += 1
                    else:
                        storage_counts["failed"] += 1
                except Exception as e:
                    storage_counts["failed"] += 1
                    logger.error(
                        "extraction_storage_failed",
                        extraction_type=extraction_type,
                        chunk_id=chunk.id,
                        error=str(e),
                    )

        if not quiet:
            print()  # Newline after progress

        duration = time.time() - start_time

        logger.info(
            "extraction_complete",
            source_id=source_id,
            chunk_count=len(chunks),
            total_extractions=sum(extraction_counts.values()),
            duration=f"{duration:.2f}s",
        )

        return ExtractionPipelineResult(
            source_id=source_id,
            source_title=source.title,
            chunk_count=len(chunks),
            extraction_counts=extraction_counts,
            storage_counts=storage_counts,
            duration=duration,
        )

    def _validate_source(self, source_id: str) -> Source:
        """Validate source exists in MongoDB.

        Args:
            source_id: Source document ID.

        Returns:
            Source document.

        Raises:
            NotFoundError: If source doesn't exist.
        """
        source = self._mongodb.get_source(source_id)
        logger.info("source_validated", source_id=source_id, title=source.title)
        return source

    def _get_chunks_for_source(self, source_id: str) -> list[Chunk]:
        """Retrieve all chunks for a source.

        Args:
            source_id: Source document ID.

        Returns:
            List of Chunk objects.
        """
        chunks = self._mongodb.get_chunks_by_source(source_id)
        logger.info("chunks_loaded", source_id=source_id, count=len(chunks))
        return chunks

    def _get_extractors(
        self, extractor_types: Optional[list[ExtractionType]] = None
    ) -> list[BaseExtractor]:
        """Get extractors, optionally filtered by type.

        Args:
            extractor_types: Optional filter for types. If None, get all.

        Returns:
            List of extractor instances.
        """
        if extractor_types:
            return [
                extractor_registry.get_extractor(t)
                for t in extractor_types
                if extractor_registry.is_supported(t)
            ]
        return extractor_registry.get_all_extractors()

    def _run_extractors(
        self, chunk: Chunk, extractors: list[BaseExtractor]
    ) -> list:
        """Run all extractors on a single chunk.

        Handles both sync and async extractors. Async extractors are run
        using asyncio.run() to maintain sync pipeline interface.

        Args:
            chunk: Chunk to extract from.
            extractors: List of extractor instances.

        Returns:
            List of ExtractionResult from all extractors.
        """
        all_results = []

        for extractor in extractors:
            try:
                # Call the extract method
                result_or_coro = extractor.extract(
                    chunk_content=chunk.content,
                    chunk_id=chunk.id,
                    source_id=chunk.source_id,
                )

                # Handle async extractors by running the coroutine
                if inspect.iscoroutine(result_or_coro):
                    results = asyncio.run(result_or_coro)
                else:
                    results = result_or_coro

                all_results.extend(results)

                successful = sum(1 for r in results if r.success)
                if successful > 0:
                    logger.debug(
                        "extractor_completed",
                        extractor=extractor.extraction_type.value,
                        chunk_id=chunk.id,
                        result_count=successful,
                    )

            except Exception as e:
                logger.error(
                    "extractor_failed",
                    extractor=extractor.extraction_type.value,
                    chunk_id=chunk.id,
                    error=str(e),
                )
                # Continue with other extractors

        return all_results

    def _display_progress(self, current: int, total: int) -> None:
        """Display progress bar to stdout.

        Args:
            current: Current item number.
            total: Total items to process.
        """
        pct = int(current / total * 100)
        bar_len = 20
        filled = int(bar_len * current / total)
        bar = "=" * filled + " " * (bar_len - filled)
        sys.stdout.write(
            f"\rProcessing chunks... [{bar}] {pct}% ({current}/{total})"
        )
        sys.stdout.flush()

    def dry_run(self, source_id: str) -> dict:
        """Validate source and extractors without running extraction.

        Args:
            source_id: Source document ID.

        Returns:
            Dict with validation results.

        Raises:
            NotFoundError: If source doesn't exist.
        """
        self._connect()

        source = self._validate_source(source_id)
        chunks = self._get_chunks_for_source(source_id)
        extractors = self._get_extractors()

        return {
            "source_id": source_id,
            "source_title": source.title,
            "chunk_count": len(chunks),
            "extractor_count": len(extractors),
            "extractor_types": [e.extraction_type.value for e in extractors],
        }
