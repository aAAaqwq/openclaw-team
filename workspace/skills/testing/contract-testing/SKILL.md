---
name: contract-testing
description: >
  Consumer-Driven Contract Testing (CDC) using Pact framework and OpenAPI-based
  contract validation. Covers microservice-to-microservice contract verification,
  provider contract testing, consumer contract testing, contract publishing
  pipelines, and contract breaking-change detection.

  USE WHEN: designing microservice APIs, establishing service boundaries,
  verifying service-to-service contract compatibility, integrating with Pact
  framework, preventing contract-breaking changes, or setting up a contract
  testing pipeline in CI/CD. Triggers on "contract test", "Pact", "consumer-
  driven contract", "CDC", "service contract", "API contract", "breaking change".
---

# Contract Testing (Consumer-Driven Contracts)

> **Source**: Pact framework + Martin Fowler + real-world microservice architectures
> at Google, ThoughtWorks, and ByteDance
> **Core Philosophy**: Integration tests are slow and brittle. Contract tests
> are fast, isolated, and the only practical way to verify microservice
> compatibility without deploying everything.

## Why Contract Testing Matters

```
  Without contract tests:
  ❌ Services A and B pass all unit tests but fail together on Sunday night
  ❌ "It worked in staging!" — because staging has different data/config
  ❌ Integration test suites take 45+ minutes and flake constantly
  ❌ API changes break consumers who were "supposed to be notified"

  With contract tests:
  ✅ Each service is verified independently against its contracts
  ✅ Providers know exactly who depends on what
  ✅ CI fails in 30 seconds, not 45 minutes
  ✅ Breaking changes are caught before deployment, not after
```

## Core Concepts

### Three Roles

```
  ┌──────────────────────────────────────────────────────────────┐
  │                                                               │
  │  Consumer: The service that calls an API                     │
  │    → Writes contract tests that document its expectations    │
  │    → "I expect POST /orders to return 201 with order ID"    │
  │                                                               │
  │  Provider: The service that serves the API                   │
  │    → Verifies that it satisfies all consumer contracts       │
  │    → "Can I still satisfy all my consumers after this change?"│
  │                                                               │
  │  Broker: The central repository of contracts                 │
  │    → Stores all pacts from all consumers                     │
  │    → Enables can-i-deploy checks                             │
  │    → Shows dependency graph between services                 │
  │                                                               │
  └──────────────────────────────────────────────────────────────┘
```

### The Contract Testing Flow

```
  Consumer writes test
  ┌──────────┐     ┌──────────┐
  │ Consumer │────→│  Pact   │  Consumer defines expectations
  │ Service  │     │  File   │  (what it expects from the API)
  └──────────┘     └──────────┘
                        │
                        ▼
                   ┌──────────┐
                   │  Broker  │  Pact file is published to broker
                   └──────────┘
                        │
                        ▼
                   ┌──────────┐  Provider downloads ALL consumer pacts
                   │ Provider │  and verifies each one against its
                   │ Service  │  actual implementation
                   └──────────┘
                        │
                        ▼
                   ✅ All contracts pass → Safe to deploy
                   ❌ Any contract fails  → Must fix before deploy
```

---

## 1. Consumer Test (Pact — JavaScript/TypeScript)

### 1.1 Setup

```bash
npm install --save-dev @pact-foundation/pact @pact-foundation/pact-core
```

### 1.2 Writing Consumer Tests

