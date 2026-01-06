# Operations Knowledge - Query Examples

Complete working examples for querying the knowledge MCP in Phase 5.

---

## Example 1: Design Continuous Monitoring System

### Scenario
Building the monitoring infrastructure for Phase 5 Operations. Need to know what metrics to track, how frequently, and what thresholds to use.

### Query
```
search_knowledge("production monitoring metrics deployment health")
```

### Expected Results (from current database)
- 51 monitoring-related extractions
- Primarily patterns and methodologies
- Key pattern: "Unified Monitoring" dashboard concept
- Topics: `evaluation`, `deployment`, `inference`

### Sample Synthesis Steps

1. **Extract patterns**
   - Unified monitoring dashboard (aggregate health)
   - Metric aggregation approaches
   - Real-time vs batch monitoring trade-offs

2. **Identify metrics to track**
   - Model latency (340 extractions available)
   - Error rates
   - Drift signals
   - Cost metrics

3. **Surface warnings**
   - Don't rely on single metric
   - Embedding model changes break all vectors
   - Silent failures without monitoring

### Example Output (Synthesized)
> "Implement unified monitoring with three metric categories:
> 1. Performance: latency (target <500ms), throughput
> 2. Quality: error rate (target <1%), drift detection
> 3. Cost: API costs, compute usage
>
> Update frequency: Real-time for latency/errors, hourly for drift.
> Thresholds derived from 944 drift detection extractions in knowledge base."

---

## Example 2: Define Retraining Triggers

### Scenario
Need to establish when to automatically trigger model retraining in production.

### Query
```
search_knowledge("model drift detection retraining triggers evaluation")
```

### Expected Results
- Multiple "Model Retraining Workflow" extractions
- 944 drift detection patterns available
- Workflow triggers specified in detail
- Topics: `evaluation`, `deployment`, `training`

### Sample Synthesis Steps

1. **Extract trigger conditions**
   - Performance drops below threshold
   - Drift detected above statistical significance
   - Data distribution shift detected

2. **Identify workflow steps**
   - Trigger detection (automated)
   - Data preparation
   - Model training
   - Evaluation gate
   - Production deployment

3. **Surface evaluation gates**
   - Validate new model beats baseline
   - Check for model degradation
   - Review metrics comprehensive (not single metric)

### Example Output
> "Establish three retraining triggers:
> 1. Performance Trigger: Model accuracy drops >5% from baseline
> 2. Drift Trigger: Detected drift p-value < 0.05 over 7-day window
> 3. Scheduled Trigger: Weekly retraining regardless of metrics
>
> Workflow:
> - Step 1: Trigger condition detected
> - Step 2: Prepare training data (validate quality gates)
> - Step 3: Train new model (fine-tune or retrain)
> - Step 4: Evaluate against current model (A/B test framework)
> - Step 5: Deploy if performance gate passes
> - Step 6: Monitor retraining impact
>
> This retraining workflow pattern found in 91 operations workflow extractions."

---

## Example 3: Setup Cost Monitoring & Budget Gates

### Scenario
Need to implement cost tracking and establish budget gates to prevent runaway API costs.

### Query
```
search_knowledge("cost monitoring API usage inference serving budget")
```

### Expected Results
- 274 cost-related extractions
- Caching patterns (semantic, prompt) for cost reduction
- Budget gate frameworks
- Topics: `inference`, `deployment`

### Sample Synthesis Steps

1. **Extract cost sources**
   - LLM API calls (primary)
   - Embedding API calls
   - Vector database queries
   - Compute resources

2. **Identify monitoring points**
   - Per-request cost tracking
   - Daily/monthly budget tracking
   - Cost alerts above threshold

3. **Surface optimization patterns**
   - Semantic caching (reduce repeated queries)
   - Prompt caching (reduce input tokens)
   - Batch processing (cheaper rates)
   - Model selection (cheaper models available)

### Example Output
> "Implement tiered cost monitoring:
>
> **Real-time Tracking:**
> - Track cost per request
> - Alert when daily cost exceeds $X
> - Block requests if monthly budget exceeded
>
> **Cost Optimization (from 274 extractions):**
> - Semantic caching: Cache embeddings for similar queries (20-50% cost reduction)
> - Prompt caching: Cache system prompts + few-shots (10-30% reduction)
> - Model selection: Use cheaper model when acceptable (cost_effective tag)
> - Batch processing: Group requests where latency acceptable
>
> **Gates:**
> - Daily budget gate: Pause new requests if $X spent
> - Monthly budget gate: Require approval for overages
> - Cost-per-metric gate: Cost per accuracy point should decrease over time"

---

## Example 4: Define Production Deployment Checklist

### Scenario
Creating the pre-deployment checklist for moving models to production.

### Query
```
search_knowledge("production deployment checklist inference evaluation")
```

### Expected Results
- 70 production checklists
- 156 production workflow extractions
- Latency/error rate specifications
- Validation requirements

