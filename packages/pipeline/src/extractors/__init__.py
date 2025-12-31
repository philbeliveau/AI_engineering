"""Knowledge extractors for the knowledge pipeline.

This module provides the base extractor interface and registry
for extracting structured knowledge from document chunks.

Example:
    from src.extractors import BaseExtractor, Decision, extractor_registry

    class MyExtractor(BaseExtractor):
        @property
        def extraction_type(self):
            return ExtractionType.DECISION

        @property
        def model_class(self):
            return Decision

        def extract(self, chunk_content, chunk_id, source_id):
            # Implementation
            pass

        def get_prompt(self):
            return self._load_prompt("decision")

    extractor_registry.register(ExtractionType.DECISION, MyExtractor)
"""

from src.extractors.base import (
    # Enums
    ExtractionType,
    # Base models
    ExtractionBase,
    ExtractionResult,
    ExtractorConfig,
    # Type-specific models
    Decision,
    Pattern,
    Warning,
    Methodology,
    MethodologyStep,
    Checklist,
    ChecklistItem,
    Persona,
    Workflow,
    WorkflowStep,
    # Base class
    BaseExtractor,
    # Exceptions
    ExtractorError,
    PromptLoadError,
    ExtractionParseError,
    ExtractionValidationError,
    UnsupportedExtractionTypeError,
    # Registry
    ExtractorRegistry,
    extractor_registry,
)

__all__ = [
    # Enums
    "ExtractionType",
    # Base models
    "ExtractionBase",
    "ExtractionResult",
    "ExtractorConfig",
    # Type-specific models
    "Decision",
    "Pattern",
    "Warning",
    "Methodology",
    "MethodologyStep",
    "Checklist",
    "ChecklistItem",
    "Persona",
    "Workflow",
    "WorkflowStep",
    # Base class
    "BaseExtractor",
    # Exceptions
    "ExtractorError",
    "PromptLoadError",
    "ExtractionParseError",
    "ExtractionValidationError",
    "UnsupportedExtractionTypeError",
    # Registry
    "ExtractorRegistry",
    "extractor_registry",
]
