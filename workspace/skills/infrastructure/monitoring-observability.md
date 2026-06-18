# Monitoring & Observability

> Level: Advanced | File: `monitoring-observability.md`
> 
> Engineering-grade observability: three pillars, service-level objectives, on-call best practices, and production-quality dashboards.

---

## Table of Contents
1. [The Three Pillars in Depth](#1-the-three-pillars-in-depth)
2. [Service Level Objectives (SLOs)](#2-service-level-objectives-slos)
3. [Metrics: RED, USE, and Application Metrics](#3-metrics-red-use-and-application-metrics)
4. [Logging: Structured, Centralized, and Actionable](#4-logging-structured-centralized-and-actionable)
5. [Distributed Tracing](#5-distributed-tracing)
6. [Alerting: Reduce Noise, Increase Signal](#6-alerting-reduce-noise-increase-signal)
7. [On-Call Best Practices](#7-on-call-best-practices)
8. [Dashboards: The Art of Visual Debugging](#8-dashboards-the-art-of-visual-debugging)
9. [Tool-Specific Guides](#9-tool-specific-guides)
10. [Appendix: Runbook Templates](#10-appendix-runbook-templates)

---

## 1. The Three Pillars in Depth

### 1.1 Logging
- **Purpose**: Record discrete events — errors, state transitions, access patterns
- **Must be**: structured (JSON), contextual (trace_id, span_id), and centralized
- **Anti-pattern**: "printf debugging" — your staging log must match production format

### 1.2 Metrics
- **Purpose**: Aggregated numeric time-series data — rates, latencies, saturation
- **Characteristics**: low cardinality, indexed by time, can be pre-aggregated
- **Cardinality warning**: tags with high uniqueness (user_id, request_id) → Prometheus memory OOM

### 1.3 Distributed Tracing
- **Purpose**: End-to-end view of a single request through multiple services
- **Components**: Trace (root) → Spans (individual operations) → Context (traceparent header)
- **Cost**: 1-10% sampling is typical for high-throughput systems

---

## 2. Service Level Objectives (SLOs)

### 2.1 Terminology
| Term | Definition | Example |
|------|-----------|---------|
| **SLI** | The actual metric you measure | "p99 latency of HTTP 200 responses over 5 min window" |
| **SLO** | Target value for SLI | "95% of requests complete in < 500ms over 30 days" |
| **SLA** | Contract with external party (usually looser than SLO) | "99.9% monthly uptime" |

### 2.2 Standard SLOs by Tier

| Tier | Example | Uptime | p99 Latency | Error Rate | Window |
|------|---------|--------|-------------|------------|--------|
| **Critical** | Payment processing, auth | 99.99% | < 200ms | < 0.01% | 30d |
| **Standard** | Web API, order service | 99.9% | < 500ms | < 0.1% | 30d |
| **Best-effort** | Analytics, report gen | 99% | < 2s | < 1% | 7d |

### 2.3 Error Budget Policy
```
Error Budget = 1 - SLO performance target
  Example: 99.9% SLO → 0.1% error budget over 30d = 43 minutes total downtime allowed

Budget Consumption:
  - < 50% used → normal development velocity
  - 50-80% → freeze non-critical features, focus on reliability
  - > 80% → all hands on deck, any deploy requires SRE approval
```

---

## 3. Metrics: RED, USE, and Application Metrics

### 3.1 RED Method (for services)
- **Rate** — requests per second
- **Errors** — failed requests (5xx, latency > timeout, business errors)
- **Duration** — distribution of response times (p50, p95, p99)

### 3.2 USE Method (for resources)
- **Utilization** — percentage of resource being used (CPU 70%, memory 80%)
- **Saturation** — queued/delayed work (CPU run queue, disk I/O wait)
- **Errors** — failed operations (disk errors, NIC drops)

### 3.3 Canonical Metric Set per Component

#### API Service (Prometheus style)
```promql
# Request rate
rate(http_requests_total[5m])

# Error ratio
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# p99 latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Active connections
http_connections_active
```

#### Database (PostgreSQL)
```promql
# Query latency
rate(pg_stat_activity_query_duration_seconds_sum[1m]) / rate(pg_stat_activity_query_duration_seconds_count[1m])

# Connection count
pg_stat_database_numbackends

# Replication lag
pg_replication_lag_seconds

# Cache hit ratio
rate(pg_stat_database_blks_hit[5m]) / (rate(pg_stat_database_blks_hit[5m]) + rate(pg_stat_database_blks_read[5m]))
```

#### Queue (Kafka / RabbitMQ)
```promql
# Consumer lag (Kafka)
kafka_consumer_lag

# Queue depth (RabbitMQ)
rabbitmq_queue_messages_ready

# Processing rate
rate(kafka_consumer_fetch_rate[1m])
```

### 3.4 Cardinality Management
- **Always** bound label values: HTTP methods (GET/POST/PUT/DELETE), status codes (2xx/3xx/4xx/5xx)
- **Never** put request_id, user_id, or session_id in metric labels
- **Aggregate** high-cardinality data via logging/tracing, not metrics
- **Budget**: < 10,000 time-series per target per scraper

---

## 4. Logging: Structured, Centralized, and Actionable

### 4.1 Canonical Log Format
```json
{
  "timestamp": "2026-05-02T14:30:00.123Z",
  "level": "INFO",
  "service": "order-service",
  "trace_id": "abc123def456",
  "span_id": "a1b2c3d4",
  "message": "Order created successfully",
  "user_id": "usr_789",
  "order_id": "ord_456",
  "duration_ms": 42,
  "http": {
    "method": "POST",
    "path": "/api/v1/orders",
    "status": 201,
    "ip": "203.0.113.1"
  },
  "error": null
}
```

### 4.2 Log Levels in Practice
| Level | Meaning | Action |
|-------|---------|--------|
| ERROR | Something is broken right now | Alert, page on-call |
| WARN | Something might break soon | Dashboard, investigation if recurring |
| INFO | Normal operation, key events | Search, debugging |
| DEBUG | Detailed flow (off in prod) | On-demand debugging |

### 4.3 Centralized Logging Stack Comparison
| Stack | Strengths | Weaknesses | Best For |
|-------|-----------|------------|----------|
| **ELK** | Full-text search, Kibana dashboards | Heavy, expensive at scale | Small-medium teams |
| **Loki + Grafana** | Cheap, native Prometheus integration | Limited full-text search | Prometheus ecosystem |
| **SigNoz** | OpenTelemetry-native, metrics+logs+tracing | Smaller community | OTel shops |
| **Datadog** | All-in-one, best UX | $$$ per host | Budget-unconstrained |

### 4.4 Logging Anti-Patterns
- ❌ Logging sensitive data (passwords, tokens, PII)
- ❌ String interpolation instead of structured fields
- ❌ Logging every single request at INFO level in a high-throughput service
- ❌ No log rotation or retention policy
- ❌ Different format per service → no unified query

---

## 5. Distributed Tracing

### 5.1 OpenTelemetry Setup (minimal)
```python
# Python — FastAPI auto-instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

FastAPIInstrumentor.instrument_app(app)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
# See full integration in tracing checklist
```

```javascript
// Node.js — Express auto-instrumentation
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');

const provider = new NodeTracerProvider();
provider.register();
registerInstrumentations({
  instrumentations: [new ExpressInstrumentation()],
});
```

### 5.2 W3C Trace Context (Traceparent Header)
```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
  └─ version ─└───── trace_id (16 bytes) ────└──── span_id (8 bytes) ──└─ flags
```

- **flag `01`**: sampled; **`00`**: not sampled
- Every service must **propagate** the traceparent header downstream
- Failure to propagate = broken trace

### 5.3 Sampling Strategies
| Strategy | Usage | Cost |
|----------|-------|------|
| **Head-based** (fixed rate 1-10%) | Default in most SDKs | Predictable, low |
| **Head-based** (rate limiting per root) | High-throughput services | Moderate |
| **Tail-based** (sample traces with errors) | Error analysis | High (buffering) |
| **Probabilistic** (consistent hash of trace_id) | Multi-service consistency | Low |

### 5.4 Span Design Guidelines
- Each **external call** (HTTP, DB, queue) should be a child span
- Add **attributes** that help debugging: `db.statement`, `http.url`, `error.message`
- Set span **status** correctly: `STATUS_OK` / `STATUS_ERROR`
- Never create spans for in-memory operations (< 1ms) — noise

---

## 6. Alerting: Reduce Noise, Increase Signal

### 6.1 Alert Severity Levels
| Level | Response Time | Example |
|-------|---------------|---------|
| **P0 (Critical)** | < 5 min | Service down, data loss |
| **P1 (High)** | < 15 min | High error rate, latency spike |
| **P2 (Medium)** | < 1 hour | High saturation, approaching limits |
| **P3 (Low)** | < 1 day | Disk space > 80%, cert expiring |

### 6.2 Alert Fatigue Prevention
1. **Every alert must be actionable** — if the recipient can't take action, it's a dashboard panel, not an alert
2. **Use `for:` duration** — transient spikes < 5 minutes are noise
3. **Add runbook links** — every alert should point to a runbook
4. **Alert on SLO burn rate**, not raw thresholds when possible
5. **Weekly alert review** — tune or delete noisy alerts

### 6.3 Multi-Window, Multi-Burn-Rate Alerting
```
Idea: Alert when error budget is burning too fast over BOTH a short AND long window

  - Short window (5m): catches fast problems
  - Long window (1h): confirms it's not just a transient spike

Example: Alert if (error_rate_5m > 0.1%) AND (error_rate_1h > 0.05%)

This prevents false positives from brief blips while catching real trends.
```

### 6.4 Canonical Alert Rules (Prometheus/AlertManager)

```yaml
groups:
  - name: service-level
    rules:
      - alert: HighErrorRate
        expr: |
          (
            rate(http_requests_total{status=~"5.."}[5m])
            /
            rate(http_requests_total[5m])
          ) > 0.05
        for: 5m
        labels:
          severity: p1
          team: backend
        annotations:
          summary: "Service {{ $labels.service }} error rate {{ $value | humanizePercentage }}"
          runbook: "https://runbook.example.com/high-error-rate"

      - alert: HighP99Latency
        expr: |
          histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: p1
        annotations:
          summary: "p99 latency {{ $value | humanizeDuration }} for service {{ $labels.service }}"

      - alert: DiskSpaceLow
        expr: |
          (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        labels:
          severity: p2
        annotations:
          summary: "Disk {{ $labels.mountpoint }} on {{ $labels.instance }} has {{ $value | humanizePercentage }} free"

  - name: slo-burn-rate
    rules:
      - alert: SLOSlowBurn
        expr: |
          (
            1 - (sum(rate(http_requests_total{status!~"5.."}[30d])) / sum(rate(http_requests_total[30d])))
          ) < 0.995
        labels:
          severity: p0
        annotations:
          summary: "SLO breach risk: 30-day availability is {{ $value | humanizePercentage }}"
```

---

## 7. On-Call Best Practices

### 7.1 Incident Severity and Response

**P0 Incident (SEV-1) — Service outage or data loss**
```
1. Alert triggered → on-call acknowledged within 5 min
2. IC (Incident Commander) declared — first responder becomes IC
3. IC's ONLY job: coordinate, not debug
4. Scribe starts logging timeline
5. Every 15 min: status update to stakeholders
6. Fix applied → verify → declare resolved
7. < 48h: postmortem drafted
```

**P1 Incident (SEV-2) — Partial outage, high error rate**
```
1. Acknowledge within 15 min
2. Investigate and fix
3. Postmortem optional if root cause is obvious
```

### 7.2 Handover Template
```
On-Call Handover — YYYY-MM-DD

Current state:
  - Active incidents: None / [list]
  - Pending items: [backlog, known issues]

Dashboard status:
  - SLO: 99.9% ✅ / 99.7% ⚠️ / 99.0% ❌
  - Queue depth: normal / elevated / critical
  - Deploy in progress: yes/no

Known issues:
  - Service X has memory leak, restart due at ~3am
  - Database migration scheduled for tomorrow 2am

Tip from previous shift: "If you see alert Y, restart service Z first — it's a known 
                       issue, fix is in next release."
```

---

## 8. Dashboards: The Art of Visual Debugging

### 8.1 Dashboard Design Principles
1. **One screen, one story** — Each dashboard answers ONE question
2. **Left to right, top to bottom** — Most important in top-left
3. **Use meaningful time ranges** — 1h for debugging, 7d for trends, 30d for SLOs
4. **Every panel must have a clear unit** — seconds, requests/s, percentage
5. **Avoid chart junk** — no 3D effects, no unnecessary legends

### 8.2 Standard Dashboard Layouts

**Service Overview** (for on-call)
```
Row 1:                [LATENCY: p50/p95/p99]    [ERROR RATE %]        [THROUGHPUT]
Row 2: (per endpoint) [latency per endpoint]    [error per endpoint]  [rate per endpoint]
Row 3:                [CPU %]                   [Memory GB]           [GC pause]
Row 4: (external)     [DB latency]              [Cache hit rate]      [Queue depth]
```

**SLO Dashboard** (for management)
```
Row 1: [SLO compliance 30d] [Error budget remaining] [Burn rate]
Row 2: [SLI trend per service] [SLA compliance] [Recent breaches]
```

**Infrastructure** (for ops)
```
Row 1: [CPU by host]    [Memory by host]    [Disk by host]
Row 2: [Network I/O]    [Disk I/O]          [TCP connections]
Row 3: [Node health]    [Pod restarts]      [Certificate expiry]
```

### 8.3 Grafana Best Practices
- Use **variables** (cluster, service, host) — never hardcode
- Use **repeating panels** for per-service/per-host breakdowns
- Use **annotations** to mark deploys and incidents
- Set **min step** relative to time range (1m for 1h, 5m for 7d, 1h for 30d)
- **Alert annotations**: Grafana can push to AlertManager → pagers

---

## 9. Tool-Specific Guides

### 9.1 Prometheus Optimization
```yaml
# prometheus.yml — production-scale config

global:
  scrape_interval: 15s          # default, adjust per target
  evaluation_interval: 15s      # rule evaluation interval
  scrape_timeout: 10s

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)

# Storage: 15 days local retention
# Remote write: Thanos receiver or Cortex for long-term
```

### 9.2 OpenTelemetry Collector Pipeline
```yaml
# otel-collector-config.yaml

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 8192
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  filter:
    error_mode: ignore
    traces:
      span:
        - 'attributes["http.target"] == "/health"'
  attributes:
    actions:
      - key: environment
        value: production
        action: upsert

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp:
    endpoint: tempo.example.com:4317
    tls:
      insecure: false
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, filter, batch, attributes]
      exporters: [otlp]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [loki]
```

---

## 10. Appendix: Runbook Templates

### 10.1 Generic Incident Runbook
```markdown
# Runbook: [Alert Name]

## Severity: P0/P1/P2/P3
## Team: [service team]

### Step 1: Acknowledge
- [ ] Confirm you are the on-call (check PagerDuty/OpsGenie)
- [ ] State "I am the IC" in the incident channel

### Step 2: Assess impact
- [ ] Check service dashboard: [link]
- [ ] Check SLO dashboard: [link]
- [ ] Is there a recent deploy? Check #deploy channel

### Step 3: Mitigate
- **First action**: Try rollback if recent deploy
- **Second action**: [service-specific mitigation commands]

### Step 4: Fix
- [ ] Identify root cause
- [ ] Create hotfix PR
- [ ] Merge and deploy

### Step 5: Resolve
- [ ] Verify in staging
- [ ] Deploy to prod
- [ ] Confirm metrics return to baseline
- [ ] Declare resolved with timestamp
```

### 10.2 Observability Audit Checklist
```
□ Every service exposes /metrics endpoint
□ Every service exports (at minimum): request rate, error rate, latency histogram
□ Every service is registered in Prometheus service discovery
□ Logs are structured JSON, centrally collected
□ Distributed tracing is instrumented (or planned) for all critical paths
□ Every P0/P1 alert has an associated runbook
□ Runbooks are tested at least quarterly
□ Dashboard links are in the on-call rotation handbook
□ Log retention policy is defined and enforced
□ Metrics retention: < 7 days local Prometheus, > 30 days remote storage
```
