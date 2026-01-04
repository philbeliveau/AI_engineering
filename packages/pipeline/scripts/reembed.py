#!/usr/bin/env python3
"""Re-embed all chunks with nomic-embed-text-v1.5.

This script migrates from all-MiniLM-L6-v2 (384d) to nomic-embed-text-v1.5 (768d).
It recreates the Qdrant collection with the new vector size and re-embeds all
chunks from MongoDB.

Usage:
    uv run scripts/reembed.py
    uv run scripts/reembed.py --batch-size 50
    uv run scripts/reembed.py --dry-run
    uv run scripts/reembed.py --verbose

Options:
    --batch-size    Number of chunks to process per batch (default: 100)
    --dry-run       Preview what would be done without modifying data
    --verbose       Enable verbose logging
    --project       Project ID for namespacing (overrides PROJECT_ID env var)

Warning:
    This operation is DESTRUCTIVE for the Qdrant collection.
    The old collection will be deleted and recreated with 768d vectors.
    MongoDB data is NOT modified.
"""

import argparse
import logging
import sys
from pathlib import Path

import structlog
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config import EMBEDDING_CONFIG, KNOWLEDGE_VECTORS_COLLECTION, settings
from src.processors.embedder import NomicEmbedder
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient, VECTOR_SIZE


def configure_logging(verbose: bool) -> None:
    """Configure structlog for CLI output."""
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


def count_all_chunks(mongo: MongoDBClient) -> int:
    """Count total chunks across all sources."""
    if mongo._db is None:
        raise RuntimeError("MongoDB not connected")
    return mongo._db[settings.chunks_collection].count_documents({})


def get_all_chunks_cursor(mongo: MongoDBClient, batch_size: int):
    """Get cursor for all chunks with batching."""
    if mongo._db is None:
        raise RuntimeError("MongoDB not connected")
    return mongo._db[settings.chunks_collection].find({}).batch_size(batch_size)


def recreate_qdrant_collection(qdrant: QdrantStorageClient, dry_run: bool) -> None:
    """Delete and recreate Qdrant collection with new vector size."""
    logger = structlog.get_logger()

    collection_name = KNOWLEDGE_VECTORS_COLLECTION

    if dry_run:
        logger.info(
            "dry_run_would_recreate_collection",
            collection=collection_name,
            new_vector_size=VECTOR_SIZE,
        )
        return

    # Delete existing collection
    try:
        qdrant.client.delete_collection(collection_name)
        logger.info("collection_deleted", collection=collection_name)
    except Exception as e:
        logger.warning("collection_delete_skipped", reason=str(e))

    # Create new collection with 768d vectors
    qdrant.ensure_knowledge_collection()
    logger.info(
        "collection_recreated",
        collection=collection_name,
        vector_size=VECTOR_SIZE,
    )


def reembed_chunks(
    mongo: MongoDBClient,
    qdrant: QdrantStorageClient,
    embedder: NomicEmbedder,
    batch_size: int,
    dry_run: bool,
) -> dict:
    """Re-embed all chunks and upsert to Qdrant.

    Returns:
        Statistics dict with counts.
    """
    logger = structlog.get_logger()

    total_chunks = count_all_chunks(mongo)
    processed = 0
    errors = 0

    logger.info("reembed_started", total_chunks=total_chunks, batch_size=batch_size)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Re-embedding chunks...", total=total_chunks)

        batch_texts = []
        batch_chunks = []

        cursor = get_all_chunks_cursor(mongo, batch_size)

        for doc in cursor:
            chunk_id = str(doc["_id"])
            content = doc.get("content", "")
            source_id = doc.get("source_id", "")
            position = doc.get("position", {})

            if not content:
                logger.warning("empty_chunk_skipped", chunk_id=chunk_id)
                progress.update(task, advance=1)
                continue

            batch_texts.append(content)
            batch_chunks.append({
                "chunk_id": chunk_id,
                "source_id": source_id,
                "position": position,
                "project_id": doc.get("project_id", settings.project_id),
            })

            # Process batch when full
            if len(batch_texts) >= batch_size:
                if not dry_run:
                    try:
                        vectors = embedder.embed_documents(batch_texts)

                        for i, vector in enumerate(vectors):
                            chunk_info = batch_chunks[i]
                            payload = {
                                "source_id": chunk_info["source_id"],
                                "chunk_id": chunk_info["chunk_id"],
                                "chapter": chunk_info["position"].get("chapter"),
                                "section": chunk_info["position"].get("section"),
                                "page": chunk_info["position"].get("page"),
                            }
                            qdrant.upsert_chunk_vector(
                                chunk_id=chunk_info["chunk_id"],
                                vector=vector,
                                payload=payload,
                                project_id=chunk_info["project_id"],
                            )

                        processed += len(batch_texts)
                    except Exception as e:
                        logger.error("batch_embedding_failed", error=str(e))
                        errors += len(batch_texts)
                else:
                    processed += len(batch_texts)

                progress.update(task, advance=len(batch_texts))
                batch_texts = []
                batch_chunks = []

        # Process remaining batch
        if batch_texts:
            if not dry_run:
                try:
                    vectors = embedder.embed_documents(batch_texts)

                    for i, vector in enumerate(vectors):
                        chunk_info = batch_chunks[i]
                        payload = {
                            "source_id": chunk_info["source_id"],
                            "chunk_id": chunk_info["chunk_id"],
                            "chapter": chunk_info["position"].get("chapter"),
                            "section": chunk_info["position"].get("section"),
                            "page": chunk_info["position"].get("page"),
                        }
                        qdrant.upsert_chunk_vector(
                            chunk_id=chunk_info["chunk_id"],
                            vector=vector,
                            payload=payload,
                            project_id=chunk_info["project_id"],
                        )

                    processed += len(batch_texts)
                except Exception as e:
                    logger.error("batch_embedding_failed", error=str(e))
                    errors += len(batch_texts)
            else:
                processed += len(batch_texts)

            progress.update(task, advance=len(batch_texts))

    return {
        "total_chunks": total_chunks,
        "processed": processed,
        "errors": errors,
    }


