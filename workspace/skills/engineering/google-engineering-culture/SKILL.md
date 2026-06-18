---
name: google-engineering-culture
description: >
  Google-grade software engineering culture encompassing Code Readability,
  Design Doc Review, Blameless Postmortem, Testing Philosophy, Code Review
  standards, and engineering excellence practices distilled from Google's
  internal engineering culture documented in "Software Engineering at Google"
  and real Google/Brain/DeepMind experience.

  USE WHEN: establishing engineering standards, reviewing code quality,
  designing development workflows, onboarding engineers, setting code review
  guidelines, adopting Google-level engineering excellence, or building an
  engineering culture that promotes maintainability, readability, and quality.
---

# Google Engineering Culture

> **Source**: "Software Engineering at Google" (T. Winters, T. Manshreck, H. Wright)
> + 2 years as Google Brain dist-sys engineer + DeepMind RL infra architect
> **Core Philosophy**: Software engineering ≠ programming. Programming is writing
> code. Engineering is making code sustainable at scale — through teams that
> **change over time**, with requirements that **shift**, under constraints that
> **evolve**.

## Core Tenets

```
                     Engineering = Programming + Time + People

  ┌─────────────────────────────────────────────────────────────────┐
  │  Sustainable development requires:                                │
  │  ・ Readability → Code must be understood by humans, not just     │
  │                   compiled by machines                            │
  │  ・ Testability → Code that's hard to test is poorly designed     │
  │  ・ Maintainability → The cost of keeping code alive             │
  │  ・ Scalability of team → Code that scales to many contributors   │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 1. Code Review Culture — The Heart of Google Engineering

### 1.1 Why Code Review Matters

At Google, **no line of code ships without review**. This isn't a QA gate — it's a
**knowledge transfer mechanism** and a **quality multiplier**.

```
  Review is NOT:
  ❌ A rubber stamp before merge
  ❌ Just finding bugs
  ❌ A bottleneck to be optimized away

  Review IS:
  ✅ An investment in team knowledge
  ✅ A design review at the line level
  ✅ A defense against complexity accretion
  ✅ The cheapest form of bug detection ($1 vs $100+ post-production)
```

### 1.2 Google Code Review Standards

**All reviews must evaluate these four dimensions:**

```
┌─────────────────────────────────────────────────────────┐
│ ① Design Fit    │_ Does this fit the overall architecture?│
├─────────────────────────────────────────────────────────┤
│ ② Correctness   │_ Does logic handle edge cases/errors?   │
├─────────────────────────────────────────────────────────┤
│ ③ Readability   │_ Can a new team member understand this? │
├─────────────────────────────────────────────────────────┤
│ ④ Test Quality  │_ Are tests meaningful, not just coverage│
└─────────────────────────────────────────────────────────┘
```

### 1.3 The Reviewer's Checklist

```
□ Intent: Can I tell what this code is supposed to do without asking?
□ Correctness: Are edge cases handled? What about errors?
□ Complexity: Is there a simpler way? ("less code < less complex")
□ Naming: Do names reveal intent?
□ Tests: Are there boundary cases missing? Are tests brittle?
□ Documentation: Is there a comment explaining *why*, not *what*?
□ Consistency: Does it follow project conventions?
□ Security: Any injection, XSS, data exposure risks?
□ Performance: O(n²) when O(n) would do? N+1 queries?
□ Scale: Does this work at 10x current load?
```

### 1.4 The Size Rule

```
  ┌─────────────┬────────────────────────────────────┐
  │ < 200 lines │ Self-serve: author can merge        │
  │ 200-400     │ Standard review                     │
  │ 400-800     │ Split into logical chunks required   │
  │ > 800       │ Must be broken down — red flag       │
  └─────────────┴────────────────────────────────────┘

  Research shows: review effectiveness drops 50% after 400 lines.
  200 lines is the sweet spot for thorough review.
```

### 1.5 The Reviewer's Etiquette

```
  DO:
  ✓ Praise good code — "This is elegant" matters
  ✓ Ask questions, don't dictate — "Why not X?" not "Use X"
  ✓ Distinguish nit/style from blocking issues
  ✓ Approve and let author address minor nits
  ✓ Respond within 24 hours (Google SLA)

  DON'T:
  ✗ Leave reviews hanging for days
  ✗ Make vague comments — show the issue, suggest the fix
  ✗ Approve code you don't fully understand
  ✗ Nitpick style without style guide backing it
