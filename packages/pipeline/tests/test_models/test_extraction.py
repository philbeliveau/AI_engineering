"""Tests for Extraction models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models import (
    ChecklistContent,
    ChecklistExtraction,
    DecisionContent,
    DecisionExtraction,
    Extraction,
    MethodologyContent,
    MethodologyExtraction,
    PatternContent,
    PatternExtraction,
    PersonaContent,
    PersonaExtraction,
    WarningContent,
    WarningExtraction,
    WorkflowContent,
    WorkflowExtraction,
)
from src.models.extraction import CURRENT_SCHEMA_VERSION


class TestContentModels:
    """Tests for type-specific content models."""

    def test_decision_content_complete(self) -> None:
        """Test creating a DecisionContent with all fields."""
        content = DecisionContent(
            question="Which embedding model should we use?",
            options=["all-MiniLM-L6-v2", "text-embedding-ada-002"],
            considerations=["Cost", "Latency", "Quality"],
            recommended_approach="all-MiniLM-L6-v2 for local inference",
        )

        assert content.question == "Which embedding model should we use?"
        assert len(content.options) == 2
        assert len(content.considerations) == 3
        assert content.recommended_approach == "all-MiniLM-L6-v2 for local inference"

    def test_decision_content_minimal(self) -> None:
        """Test creating a DecisionContent with minimal fields."""
        content = DecisionContent(question="What database to use?")

        assert content.question == "What database to use?"
        assert content.options == []
        assert content.considerations == []
        assert content.recommended_approach is None

    def test_pattern_content_complete(self) -> None:
        """Test creating a PatternContent with all fields."""
        content = PatternContent(
            name="Repository Pattern",
            problem="Need to abstract data access layer",
            solution="Create repository interface with CRUD methods",
            code_example="class UserRepository:\n    def get(self, id): ...",
            context="Domain-driven design applications",
            trade_offs=["Adds abstraction layer", "May be overkill for simple apps"],
        )

        assert content.name == "Repository Pattern"
        assert "abstract" in content.problem
        assert "repository" in content.solution.lower()
        assert "class" in content.code_example
        assert content.context is not None
        assert len(content.trade_offs) == 2

    def test_warning_content_complete(self) -> None:
        """Test creating a WarningContent with all fields."""
        content = WarningContent(
            title="N+1 Query Problem",
            description="Loading related data causes excessive database queries",
            symptoms=["Slow page loads", "High database CPU"],
            consequences=["Performance degradation", "Database overload"],
            prevention="Use eager loading or batch queries",
        )

        assert content.title == "N+1 Query Problem"
        assert len(content.symptoms) == 2
        assert len(content.consequences) == 2
        assert content.prevention is not None

    def test_methodology_content_complete(self) -> None:
        """Test creating a MethodologyContent with all fields."""
        content = MethodologyContent(
            name="Test-Driven Development",
            steps=["Write failing test", "Write minimal code", "Refactor"],
            prerequisites=["Testing framework", "Code coverage tools"],
            outputs=["Tested code", "High coverage"],
        )

        assert content.name == "Test-Driven Development"
        assert len(content.steps) == 3
        assert len(content.prerequisites) == 2
        assert len(content.outputs) == 2

    def test_checklist_content_complete(self) -> None:
        """Test creating a ChecklistContent with all fields."""
        content = ChecklistContent(
            name="Code Review Checklist",
            items=["Check for bugs", "Verify tests", "Review style"],
            context="Before merging pull requests",
        )

        assert content.name == "Code Review Checklist"
        assert len(content.items) == 3
        assert content.context is not None

    def test_persona_content_complete(self) -> None:
        """Test creating a PersonaContent with all fields."""
        content = PersonaContent(
            role="Senior Developer",
            responsibilities=["Code review", "Architecture decisions", "Mentoring"],
            expertise=["Python", "System design", "Testing"],
            communication_style="Clear and constructive",
        )

        assert content.role == "Senior Developer"
        assert len(content.responsibilities) == 3
        assert len(content.expertise) == 3
        assert content.communication_style is not None

    def test_workflow_content_complete(self) -> None:
        """Test creating a WorkflowContent with all fields."""
        content = WorkflowContent(
            name="Feature Development Workflow",
            trigger="New feature request",
            steps=["Design", "Implement", "Test", "Review", "Deploy"],
            decision_points=["Technical approach", "Scope changes"],
        )

        assert content.name == "Feature Development Workflow"
        assert content.trigger is not None
        assert len(content.steps) == 5
        assert len(content.decision_points) == 2


class TestExtractionModel:
    """Tests for the base Extraction Pydantic model."""

    def test_extraction_valid_complete(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test creating a valid Extraction with all fields."""
        extraction = Extraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            type="decision",
            content={
                "question": "Which database?",
                "options": ["MongoDB", "PostgreSQL"],
                "considerations": ["Flexibility", "ACID"],
                "recommended_approach": "MongoDB for document store",
            },
            topics=["database", "architecture"],
            extracted_at=sample_datetime,
        )

        assert extraction.id == valid_object_id
        assert extraction.source_id == valid_object_id_2
        assert extraction.chunk_id == valid_object_id_3
        assert extraction.type == "decision"
        # Content can be coerced to DecisionContent if it matches the schema
        if isinstance(extraction.content, dict):
            assert extraction.content["question"] == "Which database?"
        else:
            assert extraction.content.question == "Which database?"
        assert extraction.topics == ["database", "architecture"]
        assert extraction.schema_version == CURRENT_SCHEMA_VERSION
        assert extraction.extracted_at == sample_datetime

    def test_extraction_valid_minimal(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test creating a valid Extraction with minimal required fields."""
        extraction = Extraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            type="warning",
            content={"title": "Warning", "description": "Be careful"},
            extracted_at=sample_datetime,
        )

        assert extraction.id == valid_object_id
        assert extraction.type == "warning"
        assert extraction.topics == []  # Default empty list
        assert extraction.schema_version == CURRENT_SCHEMA_VERSION

    def test_extraction_all_types(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test all valid extraction types with type-appropriate content."""
        # Each extraction type needs content that matches its schema
        type_content_map = {
            "decision": {"question": "Test question?", "options": [], "considerations": []},
            "pattern": {"name": "Test", "problem": "Test problem", "solution": "Test solution"},
            "warning": {"title": "Test", "description": "Test warning"},
            "methodology": {"name": "Test", "steps": [], "prerequisites": [], "outputs": []},
            "checklist": {"name": "Test", "items": []},
            "persona": {"role": "Test", "responsibilities": [], "expertise": []},
            "workflow": {"name": "Test", "steps": [], "decision_points": []},
        }

        for extraction_type, content in type_content_map.items():
            extraction = Extraction(
                id=valid_object_id,
                source_id=valid_object_id_2,
                chunk_id=valid_object_id_3,
                type=extraction_type,
                content=content,
                extracted_at=sample_datetime,
            )
            assert extraction.type == extraction_type

    def test_extraction_invalid_type(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test that invalid extraction type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Extraction(
                id=valid_object_id,
                source_id=valid_object_id_2,
                chunk_id=valid_object_id_3,
                type="invalid_type",
                content={},
                extracted_at=sample_datetime,
            )

        errors = exc_info.value.errors()
        assert any("type" in str(e["loc"]) for e in errors)

    def test_extraction_invalid_ids(
        self, valid_object_id: str, valid_object_id_2: str, sample_datetime: datetime
    ) -> None:
        """Test that invalid ObjectIds are rejected."""
        # Invalid id
        with pytest.raises(ValidationError):
            Extraction(
                id="invalid",
                source_id=valid_object_id,
                chunk_id=valid_object_id_2,
                type="decision",
                content={},
                extracted_at=sample_datetime,
            )

        # Invalid source_id
        with pytest.raises(ValidationError):
            Extraction(
                id=valid_object_id,
                source_id="invalid",
                chunk_id=valid_object_id_2,
                type="decision",
                content={},
                extracted_at=sample_datetime,
            )

        # Invalid chunk_id
        with pytest.raises(ValidationError):
            Extraction(
                id=valid_object_id,
                source_id=valid_object_id_2,
                chunk_id="invalid",
                type="decision",
                content={},
                extracted_at=sample_datetime,
            )

    def test_extraction_json_serialization(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test JSON serialization produces snake_case output."""
        extraction = Extraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            type="pattern",
            content={"name": "Test", "problem": "Test", "solution": "Test"},
            topics=["test"],
            extracted_at=sample_datetime,
        )

        # Test model_dump()
        data = extraction.model_dump()
        assert "schema_version" in data
        assert "source_id" in data
        assert "chunk_id" in data
        assert "extracted_at" in data
        assert data["schema_version"] == CURRENT_SCHEMA_VERSION

        # Test model_dump_json()
        json_str = extraction.model_dump_json()
        assert "schema_version" in json_str
        assert "source_id" in json_str
        assert "chunk_id" in json_str
        assert "extracted_at" in json_str
        # Ensure snake_case (not camelCase)
        assert "schemaVersion" not in json_str
        assert "sourceId" not in json_str
        assert "chunkId" not in json_str
        assert "extractedAt" not in json_str

    def test_extraction_schema_version_default(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test that schema_version is present with default value."""
        extraction = Extraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            type="decision",
            content={"question": "Test?"},  # Valid decision content
            extracted_at=sample_datetime,
        )

        assert extraction.schema_version == CURRENT_SCHEMA_VERSION
        assert extraction.schema_version == "1.0"

    def test_extraction_content_type_mismatch_rejected(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test that mismatched content type is rejected."""
        # Try to create a decision extraction with warning-like content
        with pytest.raises(ValidationError) as exc_info:
            Extraction(
                id=valid_object_id,
                source_id=valid_object_id_2,
                chunk_id=valid_object_id_3,
                type="decision",
                content={"title": "Warning", "description": "This is a warning"},  # Warning schema
                extracted_at=sample_datetime,
            )

        errors = exc_info.value.errors()
        assert any("mismatch" in str(e["msg"]).lower() for e in errors)


class TestTypedExtractionModels:
    """Tests for type-specific extraction models."""

    def test_decision_extraction(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test DecisionExtraction with typed content."""
        extraction = DecisionExtraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            content=DecisionContent(
                question="Which framework?",
                options=["FastAPI", "Flask"],
                considerations=["Performance", "Ease of use"],
                recommended_approach="FastAPI for async support",
            ),
            topics=["framework"],
            extracted_at=sample_datetime,
        )

        assert extraction.type == "decision"
        assert extraction.content.question == "Which framework?"
        assert len(extraction.content.options) == 2

    def test_pattern_extraction(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test PatternExtraction with typed content."""
        extraction = PatternExtraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            content=PatternContent(
                name="Factory Pattern",
                problem="Creating objects without specifying class",
                solution="Use factory method",
            ),
            topics=["design-patterns"],
            extracted_at=sample_datetime,
        )

        assert extraction.type == "pattern"
        assert extraction.content.name == "Factory Pattern"

    def test_warning_extraction(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test WarningExtraction with typed content."""
        extraction = WarningExtraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            content=WarningContent(
                title="Memory Leak",
                description="Improper resource cleanup",
            ),
            topics=["performance"],
            extracted_at=sample_datetime,
        )

        assert extraction.type == "warning"
        assert extraction.content.title == "Memory Leak"

    def test_methodology_extraction(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test MethodologyExtraction with typed content."""
        extraction = MethodologyExtraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            content=MethodologyContent(
                name="Agile Sprint",
                steps=["Planning", "Development", "Review", "Retrospective"],
            ),
            topics=["agile"],
            extracted_at=sample_datetime,
        )

        assert extraction.type == "methodology"
        assert extraction.content.name == "Agile Sprint"
        assert len(extraction.content.steps) == 4

    def test_checklist_extraction(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test ChecklistExtraction with typed content."""
        extraction = ChecklistExtraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            content=ChecklistContent(
                name="Deployment Checklist",
                items=["Run tests", "Update docs", "Tag release"],
            ),
            topics=["deployment"],
            extracted_at=sample_datetime,
        )

        assert extraction.type == "checklist"
        assert extraction.content.name == "Deployment Checklist"
        assert len(extraction.content.items) == 3

    def test_persona_extraction(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test PersonaExtraction with typed content."""
        extraction = PersonaExtraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            content=PersonaContent(
                role="Product Manager",
                responsibilities=["Roadmap", "Prioritization"],
            ),
            topics=["roles"],
            extracted_at=sample_datetime,
        )

        assert extraction.type == "persona"
        assert extraction.content.role == "Product Manager"

    def test_workflow_extraction(
        self,
        valid_object_id: str,
        valid_object_id_2: str,
        valid_object_id_3: str,
        sample_datetime: datetime,
    ) -> None:
        """Test WorkflowExtraction with typed content."""
        extraction = WorkflowExtraction(
            id=valid_object_id,
            source_id=valid_object_id_2,
            chunk_id=valid_object_id_3,
            content=WorkflowContent(
                name="CI/CD Pipeline",
                trigger="Push to main",
                steps=["Build", "Test", "Deploy"],
            ),
            topics=["devops"],
            extracted_at=sample_datetime,
        )

        assert extraction.type == "workflow"
        assert extraction.content.name == "CI/CD Pipeline"
        assert extraction.content.trigger == "Push to main"
        assert len(extraction.content.steps) == 3
