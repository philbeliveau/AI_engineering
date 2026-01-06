---
name: 'step-07-operations-and-complete'
description: 'Phase 5: Operations and Workflow Completion - monitoring, drift detection, runbook, and finalization'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/ai-engineering-workflow'

# File References
thisStepFile: '{workflow_path}/steps/step-07-operations-and-complete.md'
workflowFile: '{workflow_path}/workflow.md'

# Output References
outputFolder: '{output_folder}/{project_name}'
sidecarFile: '{outputFolder}/sidecar.yaml'
projectSpecFile: '{outputFolder}/project-spec.md'
decisionLogFile: '{outputFolder}/decision-log.md'
operationsFolder: '{outputFolder}/phase-5-operations'
runbookFile: '{operationsFolder}/runbook.md'
alertsConfigTemplate: '{operationsFolder}/templates/alerts-config.template.yaml'
---

# Step 7: Phase 5 - Operations and Workflow Completion

## STEP GOAL:

To design production operations including monitoring, drift detection, alerting, and incident response - then finalize and complete the workflow with a comprehensive project summary.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 This is the FINAL step - completion requires explicit confirmation
- 📋 YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- ✅ You are an AI Engineering Architect
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring FTI pipeline expertise backed by the Knowledge MCP
- ✅ User brings their domain requirements and constraints
- ✅ Maintain collaborative, technical tone throughout

### Step-Specific Rules:

- 🎯 Focus on operations and completion
- 🚫 FORBIDDEN to revisit design decisions (those are locked)
- 💬 This phase produces operational artifacts
- 🧠 Query Knowledge MCP for drift detection methodologies

## EXECUTION PROTOCOLS:

- 🎯 Show your reasoning before making recommendations
- 💾 Update sidecar to mark workflow complete
- 📖 Create runbook and operational templates
- ✅ Provide comprehensive completion summary

## CONTEXT BOUNDARIES:

- Quality Gate has been passed (GO or CONDITIONAL)
- All design phases are complete
- This phase is about OPERATING the designed system
- Completion marks the end of the design workflow

## OPERATIONS SEQUENCE:

### 1. Welcome to Phase 5

Present the phase introduction:

"**Phase 5: Operations - Keeping Your System Healthy**

Congratulations on passing the Quality Gate! Now we need to ensure your system stays healthy in production.

**This Phase Covers:**
1. Monitoring and observability setup
2. Drift detection strategy
3. Alerting configuration
4. Incident response runbook
5. Continuous improvement plan

Then we'll complete the workflow with a full project summary."

### 2. Query Knowledge MCP for Methodologies

**Query 1: Drift Detection**
```
Endpoint: get_methodologies
Topic: drift detection
```

**Query 2: MLOps Practices**
```
Endpoint: get_methodologies
Topic: MLOps monitoring
```

**Query 3: Operations Warnings**
```
Endpoint: get_warnings
Topic: production ML
```

Present relevant methodologies and warnings to user.

### 3. Monitoring Strategy

**A. Observability Pillars**

| Pillar | What to Capture | Tools |
|--------|-----------------|-------|
| **Metrics** | Latency, throughput, errors | Prometheus, CloudWatch |
| **Logs** | Requests, responses, errors | ELK, CloudWatch Logs |
| **Traces** | Request flow through system | Jaeger, X-Ray |

**B. LLM-Specific Monitoring**

| Metric | Why Monitor | Alert Threshold |
|--------|-------------|-----------------|
| **Token Usage** | Cost control | > budget |
| **Response Length** | Quality signal | Unusual variance |
| **Latency by Query Type** | Performance | > SLA |
| **Error Rate** | Reliability | > baseline |
| **Cache Hit Rate** | Efficiency | < expected |

**C. RAG-Specific Monitoring (If Applicable)**

| Metric | Why Monitor | Alert Threshold |
|--------|-------------|-----------------|
| **Retrieval Latency** | Performance | > P99 target |
| **Empty Retrieval Rate** | Coverage | > 5% |
| **Context Utilization** | Efficiency | Very high/low |
| **Source Distribution** | Balance | Unexpected skew |

**Recommended Tool (from Knowledge Base):** Opik
- Purpose-built for LLM/prompt monitoring
- Tracks prompt performance over time
- Integrates with common LLM frameworks

Ask: "What monitoring infrastructure do you have? What metrics are most critical for your use case?"

### 4. Drift Detection Strategy

**Query Knowledge MCP:**
```
Endpoint: get_methodologies
Topic: data drift
```

**A. Types of Drift**

| Drift Type | What Changes | Detection Method |
|------------|--------------|------------------|
| **Data Drift** | Input distribution shifts | Statistical tests on inputs |
| **Concept Drift** | Relationship between input/output changes | Performance degradation |
| **Model Drift** | Model behavior changes over time | Output distribution analysis |
| **Label Drift** | Ground truth distribution changes | Label monitoring |