```typescript
// test/contract/order-service.pact.test.ts
import { PactV3, MatchersV3 } from '@pact-foundation/pact';
import { OrderApiClient } from '../src/clients/order-service';

const { like, eachLike, term, iso8601DateTime } = MatchersV3;

describe('Order Service Pact', () => {
  const provider = new PactV3({
    consumer: 'payment-service',      // Who you are
    provider: 'order-service',        // Who you're calling
    port: 4000,                       // Mock server port
  });

  describe('GET /orders/{id}', () => {
    it('returns order details for valid id', async () => {
      // Arrange: define what the provider should respond with
      provider
        .uponReceiving('a request for order ID 123')
        .withRequest({
          method: 'GET',
          path: '/orders/123',
          headers: { Accept: 'application/json' },
        })
        .willRespondWith({
          status: 200,
          headers: { 'Content-Type': 'application/json' },
          body: {
            id: like('123'),
            status: term({ generate: 'confirmed', matcher: '^(pending|confirmed|shipped)$' }),
            items: eachLike({
              productId: like('p001'),
              quantity: like(2),
              price: like(29.99),
            }),
            createdAt: iso8601DateTime(),
          },
        });

      // Act: run the interaction through the mock provider
      await provider.executeTest(async (mockServer) => {
        // Point your real client to the mock server
        const client = new OrderApiClient(mockServer.url);
        const result = await client.getOrder('123');

        // Assert: verify the client parses the response correctly
        expect(result.id).toBe('123');
        expect(result.status).toMatch(/^(pending|confirmed|shipped)$/);
        expect(result.items.length).toBeGreaterThanOrEqual(0);
      });
    });
  });

  describe('POST /orders', () => {
    it('creates an order successfully', async () => {
      provider
        .uponReceiving('a request to create an order')
        .withRequest({
          method: 'POST',
          path: '/orders',
          headers: { 
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
          body: {
            customerId: like('c001'),
            items: eachLike({ productId: like('p001'), quantity: like(1) }),
          },
        })
        .willRespondWith({
          status: 201,
          headers: { 'Content-Type': 'application/json' },
          body: {
            id: like('new-order-id'),
            status: term({ generate: 'pending', matcher: '^(pending|confirmed)$' }),
          },
        });

      await provider.executeTest(async (mockServer) => {
        const client = new OrderApiClient(mockServer.url);
        const result = await client.createOrder({
          customerId: 'c001',
          items: [{ productId: 'p001', quantity: 1 }],
        });

        expect(result.id).toBeDefined();
        expect(result.status).toBe('pending');
      });
    });
  });
});
```

### 1.3 Publishing Contract to Pact Broker

```typescript
// scripts/publish-pacts.ts
import { Publisher } from '@pact-foundation/pact';

const publisher = new Publisher({
  pactBrokerUrl: process.env.PACT_BROKER_URL || 'https://pact-broker.example.com',
  pactBrokerToken: process.env.PACT_BROKER_TOKEN,
  consumerVersion: process.env.GIT_COMMIT || '1.0.0',
  pactFilesOrDirs: ['./pacts/'],
});

publisher.publishPacts().then(() => console.log('Contracts published'));
```

```yaml
# .github/workflows/publish-contracts.yml (consumer side)
name: Publish Consumer Contracts

on: push

jobs:
  test-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run test:contract  # Runs pact tests, generates pact files
      
      - name: Publish pacts to broker
        env:
          PACT_BROKER_URL: ${{ vars.PACT_BROKER_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
          GIT_COMMIT: ${{ github.sha }}
        run: npx ts-node scripts/publish-pacts.ts
```

---

## 2. Provider Verification (JavaScript/TypeScript)

### 2.1 Setup Provider Verification

```typescript
// test/contract/order-service-verification.test.ts
import { Verifier } from '@pact-foundation/pact';
import { startServer, stopServer } from '../src/server';

describe('Order Service — Pact Provider Verification', () => {
  beforeAll(async () => {
    await startServer(4001);  // Start real service on test port
  });

  afterAll(async () => {
    await stopServer();
  });

  it('satisfies all consumer contracts', async () => {
    const opts = {
      provider: 'order-service',
      providerBaseUrl: 'http://localhost:4001',
      
      // Option A: Verify against broker (preferred)
      pactBrokerUrl: process.env.PACT_BROKER_URL || 'https://pact-broker.example.com',
      pactBrokerToken: process.env.PACT_BROKER_TOKEN,
      
      // Option B: Verify against local pact files (for dev)
      // pactUrls: [path.resolve(__dirname, '../../pacts/payment-service-order-service.json')],

      // Provider states (setup data for test scenarios)
      stateHandlers: {
        'order 123 exists': async () => {
          // Seed database with order ID 123
          await seedOrder({ id: '123', status: 'confirmed' });
        },
        'no orders exist': async () => {
          // Clear the orders table
          await clearOrders();
        },
      },
      
      // Custom verifications beyond default
      requestFilter: (req, res, next) => {
        // Add any custom headers needed
        req.headers['x-request-id'] = 'pact-test';
        next();
      },
    };

    await new Verifier(opts).verifyProvider();
  });
});
```

