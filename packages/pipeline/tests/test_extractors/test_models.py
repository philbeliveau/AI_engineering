"""Tests for extraction Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.extractors import (
    Checklist,
    ChecklistItem,
    Decision,
    ExtractionType,
    Methodology,
    MethodologyStep,
    Pattern,
    Persona,
    Warning,
    Workflow,
    WorkflowStep,
)
from src.extractors.base import ExtractionBase, ExtractionLevel


class TestExtractionType:
    """Test ExtractionType enum."""

    def test_all_types_defined(self):
        """All 7 extraction types are defined."""
        types = list(ExtractionType)
        assert len(types) == 7
        assert ExtractionType.DECISION in types
        assert ExtractionType.PATTERN in types
        assert ExtractionType.WARNING in types
        assert ExtractionType.METHODOLOGY in types
        assert ExtractionType.CHECKLIST in types
        assert ExtractionType.PERSONA in types
        assert ExtractionType.WORKFLOW in types

    def test_type_values_are_lowercase(self):
        """Extraction type values are lowercase strings."""
        for t in ExtractionType:
            assert t.value == t.value.lower()


class TestDecisionModel:
    """Test Decision model."""

    def test_decision_required_fields(self):
        """Decision model requires source_id, chunk_id, question."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Should I use RAG or fine-tuning?",
        )
        assert decision.source_id == "src-123"
        assert decision.chunk_id == "chunk-456"
        assert decision.question == "Should I use RAG or fine-tuning?"

    def test_decision_default_values(self):
        """Decision model has correct default values."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Test?",
        )
        assert decision.type == ExtractionType.DECISION
        assert decision.schema_version == "1.1.0"  # Updated for hierarchical extraction
        assert decision.options == []
        assert decision.considerations == []
        assert decision.recommended_approach is None
        assert decision.context == ""
        assert decision.topics == []
        assert decision.confidence == 0.8
        # New v1.1.0 defaults for hierarchical extraction
        assert decision.context_level == ExtractionLevel.CHUNK
        assert decision.context_id == ""
        assert decision.chunk_ids == []

    def test_decision_with_all_fields(self):
        """Decision model accepts all optional fields."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Should I use RAG?",
            options=["Yes", "No", "Both"],
            considerations=["Cost", "Accuracy"],
            recommended_approach="RAG for most cases",
            context="When building LLM apps",
            topics=["rag", "llm"],
            confidence=0.9,
        )
        assert len(decision.options) == 3
        assert len(decision.considerations) == 2
        assert decision.recommended_approach == "RAG for most cases"

    def test_decision_missing_required_field(self):
        """Decision model raises for missing required fields."""
        with pytest.raises(ValidationError):
            Decision(source_id="src-123", chunk_id="chunk-456")  # Missing question


class TestPatternModel:
    """Test Pattern model."""

    def test_pattern_required_fields(self):
        """Pattern model requires name, problem, solution."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="RAG",
            problem="LLM knowledge cutoff",
            solution="Retrieve relevant documents",
        )
        assert pattern.name == "RAG"
        assert pattern.problem == "LLM knowledge cutoff"
        assert pattern.solution == "Retrieve relevant documents"

    def test_pattern_default_type(self):
        """Pattern model has correct default type."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test",
            problem="Problem",
            solution="Solution",
        )
        assert pattern.type == ExtractionType.PATTERN

    def test_pattern_with_code_example(self):
        """Pattern model accepts code example."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Chunking",
            problem="Long documents",
            solution="Split into chunks",
            code_example="chunks = text.split('\\n\\n')",
        )
        assert pattern.code_example is not None


class TestWarningModel:
    """Test Warning model."""

    def test_warning_required_fields(self):
        """Warning model requires title, description."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Context Overflow",
            description="Too many tokens in prompt",
        )
        assert warning.title == "Context Overflow"
        assert warning.description == "Too many tokens in prompt"

    def test_warning_default_type(self):
        """Warning model has correct default type."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test",
            description="Test description",
        )
        assert warning.type == ExtractionType.WARNING

    def test_warning_with_all_fields(self):
        """Warning model accepts all optional fields."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Embedding Mismatch",
            description="Wrong vector dimensions",
            symptoms=["Search returns no results", "Index errors"],
            consequences=["Failed queries", "Data corruption"],
            prevention="Verify dimensions match index config",
        )
        assert len(warning.symptoms) == 2
        assert len(warning.consequences) == 2
        assert warning.prevention != ""