**B. Detection Approaches**

| Approach | Complexity | Effectiveness |
|----------|------------|---------------|
| **Statistical Tests** | Low | Good for numerical features |
| **Embedding Similarity** | Medium | Good for text inputs |
| **Performance Monitoring** | Low | Catches all drift types |
| **Reference Window Comparison** | Medium | Comprehensive |

**C. Response Actions**

| Severity | Trigger | Action |
|----------|---------|--------|
| **Low** | Minor distribution shift | Log and monitor |
| **Medium** | Performance degradation | Alert team, investigate |
| **High** | Significant quality drop | Alert + consider rollback |
| **Critical** | Safety issue detected | Automatic rollback |

Ask: "How quickly do you expect your data/domain to change? What drift detection approach fits your resources?"

### 5. Alerting Configuration

**A. Alert Categories**

| Category | Examples | Severity |
|----------|----------|----------|
| **Availability** | Service down, high error rate | Critical |
| **Performance** | Latency spike, throughput drop | High |
| **Quality** | Accuracy drop, drift detected | Medium |
| **Cost** | Budget threshold exceeded | Medium |
| **Security** | Unusual access patterns | High |

**B. Alert Design Principles**

| Principle | Description |
|-----------|-------------|
| **Actionable** | Every alert should have a clear response |
| **Prioritized** | Severity levels matter |
| **Deduplicated** | Avoid alert storms |
| **Contextual** | Include relevant information |
| **Tested** | Verify alerts fire correctly |

**C. Alert Configuration Template**

```yaml
alerts:
  - name: "High Error Rate"
    condition: "error_rate > 0.05 for 5m"
    severity: critical
    channel: pagerduty
    runbook: "#error-rate-high"

  - name: "Latency SLA Breach"
    condition: "p99_latency > 5s for 10m"
    severity: high
    channel: slack
    runbook: "#latency-high"

  - name: "Drift Detected"
    condition: "drift_score > 0.3"
    severity: medium
    channel: slack
    runbook: "#drift-detected"
```

Ask: "What alerting channels do you use? Who should be notified for different severity levels?"

### 6. Incident Response

**A. Incident Levels**

| Level | Description | Response Time | Responders |
|-------|-------------|---------------|------------|
| **P1 - Critical** | Service down, data breach | < 15 min | On-call + escalation |
| **P2 - High** | Degraded service, quality issues | < 1 hour | On-call |
| **P3 - Medium** | Minor issues, drift detected | < 4 hours | Next business day OK |
| **P4 - Low** | Improvements, non-urgent | Best effort | Backlog |

**B. Response Workflow**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Detect    │────▶│   Triage    │────▶│  Respond    │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Learn     │◀────│   Review    │◀────│   Resolve   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 7. Create Runbook

**Create runbook.md in phase-5-operations/:**

```markdown
# {project_name} Operations Runbook

## System Overview

**Architecture:** {architecture}
**Key Components:**
- [Component 1]: [Purpose]
- [Component 2]: [Purpose]
- [Component 3]: [Purpose]

**Dependencies:**
- [Dependency 1]: [What breaks if unavailable]
- [Dependency 2]: [What breaks if unavailable]

---

## Health Checks

### Service Health
- **Endpoint:** `/health`
- **Expected Response:** `{"status": "healthy"}`
- **Check Frequency:** Every 30 seconds

### Component Health
| Component | Health Check | Expected State |
|-----------|--------------|----------------|
| API | [Check] | [State] |
| Vector DB | [Check] | [State] |
| Cache | [Check] | [State] |
| LLM Provider | [Check] | [State] |

---

## Common Issues and Resolutions

### High Error Rate {#error-rate-high}

**Symptoms:**
- Error rate > 5%
- Users reporting failures

**Diagnosis Steps:**
1. Check error logs: `[command]`
2. Identify error pattern
3. Check dependent services

**Resolution:**
- If LLM provider issue: [steps]
- If vector DB issue: [steps]
- If code issue: [steps]

**Escalation:** If unresolved in 30 minutes, escalate to [team/person]

---

### High Latency {#latency-high}

**Symptoms:**
- P99 latency > 5s
- User complaints about slowness

**Diagnosis Steps:**
1. Check component latencies
2. Identify bottleneck
3. Check for traffic spike

**Resolution:**
- If retrieval slow: [steps]
- If LLM slow: [steps]
- If traffic spike: [steps]

---

### Drift Detected {#drift-detected}

**Symptoms:**
- Drift alert fired
- Quality metrics degrading

**Diagnosis Steps:**
1. Review drift metrics
2. Identify drift type (data/concept/model)
3. Analyze recent changes

**Resolution:**
- If data drift: [steps]
- If concept drift: [steps]
- Schedule retraining if needed

---

### Vector DB Issues {#vector-db-issues}

**Symptoms:**
- Retrieval failures
- Empty results

**Diagnosis Steps:**
1. Check Qdrant health
2. Verify collection exists
3. Check index status

**Resolution:**
- If connection issue: [steps]
- If index corrupted: [steps]
- If collection missing: [steps]

---

## Rollback Procedures

### Full Rollback

**When to Use:** Critical production issue

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. Verify rollback successful
5. Notify stakeholders

### Partial Rollback (Feature Flag)

**When to Use:** Issue with specific feature

**Steps:**
1. Disable feature flag: [command]
2. Verify feature disabled
3. Monitor for resolution

---

## Maintenance Procedures

### Scheduled Maintenance

**Pre-Maintenance:**
1. Notify users [X hours] in advance
2. Prepare rollback plan
3. Schedule maintenance window

**During Maintenance:**
1. Enable maintenance mode
2. Perform updates
3. Run health checks
4. Disable maintenance mode

**Post-Maintenance:**
1. Monitor for issues
2. Confirm all services healthy
3. Send completion notification

### Index Rebuilding

**When Needed:** After embedding model change, corruption

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Contacts

| Role | Name | Contact |
|------|------|---------|
| On-Call | [Name] | [Contact] |
| Escalation | [Name] | [Contact] |
| LLM Provider Support | [Provider] | [Contact] |

---

## Appendix

### Useful Commands

```bash
# Check service status
[command]

