# Alert Rules Examples (Prometheus)

## Availability Alert (P0)

```yaml
groups:
  - name: availability
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) 
          / 
          sum(rate(http_requests_total[5m])) > 0.01
        for: 2m
        labels:
          severity: page
          pagerduty: p0
        annotations:
          summary: "Error rate > 1% for {{ $labels.service }}"
          runbook: "high-error-rate.md"
```

## Latency Alert (P0)

```yaml
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, 
            rate(http_request_duration_seconds_bucket[5m])
          ) > 0.5
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "p99 latency > 500ms for {{ $labels.service }}"
```

## Saturation Alert (P1)

```yaml
      - alert: HighCPU
        expr: |
          rate(container_cpu_usage_seconds_total[5m]) 
          / 
          container_spec_cpu_quota / container_spec_cpu_period > 0.8
        for: 10m
        labels:
          severity: ticket
        annotations:
          summary: "CPU > 80% for {{ $labels.pod }}"
          runbook: "check-saturation.md"
```

## Error Budget Burn Rate Alert (P0)

```yaml
      - alert: ErrorBudgetBurningFast
        expr: |
          (
            (1 - (
              sum(rate(http_requests_total{status!~"5.."}[1h]))
              /
              sum(rate(http_requests_total[1h]))
            ))
            > 0.001  # 0.1% error rate in 1h
          )
          and ignoring()
          (
            (
              # 1h burn rate
              (1 - (
                sum(rate(http_requests_total{status!~"5.."}[1h]))
                /
                sum(rate(http_requests_total[1h]))
              ))
              *
              30 * 24  # budget period in hours
            )
            > 0.1  # > 10% budget burned in 1h
          )
        labels:
          severity: page
        annotations:
          summary: "Error budget burning > 10%/hour"
```

## Certificate Expiry (P2)

```yaml
      - alert: CertificateExpiry
        expr: |
          probe_ssl_earliest_cert_expiry - time() < 604800  # 7 days
        labels:
          severity: ticket
        annotations:
          summary: "TLS cert for {{ $labels.target }} expires in < 7 days"
```

## No Data Alert (P0)

```yaml
      - alert: NoData
        expr: |
          absent(http_requests_total) == 1
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "No metrics data received for 5+ minutes — system may be down"
```
