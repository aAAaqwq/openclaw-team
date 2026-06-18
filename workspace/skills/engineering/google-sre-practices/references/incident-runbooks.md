# Incident Runbook Templates

## Runbook: High Error Rate (>1% 5xx)

```
Classification: P0 (Page)
Detection: Prometheus → AlertManager → PagerDuty/Telegram
SLO Impact: Yes (availability SLO at risk)

### Immediate Actions (0-5 min)
1. ACKNOWLEDGE the alert
2. CHECK current error rate:
   `curl -s "http://your-service/metrics" | grep http_requests_total`
3. CHECK recent deploy:
   `kubectl rollout history deployment/your-service`
4. ROLLBACK if deploy happened in last 30 min:
   `kubectl rollout undo deployment/your-service`

### Diagnostic Actions (5-15 min)
1. CHECK upstream dependencies:
   `curl -s "http://dependency/health" | jq .`
2. CHECK database:
   `kubectl exec pod/db-0 -- pg_isready`
3. CHECK config changes:
   `kubectl describe configmap your-service-config`
4. CHECK recent logs:
   `stern your-service --since 10m | grep ERROR | head -50`

### Mitigation
- If database slow → scale up DB or use read replicas
- If upstream failing → enable circuit breaker or fallback
- If code bug → rollback + create minimal reproduction
- If config error → revert config change

### Escalation
- 15 min: Page senior engineer
- 30 min: Declare incident, engage incident commander
- 60 min: Escalate to engineering director

### Post-Incident
1. Notify stakeholders through status page
2. File postmortem within 48 hours
3. Update monitoring: "Why didn't we catch this earlier?"
```

## Runbook: High Latency (p99 > 500ms)

```
Classification: P1 (Ticket) or P0 if user-facing

### Check
1. WHERE is the latency? (use tracing)
   `kubectl exec pod/app -- curl -s localhost:16686/api/traces`
2. Database query slowness:
   `SHOW FULL PROCESSLIST` — look for long-running queries
3. Resource saturation:
   `top`, `iostat`, `vmstat` on affected pods
4. Garbage collection (JVM/Node/Go):
   Check GC metrics from runtime

### Common Fixes
- Missing index → create and add migration
- N+1 queries → eager loading / batch query
- Lock contention → reduce transaction scope
- GC pressure → increase heap / reduce allocations
- Hot shard → rebalance / split shards
```

## Runbook: Service Unreachable (Connection Refused / Timeout)

```
Classification: P0

### Check
1. IS the process running?
   `kubectl get pods -l app=your-service`
2. WAS it OOMKilled?
   `kubectl describe pod <pod> | grep -A5 "State:"`
3. WAS there a readiness probe failure?
   `kubectl describe pod <pod> | grep Readiness`
4. Pod logs indicate crash?
   `kubectl logs --previous <pod>`

### Quick Recovery
- If crash loop: check `kubectl rollout history` and rollback
- If OOM: `kubectl set resources deployment/your-service --limits memory=2Gi`
- If hanging: `kubectl delete pod <pod>` (K8s recreates it)

### Root Cause Analysis
- Review recent code changes (git log --oneline)
- Review recent config changes
- Review dependency version changes
- Check if traffic spike triggered resource exhaustion
```
