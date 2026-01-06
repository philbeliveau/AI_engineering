# Evaluation Placement: Mapping to AI Engineering Workflow

**Purpose:** Show how evaluation findings map to the existing AI Engineering Workflow structure

---

## Workflow Phase Overview

```
Phase 0: SCOPING
├─ Define quality targets
├─ Define success metrics
└─ Set stakeholder expectations

Phase 1: FEATURE PIPELINE
├─ Data collection & processing
├─ Chunking strategy
├─ Integrated Testing: Spot-check data quality
└─ Goal: Prepared data ready for training (if needed)

Phase 2: TRAINING PIPELINE (optional, for fine-tuning)
├─ Fine-tune model
├─ Integrated Testing: Monitor convergence
└─ Goal: Fine-tuned model ready for inference

Phase 3: INFERENCE PIPELINE
├─ Design RAG (retrieval + generation)
├─ Design prompts
├─ Integrated Testing: Quick manual tests
└─ Goal: Inference system ready for evaluation

└──────────────────────────────────────────────────────┐
                                                       ▼
╔═══════════════════════════════════════════════════════╗
║ Phase 4: EVALUATION (Quality Gate)                   ║
║ Duration: 1-2 weeks                                  ║
║ Deliverable: Quality gate decision (GO/NO-GO)        ║
║                                                       ║
║ THIS IS WHERE EVALUATION PLACEMENT MATTERS MOST      ║
╚═══════════════════════════════════════════════════════╝
                                                       │
                            ┌──────────────────────────┘
                            ▼
Phase 5: OPERATIONS (Deployment & Monitoring)
├─ Deploy to production
├─ Set up monitoring
├─ Production Testing: Real-time dashboards
└─ Goal: System in production with feedback loops

Phase 6+: CONTINUOUS IMPROVEMENT
├─ User feedback loops
├─ Metric tracking
├─ Iterative refinement
└─ Goal: Improved system performance
```

---

## Phase 4: Evaluation - The Critical Gate

### Why Phase 4 Placement is Optimal

Phase 4 (Evaluation) is positioned AFTER all pipelines are designed and BEFORE deployment:

**Advantages:**
1. **All components complete** - Evaluating the full system, not partial
2. **No architectural blockers** - Issues are fixable without rework
3. **Explicit decision point** - GO/NO-GO prevents unclear deployments
4. **Baseline for monitoring** - Quality gate targets drive Phase 5 alerting
5. **Stakeholder confidence** - Documented gate provides audit trail

**Disadvantages:** (Mitigated by integrated testing in Phases 1-3)
- Issues discovered late BUT caught before users see them
- Fixes required BUT still avoidable due to gate

### Phase 4 Detailed Structure

From Step 8: LLM Evaluator

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: EVALUATION                                         │
│ Duration: 1-2 weeks                                         │
│                                                             │
│ INPUT: Completed Phase 3 (Inference Pipeline)              │
│        + Quality targets from Phase 0                       │
│        + Decisions from Phases 1-3                          │
│                                                             │
│ OUTPUT: evaluation-spec.md (criteria, tests, methods)       │
│         evaluation-results.md (actual results)              │
│         Quality gate decision (GO/CONDITIONAL/NO-GO)        │
│         Stories for evaluation implementation               │
│                                                             │
│ STEP 8 WORKFLOW:                                            │
│ ├─ Load context (project specs, business requirements)     │
│ ├─ Query Knowledge MCP (mandatory)                          │
│ │  ├─ get_warnings(topic="evaluation")                     │
│ │  ├─ search_knowledge("LLM judge bias mitigation")        │
│ │  ├─ get_methodologies(topic="evaluation")                │
│ │  └─ search_knowledge("evaluation metrics benchmark")     │
│ ├─ Design evaluation framework                              │
│ │  ├─ Define functional criteria                           │
│ │  ├─ Define non-functional criteria                       │
│ │  ├─ Plan test categories & datasets                      │
│ │  └─ Select evaluation methods                            │
│ ├─ Execute evaluation                                       │
│ │  ├─ Run retrieval layer tests (if RAG)                   │
│ │  ├─ Run generation layer tests                           │
│ │  ├─ Run end-to-end tests                                 │
│ │  ├─ Run safety/adversarial tests                         │
│ │  └─ Document all results                                 │
│ ├─ Make quality gate decision                               │
│ │  ├─ Compare metrics vs thresholds                        │
│ │  ├─ Choose: GO / CONDITIONAL / NO-GO                     │
│ │  ├─ Document rationale                                   │
│ │  └─ Update sidecar with decision                         │
│ └─ Generate implementation stories                         │
│    └─ Stories for evaluation system implementation          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Mapping: Phases 1-3 Integrated Evaluation

