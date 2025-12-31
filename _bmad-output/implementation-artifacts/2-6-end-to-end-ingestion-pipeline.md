# Story 2.6: End-to-End Ingestion Pipeline

Status: done

<!--
COURSE CORRECTION: 2025-12-30
This story was updated to reference DoclingAdapter and DoclingChunker.
See: epic-2-sprint-change-proposal.md for details.
-->

## Story

As a **builder**,
I want to run a complete ingestion pipeline via CLI script,
So that I can ingest a document, chunk it, embed it, and store everything in one command.

## Acceptance Criteria

**Given** a document path (PDF, Markdown, DOCX, HTML, or PPTX)
**When** I run `uv run scripts/ingest.py <file>`
**Then** source metadata is stored in MongoDB `sources` collection
**And** chunks are stored in MongoDB `chunks` collection with `source_id` reference
**And** chunk embeddings are stored in Qdrant `chunks` collection
**And** ingestion status is tracked (pending -> processing -> complete/failed)
**And** the script outputs a summary of chunks created

## Dependency Analysis

**Depends On:**
- **Story 2.1** (Base Source Adapter Interface) - MUST be completed
  - Requires `SourceAdapter` ABC and adapter registry
  - Requires adapter exceptions and error handling patterns
- **Story 2.2** (Docling Document Adapter) - MUST be completed
  - Requires `DoclingAdapter` registered in adapter registry
  - Provides unified ingestion for PDF, Markdown, DOCX, HTML, PPTX
  - Returns `DoclingDocument` in metadata for chunker
- ~~**Story 2.3** (Markdown Document Adapter)~~ - **ARCHIVED**
  - Merged into Story 2.2 (Docling handles Markdown natively)
- **Story 2.4** (Text Chunking Processor) - MUST be completed
  - Requires `DoclingChunker` wrapper around HybridChunker
  - Uses DoclingDocument from adapter metadata
  - Provides `ChunkOutput` models with accurate token counts
- **Story 2.5** (Local Embedding Generator) - MUST be completed
  - Requires local embedding generation using all-MiniLM-L6-v2
  - Requires batch embedding support for efficiency
  - Must satisfy NFR3 (zero external LLM API costs)
- **Story 1.4** (MongoDB Storage Client) - MUST be completed
  - Requires MongoDB client for storing sources and chunks
  - Provides storage patterns for source/chunk persistence
- **Story 1.5** (Qdrant Storage Client) - MUST be completed
  - Requires Qdrant client for vector storage
  - Provides semantic search capabilities

**Blocks:**
- **Story 3.1** (Base Extractor Interface) - Uses ingested chunks for extraction
- **Story 3.7** (Extraction Pipeline CLI) - Builds on ingestion pipeline pattern

## Tasks / Subtasks

- [x] **Task 1: Create Ingestion Pipeline Orchestrator** (AC: All)
  - [x] Create `packages/pipeline/src/ingestion/` module
  - [x] Create `packages/pipeline/src/ingestion/pipeline.py`
  - [x] Implement `IngestionPipeline` class that coordinates all steps
  - [x] Define pipeline stages: validate → extract → chunk → embed → store
  - [x] Implement status tracking (pending, processing, complete, failed)
  - [x] Add progress logging for each stage

- [x] **Task 2: Implement Pipeline Status Tracking** (AC: Status tracking)
  - [x] Create `IngestionStatus` enum (pending, processing, complete, failed)
  - [x] Track current stage in pipeline
  - [x] Log stage transitions with structlog
  - [x] Store status in MongoDB `sources` collection
  - [x] Handle partial failures (e.g., some chunks fail embedding)

- [x] **Task 3: Integrate Adapter Selection** (AC: Multi-format support)
  - [x] Use `adapter_registry.get_adapter(file_path)` from Story 2.1
  - [x] DoclingAdapter handles all formats: .pdf, .md, .docx, .html, .pptx
  - [x] Raise `UnsupportedFileError` for unsupported types
  - [x] Log adapter selection: `logger.info("adapter_selected", adapter="DoclingAdapter")`

- [x] **Task 4: Integrate Chunking Processor** (AC: Chunks stored)
  - [x] Import `DoclingChunker` from Story 2.4
  - [x] Extract `DoclingDocument` from adapter result metadata
  - [x] Pass DoclingDocument to `DoclingChunker.chunk_document()`
  - [x] Receive list of `ChunkOutput` with accurate token counts
  - [x] Log chunk statistics: `logger.info("chunking_complete", chunk_count=len(chunks))`

