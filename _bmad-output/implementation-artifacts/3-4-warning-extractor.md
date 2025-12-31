# Story 3.4: Warning Extractor

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **builder**,
I want to extract warnings, gotchas, and anti-patterns from chunks,
So that end users can query for failure modes and things to avoid.

## Acceptance Criteria

**Given** a chunk of text describing a warning or anti-pattern
**When** I run the warning extractor
**Then** a structured Warning is extracted with: title, description, symptoms, consequences, prevention
**And** the extraction includes source attribution (source_id, chunk_id)
**And** relevant topics are auto-tagged
**And** the extraction prompt is stored in `extractors/prompts/warning.md`

**Implementation Note:** Use LLMClient from `src/extractors/llm_client.py` for extraction. Pass prompt from `prompts/warning.md` to LLMClient. Parse JSON response using Pydantic model validation.

## Tasks / Subtasks

- [x] **Task 1: Verify Prerequisites** (AC: Dependencies available)
  - [x] 1.1: Confirm Story 3.1 complete: `ls packages/pipeline/src/extractors/base.py`
  - [x] 1.2: Confirm Warning model exists: `cd packages/pipeline && uv run python -c "from src.extractors import Warning, BaseExtractor, ExtractionType; print('OK')"`
  - [x] 1.3: Confirm Story 3.2/3.3 exist (pattern reference): `ls packages/pipeline/src/extractors/decision_extractor.py packages/pipeline/src/extractors/pattern_extractor.py`
  - [x] 1.4: Confirm prompts directory: `ls packages/pipeline/src/extractors/prompts/`

