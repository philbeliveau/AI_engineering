<!--
================================================================================
ARCHITECTURE DECISION TEMPLATE - USAGE INSTRUCTIONS
================================================================================

This template documents the RAG vs Fine-tuning vs Hybrid architecture decision.
It is generated during Step 2 (FTI Architect) of the AI Engineering Workflow.

COMPANION DOCUMENTS:
This template works with two other files that must be updated together:

1. decision-log.md - Add a summary entry for this decision:
   ```markdown
   ### ARCH-001: Architecture Selection - [RAG-only | Fine-tuning | Hybrid]

   **Decision:** Selected [architecture] approach for [project]
   **Date:** [date]
   **Phase:** Phase 0 - Scoping

   **Context:** [Brief problem statement]

   **Options Considered:**
   1. RAG-only: Retrieval-augmented generation with base model
   2. Fine-tuning: SFT/DPO on domain data
   3. Hybrid: Fine-tuned model with RAG

   **Choice:** [Selected option]

   **Rationale:** [Why chosen]

   **Knowledge Reference:**
   - Query: `get_decisions: "RAG vs fine-tuning"`
   - Key insights: [Summary]

   **Consequences:**
   - [Key implications]

   **Full Details:** See `phase-0-scoping/architecture-decision.md`
   ```

2. sidecar.yaml - Update the architecture field:
   ```yaml
   architecture: "rag-only"  # or "fine-tuning" or "hybrid"
   ```

USAGE:
1. Replace all {{PLACEHOLDER}} values with actual content
2. Fill in Knowledge MCP query results
3. Complete the decision matrix
4. Generate implementation stories
5. Update companion documents

================================================================================
-->
---
project_name: "{{PROJECT_NAME}}"
decision_id: "ARCH-001"
decision_date: "{{DATE}}"
decision_owner: "{{OWNER}}"
status: "PROPOSED | ACCEPTED | SUPERSEDED"
version: "1.0"
---

# {{PROJECT_NAME}} - Architecture Decision Record

## Decision Summary

| Field | Value |
|-------|-------|
| **Architecture** | RAG-only \| Fine-tuning \| Hybrid |
| **Confidence** | High \| Medium \| Low |
| **Reversibility** | Easy \| Moderate \| Difficult |
| **Decision Date** | {{DATE}} |

---

## 1. Context

### Problem Statement
<!-- What problem are we solving? What is the business or technical need? -->

{{PROBLEM_STATEMENT}}

### Current State
<!-- What exists today? What are the pain points? -->

{{CURRENT_STATE}}

### Goals
<!-- What are we trying to achieve with this system? -->

- [ ] {{GOAL_1}}
- [ ] {{GOAL_2}}
- [ ] {{GOAL_3}}

---

## 2. Decision Drivers

Factors that influenced this decision, ranked by importance:

| Priority | Driver | Weight | Notes |
|----------|--------|--------|-------|
| P0 | {{DRIVER_1}} | Critical | |
| P1 | {{DRIVER_2}} | High | |
| P2 | {{DRIVER_3}} | Medium | |
| P3 | {{DRIVER_4}} | Low | |

### Constraints

| Constraint | Impact |
|------------|--------|
| Budget | {{BUDGET_CONSTRAINT}} |
| Timeline | {{TIMELINE_CONSTRAINT}} |
| Team Expertise | {{TEAM_CONSTRAINT}} |
| Infrastructure | {{INFRA_CONSTRAINT}} |
| Data Availability | {{DATA_CONSTRAINT}} |

---

## 3. Knowledge MCP Queries

### Mandatory Queries Executed

#### Query 1: RAG vs Fine-tuning Decision Criteria
```
Endpoint: get_decisions
Topic: "RAG vs fine-tuning when to use"
```

**Key Findings:**
- {{FINDING_1}}
- {{FINDING_2}}
- {{FINDING_3}}

#### Query 2: Architecture Patterns
```
Endpoint: get_patterns
Topic: "LLM application architecture"
```

**Key Findings:**
- {{PATTERN_1}}
- {{PATTERN_2}}

#### Query 3: Anti-patterns to Avoid
```
Endpoint: get_warnings
Topic: "LLM architecture pitfalls"
```

**Key Warnings:**
- {{WARNING_1}}
- {{WARNING_2}}

### Synthesis Approach

1. **Extracted Criteria:** What decision factors emerged from knowledge queries?
2. **Matched to Context:** How do our constraints map to recommended approaches?
3. **Identified Trade-offs:** What are we optimizing for vs accepting as limitations?

---

## 4. Options Considered

### Option A: RAG-Only Architecture

**Description:**
Retrieval-Augmented Generation using a base foundation model with external knowledge retrieval.

**Pros:**
- [ ] Lower initial investment and faster time-to-value
- [ ] No training data requirements
- [ ] Knowledge can be updated without model changes
- [ ] Easier to audit and explain (source attribution)

**Cons:**
- [ ] Limited by retrieval quality
- [ ] May struggle with complex reasoning over retrieved content
- [ ] Higher inference latency due to retrieval step
- [ ] Base model limitations in domain-specific tasks

