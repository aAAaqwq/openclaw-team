# VibeCoding

> Level: Expert | File: `vibecoding.md`
> 
> High-throughput AI-assisted software development: flow-state engineering,
> iteration speed maximization, context management, and the art of staying in the zone
> while collaborating with AI coding agents.

---

## Table of Contents
1. [What is VibeCoding?](#1-what-is-vibecoding)
2. [Flow State Engineering](#2-flow-state-engineering)
3. [Prompt Engineering for Velocity](#3-prompt-engineering-for-velocity)
4. [Context Management](#4-context-management)
5. [Multi-File Edit Strategies](#5-multi-file-edit-strategies)
6. [Parallel Branches & Hot Reload](#6-parallel-branches--hot-reload)
7. [AI Agent Orchestration Patterns](#7-ai-agent-orchestration-patterns)
8. [Error Recovery Flow](#8-error-recovery-flow)
9. [The Anti-Patterns of Slow Coding](#9-the-anti-patterns-of-slow-coding)
10. [VibeCoding Metrics](#10-vibecoding-metrics)

---

## 1. What is VibeCoding?

### 1.1 The Core Idea

> VibeCoding is the practice of maintaining uninterrupted flow state with AI agents
> by optimizing the feedback loop: write → run → fix → iterate.

```
Traditional dev loop:
  Write 50 lines → cmd+S → terminal → compile → scroll → fix → 30s lost

VibeCoding dev loop:
  Edit → AI suggests completion → auto-compile in background → test on save
  → if fails → AI auto-fixes → re-test → if passes → next task

Gap between the two: 3x-10x throughput difference
```

### 1.2 Principles

| Principle | Description |
|-----------|-------------|
| **Never break flow** | Every context switch costs 15-25 min to regain deep focus. Optimize for uninterrupted 2-hour blocks. |
| **Fail fast, fix faster** | Make the AI agent compile on every change. Catch errors in 3 seconds, not 3 minutes. |
| **Small diffs, high velocity** | A 5-line change every 2 minutes beats a 50-line change every 20 minutes. |
| **Trust the AI, verify the contract** | Let the AI implement, you verify contracts and tests. |
| **Document by exception** | If the code is clear, don't write comments. If it needs a comment, refactor the code. |

### 1.3 The VibeCoding Score

```
How fast can you deliver a feature end-to-end?

1 line / minute:      reading legacy code, figuring out where to start
3 lines / minute:     typing manually, looking up syntax
10 lines / minute:    using AI completions, good flow state
30 lines / minute:    VibeCoding mastery — multi-file edits, AI agents do implementation
100+ lines / minute:  Batch generation + AI test + auto-fix cycle (sustained peak)

Target for expert: sustained 30-50 lines/min over 2-hour blocks
Target for peak: bursts of 100-200 lines/min for boilerplate/patterns
```

---

## 2. Flow State Engineering

### 2.1 Setting Up Flow

```
Pre-requisites before a VibeCoding session:

1. Clear task definition (30 min prep for 2h flow)
   □ I know EXACTLY what I'm building
   □ I have the data model sketched
   □ I know the test cases before I write code
   □ PRD/AC in hand

2. Ready environment (5 min)
   □ Tests pass before I start
   □ Terminal open, test runner in watch mode
   □ API server in hot-reload mode
   □ AI agent loaded with the right context

3. Distraction-free (phone away, notifications off)
   □ 2 hours minimum uninterrupted
   □ No meetings, no slack, no notifications
```

### 2.2 The Iteration Cadence

```
Timeline (average VibeCoding session):
  0:00  → Start: open PRD, load context into AI
  0:02  → AI generates first draft implementation
  0:04  → Compilation check (auto)
  0:05  → Test run (auto, watch mode)
  0:06  → Fix test failures (auto-fix cycle)
  0:10  → All tests pass → commit
  0:15  → Next task...

Key metric: time from "start task" to "green tests"
  Expert: 5-15 min per module
  Average: 30-60 min per module
  Slow: 2+ hours (need to refactor approach)
```

### 2.3 The VibeCoding Loop

```mermaid
graph TD
    A[Read PRD/AC] --> B[Sketch in head: model, API, test cases]
    B --> C[Tell AI: "Implement X"]
    C --> D{AI writes code}
    D --> E[Auto-compile + test]
    E --> F{All green?}
    F -->|Yes| G[Commit + Next task]
    F -->|No| H{Error type?}
    H -->|Compile| I[Tell AI to fix]
    H -->|Test| J[Tell AI to fix test or code]
    I --> D
    J --> D
    G --> B
```

### 2.4 When Flow Breaks (and How to Recover)

```
Flow break signal                   Recovery action
──────────────────────────────────────────────────
Stuck on same error for 5 min     → Step back: is this the right approach?
                                   → Re-read the API contract
                                   → Ask AI: "Rewrite from scratch, different approach"

Test takes >30s to run            → Fix test isolation (mocks, in-memory DB)
                                   → Add --only flag for current test

AI keeps producing same bug       → "Stop. Restart. New context scope."
                                   → Clear AI context, re-prompt with narrower scope

Need to check documentation       → "Don't open docs. Ask AI."
                                   → If AI wrong, then check docs (but try AI first)

Integration with another service  → Mock it, don't test against it live
                                   → If mocking is complex → contract test
```

---

## 3. Prompt Engineering for Velocity

### 3.1 The One-Shot Prompt Formula

```typescript
// ❌ Slow prompt
"Create an order service"

// ✅ Fast prompt (one-shot = immediate correct code)
`
Implement POST /api/v1/orders endpoint in this existing Fastify app.

Context:
- Database: Prisma, model Order { id, userId, items, total, status }
- Validate 'items' array (1-100 items, each with productId and quantity)
- Calculate total from product prices (Product model has price field in cents)
- Set initial status: "pending"
- Return 201 with { id, total, status }
- Handle: 400 on validation fail, 404 on invalid product, 500 on DB error

Location: src/routes/orders.ts
Test file: tests/routes/orders.test.ts (already exists, update it)

Do NOT:
- Create new files unless absolutely necessary
- Change Prisma schema
- Add new dependencies
`
```

### 3.2 Prompt Structure Template

```markdown
**Action**: [create | update | fix | refactor] [file/component]
**Context**: [input/output contracts, relevant types]
**Constraints**: [what NOT to do]
**Location**: [exact file path]
**Verification**: [test file, curl command]
**Style**: [patterns to follow, naming conventions]

Example:
```
Action: Refactor PaymentService.processCharge method
Context: Currently 200 lines, needs to extract PaymentStrategy pattern
  Input: { amount, currency, sourceId }
  Output: { chargeId, status, error? }
Constraints: 
  - Keep StripeGateway interface unchanged
  - No new dependencies
  - Existing tests must pass without modification
Location: src/services/payment/PaymentService.ts
Verification: tests/services/payment/process.test.ts
Style: 
  - Use factory pattern for strategy selection
  - Single responsibility per class
  - Pure functions where possible
```

### 3.3 Fix vs. Rewrite Decision

```markdown
When to fix (small error):
  "Fix the TypeScript compilation error on line 47: 
   'amount' is of type 'number' but expected 'Money'"

When to rewrite (design flaw):
  "This approach has a race condition. Delete everything 
   and implement with a database-level transaction."

When to prompt differently:
  "Your approach isn't working. Let me explain the problem again: 
   [different explanation]."

When to escalate (complex):
  "This requires understanding the full payment flow. 
   Let me reframe the task with all dependencies."
```

### 3.4 Multi-Model Strategy

```yaml
Strategize: DeepSeek / Claude Opus
  - Cost: higher (but worth it for architecture)
  - Use: decompose complex tasks, plan implementation
  - Prompt: "Design the API contract and data model for X"

Implement: Claude Sonnet / GPT-4o
  - Cost: medium
  - Use: generate code from clear spec
  - Prompt: "Implement the endpoint per this contract"

Fix: Fast model (Claude Haiku / GPT-4o-mini)
  - Cost: low
  - Use: auto-fix compilation, simple bug fixes
  - Prompt: "Fix test failure: expected 403 but got 200"

Review: DeepSeek / Claude Opus
  - Cost: higher
  - Use: code review, architecture feedback
  - Prompt: "Review this PR: security, performance, correctness"
```

### 3.5 Prompt Chaining

```
Phase 1: "Design the data model for order management"
  → AI outputs: Prisma schema, TypeScript types
  
Phase 2: "Based on this data model, design the API endpoints"
  → AI outputs: API contract, route structure
  
Phase 3: "Implement the create order endpoint per this contract"
  → AI outputs: working code
  
Phase 4: "Write tests for the create endpoint"
  → AI outputs: test file
  
Phase 5: "Review for security: is there any injection risk or IDOR?"
  → AI outputs: security report + fixes

Each phase feeds directly into the next. No context loss.
```

---

## 4. Context Management

### 4.1 Context Window Optimization

```yaml
Model Limits:
  Claude Opus:     200K tokens (200 pages of text)
  DeepSeek:        128K tokens
  GPT-4 Turbo:    128K tokens

What fits in 128K context:
  - 5,000 lines of TypeScript code (~100KB)
  - 10 medium-sized files (500 lines each)
  - OR: 1 PRD + 3 key source files + 1 test + 1 config file

Context strategy (fit the MOST relevant in the window):
  1. PRD / Acceptance Criteria (< 2K tokens)
  2. Files you're modifying (< 5K tokens each)
  3. Key interface/type definitions (< 1K tokens)
  4. Relevant test files (< 5K tokens)
  5. Config files if relevant (< 1K tokens)
  
  AVOID: node_modules, generated files, logs, binary data
```

### 4.2 File Context Prioritization

```markdown
Given a task to "Add payment webhook handling" — provide:

✅ MUST include:
  - Current webhook handler (the file you're modifying)
  - Event type definitions
  - Payment service interface
  - Test file for webhook
  
❌ DON'T include:
  - All models (just the relevant model file)
  - All routes (just the one you're modifying)
  - Full Prisma schema (just the relevant tables)
  - package.json, tsconfig, Dockerfile
```

### 4.3 Context Persistence Strategy

```typescript
// Project-level context file: .vibecoding/context.md
// This file is maintained as you work and included in AI prompts

# VibeCoding Context — Order Service

## Architecture
- Express + Prisma + PostgreSQL
- Controllers call Services, Services call Repositories
- All business logic in Services
- JSONB for order items (not separate table)

## Key Decisions (from ADRs)
- ADR-001: Use ULID for order IDs (not UUID)
- ADR-004: Webhook processing uses idempotency key dedup

## Current Task
- Creating POST /api/v1/orders endpoint
- Working in src/controllers/orderController.ts

## Known Patterns
- Error handling: throw AppError(statusCode, code, message)
- Response format: { success: boolean, data?: T, error?: ErrorResponse }
- Pagination: cursor-based, use 'cursor' query param

## Common Pitfalls
- Prisma client must be instantiated once (singleton)
- Decimal fields: use Prisma.Decimal, not number
- All times in UTC, convert on frontend
```

---

## 5. Multi-File Edit Strategies

### 5.1 Strategy: One-Shot Multi-File

```
Best for: well-defined features with clear contracts

1. Tell AI all files to create/modify at once
2. AI outputs all files in sequence
3. Apply all edits
4. Test

Example prompt:
"""
I need to add payment webhook handling:

1. Create: src/webhooks/stripe/handler.ts
   - Verify Stripe signature
   - Map event types to our domain events
   - Update order status on payment_intent.succeeded

2. Update: src/services/PaymentService.ts  
   - Add handleWebhook method
   - Return { eventType, orderId, status }

3. Update: src/routes/webhooks.ts
   - Add POST /webhooks/stripe endpoint
   - Use the handler

4. Create: tests/webhooks/stripe.test.ts
   - Test signature verification
   - Test event handling for all event types
   - Test invalid signature returns 401
"""
```

### 5.2 Strategy: Iterative Refinement

```
Best for: when you're iterating on a design

1. Start with models and interfaces
2. Finish one file, test, move to next
3. Let the AI handle the "glue" between files

Cadence:
  Round 1: User model + interfaces → test
  Round 2: Order model + repository → test
  Round 3: CreateOrder service → test
  Round 4: POST /orders route + controller → test
  Round 5: Error handling + edge cases → test
```

### 5.3 Concurrent File Editing

```markdown
When using Cursor / Windsurf with AI agents:

Rule 1: Never have two AI edits touching the SAME file simultaneously
  → Causes merge conflicts that waste time
  → Solution: assign one file per agent

Rule 2: If files have dependency, build order matters
  → Model before Service before Route
  → Interface before Implementation

Rule 3: Let the AI handle boilerplate mapping
  "The models are done. Now generate a Prisma CRUD repository 
   for Order that implements IOrderRepository"
```

---

## 6. Parallel Branches & Hot Reload

### 6.1 Branch Strategy for VibeCoding

```yaml
Main branch: clean, tested, stable
Feature branch: where magic happens

Feature branch workflow:
  1. Branch off main: "feature/payment-webhook"
  2. VibeCode: rapid iteration (rebuild, test, fix, commit)
  3. Commit every green-test state (10-15 min cycles)
  4. Squash to 1-3 meaningful commits before PR
  5. PR reviewed (human or AI) → merge to main

Never leave a feature branch uncommitted:
  - If interrupted: commit with "WIP" prefix
  - If session ends: push branch, clean up later
  - If approach fails: reset to last green commit
```

### 6.2 Hot Reload Setup

```bash
# Backend: nodemon + ts-node (Node)
nodemon --watch 'src/**/*.ts' --exec 'ts-node' src/index.ts

# Backend: air (Go)
air -c .air.toml  # rebuilds on file change, sub-second

# Backend: uvicorn --reload (Python)
uvicorn app.main:app --reload --port 8000

# Frontend: Next.js (built-in HMR)
next dev

# Test runner: watch mode
vitest --watch    # Runs only changed test files
```

### 6.3 Test Feedbacks That Keep Flow

```markdown
❌ Bad: Tests take 3 min to run
  "Test failed... wait... scroll scroll scroll... oh, assertion mismatch"
  → Flow broken, 5 min to recover

✅ Good: Tests run in < 3 seconds
  Tests pass on save. Auto-re-run focused tests.
  Compilation error caught in < 1 second.

✅ Best: Tests on save + background full suite
  1. On save: run ONLY affected tests (vitest --changed)
  2. In background: full test suite runs
  3. If background fails: notify
```

---

## 7. AI Agent Orchestration Patterns

### 7.1 Single-Agent Flow (Simple Tasks)

```
[User] → Prompt → [AI Agent] → Code + Tests → [User] validates → Done

Best for: small tasks < 100 lines
  - Creating a single endpoint
  - Writing unit tests for an existing function
  - Fixing a specific bug
```

### 7.2 Multi-Agent Parallel (Medium Tasks)

```
[User] → Decompose into N independent tasks
  Task 1 → Agent A → Module A code + tests
  Task 2 → Agent B → Module B code + tests  
  Task N → Agent N → Module N code + tests
[User] → Verify integration + run full test suite

Best for: medium features 100-500 lines
  - New feature with 2-3 files
  - Adding CRUD for a new entity
  - Creating a new microservice
```

### 7.3 Swarm (Complex Tasks)

```
[User] → PRD → [Orchestrator AI] 
  → Decompose to task graph
  → Assign to swarm agents
  → [Agents A-N] → Parallel implementation
  → [Orchestrator] → Integration + test
  → [Heal Agent] → Auto-fix failures  
  → [Review Agent] → Quality gate
  → [User] → Final review

Best for: complex features > 500 lines
  - Building a complete microservice
  - End-to-end feature with UI + API + DB
  - Large refactoring with tests
```

### 7.4 Multi-Agent Communication Rule

```markdown
Golden rule: Agents do NOT talk to each other

Instead:
  - User acts as the hub
  - One agent's output = next agent's input
  - Contracts are explicit (shared types, API spec)

Why: 
  - AI-to-AI conversation wastes tokens and drifts
  - User keeps context of the big picture
  - Easier to debug when something goes wrong
```

---

## 8. Error Recovery Flow

### 8.1 The 3-Second Rule

```
If error takes > 3 seconds to understand → don't read error manually
  → Paste to AI: "This test failed. Fix it."

If AI takes > 2 attempts to fix → step back
  → Maybe the approach is wrong
  → Maybe the test is wrong (not the code)
  
If 3 attempts fail → escalate approach
  → "Delete everything I just did. Different approach needed."
  → Consider: different algorithm? different library? different abstraction?
```

### 8.2 Error Categories & Recovery

```
Compilation Error (easy fix):
  Recovery: Paste error to AI → "Fix this compilation error"
  Average time: 10-30 seconds

Test Failure (medium):
  Recovery: Paste test output → "Fix the failing test"
  Options:
    - Code is wrong → AI fixes code
    - Test is wrong (stale assumption) → AI fixes test
    - Both → "Re-evaluate the test and the implementation"
  Average time: 30 seconds - 2 minutes

Logical Error (hard):
  Recovery: "This code doesn't handle [edge case]. Rewrite the function."
  Average time: 2-5 minutes

Design Flaw (hardest):
  Recovery: "Delete function X. We'll use approach Y instead."
  Average time: 5-15 minutes (need new approach)
```

### 8.3 The Emergency Stop

```markdown
When to emergency stop:
  1. Same test fails > 3 attempts → approach is wrong
  2. AI enters infinite loop of "fix one thing, break another"
  3. You've spent 30 min on what should be a 5 min task
  4. You don't understand what the AI produced

Recovery:
  1. git reset --hard HEAD (back to last green state)
  2. git stash (save current work, revert to clean state)
  3. Take 5 min to reconsider approach
  4. Write down what went WRONG before continuing
```

---

## 9. The Anti-Patterns of Slow Coding

### ❌ Anti-Pattern 1: Manually Reading Error Messages

```
BAD: Error pops up. You read 20 lines of stack trace.
     "Oh, line 47... 'amount' is type Mismatch..."
     Scroll to line 47. "Ah, I need to cast this."
     Type: `(amount as Money)` — saved 5 seconds vs AI doing it.

GOOD: Select error → Cmd+K → "Fix this" → AI fixes → save → tests pass
     Total: 3 seconds. Maintained flow.
```

### ❌ Anti-Pattern 2: Manual Boilerplate

```
BAD: Create a new endpoint:
     - Create route file (20 lines boilerplate)
     - Create controller (10 lines boilerplate)
     - Create service (5 lines boilerplate)
     - Create test (40 lines boilerplate)
     - 75 lines boilerplate × 2 min = 10 min wasted

GOOD: 
     Prompt: "Create POST /api/v1/categories endpoint. Same pattern as
              orders controller. Categories have { id, name, parentId }."
     → AI outputs 4 files in 15 seconds
```

### ❌ Anti-Pattern 3: Perfect First Try

```
BAD: Spend 20 min thinking about the "perfect" design
     Write 200 lines of code
     Test fails
     "Argh! 20 min wasted!"
     Refactor for another 20 min

GOOD: Skeleton → AI implements → test → fail → fix → pass
      Total: 5 min for the same 200 lines
      The first attempt doesn't need to be perfect — 
      it just needs to be FAST.
```

### ❌ Anti-Pattern 4: Manual Search

```
BAD: "How do I implement Stripe webhook verification?"
     Open browser → search → read 5 docs → skim SDK docs
     Write code → test → it doesn't work → re-read docs
     Total: 30 min

GOOD: "Implement Stripe webhook verification for event type
       payment_intent.succeeded. Use Stripe SDK's webhook 
       helper. Test with mock payload."
     → AI knows the API. It's in training data. 30 seconds.
     → If wrong: "This didn't work. Here's what the docs say: ..."
```

### ❌ Anti-Pattern 5: Manual Testing

```
BAD: Every time you change code:
     - Switch to terminal
     - Type npm test
     - Wait 30s for full test suite
     - Scroll to find relevant test output
     - Switch back to editor

GOOD: 
     vitest --watch --changed
     On save: only affected tests run (< 2 seconds)
     Result shown in-editor (inline, no context switch)
```

---

## 10. VibeCoding Metrics

### 10.1 Personal Metrics

```
Measure per session:
  - Lines of code written (net, not deleted)
  - Time to green tests (from first edit to all passing)
  - Number of AI corrections (should be 1-3 per task)
  - Flow interruptions per hour (target: < 1)

Session report:
  Session: 14:00 - 16:00 (2 hours)
  Tasks completed: 4
  Net lines: +520
  Test failures: 7 → all auto-fixed
  AI corrections: 2 (both < 10 seconds)
  Flow interruptions: 0
  State: Exhausted but happy 🚀
```

### 10.2 Project Metrics

```
Feature velocity:
  - Lines per day (sustained): 1,000-3,000
  - Features per week: 3-10 (depending on complexity)
  - Time to first usable prototype: 1-3 days
  
Quality:
  - Review score: > 0.8 (target)
  - Test coverage: > 80% on new code
  - Heal rate: < 20% (less than 1 in 5 tasks needs fixes)
  
Cost:
  - AI tokens per feature: optimize (smaller context = less tokens)
  - Cost per line: varies by model
  - Time saved vs manual: 3-10x
```

### 10.3 Maturity Model

```
Level 1: Competent (100-500 lines/session)
  - Uses AI autocomplete
  - Manually copies/pastes multi-file changes
  - Reads error messages manually
  
Level 2: Proficient (500-2000 lines/session)
  - Prompts AI for code generation
  - Lets AI fix errors
  - Multi-file edits via prompt
  
Level 3: Expert (2000-5000 lines/session)
  - Hybrid: strategies in AI, implementation in AI
  - Swarm: decomposes work, runs agents in parallel
  - Context management: optimized prompts per task
  
Level 4: Master (5000+ lines/session)
  - Full feature generation with zero manual code
  - Self-healing agents for test failure recovery
  - Parallel swarms for independent modules
  - Error rate < 5% code needs manual fixes
```