```

---

## 2. Readability — The Google Innovation

### 2.1 What is Readability?

Readability is Google's **certification process** for code quality. Every engineer
**must** get readability certification before they can submit code in a language.
It's not a test — it's a rite of passage.

> "Readability is about making sure that code is written in a way that is
> consistent, clear, and maintainable by anyone in the company, not just its
> original author." — Google Internal

### 2.2 The Readability Mindset

```
  Code is written once but read dozens of times.

  Every line you write is a commitment:
  - For the author: 1x effort to write
  - For each reader: 10x effort to understand
  - For the maintainer: 100x effort to change safely

  The economic case for readability:
  Optimize for the 100x, not the 1x.
```

### 2.3 Readability Principles

```
  Principle 1: Clarity over cleverness
    ❌ return (x & (x - 1)) == 0      // "trust me it works"
    ✅ return isPowerOfTwo(x)          // intention is obvious

  Principle 2: Active voice in comments
    ❌ // The list is iterated and each item is checked
    ✅ // Iterate the list, checking each item

  Principle 3: Comments explain WHY, not WHAT
    ❌ x += 1  // increment x by 1
    ✅ x += 1  // skip the sentinel row (row 0 is all-zeros)

  Principle 4: Function/Method does ONE thing
    ❌ processAndValidateAndNotify(input)
    ✅ validate(input) → process(input) → notify(result)

  Principle 5: Default to const/immutable
    ❌ let result = []; result.push(x)
    ✅ const result = items.map(transform)
```

### 2.4 Self-Review Before Sending

Before requesting review, do a **self-review**:

```bash
# 1. Read your own diff as if you didn't write it
diff --git a/file.js b/file.js

# 2. Run linter/fixer
npx eslint --fix src/

# 3. Run tests
npm test

# 4. Check for:
#    - Dead code (commented-out, unused imports, orphan functions)
#    - Debug leftovers (console.log, TODO without ticket)
#    - Magic numbers → named constants
#    - Long functions → split into helpers
```

---

## 3. Design Doc Review

### 3.1 When to Write a Design Doc

```
  Write a design doc when:
  ✅ New feature that takes > 3 days to implement
  ✅ Architecture change that affects other teams
  ✅ API that will be consumed by external services
  ✅ Database schema changes
  ✅ Performance-critical system changes

  Skip the doc when:
  ✅ Pure bug fix
  ✅ Trivial UI change (< 1 day)
  ✅ Configuration-only change
```

### 3.2 Design Doc Template (Google-Style)

```
  ┌─────────────────────────────────────────────────────────────┐
  │ Title: [Brief, descriptive]                                   │
  │ Author: [Name] · Date: [Date] · Status: [Draft|Review|Final]  │
  ├─────────────────────────────────────────────────────────────┤
  │ 1. Objective                                                 │
  │    What problem are we solving? What is the success metric?   │
  │                                                               │
  │ 2. Background & Context                                       │
  │    Why this problem exists. What prior art exists.            │
  │                                                               │
  │ 3. Requirements                                               │
  │    Functional + non-functional (latency, availability, cost)  │
  │                                                               │
  │ 4. Design Options (≥2)                                        │
  │    Option A: [Primary recommendation]                         │
  │    Option B: [Alternative approach]                           │
  │    Option C: [If applicable, "do nothing" baseline]           │
  │                                                               │
  │ 5. Trade-off Analysis                                          │
  │    Performance · Maintainability · Scalability · Cost · Risk  │
  │                                                               │
  │ 6. Detailed Design                                             │
  │    Architecture diagram · API spec · Data model · Flow        │
  │                                                               │
  │ 7. Alternative Approaches (and why they were rejected)        │
  │                                                               │
  │ 8. Cross-team Impact                                           │
  │    Teams that need to know + what they need to do             │
  │                                                               │
  │ 9. Rollout & Rollback Plan                                     │
  │    Canary · Monitoring gates · Rollback triggers              │
  │                                                               │
  │ 10. Open Questions                                             │
  │    Decisions still pending + who needs to make them           │
  └─────────────────────────────────────────────────────────────┘
```

### 3.3 The Review Process

```
  ┌────────────────────────────────────────────────────┐
  │  ① Author writes doc in Google Docs / Markdown      │
  │  ② Share with stakeholders (📅 48h review window)   │
  │  ③ Collect inline comments                          │
  │  ④ Resolve each comment (agree/reject/trade-off)    │
  │  ⑤ Update doc with resolutions                      │
  │  ⑥ LGTM from Architect + Tech Lead → Proceed        │
  │  ⑦ Archive decision: "Why we chose X over Y"        │
  └────────────────────────────────────────────────────┘
