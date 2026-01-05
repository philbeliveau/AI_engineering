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
    ExtractionLevel,
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
from src.extractors.llm_client import LLMClient, LLMClientError
from src.extractors.utils import generate_extraction_summary
from src.extractors.extraction_levels import (
    ExtractionLevelConfig,
    EXTRACTION_LEVEL_CONFIG,
    get_level_for_extraction_type,
    get_extraction_types_for_level,
    get_max_tokens_for_level,
)
from src.extractors.hierarchy import (
    ChapterNode,
    SectionNode,
    DocumentHierarchy,
    CombinedContent,
    build_hierarchy,
    combine_chunks,
)
from src.extractors.hierarchical import (
    HierarchicalExtractor,
    HierarchicalExtractionResult,
    LevelExtractionStats,
)
from src.extractors.decision_extractor import DecisionExtractor
from src.extractors.pattern_extractor import PatternExtractor
from src.extractors.warning_extractor import WarningExtractor
from src.extractors.methodology_extractor import MethodologyExtractor
from src.extractors.checklist_extractor import ChecklistExtractor
from src.extractors.persona_extractor import PersonaExtractor
from src.extractors.workflow_extractor import WorkflowExtractor

__all__ = [
    # Enums
    "ExtractionType",
    "ExtractionLevel",
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
    # LLM Client
    "LLMClient",
    "LLMClientError",
    # Utilities
    "generate_extraction_summary",
    # Extraction Levels
    "ExtractionLevelConfig",
    "EXTRACTION_LEVEL_CONFIG",
    "get_level_for_extraction_type",
    "get_extraction_types_for_level",
    "get_max_tokens_for_level",
    # Document Hierarchy
    "ChapterNode",
    "SectionNode",
    "DocumentHierarchy",
    "CombinedContent",
    "build_hierarchy",
    "combine_chunks",
    # Hierarchical Extractor
    "HierarchicalExtractor",
    "HierarchicalExtractionResult",
    "LevelExtractionStats",
    # Extractors
    "DecisionExtractor",
    "PatternExtractor",
    "WarningExtractor",
    "MethodologyExtractor",
    "ChecklistExtractor",
    "PersonaExtractor",
    "WorkflowExtractor",
]