- [x] **Task 5: Integrate Embedding Generator** (AC: Embeddings stored)
  - [x] Import embedder from Story 2.5
  - [x] Generate embeddings for all chunks (batch mode for efficiency)
  - [x] Validate embedding dimensions (384d)
  - [x] Handle embedding failures gracefully
  - [x] Log embedding performance: `logger.info("embedding_complete", duration=elapsed)`

- [x] **Task 6: Implement Storage Orchestration** (AC: MongoDB + Qdrant)
  - [x] Store source metadata in MongoDB `sources` collection
  - [x] Store chunks in MongoDB `chunks` collection with `source_id` reference
  - [x] Store chunk embeddings in Qdrant `chunks` collection
  - [x] Use MongoDB bulk operations for efficiency
  - [x] Handle storage failures with source status update to "failed"
  - [x] Log storage results: `logger.info("storage_complete", source_id=source.id)`

- [x] **Task 7: Create CLI Script** (AC: `uv run scripts/ingest.py <file>`)
  - [x] Create `packages/pipeline/scripts/ingest.py`
  - [x] Use argparse for command-line argument parsing
  - [x] Accept file path as required argument
  - [x] Add optional arguments: `--chunk-size`, `--dry-run`, `--verbose`
  - [x] Initialize pipeline with PipelineConfig
  - [x] Call `IngestionPipeline.ingest(file_path)`
  - [x] Display progress and summary to stdout

- [x] **Task 8: Implement Summary Output** (AC: Summary of chunks)
  - [x] Display ingestion summary after completion
  - [x] Include: source title, file type, chunk count, total tokens
  - [x] Include: processing time, embedding time, storage time
  - [x] Include: source_id for reference in extraction workflows
  - [x] Format output for readability (structured text with separator lines)

- [x] **Task 9: Add Error Handling and Recovery** (AC: Status failed)
  - [x] Wrap pipeline execution in try/except
  - [x] Catch adapter errors, chunking errors, embedding errors, storage errors
  - [x] Update source status to "failed" with error details
  - [x] Log full error context with structlog
  - [x] Return meaningful error messages to user
  - [x] Preserve partial progress where possible

- [x] **Task 10: Create Integration Tests** (AC: All)
  - [x] Create `packages/pipeline/tests/test_ingestion/test_pipeline.py`
  - [x] Test end-to-end pipeline with sample Markdown (dry run)
  - [x] Test error handling (unsupported file, file not found)
  - [x] Test status transitions (pending → processing → complete)
  - [x] Integration tests marked with @pytest.mark.integration for Docker services

## Dev Notes

### Pipeline Architecture

**From Architecture Document (architecture.md:592-665):**

This story implements the **complete ingestion pipeline** that ties together all Epic 2 components:

```
Source File → Adapter → Chunker → Embedder → Storage (MongoDB + Qdrant)
```

**Data Flow:**
```
1. Validate: Check file exists, get adapter, verify format
2. Extract: Use adapter.extract_text() to get raw text + metadata
3. Chunk: Use chunker to split text into semantic chunks
4. Embed: Use embedder to generate 384d vectors for each chunk
5. Store: Save source metadata (MongoDB), chunks (MongoDB), vectors (Qdrant)
6. Track: Update source status throughout pipeline stages
```

### Architecture-Specified Directory Structure

**From Architecture Document (architecture.md:605-660):**

```
packages/pipeline/
├── src/
│   ├── ingestion/              # NEW: Pipeline orchestration
│   │   ├── __init__.py
│   │   └── pipeline.py         # IngestionPipeline class
│   ├── adapters/               # From Stories 2.1-2.3
│   ├── processors/             # From Story 2.4
│   ├── embeddings/             # From Story 2.5
│   ├── storage/                # From Stories 1.4-1.5
│   └── models/                 # Shared Pydantic models
├── scripts/
│   └── ingest.py               # NEW: CLI entry point
└── tests/
    └── test_ingestion/         # NEW: Integration tests
        └── test_pipeline.py
```

### Implementation Pattern

**Pipeline Orchestrator Example:**

