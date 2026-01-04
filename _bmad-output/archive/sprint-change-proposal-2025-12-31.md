# Sprint Change Proposal: Automated LLM Extraction

**Date:** 2025-12-31
**Author:** Philippebeliveau
**Status:** APPROVED
**Change Scope:** Minor

---

## Section 1: Issue Summary

**Problem Statement:** The Knowledge Pipeline needs to process ~1,600 pages of PDF content (~2,400 chunks). The original "Claude-as-Extractor" pattern assumed manual interaction via Claude Code during ingestion. At scale (16,800+ extraction calls), this is impractical.

**Solution:** Automate extraction using Claude Haiku API calls in batch processing.

**Discovery Context:** Identified during Epic 3 planning when calculating extraction operation volume.

**Evidence:**
- 1,600 pages ÷ ~700 tokens/chunk = ~2,400 chunks
- 2,400 chunks × 7 extraction types = 16,800 extraction calls
- Manual extraction not feasible at this scale

---

## Section 2: Impact Analysis

### Constraint Clarification

The "zero LLM API cost" constraint applies to **query time only** (community users searching via MCP). Ingestion-time LLM costs were always expected with the Claude-as-Extractor pattern.

| Phase | Cost Model | Status |
|-------|-----------|--------|
| Ingestion/Extraction | LLM API costs (~$10/book) | Expected |
| Query Time | Zero LLM costs | Preserved |

### Epic Impact

| Epic | Impact |
|------|--------|
| Epic 1-2 | None (complete) |
| Epic 3 | Stories 3.2-3.5 use LLMClient |
| Epic 4-5 | None |

### Artifact Changes Required

| Artifact | Change Type | Description |
|----------|-------------|-------------|
| `architecture.md` | Clarification | Add "at query time" to NFR-3 |
| `project-context.md` | Addition | Add ANTHROPIC_API_KEY rules |
| `pyproject.toml` | Addition | Add `anthropic` dependency |
| Story 3.1 | Update | Add LLMClient to acceptance criteria |
| Stories 3.2-3.5 | Update | Implementation notes for LLMClient usage |

---

## Section 3: Recommended Approach

**Selected Path:** Direct Adjustment

**Rationale:**
1. Low effort - one utility class + one dependency
2. No breaking changes - additive modification only
3. No constraint violations - query-time zero-cost preserved
4. Enables practical extraction at scale

**Effort:** Low (1-2 hours)
**Risk:** Low
**Timeline Impact:** None (enables implementation)

---

## Section 4: Detailed Change Proposals

### 4.1 Architecture.md - NFR-3 Clarification

**Section:** NFR-3: Cost

**OLD:**
```
| Zero LLM API costs | Claude-as-extractor during ingestion, local embeddings |
```

**NEW:**
```
| Zero LLM API costs at query time | Pre-extracted knowledge served from storage |
| Ingestion costs | ~$10/book via Claude Haiku batch extraction |
| Zero embedding costs | Local all-MiniLM-L6-v2 model |
```

---

### 4.2 Project-Context.md - Add LLM Configuration Rules

**Add to Critical Implementation Rules:**

```markdown
### LLM Client Configuration
- ALWAYS use `pydantic_settings.BaseSettings` for `ANTHROPIC_API_KEY`
- Default model: `claude-3-haiku-20240307`
- Never hardcode API keys or model IDs
- Use structured logging for all API calls
- Implement retry logic with exponential backoff
```

---

### 4.3 Dependencies - pyproject.toml

**Add to dependencies:**
```toml
anthropic = ">=0.40.0"
tenacity = ">=8.0.0"  # For retry logic
```

---

### 4.4 New Component - LLMClient

**File:** `packages/pipeline/src/extractors/llm_client.py`

```python
"""LLM client for automated knowledge extraction."""

import anthropic
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings

logger = structlog.get_logger()


class LLMClient:
    """Client for LLM-based knowledge extraction.

    Uses Claude Haiku for cost-effective batch extraction.
    """

    def __init__(
        self,
        model: str | None = None,
        max_tokens: int = 1024,
    ):
        self.client = anthropic.Anthropic()
        self.model = model or settings.llm_model
        self.max_tokens = max_tokens

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    async def extract(self, prompt: str, content: str) -> str:
        """Extract structured knowledge using LLM.

        Args:
            prompt: Extraction prompt with instructions
            content: Chunk content to extract from

        Returns:
            Raw LLM response (JSON string)
        """
        logger.debug(
            "llm_extraction_start",
            model=self.model,
            content_length=len(content)
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\n---\n\nCONTENT TO EXTRACT FROM:\n{content}"
                }
            ]
        )

        result = response.content[0].text
        logger.info(
            "llm_extraction_complete",
            model=self.model,
            response_length=len(result)
        )
        return result
```

---

### 4.5 Configuration Updates

**Add to `packages/pipeline/src/config.py`:**
```python
# LLM Configuration
anthropic_api_key: str = ""
llm_model: str = "claude-3-haiku-20240307"
llm_max_tokens: int = 1024
```

**Add to `.env.example`:**
```bash
# LLM Extraction
ANTHROPIC_API_KEY=your-api-key-here
LLM_MODEL=claude-3-haiku-20240307
```

---

### 4.6 Story Updates

**Story 3.1 - Add acceptance criteria:**
```
**And** LLMClient utility class exists at `src/extractors/llm_client.py`
**And** LLMClient provides async `extract(prompt, content)` method
**And** LLMClient uses `ANTHROPIC_API_KEY` from settings
**And** LLMClient includes retry logic with exponential backoff
```

**Stories 3.2-3.5 - Add implementation note:**
```
**Implementation Note:**
- Use LLMClient from `src/extractors/llm_client.py` for extraction
- Pass prompt from `prompts/{type}.md` to LLMClient
- Parse JSON response using Pydantic model validation
- Log extraction metrics via structlog
```

---

## Section 5: Implementation Handoff

**Change Scope:** Minor - Direct implementation by development team

### Deliverables

| # | Task | Owner |
|---|------|-------|
| 1 | Update `architecture.md` NFR-3 wording | Developer |
| 2 | Add LLM rules to `project-context.md` | Developer |
| 3 | Add `anthropic`, `tenacity` to pyproject.toml | Developer |
| 4 | Create `llm_client.py` with LLMClient class | Developer |
| 5 | Update config.py with LLM settings | Developer |
| 6 | Update .env.example with ANTHROPIC_API_KEY | Developer |
| 7 | Update Story 3.1 acceptance criteria | Developer |
| 8 | Update Stories 3.2-3.5 implementation notes | Developer |

### Success Criteria

- [ ] All document updates complete
- [ ] `anthropic` dependency added and installable
- [ ] LLMClient implemented with retry logic
- [ ] Configuration loads ANTHROPIC_API_KEY from environment
- [ ] Small batch extraction test succeeds

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limits | Retry logic with exponential backoff |
| Cost overrun | Run small batch first, review before full run |
| API key exposure | pydantic-settings, never commit .env |

---

## Approval

**Approved by:** Philippebeliveau
**Date:** 2025-12-31
**Next Action:** Implement changes per handoff task list

---

*Generated by Correct Course Workflow*
