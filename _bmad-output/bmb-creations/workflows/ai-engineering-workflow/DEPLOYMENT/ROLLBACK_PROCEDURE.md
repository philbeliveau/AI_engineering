# AI Engineering Workflow - Rollback Procedure

**Document Purpose:** Emergency rollback procedures for AI Engineering Workflow v2.0.0
**Effective Date:** Upon deployment of v2.0.0
**Authority:** Tech Lead or Infrastructure Lead
**Estimated Rollback Time:** 15-30 minutes (fully automatic)
**Post-Rollback Verification:** 30 minutes

---

## Executive Summary

This document provides procedures to quickly roll back from AI Engineering Workflow v2.0.0 to v1.0.0 if critical issues are discovered in production.

**Rollback is appropriate when:**
- Critical functionality is broken (workflow cannot execute)
- Multiple users cannot complete tasks
- Knowledge MCP integration is severely degraded (> 10% error rate)
- Security issue discovered
- Data corruption suspected
- Performance degradation exceeds 50%

**Rollback is NOT appropriate for:**
- Minor bugs with workarounds
- Single-user issues
- Feature requests
- Non-critical performance issues

---

## Pre-Rollback Checklist

### Decision Authority
**Only the following can authorize rollback:**
- [ ] Tech Lead (primary)
- [ ] Infrastructure Lead (if Tech Lead unavailable)
- [ ] Senior Engineer on-call (if both above unavailable)

**Decision Documentation:**
```
Rollback Authorization Form:
- Authorized by: [Name and role]
- Time authorized: [HH:MM UTC]
- Critical issue: [Description, max 200 chars]
- User impact: [Count of affected users]
- Data impact: [None / Data loss possible / Data loss likely]
- Severity: [Critical / Major / Other]
```

### Impact Assessment
**Complete before proceeding:**
- [ ] Identify number of users affected
- [ ] Identify time since last backup
- [ ] Identify any data created since deployment
- [ ] Determine if data loss is acceptable
- [ ] Assess customer impact
- [ ] Plan post-rollback communication

---

## Rollback Triggers

### Automatic Rollback Triggers
The following issues automatically trigger rollback consideration:

**Tier 1: Automatic Rollback (Execute within 5 minutes)**
- [ ] Workflow execution failure rate > 20% (continuous)
- [ ] Knowledge MCP completely unavailable (> 15 min)
- [ ] All users unable to start Step 1
- [ ] Critical security vulnerability discovered
- [ ] Database corruption detected

**Tier 2: Escalated Review (Discuss with Tech Lead)**
- [ ] Workflow execution failure rate 10-20%
- [ ] Knowledge MCP error rate > 5%
- [ ] Multiple users (> 5) with blocking issues
- [ ] Performance degradation > 30%
- [ ] Data integrity warnings in logs

**Tier 3: Monitor and Fix (Attempt hotfix first)**
- [ ] Workflow execution failure rate 5-10%
- [ ] Knowledge MCP error rate 2-5%
- [ ] Single user or small group affected
- [ ] Performance degradation 10-30%
- [ ] Non-critical features affected

### Manual Rollback Authorization
Tech Lead can authorize rollback for:
- Undiscovered critical bugs
- Integration failures not caught in testing
- Infrastructure incompatibilities
- Third-party dependency failures
- Regulatory/compliance issues

---

## Quick Start: Emergency Rollback (5 minutes)

If you need to roll back immediately due to critical issue:

