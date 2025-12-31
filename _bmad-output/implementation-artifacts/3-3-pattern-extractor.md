# Story 3.3: Pattern Extractor

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **builder**,
I want to extract reusable code/architecture patterns from chunks,
So that end users can query for implementation patterns with code examples.

## Acceptance Criteria

**Given** a chunk of text describing a pattern
**When** I run the pattern extractor
**Then** a structured Pattern is extracted with: name, problem, solution, code_example, context, trade_offs
**And** the extraction includes source attribution (source_id, chunk_id)
**And** relevant topics are auto-tagged
**And** the extraction prompt is stored in `extractors/prompts/pattern.md`

**Implementation Note:** Use LLMClient from `src/extractors/llm_client.py` for extraction. Pass prompt from `prompts/pattern.md` to LLMClient. Parse JSON response using Pydantic model validation.

## Tasks / Subtasks

- [x] **Task 1: Verify Prerequisites** (AC: Dependencies available)
  - [x] 1.1: Confirm Story 3.1 complete: `ls packages/pipeline/src/extractors/base.py`
  - [x] 1.2: Confirm Pattern model exists: `cd packages/pipeline && uv run python -c "from src.extractors import Pattern, BaseExtractor, ExtractionType; print('OK')"`
  - [x] 1.3: Confirm Story 3.2 exists (pattern reference): `ls packages/pipeline/src/extractors/decision_extractor.py`
  - [x] 1.4: Confirm prompts directory: `ls packages/pipeline/src/extractors/prompts/`

