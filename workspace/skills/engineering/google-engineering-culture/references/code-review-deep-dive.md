# Code Review — Deep Dive Reference

## 1. Security Review Checklist (Every PR)

```
□ SQL Injection: No raw string concatenation in queries. Use parameterized.
□ XSS: All user input is sanitized before rendering.
□ CSRF: State-changing requests require CSRF token.
□ Authz: Every endpoint checks authorization (not just authentication).
□ Rate Limit: API endpoints have reasonable rate limits.
□ Secrets: No API keys, passwords, tokens hardcoded.
□ Logging: No sensitive data (PII) logged.
□ Dependency: No new deps without security audit.
□ Data Exposure: API responses return only necessary fields.
□ File Upload: File type/size validation, no arbitrary path writes.
```

## 2. Performance Front-Burners

```
□ N+1 Queries: Check loops making individual DB calls.
□ Large Payloads: Pagination, field selection, compression.
□ Unbounded Growth: Arrays/lists/maps without size limits.
□ Expensive Loops: O(n²) or O(n*m) in hot paths.
□ Sync Blocking: DB/network calls inside request thread (Node.js).
□ Memory Leaks: Event listeners, closures, global caches.
□ Object Allocation: Hot-path object/closure allocation (GC pressure).
□ String Operations: Repeated string concatenation in hot loops.
```

## 3. Multi-Language Conventions

### Python (Google Style)
```
- PEP 8 enforced via pylint/flake8
- Type annotations required for all public APIs
- Docstrings: Google-style (not numpy, not reStructuredText)
- Exception handling: Prefer EAFP (Easier to Ask Forgiveness than Permission)
- Import order: standard lib → third-party → local (alphabetical groups)
```

### TypeScript/JavaScript
```
- ESLint + Prettier — consistency is non-negotiable
- `const` by default, `let` when reassignment needed, `var` banned
- Null vs undefined: Prefer undefined, use null only for explicit "no value"
- Async: Prefer async/await, ban raw promise chains
- Error types: Custom error classes, never `throw string`
```

### Go
```
- gofmt enforced (no style discussions allowed in reviews)
- Error handling: Always check errors, wrap with context
- Interface: Accept interfaces, return structs
- Concurrency: Document goroutine lifecycle + ownership
- No `init()` functions unless absolutely necessary
```

## 4. Common Anti-Patterns to Flag

| Anti-pattern | Signal | Fix |
|-------------|--------|-----|
| **God Object** | One class does everything | Split by responsibility |
| **Shotgun Surgery** | One change touches many files | Cohesion boundary violated |
| **Speculative Generality** | "We might need this later" YAGNI | Remove unused abstraction |
| **Copy-Paste Inheritance** | Duplicate code blocks | Extract to shared function |
| **Feature Envy** | Method uses another class's data more than its own | Move method to correct class |
| **Message Chain** | a.getB().getC().doD() | Demeter's Law violation |
| **Primitive Obsession** | Using strings for domain concepts | Value objects/money types |
| **Temporal Coupling** | Methods must be called in specific order | Builder pattern or state machine |

## 5. Code Review Ownership Model

```
Author responsibilities:
  ✓ Self-review before requesting
  ✓ Respond to all comments within 24h
  ✓ Explain design decisions clearly
  ✓ Keep PR small (< 400 lines preferred)

Reviewer responsibilities:
  ✓ Review within 24 hours of request
  ✓ Be specific: "Line 42: What if items is empty?"
  ✓ Distinguish blocking vs non-blocking
  ✓ Approve once all blocking issues resolved

Tech Lead responsibilities:
  ✓ Ensures design alignment
  ✓ Stops bad patterns from spreading
  ✓ Teaches through review comments
  ✓ Blocker resolution (design disagreements)
```

## 6. Speed Reading a Diff

1. **Read the description first** — this is the author's contract about intent
2. **Check the test file second** — tests reveal the expected behavior better than implementation
3. **Read the implementation third** — now you know what to look for
4. **Review the configuration last** — env vars, intents, settings are often forgotten

> "A reviewer who reads tests before implementation is 2x more effective at catching logic errors." — Google Internal Study