Each phase includes lightweight, integrated evaluation:

### Phase 1: Feature Pipeline - Integrated Testing

```
Activity: Data processing & chunking
│
├─ Integrated Test: Spot-check
│  ├─ Run 10-20 examples through pipeline
│  ├─ Manually verify output quality
│  ├─ Check for obvious errors
│  └─ Duration: 30 minutes
│
├─ Success Metric: "Data looks good"
├─ Failure Action: Fix pipeline, retry
└─ Documentation: Quick notes in sidecar
```

**Why Integrated?** Guides architecture decisions (chunk size, overlap, etc.)
**Why Lightweight?** Feedback within same day, no formal process needed

### Phase 2: Training Pipeline - Integrated Testing

```
Activity: Fine-tuning (if applicable)
│
├─ Integrated Test: Monitor convergence
│  ├─ Watch training loss curve
│  ├─ Validate on hold-out set
│  ├─ Stop if not converging
│  └─ Duration: Continuous during training
│
├─ Success Metric: Loss decreasing, no divergence
├─ Failure Action: Adjust hyperparameters, retrain
└─ Documentation: Convergence curve in sidecar
```

**Why Integrated?** Immediate feedback on model training quality
**Why Lightweight?** Metrics are basic (loss, not accuracy)

### Phase 3: Inference Pipeline - Integrated Testing

```
Activity: RAG design + prompt engineering
│
├─ Integrated Test: Manual examples
│  ├─ Run 10-20 examples end-to-end
│  ├─ Check retrieval quality (relevant docs?)
│  ├─ Check generation quality (good answer?)
│  ├─ Adjust prompts if needed
│  └─ Duration: 2-4 hours per iteration
│
├─ Success Metric: "Answers look reasonable"
├─ Failure Action: Adjust prompt, retry
└─ Documentation: Best prompt version in sidecar
```

**Why Integrated?** Guides prompt engineering and RAG parameter choices
**Why Lightweight?** Subjective evaluation, small test sets, developer assessment

---

## Evaluation Progression: From Integrated to Gate

```
TIMELINE SHOWING EVALUATION INTENSITY
═════════════════════════════════════════════════════════════

Phase 1-3: Low-Intensity, High-Frequency Testing
│
│  Week 1    Week 2    Week 3    Week 4    Week 5    Week 6
│  ├─ Data  ├─ Data  ├─ Train ├─ Train ├─ RAG  ├─ Prompt
│  │ tests  │ tests  │ tests  │ tests  │ tests │ tests
│  ▼        ▼        ▼        ▼        ▼       ▼
│  ◆        ◆        ◆        ◆        ◆       ◆        (informal)
│  20%      20%      30%      30%      40%     50%      (effort)
│  work week distributed across development phases
│
└──────────────────────────────────────────────────────────────┘

Phase 4: High-Intensity, Focused Evaluation
│
│  Week 7          Week 8
│  ├─ Design       ├─ Execute
│  │ framework     │ evaluation
│  │ (3 days)      │ (3 days)
│  │ ◆◆◆           │ ◆◆◆◆◆
│  │ Query MCP    │ Run all tests
│  │ Define        │ Generate metrics
│  │ criteria      │ Spot check
│  │               │ Human eval
│  │               │
│  │ Make decision │
│  │ (1 day)       │
│  │ ◆             │
│  │ GO/NO-GO      │
│  │ (final)       │
│  └─ 100% effort for 1-2 weeks, then gate
│
└──────────────────────────────────────────────────────────────┘

Phase 5+: Continuous Monitoring (Light Intensity)
│
│  Week 9+
│  ├─ Monitoring
│  │ dashboard
│  │ ◆ (24/7)
│  │ Real-time alerts
│  │ Production signals
│  │
│  └─ 5-10% effort ongoing, always on
```

