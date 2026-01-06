---
project_name: "{{PROJECT_NAME}}"
architecture: "{{ARCHITECTURE}}"
created: "{{DATE}}"
optimized_for_llm: true
rule_count: "{{RULE_COUNT}}"
---

# Project Context for AI Agents

_Critical rules and patterns for implementing code in this project. Focus on unobvious details that agents might miss._

---

## Project Overview

- **Project:** {{PROJECT_NAME}}
- **Architecture:** {{ARCHITECTURE}} (RAG-only | Fine-tuning | Hybrid)
- **Generated:** {{DATE}}
- **Use Case:** {{USE_CASE}}

---

## Architecture Summary

### FTI Pipeline Pattern

```
{{FTI_DIAGRAM}}
```

**Active Pipelines:**
- Feature Pipeline: {{FEATURE_PIPELINE_STATUS}}
- Training Pipeline: {{TRAINING_PIPELINE_STATUS}}
- Inference Pipeline: {{INFERENCE_PIPELINE_STATUS}}

### Key Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
{{DESIGN_DECISIONS}}

### Integration Points

| Component | Interface | Protocol |
|-----------|-----------|----------|
{{INTEGRATION_POINTS}}

---

## Technology Stack

### Runtime & Package Management

{{RUNTIME_STACK}}

### Package Management

- **Package manager:** {{PACKAGE_MANAGER}}
- **Install dependencies:** `{{INSTALL_COMMAND}}`
- **Run commands:** `{{RUN_COMMAND}}`
- **Add dependency:** `{{ADD_DEPENDENCY_COMMAND}}`
- **Add dev dependency:** `{{ADD_DEV_DEPENDENCY_COMMAND}}`
- NEVER use raw `python` or `pip` commands directly

### API Framework

{{API_FRAMEWORK}}

### Data Storage

{{DATA_STORAGE}}

### ML/AI Components

{{ML_COMPONENTS}}

### Development Tools

{{DEV_TOOLS}}

---

## Coding Standards

### Naming Conventions

