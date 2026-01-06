# Evaluation Timing Architecture - Visual Reference

## 1. Timeline: When Evaluation Happens

```
PROJECT TIMELINE
═══════════════════════════════════════════════════════════════════════════════

                       ╔════════════════════════════════════╗
PHASE 0: SCOPING       ║ Define quality targets & success   ║
(1-2 weeks)           ║ metrics upfront                    ║
                       ╚════════════════════════════════════╝
                                  ↓
    ┌─────────────────────────────────────────────────────────┐
    │                                                           │
    ├──────────────────────────────────────────────────────────┤
    │   PHASE 1-3: BUILD PIPELINES (Feature, Training, RAG)    │
    │   Timeline: 4-12 weeks depending on complexity            │
    │                                                           │
    │   ◆ Continuous Integration Testing                       │
    │   │ └─ Manual spot checks during development            │
    │   │ └─ Quick feedback loops (<5 min)                    │
    │   │ └─ Informal golden examples                         │
    │   │ └─ Guide design decisions                           │
    │   │ └─ NOT for deployment decision                      │
    │   │                                                       │
    │   └─ Timeline: Continuous, throughout 4-12 weeks        │
    │                                                           │
    └─────────────────────────────────────────────────────────┘
                                  ↓
    ╔═════════════════════════════════════════════════════════╗
    ║  CRITICAL: PHASE 4 - FORMAL QUALITY GATE                ║
    ║  Timeline: 1-2 weeks                                    ║
    ║                                                          ║
    ║  The "Quality Checkpoint" - Explicit GO/NO-GO           ║
    ║  ┌──────────────────────────────────────────────────┐   ║
    ║  │ 1. Design evaluation framework (1-2 days)        │   ║
    ║  │    - Define metrics, thresholds, test datasets   │   ║
    ║  │    - Query Knowledge MCP for best practices      │   ║
    ║  │                                                  │   ║
    ║  │ 2. Execute evaluation (3-5 days)                │   ║
    ║  │    - Retrieval layer (if RAG)                   │   ║
    ║  │    - Generation layer                           │   ║
    ║  │    - End-to-end quality                         │   ║
    ║  │    - Safety & adversarial tests                 │   ║
    ║  │    - Document all results                       │   ║
    ║  │                                                  │   ║
    ║  │ 3. Make gate decision (1 day)                   │   ║
    ║  │    - GO: Deploy to production                   │   ║
    ║  │    - CONDITIONAL GO: Deploy with conditions     │   ║
    ║  │    - NO-GO: Return to Phase 3 for fixes         │   ║
    ║  │                                                  │   ║
    ║  └──────────────────────────────────────────────────┘   ║
    ║                                                          ║
    ║  GUARDRAIL: No deployment without gate decision         ║
    ╚═════════════════════════════════════════════════════════╝
                                  ↓
    ┌─────────────────────────────────────────────────────────┐
    │                                                          │
    │  PHASE 5: OPERATIONS - DEPLOYMENT                       │
    │  Timeline: Day 1 (if GO) or conditional timeline       │
    │                                                          │
    │  ◆ Production Monitoring (Continuous)                   │
    │  │ └─ Real-time metric dashboards                      │
    │  │ └─ Alerts on regression                             │
    │  │ └─ Compare against gate targets                     │
    │  │ └─ User feedback collection                         │
    │  │                                                      │
    │  └─ Timeline: Ongoing, 24/7                            │
    │                                                          │
    └─────────────────────────────────────────────────────────┘
                                  ↓
    PHASE 6+: CONTINUOUS IMPROVEMENT
    │ Feedback loops from production
    │ Update test datasets
    │ Iterate on pipelines
    └─→ [Cycle back to Phase 1-3 for improvements]
```

---

## 2. Evaluation Methods by Phase

```
PHASE PROGRESSION & EVALUATION METHODS
═══════════════════════════════════════════════════════════════════════════════

INTEGRATED EVALUATION
(Phases 1-3, Continuous)
├─ Method: Manual spot checking
├─ Speed: <5 min per test
├─ Rigor: Informal, subjective
├─ Scope: Small test sets (10-20 examples)
├─ Goal: Guide development decisions
└─ Example: Prompt engineer tests revised system message on 10 examples

            ↓ TRANSITION (still Phase 3)

FORMAL EVALUATION
(Phase 4, Week 1-2)
├─ Method: Structured, documented evaluation
├─ Speed: 3-5 days full execution
├─ Rigor: Formal, reproducible, auditable
├─ Scope: Comprehensive test sets (200+ examples)
├─ Goal: Make deployment decision
├─ Components:
│  ├─ Automated metrics (latency, accuracy, retrieval)
│  ├─ LLM-as-judge evaluation (with bias mitigation)
│  ├─ Human evaluation (spot checks, expert review)
│  └─ Adversarial testing (safety validation)
└─ Example: Full evaluation framework with multiple metrics, decision log

            ↓ GATE DECISION (GO/NO-GO)

PRODUCTION MONITORING
(Phase 5+, Continuous)
├─ Method: Real-time dashboard + alerting
├─ Speed: Continuous, real-time response
├─ Rigor: Automated + human review on alerts
├─ Scope: All production traffic
├─ Goal: Detect regressions, collect user feedback
└─ Example: Monitor accuracy in real time, alert if drops below gate target

```

