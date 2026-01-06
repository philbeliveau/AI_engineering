# Quality Gate Checklist

**Project:** {{PROJECT_NAME}}
**Date:** {{DATE}}
**Reviewer:** {{REVIEWER}}

---

## Purpose

This checklist ensures deployment readiness before proceeding from Phase 4 (Evaluation) to Phase 5 (Operations). All critical items must be checked before approving the quality gate.

---

## Pre-Deployment Verification

### Functional Readiness

| Item | Status | Notes |
|------|--------|-------|
| [ ] All critical functional requirements met | | |
| [ ] Core use cases tested and working | | |
| [ ] Edge cases handled appropriately | | |
| [ ] Error messages are clear and helpful | | |
| [ ] No known critical bugs | | |
| [ ] Regression tests pass | | |

### Performance Readiness

| Item | Status | Notes |
|------|--------|-------|
| [ ] P50 latency target achieved | | Target: ___ms |
| [ ] P99 latency target achieved | | Target: ___ms |
| [ ] Throughput target achieved | | Target: ___req/min |
| [ ] System stable under expected load | | Tested: ___concurrent |
| [ ] Memory usage acceptable | | Max: ___MB |
| [ ] No memory leaks detected | | |

### Quality Readiness

| Item | Status | Notes |
|------|--------|-------|
| [ ] Accuracy meets target threshold | | Target: ___% |
| [ ] Relevance scores acceptable | | Target: ___% |
| [ ] Hallucination rate below threshold | | Max: ___% |
| [ ] RAG retrieval quality verified | | Recall@K: ___ |
| [ ] Response format consistent | | |
| [ ] Citation accuracy verified (if applicable) | | |

### Safety Readiness

| Item | Status | Notes |
|------|--------|-------|
| [ ] Safety testing completed | | |
| [ ] No critical safety issues identified | | |
| [ ] Harmful content filtering in place | | |
| [ ] Bias testing completed (if applicable) | | |
| [ ] PII handling verified | | |
| [ ] Jailbreak resistance tested | | |

### Operational Readiness

| Item | Status | Notes |
|------|--------|-------|
| [ ] Monitoring configured and tested | | |
| [ ] Alerting configured and tested | | |
| [ ] Logging adequate for debugging | | |
| [ ] Health check endpoints working | | |
| [ ] Rollback plan documented | | |
| [ ] Backup procedures in place | | |

### Documentation Readiness

| Item | Status | Notes |
|------|--------|-------|
| [ ] API documentation complete | | |
| [ ] User documentation complete | | |
| [ ] Runbook drafted | | |
| [ ] Architecture documented | | |
| [ ] Known limitations documented | | |

### Security Readiness

| Item | Status | Notes |
|------|--------|-------|
| [ ] Authentication configured | | Method: ___ |
| [ ] Authorization rules in place | | |
| [ ] Rate limiting configured | | Limit: ___/min |
| [ ] Input validation implemented | | |
| [ ] Secrets management verified | | |
| [ ] Security review completed | | |

### Stakeholder Readiness

| Item | Status | Notes |
|------|--------|-------|
| [ ] Stakeholders informed of capabilities | | |
| [ ] Stakeholders informed of limitations | | |
| [ ] Support plan in place | | |
| [ ] Escalation path defined | | |
| [ ] User training completed (if needed) | | |

---

## Known Limitations

Document any known limitations that stakeholders have accepted:

| ID | Limitation | Impact | Mitigation | Accepted By |
|----|------------|--------|------------|-------------|
| L1 | | | | |
| L2 | | | | |
| L3 | | | | |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation | Residual Risk |
|------|------------|--------|------------|---------------|
| | Low/Med/High | Low/Med/High | | Acceptable? |
| | | | | |
| | | | | |

---

## Evaluation Results Summary

### Test Results

| Test Category | Pass Rate | Critical Failures |
|---------------|-----------|-------------------|
| Unit Tests | ___% | |
| Integration Tests | ___% | |
| E2E Tests | ___% | |
| Performance Tests | ___% | |
| Safety Tests | ___% | |

### Quality Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Accuracy | | | ✅/❌ |
| Latency P50 | | | ✅/❌ |
| Latency P99 | | | ✅/❌ |
| Error Rate | | | ✅/❌ |
| | | | |

---

## Gate Decision

### Checklist Summary

| Category | Items | Passed | Failed | Blocked |
|----------|-------|--------|--------|---------|
| Functional | | | | |
| Performance | | | | |
| Quality | | | | |
| Safety | | | | |
| Operational | | | | |
| Documentation | | | | |
| Security | | | | |
| Stakeholder | | | | |
| **TOTAL** | | | | |

### Decision

**Quality Gate Decision:**

- [ ] **GO** - All critical criteria met, proceed to production
- [ ] **NO-GO** - Critical issues must be resolved before proceeding
- [ ] **CONDITIONAL** - Proceed with listed conditions to address post-deployment

### If GO:

- Proceed to Phase 5: Operations
- Acceptance criteria documented above

### If NO-GO:

**Blocking Issues:**
1.
2.
3.

**Return to Phase:** ___

**Re-evaluation Date:** ___

### If CONDITIONAL:

**Conditions to Address:**
1.
2.
3.

**Deadline for Conditions:** ___

**Responsible Party:** ___

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | | | |
| Product Owner | | | |
| QA Lead | | | |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | | | Initial checklist |

---

*Generated by AI Engineering Workflow v1.0*
