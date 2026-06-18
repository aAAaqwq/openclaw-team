# Distributed Systems

> Level: Advanced | File: `distributed-systems.md`
> 
> Engineering practices for building, debugging, and operating distributed systems —
> from consensus algorithms and consistency models to failure detection and observability.

---

## Table of Contents
1. [Foundations: CAP, FLP, PACELC](#1-foundations-cap-flp-pacelc)
2. [Consensus Algorithms in Practice](#2-consensus-algorithms-in-practice)
3. [Clock, Time, and Ordering](#3-clock-time-and-ordering)
4. [Failure Detection](#4-failure-detection)
5. [Distributed Consistency Models](#5-distributed-consistency-models)
6. [Distributed Locking & Leader Election](#6-distributed-locking--leader-election)
7. [Distributed Storage Patterns](#7-distributed-storage-patterns)
8. [The Google Legacy: GFS, MapReduce, BigTable, Spanner](#8-the-google-legacy-gfs-mapreduce-bigtable-spanner)
9. [Distributed System Testing](#9-distributed-system-testing)
10. [Observability for Distributed Systems](#10-observability-for-distributed-systems)

---

## 1. Foundations: CAP, FLP, PACELC

### 1.1 CAP Theorem (Brewer's Conjecture)
> A distributed data store can provide at most two of three guarantees:
> **C**onsistency, **A**vailability, **P**artition tolerance.

```
CP (Consistency + Partition tolerance):
  - When partition occurs: block writes until consistency is restored
  - Example: ZooKeeper, etcd, HBase, MongoDB (with write concern: majority)
  - Behavior: reads are consistent, but system rejects writes during partition
  - In practice: choose CP when you cannot serve stale data (configuration, locks)

AP (Availability + Partition tolerance):
  - When partition occurs: accept writes on both sides, resolve conflicts later
  - Example: Cassandra, DynamoDB, CouchDB, Riak
  - Behavior: always writable, but reads may be stale (eventual consistency)
  - In practice: choose AP when availability > strong consistency (feeds, profiles)

CA (Consistency + Availability):
  - Cannot handle partitions — if partition occurs, CP or AP behavior emerges
  - Single-node databases effectively, or consensus-based with no partitions
  - Reality: in a distributed system, partitions WILL happen → CA is a pipe dream
```

### 1.2 PACELC Extension
> If a partition (P) occurs, trade off availability (A) vs consistency (C). 
> Else (E), trade off latency (L) vs consistency (C).

```
Illustration:
                Partition? ──Yes──► A vs C (same as CAP)
                    │
                   No
                    │
                    ▼
              Latency vs Consistency

Examples:
  - DynamoDB:              PA/EL (prefers A when partitioned, low latency when not)
  - Spanner:               PC/EC (always chooses consistency, higher latency)
  - Cassandra (quorum):    PA/EC (available during partition, consistent when not)
  - MongoDB (primary):     PA/EL (available, eventually consistent by default)
```

### 1.3 FLP Impossibility
> In an asynchronous network, no consensus algorithm can guarantee progress 
> with even a single faulty process.

```
Practical implications:
  - "Asynchronous" = network messages can be arbitrarily delayed
  - "Faulty" = process can crash at any time
  - Therefore: ALL consensus algorithms rely on timeouts (synchronous assumptions)
  - Raft, Paxos, Zab all use leader election timeouts
  - If timeouts are too short → unnecessary leader changes
  - If too long → slow failure detection

Mitigation: Randomized timeouts (Raft-style)
  - Each node picks a random timeout between T and 2T
  - Prevents multiple simultaneous leader elections
```

---

## 2. Consensus Algorithms in Practice

### 2.1 Raft — The Understandable Consensus

```
State Machine:
  Each server has: log[] | state machine | term counter

Three states: Follower, Candidate, Leader

Leader Election:
  1. Followers start with random timeouts (150-300ms typical)
  2. Timeout → Candidate → request votes from other servers
  3. Majority votes → becomes Leader
  4. Leader sends heartbeats (AppendEntries with no entries) to maintain authority

Log Replication:
  1. Client sends command to Leader
  2. Leader appends to local log
  3. Leader sends AppendEntries RPC to Followers
  4. Majority acknowledge → entry is committed
  5. Leader applies to state machine → responds to client

Safety:
  - Election Safety: at most one leader per term
  - Log Matching: if two logs have same (term, index), they are identical
  - Leader Completeness: committed entries are present in all future leaders
  - State Machine Safety: if a server applies entry at a given index, 
    no other server applies a different entry at the same index

Common Raft pitfalls:
  - Pre-Vote: prevents a disconnected node from triggering unnecessary elections
  - CheckQuorum: leader steps down if it can't reach majority
  - Leadership Transfer: graceful leader transfer for maintenance
```

### 2.2 ZooKeeper Atomic Broadcast (Zab)

```
Similar to Raft, but different enough to matter:

Differences from Raft:
  - Uses epochs (like terms) + ZXID (transaction ID = epoch + counter)
  - Leader synchronization phase before accepting writes
  - Zab guarantees total order (all messages processed in order)
  - Dynamic membership changes are more complex

Zab Phases:
  1. Discovery: peer finds current epoch and leader
  2. Synchronization: follower catches up with leader's log
  3. Broadcast: leader accepts writes, broadcasts with quorum

When ZooKeeper vs etcd:
  - ZooKeeper: heavier (Java JVM), richer API (watches, ephemeral nodes, sequences)
  - etcd: lighter (Go), gRPC API, K8s native
  - Both: consistent key-value store, not a database
```

### 2.3 Paxos Implementations

```
Multi-Paxos (the practical variant):
  1. A stable leader is elected (avoids running full Paxos per entry)
  2. Leader assigns log positions and sends Accept messages
  3. Followers acknowledge
  4. Leader commits when majority acknowledged

Chubby (Google's lock service): Multi-Paxos
  - Coarse-grained locks, 5 replicas
  - Used for: GFS master election, BigTable master election
  - Paxos for leader election, not for every write

Cheap Paxos:
  - Acceptors = 2F+1 machines (standard)
  - Learners/leaders can be much cheaper (throwaway VMs)
  - Uses: availability with lower cost (leader runs on cheap instance)

Fast Paxos:
  - Clients propose directly, skipping the leader
  - Higher latency (conflict resolution) but higher throughput
  - Requires: all acceptors to be non-faulty
```

### 2.4 Consensus Algorithm Decision Matrix

| Algorithm | Throughput | Latency | Complexity | Best For |
|-----------|-----------|---------|------------|----------|
| **Raft** | Medium (~10k/s) | Low (5-15ms) | Low | General consensus (etcd, Consul, TiKV) |
| **Multi-Paxos** | Medium (~10k/s) | Low (5-20ms) | High | When Raft isn't compatible |
| **Zab** | Medium (~10k/s) | Low (5-15ms) | Medium | ZooKeeper-based systems |
| **EPaxos** | High (~100k/s) | Low (5-10ms) | Very High | Multi-region, geo-distributed |
| **PBFT** | Low (~1k/s) | High (100ms+) | Extreme | Permissioned blockchains |

---

## 3. Clock, Time, and Ordering

### 3.1 Clock Types

```
Physical clocks (wall clocks):
  - NTP synchronized, but skew always exists (1-50ms typical, 100ms+ worst case)
  - Drift: hardware clocks drift 1-5 seconds per day
  - Failure: VM pause, leap seconds, NTP leap smearing
  
  Example problem:
    Event A happens at 10:00:00.100 (server 1)
    Event B happens at 10:00:00.050 (server 2) — due to clock skew, B appears earlier
    But A actually happened first (wait, did it?)

Logical clocks (Lamport / Vector):
  - Lamport clock: simple counter, tracks happens-before
    A → B: L(A) < L(B), but L(A) < L(B) does NOT imply A → B
  - Vector clock: one counter per node, tracks causality
    A → B iff all elements of V(A) ≤ V(B) and at least one is strictly less
  - Used in: Dynamo, Cassandra, Riak for conflict detection

Hybrid clocks (HLC, TrueTime):
  - HLC: physical + logical component — bounds error and preserves causality
  - TrueTime (Spanner): GPS + atomic clocks, exposes time uncertainty interval
    TT.before() = TT.now().earliest
    TT.after() = TT.now().latest + clock error bound
```

### 3.2 Timestamp Ordering in Practice

```
Problem: "happened before" is expensive to compute in large systems

Solutions by scenario:
  - Event ordering within a partition: use the partition offset (Kafka)
  - Event ordering for a single entity: use the entity's version counter
  - Event ordering across partitions: don't need it (choose partition key carefully)
  - Event ordering across systems: use HLC or TrueTime (Spanner)

Practical rule: 
  If you need global ordering, use a single leader (bottleneck).
  If you don't, use entities/partitions as ordering scopes.
```

---

## 4. Failure Detection

### 4.1 Phi Accrual Failure Detector (Cassandra-style)

```
Instead of "Is the node dead?" (binary), measure a suspicion level.

T = time since last heartbeat was received
Phi(T) = -log10( P_later(T) ) where P_later is the probability of
         hearing nothing for T time units, given recent heartbeat history

Interpretation:
  Phi = 1   → 10% chance the node is dead (very suspicious)
  Phi = 2   → 1% chance
  Phi = 8   → 0.000001% chance (do NOT ignore)

Advantages:
  - Adapts to network conditions (TCP-friendly)
  - Configurable suspicion threshold (not binary)
  - Fewer false positives than fixed timeout

Used by: Cassandra (org.apache.cassandra.gms.FailureDetector), Akka
```

### 4.2 Gossip Protocol

```
Periodic membership propagation:
  Each node, every T seconds:
    1. Pick a random node (or K nodes) to gossip with
    2. Exchange membership information (heartbeat, IP, port, state)
    3. Update local membership table

Properties:
  - Convergence: O(log N) rounds for information to reach all nodes
  - Fault-tolerant: no single point of failure
  - Decentralized: no master node for membership
  - But: eventual consistency of membership list

Used by: Cassandra (gossip), Consul (gossip + Raft for consistency), SWIM
```

### 4.3 SWIM Protocol (Scalable Weakly-consistent Infection-style)

```
Improvement on basic gossip:
  - Ping + indirect ping (A asks B to ping C to check if C is alive)
  - Ack + Nack for failure confirmation
  - Suspicion mechanism before declaring death

Components:
  - Dissemination: gossip to spread membership
  - Failure detection: direct + indirect pings
  - Suspicion: "suspect" before "alive" → "confirmed dead"
```

---

## 5. Distributed Consistency Models

### 5.1 Linearizability (Strongest)

```
Every operation appears to take effect atomically at some point between its
invocation and its response.

Example:
  Write(x=1) returns → all subsequent reads must return 1
  Two writes: if write A returns before write B starts, B's value is the final

Achieving linearizability:
  - Single-leader replication (fast reads from leader)
  - Quorum reads (R + W > N)
  - Consensus-based reads (RAFT leader read)

Cost:
  - Throughput: limited by leader
  - Latency: quorum waits for slowest node
  - Availability: minority partition cannot serve writes
```

### 5.2 Sequential Consistency

```
Operations from each process execute in the order the process issued them.
Operations from different processes may interleave, but all processes see the same interleaving.

Difference from linearizability:
  - Sequential: operations are not constrained to happen between invocation/response
  - Linearizability: operations take effect at a real-time point

Cheaper than linearizability but rarely used directly in production systems.
```

### 5.3 Causal Consistency

```
Causally related operations are seen in the same order by all processes.
Concurrent operations can be seen in different orders.

Achieving:
  - Vector clocks to track causality
  - COPS (CAUSAL Consistency in Partition-tolerant Stores) — from SOSP '11 paper
  
Best for: Multi-region systems where causal ordering matters but strong consistency is
         too expensive (social feeds, collaborative editing)
```

### 5.4 Eventual Consistency

```
Given enough time without new updates, all replicas converge to the same value.
No guarantee about when convergence happens.

Types:
  - Read-your-writes: user always sees their own writes
  - Monotonic read: reads from same replica, don't go back in time
  - Monotonic write: writes applied in order per user
  - Write-follows-read: if read X then write Y, Y is causally after X

Implementing read-your-writes:
  - Route reads for recently modified data to the leader
  - Client caches version timestamps per partition
```

---

## 6. Distributed Locking & Leader Election

### 6.1 Distributed Locking (etcd/Redis/ZooKeeper)

```bash
# etcd — distributed lock
etcdctl lock mylock --ttl 10
# Critical section...
# Lock auto-releases on command exit or TTL expiry
```

```typescript
// Node.js — etcd lock
import { Lock } from 'etcd3';

const lock = new Lock(etcdClient, '/locks/order-processor');
await lock.acquire();
try {
  // Critical section
} finally {
  await lock.release();
}
```

### 6.2 Redlock (Redis-based) — Controversial

```
Martin Kleppmann vs Redis:
  - Redlock is NOT safe with arbitrary network delays
  - Do NOT use for operations that need correctness (payment, inventory)
  - Acceptable for: rate limiting, idempotency keys (stateless, no harm if lost)

Better alternative: use etcd or ZooKeeper for locks that matter
```

### 6.3 Leader Election Patterns

```yaml
Pattern 1: Lease-based (etcd)
  - Candidate creates lease with TTL
  - Refreshes lease periodically
  - On failure: lease expires, new leader acquires

Pattern 2: Ephemeral Node (ZooKeeper)
  - Candidates try to create /election/leader (ephemeral)
  - Success → leader. Failure → watch, wait for leader to disappear
  - Leader dies → ephemeral node dies → next candidate creates

Pattern 3: Bully Algorithm
  - Highest ID node is leader
  - New node with higher ID announces itself
  - Simple but doesn't handle network partitions well
```

---

## 7. Distributed Storage Patterns

### 7.1 Consistent Hashing

```
Standard hashing: key % N → when N changes, ALL keys remap (terrible for caches)

Consistent hashing:
  1. Hash servers and keys to a ring (0 to 2^32)
  2. Key assigned to next server clockwise
  3. Adding/removing server: only keys on neighbors move

Virtual nodes:
  - Each physical server maps to 100-1000 virtual nodes on the ring
  - Better load distribution
  - Easier to handle heterogeneous hardware (more VNs for bigger servers)

Used in: Cassandra, DynamoDB, RLedger, discuz!
```

### 7.2 Quorum-Based Reads

```
N = replication factor
W = minimum nodes to confirm write
R = minimum nodes to read

Tunable consistency:
  - Strong: W + R > N  
    Write must be acknowledged by more than half
    Read must include at least one node with latest write

  - Eventual: W = 1, R = 1 (fastest, weakest)
  - Default DynamoDB: N=3, W=2, R=2

Hinted handoff:
  When a replica is down, another node accepts the write
  Forwards to correct replica when it comes back

Read repair:
  Background process that compares replicas and fixes inconsistencies
```

### 7.3 CRDTs (Conflict-Free Replicated Data Types)

```
Automatic conflict resolution without locks or consensus:

G-Counter (Grow-only Counter):
  Each node has its own count. Total = sum of all counts.
  No decrements. Merge = element-wise max.

PN-Counter:
  G-counter for increments + G-counter for decrements. Total = inc - dec.

OR-Set (Observed-Remove Set):
  Add: element with unique tag. Remove: add tombstone for all observed tags.
  Merged: (all adds) - (all tombstones not in adds)

G-Set (Grow-only Set):
  Add only. Merged = Union. Never remove.

LWW-Register (Last-Writer-Wins):
  Value + timestamp. Merged = highest timestamp wins.

Used by: Riak (CRDT support), Redis (with some CRDT structures),
         Figma (collaborative editing), Google Docs (operational transformation, similar)
```

---

## 8. The Google Legacy: GFS, MapReduce, BigTable, Spanner

### 8.1 GFS (Google File System) — 2003

```
Design: single master + chunk servers
  - Files divided into 64MB chunks
  - Each chunk replicated 3x
  - Master holds metadata (small, fits in RAM)
  - Chunk servers store data and serve reads/writes directly

Key innovations:
  - Assumed component failures were normal (build for failures)
  - Optimized for large streaming reads (not random access)
  - Relaxed consistency model (atomic append, not strong consistency on mutations)
  - Control path separate from data path (master just coordinates, clients talk to chunkservers)

Legacy: Hadoop HDFS is the open-source implementation
         Object stores (S3, GCS) have largely replaced GFS-style systems
```

### 8.2 MapReduce — 2004

```
Programming model:
  Map: (k1, v1) → list(k2, v2)
  Reduce: (k2, list(v2)) → list(v3)

Execution:
  1. Input split into M pieces
  2. Master assigns Map tasks to workers
  3. Map outputs intermediate (k2, v2) — stored locally
  4. Shuffle: partition intermediate keys to Reduce workers
  5. Reduce: sort, aggregate, write output

Why it was revolutionary:
  - Hid all distributed systems complexity from programmers
  - Fault tolerance: re-execute failed tasks
  - Locality: move computation to data (not data to compute)

Modern evolution:
  - MapReduce → Spark (in-memory, DAG) → Flink (streaming)
  - SQL on top: Hive, Presto, BigQuery
  - The programming model lives on in DataFrame APIs
```

### 8.3 BigTable — 2006

```
Distributed key-value store:
  Row key → Column family → Column qualifier → Timestamp → Value

Architecture:
  - Table splits into tablets (~100-200MB each)
  - Tablet servers manage tablets
  - Chubby (Paxos-based lock service) for coordination
  - GFS for storage
  - SSTable file format on top of GFS

Capabilities:
  - Random read/write access (not just batch like GFS)
  - Timestamp-based versioning
  - Column families for compression and locality

Modern equivalents:
  - HBase (open source)
  - Cassandra (Dynamo-inspired, not BigTable)
  - BigQuery (evolved from Dremel, not BigTable)
```

### 8.4 Spanner — 2012 (and beyond)

```
Globally-distributed SQL database:
  - TrueTime (GPS + atomic clocks) for external consistency
  - Synchronous replication across zones
  - SQL query interface (wider tables)
  - Automatic sharding + rebalancing

TrueTime:
  TT.now() returns an interval [earliest, latest]
  Commit waits for TT.after(commit_timestamp) → guarantees linearizability across continents

How AWS competes:
  - Aurora: single-region, shared storage
  - DynamoDB: multi-region with global tables (eventual consistency, but fast)
  - No cloud provider matches Spanner's global strong consistency

Open source alternatives:
  - CockroachDB (HLC-based, hybrid clock, not TrueTime)
  - TiDB (Raft-based, not global)
  - YugaByte (not as mature for global)
```

---

## 9. Distributed System Testing

### 9.1 Testing Levels

```
Unit: test individual consensus logic
  - Mock network, test leader election logic
  - Raft: test log replication with fake peers

Integration: test with real network
  - Start 3-5 nodes, verify leader election
  - Kill leader, verify new leader elected with correct log

Network simulation: controlled chaos
  - Jepsen: injected network partitions, clock drift, process crashes
  - Chaos Mesh: inject failures into K8s clusters

Jepsen tests (requires Clojure):
  - Helper library for building distributed system test workloads
  - Can test: linearizability checker, queue, register, set
  - Failures: network partition, process pause, clock skew, packet drop
```

### 9.2 Model Checking (TLA+)

```
Formal specification for distributed algorithms:
  - Lesie Lamport created TLA+ for specifying and verifying protocols
  - "If you haven't spec'd your algorithm in TLA+, you don't understand it"

What TLA+ catches:
  - Liveness: the system eventually makes progress (e.g., leader is eventually elected)
  - Safety: nothing bad ever happens (e.g., two leaders are never elected)
  - State space explosion: catch bugs that are impossible to find in testing

Practical use:
  - Write TLA+ spec → model check with TLC
  - Find deadlock, livelock, or safety violations
  - Implement in your language of choice

Simple example:
  VARIABLES leader, term
  Init == leader = NONE ∧ term = 0
  Next == ∃ t ∈ Terms, s ∈ Servers:
    leader' = s ∧ term' = t ∧ t > term
  Spec == Init ∧ □[Next]_<<leader, term>>
```

### 9.3 Testing in Production

```
Chaos engineering:
  - Inject failures in staging → predictable behavior
  - Inject failures in production → verify resilience
  
  Tools: Chaos Mesh, Litmus, Gremlin, AWS FIS

Verification strategies:
  - Fault injection on one instance: kill one pod
  - Network latency: add artificial delay between services
  - Resource exhaustion: fill disk, saturate CPU

Gray failure detection:
  - Partial failures (disk is slow, but not dead)
  - Packet loss on one link
  - Bit flips in memory
  - Hardest class of failures to detect
```

---

## 10. Observability for Distributed Systems

### 10.1 Metrics That Matter
```
System (per node):
  CPU, Memory, Network I/O, Disk I/O, Disk usage, File descriptors

Protocol-level:
  Consensus: leader changes, term changes, voting metrics
  Replication: log position, commit index, follower lag
  Quorum: time to reach consensus, failed consensus rounds

Application-level:
  Request rate, error rate, latency distribution
  Cache hit ratio, database query distribution
  Queue depth, consumer lag, dead-letter count
```

### 10.2 Tracing in Distributed Systems

```
Trace = one request's journey through all services
Span = one operation within a trace

Must capture:
  - Service name, operation name, duration
  - Span kind (client, server, internal, producer, consumer)
  - Status (OK, ERROR) with error details
  - Tags: node ID, partition/replica role, consensus term

Critical distributed systems scenarios:
  - "Why did the leader election take 30 seconds?"
    → Trace the election from start to completion
    → Check: timeout duration, RPC latency, vote computation time
  
  - "Why is replication lag spiking?"
    → Check: network latency, disk I/O on follower, compaction running
    → Metrics: follower's WAL write latency, index apply latency
```

### 10.3 Distributed System Debugging Checklist
```
□ Verify time synchronization (NTP) — #1 cause of weird distributed bugs
□ Check consensus term (stale read from old leader?)
□ Check quorum state (minority partition?)
□ Check disk latency on replicas (compaction causing spikes?)
□ Check network latency between nodes (cross-AZ latency?)
□ Check connection pool exhaustion
□ Check for clock drift > 100ms
□ Check for application-level backpressure (slow consumers)
□ Check for GC pauses (JVM) / stop-the-world events (Go 1.x GC with large heap)
□ Check for file descriptor exhaustion (too many open connections)
```

### 10.4 Production Checklist
```
□ NTP configured on all nodes, clock skew < 50ms (monitored)
□ Consensus timeout tuned for network latency (not too aggressive)
□ Quorum (W+R > N) configured for consistency requirements
□ Failure detection timeout configured per workload
□ Cross-region replication uses async (at most txn consistency when possible)
□ Leader election timeout is 5x RTT (prevents flapping)
□ Replication lag is monitored and alerted
□ Partition count is logged and monitored
□ Dead node detection time < desired failover time
□ Jepsen/Chaos testing run before deploying consensus changes
```
