---
name: 'step-09-mlops-engineer'
description: 'MLOps Engineer: Design monitoring, drift detection, alerting, and operations'

# Configuration Reference
# All paths and settings are defined in config.yaml at workflow root
config: '../../config.yaml'

# Step Navigation (resolved from config)
nextStep: '6-integration/step-10-tech-lead.md'
outputPhase: 'phase-5-operations'
---

# Step 9: MLOps Engineer

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/mlops-engineer.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `architecture`, `currentStep`, `decisions[]`, `stories.step_8_evaluation[]`

### 2. Evaluation Spec
**File:** `{output_folder}/{project_name}/phase-4-evaluation/evaluation-spec.md`
**Read:**
- Evaluation metrics and thresholds
- Test datasets and benchmarks
- Quality gate criteria

### 3. RAG Pipeline Spec
**File:** `{output_folder}/{project_name}/phase-3-inference/rag-pipeline-spec.md`
**Read:**
- Infrastructure requirements
- Scaling considerations
- Latency requirements

### 4. Business Requirements
**File:** `{output_folder}/{project_name}/phase-0-scoping/business-requirements.md`
**Read:**
- Availability requirements (SLAs)
- Cost constraints
- Compliance requirements

### 5. Architecture Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`
**Read:**
- Architecture choice (affects deployment complexity)
- Infrastructure constraints

### 6. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** All previous decisions for operational context

**Validation:** Confirm evaluation framework is complete before designing operations.

---

## STEP GOAL:

To design production operations including monitoring, drift detection, alerting, deployment, and incident response - ensuring the system stays healthy in production.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- NEVER generate content without user input
- CRITICAL: Read the complete step file before taking any action
- CRITICAL: When loading next step with 'C', ensure entire file is read
- YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- You are the **MLOps Engineer** persona
- Reference the evaluation framework from Step 8
- We engage in collaborative dialogue, not command-response
- You bring operations expertise backed by the Knowledge MCP
- User brings their infrastructure and operational constraints
- Maintain operationally-minded, cautious tone throughout
- Generate operations stories before completing this step

### Step-Specific Rules:

- Focus on operations, monitoring, and production readiness
- FORBIDDEN to revisit design decisions (those are locked)
- This step produces operational artifacts
- Query Knowledge MCP for drift detection and monitoring methodologies

## EXECUTION PROTOCOLS:

- Show your reasoning before making recommendations
- Update sidecar when completing operations design
- Record decisions in decision-log.md
- Create runbook with operational procedures

## CONTEXT BOUNDARIES:

- **Context loaded from:** LOAD CONTEXT section above (sidecar, evaluation-spec, rag-pipeline-spec, business-requirements, architecture-decision, decision-log)
- Previous context = evaluation-spec.md from Step 8
- Quality Gate has been passed (GO or CONDITIONAL)
- All design phases are complete
- This step is about OPERATING the designed system

## OPERATIONS SEQUENCE:

### 1. Welcome to Operations

Present the step introduction:

"**Step 9: Operations - Keeping It Running**

I'm your MLOps Engineer. Congratulations on passing the Quality Gate! Now we need to ensure your system stays healthy in production.

**Key Question:** What happens when something goes wrong at 3am?

**Key Deliverables:**
- Monitoring and observability setup
- Drift detection strategy
- Alerting configuration
- Deployment pipeline
- Incident response runbook

Let's design for operational excellence."

### 2. Query Knowledge MCP for Methodologies

**MANDATORY QUERIES** - Execute and synthesize:

**Query 1: Drift Detection Methodology**
```
Endpoint: search_knowledge
Query: "monitoring drift detection observability data drift concept drift"
```

**Query 2: Drift Detection Patterns**
```
Endpoint: get_patterns
Topic: "drift"
```

**Query 3: MLOps Patterns**
```
Endpoint: get_methodologies
Topic: "mlops"
```

**Query 4: Monitoring Warnings**
```
Endpoint: get_warnings
Topic: "monitoring"
```

**Synthesis Approach:**
1. Extract **drift types** (data, target, concept) and detection methods
2. Understand **reference vs test window** pattern
3. Surface **hypothesis testing methods** for drift detection
4. Note **alerting threshold guidance**

Present synthesized insights:
"Here's what the knowledge base tells us about production monitoring..."

**Key Pattern to Surface:**
> Drifts are proxy metrics that detect production model issues WITHOUT ground truth labels. Monitor changes in input distribution (data drift), output distribution (target drift), and input-output relationship (concept drift).