```python
# packages/pipeline/src/ingestion/pipeline.py
from pathlib import Path
from typing import Optional
import structlog

from src.adapters import adapter_registry
from src.processors.chunker import Chunker
from src.embeddings.local_embedder import LocalEmbedder
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantClient
from src.models.source import Source, IngestionStatus
from src.models.chunk import Chunk
from src.config import Settings
from src.exceptions import KnowledgeError, IngestionError

logger = structlog.get_logger()


class IngestionError(KnowledgeError):
    """Base exception for ingestion pipeline errors."""
    pass


class IngestionPipeline:
    """Orchestrates the complete document ingestion pipeline.

    Stages:
    1. Validate file and select adapter
    2. Extract text and metadata
    3. Chunk text into semantic units
    4. Generate embeddings for chunks
    5. Store source, chunks, and vectors
    6. Track status throughout

    Example:
        pipeline = IngestionPipeline(settings)
        result = await pipeline.ingest(Path("book.pdf"))
        print(f"Ingested {result.chunk_count} chunks")
    """

    def __init__(self, settings: Settings):
        """Initialize pipeline with configuration."""
        self.settings = settings
        self.chunker = Chunker(settings.chunk_size)
        self.embedder = LocalEmbedder(settings.embedding_model)
        self.mongodb = MongoDBClient(settings.mongodb_uri)
        self.qdrant = QdrantClient(settings.qdrant_url)

        logger.info(
            "pipeline_initialized",
            chunk_size=settings.chunk_size,
            embedding_model=settings.embedding_model
        )

    async def ingest(self, file_path: Path) -> IngestionResult:
        """Run complete ingestion pipeline for a document.

        Args:
            file_path: Path to document to ingest.

        Returns:
            IngestionResult with summary statistics.

        Raises:
            IngestionError: If any pipeline stage fails.
            UnsupportedFileError: If file type not supported.
        """
        import time
        start_time = time.time()

        # Create source record with pending status
        source = Source(
            title=file_path.name,
            path=str(file_path),
            type=self._detect_type(file_path),
            status=IngestionStatus.PENDING
        )
        source_id = await self.mongodb.create_source(source)

        try:
            # Stage 1: Validate and select adapter
            logger.info("stage_started", stage="validate", file=str(file_path))
            adapter = adapter_registry.get_adapter(file_path)

            # Stage 2: Extract text and metadata
            logger.info("stage_started", stage="extract", adapter=adapter.__class__.__name__)
            await self.mongodb.update_source_status(source_id, IngestionStatus.PROCESSING)

            result = adapter.extract_text(file_path)
            metadata = adapter.get_metadata(file_path)

            # Update source with extracted metadata
            await self.mongodb.update_source(source_id, {
                "title": metadata.get("title", source.title),
                "authors": metadata.get("authors", []),
                "metadata": metadata
            })

            # Stage 3: Chunk text
            logger.info("stage_started", stage="chunk", text_length=len(result.text))
            chunks = self.chunker.chunk_text(result.text, source_id)
            logger.info("chunking_complete", chunk_count=len(chunks))

            # Stage 4: Generate embeddings
            logger.info("stage_started", stage="embed", chunk_count=len(chunks))
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = self.embedder.embed_batch(chunk_texts)
            logger.info("embedding_complete", embedding_count=len(embeddings))

            # Validate embedding dimensions
            if embeddings and len(embeddings[0]) != 384:
                raise IngestionError(
                    code="INVALID_EMBEDDING_DIMENSION",
                    message=f"Expected 384d embeddings, got {len(embeddings[0])}d",
                    details={"expected": 384, "actual": len(embeddings[0])}
                )

            # Stage 5: Store everything
            logger.info("stage_started", stage="store")

            # Store chunks in MongoDB
            chunk_ids = await self.mongodb.create_chunks(chunks)

            # Store embeddings in Qdrant with chunk metadata
            await self.qdrant.upsert_vectors(
                collection="chunks",
                ids=chunk_ids,
                vectors=embeddings,
                payloads=[{
                    "source_id": source_id,
                    "chunk_id": chunk_id,
                    "position": chunk.position
                } for chunk_id, chunk in zip(chunk_ids, chunks)]
            )

            # Mark source as complete
            await self.mongodb.update_source_status(source_id, IngestionStatus.COMPLETE)

            elapsed = time.time() - start_time
            logger.info(
                "ingestion_complete",
                source_id=source_id,
                chunk_count=len(chunks),
                duration=f"{elapsed:.2f}s"
            )

            return IngestionResult(
                source_id=source_id,
                title=metadata.get("title", file_path.name),
                chunk_count=len(chunks),
                total_tokens=sum(chunk.token_count for chunk in chunks),
                duration=elapsed
            )

        except Exception as e:
            # Mark source as failed
            await self.mongodb.update_source_status(
                source_id,
                IngestionStatus.FAILED,
                error_details={"error": str(e), "type": type(e).__name__}
            )

            logger.error(
                "ingestion_failed",
                source_id=source_id,
                file=str(file_path),
                error=str(e),
                error_type=type(e).__name__
            )

            raise IngestionError(
                code="INGESTION_FAILED",
                message=f"Pipeline failed: {str(e)}",
                details={"source_id": source_id, "file": str(file_path)}
            ) from e

    def _detect_type(self, file_path: Path) -> str:
        """Detect document type from extension."""
        ext = file_path.suffix.lower()
        type_map = {
            ".pdf": "book",
            ".md": "documentation",
            ".markdown": "documentation"
        }
        return type_map.get(ext, "unknown")


class IngestionResult:
    """Result summary from ingestion pipeline."""
    def __init__(
        self,
        source_id: str,
        title: str,
        chunk_count: int,
        total_tokens: int,
        duration: float
    ):
        self.source_id = source_id
        self.title = title
        self.chunk_count = chunk_count
        self.total_tokens = total_tokens
        self.duration = duration
```