**Best Fit When:**
- Knowledge changes frequently
- Budget/timeline constrained
- Need for source attribution
- Domain knowledge is explicit and retrievable

**Knowledge Reference:**
> {{KNOWLEDGE_QUOTE_RAG}}

---

### Option B: Fine-tuning Approach

**Description:**
Supervised fine-tuning (SFT) and/or preference optimization (DPO) on a base model with domain-specific data.

**Pros:**
- [ ] Better internalization of domain knowledge
- [ ] Improved task-specific performance
- [ ] Lower inference latency (no retrieval)
- [ ] Can capture implicit patterns and style

**Cons:**
- [ ] Requires curated training data
- [ ] Higher upfront cost and complexity
- [ ] Knowledge becomes stale without retraining
- [ ] Risk of catastrophic forgetting

**Best Fit When:**
- Stable domain knowledge
- Sufficient training data available
- Need for style/format consistency
- Performance is critical

**Knowledge Reference:**
> {{KNOWLEDGE_QUOTE_FINETUNE}}

---

### Option C: Hybrid Architecture

**Description:**
Fine-tuned model combined with RAG for complementary strengths.

**Pros:**
- [ ] Best of both approaches
- [ ] Fine-tuning for reasoning, RAG for knowledge
- [ ] Can update knowledge without retraining
- [ ] Higher ceiling for performance

**Cons:**
- [ ] Highest complexity
- [ ] Requires both training data AND retrieval infrastructure
- [ ] More difficult to debug and maintain
- [ ] Higher total cost

**Best Fit When:**
- Complex domain requiring both learned patterns and dynamic knowledge
- Sufficient resources for both approaches
- Long-term investment horizon

**Knowledge Reference:**
> {{KNOWLEDGE_QUOTE_HYBRID}}

---

## 5. Decision Outcome

### Chosen Option

**Architecture:** {{CHOSEN_ARCHITECTURE}}

### Rationale

{{RATIONALE_PARAGRAPH}}

### Decision Matrix

| Criterion | Weight | RAG | Fine-tune | Hybrid |
|-----------|--------|-----|-----------|--------|
| Time to MVP | {{WEIGHT_1}} | {{SCORE_RAG_1}} | {{SCORE_FT_1}} | {{SCORE_HYB_1}} |
| Data Requirements | {{WEIGHT_2}} | {{SCORE_RAG_2}} | {{SCORE_FT_2}} | {{SCORE_HYB_2}} |
| Maintenance Complexity | {{WEIGHT_3}} | {{SCORE_RAG_3}} | {{SCORE_FT_3}} | {{SCORE_HYB_3}} |
| Performance Ceiling | {{WEIGHT_4}} | {{SCORE_RAG_4}} | {{SCORE_FT_4}} | {{SCORE_HYB_4}} |
| Cost (Initial) | {{WEIGHT_5}} | {{SCORE_RAG_5}} | {{SCORE_FT_5}} | {{SCORE_HYB_5}} |
| Cost (Ongoing) | {{WEIGHT_6}} | {{SCORE_RAG_6}} | {{SCORE_FT_6}} | {{SCORE_HYB_6}} |
| **Weighted Total** | | **{{TOTAL_RAG}}** | **{{TOTAL_FT}}** | **{{TOTAL_HYB}}** |

---

## 6. Implications

### For Phase 1: Feature Pipeline

| If RAG-Only | If Fine-tuning | If Hybrid |
|-------------|----------------|-----------|
| Focus on chunking strategy | Focus on training data curation | Both chunking AND data curation |
| Vector DB selection critical | Training infrastructure needed | Full stack required |
| Embedding model selection | Format conversion | Combined complexity |

**Implication for this project:**
{{PHASE_1_IMPLICATION}}

### For Phase 2: Training Pipeline

| If RAG-Only | If Fine-tuning | If Hybrid |
|-------------|----------------|-----------|
| **SKIP this phase** | Full SFT/DPO pipeline | Fine-tuning component |
| N/A | PEFT configuration | May use smaller model |

**Implication for this project:**
{{PHASE_2_IMPLICATION}}

### For Phase 3: Inference Pipeline

| If RAG-Only | If Fine-tuning | If Hybrid |
|-------------|----------------|-----------|
| Retrieval + generation | Model serving only | Both components |
| Reranking important | Simpler architecture | Orchestration needed |
| API provider possible | May need self-hosting | Higher complexity |

**Implication for this project:**
{{PHASE_3_IMPLICATION}}

### For Phase 4: Evaluation

| If RAG-Only | If Fine-tuning | If Hybrid |
|-------------|----------------|-----------|
| Retrieval metrics matter | Task metrics focus | Both metric sets |
| Context relevance key | Generation quality | End-to-end testing |

**Implication for this project:**
{{PHASE_4_IMPLICATION}}

---

## 7. Trade-offs Acknowledged

### What We Are Optimizing For

1. {{OPTIMIZE_FOR_1}}
2. {{OPTIMIZE_FOR_2}}
3. {{OPTIMIZE_FOR_3}}

