# Backend Architect

> Level: Advanced | File: `backend-architect.md`
> 
> Backend system design: capacity estimation, microservice boundaries, event-driven patterns,
> idempotency, distributed transactions, and anti-pattern avoidance.

---

## Table of Contents
1. [System Design Process](#1-system-design-process)
2. [Capacity Estimation](#2-capacity-estimation)
3. [Architecture Patterns](#3-architecture-patterns)
4. [Microservice Boundaries](#4-microservice-boundaries)
5. [Distributed Transactions](#5-distributed-transactions)
6. [Idempotency & Retries](#6-idempotency--retries)
7. [Caching Architecture](#7-caching-architecture)
8. [Rate Limiting & Throttling](#8-rate-limiting--throttling)
9. [Microservice Anti-Patterns](#9-microservice-anti-patterns)
10. [Appendix: Design Templates](#10-appendix-design-templates)

---

## 1. System Design Process

### 1.1 The 4-Step Design Framework
```
Step 1: Understand requirements
  - Functional: what must the system do?
  - Non-functional: latency (p99 < 200ms), throughput (10k req/s), 
    availability (99.9%), consistency (eventual vs strong)

Step 2: Capacity estimation
  - Traffic: DAU (10M) × actions per session (5) = 50M daily actions
  - Peak: daily / (seconds per day) × peak factor (5x) ≈ 3k req/s
  - Storage: 50M actions × 1KB per action × 365 days ≈ 18TB/year
  - Network: 3k req/s × 50KB response ≈ 150MB/s ≈ 1.2 Gbps

Step 3: Data model & API design
  - Entities, relationships, indexes
  - API endpoints, request/response schemas
  - Consistency model (strong for payments, eventual for feeds)

Step 4: System topology
  - Components diagram: LB → API → Cache → DB → Queue → Workers
  - Data flow: how data moves through the system
  - Failure modes: what breaks and how we survive it
```

### 1.2 Design Document Template
```markdown
# System Design: [Service Name]

## Context & Goals
- Business problem: [one sentence]
- Success metrics: [throughput, latency, availability targets]

## Constraints
- Budget: [infra cost ceiling]
- Team: [team size and skill set]
- Timeline: [when to ship]

## Key Design Decisions
| # | Decision | Rationale | Alternatives Considered |
|---|----------|-----------|-------------------------|
| 1 | Use Postgres | Need ACID, team knows it | MySQL (weaker JSONB), CockroachDB (overkill) |
| 2 | Event-driven | Async processing for scale | Synchronous (too slow for peak) |

## Architecture
[ASCII art / diagram here]

## API Contract
[List endpoints]

## Data Model
[Schema ER diagram]

## Failure Scenarios
| Failure | Impact | Mitigation |
|---------|--------|------------|
| DB unavailable | Orders fail | Read replica + circuit breaker |
| Queue backlog | Delayed emails | Auto-scale consumers |
```

---

## 2. Capacity Estimation

### 2.1 Quick Estimation Numbers
```
DAU → QPS:
  10M DAU, 10 actions/user/day → 100M daily actions
  Peak factor 5x → ~5,800 req/s peak
  
Bandwidth:
  5,800 req/s × 50KB response → 290 MB/s → ~2.3 Gbps

Storage:
  100M actions × 2KB storage → 200 GB/day → 73 TB/year

Database connections:
  QPS × avg query time (50ms) → DB connections needed
  5,800 × 0.05 = 290 connections → ~1.5x overhead ≈ 450 connections
```

### 2.2 Resource Calculation Template
```yaml
User load:
  DAU: [number]
  Actions per user per day: [number]
  Total daily actions: [DAU × actions]

Traffic:
  Peak requests/sec: [daily_actions / 86400 × peak_factor]
  Peak read QPS: [peak_req × read_ratio]
  Peak write QPS: [peak_req × write_ratio]

Data:
  Average payload: [KB]
  Daily data volume: [GB]
  Retention period: [days]
  Total storage: [daily_volume × retention]

Infrastructure:
  API servers: [peak_req / capacity_per_instance]
  DB read replicas: [peak_reads / replica_capacity]
  Cache memory: [hot_data_size × 1.5]
  Queue throughput: [peak_writes × retry_factor]
```

### 2.3 Real-World Benchmarks
```
Single server (16 vCPU, 64GB):
  Node.js (Fastify):  ~20k req/s   (simple JSON response)
  Go (Gin):           ~80k req/s
  Python (FastAPI):   ~8k req/s    (async, I/O bound)

PostgreSQL single instance:
  Simple read:        ~50k qps     (in cache)
  Simple write:       ~10k qps     (single row)
  Complex join:       ~2k qps      (3+ tables, sorted)

Redis single instance:
  Read:               ~100k ops/s  (in-memory)
  Write:              ~80k ops/s

Kafka single partition:
  Throughput:         ~1 MB/s per partition
  Multi-partition:    linear scaling
```

---

## 3. Architecture Patterns

### 3.1 Event-Driven (Async)
```
┌──────┐   ┌──────────┐   ┌────────────┐
│Order │──→│Kafka/    │──→│Payment     │
│Service│   │Event Bus │   │Consumer    │
└──────┘   └─────┬────┘   └────────────┘
                  │        ┌────────────┐
                  └────────│Email       │
                           │Consumer    │
                           └────────────┘

Event format (CloudEvents spec):
{
  "specversion": "1.0",
  "type": "order.created",
  "source": "/orders/v1",
  "id": "ord_abc123",
  "time": "2026-05-02T14:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "userId": "usr_789",
    "amount": 2999
  }
}

Pros: Decoupled services, independent scaling, async resilience
Cons: Eventual consistency, harder debugging, ordering challenges
```

### 3.2 CQRS (Command Query Responsibility Segregation)
```
Write Path (Commands):
  API → Command Handler → Write DB (Normalized)

Read Path (Queries):
  API → Query Handler → Read DB (Denormalized/Materialized)

Sync Mechanism:
  Write DB → Change Data Capture (CDC) → Read DB

When to use:
  ✅ Read/write ratio > 10:1
  ✅ Complex read models (search, aggregation, reports)
  ✅ Write model is normalized, read model is denormalized
  
When NOT to use:
  ❌ Simple CRUD with equal read/write ratio
  ❌ Small team, simple domain
  ❌ Stringent strong consistency between read and write
```

### 3.3 Saga Pattern (Distributed Transactions)
```
Choreography Saga (no coordinator):
  Order Service: "Order Created" → Payment Service: "Payment Processed" 
  → Inventory Service: "Inventory Reserved" → ...

Orchestrator Saga (central coordinator):
  Saga Orchestrator:
    1. "Create Order" → Order Service (compensation: cancel order)
    2. "Process Payment" → Payment Service (compensation: refund)
    3. "Reserve Inventory" → Inventory Service (compensation: release)
    4. If any fails → run all previous compensations in reverse

Choose:
  Choreography: simpler, fewer components, harder to trace
  Orchestrator: better observability, centralized rollback, single point of failure
```

---

## 4. Microservice Boundaries

### 4.1 How to Find Service Boundaries
```
Method 1: Business Capability
  - Each bounded context → one service
  - Example: Orders, Payments, Inventory, Shipping, Notifications

Method 2: Change Frequency
  - Components that change together → same service
  - Components that change independently → separate services

Method 3: Data Ownership
  - Each service owns its data (no shared DB)
  - Communication via API/events, not DB joins

Method 4: Team Structure (Conway's Law)
  - One team owns 2-3 services (never more than 3)
  - Team owns the full lifecycle: code → test → deploy → operate
```

### 4.2 Service Granularity Checklist
```
✅ Service has a clear, bounded business capability
✅ Service can be deployed independently
✅ Service owns its data (no direct DB access from other services)
✅ Service can be tested in isolation
✅ Service has a single reason to change (Single Responsibility)
✅ Service could be rewritten in a different language without breaking others
✅ Team size supports owning this service
✅ Cross-service coordination is limited (not more than 2-3 other services per transaction)
```

### 4.3 When NOT to Microservice
```
❌ Team < 5 people (monolith is faster)
❌ Domain is simple and stable (CRUD is fine as monolith)
❌ Time to market is critical (microservices slow initial velocity)
❌ Organization lacks DevOps maturity (no CI/CD, no monitoring)
❌ No clear bounded contexts exist
```

---

## 5. Distributed Transactions

### 5.1 Trade-Offs
```
| Approach          | Consistency | Performance | Complexity | Best For         |
|-------------------|-------------|-------------|------------|------------------|
| No distributed tx | Eventual    | High        | Low        | Feeds, analytics  |
| Saga              | Eventual    | Medium      | Medium     | Order processing  |
| 2PC               | Strong      | Low         | High       | Financial (rare)  |
| TCC (Try/Confirm) | Strong      | Medium      | Very high  | High-value assets |
```

### 5.2 Outbox Pattern (Reliable Event Publishing)
```sql
-- Order table + outbox table, same DB transaction
BEGIN;
  INSERT INTO orders (id, user_id, amount) VALUES ('ord_1', 'usr_1', 2999);
  INSERT INTO outbox (aggregate_id, event_type, payload, created_at)
    VALUES ('ord_1', 'order.created', '{"orderId":"ord_1",...}', now());
COMMIT;

-- Separate publisher process reads outbox and sends to event bus
-- Delete after confirmed delivery (at-least-once)
```

### 5.3 Idempotency Key Pattern
```typescript
// Client sends idempotency key in header
POST /api/v1/charges
Idempotency-Key: idem_abc123

// Server:
app.post('/api/v1/charges', async (req, reply) => {
  const idemKey = req.headers['idempotency-key'];
  
  // Check if already processed
  const existing = await redis.get(`idem:${idemKey}`);
  if (existing) {
    return reply.status(200).send(JSON.parse(existing));  // Return cached result
  }
  
  // Process charge
  const result = await paymentGateway.charge(req.body);
  
  // Cache result (TTL 24h for replay protection)
  await redis.set(`idem:${idemKey}`, JSON.stringify(result), 'EX', 86400);
  
  return reply.status(201).send(result);
});
```

---

## 6. Idempotency & Retries

### 6.1 Retry Strategy
```typescript
// Exponential backoff with jitter
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts?: number;        // default: 3
    baseDelayMs?: number;        // default: 100
    maxDelayMs?: number;         // default: 10000
  } = {}
): Promise<T> {
  const { maxAttempts = 3, baseDelayMs = 100, maxDelayMs = 10000 } = options;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxAttempts) throw error;
      
      // Non-retryable errors
      if (error.statusCode === 400 || error.statusCode === 401 || error.statusCode === 403 || error.statusCode === 404) {
        throw error;
      }
      
      const delay = Math.min(baseDelayMs * Math.pow(2, attempt - 1), maxDelayMs);
      const jitter = Math.random() * delay * 0.1;  // 10% jitter
      await sleep(delay + jitter);
    }
  }
}
```

### 6.2 Non-Retryable Errors
```
Don't retry:
  - 400 Bad Request (fix the request first)
  - 401 Unauthorized (credentials invalid)
  - 403 Forbidden (no access)
  - 404 Not Found (resource doesn't exist)
  - 422 Unprocessable Entity (validation failure)
  - User-caused failures (insufficient balance, inventory shortage)

Do retry:
  - 429 Too Many Requests (rate limited — honor Retry-After header)
  - 503 Service Unavailable (temporary overload)
  - 504 Gateway Timeout (upstream slow)
  - Network errors (connection refused, DNS resolution failure)
```

---

## 7. Caching Architecture

### 7.1 Cache Layers
```
L1: Browser Cache
  - Cache-Control headers: max-age=3600, public/private
  - ETag for conditional requests
  - Hits: returning user, shared assets

L2: CDN Cache
  - Static assets: images, JS/CSS bundles (immutable content, long TTL)
  - API response: only for public, non-personalized data
  - Cache invalidation: purge by path pattern

L3: In-Memory Cache (Redis/Memcached)
  - Session data, rate limiting counters, leaderboards
  - Database query results (hot data)
  - Distributed locks

L4: Application-Level Cache
  - In-process: LRU cache (lru-cache npm, go-cache)
  - Best for: reference data (config, feature flags)
  - Watch out: stale data across multiple instances
```

### 7.2 Cache-Aside Pattern (Most Common)
```typescript
async function getProduct(id: string): Promise<Product> {
  // 1. Try cache
  const cached = await redis.get(`product:${id}`);
  if (cached) return JSON.parse(cached);
  
  // 2. Cache miss → fetch from DB
  const product = await db.query('SELECT * FROM products WHERE id = $1', [id]);
  if (!product) return null;
  
  // 3. Write to cache (with TTL)
  await redis.set(`product:${id}`, JSON.stringify(product), 'EX', 3600);
  
  return product;
}

// Write-through pattern (for writes):
async function updateProduct(id: string, data: Partial<Product>) {
  // 1. Update DB
  await db.query('UPDATE products SET ... WHERE id = $1', [id]);
  
  // 2. Invalidate cache (not update — let next read populate it)
  await redis.del(`product:${id}`);
}
```

### 7.3 Cache Invalidation Strategies
```
TTL-based (simplest):
  - Set TTL equal to acceptable staleness
  - OK for: product catalogs, user profiles
  - NOT OK for: inventory counts, balances

Write-through (strongest consistency):
  - Update DB → invalidate/update cache in same operation
  - Slightly higher write latency

Write-behind (async):
  - Update cache first, async write to DB
  - Risk: data loss if cache goes down before DB write

Pub/Sub invalidation (distributed):
  - Redis Pub/Sub to broadcast cache invalidation to all instances
  - Prevents stale reads from one instance after another modified data
```

---

## 8. Rate Limiting & Throttling

### 8.1 Algorithms
```
Token Bucket:
  - Bucket holds N tokens, refills at R tokens/second
  - Each request consumes 1 token
  - Allows bursts up to N, then rate-limited to R/s
  - Pros: allows bursts, simple
  - Cons: can exceed limit on long time scales
  
Leaky Bucket:
  - Queue of N requests, processed at R req/s
  - Overflowed requests are rejected
  - Pros: smooth output rate
  - Cons: no bursts
  
Sliding Window Log:
  - Track timestamps of requests per user
  - Count requests in last N seconds
  - Pros: accurate
  - Cons: memory per user
  
Sliding Window Counter (Redis):
  - ZINCRBY for each user +1 (score = timestamp)
  - ZREMRANGEBYSCORE to clean old entries
  - ZCOUNT to count entries in window
  - Pros: accurate + efficient
  - Cons: complex
```

### 8.2 Rate Limit Implementation (Redis)
```typescript
// Sliding window counter — 100 req/min per user
async function checkRateLimit(userId: string): Promise<boolean> {
  const key = `ratelimit:${userId}`;
  const window = 60;  // 60 seconds
  const max = 100;    // 100 requests
  
  const now = Math.floor(Date.now() / 1000);
  const windowStart = now - window;
  
  const multi = redis.multi();
  multi.zremrangebyscore(key, 0, windowStart);  // Remove old entries
  multi.zadd(key, now, `${now}:${Math.random()}`);  // Add current
  multi.zcard(key);  // Count entries
  multi.expire(key, window);  // Auto-clean
  
  const results = await multi.exec();
  const count = results[2][1] as number;  // zcard result
  
  return count <= max;
}
```

---

## 9. Microservice Anti-Patterns

### ❌ 1. Distributed Monolith
```
Service A ──→ Service B ──→ Service C ──→ Service D
                 ↑               ↑
                 └─Same data ────┘  (shared DB)

Symptoms: Service A needs Service B + C + D to function
Fix: Merge tightly coupled services back into a single monolith
```

### ❌ 2. Chatty Services
```
Order Service needs to call 5 microservices to create one order:
  User Service (get user) → Product Service (validate items) → 
  Payment Service (verify card) → Inventory Service (reserve) → 
  Notification Service (send confirmation)

Fix: Bulk data in initial request, async processing, or consider merging services
```

### ❌ 3. Shared Database
```
Services A, B, C all read/write the same orders table directly

Problems:
  - Schema changes require coordinated releases
  - One service's slow query impacts all others
  - No service autonomy

Fix: Each service owns its data. Eventual consistency for cross-service queries.
```

### ❌ 4. Everything Over HTTP
```
Service A calls Service B, which calls Service C, ... synchronous chain

Problems: cascading failures, increased latency, tighter coupling
Fix: Use async messaging (queue/event bus) for non-critical paths
```

### ❌ 5. Premature Splitting
```
5-person team manages 15 microservices.
Each deploy requires updating 3-8 services simultaneously.

Fix: Start with monolith. Extract services only when:
  - Team crosses 8 people
  - Two unrelated features frequently conflict in code
  - Different parts need different scaling or deployment
```

### ❌ 6. Missing Data Consistency
```
Order Service: "Order created" → Payment fails
Inventory Service already reserved the items → now orphaned

Fix: Implement Saga pattern with compensating transactions
```

---

## 10. Appendix: Design Templates

### 10.1 System Design Review Checklist
```
□ Functional requirements clearly stated
□ Non-functional requirements (latency, throughput, availability) quantified
□ Capacity estimation done (traffic, storage, bandwidth, connections)
□ Data model designed (entities, relationships, key indexes)
□ API contract defined (endpoints, request, response, error codes)
□ Architecture diagram drawn (components, data flow, network boundaries)
□ Failure modes identified (DB down, cache miss, queue backlog)
□ Error budget and SLOs defined
□ Monitoring and alerting plan included
□ Security considerations documented (auth, encryption, secrets)
```

### 10.2 Service Template Checklist
```
□ Service name, owner team
□ Language & framework
□ Data store
□ API / event contracts
□ Dependencies (upstream/downstream)
□ SLO targets (latency, availability, error rate)
□ Scaling strategy (horizontal, vertical)
□ Deployment method (rolling, canary, blue-green)
□ Monitoring dashboards (Grafana links)
□ Runbook links (top 3 failure modes)
```

### 10.3 Architecture Decision Record (ADR-Quick)
```markdown
# ADR-XXX: [Title]

Status: [Proposed | Accepted | Deprecated]
Date: YYYY-MM-DD

## Context
[Why this decision is needed]

## Decision
[What we decided]

## Consequences
[Positive and negative effects]

## Alternatives
[What we didn't choose and why]
```