---

## 3. RAG System: Evaluation Layer Separation

```
┌─────────────────────────────────────────────────────────────────┐
│                    FULL RAG SYSTEM                              │
│                                                                 │
│  Query Input → Retrieval → Retrieved Context → Generation       │
│                   ↓                              ↓              │
│              [Layer A]                      [Layer B]           │
│            Retrieval Eval                 Generation Eval       │
│                                                                 │
│  ├─ Retrieval Layer (Layer A)                                  │
│  │  └─ Metrics: Recall@K, Precision@K, MRR, NDCG              │
│  │  └─ Question: "Are the right docs retrieved?"              │
│  │  └─ Target: Recall@5 >= 80%                                │
│  │  └─ Failure diagnosis: Vector search issue                 │
│  │  └─ Fix strategy: Improve embeddings, adjust K, rerank    │
│  │                                                              │
│  ├─ Generation Layer (Layer B)                                 │
│  │  └─ Metrics: Faithfulness, Hallucination, Relevance       │
│  │  └─ Question: "Is the answer grounded in context?"        │
│  │  └─ Target: Faithfulness >= 90%, Hallucination < 5%       │
│  │  └─ Failure diagnosis: Prompt issue or context confusion  │
│  │  └─ Fix strategy: Adjust prompt, improve context, different model │
│  │                                                              │
│  └─ End-to-End Layer (Layers A+B Combined)                    │
│     └─ Metrics: Accuracy, Citation Accuracy, Completeness     │
│     └─ Question: "Does the full system answer correctly?"     │
│     └─ Target: Accuracy >= 85%, Citations >= 90%              │
│     └─ Failure diagnosis: Either retrieval or generation      │
│     └─ Fix strategy: Debug layer A and B independently        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Why Separate?

  Without separation:          With separation:
  ─────────────────────────    ──────────────────
  Accuracy = 70%               Layer A (Retrieval): 75% Recall
  ❌ Which is broken?          ✓ Retrieval OK, improve ranking
    - Retrieval?               Layer B (Generation): 80% Faithful
    - Generation?              ✓ Generation OK, improve prompt
    - Both?                     End-to-End: 70% Accuracy

  → Expensive debugging        → Targeted fixes
  → Wrong component fixed      → Correct component fixed
```

---

## 4. Quality Gate Decision Matrix

```
QUALITY GATE: Three Possible Outcomes
═══════════════════════════════════════════════════════════════════════════════

Criterion                    GO                CONDITIONAL        NO-GO
─────────────────────────────────────────────────────────────────────────────
Accuracy                     >= 85%             80-84%             < 80%
Latency P99                  <= 500ms           500-1000ms         > 1000ms
Safety (adversarial)         No failures        Minor issues       Critical issues
Hallucination Rate           < 5%               5-10%              > 10%
Citation Accuracy (RAG)      >= 90%             85-89%             < 85%
─────────────────────────────────────────────────────────────────────────────

DECISION RULES:
──────────────

GO (All criteria in "GO" column)
├─ Action: Proceed to Phase 5 (Production Deployment)
├─ Timeline: Deploy within 1 week
├─ Monitoring: Set up production dashboards
└─ Example: All metrics green, zero critical failures

CONDITIONAL GO (Some criteria in "CONDITIONAL", none in "NO-GO")
├─ Action: Proceed to Phase 5 WITH documented conditions
├─ Conditions: List specific items to fix post-deployment
├─ Timeline: Deploy + fix conditions within 2 weeks
├─ Monitoring: Enhanced alerting for conditional items
├─ Escalation: Auto-rollback if condition worsens
└─ Example: Accuracy acceptable (83%), latency needs optimization

NO-GO (Any criterion in "NO-GO" column)
├─ Action: Return to Phase 3 (Inference Pipeline) for fixes
├─ Blocker Analysis: Identify which component needs work
│  ├─ If retrieval metrics low → improve RAG architecture
│  ├─ If generation metrics low → improve prompt/model
│  └─ If both low → fundamental architecture review
├─ Timeline: 1-4 weeks depending on fixes needed
├─ Reschedule: Quality gate re-evaluation after fixes
└─ Example: Safety testing revealed jailbreak vulnerability


TRACKING THE GATE DECISION:
───────────────────────────
├─ Document in: evaluation-spec.md
├─ Update decision log: decision-log.md
├─ Assign responsibility: Who will monitor conditions?
├─ Set milestones: When will conditions be resolved?
└─ Approval: Get sign-off from stakeholders before deployment
```

