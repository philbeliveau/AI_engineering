# Story 3.5: Methodology and Process Extractors

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **builder**,
I want to extract methodologies, checklists, personas, and workflows from chunks,
So that I can use these to build BMAD workflows and agent prompts.

## Acceptance Criteria

**Given** chunks containing process-oriented content
**When** I run the methodology/checklist/persona/workflow extractors
**Then** structured extractions are created for each type:
- **Methodology:** name, steps[], prerequisites, outputs
- **Checklist:** name, items[], context
- **Persona:** role, responsibilities, expertise, communication_style
- **Workflow:** name, trigger, steps[], decision_points
**And** all extractions include source attribution (source_id, chunk_id) and topic tags
**And** extraction prompts are stored in respective prompt files (methodology.md, checklist.md, persona.md, workflow.md)

## Dependency Analysis

**Depends On (MUST BE COMPLETE):**
- **Story 3.1:** Base Extractor Interface - Provides `BaseExtractor` ABC, all four Pydantic models (`Methodology`, `MethodologyStep`, `Checklist`, `ChecklistItem`, `Persona`, `Workflow`, `WorkflowStep`), `ExtractionType` enum, `extractor_registry`
- **Story 3.2:** Decision Extractor - Establishes implementation pattern to follow
- **Story 3.3:** Pattern Extractor - Validates pattern consistency across extractors

**Recommended Pattern Reference:**
- **Story 3.4:** Warning Extractor - Validates all extractor types follow same pattern (if complete)

**Blocks:**
- **Story 3.6:** Extraction Storage and Embedding - Uses all extraction types
- **Story 3.7:** Extraction Pipeline CLI - Runs all extractors including these four

## Tasks / Subtasks

- [ ] **Task 1: Verify Prerequisites** (AC: Dependencies available)
  - [ ] 1.1: Confirm Story 3.1 complete: `ls packages/pipeline/src/extractors/base.py`
  - [ ] 1.2: Confirm all four models exist: `cd packages/pipeline && uv run python -c "from src.extractors import Methodology, MethodologyStep, Checklist, ChecklistItem, Persona, Workflow, WorkflowStep, BaseExtractor, ExtractionType; print('OK')"`
  - [ ] 1.3: Confirm prompts directory: `ls packages/pipeline/src/extractors/prompts/`
  - [ ] 1.4: Confirm Story 3.2/3.3 pattern reference exists: `ls packages/pipeline/src/extractors/decision_extractor.py packages/pipeline/src/extractors/pattern_extractor.py`

- [ ] **Task 2: Create MethodologyExtractor Class** (AC: Methodology extraction)
  - [ ] 2.1: Create `packages/pipeline/src/extractors/methodology_extractor.py`
  - [ ] 2.2: Extend `BaseExtractor` ABC
  - [ ] 2.3: Implement `extraction_type` property returning `ExtractionType.METHODOLOGY`
  - [ ] 2.4: Implement `model_class` property returning `Methodology`
  - [ ] 2.5: Implement `extract()` method with Methodology model validation
  - [ ] 2.6: Implement `get_prompt()` method loading from `methodology.md`
  - [ ] 2.7: Register with `extractor_registry`

- [ ] **Task 3: Create ChecklistExtractor Class** (AC: Checklist extraction)
  - [ ] 3.1: Create `packages/pipeline/src/extractors/checklist_extractor.py`
  - [ ] 3.2: Extend `BaseExtractor` ABC
  - [ ] 3.3: Implement `extraction_type` property returning `ExtractionType.CHECKLIST`
  - [ ] 3.4: Implement `model_class` property returning `Checklist`
  - [ ] 3.5: Implement `extract()` method with Checklist model validation
  - [ ] 3.6: Implement `get_prompt()` method loading from `checklist.md`
  - [ ] 3.7: Register with `extractor_registry`

- [ ] **Task 4: Create PersonaExtractor Class** (AC: Persona extraction)
  - [ ] 4.1: Create `packages/pipeline/src/extractors/persona_extractor.py`
  - [ ] 4.2: Extend `BaseExtractor` ABC
  - [ ] 4.3: Implement `extraction_type` property returning `ExtractionType.PERSONA`
  - [ ] 4.4: Implement `model_class` property returning `Persona`
  - [ ] 4.5: Implement `extract()` method with Persona model validation
  - [ ] 4.6: Implement `get_prompt()` method loading from `persona.md`
  - [ ] 4.7: Register with `extractor_registry`