```bash
# 1. STOP all running workflow instances
# (Users will see "workflow paused" message)

# 2. ALERT: Notify on-call infrastructure team immediately
# Phone: [On-call number]
# Slack: @infrastructure-oncall

# 3. EXECUTE rollback commands:
cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/bmb-creations/workflows/ai-engineering-workflow

# Backup current (broken) version
tar -czf /backups/ai-engineering-workflow-v2.0.0-broken-$(date +%s).tar.gz \
  agents/ steps/ templates/ config.yaml

# Restore previous version from backup
tar -xzf /backups/ai-engineering-workflow-v1.0.0-backup-latest.tar.gz

# Verify restoration
./validate-workflow.sh

# 4. NOTIFY users
# Message: "AI Engineering Workflow v1.0.0 restored. v2.0.0 rollback in progress."

# 5. VERIFY basic functionality
# - Can start Step 1? Yes/No
# - Can access Knowledge MCP? Yes/No
# - No errors in logs? Yes/No

# 6. CONFIRM rollback complete
echo "Rollback to v1.0.0 COMPLETE at $(date)" >> /logs/rollback.log
```

**This takes approximately 5 minutes**

---

## Detailed Rollback Procedure

### Phase 1: Decision and Preparation (5 minutes)

#### Step 1.1: Alert the Team
```
1. Send urgent Slack message:
   "@infrastructure-oncall CRITICAL ISSUE DETECTED
    v2.0.0 rollback may be needed
    Issue: [Brief description]
    Authorized by: [Name]
    Time: [HH:MM UTC]"

2. Call on-call infrastructure engineer
   Phone: [Number]
   Message: "Critical issue with v2.0.0, rollback authorization granted"

3. Send email to stakeholders:
   To: tech-lead@, pm@, infrastructure@
   Subject: "URGENT: AI Workflow v2.0.0 Rollback in Progress"
   Body: "Issue detected, rolling back to v1.0.0. ETA 30 min."
```

#### Step 1.2: Capture Diagnostic Information
```bash
# BEFORE rolling back, capture state for post-mortem
mkdir -p /diagnostics/rollback-$(date +%Y%m%d-%H%M%S)

# Capture system metrics
vmstat 1 30 > /diagnostics/rollback-*/vmstat.txt
iostat 1 30 > /diagnostics/rollback-*/iostat.txt
top -b -n 10 > /diagnostics/rollback-*/top.txt

# Capture logs
cp /var/log/workflow/* /diagnostics/rollback-*/ 2>/dev/null || true
journalctl -n 1000 > /diagnostics/rollback-*/journal.log

# Capture error logs from all agents
find /Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/ai-projects \
  -name "*.log" -type f \
  -exec cp {} /diagnostics/rollback-*/ \; 2>/dev/null || true

# Document current version info
echo "Current Version: $(grep "version:" config.yaml)" > /diagnostics/rollback-*/version.txt
ls -la agents/ steps/ templates/ > /diagnostics/rollback-*/file-manifest.txt
```

#### Step 1.3: Identify Backup to Restore
```bash
# List available backups (from pre-deployment preparation)
ls -lh /backups/ai-engineering-workflow-v1.0.0-backup-*.tar.gz

# Identify most recent v1.0.0 backup
BACKUP_FILE=$(ls -t /backups/ai-engineering-workflow-v1.0.0-backup-*.tar.gz | head -1)
echo "Backup to restore: $BACKUP_FILE"
echo "Backup size: $(du -h $BACKUP_FILE)"
echo "Backup date: $(stat -f %Sm -t '%Y-%m-%d %H:%M:%S' $BACKUP_FILE)"

# Verify backup integrity
tar -tzf $BACKUP_FILE > /dev/null 2>&1 && echo "✓ Backup valid" || echo "✗ Backup corrupted!"

# If backup corrupted, use git history
git log --oneline | grep "v1.0.0"
```

### Phase 2: Execution (10 minutes)

#### Step 2.1: Stop All Workflow Processes
```bash
# Find and kill all running workflow processes
pkill -f "claude.*ai-engineering" || true
pkill -f "step-0[0-9]" || true
pkill -f "step-[0-9][0-9]" || true

# Wait for graceful shutdown
sleep 10

# Verify all processes stopped
ps aux | grep -i "workflow\|step-0" | grep -v grep
# Expected: No results

# Log the stop action
echo "Workflow processes stopped at $(date)" >> /logs/rollback.log
```

