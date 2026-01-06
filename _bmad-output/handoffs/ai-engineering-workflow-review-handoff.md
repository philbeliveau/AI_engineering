# Handoff: AI Engineering Workflow Review

**Created:** 2026-01-06
**Purpose:** Review and validate the AI Engineering Workflow for completeness, consistency, and best practices alignment
**Priority:** High

---

## Context

The AI Engineering Workflow has been authored as a BMAD-compliant workflow to guide AI/LLM engineering projects from business analysis through operations. The workflow uses the Feature-Training-Inference (FTI) pipeline pattern with 11 specialized agents.

**Recent Changes:**
1. Created 10 agent files in `agents/` folder (extracted from embedded personas)
2. Updated all 11 step files to reference agents instead of embedding personas
3. Created `config.yaml` to centralize all path and configuration settings
4. Simplified step file frontmatter to reference config instead of duplicating paths
5. Updated `workflow.md` to document configuration architecture

---

## Workflow Location

```
_bmad-output/bmb-creations/workflows/ai-engineering-workflow/
├── config.yaml              # Central configuration (NEW)
├── workflow.md              # Main workflow definition
├── agents/                  # Agent personas (10 files)
│   ├── business-analyst.md
│   ├── fti-architect.md
│   ├── data-engineer.md
│   ├── embeddings-engineer.md
│   ├── fine-tuning-specialist.md
│   ├── rag-specialist.md
│   ├── prompt-engineer.md
│   ├── llm-evaluator.md
│   ├── mlops-engineer.md
│   └── tech-lead.md
├── steps/                   # Step workflow files (11 files)
│   ├── step-01-business-analyst.md
│   ├── step-02-fti-architect.md
│   ├── step-03-data-engineer.md
│   ├── step-04-embeddings-engineer.md
│   ├── step-05-fine-tuning-specialist.md
│   ├── step-06-rag-specialist.md
│   ├── step-07-prompt-engineer.md
│   ├── step-08-llm-evaluator.md
│   ├── step-09-mlops-engineer.md
│   ├── step-10-tech-lead.md
│   └── step-11-story-elaborator.md
├── templates/               # Config templates (to be created)
└── checklists/              # Quality checklists (to be created)
```

---

## Review Task

Perform a comprehensive review of the AI Engineering Workflow to validate:

1. **Structural Integrity** - All files exist, cross-references work, no broken links
2. **BMAD Compliance** - Follows BMAD workflow and agent conventions
3. **Knowledge-Grounding** - Agents properly query Knowledge MCP at decision points
4. **Consistency** - Terminology, formatting, and patterns are consistent across files
5. **Completeness** - All necessary components are present, no gaps
6. **Best Practices** - Aligns with AI/ML engineering best practices from literature

---

## CRITICAL: Use Knowledge MCP Extensively

**This review MUST be grounded in the Knowledge MCP.** Query extensively to validate that the workflow follows established best practices.

### Knowledge MCP Endpoint
```
https://knowledge-mcp-production.up.railway.app
```

### Mandatory Queries During Review

**1. Validate FTI Architecture Pattern**
```
Endpoint: search_knowledge
Query: "FTI feature training inference pipeline architecture"
```
- Does the workflow correctly implement the FTI pattern?
- Are the phase boundaries appropriate?

**2. Validate RAG vs Fine-tuning Decision Framework**
```
Endpoint: get_decisions
Topic: "RAG vs fine-tuning"
```
- Does Step 2 (FTI Architect) capture all decision criteria?
- Are trade-offs properly presented?

**3. Validate Data Pipeline Patterns**
```
Endpoint: get_patterns
Topic: "data pipeline"
```
- Does Step 3 (Data Engineer) follow recommended patterns?
- Are quality gates appropriately designed?

**4. Validate Chunking and Embedding Guidance**
```
Endpoint: get_patterns
Topic: "chunking"

Endpoint: get_warnings
Topic: "embeddings"
```
- Does Step 4 cover all chunking strategies from literature?
- Are embedding model migration warnings included?

**5. Validate Fine-tuning Methodology**
```
Endpoint: get_methodologies
Topic: "fine-tuning"

Endpoint: get_warnings
Topic: "fine-tuning"
```
- Does Step 5 follow SFT/DPO best practices?
- Are dataset quality warnings prominent?

**6. Validate RAG Pipeline Patterns**
```
Endpoint: get_patterns
Topic: "rag"

Endpoint: get_warnings
Topic: "rag"
```
- Does Step 6 cover retrieval, reranking, context assembly?
- Are common RAG failure modes addressed?

