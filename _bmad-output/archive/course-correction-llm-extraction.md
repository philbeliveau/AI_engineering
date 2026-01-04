# Course Correction: Automated LLM Extraction

## Change Summary

**From:** Manual "Claude-as-Extractor" pattern (user interactively extracts via Claude Code)
**To:** Automated LLM API extraction (batch processing with Claude Haiku)

## Trigger

User needs to process **1,600 pages of PDF** through the extraction pipeline. Manual extraction would require clicking through thousands of chunks - not practical.

## Decision Made

User selected **Option 2: Add LLM API integration** for automated batch extraction.

**Chosen LLM:** Claude Haiku
- Cost: ~$5-10 for full corpus
- Model ID: `claude-3-haiku-20240307`
- Rationale: Best cost/quality ratio for structured extraction tasks

## Impact Analysis

### Documents to Update

| Document | Change Required |
|----------|-----------------|
| `_bmad-output/architecture.md` | Add LLM integration decision, update NFR-3 |
| `_bmad-output/project-context.md` | Add ANTHROPIC_API_KEY handling rules |
| `packages/pipeline/pyproject.toml` | Add `anthropic` dependency |

### Stories Affected

| Story | Current State | Change Required |
|-------|---------------|-----------------|
| 3.2 Decision Extractor | ready-for-dev | Update to use LLMClient, remove manual pattern references |
| 3.3 Pattern Extractor | ready-for-dev | Same updates |
| 3.4 Warning Extractor | ready-for-dev | Same updates |
| 3.5 Methodology Extractor | ready-for-dev | Same updates |

### New Components to Add

1. **LLMClient utility class** (`packages/pipeline/src/extractors/llm_client.py`)
   - Wrapper for Anthropic API calls
   - Configurable model selection
   - Async support for batch processing
   - Error handling with retries

2. **Environment configuration**
   - `ANTHROPIC_API_KEY` in `.env`
   - Add to `.env.example` template

## Proposed Implementation

```python
# packages/pipeline/src/extractors/llm_client.py

import anthropic
from typing import Optional
import structlog

logger = structlog.get_logger()

class LLMClient:
    """Client for LLM-based knowledge extraction."""

    def __init__(
        self,
        model: str = "claude-3-haiku-20240307",
        max_tokens: int = 1024,
    ):
        self.client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY
        self.model = model
        self.max_tokens = max_tokens

    async def extract(self, prompt: str, content: str) -> str:
        """Extract structured knowledge using LLM.

        Args:
            prompt: Extraction prompt with instructions
            content: Chunk content to extract from

        Returns:
            Raw LLM response (JSON string)
        """
        logger.debug("llm_extraction_start", model=self.model, content_length=len(content))

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "user", "content": f"{prompt}\n\n---\n\nCONTENT TO EXTRACT FROM:\n{content}"}
            ]
        )

        result = response.content[0].text
        logger.info("llm_extraction_complete", model=self.model, response_length=len(result))
        return result
```

## Cost Estimate

| Item | Calculation | Cost |
|------|-------------|------|
| Input tokens | 2,400 chunks × 7 extractors × 800 tokens | 13.4M tokens |
| Output tokens | 16,800 calls × 300 tokens | 5M tokens |
| **Haiku pricing** | $0.25/1M in + $1.25/1M out | **~$10** |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limits | Add retry logic with exponential backoff |
| Cost overrun | Add token counting and budget limits |
| Extraction quality | Run small batch first, review before full run |
| API key exposure | Use pydantic-settings, never commit .env |

## Questions for Architect

1. Should LLMClient be a shared utility or per-extractor?
2. Add model selection to ExtractorConfig or separate LLMConfig?
3. Support multiple providers (OpenAI fallback) or Anthropic-only for now?

## Next Steps

1. Update architecture.md with LLM integration decision
2. Add `anthropic` to pipeline dependencies
3. Create LLMClient utility class
4. Update Story 3.2 dev notes to reference LLMClient
5. Update remaining extractor stories (3.3, 3.4, 3.5)