- [ ] **Task 5: Create WorkflowExtractor Class** (AC: Workflow extraction)
  - [ ] 5.1: Create `packages/pipeline/src/extractors/workflow_extractor.py`
  - [ ] 5.2: Extend `BaseExtractor` ABC
  - [ ] 5.3: Implement `extraction_type` property returning `ExtractionType.WORKFLOW`
  - [ ] 5.4: Implement `model_class` property returning `Workflow`
  - [ ] 5.5: Implement `extract()` method with Workflow model validation
  - [ ] 5.6: Implement `get_prompt()` method loading from `workflow.md`
  - [ ] 5.7: Register with `extractor_registry`

- [ ] **Task 6: Create All Four Extraction Prompts** (AC: Prompt files exist)
  - [ ] 6.1: Create `packages/pipeline/src/extractors/prompts/methodology.md`
  - [ ] 6.2: Create `packages/pipeline/src/extractors/prompts/checklist.md`
  - [ ] 6.3: Create `packages/pipeline/src/extractors/prompts/persona.md`
  - [ ] 6.4: Create `packages/pipeline/src/extractors/prompts/workflow.md`
  - [ ] 6.5: Include specific extraction rules for each type
  - [ ] 6.6: Include JSON schema for each extraction type
  - [ ] 6.7: Include example extractions for each type

- [ ] **Task 7: Update Module Exports** (AC: Clean imports)
  - [ ] 7.1: Add all four extractors to `packages/pipeline/src/extractors/__init__.py`
  - [ ] 7.2: Verify imports work: `from src.extractors import MethodologyExtractor, ChecklistExtractor, PersonaExtractor, WorkflowExtractor`
  - [ ] 7.3: Verify registry contains all four: `extractor_registry.is_supported(ExtractionType.METHODOLOGY)`, etc.

- [ ] **Task 8: Create Unit Tests for All Four Extractors** (AC: All tests pass)
  - [ ] 8.1: Create `packages/pipeline/tests/test_extractors/test_methodology_extractor.py`
  - [ ] 8.2: Create `packages/pipeline/tests/test_extractors/test_checklist_extractor.py`
  - [ ] 8.3: Create `packages/pipeline/tests/test_extractors/test_persona_extractor.py`
  - [ ] 8.4: Create `packages/pipeline/tests/test_extractors/test_workflow_extractor.py`
  - [ ] 8.5: Test each extractor's `extraction_type` and `model_class` properties
  - [ ] 8.6: Test `extract()` returns list of results for each
  - [ ] 8.7: Test prompt loading for each extractor
  - [ ] 8.8: Test registry retrieval for each extraction type
  - [ ] 8.9: Test all Pydantic models (including nested: MethodologyStep, ChecklistItem, WorkflowStep)
  - [ ] 8.10: Test source attribution preservation for all models
  - [ ] 8.11: Run all tests: `cd packages/pipeline && uv run pytest tests/test_extractors/test_*_extractor.py -v`

## Dev Notes

### Critical Builder-Focused Context

**THESE FOUR EXTRACTORS ARE FOR THE BUILDER (Philippebeliveau), NOT END USERS.**

From the Architecture Document (architecture.md:62-73):

| Type | Audience | Purpose | FR |
|------|----------|---------|-----|
| Methodology | **Builder** | Step-by-step processes from books | FR2.4 |
| Checklist | **Builder** | Verification criteria for workflow steps | FR2.5 |
| Persona | **Builder** | Role definitions for agent creation | FR2.6 |
| Workflow | **Builder** | Process sequences for BMAD workflow design | FR2.7 |

**Builder Workflow (From PRD User Journey):**
```
1. Ingest book into knowledge base
2. Query: "What methodologies does this book describe?"
3. Extract methodology steps, decisions, warnings for each step
4. Use extractions to build BMAD workflow structure
5. Query: "What persona handles this domain?"
6. Use persona extraction to define BMAD agent
7. Query: "What should this agent know about X?"
8. Use decisions/patterns/warnings to craft agent prompts
```

