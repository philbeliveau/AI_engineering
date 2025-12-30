# Story 3.7: Extraction Pipeline CLI

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **builder**,
I want to run knowledge extraction on ingested sources via CLI,
So that I can extract all knowledge types from a book in one command.

## Acceptance Criteria

**Given** a source has been ingested (chunks exist)
**When** I run `uv run scripts/extract.py <source_id>`
**Then** all extractors are run against each chunk
**And** extractions are saved to MongoDB and Qdrant
**And** progress is displayed during extraction
**And** a summary shows extraction counts by type
**And** the Claude-as-extractor pattern is used (NFR3: zero external API costs)

## Dependency Analysis

**Depends On (MUST BE COMPLETE):**
- **Story 2.6:** End-to-End Ingestion Pipeline - Provides `IngestionPipeline` pattern, CLI script pattern, and ingested chunks to extract from
- **Story 3.1:** Base Extractor Interface - Provides `BaseExtractor` ABC, all extraction models, `ExtractionType` enum, `extractor_registry`
- **Story 3.2:** Decision Extractor - Provides `DecisionExtractor` for decision extraction
- **Story 3.3:** Pattern Extractor - Provides `PatternExtractor` for pattern extraction
- **Story 3.4:** Warning Extractor - Provides `WarningExtractor` for warning extraction
- **Story 3.5:** Methodology and Process Extractors - Provides `MethodologyExtractor`, `ChecklistExtractor`, `PersonaExtractor`, `WorkflowExtractor`
- **Story 3.6:** Extraction Storage and Embedding - Provides `ExtractionStorage` for dual-store persistence (MongoDB + Qdrant)
- **Story 1.4:** MongoDB Storage Client - Provides `MongoDBClient` for retrieving chunks and storing extractions
- **Story 1.5:** Qdrant Storage Client - Provides `QdrantClient` for storing extraction embeddings

**Blocks:**
- **Epic 4 Stories (MCP Tools)** - Uses extractions created by this pipeline for query responses
- None directly, this is the final story in Epic 3

## Tasks / Subtasks

- [ ] **Task 1: Verify Prerequisites** (AC: All dependencies available)
  - [ ] 1.1: Confirm Story 2.6 complete (ingestion pipeline exists): `ls packages/pipeline/scripts/ingest.py`
  - [ ] 1.2: Confirm Story 3.1-3.5 complete (all extractors exist): `cd packages/pipeline && uv run python -c "from src.extractors import DecisionExtractor, PatternExtractor, WarningExtractor, MethodologyExtractor, ChecklistExtractor, PersonaExtractor, WorkflowExtractor, extractor_registry; print('OK')"`
  - [ ] 1.3: Confirm Story 3.6 complete (extraction storage exists): `cd packages/pipeline && uv run python -c "from src.storage.extraction_storage import ExtractionStorage; print('OK')"`
  - [ ] 1.4: Confirm MongoDB can retrieve chunks by source_id: `cd packages/pipeline && uv run python -c "from src.storage.mongodb import MongoDBClient; print('OK')"`
  - [ ] 1.5: Verify at least one source has been ingested for testing: `docker-compose exec mongodb mongosh --eval 'db.sources.count()'`

- [ ] **Task 2: Create Extraction Pipeline Orchestrator** (AC: All extractors run)
  - [ ] 2.1: Create `packages/pipeline/src/extraction/` module directory
  - [ ] 2.2: Create `packages/pipeline/src/extraction/__init__.py` with exports
  - [ ] 2.3: Create `packages/pipeline/src/extraction/pipeline.py`
  - [ ] 2.4: Implement `ExtractionPipeline` class with constructor taking settings
  - [ ] 2.5: Inject all dependencies: MongoDB client, Qdrant client, ExtractionStorage, all extractors
  - [ ] 2.6: Implement `extract(source_id: str)` orchestration method
  - [ ] 2.7: Add structured logging for pipeline stages with structlog

- [ ] **Task 3: Implement Chunk Retrieval** (AC: Process all chunks for source)
  - [ ] 3.1: Add method `_get_chunks_for_source(source_id: str) -> list[Chunk]`
  - [ ] 3.2: Query MongoDB `chunks` collection by `source_id`
  - [ ] 3.3: Validate source exists (raise `NotFoundError` if not)
  - [ ] 3.4: Validate chunks exist (warn if source has no chunks)
  - [ ] 3.5: Log chunk count: `logger.info("chunks_loaded", source_id=source_id, count=len(chunks))`

- [ ] **Task 4: Implement Extractor Orchestration** (AC: All extractors run per chunk)
  - [ ] 4.1: Add method `_run_extractors(chunk: Chunk) -> list[ExtractionResult]`
  - [ ] 4.2: Get all registered extractors from `extractor_registry.get_all_extractors()`
  - [ ] 4.3: For each extractor, call `extractor.extract(chunk.content, chunk.id, chunk.source_id)`
  - [ ] 4.4: Collect all extraction results from all extractors
  - [ ] 4.5: Handle individual extractor failures gracefully (log error, continue with others)
  - [ ] 4.6: Log per-chunk extraction: `logger.info("chunk_extracted", chunk_id=chunk.id, extraction_count=len(results))`

