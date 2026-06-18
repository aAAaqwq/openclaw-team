---
name: debugging-mastery
description: >
  Systematic debugging methodology covering root cause analysis, log-based
  debugging, production debugging, memory leak diagnosis, deadlock detection,
  performance anomaly investigation, and reproducible bug reproduction.
  Distilled from real experience at Google, DeepMind, ByteDance, and Huawei.

  USE WHEN: investigating production incidents, debugging hard-to-reproduce
  bugs, analyzing crash dumps, finding race conditions, diagnosing memory
  leaks, debugging performance regressions, or any situation requiring
  systematic root cause analysis. Triggers on "debugging", "root cause",
  "bug", "crash", "segfault", "deadlock", "race condition", "memory leak".
---

# Debugging Mastery

> **Source**: "Debugging" (David Agans) + Google/DeepMind/ByteDance production
> debugging experience + years of midnight production incidents
> **Core Philosophy**: "Debugging is the art of systematically testing hypotheses
> until the root cause is found. It is NOT randomly changing things hoping."

## The Nine Indispensable Rules

From David Agans' "Debugging" — the debugging bible:

```
  1. Understand the system
  2. Make it fail
  3. Quit thinking and look
  4. Divide and conquer
  5. Change one thing at a time
  6. Keep an audit trail
  7. Check the plug
  8. Get a fresh view
  9. If you didn't fix it, it ain't fixed
```

---

## 1. The Debugging Workflow

### 1.1 Systematic RCA Flow

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Step 1: REPRODUCE                                            │
  │     Can you make it happen?                                   │
  │     If not: this is the first problem to solve                │
  │                                                                │
  │  Step 2: ISOLATE                                               │
  │     Binary search through the system to find the component    │
  │     Remove variables: isolate the MINIMAL reproducing case    │
  │                                                                │
  │  Step 3: MEASURE                                               │
  │     Log everything. Add MORE logging if needed.               │
  │     "The resolution of your debugging is limited by the       │
  │      resolution of your instrumentation"                      │
  │                                                                │
  │  Step 4: HYPOTHESIZE                                           │
  │     Form a specific, testable hypothesis                      │
  │     Bad: "Maybe there's a memory issue"                       │
  │     Good: "The cache eviction runs on the wrong goroutine"    │
  │                                                                │
  │  Step 5: TEST THE HYPOTHESIS                                   │
  │     If hypothesis is wrong → return to Step 3                  │
  │     If hypothesis is right → FIX it                           │
  │                                                                │
  │  Step 6: VERIFY THE FIX                                        │
  │     Run the reproduction case again (it should pass)          │
  │     Run the full test suite                                    │
  │     Add the reproduction case as a REGRESSION TEST             │
  └──────────────────────────────────────────────────────────────┘
```

### 1.2 The Binary Search Debugging Technique

```
  Step through the system components:

  ┌──────────────────────────────────────────────────────────────┐
  │  Input → [A] → [B] → [C] → [D] → [E] → Output              │
  │                                                               │
  │  Check output at C:                                           │
  │  ✅ C passes → bug is in D or E                              │
  │  ❌ C fails  → bug is in A, B, or C                         │
  │                                                               │
  │  Repeat: check at B (or D, depending on result)              │
  │  Continue until you've isolated the single component         │
  │                                                               │
  │  This is O(log n) — exponentially faster than linear scan    │
  └──────────────────────────────────────────────────────────────┘
```

---

## 2. Log-Based Debugging

### 2.1 Structured Logging for Debuggability

```typescript
// ❌ Bad: unstructured, no context
console.log('Order processed');
console.log(`Error: ${err}`);

// ✅ Good: structured, searchable, contextual
logger.info('order.processed', {
    orderId: order.id,
    userId: order.userId,
    duration: Date.now() - start,
    items: order.items.length,
    total: order.total,
});