### CLI Script Pattern

**From Architecture Document (architecture.md:774-791):**

```python
# packages/pipeline/scripts/ingest.py
"""CLI script for ingesting documents into the knowledge pipeline.

Usage:
    uv run scripts/ingest.py <file>
    uv run scripts/ingest.py <file> --chunk-size 512
    uv run scripts/ingest.py <file> --dry-run

Examples:
    uv run scripts/ingest.py data/raw/llm-handbook.pdf
    uv run scripts/ingest.py docs/architecture.md --verbose
"""
import sys
import asyncio
import argparse
from pathlib import Path
import structlog

from src.config import Settings
from src.ingestion.pipeline import IngestionPipeline, IngestionError
from src.adapters import UnsupportedFileError

logger = structlog.get_logger()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into knowledge pipeline",
        epilog="Example: uv run scripts/ingest.py data/raw/book.pdf"
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to document file (PDF or Markdown)"
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Override default chunk size"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate file without ingesting"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG)
        )

    # Load settings
    settings = Settings()
    if args.chunk_size:
        settings.chunk_size = args.chunk_size

    # Validate file exists
    if not args.file.exists():
        print(f"❌ Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Dry run mode
    if args.dry_run:
        print(f"✓ File exists: {args.file}")
        print(f"✓ File type: {args.file.suffix}")
        print(f"✓ Chunk size: {settings.chunk_size}")
        print("Dry run complete (no ingestion performed)")
        return

    # Run pipeline
    print(f"📄 Ingesting: {args.file.name}")
    print(f"📊 Chunk size: {settings.chunk_size}")
    print()

    try:
        pipeline = IngestionPipeline(settings)
        result = asyncio.run(pipeline.ingest(args.file))

        # Display summary
        print("✅ Ingestion Complete!")
        print()
        print(f"  Source ID:    {result.source_id}")
        print(f"  Title:        {result.title}")
        print(f"  Chunks:       {result.chunk_count}")
        print(f"  Total Tokens: {result.total_tokens:,}")
        print(f"  Duration:     {result.duration:.2f}s")
        print()
        print(f"Next step: Run extraction with: uv run scripts/extract.py {result.source_id}")

    except UnsupportedFileError as e:
        print(f"❌ Error: {e.message}", file=sys.stderr)
        print(f"Supported extensions: {', '.join(e.details['supported'])}", file=sys.stderr)
        sys.exit(1)

    except IngestionError as e:
        print(f"❌ Error: {e.message}", file=sys.stderr)
        logger.error("ingestion_failed", error=str(e), details=e.details)
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

### Ingestion Status Enum

**MongoDB Source Status Tracking:**

```python
# packages/pipeline/src/models/source.py
from enum import Enum

class IngestionStatus(str, Enum):
    """Status of document ingestion pipeline."""
    PENDING = "pending"          # Created but not started
    PROCESSING = "processing"    # Currently ingesting
    COMPLETE = "complete"        # Successfully ingested
    FAILED = "failed"            # Ingestion failed