**Key Methodology to Surface:**
> Drift detection requires: (1) Reference window - baseline from training, (2) Test window - production data, (3) Hypothesis tests to compare distributions (KS test for numerical, chi-squared for categorical, MMD for multivariate).

### 3. Monitoring Strategy

**A. Observability Pillars**

| Pillar | What to Capture | Tools |
|--------|-----------------|-------|
| **Metrics** | Latency, throughput, errors | Prometheus, CloudWatch, Datadog |
| **Logs** | Requests, responses, errors | ELK, CloudWatch Logs, Loki |
| **Traces** | Request flow through system | Jaeger, X-Ray, Tempo |

**B. LLM-Specific Monitoring**

| Metric | Why Monitor | Alert Threshold |
|--------|-------------|-----------------|
| **Token Usage** | Cost control | > budget |
| **Response Length** | Quality signal | Unusual variance |
| **Latency by Query Type** | Performance | > SLA |
| **Error Rate** | Reliability | > baseline |
| **Cache Hit Rate** | Efficiency | < expected |
| **Guardrail Triggers** | Safety | Unexpected increase |

**C. RAG-Specific Monitoring (If Applicable)**

| Metric | Why Monitor | Alert Threshold |
|--------|-------------|-----------------|
| **Retrieval Latency** | Performance | > P99 target |
| **Empty Retrieval Rate** | Coverage | > 5% |
| **Context Utilization** | Efficiency | Very high/low |
| **Source Distribution** | Balance | Unexpected skew |
| **Reranking Score Distribution** | Quality | Degradation |

```yaml
monitoring:
  metrics:
    - name: "request_latency_p50"
      type: histogram
      alert_threshold: ">500ms"

    - name: "error_rate"
      type: counter
      alert_threshold: ">1%"

    - name: "token_usage_daily"
      type: gauge
      alert_threshold: ">budget"

    - name: "retrieval_empty_rate"
      type: gauge
      alert_threshold: ">5%"

  logging:
    level: INFO
    sample_rate: 0.1  # Log 10% of requests
    include_prompt: false  # Privacy
    include_response: false

  tracing:
    enabled: true
    sample_rate: 0.01
```

Ask: "What monitoring infrastructure do you have? What metrics are most critical for your use case?"

### 4. Drift Detection Strategy

**A. Types of Drift**

| Drift Type | What Changes | Detection Method | Response |
|------------|--------------|------------------|----------|
| **Data Drift** | Input distribution shifts | KS test, chi-squared | Investigate source |
| **Concept Drift** | Input-output relationship | Performance degradation | Retrain |
| **Target Drift** | Output distribution shifts | Distribution comparison | Investigate |

**Key Warning:**
> Data drift can result from natural real-life changes OR systemic problems (missing data, pipeline errors, schema modifications). Both need different responses.

**B. Detection Methodology**

1. **Establish Reference Window**: Baseline data from training/validation
2. **Establish Test Window**: Production data (sliding or tumbling)
3. **Apply Hypothesis Tests**: Compare distributions

| Data Type | Recommended Test |
|-----------|-----------------|
| **Numerical (univariate)** | Kolmogorov-Smirnov (KS) test |
| **Categorical** | Chi-squared test |
| **Text/Embeddings** | Maximum Mean Discrepancy (MMD) |

**C. Drift Configuration**

```yaml
drift_detection:
  reference_window:
    type: "training_data"
    path: "data/reference_embeddings.npy"

  test_window:
    type: "sliding"
    size_days: 7
    slide_days: 1

  tests:
    - name: "query_embedding_drift"
      type: "mmd"
      threshold: 0.05  # p-value

    - name: "response_length_drift"
      type: "ks"
      threshold: 0.05

    - name: "category_distribution_drift"
      type: "chi_squared"
      threshold: 0.05

  actions:
    on_drift_detected:
      - alert: "slack"
      - log: "drift_events"
      - investigate: "manual"
```

### 5. Alerting Configuration

**A. Alert Severity Levels**

| Level | Examples | Response Time | Notification |
|-------|----------|---------------|--------------|
| **Critical** | System down, data breach | Immediate | PagerDuty + Slack |
| **High** | Latency > 2x SLA, error > 5% | 15 min | Slack + Email |
| **Medium** | Drift detected, cost spike | 1 hour | Slack |
| **Low** | Performance degradation | Next day | Email digest |