- [x] **Task 2: Create WarningExtractor Class** (AC: #1, #2, #3)
  - [x] 2.1: Create `packages/pipeline/src/extractors/warning_extractor.py`
  - [x] 2.2: Extend `BaseExtractor` ABC from Story 3.1
  - [x] 2.3: Implement `extraction_type` property returning `ExtractionType.WARNING`
  - [x] 2.4: Implement `model_class` property returning `Warning`
  - [x] 2.5: Implement `extract()` method with Warning model validation
  - [x] 2.6: Implement `get_prompt()` method loading from `warning.md`
  - [x] 2.7: Register extractor with `extractor_registry`

- [x] **Task 3: Create Extraction Prompt** (AC: #4)
  - [x] 3.1: Create/update `packages/pipeline/src/extractors/prompts/warning.md`
  - [x] 3.2: Define prompt structure for identifying warnings, gotchas, anti-patterns
  - [x] 3.3: Include guidance for `title`, `description` extraction
  - [x] 3.4: Include guidance for `symptoms` extraction (how to recognize the problem)
  - [x] 3.5: Include guidance for `consequences` extraction (what happens if ignored)
  - [x] 3.6: Include guidance for `prevention` extraction (how to avoid)
  - [x] 3.7: Add examples of good warning extractions

- [x] **Task 4: Update Module Exports** (AC: Clean imports)
  - [x] 4.1: Add `WarningExtractor` to `packages/pipeline/src/extractors/__init__.py` exports
  - [x] 4.2: Verify import: `from src.extractors import WarningExtractor`
  - [x] 4.3: Verify registry contains warning extractor

- [x] **Task 5: Create Unit Tests** (AC: All)
  - [x] 5.1: Create `packages/pipeline/tests/test_extractors/test_warning_extractor.py`
  - [x] 5.2: Test `extract()` with sample warning chunk
  - [x] 5.3: Test Warning model validation (all required fields)
  - [x] 5.4: Test topic auto-tagging for warning content
  - [x] 5.5: Test source attribution preservation (source_id, chunk_id)
  - [x] 5.6: Test prompt loading from `warning.md`
  - [x] 5.7: Test registry retrieval: `extractor_registry.get_extractor(ExtractionType.WARNING)`
  - [x] 5.8: Test symptoms[], consequences[] list handling
  - [x] 5.9: All tests pass: `cd packages/pipeline && uv run pytest tests/test_extractors/test_warning_extractor.py -v`

## Dev Notes

### Critical Implementation Context

**Core Philosophy:** Warning extractions are for NAVIGATION, Claude is for SYNTHESIS. The extractor creates structured warning maps that Claude can reason about, prioritize for user context, and help users avoid common mistakes in AI engineering.

**Warning vs Pattern vs Decision:**
- **Decisions** capture "what to choose" (choice points)
- **Patterns** capture "how to implement" (solutions)
- **Warnings** capture "what to avoid" (failure modes, gotchas, anti-patterns)

Warnings are CRITICAL for preventing costly mistakes in AI engineering. They represent lessons learned, common pitfalls, and anti-patterns that are often only discovered through painful experience.

### Warning Model Structure (from Story 3.1)

```python
class Warning(ExtractionBase):
    """Warning/gotcha extraction.

    Captures anti-patterns, failure modes, gotchas.
    Used by end users to avoid common mistakes.
    """
    type: ExtractionType = ExtractionType.WARNING
    title: str                        # Warning title (concise, descriptive)
    description: str                  # What the warning is about (full explanation)
    symptoms: list[str] = []          # How to recognize the problem
    consequences: list[str] = []      # What happens if ignored
    prevention: str = ""              # How to avoid the issue
```

**Inherited from ExtractionBase:**
- `id: str` - Unique extraction ID
- `source_id: str` - Reference to sources collection
- `chunk_id: str` - Reference to chunks collection
- `type: ExtractionType` - Set to WARNING
- `topics: list[str]` - Auto-tagged topics
- `schema_version: str` - "1.0.0"
- `extracted_at: datetime` - Timestamp
- `confidence: float` - 0.0-1.0 score

### Implementation Pattern (Follow Story 3.2/3.3)

```python
# packages/pipeline/src/extractors/warning_extractor.py
from typing import Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionType,
    ExtractionBase,
    ExtractionResult,
    Warning,
    extractor_registry,
)

logger = structlog.get_logger()


class WarningExtractor(BaseExtractor):
    """Extractor for warnings, gotchas, and anti-patterns.

    Identifies and structures failure modes, common mistakes, and things
    to avoid from text chunks. Used by end users to prevent costly
    errors via the get_warnings MCP tool.

    Example warnings:
    - Context Window Overflow: Sending too many tokens causes truncation
    - Cold Start Latency: First inference is slow due to model loading
    - Embedding Drift: Changing embedding models breaks existing vectors
    """

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for warnings."""
        return ExtractionType.WARNING

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Warning model class."""
        return Warning

    def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str
    ) -> list[ExtractionResult]:
        """Extract warnings from chunk content.

        Args:
            chunk_content: Text content to extract warnings from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with Warning extractions.
        """
        logger.info(
            "warning_extraction_started",
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
        # 3. Validate each warning with _validate_extraction()
        # 4. Auto-tag topics with _generate_topics()

        logger.info(
            "warning_extraction_completed",
            chunk_id=chunk_id,
            warning_count=len(results)
        )

        return results

    def get_prompt(self) -> str:
        """Load warning extraction prompt from file.

        Returns:
            Prompt string for LLM extraction.

        Raises:
            PromptLoadError: If prompt file cannot be loaded.
        """
        return self._load_prompt("warning")


# Register extractor with global registry
extractor_registry.register(ExtractionType.WARNING, WarningExtractor)
```

### Prompt File Structure

```markdown
# packages/pipeline/src/extractors/prompts/warning.md

# Warning Extraction Prompt

You are a knowledge extraction assistant. Extract warnings, gotchas, and anti-patterns from the provided text.

## What is a Warning?

A warning captures things that can go wrong in AI engineering:
- **Gotchas**: Non-obvious problems that catch people off guard
- **Anti-patterns**: Common but problematic approaches to avoid
- **Failure modes**: Ways systems can fail under specific conditions
- **Common mistakes**: Errors that practitioners frequently make
- **Technical debt**: Short-term solutions with long-term consequences

## Extraction Rules

1. Only extract warnings explicitly described or strongly implied in the text
2. A warning MUST have a clear title and description
3. Include symptoms (how to recognize the problem is occurring)
4. Include consequences (what happens if the warning is ignored)
5. Include prevention (how to avoid or mitigate the issue)
6. Return valid JSON matching the schema below
7. If no warnings found, return an empty array []

## Output Schema

{
  "title": "Brief, descriptive warning title",
  "description": "Full explanation of the warning and why it matters",
  "symptoms": ["Sign 1 that indicates problem", "Sign 2 that indicates problem"],
  "consequences": ["What happens if ignored 1", "What happens if ignored 2"],
  "prevention": "How to avoid or mitigate this issue"
}

## Example Extraction

**Input text:**
"Be careful when changing your embedding model - all your existing vectors become incompatible. If you switch from OpenAI ada-002 to a different model, you'll need to re-embed your entire corpus. For large datasets, this can take days and cost thousands of dollars. Always version your embedding model choice and plan migrations carefully."

**Extracted warning:**
{
  "title": "Embedding Model Migration Incompatibility",
  "description": "Changing embedding models invalidates all existing vectors in your database. Different models produce incompatible vector spaces, meaning vectors from one model cannot be compared with vectors from another.",
  "symptoms": [
    "Search relevance suddenly drops after model change",
    "Similarity scores become meaningless or random",
    "Previously working queries return irrelevant results"
  ],
  "consequences": [
    "Must re-embed entire document corpus",
    "Days of processing time for large datasets",
    "Thousands of dollars in embedding API costs",
    "Potential service downtime during migration"
  ],
  "prevention": "Version your embedding model choice from the start. Maintain backward compatibility or plan dedicated migration windows. Consider storing raw text alongside vectors to enable re-embedding."
}

## Warning Categories to Look For

- **Performance**: Latency issues, memory problems, scaling limits
- **Cost**: Unexpected expenses, quota exhaustion, inefficient usage
- **Quality**: Accuracy degradation, hallucinations, bias issues
- **Security**: Data leakage, prompt injection, API key exposure
- **Operations**: Deployment failures, monitoring gaps, recovery issues
- **Data**: Corruption, loss, incompatibility, format issues
- **Integration**: API breaking changes, version conflicts, dependency issues

## Now extract warnings from this text:

{{chunk_content}}
```

### Topic Auto-Tagging for Warnings

The base class `_generate_topics()` method handles topic extraction. For warnings, relevant topics include:

- `rag` - RAG-related warnings
- `embeddings` - Embedding issues
- `llm` - LLM-specific gotchas
- `prompting` - Prompt engineering pitfalls
- `evaluation` - Evaluation mistakes
- `deployment` - Deployment anti-patterns
- `fine-tuning` - Fine-tuning gotchas
- `training` - Training issues
- `inference` - Inference problems
- `agents` - Agent architecture pitfalls

### Testing Strategy

```python
# packages/pipeline/tests/test_extractors/test_warning_extractor.py
import pytest
from datetime import datetime

from src.extractors import (
    WarningExtractor,
    Warning,
    ExtractionType,
    ExtractionResult,
    ExtractorRegistry,
    extractor_registry,
)


class TestWarningExtractor:
    """Test WarningExtractor implementation."""

    @pytest.fixture
    def extractor(self) -> WarningExtractor:
        """Create warning extractor instance."""
        return WarningExtractor()

    def test_extraction_type_is_warning(self, extractor):
        """Extractor returns WARNING extraction type."""
        assert extractor.extraction_type == ExtractionType.WARNING

    def test_model_class_is_warning(self, extractor):
        """Extractor uses Warning model class."""
        assert extractor.model_class == Warning

    def test_get_prompt_loads_warning_md(self, extractor):
        """Prompt is loaded from warning.md file."""
        prompt = extractor.get_prompt()
        assert "warning" in prompt.lower()
        assert len(prompt) > 100

    def test_extract_returns_list(self, extractor):
        """Extract method returns list of results."""
        results = extractor.extract(
            chunk_content="Sample warning text about common mistakes",
            chunk_id="chunk-123",
            source_id="source-456"
        )
        assert isinstance(results, list)

    def test_registry_contains_warning_extractor(self):
        """Warning extractor is registered in global registry."""
        assert extractor_registry.is_supported(ExtractionType.WARNING)
        extractor = extractor_registry.get_extractor(ExtractionType.WARNING)
        assert isinstance(extractor, WarningExtractor)


class TestWarningModel:
    """Test Warning Pydantic model."""

    def test_warning_required_fields(self):
        """Warning requires source_id, chunk_id, title, description."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Context Window Overflow",
            description="Sending too many tokens causes truncation"
        )
        assert warning.source_id == "src-123"
        assert warning.chunk_id == "chunk-456"
        assert warning.type == ExtractionType.WARNING
        assert warning.schema_version == "1.0.0"

    def test_warning_optional_fields(self):
        """Warning allows optional symptoms, consequences, prevention."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Cold Start Latency",
            description="First inference is slow due to model loading",
            symptoms=["Long initial response time", "Timeout on first request"],
            consequences=["Poor user experience", "Failed health checks"],
            prevention="Use model warming or keep-alive requests"
        )
        assert len(warning.symptoms) == 2
        assert len(warning.consequences) == 2
        assert warning.prevention == "Use model warming or keep-alive requests"

    def test_warning_empty_lists_valid(self):
        """Warning allows empty symptoms and consequences lists."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test Warning",
            description="Test description"
        )
        assert warning.symptoms == []
        assert warning.consequences == []
        assert warning.prevention == ""

    def test_warning_has_source_attribution(self):
        """Warning includes source attribution fields."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test",
            description="Test"
        )
        assert hasattr(warning, "source_id")
        assert hasattr(warning, "chunk_id")
        assert hasattr(warning, "topics")
        assert hasattr(warning, "schema_version")

    def test_warning_multiple_symptoms(self):
        """Warning can have multiple symptoms."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Rate Limiting Issues",
            description="Hitting API rate limits causes failures",
            symptoms=[
                "429 Too Many Requests errors",
                "Exponential backoff triggered",
                "Request queue growing",
                "Response latency increasing"
            ]
        )
        assert len(warning.symptoms) == 4

    def test_warning_multiple_consequences(self):
        """Warning can have multiple consequences."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Missing Input Validation",
            description="Not validating prompt inputs exposes security risks",
            consequences=[
                "Prompt injection attacks",
                "Data exfiltration",
                "Cost explosion from long inputs",
                "Service disruption"
            ]
        )
        assert len(warning.consequences) == 4


class TestTopicAutoTagging:
    """Test topic auto-tagging for warnings."""

    @pytest.fixture
    def extractor(self) -> WarningExtractor:
        return WarningExtractor()

    def test_generates_topics_from_content(self, extractor):
        """Topics are generated from warning content."""
        topics = extractor._generate_topics(
            "This warning about embedding model changes affects RAG systems"
        )
        assert isinstance(topics, list)
        # Should detect rag, embeddings, or related topics
        assert len(topics) > 0

    def test_limits_topics_to_five(self, extractor):
        """Topic generation limits to 5 topics max."""
        topics = extractor._generate_topics(
            "RAG embedding fine-tuning LLM prompting evaluation deployment training inference agents"
        )
        assert len(topics) <= 5
```

### Project Structure Alignment

```
packages/pipeline/
├── src/
│   ├── extractors/
│   │   ├── __init__.py           # Add WarningExtractor export
│   │   ├── base.py               # Story 3.1 - BaseExtractor, Warning model
│   │   ├── decision_extractor.py # Story 3.2 - Reference implementation
│   │   ├── pattern_extractor.py  # Story 3.3 - Reference implementation
│   │   ├── warning_extractor.py  # THIS STORY
│   │   └── prompts/
│   │       ├── _base.md          # Common instructions
│   │       ├── decision.md       # Story 3.2
│   │       ├── pattern.md        # Story 3.3
│   │       └── warning.md        # THIS STORY
│   └── models/
│       └── ...
└── tests/
    └── test_extractors/
        ├── conftest.py
        ├── test_base.py               # Story 3.1
        ├── test_decision_extractor.py # Story 3.2
        ├── test_pattern_extractor.py  # Story 3.3
        └── test_warning_extractor.py  # THIS STORY
```

### Dependencies

**Blocked By:**
- Story 3.1: Base Extractor Interface - Provides `BaseExtractor`, `Warning`, `ExtractionType`, `extractor_registry`

**Pattern References:**
- Story 3.2: Decision Extractor - Follow same implementation pattern
- Story 3.3: Pattern Extractor - Follow same implementation pattern

**Blocks:**
- Story 3.6: Extraction Storage and Embedding - Uses Warning extractions
- Story 3.7: Extraction Pipeline CLI - Runs WarningExtractor

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

1. **Don't confuse warnings with patterns** - Warnings are about what NOT to do, patterns are about what TO do
2. **Don't skip symptoms** - How to recognize the problem is critical information
3. **Don't skip consequences** - Users need to understand impact to prioritize
4. **Don't skip prevention** - Actionable prevention is the key value of warnings
5. **Don't create duplicate Warning model** - Use `Warning` from `src.extractors.base`
6. **Don't forget registry registration** - Call `extractor_registry.register()` at module level
7. **Don't use print() for logging** - Use structlog only

### Architecture Compliance Checklist

- [ ] File at `packages/pipeline/src/extractors/warning_extractor.py`
- [ ] Extends `BaseExtractor` ABC from Story 3.1
- [ ] Implements `extraction_type` property returning `ExtractionType.WARNING`
- [ ] Implements `model_class` property returning `Warning`
- [ ] Implements `extract()` method returning `list[ExtractionResult]`
- [ ] Implements `get_prompt()` method loading from `warning.md`
- [ ] Registered with `extractor_registry` at module level
- [ ] Uses structlog for all logging (no print statements)
- [ ] Prompt file at `packages/pipeline/src/extractors/prompts/warning.md`
- [ ] Tests at `packages/pipeline/tests/test_extractors/test_warning_extractor.py`
- [ ] All tests pass: `cd packages/pipeline && uv run pytest tests/test_extractors/test_warning_extractor.py -v`

### Example Warning Extractions

**Example 1: Embedding Model Drift**
```json
{
  "title": "Embedding Model Migration Incompatibility",
  "description": "Changing embedding models invalidates all existing vectors. Different models produce incompatible vector spaces that cannot be compared.",
  "symptoms": [
    "Search relevance suddenly drops after model change",
    "Similarity scores become meaningless",
    "Previously working queries return irrelevant results"
  ],
  "consequences": [
    "Must re-embed entire document corpus",
    "Days of processing time for large datasets",
    "Thousands of dollars in embedding API costs"
  ],
  "prevention": "Version your embedding model choice from the start. Plan dedicated migration windows with downtime budget.",
  "topics": ["embeddings", "rag", "deployment"]
}
```

**Example 2: Context Window Overflow**
```json
{
  "title": "Context Window Overflow",
  "description": "Sending too many tokens to an LLM causes silent truncation or errors. The model only sees part of your input.",
  "symptoms": [
    "Responses ignore information at the end of prompts",
    "API returns 400 errors with token count messages",
    "Model 'forgets' earlier parts of conversation"
  ],
  "consequences": [
    "Incomplete or incorrect responses",
    "Silent failures that are hard to debug",
    "Wasted API costs on unusable responses"
  ],
  "prevention": "Always count tokens before sending. Implement chunking strategies. Use summarization for long contexts.",
  "topics": ["llm", "prompting", "inference"]
}
```

**Example 3: Rate Limit Exhaustion**
```json
{
  "title": "API Rate Limit Exhaustion",
  "description": "Hitting API rate limits causes cascading failures in production systems with no graceful degradation.",
  "symptoms": [
    "429 Too Many Requests errors appearing in logs",
    "Exponential backoff filling request queues",
    "Response latencies increasing sharply"
  ],
  "consequences": [
    "Complete service outage during rate limit window",
    "Lost user requests with no retry",
    "Potential billing spikes from retry storms"
  ],
  "prevention": "Implement client-side rate limiting before hitting server limits. Use request queuing with backpressure. Design for graceful degradation.",
  "topics": ["deployment", "llm", "inference"]
}
```

### Previous Story Intelligence

**From Story 3.1 (Base Extractor Interface):**
- Established ABC pattern with `BaseExtractor`
- Established `Warning` model with required fields: `title`, `description`, `symptoms`, `consequences`, `prevention`
- Established `ExtractorRegistry` for extensibility (NFR6)
- Established exception hierarchy: `ExtractorError`, `PromptLoadError`, etc.
- Established utility methods: `_load_prompt()`, `_parse_llm_response()`, `_validate_extraction()`, `_generate_topics()`

**From Story 3.2 (Decision Extractor):**
- Established extractor implementation pattern
- Established prompt file structure in `prompts/decision.md`
- Established test file structure in `tests/test_extractors/`
- Established registry registration at module level

**From Story 3.3 (Pattern Extractor):**
- Confirmed same implementation pattern works
- Confirmed prompt file pattern with `{{chunk_content}}` placeholder
- Confirmed test coverage patterns for list fields

**Patterns to Follow:**
- Exception classes inherit from `KnowledgeError`
- All exceptions include `code`, `message`, `details`
- Use structlog for all logging
- Pydantic models for data validation
- Tests mirror src structure
- Registry pattern for extensibility

### Git Intelligence

**Recent Commits:**
- `4a59247` feat(story-1-1): initialize monorepo structure
- `44323de` Definition of architecture
- `bc247ce` first commit

**Files likely created by Story 3.1-3.3:**
- `packages/pipeline/src/extractors/base.py`
- `packages/pipeline/src/extractors/__init__.py`
- `packages/pipeline/src/extractors/decision_extractor.py`
- `packages/pipeline/src/extractors/pattern_extractor.py`
- `packages/pipeline/src/extractors/prompts/` (directory)

### References

**Architecture Decisions:**
- [Architecture: Extraction Types] `_bmad-output/architecture.md:66-73` - Warning for end user gotchas, anti-patterns, failure modes
- [Architecture: Warning model] `_bmad-output/architecture.md:325-334` (Warning fields in extraction schema)
- [Architecture: NFR6 Extensibility] `_bmad-output/architecture.md:80` - Abstract extractor patterns

**Requirements:**
- [Epics: FR-2.3 Warning Extraction] `_bmad-output/epics.md:31` - FR2.3: Warning extraction (gotchas, anti-patterns, failure modes)
- [Epics: FR-2.8 Topic Tagging] `_bmad-output/epics.md:38` - FR2.8: Topic tagging for all extractions
- [Epics: FR-2.9 Source Attribution] `_bmad-output/epics.md:39` - FR2.9: Source attribution (every extraction traces back)

**Epic Context:**
- [Epics: Story 3.4] `_bmad-output/epics.md:429-442` - Story 3.4 acceptance criteria
- [Epics: Epic 3 Goals] `_bmad-output/epics.md:371-376` - Extract structured knowledge with source attribution

**Project Rules:**
- [Project Context: All Rules] `_bmad-output/project-context.md` - Implementation patterns and anti-patterns

**Story Dependencies:**
- [Story 3.1: Base Extractor Interface] - Warning model, BaseExtractor ABC, extractor_registry
- [Story 3.2: Decision Extractor] - Implementation pattern to follow
- [Story 3.3: Pattern Extractor] - Implementation pattern to follow

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 32 unit tests pass
- Full test suite (507 tests) passes with no regressions
- Ruff linting passes with no errors

### Completion Notes List

- ✅ Implemented WarningExtractor class extending BaseExtractor ABC
- ✅ Properties: extraction_type returns WARNING, model_class returns Warning
- ✅ Implements extract() sync method (placeholder) and extract_async() async method with LLMClient
- ✅ Uses _load_full_prompt("warning") to load prompt with base instructions
- ✅ Registered with extractor_registry at module level
- ✅ Enhanced warning.md prompt with categories, examples, and detailed schema
- ✅ Comprehensive test coverage: 32 tests covering extractor, model, topic tagging, validation, and prompt loading
- ✅ All tests pass: `uv run pytest tests/test_extractors/test_warning_extractor.py -v`

### File List

- packages/pipeline/src/extractors/warning_extractor.py (CREATE)
- packages/pipeline/src/extractors/prompts/warning.md (UPDATE - enhanced from placeholder)
- packages/pipeline/src/extractors/__init__.py (MODIFY - added WarningExtractor export)
- packages/pipeline/tests/test_extractors/test_warning_extractor.py (CREATE)

### Change Log

- 2025-12-31: Story 3.4 implementation complete - WarningExtractor with 32 passing tests
- 2025-12-31: Code review completed - 5 issues fixed (1 HIGH, 4 MEDIUM)

## Senior Developer Review (AI)

### Review Date: 2025-12-31
### Reviewer: Claude Opus 4.5 (Adversarial Code Review)

### Issues Found & Fixed

**HIGH SEVERITY (1):**
1. **DecisionExtractor Not Registered** - Story 3.2's DecisionExtractor was missing `extractor_registry.register()` call. Fixed by adding registration at module level in `decision_extractor.py`. This was a cross-story defect discovered during this review.

**MEDIUM SEVERITY (4):**
2. **Prompt Missing Placeholder** - `warning.md` prompt was missing the `{{chunk_content}}` placeholder. Fixed by adding proper placeholder section at end of prompt.
3. **Sync Method Clarity** - The sync `extract()` method docstring was unclear about being a placeholder. Fixed with comprehensive docstring explaining it returns empty list and directing users to `extract_async()`.
4. **Docstring Improvement** - `get_prompt()` docstring improved to clearly explain the two-part prompt loading (base + specific) and the placeholder usage.
5. **Logging Enhancement** - Added `mode="sync_placeholder"` to logging calls in sync extract() for clearer observability.

**LOW SEVERITY (Not Fixed - Acceptable):**
- Async method test coverage: Current tests adequately cover the interface; async testing with mocked LLMClient would be valuable but not blocking.

### Verification

- All 32 unit tests pass
- Full test suite: 599 passed, 5 skipped
- Ruff linting: All checks passed
- Registry verification: All 7 extraction types now properly registered
- DecisionExtractor now appears in registry output

### Review Outcome

**APPROVED** - All HIGH and MEDIUM issues fixed. Story 3.4 implementation meets acceptance criteria.