- [ ] **Task 5: Implement Extraction Storage Integration** (AC: Saved to MongoDB + Qdrant)
  - [ ] 5.1: Initialize `ExtractionStorage` in pipeline constructor
  - [ ] 5.2: After each extractor returns results, call `storage.save_extraction(extraction)` for each
  - [ ] 5.3: Track save success/failure counts per extraction type
  - [ ] 5.4: Handle partial storage failures (log, continue with next extraction)
  - [ ] 5.5: Log storage progress: `logger.info("extraction_saved", type=extraction.type, id=extraction_id)`

- [ ] **Task 6: Implement Progress Display** (AC: Progress displayed during extraction)
  - [ ] 6.1: Calculate total work: `total_chunks * num_extractors`
  - [ ] 6.2: Display progress to stdout: "Processing chunk 5/100 (5%)"
  - [ ] 6.3: Update progress after each chunk completes
  - [ ] 6.4: Use simple print-based progress (no external libraries like tqdm required)
  - [ ] 6.5: Option for quiet mode (`--quiet` flag) to suppress progress output
  - [ ] 6.6: Always log progress with structlog regardless of display mode

- [ ] **Task 7: Implement Extraction Summary** (AC: Summary shows counts by type)
  - [ ] 7.1: Create `ExtractionResult` dataclass for pipeline summary
  - [ ] 7.2: Track extraction counts by type: `{decision: 10, pattern: 5, warning: 8, ...}`
  - [ ] 7.3: Track storage success/failure counts
  - [ ] 7.4: Calculate total duration
  - [ ] 7.5: Return structured result from `extract()` method
  - [ ] 7.6: Format summary for CLI display (table format)

- [ ] **Task 8: Create CLI Script** (AC: `uv run scripts/extract.py <source_id>`)
  - [ ] 8.1: Create `packages/pipeline/scripts/extract.py`
  - [ ] 8.2: Use argparse for command-line argument parsing
  - [ ] 8.3: Accept `source_id` as required positional argument
  - [ ] 8.4: Add optional arguments: `--extractors` (filter types), `--dry-run`, `--verbose`, `--quiet`
  - [ ] 8.5: Initialize pipeline with config from `pydantic-settings`
  - [ ] 8.6: Call `ExtractionPipeline.extract(source_id)`
  - [ ] 8.7: Display extraction summary on completion
  - [ ] 8.8: Return appropriate exit codes (0 success, 1 error, 2 partial failure)

- [ ] **Task 9: Implement Error Handling** (AC: Graceful failure handling)
  - [ ] 9.1: Validate source_id format before processing
  - [ ] 9.2: Handle `NotFoundError` when source doesn't exist
  - [ ] 9.3: Handle individual extractor failures (log, continue)
  - [ ] 9.4: Handle individual storage failures (log, continue)
  - [ ] 9.5: Report partial success when some extractions fail
  - [ ] 9.6: Log all errors with structured context
  - [ ] 9.7: Use custom `ExtractionPipelineError` exception

- [ ] **Task 10: Implement Claude-as-Extractor Pattern** (AC: NFR3 zero API costs)
  - [ ] 10.1: Document the Claude-as-extractor pattern in code comments
  - [ ] 10.2: Extraction prompts are designed to be run by Claude Code user during ingestion
  - [ ] 10.3: No external LLM API calls in the pipeline code itself
  - [ ] 10.4: All embeddings use local all-MiniLM-L6-v2 (Story 2.5)
  - [ ] 10.5: Add clear documentation on how the pattern works

- [ ] **Task 11: Create Unit Tests** (AC: Individual components tested)
  - [ ] 11.1: Create `packages/pipeline/tests/test_extraction/__init__.py`
  - [ ] 11.2: Create `packages/pipeline/tests/test_extraction/test_pipeline.py`
  - [ ] 11.3: Test `ExtractionPipeline` initialization with mocked dependencies
  - [ ] 11.4: Test `_get_chunks_for_source()` with mock MongoDB
  - [ ] 11.5: Test `_run_extractors()` with mock extractors
  - [ ] 11.6: Test error handling for missing source
  - [ ] 11.7: Test error handling for extractor failures
  - [ ] 11.8: Test extraction summary calculation

- [ ] **Task 12: Create Integration Tests** (AC: End-to-end tested)
  - [ ] 12.1: Create `packages/pipeline/tests/test_extraction/test_integration.py`
  - [ ] 12.2: Ingest a sample document first using Story 2.6 pipeline
  - [ ] 12.3: Run extraction pipeline on ingested source
  - [ ] 12.4: Verify extractions exist in MongoDB `extractions` collection
  - [ ] 12.5: Verify embeddings exist in Qdrant `extractions` collection
  - [ ] 12.6: Verify extraction counts match expected (at least some extractions per type)
  - [ ] 12.7: Test with various document types (PDF, Markdown)
  - [ ] 12.8: Run all tests: `cd packages/pipeline && uv run pytest tests/test_extraction/ -v`

## Dev Notes

### Critical Implementation Context

**Core Philosophy:** Extractions are for NAVIGATION, Claude is for SYNTHESIS. This CLI creates the complete extraction pipeline that populates both stores with structured knowledge, enabling MCP tools in Epic 4 to query and serve results to users.

