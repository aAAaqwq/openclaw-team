# Database Master

> Level: Advanced | File: `database-master.md`
> 
> Relational and NoSQL database design, optimization, migration, and production operations.
> PostgreSQL-focused with MySQL, NoSQL, and NewSQL patterns.

---

## Table of Contents
1. [SQL vs NoSQL Decision Tree](#1-sql-vs-nosql-decision-tree)
2. [Relational Database Design](#2-relational-database-design)
3. [Index Design & Optimization](#3-index-design--optimization)
4. [Query Optimization (EXPLAIN)](#4-query-optimization-explain)
5. [ORM Anti-Patterns](#5-orm-anti-patterns)
6. [Sharding & Partitioning](#6-sharding--partitioning)
7. [Replication & High Availability](#7-replication--high-availability)
8. [Migration Strategies (Zero-Downtime)](#8-migration-strategies-zero-downtime)
9. [Distributed ID Generation](#9-distributed-id-generation)
10. [Production Runbooks](#10-production-runbooks)

---

## 1. SQL vs NoSQL Decision Tree

```
Is data structured and relational?
├── Yes → Need ACID?
│   ├── Yes → PostgreSQL (general purpose)
│   │           MySQL (simple web, read-heavy)
│   │           CockroachDB (distributed, multi-region)
│   └── No → Write throughput > 100k QPS?
│       ├── Yes → NoSQL path (below)
│       └── No → PostgreSQL (JSONB handles semi-structured)
└── No → Data model fixed?
    ├── Yes → DynamoDB / Cassandra
    └── No → Document (MongoDB) / Graph (Neo4j)
```

### Quick Reference by Scenario
| Scenario | Recommended | Why |
|----------|-------------|-----|
| E-commerce orders | PostgreSQL | ACID, complex joins, JSONB for flexible attributes |
| User sessions | Redis | Sub-ms latency, TTL expiry |
| IoT time-series | TimescaleDB / InfluxDB | Columnar compression, window functions |
| Full-text search | Elasticsearch | Inverted index, fuzzy matching, faceted search |
| Social graph | Neo4j | Graph traversal (friends-of-friends, recommendations) |
| Log aggregation | ClickHouse | Columnar, 10x compression, sub-second aggregations |
| Doc snapshots | MongoDB | Schema-flexible, embedded documents |
| Distributed SQL | CockroachDB | Multi-region, strong consistency, PostgreSQL wire protocol |
| Key-value at scale | DynamoDB / ScyllaDB | Predictable p99, auto-scaling |

---

## 2. Relational Database Design

### 2.1 Schema Design Principles
- **Normalize until it hurts, denormalize until it works**
- Third Normal Form (3NF) as baseline; denormalize only for query performance
- Every table needs a primary key (UUID/ULID preferred over auto-increment)
- Use `TIMESTAMPTZ` over `TIMESTAMP` (PostgreSQL) — store in UTC always
- Avoid ENUMs: use lookup tables or VARCHAR CHECK constraints

### 2.2 Column Type Guide (PostgreSQL)

| Data | Best Type | Avoid |
|------|-----------|-------|
| Money | `NUMERIC(12,2)` or `BIGINT` (cents) | `FLOAT`/`DOUBLE` (floating point errors) |
| User ID | `UUID` or `TEXT` | `SERIAL` (sequential, fingerprintable) |
| IP Address | `INET` | `VARCHAR(45)` |
| Timestamp | `TIMESTAMPTZ` | `TIMESTAMP` (no TZ, human error) |
| Tags | `TEXT[]` | JSONB for simple arrays |
| Flexible attributes | `JSONB` + GIN index | JSON (no indexing) |
| Geo coordinates | `GEOGRAPHY(POINT)` | Two `FLOAT` columns |

### 2.3 Constraints as Documentation
```sql
CREATE TABLE orders (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    amount      NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    status      TEXT NOT NULL CHECK (status IN ('pending','paid','shipped','cancelled')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 3. Index Design & Optimization

### 3.1 B-Tree (Default) — The Workhorse
- **Best for**: equality + range queries
- **High cardinality**: columns with many unique values
- **Anti-pattern**: index on low-cardinality boolean column (use partial index instead)

### 3.2 Composite Index Rules
```
Rule 1: Leftmost prefix — index (a, b, c) covers:
  ✅ WHERE a = ?
  ✅ WHERE a = ? AND b = ?
  ✅ WHERE a = ? AND b = ? AND c = ?
  ❌ WHERE b = ?          (no a prefix)
  ❌ WHERE a = ? AND c = ? (skips b; uses only 'a' part)

Rule 2: Place equality conditions first, range conditions last
  ✅ INDEX(user_id, created_at)  — WHERE user_id = ? AND created_at > ?
  ❌ INDEX(created_at, user_id)  — range-first loses selectivity

Rule 3: Covering index — include extra columns via INCLUDE clause (PostgreSQL):
  CREATE INDEX idx_orders_user ON orders(user_id) INCLUDE (amount, status);
  -- Query only hits the index, no table heap access
```

### 3.3 Special Index Types

| Type | Best For | Notes |
|------|----------|-------|
| **GIN** | JSONB, arrays, full-text search | Multi-key, larger |
| **GiST** | Geography, range overlap, full-text | Slower build, good for exclusion constraints |
| **BRIN** | Append-only, physically ordered tables | 100x smaller than B-tree; excellent for time-series |
| **Hash** | Equality only | Rarely beats B-tree; not WAL-logged in some DBs |
| **Partial** | Filtered queries | `CREATE INDEX idx_active ON users(email) WHERE active = true;` |
| **Expression** | Function-based queries | `CREATE INDEX idx_lower_email ON users(LOWER(email));` |

### 3.4 BRIN for Time-Series (Production Use Case)
```sql
-- 1 billion rows, append-only log table
-- B-tree index: ~100 GB
-- BRIN index:  ~1 GB, almost as fast for range queries

CREATE INDEX idx_logs_created_brin 
ON event_logs USING BRIN (created_at)
WITH (pages_per_range = 32);  -- Tune: smaller = more accurate, larger = smaller index
```

### 3.5 Index Maintenance
```sql
-- PostgreSQL: Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0;  -- Unused indexes (candidate for removal)

-- Rebuild index (less bloat; concurrent version avoids lock)
REINDEX INDEX CONCURRENTLY idx_orders_created;
```

---

## 4. Query Optimization (EXPLAIN)

### 4.1 PostgreSQL EXPLAIN (ANALYZE, BUFFERS)
```sql
EXPLAIN (ANALYZE, BUFFERS, TIMING) 
SELECT * FROM orders WHERE user_id = 'abc' AND created_at > '2026-01-01';
```

**Interpretation:**
```
Seq Scan on orders  (cost=0.00..100000.00 rows=1 width=100) 
  Filter: ((user_id = 'abc'::uuid) AND (created_at > '2026-01-01'::date))
  Rows Removed by Filter: 5000000
  Buffers: shared hit=500, read=1000
  Planning Time: 0.1 ms
  Execution Time: 1500 ms
```
**Symptoms:**
- `Seq Scan` on large table → 🚩 Missing index
- `Rows Removed by Filter` much larger than returned → 🚩 Need better selectivity
- `Buffers` with `read` (not `hit`) → 🚩 Not in cache

### 4.2 Performance Targets
```
                 Good     Needs Work     🚩 Critical
─────────────────────────────────────────────────
Seq Scan         < 10k    < 100k         > 1M rows scanned
Index Scan       < 50     < 500          > 5k rows returned
Nested Loop      < 1k     < 10k          > 100k iterations
Hash Join        < 10k    < 100k         > 1M rows per side
Sort             < 10k    < 100k         > 1M rows sorted
Shared Hit       > 99%    > 95%          < 90%
```

### 4.3 Common Slow Queries & Fixes
```sql
-- BAD: Function on indexed column prevents index use
SELECT * FROM users WHERE DATE(created_at) = '2026-01-01';
-- FIX: Range query
SELECT * FROM users WHERE created_at >= '2026-01-01' AND created_at < '2026-01-02';

-- BAD: LIKE with leading wildcard prevents index use
SELECT * FROM products WHERE name LIKE '%ultra%';
-- FIX: Full-text search (GIN + tsvector)
SELECT * FROM products WHERE to_tsvector('english', name) @@ to_tsquery('ultra');

-- BAD: Large offset pagination (reads all skipped rows)
SELECT * FROM logs ORDER BY id LIMIT 20 OFFSET 100000;
-- FIX: Keyset pagination (cursor-based)
SELECT * FROM logs WHERE id > 100000 ORDER BY id LIMIT 20;

-- BAD: +1 query per item in nested loop (N+1)
-- FIX: Batch fetch in single query or use JOIN
```

---

## 5. ORM Anti-Patterns

### ❌ N+1 Queries
```typescript
// BAD: 1 query for users + N queries for orders (N=1000 → 1001 queries)
const users = await prisma.user.findMany();
for (const user of users) {
  const orders = await prisma.order.findMany({ where: { userId: user.id } });
}

// GOOD: One query with eager loading
const users = await prisma.user.findMany({ include: { orders: true } });
```

### ❌ Implicit Transactions Across Remote Calls
```typescript
// BAD: Transaction holds connection open during HTTP/queue calls
await prisma.$transaction(async (tx) => {
  await tx.order.update(...);
  await paymentGateway.charge(...);  // HTTP call — connection held for seconds!
  await tx.inventory.update(...);
});
// FIX: Do payment outside transaction, retry pattern inside
```

### ❌ Loading Entire Tables
```typescript
// BAD: `findMany()` with no filter → loads 10M rows to memory
const allOrders = await prisma.order.findMany();
const recent = allOrders.filter(o => o.createdAt > weekAgo);  // memory OOM in prod

// GOOD: Filter at DB level
const recentOrders = await prisma.order.findMany({
  where: { createdAt: { gte: weekAgo } }
});
```

### ❌ Missing Connection Pool Limits
```typescript
// BAD: Default pool of 10 connections; 50 concurrent requests queue up
const prisma = new PrismaClient();

// GOOD: Tune pool to match workload
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL + '&connection_limit=25&pool_timeout=10'
    }
  }
});
```

---

## 6. Sharding & Partitioning

### 6.1 Table Partitioning (PostgreSQL)
```sql
-- Partition by range (recommended for time-series)
CREATE TABLE events (
    id UUID,
    created_at TIMESTAMPTZ,
    event_type TEXT,
    payload JSONB
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2026_q1 PARTITION OF events
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE events_2026_q2 PARTITION OF events
    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');

-- Auto-detach old partitions
CREATE EVENT TRIGGER detach_old_partitions
    ...  -- See runbook for scheduled job
```

### 6.2 Horizontal Sharding Strategy
```
Shard Key Selection Criteria:
  1. High cardinality (distributes evenly)
  2. Business-affinity (minimizes cross-shard queries)
  3. Immutable (never changes after creation)

Good shard keys: user_id, tenant_id, org_id
Bad shard keys: created_at (hot spot), status (skewed), country (skewed)

Strategies:
  - Hash-based:    shard = hash(shard_key) % N
  - Range-based:   shard A: user_id 0000-3FFF, B: 4000-7FFF, C: 8000-BFFF, D: C000-FFFF
  - Directory:     lookup table: user_id → shard mapping (flexible but extra query)
```

### 6.3 Shard Rebalancing (Live Migration)
```
1. Add new shard (N+1)
2. Write to both old and new shard (dual-write)
3. Backfill old data to new shard (async)
4. Verify consistency
5. Switch reads to new shard
6. Remove old shard

Total time:   Hours to days depending on data volume
Risk:         Inconsistency if dual-write misses a path
Safest:       Maintenance window + full sync
```

---

## 7. Replication & High Availability

### 7.1 PostgreSQL Replication Setup
```yaml
# Streaming replication (async)
primary:
  wal_level: replica
  max_wal_senders: 5
  wal_keep_size: 1GB

replica:
  primary_conninfo: 'host=primary port=5432 user=replicator'
  hot_standby: on
```

### 7.2 Failover Config (Patroni + etcd)
```yaml
# patroni.yml
scope: mydb
namespace: /service/
name: pg-primary

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.0.1:8008

etcd:
  host: etcd-cluster:2379

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.0.1:5432
  data_dir: /data/postgresql
  parameters:
    wal_level: replica
    hot_standby: "on"
    max_wal_senders: 5

  # Automatic failover
  create_replica_methods:
    - basebackup
  pg_hba:
    - host replication replicator 10.0.0.0/8 md5
```

### 7.3 HA Architecture
```
App ─→ PgBouncer/Pgpool-II ─→ Primary (write) ──────────→ Replica 1 (read)
                                  │ sync/async            └→ Replica 2 (read)
                                  └── WAL sender
                        Patroni (auto-failover)
                        etcd/ZooKeeper (consensus)

Failover time targets:
  - Auto-detection:  < 10s
  - Promote replica: < 5s
  - DNS/connection update: < 30s
  - Total RTO:       < 60s
  - RPO:             0 (sync replication) or < 1s (async)
```

---

## 8. Migration Strategies (Zero-Downtime)

### 8.1 Migration Types & Lock Impact

| Migration Type | Lock | Safe for Prod? |
|----------------|------|----------------|
| `CREATE TABLE` | None | ✅ Yes |
| `ADD COLUMN ... DEFAULT NULL` | None (PG) | ✅ Yes |
| `ADD COLUMN ... DEFAULT <value>` | Row-level lock (PG 11+ — rewrite) | ⚠️ Check DB version |
| `CREATE INDEX` | Read lock | Use `CONCURRENTLY` |
| `DROP COLUMN` | None (mark as dropped) | ✅ Yes (but vacuum needed) |
| `ALTER COLUMN TYPE` | Full table lock | 🚫 Use multi-step approach |
| `RENAME COLUMN` | AccessExclusive | 🚫 Use column addition + drop |

### 8.2 Zero-Downtime Schema Change Workflow
```sql
-- Step 1: Add new column (nullable)
ALTER TABLE orders ADD COLUMN status_v2 TEXT;

-- Step 2: Dual-write — write to both old and new columns (app change)
-- (deploy code that writes to both columns)

-- Step 3: Backfill old data
UPDATE orders SET status_v2 = status WHERE status_v2 IS NULL;
-- (batch in transactions of 1000 rows at a time)

-- Step 4: Switch reads to new column (app change)
-- (deploy code that reads from new column)

-- Step 5: Drop old column (in low-traffic window)
ALTER TABLE orders DROP COLUMN status;
ALTER TABLE orders RENAME COLUMN status_v2 TO status;
```

### 8.3 Tooling
```
For PostgreSQL: gh-ost (GitHub Online Schema Transformation)
  - No triggers (unlike pt-online-schema-change)
  - Works via binary log replication
  - Can be throttled by replica lag

Usage:
  gh-ost \
    --host=localhost \
    --database=myapp \
    --table=orders \
    --alter="ADD COLUMN priority INT DEFAULT 0" \
    --execute
```

### 8.4 Migration Checklist
```
□ Migration has rollback plan (reverse migration script)
□ Migration tested on staging with production-sized data
□ Migration runs inside a transaction (one unit: success or full rollback)
□ Migration is idempotent (safe to re-run)
□ Large migrations use batch processing (1000 rows per batch, sleep between)
□ Migration duration measured — does it fit in maintenance window?
□ Lock monitoring on all affected tables during migration
□ Replica lag monitored during data migration
```

---

## 9. Distributed ID Generation

### 9.1 ID Schemes Comparison
| Scheme | Sortable | Unique | Size | Best For |
|--------|----------|--------|------|----------|
| `UUID v4` | ❌ | ✅ | 36 chars | Primary key (any DB) |
| `UUID v7` | ✅ (ms) | ✅ | 36 chars | Primary key, sort by time |
| `ULID` | ✅ (ms) | ✅ | 26 chars | Human-readable, sortable |
| `Snowflake` | ✅ (ms) | ✅ (node ID) | 19 chars (int64) | Distributed systems |
| `KSUID` | ✅ (s) | ✅ | 27 chars | K8s-native, base62 |
| `NanoID` | ❌ | ✅ | 21 chars | Short URLs, tokens |
| `Auto-increment` | ✅ | ❌ (per table) | 4-8 bytes | Internal IDs, never exposed |

### 9.2 Snowflake Variant (Go example)
```go
// 63-bit ID: [1-bit sign][41-bit timestamp][10-bit worker][12-bit sequence]
// Good for ~69 years, 4096 IDs/ms per worker, 1024 workers
func NewSnowflake(nodeID int64) int64 {
    const (
        epoch     = 1700000000000  // Custom epoch
        nodeBits  = 10
        seqBits   = 12
        nodeMax   = -1 ^ (-1 << nodeBits)
        seqMax    = -1 ^ (-1 << seqBits)
        nodeShift = seqBits
        timeShift = nodeBits + seqBits
    )
    // ... (mutex-protected, sequence rolls over to next ms)
}
```

---

## 10. Production Runbooks

### 10.1 High Connection Count
```
Symptom:  App reports "too many connections"
          PostgreSQL max_connections reached

Steps:
  1. Check current connections: 
     SELECT count(*), state, usename FROM pg_stat_activity GROUP BY state, usename;
  2. Identify idle-in-transaction: 
     SELECT pid, query, state, now() - query_start AS duration 
     FROM pg_stat_activity WHERE state = 'idle in transaction';
  3. Kill idle connections: 
     SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
     WHERE state = 'idle' AND pid <> pg_backend_pid();
  4. Check connection pool (PGBouncer): 
     SHOW POOLS;  -- look for cl_waiting > 0
  5. Tune pool: max client_conn, default_pool_size
```

### 10.2 Replication Lag
```
Steps:
  1. Check lag: SELECT * FROM pg_stat_replication;
     Desired: write_lag < 10ms, replay_lag < 10ms
  2. Is the replica WAITing for WAL? 
     ALERT: replay_lag > 10s OR flush_lag > 10s
  3. Check disk I/O on replica: iostat -x 1
  4. If replica is too slow:
     a. Increase shared_buffers on replica
     b. Reduce wal_keep_size to force replica to catch up
     c. Worst case: rebuild replica from backup
  5. If failover needed: patronictl switchover
```

### 10.3 Slow Query Detection
```sql
-- Find queries running > 5 seconds
SELECT pid, now() - pg_stat_activity.query_start AS duration,
       query, state, wait_event, wait_event_type
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - pg_stat_activity.query_start > interval '5 seconds'
ORDER BY duration DESC;

-- Kill offender (use with extreme caution in prod)
SELECT pg_terminate_backend(pid);
```

### 10.4 Maintenance Checklist
```
Daily:
  □ Check slow query log (pg_stat_statements)
  □ Check table bloat (pgstattuple)
  □ Monitor replication lag

Weekly:
  □ Check unused indexes (idx_scan = 0)
  □ VACUUM ANALYZE for tables with > 20% dead tuples
  □ Review autovacuum logs

Monthly:
  □ REINDEX CONCURRENTLY for heavily updated tables
  □ Review and archive old partitions
  □ Review connection pool settings for workload changes
```

### 10.5 Backup & Restore Verification
```bash
# PostgreSQL backup (pg_dump)
pg_dump -h localhost -U app -d myapp \
  --format=custom --compress=9 \
  --file=/backup/myapp_$(date +%Y%m%d).dump

# WAL archiving (point-in-time recovery)
archive_mode = on
archive_command = 'cp %p /archive/%f'

# Restore test (monthly)
pg_restore -d test_restore /backup/latest.dump
# Verify row count matches
psql -d myapp -c "SELECT count(*) FROM orders" -- production count
psql -d test_restore -c "SELECT count(*) FROM orders" -- restore count
```
