"""Shared utilities for Streamlit web interface.

This module provides common functions used across all Streamlit pages:
- Database statistics and connection checks
- CRUD operations for sources
- Ingestion and extraction pipelines
- Knowledge search functionality
"""

import re
import subprocess
from pathlib import Path
from typing import Any

import streamlit as st
import structlog
from bson import ObjectId

from src.config import KNOWLEDGE_VECTORS_COLLECTION, settings

logger = structlog.get_logger()
from src.embeddings.local_embedder import LocalEmbedder
from src.extraction.pipeline import ExtractionPipeline, ExtractionPipelineResult
from src.extractors import ExtractionType
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient


# Cache embedder to avoid reloading model on every search
@st.cache_resource
def get_embedder() -> LocalEmbedder:
    """Get cached embedder instance."""
    return LocalEmbedder()


@st.cache_data(ttl=60)
def get_mongodb_stats() -> dict[str, Any]:
    """Get MongoDB collection statistics.

    Returns:
        Dict with connection status, counts, and recent sources.
        On failure, returns {"connected": False, "error": str}.
    """
    client = None
    try:
        client = MongoDBClient()
        client.connect()
        db = client._client[settings.mongodb_database]

        # Get collection stats
        sources_count = db[settings.sources_collection].count_documents({})
        chunks_count = db[settings.chunks_collection].count_documents({})
        extractions_count = db[settings.extractions_collection].count_documents({})

        # Get recent sources with more fields
        recent_sources = list(
            db[settings.sources_collection]
            .find({}, {
                "title": 1,
                "status": 1,
                "ingested_at": 1,
                "type": 1,
                "category": 1,
                "tags": 1,
                "file_size": 1,
            })
            .sort("ingested_at", -1)
            .limit(50)
        )

        # Get extraction counts per source using aggregation (avoids N+1 queries)
        extraction_counts_by_source = {}
        extraction_breakdown_by_source = {}

        # Single aggregation for all extraction counts and breakdowns
        extraction_pipeline = [
            {"$group": {
                "_id": {"source_id": "$source_id", "type": "$type"},
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.source_id",
                "total": {"$sum": "$count"},
                "breakdown": {"$push": {"type": "$_id.type", "count": "$count"}}
            }}
        ]
        for doc in db[settings.extractions_collection].aggregate(extraction_pipeline):
            source_id = doc["_id"]
            extraction_counts_by_source[source_id] = doc["total"]
            extraction_breakdown_by_source[source_id] = {
                item["type"]: item["count"] for item in doc["breakdown"]
            }

        # Get chunk counts per source using aggregation (avoids N+1 queries)
        chunk_counts_by_source = {}
        chunk_pipeline = [
            {"$group": {"_id": "$source_id", "count": {"$sum": 1}}}
        ]
        for doc in db[settings.chunks_collection].aggregate(chunk_pipeline):
            chunk_counts_by_source[doc["_id"]] = doc["count"]

        return {
            "connected": True,
            "sources": sources_count,
            "chunks": chunks_count,
            "extractions": extractions_count,
            "recent_sources": recent_sources,
            "extraction_counts_by_source": extraction_counts_by_source,
            "extraction_breakdown_by_source": extraction_breakdown_by_source,
            "chunk_counts_by_source": chunk_counts_by_source,
            "database": settings.mongodb_database,
            "project_id": settings.project_id,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
    finally:
        if client:
            client.close()


@st.cache_data(ttl=60)
def get_qdrant_stats() -> dict[str, Any]:
    """Get Qdrant collection statistics.

    Returns:
        Dict with connection status and collection info.
        On failure, returns {"connected": False, "error": str}.
    """
    try:
        client = QdrantStorageClient()
        client.ensure_knowledge_collection()

        collection_name = KNOWLEDGE_VECTORS_COLLECTION
        info = client.client.get_collection(collection_name)

        return {
            "connected": True,
            "collection": collection_name,
            "vectors_count": info.points_count,
            "vector_dimension": info.config.params.vectors.size,
            "status": info.status.value,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


def rename_source(source_id: str, new_title: str) -> tuple[bool, str]:
    """Rename a source in MongoDB.

    Args:
        source_id: MongoDB ObjectId string.
        new_title: New title for the source.

    Returns:
        Tuple of (success: bool, message: str).
    """
    # Input validation
    if not new_title or not new_title.strip():
        return False, "Title cannot be empty"

    new_title = new_title.strip()

    if len(new_title) > 500:
        return False, "Title cannot exceed 500 characters"

    if len(new_title) < 2:
        return False, "Title must be at least 2 characters"

    client = None
    try:
        client = MongoDBClient()
        client.connect()
        db = client._client[settings.mongodb_database]
        result = db[settings.sources_collection].update_one(
            {"_id": ObjectId(source_id)},
            {"$set": {"title": new_title}}
        )
        if result.modified_count > 0:
            logger.info("source_renamed", source_id=source_id, new_title=new_title)
            return True, f"Renamed to: {new_title}"
        return False, "Source not found or title unchanged"
    except Exception as e:
        logger.error("rename_source_failed", source_id=source_id, error=str(e))
        return False, f"Failed to rename: {e}"
    finally:
        if client:
            client.close()


def delete_source(source_id: str) -> tuple[bool, str]:
    """Delete a source and all related data from MongoDB and Qdrant.

    Args:
        source_id: MongoDB ObjectId string.

    Returns:
        Tuple of (success: bool, message: str).
    """
    mongo_client = None
    try:
        # Connect to MongoDB
        mongo_client = MongoDBClient()
        mongo_client.connect()
        db = mongo_client._client[settings.mongodb_database]

        # Count related documents for summary
        chunks_count = db[settings.chunks_collection].count_documents(
            {"source_id": source_id}
        )
        extractions_count = db[settings.extractions_collection].count_documents(
            {"source_id": source_id}
        )

        # Delete from MongoDB
        db[settings.chunks_collection].delete_many({"source_id": source_id})
        db[settings.extractions_collection].delete_many({"source_id": source_id})
        result = db[settings.sources_collection].delete_one(
            {"_id": ObjectId(source_id)}
        )

        if result.deleted_count == 0:
            return False, "Source not found"

        # Delete from Qdrant
        qdrant_client = QdrantStorageClient()
        qdrant_client.delete_by_source(KNOWLEDGE_VECTORS_COLLECTION, source_id)

        return True, f"Deleted source with {chunks_count} chunks and {extractions_count} extractions"

    except Exception as e:
        return False, f"Delete failed: {str(e)}"
    finally:
        if mongo_client:
            mongo_client.close()


def _validate_cli_arg(value: str, arg_name: str) -> str | None:
    """Validate and sanitize CLI argument to prevent injection.

    Args:
        value: The argument value to validate.
        arg_name: Name of the argument for error messages.

    Returns:
        Sanitized value or None if invalid.
    """
    if not value:
        return None

    # Strip whitespace
    value = value.strip()

    # Reject shell metacharacters and control characters
    dangerous_patterns = [";", "&", "|", "$", "`", "(", ")", "{", "}", "<", ">", "\n", "\r"]
    for pattern in dangerous_patterns:
        if pattern in value:
            logger.warning(
                "cli_arg_rejected",
                arg_name=arg_name,
                reason="contains_dangerous_char",
                char=pattern,
            )
            return None

    return value


def run_ingestion(
    file_path: str,
    category: str | None,
    tags: str | None,
    year: int | None,
) -> tuple[str, str, int]:
    """Run the ingestion pipeline via subprocess.

    Args:
        file_path: Path to file to ingest.
        category: Optional category (validated).
        tags: Optional comma-separated tags (validated).
        year: Optional publication year.

    Returns:
        Tuple of (stdout, stderr, returncode).
    """
    cmd = ["uv", "run", "scripts/ingest.py", file_path]

    # Validate and add category
    if category:
        validated_category = _validate_cli_arg(category, "category")
        if validated_category:
            cmd.extend(["--category", validated_category])

    # Validate and add tags
    if tags:
        validated_tags = _validate_cli_arg(tags, "tags")
        if validated_tags:
            cmd.extend(["--tags", validated_tags])

    if year:
        cmd.extend(["--year", str(year)])

    logger.info("run_ingestion_started", file_path=file_path, category=category, tags=tags)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,  # packages/pipeline
    )

    return result.stdout, result.stderr, result.returncode


def run_extraction(
    source_id: str,
    extractor_types: list[ExtractionType] | None = None,
) -> ExtractionPipelineResult:
    """Run hierarchical extraction pipeline on a source.

    Args:
        source_id: MongoDB source document ID.
        extractor_types: Optional list of extraction types.
                        If None, all extractors are used.

    Returns:
        ExtractionPipelineResult with counts and statistics.
    """
    with ExtractionPipeline() as pipeline:
        return pipeline.extract_hierarchical(
            source_id=source_id,
            extractor_types=extractor_types,
            quiet=True,
        )


def search_knowledge(
    query: str,
    limit: int = 20,
    extraction_type: str | None = None,
    source_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search the knowledge base using semantic search.

    Args:
        query: Search query text.
        limit: Maximum results to return.
        extraction_type: Optional filter by extraction type.
        source_id: Optional filter by source.

    Returns:
        List of search results with scores and metadata.
    """
    # Generate embedding for query
    embedder = get_embedder()
    query_vector = embedder.embed_query(query)

    # Search Qdrant
    qdrant_client = QdrantStorageClient()
    results = qdrant_client.search_extractions(
        query_vector=query_vector,
        limit=limit,
        extraction_type=extraction_type,
        source_id=source_id,
    )

    return results


def get_source_options(mongo_stats: dict[str, Any]) -> dict[str, str]:
    """Get source options for dropdown selection.

    Args:
        mongo_stats: MongoDB stats from get_mongodb_stats().

    Returns:
        Dict mapping display labels to source IDs.
    """
    if not mongo_stats.get("connected") or not mongo_stats.get("recent_sources"):
        return {}

    extraction_counts = mongo_stats.get("extraction_counts_by_source", {})
    options = {}

    for src in mongo_stats["recent_sources"]:
        source_id = str(src.get("_id", ""))
        title = src.get("title", "Untitled")
        count = extraction_counts.get(source_id, 0)
        options[f"{title} ({count} extractions)"] = source_id

    return options


def render_sidebar_stats() -> tuple[dict, dict]:
    """Render database status in sidebar.

    Returns:
        Tuple of (mongo_stats, qdrant_stats) dicts.
    """
    with st.sidebar:
        st.header("Database Status")

        if st.button("Refresh Status", key="refresh_stats"):
            st.cache_data.clear()

        # MongoDB Status
        st.subheader("MongoDB")
        mongo_stats = get_mongodb_stats()

        if mongo_stats["connected"]:
            st.success(f"Connected to `{mongo_stats['database']}`")
            st.metric("Sources", mongo_stats["sources"])
            st.metric("Chunks", mongo_stats["chunks"])
            st.metric("Extractions", mongo_stats["extractions"])
            st.caption(f"Project: `{mongo_stats['project_id']}`")
        else:
            st.error(f"Disconnected: {mongo_stats.get('error', 'Unknown')}")

        st.divider()

        # Qdrant Status
        st.subheader("Qdrant")
        qdrant_stats = get_qdrant_stats()

        if qdrant_stats["connected"]:
            st.success("Connected")
            st.metric("Vectors", qdrant_stats["vectors_count"])
            st.caption(f"Dimension: {qdrant_stats['vector_dimension']}d")
            st.caption(f"Collection: `{qdrant_stats['collection']}`")
        else:
            st.error(f"Disconnected: {qdrant_stats.get('error', 'Unknown')}")

    return mongo_stats, qdrant_stats