- **Files/modules:** `snake_case.py` (e.g., `pdf_adapter.py`)
- **Classes:** `PascalCase` (e.g., `PdfAdapter`, `SearchResult`)
- **Functions/variables:** `snake_case` (e.g., `extract_decisions`, `source_id`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CHUNK_SIZE`)
- **Pydantic models:** `PascalCase` class, `snake_case` fields

### Mandatory Patterns

- Type hints required for all function signatures
- Docstrings for all public functions (Google style)
- Async patterns for all I/O operations
- Tests required for business logic (pytest)

### Style

{{CODE_STYLE}}

### API Response Format (MANDATORY)

All API endpoints MUST return wrapped responses:

```json
{
  "status": "success",
  "data": {
    "results": [],
    "metadata": {
      "query": "original query",
      "result_count": 0,
      "sources_cited": []
    }
  },
  "message": null
}
```

### Error Response Format (MANDATORY)

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Human readable message",
  "details": {}
}
```

**Standard Error Codes:**
- `VALIDATION_ERROR` - Invalid input data
- `NOT_FOUND` - Resource not found
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Unexpected server error
- `UNAUTHORIZED` - Missing or invalid credentials

### Error Handling

- Custom exceptions inherit from base project exception
- Always include: `code`, `message`, `details` dict
- Structured logging with context (no `print()`)
- Graceful degradation where possible
- Never catch bare `Exception` without re-raising

### Testing Requirements

- **Unit tests:** Mock external dependencies for fast CI runs
- **Integration tests:** Test actual API calls against real services
- **Test file naming:** `test_{module}.py`
- **Integration test naming:** `test_{module}_integration.py`
- **Async tests:** Use `@pytest.mark.asyncio` decorator
- **Async fixtures:** Use `@pytest_asyncio.fixture`
- **Coverage target:** {{COVERAGE_TARGET}}%
- **Each test function:** Tests ONE behavior only

**Test Commands:**
```bash
# Run all tests
{{TEST_RUN_COMMAND}}

# Run with coverage
{{TEST_COVERAGE_COMMAND}}

# Run integration tests only
{{TEST_INTEGRATION_COMMAND}}
```

---

## Code Pattern Examples

### CORRECT Pattern

```python
{{CORRECT_PATTERN_EXAMPLE}}
```

### WRONG Pattern (avoid)

```python
{{WRONG_PATTERN_EXAMPLE}}
```

### Async Pattern (CORRECT)

```python
# CORRECT: Async endpoint with proper error handling
@app.get("/items/{item_id}")
async def get_item(item_id: str) -> ItemResponse:
    """Retrieve item by ID."""
    try:
        result = await item_service.get(item_id)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return ItemResponse(status="success", data=result)
    except ValidationError as e:
        logger.error("validation_failed", item_id=item_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```

### Async Pattern (WRONG)

```python
# WRONG: Blocking sync call in async endpoint
@app.get("/items/{item_id}")
async def get_item(item_id: str):
    result = item_service.get_sync(item_id)  # NEVER DO THIS - blocks event loop
    print(f"Got item: {item_id}")  # NEVER USE print()
    return result  # NEVER return unwrapped response
```

---

## Architecture Patterns

### RAG Patterns (if applicable)

{{RAG_PATTERNS}}

### Embedding Patterns

{{EMBEDDING_PATTERNS}}

### Evaluation Patterns

{{EVALUATION_PATTERNS}}

### Caching Patterns

{{CACHING_PATTERNS}}

---

## File Organization

```
{{PROJECT_NAME}}/
{{FILE_STRUCTURE}}
```

### Module Boundaries

{{MODULE_BOUNDARIES}}

---

## Critical Constraints

### Performance Requirements

| Metric | Target | Source |
|--------|--------|--------|
{{PERFORMANCE_CONSTRAINTS}}

### Security Requirements

{{SECURITY_REQUIREMENTS}}

### Compliance Requirements

{{COMPLIANCE_REQUIREMENTS}}

### Resource Constraints

| Resource | Limit | Notes |
|----------|-------|-------|
{{RESOURCE_CONSTRAINTS}}

---

## Anti-Patterns to Avoid

**From Knowledge MCP warnings and project experience:**

{{ANTI_PATTERNS}}

---

## Critical Don't-Miss Rules

### NEVER DO

{{NEVER_DO_RULES}}

**Universal NEVER Rules:**
- NEVER use `print()` - always use structured logging
- NEVER hardcode connection strings - use Settings/env vars
- NEVER return bare results - always wrap in response format
- NEVER catch bare `Exception` - use specific types
- NEVER commit `.env` files or secrets
- NEVER block async endpoints with sync I/O

### ALWAYS DO

{{ALWAYS_DO_RULES}}

**Universal ALWAYS Rules:**
- ALWAYS use type hints for function signatures
- ALWAYS wrap API responses in standard format
- ALWAYS log with context (structured logging)
- ALWAYS validate input at API boundary
- ALWAYS include `source_id` for traceability

### Edge Cases to Handle

{{EDGE_CASES}}

---

## Key References

| Document | Purpose | Location |
|----------|---------|----------|
| Architecture Decision | Core architecture choice | `phase-0-scoping/architecture-decision.md` |
| Project Spec | Full system specification | `project-spec.md` |
| Decision Log | All decisions with rationale | `decision-log.md` |
| Phase 1 Spec | Feature pipeline details | `phase-1-feature/spec.md` |
| Phase 2 Spec | Training pipeline details | `phase-2-training/spec.md` |
| Phase 3 Spec | Inference pipeline details | `phase-3-inference/spec.md` |
| Phase 4 Report | Evaluation results | `phase-4-evaluation/report.md` |
| Phase 5 Runbook | Operations guide | `phase-5-operations/runbook.md` |

---

## Knowledge Base References

Key insights from Knowledge MCP that informed this project:

| Query | Key Insight | Applied In |
|-------|-------------|------------|
{{KNOWLEDGE_REFERENCES}}

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Reference phase specs for detailed requirements

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Remove rules that become obvious over time

---

_Generated by AI Engineering Workflow v1.0_