```

### Storage Orchestration Pattern

**Transaction Pattern for Atomicity:**

```python
# Use MongoDB transactions for atomicity
async with await self.mongodb.client.start_session() as session:
    async with session.start_transaction():
        # Store source
        source_id = await self.mongodb.create_source(source, session=session)

        # Store chunks with source_id reference
        chunk_ids = await self.mongodb.create_chunks(chunks, session=session)

        # If anything fails, transaction rolls back automatically
```

**Qdrant Storage with Metadata:**

```python
# Store chunk embeddings with payload for filtering
await self.qdrant.upsert_vectors(
    collection="chunks",
    ids=chunk_ids,
    vectors=embeddings,
    payloads=[{
        "source_id": source_id,
        "chunk_id": chunk_id,
        "type": "chunk",
        "position": chunk.position  # {chapter, section, page}
    } for chunk_id, chunk in zip(chunk_ids, chunks)]
)
```

### Integration Testing Pattern

**Docker Compose Integration:**

```python
# packages/pipeline/tests/test_ingestion/test_pipeline.py
import pytest
import asyncio
from pathlib import Path

from src.ingestion.pipeline import IngestionPipeline
from src.config import Settings


@pytest.mark.asyncio
class TestIngestionPipeline:
    """Integration tests for end-to-end ingestion pipeline."""

    @pytest.fixture
    async def pipeline(self):
        """Create pipeline with test settings."""
        settings = Settings(
            mongodb_uri="mongodb://localhost:27017/test_db",
            qdrant_url="http://localhost:6333"
        )
        pipeline = IngestionPipeline(settings)
        yield pipeline
        # Cleanup: drop test database after tests
        await pipeline.mongodb.drop_database()

    @pytest.fixture
    def sample_pdf(self, tmp_path):
        """Create sample PDF for testing."""
        # Use pytest-pdf or copy fixture file
        return Path("tests/fixtures/sample.pdf")

    @pytest.fixture
    def sample_markdown(self, tmp_path):
        """Create sample Markdown for testing."""
        md_file = tmp_path / "test.md"
        md_file.write_text("""# Test Document

This is a test document with multiple paragraphs.

## Section 1

Content for section 1.

## Section 2

Content for section 2.
""")
        return md_file

    async def test_ingest_pdf_end_to_end(self, pipeline, sample_pdf):
        """Test complete pipeline with PDF input."""
        result = await pipeline.ingest(sample_pdf)

        # Verify result
        assert result.source_id is not None
        assert result.chunk_count > 0
        assert result.total_tokens > 0
        assert result.duration > 0

        # Verify MongoDB storage
        source = await pipeline.mongodb.get_source(result.source_id)
        assert source.status == IngestionStatus.COMPLETE
        assert source.type == "book"

        chunks = await pipeline.mongodb.get_chunks_by_source(result.source_id)
        assert len(chunks) == result.chunk_count
        assert all(chunk.source_id == result.source_id for chunk in chunks)

        # Verify Qdrant storage
        vectors = await pipeline.qdrant.get_vectors("chunks", limit=100)
        assert len(vectors) >= result.chunk_count

    async def test_ingest_markdown_end_to_end(self, pipeline, sample_markdown):
        """Test complete pipeline with Markdown input."""
        result = await pipeline.ingest(sample_markdown)

        assert result.chunk_count > 0

        # Verify source metadata
        source = await pipeline.mongodb.get_source(result.source_id)
        assert source.title == "Test Document"  # From H1
        assert source.type == "documentation"
        assert source.status == IngestionStatus.COMPLETE

    async def test_ingest_unsupported_file_raises(self, pipeline, tmp_path):
        """Test that unsupported file types raise error."""
        unsupported = tmp_path / "file.xyz"
        unsupported.touch()

        with pytest.raises(UnsupportedFileError) as exc_info:
            await pipeline.ingest(unsupported)

        assert exc_info.value.code == "UNSUPPORTED_FILE"

    async def test_ingest_status_tracking(self, pipeline, sample_markdown):
        """Test that status is tracked through pipeline stages."""
        # Monitor status changes
        statuses = []

        async def track_status(source_id):
            """Poll source status during ingestion."""
            for _ in range(10):
                source = await pipeline.mongodb.get_source(source_id)
                statuses.append(source.status)
                await asyncio.sleep(0.1)

        # Run ingestion with concurrent status tracking
        result = await pipeline.ingest(sample_markdown)

        # Verify final status
        source = await pipeline.mongodb.get_source(result.source_id)
        assert source.status == IngestionStatus.COMPLETE

        # Should have transitioned through: pending -> processing -> complete
        # (exact timing depends on execution speed)

    async def test_ingest_failure_marks_failed(self, pipeline, tmp_path):
        """Test that pipeline failures mark source as failed."""
        # Create corrupted PDF
        corrupted = tmp_path / "corrupted.pdf"
        corrupted.write_bytes(b"Not a real PDF")

        with pytest.raises(IngestionError):
            await pipeline.ingest(corrupted)

        # Status should be marked as failed
        # (Would need to track source_id even on failure)