### Sample Synthesis Steps

1. **Extract from checklists**
   - Model latency <500ms
   - Error rate <1%
   - Input validation in place
   - Monitoring configured

2. **Identify validation gates**
   - Performance meets SLA
   - No embedding model changes from training
   - Cost monitoring active
   - Rollback plan documented

3. **Surface warnings**
   - Embedding model migration breaks production (invalid vectors)
   - Ensure backward compatibility

### Example Output (Checklist)
```markdown
## Pre-Production Deployment Checklist

**Performance Requirements (from 340+ latency extractions)**
- [ ] Model latency under 500ms p95
- [ ] Throughput meets expected QPS
- [ ] Error rate below 1%
- [ ] Cold start latency documented

**Quality Validation (from 465 evaluation extractions)**
- [ ] Model performance validated against test set
- [ ] Edge cases tested
- [ ] Prompt injection vulnerabilities assessed
- [ ] Bias evaluation completed

**Operations Readiness (from 178 deployment extractions)**
- [ ] Monitoring configured (metrics, alerts, thresholds)
- [ ] Retraining pipeline dry-run completed
- [ ] Cost monitoring active and budget set
- [ ] Rollback procedure documented and tested

**Data/Model Integrity (from 140 feature drift extractions)**
- [ ] Feature definitions match training
- [ ] Embedding models identical to training environment
- [ ] Input data transformations documented
- [ ] Drift monitoring baseline established

**Operational Procedures (custom - not in knowledge base)**
- [ ] On-call escalation defined
- [ ] Incident response procedure prepared
- [ ] Deployment strategy (canary vs blue-green vs rolling) chosen
```

---

## Example 5: Design Alert Configuration

### Scenario
Establishing which metrics to alert on, at what thresholds, and to whom.

### Query
```
search_knowledge("alerting thresholds reliability monitoring production metrics")
```

### Expected Results
- 10 alerting methodology extractions
- 13 reliability patterns
- Threshold recommendations
- SLA patterns (131 extractions)

### Sample Synthesis Steps

1. **Extract alerting categories**
   - Performance alerts (latency)
   - Reliability alerts (error rate)
   - Drift alerts (data quality)
   - Cost alerts (budget)

2. **Identify threshold recommendations**
   - From SLA extractions: P95 latency targets
   - From reliability patterns: 99.9% uptime targets
   - From evaluation: Metric thresholds

3. **Surface escalation logic**
   - Immediate escalation for error spikes
   - Gradual escalation for drift increase
   - Daily summary for cost tracking

### Example Output
```markdown
## Alert Configuration (from knowledge base)

**Tier 1 Alerts (Immediate Escalation)**
- Error rate spike >5% above baseline (p-value < 0.05)
  Threshold: Alert immediately, page on-call
- Model latency p95 > 800ms (vs 500ms baseline)
  Threshold: Alert immediately, page on-call
- Monthly budget exceeded
  Threshold: Block new requests, escalate to finance

**Tier 2 Alerts (Next 30 minutes)**
- Drift detected (statistical significance p < 0.05)
  From: 944 drift detection extractions
  Action: Trigger retraining workflow
- Error rate trending up >2% over 1 hour
  Threshold: Alert, monitor closely, escalate if continues
- Daily cost 50% above average
  Threshold: Alert on-call, investigate

**Tier 3 Alerts (Batch Summary)**
- Daily performance summary (email)
  Threshold: Always sent
- Weekly cost breakdown (dashboard)
  Threshold: Always updated
- Monthly evaluation results (report)
  Threshold: Auto-generated

Note: Specific on-call escalation procedures not available in knowledge base.
Custom procedures required for your team.
```

---

## Example 6: A/B Testing in Production

### Scenario
Setting up controlled experimentation to safely test model improvements before full rollout.

### Query
```
search_knowledge("a/b testing experimentation evaluation production metrics")
```

### Expected Results
- 94 A/B testing extractions
- Multi-armed bandit patterns
- Statistical significance methodology
- Sample size calculation

### Sample Synthesis Steps

1. **Extract experimentation framework**
   - Control vs treatment split
   - Randomization methodology
   - Duration requirements

2. **Identify metric selection**
   - Primary metric (accuracy, revenue, user satisfaction)
   - Secondary metrics (latency, cost)
   - Statistical significance threshold (p < 0.05)

3. **Surface power analysis requirements**
   - Required sample size
   - Minimum detectable effect
   - Power level (80%, 90%)