#### Step 2.2: Backup Current (Broken) Version
```bash
# Create timestamped backup of broken version
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BROKEN_BACKUP="/backups/ai-engineering-workflow-v2.0.0-broken-${TIMESTAMP}.tar.gz"

cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/bmb-creations/workflows/ai-engineering-workflow

tar --exclude='.git' \
    --exclude='_deprecated' \
    --exclude='node_modules' \
    -czf $BROKEN_BACKUP \
    agents/ steps/ templates/ config.yaml checklists/ DEPLOYMENT/ *.md

# Verify backup created
ls -lh $BROKEN_BACKUP
echo "Broken version backed up: $BROKEN_BACKUP" >> /logs/rollback.log

# Document all files in backup (for post-mortem)
tar -tzf $BROKEN_BACKUP | sort > /diagnostics/rollback-${TIMESTAMP}/v2.0.0-files.txt
```

#### Step 2.3: Restore v1.0.0 from Backup
```bash
# Get backup location
BACKUP_FILE=$(ls -t /backups/ai-engineering-workflow-v1.0.0-backup-*.tar.gz | head -1)

# Change to workflow directory
cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/bmb-creations/workflows/ai-engineering-workflow

# Remove broken version (but keep git history)
rm -rf agents/ steps/ templates/ config.yaml checklists/

# Extract v1.0.0 backup
echo "Restoring from $BACKUP_FILE..."
tar -xzf $BACKUP_FILE

# Verify critical files restored
echo "Verifying restoration..."
test -f config.yaml && echo "✓ config.yaml restored" || echo "✗ config.yaml missing!"
test -d agents && echo "✓ agents/ restored" || echo "✗ agents/ missing!"
test -d steps && echo "✓ steps/ restored" || echo "✗ steps/ missing!"
test -f workflow.md && echo "✓ workflow.md restored" || echo "✗ workflow.md missing!"

echo "Restoration completed at $(date)" >> /logs/rollback.log
```

#### Step 2.4: Validate Restored Version
```bash
# 1. Check syntax of critical files
cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/bmb-creations/workflows/ai-engineering-workflow

echo "Validating YAML syntax..."
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" && \
  echo "✓ config.yaml valid" || \
  echo "✗ config.yaml invalid!"

# 2. Verify all step files exist
echo "Checking step files..."
for step in steps/0-scoping/step-01-*.md \
            steps/0-scoping/step-02a-*.md \
            steps/0-scoping/step-02b-*.md \
            steps/1-feature/step-03a-*.md \
            steps/1-feature/step-03b-*.md \
            steps/1-feature/step-04-*.md \
            steps/2-training/step-05-*.md \
            steps/3-inference/step-06-*.md \
            steps/3-inference/step-07-*.md \
            steps/4-evaluation/step-08-*.md \
            steps/5-operations/step-09-*.md \
            steps/6-integration/step-10-*.md \
            steps/6-integration/step-11-*.md; do
  test -f "$step" && echo "✓ $(basename $step)" || echo "✗ $(basename $step) missing!"
done

# 3. Verify all agents present
echo "Checking agent files..."
for agent in business-analyst.md fti-architect.md data-engineer.md \
             embeddings-engineer.md fine-tuning-specialist.md \
             rag-specialist.md prompt-engineer.md llm-evaluator.md \
             mlops-engineer.md tech-lead.md dev.md; do
  test -f "agents/$agent" && echo "✓ $agent" || echo "✗ $agent missing!"
done

# 4. Verify version is v1.0.0
echo "Checking version..."
VERSION=$(grep "version:" config.yaml | head -1 | awk '{print $2}')
if [ "$VERSION" = '"1.0.0"' ]; then
  echo "✓ Version v1.0.0 confirmed"
else
  echo "✗ Version mismatch! Found: $VERSION"
fi

echo "Validation completed at $(date)" >> /logs/rollback.log
```