```

### Python Naming Conventions

**From Architecture Document (architecture.md:418-432) and project-context.md:**

| Element | Convention | Example |
|---------|------------|---------|
| Files/modules | `snake_case.py` | `pipeline.py`, `ingest.py` |
| Classes | `PascalCase` | `IngestionPipeline`, `IngestionResult` |
| Functions | `snake_case` | `ingest()`, `_detect_type()` |
| Variables | `snake_case` | `source_id`, `chunk_count` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_BATCH_SIZE` |

### Error Handling Pattern

**From Architecture Document (architecture.md:545-559):**

All exceptions must:
1. Inherit from `KnowledgeError` base class
2. Include `code`, `message`, `details` fields
3. Follow structured error format
4. Be logged with full context using structlog

**Example:**

```python
class IngestionError(KnowledgeError):
    """Raised when ingestion pipeline fails."""
    pass
```

### Logging Pattern

**From Architecture Document (architecture.md:535-542) and project-context.md:**

```python
import structlog
logger = structlog.get_logger()

# Good: structured with context
logger.info("stage_started", stage="chunk", text_length=10000)
logger.info("ingestion_complete", source_id="abc123", chunk_count=42)
logger.error("ingestion_failed", source_id="abc123", error=str(e))
```

**CRITICAL:** Use structlog, no print statements (except in CLI display output).

### Configuration Pattern

**From Architecture Document (architecture.md:519-533):**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    qdrant_url: str = "http://localhost:6333"
    chunk_size: int = 512
    embedding_model: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"