### Pydantic Model Structures (From Story 3.1)

**Methodology Model:**
```python
class MethodologyStep(BaseModel):
    """Single step in a methodology."""
    order: int              # Step number (1, 2, 3...)
    title: str              # Step title
    description: str        # Detailed step description
    tips: list[str] = []    # Optional tips for this step


class Methodology(ExtractionBase):
    """Methodology extraction.

    Captures step-by-step processes from books.
    Used by builder for BMAD workflow creation.
    """
    type: ExtractionType = ExtractionType.METHODOLOGY
    name: str                           # Methodology name
    steps: list[MethodologyStep] = []   # Ordered steps
    prerequisites: list[str] = []       # Required before starting
    outputs: list[str] = []             # Expected deliverables
```

**Checklist Model:**
```python
class ChecklistItem(BaseModel):
    """Single checklist item."""
    item: str           # Checklist item text
    required: bool = True  # Whether mandatory


class Checklist(ExtractionBase):
    """Checklist extraction.

    Captures verification criteria.
    Used by builder for workflow validation steps.
    """
    type: ExtractionType = ExtractionType.CHECKLIST
    name: str                           # Checklist name
    items: list[ChecklistItem] = []     # Checklist items
    context: str = ""                   # When to use this checklist
```

**Persona Model:**
```python
class Persona(ExtractionBase):
    """Persona extraction.

    Captures role definitions.
    Used by builder for BMAD agent creation.
    """
    type: ExtractionType = ExtractionType.PERSONA
    role: str                           # Role title
    responsibilities: list[str] = []    # What they do
    expertise: list[str] = []           # Domain expertise
    communication_style: str = ""       # How they communicate
```

**Workflow Model:**
```python
class WorkflowStep(BaseModel):
    """Single step in a workflow."""
    order: int          # Step number
    action: str         # What to do
    outputs: list[str] = []  # Step outputs


class Workflow(ExtractionBase):
    """Workflow extraction.

    Captures process sequences.
    Used by builder for BMAD workflow design.
    """
    type: ExtractionType = ExtractionType.WORKFLOW
    name: str                           # Workflow name
    trigger: str = ""                   # What starts the workflow
    steps: list[WorkflowStep] = []      # Workflow steps
    decision_points: list[str] = []     # Key decision points
```

**All inherit from ExtractionBase:**
- `id: str` - Unique extraction ID
- `source_id: str` - Reference to sources collection (REQUIRED)
- `chunk_id: str` - Reference to chunks collection (REQUIRED)
- `type: ExtractionType` - Set to appropriate type
- `topics: list[str]` - Auto-tagged topics
- `schema_version: str` - "1.0.0"
- `extracted_at: datetime` - Timestamp
- `confidence: float` - 0.0-1.0 score

### Implementation Pattern (Follow Story 3.2/3.3)

```python
# packages/pipeline/src/extractors/methodology_extractor.py
from typing import Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionType,
    ExtractionBase,
    ExtractionResult,
    Methodology,
    extractor_registry,
)

logger = structlog.get_logger()


class MethodologyExtractor(BaseExtractor):
    """Extractor for step-by-step methodologies from books.

    Identifies and structures process methodologies for BMAD workflow
    creation. Used by builder to transform book content into executable
    workflows.

    Example methodologies:
    - RAG Implementation Methodology: Steps to build a RAG system
    - LLM Evaluation Framework: Process for evaluating model outputs
    - Fine-tuning Workflow: Steps for domain-specific fine-tuning
    """

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for methodologies."""
        return ExtractionType.METHODOLOGY

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Methodology model class."""
        return Methodology

    def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str
    ) -> list[ExtractionResult]:
        """Extract methodologies from chunk content.

        Args:
            chunk_content: Text content to extract methodologies from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with Methodology extractions.
        """
        logger.info(
            "methodology_extraction_started",
            chunk_id=chunk_id,
            source_id=source_id,
            content_length=len(chunk_content)
        )

        # Get prompt for Claude
        prompt = self.get_prompt()

        # Claude-as-extractor pattern: actual extraction done during ingestion
        results: list[ExtractionResult] = []

        logger.info(
            "methodology_extraction_completed",
            chunk_id=chunk_id,
            methodology_count=len(results)
        )

        return results

    def get_prompt(self) -> str:
        """Load methodology extraction prompt from file.

        Returns:
            Prompt string for LLM extraction.

        Raises:
            PromptLoadError: If prompt file cannot be loaded.
        """
        return self._load_prompt("methodology")


# Register extractor with global registry
extractor_registry.register(ExtractionType.METHODOLOGY, MethodologyExtractor)
```