---

## Quality Gate: The Three Possible Outcomes

### Outcome 1: GO (All Criteria Met)

```
Quality Gate Decision: GO
┌─────────────────────────────────────────┐
│ All functional criteria >= threshold     │
│ All non-functional criteria met          │
│ No critical failures                     │
│ Safety tests passed                      │
│ Documentation complete                   │
└─────────────────────────────────────────┘
              ▼
PROCEED TO PHASE 5
├─ Deploy to production
├─ Set up monitoring dashboards
├─ Configure alerts
└─ Go live within 1 week
```

**Documentation:**
- Update sidecar: `currentStep: 4, stepsCompleted: [0,1,2,3,4]`
- Record decision in decision-log.md: "EVAL-GATE: GO (all criteria met)"
- Generate implementation stories for Phase 5

---

### Outcome 2: CONDITIONAL GO (Minor Issues, Mitigations)

```
Quality Gate Decision: CONDITIONAL GO
┌──────────────────────────────────────────┐
│ Most criteria met                         │
│ Minor issues identified                   │
│ Mitigations documented                    │
│ Risk assessment acceptable                │
└──────────────────────────────────────────┘
              ▼
PROCEED TO PHASE 5 WITH CONDITIONS
├─ Deploy to production (with enhanced monitoring)
├─ List conditions: "Accuracy within 2% of target"
├─ Set deadline: "Improve by Week 4 of Phase 5"
├─ Configure tight alerting for condition items
└─ Auto-rollback if condition worsens
```

**Documentation:**
- Update sidecar: `currentStep: 4, gate_decision: CONDITIONAL`
- Record decision: "EVAL-GATE: CONDITIONAL (3 items to fix post-deployment)"
- List conditions with deadlines
- Set monitoring thresholds tighter than gate targets
- Assign owner for each condition

---

### Outcome 3: NO-GO (Critical Criteria Failed)

```
Quality Gate Decision: NO-GO
┌──────────────────────────────────────────┐
│ Critical criteria failed                  │
│ Showstopper issues identified             │
│ Mitigations not feasible                  │
└──────────────────────────────────────────┘
              ▼
RETURN TO PHASE 3
├─ Identify which component failed
│  ├─ Retrieval metrics low → improve RAG
│  ├─ Generation metrics low → improve prompts/model
│  └─ Both low → fundamental rethink needed
├─ Estimate fix timeline
├─ Implement fixes
└─ Return to Phase 4 for re-evaluation
```

**Documentation:**
- Update sidecar: `currentStep: 3, gate_decision: NO-GO`
- Record blocker in decision-log.md: "EVAL-GATE: NO-GO (safety tests failed)"
- List each blocking issue with diagnosis
- Estimate re-evaluation timeline (typically 1-4 weeks)

---

## Integration Points with Workflow Documents

### Sidecar.yaml Updates

The project sidecar (YAML state file) tracks evaluation progress:

```yaml
currentStep: 4
stepsCompleted: [0, 1, 2, 3, 4]

phases:
  phase_4_evaluation: "designed"  # → "executed" → "gated"

decisions:
  - id: "EVAL-001"
    step: 4
    choice: "Multi-method evaluation: automated + human"
    rationale: "Balanced approach recommended by knowledge base"
  - id: "EVAL-002"
    step: 4
    choice: "Quality gate criteria: Accuracy>=85%, Latency<=500ms"
    rationale: "Thresholds set from business requirements and literature"

gateDecision:
  status: "GO"  # or "CONDITIONAL" or "NO-GO"
  criteria_met: 12
  criteria_failed: 0
  evaluation_date: "2026-01-13"
  approved_by: "stakeholder"
```

