# Chaos Engineering Experiment Templates

## Template: Pod Kill Experiment

```yaml
# chaos-experiment-kill-pod.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: pod-kill-experiment
spec:
  appinfo:
    appns: "default"
    applabel: "app=your-service"
    appkind: "deployment"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-kill
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "60"           # Run for 60 seconds
            - name: CHAOS_INTERVAL
              value: "10"            # Kill every 10 seconds
            - name: FORCE
              value: "true"          # Force kill (-9 vs -15)
        probe:
          - name: "check-service-health"
            type: "httpProbe"
            httpProbe/inputs:
              url: "http://your-service:8080/health"
              insecure: true
            mode: "Continuous"
            runProperties:
              probeTimeout: 5
              interval: 2
              retry: 1
              probePollingInterval: 2
```

## Template: Network Latency Injection

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: network-latency-experiment
spec:
  appinfo:
    appns: "default"
    applabel: "app=your-service"
    appkind: "deployment"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-network-latency
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "120"
            - name: NETWORK_LATENCY
              value: "1000"          # 1000ms extra latency
            - name: JITTER
              value: "100"           # +/- 100ms jitter
        probe:
          - name: "check-p99-latency"
            type: "promProbe"
            promProbe/inputs:
              endpoint: "http://prometheus:9090"
              query: "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[1m]))"
            mode: "Edge"
            runProperties:
              probeTimeout: 30
              interval: 10
              retry: 2
```

## Template: Database Failure Simulation

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: db-failure-experiment
spec:
  appinfo:
    appns: "database"
    applabel: "app=postgres"
    appkind: "statefulset"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-kill
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "30"            # Kill one replica for 30s
            - name: TARGET_POD
              value: "postgres-1"    # Kill the replica, not the primary
            - name: SEQUENTIAL
              value: "true"
        probe:
          - name: "check-app-health-after-restore"
            type: "k8sProbe"
            mode: "OnChaos"
            runProperties:
              probeTimeout: 10
        probes:
          - name: "check-read-path"
            type: "httpProbe"
            httpProbe/inputs:
              url: "http://your-service:8080/api/read"
            mode: "Continuous"
```

## Minimal Chaos Experiment (Quick Test)

```bash
#!/bin/bash
# minimal-chaos.sh — Quick chaos experiment for confidence

# 1. Define the hypothesis
echo "Hypothesis: Service handles single pod failure with < 1s recovery"

# 2. Measure steady state
BASELINE=$(curl -s -o /dev/null -w "%{http_code}" http://your-service/health)
echo "Steady state: HTTP $BASELINE"

# 3. Introduce failure
kubectl delete pod -l app=your-service --now
echo "Pod killed at $(date)"

# 4. Wait and measure recovery
sleep 10
RECOVERED=$(curl -s -o /dev/null -w "%{http_code}" http://your-service/health)
echo "After recovery: HTTP $RECOVERED"

# 5. Evaluate hypothesis
if [ "$RECOVERED" == "200" ]; then
  echo "✅ PASS: Service recovered within 10 seconds"
else
  echo "❌ FAIL: Service did not recover — investigate"
fi
```

## Chaos Experiment Checklist

```
Before running any chaos experiment:
□ Defined steady state metric (latency, error rate, availability)
□ Written hypothesis with expected outcome
□ Set blast radius limits (max 1 pod, max 2 instances)
□ Set auto-rollback condition (error rate > 2x baseline)
□ Communicated experiment to team (slack/email)
□ Scheduled during low-traffic window
□ Designated IC for experiment
□ Rollback plan ready (just in case)
```