### 2.2 CI Integration (Provider Side)

```yaml
# .github/workflows/verify-contracts.yml (provider side)
name: Verify Consumer Contracts

on:
  push:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours — catch new contracts from consumers

jobs:
  verify:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:provider-verification
        env:
          PACT_BROKER_URL: ${{ vars.PACT_BROKER_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
          DB_URL: postgres://postgres:test@localhost:5432/test
```

---

## 3. Can-I-Deploy — The Safety Gate

### 3.1 What is Can-I-Deploy?

The broker tracks **which consumer versions** have been verified against **which provider versions**. Can-I-Deploy checks this matrix:

```bash
# Before deploying a new provider version:
pact-broker can-i-deploy \
  --pacticipant order-service \
  --version $(git rev-parse HEAD) \
  --to-environment production

# Before deploying a new consumer version:
pact-broker can-i-deploy \
  --pacticipant payment-service \
  --version $(git rev-parse HEAD) \
  --to-environment production
```

### 3.2 The Matrix

```
                              Provider: order-service
                    ┌────────────────────────────────────┐
                    │  v1.0 │  v1.1 │  v2.0 (proposed)  │
  ┌─────────────────┼───────┼───────┼───────────────────┤
  │ payment v2.1    │ ✅    │ ✅    │ ❌                 │
  │ notification v1.0 │ ✅  │ ❌    │ ❌                 │
  │ analytics v3.0  │ ✅    │ ⚠️    │ ✅                 │
  └─────────────────┴───────┴───────┴───────────────────┘

Result: payment v2.1 is NOT verified against order v2.0
→ Block deployment until contract is resolved
```

### 3.3 GitLab CI / GitHub Actions Gate

```yaml
# Add to deployment workflow
deploy:
  stage: deploy
  script:
    - pact-broker can-i-deploy
      --pacticipant order-service
      --version $CI_COMMIT_SHA
      --to-environment production
    - ./deploy.sh
  only:
    - main
```

---

## 4. Contract Testing in Python

### 4.1 Consumer Test (Pact-Python)

```python
# tests/contract/test_order_consumer.py
import atexit
from pact import Consumer, Provider

pact = Consumer('payment-service').has_pact_with(
    Provider('order-service'),
    host_name='localhost',
    port=4000,
    pact_dir='./pacts'
)
pact.start_service()
atexit.register(pact.stop_service)

def test_get_order():
    expected = {
        'id': '123',
        'status': 'confirmed',
        'items': [
            {'product_id': 'p001', 'quantity': 2, 'price': 29.99}
        ]
    }

    (pact
     .given('order 123 exists')
     .upon_receiving('a request for order 123')
     .with_request('GET', '/orders/123')
     .will_respond_with(200, body=expected))

    with pact:
        client = OrderClient(f'http://localhost:{pact.port}')
        result = client.get_order('123')

    assert result['id'] == '123'
```

### 4.2 Provider Verification (Python)

```python
# tests/contract/test_order_provider.py
from pact import Verifier

def test_verify_consumer_contracts():
    verifier = Verifier(
        provider='order-service',
        provider_base_url='http://localhost:4001',
    )

    result = verifier.verify_with_broker(
        broker_url='https://pact-broker.example.com',
        broker_token='token-here',
        publish_version='1.0.0',
        publish_verification_results=True,
        provider_states_setup_url='http://localhost:4001/_pact/provider-states',
    )

    assert result == 0, "Contract verification failed!"
```

---

## 5. Contract Testing Without Pact (OpenAPI / Spring Cloud Contract)

### 5.1 OpenAPI-Based Contract Validation

For simpler cases where full CDC is overkill:

```typescript
// test/contract/openapi-contract-test.ts
import { validate } from 'openapi-validator-middleware';
import { spec } from '../../openapi/spec.yaml';

describe('API Contract Validation', () => {
  it('GET /orders/:id response matches OpenAPI spec', async () => {
    const response = await apiClient.getOrder('test-123');
    
    // Validate response shape against OpenAPI schema
    const result = validate.response(spec, '/orders/{id}', 'get', response);
    
    expect(result.valid).toBe(true);
    if (!result.valid) {
      console.error('Contract violations:', result.errors);
    }
  });
});
```

