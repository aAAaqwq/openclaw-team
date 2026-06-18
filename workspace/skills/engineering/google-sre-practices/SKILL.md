---
name: google-sre-practices
description: >
  Google SRE (Site Reliability Engineering) practices distilled from the
  SRE book series and real Google Brain/Meta/ByteDance production experience.
  Covers SLI/SLO/Error Budget design, incident response, capacity planning,
  toil automation, monitoring golden signals, and chaos engineering principles.

  USE WHEN: designing reliability targets, setting up monitoring/alerting,
  planning capacity, reducing operational load, building incident response
  runbooks, implementing chaos engineering, defining error budgets, or
  establishing reliability culture that balances velocity with stability.
---

# Google SRE Practices

> **Source**: Google SRE Book + SRE Workbook + The Site Reliability Workbook
> + Practical Google/ByteDance production operations experience
> **Core Philosophy**: Reliability is a feature, and like any feature, it has
> a cost. SRE makes the trade-off explicit via Error Budgets.

## Core Principles

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  Google SRE's core insight:                                      │
  │  ◆ 100% reliability is the WRONG target (impossible cost)       │
  │ ◆ Error Budgets make reliability a PRODUCT decision, not free   │
  │ ◆ Automation > Manual (toil is the enemy of SRE)                │
  │ ◆ Everything fails — design for failure, not for perfection     │
  │ ◆ Observability requires three pillars: logs, metrics, traces  │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 1. SLI / SLO / SLA — The Service Level Triad

### 1.1 Definitions

```
  SLI (Service Level Indicator):
    A quantifiable measure of some aspect of service level.
    Examples: request latency, error rate, throughput, availability.
    
    GOOD SLI: "fraction of requests completed in < 200ms"
    BAD SLI:  "user happiness" (can't measure)
    BAD SLI:  "average latency" (hides p99 problems under p50)

  SLO (Service Level Objective):
    A target value or range for a service level.
    Examples: 99.9% availability, p99 latency < 200ms.
    
    ⚠️ Design for reality, not hubris:
    ❌ "We'll aim for 99.99% because Google does it!"
    ✅ "The business needs 99.9% and we can sustain that"

  SLA (Service Level Agreement):
    A promise to your customers about the level of service.
    Usually with consequences (credits, penalties).
    Always stricter than SLOs (SLA < SLO, because you need a buffer).
```

### 1.2 How to Define SLIs

Start by asking: **"What matters to our users?"**

```
  For a web API service:
    Availability:   % of HTTP requests that return 2xx/3xx
    Latency:        % of requests completing in < 200ms (p99)
    Throughput:     Requests per second sustained
    Durability:     % of writes not lost (for storage)

  For a data pipeline:
    Freshness:      Age of most recent data
    Correctness:    % of records passing validation
    Completeness:   % of expected data actually delivered
    Latency:        Time from event → available for query

  For an ML inference service:
    Availability:   % of inference requests served successfully
    Latency:        p99 inference time
    Accuracy:       Model quality metric (e.g., BLEU, perplexity)
    Freshness:      Age of model since last training
```

### 1.3 Choosing SLO Targets — The Hard Part

```
  SLO Selection Process:

  1. Set an initial target (e.g., 99.9%)
  
  2. Ask: "If customer satisfaction dropped 1%, would this target cause it?"
     If YES → Raise the target
     If NO  → Lower the target
  
  3. Ask: "Can we sustain this target for 3 months without burning out?"
     If NO  → Lower the target (unsustainable = undeliverable)
     If YES → Accept the target
  
  4. Monitor for 1 quarter, then adjust
     → If we never miss SLO → it's too loose
     → If we always miss SLO → it's too tight
     → Goldilocks zone: hit SLO 95-99% of the time

  Magic formula: Good SLO = targets that keep customers happy
                   without creating false urgency.
```

### 1.4 Common SLO Patterns

```
  ┌──────────────────────────────────────────────────────────────┐
  │                          │ Tight (< 99.9%) │    SLO Target   │
  ├──────────────────────────┼─────────────────┼─────────────────┤
  │ Internal/Cost-sensitive  │ 99%             │ 99.5%           │
  │ Customer-facing  │ 99.9%           │ 99.99%          │
  │ Critical infra   │ 99.99%          │ 99.999%         │
  │ Money-related    │ 99.999%         │ 99.9999%        │
  └──────────────────────────┴─────────────────┴─────────────────┘

  9s translate to downtime per year:
  99%     → 3.65 days/year
  99.9%   → 8.76 hours/year
  99.99%  → 52.6 minutes/year
  99.999% → 5.26 minutes/year
  99.9999% → 31.5 seconds/year
```

