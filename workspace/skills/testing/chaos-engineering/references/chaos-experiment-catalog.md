# Chaos Experiment Catalog

## 30 Experiments by Category

### Infrastructure (Start Here)

```yaml
# 1. Pod Kill (Basic)
# Kill single pod, verify auto-recovery
hypothesis: "Pod recovery completes within 30s with zero user impact"
blast_radius: "1 pod (out of min 20)"
tools: [litmus, chaos-mesh]
```

```yaml
# 2. Node Failure
# Drain a Kubernetes node
hypothesis: "Workloads reschedule on remaining nodes within 2 minutes"
blast_radius: "1 node (out of 5+ available nodes)"
tools: [litmus]
```

```yaml
# 3. AZ Failure Simulation
# Block all traffic to/from pods in one AZ
hypothesis: "Service remains available with < 1% error rate when one AZ is lost"
blast_radius: "All pods in one availability zone"
prerequisites: "Must have multi-AZ deployment"
tools: [chaos-mesh, custom iptables]
```

```yaml
# 4. CPU Saturation
# Saturate CPU to 80% on target pods
hypothesis: "CPU auto-scaling triggers within 5 minutes, latency degrades < 2x"
blast_radius: "2 pods"
tools: [litmus, stress-ng]
```

```yaml
# 5. Memory Pressure
# Fill memory to 80% on target pods
hypothesis: "Memory OOM killer does not kill critical containers, HPA scales"
blast_radius: "2 pods"
tools: [litmus, stress-ng]
```

```yaml
# 6. Disk I/O Saturation
# Inflate disk IOPS on database nodes
hypothesis: "Query p99 latency degrades gracefully, no connection drops"
blast_radius: "1 DB replica"
tools: [fio, stress-ng]
```

```yaml
# 7. Network Packet Loss (1%)
hypothesis: "TCP retransmission handles 1% loss, p99 latency stays < 500ms"
blast_radius: "Critical service pods"
tools: [tc, chaos-mesh]
```

### Service Degradation

```yaml
# 8. Inter-Service Latency (+500ms)
hypothesis: "Circuit breaker opens within 10s, fallback is served"
blast_radius: "1 upstream dependency for 1 service"
tools: [chaos-mesh, istio fault injection]
```

```yaml
# 9. DNS Failure
hypothesis: "Service locally caches DNS, continues without interruption"
blast_radius: "All pods with external DNS dependencies"
tools: [iptables, /etc/hosts manipulation]
```

```yaml
# 10. Rate Limited Upstream
# Simulate 429 response from a dependency
hypothesis: "Client implements exponential backoff + circuit breaker"
blast_radius: "1 external dependency"
tools: [envoy/mock server]
```

```yaml
# 11. HTTP 500 from Service
hypothesis: "Caller handles 500s gracefully, retries with backoff"
blast_radius: "1 service endpoint"
tools: [chaos-mesh, custom proxy]
```

```yaml
# 12. TLS/SSL Certificate Expired
hypothesis: "Certificate expires gracefully, system alerts on T-30d"
blast_radius: "1 service endpoint"
tools: [certificate date manipulation]
```

```yaml
# 13. gRPC Connection Timeout
hypothesis: "gRPC client timeout configured, failover to alternate endpoint"
blast_radius: "1 gRPC dependency"
tools: [tc, iptables, chaos-mesh]
```

### Data Plane

```yaml
# 14. Redis Cache Corruption
# Set wrong values in cache keys
hypothesis: "Cache miss triggers DB fallback, data integrity maintained"
blast_radius: "1 cache key set"
tools: [redis-cli SET with bad data]
```

```yaml
# 15. DB Connection Pool Exhaustion
# Open connections until pool is full
hypothesis: "Connection pool has backpressure, queue depth is bounded"
blast_radius: "1 DB connection pool"
tools: [pgbouncer/pgpool simulation]
```

```yaml
# 16. Kafka Consumer Lag (Simulate)
# Pause consumer processing, create large lag
hypothesis: "Consumer autoscaling catches up within 5 minutes"
blast_radius: "1 Kafka consumer group"
tools: [kafka consumer pause]
```

```yaml
# 17. S3/Object Storage Unreachable
hypothesis: "CDN fallback or cached version served, writes queued"
blast_radius: "1 storage bucket (via network rules)"
tools: [S3 bucket policy, iptables]
```

```yaml
# 18. Dead Letter Queue Filled
hypothesis: "Alert fires on DLQ threshold, no message loss"
blast_radius: "1 message queue"
tools: [script to flood DLQ]
```

```yaml
# 19. Database Replication Lag (>30s)
hypothesis: "Read replicas lag gracefully, stale reads are acceptable"
blast_radius: "DB replica"
tools: [pg_sleep injection, DB load simulation]
```

```yaml
# 20. Feature Flag Flip (wrong value)
hypothesis: "Feature flag system supports instant rollback"
blast_radius: "1 feature flag"
tools: [launchdarkly/split SDK test]
```

### Compound and Advanced

```yaml
# 21. Two Simultaneous Pod Failures
hypothesis: "K8s ReplicaSet recreates both pods, no cumulative impact"
blast_radius: "2 pods in same deployment"
tools: [litmus sequential kill]
```

```yaml
# 22. Cascading Failure: DB Slow → Cache Miss → DB Slower
hypothesis: "Circuit breaker prevents cascading, degraded mode activates"
blast_radius: "Entire service chain"
tools: [combined: db latency + cache invalidation]
```

```yaml
# 23. Config Deployed to Wrong Region
hypothesis: "Config validation prevents cross-region deployment"
blast_radius: "Production region"
tools: [config management API manipulation]
```

```yaml
# 24. Dependency Chain: A fails → B fails → C fails
hypothesis: "Bulkhead pattern isolates failures per service"
blast_radius: "Service chain A-B-C"
tools: [multi-service chaos orchestration]
```

```yaml
# 25. Blast Radius Limit Test
# What happens if chaos experiment exceeds blast radius?
hypothesis: "Chaos platform enforces blast radius limits correctly"
blast_radius: "Chaos platform itself"
tools: [litmus/chaos-mesh admin API]
```

```yaml
# 26-30: Customer Journey Failures
# e.g., "Checkout flow with slow payment" (customer-facing)
# e.g., "Login flow with broken SSO" (customer-facing)
# e.g., "Search with broken Elasticsearch" (customer-facing)
```

## Experiment Selection Matrix

```
  Choose experiments based on:
  
  ┌─────────────┬──────────────┬──────────────┬──────────────┐
  │             │ NEW Service  │ Established  │ Critical     │
  │             │              │ Service      │ Service      │
  ├─────────────┼──────────────┼──────────────┼──────────────┤
  │ First Month │ 1-3 (infra)  │ 4-7 (degrd)  │ 1-3 (infra)  │
  │             │              │              │ 8-13 (degrd) │
  ├─────────────┼──────────────┼──────────────┼──────────────┤
  │ Monthly     │ 1-3 (infra)  │ 1-7 (infra)  │ 14-20 (data) │
  │             │              │ 8-13 (degrd) │ + rotation   │
  ├─────────────┼──────────────┼──────────────┼──────────────┤
  │ Quarterly   │ Full suite   │ Full         │ Full suite   │
  │             │ level 1-2    │ suite 1-20   │ + compound   │
  └─────────────┴──────────────┴──────────────┴──────────────┘
```
