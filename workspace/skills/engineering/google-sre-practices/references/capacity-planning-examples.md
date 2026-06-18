# Capacity Planning — Practical Examples

## Example 1: API Service

```
Given:
  - 5M DAU
  - Each user makes 20 API calls/day
  - Response time target: p99 < 200ms
  - 1 request ≈ 50KB bandwidth
  - Avg request processing: 100ms

Compute:
  Total daily requests: 5M × 20 = 100M requests/day
  QPS average: 100M / 86400 ≈ 1,157 QPS
  
  Peak QPS (2x daily peak): 2,314 QPS
  Peak QPS (3x holiday factor): 3,471 QPS  ← design target

Compute needed instances:
  Each instance handles 100 req/sec (safe estimate)
  Baseline: 3,471 / 100 = ~35 instances
  Headroom (2x for failover): 70 instances

Memory:
  Each instance: 512MB heap + 256MB overhead = 768MB
  Total: 70 × 768MB ≈ 54GB

CPU:
  If 1 CPU core per instance: 70 cores
  Over-provision by 30%: 90 cores
```

## Example 2: Database

```
Given:
  - 1M new records/day
  - Each record: ~500 bytes
  - Retention: 90 days online, 1 year cold
  - Read:Write ratio: 10:1
  
Storage:
  Active data: 1M × 500B × 90 = 45GB (hot storage, SSD)
  Cold data: 1M × 500B × 365 = 183GB (cold storage, HDD)
  
  With indexes (2x data size): 90GB hot → round up to 100GB
  With WAL/logs (1.5x): 150GB hot storage

Compute:
  Write QPS: 1M / 86400 ≈ 12 writes/sec (peak: 60 writes/sec)
  Read QPS: 12 × 10 = 120 reads/sec (peak: 600 reads/sec)
  
  Single Postgres instance handles 2000+ QPS for simple queries
  → Single DB is fine. But add read replica for heavy reporting.

Memory:
  Working set: records accessed in last hour
  If 10% of hot data is "hot": 10GB → needs 32GB RAM for Postgres
  Shared buffers: 25% of RAM → 8GB

Disk IOPS:
  Estimating 16KB per read/write operation:
  Peak IOPS: (600 reads + 60 writes) × 64KB / 16KB ≈ 2,640 IOPS
  Any modern SSD can handle this (10K+ IOPS)
  → Not a bottleneck
```

## Example 3: Event Streaming (Kafka)

```
Given:
  - 500M events/day
  - Each event: ~1KB
  - 3 topics, 3 partitions each
  - Retention: 7 days

Throughput:
  Events/sec: 500M / 86400 ≈ 5,787 events/sec
  Throughput: 5,787 × 1KB ≈ 5.7 MB/s
  Peak (3x): 17 MB/s

Storage:
  5.7 MB/s × 86400 × 7 = ~3.4 TB total
  With replication factor 3: ~10 TB cluster storage
  Per broker (5 brokers): ~2 TB each

Partitions:
  Throughput per partition: ~2,000 events/sec max (safe)
  Event key distribution = 3 topics × 3 partitions = 9 partitions
  Max: 9 × 2,000 = 18,000 events/sec → ✅ enough

Broker sizing:
  5 brokers × 2TB each → 10TB raw
  5 brokers × 4 vCPU → 20 vCPU cluster
  Memory: 5 brokers × 16GB → 80GB
```

## Quick Capacity Estimation Cheat Sheet

```
Cloud Resources:
  CPU: 1 vCPU ≈ handles ~100 simple HTTP req/s
  Memory: 1GB RAM ≈ handles ~200 concurrent connections
  Disk: 1TB HDD ≈ $40/month (cloud), $15/month (bare metal)
  Network: 1Gbps ≈ ~12M HTTP requests/hour (5KB response)

Database:
  Postgres single node: ~10K simple queries/sec
  Redis single node: ~100K ops/sec
  DynamoDB equivalent: ~1000 WCU per shard (1KB items)
  Elasticsearch: ~5K doc writes/sec per node (with indexing)

Traffic Multiples:
  Daily peak: 2-3x average
  Holiday peak: 3-5x average  
  Campaign peak: 5-10x average
  Viral peak: 10-50x average (have autoscaling ready!)
```