**REPEAT THIS PATTERN FOR ALL FOUR EXTRACTORS** - Only change:
- Class name (ChecklistExtractor, PersonaExtractor, WorkflowExtractor)
- Docstring examples
- ExtractionType value
- Model class
- Prompt file name
- Log event names

### Prompt Templates

**methodology.md:**
```markdown
# Methodology Extraction Prompt

You are a knowledge extraction assistant. Extract step-by-step methodologies from the provided text.

## What is a Methodology?

A methodology is a structured process with ordered steps. In AI engineering, methodologies include:
- Implementation processes (e.g., "How to build a RAG system")
- Evaluation frameworks (e.g., "LLM output quality assessment")
- Development workflows (e.g., "Fine-tuning preparation steps")
- Design processes (e.g., "Prompt engineering methodology")

## Extraction Rules

1. Only extract methodologies with clear, ordered steps
2. A methodology MUST have a name and at least 2 steps
3. Each step MUST have order, title, and description
4. Capture prerequisites (what must be done/known before starting)
5. Capture outputs (what the methodology produces)
6. Return valid JSON matching the schema below
7. If no methodologies found, return an empty array []

## Output Schema

```json
{
  "name": "Methodology Name",
  "steps": [
    {
      "order": 1,
      "title": "Step Title",
      "description": "Detailed description of what to do",
      "tips": ["Optional helpful tip"]
    }
  ],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
  "outputs": ["Output/deliverable 1", "Output/deliverable 2"]
}
```

## Example Extraction

**Input text:**
"Building a RAG system requires several key steps. First, prepare your document corpus by collecting and cleaning your source documents. Next, implement chunking - split documents into semantically coherent pieces of 500-1000 tokens. Third, generate embeddings using a model like all-MiniLM-L6-v2. Fourth, store vectors in a database like Qdrant. Finally, implement retrieval with reranking for quality results. Before starting, ensure you have access to your document corpus and have chosen your embedding model. The result is a working retrieval pipeline."

**Extracted methodology:**
```json
{
  "name": "RAG System Implementation",
  "steps": [
    {
      "order": 1,
      "title": "Prepare Document Corpus",
      "description": "Collect and clean source documents for processing",
      "tips": []
    },
    {
      "order": 2,
      "title": "Implement Chunking",
      "description": "Split documents into semantically coherent pieces of 500-1000 tokens",
      "tips": ["Keep chunks semantically coherent"]
    },
    {
      "order": 3,
      "title": "Generate Embeddings",
      "description": "Use embedding model like all-MiniLM-L6-v2 to create vector representations",
      "tips": []
    },
    {
      "order": 4,
      "title": "Store Vectors",
      "description": "Store embeddings in vector database like Qdrant",
      "tips": []
    },
    {
      "order": 5,
      "title": "Implement Retrieval",
      "description": "Build retrieval pipeline with reranking for quality results",
      "tips": ["Add reranking for better quality"]
    }
  ],
  "prerequisites": [
    "Access to document corpus",
    "Embedding model selected"
  ],
  "outputs": [
    "Working retrieval pipeline"
  ]
}
```

## Now extract methodologies from this text:

{{chunk_content}}
```

