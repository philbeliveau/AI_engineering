"""Document hierarchy builder for hierarchical knowledge extraction.

This module builds a hierarchical representation of document chunks,
grouping them by chapter and section for appropriate extraction context.

The hierarchy enables:
- CHAPTER level: Combining all chunks in a chapter (methodology, workflow)
- SECTION level: Combining chunks in a section (decision, pattern, checklist, persona)
- CHUNK level: Individual chunks (warning)
"""

import hashlib
from dataclasses import dataclass, field
from typing import Optional

import structlog

from src.models.chunk import Chunk

logger = structlog.get_logger()


@dataclass
class SectionNode:
    """A section within a chapter containing one or more chunks.

    Attributes:
        section_id: Stable unique ID for this section.
        section_name: Human-readable section name (from chunk.position.section).
        chapter_name: Parent chapter name for context.
        chunks: List of chunks belonging to this section, sorted by chunk_index.
    """

    section_id: str
    section_name: str
    chapter_name: str
    chunks: list[Chunk] = field(default_factory=list)

    @property
    def chunk_ids(self) -> list[str]:
        """Get all chunk IDs in this section."""
        return [chunk.id for chunk in self.chunks]

    @property
    def total_tokens(self) -> int:
        """Sum of token counts for all chunks in this section."""
        return sum(chunk.token_count for chunk in self.chunks)


@dataclass
class ChapterNode:
    """A chapter containing one or more sections.

    Attributes:
        chapter_id: Stable unique ID for this chapter.
        chapter_name: Human-readable chapter name (from chunk.position.chapter).
        sections: Dict mapping section_name to SectionNode.
        uncategorized_chunks: Chunks without section metadata (directly under chapter).
    """

    chapter_id: str
    chapter_name: str
    sections: dict[str, SectionNode] = field(default_factory=dict)
    uncategorized_chunks: list[Chunk] = field(default_factory=list)

    @property
    def all_chunks(self) -> list[Chunk]:
        """Get all chunks in this chapter, including uncategorized."""
        chunks = list(self.uncategorized_chunks)
        for section in self.sections.values():
            chunks.extend(section.chunks)
        return sorted(chunks, key=lambda c: _get_chunk_index(c))

    @property
    def chunk_ids(self) -> list[str]:
        """Get all chunk IDs in this chapter."""
        return [chunk.id for chunk in self.all_chunks]

    @property
    def total_tokens(self) -> int:
        """Sum of token counts for all chunks in this chapter."""
        return sum(chunk.token_count for chunk in self.all_chunks)


@dataclass
class DocumentHierarchy:
    """Complete document hierarchy for a source.

    Attributes:
        source_id: ID of the source document.
        chapters: Dict mapping chapter_name to ChapterNode.
        uncategorized_chunks: Chunks without chapter metadata.
    """

    source_id: str
    chapters: dict[str, ChapterNode] = field(default_factory=dict)
    uncategorized_chunks: list[Chunk] = field(default_factory=list)

    @property
    def all_chunks(self) -> list[Chunk]:
        """Get all chunks in the document."""
        chunks = list(self.uncategorized_chunks)
        for chapter in self.chapters.values():
            chunks.extend(chapter.all_chunks)
        return sorted(chunks, key=lambda c: _get_chunk_index(c))

    @property
    def chapter_count(self) -> int:
        """Number of chapters in the document."""
        return len(self.chapters)

    @property
    def section_count(self) -> int:
        """Total number of sections across all chapters."""
        return sum(len(ch.sections) for ch in self.chapters.values())

    @property
    def chunk_count(self) -> int:
        """Total number of chunks in the document."""
        return len(self.all_chunks)

    def get_chapter_nodes(self) -> list[ChapterNode]:
        """Get all chapter nodes, sorted by first chunk index."""
        chapters = list(self.chapters.values())
        return sorted(
            chapters,
            key=lambda ch: _get_chunk_index(ch.all_chunks[0]) if ch.all_chunks else 0,
        )

    def get_section_nodes(self) -> list[SectionNode]:
        """Get all section nodes across all chapters, sorted by first chunk index."""
        sections = []
        for chapter in self.chapters.values():
            sections.extend(chapter.sections.values())
        return sorted(
            sections,
            key=lambda s: _get_chunk_index(s.chunks[0]) if s.chunks else 0,
        )