---

## 2. Error Budgets — The SRE Superpower

### 2.1 What is an Error Budget?

```
  Error Budget = 1 − SLO

  If your SLO is 99.9% availability:
  Error Budget = 0.1% of total requests = your "allowed failure"

  Think of it as:
  "You have X failures budgeted for this month.
   Spend them wisely."

  After the budget is spent:
  → Release velocity slows down (stability mode)
  → Before budget spent:
  → Full speed ahead (feature mode)
```

### 2.2 How Error Budgets Transform Decision-Making

```
  Without Error Budget:
  ❌ "Can we deploy? I don't know, let's see if it feels risky"
  ❌ Ops says "no" → feature team feels blocked
  ❌ No explicit trade-off — everything is crisis

  With Error Budget:
  ✅ "We have 10% budget left this month — safe to deploy"
  ✅ "We have 0% budget left — NO DEPLOYS until next month"
  ✅ Trade-off is explicit, data-driven, not political
  ✅ Product owns the budget: "Want more releases? Accept more risk"
```

### 2.3 Error Budget Policy Template

```
  ┌──────────────────────────────────────────────────────────────┐
  │                    Error Budget Policy                        │
  │                                                              │
  │  Budget Period: Calendar month (30 day rolling window)       │
  │                                                              │
  │  Budget burned thresholds:                                    │
  │  ┌────────────┬──────────┬────────────────────────────────┐ │
  │  │ Threshold  │ Action   │ Owner                         │ │
  │  ├────────────┼──────────┼────────────────────────────────┤ │
  │  │ < 50%      │ Normal   │ Team makes own decisions      │ │
  │  │ 50-80%     │ Caution  │ Feature freeze unless critical│ │
  │  │ 80-100%    │ Alert    │ Postmortem required           │ │
  │  │ > 100%     │ Freeze   │ NO deploys. Reliability mode  │ │
  │  └────────────┴──────────┴────────────────────────────────┘ │
  │                                                              │
  │  Budget reset: Beginning of each calendar month              │
  └──────────────────────────────────────────────────────────────┘
```

---

## 3. Monitoring & Alerting — The Golden Signals

### 3.1 Google's Four Golden Signals

```
  ┌──────────────────────────────────────────────────────────────┐
  │ ①  Latency         Time to service a request                │
  │                     → Distinguish "fast errors" from "slow  │
  │                       success" (both are bad, different fix)│
  │                     → Track p50, p95, p99                   │
  │                                                             │
  │ ②  Traffic         Demand on your system                    │
  │                     → Requests/sec, connections, QPS        │
  │                     → Track per route/endpoint              │
  │                                                             │
  │ ③  Errors          Rate of failed requests                  │
  │                     → Explicit 5xx, implicit (200 but wrong)│
  │                     → Track per error code + per endpoint   │
  │                                                             │
  │ ④  Saturation      How "full" your service is               │
  │                     → CPU, memory, disk, network I/O        │
  │                     → Connection pool, queue depth          │
  │                     → Best leading indicator of trouble     │
  └──────────────────────────────────────────────────────────────┘
```

### 3.2 Alert Severity Classification

```
  ┌─────────┬──────────────────────────────────┬──────────────────┐
  │ Level   │ When to use it                   │ Response         │
  ├─────────┼──────────────────────────────────┼──────────────────┤
  │ P0/Page │ User-facing outage               │ Wake the person  │
  │          │ SLO breach likely in < 10 min    │                   │
  │          │ Data loss risk                    │                   │
  ├─────────┼──────────────────────────────────┼──────────────────┤
  │ P1/Ticket│ Error budget > 50% burned       │ Next business day │
  │          │ Non-critical degradation         │                   │
  │          │ Capacity threshold warning       │                   │
  ├─────────┼──────────────────────────────────┼──────────────────┤
  │ P2/Log  │ Non-urgent anomaly               │ Next sprint       │
  │          │ Performance drift                │                   │
  │          │ Deprecation warnings             │                   │
  └─────────┴──────────────────────────────────┴──────────────────┘
```

