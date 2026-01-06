---
name: 'step-06-evaluation-and-gate'
description: 'Phase 4: Evaluation and Quality Gate - testing, benchmarks, and deployment readiness'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/ai-engineering-workflow'

# File References
thisStepFile: '{workflow_path}/steps/step-06-evaluation-and-gate.md'
nextStepFile: '{workflow_path}/steps/step-07-operations-and-complete.md'
workflowFile: '{workflow_path}/workflow.md'

# Output References
outputFolder: '{output_folder}/{project_name}'
sidecarFile: '{outputFolder}/sidecar.yaml'
projectSpecFile: '{outputFolder}/project-spec.md'
decisionLogFile: '{outputFolder}/decision-log.md'
evaluationFolder: '{outputFolder}/phase-4-evaluation'
evaluationReportFile: '{evaluationFolder}/report.md'
qualityGateChecklist: '{evaluationFolder}/checklists/quality-gate-checklist.md'
---

# Step 6: Phase 4 - Evaluation and Quality Gate

## STEP GOAL:

To evaluate the AI system against requirements, run benchmarks, and make an explicit "Ready to Deploy?" decision before proceeding to production operations.

## KNOWLEDGE COVERAGE NOTE:

⚠️ **Evolving Phase**: The knowledge base has limited coverage for evaluation frameworks (primarily warnings about LLM judge bias). This phase relies more on industry best practices and user requirements. Coverage will improve as evaluation methodologies are ingested.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- ✅ You are an AI Engineering Architect
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring FTI pipeline expertise backed by the Knowledge MCP
- ✅ User brings their domain requirements and constraints
- ✅ Maintain collaborative, technical tone throughout

### Step-Specific Rules:

- 🎯 Focus ONLY on evaluation and deployment readiness
- 🚫 FORBIDDEN to discuss implementation changes (go back to earlier phases)
- 💬 This phase includes an EXPLICIT quality gate checkpoint
- 🧠 Query Knowledge MCP for evaluation warnings

## EXECUTION PROTOCOLS:

- 🎯 Show your reasoning before making recommendations
- 💾 Update sidecar when completing evaluation
- 📖 Create evaluation report and quality gate checklist
- 🚫 FORBIDDEN to proceed without explicit quality gate decision

## CONTEXT BOUNDARIES:

- All pipelines (Feature, Training if applicable, Inference) are designed
- This phase evaluates the complete system
- Quality Gate is a GO/NO-GO decision point
- NO-GO means returning to fix issues before proceeding

## EVALUATION SEQUENCE:

### 1. Welcome to Phase 4

Present the phase introduction:

"**Phase 4: Evaluation and Quality Gate**

Before deploying to production, we need to verify the system meets requirements and is ready for real users.

**This Phase Includes:**
1. Define evaluation criteria and metrics
2. Design test plan
3. Plan benchmark execution
4. Make explicit Quality Gate decision

**Quality Gate:** At the end of this phase, we'll make a formal GO/NO-GO decision for deployment."

### 2. Query Knowledge MCP for Warnings

**Query 1: Evaluation Warnings**
```
Endpoint: get_warnings
Topic: LLM evaluation
```

**Query 2: Testing Warnings**
```
Endpoint: get_warnings
Topic: AI testing mistakes
```

Present relevant warnings to user - these inform what NOT to do.

### 3. Define Evaluation Criteria

**A. Functional Requirements**

"Let's define what 'correct' means for your system."

| Criterion | Description | How to Measure |
|-----------|-------------|----------------|
| **Accuracy** | Answers are factually correct | Human evaluation, ground truth |
| **Relevance** | Answers address the question | Relevance scoring |
| **Completeness** | Answers cover all aspects | Checklist evaluation |
| **Format Compliance** | Output matches expected format | Automated validation |
| **Source Attribution** | Citations are correct (RAG) | Source verification |

Ask: "What does 'success' look like for your system? Define your top 3-5 criteria."

