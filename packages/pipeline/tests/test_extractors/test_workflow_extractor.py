"""Tests for WorkflowExtractor class."""

from unittest.mock import AsyncMock, patch

import pytest

from src.extractors import (
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
    Workflow,
    WorkflowStep,
)
from src.extractors.workflow_extractor import WorkflowExtractor


class TestWorkflowExtractorProperties:
    """Test WorkflowExtractor properties and configuration."""

    def test_instantiation(self):
        """WorkflowExtractor can be instantiated."""
        extractor = WorkflowExtractor()
        assert extractor is not None

    def test_extraction_type_is_workflow(self):
        """WorkflowExtractor has WORKFLOW extraction type."""
        extractor = WorkflowExtractor()
        assert extractor.extraction_type == ExtractionType.WORKFLOW

    def test_model_class_is_workflow(self):
        """WorkflowExtractor uses Workflow model class."""
        extractor = WorkflowExtractor()
        assert extractor.model_class == Workflow

    def test_uses_default_config(self):
        """WorkflowExtractor uses default config when none provided."""
        extractor = WorkflowExtractor()
        assert extractor.config.max_extractions_per_chunk == 5
        assert extractor.config.min_confidence == 0.5
        assert extractor.config.auto_tag_topics is True

    def test_accepts_custom_config(self):
        """WorkflowExtractor accepts custom configuration."""
        config = ExtractorConfig(
            max_extractions_per_chunk=10,
            min_confidence=0.8,
            auto_tag_topics=False,
        )
        extractor = WorkflowExtractor(config=config)
        assert extractor.config.max_extractions_per_chunk == 10
        assert extractor.config.min_confidence == 0.8


class TestWorkflowExtractorGetPrompt:
    """Test WorkflowExtractor.get_prompt method."""

    def test_get_prompt_returns_string(self):
        """get_prompt returns prompt string."""
        extractor = WorkflowExtractor()
        prompt = extractor.get_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_get_prompt_contains_workflow_instructions(self):
        """get_prompt contains workflow-specific instructions."""
        extractor = WorkflowExtractor()
        prompt = extractor.get_prompt()
        # Should contain base instructions
        assert "knowledge extraction assistant" in prompt.lower()
        # Should contain workflow-specific content
        assert "workflow" in prompt.lower()
        assert "trigger" in prompt.lower()


class TestWorkflowExtractorAutoTagTopics:
    """Test WorkflowExtractor topic auto-tagging."""

    def test_auto_tag_topics_from_name(self):
        """auto_tag_topics extracts topics from workflow name."""
        extractor = WorkflowExtractor()
        workflow = Workflow(
            source_id="src-1",
            chunk_id="chunk-1",
            name="RAG Query Processing Workflow",
            trigger="User query received",
            steps=[WorkflowStep(order=1, action="Process query")],
        )
        topics = extractor.auto_tag_topics(workflow)
        assert "rag" in topics

    def test_auto_tag_topics_from_steps(self):
        """auto_tag_topics extracts topics from steps."""
        extractor = WorkflowExtractor()
        workflow = Workflow(
            source_id="src-1",
            chunk_id="chunk-1",
            name="Model Training Workflow",
            trigger="New data available",
            steps=[
                WorkflowStep(order=1, action="Generate embeddings"),
                WorkflowStep(order=2, action="Fine-tune LLM model"),
            ],
        )
        topics = extractor.auto_tag_topics(workflow)
        assert "embeddings" in topics or "fine-tuning" in topics or "llm" in topics

    def test_auto_tag_topics_from_decision_points(self):
        """auto_tag_topics extracts topics from decision points."""
        extractor = WorkflowExtractor()
        workflow = Workflow(
            source_id="src-1",
            chunk_id="chunk-1",
            name="Processing Workflow",
            trigger="Start",
            steps=[WorkflowStep(order=1, action="Process")],
            decision_points=["Check RAG accuracy", "Evaluate embedding quality"],
        )
        topics = extractor.auto_tag_topics(workflow)
        assert "rag" in topics or "embeddings" in topics or "evaluation" in topics

    def test_auto_tag_topics_limits_to_five(self):
        """auto_tag_topics returns at most 5 topics."""
        extractor = WorkflowExtractor()
        workflow = Workflow(
            source_id="src-1",
            chunk_id="chunk-1",
            name="Complete LLM RAG Pipeline",
            trigger="On deployment",
            steps=[
                WorkflowStep(order=1, action="Generate embeddings"),
                WorkflowStep(order=2, action="Fine-tune model"),
                WorkflowStep(order=3, action="Optimize prompts"),
            ],
            decision_points=["Evaluate inference", "Check training metrics"],
        )
        topics = extractor.auto_tag_topics(workflow)
        assert len(topics) <= 5