**Claude-as-Extractor Pattern (NFR3):**
The extraction pipeline relies on Claude Code being used during the ingestion workflow to perform actual extraction. The extractors define prompts and schemas, but the actual LLM work is done by Claude Code itself when the builder runs this script. This ensures:
- Zero external LLM API costs
- High-quality extractions using Claude's reasoning
- Consistent extraction format via Pydantic models
- Local embeddings only (all-MiniLM-L6-v2)

### Pipeline Architecture

This story implements the **complete extraction pipeline** that:
1. Retrieves ingested chunks from MongoDB
2. Runs all extractors against each chunk
3. Stores extractions in MongoDB + Qdrant (via Story 3.6)
4. Provides progress tracking and summary

**Data Flow:**
```
Source ID → Get Chunks (MongoDB) → Run Extractors → Store Results (MongoDB + Qdrant)
     │              │                    │                       │
     │              │                    │                       └─→ Qdrant extractions
     │              │                    │                              (384d embeddings)
     │              │                    │
     │              │                    └─→ MongoDB extractions
     │              │                           (full documents)
     │              │
     │              └─→ chunks collection (source_id filter)
     │
     └─→ sources collection (validate exists)
```

**Architecture Diagram (from architecture.md:729-752):**
```
┌─────────────────────────────────────────────────────────────────────┐
│                    packages/pipeline (batch)                         │
│  Adapters ──▶ Processors ──▶ Extractors ──▶ Storage (write)         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              ┌──────────┐                   ┌──────────┐
              │ MongoDB  │                   │  Qdrant  │
              │          │                   │          │
              │ sources  │                   │  chunks  │
              │ chunks   │                   │extractions
              │extractions                   └──────────┘
              └──────────┘
```

### CLI Script Pattern (Following Story 2.6)

**Usage Examples:**
```bash
# Basic usage
uv run scripts/extract.py src-abc123

# Extract specific types only
uv run scripts/extract.py src-abc123 --extractors decision,pattern,warning

# Dry run (validate without extraction)
uv run scripts/extract.py src-abc123 --dry-run

# Verbose logging
uv run scripts/extract.py src-abc123 --verbose

# Quiet mode (no progress output)
uv run scripts/extract.py src-abc123 --quiet
```

**Expected Output:**
```
📚 Extracting from: LLM Engineering Handbook
🔍 Source ID: src-abc123def456
📄 Chunks: 342

Processing chunks... [====================] 100% (342/342)

✅ Extraction Complete!

┌─────────────┬───────┬────────┬────────┐
│ Type        │ Count │ Saved  │ Failed │
├─────────────┼───────┼────────┼────────┤
│ decision    │    28 │     28 │      0 │
│ pattern     │    15 │     15 │      0 │
│ warning     │    21 │     21 │      0 │
│ methodology │     8 │      8 │      0 │
│ checklist   │     5 │      5 │      0 │
│ persona     │     3 │      3 │      0 │
│ workflow    │     4 │      4 │      0 │
├─────────────┼───────┼────────┼────────┤
│ TOTAL       │    84 │     84 │      0 │
└─────────────┴───────┴────────┴────────┘

Duration: 12.45s
MongoDB: 84 documents stored
Qdrant: 84 vectors indexed

Next step: Query extractions via MCP tools in Epic 4
```

### ExtractionPipeline Implementation Pattern