#### Step 2.5: Verify Knowledge MCP Connectivity
```bash
# Test Knowledge MCP is accessible from restored version
echo "Testing Knowledge MCP connectivity..."

curl -s -w "%{http_code}" \
  https://knowledge-mcp-production.up.railway.app/health \
  -o /dev/null && echo "✓ Knowledge MCP accessible" || \
  echo "✗ Knowledge MCP connection failed"

# If Knowledge MCP not responding, this is critical
# Contact infrastructure team immediately
```

#### Step 2.6: Start Restored Workflow
```bash
# Restart workflow processes
echo "Starting restored workflow..."

# (Specific startup commands depend on your deployment method)
# Example for systemd:
# systemctl restart ai-workflow

# Example for Docker:
# docker-compose restart ai-engineering-workflow

# Example for manual:
# background workflow startup process

echo "Workflow restart initiated at $(date)" >> /logs/rollback.log

# Wait for startup
sleep 15

# Verify processes are running
ps aux | grep -i "workflow" | grep -v grep
echo "Workflow status verified at $(date)" >> /logs/rollback.log
```

### Phase 3: Verification (10 minutes)

#### Step 3.1: Smoke Testing
```bash
# Test 1: Can Step 1 (Business Analyst) execute?
echo "Test 1: Step 1 executability..."
# Run a test instance
# Expected: Can load step-01-business-analyst.md without errors

# Test 2: Can Knowledge MCP be queried?
echo "Test 2: Knowledge MCP queries..."
# Query: "RAG architecture patterns"
# Expected: Results returned in < 2 seconds

# Test 3: Can agents load their personas?
echo "Test 3: Agent loading..."
# Load business-analyst agent
# Expected: Agent persona loads without errors

# Test 4: Can config be parsed?
echo "Test 4: Config parsing..."
# Parse config.yaml
# Expected: All paths resolve correctly

# Document smoke test results
echo "Smoke testing completed at $(date)" >> /logs/rollback.log
cat > /logs/smoke-test-results.txt << EOF
Test 1 (Step 1): PASS/FAIL
Test 2 (Knowledge MCP): PASS/FAIL
Test 3 (Agent Loading): PASS/FAIL
Test 4 (Config Parsing): PASS/FAIL
Overall: PASS/FAIL
EOF
```

#### Step 3.2: Functional Testing
```bash
# Test: Run a sample workflow from start to completion
echo "Functional test: Complete workflow..."

# Create test project with sample requirements
# Run through all 11 steps (or until first error)
# Expected: All steps execute successfully

# Time execution
START_TIME=$(date +%s)
# ... run workflow ...
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "Functional test completed in $DURATION seconds" >> /logs/rollback.log
test $DURATION -lt 3600 && echo "✓ Performance acceptable" || \
  echo "✗ Performance degraded (took > 60 min)"
```

#### Step 3.3: User Communication
```bash
# Send all-clear message to users
cat > /tmp/rollback-complete-message.txt << 'EOF'
🟢 ROLLBACK COMPLETE - AI Engineering Workflow Restored

The AI Engineering Workflow has been successfully rolled back to version 1.0.0.

Details:
- Rollback Time: [HH:MM UTC]
- Rollback Duration: [X minutes]
- Root Cause: [Brief description]
- Impact: [No user data lost / Some recent data may not be available]

Action Items:
- All users can resume using the workflow immediately
- New projects should start fresh
- Existing projects from before rollback are available
- Post-mortem analysis will be conducted

Support: Contact [support email] with any issues

We apologize for the inconvenience.
EOF

# Send via email, Slack, in-app notification
```

### Phase 4: Root Cause Analysis (Post-Rollback, next 24 hours)

