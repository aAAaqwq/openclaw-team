# Postmortem Examples & Templates

## 1. Real-World Style Template

```markdown
# [SERVICE] Production Outage — [DATE]

## Summary
Brief description of the incident in 2-3 sentences.

## Severity: S1 (Critical — customer-facing impact > 30min)

## Duration
- **Detected**: 2026-05-15 14:23 UTC
- **Mitigated**: 2026-05-15 15:01 UTC
- **Resolution**: 2026-05-15 16:12 UTC
- **Total**: ~109 minutes

## Impact
- **Users affected**: ~12,000 (read-only mode for writes)
- **Revenue impact**: $0 (no revenue lost, read was unaffected)
- **SLA breach**: Yes (write availability dropped to 92% vs 99.95% SLO)

## Detection
- Manual — customer support ticket triage noticed errors
- Monitor did NOT fire because... [gap in monitoring]

## Timeline
| Time (UTC) | Event |
|-----------|-------|
| 14:23:00 | First support ticket: "Cannot save document" |
| 14:25:00 | On-call paged |
| 14:27:00 | Initial assessment: 503s on write API |
| 14:30:00 | Looked at database — connection pool exhausted |
| 14:35:00 | Identified: batch job holding long-running transactions |
| 14:40:00 | Applied kill: terminated all long-running transactions |
| 14:42:00 | Writes recovered! |
| 15:01:00 | Monitored for 20 min — system stable |

## Root Cause Analysis (5 Whys)

```
Why did writes fail?
 → Connection pool exhausted.
 
Why was the pool exhausted?
 → Long-running transactions held connections for 45+ seconds.
 
Why were transactions running so long?
 → Batch job `batch_export_analytics` was processing 2M+ records in a single transaction.
 
Why did this batch job process 2M records?
 → New feature triggered full re-export for all clients instead of delta.
 
Why didn't the monitoring catch this?
 → No alert on "average transaction duration" or "pending connection count".
```

### Technical Root Cause
Batch analytics export job processed full dataset (2M records) instead of delta
(typical ~5K records) due to missing WHERE clause in SQL executed by new feature
`analytics-v3`.

### Process Root Cause
1. Batch job SQL change was not reviewed by database team
2. No performance/stress testing for analytics export feature
3. Missing monitoring/alerting on connection pool health

## Action Items

| Priority | Action | Owner | Due | Status |
|----------|--------|-------|-----|--------|
| P0 | Add WHERE clause to batch export SQL | @alice | Done | ✅ |
| P0 | Kill switch for long-running batch jobs | @bob | T+48h | In Progress |
| P1 | Alert on: avg tx duration > 5s, connection utilization > 80% | @carol | T+1w | Todo |
| P1 | Rate limit for analytics export (max 50K per job) | @bob | T+1w | Todo |
| P2 | CI performance regression test for DB batch operations | @alice | T+2w | Todo |
| P2 | Code review checklist: "Does this change affect DB query patterns?" | @techlead | T+1w | Todo |

## Lessons Learned

### What went well
- Support team identified the issue quickly and escalated
- Terminating hung connections restored service within 22 min
- Team had clear ownership and acted fast

### What went wrong
- No monitoring on DB connection utilization
- Batch job design overlooked transaction size limits
- Code review didn't include SQL performance review

### What we'll do differently
1. All SQL changes in batch jobs require DB team review
2. Add connection pool monitoring to SRE dashboard
3. Implement "circuit breaker" on long-running transactions
```

## 2. Severity Classification System

```
  ┌─────────┬──────────────────────────────────┬──────────────────────┐
  │ Level   │ Definition                       │ Response Time         │
  ├─────────┼──────────────────────────────────┼──────────────────────┤
  │ S0      │ Complete service outage           │ Immediate (5 min)    │
  │          │ Data loss in progress             │                      │
  │          │ Security breach                    │                      │
  ├─────────┼──────────────────────────────────┼──────────────────────┤
  │ S1      │ Major feature unavailable         │ 15 min               │
  │          │ Significant customer impact       │                      │
  │          │ Revenue-critical system degraded  │                      │
  ├─────────┼──────────────────────────────────┼──────────────────────┤
  │ S2      │ Minor feature degraded            │ 1 hour               │
  │          │ Some customers affected           │                      │
  │          │ Non-critical path failure         │                      │
  ├─────────┼──────────────────────────────────┼──────────────────────┤
  │ S3      │ Cosmetic issue                    │ Next business day    │
  │          │ Single user issue                 │                      │
  │          │ Internal tooling problem          │                      │
  └─────────┴──────────────────────────────────┴──────────────────────┘
```

## 3. Postmortem Metrics Dashboard

Track these metrics over time to measure engineering culture health:

```
  ┌─────────────────────────────────────────────────┐
  │ Postmortem Health Scorecard                      │
  ├─────────────────────────────────────────────────┤
  │ MTTR (Mean Time To Recover)                      │
  │   → Goal: < 1 hour for S1 incidents             │
  │   → Current: [track over rolling 30 days]        │
  │                                                 │
  │ MTBF (Mean Time Between Failures)                │
  │   → Goal: Increasing trend                       │
  │   → Current: [track over rolling 90 days]        │
  │                                                 │
  │ Postmortem Coverage Rate                         │
  │   → % of S0/S1/S2 incidents with postmortems     │
  │   → Goal: 100% for S0/S1, > 50% for S2          │
  │                                                 │
  │ Action Item Completion Rate                      │
  │   → % of postmortem action items completed on time│
  │   → Goal: > 90% within due date                  │
  │                                                 │
  │ Blame Language Count                             │
  │   → Number of "who" words in postmortems         │
  │   → Goal: 0 (tracking this changes culture)     │
  └─────────────────────────────────────────────────┘
```

## 4. Google Postmortem Philosophy (Memorable Quotes)

> "Every outage is a free lesson. Only fools don't collect the tuition."

> "If your first question after an outage is 'who did this?', your second
> question should be 'why didn't our system catch it?'"

> "The best systems teams are those that have the most postmortems — not
> because they have more failures, but because they document them all."

> "There are two types of postmortems: ones that lead to new controls, and
> ones that are filed away. Only the first type improves reliability."