def _get_chunk_index(chunk: Chunk) -> int:
    """Extract chunk index for sorting.

    Chunks may have a position with chunk_index, or we fall back to id ordering.
    """
    # The Chunk model uses position.page for page number but doesn't have chunk_index
    # We'll use the chunk id's lexicographic order as fallback
    # Since MongoDB ObjectIds are time-based, this gives approximate ordering
    return int(chunk.id, 16) if chunk.id else 0


def _generate_id(source_id: str, context_type: str, name: str) -> str:
    """Generate a stable unique ID for a chapter or section.

    Uses SHA-256 hash of source_id + type + name for deterministic IDs.

    Args:
        source_id: The source document ID.
        context_type: Either "chapter" or "section".
        name: The chapter or section name.

    Returns:
        A 24-character hex string (compatible with MongoDB ObjectId format).
    """
    content = f"{source_id}:{context_type}:{name}"
    hash_digest = hashlib.sha256(content.encode()).hexdigest()
    # Take first 24 chars to match MongoDB ObjectId format
    return hash_digest[:24]


def build_hierarchy(chunks: list[Chunk], source_id: str) -> DocumentHierarchy:
    """Build a document hierarchy from a list of chunks.

    Groups chunks by their position.chapter and position.section metadata.
    Chunks without metadata are placed in uncategorized containers.

    Args:
        chunks: List of Chunk objects from the document.
        source_id: ID of the source document.

    Returns:
        DocumentHierarchy with chapters, sections, and chunks organized.
    """
    hierarchy = DocumentHierarchy(source_id=source_id)

    for chunk in chunks:
        chapter_name = _get_chapter_name(chunk)
        section_name = _get_section_name(chunk)

        if not chapter_name:
            # No chapter metadata - add to uncategorized
            hierarchy.uncategorized_chunks.append(chunk)
            continue

        # Ensure chapter exists
        if chapter_name not in hierarchy.chapters:
            chapter_id = _generate_id(source_id, "chapter", chapter_name)
            hierarchy.chapters[chapter_name] = ChapterNode(
                chapter_id=chapter_id,
                chapter_name=chapter_name,
            )

        chapter = hierarchy.chapters[chapter_name]

        if not section_name:
            # Has chapter but no section - add to chapter's uncategorized
            chapter.uncategorized_chunks.append(chunk)
            continue

        # Ensure section exists within chapter
        if section_name not in chapter.sections:
            section_id = _generate_id(source_id, "section", f"{chapter_name}:{section_name}")
            chapter.sections[section_name] = SectionNode(
                section_id=section_id,
                section_name=section_name,
                chapter_name=chapter_name,
            )

        chapter.sections[section_name].chunks.append(chunk)

    # Sort chunks within each container by chunk index
    hierarchy.uncategorized_chunks.sort(key=_get_chunk_index)
    for chapter in hierarchy.chapters.values():
        chapter.uncategorized_chunks.sort(key=_get_chunk_index)
        for section in chapter.sections.values():
            section.chunks.sort(key=_get_chunk_index)

    logger.info(
        "hierarchy_built",
        source_id=source_id,
        chapters=hierarchy.chapter_count,
        sections=hierarchy.section_count,
        chunks=hierarchy.chunk_count,
        uncategorized=len(hierarchy.uncategorized_chunks),
    )

    return hierarchy


def _get_chapter_name(chunk: Chunk) -> Optional[str]:
    """Extract chapter name from chunk position metadata.

    Args:
        chunk: The chunk to extract chapter from.

    Returns:
        Chapter name string or None if not available.
    """
    if chunk.position and chunk.position.chapter:
        return chunk.position.chapter
    return None


def _get_section_name(chunk: Chunk) -> Optional[str]:
    """Extract section name from chunk position metadata.

    Args:
        chunk: The chunk to extract section from.

    Returns:
        Section name string or None if not available.
    """
    if chunk.position and chunk.position.section:
        return chunk.position.section
    return None


# =============================================================================
# Chunk Combiner Utility
# =============================================================================


