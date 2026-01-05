#!/usr/bin/env python3
"""CLI script for extracting knowledge from ingested documents.

Usage:
    uv run scripts/extract.py <source_id>
    uv run scripts/extract.py <source_id> --hierarchical
    uv run scripts/extract.py <source_id> --extractors decision,pattern
    uv run scripts/extract.py <source_id> --dry-run
    uv run scripts/extract.py <source_id> --verbose
    uv run scripts/extract.py <source_id> --quiet

Examples:
    uv run scripts/extract.py 507f1f77bcf86cd799439011
    uv run scripts/extract.py abc123 --hierarchical --verbose
    uv run scripts/extract.py abc123 --extractors decision,warning --verbose
    uv run scripts/extract.py abc123 --dry-run

Extraction Modes:
    --hierarchical   Use hierarchical extraction (recommended for books/papers)
                     Combines chunks by chapter/section before extraction:
                     - CHAPTER level (8K tokens): methodology, workflow
                     - SECTION level (4K tokens): decision, pattern, checklist, persona
                     - CHUNK level (512 tokens): warning
    (default)        Flat extraction - process each chunk independently

Claude-as-Extractor Pattern:
    This script implements NFR3 (zero external API costs) by using Claude Code
    as the extraction engine. When you run this script, Claude analyzes each
    chunk using the extraction prompts defined in the extractors. No external
    LLM API calls are made - Claude Code itself is the extractor.
"""

import argparse
import logging
import sys
from pathlib import Path

import structlog

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.exceptions import NotFoundError, ValidationError
from src.extraction.pipeline import (
    ExtractionPipeline,
    ExtractionPipelineError,
)
from src.extractors import ExtractionType


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


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error, 2 for partial failure).
    """
    parser = argparse.ArgumentParser(
        description="Extract knowledge from ingested documents",
        epilog="Example: uv run scripts/extract.py 507f1f77bcf86cd799439011",
    )

    parser.add_argument(
        "source_id",
        type=str,
        help="MongoDB source document ID (from ingestion)",
    )

    parser.add_argument(
        "--extractors",
        type=parse_extractor_types,
        default=None,
        help="Comma-separated extractor types (e.g., decision,pattern,warning)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate source without running extraction",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output",
    )

    parser.add_argument(
        "--hierarchical",
        action="store_true",
        help="Use hierarchical extraction (combines chunks by chapter/section)",
    )

    args = parser.parse_args()

    # Configure logging
    configure_logging(args.verbose)

    # Create pipeline
    try:
        with ExtractionPipeline() as pipeline:
            # Dry run mode
            if args.dry_run:
                try:
                    result = pipeline.dry_run(args.source_id)
                    print("✓ Dry run validation passed")
                    print(f"  Source: {result['source_title']}")
                    print(f"  Chunks: {result['chunk_count']}")
                    print(f"  Extractors: {result['extractor_count']}")
                    print(f"  Types: {', '.join(result['extractor_types'])}")
                    print()
                    print("Dry run complete (no extraction performed)")
                    return 0
                except NotFoundError:
                    print(f"❌ Source not found: {args.source_id}", file=sys.stderr)
                    return 1
                except ValidationError as e:
                    print(f"❌ Validation error: {e.message}", file=sys.stderr)
                    return 1

            # Run extraction (hierarchical or flat)
            if args.hierarchical:
                result = pipeline.extract_hierarchical(
                    source_id=args.source_id,
                    extractor_types=args.extractors,
                    quiet=args.quiet,
                )
            else:
                result = pipeline.extract(
                    source_id=args.source_id,
                    extractor_types=args.extractors,
                    quiet=args.quiet,
                )

            # Display summary
            if not args.quiet:
                print()
                mode = "Hierarchical" if args.hierarchical else "Flat"
                print(f"✅ {mode} Extraction Complete!")
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
                return 2  # Partial failure

            return 0

    except NotFoundError:
        print(f"❌ Source not found: {args.source_id}", file=sys.stderr)
        return 1

    except ValidationError as e:
        print(f"❌ Validation error: {e.message}", file=sys.stderr)
        if args.verbose and e.details:
            print(f"Details: {e.details}", file=sys.stderr)
        return 1

    except ExtractionPipelineError as e:
        print(f"❌ Extraction failed: {e.message}", file=sys.stderr)
        if args.verbose and e.details:
            print(f"Details: {e.details}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
