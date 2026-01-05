"""Hierarchical extractor orchestrator for multi-level knowledge extraction.

This module provides the HierarchicalExtractor class that orchestrates
extraction across different context levels (chapter/section/chunk).

The orchestrator:
1. Builds document hierarchy from chunks
2. Routes extraction types to appropriate context levels
3. Combines chunks respecting token budgets
4. Collects results with proper traceability metadata

Architecture:
- CHAPTER level (8K tokens): methodology, workflow extractors
- SECTION level (4K tokens): decision, pattern, checklist, persona extractors
- CHUNK level (512 tokens): warning extractor
"""

from dataclasses import dataclass, field
from typing import Optional

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionLevel,
    ExtractionResult,
    ExtractionType,
    extractor_registry,
)
from src.extractors.extraction_levels import (
    EXTRACTION_LEVEL_CONFIG,
    get_extraction_types_for_level,
    get_level_for_extraction_type,
)
from src.extractors.hierarchy import (
    ChapterNode,
    CombinedContent,
    DocumentHierarchy,
    SectionNode,
    build_hierarchy,
    combine_chunks,
)
from src.models.chunk import Chunk

logger = structlog.get_logger()


@dataclass
class LevelExtractionStats:
    """Statistics for extraction at a single level.

    Attributes:
        level: The extraction level.
        contexts_processed: Number of contexts (chapters/sections/chunks) processed.
        extractions_attempted: Number of extraction attempts.
        extractions_successful: Number of successful extractions.
        extractions_failed: Number of failed extractions.
        total_tokens_processed: Total tokens processed at this level.
    """

    level: ExtractionLevel
    contexts_processed: int = 0
    extractions_attempted: int = 0
    extractions_successful: int = 0
    extractions_failed: int = 0
    total_tokens_processed: int = 0


@dataclass
class HierarchicalExtractionResult:
    """Complete result of hierarchical extraction for a document.

    Attributes:
        source_id: ID of the source document.
        results: List of all extraction results across all levels.
        stats_by_level: Statistics broken down by extraction level.
        total_chunks: Total number of chunks in the document.
        hierarchy_chapters: Number of chapters in document hierarchy.
        hierarchy_sections: Number of sections in document hierarchy.
    """

    source_id: str
    results: list[ExtractionResult] = field(default_factory=list)
    stats_by_level: dict[ExtractionLevel, LevelExtractionStats] = field(default_factory=dict)
    total_chunks: int = 0
    hierarchy_chapters: int = 0
    hierarchy_sections: int = 0

    @property
    def total_extractions(self) -> int:
        """Total number of extraction attempts across all levels."""
        return sum(s.extractions_attempted for s in self.stats_by_level.values())

    @property
    def successful_extractions(self) -> int:
        """Total number of successful extractions across all levels."""
        return sum(s.extractions_successful for s in self.stats_by_level.values())

    @property
    def failed_extractions(self) -> int:
        """Total number of failed extractions across all levels."""
        return sum(s.extractions_failed for s in self.stats_by_level.values())

    def get_successful_results(self) -> list[ExtractionResult]:
        """Get only successful extraction results."""
        return [r for r in self.results if r.success]


