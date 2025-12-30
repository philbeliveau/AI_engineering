"""Pydantic models for data validation.

This module exports all core entity models for the knowledge pipeline.
"""

from src.models.chunk import Chunk, ChunkPosition
from src.models.extraction import (
    ChecklistContent,
    ChecklistExtraction,
    ContentType,
    DecisionContent,
    DecisionExtraction,
    Extraction,
    ExtractionType,
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
from src.models.source import Source

# Schema version constant
CURRENT_SCHEMA_VERSION = "1.0"

__all__ = [
    # Core entities
    "Source",
    "Chunk",
    "ChunkPosition",
    "Extraction",
    # Extraction types
    "ExtractionType",
    "ContentType",
    # Content models
    "DecisionContent",
    "PatternContent",
    "WarningContent",
    "MethodologyContent",
    "ChecklistContent",
    "PersonaContent",
    "WorkflowContent",
    # Typed extraction models
    "DecisionExtraction",
    "PatternExtraction",
    "WarningExtraction",
    "MethodologyExtraction",
    "ChecklistExtraction",
    "PersonaExtraction",
    "WorkflowExtraction",
    # Constants
    "CURRENT_SCHEMA_VERSION",
]
