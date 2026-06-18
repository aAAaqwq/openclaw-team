---
name: architecture-decision-record
description: >
  Architecture Decision Records (ADR) — a lightweight method for capturing
  important architectural decisions with context, trade-offs, and rationale.
  Based on Michael Nygard's ADR pattern and Google/Meta/ByteDance's design
  documentation culture.

  USE WHEN: deciding between technology choices, designing new architecture,
  changing existing architecture, documenting why a decision was made,
  onboarding new team members, or preserving design context for future
  maintainers. Triggered by terms like "tech choice", "architecture decision",
  "why did we choose", "design rationale", "ADR", or "architectural decision record".
---

# Architecture Decision Record (ADR)

> **Source**: Michael Nygard's ADR pattern + Google/Meta/ByteDance design doc culture
> **Core Philosophy**: Every architectural decision is a bet. ADRs record the bet,
> the rationale, and the expected payout so future teams know why you bet what you bet.

## Why ADRs Matter

```
  Without ADRs:
  ❌ "Why did we use MongoDB instead of Postgres?" — nobody knows
  ❌ New hires repeat old debates endlessly
  ❌ Trade-offs are forgotten — only the outcome is visible
  ❌ Bad decisions can't be revisited because we don't know why they were made

  With ADRs:
  ✅ Every decision has context — future developers understand the "why"
  ✅ Decision quality improves — writing it down forces clearer thinking
  ✅ New hires can catch up by reading ADRs, not hunting through Slack history
  ✅ Revisiting decisions is easier — "has the context changed?"
```

## ADR Lifecycle

```
  Proposed → Accepted → Superseded → Deprecated

  Proposed:   Decision is suggested but not yet agreed
  Accepted:   Team agrees and implementation begins
  Superseded: A newer ADR replaces this decision (links to it)
  Deprecated: Decision is no longer relevant (system changed)
```

---

## ADR Template

```markdown
# ADR-NNN: [Title — short, descriptive]

- **Status**: [Proposed | Accepted | Superseded | Deprecated]
- **Date**: YYYY-MM-DD
- **Author**: [Name]
- **Supersedes**: ADR-NNN (if applicable)
- **Superseded by**: ADR-NNN (if applicable)

## Context

What is the context that makes this decision necessary?

Include:
- The specific problem being solved
- Business constraints (time, cost, resources)
- Technical constraints (existing stack, team expertise)
- Any relevant background or prior art

## Decision

What are we deciding? State the decision clearly.

"We will use [Technology/Method] for [Purpose] because [Primary Reason]."

Provide a concise, unambiguous statement of what the team is committing to.

## Options Considered

### Option A: [Name] (Recommended)

**Description**: Brief explanation of the approach.

**Pros:**
- Pro 1
- Pro 2

**Cons:**
- Con 1
- Con 2

### Option B: [Name]

**Description**: Brief explanation of the approach.

**Pros:**
- Pro 1
- Pro 2

**Cons:**
- Con 1
- Con 2

### Option C: [Name] (Do nothing / Baseline)

**Description**: Keeping the current approach.

**Pros:**
- Pro 1

**Cons:**
- Con 1
- Con 2

## Trade-off Analysis

Use a clear comparison table to show the decision rationale:

| Criteria           | Option A | Option B | Option C |
|--------------------|----------|----------|----------|
| Performance        | High     | Medium   | Low      |
| Maintainability    | High     | High     | Medium   |
| Learning curve     | Medium   | Low      | None     |
| Operational cost   | Low      | High     | Medium   |
| Time to implement  | 2 weeks  | 1 week   | 0        |
| Risk               | Low      | Medium   | High     |

## Consequences

What are the implications of this decision?

**Positive:**
- Consequence 1: What becomes easier/better?
- Consequence 2: What new capabilities do we gain?

**Negative:**
- Consequence 1: What becomes harder?
- Consequence 2: What trade-offs did we accept?

**Neutral:**
- Consequence 1: What changes about how we operate?

## Validation

How will we validate this decision was correct?

- [ ] Metric to track: [e.g., p99 latency, error rate, dev velocity]
- [ ] Review date: YYYY-MM-DD (3-6 months after decision)
- [ ] Success criteria: [e.g., "p99 < 200ms", "deploy time < 10 min"]

## Related Decisions

- ADR-NNN: [Related decision title]
- ADR-MMM: [Related decision title]
```

---

## ADR Quick Template (2-minute version)

For small decisions that still need documentation:

```markdown
# ADR-NNN: [Title]

- **Status**: Accepted
- **Date**: YYYY-MM-DD

## Context
[1-2 sentences]

## Decision
Use [X] for [Y].

## Rationale
[1-2 sentences on key trade-off]

## Consequences
[What changes as a result]
```

---

## Examples

### Example 1: Full ADR

