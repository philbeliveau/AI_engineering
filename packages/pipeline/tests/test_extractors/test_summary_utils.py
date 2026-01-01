"""Tests for extraction summary generator utilities.

Tests cover summary generation for all extraction types:
- Decision: question + recommended_approach
- Pattern: name + problem + solution[:200]
- Warning: title + description[:200]
- Methodology: name + steps[:3]
- Checklist: name + items[:3]
- Persona: role + responsibilities[:3]
- Workflow: name + trigger + steps[:3]
"""

import pytest

from src.extractors import (
    Checklist,
    ChecklistItem,
    Decision,
    Methodology,
    MethodologyStep,
    Pattern,
    Persona,
    Warning,
    Workflow,
    WorkflowStep,
)
from src.extractors.utils import generate_extraction_summary


class TestDecisionSummary:
    """Test summary generation for Decision extractions."""

    def test_decision_with_recommendation(self):
        """Summary includes question and recommended approach."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Should I use RAG or fine-tuning?",
            recommended_approach="RAG for most use cases",
        )
        summary = generate_extraction_summary(decision)

        assert "Should I use RAG or fine-tuning?" in summary
        assert "RAG for most use cases" in summary

    def test_decision_without_recommendation(self):
        """Summary works when no recommendation is provided."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Which database to use?",
            options=["PostgreSQL", "MongoDB"],
        )
        summary = generate_extraction_summary(decision)

        assert "Which database to use?" in summary

    def test_decision_summary_length(self):
        """Summary is limited to ~500 characters."""
        long_question = "Q" * 300
        long_recommendation = "R" * 300
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question=long_question,
            recommended_approach=long_recommendation,
        )
        summary = generate_extraction_summary(decision)

        assert len(summary) <= 550  # Allow slight overflow for natural truncation


class TestPatternSummary:
    """Test summary generation for Pattern extractions."""

    def test_pattern_summary_fields(self):
        """Summary includes name, problem, and solution."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Semantic Caching",
            problem="High API costs from repeated similar queries",
            solution="Cache responses using embedding similarity",
        )
        summary = generate_extraction_summary(pattern)

        assert "Semantic Caching" in summary
        assert "High API costs" in summary
        assert "embedding similarity" in summary

    def test_pattern_truncates_long_solution(self):
        """Long solutions are truncated at word boundary."""
        long_solution = "This is a very long solution. " * 50  # ~1700 chars
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Pattern",
            problem="Test problem",
            solution=long_solution,
        )
        summary = generate_extraction_summary(pattern)

        assert len(summary) <= 550


class TestWarningSummary:
    """Test summary generation for Warning extractions."""

    def test_warning_summary_fields(self):
        """Summary includes title and description."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Context Window Overflow",
            description="Exceeding token limits causes silent truncation",
        )
        summary = generate_extraction_summary(warning)

        assert "Context Window Overflow" in summary
        assert "token limits" in summary

    def test_warning_truncates_long_description(self):
        """Long descriptions are truncated."""
        long_description = "Warning details go here. " * 50
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test Warning",
            description=long_description,
        )
        summary = generate_extraction_summary(warning)

        assert len(summary) <= 550


class TestMethodologySummary:
    """Test summary generation for Methodology extractions."""

    def test_methodology_summary_fields(self):
        """Summary includes name and first few steps."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="RAG Implementation Methodology",
            steps=[
                MethodologyStep(order=1, title="Define requirements", description="..."),
                MethodologyStep(order=2, title="Choose embedding model", description="..."),
                MethodologyStep(order=3, title="Set up vector store", description="..."),
                MethodologyStep(order=4, title="Implement retrieval", description="..."),
            ],
        )
        summary = generate_extraction_summary(methodology)

        assert "RAG Implementation Methodology" in summary
        assert "Define requirements" in summary
        assert "Choose embedding model" in summary
        assert "Set up vector store" in summary
        # Fourth step should not be included
        assert "Implement retrieval" not in summary

    def test_methodology_empty_steps(self):
        """Summary works with no steps."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Empty Methodology",
            steps=[],
        )
        summary = generate_extraction_summary(methodology)

        assert "Empty Methodology" in summary


