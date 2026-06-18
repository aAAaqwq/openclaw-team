# Concurrent & Parallel Programming

> Level: Expert | File: `concurrent-programming.md`
> 
> Practical concurrent programming across Go, Rust, TypeScript, Python, and Java:
> goroutines/threads, async/await, channels/message passing, shared memory with 
> synchronization, and production debugging.

---

## Table of Contents
1. [Concurrency vs Parallelism](#1-concurrency-vs-parallelism)
2. [Goroutines & Channels (Go)](#2-goroutines--channels-go)
3. [Async/Await & Event Loop (TypeScript/Python)](#3-asyncawait--event-loop-typescriptpython)
4. [Threads & Shared State (Java/Rust)](#4-threads--shared-state-javarust)
5. [Synchronization Primitives](#5-synchronization-primitives)
6. [Common Concurrency Patterns](#6-common-concurrency-patterns)
7. [Race Conditions & Deadlocks](#7-race-conditions--deadlocks)
8. [Profiling & Debugging Concurrent Code](#8-profiling--debugging-concurrent-code)
9. [Production Concurrency Anti-Patterns](#9-production-concurrency-anti-patterns)
10. [Benchmarking & Tuning](#10-benchmarking--tuning)

---

## 1. Concurrency vs Parallelism

### 1.1 The Distinction

```
Concurrency: Dealing with multiple things at once (structuring programs)
Parallelism: Doing multiple things at once (execution, needs hardware)

       Concurrency (goroutines, async)       Parallelism (multiple cores)
       ┌──────────────────────────┐         ┌──────────────────────────┐
       │ Task A: ──▶ ──▶ ──▶     │         │ Core 1: ████░░░░░░      │
       │ Task B: ──▶ ──▶ ──▶     │         │ Core 2: ░░░░████░░░░    │
       │ Interleaved execution    │         │ True parallel execution  │
       └──────────────────────────┘         └──────────────────────────┘

Go proverb: "Concurrency is about dealing with lots of things at once.
            Parallelism is about doing lots of things at once."
```

### 1.2 The Concurrency Models

```
| Model               | Language         | Primitives            | Best For              |
|---------------------|------------------|-----------------------|-----------------------|
| Communicating Sequential Processes (CSP) | Go | goroutines + channels | Systems programming   |
| Actor Model         | Erlang/Elixir     | actors + messages     | Telecom, distributed  |
| Async/Await         | TypeScript/Python/Kotlin | async fn + await     | I/O-bound apps       |
| Threads + Locks     | Java/C++/Rust     | Thread, Mutex         | CPU-bound compute     |
| Structured Concurrency | Kotlin/Zig/JVM | scoped coroutines      | Resource safety       |
```

### 1.3 When to Use Which

```
I/O-bound (network, disk, DB): Async/await or goroutines
  - 10k connections on a single thread (Node.js, Python asyncio)
  - Why: CPU is idle waiting for I/O, so we switch tasks

CPU-bound (compute, compression, encoding): Threads + parallelism
  - 4 cores = 4 parallel computations
  - Why: we need more CPU cores, not more task switching

Mixed: Goroutines or thread pool + async
  - Pattern: goroutine per request, worker pool for CPU tasks
  - Go: goroutines handle I/O, send CPU tasks to worker pool
```

---

## 2. Goroutines & Channels (Go)

### 2.1 Goroutine Basics

```go
// Start a goroutine
go func() {
    fmt.Println("Hello from goroutine")
}()

// Wait for goroutines to finish
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        fmt.Printf("Worker %d done\n", id)
    }(i)
}
wg.Wait()
```

### 2.2 Channels

```go
// Unbuffered channel (synchronous — send blocks until receive)
ch := make(chan int)
go func() {
    ch <- 42               // Blocks until someone receives
}()
value := <-ch              // Receives the value

// Buffered channel (async up to buffer size)
ch := make(chan int, 100)
ch <- 1                    // Doesn't block (buffer has space)
ch <- 2                    // Still doesn't block
<-ch                       // Read first value

// Channel patterns
func fanOut(in <-chan int, workers int) []<-chan int {
    channels := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        ch := make(chan int)
        channels[i] = ch
        go func() {
            for val := range in {
                ch <- process(val)
            }
            close(ch)
        }()
    }
    return channels
}
```

### 2.3 Select Statement

```go
// Multiplex multiple channels
select {
case msg1 := <-ch1:
    fmt.Println("Received from ch1:", msg1)
case msg2 := <-ch2:
    fmt.Println("Received from ch2:", msg2)
case <-time.After(5 * time.Second):
    fmt.Println("Timeout!")
default:
    fmt.Println("No channel ready (non-blocking)")
}
```

### 2.4 Pipeline Pattern

```go
// Stage 1: Generate numbers
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

// Stage 2: Square numbers
func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// Usage: gen → sq → main
func main() {
    c := gen(2, 3, 4, 5)
    out := sq(c)
    
    for result := range out {
        fmt.Println(result)  // 4, 9, 16, 25
    }
}
```

### 2.5 Context Cancellation

```go
func longRunningOp(ctx context.Context) error {
    select {
    case result := <-doWork():
        return result
    case <-ctx.Done():
        return ctx.Err()  // Canceled or DeadlineExceeded
    }
}

// Timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

err := longRunningOp(ctx)

// Cancellation propagation
func handler(ctx context.Context, req Request) {
    ctx, cancel := context.WithCancel(ctx)
    defer cancel()
    
    // If handler returns early, all goroutines with ctx are canceled
    go firstSubTask(ctx)
    go secondSubTask(ctx)
    result, _ := thirdSubTask(ctx)
    return result
}
```

---

## 3. Async/Await & Event Loop (TypeScript/Python)

### 3.1 TypeScript Async/Await

```typescript
// Promise basics
async function fetchOrder(id: string): Promise<Order> {
    const response = await fetch(`/api/orders/${id}`);
    if (!response.ok) throw new Error(`Order ${id} not found`);
    return response.json();
}

// Parallel execution (await all)
async function loadDashboard(userId: string): Promise<Dashboard> {
    const [orders, profile, notifications] = await Promise.all([
        fetchOrders(userId),
        fetchProfile(userId),
        fetchNotifications(userId),
    ]);
    return { orders, profile, notifications };
}

// Race pattern (first one wins)
async function firstSuccessful(...promises: Promise<any>[]): Promise<any> {
    return Promise.race(promises);
}

// Sequential vs parallel
async function processAll(items: Item[]): Promise<void> {
    // Sequential (one at a time) — slow, preserves order
    for (const item of items) {
        await process(item);
    }
    
    // Parallel (all at once) — fast, no order guarantee
    await Promise.all(items.map(item => process(item)));
    
    // Throttled (N at a time)
    const results = [];
    for (let i = 0; i < items.length; i += CONCURRENCY) {
        const batch = items.slice(i, i + CONCURRENCY);
        results.push(...await Promise.all(batch.map(item => process(item))));
    }
    return results;
}
```

### 3.2 Event Loop (Node.js)

```
Node.js event loop phases:
  1. timers: setTimeout, setInterval callbacks
  2. pending callbacks: I/O callbacks deferred to next iteration
  3. idle, prepare: internal use
  4. poll: retrieve new I/O events (blocking)
  5. check: setImmediate callbacks
  6. close callbacks: socket.on('close', ...)

Never block the event loop:
  ❌ CPU-intensive sync operation > 10ms
  ❌ JSON.parse of multi-MB payloads
  ❌ crypto operations (use worker threads)
  ❌ fs.readFileSync (use fs.promises)
```

### 3.3 Python Async/Await

```python
import asyncio
import aiohttp

async def fetch_order(session: aiohttp.ClientSession, id: str) -> dict:
    async with session.get(f'/api/orders/{id}') as response:
        return await response.json()

async def load_dashboard(user_id: str) -> dict:
    async with aiohttp.ClientSession() as session:
        orders, profile = await asyncio.gather(
            fetch_orders(session, user_id),
            fetch_profile(session, user_id),
        )
        return {'orders': orders, 'profile': profile}

# Semaphore for concurrency control
sem = asyncio.Semaphore(10)

async def throttled_request(url: str):
    async with sem:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
```

### 3.4 Python GIL Impact

```
GIL (Global Interpreter Lock):
  - Only one thread executes Python bytecode at a time
  - CPU-bound threads DO NOT run in parallel
  - I/O-bound threads benefit from GIL release (network, disk)

Workarounds:
  - multiprocessing: separate processes (bypasses GIL)
  - asyncio: single-threaded async (works great for I/O)
  - C extensions: can release GIL (numpy, pandas)
  - Rust/Python: PyO3 with no GIL

Rule of thumb (Python):
  - I/O-bound: use asyncio or threading
  - CPU-bound: use multiprocessing or write the hot path in C/Rust
  - Mixed: asyncio + run_in_executor for CPU tasks
```

---

## 4. Threads & Shared State (Java/Rust)

### 4.1 Java Threads

```java
// Thread creation (old school)
Thread thread = new Thread(() -> {
    System.out.println("Hello from thread");
});
thread.start();
thread.join();  // Wait for completion

// ExecutorService (preferred)
ExecutorService executor = Executors.newFixedThreadPool(10);
Future<Integer> future = executor.submit(() -> {
    Thread.sleep(1000);
    return 42;
});
Integer result = future.get();  // Blocks if not done
executor.shutdown();

// CompletableFuture (async composition)
CompletableFuture.supplyAsync(() -> fetchOrder(id))
    .thenApplyAsync(order -> calculateTotal(order))
    .thenAcceptAsync(total -> updateCache(id, total))
    .exceptionally(e -> {
        log.error("Failed to process order", e);
        return null;
    });

// Virtual Threads (Java 21+) — lightweight like goroutines
Thread.ofVirtual().start(() -> {
    // Thousands of virtual threads on a single platform thread
});
```

### 4.2 Rust Ownership & Threads

```rust
use std::thread;
use std::sync::{Arc, Mutex};

// Thread-safe shared state
let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}

// Channels (like Go's goroutines)
use std::sync::mpsc;

let (tx, rx) = mpsc::channel();
thread::spawn(move || {
    tx.send(42).unwrap();
});

println!("Received: {}", rx.recv().unwrap());

// Rayon — data parallelism
use rayon::prelude::*;

let sum: i32 = (0..1000000)
    .into_par_iter()     // Parallel iterator
    .map(|x| x * 2)
    .sum();
```

---

## 5. Synchronization Primitives

### 5.1 Mutex (Mutual Exclusion)

```go
// Go mutex
var mu sync.Mutex
var counter int

func increment() {
    mu.Lock()
    counter++
    mu.Unlock()
}

// Go RWMutex (readers don't block readers)
var rw sync.RWMutex
var data map[string]string

func read(key string) string {
    rw.RLock()
    defer rw.RUnlock()
    return data[key]
}

func write(key, value string) {
    rw.Lock()
    defer rw.Unlock()
    data[key] = value
}
```

### 5.2 Atomic Operations

```go
// Go atomics (faster than mutex for simple operations)
var count atomic.Int64

func increment() {
    count.Add(1)
}

// Compare and swap
swapped := count.CompareAndSwap(42, 43)

// Load/Store
value := count.Load()
count.Store(100)
```

### 5.3 WaitGroup / CountDownLatch

```go
// Go — WaitGroup
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        doWork(id)
    }(i)
}
wg.Wait()  // Blocks until all Done()

// Java — CountDownLatch
CountDownLatch latch = new CountDownLatch(3);
for (int i = 0; i < 3; i++) {
    executor.submit(() -> {
        try { doWork(); }
        finally { latch.countDown(); }
    });
}
latch.await();  // Blocks until count reaches 0
```

### 5.4 Semaphore

```go
// Go — semaphore via buffered channel
sem := make(chan struct{}, 10)  // Max 10 concurrent

for _, task := range tasks {
    sem <- struct{}{}  // Acquire (block if full)
    go func(t Task) {
        defer func() { <-sem }()  // Release
        process(t)
    }(task)
}

// Wait for all to finish
for i := 0; i < cap(sem); i++ {
    sem <- struct{}{}
}
```

---

## 6. Common Concurrency Patterns

### 6.1 Fan-Out / Fan-In

```go
// Fan-Out: distribute work across multiple goroutines
func fanOut(in <-chan Job, workers int) []<-chan Result {
    channels := make([]<-chan Result, workers)
    for i := 0; i < workers; i++ {
        ch := make(chan Result)
        channels[i] = ch
        go func() {
            for job := range in {
                ch <- process(job)
            }
            close(ch)
        }()
    }
    return channels
}

// Fan-In: merge multiple channels into one
func fanIn(channels ...<-chan Result) <-chan Result {
    out := make(chan Result)
    var wg sync.WaitGroup
    wg.Add(len(channels))
    
    for _, ch := range channels {
        go func(c <-chan Result) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}
```

### 6.2 Worker Pool

```go
type Pool struct {
    jobs    chan func()
    sem     chan struct{}  // bounded semaphore
    quit    chan struct{}
}

func NewPool(maxWorkers int) *Pool {
    return &Pool{
        jobs: make(chan func(), 1000),
        sem:  make(chan struct{}, maxWorkers),
        quit: make(chan struct{}),
    }
}

func (p *Pool) Submit(job func()) {
    p.jobs <- job
}

func (p *Pool) Start() {
    go func() {
        for {
            select {
            case job := <-p.jobs:
                p.sem <- struct{}{}  // acquire
                go func() {
                    defer func() { <-p.sem }()  // release
                    job()
                }()
            case <-p.quit:
                return
            }
        }
    }()
}
```

### 6.3 Circuit Breaker

```go
type CircuitBreaker struct {
    mu             sync.RWMutex
    failures        int
    threshold       int
    timeout         time.Duration
    lastFailureTime time.Time
    state           string
}

func (cb *CircuitBreaker) Call(fn func() error) error {
    cb.mu.RLock()
    state := cb.state
    cb.mu.RUnlock()
    
    if state == "open" {
        if time.Since(cb.lastFailureTime) > cb.timeout {
            cb.mu.Lock()
            cb.state = "half-open"
            cb.mu.Unlock()
        } else {
            return ErrCircuitOpen
        }
    }
    
    err := fn()
    
    cb.mu.Lock()
    defer cb.mu.Unlock()
    
    if err != nil {
        cb.failures++
        cb.lastFailureTime = time.Now()
        if cb.failures >= cb.threshold {
            cb.state = "open"
        }
        return err
    }
    
    cb.failures = 0
    cb.state = "closed"
    return nil
}
```

### 6.4 Rate Limiter

```go
// Token bucket rate limiter
type RateLimiter struct {
    rate     int
    capacity int
    tokens   int
    lastRefill time.Time
    mu       sync.Mutex
}

func (rl *RateLimiter) Allow() bool {
    rl.mu.Lock()
    defer rl.mu.Unlock()
    
    // Refill
    now := time.Now()
    elapsed := now.Sub(rl.lastRefill)
    rl.tokens = min(rl.capacity, rl.tokens + int(elapsed.Seconds()*float64(rl.rate)))
    rl.lastRefill = now
    
    if rl.tokens > 0 {
        rl.tokens--
        return true
    }
    return false
}
```

---

## 7. Race Conditions & Deadlocks

### 7.1 Race Condition Detection

```go
// Go race detector (compiled in)
// go run -race main.go
// go build -race main.go

// Example race:
var counter int

func main() {
    for i := 0; i < 1000; i++ {
        go func() {
            counter++  // RACE: multiple goroutines write without sync
        }()
    }
}

// Fix:
var mu sync.Mutex
mu.Lock()
counter++
mu.Unlock()
```

### 7.2 Deadlock Detection

```
Deadlock conditions (all 4 must hold):
  1. Mutual exclusion: resource is not shareable
  2. Hold and wait: thread holds one resource while waiting for another
  3. No preemption: can't forcibly take a resource
  4. Circular wait: two or more threads waiting for each other

Example (Java):
    Thread A:  lock(A); lock(B);
    Thread B:  lock(B); lock(A);
               // Both can't proceed!

Prevention:
  - Lock ordering: always acquire locks in the same order
  - Timeout: tryLock with timeout (Go: select with time.After)
  - Avoid nested locks (if lock A → need B, expose helper that locks both)
```

### 7.3 Memory Ordering Issues

```
Go memory model:
  - goroutines don't guarantee visibility of shared memory
  - A write in goroutine A may NOT be visible in goroutine B
  - Synchronization primitives (mutex, channel, atomic) create happens-before edges

Example:
  var ready bool
  var data int
  
  // Goroutine A
  go func() {
      data = 42
      ready = true  // May be visible before data = 42 in B!
  }()
  
  // Goroutine B
  for !ready { }   // May see ready = true but data = 0!
  fmt.Println(data)

Fix: use synchronization (channel, mutex, atomic)
```

---

## 8. Profiling & Debugging Concurrent Code

### 8.1 Go Profiling

```bash
# CPU profile
go test -bench=. -cpuprofile=cpu.prof
go tool pprof -http=:8080 cpu.prof

# Memory profile
go test -bench=. -memprofile=mem.prof

# Trace (goroutine visualization)
go test -trace=trace.out
go tool trace trace.out

# Live profiling (for running server):
import _ "net/http/pprof"

# Then:
curl http://localhost:6060/debug/pprof/goroutine?debug=2
curl http://localhost:6060/debug/pprof/heap?debug=2
```

### 8.2 Node.js Profiling

```bash
# CPU profiling
node --cpu-prof --cpu-prof-dir=./profiles app.js

# Heap dump
node --heapsnapshot-signal=SIGUSR2 app.js
kill -USR2 <pid>

# Clinic.js (full suite)
npx clinic doctor -- node app.js
npx clinic flame -- node app.js
npx clinic bubbleprof -- node app.js
```

### 8.3 Detecting Deadlocks in Production

```bash
# Go: get all goroutine stacks
curl http://localhost:6060/debug/pprof/goroutine?debug=2

# Java: thread dump
jstack <pid>
# or: kill -3 <pid> (prints to stdout)

# Python: trace all threads
import threading
threading.enumerate()
import faulthandler; faulthandler.dump_traceback()

# Common deadlock pattern in stack trace:
# - Thread A holding lock L1, waiting for L2
# - Thread B holding lock L2, waiting for L1
```

### 8.4 Go Debugging Quick Reference

```bash
# Get all goroutines
go tool pprof http://localhost:6060/debug/pprof/goroutine

# Count goroutines (expected: steady state, not growing)
curl -s http://localhost:6060/debug/pprof/goroutine?debug=2 | grep "goroutine " | wc -l

# Suspicious patterns:
# - Growing goroutine count = goroutine leak
# - Many goroutines blocked on sync.Mutex.Lock = contention
# - Many goroutines in runtime.gopark = waiting for channels

# Goroutine leak detection:
import "runtime/pprof"
// Every 10 seconds:
pprof.Lookup("goroutine").WriteTo(os.Stdout, 1)
// Look for goroutines that never complete
```

---

## 9. Production Concurrency Anti-Patterns

### ❌ Goroutine Leak

```go
// BAD: goroutine waits forever
func leak() {
    ch := make(chan int)
    go func() {
        val := <-ch  // Never receives → goroutine lives forever
        fmt.Println(val)
    }()
    // Never sends on ch → goroutine leaks
}

// GOOD: use context cancellation
func notLeak(ctx context.Context) {
    ch := make(chan int)
    go func() {
        select {
        case val := <-ch:
            fmt.Println(val)
        case <-ctx.Done():
            return  // Clean exit on cancellation
        }
    }()
}
```

### ❌ Unbounded Concurrency

```go
// BAD: unlimited goroutines for incoming requests
func handler(w http.ResponseWriter, r *http.Request) {
    go processRequest(r)  // If 10k requests → 10k goroutines → OOM
}

// GOOD: bounded worker pool
var pool = NewPool(100)  // Max 100 goroutines

func handler(w http.ResponseWriter, r *http.Request) {
    pool.Submit(func() {
        processRequest(r)
    })
}
```

### ❌ Channel Blocking

```go
// BAD: unbuffered channel, receiver not ready
func main() {
    ch := make(chan int)
    ch <- 42  // Blocks forever (no receiver)
    val := <-ch
}

// GOOD: buffered channel or ensure sender/receiver matching
ch := make(chan int, 1)  // Buffered, won't block
ch <- 42
val := <-ch
```

### ❌ Shared State Without Synchronization

```go
// BAD: map read/write without sync (will crash with concurrent map writes)
var cache = make(map[string]*Order)

func getOrder(id string) *Order {
    if o, ok := cache[id]; ok {
        return o
    }
    o := fetchFromDB(id)
    cache[id] = o  // MUTEX NEEDED
    return o
}

// GOOD: use sync.Map or mutex-protected map
var cache sync.Map

func getOrder(id string) *Order {
    if o, ok := cache.Load(id); ok {
        return o.(*Order)
    }
    o := fetchFromDB(id)
    cache.Store(id, o)
    return o
}
```

---

## 10. Benchmarking & Tuning

### 10.1 Benchmarking Concurrent Code

```go
// Go benchmark
func BenchmarkWorkerPool(b *testing.B) {
    pool := NewPool(10)
    jobs := make([]func(), b.N)
    for i := range jobs {
        job := func() { expensiveOp() }
        jobs[i] = job
    }
    
    b.ResetTimer()
    for _, job := range jobs {
        pool.Submit(job)
    }
}
```

### 10.2 Tuning Guidelines

```
Number of goroutines/threads:
  CPU-bound: runtime.NumCPU() (1 per core)
  I/O-bound: depends on latency (100-10000)
  
  Rule of thumb for I/O-bound:
    concurrent = latency_ms × throughput_per_second
  
  Example: latency = 50ms, target = 1000 req/s
    concurrent = 0.05 × 1000 = 50

Channel buffer sizes:
  Rule: choose based on producer/consumer speed difference
  Small buffer (1-10): tight coupling, backpressure
  Large buffer (100+): loose coupling, memory cost
  Too large: memory waste, hides latency issues

Mutex granularity:
  Coarse (one lock for whole app): simple, low concurrency
  Fine (lock per entry): complex, high concurrency  
  Sharding: N locks for N buckets → good middle ground
```

### 10.3 Production Tuning Checklist

```
□ Number workers tuned (not max, not min — optimal for workload)
□ Channel buffer sizes appropriate (not 1, not 100k)
□ Mutex scope minimal (lock around shared state only, not whole function)
□ No goroutine leaks (each goroutine has an exit path)
□ Context cancellation propagates properly
□ Resource cleanup on shutdown (Wait())
□ Rate limiting for external calls
□ Circuit breaker for dependant services
□ No unbounded goroutine/channel creation
□ Pool size matches workload (not random number)
□ Memory usage stable (no growth over time)
```