---

## 5. Knowledge MCP Integration Points

```
EVALUATION PHASE WORKFLOW WITH KNOWLEDGE MCP
═══════════════════════════════════════════════════════════════════════════════

Step 8: LLM Evaluator (Phase 4)
│
├─ 1. Welcome to Evaluation
│   └─ Present step introduction & context
│
├─ 2. ◆ QUERY KNOWLEDGE MCP ◆
│   │
│   ├─ Query 1: get_warnings(topic="evaluation")
│   │  └─ Returns: Evaluation anti-patterns, pitfalls
│   │  └─ Surfaces: LLM-as-judge biases, circular evaluation risks
│   │
│   ├─ Query 2: search_knowledge("LLM judge evaluation bias pitfalls")
│   │  └─ Returns: Bias mitigation strategies
│   │  └─ Surfaces: Position bias, verbosity bias, self-preference bias
│   │
│   ├─ Query 3: get_methodologies(topic="evaluation")
│   │  └─ Returns: Step-by-step evaluation processes
│   │  └─ Surfaces: Recommended metrics, test dataset design
│   │
│   └─ Query 4: search_knowledge("model evaluation metrics benchmark testing")
│      └─ Returns: Implementation patterns for evaluation frameworks
│      └─ Surfaces: Metric selection, threshold recommendations
│
├─ 3. Synthesize Knowledge Base Insights
│   │
│   ├─ Anti-patterns to avoid:
│   │  ├─ Using LLM-generated test data
│   │  ├─ Single metric for quality assessment
│   │  ├─ Skipping retrieval layer evaluation (RAG)
│   │  └─ Using same model for evaluation and generation
│   │
│   ├─ Recommended approaches:
│   │  ├─ Multi-method evaluation (automated + human)
│   │  ├─ Separate retrieval and generation metrics
│   │  ├─ LLM-as-judge with bias mitigation
│   │  └─ Human-verified test datasets
│   │
│   └─ Critical warnings:
│      ├─ Position bias in LLM judgments
│      ├─ Hallucination evaluation ambiguity
│      └─ Production metric drift from gate targets
│
├─ 4. Design Evaluation Framework (with user)
│   ├─ Define functional criteria
│   ├─ Define non-functional criteria
│   ├─ Design test plan
│   ├─ Design test datasets
│   └─ Select evaluation methods
│
├─ 5. Execute Evaluation (outside MCP)
│   ├─ Run retrieval layer tests
│   ├─ Run generation layer tests
│   ├─ Run end-to-end tests
│   └─ Document all results
│
├─ 6. Make Quality Gate Decision
│   ├─ Evaluate against pre-defined criteria
│   ├─ Document decision in evaluation-spec.md
│   ├─ Update decision-log.md
│   └─ Generate implementation stories
│
└─ 7. Menu: [A] Analyze further [P] View progress [C] Continue to Phase 5

MCP TOOLS ACTIVE DURING EVALUATION:
───────────────────────────────────
┌─────────────────────────────────────┐
│  Knowledge MCP Provides:             │
├─────────────────────────────────────┤
│ ✓ Evaluation best practices         │
│ ✓ Anti-pattern warnings             │
│ ✓ Implementation patterns           │
│ ✓ Methodology guidance              │
│ ✓ Metric recommendations            │
│ ✓ Test dataset design               │
│ ✓ Bias mitigation strategies        │
│ ✓ RAG-specific evaluation guidance  │
└─────────────────────────────────────┘

Workflow does NOT query MCP for:
├─ Actual evaluation execution (that's the developer's job)
├─ Specific metric values (domain-specific)
├─ Test dataset content (user-specific)
└─ Final gate decision (user's choice based on requirements)

MCP serves as: Knowledge base for HOW to evaluate, not WHAT values to use
```

---

## 6. Common Failure Modes & Prevention