class HierarchicalExtractor:
    """Orchestrator for hierarchical knowledge extraction.

    Coordinates extraction across chapter, section, and chunk levels,
    routing each extraction type to its appropriate context window.

    Example:
        extractor = HierarchicalExtractor()
        result = await extractor.extract_document(chunks, source_id)

        print(f"Extracted {result.successful_extractions} knowledge items")
        for level, stats in result.stats_by_level.items():
            print(f"  {level.value}: {stats.extractions_successful} successful")

    Attributes:
        extraction_types: Optional list of extraction types to run.
            If None, runs all extraction types across all levels.
    """

    def __init__(
        self,
        extraction_types: Optional[list[ExtractionType]] = None,
    ):
        """Initialize the hierarchical extractor.

        Args:
            extraction_types: Optional list of extraction types to run.
                If None, all registered extraction types are used.
                If empty list, no extractions will run.
        """
        if extraction_types is not None:
            self.extraction_types = extraction_types
        else:
            # Get all registered extraction types
            self.extraction_types = extractor_registry.list_extraction_types()

        logger.debug(
            "hierarchical_extractor_initialized",
            extraction_types=[et.value for et in self.extraction_types],
        )

    async def extract_document(
        self,
        chunks: list[Chunk],
        source_id: str,
    ) -> HierarchicalExtractionResult:
        """Extract knowledge from a document using hierarchical context.

        This is the main entry point for hierarchical extraction. It:
        1. Builds document hierarchy from chunks
        2. Extracts at chapter level (methodology, workflow)
        3. Extracts at section level (decision, pattern, checklist, persona)
        4. Extracts at chunk level (warning)

        Args:
            chunks: List of document chunks with position metadata.
            source_id: ID of the source document.

        Returns:
            HierarchicalExtractionResult with all extractions and statistics.
        """
        logger.info(
            "hierarchical_extraction_started",
            source_id=source_id,
            chunk_count=len(chunks),
            extraction_types=[et.value for et in self.extraction_types],
        )

        # Initialize result
        result = HierarchicalExtractionResult(
            source_id=source_id,
            total_chunks=len(chunks),
        )

        # Initialize stats for all levels
        for level in ExtractionLevel:
            result.stats_by_level[level] = LevelExtractionStats(level=level)

        if not chunks:
            logger.warning("hierarchical_extraction_no_chunks", source_id=source_id)
            return result

        # Build document hierarchy
        hierarchy = build_hierarchy(chunks, source_id)
        result.hierarchy_chapters = hierarchy.chapter_count
        result.hierarchy_sections = hierarchy.section_count

        # Extract at each level
        chapter_results = await self._extract_chapter_level(hierarchy, source_id)
        section_results = await self._extract_section_level(hierarchy, source_id)
        chunk_results = await self._extract_chunk_level(hierarchy, source_id)

        # Combine results
        result.results.extend(chapter_results)
        result.results.extend(section_results)
        result.results.extend(chunk_results)

        # Update stats
        self._update_stats(result, chapter_results, ExtractionLevel.CHAPTER)
        self._update_stats(result, section_results, ExtractionLevel.SECTION)
        self._update_stats(result, chunk_results, ExtractionLevel.CHUNK)

        logger.info(
            "hierarchical_extraction_completed",
            source_id=source_id,
            total_extractions=result.total_extractions,
            successful=result.successful_extractions,
            failed=result.failed_extractions,
            chapters=result.hierarchy_chapters,
            sections=result.hierarchy_sections,
        )

        return result

    async def _extract_chapter_level(
        self,
        hierarchy: DocumentHierarchy,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract at chapter level (methodology, workflow).

        Args:
            hierarchy: Document hierarchy with chapters.
            source_id: Source document ID.

        Returns:
            List of extraction results from chapter-level extraction.
        """
        results: list[ExtractionResult] = []
        config = EXTRACTION_LEVEL_CONFIG[ExtractionLevel.CHAPTER]

        # Filter to extraction types that run at chapter level
        chapter_types = [
            et for et in self.extraction_types
            if et.value in config.extraction_types
        ]

        if not chapter_types:
            logger.debug(
                "chapter_level_skipped",
                reason="no_matching_extraction_types",
                source_id=source_id,
            )
            return results

        # Process each chapter
        for chapter in hierarchy.get_chapter_nodes():
            chapter_results = await self._extract_from_chapter(
                chapter=chapter,
                source_id=source_id,
                extraction_types=chapter_types,
                max_tokens=config.max_tokens,
                strategy=config.combination_strategy,
            )
            results.extend(chapter_results)

        # Also process uncategorized chunks as a pseudo-chapter if any
        if hierarchy.uncategorized_chunks:
            uncategorized_results = await self._extract_from_uncategorized(
                chunks=hierarchy.uncategorized_chunks,
                source_id=source_id,
                extraction_types=chapter_types,
                level=ExtractionLevel.CHAPTER,
                max_tokens=config.max_tokens,
                strategy=config.combination_strategy,
            )
            results.extend(uncategorized_results)

        return results

    async def _extract_section_level(
        self,
        hierarchy: DocumentHierarchy,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract at section level (decision, pattern, checklist, persona).

        Args:
            hierarchy: Document hierarchy with sections.
            source_id: Source document ID.

        Returns:
            List of extraction results from section-level extraction.
        """
        results: list[ExtractionResult] = []
        config = EXTRACTION_LEVEL_CONFIG[ExtractionLevel.SECTION]

        # Filter to extraction types that run at section level
        section_types = [
            et for et in self.extraction_types
            if et.value in config.extraction_types
        ]

        if not section_types:
            logger.debug(
                "section_level_skipped",
                reason="no_matching_extraction_types",
                source_id=source_id,
            )
            return results

        # Process each section
        for section in hierarchy.get_section_nodes():
            section_results = await self._extract_from_section(
                section=section,
                source_id=source_id,
                extraction_types=section_types,
                max_tokens=config.max_tokens,
                strategy=config.combination_strategy,
            )
            results.extend(section_results)

        # Process uncategorized chunks in each chapter (have chapter but no section)
        for chapter in hierarchy.get_chapter_nodes():
            if chapter.uncategorized_chunks:
                uncategorized_results = await self._extract_from_uncategorized(
                    chunks=chapter.uncategorized_chunks,
                    source_id=source_id,
                    extraction_types=section_types,
                    level=ExtractionLevel.SECTION,
                    max_tokens=config.max_tokens,
                    strategy=config.combination_strategy,
                )
                results.extend(uncategorized_results)

        return results

    async def _extract_chunk_level(
        self,
        hierarchy: DocumentHierarchy,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract at chunk level (warning).

        Args:
            hierarchy: Document hierarchy with chunks.
            source_id: Source document ID.

        Returns:
            List of extraction results from chunk-level extraction.
        """
        results: list[ExtractionResult] = []
        config = EXTRACTION_LEVEL_CONFIG[ExtractionLevel.CHUNK]

        # Filter to extraction types that run at chunk level
        chunk_types = [
            et for et in self.extraction_types
            if et.value in config.extraction_types
        ]

        if not chunk_types:
            logger.debug(
                "chunk_level_skipped",
                reason="no_matching_extraction_types",
                source_id=source_id,
            )
            return results

        # Process each individual chunk
        all_chunks = hierarchy.all_chunks
        for chunk in all_chunks:
            chunk_results = await self._extract_from_single_chunk(
                chunk=chunk,
                source_id=source_id,
                extraction_types=chunk_types,
            )
            results.extend(chunk_results)

        return results

    async def _extract_from_chapter(
        self,
        chapter: ChapterNode,
        source_id: str,
        extraction_types: list[ExtractionType],
        max_tokens: int,
        strategy: str,
    ) -> list[ExtractionResult]:
        """Extract from a single chapter context.

        Combines chapter chunks and runs appropriate extractors.

        Args:
            chapter: Chapter node containing chunks.
            source_id: Source document ID.
            extraction_types: Extraction types to run.
            max_tokens: Token budget for combined content.
            strategy: Combination strategy.

        Returns:
            List of extraction results.
        """
        results: list[ExtractionResult] = []

        if not chapter.all_chunks:
            return results

        # Combine chapter chunks
        combined = combine_chunks(chapter.all_chunks, max_tokens, strategy)

        if not combined.content:
            return results

        logger.debug(
            "extracting_from_chapter",
            chapter_id=chapter.chapter_id,
            chapter_name=chapter.chapter_name,
            chunk_count=len(chapter.all_chunks),
            combined_tokens=combined.total_tokens,
            truncated=combined.truncated,
        )

        # Run each extractor
        for extraction_type in extraction_types:
            extractor = self._get_extractor(extraction_type)
            if extractor:
                type_results = await extractor.extract(
                    content=combined.content,
                    source_id=source_id,
                    context_level=ExtractionLevel.CHAPTER,
                    context_id=chapter.chapter_id,
                    chunk_ids=combined.chunk_ids,
                )
                results.extend(type_results)

        return results

    async def _extract_from_section(
        self,
        section: SectionNode,
        source_id: str,
        extraction_types: list[ExtractionType],
        max_tokens: int,
        strategy: str,
    ) -> list[ExtractionResult]:
        """Extract from a single section context.

        Combines section chunks and runs appropriate extractors.

        Args:
            section: Section node containing chunks.
            source_id: Source document ID.
            extraction_types: Extraction types to run.
            max_tokens: Token budget for combined content.
            strategy: Combination strategy.

        Returns:
            List of extraction results.
        """
        results: list[ExtractionResult] = []

        if not section.chunks:
            return results

        # Combine section chunks
        combined = combine_chunks(section.chunks, max_tokens, strategy)

        if not combined.content:
            return results

        logger.debug(
            "extracting_from_section",
            section_id=section.section_id,
            section_name=section.section_name,
            chapter_name=section.chapter_name,
            chunk_count=len(section.chunks),
            combined_tokens=combined.total_tokens,
            truncated=combined.truncated,
        )

        # Run each extractor
        for extraction_type in extraction_types:
            extractor = self._get_extractor(extraction_type)
            if extractor:
                type_results = await extractor.extract(
                    content=combined.content,
                    source_id=source_id,
                    context_level=ExtractionLevel.SECTION,
                    context_id=section.section_id,
                    chunk_ids=combined.chunk_ids,
                )
                results.extend(type_results)

        return results

    async def _extract_from_single_chunk(
        self,
        chunk: Chunk,
        source_id: str,
        extraction_types: list[ExtractionType],
    ) -> list[ExtractionResult]:
        """Extract from a single chunk.

        Args:
            chunk: Single chunk to extract from.
            source_id: Source document ID.
            extraction_types: Extraction types to run.

        Returns:
            List of extraction results.
        """
        results: list[ExtractionResult] = []

        if not chunk.content:
            return results

        logger.debug(
            "extracting_from_chunk",
            chunk_id=chunk.id,
            token_count=chunk.token_count,
        )

        # Run each extractor
        for extraction_type in extraction_types:
            extractor = self._get_extractor(extraction_type)
            if extractor:
                type_results = await extractor.extract(
                    content=chunk.content,
                    source_id=source_id,
                    context_level=ExtractionLevel.CHUNK,
                    context_id=chunk.id,
                    chunk_ids=[chunk.id],
                )
                results.extend(type_results)

        return results

    async def _extract_from_uncategorized(
        self,
        chunks: list[Chunk],
        source_id: str,
        extraction_types: list[ExtractionType],
        level: ExtractionLevel,
        max_tokens: int,
        strategy: str,
    ) -> list[ExtractionResult]:
        """Extract from uncategorized chunks at a given level.

        For chunks without chapter/section metadata, we still extract
        by combining them according to the level's token budget.

        Args:
            chunks: Uncategorized chunks to process.
            source_id: Source document ID.
            extraction_types: Extraction types to run.
            level: Extraction level for context_level field.
            max_tokens: Token budget for combined content.
            strategy: Combination strategy.

        Returns:
            List of extraction results.
        """
        results: list[ExtractionResult] = []

        if not chunks:
            return results

        # Combine uncategorized chunks
        combined = combine_chunks(chunks, max_tokens, strategy)

        if not combined.content:
            return results

        # Generate a context ID for uncategorized content
        context_id = f"uncategorized_{source_id}_{level.value}"

        logger.debug(
            "extracting_from_uncategorized",
            source_id=source_id,
            level=level.value,
            chunk_count=len(chunks),
            combined_tokens=combined.total_tokens,
        )

        # Run each extractor
        for extraction_type in extraction_types:
            extractor = self._get_extractor(extraction_type)
            if extractor:
                type_results = await extractor.extract(
                    content=combined.content,
                    source_id=source_id,
                    context_level=level,
                    context_id=context_id,
                    chunk_ids=combined.chunk_ids,
                )
                results.extend(type_results)

        return results

    def _get_extractor(self, extraction_type: ExtractionType) -> Optional[BaseExtractor]:
        """Get extractor instance for a given type.

        Args:
            extraction_type: The extraction type to get extractor for.

        Returns:
            Extractor instance or None if not registered.
        """
        try:
            return extractor_registry.get_extractor(extraction_type)
        except Exception as e:
            logger.warning(
                "extractor_not_found",
                extraction_type=extraction_type.value,
                error=str(e),
            )
            return None

    def _update_stats(
        self,
        result: HierarchicalExtractionResult,
        level_results: list[ExtractionResult],
        level: ExtractionLevel,
    ) -> None:
        """Update statistics for a level.

        Args:
            result: Overall extraction result to update.
            level_results: Results from this level.
            level: The extraction level.
        """
        stats = result.stats_by_level[level]
        stats.extractions_attempted += len(level_results)
        stats.extractions_successful += sum(1 for r in level_results if r.success)
        stats.extractions_failed += sum(1 for r in level_results if not r.success)