**B. Alert Configuration**

```yaml
alerting:
  channels:
    - name: "pagerduty"
      type: "pagerduty"
      severity: ["critical"]

    - name: "slack-alerts"
      type: "slack"
      webhook: "${SLACK_WEBHOOK}"
      severity: ["critical", "high", "medium"]

    - name: "email-digest"
      type: "email"
      recipients: ["team@company.com"]
      severity: ["low"]
      frequency: "daily"

  alerts:
    - name: "high_error_rate"
      condition: "error_rate > 5%"
      severity: "high"
      message: "Error rate exceeded threshold"

    - name: "latency_degradation"
      condition: "p99_latency > 2000ms"
      severity: "high"
      message: "P99 latency exceeded SLA"

    - name: "drift_detected"
      condition: "drift_p_value < 0.05"
      severity: "medium"
      message: "Data drift detected in {feature}"

    - name: "cost_spike"
      condition: "daily_cost > budget * 1.5"
      severity: "medium"
      message: "Token usage exceeding budget"
```

### 6. Deployment Pipeline

**A. Deployment Strategy**

| Strategy | Description | Best For |
|----------|-------------|----------|
| **Blue-Green** | Two environments, instant switch | Zero-downtime updates |
| **Canary** | Gradual rollout with monitoring | Risk mitigation |
| **Rolling** | Incremental instance updates | Resource efficient |

**B. CI/CD Pipeline**

```yaml
pipeline:
  stages:
    - name: "test"
      steps:
        - unit_tests
        - integration_tests
        - evaluation_suite

    - name: "build"
      steps:
        - docker_build
        - push_to_registry

    - name: "deploy-staging"
      steps:
        - deploy_to_staging
        - smoke_tests
        - performance_tests

    - name: "deploy-production"
      strategy: "canary"
      steps:
        - deploy_canary_10_percent
        - monitor_30_minutes
        - gradual_rollout
        - full_deployment

  rollback:
    automatic: true
    trigger: "error_rate > 5%"
```

**C. Deployment Checklist**

```markdown
## Pre-Deployment
- [ ] All tests passing
- [ ] Evaluation metrics meet thresholds
- [ ] Documentation updated
- [ ] Rollback plan ready

## Deployment
- [ ] Canary deployed
- [ ] Metrics baseline established
- [ ] Alerts configured
- [ ] Team notified

## Post-Deployment
- [ ] Metrics within normal range
- [ ] No error spikes
- [ ] User feedback monitored
- [ ] Deployment logged
```

### 7. Incident Response Runbook

**A. Runbook Structure**

```markdown
# Incident Response Runbook

## Quick Reference
| Issue | Severity | First Response |
|-------|----------|----------------|
| System down | Critical | [link to procedure] |
| High error rate | High | [link to procedure] |
| Drift detected | Medium | [link to procedure] |

## Procedures

### PROC-001: High Error Rate

**Symptoms:** Error rate > 5%, user complaints

**Diagnosis:**
1. Check error logs: `kubectl logs -l app=llm-service`
2. Identify error type distribution
3. Check upstream dependencies

**Resolution:**
- If API rate limit: Enable request throttling
- If model timeout: Scale compute or optimize
- If data issue: Check data pipeline

**Escalation:**
- After 15 min: Page on-call engineer
- After 30 min: Escalate to team lead
```

**B. Common Procedures**

| Procedure | Trigger | Key Steps |
|-----------|---------|-----------|
| **Service Restart** | Unresponsive | Graceful shutdown, health check |
| **Rollback** | Bad deployment | Switch to previous version |
| **Scale Up** | High load | Add instances |
| **Cache Clear** | Stale data | Invalidate caches |
| **Model Rollback** | Quality drop | Revert to previous model |

### 8. Document Decisions

Once user confirms operations design, create specifications.

**Update sidecar.yaml:**
```yaml
currentStep: 9
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9]  # or without 5 if RAG-only
phases:
  phase_5_operations: "designed"
decisions:
  - id: "OPS-001"
    step: 9
    choice: "[monitoring strategy]"
    rationale: "[rationale]"
  - id: "OPS-002"
    step: 9
    choice: "[drift detection approach]"
    rationale: "[rationale]"
  - id: "OPS-003"
    step: 9
    choice: "[deployment strategy]"
    rationale: "[rationale]"
```