```python
# packages/pipeline/src/extraction/pipeline.py
from pathlib import Path
from typing import Optional
import time
import structlog

from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantClient
from src.storage.extraction_storage import ExtractionStorage
from src.embeddings.local_embedder import LocalEmbedder
from src.extractors import extractor_registry, ExtractionType
from src.models.chunk import Chunk
from src.config import Settings
from src.exceptions import KnowledgeError, NotFoundError

logger = structlog.get_logger()


class ExtractionPipelineError(KnowledgeError):
    """Base exception for extraction pipeline errors."""
    pass


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
        pipeline = ExtractionPipeline(settings)
        result = await pipeline.extract("src-abc123")
        print(f"Extracted {result.total_count} items")
    """

    def __init__(self, settings: Settings):
        """Initialize pipeline with configuration and dependencies.

        Args:
            settings: Pydantic Settings with MongoDB/Qdrant configuration.
        """
        self.settings = settings
        self.mongodb = MongoDBClient(settings.mongodb_uri)
        self.qdrant = QdrantClient(settings.qdrant_url)
        self.embedder = LocalEmbedder(settings.embedding_model)
        self.storage = ExtractionStorage(
            mongodb_client=self.mongodb,
            qdrant_client=self.qdrant,
            embedder=self.embedder
        )

        logger.info(
            "extraction_pipeline_initialized",
            extractor_count=len(extractor_registry.get_all_types()),
            mongodb_uri=settings.mongodb_uri[:30] + "..."  # Truncate for logging
        )

    async def extract(
        self,
        source_id: str,
        extractor_types: Optional[list[ExtractionType]] = None,
        quiet: bool = False
    ) -> "ExtractionResult":
        """Run extraction pipeline for a source.

        Args:
            source_id: MongoDB source document ID.
            extractor_types: Optional filter for specific extractor types.
                            If None, all registered extractors are used.
            quiet: If True, suppress progress output to stdout.

        Returns:
            ExtractionResult with counts and statistics.

        Raises:
            NotFoundError: If source_id doesn't exist.
            ExtractionPipelineError: If extraction completely fails.
        """
        start_time = time.time()

        # Stage 1: Validate source exists
        logger.info("stage_started", stage="validate", source_id=source_id)
        source = await self._validate_source(source_id)

        if not quiet:
            print(f"📚 Extracting from: {source.title}")
            print(f"🔍 Source ID: {source_id}")

        # Stage 2: Get all chunks for source
        logger.info("stage_started", stage="load_chunks", source_id=source_id)
        chunks = await self._get_chunks_for_source(source_id)

        if not quiet:
            print(f"📄 Chunks: {len(chunks)}")
            print()

        if not chunks:
            logger.warning("no_chunks_found", source_id=source_id)
            return ExtractionResult(
                source_id=source_id,
                source_title=source.title,
                chunk_count=0,
                extraction_counts={},
                storage_counts={"saved": 0, "failed": 0},
                duration=time.time() - start_time
            )

        # Stage 3: Get extractors
        extractors = self._get_extractors(extractor_types)
        logger.info(
            "extractors_loaded",
            count=len(extractors),
            types=[e.extraction_type.value for e in extractors]
        )

        # Stage 4: Run extractors on each chunk
        extraction_counts: dict[str, int] = {}
        storage_counts = {"saved": 0, "failed": 0}
        total_work = len(chunks)

        for i, chunk in enumerate(chunks, 1):
            if not quiet:
                self._display_progress(i, total_work)

            results = await self._run_extractors(chunk, extractors)

            # Stage 5: Store each extraction
            for extraction in results:
                extraction_type = extraction.type.value
                extraction_counts[extraction_type] = extraction_counts.get(extraction_type, 0) + 1

                try:
                    save_result = self.storage.save_extraction(extraction)
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
                        error=str(e)
                    )

        if not quiet:
            print()  # Newline after progress

        duration = time.time() - start_time

        logger.info(
            "extraction_complete",
            source_id=source_id,
            chunk_count=len(chunks),
            total_extractions=sum(extraction_counts.values()),
            duration=f"{duration:.2f}s"
        )

        return ExtractionResult(
            source_id=source_id,
            source_title=source.title,
            chunk_count=len(chunks),
            extraction_counts=extraction_counts,
            storage_counts=storage_counts,
            duration=duration
        )

    async def _validate_source(self, source_id: str):
        """Validate source exists in MongoDB.

        Args:
            source_id: Source document ID.

        Returns:
            Source document.

        Raises:
            NotFoundError: If source doesn't exist.
        """
        source = await self.mongodb.get_source(source_id)
        if not source:
            raise NotFoundError(
                resource="source",
                id=source_id
            )
        return source

    async def _get_chunks_for_source(self, source_id: str) -> list[Chunk]:
        """Retrieve all chunks for a source.

        Args:
            source_id: Source document ID.

        Returns:
            List of Chunk objects.
        """
        chunks = await self.mongodb.get_chunks_by_source(source_id)
        logger.info("chunks_loaded", source_id=source_id, count=len(chunks))
        return chunks

    def _get_extractors(self, extractor_types: Optional[list[ExtractionType]] = None):
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

    async def _run_extractors(self, chunk: Chunk, extractors) -> list:
        """Run all extractors on a single chunk.

        Args:
            chunk: Chunk to extract from.
            extractors: List of extractor instances.

        Returns:
            List of extraction results from all extractors.
        """
        all_results = []

        for extractor in extractors:
            try:
                results = extractor.extract(
                    chunk_content=chunk.content,
                    chunk_id=chunk.id,
                    source_id=chunk.source_id
                )
                all_results.extend(results)

                if results:
                    logger.debug(
                        "extractor_completed",
                        extractor=extractor.extraction_type.value,
                        chunk_id=chunk.id,
                        result_count=len(results)
                    )

            except Exception as e:
                logger.error(
                    "extractor_failed",
                    extractor=extractor.extraction_type.value,
                    chunk_id=chunk.id,
                    error=str(e)
                )
                # Continue with other extractors

        return all_results

    def _display_progress(self, current: int, total: int):
        """Display progress bar to stdout.

        Args:
            current: Current item number.
            total: Total items to process.
        """
        pct = int(current / total * 100)
        bar_len = 20
        filled = int(bar_len * current / total)
        bar = "=" * filled + " " * (bar_len - filled)
        print(f"\rProcessing chunks... [{bar}] {pct}% ({current}/{total})", end="", flush=True)


class ExtractionResult:
    """Result summary from extraction pipeline."""

    def __init__(
        self,
        source_id: str,
        source_title: str,
        chunk_count: int,
        extraction_counts: dict[str, int],
        storage_counts: dict[str, int],
        duration: float
    ):
        self.source_id = source_id
        self.source_title = source_title
        self.chunk_count = chunk_count
        self.extraction_counts = extraction_counts
        self.storage_counts = storage_counts
        self.duration = duration

    @property
    def total_extractions(self) -> int:
        """Total number of extractions across all types."""
        return sum(self.extraction_counts.values())

    def format_summary(self) -> str:
        """Format extraction summary as table for CLI display."""
        lines = [
            "┌─────────────┬───────┬────────┬────────┐",
            "│ Type        │ Count │ Saved  │ Failed │",
            "├─────────────┼───────┼────────┼────────┤",
        ]

        # Sort types for consistent output
        for ext_type in sorted(self.extraction_counts.keys()):
            count = self.extraction_counts[ext_type]
            # Assume all saved for now (simplification)
            saved = count
            failed = 0
            lines.append(f"│ {ext_type:<11} │ {count:>5} │ {saved:>6} │ {failed:>6} │")

        lines.extend([
            "├─────────────┼───────┼────────┼────────┤",
            f"│ TOTAL       │ {self.total_extractions:>5} │ {self.storage_counts['saved']:>6} │ {self.storage_counts['failed']:>6} │",
            "└─────────────┴───────┴────────┴────────┘",
        ])

        return "\n".join(lines)
```