settings = Settings()
```

### NFR Compliance

**NFR2: Batch Efficiency** (architecture.md:301-306)
- Single-session ingestion: Complete 800-page book in one run
- This story implements the batch pipeline that satisfies this requirement

**NFR3: Cost** (architecture.md:308-314)
- Zero external LLM API costs at query time
- Uses local embeddings from Story 2.5 (sentence-transformers)
- No API calls to OpenAI, Anthropic, or other embedding services

**NFR5: Extensibility** (architecture.md:324-331)
- Uses adapter registry from Story 2.1
- Easy to add new file types without modifying pipeline

### Previous Story Intelligence

**Story 2.1: Base Source Adapter Interface**
- Provides `adapter_registry` for file type detection
- Defines `UnsupportedFileError` exception
- Establishes adapter pattern for extensibility

**Story 2.2: PDF Document Adapter**
- `PdfAdapter` should be registered in adapter registry
- Provides PDF text extraction and metadata

**Story 2.3: Markdown Document Adapter**
- `MarkdownAdapter` should be registered in adapter registry
- Provides Markdown text extraction with structure

**Story 2.4: Text Chunking Processor**
- Provides `Chunker` class with configurable chunk size
- Returns list of `Chunk` objects with position metadata
- Preserves sentence boundaries

**Story 2.5: Local Embedding Generator**
- Provides `LocalEmbedder` class using all-MiniLM-L6-v2
- Generates 384d embeddings
- Supports batch mode for efficiency
- Zero external API costs (NFR3)

**Story 1.4: MongoDB Storage Client**
- Provides `MongoDBClient` for sources and chunks collections
- Supports transactions for atomicity
- Provides status update methods

**Story 1.5: Qdrant Storage Client**
- Provides `QdrantClient` for vector storage
- Supports upsert with payloads
- 384d vectors, Cosine distance metric

### Architecture Compliance Checklist

- [x] Pipeline orchestrator in `packages/pipeline/src/ingestion/pipeline.py`
- [x] CLI script in `packages/pipeline/scripts/ingest.py`
- [x] Uses adapter registry from Story 2.1 for file type detection
- [x] Uses chunker from Story 2.4 for text processing
- [x] Uses embedder from Story 2.5 for vector generation (NFR3)
- [x] Stores in MongoDB (sources, chunks) from Story 1.4
- [x] Stores in Qdrant (chunk vectors) from Story 1.5
- [x] Tracks status: pending → processing → complete/failed
- [x] Uses structlog for all logging (architecture.md:535-542)
- [x] Uses Pydantic for configuration (see design note below about PipelineConfig)
- [x] Exceptions inherit from `KnowledgeError` (architecture.md:545-559)
- [x] Integration tests in `tests/test_ingestion/` using Docker Compose
- [x] CLI outputs summary with chunk count, tokens, duration

**Design Note - PipelineConfig:** `PipelineConfig` uses `pydantic.BaseModel` instead of `pydantic_settings.BaseSettings` by design. This is a CLI-specific config that receives values from argparse, not environment variables. The main `Settings` class in `src/config.py` correctly uses `BaseSettings` for env var loading.

### References

- [Source: epics.md#Story-2.6] - Story acceptance criteria (lines 353-368)
- [Source: architecture.md#Project-Structure-&-Boundaries] - File locations (lines 592-665)
- [Source: architecture.md#NFR2-Batch-Efficiency] - Single-session requirement (lines 301-306)
- [Source: architecture.md#NFR3-Cost] - Zero API costs (lines 308-314)
- [Source: architecture.md#Implementation-Patterns] - Logging, config patterns (lines 519-560)
- [Source: project-context.md#Critical-Implementation-Rules] - Naming, async, errors
- [Source: prd.md#FR-1.4-FR-1.5] - Ingestion status tracking, source metadata (lines 245-248)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A - No significant debugging issues encountered.

### Completion Notes List

1. **Implementation Approach**: Implemented synchronous pipeline (not async) because:
   - pymongo is not async-native (as noted in mongodb.py)
   - sentence-transformers is synchronous
   - Docling library is synchronous
   - Simpler implementation for batch processing use case

2. **Source Type Detection**: Changed `_detect_type()` to return valid values (`book`, `paper`) instead of `documentation` since the `Source` model only accepts `book`, `paper`, or `case_study` literals.

3. **MongoDB Transactions**: Did not implement transactions (as originally specified) because:
   - pymongo transactions require replica sets
   - Instead, implemented failure handling that marks source as "failed" if any stage fails
   - Source is created first, then updated with status throughout pipeline

4. **Test Coverage**: 20 unit tests passing, 3 integration tests (require Docker) marked as skipped. The `@pytest.mark.integration` marker is registered in `pyproject.toml` to avoid warnings:
   - TestPipelineConfig: 4 tests
   - TestPipelineInitialization: 3 tests
   - TestDryRun: 2 tests
   - TestErrorHandling: 3 tests
   - TestStatusTracking: 2 tests
   - TestIngestionResult: 1 test
   - TestExceptions: 5 tests
   - TestIntegration: 3 tests (skipped, require Docker)

5. **CLI Design**: CLI script uses `--dry-run` mode for validation without database storage. This is useful for testing the pipeline stages without requiring MongoDB/Qdrant.

6. **Architecture Compliance**:
   - Uses adapter_registry from Story 2.1
   - Uses DoclingChunker from Story 2.4
   - Uses LocalEmbedder (get_embedder) from Story 2.5
   - Uses MongoDBClient from Story 1.4
   - Uses QdrantStorageClient from Story 1.5
   - All logging uses structlog
   - All exceptions inherit from KnowledgeError

### File List

_Files created:_
- packages/pipeline/src/ingestion/__init__.py (CREATE)
- packages/pipeline/src/ingestion/pipeline.py (CREATE)
- packages/pipeline/scripts/ingest.py (CREATE)
- packages/pipeline/tests/test_ingestion/__init__.py (CREATE)
- packages/pipeline/tests/test_ingestion/test_pipeline.py (CREATE)
- packages/pipeline/.env.example (CREATE) - Environment template for local development

_Files modified (code review fixes):_
- packages/pipeline/pyproject.toml (MODIFY) - Added pytest `integration` marker registration
