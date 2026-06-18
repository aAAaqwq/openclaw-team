# ADR Examples — Real-World Reference

## Example: Choosing a Message Queue

```markdown
# ADR-021: Choose Kafka as Event Bus for Order Pipeline

- **Status**: Accepted
- **Date**: 2026-04-15
- **Author**: XuanYuan

## Context

The order pipeline needs an event bus to decouple order ingestion, payment
processing, inventory updates, and notification services. Current approach
(HTTP webhooks) is fragile and doesn't scale to 500+ events/sec.

Key requirements:
- At-least-once delivery
- Order-preserving per order ID
- Replay capability for debugging
- 30-day retention
- 500 - 5000 events/sec range

## Decision

Use Apache Kafka as the event bus for the order pipeline.

## Options Considered

### Option A: Apache Kafka (Recommended)
+ Built-in partitioning for ordering guarantees
+ 30-day retention by configuration
+ High throughput (millions/sec at peak)
+ Strong ecosystem (Kafka Connect, Schema Registry)
- Operational complexity (ZooKeeper/KRaft, brokers)
- Team needs to learn Kafka

### Option B: RabbitMQ
+ Simpler to operate
+ Good routing flexibility (exchanges)
- No built-in replay (acks remove messages)
- Throughput ceiling at ~10K/sec
- No ordering guarantee across partitions

### Option C: AWS SQS/SNS
+ Zero ops
+ Auto-scaling
- No ordering guarantee (FIFO limited to 300 TPS)
- No replay capability
- Vendor lock-in

## Trade-off Analysis

| Criteria       | Kafka      | RabbitMQ   | SQS/SNS    |
|----------------|------------|------------|------------|
| Ordering       | ✅ Yes     | ⚠️ Per queue | ⚠️ FIFO only |
| Replay         | ✅ Yes     | ❌ No      | ❌ No      |
| Throughput     | ✅ 1M+/sec | ⚠️ 10K/sec | ⚠️ 10K/sec |
| Operations     | ⚠️ Complex | ✅ Simple  | ✅ Zero    |
| Cost (1yr)     | $12K       | $6K        | $8K        |
| Team learning  | 2 weeks    | 1 week     | 1 day      |

## Consequences

+ Reliable ordering per order ID (critical for payment flow)
+ Built-in replay for debugging (massive productivity gain)
+ Schema Registry ensures contract compatibility
- Need dedicated Kafka ops training (1-2 engineers, 1 week)
- Need KRaft migration planned (ZooKeeper → KRaft in 6 months)
- Increased infrastructure complexity

## Validation

- [ ] P99 produce latency < 10ms at 2000 events/sec
- [ ] Consumer lag < 50ms during normal operation
- [ ] Full replay completes within 2 hours for 7 days of data
- [ ] Review in 6 months: is Kafka still the right choice at 10K+ events/sec?
```

## Example: Frontend State Management

```markdown
# ADR-015: Use Zustand for Global State Management

- **Status**: Accepted
- **Date**: 2026-03-10
- **Author**: Frontend Team

## Context

React micro-frontend app with shared auth/cart/notification state.
Current approach (React Context) causes unnecessary re-renders
and makes state flow hard to trace.

## Decision

Use Zustand for global state management instead of Redux or React Context.

## Rationale

Zustand provides:
- Simpler API than Redux (no reducers, actions, dispatchers)
- Better performance than Context (selective re-rendering)
- Middleware support (persist, devtools, immer)
- TypeScript-first API
- Tiny bundle size (< 1KB)

Redux was rejected due to boilerplate overhead. Context was rejected
due to re-render performance.

## Consequences

+ 40% reduction in re-renders compared to Context
+ Cleaner code (no action types, no reducer switch cases)
+ Easier testing (store can be tested without React)
- Need migration plan for existing Context-based state
- Team needs to learn Zustand patterns (2-day adoption)
```

## Example: CI/CD Platform

```markdown
# ADR-012: Use GitHub Actions for CI/CD

- **Status**: Accepted
- **Date**: 2026-02-20

## Context
Team uses GitHub for code hosting. CI currently uses Jenkins (self-hosted,
frequently broken). Want unified CI/CD experience.

## Decision
Replace Jenkins with GitHub Actions for CI/CD.

## Rationale
- Tight integration with GitHub (PR status, checks API, secrets)
- No infrastructure to maintain (vs Jenkins self-hosted)
- Marketplace with 10K+ actions
- Team already has GitHub access — no new tool to learn
- Sufficient for our scale (< 200 builds/day)

## Consequences
+ Zero ops for CI infrastructure
+ Average CI time drops from 12min to 4min (caching, parallelism)
+ PR status shows directly in GitHub UI
+ Secret management simplified (GitHub secrets)
- Linux/macOS runners only (no Windows for now)
- Self-hosted runner needed for GPU/ML builds
- Marketplace actions need security vetting
```