### CLI Script Pattern

```python
# packages/pipeline/scripts/extract.py
"""CLI script for extracting knowledge from ingested documents.

Usage:
    uv run scripts/extract.py <source_id>
    uv run scripts/extract.py <source_id> --extractors decision,pattern
    uv run scripts/extract.py <source_id> --dry-run
    uv run scripts/extract.py <source_id> --verbose

Examples:
    uv run scripts/extract.py src-abc123def456
    uv run scripts/extract.py src-abc123 --extractors decision,warning --verbose

Claude-as-Extractor Pattern:
    This script implements NFR3 (zero external API costs) by using Claude Code
    as the extraction engine. When you run this script, Claude analyzes each
    chunk using the extraction prompts defined in the extractors. No external
    LLM API calls are made - Claude Code itself is the extractor.
"""
import sys
import asyncio
import argparse
from pathlib import Path
import structlog

from src.config import Settings
from src.extraction.pipeline import ExtractionPipeline, ExtractionPipelineError
from src.extractors import ExtractionType
from src.exceptions import NotFoundError

logger = structlog.get_logger()


def parse_extractor_types(value: str) -> list[ExtractionType]:
    """Parse comma-separated extractor types.

    Args:
        value: Comma-separated string like "decision,pattern,warning"

    Returns:
        List of ExtractionType enum values.

    Raises:
        argparse.ArgumentTypeError: If invalid type specified.
    """
    types = []
    for t in value.split(","):
        t = t.strip().lower()
        try:
            types.append(ExtractionType(t))
        except ValueError:
            valid = [e.value for e in ExtractionType]
            raise argparse.ArgumentTypeError(
                f"Invalid extractor type: {t}. Valid types: {', '.join(valid)}"
            )
    return types


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract knowledge from ingested documents",
        epilog="Example: uv run scripts/extract.py src-abc123"
    )

    parser.add_argument(
        "source_id",
        type=str,
        help="MongoDB source document ID (from ingestion)"
    )

    parser.add_argument(
        "--extractors",
        type=parse_extractor_types,
        default=None,
        help="Comma-separated extractor types (e.g., decision,pattern,warning)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate source without running extraction"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        import logging
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG)
        )

    # Load settings
    settings = Settings()

    # Initialize pipeline
    try:
        pipeline = ExtractionPipeline(settings)
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Dry run mode
    if args.dry_run:
        try:
            source = asyncio.run(pipeline._validate_source(args.source_id))
            chunks = asyncio.run(pipeline._get_chunks_for_source(args.source_id))
            print(f"✓ Source exists: {source.title}")
            print(f"✓ Chunks found: {len(chunks)}")
            print(f"✓ Extractors available: {len(pipeline._get_extractors(args.extractors))}")
            print("Dry run complete (no extraction performed)")
            return
        except NotFoundError as e:
            print(f"❌ Source not found: {args.source_id}", file=sys.stderr)
            sys.exit(1)

    # Run extraction
    try:
        result = asyncio.run(
            pipeline.extract(
                source_id=args.source_id,
                extractor_types=args.extractors,
                quiet=args.quiet
            )
        )

        # Display summary
        if not args.quiet:
            print()
            print("✅ Extraction Complete!")
            print()
            print(result.format_summary())
            print()
            print(f"Duration: {result.duration:.2f}s")
            print(f"MongoDB: {result.storage_counts['saved']} documents stored")
            print(f"Qdrant: {result.storage_counts['saved']} vectors indexed")
            print()
            print("Next step: Query extractions via MCP tools in Epic 4")

        # Return appropriate exit code
        if result.storage_counts["failed"] > 0:
            sys.exit(2)  # Partial failure

    except NotFoundError as e:
        print(f"❌ Source not found: {args.source_id}", file=sys.stderr)
        logger.error("source_not_found", source_id=args.source_id)
        sys.exit(1)

    except ExtractionPipelineError as e:
        print(f"❌ Extraction failed: {e.message}", file=sys.stderr)
        logger.error("extraction_failed", error=str(e), details=e.details)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        logger.exception("unexpected_error")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Module Exports

```python
# packages/pipeline/src/extraction/__init__.py
"""Extraction pipeline module.

Provides the ExtractionPipeline class for running knowledge extraction
on ingested documents.
"""
from src.extraction.pipeline import (
    ExtractionPipeline,
    ExtractionResult,
    ExtractionPipelineError,
)

