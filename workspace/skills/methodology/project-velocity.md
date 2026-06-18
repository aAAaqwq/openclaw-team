# Project Velocity & SDLC Engineering

> Level: Expert | File: `project-velocity.md`
> 
> Engineering-driven project management: from PRD to ship, milestone planning,
> bottleneck identification, parallelization strategy, and velocity optimization.

---

## Table of Contents
1. [The Engineering PM Mindset](#1-the-engineering-pm-mindset)
2. [From PRD to Ship: The Full Pipeline](#2-from-prd-to-ship-the-full-pipeline)
3. [Milestone Planning](#3-milestone-planning)
4. [Work Breakdown & Estimation](#4-work-breakdown--estimation)
5. [Parallelization Strategy](#5-parallelization-strategy)
6. [Bottleneck Identification](#6-bottleneck-identification)
7. [Velocity Metrics & Dashboards](#7-velocity-metrics--dashboards)
8. [Kanban for Engineers](#8-kanban-for-engineers)
9. [Agile Anti-Patterns](#9-agile-anti-patterns)
10. [Multi-Project Portfolio Management](#10-multi-project-portfolio-management)

---

## 1. The Engineering PM Mindset

### 1.1 Engineer ≠ PM, But...

```
The best tech leads think like PMs:
  - Not "How do I build this?"
  - But "How do we ship this efficiently?"

Mindset shifts:
  Traditional engineer:                    Engineering PM:
  "Let me write the perfect code first"    "Let me get a working prototype, then iterate"
  "Tests must be 100% coverage"            "80% coverage on critical path, ship, add tests"
  "I can do it alone"                      "I'll decompose so 3 people can work in parallel"
  "Let me think about it for 2 days"       "I'll make a decision in 30 min and iterate"
  "The architecture must be perfect"       "The architecture must be good enough to ship"
```

### 1.2 The Two Steering Wheels

```
┌─────────────────┐     ┌─────────────────┐
│  Quality        │     │  Velocity        │
│  (tests, review,│     │  (time to ship,  │
│   stability)    │     │   iteration speed)│
└────────┬────────┘     └────────┬────────┘
         │                       │
         └────── Trade-off ──────┘
               Every sprint

When to prioritize quality:
  - Payment processing, auth, data integrity
  - Public API (you can't undo a shipped API mistake)
  - Before a major demo / customer milestone

When to prioritize velocity:
  - Early prototype / MVP
  - Feature that's behind schedule
  - Experiment that might be abandoned
  - When PM says "ship date is hard, quality is soft"
```

---

## 2. From PRD to Ship: The Full Pipeline

### 2.1 The Engineering Pipeline

```
PRD → Tech Design → Sprint Planning → Implementation → Review → Staging → Production
 │        │              │                  │            │         │          │
 5%      10%            5%                50%           10%       10%        10%

Percentage of total effort per phase (typical):
  PRD alignment:    5% (but if PRD is wrong → 50% rework)
  Tech design:     10% (skipping this → 30% rework)
  Sprint planning:  5%
  Implementation:  50% (can parallelize)
  Code review:     10% (bottleneck if serial)
  Staging deploy:  10% (serverless = 2%, heavy infra = 20%)
  Production:      10% (canary, monitoring, rollback)
```

### 2.2 Phase Gating: Do NOT Skip

```markdown
Gate 1: PRD sign-off
  ✅ Acceptance criteria are testable
  ✅ "Done" is clearly defined
  ✅ Dependencies are identified
  ❌ Skipping this: 50% rework rate

Gate 2: Tech design review  
  ✅ Architecture is drawn (even if ASCII)
  ✅ Data model is designed
  ✅ API contracts are defined (OpenAPI/Swagger)
  ❌ Skipping this: 30% rework rate (interface mismatches)

Gate 3: Sprint commitment
  ✅ Tasks are decomposed into < 4h units
  ✅ Each task has an owner
  ✅ Dependencies are identified
  ❌ Skipping this: "I thought you were doing that" syndrome

Gate 4: Code review
  ✅ Reviews happen within 24h of PR being raised
  ✅ Reviewer understands the context
  ❌ Skipping this: technical debt, bugs, knowledge silos

Gate 5: Staging validation
  ✅ Integration tests pass
  ✅ Performance within threshold
  ❌ Skipping this: production incidents from integration issues
```

### 2.3 Ship-Ready Checklist

```
□ PRD signed off by stakeholders
□ Tech design reviewed (at least by one other engineer)
□ Data model finalized (migrations written)
□ API contract published (OpenAPI/Swagger)
□ Unit tests pass (> 80% coverage on new code)
□ Integration tests pass
□ Performance: p99 < 500ms for critical endpoints
□ Security scan passes (SAST, dependency scan)
□ Documentation updated (README, API docs, changelog)
□ Monitoring dashboards ready
□ Alert rules configured
□ Rollback plan documented
□ Feature flag in place (for progressive rollout)
□ Stakeholders notified
```

---

## 3. Milestone Planning

### 3.1 Milestone Structure

```
Epic: Payment system overhaul
  Milestone 1 (Week 1-2): Foundation — models, interfaces, tests
  Milestone 2 (Week 3-4): Core — create, process, refund
  Milestone 3 (Week 5-6): Edge cases, error handling, retries
  Milestone 4 (Week 7-8): Production hardening, monitoring, docs

Each milestone is a SHIPPABLE increment:
  Milestone 1: Can call the API, even if it returns mock data
  Milestone 2: Can create and process payments (happy path)
  Milestone 3: Handles edge cases (partial refund, network timeouts)
  Milestone 4: Production ready with monitoring and docs
```

### 3.2 Milestone Exit Criteria

```markdown
M1: Foundation
  □ Data models created (migrations v1)
  □ Repository interfaces defined
  □ Unit tests for models pass
  □ Can start the app and hit /health

M2: Core Happy Path
  □ Create payment works (unit test passes)
  □ Process payment works (integration test with mock gateway)
  □ Refund works
  □ > 80% test coverage on new code

M3: Edge Cases
  □ All API errors are handled (400, 404, 409, 500)
  □ Idempotency works (retry same request → same result)
  □ Network failures have retry logic
  □ Partial refund tested

M4: Production Ready
  □ Staging deploy passes E2E tests
  ✅ Performance: p99 < 300ms
  □ Monitoring: 3 golden signals dashboards ready
  □ Alert rules configured, runbooks written
  □ Canary deploy to production (10%)
  □ Production monitoring for 24h → full rollout
```

### 3.3 Dealing with Missed Milestones

```markdown
Milestone slip symptoms (catch early):
  - Estimation was off by > 2x in first sprint
  - Dependency project is delayed
  - Unforeseen complexity: "We didn't know X was this hard"

Action:
  1. Assess: How much is left vs how much time?
  2. Options:
     a. Reduce scope (cut non-critical features)
     b. Add resources (another engineer, pair programming)
     c. Extend timeline (tell stakeholders EARLY, not the day before)
  3. Communicate: "We'll miss M2 by 2 weeks. Options are A, B, C."
     Bad: "We're behind. We'll try harder."
     Good: "We're behind because X. I recommend reducing scope on Y. 
             This delays M3 by 1 week instead of 2."
```

---

## 4. Work Breakdown & Estimation

### 4.1 The Art of Decomposition

```markdown
Rule: A task should be completable in 2-4 hours.

If it takes longer → decompose.
If it takes shorter → combine.

Examples:
  Bad (8h): "Implement orders API"
  Good (2-4h each): 
    - Create Order model + Prisma migration
    - Implement CreateOrder endpoint (POST /orders)
    - Implement GetOrder endpoint (GET /orders/:id)
    - Implement ListOrders endpoint (GET /orders)
    - Write integration tests for orders API
```

### 4.2 Estimation Techniques

```markdown
Method 1: T-Shirt Sizes (back-of-envelope)
  XS: < 2h — fix a bug, add a test case
  S:  2-4h — single endpoint, simple UI change
  M:  4-8h — one feature (model + endpoint + test)
  L:  1-3d — complex feature (multiple endpoints, async processing)
  XL: 1-2w — entire epic (multi-module, integration)
  XXL: > 2w — project (needs decomposition)

Method 2: 3-Point Estimation
  Best case (optimistic): 2h
  Worst case: 8h
  Most likely: 4h
  Expected: (O + 4M + W) / 6 = (2 + 16 + 8) / 6 = 4.3h
  
Method 3: Reference-based
  "Remember the CreateProduct endpoint? It took 4h. This is similar."
  "Identify the differences: has more fields but same pattern. Add 2h. Total 6h."
```

### 4.3 Estimation Anti-Patterns

```markdown
❌ "It's simple, it'll take 2h" — and it takes 2 days
    → Because "simple" often means "I haven't thought about edge cases"
    → Fix: Ask "What's the worst case?" and use 3-point estimation

❌ "Just multiply by π" — padding without analysis
    → "It should take 2h, but let me say 6h to be safe"
    → Fix: communicate uncertainty, don't hide in padding

❌ "We don't estimate, we just sprint" — velocity is invisible
    → Without estimation, you can't know if you're on track
    → Fix: Even T-shirt sizes are better than nothing
```

---

## 5. Parallelization Strategy

### 5.1 Dependency Graph Analysis

```
Task decomposition reveals parallelism:

Serial path (can't parallelize):
  Domain model → Repository → Service → API → Test
  (each depends on the previous)

Parallelizable:
  Model A ← Independent → Model B ← Independent → Model C
  (can be done simultaneously)

Strategy:
  1. Identify independent modules
  2. Assign to different engineers
  3. Define contracts first (API, data model) — then parallelize the implementation
```

### 5.2 Conway's Law Applied

```
"Systems resemble the communication structures of the people who build them."

Application to parallelization:
  - 2 engineers can work on 2 microservices in parallel (if they don't need to talk)
  - 2 engineers on the same file = slow (merge conflicts, coordination overhead)
  - 1 engineer per module + 1 engineer cross-cutting = max throughput for small team

Pipeline for 2 engineers:
  Engineer A: Model → Repository → Service
  Engineer B: API endpoints → Tests
  
  When A finishes Model: A proceeds to Service
  B uses the model from A's PR for tests
```

### 5.3 Synchronization Points

```
Every sprint needs sync points to avoid going off-track:

Daily standup (15 min):
  - What did I do yesterday?
  - What will I do today?
  - What's blocking me?

Mid-sprint check (30 min, Day 3 of 2-week sprint):
  - Are we on track for sprint goal?
  - Any scope changes needed?
  - Any blockers emerging?

Demo (60 min, end of sprint):
  - Show what was built
  - Stakeholder feedback
  - Prioritize backlog

Retro (60 min, end of sprint):
  - What went well?
  - What went wrong?
  - What to improve?
```

---

## 6. Bottleneck Identification

### 6.1 Common Bottlenecks

```markdown
Bottleneck 1: Dependencies (waiting for other teams)
  - "We need the auth team's API first"
  - Fix: mock it. Define contract, mock the dependency, implement in parallel

Bottleneck 2: Code review queue
  - "My PR has been waiting for review for 3 days"
  - Fix: set SLA for reviews (within 24h), rotate reviewers, pair review

Bottleneck 3: Testing environment
  - "I can't deploy to staging, someone else is using it"
  - Fix: ephemeral environments per PR (Preview environments)

Bottleneck 4: Deploy pipeline
  - "Deploy takes 30 minutes and blocks other deploys"
  - Fix: CI/CD optimization (parallel stages, faster builds)

Bottleneck 5: Decision paralysis
  - "We need to decide between X and Y before proceeding"
  - Fix: timebox decision to 30 minutes. If can't decide, flip a coin and iterate
```

### 6.2 Bottleneck Detection Metrics

```yaml
Metric: PR cycle time
  Good: < 1 hour from open to merge
  OK: < 4 hours
  Bad: > 1 day → check review queue
  Critical: > 1 week → process problem

Metric: Deploy frequency
  Good: multiple deploys per day (CI/CD maturity)
  OK: daily
  Bad: weekly
  Critical: monthly

Metric: Sprint completion rate
  Good: > 90% committed stories delivered
  OK: 70-90%
  Bad: < 70% → overcommitment or wrong estimation

Metric: Time from "decision" to "first working code"
  Good: same day
  OK: 2-3 days
  Bad: > 1 week
```

### 6.3 The Theory of Constraints Applied

```
Identify the constraint → exploit it → subordinate everything → elevate → repeat

Example:
  1. Constraint: code reviews take 3 days
  2. Exploit: reviewer SLAs, rotation schedule
  3. Subordinate: limit WIP (each engineer submits max 1 PR, 
     reviews others' before submitting next)
  4. Elevate: hire another reviewer, automate reviews (lint, type-check, AI review)
  5. Repeat: next constraint is... deploy pipeline (30 min per deploy)
```

---

## 7. Velocity Metrics & Dashboards

### 7.1 Metrics That Matter

```yaml
Leading indicators (predict future problems):
  - WIP (work in progress): > 3 per engineer = multitasking
  - Cycle time: how long from "start" to "done"
  - Review time: how long PR waits for review
  - Deploy success rate: % of deploys that don't need rollback

Lagging indicators (measure past performance):
  - Sprint velocity: story points per sprint (trend, not absolute)
  - Bug rate: bugs found per feature
  - On-time delivery: % of sprints hitting commitment
  - Time to market: from idea to production

Anti-metrics (don't measure these):
  - Lines of code per day (vanity metric)
  - Individual developer velocity (team sport)
  - Hours worked (input, not output)
```

### 7.2 Dashboard

```yaml
Row 1: Sprint health
  [Sprint burndown]  [Velocity trend (last 8 sprints)]  [Bug rate per sprint]

Row 2: Flow metrics
  [WIP count]        [Cycle time histogram]            [Review time p50/p95]

Row 3: Quality
  [Test pass rate]   [Coverage trend]                  [Deploy success rate]

Row 4: Ship
  [Time to prod]     [Deploy frequency]                [Features shipped this month]
```

### 7.3 The Velocity Trend Chart

```
Sprint Velocity over 8 sprints:
  
  40 |    ██
  35 | ██ ██ ██
  30 | ██ ██ ██ ██    ██
  25 | ██ ██ ██ ██ ██ ██ ██
  20 | ██ ██ ██ ██ ██ ██ ██ ██
     └─────────────────────────
       S1  S2  S3  S4  S5  S6  S7  S8

Interpretation:
  - Stable trend (25-35 range) → good predictability
  - Declining trend → team is accumulating debt, burnout, or complexity
  - Sudden spike → overcommitment (they'll crash next sprint)
  - Sudden drop → bottleneck emerged
```

---

## 8. Kanban for Engineers

### 8.1 The Engineering Kanban Board

```
┌──────────────┬────────────┬────────────┬──────────────┬──────────────┐
│   Backlog    │  To Do     │  In Progress│  Review      │  Done        │
│              │            │  (WIP: 2/3) │  (24h SLA)   │              │
├──────────────┼────────────┼────────────┼──────────────┼──────────────┤
│ [ ] Order API│ [ ] Fix bug │ [▶] Payment│ [▶] Review   │ [✔] Auth API│
│ [ ] Cache    │ [ ] Refactor│ [▶] Email  │   Order API  │ [✔] User API│
│ [ ] Webhook  │ [ ] Tests  │            │              │ [✔] Config  │
│ [ ] Rate     │            │            │              │              │
│     limiting │            │            │              │              │
└──────────────┴────────────┴────────────┴──────────────┴──────────────┘
```

### 8.2 WIP Limits by Team Size

```
Single engineer:
  WIP limit: 2 (1 active, 1 in review)
  Anything more = context switching

2-3 engineers:
  WIP limit: 3-4 total, max 2 per person
  Review column: build review into schedule (dedicated time)

4-8 engineers:
  WIP limit: 2 per person, 6-10 total
  Review column SLA: < 4 hours
  Dedicated reviewer rotation: 20% time

> 8 engineers:
  Distributed teams: different boards per service
  Each board: same WIP limits
```

### 8.3 Pull, Don't Push

```
❌ Push: Manager assigns tasks to engineers
    "You do X. You do Y. You do Z."
    → Engineers have no ownership, no autonomy
    → Worse: engineer gets blocked on X, can't pick up Y

✅ Pull: Engineers pull from the backlog
    "Here's the prioritized backlog. Pick your next task."
    → Ownership: "I chose this"
    → Flow: if blocked, pull next task immediately
    → Requires: well-groomed backlog with clear tasks
```

---

## 9. Agile Anti-Patterns

### ❌ Anti-Pattern 1: Sprint Is a Deadline, Not a Box

```
BAD: "We must ship everything in sprint backlog by Friday"
     → Quality suffers, overtime, bugs go to prod

GOOD: "This sprint's goal is to get CreateOrder working.
       If UserProfile doesn't make it, it's fine."
     → Scope is flexible within a sprint
     → The goal is non-negotiable, the tasks are
```

### ❌ Anti-Pattern 2: Standup = Status Report

```
BAD: 
  Scrum Master: "Alice?"
  Alice: "I did X, I'm doing Y, no blockers."
  Bob: "I did Z, I'm doing W, no blockers."
  ... 15 minutes later, no actual discussion happened.

GOOD:
  Alice: "I finished Order model PR. Waiting on review from Bob. 
          Starting on Order service."
  Bob: "I can review Alice's PR this afternoon. 
        Currently blocked on database migration — need schema review."
  Team: (spends 5 minutes discussing schema)
  → Actual progress + unblocking
```

### ❌ Anti-Pattern 3: Retro Is a Complaint Session

```
BAD: 
  "We should do more testing"
  "Communication could be better"
  (no concrete actions, same complaints next sprint)

GOOD:
  "Problem: PRs wait 2 days for review"
  "Root cause: No review SLA + everyone has their own PRs"
  "Action: We'll rotate reviewer duty daily. 
           Reviewer has no new commits on review day.
           Experiment for 2 sprints, then evaluate."
```

### ❌ Anti-Pattern 4: Estimation as Performance Metric

```
BAD: 
  "Alice completed 30 points, Bob completed 20 points. 
   Alice is 50% more productive!"

GOOD:
  "Team velocity is 50 points/sprint. 
   We've delivered 50 points reliably for 4 sprints. 
   Good predictability for planning."

  Velocity is a TEAM metric for PREDICTABILITY.
  Not an INDIVIDUAL metric for PERFORMANCE.
```

### ❌ Anti-Pattern 5: Ceremony Over Substance

```
BAD: 
  Sprint planning: 4 hours for a 1-week sprint
  Standup: 30 minutes (everyone has a 2-minute turn)
  Retro: 2 hours
  Sprint review: 2 hours (with stakeholders presenting)
  
  Ceremony: 8 hours / week (20% of engineering time)

GOOD:
  Sprint planning: 2 hours (2-week sprint)
  Standup: 10 minutes  
  Retro: 45 minutes
  Sprint review: 30 minutes
  
  Ceremony: 3.5 hours / 2 weeks = < 5% of time
```

---

## 10. Multi-Project Portfolio Management

### 10.1 Resource Allocation

```markdown
Single large project: 100% of team → high throughput, high risk
  Risk: one dependency blocks whole team
  Strategy: decompose into parallel workstreams

Multiple smaller projects: split team → lower risk, lower throughput
  Risk: context switching overhead (each project has overhead)
  Strategy: commit team to ONE project per sprint

Skip projects: > 50% time on operations
  Risk: no innovation
  Strategy: budget operations time explicitly (20% of sprint)
```

### 10.2 Portfolio Board

```yaml
Project:               Priority:    Status:      Next Milestone:      Owner:
──────────────────────────────────────────────────────────────────────────
Payment system           P0           On track     M2 (end of Sprint 4)   Alice
User profile redesign    P1           At risk      M1 (end of Sprint 5)   Bob
Rate limiting            P2           Blocked      Awaiting infra team   —
API docs                 P2           On track     v2 docs (end Wk 3)    Charlie

Resource allocation next sprint:
  Alice: 100% Payment (P0)
  Bob:   60% User Profile (P1) + 40% unblock Rate Limiting (P2)
  Charlie: 100% API docs (P2)
```

### 10.3 Decision Framework: What to Build Next

```markdown
Priority matrix:

                        High Impact              Low Impact
High Urgency       🚨 Do this NOW           🔷 Do this soon
                   (Payment system,         (Dashboard redesign)
                    Auth vulnerability)

Low Urgency        🟢 Plan for next month   ❌ Don't do
                   (Rate limiting,          (Feature nobody asked for)
                    Performance optimization)
```

### 10.4 Project Completion Checklist

```
□ All acceptance criteria met
□ Integration tests pass in staging
□ Performance within SLOs
□ Monitoring dashboards in place
□ Alert rules configured
□ Runbooks written (top 3 failure scenarios)
□ Documentation updated (README, API docs, changelog)
□ Stakeholders have been demo'd
□ Rollback plan documented
□ Post-mortem scheduled (for any incidents during rollout)
□ Team retrospectives captured (what to do differently next time)
```
