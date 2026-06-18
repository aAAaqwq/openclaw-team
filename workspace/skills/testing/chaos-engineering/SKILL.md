---
name: chaos-engineering
description: >
  Chaos Engineering discipline — proactive experimentation on distributed
  systems to build confidence in their resilience. Covers Netflix-inspired
  chaos principles, experiment design, blast radius control, LitmusChaos
  and Chaos Mesh usage, game day planning, and production safety.

  USE WHEN: validating system resilience before production incidents,
  designing chaos experiments, planning game days, implementing CI/CD
  chaos pipeline, or building confidence in fault tolerance. Triggers on
  "chaos engineering", "chaos experiment", "game day", "resilience test",
  "fault injection", "Litmus", "Chaos Mesh", "break things on purpose".
---

# Chaos Engineering

> **Source**: Netflix Chaos Engineering + Google SRE + Principles of Chaos
> (Principles of Chaos Engineering book + real production experience at
> Netflix/ByteDance)
> **Core Philosophy**: "Chaos Engineering is the discipline of experimenting
> on a distributed system to build confidence in the system's capability
> to withstand turbulent conditions in production."

## Core Principles

```
  Chaos Engineering is NOT:
  ❌ Randomly breaking things hoping to learn something
  ❌ "Let's just kill a pod and see what happens"
  ❌ A one-time event (we did chaos, we're done!)

  Chaos Engineering IS:
  ✅ The scientific method applied to production resilience
  ✅ Systematic, controlled, and measured
  ✅ A continuous practice — every release should make the system more resilient
```

---

## 1. The Scientific Method for Production

### 1.1 The Five Steps

```
  ┌──────────────────────────────────────────────────────────────┐
  │  ① Define "steady state"                                      │
  │     → A measurable output that indicates normal behavior       │
  │     → e.g., "p99 latency < 200ms, error rate < 0.1%"           │
  │                                                                │
  │  ② Hypothesize                                                 │
  │     → "The system will remain in steady state when [failure]   │
  │       occurs"                                                  │
  │     → e.g., "p99 stays < 200ms when a single pod dies"         │
  │                                                                │
  │  ③ Introduce failure                                           │
  │     → Controlled experiment — NOT production fire drill        │
  │     → Kill pod, inject latency, block network, saturate CPU    │
  │                                                                │
  │  ④ Measure against steady state                                │
  │     → Compare actual behavior against the hypothesis           │
  │     → Did we stay within bounds?                               │
  │                                                                │
  │  ⑤ Fix or Confirm                                              │
  │     ✅ Hypothesis true  → System is resilient as expected      │
  │     ❌ Hypothesis false → You found a weakness: FIX IT        │
  └──────────────────────────────────────────────────────────────┘
```

### 1.2 The Golden Rule: Blast Radius Control

```
  ┌──────────────────────────────────────────────────────────────┐
  │  ALL CHAOS EXPERIMENTS MUST:                                   │
  │  ✦ Have an explicit hypothesis                                 │
  │  ✦ Have measurable steady state metrics                        │
  │  ✦ Have a defined blast radius                                 │
  │  ✦ Have automatic rollback conditions                          │
  │  ✦ Be communicated to the team beforehand                      │
  │  ✦ Run during low-traffic windows initially                    │
  └──────────────────────────────────────────────────────────────┘
```

---

## 2. Experiment Types by Maturity

### Level 1: Infrastructure Failures (Start here)

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Experiment                │ Blast Radius │  Difficulty       │
  ├────────────────────────────┼──────────────┼───────────────────┤
  │ Kill a single pod          │ Small        │ Easy              │
  │ Network partition a pod    │ Small        │ Easy              │
  │ Kill a DB read replica     │ Medium       │ Medium            │
  │ CPU saturation (80-100%)   │ Small        │ Easy              │
  │ Memory pressure            │ Small        │ Easy              │
  │ AZ (availability zone) fail│ Large        │ Hard              │
  └──────────────────────────────────────────────────────────────┘
