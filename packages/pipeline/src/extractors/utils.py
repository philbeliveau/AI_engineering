"""Utility functions for knowledge extraction.

This module provides helper functions for extraction operations,
including summary generation for embedding optimization.
"""

import structlog

from src.extractors.base import (
    Checklist,
    Decision,
    ExtractionBase,
    ExtractionType,
    Methodology,
    Pattern,
    Persona,
    Warning,
    Workflow,
)

logger = structlog.get_logger()

# Maximum summary length for embedding efficiency
MAX_SUMMARY_LENGTH = 500


def _truncate_at_word_boundary(text: str, max_length: int) -> str:
    """Truncate text at word boundary to avoid cutting words.

    Args:
        text: Text to truncate.
        max_length: Maximum length for truncated text.

    Returns:
        Truncated text ending at word boundary.
    """
    if len(text) <= max_length:
        return text

    # Find the last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")

    if last_space > 0:
        return truncated[:last_space].rstrip()

    # No space found, just truncate
    return truncated.rstrip()


def _generate_decision_summary(extraction: Decision) -> str:
    """Generate summary for Decision extraction.

    Combines question and recommended approach for embedding.

    Args:
        extraction: Decision extraction to summarize.

    Returns:
        Summary string for embedding.
    """
    parts = [extraction.question]

    if extraction.recommended_approach:
        parts.append(extraction.recommended_approach)

    return " ".join(parts)


def _generate_pattern_summary(extraction: Pattern) -> str:
    """Generate summary for Pattern extraction.

    Combines name, problem, and truncated solution.

    Args:
        extraction: Pattern extraction to summarize.

    Returns:
        Summary string for embedding.
    """
    # Truncate solution to 200 chars for balance
    solution_truncated = _truncate_at_word_boundary(extraction.solution, 200)

    return f"{extraction.name}: {extraction.problem}. {solution_truncated}"


def _generate_warning_summary(extraction: Warning) -> str:
    """Generate summary for Warning extraction.

    Combines title and truncated description.

    Args:
        extraction: Warning extraction to summarize.

    Returns:
        Summary string for embedding.
    """
    # Truncate description to 200 chars for balance
    description_truncated = _truncate_at_word_boundary(extraction.description, 200)

    return f"{extraction.title}: {description_truncated}"


def _generate_methodology_summary(extraction: Methodology) -> str:
    """Generate summary for Methodology extraction.

    Combines name and first 3 step titles.

    Args:
        extraction: Methodology extraction to summarize.

    Returns:
        Summary string for embedding.
    """
    step_titles = [step.title for step in extraction.steps[:3]]
    steps_str = " → ".join(step_titles) if step_titles else ""

    if steps_str:
        return f"{extraction.name}: {steps_str}"
    return extraction.name


def _generate_checklist_summary(extraction: Checklist) -> str:
    """Generate summary for Checklist extraction.

    Combines name and first 3 checklist items.

    Args:
        extraction: Checklist extraction to summarize.

    Returns:
        Summary string for embedding.
    """
    item_texts = [item.item for item in extraction.items[:3]]
    items_str = "; ".join(item_texts) if item_texts else ""

    if items_str:
        return f"{extraction.name}: {items_str}"
    return extraction.name


def _generate_persona_summary(extraction: Persona) -> str:
    """Generate summary for Persona extraction.

    Combines role and first 3 responsibilities.

    Args:
        extraction: Persona extraction to summarize.

    Returns:
        Summary string for embedding.
    """
    responsibilities = extraction.responsibilities[:3]
    resp_str = "; ".join(responsibilities) if responsibilities else ""

    if resp_str:
        return f"{extraction.role}: {resp_str}"
    return extraction.role


def _generate_workflow_summary(extraction: Workflow) -> str:
    """Generate summary for Workflow extraction.

    Combines name, trigger, and first 3 step actions.

    Args:
        extraction: Workflow extraction to summarize.

    Returns:
        Summary string for embedding.
    """
    parts = [extraction.name]

    if extraction.trigger:
        parts.append(f"(triggered by: {extraction.trigger})")

    step_actions = [step.action for step in extraction.steps[:3]]
    if step_actions:
        parts.append("; ".join(step_actions))

    return " ".join(parts)


def generate_extraction_summary(extraction: ExtractionBase) -> str:
    """Generate embedding-optimized summary from extraction.

    Creates a concise text representation of an extraction suitable for
    embedding. The summary is limited to ~500 characters for efficiency.

    Args:
        extraction: Any extraction type inheriting from ExtractionBase.

    Returns:
        Summary string limited to ~500 characters.

    Raises:
        ValueError: If extraction type is not supported.
    """
    summary_generators = {
        ExtractionType.DECISION: _generate_decision_summary,
        ExtractionType.PATTERN: _generate_pattern_summary,
        ExtractionType.WARNING: _generate_warning_summary,
        ExtractionType.METHODOLOGY: _generate_methodology_summary,
        ExtractionType.CHECKLIST: _generate_checklist_summary,
        ExtractionType.PERSONA: _generate_persona_summary,
        ExtractionType.WORKFLOW: _generate_workflow_summary,
    }

    generator = summary_generators.get(extraction.type)

    if generator is None:
        logger.error(
            "unsupported_extraction_type_for_summary",
            type=extraction.type,
        )
        raise ValueError(f"Unsupported extraction type: {extraction.type}")

    # Generate raw summary
    raw_summary = generator(extraction)

    # Truncate to max length at word boundary
    summary = _truncate_at_word_boundary(raw_summary, MAX_SUMMARY_LENGTH)

    logger.debug(
        "extraction_summary_generated",
        type=extraction.type.value,
        summary_length=len(summary),
    )

    return summary