```
EVALUATION TIMING PITFALLS & HOW TO AVOID
═══════════════════════════════════════════════════════════════════════════════

PITFALL #1: Evaluation Too Late
─────────────────────────────────
Scenario:  Discover critical issues only after full system built
           Requires major rearchitecture
           Stakeholder disappointment
Cost:      2-4 weeks delay, rework

Prevention:
├─ Integrate continuous testing during phases 1-3
├─ Use golden examples throughout development
├─ Do weekly informal evaluations
└─ Phase 4 just formalizes what's already tested


PITFALL #2: Single Metric Optimization
───────────────────────────────────────
Scenario:  Optimize for accuracy, break latency
           Optimize for latency, increase hallucination
           Game metrics to pass gate
Cost:      Production failures after gate approval

Prevention:
├─ Define balanced scorecard with correlated metrics
├─ Query knowledge base for complementary metrics
├─ Set minimum thresholds for ALL metrics
└─ Regular human review during metric definition


PITFALL #3: Circular Evaluation Bias
──────────────────────────────────────
Scenario:  Generate test data with LLM
           Evaluate LLM answers using LLM judge
           System optimizes for its own outputs
Cost:      False confidence in readiness

Prevention:
├─ Source test data from humans or production examples
├─ Use different model for LLM-as-judge
├─ Include human evaluation spot checks
└─ Query warnings about evaluation biases


PITFALL #4: Forgetting Retrieval (RAG Systems)
─────────────────────────────────────────────
Scenario:  Test generation quality without checking retrieval
           Blame generation for retrieval failures
           Fix wrong component
Cost:      Wrong optimization, continued failures in production

Prevention:
├─ Separate retrieval metrics (Recall@K, NDCG)
├─ Separate generation metrics (faithfulness, hallucination)
├─ Debug layers independently
└─ Document layer-specific thresholds


PITFALL #5: Vague Quality Gate
───────────────────────────────
Scenario:  Criteria like "good quality" or "acceptable latency"
           Different team members interpret differently
           Conflict at deployment decision time
Cost:      Blocked deployment, rework decisions

Prevention:
├─ Define ALL criteria quantitatively: "Accuracy >= 85%"
├─ Pre-define pass/fail thresholds
├─ Make gate decision reproducible
└─ Document rationale for each threshold


PITFALL #6: Skipping Production Monitoring
──────────────────────────────────────────
Scenario:  System passes gate but degrades in production
           No alerting, issues go undetected for weeks
           User complaints before team knows
Cost:      Reputation damage, urgent hotfixes

Prevention:
├─ Set up production dashboards matching gate metrics
├─ Configure alerts for regression below gate targets
├─ Establish baseline from gate evaluation
└─ Include production monitoring in Phase 5 launch plan
```

---

## 7. Decision Flowchart: When to Evaluate

```
DECISION FLOWCHART: What Evaluation Approach to Use?
═══════════════════════════════════════════════════════════════════════════════

START: New AI System Feature
│
├─ Have pipelines been designed? (Phases 1-3 complete)
│  NO  → Continue building, use integrated testing
│  YES ↓
│
├─ Have quality targets been defined? (From Phase 0)
│  NO  → Define success metrics in scoping
│  YES ↓
│
├─ Are you ready to decide on deployment?
│  NO  → Use integrated evaluation to guide iteration
│  YES ↓
│
├─ Time for formal quality gate (Phase 4)
│  │
│  ├─ Is this a RAG system?
│  │  YES → Evaluate retrieval + generation separately
│  │  NO  → Evaluate end-to-end generation
│  │
│  ├─ What test data do you have?
│  │  LLM-generated  → ❌ Don't use, get human data
│  │  Human-curated  → ✓ Use as golden set
│  │  From production → ✓ Use for real-world validation
│  │
│  ├─ Will you use LLM-as-judge?
│  │  YES → Query Knowledge MCP for bias mitigation
│  │  NO  → Use automated metrics or human evaluation
│  │
│  ├─ Execute evaluation with chosen methods
│  │  Document all results
│  │  Compare against pre-defined thresholds
│  │
│  ├─ Make explicit gate decision
│  │  ├─ GO           → Proceed to Phase 5
│  │  ├─ CONDITIONAL  → Proceed with conditions listed
│  │  └─ NO-GO        → Return to Phase 3 for fixes
│  │
│  └─ Document decision
│     ├─ evaluation-spec.md
│     ├─ decision-log.md
│     └─ Stakeholder approval
│
└─ DEPLOYMENT (if GO or CONDITIONAL)
   │
   └─ Set up production monitoring
      ├─ Dashboards
      ├─ Alerts
      ├─ Baseline from gate evaluation
      └─ Continuous feedback loops
```

---

## Summary: The Three Layers Recap

| Layer | When | Why | Method | Duration |
|-------|------|-----|--------|----------|
| **Integrated** | Phases 1-3 (continuous) | Quick feedback to guide development | Manual spot checking | <5 min per test |
| **Quality Gate** | Phase 4 (formal) | Explicit checkpoint before deployment | Structured evaluation framework | 3-5 days execution |
| **Production** | Phase 5+ (ongoing) | Real-world validation and regression detection | Continuous monitoring & alerting | Lifetime of system |

**The Key Rule:** Never skip the quality gate. The gate is where design decisions become deployment commitments.