def format_summary(stats: dict, dry_run: bool) -> str:
    """Format results as a summary string."""
    mode = "DRY RUN" if dry_run else "COMPLETE"
    lines = [
        "",
        "=" * 60,
        f"RE-EMBEDDING {mode}",
        "=" * 60,
        "",
        f"  Model:            {EMBEDDING_CONFIG['model_id']}",
        f"  Vector Size:      {VECTOR_SIZE} dimensions",
        f"  Collection:       {KNOWLEDGE_VECTORS_COLLECTION}",
        "",
        f"  Total Chunks:     {stats['total_chunks']:,}",
        f"  Processed:        {stats['processed']:,}",
        f"  Errors:           {stats['errors']:,}",
        "",
        "=" * 60,
    ]
    return "\n".join(lines)


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Re-embed all chunks with nomic-embed-text-v1.5",
        epilog="Example: uv run scripts/reembed.py --batch-size 50",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of chunks to process per batch (default: 100)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be done without modifying data",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project ID for namespacing (overrides PROJECT_ID env var)",
    )

    args = parser.parse_args()

    # Configure logging
    configure_logging(args.verbose)
    logger = structlog.get_logger()

    # Override project ID if specified
    if args.project:
        settings.project_id = args.project

    # Display startup info
    print(f"Re-embedding with: {EMBEDDING_CONFIG['model_id']}")
    print(f"New vector size: {VECTOR_SIZE} dimensions")
    print(f"Batch size: {args.batch_size}")
    print(f"Project: {settings.project_id}")
    if args.dry_run:
        print("Mode: DRY RUN (no database modifications)")
    print()

    try:
        # Initialize clients
        print("Connecting to databases...")
        mongo = MongoDBClient()
        mongo.connect()

        qdrant = QdrantStorageClient()

        # Initialize embedder (this downloads the model if needed)
        print("Loading embedding model (this may take a while on first run)...")
        embedder = NomicEmbedder()

        # Confirm with user if not dry run
        if not args.dry_run:
            total = count_all_chunks(mongo)
            print()
            print(f"WARNING: This will delete and recreate the Qdrant collection!")
            print(f"         {total:,} chunks will be re-embedded.")
            print()
            response = input("Continue? [y/N] ")
            if response.lower() != "y":
                print("Aborted.")
                return 0
            print()

        # Step 1: Recreate Qdrant collection
        print("Step 1/2: Recreating Qdrant collection...")
        recreate_qdrant_collection(qdrant, args.dry_run)

        # Step 2: Re-embed all chunks
        print("Step 2/2: Re-embedding chunks...")
        stats = reembed_chunks(
            mongo=mongo,
            qdrant=qdrant,
            embedder=embedder,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
        )

        # Display summary
        print(format_summary(stats, args.dry_run))

        # Cleanup
        mongo.close()

        return 0 if stats["errors"] == 0 else 1

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130

    except Exception as e:
        logger.error("reembed_failed", error=str(e))
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
