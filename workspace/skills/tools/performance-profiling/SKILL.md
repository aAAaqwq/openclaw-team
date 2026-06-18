---
name: performance-profiling
description: >
  Systematic performance profiling and optimization methodology. Covers CPU
  profiling, memory profiling, heap analysis, goroutine/thread analysis,
  FlameGraph generation, latency profiling, database query profiling,
  network I/O profiling, and continuous performance regression detection.

  USE WHEN: investigating performance issues, optimizing slow code, reducing
  memory usage, diagnosing GC/CPU bottlenecks, finding N+1 queries, analyzing
  pprof/flamegraph output, or establishing a performance baseline. Triggers on
  "profiling", "performance analysis", "slow code", "flame graph", "pprof",
  "heap dump", "memory leak", "CPU spike", "bottleneck".
---

# Performance Profiling

> **Source**: Google performance engineering + pprof/cpuprofile/flamegraph
> practical experience + real-world debugging at Google Brain/ByteDance
> **Core Philosophy**: "Don't optimize what you can't measure. Don't measure
> what you can't understand."

## Core Principles

```
  Performance optimization is NOT:
  ✦ "I think this might be slow" — guessing
  ✦ "Let's micro-optimize this function" — premature
  ✦ "Rewrite in Rust/Go" — last resort

  Performance optimization IS:
  ✓ Instrument first → profile second → fix third
  ✓ Optimizing the right 10% (Pareto principle)
  ✓ Measuring before AND after every change
  ✓ Understanding the system, not just the code
```

---

## 1. The Profiling Workflow

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Step 1: DEFINE THE PROBLEM                                   │
  │     "The request takes 500ms, it should take < 100ms"        │
  │     1a. Check monitoring: where is the time spent?           │
  │     1b. Hypothesis: "Time is spent in database queries"       │
  │                                                                │
  │  Step 2: PROFILE (measure current state)                      │
  │     2a. Collect CPU profile (pprof, perf)                     │
  │     2b. Collect memory/heap profile                           │
  │     2c. Collect latency breakdown (tracing)                   │
  │                                                                │
  │  Step 3: ANALYZE (find the bottleneck)                        │
  │     3a. Generate flame graph                                   │
  │     3b. Identify hottest paths                                 │
  │     3c. Confirm hypothesis or revise                          │
  │                                                                │
  │  Step 4: FIX (targeted optimization)                          │
  │     4a. Apply minimal, targeted fix                           │
  │     4b. NEVER guess — fix only what the profile reveals       │
  │                                                                │
  │  Step 5: VERIFY (measure again)                                │
  │     5a. Re-run profile                                         │
  │     5b. Compare before/after metrics                           │
  │     5c. If not fixed → return to Step 2                       │
  └──────────────────────────────────────────────────────────────┘
```

---

## 2. CPU Profiling

### 2.1 Go (pprof)

```go
// Add to your application
import (
    "net/http"
    _ "net/http/pprof"
)