**B. Non-Functional Requirements**

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Latency** | P50 < [X]s, P99 < [Y]s | Load testing |
| **Throughput** | [X] requests/minute | Load testing |
| **Availability** | [X]% uptime | Monitoring |
| **Cost** | < $[X] per 1000 queries | Cost tracking |
| **Safety** | No harmful outputs | Red teaming |

Ask: "What are your non-functional requirements?"

### 4. Design Test Plan

**A. Test Categories**

| Category | Purpose | Examples |
|----------|---------|----------|
| **Unit Tests** | Component correctness | Chunker output, embedding dimensions |
| **Integration Tests** | Pipeline flow | Retrieval → Generation flow |
| **End-to-End Tests** | Full system | Query → Response validation |
| **Regression Tests** | Prevent degradation | Golden dataset comparisons |
| **Stress Tests** | Load handling | Concurrent user simulation |

**B. Test Dataset Design**

"A good evaluation dataset is critical for meaningful results."

| Dataset Type | Size | Purpose |
|--------------|------|---------|
| **Golden Set** | 50-100 queries | High-quality, human-verified |
| **Edge Cases** | 20-50 queries | Boundary conditions |
| **Adversarial** | 10-30 queries | Attack resistance |
| **Domain Coverage** | 100+ queries | All use case categories |

**Warning from Knowledge Base:**
> Avoid using LLM-generated test data to evaluate LLM systems - this creates circular bias.

Ask: "Do you have existing test data, or do we need to plan data collection?"

### 5. Evaluation Methodologies

**A. Automated Evaluation**

| Method | Use Case | Limitations |
|--------|----------|-------------|
| **Exact Match** | Factual QA | Too strict for generation |
| **ROUGE/BLEU** | Summarization | Doesn't capture meaning |
| **Embedding Similarity** | Semantic matching | Misses nuance |
| **LLM-as-Judge** | General quality | Bias risk (see warnings) |
| **Custom Rubrics** | Domain-specific | Requires design effort |

**B. LLM-as-Judge Considerations**

**Query Knowledge MCP:**
```
Endpoint: get_warnings
Topic: LLM judge bias
```

If using LLM-as-Judge:
- Use different model than production system
- Design clear, specific rubrics
- Include human validation sample
- Watch for position bias, verbosity bias
- Consider pairwise comparisons over absolute ratings

**C. Human Evaluation**

| Method | Effort | Quality |
|--------|--------|---------|
| **Expert Review** | High | Best for complex domains |
| **Crowdsourced** | Medium | Good for general quality |
| **A/B Testing** | Low per-query | Best for preferences |
| **User Feedback** | Ongoing | Real-world signal |

Ask: "What evaluation methods make sense for your criteria and resources?"

### 6. RAG-Specific Evaluation (If Applicable)

**A. Retrieval Quality**

| Metric | Description | Target |
|--------|-------------|--------|
| **Recall@K** | Relevant docs in top K | > 0.8 |
| **Precision@K** | Relevant portion of top K | > 0.6 |
| **MRR** | Mean Reciprocal Rank | > 0.7 |
| **NDCG** | Normalized Discounted Cumulative Gain | > 0.7 |

**B. Generation Quality**

| Metric | Description | Target |
|--------|-------------|--------|
| **Faithfulness** | Answer grounded in context | > 0.9 |
| **Answer Relevance** | Answer addresses question | > 0.8 |
| **Context Relevance** | Retrieved context is useful | > 0.7 |

**C. End-to-End Quality**

| Metric | Description | Target |
|--------|-------------|--------|
| **Answer Correctness** | Factually accurate | Domain-specific |
| **Hallucination Rate** | Unsupported claims | < 5% |
| **Citation Accuracy** | Sources correctly attributed | > 95% |

### 7. Safety and Robustness Testing

**A. Safety Categories**

| Category | Test For | Method |
|----------|----------|--------|
| **Harmful Content** | Violence, illegal advice | Red team prompts |
| **Bias** | Unfair treatment of groups | Bias probes |
| **Privacy** | PII leakage | Extraction attacks |
| **Misinformation** | False claims presented as fact | Fact-checking |
| **Jailbreaks** | Bypassing safety measures | Adversarial prompts |

