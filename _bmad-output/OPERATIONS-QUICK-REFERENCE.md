# Operations Knowledge - Quick Reference Guide

## Overview

The knowledge MCP contains **450 operations-related extractions** (26.7% of 1,684 total), primarily from **LLM Handbook** (79%).

## What You Can Query Today

### Category 1: Model Monitoring & Retraining ✅ EXCELLENT
**Available:** 944 drift detection extractions, retraining workflows, performance thresholds

Query patterns:
```
search_knowledge("model drift detection retraining")
search_knowledge("production monitoring metrics")
search_knowledge("model performance degradation triggers")
```

**Use for:** Phase 5 Operations step - continuous monitoring design, drift response automation

---

### Category 2: Performance & Cost Optimization ✅ EXCELLENT
**Available:** 354 performance, 274 cost extractions, caching patterns (semantic, prompt)

Query patterns:
```
search_knowledge("latency optimization inference serving")
search_knowledge("cost monitoring API usage")
search_knowledge("semantic caching batching")
```

**Use for:** Inference phase optimization, budget gates

---

### Category 3: Evaluation & Quality Metrics ✅ EXCELLENT
**Available:** 465 evaluation extractions, metric selection frameworks, A/B testing (94)

Query patterns:
```
search_knowledge("metrics evaluation framework")
search_knowledge("a/b testing production")
search_knowledge("quality gates evaluation")
```

**Use for:** Phase 4 Evaluation step, metric design

---

### Category 4: Deployment Workflows ✅ GOOD
**Available:** 178 deployment workflows, 156 production patterns, checklists (70)

Query patterns:
```
search_knowledge("deployment workflows production")
search_knowledge("production deployment checklist")
search_knowledge("inference serving deployment")
```

**Use for:** CI/CD integration, production release

⚠️ **WARNING:** Missing canary/blue-green patterns - must supplement

---

### Category 5: Data & Feature Monitoring ✅ GOOD
**Available:** 140 feature drift, 107 logging, 56 distributed tracing

Query patterns:
```
search_knowledge("feature drift data quality")
search_knowledge("distributed tracing debugging")
search_knowledge("production logging")
```

**Use for:** Data validation, error investigation

---

### Category 6: Alerting & Incident Response ⚠️ PARTIAL
**Available:** 10 alerting extractions, 1 incident response, 13 reliability patterns

Query patterns:
```
search_knowledge("alerting thresholds monitoring")
search_knowledge("production reliability")
```

**Use for:** Alert threshold design

⚠️ **WARNING:** On-call procedures, incident response playbooks are missing

---

### Category 7: Model Governance & Compliance ❌ MISSING
**Available:** 8 governance extractions (minimal)

**DO NOT RELY on knowledge base for:**
- Compliance audit trails
- Model versioning strategies
- Model registry patterns
- Governance frameworks

**Must provide custom guidance**

---

## What's Missing (Don't Query)

### Critical Gaps
1. **Canary Deployments** (0) - Progressive rollout safety patterns
2. **Blue-Green Deployments** (0) - Zero-downtime switching
3. **Rolling Deployments** (0) - Instance-by-instance replacement
4. **Incident Response** (1) - On-call, escalation, postmortems
5. **Dashboarding** (1) - Dashboard design, tool selection
6. **Model Governance** (8) - Compliance, audit, versioning

### Moderate Gaps
- Feature flag / circuit breaker patterns (0)
- Infrastructure as Code for ops (0)
- Cost governance frameworks (partial)
- Rollback automation (50 - some coverage)

---

## Topic Tags (For Filtering Queries)

Available tags you can combine:
- `deployment` - (332 total)
- `evaluation` - (465 total)
- `inference` - (480 total)
- `llm` - (721 total)
- `training` - (370 total)
- `fine-tuning` - (338 total)
- `rag` - (635 total)
- `agents` - (36 total)
- `embeddings` - (465 total)
- `prompting` - (148 total)

**Recommended combinations:**
- `deployment` + `evaluation` = Production readiness
- `inference` + `metrics` = Serving optimization
- `evaluation` + `training` = Retraining workflows

---

## Sample Extraction Types by Category

### Workflows (91 total operations-related)
**Best for:** Step-by-step procedures

Examples:
- Model Retraining Workflow (6 steps)
- AI Model Deployment Workflow (3 steps)
- Model Deployment and Monitoring Workflow (4 steps)

---

### Patterns (71 total operations-related)
**Best for:** Architectural approaches, problem-solving

Examples:
- Unified Monitoring dashboard pattern
- AgentOps continuous monitoring pattern
- Semantic Caching for cost reduction

---

### Checklists (70 total operations-related)
**Best for:** Verification, pre-production gates

Examples:
- Model latency checks (500ms SLO)
- Error rate thresholds (1%)
- Input validation requirements

---

### Warnings (70 total operations-related)
**Best for:** Anti-patterns, pitfalls to avoid

Examples:
- Embedding model migration incompatibility (invalidates all vectors)
- Concept drift without monitoring (silent failures)
- Cost explosion from API calls (no rate limiting)

---

### Decisions (56 total operations-related)
**Best for:** Trade-off guidance

Examples:
- Synchronous vs Asynchronous processing
- RAG vs Fine-tuning for knowledge update
- Batch vs Real-time serving

---

## How to Use in Phase 5 (Operations & Complete)

### Query Strategy

```markdown
## Phase 5: Operations & Complete

### Step 1: Monitoring Design
Query: "production monitoring metrics deployment health"
- Extract patterns for continuous monitoring
- Identify drift detection workflows
- Surface cost tracking warnings

### Step 2: Deployment Strategy
Query: "deployment workflows evaluation gates production"
- Extract deployment checklists
- Review production patterns
- *Custom guidance needed for canary/blue-green*

### Step 3: Retraining Automation
Query: "model drift detection retraining triggers evaluation"
- Extract retraining workflows
- Identify performance thresholds
- Establish automated gates

### Step 4: Alert Configuration
Query: "alerting thresholds reliability production metrics"
- Extract alerting methodology
- Review threshold recommendations
- *Custom guidance needed for on-call procedures*

### Step 5: Cost Optimization
Query: "cost monitoring API usage inference serving"
- Extract cost optimization patterns
- Review budget gates
- Identify caching opportunities
```

---

## Synthesis Notes for Agents

When agents use this knowledge:

1. **Confidence Level:** Use with confidence for monitoring/evaluation/cost
2. **Supplement Required:** Add custom guidance for deployment patterns
3. **Not Available:** Don't query for governance, incident response, on-call
4. **Source Concentration:** 79% from LLM Handbook - note this in synthesis
5. **Currency:** Primarily from books; may be 1-2 years old

---

## Future Enhancement Priorities

When ingesting new sources, prioritize:
1. Deployment strategies (canary, blue-green, rolling)
2. Incident response procedures
3. Model governance frameworks
4. Observability tool patterns
5. Cost governance approaches

These would increase Operations readiness from 70% to 90%+.