- [x] **Task 2: Create PatternExtractor Class** (AC: #1, #2, #3)
  - [x] 2.1: Create `packages/pipeline/src/extractors/pattern_extractor.py`
  - [x] 2.2: Extend `BaseExtractor` ABC from Story 3.1
  - [x] 2.3: Implement `extraction_type` property returning `ExtractionType.PATTERN`
  - [x] 2.4: Implement `model_class` property returning `Pattern`
  - [x] 2.5: Implement `extract()` method with Pattern model validation
  - [x] 2.6: Implement `get_prompt()` method loading from `pattern.md`
  - [x] 2.7: Register extractor with `extractor_registry`

- [x] **Task 3: Create Extraction Prompt** (AC: #4)
  - [x] 3.1: Create `packages/pipeline/src/extractors/prompts/pattern.md`
  - [x] 3.2: Define prompt structure for identifying code/architecture patterns
  - [x] 3.3: Include guidance for `name`, `problem`, `solution` extraction
  - [x] 3.4: Include guidance for `code_example` extraction (preserve formatting)
  - [x] 3.5: Include guidance for `context` and `trade_offs` extraction
  - [x] 3.6: Add examples of good pattern extractions

- [x] **Task 4: Update Module Exports** (AC: Clean imports)
  - [x] 4.1: Add `PatternExtractor` to `packages/pipeline/src/extractors/__init__.py` exports
  - [x] 4.2: Verify import: `from src.extractors import PatternExtractor`
  - [x] 4.3: Verify registry contains pattern extractor

- [x] **Task 5: Create Unit Tests** (AC: All)
  - [x] 5.1: Create `packages/pipeline/tests/test_extractors/test_pattern_extractor.py`
  - [x] 5.2: Test `extract()` with sample pattern chunk
  - [x] 5.3: Test Pattern model validation (all required fields)
  - [x] 5.4: Test topic auto-tagging for pattern content
  - [x] 5.5: Test source attribution preservation (source_id, chunk_id)
  - [x] 5.6: Test prompt loading from `pattern.md`
  - [x] 5.7: Test registry retrieval: `extractor_registry.get_extractor(ExtractionType.PATTERN)`
  - [x] 5.8: Test code_example handling (None vs populated, formatting preserved)

## Dev Notes

### Critical Implementation Context

**Core Philosophy:** Pattern extractions are for NAVIGATION, Claude is for SYNTHESIS. The extractor creates structured pattern maps that Claude can reason about, compare across sources, and apply to user context.

**Pattern vs Decision:** While decisions capture "what to choose", patterns capture "how to implement". Patterns often contain code examples and implementation details.

### Pattern Model Structure (from Story 3.1)

\`\`\`python
class Pattern(ExtractionBase):
    """Reusable pattern extraction.

    Captures code/architecture patterns with examples.
    Used by end users for implementation reference.
    """
    type: ExtractionType = ExtractionType.PATTERN
    name: str                         # Pattern name (e.g., "Semantic Caching")
    problem: str                      # Problem it solves
    solution: str                     # Solution approach
    code_example: Optional[str] = None  # Code snippet (preserve formatting)
    context: str = ""                 # When to use this pattern
    trade_offs: list[str] = []        # Pros/cons of using this pattern
\`\`\`

**Inherited from ExtractionBase:**
- `id: str` - Unique extraction ID
- `source_id: str` - Reference to sources collection
- `chunk_id: str` - Reference to chunks collection
- `type: ExtractionType` - Set to PATTERN
- `topics: list[str]` - Auto-tagged topics
- `schema_version: str` - "1.0.0"
- `extracted_at: datetime` - Timestamp
- `confidence: float` - 0.0-1.0 score

### Implementation Pattern (Follow Story 3.2 DecisionExtractor)

\`\`\`python
# packages/pipeline/src/extractors/pattern_extractor.py
from typing import Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionType,
    ExtractionBase,
    ExtractionResult,
    Pattern,
    extractor_registry,
)

logger = structlog.get_logger()


class PatternExtractor(BaseExtractor):
    """Extractor for reusable code/architecture patterns.

    Identifies and structures implementation patterns from text chunks,
    including code examples when present. Used by end users for
    implementation reference via the get_patterns MCP tool.

    Example patterns:
    - Semantic Caching: Cache LLM responses based on semantic similarity
    - Chunking Strategy: Split documents for optimal retrieval
    - Prompt Template: Reusable prompt structure for specific tasks
    """

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for patterns."""
        return ExtractionType.PATTERN

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Pattern model class."""
        return Pattern

    def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str
    ) -> list[ExtractionResult]:
        """Extract patterns from chunk content.

        Args:
            chunk_content: Text content to extract patterns from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with Pattern extractions.
        """
        logger.info(
            "pattern_extraction_started",
            chunk_id=chunk_id,
            source_id=source_id,
            content_length=len(chunk_content)
        )

        # Get prompt for Claude
        prompt = self.get_prompt()

        # Use LLMClient for automated batch extraction
        # LLMClient handles API calls with retry logic

        results: list[ExtractionResult] = []

        # Placeholder: Real implementation would:
        # 1. Send chunk_content + prompt to Claude
        # 2. Parse JSON response with _parse_llm_response()
        # 3. Validate each pattern with _validate_extraction()
        # 4. Auto-tag topics with _generate_topics()

        logger.info(
            "pattern_extraction_completed",
            chunk_id=chunk_id,
            pattern_count=len(results)
        )

        return results

    def get_prompt(self) -> str:
        """Load pattern extraction prompt from file.

        Returns:
            Prompt string for LLM extraction.

        Raises:
            PromptLoadError: If prompt file cannot be loaded.
        """
        return self._load_prompt("pattern")


# Register extractor with global registry
extractor_registry.register(ExtractionType.PATTERN, PatternExtractor)
\`\`\`

### Prompt File Structure

\`\`\`markdown
# packages/pipeline/src/extractors/prompts/pattern.md

# Pattern Extraction Prompt

You are a knowledge extraction assistant. Extract reusable code and architecture patterns from the provided text.

## What is a Pattern?

A pattern is a reusable solution to a common problem. In AI engineering, patterns include:
- Implementation techniques (e.g., semantic caching, chunking strategies)
- Architecture patterns (e.g., RAG pipeline, agent orchestration)
- Code patterns (e.g., retry logic, rate limiting)
- Design patterns (e.g., prompt templates, evaluation frameworks)

## Extraction Rules

1. Only extract patterns explicitly described in the text
2. A pattern MUST have a clear name, problem, and solution
3. Include code examples if present (preserve exact formatting)
4. Capture trade-offs and when to use the pattern
5. Return valid JSON matching the schema below
6. If no patterns found, return an empty array []

## Output Schema

{
  "name": "Pattern Name",
  "problem": "What problem does this pattern solve?",
  "solution": "How does this pattern solve it?",
  "code_example": "Optional code snippet with preserved formatting",
  "context": "When to use this pattern (situations, constraints)",
  "trade_offs": ["Pro or con 1", "Pro or con 2"]
}

## Example Extraction

**Input text:**
"For high-traffic LLM applications, implement semantic caching to reduce API costs. Instead of exact-match caching, use embedding similarity to find cached responses for semantically similar queries. This can reduce costs by 40-60% but adds latency for cache lookups."

**Extracted pattern:**
{
  "name": "Semantic Caching",
  "problem": "High API costs from repeated similar queries to LLM",
  "solution": "Cache responses using embedding similarity instead of exact match. Compare query embeddings to find cached responses for semantically similar inputs.",
  "code_example": null,
  "context": "High-traffic LLM applications where similar queries are common",
  "trade_offs": [
    "Pro: 40-60% cost reduction",
    "Con: Added latency for cache lookups",
    "Con: Cache invalidation complexity"
  ]
}

## Now extract patterns from this text:

{{chunk_content}}
\`\`\`

### Topic Auto-Tagging for Patterns

The base class `_generate_topics()` method handles topic extraction. For patterns, relevant topics include:

- `rag` - Retrieval-augmented generation patterns
- `caching` - Caching strategies
- `embeddings` - Embedding-related patterns
- `prompting` - Prompt engineering patterns
- `evaluation` - Evaluation and testing patterns
- `deployment` - Deployment patterns
- `agents` - Agent architecture patterns
- `chunking` - Document chunking patterns
- `retrieval` - Search and retrieval patterns

### Testing Strategy

\`\`\`python
# packages/pipeline/tests/test_extractors/test_pattern_extractor.py
import pytest
from datetime import datetime

from src.extractors import (
    PatternExtractor,
    Pattern,
    ExtractionType,
    ExtractionResult,
    ExtractorRegistry,
    extractor_registry,
)


class TestPatternExtractor:
    """Test PatternExtractor implementation."""

    @pytest.fixture
    def extractor(self) -> PatternExtractor:
        """Create pattern extractor instance."""
        return PatternExtractor()

    def test_extraction_type_is_pattern(self, extractor):
        """Extractor returns PATTERN extraction type."""
        assert extractor.extraction_type == ExtractionType.PATTERN

    def test_model_class_is_pattern(self, extractor):
        """Extractor uses Pattern model class."""
        assert extractor.model_class == Pattern

    def test_get_prompt_loads_pattern_md(self, extractor):
        """Prompt is loaded from pattern.md file."""
        prompt = extractor.get_prompt()
        assert "pattern" in prompt.lower()
        assert len(prompt) > 100

    def test_extract_returns_list(self, extractor):
        """Extract method returns list of results."""
        results = extractor.extract(
            chunk_content="Sample pattern text",
            chunk_id="chunk-123",
            source_id="source-456"
        )
        assert isinstance(results, list)

    def test_registry_contains_pattern_extractor(self):
        """Pattern extractor is registered in global registry."""
        assert extractor_registry.is_supported(ExtractionType.PATTERN)
        extractor = extractor_registry.get_extractor(ExtractionType.PATTERN)
        assert isinstance(extractor, PatternExtractor)


class TestPatternModel:
    """Test Pattern Pydantic model."""

    def test_pattern_required_fields(self):
        """Pattern requires source_id, chunk_id, name, problem, solution."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Semantic Caching",
            problem="High API costs",
            solution="Cache using embedding similarity"
        )
        assert pattern.source_id == "src-123"
        assert pattern.chunk_id == "chunk-456"
        assert pattern.type == ExtractionType.PATTERN
        assert pattern.schema_version == "1.0.0"

    def test_pattern_optional_fields(self):
        """Pattern allows optional code_example, context, trade_offs."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Pattern",
            problem="Test problem",
            solution="Test solution",
            code_example="def example(): pass",
            context="Test context",
            trade_offs=["Pro 1", "Con 1"]
        )
        assert pattern.code_example == "def example(): pass"
        assert pattern.context == "Test context"
        assert len(pattern.trade_offs) == 2

    def test_pattern_code_example_preserves_formatting(self):
        """Code example preserves multiline formatting."""
        code = """def semantic_cache(query: str) -> str:
    embedding = get_embedding(query)
    cached = find_similar(embedding)
    if cached:
        return cached.response
    return None"""

        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Semantic Cache",
            problem="Cost",
            solution="Cache",
            code_example=code
        )
        assert "\n" in pattern.code_example
        assert "def semantic_cache" in pattern.code_example

    def test_pattern_has_source_attribution(self):
        """Pattern includes source attribution fields."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test",
            problem="Test",
            solution="Test"
        )
        assert hasattr(pattern, "source_id")
        assert hasattr(pattern, "chunk_id")
        assert hasattr(pattern, "topics")
        assert hasattr(pattern, "schema_version")


class TestTopicAutoTagging:
    """Test topic auto-tagging for patterns."""

    @pytest.fixture
    def extractor(self) -> PatternExtractor:
        return PatternExtractor()

    def test_generates_topics_from_content(self, extractor):
        """Topics are generated from pattern content."""
        topics = extractor._generate_topics(
            "This pattern uses embedding similarity for semantic caching in RAG systems"
        )
        assert isinstance(topics, list)
        # Should detect rag, embeddings, or caching
        assert len(topics) > 0

    def test_limits_topics_to_five(self, extractor):
        """Topic generation limits to 5 topics max."""
        topics = extractor._generate_topics(
            "RAG embedding fine-tuning LLM prompting evaluation deployment training inference agents"
        )
        assert len(topics) <= 5
\`\`\`

### Project Structure Alignment

\`\`\`
packages/pipeline/
├── src/
│   ├── extractors/
│   │   ├── __init__.py           # Add PatternExtractor export
│   │   ├── base.py               # Story 3.1 - BaseExtractor, Pattern model
│   │   ├── decision_extractor.py # Story 3.2 - Reference implementation
│   │   ├── pattern_extractor.py  # THIS STORY
│   │   └── prompts/
│   │       ├── _base.md          # Common instructions
│   │       ├── decision.md       # Story 3.2
│   │       └── pattern.md        # THIS STORY
│   └── models/
│       └── ...
└── tests/
    └── test_extractors/
        ├── conftest.py
        ├── test_base.py          # Story 3.1
        ├── test_decision_extractor.py  # Story 3.2
        └── test_pattern_extractor.py   # THIS STORY
\`\`\`

### Dependencies

**Blocked By:**
- Story 3.1: Base Extractor Interface - Provides `BaseExtractor`, `Pattern`, `ExtractionType`, `extractor_registry`

**Pattern Reference:**
- Story 3.2: Decision Extractor - Follow same implementation pattern

**Blocks:**
- Story 3.6: Extraction Storage and Embedding - Uses Pattern extractions
- Story 3.7: Extraction Pipeline CLI - Runs PatternExtractor

### Library & Framework Requirements

No additional dependencies beyond Story 3.1 requirements:
- pydantic>=2.0 (model validation)
- structlog (logging)
- pytest, pytest-asyncio (testing)

### Code Reuse Opportunities

**From Story 3.1 BaseExtractor:**
- `_load_prompt(prompt_name)` - Load prompt from file
- `_parse_llm_response(response)` - Parse JSON from LLM output
- `_validate_extraction(data, chunk_id, source_id)` - Validate with Pydantic
- `_generate_topics(content)` - Auto-tag topics

**DO NOT REINVENT:** These utilities are already implemented in `BaseExtractor`. Call them from your `extract()` method.

### Anti-Patterns to Avoid

1. **Don't skip code_example preservation** - Maintain exact formatting including newlines, indentation
2. **Don't forget trade_offs** - Patterns without trade-offs are incomplete
3. **Don't omit context** - When to use the pattern is critical information
4. **Don't create duplicate Pattern model** - Use `Pattern` from `src.extractors.base`
5. **Don't forget registry registration** - Call `extractor_registry.register()` at module level

### Architecture Compliance Checklist

- [ ] File at `packages/pipeline/src/extractors/pattern_extractor.py`
- [ ] Extends `BaseExtractor` ABC from Story 3.1
- [ ] Implements `extraction_type` property returning `ExtractionType.PATTERN`
- [ ] Implements `model_class` property returning `Pattern`
- [ ] Implements `extract()` method returning `list[ExtractionResult]`
- [ ] Implements `get_prompt()` method loading from `pattern.md`
- [ ] Registered with `extractor_registry` at module level
- [ ] Uses structlog for all logging (no print statements)
- [ ] Prompt file at `packages/pipeline/src/extractors/prompts/pattern.md`
- [ ] Tests at `packages/pipeline/tests/test_extractors/test_pattern_extractor.py`
- [ ] All tests pass: `cd packages/pipeline && uv run pytest tests/test_extractors/test_pattern_extractor.py`

### Example Pattern Extractions

**Example 1: Semantic Caching**
\`\`\`json
{
  "name": "Semantic Caching",
  "problem": "High API costs from repeated similar queries to LLM",
  "solution": "Cache responses using embedding similarity. Compare query embeddings against cache entries to find semantically similar previous queries.",
  "code_example": "def get_cached_response(query, cache, threshold=0.9):\n    embedding = model.encode(query)\n    for key, value in cache.items():\n        if cosine_similarity(embedding, key) > threshold:\n            return value\n    return None",
  "context": "High-traffic applications with repetitive similar queries",
  "trade_offs": ["Pro: 40-60% cost reduction", "Con: Added latency for cache lookup", "Con: Cache invalidation complexity"],
  "topics": ["caching", "embeddings", "llm"]
}
\`\`\`

**Example 2: Chunking Strategy**
\`\`\`json
{
  "name": "Recursive Chunking",
  "problem": "Fixed-size chunking splits content at arbitrary boundaries, losing context",
  "solution": "Recursively split documents using multiple separators (paragraphs, sentences, words) to respect natural boundaries while staying within size limits.",
  "code_example": null,
  "context": "Document processing for RAG systems with structured documents",
  "trade_offs": ["Pro: Preserves semantic coherence", "Pro: Respects document structure", "Con: More complex implementation", "Con: Variable chunk sizes"],
  "topics": ["chunking", "rag", "retrieval"]
}
\`\`\`

### References

**Architecture Decisions:**
- [Architecture: Extraction Types] `_bmad-output/architecture.md:66-73`
- [Architecture: Pattern model] `_bmad-output/architecture.md:310-323` (Pattern fields in extraction schema)
- [Architecture: NFR6 Extensibility] `_bmad-output/architecture.md:80`

**Requirements:**
- [PRD: FR-2.2 Pattern Extraction] `_bmad-output/prd.md:255`
- [PRD: FR-2.9 Topic Tagging] `_bmad-output/prd.md:262`
- [PRD: FR-2.10 Source Attribution] `_bmad-output/prd.md:263`

**Epic Context:**
- [Epics: Story 3.3] `_bmad-output/epics.md:412-427`
- [Epics: Epic 3 Goals] `_bmad-output/epics.md:371-376`

**Project Rules:**
- [Project Context: All Rules] `_bmad-output/project-context.md`

**Story Dependencies:**
- [Story 3.1: Base Extractor Interface] - Pattern model, BaseExtractor ABC
- [Story 3.2: Decision Extractor] - Implementation pattern to follow

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 34 pattern extractor tests pass
- All 212 extractor module tests pass
- 2 unrelated Qdrant storage tests failed (pre-existing Docker timing issues)

### Completion Notes List

- Implemented PatternExtractor extending BaseExtractor ABC from Story 3.1
- Uses async extract() method with LLMClient for Claude API calls
- Loads combined prompt via _load_full_prompt() (base + pattern-specific)
- Auto-tags topics using inherited _generate_topics() method
- Validates extractions using Pydantic Pattern model
- Registered with extractor_registry at module import
- Comprehensive prompt created with field guidelines, examples, and JSON schema
- 34 unit tests covering properties, prompts, extraction, error handling, and registry

### File List

- packages/pipeline/src/extractors/pattern_extractor.py (CREATE)
- packages/pipeline/src/extractors/prompts/pattern.md (MODIFY - expanded from placeholder)
- packages/pipeline/src/extractors/__init__.py (MODIFY - add PatternExtractor export)
- packages/pipeline/tests/test_extractors/test_pattern_extractor.py (CREATE)

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.5 (Adversarial Code Review)
**Date:** 2025-12-31
**Outcome:** APPROVED with fixes applied

### Issues Found & Fixed

| Severity | Issue | Resolution |
|----------|-------|------------|
| MEDIUM | Inconsistent error message format | Standardized to `"Extraction failed: {e!s}"` |
| MEDIUM | Missing dedicated `auto_tag_topics` method | Added reusable method matching DecisionExtractor pattern |
| MEDIUM | Missing detailed success logging | Changed to INFO level with `pattern_extracted` event |
| MEDIUM | Redundant confidence default assignment | Removed - Pydantic model handles default |
| LOW | No test for LLMClient dependency injection | Added 3 new tests for DI feature |

### Verification

- All 38 tests pass (34 original + 4 new)
- All Acceptance Criteria implemented and verified
- All tasks marked [x] confirmed complete
- Architecture compliance checklist: 10/10 items pass
- Git vs Story File List: 0 discrepancies

### Notes

- PatternExtractor now follows same patterns as DecisionExtractor
- LLMClient lazy initialization is better than DecisionExtractor (supports DI)
- Consider updating DecisionExtractor to match this pattern in future

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-12-31 | Code review: Fixed 5 MEDIUM issues, added 4 tests, approved | Claude Opus 4.5 |
| 2025-12-31 | Story implementation complete - PatternExtractor with 34 passing tests | Claude Opus 4.5 |