### 3.3 Alert Design Principles

```
  Rule 1: Every alert must be actionable.
    ❌ "CPU at 80%" — what do you want me to DO?
    ✅ "CPU at 80% with traffic rising" — scale up or investigate.
    
  Rule 2: Alert on symptoms (user-facing), not causes (internal).
    ❌ "Redis memory high" — I don't care about Redis
    ✅ "Request timeout rate > 1%" — NOW I care

  Rule 3: No alert should be "noise more than twice."
    If an alert fires and the response is "ignore it" 2x in a row,
    either fix the alert or delete it. Alert fatigue kills.

  Rule 4: Every alert must have a runbook.
    The runbook doesn't need to be 10 pages, but it must answer:
    - "What's broken?" (symptom)
    - "How do I confirm it?" (diagnostic step)
    - "What do I do?" (mitigation)
    - "When do I escalate?" (threshold)
```

### 3.4 Runbook Template

```
  ┌──────────────────────────────────────────────────────────────┐
  │ Alert: High Error Rate (>1% 5xx)                            │
  │                                                             │
  │ 1. CHECK                                                    │
  │    `kubectl get pods` → any pods restarting?                 │
  │    `curl -I /health` → service alive?                        │
  │    `tail -100 logs/app.log` → any error stack?               │
  │                                                             │
  │ 2. TRIAGE                                                    │
  │    → If all pods healthy → check upstream dependencies      │
  │    → If pods crashing → `kubectl describe pod` for reason    │
  │    → If upstream failing → escalate to dependency team      │
  │                                                             │
  │ 3. MITIGATE                                                  │
  │    → If dependency issue: circuit breaker / fallback         │
  │    → If code issue: rollback to last known good image       │
  │    → If data issue: database rollback / recovery            │
  │                                                             │
  │ 4. ESCALATE                                                  │
  │    → If not resolved in 15 min → page senior SRE            │
  │    → If data loss suspected → page DBA + engineering lead   │
  │    → If security breach → security team + legal             │
  └──────────────────────────────────────────────────────────────┘
```

---

## 4. Incident Response — Triage & Manage

### 4.1 Incident Command System

```
  ┌──────────────────────────────────────────────────────────────┐
  │  INCIDENT COMMAND STRUCTURE                                   │
  │                                                               │
  │  IC (Incident Commander):                                     │
  │   × NOT responsible for fixing                                │
  │   ✓ Coordinates response, communications, timeline            │
  │   ✓ Decides when to call in more people                       │
  │   ✓ Decides when to declare incident over                    │
  │                                                               │
  │  Ops Lead:                                                    │
  │   ✓ Directs technical mitigation                              │
  │   ✓ Coordinates with IC on progress                           │
  │                                                               │
  │  Scribe:                                                      │
  │   ✓ Documents timeline and actions                            │
  │   ✓ Relieves IC from note-taking                              │
  │                                                               │
  │  Comms Lead:                                                  │
  │   ✓ Internal/external communications                          │
  │   ✓ Status updates to stakeholders                            │
  └──────────────────────────────────────────────────────────────┘
```

### 4.2 Incident Triage Process

```
  1. STOP THE BLEEDING (first 5 min)
     → Is there automatic mitigation? (circuit breaker, scale-up)
     → If not: rollback, restart, or redirect traffic
     → Don't investigate root cause yet — stabilize first

  2. STABILIZE (5-30 min)
     → Implement immediate workaround
     → Restore service to acceptable state
     → Document what was done

  3. INVESTIGATE (30 min +)
     → Root cause analysis begins
     → Use timeline to track discoveries
     → Avoid blame — focus on systems

  4. RESOLVE
     → Permanent fix deployed
     → Monitoring confirms normal operation
     → Incident declared over

  5. POSTMORTEM (within 1 week)
     → Full timeline
     → 5 Whys
     → Action items with owners + due dates
     → Blameless review
```

---

## 5. Chaos Engineering — Proactive Reliability

### 5.1 Core Principle

> "Chaos Engineering is the discipline of experimenting on a distributed system
> in order to build confidence in the system's capability to withstand turbulent
> conditions in production." — Netflix

### 5.2 The Scientific Method for Production

