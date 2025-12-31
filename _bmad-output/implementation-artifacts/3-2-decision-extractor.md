# Story 3.2: Decision Extractor

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **builder**,
I want to extract decision points from chunks,
So that end users can query for AI engineering choice points with options and considerations.

## Acceptance Criteria

**Given** a chunk of text containing a decision point
**When** I run the decision extractor
**Then** a structured Decision is extracted with: question, options[], considerations[], recommended_approach
**And** the extraction includes source attribution (source_id, chunk_id)
**And** relevant topics are auto-tagged
**And** the extraction prompt is stored in `extractors/prompts/decision.md`

**Implementation Note:** Use LLMClient from `src/extractors/llm_client.py` for extraction. Pass prompt from `prompts/decision.md` to LLMClient. Parse JSON response using Pydantic model validation.

## Tasks / Subtasks

- [x] Task 1: Create DecisionExtractor class (AC: #1, #2)
  - [x] 1.1: Extend BaseExtractor ABC from Story 3.1
  - [x] 1.2: Implement extract() method with Decision model validation
  - [x] 1.3: Implement get_prompt() method loading from decision.md
  - [x] 1.4: Add Claude-as-extractor pattern (LLM-based extraction via LLMClient)
  - [x] 1.5: Add topic auto-tagging logic

- [x] Task 2: Create Decision Pydantic model (AC: #1) - ALREADY EXISTS in base.py
  - [x] 2.1: Define Decision model with all required fields
  - [x] 2.2: Add validation for question, options[], considerations[]
  - [x] 2.3: Include source attribution fields (source_id, chunk_id)
  - [x] 2.4: Add topics[] field and schema_version
  - [x] 2.5: Ensure JSON serialization compatibility

- [x] Task 3: Create extraction prompt (AC: #4) - ALREADY EXISTS
  - [x] 3.1: Create extractors/prompts/decision.md
  - [x] 3.2: Define prompt structure for identifying decision points
  - [x] 3.3: Include guidance for options[] extraction
  - [x] 3.4: Include guidance for considerations[] extraction
  - [x] 3.5: Add examples of good decision extractions

- [x] Task 4: Unit tests (AC: All)
  - [x] 4.1: Test extract() with sample decision chunk
  - [x] 4.2: Test Decision model validation
  - [x] 4.3: Test topic auto-tagging
  - [x] 4.4: Test source attribution preservation
  - [x] 4.5: Test prompt loading from decision.md

## Dev Notes

### Critical Implementation Context

**🔥 CRITICAL MISSION:** This extractor is the FIRST knowledge extraction component for end users. It must demonstrate the pattern for all future extractors while delivering immediate value by helping users navigate AI engineering choice points.

**Core Philosophy:** Decision extractions are for NAVIGATION, Claude is for SYNTHESIS. The extractor creates structured decision maps that Claude can reason about, weigh across sources, and apply to user context.

### Architecture Patterns from PRD & Architecture

**Source:** `_bmad-output/prd.md`, `_bmad-output/architecture.md`

**Extraction Pipeline Flow:**
```
Chunk → DecisionExtractor → Decision Model → MongoDB extractions + Qdrant vectors
```

**Key Architectural Decisions:**
1. **LLM-Based Extraction:** Automated batch extraction using Claude Haiku
   - Extraction happens during ingestion (WRITE phase)
   - Use LLMClient from `src/extractors/llm_client.py` for API calls
   - ~$10 per book for full extraction (cost-effective batch processing)

2. **Source Attribution (FR-2.10):** Every extraction must trace back
   - `source_id` → which book/paper
   - `chunk_id` → which specific text chunk
   - Enables "show me context" queries later

3. **Topic Tagging (FR-2.9):** Auto-tag for filtering
   - Extract topics from decision content
   - Store in topics[] field
   - Used for filtered queries via `get_decisions(topic="retrieval")`

4. **Schema Versioning (FR-3.7):** Future-proof
   - All extractions include `schema_version` field
   - Current version: "1.0"
   - Enables backward compatibility during schema evolution

### Decision Model Structure

**Source:** Epic 3 requirements, Story 3.1 base patterns

```python
class Decision(BaseModel):
    """Extraction model for decision points in AI engineering."""

    # Core decision content
    question: str  # The decision being made
    options: List[str]  # Available choices
    considerations: List[str]  # Trade-offs, constraints, factors
    recommended_approach: Optional[str]  # Author's recommendation if present

    # Context and categorization
    context: Optional[str]  # When/where this decision applies
    topics: List[str]  # Auto-tagged topics (e.g., ["retrieval", "chunking"])

    # Source attribution (MANDATORY)
    source_id: str  # MongoDB sources._id
    chunk_id: str  # MongoDB chunks._id

    # Metadata
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    schema_version: str = "1.0"
    type: Literal["decision"] = "decision"  # For polymorphic queries
```

### BaseExtractor Interface (from Story 3.1)

**IMPORTANT:** You MUST extend the BaseExtractor ABC defined in Story 3.1:

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T', bound=BaseModel)

class BaseExtractor(ABC, Generic[T]):
    """Base class for all knowledge extractors."""

    @abstractmethod
    async def extract(self, chunk: Chunk) -> T:
        """Extract knowledge from a chunk.

        Args:
            chunk: Chunk object with content and metadata

        Returns:
            Extraction model instance (Decision, Pattern, etc.)
        """
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """Load extraction prompt from prompts/ directory."""
        pass
```

### Critical Implementation Rules

**Source:** `_bmad-output/project-context.md`

1. **File Location:** `packages/pipeline/src/extractors/decision_extractor.py`
2. **Prompt Location:** `packages/pipeline/src/extractors/prompts/decision.md`
3. **Model Location:** `packages/pipeline/src/models/extraction.py` (Decision class)
4. **Test Location:** `packages/pipeline/tests/test_extractors/test_decision_extractor.py`

5. **Naming Conventions:**
   - Class: `DecisionExtractor` (PascalCase)
   - File: `decision_extractor.py` (snake_case)
   - Functions: `extract()`, `get_prompt()`, `auto_tag_topics()` (snake_case)

6. **Async Patterns:**
   - `extract()` can be `async def` (future LLM API calls)
   - `get_prompt()` is sync (file I/O)
   - `auto_tag_topics()` is sync (text processing)

7. **Error Handling:**
   - Inherit from `KnowledgeError` base class
   - Specific: `ExtractionError` for extraction failures
   - Always include `code`, `message`, `details`

8. **Logging:**
   - Use `structlog` ONLY (never print)
   - Log with context: `logger.info("decision_extracted", chunk_id=chunk.id, topics=topics)`

### Topic Auto-Tagging Strategy

**Extract topics from decision content to enable filtered queries:**

```python
def auto_tag_topics(self, decision: Decision) -> List[str]:
    """Auto-tag topics from decision content.

    Strategy:
    1. Extract keywords from question
    2. Extract keywords from options and considerations
    3. Match against known AI engineering domains
    4. Return 3-5 most relevant topics

    Known domains: retrieval, embedding, chunking, llm, prompting,
                   evaluation, deployment, scaling, monitoring
    """
    # Simple keyword matching for MVP
    # Can be enhanced with semantic similarity later
```

### Prompt Engineering Guidance

**Source:** `extractors/prompts/decision.md` to be created

The prompt should guide Claude to:
1. Identify explicit decision points ("should I...", "choose between...", "which approach...")
2. Extract all available options as discrete choices
3. Capture considerations (trade-offs, constraints, when to use each option)
4. Note recommended approach if author provides one
5. Identify context (when/where this decision applies)

**Example Decision Extraction:**

```
CHUNK:
"When choosing a chunking strategy for RAG, you should consider
three main approaches: fixed-size chunking (simple, 512 tokens),
semantic chunking (respects boundaries, variable size), and
recursive chunking (hierarchical, preserves structure). Fixed-size
is fastest but may split concepts. Semantic preserves meaning but
slower. For technical documentation, semantic chunking is recommended."

EXTRACTED DECISION:
{
  "question": "Which chunking strategy should I use for RAG?",
  "options": [
    "Fixed-size chunking (512 tokens)",
    "Semantic chunking (respects boundaries)",
    "Recursive chunking (hierarchical)"
  ],
  "considerations": [
    "Fixed-size is fastest but may split concepts",
    "Semantic preserves meaning but slower",
    "Recursive preserves document structure"
  ],
  "recommended_approach": "Semantic chunking for technical documentation",
  "context": "RAG systems with technical documentation",
  "topics": ["chunking", "retrieval", "rag"]
}
```

### Integration with Storage (Story 3.6)

**This story does NOT implement storage.** Story 3.6 handles:
- Saving Decision to MongoDB `extractions` collection
- Generating embedding from decision summary
- Storing embedding in Qdrant `extractions` collection

**DecisionExtractor responsibility:** Return valid Decision model
**Storage responsibility:** Persist Decision to databases

### Testing Strategy

**Source:** `_bmad-output/project-context.md` testing rules

```python
# tests/test_extractors/test_decision_extractor.py

@pytest.fixture
def sample_decision_chunk() -> Chunk:
    """Chunk containing a clear decision point."""
    return Chunk(
        id="chunk-123",
        source_id="source-456",
        content="When choosing between OpenAI and local models...",
        position={"chapter": 5, "section": 2},
        token_count=150
    )

@pytest.mark.asyncio
async def test_extract_decision(sample_decision_chunk):
    """Test decision extraction from chunk."""
    extractor = DecisionExtractor()
    decision = await extractor.extract(sample_decision_chunk)

    assert decision.question
    assert len(decision.options) > 0
    assert decision.source_id == "source-456"
    assert decision.chunk_id == "chunk-123"
    assert decision.schema_version == "1.0"
    assert "decision" in decision.type

def test_auto_tag_topics():
    """Test topic auto-tagging logic."""
    extractor = DecisionExtractor()
    decision = Decision(
        question="Which embedding model should I use?",
        options=["OpenAI ada-002", "all-MiniLM-L6-v2"],
        considerations=["Cost vs quality trade-off"],
        source_id="test",
        chunk_id="test"
    )

    topics = extractor.auto_tag_topics(decision)
    assert "embedding" in topics

def test_get_prompt():
    """Test prompt loading from file."""
    extractor = DecisionExtractor()
    prompt = extractor.get_prompt()

    assert "decision" in prompt.lower()
    assert len(prompt) > 100  # Substantial prompt
```

### Files to Create/Modify

**Create:**
1. `packages/pipeline/src/extractors/decision_extractor.py` - DecisionExtractor class
2. `packages/pipeline/src/extractors/prompts/decision.md` - Extraction prompt
3. `packages/pipeline/src/models/extraction.py` - Decision model (if not in base.py)
4. `packages/pipeline/tests/test_extractors/test_decision_extractor.py` - Unit tests

**Modify:**
- `packages/pipeline/src/extractors/__init__.py` - Export DecisionExtractor
- `packages/pipeline/src/models/__init__.py` - Export Decision model

### Dependencies on Other Stories

**Blocks:** None (can be implemented independently)

**Blocked By:**
- Story 3.1: Base Extractor Interface ❌ NOT YET IMPLEMENTED
  - Need BaseExtractor ABC to extend
  - Need extraction model base patterns

**Depends On:**
- Story 1.3: Pydantic Models ✅ (Chunk model exists)
- Story 1.4: MongoDB Client ✅ (for source_id/chunk_id references)

**⚠️ CRITICAL:** Story 3.1 MUST be implemented first! Check sprint-status.yaml for current status.

### Library & Framework Requirements

**From Architecture:**
```bash
# Already installed in packages/pipeline
pydantic>=2.0         # Model validation
structlog             # Logging
pytest-asyncio        # Async testing
```

**No additional dependencies required.**

### Project Structure Notes

**Alignment with Monorepo Structure:**
```
packages/pipeline/
├── src/
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py              # Story 3.1 - BaseExtractor ABC
│   │   ├── decision_extractor.py # THIS STORY
│   │   └── prompts/
│   │       └── decision.md       # THIS STORY
│   │
│   └── models/
│       ├── __init__.py
│       ├── extraction.py         # Decision model (THIS STORY)
│       └── ...
│
└── tests/
    └── test_extractors/
        ├── conftest.py
        └── test_decision_extractor.py  # THIS STORY
```

### References

**Architecture Decisions:**
- [Architecture: Extensibility Pattern (NFR-6)] `_bmad-output/architecture.md:650-660`
- [Architecture: Extraction Types] `_bmad-output/architecture.md:66-73`
- [Architecture: Data Model - extractions collection] `_bmad-output/architecture.md:282-290`

**Requirements:**
- [PRD: FR-2.1 Decision Extraction] `_bmad-output/prd.md:254`
- [PRD: FR-2.9 Topic Tagging] `_bmad-output/prd.md:262`
- [PRD: FR-2.10 Source Attribution] `_bmad-output/prd.md:263`

**Epic Context:**
- [Epics: Story 3.2] `_bmad-output/epics.md:396-410`
- [Epics: Epic 3 Goals] `_bmad-output/epics.md:372-376`

**Project Rules:**
- [Project Context: All Rules] `_bmad-output/project-context.md`

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None - all tests passed without debugging required.

### Completion Notes List

1. **Task 2 & 3 Pre-completed:** The Decision Pydantic model and extraction prompt were already implemented in Story 3.1 (`src/extractors/base.py` lines 114-133) and `src/extractors/prompts/decision.md`.

2. **DecisionExtractor Implementation:** Created `src/extractors/decision_extractor.py` extending BaseExtractor:
   - Implements `extraction_type` property returning `ExtractionType.DECISION`
   - Implements `model_class` property returning `Decision`
   - Implements async `extract()` method using LLMClient for LLM-based extraction
   - Implements `get_prompt()` using `_load_full_prompt("decision")` to combine base + decision prompts
   - Implements `auto_tag_topics()` for topic extraction from decision content

3. **LLM Integration:** Uses LLMClient from `src/extractors/llm_client.py` for automated extraction. The `extract()` method:
   - Loads prompt via `get_prompt()`
   - Calls LLMClient.extract() with prompt and chunk content
   - Parses JSON response via `_parse_llm_response()`
   - Validates with `_validate_extraction()`
   - Auto-tags topics if `config.auto_tag_topics` is enabled
   - Returns list of ExtractionResult objects

4. **Comprehensive Test Coverage:** 24 unit tests covering:
   - Properties and configuration (5 tests)
   - Prompt loading (2 tests)
   - Topic auto-tagging (6 tests) - includes context/recommended_approach test
   - Extract method with mocked LLM (8 tests) - includes exception handling test
   - Integration and registry (3 tests)

5. **Registry Export:** Added DecisionExtractor to `src/extractors/__init__.py` exports.

### File List

**Created:**
- `packages/pipeline/src/extractors/decision_extractor.py` - DecisionExtractor class (200 lines)
- `packages/pipeline/tests/test_extractors/test_decision_extractor.py` - Unit tests (24 tests, 100% coverage)

**Modified:**
- `packages/pipeline/src/extractors/__init__.py` - Added DecisionExtractor import and export
- `packages/pipeline/src/extractors/prompts/decision.md` - Enhanced with confidence scoring guidance (code review fix)

**Pre-existing (verified):**
- `packages/pipeline/src/extractors/base.py` - Decision model (lines 114-133)
- `packages/pipeline/src/extractors/prompts/_base.md` - Base extraction instructions

## Change Log

- 2025-12-31: Implemented DecisionExtractor class with LLM-based extraction, auto-tagging, and comprehensive test coverage (22 tests passing)
- 2025-12-31: **Code Review Fixes** - Added 2 tests (exception handling, context/recommended_approach topic extraction), enhanced decision.md prompt with confidence guidance. Coverage: 100%