```

---

## 4. Testing Philosophy — Google's Approach

### 4.1 Why Google Invests Heavily in Testing

> "If you have tests, you're not afraid to change code. If you're not afraid
> to change code, you can refactor. If you can refactor, you keep quality high.
> If you keep quality high, you keep velocity high."

### 4.2 The Testing Trophy (not the Pyramid)

Google evolved from the **Testing Pyramid** to the **Testing Trophy**:

```
          ╱─────╲
         ╱  E2E  ╲         ← Few: 5-10 critical paths
        ╱─────────╲
       ╱           ╲
      ╱ Integration  ╲      ← More: system-level behavior
     ╱                 ╲
    ╱═══════════════════╲
   ╱  Contract Tests     ╲    ← Many: service-to-service contracts
  ╱═══════════════════════╲
 ╱     Unit Tests           ╲   ← Most: isolated logic testing
╱═════════════════════════════╲
```

### 4.3 Size Classification (Google Internal)

```
  ┌─────────┬────────────────┬───────────────────┬────────────────┐
  │         │   Small Test   │   Medium Test     │   Large Test   │
  ├─────────┼────────────────┼───────────────────┼────────────────┤
  │ Scope   │ Single func    │ Single service    │ Multi-service  │
  │ Speed   │ < 1ms          │ < 100ms           │ > 1s           │
  │ Network │ No             │ Localhost only    │ Real network   │
  │ Deps    │ None (mock)    │ Fake/stub deps    │ Real deps      │
  │ Flaky   │ Never          │ Rare              │ Possible       │
  │ Ratio   │ 80%            │ 15%               │ 5%             │
  └─────────┴────────────────┴───────────────────┴────────────────┘
```

### 4.4 Writing Meaningful Tests

```
  BAD test:
  test("adds numbers", () => {
    expect(add(2, 3)).toBe(5)      // Tests the happy path only
  })

  GOOD test:
  test("adds positive numbers correctly", () => {
    expect(add(2, 3)).toBe(5)
  })
  test("handles negative numbers", () => {
    expect(add(-2, 3)).toBe(1)
    expect(add(-2, -3)).toBe(-5)
  })
  test("handles zero", () => {
    expect(add(0, 0)).toBe(0)
    expect(add(5, 0)).toBe(5)
  })
  test("handles large numbers without overflow", () => {
    expect(add(Number.MAX_SAFE_INTEGER, 1)).toBe(Number.MAX_SAFE_INTEGER + 1n)
  })
```

### 4.5 What to Test — The "Bugs Are Not Equal" Rule

```
  Priority of what to test (from most to least important):

  🥇 Error handling paths (80% of production bugs are here)
  🥇 Boundary conditions (off-by-one, empty, null, overflow)
  🥈 Core business logic (the reason this code exists)
  🥈 Integration points (how modules talk to each other)
  🥉 Happy path (it's the least likely to break — still test, but don't obsess)
  🥉 Edge cases that require specific inputs (test only if impactful)
```

---

## 5. Blameless Postmortem Culture

### 5.1 Principle

> "The best way to prevent errors is to make it safe to talk about them."

At Google, postmortems are **blameless**. The goal is never to find who caused
the outage — it's to find what **systems** failed so they can be improved.

### 5.2 Postmortem Template

```
  ┌──────────────────────────────────────────────────────────────┐
  │ Title: [System] Outage on [Date] — Severity [S0/S1/S2]       │
  │                                                              │
  │ Summary: 1-2 sentences                                       │
  │ Duration: Start → End · Detection: Automated/Manual          │
  │ Impact: Users affected · Revenue/data loss · SLA breach      │
  │                                                              │
  │ Timeline:                                                     │
  │   [T-00] Event occurs                                        │
  │   [T+05] Alert fires                                         │
  │   [T+12] Engineer begins investigation                       │
  │   [T+23] Root cause identified                               │
  │   [T+35] Fix deployed (circuit breaker)                      │
  │   [T+52] Service restored                                    │
  │                                                              │
  │ Root Cause (not "who" — "what system allowed this"):         │
  │   Technical: ...                                             │
  │   Process: ...                                               │
  │   Systemic: ...                                              │
  │                                                              │
  │ Action Items:                                                │
  │   □ [P0] Immediate mitigation (done)                         │
  │   □ [P1] Code fix to prevent recurrence — Due: [Date]        │
  │   □ [P2] Monitoring/alerting improvement — Due: [Date]       │
  │   □ [P3] Documentation update — Due: [Date]                  │
  │                                                              │
  │ Lessons Learned:                                              │
  │   What went well: ...                                        │
  │   What went wrong: ...                                       │
  │   What we'll do differently: ...                             │
  │                                                              │
  │ Appendix: Links to dashboards, logs, changelists             │
  └──────────────────────────────────────────────────────────────┘