func main() {
    // Start pprof HTTP server (separate port is best practice)
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()

    // Your application continues normally
    http.HandleFunc("/", handler)
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

```bash
# Collect CPU profile (30 seconds)
curl -o cpu.pprof 'http://localhost:6060/debug/pprof/profile?seconds=30'

# Analyze in interactive mode
go tool pprof cpu.pprof
(pprof) top 20           # Top 20 functions by CPU time
(pprof) web              # Generate call graph (SVG)
(pprof) list handleOrder # Show hot lines in a function

# Generate flame graph
git clone https://github.com/brendangregg/FlameGraph
go tool pprof -raw cpu.pprof > cpu_raw.txt
./FlameGraph/stackcollapse-go.pl cpu_raw.txt > cpu_collapsed.txt
./FlameGraph/flamegraph.pl cpu_collapsed.txt > cpu_flame.svg

# One-liner alternative (if installed)
pprof -http=:8081 cpu.pprof  # Web UI with flame graph built-in
```

### 2.2 Node.js

```typescript
import * as profiler from 'v8-profiler-next';

// Start profiling
profiler.startProfiling('cpu-profile');

// Your code runs here
await doWork();

// Stop and save
const profile = profiler.stopProfiling('cpu-profile');
profile.export((err, result) => {
    fs.writeFileSync('cpu-profile.cpuprofile', result);
    profile.delete();
});
```

```bash
# Alternative: use Chrome DevTools protocol
node --inspect-brk app.js
# Open chrome://inspect → start CPU profiling

# Or use clinic.js (zero-config)
npx clinic doctor -- node app.js
npx clinic flame -- node app.js
```

### 2.3 Python (cProfile)

```python
# Command line
python -m cProfile -o profile.cprof myscript.py

# In code
import cProfile

profiler = cProfile.Profile()
profiler.enable()
# Your code
result = process_orders()
profiler.disable()
profiler.dump_stats('profile.cprof')
```

```bash
# Visualize
python -m snakeviz profile.cprof  # Web UI

# Generate flamegraph
pip install py-spy
py-spy record -o python_flame.svg -- python myscript.py

# Live profiling (no code change)
py-spy top --pid 12345  # Live CPU usage per function
py-spy record -o profile.svg --pid 12345  # Flame graph from running process
```

---

## 3. Memory Profiling

### 3.1 Go (Heap Profiling)

```bash
# Collect heap profile
curl -o heap.pprof 'http://localhost:6060/debug/pprof/heap'

# Analyze
go tool pprof -http=:8082 heap.pprof

# Compare two heap profiles (find leak)
go tool pprof -base heap_before.pprof heap_after.pprof
# Shows what objects were ALLOCATED but not FREED

# In use objects (current)
go tool pprof -inuse_objects heap.pprof
# Allocated objects (cumulative)
go tool pprof -alloc_objects heap.pprof

# Allocated space vs count
go tool pprof -inuse_space heap.pprof    # Bytes in use
go tool pprof -inuse_objects heap.pprof  # Objects count
```

### 3.2 Node.js

```javascript
// Heap snapshot
const heapdump = require('heapdump');

// Trigger heap dump on signal
process.on('SIGUSR2', () => {
    heapdump.writeSnapshot(`/tmp/heap-${Date.now()}.heapsnapshot`);
});

// Or periodic snapshots
setInterval(() => {
    heapdump.writeSnapshot(`/tmp/heap-${Date.now()}.heapsnapshot`);
}, 60000);  // Every minute
```

```bash
# Analyze in Chrome DevTools:
# Memory tab → Load → Select .heapsnapshot file

# Or use command-line
node --expose-gc app.js

# Monitor heap in real-time
node --trace-gc app.js 2>&1 | grep -E 'Mark-sweep|Scavenge|IncrementalMark'
```

### 3.3 Python

```python
# tracemalloc (Python 3.4+)
import tracemalloc

tracemalloc.start()

# Take snapshot
snapshot = tracemalloc.take_snapshot()
stats = snapshot.statistics('lineno')

# Show top memory consumers
for stat in stats[:10]:
    print(stat)
```

```bash
# Memory profiling tools
pip install memory_profiler
python -m memory_profiler myscript.py

# Line-by-line memory (decorator)
# @profile decorator from memory_profiler
```

---

## 4. Latency Profiling (Tracing)

### 4.1 Distributed Tracing

```javascript
// OpenTelemetry — modern standard
const opentelemetry = require('@opentelemetry/api');
const tracer = opentelemetry.trace.getTracer('order-service');

async function processOrder(orderId) {
    const span = tracer.startSpan('processOrder');
    span.setAttribute('order.id', orderId);
    
    try {
        // Your logic here
        const order = await db.getOrder(orderId);  // Creates sub-span
        const priced = await pricingService.calculate(order);  // Creates sub-span
        return priced;
    } finally {
        span.end();
    }
}
```

```bash
# View traces in Jaeger or Tempo
# Each trace shows: 
# Service A: 50ms → Service B: 200ms → Service C: 150ms
#                            → Cache: 2ms
# Total: 402ms (57% in Service B!)
```

### 4.2 Database Query Profiling

```sql
-- PostgreSQL: slow query logging
SET log_min_duration_statement = 100;  -- Log queries > 100ms

-- Show running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration,
       query, state
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Explain analyze (real execution plan)
EXPLAIN ANALYZE 
SELECT * FROM orders 
WHERE customer_id = 'c001' 
  AND created_at > '2026-01-01';

-- Look for: sequential scan → missing index
-- Look for: nested loop join with many rows
-- Look for: sort with high memory
```

### 4.3 N+1 Query Detection

```python
# Django — auto-detect N+1
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    result = get_orders_with_items()
    
num_queries = len(ctx.captured_queries)
# If num_queries > len(result) + 1, you have N+1!
```

```javascript
// TypeORM — N+1 detection
import { getConnection } from 'typeorm';

const queryCount = 0;
getConnection().driver.postgres.on('query', () => queryCount++);
// Run your code
// Check queryCount — should be exactly the number you expect
```

---

## 5. FlameGraph Interpretation

### 5.1 Reading a Flame Graph

```
  ┌──────────────────────────────────────────────────────────────┐
  │                                                               │
  │  X-axis: Stack profile population (width = time spent)       │
  │  Y-axis: Stack depth (bottom = entry, top = leaf)            │
  │                                                               │
  │  🔥 WIDE columns = HOT (spend lots of time here)            │
  │  🔥 TALL stacks = DEEP (many nested calls)                  │
  │                                                               │
  │  What to look for:                                            │
  │  1. WIDEST top-level plateaus = hottest functions           │
  │  2. "Plateaus" where many tall stacks converge =           │
  │     serialization points, lock contention                    │
  │  3. Missing functions = time spent outside your code        │
  │     (GC, kernel, I/O wait)                                  │
  │                                                               │
  └──────────────────────────────────────────────────────────────┘
```

### 5.2 Common Patterns

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Pattern 1: "Wide Mountain"                                   │
  │     A single wide column → this function IS the bottleneck   │
  │     Fix: optimize that function or cache its result           │
  │                                                                │
  │  Pattern 2: "Many Same-Width Peaks"                           │
  │     Many functions each consuming similar time                │
  │     Fix: reduce the number of calls (batch, cache)            │
  │                                                                │
  │  Pattern 3: "Tall Spiky Tower"                                 │
  │     Deep recursion → O(n²) algorithm or deep call chain      │
  │     Fix: flatten the recursion, cache intermediate results     │
  │                                                                │
  │  Pattern 4: "GC/Alloc Cloud"                                   │
  │     Large chunk of CPU in GC/malloc → too many allocations   │
  │     Fix: reduce allocations, object pooling, stack alloc       │
  │                                                                │
  │  Pattern 5: "Empty Space"                                      │
  │     CPU profile doesn't show much → I/O bound                │
  │     Fix: measure I/O separately (disk, network, lock)        │
  └──────────────────────────────────────────────────────────────┘
```

---

## 6. Common Bottlenecks & Fixes

```
  ┌──────────────────────┬──────────────┬────────────────────────┐
  │ Symptom              │ Likely Cause │ Fix                    │
  ├──────────────────────┼──────────────┼────────────────────────┤
  │ CPU 100%, high req   │ Inefficient │ Profile → optimize     │
  │ latency              │ algorithm    │ hot path                │
  ├──────────────────────┼──────────────┼────────────────────────┤
  │ Memory grows forever │ Memory leak  │ Heap diff → find       │
  │                      │              │ growing object graph   │
  ├──────────────────────┼──────────────┼────────────────────────┤
  │ Periodic latency     │ GC / Full GC │ Reduce alloc rate,     │
  │ spikes               │              │ tune gc params         │
  ├──────────────────────┼──────────────┼────────────────────────┤
  │ High DB query latency│ Missing index│ EXPLAIN ANALYZE →      │
  │                      │              │ add index              │
  ├──────────────────────┼──────────────┼────────────────────────┤
  │ Many DB queries for  │ N+1 problem  │ Eager loading / batching│
  │ 1 request            │              │                        │
  ├──────────────────────┼──────────────┼────────────────────────┤
  │ Threads blocked      │ Lock         │ Reduce lock scope,     │
  │ waiting              │ contention    │ use lock-free, shard   │
  ├──────────────────────┼──────────────┼────────────────────────┤
  │ Low network throughput│ TCP buffer  │ Tune TCP params,       │
  │                      │ too small    │ batching               │
  ├──────────────────────┼──────────────┼────────────────────────┤
  │ Slow after deploy    │ Config       │ Check config, warm     │
  │                      │ change / cold│ caches, pre-compile    │
  │                      │ start        │                        │
  └──────────────────────┴──────────────┴────────────────────────┘
```

---

## 7. Continuous Performance

### 7.1 Benchmarking in CI

```go
// Go: benchstat for regression detection
// bench_test.go
func BenchmarkProcessOrder(b *testing.B) {
    order := createTestOrder()
    for i := 0; i < b.N; i++ {
        processOrder(order)
    }
}
```

```bash
# Run and save baseline
go test -bench=. -benchmem -count=5 > /tmp/before.txt

# After change
go test -bench=. -benchmem -count=5 > /tmp/after.txt

# Compare
go install golang.org/x/perf/cmd/benchstat@latest
benchstat /tmp/before.txt /tmp/after.txt

# Output:
# name                  old time/op    new time/op    delta
# ProcessOrder-8         2.35ms ± 3%   1.89ms ± 2%   -19.6%  ✨
```

### 7.2 Performance Dashboard

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Performance Dashboard (Grafana)                              │
  │                                                               │
  │  Request Latency (p50/p95/p99)                                │
  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━              │
  │  ┌────────────────────────────────────────────────┐          │
  │  │ ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁  p50: 45ms  p95: 120ms       │          │
  │  │                     p99: 890ms  (spike at 2pm)│          │
  │  └────────────────────────────────────────────────┘          │
  │                                                               │
  │  CPU Profile (Hot Functions, latest deploy)                   │
  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━              │
  │  orderService.processOrder: 45% (+12% from baseline) 🚨    │
  │  db.query: 22% (-3% from baseline)                          │
  │  json.Marshal: 18% (new!) ⚠️                                │
  └──────────────────────────────────────────────────────────────┘
```

---

## 8. Golden Rules

```
  1. ALWAYS profile before optimizing
     The hottest function is never the one you think it is.

  2. One change at a time
     Apply one optimization → measure → verify → commit.
     Multiple changes at once → you don't know what worked.

  3. Measure p99, not average
     Average hides the problem. p99 shows the true user experience.

  4. Profile under realistic load
     Empty system and loaded system have entirely different profiles.

  5. Cache is not a performance strategy, it's a complexity trade-off
     Adding cache means adding: invalidation logic, staleness tolerance,
     operational complexity, cold-start code paths.

  6. Don't optimize allocs that don't matter
     A 1ms allocation reduction when p99 is 500ms → misdirected effort.

  7. The best optimization is not doing the work at all
     → Can we skip this computation?
     → Can we pre-compute and cache?
     → Can we defer and batch?
```

---

## References

- `references/flamegraph-interpretation.md` — Detailed flame graph reading guide
- `references/perf-command-guide.md` — Linux perf tool comprehensive reference
- `references/profiling-recipes.md` — Language-specific profiling recipes
