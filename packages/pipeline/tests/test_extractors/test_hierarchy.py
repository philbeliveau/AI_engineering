"""Tests for document hierarchy builder."""

import pytest

from src.extractors.hierarchy import (
    ChapterNode,
    CombinedContent,
    DocumentHierarchy,
    SectionNode,
    _generate_id,
    build_hierarchy,
    combine_chunks,
)
from src.models.chunk import Chunk, ChunkPosition


def make_chunk(
    chunk_id: str,
    source_id: str = "507f1f77bcf86cd799439011",
    content: str | None = None,
    chapter: str | None = None,
    section: str | None = None,
    page: int | None = None,
    token_count: int = 100,
) -> Chunk:
    """Factory for creating test chunks.

    Content is auto-generated to be longer than token_count to pass validation.
    """
    # Generate content longer than token_count if not provided
    # Chunk model validates token_count <= len(content)
    if content is None:
        content = "x" * (token_count + 50)
    elif len(content) < token_count:
        content = content + "x" * (token_count - len(content) + 50)

    return Chunk(
        id=chunk_id,
        source_id=source_id,
        content=content,
        position=ChunkPosition(chapter=chapter, section=section, page=page),
        token_count=token_count,
    )


class TestGenerateId:
    """Tests for _generate_id function."""

    def test_generates_24_char_hex(self):
        """Generated IDs should be 24 hex characters (MongoDB ObjectId compatible)."""
        result = _generate_id("source123", "chapter", "Chapter 1")
        assert len(result) == 24
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic(self):
        """Same inputs should produce same ID."""
        id1 = _generate_id("source123", "chapter", "Chapter 1")
        id2 = _generate_id("source123", "chapter", "Chapter 1")
        assert id1 == id2

    def test_different_sources_different_ids(self):
        """Different source IDs should produce different IDs."""
        id1 = _generate_id("source123", "chapter", "Chapter 1")
        id2 = _generate_id("source456", "chapter", "Chapter 1")
        assert id1 != id2

    def test_different_types_different_ids(self):
        """Different context types should produce different IDs."""
        id1 = _generate_id("source123", "chapter", "Chapter 1")
        id2 = _generate_id("source123", "section", "Chapter 1")
        assert id1 != id2

    def test_different_names_different_ids(self):
        """Different names should produce different IDs."""
        id1 = _generate_id("source123", "chapter", "Chapter 1")
        id2 = _generate_id("source123", "chapter", "Chapter 2")
        assert id1 != id2


class TestSectionNode:
    """Tests for SectionNode dataclass."""

    def test_chunk_ids_property(self):
        """chunk_ids should return list of all chunk IDs."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001")
        chunk2 = make_chunk("507f1f77bcf86cd799439002")
        section = SectionNode(
            section_id="section1",
            section_name="Introduction",
            chapter_name="Chapter 1",
            chunks=[chunk1, chunk2],
        )
        assert section.chunk_ids == ["507f1f77bcf86cd799439001", "507f1f77bcf86cd799439002"]

    def test_total_tokens_property(self):
        """total_tokens should sum token counts."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001", token_count=100)
        chunk2 = make_chunk("507f1f77bcf86cd799439002", token_count=150)
        section = SectionNode(
            section_id="section1",
            section_name="Introduction",
            chapter_name="Chapter 1",
            chunks=[chunk1, chunk2],
        )
        assert section.total_tokens == 250

    def test_empty_section(self):
        """Empty section should have empty lists and zero tokens."""
        section = SectionNode(
            section_id="section1",
            section_name="Empty",
            chapter_name="Chapter 1",
        )
        assert section.chunk_ids == []
        assert section.total_tokens == 0