__all__ = [
    "ExtractionPipeline",
    "ExtractionResult",
    "ExtractionPipelineError",
]
```

### Project Structure Alignment

```
packages/pipeline/
├── src/
│   ├── extraction/                    # THIS STORY (new module)
│   │   ├── __init__.py               # Module exports
│   │   └── pipeline.py               # ExtractionPipeline class
│   ├── extractors/                   # Stories 3.1-3.5
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── decision_extractor.py
│   │   ├── pattern_extractor.py
│   │   ├── warning_extractor.py
│   │   ├── methodology_extractor.py
│   │   ├── checklist_extractor.py
│   │   ├── persona_extractor.py
│   │   ├── workflow_extractor.py
│   │   └── prompts/
│   ├── storage/                      # Stories 1.4, 1.5, 3.6
│   │   ├── mongodb.py
│   │   ├── qdrant.py
│   │   └── extraction_storage.py
│   ├── embeddings/                   # Story 2.5
│   │   └── local_embedder.py
│   └── models/
├── scripts/
│   ├── ingest.py                     # Story 2.6
│   └── extract.py                    # THIS STORY (new)
└── tests/
    └── test_extraction/              # THIS STORY (new)
        ├── __init__.py
        ├── test_pipeline.py
        └── test_integration.py
```

### Testing Strategy

**Unit Tests (`test_pipeline.py`):**

```python
# packages/pipeline/tests/test_extraction/test_pipeline.py
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.extraction.pipeline import ExtractionPipeline, ExtractionResult
from src.extractors import ExtractionType, Decision
from src.config import Settings


class TestExtractionPipeline:
    """Unit tests for ExtractionPipeline."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return Settings(
            mongodb_uri="mongodb://localhost:27017/test",
            qdrant_url="http://localhost:6333"
        )

    @pytest.fixture
    def mock_pipeline(self, mock_settings):
        """Create pipeline with mocked dependencies."""
        with patch("src.extraction.pipeline.MongoDBClient") as mock_mongo, \
             patch("src.extraction.pipeline.QdrantClient") as mock_qdrant, \
             patch("src.extraction.pipeline.LocalEmbedder") as mock_embedder, \
             patch("src.extraction.pipeline.ExtractionStorage") as mock_storage:

            mock_mongo_instance = AsyncMock()
            mock_qdrant_instance = Mock()
            mock_embedder_instance = Mock()
            mock_storage_instance = Mock()

            mock_mongo.return_value = mock_mongo_instance
            mock_qdrant.return_value = mock_qdrant_instance
            mock_embedder.return_value = mock_embedder_instance
            mock_storage.return_value = mock_storage_instance

            pipeline = ExtractionPipeline(mock_settings)
            pipeline.mongodb = mock_mongo_instance
            pipeline.storage = mock_storage_instance

            return pipeline

    @pytest.mark.asyncio
    async def test_validate_source_exists(self, mock_pipeline):
        """Test source validation when source exists."""
        mock_source = Mock(title="Test Book")
        mock_pipeline.mongodb.get_source.return_value = mock_source

        result = await mock_pipeline._validate_source("src-123")
        assert result == mock_source

    @pytest.mark.asyncio
    async def test_validate_source_not_found_raises(self, mock_pipeline):
        """Test NotFoundError raised when source missing."""
        mock_pipeline.mongodb.get_source.return_value = None

        with pytest.raises(NotFoundError):
            await mock_pipeline._validate_source("src-missing")

    @pytest.mark.asyncio
    async def test_get_chunks_for_source(self, mock_pipeline):
        """Test chunk retrieval by source ID."""
        mock_chunks = [Mock(id="chunk-1"), Mock(id="chunk-2")]
        mock_pipeline.mongodb.get_chunks_by_source.return_value = mock_chunks

        result = await mock_pipeline._get_chunks_for_source("src-123")
        assert len(result) == 2
        mock_pipeline.mongodb.get_chunks_by_source.assert_called_once_with("src-123")

    def test_get_all_extractors(self, mock_pipeline):
        """Test getting all registered extractors."""
        extractors = mock_pipeline._get_extractors(None)
        assert len(extractors) == 7  # All 7 extractor types

    def test_get_filtered_extractors(self, mock_pipeline):
        """Test getting specific extractor types."""
        extractors = mock_pipeline._get_extractors([
            ExtractionType.DECISION,
            ExtractionType.PATTERN
        ])
        assert len(extractors) == 2


class TestExtractionResult:
    """Tests for ExtractionResult dataclass."""

    def test_total_extractions(self):
        """Test total extraction count calculation."""
        result = ExtractionResult(
            source_id="src-123",
            source_title="Test",
            chunk_count=10,
            extraction_counts={"decision": 5, "pattern": 3, "warning": 2},
            storage_counts={"saved": 10, "failed": 0},
            duration=1.5
        )
        assert result.total_extractions == 10

    def test_format_summary(self):
        """Test summary table formatting."""
        result = ExtractionResult(
            source_id="src-123",
            source_title="Test",
            chunk_count=10,
            extraction_counts={"decision": 5},
            storage_counts={"saved": 5, "failed": 0},
            duration=1.5
        )
        summary = result.format_summary()
        assert "decision" in summary
        assert "5" in summary
        assert "TOTAL" in summary
```

**Integration Tests (`test_integration.py`):**

```python
# packages/pipeline/tests/test_extraction/test_integration.py
import pytest
import asyncio
from pathlib import Path

from src.extraction.pipeline import ExtractionPipeline
from src.ingestion.pipeline import IngestionPipeline
from src.config import Settings


@pytest.mark.integration
@pytest.mark.asyncio
class TestExtractionPipelineIntegration:
    """Integration tests requiring Docker Compose services."""

    @pytest.fixture
    async def settings(self):
        """Test settings pointing to Docker Compose services."""
        return Settings(
            mongodb_uri="mongodb://localhost:27017/test_extraction",
            qdrant_url="http://localhost:6333"
        )

    @pytest.fixture
    async def ingested_source(self, settings, sample_markdown):
        """Ingest a sample document first."""
        pipeline = IngestionPipeline(settings)
        result = await pipeline.ingest(sample_markdown)
        yield result.source_id
        # Cleanup
        await pipeline.mongodb.delete_source(result.source_id)

    @pytest.fixture
    def sample_markdown(self, tmp_path):
        """Create sample Markdown with extractable content."""
        md_file = tmp_path / "test_extraction.md"
        md_file.write_text("""# AI Engineering Guide