### Example Output
> "A/B Testing Framework (from 94 production experimentation extractions):
>
> **Setup Phase:**
> 1. Define primary metric (e.g., accuracy)
> 2. Calculate required sample size for 90% power
> 3. Plan test duration (minimum 1 week to capture daily patterns)
> 4. Randomize traffic 50/50 control vs treatment
>
> **Monitoring Phase:**
> 1. Track cumulative metrics (daily, hourly updates)
> 2. Set significance level p < 0.05
> 3. Don't peek until scheduled end time (avoid false positives)
> 4. Monitor for interaction effects (time of day, user cohorts)
>
> **Evaluation Phase:**
> 1. Calculate confidence intervals for effect size
> 2. If significant, roll out treatment to 100%
> 3. If not significant, keep control or extend test
> 4. Document results for model genealogy
>
> **Cost Consideration:**
> Can use cheaper model in control, newer in treatment to measure
> accuracy-cost trade-off (from cost optimization patterns)"

---

## Example 7: Feature Drift & Data Quality Monitoring

### Scenario
Detecting when the input data distribution shifts, which indicates model retraining needed.

### Query
```
search_knowledge("feature drift data quality monitoring production degradation")
```

### Expected Results
- 140 feature drift extractions
- 107 logging/debugging patterns
- Data quality framework
- Degradation detection methods

### Sample Synthesis Steps

1. **Extract drift detection methods**
   - Statistical tests (KS test, chi-square)
   - Embedding distance changes
   - Class distribution shifts

2. **Identify monitoring frequency**
   - Real-time for critical features
   - Hourly for secondary features
   - Daily for summary reports

3. **Surface warning signals**
   - Silent degradation from feature drift
   - Embedding space changes break production

### Example Output
> "Data Quality & Drift Monitoring (from 140 feature drift + 107 logging extractions):
>
> **Feature Drift Detection:**
> 1. Establish training distribution baseline (mean, std, quantiles)
> 2. Continuous monitoring of production feature distributions
> 3. Statistical test (KS test, p < 0.05) to detect shifts
> 4. Alert when p < 0.05 detected (shift is real)
>
> **Monitoring Strategy:**
> - Critical features: Monitor every hour
> - Secondary features: Monitor every 6 hours
> - Embeddings: Monitor daily (compare to baseline embeddings)
>
> **When Drift Detected:**
> 1. Alert operations team (informational)
> 2. Trigger retraining workflow automatically (from retraining patterns)
> 3. Compare new model performance to current (A/B test)
> 4. If improvement >X%, deploy; otherwise wait
>
> **Critical Warning:** If embedding model changed, all existing vectors
> are invalid - this is a production emergency requiring immediate
> reindexing. (From 140 feature drift warnings in knowledge base)"

---

## How to Implement These Queries in Workflow

### Pseudo-code for Phase 5 Step

```python
# Phase 5: Operations & Complete

class OperationsStep:
    def __init__(self, knowledge_mcp):
        self.mcp = knowledge_mcp

    def design_monitoring(self):
        """Step 1: Design continuous monitoring"""
        results = self.mcp.search_knowledge(
            "production monitoring metrics deployment health"
        )
        # Synthesize into monitoring design
        return self.synthesize_monitoring(results)

    def setup_retraining(self):
        """Step 2: Setup automated retraining"""
        results = self.mcp.search_knowledge(
            "model drift detection retraining triggers evaluation"
        )
        # Synthesize into retraining workflow
        return self.synthesize_retraining(results)

    def implement_cost_gates(self):
        """Step 3: Cost monitoring & budget gates"""
        results = self.mcp.search_knowledge(
            "cost monitoring API usage inference serving budget"
        )
        # Synthesize into cost strategy
        return self.synthesize_cost_gates(results)

    def create_deployment_checklist(self):
        """Step 4: Pre-deployment validation"""
        results = self.mcp.search_knowledge(
            "production deployment checklist inference evaluation"
        )
        # Synthesize into checklist
        return self.synthesize_checklist(results)

    def design_alerts(self):
        """Step 5: Alert configuration"""
        results = self.mcp.search_knowledge(
            "alerting thresholds reliability monitoring production"
        )
        # Synthesize into alert rules
        # Note: On-call procedures require custom implementation
        return self.synthesize_alerts(results)
```

---

## Summary: Which Queries Work Best

| Use Case | Query | Confidence | Notes |
|----------|-------|-----------|-------|
| Monitoring | `production monitoring metrics` | High | 51 extractions |
| Retraining | `model drift detection retraining` | High | 944 extractions |
| Cost Control | `cost monitoring API usage` | High | 274 extractions |
| Deployment | `production deployment checklist` | Medium | Missing canary/blue-green |
| Alerting | `alerting thresholds monitoring` | Medium | Thin on on-call |
| Governance | `model governance compliance` | Low | Only 8 extractions |
| Incident Response | `incident response procedures` | None | Not in knowledge base |

---

## Next Steps for Your Team

1. **Test these queries** against your knowledge MCP
2. **Implement the synthesis patterns** in your Phase 5 step
3. **Document gaps** you encounter (governance, incident response, on-call)
4. **Plan knowledge base enhancement** with priority ingest of missing sources
5. **Iterate** based on workflow execution feedback