```

### Level 2: Service Degradation

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Experiment                │ What It Tests                   │
  ├────────────────────────────┼─────────────────────────────────┤
  │ Inject 500ms latency on    │ Timeout handling + retry logic  │
  │   inter-service calls      │                                 │
  │ Simulate DNS failure       │ DNS caching + fallback          │
  │ Rate-limit an upstream     │ Circuit breaker + backpressure  │
  │ Return 500 from a service  │ Error handling + degraded mode  │
  │ Simulate cert expiry       │ Graceful SSL failure handling   │
  └──────────────────────────────────────────────────────────────┘
```

### Level 3: Data Plane Issues

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Experiment                │ What It Tests                   │
  ├────────────────────────────┼─────────────────────────────────┤
  │ Corrupt a cache entry      │ Cache invalidation + fallback   │
  │ DB connection pool drain   │ Connection pool + retry + queue │
  │ Queue backlog (Kafka lag)  │ Consumer scaling + DLQ handling │
  │ S3/object store unreachable│ CDN failover + local cache     │
  │ Feature flag mismatch      │ Graceful degradation paths      │
  └──────────────────────────────────────────────────────────────┘
```

### Level 4: Compound Failures (Advanced)

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Experiment                │ What It Tests                   │
  ├────────────────────────────┼─────────────────────────────────┤
  │ Two simultaneous AZ fails  │ Multi-AZ architecture           │
  │ Cascading failure: DB slow │ Full resilience chain           │
  │   → cache miss → DB slower │                                 │
  │ Config pushed to wrong     │ Config isolation + rollback     │
  │   region                   │                                 │
  │ Dependency chain failure:  │ Bulkhead pattern                │
  │   A fails → B fails → C    │                                 │
  └────────────────────────────┴─────────────────────────────────┘
```

---

## 3. Tool Integration

### 3.1 LitmusChaos (Kubernetes-Native)

```yaml
# chaos-experiment-pod-kill.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: pod-kill-weekly
spec:
  appinfo:
    appns: "production"
    applabel: "app=order-service"
    appkind: "deployment"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-kill
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "120"
            - name: CHAOS_INTERVAL
              value: "15"
            - name: FORCE
              value: "false"    # Graceful kill (SIGTERM)
            - name: RAMP_TIME
              value: "10"
        probes:
          - name: "check-service-health"
            type: "httpProbe"
            httpProbe/inputs:
              url: "http://order-service.production:8080/health"
              insecure: true
            mode: "Continuous"
            runProperties:
              probeTimeout: 5
              interval: 2
```

```bash
# Run the experiment
kubectl apply -f chaos-experiment-pod-kill.yaml

# Monitor experiment progress
kubectl describe chaosengine pod-kill-weekly

# Check experiment results
kubectl get chaosresult pod-kill-weekly-pod-kill -o yaml
```

### 3.2 Chaos Mesh (Alternative)

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
spec:
  action: delay
  mode: fixed-percent
  value: "20"
  selector:
    namespaces: ["production"]
    labelSelectors:
      app: payment-service
  delay:
    latency: "500ms"
    jitter: "100ms"
    correlation: "50"
  duration: "60s"
  scheduler:
    cron: "@every 24h"
```

### 3.3 Minimal Chaos Script (Quick Ad-Hoc)

```bash
#!/bin/bash
# quick-chaos.sh — Run a quick resilience check in 60 seconds

set -euo pipefail

SERVICE=${1:-order-service}
NAMESPACE=${2:-production}

echo "🔬 CHAOS EXPERIMENT: Kill one pod of $SERVICE in $NAMESPACE"