#### Step 4.1: Collect Evidence
```bash
# Save all diagnostic information
cp /diagnostics/rollback-*/* /archive/rollback-analysis-$(date +%Y%m%d)/

# Preserve broken v2.0.0 for analysis
# Already saved in: /backups/ai-engineering-workflow-v2.0.0-broken-*.tar.gz

# Document timeline of events
cat > /archive/rollback-timeline.md << 'EOF'
# Rollback Timeline

## Detection
- Time: [HH:MM UTC]
- Who: [Name]
- How: [Monitoring alert / User report / Automated test]

## Investigation
- Initial symptoms: [Description]
- Diagnostic steps taken: [List]
- Root cause identified: [Description]

## Authorization
- Authorized by: [Name, role]
- Time: [HH:MM UTC]

## Execution
- Rollback start: [HH:MM UTC]
- Rollback complete: [HH:MM UTC]
- Duration: [X minutes]

## Verification
- Smoke tests: [PASS/FAIL]
- Functional tests: [PASS/FAIL]
- Performance: [PASS/FAIL]

## Resolution
- Root cause analysis: [In progress / Complete]
- Fix development: [Not started / In progress / Complete]
- Redeployment plan: [Planned for [date]]
EOF
```

#### Step 4.2: Root Cause Analysis
```bash
# Compare v1.0.0 vs v2.0.0
diff -r /backups/ai-engineering-workflow-v1.0.0-backup-latest/ \
         /backups/ai-engineering-workflow-v2.0.0-broken-* \
         > /archive/rollback-analysis-*/differences.txt

# Analyze error patterns
grep -r "ERROR\|CRITICAL\|FAILED" /logs/ > /archive/rollback-analysis-*/errors.txt

# Review change logs
git log v1.0.0..v2.0.0 --oneline > /archive/rollback-analysis-*/changes.txt

# Identify which change(s) caused the issue
# Review: DEPLOYMENT_PLAN.md changes
# Review: Agent changes
# Review: Step changes
# Review: Config changes
```

#### Step 4.3: Post-Mortem Meeting
```markdown
# Rollback Post-Mortem Meeting

Scheduled: [Date/Time]
Participants: Tech Lead, PM, Infra Lead, QA Lead, affected engineers

Topics:
1. What happened? (Describe the issue)
2. Why did it happen? (Root cause)
3. How did we detect it? (Detection mechanism)
4. How did we respond? (Incident response)
5. What should we do differently? (Lessons learned)
6. What's the fix? (Resolution plan)
7. How do we prevent this? (Process improvements)

Action items:
- [ ] Fix developed and tested
- [ ] Code review completed
- [ ] Testing plan for redeployment
- [ ] Monitoring improvements
- [ ] Process improvements documented
```

---

## Re-Deployment After Rollback

### Timeline
```
Rollback: Day 0
Analysis & Fix: Day 0-1
Testing: Day 1-2
Redeployment: Day 2-3
Validation: Day 3+
```

### Steps to Redeployment
1. **Root Cause Analysis Complete**
   - Issue fully understood
   - Fix validated in development
   - All tests passing

2. **Testing & Validation**
   - Hotfix tested in staging
   - All 20+ test cases passing
   - Performance acceptable
   - No new issues introduced

3. **Stakeholder Review**
   - Tech Lead approves fix
   - QA Lead certifies testing
   - Product Manager approves deployment

4. **Deployment with Enhanced Monitoring**
   - Deploy v2.0.1 (hotfix version)
   - Enhanced monitoring enabled
   - Staged rollout (if possible)
   - 24-hour heightened monitoring

---

## Rollback Decision Tree

```
CRITICAL ISSUE DETECTED?
    │
    ├─→ YES, BLOCKING (Users cannot work)
    │   └─→ ROLLBACK IMMEDIATELY
    │       Authorize: Tech Lead (no approval needed if blocking)
    │       Duration: 15-30 minutes
    │
    ├─→ YES, SEVERE (Multiple users affected)
    │   ├─→ Can fix in < 1 hour?
    │   │   ├─→ YES: Attempt hotfix
    │   │   └─→ NO: ROLLBACK
    │   └─→ Authorize: Tech Lead + PM approval
    │
    ├─→ YES, MODERATE (Some users affected)
    │   ├─→ Can fix in < 2 hours?
    │   │   ├─→ YES: Attempt hotfix with degraded service
    │   │   └─→ NO: ROLLBACK
    │   └─→ Authorize: Tech Lead approval
    │
    ├─→ YES, MINOR (Few users, workaround exists)
    │   ├─→ Can fix in < 4 hours?
    │   │   ├─→ YES: Plan hotfix, provide workaround
    │   │   └─→ NO: Plan rollback for next maintenance window
    │   └─→ No immediate rollback needed
    │
    └─→ NO
        └─→ CONTINUE MONITORING
            Attempt fix without rollback
```