class TestChapterNode:
    """Tests for ChapterNode dataclass."""

    def test_all_chunks_includes_sections_and_uncategorized(self):
        """all_chunks should include chunks from all sections and uncategorized."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001")
        chunk2 = make_chunk("507f1f77bcf86cd799439002")
        chunk3 = make_chunk("507f1f77bcf86cd799439003")

        section = SectionNode(
            section_id="section1",
            section_name="Intro",
            chapter_name="Chapter 1",
            chunks=[chunk1, chunk2],
        )

        chapter = ChapterNode(
            chapter_id="chapter1",
            chapter_name="Chapter 1",
            sections={"Intro": section},
            uncategorized_chunks=[chunk3],
        )

        all_chunks = chapter.all_chunks
        assert len(all_chunks) == 3
        assert all(c.id in ["507f1f77bcf86cd799439001", "507f1f77bcf86cd799439002", "507f1f77bcf86cd799439003"] for c in all_chunks)

    def test_chunk_ids_property(self):
        """chunk_ids should return all chunk IDs in chapter."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001")
        chunk2 = make_chunk("507f1f77bcf86cd799439002")

        section = SectionNode(
            section_id="section1",
            section_name="Intro",
            chapter_name="Chapter 1",
            chunks=[chunk1],
        )

        chapter = ChapterNode(
            chapter_id="chapter1",
            chapter_name="Chapter 1",
            sections={"Intro": section},
            uncategorized_chunks=[chunk2],
        )

        chunk_ids = chapter.chunk_ids
        assert "507f1f77bcf86cd799439001" in chunk_ids
        assert "507f1f77bcf86cd799439002" in chunk_ids

    def test_total_tokens_property(self):
        """total_tokens should sum all chunks in chapter."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001", token_count=100)
        chunk2 = make_chunk("507f1f77bcf86cd799439002", token_count=200)

        section = SectionNode(
            section_id="section1",
            section_name="Intro",
            chapter_name="Chapter 1",
            chunks=[chunk1],
        )

        chapter = ChapterNode(
            chapter_id="chapter1",
            chapter_name="Chapter 1",
            sections={"Intro": section},
            uncategorized_chunks=[chunk2],
        )

        assert chapter.total_tokens == 300


class TestDocumentHierarchy:
    """Tests for DocumentHierarchy dataclass."""

    def test_all_chunks_includes_everything(self):
        """all_chunks should include all chunks in document."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001")
        chunk2 = make_chunk("507f1f77bcf86cd799439002")
        chunk3 = make_chunk("507f1f77bcf86cd799439003")

        section = SectionNode(
            section_id="section1",
            section_name="Intro",
            chapter_name="Chapter 1",
            chunks=[chunk1],
        )

        chapter = ChapterNode(
            chapter_id="chapter1",
            chapter_name="Chapter 1",
            sections={"Intro": section},
            uncategorized_chunks=[chunk2],
        )

        hierarchy = DocumentHierarchy(
            source_id="source1",
            chapters={"Chapter 1": chapter},
            uncategorized_chunks=[chunk3],
        )

        assert hierarchy.chunk_count == 3

    def test_chapter_count(self):
        """chapter_count should return number of chapters."""
        chapter1 = ChapterNode(chapter_id="ch1", chapter_name="Chapter 1")
        chapter2 = ChapterNode(chapter_id="ch2", chapter_name="Chapter 2")

        hierarchy = DocumentHierarchy(
            source_id="source1",
            chapters={"Chapter 1": chapter1, "Chapter 2": chapter2},
        )

        assert hierarchy.chapter_count == 2

    def test_section_count(self):
        """section_count should count sections across all chapters."""
        section1 = SectionNode(
            section_id="s1", section_name="Intro", chapter_name="Chapter 1"
        )
        section2 = SectionNode(
            section_id="s2", section_name="Methods", chapter_name="Chapter 1"
        )
        section3 = SectionNode(
            section_id="s3", section_name="Results", chapter_name="Chapter 2"
        )

        chapter1 = ChapterNode(
            chapter_id="ch1",
            chapter_name="Chapter 1",
            sections={"Intro": section1, "Methods": section2},
        )
        chapter2 = ChapterNode(
            chapter_id="ch2",
            chapter_name="Chapter 2",
            sections={"Results": section3},
        )

        hierarchy = DocumentHierarchy(
            source_id="source1",
            chapters={"Chapter 1": chapter1, "Chapter 2": chapter2},
        )

        assert hierarchy.section_count == 3

    def test_get_chapter_nodes(self):
        """get_chapter_nodes should return sorted list of chapters."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001")
        chunk2 = make_chunk("507f1f77bcf86cd799439099")

        chapter1 = ChapterNode(
            chapter_id="ch1",
            chapter_name="Chapter 1",
            uncategorized_chunks=[chunk1],
        )
        chapter2 = ChapterNode(
            chapter_id="ch2",
            chapter_name="Chapter 2",
            uncategorized_chunks=[chunk2],
        )

        hierarchy = DocumentHierarchy(
            source_id="source1",
            chapters={"Chapter 2": chapter2, "Chapter 1": chapter1},
        )

        chapters = hierarchy.get_chapter_nodes()
        assert len(chapters) == 2
        # First chunk ID is smaller, so Chapter 1 should come first
        assert chapters[0].chapter_name == "Chapter 1"

    def test_get_section_nodes(self):
        """get_section_nodes should return all sections across chapters."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001")
        chunk2 = make_chunk("507f1f77bcf86cd799439002")

        section1 = SectionNode(
            section_id="s1",
            section_name="Intro",
            chapter_name="Chapter 1",
            chunks=[chunk1],
        )
        section2 = SectionNode(
            section_id="s2",
            section_name="Methods",
            chapter_name="Chapter 2",
            chunks=[chunk2],
        )

        chapter1 = ChapterNode(
            chapter_id="ch1",
            chapter_name="Chapter 1",
            sections={"Intro": section1},
        )
        chapter2 = ChapterNode(
            chapter_id="ch2",
            chapter_name="Chapter 2",
            sections={"Methods": section2},
        )

        hierarchy = DocumentHierarchy(
            source_id="source1",
            chapters={"Chapter 1": chapter1, "Chapter 2": chapter2},
        )

        sections = hierarchy.get_section_nodes()
        assert len(sections) == 2