**7. Validate Prompting Best Practices**
```
Endpoint: get_patterns
Topic: "prompting"

Endpoint: get_warnings
Topic: "prompting"
```
- Does Step 7 follow structured prompt design?
- Are guardrails and safety patterns included?

**8. Validate Evaluation Framework**
```
Endpoint: get_methodologies
Topic: "evaluation"

Endpoint: get_warnings
Topic: "evaluation"
```
- Does Step 8 cover appropriate metrics?
- Are LLM-as-judge biases addressed?

**9. Validate MLOps Patterns**
```
Endpoint: get_methodologies
Topic: "mlops"

Endpoint: get_patterns
Topic: "drift"
```
- Does Step 9 follow production monitoring best practices?
- Is drift detection properly covered?

**10. Cross-Cutting Concerns**
```
Endpoint: search_knowledge
Query: "LLM production system architecture best practices"
```
- Does the overall workflow cover all essential areas?
- Are there gaps the literature suggests we should address?

---

## Review Checklist

### A. Structural Review

- [ ] All 10 agent files exist in `agents/`
- [ ] All 11 step files exist in `steps/`
- [ ] `config.yaml` is complete and valid YAML
- [ ] `workflow.md` references config correctly
- [ ] Step files reference their agent files correctly
- [ ] Step navigation (nextStep) forms complete chain
- [ ] Conditional step (step-05) handled correctly for RAG-only path

### B. Agent Review (For Each Agent)

- [ ] Has proper XML structure with `<agent>`, `<persona>`, `<expertise>`, `<activation>`, `<outputs>`, `<handoff>`
- [ ] Persona is distinct and appropriate for the domain
- [ ] Principles align with domain best practices
- [ ] Outputs match what step file expects
- [ ] Handoff context bridges to next agent

### C. Step Review (For Each Step)

- [ ] Frontmatter references config correctly
- [ ] Agent Activation section present
- [ ] MANDATORY EXECUTION RULES section present
- [ ] Knowledge MCP queries specified at decision points
- [ ] Story generation section present
- [ ] Menu options and handling logic present
- [ ] SUCCESS/FAILURE metrics defined

### D. Config Review

- [ ] All paths resolve correctly
- [ ] Knowledge MCP endpoint correct
- [ ] Phase structure matches workflow diagram
- [ ] Agent roster complete
- [ ] Step sequence accurate
- [ ] Sidecar template complete
- [ ] Story prefixes defined for all steps

### E. Knowledge-Grounding Review

- [ ] Each step specifies MANDATORY queries
- [ ] Queries use appropriate endpoints (get_decisions, get_patterns, get_warnings, get_methodologies, search_knowledge)
- [ ] Synthesis approach documented for each query set
- [ ] Key patterns/warnings to surface are specified
- [ ] Queries cover the domain appropriately

### F. Consistency Review

- [ ] Terminology consistent across files (e.g., "sidecar" vs "sidecar.yaml")
- [ ] Step numbering consistent
- [ ] Menu option format consistent
- [ ] Decision ID format consistent (ARCH-001, DATA-001, etc.)
- [ ] Story ID format consistent (ARCH-S01, DATA-S01, etc.)

---

## Expected Outputs

After review, produce:

1. **Review Report** (`ai-engineering-workflow-review.md`)
   - Summary of findings
   - Issues found (critical, major, minor)
   - Knowledge gaps identified
   - Recommendations

2. **Issue List** (if issues found)
   - Location (file, line)
   - Issue description
   - Suggested fix
   - Priority

3. **Enhancement Suggestions**
   - Based on Knowledge MCP queries
   - New patterns or warnings to incorporate
   - Gaps to address in future iterations

---

## Review Approach

1. **Start with Knowledge MCP** - Query each topic area first to understand what best practices exist

2. **Then Review Files** - Compare workflow content against knowledge base findings

3. **Document Gaps** - Note where workflow could be enhanced with knowledge base insights

4. **Check Cross-References** - Verify all file references resolve correctly

5. **Validate Flow** - Trace through the workflow as a user would experience it

6. **Compile Report** - Summarize findings with actionable recommendations

---

## Notes

- The Knowledge MCP contains extractions from AI engineering literature including "LLM Engineer's Handbook" and other sources
- Query results should guide whether the workflow captures best practices or has gaps
- This is a knowledge-grounded review - opinions should be backed by Knowledge MCP findings
- The workflow is designed to be used with Claude Code - consider the user experience

---

*Created by AI Engineering Workflow authoring session*