class TestWorkflowExtractorExtract:
    """Test WorkflowExtractor.extract method."""

    @pytest.fixture
    def sample_chunk_content(self) -> str:
        """Sample chunk containing a workflow."""
        return """
        When model performance drops below threshold, trigger the
        retraining workflow. First, collect recent production data.
        Then, validate data quality - if quality is poor, escalate
        to data team. Next, fine-tune the model on new data. Run
        evaluation suite. If metrics improve, deploy to staging.
        Finally, run A/B test before production rollout.
        """

    @pytest.fixture
    def mock_llm_response(self) -> str:
        """Mock LLM response with valid workflow JSON."""
        return """
        [
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
                        "action": "Run A/B test before production",
                        "outputs": ["A/B test results"]
                    }
                ],
                "decision_points": [
                    "Data quality check - escalate if poor",
                    "Metrics improvement check before staging"
                ],
                "confidence": 0.95
            }
        ]
        """

    @pytest.mark.asyncio
    async def test_extract_with_valid_chunk(self, sample_chunk_content, mock_llm_response):
        """extract returns ExtractionResult list for valid chunk."""
        extractor = WorkflowExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                chunk_content=sample_chunk_content,
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert isinstance(results, list)
            assert len(results) > 0
            assert all(isinstance(r, ExtractionResult) for r in results)

    @pytest.mark.asyncio
    async def test_extract_preserves_source_attribution(
        self, sample_chunk_content, mock_llm_response
    ):
        """extract preserves source_id and chunk_id."""
        extractor = WorkflowExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                chunk_content=sample_chunk_content,
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert results[0].success is True
            workflow = results[0].extraction
            assert workflow.source_id == "source-456"
            assert workflow.chunk_id == "chunk-123"

    @pytest.mark.asyncio
    async def test_extract_returns_empty_list_for_no_workflows(self):
        """extract returns empty list when no workflows found."""
        extractor = WorkflowExtractor()
        no_workflow_response = "[]"

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = no_workflow_response

            results = await extractor.extract(
                chunk_content="The sky is blue.",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert results == []

    @pytest.mark.asyncio
    async def test_extract_handles_parse_error(self):
        """extract returns error result for unparseable response."""
        extractor = WorkflowExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = "This is not valid JSON"

            results = await extractor.extract(
                chunk_content="Some content",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert len(results) == 1
            assert results[0].success is False
            assert "parse" in results[0].error.lower()


class TestWorkflowModel:
    """Test Workflow Pydantic model."""

    def test_workflow_required_fields(self):
        """Workflow requires source_id, chunk_id, name."""
        workflow = Workflow(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Workflow",
        )
        assert workflow.source_id == "src-123"
        assert workflow.chunk_id == "chunk-456"
        assert workflow.type == ExtractionType.WORKFLOW
        assert workflow.schema_version == "1.0.0"

    def test_workflow_with_steps(self):
        """Workflow can contain steps."""
        workflow = Workflow(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Workflow",
            trigger="User action",
            steps=[
                WorkflowStep(order=1, action="Step 1", outputs=["Output 1"]),
                WorkflowStep(order=2, action="Step 2", outputs=["Output 2"]),
            ],
            decision_points=["Decision 1"],
        )
        assert workflow.trigger == "User action"
        assert len(workflow.steps) == 2
        assert workflow.steps[0].order == 1
        assert len(workflow.decision_points) == 1

    def test_workflow_step_with_outputs(self):
        """WorkflowStep can include outputs."""
        step = WorkflowStep(
            order=1,
            action="Process data",
            outputs=["Processed data", "Quality report"],
        )
        assert len(step.outputs) == 2

    def test_workflow_has_source_attribution(self):
        """Workflow includes source attribution fields."""
        workflow = Workflow(source_id="src-123", chunk_id="chunk-456", name="Test")
        assert hasattr(workflow, "source_id")
        assert hasattr(workflow, "chunk_id")
        assert hasattr(workflow, "topics")
        assert hasattr(workflow, "schema_version")


class TestWorkflowExtractorRegistration:
    """Test WorkflowExtractor registration with ExtractorRegistry."""

    def test_extractor_can_be_registered(self):
        """WorkflowExtractor can be registered with registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.WORKFLOW, WorkflowExtractor)

        assert registry.is_supported(ExtractionType.WORKFLOW)

    def test_extractor_retrieved_from_registry(self):
        """WorkflowExtractor can be retrieved from registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.WORKFLOW, WorkflowExtractor)

        extractor = registry.get_extractor(ExtractionType.WORKFLOW)
        assert isinstance(extractor, WorkflowExtractor)

    def test_global_registry_contains_workflow(self):
        """Global extractor_registry contains WorkflowExtractor."""
        from src.extractors import extractor_registry

        assert extractor_registry.is_supported(ExtractionType.WORKFLOW)
        extractor = extractor_registry.get_extractor(ExtractionType.WORKFLOW)
        assert isinstance(extractor, WorkflowExtractor)