@dataclass
class CombinedContent:
    """Result of combining chunks for extraction.

    Attributes:
        content: The combined text content.
        chunk_ids: List of chunk IDs that were combined.
        total_tokens: Total token count of combined content.
        truncated: Whether content was truncated to fit token limit.
    """

    content: str
    chunk_ids: list[str]
    total_tokens: int
    truncated: bool = False


def combine_chunks(
    chunks: list[Chunk],
    max_tokens: int,
    strategy: str = "truncate",
) -> CombinedContent:
    """Combine multiple chunks into a single content string for extraction.

    Chunks are sorted by their index and concatenated with newlines.
    If combined content exceeds max_tokens, the strategy is applied.

    Args:
        chunks: List of chunks to combine.
        max_tokens: Maximum token budget for combined content.
        strategy: How to handle exceeding max_tokens:
            - "truncate": Cut off at token limit (default)
            - "summary_if_exceeded": Placeholder for future summarization
            - "none": Return as-is without limit (for single chunk level)

    Returns:
        CombinedContent with combined text and metadata.

    Raises:
        ValueError: If strategy is not recognized.
    """
    if not chunks:
        return CombinedContent(content="", chunk_ids=[], total_tokens=0)

    valid_strategies = {"truncate", "summary_if_exceeded", "none"}
    if strategy not in valid_strategies:
        raise ValueError(f"Unknown combination strategy: '{strategy}'. Valid: {valid_strategies}")

    # Sort chunks by index for proper ordering
    sorted_chunks = sorted(chunks, key=_get_chunk_index)

    # Combine all content with paragraph breaks
    combined_text = "\n\n".join(chunk.content for chunk in sorted_chunks)
    chunk_ids = [chunk.id for chunk in sorted_chunks]
    total_tokens = sum(chunk.token_count for chunk in sorted_chunks)

    # Apply strategy if exceeding limit
    if strategy == "none" or total_tokens <= max_tokens:
        return CombinedContent(
            content=combined_text,
            chunk_ids=chunk_ids,
            total_tokens=total_tokens,
            truncated=False,
        )

    if strategy == "truncate":
        return _truncate_to_limit(sorted_chunks, max_tokens)

    if strategy == "summary_if_exceeded":
        # Future: implement summarization
        # For now, fall back to truncation with a log message
        logger.warning(
            "summary_if_exceeded_not_implemented",
            message="Falling back to truncation strategy",
            total_tokens=total_tokens,
            max_tokens=max_tokens,
        )
        return _truncate_to_limit(sorted_chunks, max_tokens)

    # Should not reach here due to validation above
    return CombinedContent(
        content=combined_text,
        chunk_ids=chunk_ids,
        total_tokens=total_tokens,
    )


def _truncate_to_limit(chunks: list[Chunk], max_tokens: int) -> CombinedContent:
    """Truncate combined chunks to fit within token limit.

    Includes whole chunks until adding another would exceed the limit.

    Args:
        chunks: Pre-sorted list of chunks.
        max_tokens: Maximum token count.

    Returns:
        CombinedContent with truncated content.
    """
    included_chunks: list[Chunk] = []
    current_tokens = 0

    for chunk in chunks:
        if current_tokens + chunk.token_count > max_tokens:
            # Adding this chunk would exceed limit
            break
        included_chunks.append(chunk)
        current_tokens += chunk.token_count

    # Edge case: if first chunk already exceeds limit, include it partially
    if not included_chunks and chunks:
        first_chunk = chunks[0]
        # Estimate character ratio for truncation
        # Rough estimate: 1 token ≈ 4 characters
        char_limit = max_tokens * 4
        truncated_content = first_chunk.content[:char_limit]
        return CombinedContent(
            content=truncated_content,
            chunk_ids=[first_chunk.id],
            total_tokens=max_tokens,  # Approximate
            truncated=True,
        )

    combined_text = "\n\n".join(chunk.content for chunk in included_chunks)
    chunk_ids = [chunk.id for chunk in included_chunks]

    return CombinedContent(
        content=combined_text,
        chunk_ids=chunk_ids,
        total_tokens=current_tokens,
        truncated=len(included_chunks) < len(chunks),
    )
