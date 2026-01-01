"""Extraction pipeline module.

Provides the ExtractionPipeline class for running knowledge extraction
on ingested documents.

Example:
    from src.extraction import ExtractionPipeline, ExtractionPipelineResult

    pipeline = ExtractionPipeline()
    result = pipeline.extract("src-abc123")
    print(f"Extracted {result.total_extractions} items")
"""

from src.extraction.pipeline import (
    ExtractionPipeline,
    ExtractionPipelineResult,
    ExtractionPipelineError,
)

__all__ = [
    "ExtractionPipeline",
    "ExtractionPipelineResult",
    "ExtractionPipelineError",
]