### What We Are Accepting as Limitations

1. {{ACCEPTING_1}}
2. {{ACCEPTING_2}}
3. {{ACCEPTING_3}}

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {{RISK_1}} | High/Med/Low | High/Med/Low | {{MITIGATION_1}} |
| {{RISK_2}} | High/Med/Low | High/Med/Low | {{MITIGATION_2}} |
| {{RISK_3}} | High/Med/Low | High/Med/Low | {{MITIGATION_3}} |

---

## 8. Warnings from Knowledge Base

### Anti-Patterns to Avoid

Based on Knowledge MCP `get_warnings` queries:

#### Warning 1: {{WARNING_TITLE_1}}
> {{WARNING_QUOTE_1}}

**How we will avoid this:**
{{AVOIDANCE_STRATEGY_1}}

#### Warning 2: {{WARNING_TITLE_2}}
> {{WARNING_QUOTE_2}}

**How we will avoid this:**
{{AVOIDANCE_STRATEGY_2}}

#### Warning 3: {{WARNING_TITLE_3}}
> {{WARNING_QUOTE_3}}

**How we will avoid this:**
{{AVOIDANCE_STRATEGY_3}}

### Common Mistakes for {{CHOSEN_ARCHITECTURE}} Architecture

1. {{COMMON_MISTAKE_1}}
2. {{COMMON_MISTAKE_2}}
3. {{COMMON_MISTAKE_3}}

---

## 9. Generated Implementation Stories

Based on the architecture decision, the following implementation stories are generated for the FTI Architect phase.

### For RAG-only Architecture

```yaml
stories:
  step_2_architect:
    - id: "ARCH-S01"
      title: "Set up project repository structure"
      description: "Create standard folder structure for RAG project"
      acceptance_criteria:
        - "Repository initialized with .gitignore"
        - "Folder structure follows FTI pattern"
        - "README with project overview created"

    - id: "ARCH-S02"
      title: "Configure development environment"
      description: "Set up Python environment, dependencies, and tooling"
      acceptance_criteria:
        - "pyproject.toml configured with dependencies"
        - "Pre-commit hooks configured"
        - "Environment variables documented in .env.example"

    - id: "ARCH-S03"
      title: "Document architecture decision"
      description: "Complete architecture decision record with knowledge references"
      acceptance_criteria:
        - "Architecture decision document completed"
        - "Decision logged in decision-log.md"
        - "sidecar.yaml updated with architecture field"
```

### For Fine-tuning or Hybrid Architecture

```yaml
stories:
  step_2_architect:
    - id: "ARCH-S01"
      title: "Set up project repository structure"
      description: "Create standard folder structure for fine-tuning project"
      acceptance_criteria:
        - "Repository initialized"
        - "Folder structure includes training pipeline directories"
        - "Data versioning strategy documented"

    - id: "ARCH-S02"
      title: "Configure development environment"
      description: "Set up Python environment with ML dependencies"
      acceptance_criteria:
        - "PyTorch/transformers dependencies configured"
        - "GPU environment validated"
        - "CUDA/cuDNN versions documented"

    - id: "ARCH-S03"
      title: "Set up experiment tracking"
      description: "Configure W&B or MLflow for training experiments"
      acceptance_criteria:
        - "Tracking tool configured"
        - "Initial experiment logged"
        - "Team access configured"

    - id: "ARCH-S04"
      title: "Document architecture decision"
      description: "Complete architecture decision record with knowledge references"
      acceptance_criteria:
        - "Architecture decision document completed"
        - "Decision logged in decision-log.md"
        - "sidecar.yaml updated with architecture field"
```

### Sidecar Update

After generating stories, update `sidecar.yaml` with:

```yaml
architecture: "{{CHOSEN_ARCHITECTURE_VALUE}}"  # "rag-only" | "fine-tuning" | "hybrid"
stories:
  step_2_architect:
    - id: "ARCH-S01"
      title: "Set up project repository structure"
      status: "pending"
    - id: "ARCH-S02"
      title: "Configure development environment"
      status: "pending"
    # ... additional stories based on architecture
```

---

## 10. Approval and Sign-off

| Role | Name | Decision | Date |
|------|------|----------|------|
| Technical Lead | {{TECH_LEAD}} | Approved/Rejected | |
| Product Owner | {{PRODUCT_OWNER}} | Approved/Rejected | |
| Stakeholder | {{STAKEHOLDER}} | Approved/Rejected | |

### Review Notes

{{REVIEW_NOTES}}

---

## 11. Related Documents

| Document | Location | Relationship |
|----------|----------|--------------|
| Project Spec | `project-spec.md` | Parent document |
| Decision Log | `decision-log.md` | This decision logged as ARCH-001 |
| Phase 1 Spec | `phase-1-feature/spec.md` | Implements implications |
| Phase 2 Spec | `phase-2-training/spec.md` | Implements implications (if applicable) |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{DATE}} | {{OWNER}} | Initial decision record |

---

*Generated by AI Engineering Workflow v1.0*