class TestBuildHierarchy:
    """Tests for build_hierarchy function."""

    def test_groups_by_chapter(self):
        """Chunks should be grouped by chapter."""
        source_id = "507f1f77bcf86cd799439011"
        chunk1 = make_chunk(
            "507f1f77bcf86cd799439001",
            source_id=source_id,
            chapter="Chapter 1",
        )
        chunk2 = make_chunk(
            "507f1f77bcf86cd799439002",
            source_id=source_id,
            chapter="Chapter 1",
        )
        chunk3 = make_chunk(
            "507f1f77bcf86cd799439003",
            source_id=source_id,
            chapter="Chapter 2",
        )

        hierarchy = build_hierarchy([chunk1, chunk2, chunk3], source_id)

        assert hierarchy.chapter_count == 2
        assert "Chapter 1" in hierarchy.chapters
        assert "Chapter 2" in hierarchy.chapters
        assert len(hierarchy.chapters["Chapter 1"].all_chunks) == 2
        assert len(hierarchy.chapters["Chapter 2"].all_chunks) == 1

    def test_groups_by_section_within_chapter(self):
        """Chunks should be grouped by section within chapter."""
        source_id = "507f1f77bcf86cd799439011"
        chunk1 = make_chunk(
            "507f1f77bcf86cd799439001",
            source_id=source_id,
            chapter="Chapter 1",
            section="Introduction",
        )
        chunk2 = make_chunk(
            "507f1f77bcf86cd799439002",
            source_id=source_id,
            chapter="Chapter 1",
            section="Methods",
        )

        hierarchy = build_hierarchy([chunk1, chunk2], source_id)

        chapter = hierarchy.chapters["Chapter 1"]
        assert len(chapter.sections) == 2
        assert "Introduction" in chapter.sections
        assert "Methods" in chapter.sections

    def test_uncategorized_chunks_no_chapter(self):
        """Chunks without chapter go to document-level uncategorized."""
        source_id = "507f1f77bcf86cd799439011"
        chunk1 = make_chunk(
            "507f1f77bcf86cd799439001",
            source_id=source_id,
            chapter=None,
        )

        hierarchy = build_hierarchy([chunk1], source_id)

        assert hierarchy.chapter_count == 0
        assert len(hierarchy.uncategorized_chunks) == 1
        assert hierarchy.uncategorized_chunks[0].id == "507f1f77bcf86cd799439001"

    def test_uncategorized_chunks_no_section(self):
        """Chunks with chapter but no section go to chapter-level uncategorized."""
        source_id = "507f1f77bcf86cd799439011"
        chunk1 = make_chunk(
            "507f1f77bcf86cd799439001",
            source_id=source_id,
            chapter="Chapter 1",
            section=None,
        )

        hierarchy = build_hierarchy([chunk1], source_id)

        chapter = hierarchy.chapters["Chapter 1"]
        assert len(chapter.sections) == 0
        assert len(chapter.uncategorized_chunks) == 1

    def test_empty_chunks_list(self):
        """Empty chunks list should return empty hierarchy."""
        source_id = "507f1f77bcf86cd799439011"
        hierarchy = build_hierarchy([], source_id)

        assert hierarchy.source_id == source_id
        assert hierarchy.chapter_count == 0
        assert hierarchy.section_count == 0
        assert hierarchy.chunk_count == 0

    def test_generates_stable_chapter_ids(self):
        """Chapter IDs should be stable across multiple builds."""
        source_id = "507f1f77bcf86cd799439011"
        chunk1 = make_chunk(
            "507f1f77bcf86cd799439001",
            source_id=source_id,
            chapter="Chapter 1",
        )

        hierarchy1 = build_hierarchy([chunk1], source_id)
        hierarchy2 = build_hierarchy([chunk1], source_id)

        assert hierarchy1.chapters["Chapter 1"].chapter_id == hierarchy2.chapters["Chapter 1"].chapter_id

    def test_generates_stable_section_ids(self):
        """Section IDs should be stable across multiple builds."""
        source_id = "507f1f77bcf86cd799439011"
        chunk1 = make_chunk(
            "507f1f77bcf86cd799439001",
            source_id=source_id,
            chapter="Chapter 1",
            section="Introduction",
        )

        hierarchy1 = build_hierarchy([chunk1], source_id)
        hierarchy2 = build_hierarchy([chunk1], source_id)

        section1 = hierarchy1.chapters["Chapter 1"].sections["Introduction"]
        section2 = hierarchy2.chapters["Chapter 1"].sections["Introduction"]
        assert section1.section_id == section2.section_id

    def test_mixed_metadata_chunks(self):
        """Handle mix of chunks with different metadata levels."""
        source_id = "507f1f77bcf86cd799439011"

        # Full metadata
        chunk1 = make_chunk(
            "507f1f77bcf86cd799439001",
            source_id=source_id,
            chapter="Chapter 1",
            section="Intro",
        )
        # Chapter only
        chunk2 = make_chunk(
            "507f1f77bcf86cd799439002",
            source_id=source_id,
            chapter="Chapter 1",
            section=None,
        )
        # No metadata
        chunk3 = make_chunk(
            "507f1f77bcf86cd799439003",
            source_id=source_id,
            chapter=None,
        )

        hierarchy = build_hierarchy([chunk1, chunk2, chunk3], source_id)

        assert hierarchy.chapter_count == 1
        chapter = hierarchy.chapters["Chapter 1"]
        assert len(chapter.sections) == 1
        assert len(chapter.uncategorized_chunks) == 1
        assert len(hierarchy.uncategorized_chunks) == 1

    def test_preserves_chunk_data(self):
        """Chunks in hierarchy should have all original data."""
        source_id = "507f1f77bcf86cd799439011"
        # Content must be longer than token_count to pass Chunk validation
        content = "x" * 200
        chunk = make_chunk(
            "507f1f77bcf86cd799439001",
            source_id=source_id,
            content=content,
            chapter="Chapter 1",
            section="Intro",
            page=5,
            token_count=150,
        )

        hierarchy = build_hierarchy([chunk], source_id)
        stored_chunk = hierarchy.chapters["Chapter 1"].sections["Intro"].chunks[0]

        assert stored_chunk.id == "507f1f77bcf86cd799439001"
        assert stored_chunk.content == content
        assert stored_chunk.position.page == 5
        assert stored_chunk.token_count == 150