**checklist.md:**
```markdown
# Checklist Extraction Prompt

You are a knowledge extraction assistant. Extract verification checklists from the provided text.

## What is a Checklist?

A checklist is a list of items to verify or complete. In AI engineering, checklists include:
- Pre-deployment checks (e.g., "Model release checklist")
- Quality gates (e.g., "RAG evaluation checklist")
- Review criteria (e.g., "Prompt review checklist")
- Validation lists (e.g., "Data quality checklist")

## Extraction Rules

1. Only extract explicit checklists from the text
2. A checklist MUST have a name and at least 2 items
3. Each item should be actionable/verifiable
4. Mark items as required (true) or optional (false)
5. Include context about when to use the checklist
6. Return valid JSON matching the schema below
7. If no checklists found, return an empty array []

## Output Schema

```json
{
  "name": "Checklist Name",
  "items": [
    {"item": "Checklist item text", "required": true},
    {"item": "Optional item", "required": false}
  ],
  "context": "When and where to use this checklist"
}
```

## Example Extraction

**Input text:**
"Before deploying your LLM to production, verify: model latency under 500ms, error rate below 1%, input validation in place, rate limiting configured, logging enabled. Also consider: A/B testing setup, rollback procedure documented."

**Extracted checklist:**
```json
{
  "name": "LLM Production Deployment Checklist",
  "items": [
    {"item": "Model latency under 500ms", "required": true},
    {"item": "Error rate below 1%", "required": true},
    {"item": "Input validation in place", "required": true},
    {"item": "Rate limiting configured", "required": true},
    {"item": "Logging enabled", "required": true},
    {"item": "A/B testing setup", "required": false},
    {"item": "Rollback procedure documented", "required": false}
  ],
  "context": "Use before deploying LLM model to production environment"
}
```

## Now extract checklists from this text:

{{chunk_content}}
```

**persona.md:**
```markdown
# Persona Extraction Prompt

You are a knowledge extraction assistant. Extract role/persona definitions from the provided text.

## What is a Persona?

A persona is a role definition that can be used to create AI agents. In AI engineering, personas include:
- Technical roles (e.g., "ML Engineer", "Data Scientist")
- Domain experts (e.g., "RAG Specialist", "Prompt Engineer")
- Process roles (e.g., "Code Reviewer", "QA Engineer")
- Stakeholder views (e.g., "End User", "Product Owner")

## Extraction Rules

1. Only extract personas explicitly described in the text
2. A persona MUST have a clear role title
3. Include responsibilities (what they do)
4. Include expertise areas (what they know)
5. Include communication style if described
6. Return valid JSON matching the schema below
7. If no personas found, return an empty array []

## Output Schema

```json
{
  "role": "Role Title",
  "responsibilities": ["Responsibility 1", "Responsibility 2"],
  "expertise": ["Domain expertise 1", "Domain expertise 2"],
  "communication_style": "How they communicate (formal, technical, etc.)"
}
```

## Example Extraction

**Input text:**
"The RAG Specialist is responsible for designing and implementing retrieval-augmented generation systems. They need deep expertise in embedding models, vector databases, and chunking strategies. They should also understand query optimization and reranking techniques. They communicate technically with development teams and translate complex concepts for stakeholders."

**Extracted persona:**
```json
{
  "role": "RAG Specialist",
  "responsibilities": [
    "Design retrieval-augmented generation systems",
    "Implement RAG pipelines",
    "Optimize query and retrieval performance"
  ],
  "expertise": [
    "Embedding models",
    "Vector databases",
    "Chunking strategies",
    "Query optimization",
    "Reranking techniques"
  ],
  "communication_style": "Technical with development teams, translates complex concepts for stakeholders"
}
```

## Now extract personas from this text:

{{chunk_content}}
```

