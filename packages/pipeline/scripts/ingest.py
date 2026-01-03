#!/usr/bin/env python3
"""CLI script for ingesting documents into the knowledge pipeline.

Usage:
    uv run scripts/ingest.py <file>
    uv run scripts/ingest.py <file> --chunk-size 512
    uv run scripts/ingest.py <file> --dry-run
    uv run scripts/ingest.py <file> --verbose

Examples:
    # Basic ingestion
    uv run scripts/ingest.py data/raw/llm-handbook.pdf
    uv run scripts/ingest.py docs/architecture.md --verbose
    uv run scripts/ingest.py book.pdf --chunk-size 256 --dry-run

    # With source metadata (v1.1 schema)
    uv run scripts/ingest.py book.pdf --category foundational --year 2024
    uv run scripts/ingest.py paper.pdf --tags "rag,embeddings" --year 2024
    uv run scripts/ingest.py case.md --category case_study --tags "production,scale"

Source Metadata Options:
    --project        Project ID for namespacing (overrides PROJECT_ID env var)
    --category       Source category: foundational, advanced, reference, case_study
    --tags           Comma-separated tags for filtering (e.g., "rag,embeddings,production")
    --year           Publication year (e.g., 2024)

Project Namespacing:
    Use the PROJECT_ID environment variable or --project flag to store data in
    project-specific collections. This allows multiple knowledge bases to coexist
    without data mixing.

    Examples:
        # Using CLI flag (highest priority)
        uv run scripts/ingest.py book.pdf --project ai_engineering

        # Using environment variable
        PROJECT_ID=ai_engineering uv run scripts/ingest.py book.pdf

        # Session-wide project selection
        export PROJECT_ID=ai_engineering
        uv run scripts/ingest.py book1.pdf
        uv run scripts/ingest.py book2.pdf

        # Default project (when PROJECT_ID not set)
        uv run scripts/ingest.py book.pdf  # Uses "default" project

    Storage architecture:
        - MongoDB: {project_id}_sources, {project_id}_chunks, {project_id}_extractions
        - Qdrant: Single 'knowledge_vectors' collection with project_id payload filtering
"""

import argparse
import logging
import sys
from pathlib import Path

import structlog

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.adapters import UnsupportedFileError
from src.ingestion.pipeline import (
    IngestionPipeline,
    IngestionError,
    PipelineConfig,
)


def configure_logging(verbose: bool) -> None:
    """Configure structlog for CLI output.

    Args:
        verbose: If True, enable DEBUG level logging.
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )


def format_summary(result) -> str:
    """Format ingestion result as a summary string.

    Args:
        result: IngestionResult from pipeline.

    Returns:
        Formatted summary string.
    """
    lines = [
        "",
        "=" * 60,
        "INGESTION SUMMARY",
        "=" * 60,
        "",
        f"  Source ID:        {result.source_id}",
        f"  Title:            {result.title}",
        f"  File Type:        {result.file_type}",
        "",
        f"  Chunks Created:   {result.chunk_count}",
        f"  Total Tokens:     {result.total_tokens:,}",
        "",
        "  Timing:",
        f"    Processing:     {result.processing_time:.2f}s",
        f"    Embedding:      {result.embedding_time:.2f}s",
        f"    Storage:        {result.storage_time:.2f}s",
        f"    Total:          {result.duration:.2f}s",
        "",
        "=" * 60,
    ]
    return "\n".join(lines)


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = argparse.ArgumentParser(
        description="Ingest documents into the knowledge pipeline",
        epilog="Example: uv run scripts/ingest.py data/raw/book.pdf",
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to document file (PDF, Markdown, DOCX, HTML, or PPTX)",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Target chunk size in tokens (default: 512)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and process file without storing to databases",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    # Source metadata flags (v1.1 schema)
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project ID for namespacing (overrides PROJECT_ID env var)",
    )

    parser.add_argument(
        "--category",
        type=str,
        choices=["foundational", "advanced", "reference", "case_study"],
        default=None,
        help="Source category (default: foundational)",
    )

    parser.add_argument(
        "--tags",
        type=str,
        default=None,
        help="Comma-separated tags for filtering (e.g., 'rag,embeddings,production')",
    )

    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Publication year (e.g., 2024)",
    )

    args = parser.parse_args()

    # Configure logging
    configure_logging(args.verbose)

    # Validate file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    if not args.file.is_file():
        print(f"Error: Not a file: {args.file}", file=sys.stderr)
        return 1

    # Parse tags from comma-separated string
    tags_list = []
    if args.tags:
        tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    # Display startup info
    print(f"Ingesting: {args.file.name}")
    print(f"Chunk size: {args.chunk_size} tokens")
    if args.project:
        print(f"Project: {args.project}")
    if args.category:
        print(f"Category: {args.category}")
    if tags_list:
        print(f"Tags: {', '.join(tags_list)}")
    if args.year:
        print(f"Year: {args.year}")
    if args.dry_run:
        print("Mode: DRY RUN (no database storage)")
    print()

    # Create pipeline config
    config = PipelineConfig(
        chunk_size=args.chunk_size,
        dry_run=args.dry_run,
        verbose=args.verbose,
        # v1.1 metadata fields
        project_id=args.project,
        category=args.category,
        tags=tags_list,
        year=args.year,
    )

    try:
        # Run pipeline
        with IngestionPipeline(config) as pipeline:
            result = pipeline.ingest(args.file)

        # Display summary
        print(format_summary(result))

        if not args.dry_run:
            print()
            print("Next step: Run extraction with:")
            print(f"  uv run scripts/extract.py {result.source_id}")

        return 0

    except UnsupportedFileError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        if e.details.get("supported"):
            print(
                f"Supported extensions: {', '.join(e.details['supported'])}",
                file=sys.stderr,
            )
        return 1

    except IngestionError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        if args.verbose and e.details:
            print(f"Details: {e.details}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