```
  Step 1: Define "steady state" → measurable output (e.g., p99 < 200ms)

  Step 2: Hypothesize → "If instance fails, system degrades by at most 5%"

  Step 3: Introduce failure → Kill a pod, inject latency, blackhole traffic

  Step 4: Measure → Compare actual behavior against steady state

  Step 5: Fix or Confirm → 
    If hypothesis correct → system is resilient
    If incorrect         → you found a weakness — fix it
```

### 5.3 Practical Chaos Experiments

```
  Level 1: Infrastructure Failure
    ✅ Kill a randomly selected pod
    ✅ Network partition a service
    ✅ Kill a database replica
    ✅ Simulate AZ (availability zone) outage

  Level 2: Service Degradation
    ✅ Inject latency on inter-service calls
    ✅ Simulate DNS failure
    ✅ Rate-limit a dependency
    ✅ Certificate expiration simulation

  Level 3: Data Plane Issues
    ✅ Corrupt a cache entry
    ✅ Simulate authentication service timeout
    ✅ Media/image processing service slowdown
    ✅ Dead-letter queue overflow

  Level 4: Compound Failures
    ✅ Two simultaneous AZ outages
    ✅ Cascading failure: DB slow → cache miss → DB even slower
    ✅ Config pushed to wrong region
```

### 5.4 Chaos Engineering Safety

```
  Golden Rules:
  1. NEVER experiment during business peak hours
  2. Start with small blast radius (1 pod, not 50)
  3. Have automatic rollback:
     → If error rate > threshold → auto-stop experiment
  4. Communicate before running experiments
  5. Every experiment has explicit hypothesis + expected outcome
  6. Blast radius must be limited to non-critical path initially
```

---

## 6. Capacity Planning

### 6.1 The Capacity Planning Process

```
  ┌──────────────────────────────────────────────────────────────┐
  │              Capacity Planning Cycle (Quarterly)              │
  │                                                               │
  │  Month 1: Demand Forecasting                                  │
  │   → Analyze historical growth curves                          │
  │   → Business input: new features, campaigns, events          │
  │   → Traffic projection: "How much load in 6 months?"         │
  │                                                               │
  │  Month 2: Resource Modeling                                   │
  │   → Model capacity needs per resource type                    │
  │   → CPU, memory, disk, network, database connections          │
  │   → Size per service, per environment                         │
  │                                                               │
  │  Month 3: Procurement / Scaling                               │
  │   → Cloud resources: auto-scaling config updates              │
  │   → Budget approval for additional resources                  │
  │   → Infrastructure-as-code changes to support growth          │
  └──────────────────────────────────────────────────────────────┘
```

### 6.2 Back-of-Envelope Capacity Estimation

```
  Given: 10M MAU, 100M requests/day, 500ms avg request time

  Peak traffic (assuming 2x daily peak factor):
    100M / 86400 sec ≈ 1157 req/sec average
    1157 × 2 = ~2300 req/sec peak

  Compute needed:
    2300 req/sec × 0.5 sec = 1150 concurrent requests
    Each request uses ~200MB memory
    Need: 1150 × 200MB ≈ 230GB RAM total
    
    With 8GB per instance: 29 instances ≈ 30
    With 2x headroom: 60 instances

  Cost estimate:
    60 × $0.10/hr × 24 × 30 = $4320/month (compute only)
```

### 6.3 Autoscaling Strategy

```
  ┌─────────────┬──────────────────────────────────────────────────┐
  │ Metric       │ HPA Configuration                                │
  ├─────────────┼──────────────────────────────────────────────────┤
  │ CPU          │ Scale at 70% utilization                         │
  │ Memory       │ Scale at 80% utilization                         │
  │ Req/sec      │ Scale at 1000 req/sec per pod                    │
  │ Queue depth  │ Scale at 100 messages per worker per second      │
  │ Custom       │ Scale on SLO burn rate (error budget consumed)   │
  └─────────────┴──────────────────────────────────────────────────┘

  ⚠️ Beware of thrashing: add cooldown periods (3-5 min)
  ⚠️ Scale up fast (30s), scale down slow (5min)
  ⚠️ Have min/max instance limits (never scale to 0 for critical)
```

---

## 7. Toil — The Silent Killer

### 7.1 What is Toil?

