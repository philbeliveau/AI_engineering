"""Text chunking processor using Docling's HybridChunker.

This module provides document chunking that splits documents into appropriately
sized chunks for embedding and extraction, respecting document structure and
using accurate token counting from the embedding model's tokenizer.

Example:
    from src.processors import DoclingChunker, ChunkerConfig
    from src.adapters import DoclingAdapter

    adapter = DoclingAdapter()
    chunker = DoclingChunker()

    result = adapter.extract_text(file_path)
    docling_doc = result.metadata.get("_docling_document")
    chunks = chunker.chunk_document(docling_doc, source_id="doc-123")
"""

from __future__ import annotations

import uuid
import warnings
from typing import Optional

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc import DoclingDocument
from pydantic import BaseModel, Field
from transformers import AutoTokenizer
import structlog

from src.config import EMBEDDING_CONFIG
from src.exceptions import KnowledgeError

logger = structlog.get_logger()

# Embedding model ID from centralized config (nomic-embed-text-v1.5)
EMBED_MODEL_ID = EMBEDDING_CONFIG["model_id"]


# ============================================================================
# Configuration Models
# ============================================================================


class ChunkerConfig(BaseModel):
    """Configuration for Docling-based chunker.

    Attributes:
        chunk_size: Target maximum tokens per chunk (for HybridChunker max_tokens).
                   Default 512 fits well within all-MiniLM-L6-v2 limits.
        merge_peers: Whether to merge peer elements for better context.
                    When True, adjacent elements of the same type are combined.
    """

    chunk_size: int = Field(default=512, ge=50, le=2048)
    merge_peers: bool = True


