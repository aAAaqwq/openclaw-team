# Pact Patterns — Advanced Reference

## 1. Webhooks for Automatic Provider Verification

Configure the Pact Broker to trigger provider CI when contracts change:

```yaml
# .pact-broker/webhooks.yml
webhooks:
  - description: "Verify order-service when any consumer pact changes"
    events:
      - "contract_content_changed"
    request:
      method: POST
      url: "https://github.com/api/v3/repos/team/order-service/dispatches"
      headers:
        Authorization: "token {{ORDER_SERVICE_GITHUB_TOKEN}}"
        Content-Type: "application/json"
      body:
        event_type: "pact_changed"
        client_payload:
          consumer: "${pactbroker.consumerName}"
          version: "${pactbroker.consumerVersionNumber}"
```

## 2. Pending Pacts (Safe Evolution)

When a new consumer is added, contracts start as "pending" — they don't block
the provider's deployment. This enables gradual adoption:

```bash
# Broker config for pending pacts
pact-broker create-environment \
  --name provider-verification \
  --pending true
```

## 3. Multi-Provider Verification

When one consumer calls multiple providers:

```typescript
// Consumer test that verifies against multiple providers
describe('Payment Service — Multi-Provider Verification', () => {
  it('verifies against all providers', async () => {
    const verifier = new Verifier({
      provider: 'payment-service',  // This is the CONSUMER!
      pactBrokerUrl: PACT_BROKER_URL,
      
      // Verify all pacts where payment-service is the consumer
      consumerVersionTags: ['main'],
      
      // Custom states for each provider
      stateHandlers: {
        'user has valid account': async () => { /* ... */ },
        'payment gateway is available': async () => { /* ... */ },
      },
    });

    // This verifies ALL contracts that payment-service depends on
    await verifier.verifyProvider();
  });
});
```

## 4. Version Compatibility Strategy

```
  ┌──────────────────────────────────────────────────────────┐
  │ Version Matrix Strategy                                   │
  │                                                           │
  │ Consumer v1.1 is verified → Provider v2.1                │
  │ Consumer v1.0 is verified → Provider v1.0, v2.0          │
  │                                                           │
  │ ✅ Provider can safely deploy v2.1                        │
  │    (consumer v1.1 verified, consumer v1.0 is also valid) │
  │                                                           │
  │ ❌ Provider v2.0 has breaking change                      │
  │    → Must wait until all consumers upgrade                │
  │    → Or: maintain backward compatibility                 │
  └──────────────────────────────────────────────────────────┘
```

## 5. Handling Breaking Changes

```
  Step 1: Check contract matrix
  pact-broker can-i-deploy --pacticipant order-service --version 2.0
  
  Step 2: Identify affected consumers
  ┌────────────┬────────┬──────────┐
  │ Consumer   │ Status │ Upgrade  │
  ├────────────┼────────┼──────────┤
  │ payment    │ ❌     │ Blocked  │
  │ analytics  │ ✅     │ Ready    │
  └────────────┴────────┴──────────┘
  
  Step 3: Coordinate
  → Schedule consumer upgrade before provider deploy
  → Or: Support both API versions during migration
  
  Step 4: After all consumers upgrade
  pact-broker record-deployment \
    --pacticipant order-service \
    --version 2.0 \
    --environment production
```

## 6. Contract Test Quality Checklist

```
□ Represents realistic request/response shapes
□ Covers happy path + at least one error path
□ Uses matchers for flexible fields (dates, IDs)
□ Provider states are meaningful and reproducible
□ Consumer client handles responses correctly
□ Published to shared broker
□ Can-I-Deploy gate is implemented in CI/CD
□ Provider verifies contracts on every build
□ Breaking changes trigger automatic notification to consumers
□ Webhook triggers provider verification on contract change
```