# View recent logs
[command]

# Check vector DB health
[command]

# Force cache clear
[command]
```

### Key Metrics Dashboard

**Location:** [Dashboard URL]

**Key Panels:**
- Request rate and errors
- Latency percentiles
- Token usage
- Drift scores
```

### 8. Generate Alerts Config Template

**alerts-config.template.yaml:**
```yaml
# Alerts Configuration
# Decision reference: See decision-log.md#OP-xxx

# Alert Defaults
defaults:
  notification_channels:
    critical: ["{{PAGERDUTY_CHANNEL}}"]
    high: ["{{SLACK_CHANNEL}}", "{{EMAIL_GROUP}}"]
    medium: ["{{SLACK_CHANNEL}}"]
    low: ["{{SLACK_CHANNEL}}"]

# Availability Alerts
availability:
  - name: "Service Down"
    condition: "up == 0"
    duration: "1m"
    severity: critical
    runbook_url: "{{RUNBOOK_URL}}#service-down"

  - name: "High Error Rate"
    condition: "error_rate > {{ERROR_THRESHOLD}}"
    duration: "5m"
    severity: critical
    runbook_url: "{{RUNBOOK_URL}}#error-rate-high"

# Performance Alerts
performance:
  - name: "Latency P99 High"
    condition: "latency_p99 > {{LATENCY_P99_THRESHOLD}}"
    duration: "10m"
    severity: high
    runbook_url: "{{RUNBOOK_URL}}#latency-high"

  - name: "Throughput Drop"
    condition: "throughput < {{MIN_THROUGHPUT}}"
    duration: "15m"
    severity: medium
    runbook_url: "{{RUNBOOK_URL}}#throughput-low"

# Quality Alerts
quality:
  - name: "Data Drift Detected"
    condition: "drift_score > {{DRIFT_THRESHOLD}}"
    duration: "1h"
    severity: medium
    runbook_url: "{{RUNBOOK_URL}}#drift-detected"

  - name: "Quality Score Drop"
    condition: "quality_score < {{MIN_QUALITY}}"
    duration: "1h"
    severity: high
    runbook_url: "{{RUNBOOK_URL}}#quality-drop"

# Cost Alerts
cost:
  - name: "Token Budget Warning"
    condition: "daily_tokens > {{TOKEN_WARNING_THRESHOLD}}"
    duration: "1h"
    severity: medium
    runbook_url: "{{RUNBOOK_URL}}#cost-warning"

  - name: "Token Budget Critical"
    condition: "daily_tokens > {{TOKEN_CRITICAL_THRESHOLD}}"
    duration: "30m"
    severity: high
    runbook_url: "{{RUNBOOK_URL}}#cost-critical"

# RAG-Specific Alerts (if applicable)
rag:
  - name: "Empty Retrieval Rate High"
    condition: "empty_retrieval_rate > {{EMPTY_RETRIEVAL_THRESHOLD}}"
    duration: "30m"
    severity: medium
    runbook_url: "{{RUNBOOK_URL}}#empty-retrieval"

  - name: "Vector DB Latency High"
    condition: "vector_db_latency_p99 > {{VECTOR_LATENCY_THRESHOLD}}"
    duration: "10m"
    severity: high
    runbook_url: "{{RUNBOOK_URL}}#vector-db-issues"
```