**workflow.md:**
```markdown
# Workflow Extraction Prompt

You are a knowledge extraction assistant. Extract process workflows from the provided text.

## What is a Workflow?

A workflow is a sequence of steps triggered by an event. In AI engineering, workflows include:
- Development workflows (e.g., "Feature implementation flow")
- Operational workflows (e.g., "Model retraining trigger")
- Review workflows (e.g., "PR review process")
- Incident workflows (e.g., "Model degradation response")

## Extraction Rules

1. Only extract workflows with clear triggers and steps
2. A workflow MUST have a name, trigger, and at least 2 steps
3. Each step has order, action, and optional outputs
4. Identify decision points in the workflow
5. Return valid JSON matching the schema below
6. If no workflows found, return an empty array []

## Output Schema

```json
{
  "name": "Workflow Name",
  "trigger": "What initiates this workflow",
  "steps": [
    {
      "order": 1,
      "action": "What to do in this step",
      "outputs": ["Output from this step"]
    }
  ],
  "decision_points": ["Key decision point 1", "Key decision point 2"]
}
```

## Example Extraction

**Input text:**
"When model performance drops below threshold, trigger the retraining workflow. First, collect recent production data. Then, validate data quality - if quality is poor, escalate to data team. Next, fine-tune the model on new data. Run evaluation suite. If metrics improve, deploy to staging. Finally, run A/B test before production rollout."

**Extracted workflow:**
```json
{
  "name": "Model Retraining Workflow",
  "trigger": "Model performance drops below threshold",
  "steps": [
    {
      "order": 1,
      "action": "Collect recent production data",
      "outputs": ["Training dataset"]
    },
    {
      "order": 2,
      "action": "Validate data quality",
      "outputs": ["Quality report"]
    },
    {
      "order": 3,
      "action": "Fine-tune model on new data",
      "outputs": ["Retrained model"]
    },
    {
      "order": 4,
      "action": "Run evaluation suite",
      "outputs": ["Evaluation metrics"]
    },
    {
      "order": 5,
      "action": "Deploy to staging",
      "outputs": ["Staging deployment"]
    },
    {
      "order": 6,
      "action": "Run A/B test before production rollout",
      "outputs": ["A/B test results", "Production deployment"]
    }
  ],
  "decision_points": [
    "Data quality check - escalate if poor",
    "Metrics improvement check before staging deploy"
  ]
}
```

## Now extract workflows from this text:

{{chunk_content}}
```

### Topic Auto-Tagging for Builder Extractions

The base class `_generate_topics()` handles topic extraction. For builder-focused extractions, relevant topics include:

- `methodology` - Process methodologies
- `workflow` - Process sequences
- `checklist` - Verification lists
- `agents` - Agent/persona related
- `rag` - RAG-related content
- `evaluation` - Evaluation and testing
- `fine-tuning` - Fine-tuning processes
- `deployment` - Deployment workflows
- `prompting` - Prompt engineering
- `training` - Model training

### Testing Strategy

```python
# packages/pipeline/tests/test_extractors/test_methodology_extractor.py
import pytest

from src.extractors import (
    MethodologyExtractor,
    Methodology,
    MethodologyStep,
    ExtractionType,
    extractor_registry,
)


class TestMethodologyExtractor:
    """Test MethodologyExtractor implementation."""

    @pytest.fixture
    def extractor(self) -> MethodologyExtractor:
        """Create methodology extractor instance."""
        return MethodologyExtractor()

    def test_extraction_type_is_methodology(self, extractor):
        """Extractor returns METHODOLOGY extraction type."""
        assert extractor.extraction_type == ExtractionType.METHODOLOGY

    def test_model_class_is_methodology(self, extractor):
        """Extractor uses Methodology model class."""
        assert extractor.model_class == Methodology

    def test_get_prompt_loads_methodology_md(self, extractor):
        """Prompt is loaded from methodology.md file."""
        prompt = extractor.get_prompt()
        assert "methodology" in prompt.lower()
        assert len(prompt) > 100

    def test_extract_returns_list(self, extractor):
        """Extract method returns list of results."""
        results = extractor.extract(
            chunk_content="Sample methodology text",
            chunk_id="chunk-123",
            source_id="source-456"
        )
        assert isinstance(results, list)

    def test_registry_contains_methodology_extractor(self):
        """Methodology extractor is registered in global registry."""
        assert extractor_registry.is_supported(ExtractionType.METHODOLOGY)
        extractor = extractor_registry.get_extractor(ExtractionType.METHODOLOGY)
        assert isinstance(extractor, MethodologyExtractor)


class TestMethodologyModel:
    """Test Methodology Pydantic model."""

    def test_methodology_required_fields(self):
        """Methodology requires source_id, chunk_id, name."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="RAG Implementation"
        )
        assert methodology.source_id == "src-123"
        assert methodology.chunk_id == "chunk-456"
        assert methodology.type == ExtractionType.METHODOLOGY
        assert methodology.schema_version == "1.0.0"

    def test_methodology_with_steps(self):
        """Methodology can contain ordered steps."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Methodology",
            steps=[
                MethodologyStep(order=1, title="Step 1", description="Do first thing"),
                MethodologyStep(order=2, title="Step 2", description="Do second thing"),
            ],
            prerequisites=["Prereq 1"],
            outputs=["Output 1"]
        )
        assert len(methodology.steps) == 2
        assert methodology.steps[0].order == 1
        assert methodology.steps[1].title == "Step 2"

    def test_methodology_step_with_tips(self):
        """MethodologyStep can include tips."""
        step = MethodologyStep(
            order=1,
            title="Chunking",
            description="Split documents",
            tips=["Keep chunks semantic", "Use 500-1000 tokens"]
        )
        assert len(step.tips) == 2

    def test_methodology_has_source_attribution(self):
        """Methodology includes source attribution fields."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test"
        )
        assert hasattr(methodology, "source_id")
        assert hasattr(methodology, "chunk_id")
        assert hasattr(methodology, "topics")
        assert hasattr(methodology, "schema_version")
```