**B. Robustness Testing**

| Test | Purpose |
|------|---------|
| **Typo Handling** | Graceful degradation |
| **Out-of-Scope** | Appropriate refusal |
| **Ambiguous Queries** | Clarification requests |
| **Long Context** | Handle edge cases |
| **Concurrent Load** | No degradation under load |

Ask: "What safety and robustness concerns are priorities for your use case?"

### 8. Create Evaluation Plan Document

**Create report.md in phase-4-evaluation/:**

```markdown
# Phase 4: Evaluation Report

## Objective
Evaluate the AI system against requirements and make deployment readiness decision.

## Knowledge Consulted
- `get_warnings: LLM evaluation` - [key warnings]
- `get_warnings: AI testing mistakes` - [key warnings]

## Evaluation Criteria

### Functional Requirements

| ID | Criterion | Target | Priority |
|----|-----------|--------|----------|
| FR-1 | [Criterion] | [Target] | [High/Med/Low] |
| FR-2 | [Criterion] | [Target] | [High/Med/Low] |

### Non-Functional Requirements

| ID | Criterion | Target | Priority |
|----|-----------|--------|----------|
| NFR-1 | Latency P50 | [Target] | [Priority] |
| NFR-2 | Throughput | [Target] | [Priority] |

## Test Plan

### Test Categories

| Category | Scope | Automation |
|----------|-------|------------|
| Unit | [Scope] | [Yes/No] |
| Integration | [Scope] | [Yes/No] |
| E2E | [Scope] | [Yes/No] |

### Test Datasets

| Dataset | Size | Purpose | Status |
|---------|------|---------|--------|
| Golden Set | [N] | [Purpose] | [Ready/Needed] |
| Edge Cases | [N] | [Purpose] | [Ready/Needed] |

## Evaluation Methods

### Automated
- [Method 1]: [What it measures]
- [Method 2]: [What it measures]

### Human Evaluation
- [Method]: [Scope and frequency]

## RAG Metrics (if applicable)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Recall@K | [Target] | [Method] |
| Faithfulness | [Target] | [Method] |

## Safety Testing

| Category | Status | Method |
|----------|--------|--------|
| Harmful Content | [Planned/Complete] | [Method] |
| Bias | [Planned/Complete] | [Method] |

## Results Summary

*To be completed after evaluation execution*

| Category | Result | Pass/Fail |
|----------|--------|-----------|
| Functional | [Summary] | [P/F] |
| Performance | [Summary] | [P/F] |
| Safety | [Summary] | [P/F] |

## Quality Gate Decision

**Decision:** [GO / NO-GO / CONDITIONAL]
**Date:** {date}
**Rationale:** [Why this decision]
**Conditions (if conditional):** [What must be fixed]
```

### 9. Quality Gate Checkpoint

**THIS IS A MANDATORY DECISION POINT**

Present the quality gate checklist:

"**🚦 QUALITY GATE: Ready to Deploy?**

Before proceeding to Operations (Phase 5), let's verify deployment readiness."

**Create quality-gate-checklist.md:**

