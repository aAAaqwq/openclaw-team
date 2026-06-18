# Bounty Spec Writer

## When to Apply
Use when AI self-healing fails after 3+ attempts and a complex L2-level problem needs to be escalated to human engineers.

## Bounty Package Structure

Every bounty MUST contain:

```
┌─────────────────────────────────────┐
│         │ BOUNTY PACKAGE │           │
├─────────────────────────────────────┤
│ id:       bounty-YYYYMMDD-NNN       │
│ severity: L2 (critical)             │
│ status:   Open / In Progress / Done │
│ budget:   $/tokens (from 大才)       │
├─────────────────────────────────────┤
│ PROBLEM STATEMENT                   │
│ (What's the issue, when did it      │
│ start, what's the impact)           │
├─────────────────────────────────────┤
│ ROOT CAUSE ANALYSIS                 │
│ (What we tried, AI fix logs,        │
│ what failed after 3 attempts)       │
├─────────────────────────────────────┤
│ EXPECTED OUTPUT                     │
│ (Acceptance criteria, test cases,   │
│ performance requirements)           │
├─────────────────────────────────────┤
│ CONTEXT (ARCHIVE)                   │
│ (Code repo, system logs, config,    │
│ relevant source files)              │
└─────────────────────────────────────┘
```

## Acceptance Criteria Format

```yaml
bounty:
  id: bounty-20260501-001
  pass_conditions:
    - condition: "The fix resolves the DB deadlock under 1000+ TPS"
      verification: "Run benchmark-sim.sh — script exits 0"
    - condition: "Zero regression in existing tests"
      verification: "npm run test:all — 100% pass"
  fail_conditions:
    - "Introduces new concurrency vulnerabilities"
    - "Reduces query performance by >10%"
```

## Severity Levels

| Level | AI Attempts | Human Required | Response Time |
|-------|-------------|----------------|--------------|
| L0 | 0 | No (auto-dev) | — |
| L1 | 1-2 | Review only | — |
| L2 | 3+ | Full human | <24h |
| L3 | — | Architecture redesign | <72h |