### Decision Log Updates

The decision-log.md records evaluation decisions for audit:

```markdown
## EVAL-001: Evaluation Methodology

**Decision:** Multi-method evaluation
- Automated metrics (accuracy, latency)
- LLM-as-judge (with bias mitigations)
- Human spot check (golden set)

**Date:** 2026-01-09
**Step:** 4 - Quality Gate Design
**Rationale:** Knowledge base recommends multiple methods to capture quality

---

## EVAL-002: Quality Gate Criteria

**Decision:** Thresholds set for GO decision
- Accuracy >= 85%
- Latency P99 <= 500ms
- Hallucination rate < 5%

**Date:** 2026-01-10
**Step:** 4 - Quality Gate Execution
**Rationale:** Based on business requirements from Phase 0

---

## EVAL-GATE: Quality Gate Decision

**Decision:** GO - Proceed to Phase 5

**Date:** 2026-01-15
**Evaluation Results:**
- Accuracy: 87% ✅ (target: 85%)
- Latency: 320ms ✅ (target: 500ms)
- Hallucination: 2% ✅ (target: 5%)

**Gate Status:** PASSED
**Next Step:** Phase 5 - Operations & Deployment
```

### Knowledge MCP Queries Documented

Best practice: Record which MCP queries informed decisions:

```markdown
## Knowledge MCP References

### Step 4a: Design Phase
Queried: `get_warnings(topic="evaluation")`
Result: Identified 8 key evaluation pitfalls
Action: Designed mitigations into framework

Queried: `get_methodologies(topic="evaluation")`
Result: Found 5-step evaluation process
Action: Followed step-by-step approach

### Step 4b: Execution Phase
Queried: `search_knowledge("LLM judge evaluation bias mitigation")`
Result: Detailed bias mitigation strategies
Action: Implemented position bias and verbosity bias mitigations

Sources Cited:
- Designing ML Systems (chapters on evaluation)
- Building LLM Applications (RAG evaluation patterns)
- LLM Engineer's Handbook (methodology)
```

---

## Phase Transitions

### Phase 3 → Phase 4 (To Evaluation)

**Trigger:** Phase 3 (Inference Pipeline) complete

**Pre-requisites Check:**
- ✅ All pipelines designed
- ✅ Quality targets defined (from Phase 0)
- ✅ At least 10-20 golden examples available
- ✅ Team understands evaluation scope

**Handoff:**
- Sidecar: `currentStep: 4`
- Load Step 8 agent (LLM Evaluator persona)
- Query Knowledge MCP for guidance
- Design evaluation framework

---

### Phase 4 → Phase 5 (To Operations)

**Trigger:** Quality gate decision made (GO or CONDITIONAL)

**Pre-requisites for GO:**
- ✅ All evaluation results documented
- ✅ Metrics compared against thresholds
- ✅ Gate decision explicitly recorded
- ✅ Stakeholder approval obtained
- ✅ Implementation stories generated

**Pre-requisites for CONDITIONAL GO:**
- ✅ All above, PLUS
- ✅ Conditions clearly listed
- ✅ Deadlines set
- ✅ Monitoring thresholds defined
- ✅ Owner assigned for each condition

**Pre-requisites for NO-GO:**
- ✅ Return to Phase 3
- ✅ Document blocker issues
- ✅ Estimate fix timeline
- ✅ Plan re-evaluation

**Handoff to Phase 5:**
- Sidecar: `currentStep: 5, gate_decision: [GO|CONDITIONAL]`
- Load Step 9 agent (MLOps Engineer persona)
- Deploy with monitoring setup
- Reference Phase 4 results for baseline metrics

---

## Common Evaluation Scenarios