# 1. Measure steady state
echo "[01] Measuring steady state..."
BASELINE_ERR=$(curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{service=\"$SERVICE\",status=~\"5..\"}[1m])" | jq -r '.data.result[0].value[1] // "0"')
BASELINE_LAT=$(curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service=\"$SERVICE\"}[1m]))" | jq -r '.data.result[0].value[1] // "0"')
echo "   Baseline error rate: ${BASELINE_ERR}%"
echo "   Baseline p99 latency: ${BASELINE_LAT}s"

# 2. Define hypothesis
echo "[02] Hypothesis: Service remains healthy (error < 1%, p99 < 500ms)"

# 3. Introduce failure
echo "[03] Killing a random pod..."
kubectl delete pod -n "$NAMESPACE" -l "app=$SERVICE" --now --wait=false 2>/dev/null

# 4. Wait and measure
echo "[04] Measuring response after failure (30s wait)..."
sleep 30

RECOVERY_ERR=$(curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{service=\"$SERVICE\",status=~\"5..\"}[1m])" | jq -r '.data.result[0].value[1] // "0"')
RECOVERY_LAT=$(curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service=\"$SERVICE\"}[1m]))" | jq -r '.data.result[0].value[1] // "0"')

echo "   Recovery error rate: ${RECOVERY_ERR}%"
echo "   Recovery p99 latency: ${RECOVERY_LAT}s"

# 5. Evaluate hypothesis
THRESHOLD_ERR=1.0
THRESHOLD_LAT=0.5

PASS=true
if (( $(echo "$RECOVERY_ERR > $THRESHOLD_ERR" | bc -l) )); then
  echo "❌ FAIL: Error rate ${RECOVERY_ERR}% exceeds threshold ${THRESHOLD_ERR}%"
  PASS=false
fi
if (( $(echo "$RECOVERY_LAT > $THRESHOLD_LAT" | bc -l) )); then
  echo "❌ FAIL: p99 latency ${RECOVERY_LAT}s exceeds threshold ${THRESHOLD_LAT}s"
  PASS=false
fi

if $PASS; then
  echo "✅ PASS: Service remains resilient under pod failure"
else
  echo "🔧 FIX: Investigate and improve resilience before next release"
fi
```

---

## 4. Game Day Planning

### 4.1 Game Day Structure

```
  ┌──────────────────────────────────────────────────────────────┐
  │                 GAME DAY SCHEDULE (4 hours)                    │
  │                                                               │
  │  Preparation (1 week before):                                  │
  │  □ Define scenario + steady state metrics                     │
  │  □ Write hypothesis document                                  │
  │  □ Set up monitoring dashboard                                │
  │  □ Notify all stakeholders                                    │
  │  □ Schedule during low-traffic window                          │
  │                                                               │
  │  Game Day (4 hours):                                          │
  │  0:00 - 0:30  Briefing + roles assignment                     │
  │  0:30 - 1:30  Experiment 1 (infrastructure failure)          │
  │  1:30 - 2:30  Experiment 2 (service degradation)             │
  │  2:30 - 3:30  Experiment 3 (compound failure)                │
  │  3:30 - 4:00  Debrief + action items                          │
  │                                                               │
  │  Post-Game (next week):                                       │
  │  □ Write game day postmortem                                  │
  │  □ Assign and track action items                              │
  │  □ Schedule next game day                                     │
  └──────────────────────────────────────────────────────────────┘
```

### 4.2 Game Day Roles

```
  Chaos Engineer (planner):
  × Does NOT participate in mitigation (too much insider knowledge)
  ✓ Designs experiments
  ✓ Moderates the game day
  ✓ Monitors and records results

  IC (Incident Commander):
  ✓ Receives the "incident"
  ✓ Coordinates the response
  ✓ Exactly like a real incident

  Ops Lead:
  ✓ Diagnoses the issue
  ✓ Applies mitigations
  ✓ Makes rollback decisions

  Scribe:
  ✓ Records timeline
  ✓ Documents decisions
  ✓ Note: "Did they follow the runbook?"
```

### 4.3 Game Day Scenarios (Progressive Difficulty)

```
  Beginner:  "One pod dies at 2pm — can the team detect it?"
  Medium:    "Database replica suddenly loses network — can reads continue?"
  Hard:      "Dependency A and B both fail simultaneously — does C function?"
  Expert:    "Chaos engineer kills random pods every 5 minutes for 1 hour"
  Nightmare: "Full AZ outage during a deployment — what happens?"
```

---

## 5. Automated Chaos in CI/CD

### 5.1 Chaos Pipeline

```yaml
# .github/workflows/chaos-weekly.yml
name: Weekly Chaos Engineering

on:
  schedule:
    - cron: '0 10 * * 1'   # Monday 10am
  workflow_dispatch:

jobs:
  chaos:
    runs-on: ubuntu-latest
    environment: production-testing
    steps:
      - uses: actions/checkout@v4
      - uses: litmuschaos/litmus-actions@v1.0.0
        with:
          chaosEngine: chaos/pod-kill-weekly.yaml
          endpoint: ${{ secrets.LITMUS_ENDPOINT }}
          token: ${{ secrets.LITMUS_TOKEN }}
      
      - name: Check resilience score
        run: |
          SCORE=$(litmusctl get resilience-score --experiment pod-kill-weekly)
          if [ "$SCORE" -lt 80 ]; then
            echo "❌ Resilience score $SCORE < 80. Fix before next release."
            exit 1
          fi
          echo "✅ Resilience score: $SCORE"
```

### 5.2 Progressive Chaos

```
  ┌──────────────────────────────────────────────────────────────┐
  │  STAGE 1: Staging (1x per deploy)                             │
  │     → Run basic experiments (pod kill, latency injection)     │
  │     → Gate: if resilience score < 70 → block deployment       │
  │                                                                │
  │  STAGE 2: Canary (1x per canary release)                      │
  │     → Run medium experiments (dependency failure, data corr.) │
  │     → Gate: if resilience score < 80 → rollback canary         │
  │                                                                │
  │  STAGE 3: Production (weekly)                                  │
  │     → Run full experiment suite including compound failures    │
  │     → Post-game day report to engineering team                 │
  └──────────────────────────────────────────────────────────────┘
```

---

## 6. Safety Mechanisms

### 6.1 Automatic Rollback Conditions

```yaml
# These conditions STOP the experiment immediately
auto_rollback:
  error_rate_increase: "> 5x baseline for 1 minute"
  p99_latency_increase: "> 3x baseline for 1 minute"
  # These trigger immediate human intervention
  alert_conditions:
    - "P0 incident declared during experiment"
    - "Customer support tickets spike > 10x"
    - "Financial transaction errors detected"
```

### 6.2 Experiment Safety Checklist

```
  Before running ANY chaos experiment:

  □ Have I defined "steady state" quantitatively?
  □ Have I written the hypothesis explicitly?
  □ What is the blast radius? (number of pods: __)
  □ What is the rollback condition? (error rate > __ %)
  □ Is this during low-traffic time? (current traffic: __ QPS)
  □ Have I communicated to the team (@channel #chaos-eng)?
  □ Do I have a revert plan?
  □ Can I kill the experiment in < 30 seconds if needed?
  □ Have I tested this on staging first?
  □ Is monitoring available in real-time?
```

---

## 7. Resilience Metrics

### 7.1 Track These

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Metric                      │ What It Tracks               │
  ├──────────────────────────────┼──────────────────────────────┤
  │ Experiments Run (week)       │ Are we doing chaos regularly?│
  │ Experiments Passed (%)       │ Are we getting better?        │
  │ MTTR during experiment       │ How fast can engineers fix?   │
  │ Bleed-over incidents         │ Did chaos cause real outages? │
  │ Resilience Score (0-100)     │ Composite health metric       │
  │ Time to Detection            │ How fast is monitoring?       │
  │ Time to Mitigation           │ How fast is response?         │
  └──────────────────────────────────────────────────────────────┘
```

### 7.2 Resilience Score Calculation

```
  Scores by experiment type:
  Infrastructure  → Weight 30%
  Degradation     → Weight 30%
  Data Plane      → Weight 25%
  Compound        → Weight 15%

  For each experiment:
  Full pass (within bounds, detected by monitoring) → 100
  Partial (manual detection, slow mitigation)       → 50
  Fail (outage beyond SLO, no mitigation)           → 0

  Composite = Sum(experiment_score × weight) / total_weight
  
  Target: > 85 for production systems
```

---

## 8. Common Anti-Patterns

```
  ❌ Chaos without hypothesis: "Let's just break stuff"
     → Always have a clear hypothesis: "When X happens, Y stays within Z"

  ❌ Only running chaos on staging
     → Staging isn't production. The point is to test production behavior.

  ❌ No automatic rollback
     → If you can't stop the experiment automatically, you're not ready

  ❌ One-time chaos event
     → Chaos Engineering is a continuous practice, not a checkbox

  ❌ Not fixing what you find
     → Discovering a weakness and not fixing it is the worst outcome.
     → If you can't fix it immediately, track it with high priority.
```

---

## References

- `references/chaos-experiment-catalog.md` — Complete catalog of 30+ experiments with templates
- `references/game-day-scripts.md` — Complete game day runbooks with facilitator notes
- `references/measurement-and-dashboards.md` — Grafana dashboards for chaos experiment tracking