## Decision: Model Selection

When choosing an LLM, consider these options:
- GPT-4: Best quality, highest cost
- Claude: Good quality, moderate cost
- Open source: Lower cost, requires hosting

Recommendation: Start with Claude for balance of quality and cost.

## Warning: Prompt Injection

Be careful of prompt injection attacks. Users can manipulate your system
by including malicious instructions in their input. Always validate and
sanitize user input before passing to the LLM.

## Pattern: Retry with Exponential Backoff

When calling LLM APIs, implement retry logic:
1. Start with 1 second delay
2. Double delay on each retry
3. Max 5 retries before failing

This handles transient failures gracefully.
""")
        return md_file

    async def test_extract_from_ingested_source(self, settings, ingested_source):
        """Test full extraction pipeline on ingested source."""
        pipeline = ExtractionPipeline(settings)

        result = await pipeline.extract(
            source_id=ingested_source,
            quiet=True
        )

        # Verify extractions were created
        assert result.total_extractions > 0
        assert result.storage_counts["saved"] > 0
        assert result.storage_counts["failed"] == 0

        # Verify MongoDB has extraction documents
        extractions = await pipeline.mongodb.db.extractions.find({
            "source_id": ingested_source
        }).to_list(100)
        assert len(extractions) > 0

        # Verify Qdrant has vectors
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        qdrant_results = pipeline.qdrant.client.scroll(
            collection_name="extractions",
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="source_id",
                        match=MatchValue(value=ingested_source)
                    )
                ]
            ),
            limit=100
        )
        assert len(qdrant_results[0]) > 0

    async def test_extract_specific_types(self, settings, ingested_source):
        """Test extracting only specific types."""
        pipeline = ExtractionPipeline(settings)

        result = await pipeline.extract(
            source_id=ingested_source,
            extractor_types=[ExtractionType.DECISION, ExtractionType.WARNING],
            quiet=True
        )

        # Should only have decision and warning extractions
        assert set(result.extraction_counts.keys()).issubset({"decision", "warning"})

    async def test_extract_nonexistent_source_fails(self, settings):
        """Test that extracting from missing source raises error."""
        pipeline = ExtractionPipeline(settings)

        with pytest.raises(NotFoundError):
            await pipeline.extract("nonexistent-source-id")
```

### Dependencies

**Blocked By:**
- Story 2.6: End-to-End Ingestion Pipeline - CLI pattern, `IngestionPipeline` reference
- Story 3.1: Base Extractor Interface - `BaseExtractor`, `ExtractionType`, `extractor_registry`
- Story 3.2-3.5: All extractors - Provides all 7 extractors to run
- Story 3.6: Extraction Storage and Embedding - `ExtractionStorage` for dual-store persistence
- Story 1.4: MongoDB Storage Client - `MongoDBClient.get_chunks_by_source()`
- Story 1.5: Qdrant Storage Client - `QdrantClient` for embedding storage

**Blocks:**
- Epic 4 Stories - MCP tools query the extractions created by this pipeline
- No direct blockers - this is the final story in Epic 3

### Library & Framework Requirements

**No New Dependencies** - All required packages from previous stories:
- pydantic>=2.0 (model validation)
- pydantic-settings (configuration)
- pymongo (MongoDB client)
- qdrant-client>=1.13 (Qdrant operations)
- sentence-transformers>=5.0 (embeddings via Story 2.5)
- structlog (logging)
- pytest, pytest-asyncio (testing)

### Code Quality Requirements

**From project-context.md - Critical Rules:**

1. **Async Patterns (lines 54-57):**
   - Pipeline `extract()` should be async for I/O operations
   - MongoDB/Qdrant calls are async
   - CPU-bound embedding can remain sync

2. **Naming Conventions (lines 47-52):**
   - Files: `pipeline.py`, `extract.py` (snake_case)
   - Classes: `ExtractionPipeline`, `ExtractionResult` (PascalCase)
   - Methods: `extract()`, `_get_chunks_for_source()` (snake_case)
   - Variables: `source_id`, `extraction_counts` (snake_case)

3. **Error Handling (lines 65-68):**
   - Custom exceptions: `ExtractionPipelineError`
   - Include `code`, `message`, `details` dict
   - Inherit from base `KnowledgeError`

4. **Logging (lines 152-164):**
   - Use `structlog` only - NO print statements in core code
   - Print statements OK in CLI for user output
   - Always log with context: `logger.info("extraction_complete", source_id=id, count=n)`

### Anti-Patterns to Avoid

1. **Don't make external LLM API calls** - Claude Code IS the extractor (NFR3)
2. **Don't skip error handling** - Continue on individual failures, report at end
3. **Don't block on async** - Use proper async patterns for I/O
4. **Don't duplicate extractor logic** - Use `extractor_registry`
5. **Don't hardcode connection strings** - Use `pydantic_settings.BaseSettings`
6. **Don't use bare Exception** - Use specific error types
7. **Don't forget progress display** - User needs feedback during long extractions

### Architecture Compliance Checklist

- [ ] Pipeline orchestrator at `packages/pipeline/src/extraction/pipeline.py`
- [ ] CLI script at `packages/pipeline/scripts/extract.py`
- [ ] Module exports at `packages/pipeline/src/extraction/__init__.py`
- [ ] Uses `extractor_registry` from Story 3.1 for all extractors
- [ ] Uses `ExtractionStorage` from Story 3.6 for dual-store persistence
- [ ] Retrieves chunks from MongoDB via Story 1.4 client
- [ ] Stores embeddings in Qdrant via Story 1.5 client
- [ ] Implements Claude-as-extractor pattern (NFR3: zero external API costs)
- [ ] Uses structlog for all logging (architecture.md:535-542)
- [ ] Uses Pydantic Settings for configuration (architecture.md:519-533)
- [ ] Exceptions inherit from `KnowledgeError` (architecture.md:545-559)
- [ ] CLI outputs progress and summary table
- [ ] Integration tests in `tests/test_extraction/` using Docker Compose
- [ ] All tests pass: `cd packages/pipeline && uv run pytest tests/test_extraction/ -v`

### References

**Architecture Decisions:**
- [Architecture: Pipeline Structure] `_bmad-output/architecture.md:592-665`
- [Architecture: Data Flow] `_bmad-output/architecture.md:766-772`
- [Architecture: NFR3 Zero API Costs] `_bmad-output/architecture.md:308-314`
- [Architecture: Extractor Pattern] `_bmad-output/architecture.md:624-635`
- [Architecture: CLI Patterns] `_bmad-output/architecture.md:774-791`

**Requirements:**
- [PRD: FR-2.1-2.7 Knowledge Extraction] `_bmad-output/prd.md:254-262`
- [PRD: FR-2.9 Topic Tagging] `_bmad-output/prd.md:262`
- [PRD: FR-2.10 Source Attribution] `_bmad-output/prd.md:263`
- [PRD: NFR3 Zero External API Costs] `_bmad-output/prd.md:285`

**Epic Context:**
- [Epics: Story 3.7] `_bmad-output/epics.md:484-499`
- [Epics: Epic 3 Goals] `_bmad-output/epics.md:371-376`
- [Epics: Epic 4 Dependencies] `_bmad-output/epics.md:502-506` (this story enables MCP tools)

**Project Rules:**
- [Project Context: All Rules] `_bmad-output/project-context.md`
- [Project Context: Async Patterns] `_bmad-output/project-context.md:54-57`
- [Project Context: Error Handling] `_bmad-output/project-context.md:65-68`
- [Project Context: Logging] `_bmad-output/project-context.md:152-164`

**Story Dependencies:**
- [Story 2.6: End-to-End Ingestion Pipeline] - CLI pattern reference, provides ingested chunks
- [Story 3.1: Base Extractor Interface] - All models, BaseExtractor ABC, extractor_registry
- [Story 3.2-3.5: All Extractors] - DecisionExtractor, PatternExtractor, WarningExtractor, MethodologyExtractor, ChecklistExtractor, PersonaExtractor, WorkflowExtractor
- [Story 3.6: Extraction Storage and Embedding] - ExtractionStorage for dual-store persistence

**Previous Story Intelligence:**
From Story 3.6 (Extraction Storage and Embedding):
- Use `ExtractionStorage.save_extraction()` for each extraction
- Handle partial failures (MongoDB succeeds, Qdrant fails)
- Use Pydantic v2 `.model_dump(mode="json")` for serialization
- Structured logging with `structlog.get_logger()`

From Story 2.6 (End-to-End Ingestion Pipeline):
- Follow same CLI pattern with argparse
- Use Settings from pydantic-settings
- Display progress during long operations
- Return meaningful exit codes (0, 1, 2)
- Use asyncio.run() for async entry point

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

_To be filled by dev agent - list all files created/modified:_
- packages/pipeline/src/extraction/__init__.py (CREATE)
- packages/pipeline/src/extraction/pipeline.py (CREATE)
- packages/pipeline/scripts/extract.py (CREATE)
- packages/pipeline/tests/test_extraction/__init__.py (CREATE)
- packages/pipeline/tests/test_extraction/test_pipeline.py (CREATE)
- packages/pipeline/tests/test_extraction/test_integration.py (CREATE)