```markdown
# ADR-017: Use PostgreSQL over MongoDB for Order Service

- **Status**: Accepted
- **Date**: 2026-05-02
- **Author**: XuanYuan

## Context

The Order Service needs to store transactional order data with:
- Strong consistency (no stale reads)
- Complex relational queries (orders × items × payments)
- ACID transactions (money movement)
- No pre-defined query patterns (ad-hoc reporting)
- 1M+ orders/month, growing 10% monthly

## Decision

We will use PostgreSQL (with TimescaleDB extension) for the Order Service
because the data is inherently relational and requires ACID guarantees
that document stores cannot provide.

## Options Considered

### Option A: PostgreSQL (Recommended)

**Pros:**
- ACID compliant — critical for financial data
- Rich query language for reporting
- Mature ecosystem (ORM, migration tools, monitoring)
- TimescaleDB extension for time-series data
- JSONB for semi-structured data when needed

**Cons:**
- Vertical scaling limit (single writer)
- Schema migrations require careful planning
- Higher operational overhead vs managed alternatives

### Option B: MongoDB

**Pros:**
- Schema flexibility
- Horizontal scaling built-in
- Fast iteration cycles

**Cons:**
- No ACID across documents (vulnerable to data inconsistency)
- Joins are slow/limiting for relational data
- Reporting requires ETL to another system
- Schema-less is a liability for money-related data

### Option C: CockroachDB

**Pros:**
- ACID + horizontal scaling
- Postgres-compatible

**Cons:**
- Higher latency (distributed consensus)
- Less mature ecosystem
- Team lacks operational experience
- Overkill for current scale (< 10M orders/month)

## Trade-off Analysis

| Criteria             | PostgreSQL | MongoDB | CockroachDB |
|---------------------|------------|---------|-------------|
| ACID transactions   | ✅ Full    | ⚠️ Limited | ✅ Full    |
| Query flexibility   | ✅ High    | ⚠️ Medium | ✅ High    |
| Team experience     | ✅ High    | ⚠️ Medium | ❌ Low     |
| Horizontal scaling  | ⚠️ Manual  | ✅ Auto  | ✅ Auto    |
| Operational cost (3yr) | $30K   | $25K     | $60K       |
| Risk                | Low        | Medium   | High        |

## Consequences

**Positive:**
+ Strong data consistency for money-related operations
+ Team can leverage existing PostgreSQL expertise
+ Rich reporting capabilities without additional tooling
+ TimescaleDB covers time-series needs without another DB

**Negative:**
- Must plan for sharding when we exceed 10M orders/month (est. 18 months)
- Schema migration process needs to be robust (use Sqitch)
- Read replicas needed for reporting to avoid production impact

**Neutral:**
- Will need to use logical replication for analytics pipeline
- JSONB hybrid approach for flexible metadata

## Validation

- [x] Review PostgreSQL/CockroachDB decision in 6 months
- [ ] Track: query latency p99 < 20ms, schema migration time < 5 min
```

### Example 2: Quick ADR (small decision)

```markdown
# ADR-009: Use Biome over ESLint+Prettier

- **Status**: Accepted
- **Date**: 2025-11-15

## Context
Frontend toolchain currently uses separate tools for linting (ESLint) and
formatting (Prettier). This causes configuration drift and CI conflicts.

## Decision
Replace ESLint + Prettier with Biome for linting + formatting in web UI codebase.

## Rationale
Biome provides lint + format in a single binary (3x faster, no config conflict),
supports 95%+ of our existing rules, and eliminates two config files.

## Consequences
+ Faster CI (lint+format step drops from 45s to 12s)
+ Single config file (biome.json) instead of .eslintrc + .prettierrc
- Team needs to learn Biome's rule syntax
- Some custom ESLint plugins need to be ported
```

---

## ADR File Organization

```
docs/adr/
├── README.md              # Index of all ADRs with status table
├── ADR-001-initial-architecture.md
├── ADR-002-use-postgres-for-orders.md
├── ADR-003-use-redis-for-caching.md
├── ADR-004-supersede-003-use-memcached.md
└── ADR-005-microservices-vs-monolith.md
```

### README.md (ADR Index)

```markdown
# Architecture Decision Records

| ADR | Title | Status | Date | Author |
|-----|-------|--------|------|--------|
| 001 | Initial Architecture | Accepted | 2026-01-15 | Alice |
| 002 | Use PostgreSQL for Orders | Accepted | 2026-02-01 | Bob |
| 003 | Use Redis for Caching | Superseded | 2026-02-15 | Carol |
| 004 | Supersede 003: Use Memcached | Accepted | 2026-03-01 | Carol |
| 005 | Microservices vs Monolith | Proposed | 2026-04-01 | Alice |
```

---

## When to Write vs Not Write an ADR

```
  WRITE an ADR when:
  ✅ Choosing between two+ technologies
  ✅ Making a decision with long-term impact
  ✅ Changing an existing architectural decision
  ✅ Introducing a new pattern/paradigm to the team
  ✅ The decision has cost, risk, or dependency implications

  DON'T write an ADR when:
  ❌ Choosing a code style (that's a style guide)
  ❌ Making a trivial implementation detail
  ❌ You need a decision in 5 minutes (write it later)
  ❌ The decision is temporary and will be reversed
```

---

## ADR Review Process

```
  ┌──────────────────────────────────────────────────────────────┐
  │                                                               │
  │  ① Author drafts ADR (Proposed status)                       │
  │     ↳ Optionally shared in slack #architecture channel        │
  │                                                               │
  │  ② Team reviews (async — 48h minimum)                        │
  │     ↳ Focus on: are the options fair? Are trade-offs real?   │
  │                                                               │
  │  ③ Architecture sync (optional — if contentious)              │
  │     ↳ Discuss unresolved differences                          │
  │     ↳ Agree on final decision                                 │
  │                                                               │
  │  ④ Status → Accepted                                          │
  │     ↳ Decision is locked unless new information emerges       │
  │                                                               │
  │  ⑤ Implementation follows the ADR                             │
  │                                                               │
  │  ⑥ Review in 3-6 months                                       │
  │     ↳ Was the decision correct? Update or supersede          │
  │                                                               │
  └──────────────────────────────────────────────────────────────┘
```