**Create operations-spec.md:**
```markdown
# Operations Specification

## Monitoring
### Metrics
| Metric | Type | Alert Threshold |
|--------|------|-----------------|
| [metric] | [type] | [threshold] |

### Logging
- Level: [level]
- Sample Rate: [rate]

### Tracing
- Enabled: [yes/no]
- Sample Rate: [rate]

## Drift Detection
### Reference Window
- Type: [type]
- Source: [source]

### Test Window
- Type: [type]
- Size: [size]

### Tests
| Feature | Test | Threshold |
|---------|------|-----------|
| [feature] | [test] | [threshold] |

## Alerting
| Alert | Condition | Severity | Channel |
|-------|-----------|----------|---------|
| [alert] | [condition] | [severity] | [channel] |

## Deployment
- Strategy: [strategy]
- Rollback Trigger: [condition]

## Runbook
See: runbook.md
```

**Create runbook.md with procedures.**

**Append to decision-log.md:**
```markdown
## OPS-001: Monitoring Strategy

**Decision:** [strategy]
**Date:** {date}
**Step:** 9 - MLOps Engineer

**Rationale:** [explanation]

---

## OPS-002: Drift Detection Approach

**Decision:** [approach]
**Date:** {date}
**Step:** 9 - MLOps Engineer

**Rationale:** [explanation]

---

## OPS-003: Deployment Strategy

**Decision:** [strategy]
**Date:** {date}
**Step:** 9 - MLOps Engineer

**Rationale:** [explanation]
```

### 9. Generate Operations Stories

Based on the operations design, generate implementation stories:

```yaml
stories:
  step_9_operations:
    - id: "OPS-S01"
      title: "Set up monitoring infrastructure"
      description: "Configure metrics, logging, and tracing"
      acceptance_criteria:
        - "Metrics collection working"
        - "Dashboards created"
        - "Log aggregation configured"
        - "Tracing enabled"

    - id: "OPS-S02"
      title: "Implement drift detection"
      description: "Build drift detection pipeline"
      acceptance_criteria:
        - "Reference window established"
        - "Test window configured"
        - "Hypothesis tests implemented"
        - "Alerts on drift working"

    - id: "OPS-S03"
      title: "Configure alerting"
      description: "Set up alert channels and rules"
      acceptance_criteria:
        - "Alert channels configured"
        - "Alert rules defined"
        - "Escalation paths clear"
        - "Test alerts working"

    - id: "OPS-S04"
      title: "Build deployment pipeline"
      description: "Implement CI/CD with chosen strategy"
      acceptance_criteria:
        - "Pipeline stages working"
        - "Automated testing in place"
        - "Canary/blue-green working"
        - "Rollback tested"

    - id: "OPS-S05"
      title: "Create operational runbook"
      description: "Document incident response procedures"
      acceptance_criteria:
        - "Common procedures documented"
        - "Escalation paths defined"
        - "Runbook accessible to team"
        - "Procedures tested"
```

**Update sidecar with stories:**
```yaml
stories:
  step_9_operations:
    - "[story list based on operations design]"
```

### 10. Present MENU OPTIONS

Display: **Step 9 Complete - Select an Option:** [A] Analyze operations further [P] View progress [C] Continue to Step 10 (Tech Lead Review)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit operations decisions, allow refinement, then redisplay menu
- IF P: Show operations-spec.md, runbook.md, and decision-log.md summaries, then redisplay menu
- IF C:
  1. Verify sidecar is updated with operations decisions and stories
  2. Load, read entire file, then execute `{nextStepFile}` (Tech Lead)
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND operations are documented AND runbook is created AND stories are generated, will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Step 10: Tech Lead Review.

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

- Knowledge MCP queried for drift detection and monitoring
- Monitoring strategy designed with key metrics
- Drift detection configured with appropriate tests
- Alerting configured with severity levels
- Deployment pipeline designed
- Runbook created with procedures
- operations-spec.md created
- runbook.md created
- decision-log.md updated with OPS decisions
- Stories generated for operations implementation
- User confirmed design before proceeding

### SYSTEM FAILURE:

- Making operations decisions without user input
- Skipping Knowledge MCP queries
- Not configuring drift detection
- Not creating runbook
- Proceeding without confirmed design
- Not generating implementation stories

**Master Rule:** Operations are what keep the system running. Skipping or rushing operations design is FORBIDDEN and constitutes SYSTEM FAILURE.
