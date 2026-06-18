# Data-Intensive Applications

> Level: Advanced | File: `data-intensive-apps.md`
> 
> Designing, building, and operating systems that handle large volumes of data reliably,
> scalably, and maintainably — drawing from Kleppmann's "DDIA" and production experience.

---

## Table of Contents
1. [Reliability, Scalability, Maintainability](#1-reliability-scalability-maintainability)
2. [Data Models & Storage Engines](#2-data-models--storage-engines)
3. [Replication Patterns](#3-replication-patterns)
4. [Partitioning (Sharding)](#4-partitioning-sharding)
5. [Consistency & Consensus](#5-consistency--consensus)
6. [Batch Processing](#6-batch-processing)
7. [Stream Processing](#7-stream-processing)
8. [The Lambda & Kappa Architectures](#8-the-lambda--kappa-architectures)
9. [Data Serialization & Schemas](#9-data-serialization--schemas)
10. [Distributed Transactions in Practice](#10-distributed-transactions-in-practice)

---

## 1. Reliability, Scalability, Maintainability

### 1.1 Reliability: "The system should work correctly even when things go wrong"

```
Faults to handle:
  Hardware: disk failure, memory bit-flip, network partition (rare but real)
  Software: OS bugs, dependency incompatibility, resource leaks
  Human: config errors, deploy mistakes, fat-finger commands

Reliability budget:
  99.9% uptime = 8.7h downtime/year → plan for 10x worse
  99.99% = 52.6 min/year → multi-AZ, auto-failover required
  99.999% = 5.26 min/year → active-active multi-region, automated rollback

Mitigation:
  - Fault tolerance: design for expected failures
  - Chaos engineering: test against unexpected ones
  - Graceful degradation: degrade features, don't crash
```

### 1.2 Scalability: "The system should handle growth"

```
Measuring load:
  - Twitter: ~300M DAU, 500M tweets/day, home timeline fanout
  - Kafka: ~1M msg/s for medium cluster, millions at peak
  - YouTube: ~500h video uploaded/minute

Describing load:
  Requests per second (QPS) — API server
  Read/write ratio — cache sizing, replica count
  Data volume — storage, network bandwidth, backup window

Describing performance:
  Throughput: records/sec or MB/sec
  Latency: p50 (median), p95, p99, p999
  Head-of-line blocking: p99 matters because one slow request blocks others

Scaling strategies:
  Vertical      (bigger machine) — simpler, has limit
  Horizontal    (more machines) — harder, but theoretically unbounded
  Read replicas — offload reads to replicas
  Caching       — reduce repeated expensive computation
  Sharding      — distribute data across nodes
```

### 1.3 Maintainability: "Humans should be able to work on it"

```
Operability: good ops team can keep system running
  - Visibility into runtime behavior (monitoring)
  - Good defaults + override ability
  - Self-healing where possible
  - Predictable behavior

Simplicity: reduce accidental complexity
  - Well-defined abstractions hide complexity
  - Extract shared concerns (auth, logging, config)
  - Avoid NIH syndrome

Evolvability: easy to change
  - Loose coupling between services
  - Careful versioning of APIs and events
  - Feature flags for gradual rollout
  - Strangler pattern for replacing systems
```

---

## 2. Data Models & Storage Engines

### 2.1 Relational vs. Document vs. Graph

| Aspect | Relational | Document | Graph |
|--------|-----------|---------|-------|
| Data | Tables, rows, joins | JSON/BSON documents | Nodes, edges, properties |
| Relationships | Foreign keys, JOIN | Embedded/references | First-class edges |
| Schema | Strict (DDL) | Flexible | Flexible |
| Query | SQL | Aggregation pipelines | Graph traversal (Gremlin, Cypher) |
| Best for | Structured, ACID | Semi-structured, fast iteration | Highly connected data |
| Examples | PostgreSQL, MySQL | MongoDB, Couchbase | Neo4j, Dgraph |

### 2.2 Storage Engine: LSM-Tree vs. B-Tree

```
B-Tree (PostgreSQL, MySQL InnoDB):
  Pages: 4KB-16KB fixed size pages
  Writes: Direct page overwrite (in-place update)
  WAL: Write-Ahead Log for crash recovery
  Read: Low overhead, 1-3 page reads per lookup
  Write amplification: Moderate (write to WAL + page + occasionally split)
  Compaction: On split — localized
  Best for: Read-heavy workloads, single-row lookups

LSM-Tree (Cassandra, RocksDB, LevelDB, Bigtable):
  Structure: In-memory memtable → SSTable files on disk
  Writes: Append-only (no overwrite), very fast sequential writes
  Read: Must check multiple files + Bloom filters (false positive risk)
  Write amplification: High (compaction merges SSTables)
  Compaction: Continuous background merging (tunable)
  Best for: Write-heavy workloads, time-series, high throughput ingestion

| Writes               | B-Tree: ~10k ops/s      | LSM-Tree: ~100k+ ops/s  |
| Reads (point)        | B-Tree: ~50k ops/s      | LSM-Tree: ~20k ops/s    |
| Reads (range)        | B-Tree: ~5k ops/s       | LSM-Tree: ~15k ops/s    |
| Storage efficiency   | B-Tree: ~70-80%         | LSM-Tree: ~50-60% (before compaction) |
```

### 2.3 Column-Oriented Storage (OLAP vs. OLTP)

```
OLTP (Online Transaction Processing):
  - Row-oriented (PostgreSQL, MySQL)
  - Reads: entire row (SELECT *)
  - Writes: insert/update a row at a time
  - Indexes: per-row B-tree
  - Best for: low latency, high concurrency, small writes

OLAP (Online Analytical Processing):
  - Column-oriented (ClickHouse, Redshift, BigQuery, Parquet)
  - Reads: specific columns across many rows (SUM, COUNT, GROUP BY)
  - Compression: column compression (run-length, delta, dictionary) — 10x
  - Writes: batch inserts (rarely single row)
  - Vectorized execution: CPU SIMD over compressed data

Choose: OLTP for app data, OLAP for analytics (export via CDC/batch)
```

---

## 3. Replication Patterns

### 3.1 Single-Leader (Master-Replica)

```
Leader: accepts writes
Replicas: asynchronously replicate from leader

Use cases: Most applications (PostgreSQL, MySQL, Redis, MongoDB)
Trade-off:
  Leader write = bottleneck
  Async replication = replication lag (eventual consistency)
  Sync replication = write delay (at least one replica must confirm)

Read-after-write consistency:
  - Read-your-writes: route reads for recently modified data to leader
  - Monotonic reads: route reads per user to the same replica (hash of user_id)

Replication lag handling:
  - If lag > threshold, route to leader (on condition, not always)
  - If consumer lag in event system, produce to same partition key
```

### 3.2 Multi-Leader

```
Two or more leaders accept writes
Each leader replicates to others

Use cases:
  - Multi-datacenter: write in local DC, async replicate cross-DC
  - Offline-capable clients: calendar, note apps (sync when online)
  - Collaborative editing: CRDT-based (Figma, Google Docs)

Problems:
  - Write conflicts: same record modified in two DCs simultaneously
  - Conflict resolution strategies:
    a. "Last write wins" (LWW) — easy but data loss
    b. CRDTs (Conflict-Free Replicated Data Types) — merge automatically
    c. Custom conflict handler — manual merge or prompt user
```

### 3.3 Leaderless (Dynamo-style)

```
All nodes accept writes and reads
N = replication factor, W = write quorum, R = read quorum

Quorum conditions:
  Typical: N=3, W=2, R=2 → any 2 of 3 nodes for both reads and writes
  Strong: W + R > N → read quorum includes at least one node with latest write

Use cases:
  - Cassandra, DynamoDB, ScyllaDB, Riak
  - High availability (tolerates node failures without leader election)
  - Always writable (even during network partitions)

Problems:
  - Sloppy quorum: if too few replicas available, may accept write temporarily
  - Hinted handoff: write to a different node, forward to correct node later
  - Read repair: background process fixes stale data
```

### 3.4 Replication Strategy Decision

```
Need strong consistency across replicas?
  ├── Yes → Single-leader + synchronous replication (limited scale)
  └── No → 
    Need multi-datacenter writes?
      ├── Yes → Multi-leader (resolve conflicts)
      └── No → 
        Need always-on write availability?
          ├── Yes → Leaderless (Dynamo-style)
          └── No → Single-leader (async replication) ← 90% of apps
```

---

## 4. Partitioning (Sharding)

### 4.1 Partitioning Strategies

```
Key Range Partitioning:
  Partition 1: keys A-F
  Partition 2: keys G-L
  Partition 3: keys M-R
  Partition 4: keys S-Z
  
  Pros: Range scans are efficient, easy to split hot partitions
  Cons: Access skew (hot keys), splitting requires careful planning

Hash Partitioning:
  Partition = hash(key) % N
  
  Pros: Even distribution (assuming good hash function)
  Cons: Range queries hit all partitions, resharding = full rehash

Consistent Hashing:
  Ring of positions, each node responsible for range
  Added node takes responsibility from neighbors
  
  Pros: Minimal data movement on node add/remove
  Cons: Non-uniform load (virtual nodes help)

Document Partitioning:
  Secondary index → scatter/gather query to all partitions

  If global secondary index: every write updates the index → cross-partition coordination
  If local secondary index: query all partitions and merge
```

### 4.2 Resharding Strategies

```
Pre-splitting (recommended):
  Create more partitions than you expect to need
  Map partitions to physical nodes logically (not fixed)
  
  Example: 1024 virtual partitions mapped to 16 physical nodes
  Adding a 17th node: move 60 partitions from existing nodes → each loses ~3.5%

Re-sharding:
  1. Create new set of partitions
  2. Dual-write to both old and new partitions
  3. Backfill old data to new partitions
  4. Verify consistency (count, checksum, sample)
  5. Switch reads to new layout
  6. Drop old partitions
```

### 4.3 Partitioning Hot Spot Mitigation

```
Issue: A single key (celebrity tweet, viral product) gets 1000x normal traffic

Solutions:
  1. Break hot key into sub-keys
     key = "user_123" → key = "user_123_0", "user_123_1", ..., "user_123_N"
     Write: distribute across sub-keys
     Read: aggregate from all sub-keys

  2. Cache the hot key (pre-warm low-churn items)
  
  3. Dedicated partition for hot data
     DynamoDB: adaptive capacity — automatically splits hot partitions
  
  4. Replica reads for hot read-only data
```

---

## 5. Consistency & Consensus

### 5.1 Consistency Models Spectrum

```
                     Lower Latency ──────────────►
                     
Eventual ─── Causal ─── Read-after-Write ─── Monotonic ─── Strong (Linearizability)

                     ◄───────── Higher Cost

Eventual: replicas converge eventually (DNS, CDN)
  - "Inconsistent state may persist but will resolve"

Causal: causally related operations are seen in order
  - "If A happened before B, everyone sees A before B"
  - Implements: vector clocks, version vectors

Read-after-write: user sees their own writes
  - Route reads through leader for affected data
  - Pro tip: timestamp-based read routing

Strong (Linearizability): reads return the latest write
  - Makes the system behave as if there's one copy
  - Cost: 2-3x latency, limited throughput (single leader bottleneck)
  - Implementations: Spanner (TrueTime), ZooKeeper (Zab), etcd (Raft)
```

### 5.2 Consensus Algorithms

```
Paxos:
  - Theoretical foundation for all consensus
  - Two phases: Prepare/Promise + Accept/Accepted
  - Complex to implement correctly
  - Variants: Multi-Paxos, Fast Paxos, Cheap Paxos

Raft:
  - Designed for understandability (not performance, but close enough)
  - Leader election: random timeouts → candidate → leader
  - Log replication: leader accepts writes, replicates to followers
  - Safety: at most one leader per term, committed entries never lost
  - Used by: etcd, Consul, Kafka (KIP-500)

Zab (ZooKeeper Atomic Broadcast):
  - Similar to Raft
  - Leader election + atomic broadcast
  - Used by: Apache ZooKeeper (Kafka metadata, HBase)

Practical consensus ≠ linearizability:
  - Raft only provides linearizable reads through the leader
  - Follower reads without leader quorum = stale reads
  - ZooKeeper: sync() before read for linearizability
```

### 5.3 Distributed Transactions: 2PC (Two-Phase Commit)

```
Phase 1 (Prepare):
  Coordinator → Participant A: "Prepare to commit?"
  Coordinator → Participant B: "Prepare to commit?"
  Participants: "Yes" (with lock) or "No"

Phase 2 (Commit):
  If all said "Yes": Coordinator → A + B: "Commit!"
  If any said "No":  Coordinator → A + B: "Abort!"

Problems with 2PC:
  1. Coordinator = single point of failure
  2. Locks held during prepare phase (can be minutes in network partition)
  3. Logging for recovery (coordinator must log every decision)
  
Better alternatives:
  - Usually: don't use 2PC — use Saga (eventual consistency)
  - When necessary: XA transactions (database-level, limited to one DB type)
```

---

## 6. Batch Processing

### 6.1 MapReduce Philosophy
```
Map: "Select relevant records, transform them"
Reduce: "Aggregate/combine mapped results"

Modern implementation:
  Map = SQL SELECT + WHERE
  Reduce = GROUP BY + aggregate functions

  Spark: Dataset transformations (map, filter, flatMap → groupBy, reduceByKey, aggregate)
  Hadoop: Java MapReduce (legacy)
  
Common batch jobs:
  - Daily report generation
  - Hourly data sync between systems
  - ETL pipelines
  - Model training data preparation
```

### 6.2 Spark — Structured Streaming Defaults
```scala
// Batch: read from S3, transform, write to ClickHouse
val orders = spark.read
  .format("parquet")
  .load("s3://data/orders/dt=2026-05-01/")
  .filter($"status" === "paid")
  .groupBy($"product_id")
  .agg(
    sum($"amount") as "revenue",
    count("*") as "order_count"
  )
  .write
  .mode("overwrite")
  .format("jdbc")
  .option("url", "jdbc:clickhouse://...")
  .save()
```

### 6.3 Batch Job Reliability
```
Idempotency: Running the same batch twice produces the same result
  - Use output table partitioning: overwrite partition each run
  
Exactly-once output semantics:
  - Job fails mid-write → output in partial state
  - Solution: write to staging table, rename on success
  - Spark: .option("checkpointLocation", ...) + idempotent sink

Monitoring:
  - Row count in = row count out
  - Data quality checks (null ratios, uniqueness, referential integrity)
  - Job duration vs baseline (alert if > 2x expected)
```

---

## 7. Stream Processing

### 7.1 Stream vs. Batch

| Aspect | Batch | Stream |
|--------|-------|--------|
| Data | Complete, bounded | Unbounded, arriving over time |
| Latency | Minutes to hours | Milliseconds to seconds |
| Output | After all data processed | Continuously (micro-batch or per-event) |
| Accuracy | Exactly once | Depends on stream semantics |
| Reprocessing | Re-run the batch | Rewind consumer offset |
| Example | Daily ETL | Real-time fraud detection |

### 7.2 Stream Processing Frameworks

```
Apache Kafka Streams:
  - Library (not cluster) — runs in your app
  - Exactly-once semantics with Kafka transactions
  - State store: RocksDB (LSM-tree) for windowed joins/aggregations
  - Best for: Kafka-native, small to medium complexity

Apache Flink:
  - True streaming (not micro-batch) with low latency
  - Event-time processing, watermarks, out-of-order handling
  - Stateful processing: checkpointed state for exactly-once
  - Best for: complex event processing, large state

Apache Spark Structured Streaming:
  - Micro-batch (default) or continuous processing
  - Exactly-once sink with checkpointing
  - Best for: teams already using Spark for batch
```

### 7.3 Joins in Streams

```
Windowed Join (KStream-KStream):
  Join two streams within a time window
  Example: "Order" + "Payment" within 5 minutes

Table-Table Join (KTable-KTable):
  Join two changelog streams (current state)
  Example: "Current orders" + "Current user profiles"

Stream-Table Join (KStream-KTable):
  Enrich event with current state
  Example: Order event + User profile (enrich with user's current tier)

Out-of-order handling:
  - Watermark: "No events with t < watermark will arrive"
  - Late events: drop, side-channel to separate stream, or trigger correction
```

### 7.4 Exactly-Once Semantics in Streams

```
Source (Kafka) → Stream Processor → Sink (Kafka/DB)

Idempotent Producer:
  - Kafka: enable.idempotence=true → no duplicate writes within a producer session

Transactional Writes:
  - Kafka Streams: processing.guarantee=exactly_once_v2
  - Writes to sink Kafka are atomic with offset commits
  - If crash: consumer doesn't commit → re-processes → idempotent producer doesn't duplicate

Sink to DB:
  - Outbox pattern: write result to DB + commit offset in same transaction
  - Idempotent upsert: INSERT ... ON CONFLICT DO NOTHING / UPDATE
```

---

## 8. The Lambda & Kappa Architectures

### 8.1 Lambda Architecture
```
                    ┌──────────────┐
    Stream Data ───►│ Speed Layer   │───► Real-time view
                    │ (Stream proc) │       (approximate)
                    └──────────────┘
                                      Merge
                    ┌──────────────┐    │
    Batch Data ────►│ Batch Layer   │────┘──► Serving layer
                    │ (MapReduce/  │       (accurate)
                    │  Spark batch)│
                    └──────────────┘

Problems with Lambda:
  - Two codebases (stream + batch) → double maintenance
  - Two code paths that should produce the same result → often don't
  - Hard to test: Kappa architecture is now preferred
```

### 8.2 Kappa Architecture
```
    Stream Data ──► Kafka ──► Stream Processor ──► Serving DB
                              (Single codebase,
                               reprocess from topic)

Key insight: "Batch is just a special case of stream"
  - To reprocess: start a new consumer from beginning of topic
  - No separate batch layer
  - Single codebase, single deployment

When Kappa works:
  - Kafka has sufficient retention (or you use tiered storage)
  - Stream processor supports state (Flink, Kafka Streams)
  - You can tolerate the reprocessing cost (it's compute, not code)

When Lambda still makes sense:
  - Batch is data from external sources (not Kafka)
  - Stream processor can't handle the full historical data volume
  - You need SQL-based ETL for non-technical users (analysts)
```

---

## 9. Data Serialization & Schemas

### 9.1 Serialization Formats

| Format | Schema | Speed | Size | Evolvability | Best For |
|--------|--------|-------|------|-------------|----------|
| JSON | No | Slow | Large | Excellent | Human-readable APIs |
| Protocol Buffers | .proto | Fast | Small | Good | Service-to-service, storage |
| Avro | .avsc (JSON) | Fast | Small | Excellent | Hadoop, Kafka (compact + splittable) |
| Thrift | .thrift | Fast | Small | Good | Thrift-native systems |
| MessagePack | No | Fast | Medium | Good | JSON replacement (binary) |
| Parquet | Columnar schema | Fast | Very small (compressed) | Good | Analytical queries, columnar storage |

### 9.2 Schema Evolution Rules

```
Protocol Buffers:
  ✅ CAN add new field (with tag number, default value)
  ✅ CAN remove field (deprecate tag, don't reuse)
  ❌ Cannot change type of existing field
  ❌ Cannot change tag number
  ⚠️ Rename is fine (wire format uses tags, not names)

Avro:
  ✅ CAN add field with default
  ✅ CAN remove field with default
  ✅ CAN change type with Avro union
  ❌ Cannot remove required field (no default)
  
Best practice: Use Schema Registry (Confluent Schema Registry for Avro/Protobuf)
```

### 9.3 Schema Registry Pattern
```
Producer: 
  Register schema → get schema ID → serialize data with schema ID → send to Kafka

Consumer:
  Read message → extract schema ID → fetch schema from registry → deserialize

Storage:
  Kafka message = schema ID (4 bytes) + serialized data
  Schema stored separately → messages are compact

Benefits:
  - Schema evolves without breaking consumers (compatibility checks)
  - Forward and backward compatibility enforced
  - Centralized schema management
```

---

## 10. Distributed Transactions in Practice

### 10.1 Practical Decision Tree
```
Need to update multiple systems atomically?
├── Systems are in the same DB? → DB Transaction (BEGIN/COMMIT)
├── Systems are in the same transaction manager? → XA (rarely recommended)
├── Systems are microservices with queues? → Outbox pattern + Saga
├── Systems are microservices with no queues? → Outbox + event bus + Saga
└── Systems can tolerate inconsistency? → Idempotent operations + reconciliation

Rule of thumb:
  - 90% of "distributed transactions" can be solved with:
    Outbox + Idempotent Consumers + Saga Orchestration
  - 9% don't need transactionality at all (retry is fine)
  - 1% actually need 2PC (and you should exhaust all alternatives first)
```

### 10.2 Reconciliation (Compensating for Failures)
```
Despite best efforts, some inconsistencies will happen.

Reconciliation process:
  1. Periodic batch job compares systems
  2. Identify discrepancies: records in A but not B, wrong state, wrong amounts
  3. Automatically fix 95% of discrepancies (diff → apply)
  4. Escalate remaining 5% to human review

Example: Payment reconciliation
  Every hour:
    SELECT orders WHERE status = 'paid' AND charge_id IS NOT NULL
    Compare with payment provider's settlement report
    Flag: orders marked paid but no matching payment (can happen)
    Auto-fix: mark as failed, refund, notify user
```

### 10.3 Production Checklist for Data-Intensive Systems
```
□ Replication strategy chosen and tested (sync vs async)
□ Partitioning strategy handles hot spots
□ Consistency requirements are documented per operation
□ Error budget defined for replication lag
□ Schema evolution planned (forward/backward compatibility)
□ Outbox pattern in place for event publishing
□ Exactly-once or at-least-once semantics confirmed per consumer
□ Dead letter queue configured for all stream consumers
□ Reconciliation job in place for payment/critical flows
□ Monitoring: replication lag, consumer lag, partition skew, dead letter depth
□ Disaster recovery: can rebuild from events?
```