class ChunkOutput(BaseModel):
    """Output model for a text chunk (MongoDB storage compatible).

    This model is designed for direct storage in MongoDB's chunks collection
    and includes all fields required by the architecture specification.

    Attributes:
        id: Unique chunk identifier (UUID4 string).
        source_id: Reference to the source document ID.
        content: The actual text content of the chunk.
        position: Position metadata (chunk_index, section info, etc.).
        token_count: Accurate token count using embedding model tokenizer.
        schema_version: Schema version for future migrations.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    content: str
    position: dict = Field(default_factory=dict)
    token_count: int
    schema_version: str = "1.0"


# ============================================================================
# Exceptions
# ============================================================================


class ChunkerError(KnowledgeError):
    """Base exception for chunker errors."""

    pass


class EmptyContentError(ChunkerError):
    """Raised when input content is empty or produces no chunks."""

    def __init__(self, source_id: str = "unknown"):
        super().__init__(
            code="EMPTY_CONTENT",
            message="Cannot chunk empty document content",
            details={"source_id": source_id},
        )


class ChunkSizeError(ChunkerError):
    """Raised when chunk size configuration is invalid."""

    def __init__(self, reason: str, config: ChunkerConfig):
        super().__init__(
            code="INVALID_CHUNK_SIZE",
            message=f"Invalid chunk size configuration: {reason}",
            details={"config": config.model_dump(), "reason": reason},
        )


class MissingDoclingDocumentError(ChunkerError):
    """Raised when DoclingDocument is missing from adapter metadata."""

    def __init__(self, source_id: str = "unknown"):
        super().__init__(
            code="MISSING_DOCLING_DOCUMENT",
            message="DoclingDocument not found in adapter result metadata",
            details={
                "source_id": source_id,
                "hint": "Ensure adapter result has '_docling_document' in metadata",
            },
        )


# ============================================================================
# Main Chunker Class
# ============================================================================


class DoclingChunker:
    """Wrapper around Docling's HybridChunker for pipeline integration.

    This chunker uses Docling's HybridChunker which:
    1. Respects document structure from DoclingDocument hierarchy
    2. Uses accurate token counting with the embedding model tokenizer
    3. Provides contextualization (adds headings/context to chunk text)

    Example:
        from src.adapters import DoclingAdapter
        from src.processors import DoclingChunker

        adapter = DoclingAdapter()
        chunker = DoclingChunker()

        # Extract document
        result = adapter.extract_text(file_path)

        # Get DoclingDocument from metadata
        docling_doc = result.metadata.get("_docling_document")

        # Chunk the document
        chunks = chunker.chunk_document(docling_doc, source_id="...")
    """

    def __init__(self, config: Optional[ChunkerConfig] = None):
        """Initialize chunker with configuration.

        Args:
            config: Chunker configuration. Uses defaults if not provided.

        Raises:
            ChunkSizeError: If configuration values are invalid.
        """
        self.config = config or ChunkerConfig()
        self._validate_config()

        # Create tokenizer matching the embedding model for accurate token counts
        # nomic-embed-text-v1.5 requires trust_remote_code=True
        self._hf_tokenizer = AutoTokenizer.from_pretrained(
            EMBED_MODEL_ID,
            trust_remote_code=EMBEDDING_CONFIG.get("trust_remote_code", True),
        )
        self._tokenizer = HuggingFaceTokenizer(
            tokenizer=self._hf_tokenizer,
            max_tokens=self.config.chunk_size,
        )

        # Initialize the HybridChunker with our tokenizer
        self._chunker = HybridChunker(
            tokenizer=self._tokenizer,
            merge_peers=self.config.merge_peers,
        )

        logger.debug(
            "docling_chunker_initialized",
            max_tokens=self.config.chunk_size,
            model=EMBED_MODEL_ID,
            merge_peers=self.config.merge_peers,
        )

    def _validate_config(self) -> None:
        """Validate chunker configuration.

        Raises:
            ChunkSizeError: If chunk_size is outside valid range.
        """
        # Pydantic handles basic validation, but we add semantic validation here
        # and raise our custom exception for better error handling
        if self.config.chunk_size < 50:
            raise ChunkSizeError(
                reason="chunk_size must be at least 50 tokens",
                config=self.config,
            )
        if self.config.chunk_size > 2048:
            raise ChunkSizeError(
                reason="chunk_size must not exceed 2048 tokens",
                config=self.config,
            )

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the embedding model tokenizer.

        Args:
            text: Text to count tokens for.

        Returns:
            Accurate token count for the embedding model.
        """
        # Suppress tokenizer warning about sequence length - we're just counting
        # tokens, not running through the model, so the warning is irrelevant
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="Token indices sequence length is longer than",
                category=UserWarning,
            )
            return len(self._hf_tokenizer.encode(text, add_special_tokens=False))

    def chunk_document(
        self,
        docling_doc: DoclingDocument,
        source_id: str,
    ) -> list[ChunkOutput]:
        """Chunk a DoclingDocument into storage-ready chunks.

        This method uses Docling's HybridChunker to split the document
        while respecting its structure. Each chunk is contextualized
        (includes relevant headings) and has accurate token counts.

        Args:
            docling_doc: DoclingDocument from adapter result metadata.
            source_id: ID of the source document for linking.

        Returns:
            List of ChunkOutput objects ready for MongoDB storage.

        Raises:
            MissingDoclingDocumentError: If docling_doc is None.
            EmptyContentError: If document produces no chunks.
        """
        if docling_doc is None:
            raise MissingDoclingDocumentError(source_id)

        # Use HybridChunker to split the document
        chunk_iter = self._chunker.chunk(dl_doc=docling_doc)
        chunks = list(chunk_iter)

        if not chunks:
            raise EmptyContentError(source_id)

        outputs: list[ChunkOutput] = []

        for i, chunk in enumerate(chunks):
            # Get contextualized text (includes headings/context from document)
            text = self._chunker.contextualize(chunk=chunk)

            # Skip empty chunks
            if not text or not text.strip():
                logger.debug(
                    "skipping_empty_chunk",
                    source_id=source_id,
                    chunk_index=i,
                )
                continue

            # Accurate token count using embedding model tokenizer
            token_count = self.count_tokens(text)

            # Build position metadata matching architecture requirements
            # Architecture expects: chapter, section, page, chunk_index
            position: dict = {
                "chunk_index": len(outputs),  # Use output index for continuity
            }

            # Extract heading hierarchy and map to chapter/section structure
            if hasattr(chunk, "meta") and chunk.meta:
                meta = chunk.meta
                if hasattr(meta, "headings") and meta.headings:
                    headings = meta.headings
                    # Store full headings array for reference
                    position["headings"] = headings
                    # Map to architecture-expected chapter/section structure
                    if len(headings) >= 1:
                        position["chapter"] = headings[0]
                    if len(headings) >= 2:
                        # Use last heading as section (most specific)
                        position["section"] = headings[-1]
                if hasattr(meta, "page") and meta.page is not None:
                    position["page"] = meta.page

            outputs.append(
                ChunkOutput(
                    source_id=source_id,
                    content=text,
                    position=position,
                    token_count=token_count,
                )
            )

        logger.info(
            "chunking_complete",
            source_id=source_id,
            total_chunks=len(outputs),
            total_tokens=sum(c.token_count for c in outputs),
            avg_tokens=sum(c.token_count for c in outputs) // max(len(outputs), 1),
        )

        return outputs

    def chunk_from_adapter_result(
        self,
        adapter_result,
        source_id: str,
    ) -> list[ChunkOutput]:
        """Convenience method to chunk directly from an AdapterResult.

        Extracts the DoclingDocument from the adapter result metadata
        and chunks it.

        Args:
            adapter_result: AdapterResult from DoclingAdapter.
            source_id: ID of the source document.

        Returns:
            List of ChunkOutput objects.

        Raises:
            MissingDoclingDocumentError: If _docling_document not in metadata.
        """
        docling_doc = adapter_result.metadata.get("_docling_document")
        if docling_doc is None:
            raise MissingDoclingDocumentError(source_id)

        return self.chunk_document(docling_doc, source_id)