---

## Rollback Coordination Checklist

### Pre-Rollback (Completed before execution)
- [ ] Critical issue confirmed
- [ ] Backup verified (v1.0.0)
- [ ] Rollback authorized (by Tech Lead or Infrastructure Lead)
- [ ] Stakeholders notified
- [ ] All running workflows paused
- [ ] Diagnostic data collected

### During Rollback (Monitored in real-time)
- [ ] Current (broken) version backed up
- [ ] v1.0.0 restored from backup
- [ ] All files verified
- [ ] Syntax validation passed
- [ ] Services restarted
- [ ] Smoke tests passed

### Post-Rollback (Completed within 1 hour)
- [ ] Users notified of restoration
- [ ] All users can access workflow
- [ ] Knowledge MCP responding
- [ ] Performance acceptable
- [ ] No critical errors in logs
- [ ] Post-mortem scheduled

---

## Contact Information

| Role | Name | Phone | Email | Availability |
|------|------|-------|-------|--------------|
| **Tech Lead** | [Name] | [Phone] | [Email] | 24/7 |
| **Infrastructure Lead** | [Name] | [Phone] | [Email] | 24/7 |
| **On-Call Engineer** | [Rotating] | [Phone] | [Email] | 24/7 |
| **QA Lead** | [Name] | [Phone] | [Email] | Business hours |
| **Product Manager** | [Name] | [Phone] | [Email] | Business hours |

**Escalation Path:**
1. Contact on-call engineer immediately
2. If no response in 5 min, contact Tech Lead directly
3. If no response in 10 min, contact Infrastructure Lead
4. If still no response, authorize rollback yourself (if authorized personnel)

---

## Testing the Rollback Procedure

### When to Test
- Monthly (recommended)
- After any infrastructure changes
- Before high-risk deployments
- When team membership changes

### Testing Procedure
```bash
# 1. Set up test environment
mkdir -p /test-rollback/

# 2. Create test versions
cp -r workflow-v2.0.0 /test-rollback/
cp -r workflow-v1.0.0 /test-rollback/

# 3. Simulate the rollback
# Run through all steps in Rollback Procedure
# Time how long each step takes
# Document any issues

# 4. Measure success
# Total rollback time: [X minutes]
# All smoke tests passed? Yes/No
# All verification passed? Yes/No

# 5. Document results
# Store results in /test-rollback/results-YYYY-MM-DD.txt
```

---

## Appendix: Recovery Data

### Backup Locations
- **v1.0.0 Backups:** `/backups/ai-engineering-workflow-v1.0.0-backup-*.tar.gz`
- **v2.0.0 Broken Backup:** `/backups/ai-engineering-workflow-v2.0.0-broken-*.tar.gz`
- **Project Data:** `/Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/ai-projects/`

### Log Locations
- **Rollback Log:** `/logs/rollback.log`
- **Smoke Test Results:** `/logs/smoke-test-results.txt`
- **Workflow Logs:** `/var/log/workflow/`
- **Diagnostic Data:** `/diagnostics/rollback-*/`
- **Archive:** `/archive/rollback-analysis-*/`

### Git Recovery
```bash
# If needed, recover from git history
cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering

# Check out v1.0.0 tag
git checkout ai-engineering-workflow-v1.0.0

# Or see history
git log --oneline | grep "v1.0.0"

# Or revert specific commits
git revert <commit-hash>
```

---

**Document Version:** 2.0.0
**Last Updated:** January 6, 2026
**Next Review:** Upon v2.1.0 preparation or after first rollback