### 5.2 Schema-Based Contract (JSON Schema)

```typescript
import Ajv from 'ajv';

const ajv = new Ajv();

const orderSchema = {
  type: 'object',
  required: ['id', 'status', 'items', 'createdAt'],
  properties: {
    id: { type: 'string', pattern: '^[a-z0-9-]+$' },
    status: { type: 'string', enum: ['pending', 'confirmed', 'shipped'] },
    items: {
      type: 'array',
      items: {
        type: 'object',
        required: ['productId', 'quantity'],
        properties: {
          productId: { type: 'string' },
          quantity: { type: 'integer', minimum: 1 },
          price: { type: 'number' },
        },
      },
    },
    createdAt: { type: 'string', format: 'date-time' },
  },
};

test('GET /orders/:id returns valid JSON Schema', async () => {
  const response = await fetch('/orders/123').then(r => r.json());
  const validate = ajv.compile(orderSchema);
  const valid = validate(response);
  
  expect(valid).toBe(true);
  if (!valid) console.error(validate.errors);
});
```

---

## 6. Contract Testing CI Pipeline

### Full Pipeline

```
                        ┌──────────────────────────┐
                        │     Developer pushes      │
                        │     code change           │
                        └──────────┬───────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │ Consumer Service Push        │
                    │ ┌──────────────────────────┐│
                    │ │ 1. Unit/Integration      ││
                    │ │ 2. Consumer Pact tests   ││
                    │ │ 3. Publish pacts         ││
                    │ │ 4. ✅ → Mark commit      ││
                    │ │    as "pact published"   ││
                    │ └──────────────────────────┘│
                    └──────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │ Provider Service Push        │
                    │ ┌──────────────────────────┐│
                    │ │ 1. Unit/Integration      ││
                    │ │ 2. Download consumer     ││
                    │ │    pacts from broker     ││
                    │ │ 3. Verify all contracts  ││
                    │ │ 4. ❌ → Fix breaking     ││
                    │ │    change                ││
                    │ │ 5. ✅ → Deploy           ││
                    │ └──────────────────────────┘│
                    └──────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │ Deployment Gate              │
                    │ ┌──────────────────────────┐│
                    │ │ pact-broker can-i-deploy ││
                    │ │ ✅ → Deploy to staging   ││
                    │ │ ❌ → Block & notify      ││
                    │ └──────────────────────────┘│
                    └──────────────────────────────┘
```

---

## 7. Contract Testing Best Practices

```
  DO:
  ✓ Test realistic data shapes (use matchers for flexible fields)
  ✓ Keep pact files version-controlled
  ✓ Verify provider contracts in CI on every push
  ✓ Use Pact Broker's webhooks to trigger provider verification
  ✓ Add can-i-deploy to deployment pipeline

  DON'T:
  ✗ Test exhaustive responses — test the contract shape, not all data
  ✗ Forget to manage provider states — they are essential for meaningful testing
  ✗ Hardcode exact values unless they're contractually required
  ✗ Use contract tests for performance or load testing
  ✗ Let contract tests replace unit/integration tests — they are complementary
```

## 8. Contract Testing vs Integration Testing

```
  ┌─────────────────────┬─────────────────────┬─────────────────┐
  │ Aspect              │ Contract Test       │ Integration     │
  ├─────────────────────┼─────────────────────┼─────────────────┤
  │ Speed               │ ~100ms per pact     │ 5-60 min        │
  │ Isolation           │ Full (mock provider)│ Partial (real)  │
  │ Network required    │ No                  │ Yes             │
  │ Real data           │ No                  │ Yes             │
  │ Deployment blocking │ Yes (with broker)   │ No              │
  │ Flaky?              │ Rarely              │ Often           │
  │ Best for            │ API compatibility   │ Behavior & perf │
  └─────────────────────┴─────────────────────┴─────────────────┘
```

---

## References

See `references/pact-patterns.md` for advanced Pact patterns (webhooks, multi-provider verification, version compatibility strategies).