class TestMethodologyModel:
    """Test Methodology and MethodologyStep models."""

    def test_methodology_step_fields(self):
        """MethodologyStep has correct fields."""
        step = MethodologyStep(
            order=1,
            title="Prepare data",
            description="Clean and format data",
            tips=["Use pandas", "Handle nulls"],
        )
        assert step.order == 1
        assert step.title == "Prepare data"

    def test_methodology_required_fields(self):
        """Methodology model requires name."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="RAG Implementation",
        )
        assert methodology.name == "RAG Implementation"

    def test_methodology_with_steps(self):
        """Methodology model accepts steps."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Fine-tuning",
            steps=[
                MethodologyStep(order=1, title="Prepare data", description="Clean data"),
                MethodologyStep(order=2, title="Train model", description="Run training"),
            ],
            prerequisites=["GPU access", "Training data"],
            outputs=["Fine-tuned model"],
        )
        assert len(methodology.steps) == 2
        assert methodology.steps[0].order == 1

    def test_methodology_default_type(self):
        """Methodology model has correct default type."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test",
        )
        assert methodology.type == ExtractionType.METHODOLOGY


class TestChecklistModel:
    """Test Checklist and ChecklistItem models."""

    def test_checklist_item_fields(self):
        """ChecklistItem has correct fields."""
        item = ChecklistItem(item="Check vector dimensions", required=True)
        assert item.item == "Check vector dimensions"
        assert item.required is True

    def test_checklist_item_default_required(self):
        """ChecklistItem defaults to required=True."""
        item = ChecklistItem(item="Test item")
        assert item.required is True

    def test_checklist_required_fields(self):
        """Checklist model requires name."""
        checklist = Checklist(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Deployment Checklist",
        )
        assert checklist.name == "Deployment Checklist"

    def test_checklist_with_items(self):
        """Checklist model accepts items."""
        checklist = Checklist(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Review Checklist",
            items=[
                ChecklistItem(item="Run tests", required=True),
                ChecklistItem(item="Update docs", required=False),
            ],
            context="Before deployment",
        )
        assert len(checklist.items) == 2
        assert checklist.items[1].required is False


class TestPersonaModel:
    """Test Persona model."""

    def test_persona_required_fields(self):
        """Persona model requires role."""
        persona = Persona(
            source_id="src-123",
            chunk_id="chunk-456",
            role="ML Engineer",
        )
        assert persona.role == "ML Engineer"

    def test_persona_with_all_fields(self):
        """Persona model accepts all optional fields."""
        persona = Persona(
            source_id="src-123",
            chunk_id="chunk-456",
            role="Data Scientist",
            responsibilities=["Train models", "Analyze data"],
            expertise=["Python", "TensorFlow"],
            communication_style="Technical and precise",
        )
        assert len(persona.responsibilities) == 2
        assert len(persona.expertise) == 2

    def test_persona_default_type(self):
        """Persona model has correct default type."""
        persona = Persona(
            source_id="src-123",
            chunk_id="chunk-456",
            role="Test",
        )
        assert persona.type == ExtractionType.PERSONA


class TestWorkflowModel:
    """Test Workflow and WorkflowStep models."""

    def test_workflow_step_fields(self):
        """WorkflowStep has correct fields."""
        step = WorkflowStep(
            order=1,
            action="Process input",
            outputs=["Processed data"],
        )
        assert step.order == 1
        assert step.action == "Process input"

    def test_workflow_required_fields(self):
        """Workflow model requires name."""
        workflow = Workflow(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Document Ingestion",
        )
        assert workflow.name == "Document Ingestion"

    def test_workflow_with_all_fields(self):
        """Workflow model accepts all optional fields."""
        workflow = Workflow(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Query Processing",
            trigger="User submits query",
            steps=[
                WorkflowStep(order=1, action="Parse query", outputs=["Parsed query"]),
                WorkflowStep(order=2, action="Search index", outputs=["Results"]),
            ],
            decision_points=["Retry on failure?", "Cache results?"],
        )
        assert len(workflow.steps) == 2
        assert len(workflow.decision_points) == 2

    def test_workflow_default_type(self):
        """Workflow model has correct default type."""
        workflow = Workflow(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test",
        )
        assert workflow.type == ExtractionType.WORKFLOW


class TestAllModelsCommonFields:
    """Test that all extraction models have required common fields."""

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_source_id(self, model_class, extra_fields):
        """All extraction models include source_id field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "source_id")
        assert instance.source_id == "src-123"

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_chunk_id(self, model_class, extra_fields):
        """All extraction models include chunk_id field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "chunk_id")
        assert instance.chunk_id == "chunk-456"

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_topics(self, model_class, extra_fields):
        """All extraction models include topics field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "topics")
        assert isinstance(instance.topics, list)

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_schema_version(self, model_class, extra_fields):
        """All extraction models include schema_version field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "schema_version")
        assert instance.schema_version == "1.1.0"  # Updated for hierarchical extraction

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_extracted_at(self, model_class, extra_fields):
        """All extraction models include extracted_at field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "extracted_at")
        assert isinstance(instance.extracted_at, datetime)

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_confidence(self, model_class, extra_fields):
        """All extraction models include confidence field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "confidence")
        assert 0.0 <= instance.confidence <= 1.0


class TestExtractionBaseConfidence:
    """Test confidence field validation."""

    def test_confidence_at_bounds(self):
        """Confidence accepts values at boundaries."""
        low = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Test?",
            confidence=0.0,
        )
        high = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Test?",
            confidence=1.0,
        )
        assert low.confidence == 0.0
        assert high.confidence == 1.0

    def test_confidence_above_one_raises(self):
        """Confidence rejects values above 1.0."""
        with pytest.raises(ValidationError):
            Decision(
                source_id="src-123",
                chunk_id="chunk-456",
                question="Test?",
                confidence=1.5,
            )

    def test_confidence_below_zero_raises(self):
        """Confidence rejects values below 0.0."""
        with pytest.raises(ValidationError):
            Decision(
                source_id="src-123",
                chunk_id="chunk-456",
                question="Test?",
                confidence=-0.1,
            )


class TestExtractionLevel:
    """Test ExtractionLevel enum."""

    def test_all_levels_defined(self):
        """All 3 extraction levels are defined."""
        levels = list(ExtractionLevel)
        assert len(levels) == 3
        assert ExtractionLevel.CHAPTER in levels
        assert ExtractionLevel.SECTION in levels
        assert ExtractionLevel.CHUNK in levels

    def test_level_values_are_lowercase(self):
        """Extraction level values are lowercase strings."""
        for level in ExtractionLevel:
            assert level.value == level.value.lower()


class TestHierarchicalExtractionFields:
    """Test v1.1.0 hierarchical extraction fields on ExtractionBase."""

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_context_level(self, model_class, extra_fields):
        """All extraction models include context_level field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "context_level")
        assert instance.context_level == ExtractionLevel.CHUNK

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_context_id(self, model_class, extra_fields):
        """All extraction models include context_id field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "context_id")
        assert instance.context_id == ""

    @pytest.mark.parametrize(
        "model_class,extra_fields",
        [
            (Decision, {"question": "Test?"}),
            (Pattern, {"name": "Test", "problem": "P", "solution": "S"}),
            (Warning, {"title": "Test", "description": "Desc"}),
            (Methodology, {"name": "Test"}),
            (Checklist, {"name": "Test"}),
            (Persona, {"role": "Test"}),
            (Workflow, {"name": "Test"}),
        ],
    )
    def test_model_has_chunk_ids(self, model_class, extra_fields):
        """All extraction models include chunk_ids field."""
        instance = model_class(
            source_id="src-123",
            chunk_id="chunk-456",
            **extra_fields,
        )
        assert hasattr(instance, "chunk_ids")
        assert isinstance(instance.chunk_ids, list)
        assert instance.chunk_ids == []

    def test_hierarchical_fields_can_be_set(self):
        """Hierarchical context fields can be explicitly set."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Test?",
            context_level=ExtractionLevel.SECTION,
            context_id="section-id-789",
            chunk_ids=["chunk-456", "chunk-457", "chunk-458"],
        )
        assert decision.context_level == ExtractionLevel.SECTION
        assert decision.context_id == "section-id-789"
        assert len(decision.chunk_ids) == 3
        assert "chunk-456" in decision.chunk_ids

    def test_chapter_level_extraction(self):
        """Methodology with chapter-level context."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="RAG Implementation",
            context_level=ExtractionLevel.CHAPTER,
            context_id="chapter-id-123",
            chunk_ids=["chunk-1", "chunk-2", "chunk-3", "chunk-4", "chunk-5"],
        )
        assert methodology.context_level == ExtractionLevel.CHAPTER
        assert len(methodology.chunk_ids) == 5

    def test_backward_compatibility_defaults(self):
        """Old-style extractions (without context fields) use defaults."""
        # Simulating loading an old 1.0.0 extraction
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test Warning",
            description="Test description",
            schema_version="1.0.0",  # Old version
        )
        # Should still have defaults for new fields
        assert warning.context_level == ExtractionLevel.CHUNK
        assert warning.context_id == ""
        assert warning.chunk_ids == []