class TestCombinedContent:
    """Tests for CombinedContent dataclass."""

    def test_creation(self):
        """Should create with all fields."""
        result = CombinedContent(
            content="test content",
            chunk_ids=["id1", "id2"],
            total_tokens=100,
            truncated=False,
        )
        assert result.content == "test content"
        assert result.chunk_ids == ["id1", "id2"]
        assert result.total_tokens == 100
        assert result.truncated is False

    def test_truncated_default_false(self):
        """Truncated should default to False."""
        result = CombinedContent(
            content="test",
            chunk_ids=["id1"],
            total_tokens=50,
        )
        assert result.truncated is False


class TestCombineChunks:
    """Tests for combine_chunks function."""

    def test_empty_chunks_list(self):
        """Empty chunks should return empty result."""
        result = combine_chunks([], max_tokens=1000)
        assert result.content == ""
        assert result.chunk_ids == []
        assert result.total_tokens == 0
        assert result.truncated is False

    def test_single_chunk_within_limit(self):
        """Single chunk within limit should be returned as-is."""
        chunk = make_chunk(
            "507f1f77bcf86cd799439001",
            token_count=100,
        )
        result = combine_chunks([chunk], max_tokens=500)

        assert chunk.content in result.content
        assert result.chunk_ids == ["507f1f77bcf86cd799439001"]
        assert result.total_tokens == 100
        assert result.truncated is False

    def test_multiple_chunks_within_limit(self):
        """Multiple chunks within limit should be combined."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001", token_count=100)
        chunk2 = make_chunk("507f1f77bcf86cd799439002", token_count=100)

        result = combine_chunks([chunk1, chunk2], max_tokens=500)

        assert result.total_tokens == 200
        assert len(result.chunk_ids) == 2
        assert result.truncated is False
        # Content should contain both chunks separated by newlines
        assert "\n\n" in result.content

    def test_truncate_strategy_excludes_chunks(self):
        """Truncate strategy should exclude chunks that exceed limit."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001", token_count=100)
        chunk2 = make_chunk("507f1f77bcf86cd799439002", token_count=100)
        chunk3 = make_chunk("507f1f77bcf86cd799439003", token_count=100)

        result = combine_chunks([chunk1, chunk2, chunk3], max_tokens=150, strategy="truncate")

        # Only first chunk should be included (100 tokens < 150 limit)
        # Second chunk would push to 200, exceeding limit
        assert len(result.chunk_ids) == 1
        assert result.chunk_ids == ["507f1f77bcf86cd799439001"]
        assert result.total_tokens == 100
        assert result.truncated is True

    def test_truncate_strategy_first_chunk_too_large(self):
        """If first chunk exceeds limit, include partial content."""
        # Create a chunk with lots of tokens
        chunk = make_chunk("507f1f77bcf86cd799439001", token_count=500)

        result = combine_chunks([chunk], max_tokens=100, strategy="truncate")

        # Should include partial content
        assert result.truncated is True
        assert result.chunk_ids == ["507f1f77bcf86cd799439001"]
        # Content should be shorter than original
        assert len(result.content) < len(chunk.content)

    def test_none_strategy_ignores_limit(self):
        """None strategy should return all content regardless of limit."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001", token_count=100)
        chunk2 = make_chunk("507f1f77bcf86cd799439002", token_count=100)

        result = combine_chunks([chunk1, chunk2], max_tokens=50, strategy="none")

        # Both chunks included despite exceeding limit
        assert len(result.chunk_ids) == 2
        assert result.total_tokens == 200
        assert result.truncated is False

    def test_summary_if_exceeded_falls_back_to_truncate(self):
        """summary_if_exceeded should fall back to truncation for now."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001", token_count=100)
        chunk2 = make_chunk("507f1f77bcf86cd799439002", token_count=100)

        result = combine_chunks(
            [chunk1, chunk2], max_tokens=150, strategy="summary_if_exceeded"
        )

        # Should behave like truncate
        assert len(result.chunk_ids) == 1
        assert result.truncated is True

    def test_invalid_strategy_raises_error(self):
        """Invalid strategy should raise ValueError."""
        chunk = make_chunk("507f1f77bcf86cd799439001", token_count=100)

        with pytest.raises(ValueError) as exc_info:
            combine_chunks([chunk], max_tokens=500, strategy="invalid")

        assert "Unknown combination strategy" in str(exc_info.value)

    def test_chunks_sorted_by_index(self):
        """Chunks should be sorted by index before combining."""
        # Create chunks with IDs that sort in reverse order
        chunk1 = make_chunk("507f1f77bcf86cd799439099", token_count=50)  # Higher ID
        chunk2 = make_chunk("507f1f77bcf86cd799439001", token_count=50)  # Lower ID

        result = combine_chunks([chunk1, chunk2], max_tokens=500)

        # Lower ID (chunk2) should come first
        assert result.chunk_ids[0] == "507f1f77bcf86cd799439001"
        assert result.chunk_ids[1] == "507f1f77bcf86cd799439099"

    def test_exact_limit_fit(self):
        """Chunks that exactly fit should all be included."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001", token_count=50)
        chunk2 = make_chunk("507f1f77bcf86cd799439002", token_count=50)

        result = combine_chunks([chunk1, chunk2], max_tokens=100, strategy="truncate")

        assert len(result.chunk_ids) == 2
        assert result.total_tokens == 100
        assert result.truncated is False

    def test_content_separated_by_double_newlines(self):
        """Combined content should have double newline separators."""
        chunk1 = make_chunk("507f1f77bcf86cd799439001", token_count=10)
        chunk2 = make_chunk("507f1f77bcf86cd799439002", token_count=10)

        # Replace default content with identifiable strings
        chunk1_content = "FIRST_CHUNK_CONTENT"
        chunk2_content = "SECOND_CHUNK_CONTENT"

        # Create new chunks with specific content
        chunk1 = Chunk(
            id="507f1f77bcf86cd799439001",
            source_id="507f1f77bcf86cd799439011",
            content=chunk1_content + "x" * 100,
            position=ChunkPosition(),
            token_count=10,
        )
        chunk2 = Chunk(
            id="507f1f77bcf86cd799439002",
            source_id="507f1f77bcf86cd799439011",
            content=chunk2_content + "x" * 100,
            position=ChunkPosition(),
            token_count=10,
        )

        result = combine_chunks([chunk1, chunk2], max_tokens=500)

        assert "\n\n" in result.content
        assert "FIRST_CHUNK_CONTENT" in result.content
        assert "SECOND_CHUNK_CONTENT" in result.content