### Scenario A: Simple Prompt-Based System (No Fine-Tuning, No RAG)

```
Phase 1: Minimal - Just data collection
Phase 2: Skipped (no fine-tuning)
Phase 3: Design prompts
Phase 4: Quality Gate

Evaluation Focus:
├─ Accuracy: Does it answer correctly?
├─ Format: Does it follow output format?
├─ Safety: Does it avoid harmful outputs?
└─ Latency: Is response time acceptable?

No RAG complications → simpler evaluation
Single layer instead of retrieval + generation
Duration: Phase 4 takes 1 week instead of 2
```

### Scenario B: RAG System (No Fine-Tuning)

```
Phase 1: Feature pipeline (chunking, embeddings)
Phase 2: Skipped (no fine-tuning)
Phase 3: Design RAG + prompts
Phase 4: Quality Gate

Evaluation Focus (THREE LAYERS):
├─ Layer A - Retrieval: Recall@5, NDCG
├─ Layer B - Generation: Faithfulness, hallucination
└─ Layer C - End-to-end: Accuracy, citation accuracy

RAG complications → separate layer evaluation
Independent debugging of retrieval vs generation
Duration: Phase 4 takes 1-2 weeks (more complex)
```

### Scenario C: Fine-Tuned System

```
Phase 1: Feature pipeline (training data)
Phase 2: Training pipeline (fine-tune model)
Phase 3: Design inference (prompts, optional RAG)
Phase 4: Quality Gate

Evaluation Focus:
├─ Model-specific metrics (perplexity, task benchmarks)
├─ Comparison to baseline (pre-fine-tune)
├─ Generalization (hold-out test set)
└─ Plus all standard evaluation criteria

Fine-tuning complications → additional validation
Must show fine-tuning helped (not just memorized)
Duration: Phase 4 takes 2 weeks (most complex)
```

---

## Success Criteria by Phase

### Phase 4 Success: Quality Gate Explicitly Made

**Minimum success:**
- ✅ Evaluation framework designed
- ✅ Tests executed with results documented
- ✅ Gate decision made (GO/CONDITIONAL/NO-GO)
- ✅ Decision recorded in decision-log.md
- ✅ Stakeholder approval obtained

**Good success:**
- ✅ Above, PLUS
- ✅ Multiple evaluation methods executed
- ✅ Knowledge MCP queries documented
- ✅ Implementation stories generated
- ✅ Production monitoring plan attached

**Excellent success:**
- ✅ Above, PLUS
- ✅ Ablation studies showing why metrics changed
- ✅ Detailed failure analysis (if CONDITIONAL or NO-GO)
- ✅ Regression prevention plan documented
- ✅ User acceptance criteria validated

---

## Reference Documents

**In AI Engineering Workflow:**
- Step 8: `/workflows/ai-engineering-workflow/steps/4-evaluation/step-08-llm-evaluator.md`
- Quality Gate Checklist: `/workflows/ai-engineering-workflow/checklists/quality-gate-checklist.md`

**In This Analysis:**
- Detailed findings: `/evaluation-placement-analysis.md`
- Visual architecture: `/evaluation-timing-architecture.md`
- MCP query guide: `/evaluation-mcp-queries-reference.md`

---

## Summary

The AI Engineering Workflow positions evaluation as Phase 4 - an explicit, documented quality gate between pipeline design and deployment. This placement is optimal because:

1. **Complete system ready** - Not evaluating partial components
2. **Decisions are defensible** - Documented gate with rationale
3. **Baseline for monitoring** - Quality gate targets guide Phase 5 alerts
4. **Early enough to fix** - Issues discovered before users see them
5. **Late enough to matter** - Full integration testing on real system

The workflow integrates:
- **Phases 1-3:** Lightweight, integrated evaluation (guides iteration)
- **Phase 4:** Formal quality gate (makes deployment decision)
- **Phase 5+:** Production monitoring (validates in real world)

This three-layer approach is what the knowledge base recommends as best practice.