logger.error('order.processing_failed', {
    orderId,
    errorCode: err.code,
    errorMessage: err.message,
    stackTrace: err.stack,
    // Include relevant state at failure point
    currentState: { status, step, retryCount },
});
```

### 2.2 Log Levels for Debugging

```
  ┌──────────┬────────────────────────────────────────────────────┐
  │ TRACE    │ Every function entry/exit (noisy, turn off by     │
  │          │ default)                                           │
  ├──────────┼────────────────────────────────────────────────────┤
  │ DEBUG    │ Detailed state dumps, intermediate values          │
  │          │ Enable when investigating specific issue           │
  ├──────────┼────────────────────────────────────────────────────┤
  │ INFO     │ Normal operations, key business events             │
  │          │ "Order created", "Payment confirmed"               │
  ├──────────┼────────────────────────────────────────────────────┤
  │ WARN     │ Anomalous but non-critical                         │
  │          │ "Retry attempt 2/3", "Cache miss"                  │
  ├──────────┼────────────────────────────────────────────────────┤
  │ ERROR    │ Something is broken — needs investigation          │
  │          │ "Database connection failed", "Timeout exceeded"   │
  └──────────┴────────────────────────────────────────────────────┘
```

### 2.3 Finding the Needle in the Haystack

```bash
# Find all ERROR lines in last hour
journalctl -u your-service --since "1 hour ago" | grep ERROR

# Follow logs in real-time for a specific request
tail -f /var/log/app.log | grep "order-123"

# Extract structured logs for a trace ID
cat app.log | grep "trace_id=abc123" | jq .

# Show how long something took (timing from structured logs)
cat app.log | grep "order.processed" | awk '{print $2}' | sort | uniq -c

# Count error types
grep ERROR app.log | grep -oP '"errorCode":"[^"]*"' | sort | uniq -c | sort -rn

# Find slow operations (duration > 1000ms)
cat app.log | jq 'select(.duration > 1000)' | jq -r '.message + ": " + (.duration|tostring)'
```

---

## 3. Production Debugging

### 3.1 The Production Debugging Checklist

```
  □ Is it happening NOW?
     → Check monitoring dashboard (latency, error rate, saturation)
     → Check alerting for related incidents
     → Check recent deployments/configuration changes
  
  □ Is it a known issue?
     → Search internal KB / runbooks / postmortems
     → Search Slack history for similar symptoms
     → Check GitHub issues / bug tracker
  
  □ Can we observe the problem?
     → Check logs (see section 2)
     → Check metrics (CPU, memory, disk, network, GC)
     → Check distributed traces (Jaeger/Tempo)
  
  □ Can we reproduce it in staging?
     → Same deployment version
     → Same data or data pattern
     → Same traffic pattern
     → If not reproducible → add more instrumentation
```

### 3.2 Safe Production Debugging

```bash
# IMPORTANT: Never SSH into production unless absolutely necessary
# Try these first:

# 1. Check monitoring (Grafana, Datadog, etc.)
# 2. Check logs (Loki, Splunk, ELK)
# 3. Check traces (Jaeger, Tempo)
# 4. Check health endpoints
curl -s http://service:8080/health | jq .
curl -s http://service:8080/metrics | head -50
curl -s http://service:8080/debug/vars  # Go expvar

# 5. Only if above fails → limited safe access
kubectl exec -it pod/app -- /bin/sh -c "curl localhost:8080/debug/pprof/heap"

# NEVER modify production data
# NEVER kill/restart services without understanding the impact
# ALWAYS have a rollback plan before making any change
```

### 3.3 Postmortem-Driven Debugging

When you encounter a bug, ask:

```
  ❓ "What type of bug is this?"
     - Logic bug (wrong condition, missing case)
     - Concurrency bug (race, deadlock, stale data)
     - Data bug (corruption, encoding, validation)
     - Configuration bug (wrong env, wrong feature flag)
     - Dependency bug (upstream change, API drift)
     - Resource bug (memory, file handles, connections)

  ❓ "Does this bug belong to a known category?"
     If yes → apply known pattern fix
     If no  → write a new postmortem entry about this pattern
