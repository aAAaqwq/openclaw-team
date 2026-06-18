# Engineering Metrics — DORA & Beyond

## 1. DORA Four Key Metrics (Google Cloud DevOps Research)

These four metrics correlate with **organizational performance** more than any
others studied by Google's DORA team over 7 years of research.

### The Metrics

```
  ┌─────────────────────┬──────────────┬─────────────────┐
  │ Metric              │ Elite        │ Low Performer    │
  ├─────────────────────┼──────────────┼─────────────────┤
  │ Deploy Frequency    │ On-demand    │ 1x/month         │
  │ Lead Time for Change│ < 1 hour     │ 1-6 months       │
  │ MTTR                │ < 1 hour     │ > 1 week         │
  │ Change Failure Rate │ 0-5%         │ 30-45%           │
  └─────────────────────┴──────────────┴─────────────────┘
```

### How to Measure Each

**Deploy Frequency**: Number of production deployments per day/week
- Track via CI/CD pipeline events
- Goal: Multiple deploys per day (Elite)

**Lead Time for Change**: Time from code commit to running in production
- Track: commit timestamp → deploy completion timestamp
- Goal: < 1 hour for Elite

**Mean Time to Recover (MTTR)**: Time to restore service after incident
- Track: incident detection → service restoration
- Goal: < 1 hour

**Change Failure Rate**: % of deployments causing production incidents
- Track: deploys that trigger incident response / total deploys
- Goal: < 5%

## 2. Beyond DORA — Engineering Health Scorecard

```
  ┌──────────────────────────────────────────────────┐
  │ Engineering Health Scorecard (Monthly Review)    │
  ├──────────────────────────────────────────────────┤
  │                                                  │
  │ Code Quality                                     │
  │   │ Code Review Coverage: _____%                 │
  │   │ PR Size < 400 lines: _____%                   │
  │   │ Review Turnaround < 24h: _____%               │
  │   │ Test Coverage: _____%                         │
  │                                                  │
  │ System Health                                     │
  │   │ Availability: ____% (vs SLO ____%)           │
  │   │ p99 Latency: _____ms (vs target _____ms)      │
  │   │ Error Budget Burned: ____%                    │
  │   │ Incident Count: _____ (S0:__ S1:__ S2:__)   │
  │                                                  │
  │ Developer Productivity                             │
  │   │ Active Contributors: ____                      │
  │   │ PRs Merged: ____ (per dev per week)           │
  │   │ Time in Code Review: ____ (avg days)         │
  │   │ Time Blocked Waiting: ____ (avg days)         │
  │                                                  │
  │ Technical Debt                                      │
  │   │ Open TODO Count: _____                         │
  │   │ TODOs > 30 days old: _____                     │
  │   │ Open Security Findings: _____ (Critical:__)    │
  │   │ Deprecated Deps: _____                         │
  └──────────────────────────────────────────────────┘
```

## 3. Tracking Implementation

### GitHub Actions Dashboard Integration

```yaml
# .github/workflows/dora-metrics.yml
name: Track DORA Metrics
on:
  deployment_status:

jobs:
  record-metrics:
    runs-on: ubuntu-latest
    steps:
      - name: Record deployment
        uses: google/dora-metrics-action@v1
        with:
          metric: deploy-frequency
          timestamp: ${{ github.event.deployment.created_at }}
```

### Manual Tracking via Script For non-CI environments:

```python
#!/usr/bin/env python3
"""Simple DORA metrics tracker."""

import json
from datetime import datetime

def calculate_metrics(commits, deploys, incidents):
    """Calculate DORA metrics from event data."""
    return {
        "deploy_frequency": len(deploys) / 30,  # per day
        "lead_time_for_change": sum(
            (d - c).total_seconds()
            for c, d in zip(commits, deploys)
        ) / len(commits),
        "mttr": sum(
            i.duration.total_seconds()
            for i in incidents
        ) / len(incidents),
        "change_failure_rate": (
            sum(1 for d in deploys if d.caused_incident) / len(deploys)
        )
    }
```

## 4. Developer Satisfaction Survey (Quarterly)

A simple 5-question survey (Google's "TechStop" style):

```
  1. "I am proud of the code quality in my team."
     Strongly Disagree [1] [2] [3] [4] [5] Strongly Agree

  2. "I can ship changes without fear of breaking production."
     Strongly Disagree [1] [2] [3] [4] [5] Strongly Agree

  3. "Code reviews on my team are thorough and helpful."
     Strongly Disagree [1] [2] [3] [4] [5] Strongly Agree

  4. "I would recommend our engineering culture to a peer."
     Strongly Disagree [1] [2] [3] [4] [5] Strongly Agree

  5. "I spent more time shipping than fixing broken things."
     Strongly Disagree [1] [2] [3] [4] [5] Strongly Agree
```

> Google found that a single question — "I would recommend our engineering
> culture" — correlates 0.85 with team performance. It's all you really need.