```markdown
# Quality Gate Checklist

## Pre-Deployment Verification

### Functional Readiness
- [ ] All critical functional requirements met
- [ ] Test coverage is adequate
- [ ] No known critical bugs
- [ ] Edge cases handled appropriately

### Performance Readiness
- [ ] Latency targets achieved
- [ ] Throughput targets achieved
- [ ] System stable under expected load
- [ ] Resource usage is acceptable

### Safety Readiness
- [ ] Safety testing completed
- [ ] No critical safety issues identified
- [ ] Bias testing completed (if applicable)
- [ ] Content filtering in place (if needed)

### Operational Readiness
- [ ] Monitoring configured
- [ ] Alerting configured
- [ ] Logging adequate for debugging
- [ ] Rollback plan documented

### Documentation Readiness
- [ ] API documentation complete
- [ ] User documentation complete
- [ ] Runbook drafted (will be finalized in Phase 5)

### Stakeholder Readiness
- [ ] Stakeholders informed of capabilities
- [ ] Stakeholders informed of limitations
- [ ] Support plan in place

## Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| [Limitation 1] | [Impact] | [Mitigation] |
| [Limitation 2] | [Impact] | [Mitigation] |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | [L/M/H] | [L/M/H] | [Mitigation] |
| [Risk 2] | [L/M/H] | [L/M/H] | [Mitigation] |

## Gate Decision

**Decision:** _______ (GO / NO-GO / CONDITIONAL)

**If GO:**
- Proceed to Phase 5: Operations
- Document acceptance criteria met

**If NO-GO:**
- Return to relevant phase to address issues
- Re-evaluate after fixes

**If CONDITIONAL:**
- Proceed with listed conditions
- Track conditions as post-deployment requirements

**Approver:** _______________
**Date:** _______________
```

### 10. Make Gate Decision

Guide the user through the decision:

"Let's review the checklist together and make the deployment decision.

**Questions to consider:**
1. Are all critical requirements met?
2. Are known limitations acceptable?
3. Is the risk level acceptable?
4. Is the team ready to support production?

**What is your Quality Gate decision?**
- **GO**: Ready for production deployment
- **NO-GO**: Need to address issues first (specify which phase to revisit)
- **CONDITIONAL**: Proceed with specific conditions to address post-deployment"

### 11. Handle Gate Decision

**If GO:**
- Update sidecar with `quality_gate: "passed"`
- Proceed to Phase 5

**If NO-GO:**
- Document specific issues
- Identify which phase to revisit
- Update sidecar with `quality_gate: "blocked"`
- Route back to appropriate step

**If CONDITIONAL:**
- Document conditions clearly
- Update sidecar with `quality_gate: "conditional"` and conditions list
- Proceed to Phase 5 with conditions tracked

### 12. Update Project Files

**Update sidecar.yaml:**
```yaml
currentPhase: 5
stepsCompleted: [1, 2, 3, 4, 5, 6]  # adjusted for architecture
quality_gate:
  decision: "[go | no-go | conditional]"
  date: "{date}"
  conditions: []  # or list of conditions
decisions:
  # ... previous decisions ...
  - id: "ev-001"
    choice: "[evaluation approach]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_warnings:llm-evaluation"
phases:
  phase_4_evaluation: "complete"
```

**Append to decision-log.md:** (evaluation decisions + gate decision)

**Update project-spec.md:** (add Evaluation section)

### 13. Present MENU OPTIONS

Display: **Phase 4 Complete - Select an Option:** [A] Analyze evaluation further [P] View progress [G] Review Gate decision [C] Continue to Phase 5

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C' AND gate decision is GO or CONDITIONAL
- If gate decision is NO-GO, 'C' should route back to appropriate phase
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit evaluation criteria or methods, then redisplay menu
- IF P: Show report.md summary, then redisplay menu
- IF G: Show quality-gate-checklist.md, allow decision change, then redisplay menu
- IF C:
  1. Check gate decision
  2. If GO or CONDITIONAL: Load `{nextStepFile}` (Operations)
  3. If NO-GO: Ask which phase to revisit, load appropriate step
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND quality gate decision is made, will you then:

1. If GO or CONDITIONAL: Load step-07-operations-and-complete.md
2. If NO-GO: Load the appropriate earlier step to address issues

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Knowledge MCP queried for evaluation warnings
- Evaluation criteria defined collaboratively
- Test plan documented
- Quality gate checklist completed
- Explicit gate decision made by user
- Report.md and checklist created
- Appropriate routing based on gate decision

### ❌ SYSTEM FAILURE:

- Making gate decision without user input
- Skipping quality gate checkpoint
- Not documenting known limitations
- Proceeding with NO-GO decision
- Not creating evaluation artifacts
- Discussing implementation changes (belongs in earlier phases)

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