```

---

## 4. Debugging by Bug Type

### 4.1 Concurrency / Race Conditions

```go
// Symptom: intermittent crashes, wrong values, data corruption
// Root cause detection:

// Go race detector
go test -race ./...
go run -race ./...

// The output pinpoints the exact lines where race occurs:
// WARNING: DATA RACE
// Read at 0x00c00028c010 by goroutine 7:
//   main.updateCounter()
//       main.go:42 +0x39
// Previous write at 0x00c00028c010 by goroutine 5:
//   main.incrementCounter()
//       main.go:38 +0x58
```

```javascript
// Node.js: debug async flow
// Use --async-stack-traces (Node 14+)
node --async-stack-traces app.js

// Track promise chains
Promise.config({
    warnings: true,
    longStackTraces: true
});
```

### 4.2 Memory Leaks

```
  Symptoms: RAM grows over time, GC overhead increases, OOM crashes

  Debug flow:
  1. Take a heap snapshot (time 0)
  2. Run operation n times
  3. Take another heap snapshot
  4. Compare: what grows?
     - Growing maps (map without cleanup) ← common
     - Growing slices (append without limit) ← common
     - Event listeners without removal
     - Closed-over variables in callbacks
     - Cached objects with no eviction
```

### 4.3 Deadlocks

```go
// Go: detect deadlocks in tests
go test -v -timeout=5s ./...

// Go race detector catches lock ordering issues
go test -race ./...

// Debug deadlock: get all goroutine stacks
import "net/http/pprof"

func main() {
    // ...
}

// Then get stacks:
curl http://localhost:6060/debug/pprof/goroutine?debug=2

// Look for:
// goroutine 1 [chan receive]:
//     main.waitForResult()
//         main.go:25 +0x45
// goroutine 2 [chan receive]:
//     main.waitForResult()
//         main.go:25 +0x45
// → Two goroutines waiting on each other = deadlock
```

### 4.4 Heisenbugs (Bugs that Disappear When You Look)

```
  Symptoms:
  - Adding a log line "fixes" the bug
  - Debugger breakpoints "fix" the bug
  - Bug only happens in production, never staging

  Causes:
  - Timing-dependent bugs (race, channel, timeout)
  - Buffer flush / log delay timing
  - Heisenberg uncertainty principle of debugging:
    "The act of observing changes the behavior"

  Debug strategies:
  1. Use structured logging (less I/O impact than console.log)
  2. Use tcpdump / strace (observe without modifying)
  3. Add counters instead of log lines:
     metrics.counter('bug_scenario.hit').inc()
  4. Capture state, don't log it:
     Take periodic snapshots → analyze offline
```

### 4.5 Non-Deterministic Bugs

```
  Symptoms:
  - "Sometimes it works, sometimes it doesn't"
  - "I can't reproduce it"
  - "It only happens on Tuesdays"

  The 5 most common causes of non-determinism:
  1. Uninitialized memory → read before write
  2. Map iteration order (random in many languages)
  3. Goroutine/thread scheduling order
  4. Network timing / retry interactions
  5. Hash collision / random seed
```

---

## 5. Tools Arsenal

### 5.1 Quick Reference by Problem

```
  ┌────────────────────┬──────────────────────────────┐
  │ Problem            │ Tool                         │
  ├────────────────────┼──────────────────────────────┤
  │ CPU spike          │ pprof, perf top, top -H      │
  │ Memory leak        │ pprof heap, heap dump        │
  │ Deadlock           │ goroutine stack dump, lsof    │
  │ Race condition     │ race detector, tsan          │
  │ Slow DB query      │ EXPLAIN ANALYZE, pg_stat_activity│
  │ High GC            │ gc tracer, allocation profiler│
  │ Network issue      │ tcpdump, strace, ss, iperf   │
  │ Disk I/O           │ iostat, iotop, fio           │
  │ File handle leak   │ lsof -p PID, /proc/PID/fd    │
  │ Config wrong       │ diff config files, env vars  │
  │ SSL/TLS            │ openssl s_client, ssllabs     │
  └────────────────────┴──────────────────────────────┘