```
  Toil = operational work that is:
  ✓ Manual (requires human touch)
  ✓ Repetitive (same thing over and over)
  ✓ Automatable (if time were invested)
  ✓ Tactical (reactive, not strategic)
  ✓ No enduring value (the world is the same after you do it)

  Examples:
  ❌ Restarting crashed services manually
  ❌ Copy-paste deploys
  ❌ Manually generating reports
  ❌ SSH-ing into servers to check logs
  ❌ Manually rotating credentials

  NOT toil:
  ✓ Writing automation
  ✓ Debugging novel issues
  ✓ Architecture design
  ✓ Code review
  ✓ On-call rotation (necessary, not toil)
```

### 7.2 Toil Budget

```
  Google SRE goal: < 50% of work hours on toil
  Aspirational goal: < 25% (leaves 50% for engineering)

  Track toil per team:
  ┌──────────────────────────────────────────────────────────────┐
  │  Week ending | Total hours | Toil hours | Toil % | Actions   │
  ├──────────────┼─────────────┼────────────┼────────┼──────────┤
  │ May 1        │ 160         │ 72         │ 45%    │ Auto-deploy│
  │ May 8        │ 160         │ 60         │ 37%    │ CI pipeline│
  │ May 15       │ 160         │ 48         │ 30%    │ Done       │
  └──────────────────────────────────────────────────────────────┘
```

### 7.3 Automation Priority Framework

```
  When deciding what to automate, use this matrix:

  ┌──────────────────────────────────────────────────────────────┐
  │                    Frequency                                  │
  │              High              │          Low                 │
  ├───────────────────────────────┼──────────────────────────────┤
  │H │  AUTOMATE NOW!             │  INVESTIGATE                 │
  │I │  Monthly report generation  │  Bi-annual cert rotation    │
  │G │  Deployment                 │  Quarterly snapshot restore  │
  │H │  Incident triage            │                              │
  ├───────────────────────────────┼──────────────────────────────┤
  │L │  QUICK WIN: Document       │  IGNORE                      │
  │O │  Once-a-week password reset│  Annual manual data cleanup  │
  │W │  Common ticket responses   │  Yearly hardware audit       │
  └───────────────────────────────┴──────────────────────────────┘
```

---

## 8. Reliability Maturity Model

```
  Level 0: Hero Ops
  ├── No SLOs, no monitoring
  ├── "We fix it when it breaks"
  └── Page every time, chaos all the time

  Level 1: Reactive
  ├── Basic monitoring (CPU, memory, disk)
  ├── Runbooks for common incidents
  ├── Manual deploys
  └── MTTR: hours to days

  Level 2: Proactive
  ├── SLOs defined for critical services
  ├── Error budgets tracked
  ├── CI/CD with automated testing
  ├── Incident command structure
  └── MTTR: < 1 hour

  Level 3: Automated
  ├── Autoscaling for capacity
  ├── Auto-remediation for common failures
  ├── Chaos engineering experiments
  ├── Capacity planning automated
  └── MTTR: < 15 minutes

  Level 4: Self-Healing
  ├── System adapts to failures automatically
  ├── Proactive scaling based on leading indicators
  ├── Automated postmortem analysis
  ├── Self-service reliability tools
  └── MTTR: < 5 minutes
```

### Where We Are vs Google

```
  ┌──────────────┬───────────────┬────────────────┐
  │ Capability   │ Our Level     │ Google Target  │
  ├──────────────┼───────────────┼────────────────┤
  │ Monitoring   │ L1-L2         │ L3             │
  │ Alerting     │ L1            │ L3             │
  │ SLO/Error Budget│ L0 Not yet │ L3             │
  │ Incident Mgmt │ L1           │ L3-L4          │
  │ Chaos Eng    │ L0            │ L3             │
  │ Automation   │ L1            │ L3-L4          │
  │ Capacity Plan│ L0            │ L2-L3          │
  │ Toil Mgmt    │ L0            │ L2             │
  └──────────────┴───────────────┴────────────────┘
```

---

## References

- `references/incident-runbooks.md` — Pre-built runbook templates for common incidents
- `references/alert-rules-examples.md` — Practical Prometheus/Grafana alert rule examples
- `references/chaos-experiment-templates.md` — Chaos experiment design templates with blast radius controls
- `references/capacity-planning-examples.md` — Back-of-envelope examples for different service patterns
