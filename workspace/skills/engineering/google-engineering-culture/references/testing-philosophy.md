# Testing Philosophy — Deep Dive Reference

## 1. Google Test Double Taxonomy

Google maintains a strict distinction between test doubles. This isn't pedantry —
each type has a specific purpose and misuse leads to brittle tests.

```
  ┌────────────────────────────────────────────────────────────────┐
  │  Dummy     : Passed around but never used (filling parameter   │
  │              lists)                                            │
  │              Example: null, empty object                        │
  │                                                                │
  │  Fake       : Working implementation but with shortcuts that    │
  │              aren't suitable for production                     │
  │              Example: In-memory database, fake email sender     │
  │              ✅ PREFERRED — tests real logic through real code │
  │                                                                │
  │  Stub       : Provides pre-programmed answers to calls          │
  │              Example: getConfig() always returns {env: "test"} │
  │              ⚠️ Use sparingly — couples test to implementation │
  │                                                                │
  │  Mock       : Pre-programmed + verifies interactions            │
  │              Example: expect(sender.send).toHaveBeenCalled()   │
  │              ⚠️ Use only for external boundaries                │
  │              ❌ Avoid for internal objects — makes tests brittle│
  │                                                                │
  │  Spy        : Real object that records calls                   │
  │              Example: Console spy that captures log output     │
  │              ⚠️ Use for observability testing only              │
  └────────────────────────────────────────────────────────────────┘
```

### When to use what

```
  Internal domain logic        → Test with real code
  External service boundary    → Fake (in-memory implementation)
  Indeterministic behavior     → Stub (time, random, network)
  Cross-cutting concern         → Mock (logging, metrics, auth)
  NEVER mock what you don't own → ⛔ Use integration test instead
```

## 2. Testing Strategy by Layer

```
  ┌─────────────┬──────────────────────┬──────────────────────────┐
  │ Layer       │ Testing Approach     │ Key Techniques           │
  ├─────────────┼──────────────────────┼──────────────────────────┤
  │ API/Schema  │ Contract tests        │ OpenAPI spec validation  │
  │ Service     │ Integration tests     │ Fake dependencies        │
  │ Domain      │ Unit tests            │ Pure function testing    │
  │ Persistence │ Repository tests      │ In-memory/Testcontainers │
  │ UI          │ Component tests       │ Storybook + Playwright   │
  │ Workflow    │ E2E tests (few)       │ Critical paths only      │
  └─────────────┴──────────────────────┴──────────────────────────┘
```

## 3. Code Coverage: The Truth

Coverage is a **negative indicator** (low coverage = problem), not a positive one
(high coverage ≠ good tests).

```
  Coverage traps:
  ❌ Chasing 100% branch coverage
  ❌ Writing tests to satisfy coverage tool
  ❌ Ignoring uncovered error paths if "can't happen"
  ❌ Complex mocks that test the mock, not the code

  Coverage truths:
  ✅ 80-90% line coverage is a good baseline
  ✅ Focus on uncovered error handling (80% of bugs live here)
  ✅ Test the behavior, not the implementation
  ✅ Mutation testing is a better quality signal than coverage
```

## 4. Flaky Test Management

### Detection
```
  ┌─────────────────────────────────────────────────┐
  │ Flaky test = test that passes sometimes          │
  │                                                   │
  │ Signs:                                            │
  │   - CI fails randomly                             │
  │   - test passes locally but fails in CI           │
  │   - test passes when run alone but fails in batch │
  │   - test depends on timing (sleep, timeout)       │
  └─────────────────────────────────────────────────┘
```

### Fix Strategies (in order of preference)

```
  1. Remove shared mutable state (the #1 cause)
  2. Remove time dependencies (use deterministic clocks)
  3. Remove network dependencies (use fakes, not mocks)
  4. Remove ordering dependencies (independent test isolation)
  5. Add proper cleanup (teardown restores state)
  6. Remove the test entirely (flaky tests are worse than no tests)
```

### Google's Flaky Test Policy

```
  If a test is flaky:
  ╰→ File a bug saying "This test is flaky"
  ╰→ Auto-remove from CI within 2 weeks if not fixed
  ╰→ Teams are evaluated on: "flaky test count" not "total coverage"
  ╰→ Fixing flaky tests is higher priority than writing new ones
```

## 5. Test Naming Convention

```
  Bad:
  test("works")
  test("handles errors")
  test("add_to_cart")

  Good:
  test("addToCart increases cart total by item price")
  test("addToCart fails when item is out of stock")
  test("addToCart creates a new cart when user has no active cart")

  Google convention:
  test("MethodName_StateUnderTest_ExpectedBehavior")
  // Examples:
  test("addToCart_withZeroQuantity_throwsValidationError")
  test("validateEmail_withInvalidFormat_returnsFalse")
  test("computeDiscount_forLoyaltyMembers_appliesTieredRate")
```

## 6. Assertion Best Practices

```
  ✅ Assert on behavior, not implementation
  expect(result).toEqual({ id: 1, name: "test" })
  // This checks WHAT the function returns

  ❌ Assert on internal detail
  expect(result.createdAt).toBeDefined()
  // This checks HOW the function works, not what it does

  ✅ Use specific matchers
  expect(array).toHaveLength(3)
  expect(array).toContainEqual(expectedItem)

  ❌ Avoid generic matchers
  expect(array.length).toBeGreaterThan(0)  // Don't care about the value?
  expect(result).toBeTruthy()               // Too vague
```

## 7. Testing a PR: The Google Flow

```
  Step 1: Run tests locally
    $ npm test                     # Unit tests: should be instant
    $ npm run test:integration     # Integration: < 2 minutes
    $ npm run test:e2e             # E2E: > 5 minutes (run selectively)

  Step 2: Check test coverage diff
    $ npx jest --coverage
    # Coverage should not decrease. If it does, add missing tests.

  Step 3: Verify the test proves the fix
    # 1. Write the test first (it should fail without the fix)
    # 2. Apply the fix (test should pass)
    # 3. This proves your test actually verifies something

  Step 4: Add regression test
    # For every bug fix, add ONE test that covers the bug scenario.
    # This test prevents the exact same bug from recurring silently.
```

## 8. The Test Maintenance Budget

Google allocates **20% of every sprint** to test maintenance:
- Fix flaky tests
- Remove tests for deleted code
- Update tests for changed behavior
- Add missing tests for new uncovered paths

> "Tests are code. Tests have maintenance cost. Treat them as first-class
> citizens — they deserve the same quality as production code."