```

### 5.2 Universal Debugging Commands

```bash
# Process status
top -H -p <PID>           # Show per-thread CPU
strace -p <PID> -e trace=network  # Trace syscalls
lsof -p <PID>             # Open file descriptors
ls /proc/<PID>/fd/ | wc -l       # Count open files

# Network
ss -tulpn                  # List listening ports
tcpdump -i eth0 port 8080 -w capture.pcap  # Packet capture

# Disk
iostat -x 1                # Disk I/O stats
df -h                      # Disk space
du -sh /path               # Directory size

# System
dmesg | tail -20           # Kernel messages (OOM kills!)
free -m                    # Memory
ulimit -a                  # Resource limits
```

---

## 6. The Debugging Mindset

### 6.1 What Great Debuggers Do Differently

```
  As a junior dev, I'd panic and change random things.
  As a senior engineer, I use the scientific method.

  ┌──────────────────────────────────────────────────────────────┐
  │  Junior Engineer:                                            │
  │  "Oh no! The database is failing! Let me restart it!"       │
  │  → Restarts the DB → "It works now!"                        │
  │  → Same bug happens tomorrow                                 │
  │                                                               │
  │  Senior Engineer:                                            │
  │  "The database is failing. Let me check the logs."          │
  │  → Finds "disk space 100% full"                             │
  │  → Cleans up old data, sets up disk alert                   │
  │  → Bug never comes back                                      │
  └──────────────────────────────────────────────────────────────┘
```

### 6.2 The Two-Day Rule

```
  If you can't fix a bug after 2 hours of focused debugging:
  
  1. Step away from the keyboard (5-10 minutes)
     → Fresh perspective is the #1 debugging tool
  
  2. Explain the bug to someone else (rubber duck debugging)
     → Saying it out loud forces clarity
  
  3. Write down what you KNOW vs what you ASSUME
     → Most stuck bugs come from a wrong assumption
  
  4. Ask yourself:
     "What would have to be TRUE for this bug to reproduce?"
     "What evidence DISPROVES my current hypothesis?"
  
  5. If still stuck after 2 more hours:
     → Escalate or pair with someone who hasn't seen the issue
```

### 6.3 The Rubber Duck Debugging

```python
# Pseudocode execution:
def rubber_duck_debug(code_bug):
    """
    Explain the code line by line to a rubber duck.
    The duck doesn't know anything, so you need to
    be precise enough that a complete beginner would
    understand.
    
    90% of the time, you find the bug mid-explanation.
    """
    while not bug_found:
        for line in code_bug:
            explain_out_loud(line)
```

---

## 7. Debugging Anti-Patterns

```
  ❌ "Let me just try restarting it"
     → You learned nothing. Same bug will return.

  ❌ "Let me change this randomly and see if it helps"
     → If it "fixes" the bug, you still don't know WHY.
     → The "fix" might have introduced a different, worse bug.

  ❌ "I checked the code, it looks fine"
     → The code is NOT fine — the bug proves it.
     → The bug is in the gap between "what you think the code does"
       and "what the code actually does."

  ❌ "It must be a compiler/interpreter bug"
     → It's NEVER the compiler. (Google's postmortem: zero compiler bugs)
     → The compiler is better tested than your code.

  ❌ "This worked yesterday, nothing changed!"
     → Something ALWAYS changed. Find it.
     → Deployment, config, data, traffic pattern, time of day.
```

---

## References

- `references/debugging-recipes.md` — Language-specific debugging recipes (Go/Node/Python/Rust)
- `references/logging-standards.md` — Structured logging patterns for debuggability
- `references/post-deploy-checks.md` — What to check immediately after a deployment