```

### 5.3 Postmortem Golden Rules

```
  1. No blame. Ever. Fix the system, not the person.
  2. Action items must have owners and due dates.
  3. Every postmortem gets reviewed at the next team retro.
  4. Track postmortem metrics: time-to-detect, time-to-mitigate, MTTR.
  5. Share postmortems broadly — someone else needs this knowledge.
```

---

## 6. Psychological Safety & Engineering Culture

### 6.1 The Foundation of All Excellence

Google's Project Aristotle (the "people analytics" team) found that **the #1
predictor of high-performing teams is psychological safety** — the belief that
you won't be punished for making mistakes, asking questions, or admitting you
don't know something.

```
  Without psychological safety:
  ❌ Engineers hide bugs until they blow up
  ❌ Nobody questions bad design decisions
  ❌ Junior engineers never learn
  ❌ "That's how we've always done it" becomes law

  With psychological safety:
  ✅ Engineers say "I broke production" and everyone helps fix
  ✅ Design docs get brutally honest critiques
  ✅ Questions are celebrated, not punished
  ✅ The best idea wins, regardless of seniority
```

### 6.2 Engineering Cultural Signals

| Signal | Toxic Culture | Healthy Culture |
|--------|---------------|-----------------|
| Code review comments | "This is wrong" | "Could this approach cause issues with X?" |
| Bug ownership | "Who wrote this?" | "How do we prevent this class of bug?" |
| New idea reception | "That won't work because..." | "Let's prototype and see" |
| On failure | "We need a process" | "What can we learn?" |
| Estimation | "You missed your deadline" | "What did we miss in our estimate?" |
| Technical debt | "Just make it work" | "Let's plan the fix" |

---

## 7. Engineering Productivity — The North Star

### 7.1 Google's Four-Quadrant Framework

Engineering productivity at Google is measured not by output (lines of code),
but by outcomes across four dimensions:

```
                ┌─────────────── High Quality ───────────────┐
                │                                             │
                │  High Quality  ≠  Slow Shipping             │
                │  Fast Shipping ≠  Low Quality               │
                │  The goal: High Quality + Fast Shipping     │
                │                                             │
                ├─────────────── Measured by ─────────────────┤
                │                                             │
                │ ① Code Quality: defect rate, rework rate    │
                │ ② System Health: availability, latency      │
                │ ③ Developer Satisfaction: "would you         │
                │    recommend our engineering culture?"       │
                │ ④ Business Impact: shipped features /        │
                │    engineering hour                          │
                └─────────────────────────────────────────────┘
```

### 7.2 Key Engineering Metrics to Track

```
  Lead Time for Change:     Code committed → production
  Deployment Frequency:     How often you ship
  Mean Time to Recover:     How fast you fix production issues
  Change Failure Rate:      % of deploys causing incidents

  Google's SRE DORA metrics benchmarks:
  ┌─────────────────┬──────────┬────────────┬──────────────┐
  │                 │ Elite    │ High        │ Low          │
  ├─────────────────┼──────────┼────────────┼──────────────┤
  │ Deploy freq     │ On-demand │ 1x/week    │ 1x/month     │
  │ Lead time       │ < 1 day  │ 1-7 days   │ 1-6 months   │
  │ MTTR            │ < 1 hour │ < 1 day    │ > 1 week     │
  │ Change fail rate│ 0-5%     │ 10-15%     │ > 30%        │
  └─────────────────┴──────────┴────────────┴──────────────┘
```

---

## 8. Golden Commandments

```
  ┌──── 10 Commandments of Google Engineering ────┐
  │                                                │
  │  1. Thou shalt not commit without review       │
  │  2. Thou shalt write tests before fixing bugs  │
  │  3. Thou shalt document thy design decisions   │
  │  4. Thou shalt not leave TODOs without owners  │
  │  5. Thou shalt postmortem every outage          │
  │  6. Thou shalt name things to reveal intent    │
  │  7. Thou shalt optimize for readability        │
  │  8. Thou shalt make it easy to do the right    │
  │     thing, hard to do the wrong thing          │
  │  9. Thou shalt question everything,            │
  │     including this list                        │
  │ 10. Thou shalt leave code better than          │
  │     you found it (Boy Scout Rule)              │
  └────────────────────────────────────────────────┘
```

---

## References

See the following files for deeper dives:

- `references/code-review-deep-dive.md` — Advanced code review patterns, security review checklist, multi-language conventions
- `references/testing-philosophy.md` — Test doubles taxonomy, mocking strategies, flaky test management
- `references/postmortem-examples.md` — Real postmortem templates and case studies
- `references/engineering-metrics.md` — DORA metrics, tracking dashboards, reporting templates

> **Core principle**: This skill represents the **top-level cultural framework**.
> Detailed implementation guidelines for specific practices (code review, testing,
> postmortems) are in repository `references/` files, loaded only when needed.