**REPEAT SIMILAR TESTS FOR:** ChecklistExtractor, PersonaExtractor, WorkflowExtractor

### Project Structure Alignment

```
packages/pipeline/
├── src/
│   ├── extractors/
│   │   ├── __init__.py              # Add all 4 extractor exports
│   │   ├── base.py                  # Story 3.1 - BaseExtractor, all models
│   │   ├── decision_extractor.py    # Story 3.2
│   │   ├── pattern_extractor.py     # Story 3.3
│   │   ├── warning_extractor.py     # Story 3.4
│   │   ├── methodology_extractor.py # THIS STORY
│   │   ├── checklist_extractor.py   # THIS STORY
│   │   ├── persona_extractor.py     # THIS STORY
│   │   ├── workflow_extractor.py    # THIS STORY
│   │   └── prompts/
│   │       ├── _base.md
│   │       ├── decision.md
│   │       ├── pattern.md
│   │       ├── warning.md
│   │       ├── methodology.md       # THIS STORY
│   │       ├── checklist.md         # THIS STORY
│   │       ├── persona.md           # THIS STORY
│   │       └── workflow.md          # THIS STORY
└── tests/
    └── test_extractors/
        ├── conftest.py
        ├── test_base.py
        ├── test_decision_extractor.py
        ├── test_pattern_extractor.py
        ├── test_warning_extractor.py
        ├── test_methodology_extractor.py  # THIS STORY
        ├── test_checklist_extractor.py    # THIS STORY
        ├── test_persona_extractor.py      # THIS STORY
        └── test_workflow_extractor.py     # THIS STORY
```

### Library & Framework Requirements

No additional dependencies beyond Story 3.1 requirements:
- pydantic>=2.0 (model validation)
- structlog (logging)
- pytest, pytest-asyncio (testing)

### Code Reuse from BaseExtractor

**DO NOT REINVENT these utilities from Story 3.1:**
- `_load_prompt(prompt_name)` - Load prompt from file
- `_parse_llm_response(response)` - Parse JSON from LLM output
- `_validate_extraction(data, chunk_id, source_id)` - Validate with Pydantic
- `_generate_topics(content)` - Auto-tag topics

### Anti-Patterns to Avoid

1. **Don't duplicate Pydantic models** - Use models from `src.extractors.base`
2. **Don't forget registry registration** - Each extractor MUST call `extractor_registry.register()` at module level
3. **Don't skip nested model validation** - MethodologyStep, ChecklistItem, WorkflowStep are nested
4. **Don't omit structlog logging** - No print statements
5. **Don't create separate prompts directory** - Use existing `prompts/` folder

### Architecture Compliance Checklist

**Per Extractor (4 total):**
- [ ] File at correct location (e.g., `methodology_extractor.py`)
- [ ] Extends `BaseExtractor` ABC
- [ ] Implements `extraction_type` property with correct enum
- [ ] Implements `model_class` property with correct model
- [ ] Implements `extract()` returning `list[ExtractionResult]`
- [ ] Implements `get_prompt()` loading from correct file
- [ ] Registered with `extractor_registry` at module level
- [ ] Uses structlog for all logging