### 9. Continuous Improvement Plan

"Operations isn't just maintenance - it's continuous improvement."

**A. Feedback Loops**

| Loop | Frequency | Purpose |
|------|-----------|---------|
| **User Feedback** | Continuous | Direct quality signal |
| **Performance Review** | Weekly | Trend analysis |
| **Model Evaluation** | Monthly | Quality benchmarking |
| **Architecture Review** | Quarterly | System evolution |

**B. Improvement Triggers**

| Trigger | Action |
|---------|--------|
| Consistent quality complaints | Investigate and improve |
| New data sources available | Consider ingestion |
| Cost exceeds budget | Optimize or scale down |
| New model releases | Evaluate upgrade |
| Drift detected | Plan retraining or update |

Ask: "How do you want to structure continuous improvement? What's realistic for your team?"

### 10. Update Project Files

**Update sidecar.yaml:**
```yaml
currentPhase: 5
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]  # All steps complete
workflow_status: "complete"
completed_date: "{date}"
decisions:
  # ... previous decisions ...
  - id: "op-001"
    choice: "[monitoring approach]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_methodologies:mlops-monitoring"
  - id: "op-002"
    choice: "[drift detection approach]"
    rationale: "[brief rationale]"
    knowledge_ref: "get_methodologies:drift-detection"
phases:
  phase_5_operations: "complete"
```

**Append to decision-log.md:** (operations decisions)

**Update project-spec.md:** (add Operations section)

### 11. Workflow Completion Summary

Present the completion summary:

"**🎉 Workflow Complete: {project_name}**

Congratulations! You've completed the AI Engineering Workflow for **{project_name}**.

---

## Project Summary

**Architecture:** {architecture}
**Phases Completed:** All 5 phases (0-5)
**Quality Gate:** {gate_decision}

### Phase Outputs

| Phase | Output | Status |
|-------|--------|--------|
| Phase 0: Scoping | `architecture-decision.md` | ✅ Complete |
| Phase 1: Feature | `spec.md` + config templates | ✅ Complete |
| Phase 2: Training | `spec.md` + config template | ✅ Complete / Skipped |
| Phase 3: Inference | `spec.md` + deployment config | ✅ Complete |
| Phase 4: Evaluation | `report.md` + quality gate | ✅ Complete |
| Phase 5: Operations | `runbook.md` + alerts config | ✅ Complete |

### Key Decisions Made

[List top 5-7 decisions from decision-log.md]

### Next Steps

1. **Implement** the designed system using the specs and templates
2. **Test** according to the evaluation plan
3. **Deploy** following the deployment configuration
4. **Operate** using the runbook and monitoring setup
5. **Iterate** based on feedback and drift detection

---

## Project Artifacts Location

```
{outputFolder}/
├── sidecar.yaml              ← State tracking
├── project-spec.md           ← Complete specification
├── decision-log.md           ← All decisions + rationale
├── phase-0-scoping/
│   └── architecture-decision.md
├── phase-1-feature/
│   ├── spec.md
│   └── templates/
├── phase-2-training/
│   ├── spec.md (or SKIPPED note)
│   └── templates/
├── phase-3-inference/
│   ├── spec.md
│   └── templates/
├── phase-4-evaluation/
│   ├── report.md
│   └── checklists/
└── phase-5-operations/
    ├── runbook.md
    └── templates/
```

---

**Thank you for using the AI Engineering Workflow!**

Your project is now fully designed and ready for implementation."

### 12. Present FINAL MENU

Display: **Workflow Complete - Select an Option:** [S] View full summary [D] Review all decisions [E] Export project [X] Exit workflow

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- This is the FINAL step - no next step to load
- User can review or export before closing

#### Menu Handling Logic:

- IF S: Show complete project-spec.md
- IF D: Show complete decision-log.md
- IF E: Provide guidance on exporting/sharing artifacts
- IF X: Confirm completion and close
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

This is the FINAL step. When user selects 'X' (Exit), confirm completion and close the workflow session.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Knowledge MCP queried for operations methodologies
- Monitoring strategy defined
- Drift detection approach selected
- Alerting configured
- Runbook created with common issues
- Alerts config template generated
- Comprehensive completion summary provided
- All project artifacts finalized
- Sidecar marked as complete

### ❌ SYSTEM FAILURE:

- Making decisions without user input
- Skipping Knowledge MCP queries
- Not creating runbook
- Not generating alerts config
- Not providing completion summary
- Not marking workflow as complete
- Revisiting design decisions (those are locked)

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