class TestChecklistSummary:
    """Test summary generation for Checklist extractions."""

    def test_checklist_summary_fields(self):
        """Summary includes name and first few items."""
        checklist = Checklist(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Pre-deployment Checklist",
            items=[
                ChecklistItem(item="Verify API rate limits"),
                ChecklistItem(item="Test with production data"),
                ChecklistItem(item="Set up monitoring"),
                ChecklistItem(item="Configure alerts"),
            ],
        )
        summary = generate_extraction_summary(checklist)

        assert "Pre-deployment Checklist" in summary
        assert "Verify API rate limits" in summary
        assert "Test with production data" in summary
        assert "Set up monitoring" in summary

    def test_checklist_with_context(self):
        """Summary may include context if provided."""
        checklist = Checklist(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Testing Checklist",
            items=[ChecklistItem(item="Test item 1")],
            context="Before releasing to production",
        )
        summary = generate_extraction_summary(checklist)

        assert "Testing Checklist" in summary


class TestPersonaSummary:
    """Test summary generation for Persona extractions."""

    def test_persona_summary_fields(self):
        """Summary includes role and responsibilities."""
        persona = Persona(
            source_id="src-123",
            chunk_id="chunk-456",
            role="ML Engineer",
            responsibilities=[
                "Design and implement ML pipelines",
                "Optimize model performance",
                "Deploy models to production",
                "Monitor model drift",
            ],
        )
        summary = generate_extraction_summary(persona)

        assert "ML Engineer" in summary
        assert "Design and implement ML pipelines" in summary
        assert "Optimize model performance" in summary
        assert "Deploy models to production" in summary

    def test_persona_with_expertise(self):
        """Summary may include expertise areas."""
        persona = Persona(
            source_id="src-123",
            chunk_id="chunk-456",
            role="Data Scientist",
            responsibilities=["Analyze data"],
            expertise=["Python", "Statistics", "Machine Learning"],
        )
        summary = generate_extraction_summary(persona)

        assert "Data Scientist" in summary


class TestWorkflowSummary:
    """Test summary generation for Workflow extractions."""

    def test_workflow_summary_fields(self):
        """Summary includes name, trigger, and steps."""
        workflow = Workflow(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Model Deployment Workflow",
            trigger="New model version ready",
            steps=[
                WorkflowStep(order=1, action="Validate model metrics"),
                WorkflowStep(order=2, action="Run integration tests"),
                WorkflowStep(order=3, action="Deploy to staging"),
                WorkflowStep(order=4, action="Deploy to production"),
            ],
        )
        summary = generate_extraction_summary(workflow)

        assert "Model Deployment Workflow" in summary
        assert "New model version ready" in summary
        assert "Validate model metrics" in summary
        assert "Run integration tests" in summary
        assert "Deploy to staging" in summary

    def test_workflow_without_trigger(self):
        """Summary works without trigger."""
        workflow = Workflow(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Simple Workflow",
            steps=[WorkflowStep(order=1, action="Do something")],
        )
        summary = generate_extraction_summary(workflow)

        assert "Simple Workflow" in summary


class TestSummaryEdgeCases:
    """Test edge cases in summary generation."""

    def test_summary_max_length_enforced(self):
        """Summary never exceeds 500 chars (with margin for word boundaries)."""
        # Create extraction with maximum content
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Q" * 600,
            recommended_approach="R" * 600,
        )
        summary = generate_extraction_summary(decision)

        assert len(summary) <= 550  # Allow for word boundary adjustment

    def test_summary_preserves_word_boundaries(self):
        """Summary truncation doesn't cut words in half."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Should I use the artificial intelligence system?",
            recommended_approach="Yes you should because " + "word " * 100,
        )
        summary = generate_extraction_summary(decision)

        # Should not end with a partial word
        assert not summary.endswith("wor")

    def test_summary_handles_empty_optional_fields(self):
        """Summary works when optional fields are empty."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Test question",
            options=[],
            considerations=[],
            recommended_approach=None,
        )
        summary = generate_extraction_summary(decision)

        assert "Test question" in summary
        assert len(summary) > 0