**Prompt Files (4 total):**
- [ ] methodology.md with schema and example
- [ ] checklist.md with schema and example
- [ ] persona.md with schema and example
- [ ] workflow.md with schema and example

**Tests (4 files):**
- [ ] Tests for each extractor's properties
- [ ] Tests for model validation including nested models
- [ ] Tests for registry registration
- [ ] All tests pass

### Why This Story Has Four Extractors

From the epics file (epics.md:446-464), Story 3.5 was designed to handle all builder-focused extraction types together because:

1. **Shared Audience:** All four serve the builder, not end users
2. **Similar Complexity:** Each is simpler than Decision/Pattern extractors
3. **Related Purpose:** All feed into BMAD workflow/agent creation
4. **Efficiency:** Implementing together ensures consistent patterns

### BMAD Integration Context

These extractions enable the builder workflow:

```
Methodology → BMAD Workflow Structure
   └─ Steps map to workflow steps
   └─ Prerequisites become workflow preconditions
   └─ Outputs become workflow deliverables

Checklist → BMAD Workflow Validation
   └─ Items become validation criteria in workflow templates
   └─ Required flags determine critical vs optional checks

Persona → BMAD Agent Definition
   └─ Role becomes agent name/title
   └─ Responsibilities inform agent prompt
   └─ Expertise guides agent knowledge scope
   └─ Communication style shapes agent tone

Workflow → BMAD Workflow Triggers
   └─ Trigger events initiate workflows
   └─ Decision points become branching conditions
   └─ Steps inform workflow actions
```

### References

**Architecture Decisions:**
- [Architecture: Extraction Types] `_bmad-output/architecture.md:62-73`
- [Architecture: Model Structures] `_bmad-output/architecture.md:339-409` (nested models)
- [Architecture: NFR6 Extensibility] `_bmad-output/architecture.md:80`

**Requirements:**
- [PRD: FR-2.4 Methodology Extraction] `_bmad-output/prd.md:256`
- [PRD: FR-2.5 Checklist Extraction] `_bmad-output/prd.md:257`
- [PRD: FR-2.6 Persona Extraction] `_bmad-output/prd.md:258`
- [PRD: FR-2.7 Workflow Extraction] `_bmad-output/prd.md:259`
- [PRD: FR-2.9 Topic Tagging] `_bmad-output/prd.md:262`
- [PRD: FR-2.10 Source Attribution] `_bmad-output/prd.md:263`

**Epic Context:**
- [Epics: Story 3.5] `_bmad-output/epics.md:446-464`
- [Epics: Epic 3 Goals] `_bmad-output/epics.md:371-376`
- [Epics: Builder User Journey] `_bmad-output/prd.md:161-176`

**Project Rules:**
- [Project Context: All Rules] `_bmad-output/project-context.md`

**Story Dependencies:**
- [Story 3.1: Base Extractor Interface] - All four models, BaseExtractor ABC
- [Story 3.2: Decision Extractor] - Implementation pattern to follow
- [Story 3.3: Pattern Extractor] - Validates consistent pattern

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

_To be filled by dev agent - list all files created/modified:_
- packages/pipeline/src/extractors/methodology_extractor.py (CREATE)
- packages/pipeline/src/extractors/checklist_extractor.py (CREATE)
- packages/pipeline/src/extractors/persona_extractor.py (CREATE)
- packages/pipeline/src/extractors/workflow_extractor.py (CREATE)
- packages/pipeline/src/extractors/prompts/methodology.md (CREATE or UPDATE)
- packages/pipeline/src/extractors/prompts/checklist.md (CREATE or UPDATE)
- packages/pipeline/src/extractors/prompts/persona.md (CREATE or UPDATE)
- packages/pipeline/src/extractors/prompts/workflow.md (CREATE or UPDATE)
- packages/pipeline/src/extractors/__init__.py (MODIFY - add 4 exports)
- packages/pipeline/tests/test_extractors/test_methodology_extractor.py (CREATE)
- packages/pipeline/tests/test_extractors/test_checklist_extractor.py (CREATE)
- packages/pipeline/tests/test_extractors/test_persona_extractor.py (CREATE)
- packages/pipeline/tests/test_extractors/test_workflow_extractor.py (CREATE)
