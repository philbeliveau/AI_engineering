"""Extraction Storage Service.

Orchestrates extraction storage across MongoDB and Qdrant,
handling summary generation, embedding, and dual-store persistence.
"""

from typing import Any, Optional

import structlog

from src.config import settings
from src.embeddings.local_embedder import LocalEmbedder
from src.exceptions import KnowledgeError
from src.extractors.base import ExtractionBase
from src.extractors.utils import generate_extraction_summary
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import CONTENT_TYPE_EXTRACTION, QdrantStorageClient

logger = structlog.get_logger()


class ExtractionStorageError(KnowledgeError):
    """Error raised during extraction storage operations."""

    pass


class ExtractionStorage:
    """Orchestrates extraction storage across MongoDB and Qdrant.

    This service handles the complete extraction persistence workflow:
    1. Generate summary from extraction content
    2. Generate embedding from summary
    3. Save extraction to MongoDB (full document)
    4. Save embedding to Qdrant (vector + payload)
    5. Handle partial failures gracefully

    Attributes:
        mongodb: MongoDB client for document storage.
        qdrant: Qdrant client for vector storage.
        embedder: Local embedder for generating embeddings.

    Example:
        storage = ExtractionStorage(
            mongodb_client=mongodb,
            qdrant_client=qdrant,
            embedder=embedder,
        )
        result = storage.save_extraction(decision)
        # {'extraction_id': '...', 'mongodb_saved': True, 'qdrant_saved': True}
    """

    def __init__(
        self,
        mongodb_client: MongoDBClient,
        qdrant_client: QdrantStorageClient,
        embedder: LocalEmbedder,
    ):
        """Initialize ExtractionStorage with required dependencies.

        Args:
            mongodb_client: Connected MongoDB client for document storage.
            qdrant_client: Connected Qdrant client for vector storage.
            embedder: LocalEmbedder instance for generating embeddings.
        """
        self.mongodb = mongodb_client
        self.qdrant = qdrant_client
        self.embedder = embedder

        # Ensure the unified knowledge collection exists for storing extractions
        self.qdrant.ensure_knowledge_collection()

        logger.debug(
            "extraction_storage_initialized",
            embedder_dimension=embedder.get_dimension(),
        )

    def save_extraction(self, extraction: ExtractionBase) -> dict[str, object]:
        """Save extraction to both MongoDB and Qdrant.

        This method orchestrates the complete storage workflow:
        1. Validates extraction has required fields
        2. Generates summary for embedding
        3. Generates 384d embedding from summary
        4. Saves full extraction to MongoDB
        5. Saves embedding + payload to Qdrant

        Args:
            extraction: Validated extraction from extractor
                (Decision, Pattern, Warning, Methodology, etc.)

        Returns:
            dict with keys:
                - extraction_id: str - MongoDB extraction ID
                - mongodb_saved: bool - True if MongoDB save succeeded
                - qdrant_saved: bool - True if Qdrant save succeeded

        Raises:
            ExtractionStorageError: If validation fails, embedding fails,
                or MongoDB save fails. Qdrant failures are logged but don't
                raise (MongoDB is source of truth).
        """
        logger.info(
            "saving_extraction",
            type=extraction.type.value,
            source_id=extraction.source_id,
            chunk_id=extraction.chunk_id,
        )

        # Step 1: Validate extraction
        self._validate_extraction(extraction)

        # Step 2: Generate summary for embedding
        try:
            summary = generate_extraction_summary(extraction)
            logger.debug(
                "summary_generated",
                type=extraction.type.value,
                summary_length=len(summary),
            )
        except Exception as e:
            raise ExtractionStorageError(
                code="SUMMARY_GENERATION_FAILED",
                message=f"Failed to generate summary for extraction: {e}",
                details={
                    "type": extraction.type.value,
                    "chunk_id": extraction.chunk_id,
                    "error": str(e),
                },
            )

        # Step 3: Generate embedding (384 dimensions)
        try:
            embedding = self.embedder.embed_text(summary)
            logger.debug(
                "embedding_generated",
                type=extraction.type.value,
                dimension=len(embedding),
            )
        except Exception as e:
            raise ExtractionStorageError(
                code="EMBEDDING_GENERATION_FAILED",
                message=f"Failed to generate embedding: {e}",
                details={
                    "type": extraction.type.value,
                    "chunk_id": extraction.chunk_id,
                    "summary_length": len(summary),
                    "error": str(e),
                },
            )

        # Step 4: Save to MongoDB (source of truth)
        try:
            extraction_id = self.mongodb.save_extraction_from_extractor(extraction)
            logger.info(
                "mongodb_save_success",
                extraction_id=extraction_id,
                type=extraction.type.value,
            )
        except Exception as e:
            raise ExtractionStorageError(
                code="MONGODB_SAVE_FAILED",
                message=f"Failed to save extraction to MongoDB: {e}",
                details={
                    "type": extraction.type.value,
                    "chunk_id": extraction.chunk_id,
                    "error": str(e),
                },
            )

        # Step 5: Build rich payload with denormalized source/chunk metadata
        payload = self._build_rich_payload(extraction, extraction_id)

        # Step 6: Save to Qdrant (optional - log failures but don't raise)
        qdrant_saved = False
        try:
            self.qdrant.upsert_extraction_vector(
                extraction_id=extraction_id,
                vector=embedding,
                payload=payload,
            )
            qdrant_saved = True
            logger.info(
                "qdrant_save_success",
                extraction_id=extraction_id,
                type=extraction.type.value,
            )
        except Exception as e:
            # Log error but don't raise - MongoDB is source of truth
            # Qdrant can be backfilled later
            logger.error(
                "qdrant_save_failed",
                extraction_id=extraction_id,
                type=extraction.type.value,
                error=str(e),
            )

        # Return result with save status
        result = {
            "extraction_id": extraction_id,
            "mongodb_saved": True,
            "qdrant_saved": qdrant_saved,
        }

        logger.info(
            "extraction_saved",
            **result,
            type=extraction.type.value,
        )

        return result

    def _validate_extraction(self, extraction: ExtractionBase) -> None:
        """Validate extraction has required fields.

        Args:
            extraction: Extraction to validate.

        Raises:
            ExtractionStorageError: If required fields are missing.
        """
        if not extraction.source_id:
            raise ExtractionStorageError(
                code="VALIDATION_ERROR",
                message="Missing required field: source_id",
                details={"field": "source_id", "type": extraction.type.value},
            )

        if not extraction.chunk_id:
            raise ExtractionStorageError(
                code="VALIDATION_ERROR",
                message="Missing required field: chunk_id",
                details={"field": "chunk_id", "type": extraction.type.value},
            )

    def _get_extraction_title(self, extraction: ExtractionBase) -> str:
        """Extract a human-readable title from the extraction content.

        Args:
            extraction: The extraction to get title from.

        Returns:
            Human-readable title for the extraction.
        """
        extraction_type = extraction.type.value

        # Pattern extractions have a 'name' field
        if extraction_type == "pattern" and hasattr(extraction, "name"):
            return getattr(extraction, "name", "")

        # Warning extractions have a 'title' field
        if extraction_type == "warning" and hasattr(extraction, "title"):
            return getattr(extraction, "title", "")

        # Decision extractions have a 'question' field
        if extraction_type == "decision" and hasattr(extraction, "question"):
            question = getattr(extraction, "question", "")
            return question[:100] if question else ""

        # Methodology extractions have a 'name' field
        if extraction_type == "methodology" and hasattr(extraction, "name"):
            return getattr(extraction, "name", "")

        # Checklist extractions have a 'name' field
        if extraction_type == "checklist" and hasattr(extraction, "name"):
            return getattr(extraction, "name", "")

        # Persona extractions have a 'role' field
        if extraction_type == "persona" and hasattr(extraction, "role"):
            return getattr(extraction, "role", "")

        # Workflow extractions have a 'name' field
        if extraction_type == "workflow" and hasattr(extraction, "name"):
            return getattr(extraction, "name", "")

        return ""

    def _build_rich_payload(
        self,
        extraction: ExtractionBase,
        extraction_id: str,
        project_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Build rich payload for Qdrant with denormalized source/chunk metadata.

        Fetches source and chunk from MongoDB to enrich the payload with
        metadata for filtering and display in the unified collection.

        Args:
            extraction: The extraction being stored.
            extraction_id: MongoDB ID of the saved extraction.
            project_id: Optional project ID override.

        Returns:
            Rich payload dict with indexed and display fields.
        """
        # Resolve project_id
        resolved_project_id = project_id or settings.project_id

        # Initialize payload with extraction data
        payload: dict[str, Any] = {
            # === INDEXED FIELDS (for filtering) ===
            "project_id": resolved_project_id,
            "content_type": CONTENT_TYPE_EXTRACTION,
            "source_id": extraction.source_id,
            "extraction_type": extraction.type.value,
            "topics": extraction.topics,
            # === NON-INDEXED FIELDS (for display) ===
            "chunk_id": extraction.chunk_id,
            "extraction_id": extraction_id,
            "extraction_title": self._get_extraction_title(extraction),
            "_original_id": extraction_id,
        }

        # Fetch source metadata for denormalization
        try:
            source = self.mongodb.get_source(extraction.source_id)
            payload["source_type"] = source.type
            payload["source_category"] = source.category
            payload["source_year"] = source.year
            payload["source_tags"] = source.tags
            payload["source_title"] = source.title
            logger.debug(
                "source_metadata_fetched",
                source_id=extraction.source_id,
                source_title=source.title,
            )
        except Exception as e:
            # Log but don't fail - source metadata is optional
            logger.warning(
                "source_metadata_fetch_failed",
                source_id=extraction.source_id,
                error=str(e),
            )
            payload["source_type"] = ""
            payload["source_category"] = "foundational"
            payload["source_year"] = None
            payload["source_tags"] = []
            payload["source_title"] = ""

        # Fetch chunk metadata for position context
        try:
            chunk = self.mongodb.get_chunk(extraction.chunk_id)
            payload["chapter"] = chunk.position.chapter
            payload["section"] = chunk.position.section
            payload["page"] = chunk.position.page
            logger.debug(
                "chunk_metadata_fetched",
                chunk_id=extraction.chunk_id,
                chapter=chunk.position.chapter,
            )
        except Exception as e:
            # Log but don't fail - chunk metadata is optional
            logger.warning(
                "chunk_metadata_fetch_failed",
                chunk_id=extraction.chunk_id,
                error=str(e),
            )
            payload["chapter"] = None
            payload["section"] = None
            payload["page"] = None

        return payload
