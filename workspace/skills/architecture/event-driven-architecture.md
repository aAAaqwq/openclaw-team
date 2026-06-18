# Event-Driven Architecture

> Level: Advanced | File: `event-driven-architecture.md`
> 
> Design and implementation of event-driven systems: event sourcing, CQRS, 
> message brokers, idempotent consumers, and production operational patterns.

---

## Table of Contents
1. [Core Concepts](#1-core-concepts)
2. [Event Types & Schemas](#2-event-types--schemas)
3. [Message Brokers: Choosing the Right One](#3-message-brokers-choosing-the-right-one)
4. [Event Sourcing](#4-event-sourcing)
5. [CQRS with Events](#5-cqrs-with-events)
6. [Reliable Event Publishing (Outbox)](#6-reliable-event-publishing-outbox)
7. [Idempotent Consumers](#7-idempotent-consumers)
8. [Saga: Distributed Transactions](#8-saga-distributed-transactions)
9. [Error Handling & Dead Letters](#9-error-handling--dead-letters)
10. [Production Operational Patterns](#10-production-operational-patterns)

---

## 1. Core Concepts

### 1.1 What is Event-Driven Architecture?
- **Event**: a record of something that happened (not a command/request)
- **Producer**: emits events without knowing who consumes them
- **Consumer**: subscribes to events without knowing who produced them
- **Event Bus/Broker**: durable, ordered, scalable medium between them

### 1.2 Advantages vs. Request-Response
```
Request-Response (sync):
  Order Service → Payment Service → Inventory Service → Email Service
  Latency = sum of all calls
  Failure in any service = whole request fails

Event-Driven (async):
  Order Service emits OrderCreated event
  Payment Consumer (independent)
  Inventory Consumer (independent)
  Email Consumer (independent)
  
  Latency = Order Service only
  Failure in consumer doesn't block producer
  Easy to add new consumers
```

### 1.3 When to Use / When Not
```
✅ Use event-driven when:
  - Decoupling producers from consumers
  - Multiple services react to the same event
  - Want to add new consumers without changing producers
  - Asynchronous processing is acceptable (eventual consistency)
  - High throughput with burst tolerance

❌ Don't use event-driven when:
  - You need synchronous response (user waits for result)
  - Strong consistency is required across services
  - System is simple (adds unnecessary complexity)
  - You're not ready for eventual consistency debugging
```

---

## 2. Event Types & Schemas

### 2.1 Event Categories
```
Domain Event:
  Something meaningful happened in the domain
  Past tense: OrderCreated, PaymentProcessed, InventoryReserved
  
Integration Event:
  Cross-service communication
  Contains enough context for consumers (don't make consumers call back)
  
Snapshot Event:
  Periodic state snapshot for new consumers to catch up
  OrderStateSnapshot (every hour)

Command Event:
  Directed at a specific service to perform an action
  Future tense: ProcessPayment, ReserveInventory
  (Anti-pattern in pure event-driven — prefer domain events + side effects)
```

### 2.2 Event Schema (CloudEvents + Extensions)
```json
{
  "specversion": "1.0",
  "type": "com.example.order.created.v2",
  "source": "/orders/production",
  "id": "4fd8af02-29f9-4f14-9c10-d7a7429f3f81",
  "time": "2026-05-02T14:30:00.123Z",
  "datacontenttype": "application/json",
  "dataschema": "https://schemas.example.com/order.created.v2.json",
  "data": {
    "orderId": "ord_abc123",
    "userId": "usr_789",
    "items": [
      { "productId": "prod_1", "quantity": 2, "priceCents": 2999 }
    ],
    "totalCents": 5998,
    "currency": "USD"
  },
  "correlationid": "c_request_xyz",
  "partitionkey": "usr_789"
}
```

### 2.3 Versioning Events
```yaml
Strategy: Never modify existing event schemas

Version via new type:
  com.example.order.created.v1 → never touch again
  com.example.order.created.v2 → new consumers subscribe to v2

Migrating consumers:
  1. Subscribe to v2 (dual subscription)
  2. Deploy new consumer code
  3. When all consumers support v2, stop publishing v1
  4. Archive v1 events

Backward-compatible addition:
  New optional fields? Add without changing type
  New required fields? New event type (v2)
```

---

## 3. Message Brokers: Choosing the Right One

### 3.1 Comparison Matrix
| Feature | Kafka | RabbitMQ | Pulsar | SQS/SNS (AWS) | Redis Streams |
|---------|-------|----------|--------|---------------|---------------|
| Throughput | 1M+ msg/s | 10k msg/s | 100k+ msg/s | 10k/s per queue | 100k/s |
| Ordering | Per partition | Per queue | Per partition | FIFO queue (3k/s) | Per stream |
| Retention | Configurable | After ack | Configurable | Up to 14 days | Configurable |
| Delivery | At-least-once | At-most/At-least | At-least-once | At-least-once | At-least-once |
| Replay | ✅ Rewind offset | ❌ | ✅ Rewind | ❌ | ✅ Range |
| Consumer Groups | ✅ | ✅ | ✅ | ❌ (SNS fanout) | ✅ |
| DLQ | Manual | ✅ | ✅ | ✅ | ✅ |
| Ops Complexity | Medium | Low | High | Zero (managed) | Low |
| Best For | High throughput, log storage | Simple pub/sub, RPC | Multi-tenant, geo-replication | Serverless apps | Caching, simple streams |

### 3.2 When to Choose What
```
Kafka: You need >100k msg/s, long retention for replay, log compaction
RabbitMQ: You need routing flexibility (topics, headers), dead letter queues, simple setup
Pulsar: You need multi-tenant, geo-replication, and Kafka-like throughput without Kafka Ops
SQS/SNS: You are all-in on AWS and want zero ops
Redis Streams: You already have Redis, throughput < 100k/s, need simplicity
```

---

## 4. Event Sourcing

### 4.1 Concept
> Store the sequence of events that changed the state, not the current state itself.

```
Current state: Order(id=ord_1, status=paid, total=5998)

Event stream:
  evt_1: OrderCreated(orderId=ord_1, total=5998)
  evt_2: PaymentProcessed(orderId=ord_1, chargeId=ch_abc)
  evt_3: OrderShipped(orderId=ord_1)

To get current state: replay all events in order
```

### 4.2 Event Store Schema
```sql
CREATE TABLE event_store (
  aggregate_id   UUID NOT NULL,         -- ID of the entity
  aggregate_type TEXT NOT NULL,          -- "order", "user", etc.
  version        INT NOT NULL,          -- Monotonic increasing
  event_type     TEXT NOT NULL,         -- "OrderCreated"
  event_data     JSONB NOT NULL,        -- Full event payload
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  PRIMARY KEY (aggregate_id, version),  -- Concurrency control
  UNIQUE (aggregate_id, version)        -- Optimistic lock
);

-- Query: replay events
SELECT * FROM event_store
WHERE aggregate_id = 'ord_abc123'
ORDER BY version ASC;
```

### 4.3 Aggregate Rehydration
```typescript
// Rebuilding current state from events
class Order {
  private events: DomainEvent[] = [];
  
  static fromHistory(events: DomainEvent[]): Order {
    const order = new Order();
    for (const event of events) {
      order.apply(event);
    }
    return order;
  }
  
  private apply(event: DomainEvent): void {
    switch (event.constructor) {
      case OrderCreatedEvent:
        const e = event as OrderCreatedEvent;
        this.id = e.orderId;
        this.userId = e.userId;
        this.items = e.items;
        this.total = e.total;
        this.status = OrderStatus.PENDING;
        break;
      case PaymentProcessedEvent:
        this.status = OrderStatus.PAID;
        this.chargeId = (event as PaymentProcessedEvent).chargeId;
        break;
      case OrderShippedEvent:
        this.status = OrderStatus.SHIPPED;
        break;
    }
  }
  
  // Business method:
  cancel(reason: string): void {
    if (this.status === OrderStatus.SHIPPED) throw new Error('Cannot cancel shipped order');
    this.events.push(new OrderCancelledEvent(this.id, reason));
    this.apply(this.events[this.events.length - 1]);  // Update in-memory state too
  }
}
```

### 4.4 Snapshots (Performance Optimization)
```
Problem: Replaying 100K events to load a single aggregate is slow
Solution: Take snapshots every N events

event_store:
  evt_1: OrderCreated
  evt_2: PaymentProcessed
  ...
  evt_100: ItemAdded
  
snapshot (stored at evt_100):
  { id: "ord_1", status: "pending", total: 8998, itemCount: 3 }

Load: snapshot(evt_100) + events(101...N) → only replay N-100 events

Snapshot strategy:
  - Every 100 events for hot aggregates
  - Every 1000 events for cold aggregates
  - Store in separate table or blob store (compressed JSON)
```

---

## 5. CQRS with Events

### 5.1 Write Model (Command Side)
```typescript
class CreateOrderCommand {
  constructor(public readonly data: CreateOrderRequest) {}
}

class CreateOrderHandler {
  constructor(private readonly eventStore: EventStore) {}
  
  async handle(command: CreateOrderCommand): Promise<void> {
    const orderId = generateId();
    const event = new OrderCreatedEvent({
      orderId,
      userId: command.data.userId,
      items: command.data.items,
      total: command.data.total,
    });
    
    await this.eventStore.append('order', orderId, event);
  }
}
```

### 5.2 Read Model (Query Side)
```
Write events → event stream
                ↓
          Projector (Consumer)
          Builds read model
                ↓
          Read DB (Denormalized / Materialized)

Example read model:
  Table: order_summaries
  - order_id (PK)
  - user_id
  - total
  - item_count
  - status
  - created_at
  - last_updated

This table is built by projectors — NOT written by the command side
```

### 5.3 Projector Implementation
```typescript
// Kafka consumer that builds a materialized view
class OrderSummaryProjector {
  constructor(
    private readonly db: Database,
    private readonly consumer: Consumer
  ) { }
  
  async start(): Promise<void> {
    await this.consumer.subscribe('order.events');
    
    for await (const message of this.consumer) {
      const event = message.value;
      
      await this.db.transaction(async (tx) => {
        switch (event.type) {
          case 'OrderCreated':
            await tx.query(`
              INSERT INTO order_summaries (order_id, user_id, total, status, created_at)
              VALUES ($1, $2, $3, 'pending', $4)
            `, [event.data.orderId, event.data.userId, event.data.total, event.time]);
            break;
            
          case 'PaymentProcessed':
            await tx.query(`
              UPDATE order_summaries SET status = 'paid' WHERE order_id = $1
            `, [event.data.orderId]);
            break;
        }
      });
      
      await this.consumer.commit(message);
    }
  }
}
```

---

## 6. Reliable Event Publishing (Outbox)

### 6.1 The Problem
```
Service A: "Order created" + "Emit event"
              │
              ├── DB write succeeds → event publish fails → DATA INCONSISTENCY
              └── Event publish succeeds → DB write fails → GHOST EVENT
```

### 6.2 Outbox Pattern (Solution)
```
Transaction 1: Write to DB + outbox table (same transaction)
  BEGIN;
    INSERT INTO orders (...) VALUES (...);
    INSERT INTO outbox (event_id, event_type, payload) VALUES (...) ;
  COMMIT;

Background process (reliable publisher):
  SELECT * FROM outbox ORDER BY created_at ASC LIMIT 100;
  FOR each event:
    publish to message broker
    DELETE FROM outbox WHERE event_id = $1 (upon confirmed delivery)
```

### 6.3 Outbox Table Schema
```sql
CREATE TABLE outbox (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  aggregate_id TEXT NOT NULL,
  aggregate_type TEXT NOT NULL,
  event_type   TEXT NOT NULL,
  event_version TEXT NOT NULL DEFAULT 'v1',
  payload      JSONB NOT NULL,
  headers      JSONB NOT NULL DEFAULT '{}',  -- trace context, correlation id
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ,                  -- NULL until published
  attempt_count INT NOT NULL DEFAULT 0,
  last_error   TEXT
);

CREATE INDEX idx_outbox_unpublished 
  ON outbox (created_at) 
  WHERE published_at IS NULL;
```

### 6.4 Outbox Publisher (Reliable)
```typescript
class OutboxPublisher {
  constructor(
    private readonly db: Database,
    private readonly producer: KafkaProducer
  ) { }
  
  async publishBatch(batchSize = 100): Promise<void> {
    const events = await this.db.query(`
      SELECT * FROM outbox 
      WHERE published_at IS NULL AND attempt_count < 10
      ORDER BY created_at ASC 
      LIMIT $1
      FOR UPDATE SKIP LOCKED       -- prevents multiple publishers
    `, [batchSize]);
    
    for (const event of events) {
      try {
        await this.producer.send({
          topic: event.event_type,
          messages: [{
            key: event.aggregate_id,
            value: event.payload,
            headers: { ...event.headers },
          }],
        });
        
        await this.db.query(
          `UPDATE outbox SET published_at = now() WHERE id = $1`,
          [event.id]
        );
      } catch (err) {
        await this.db.query(
          `UPDATE outbox SET 
             attempt_count = attempt_count + 1, 
             last_error = $2 
           WHERE id = $1`,
          [event.id, err.message]
        );
      }
    }
  }
}
```

### 6.5 Alternative: Transactional Outbox with CDC
```
Instead of the background publisher polling the outbox table,
use Debezium (CDC) to stream outbox changes directly to Kafka:

1. Writes to outbox table → Postgres WAL change
2. Debezium captures the WAL change
3. Debezium publishes to Kafka with exactly the right payload
4. No background poller needed
```

---

## 7. Idempotent Consumers

### 7.1 Why Idempotency Matters
```
Kafka guarantees at-least-once delivery (not exactly-once)
Same event may be delivered twice → duplicate processing

Solution: Idempotent consumer — processing an event twice has the same effect
```

### 7.2 Deduplication with Processed Event Table
```typescript
class IdempotentConsumer {
  constructor(private readonly db: Database) {}
  
  async process(event: DomainEvent, handler: () => Promise<void>): Promise<void> {
    // 1. Check dedup table
    const processed = await this.db.query(
      'SELECT 1 FROM processed_events WHERE event_id = $1',
      [event.id]
    );
    
    if (processed.rows.length > 0) {
      // Already processed — skip
      await this.commit(event);  // Still commit offset
      return;
    }
    
    // 2. Process + record dedup (same transaction)
    await this.db.transaction(async (tx) => {
      await handler();
      await tx.query(
        'INSERT INTO processed_events (event_id, processed_at) VALUES ($1, now())',
        [event.id]
      );
    });
    
    // 3. Commit offset
    await this.commit(event);
  }
}

-- Processed events table (auto-clean old entries)
CREATE TABLE processed_events (
  event_id     TEXT PRIMARY KEY,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Cleanup old entries (TTL: 7 days)
DELETE FROM processed_events WHERE processed_at < now() - interval '7 days';
```

### 7.3 Ordering Considerations
```
Single Partition Ordering:
  - Within a partition, events are ordered
  - Kafka: messages with same key go to same partition
  - Always produce with entity ID as key: key = orderId
  
Cross-Partition Ordering:
  - NO global ordering guarantee
  - If event A before event B matters, they MUST be in the same partition
  - Anti-pattern: "event B before event A arrived" handling in consumer
```

---

## 8. Saga: Distributed Transactions

### 8.1 Choreography Saga
```
Order Service                    Payment Service                 Inventory Service
    │                                │                                │
    │── OrderCreated ──────────────►│                                │
    │                                │── PaymentProcessed ──────────►│
    │                                │                                │── InventoryReserved
    │◄──────────────────────────────│                                │
    │ (Payment Failed?)              │                                │
    │── OrderCancelled ────────────►│                                │
    │                                │── PaymentRefunded ───────────►│
    │                                │                                │── InventoryReleased

Pros: Simple, no coordinator, easy to add steps
Cons: Hard to trace, circular dependencies possible
```

### 8.2 Orchestrator Saga
```
                          ┌──────────────────────┐
                          │   Saga Orchestrator   │
                          │                      │
                          │  1. Create Order    │
                          │  2. Process Payment │
                          │  3. Reserve Inv.    │
                          │  4. If fail → rollback
                          └───────┬──────────────┘
                                  │
          ┌─────────────┬─────────┼──────────┬──────────────┐
          │             │         │          │              │
          ▼             ▼         ▼          ▼              ▼
    Order Service  PaymentSvc  Inventory  Notification  [Compensations]

Pros: Centralized orchestration, clear saga state, easy rollback
Cons: Single point of failure (orchestrator), coupling to orchestrator
```

### 8.3 Orchestrator Implementation
```typescript
class CreateOrderSaga {
  private state: SagaState;
  
  constructor(
    private readonly orderSvc: OrderServiceClient,
    private readonly paymentSvc: PaymentServiceClient,
    private readonly inventorySvc: InventoryServiceClient,
    private readonly sagaStore: SagaStore
  ) { }
  
  async execute(data: CreateOrderRequest): Promise<void> {
    this.state = SagaState.PENDING;
    
    try {
      // Step 1
      const order = await this.orderSvc.createOrder(data);
      this.state = SagaState.ORDER_CREATED;
      
      // Step 2
      const payment = await this.paymentSvc.processPayment({
        orderId: order.id,
        amount: order.total,
      });
      this.state = SagaState.PAYMENT_PROCESSED;
      
      // Step 3
      await this.inventorySvc.reserveItems(order.items);
      this.state = SagaState.COMPLETED;
      
    } catch (error) {
      // Rollback in reverse order
      switch (this.state) {
        case SagaState.PAYMENT_PROCESSED:
          await this.paymentSvc.refund({ orderId: data.orderId });
          // Fall through
        case SagaState.ORDER_CREATED:
          await this.orderSvc.cancelOrder(data.orderId);
        case SagaState.PENDING:
          break;
      }
      throw error;
    }
  }
}

// Saga store enables recovery from failures
interface SagaStore {
  saveState(sagaId: string, state: SagaState): Promise<void>;
  getState(sagaId: string): Promise<SagaState>;
}
```

---

## 9. Error Handling & Dead Letters

### 9.1 Consumer Error Handling
```
Retry Policy:
  ┌─ Non-retryable error (validation, schema mismatch) → DLQ immediately
  ├─ Retryable error (DB timeout, network blip) → retry with backoff
  └─ After max retries → DLQ

Retry Delay:
  Attempt 1: 0s
  Attempt 2: 1s
  Attempt 3: 5s
  Attempt 4: 30s
  Attempt 5: 2min
  Attempt 6: 10min  ← max
```

### 9.2 Dead Letter Queue (DLQ) Architecture
```
                  ┌─────────────┐
  Event ─────────►│ Main Queue  │──► Consumer
                  └──────┬──────┘
                         │ (max retries exceeded)
                         ▼
                  ┌─────────────┐
                  │  DLQ Queue   │──► DLQ Consumer
                  └─────────────┘    → Log error
                                     → Notify team
                                     → Store for replay
```

### 9.3 DLQ Consumer
```typescript
class DeadLetterConsumer {
  async handle(dlqMessage: DeadLetterEvent): Promise<void> {
    const { originalEvent, error, attempts } = dlqMessage;
    
    // 1. Log the failure
    logger.error({
      eventId: originalEvent.id,
      eventType: originalEvent.type,
      error: error.message,
      attempts,
    }, 'Event moved to DLQ');
    
    // 2. Store for analysis
    await this.store.saveDlqEvent(dlqMessage);
    
    // 3. Alert if critical event type
    if (this.isCriticalEvent(originalEvent.type)) {
      await this.alerter.send({
        message: `DLQ: ${originalEvent.type} failed after ${attempts} attempts`,
        severity: 'warning',
        runbook: 'https://runbook.example.com/dlq-handling',
      });
    }
  }
  
  // Manual replay
  async replay(eventId: string): Promise<void> {
    const dlqEvent = await this.store.getDlqEvent(eventId);
    if (!dlqEvent) throw new Error('Event not found in DLQ');
    await this.producer.send({
      topic: dlqEvent.originalTopic,
      key: dlqEvent.originalEvent.aggregateId,
      value: dlqEvent.originalEvent.payload,
    });
  }
}
```

---

## 10. Production Operational Patterns

### 10.1 Event Observability
```
Metrics to monitor (per topic/consumer group):
  - Events produced/s (rate)
  - Events consumed/s (rate)
  - Consumer lag (latency between produce and consume)
  - Processing duration (p50/p95/p99)
  - Error rate (processing failures)
  - DLQ depth (stuck events)

Dashboards:
  Row 1: Produce rate, Consume rate, Consumer lag
  Row 2: Processing duration p50/p95/p99
  Row 3: Error rate by event type, DLQ depth
  Row 4: Partition distribution, throughput per partition
```

### 10.2 Consumer Lag Alert
```promql
// PromQL — Alert on consumer lag > 1M or > 10min
max(kafka_consumer_lag{group=~"order.*"}) > 1000000
OR
(
  rate(kafka_consumer_current_offset[5m])
  /
  rate(kafka_consumer_lag[5m])
) < 0.1
```

### 10.3 Event Replay Strategy
```
Right-to-Deletgate:
  - Every event is immutable and retrievable
  - Downstream consumers can rewind to any point
  - New consumers catch up from stream

Replay Use Cases:
  1. New consumer deployment: read all events and build read model
  2. Bug fix: fix consumer, rewind offset, reprocess
  3. Data corruption: rebuild read model from event stream
  4. Audit: verify what happened at any point in time
```

### 10.4 Operational Checklist
```
□ Every event has a unique ID (idempotency key)
□ Every event has a timestamp (event time, not system time)
□ Event schemas are versioned and never mutated
□ Each consumer has a dead letter queue configured
□ Consumer group lag is monitored and alerted
□ Event retention is configured (min 7 days for replay)
□ Critical events have end-to-end latency monitoring
□ Outbox pattern is used for reliable publishing
□ Processed events dedup table has cleanup job
□ Saga state is persisted for recovery
□ DLQ review process is established (daily for critical topics)
```

### 10.5 Common Pitfalls
```
❌ Too many topics: one event type per topic (not one per domain)
❌ Fat events: sending 10MB payloads in events (send reference + context)
❌ No schema registry: event formats drift between services
❌ Ordering assumptions: assuming global ordering across partitions
❌ Synchronous side effects: mixing sync HTTP calls inside async consumers
❌ Missing idempotency: double processing causes data corruption
```
