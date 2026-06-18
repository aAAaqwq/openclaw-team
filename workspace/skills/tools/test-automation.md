# 测试自动化（增强版）

> 测试框架选型、并行执行、CI集成、Contract Testing、性能测试、模糊测试全部指南

## 测试框架选型

### 语言框架对比

| 语言 | 框架 | 特点 | 推荐场景 |
|------|------|------|----------|
| JavaScript/TS | Vitest | 最快 Vite原生 | 现代项目首选 |
| JavaScript/TS | Jest | 久经考验 | 遗留项目 |
| JavaScript/TS | Playwright | 浏览器自动化 | E2E/Component测试 |
| JavaScript/TS | MSW | Mock Service Worker | API Mock首选 |
| Python | pytest | 插件生态最强 | Python项目首选 |
| Go | testing | 标准库 | Go项目原生 |
| Rust | cargo test | 标准库 | Rust项目 |
| Java | JUnit 5 | 老牌经典 | Java项目 |

### 测试分层策略

```
  ┌──────────────────────────────────────────────────────────────┐
  │                   Testing Trophy (Recommended)                 │
  │                                                               │
  │  Unit (60%)       → Pure function, domain logic              │
  │  Contract (15%)   → Pact/OpenAPI — service boundaries        │
  │  Integration (20%) → Fake dependencies, real-ish data        │
  │  E2E (5%)          → Critical user journeys only             │
  └──────────────────────────────────────────────────────────────┘
```

---

## Contract Testing（新增！）

### 什么是Contract Testing？

Contract Testing验证 **服务间契约**：一个服务的API响应是否满足另一个服务的期望。

```
  Integration Test:
  Deploy everything → Hit real APIs → 45 min → Flaky
   
  Contract Test:
  Consumer writes expectation → Provider verifies against real code
  → 10 seconds → Deterministic
```

### Pact框架概览

| 组件 | 作用 |
|------|------|
| Consumer Test | 消费者定义API期望 |
| Pact文件 | 记录契约（JSON格式） |
| Pact Broker | 契约仓库+版本矩阵 |
| Provider Verification | 提供者验证所有契约 |
| Can-I-Deploy | 部署前安全检查 |

### 快速启动

```typescript
// Consumer test (payment-service testing order-service)
import { PactV3, MatchersV3 } from '@pact-foundation/pact';

const provider = new PactV3({
  consumer: 'payment-service',
  provider: 'order-service',
  port: 4000,
});

test('GET /orders/123 returns order with items', async () => {
  provider
    .uponReceiving('a request for order ID 123')
    .withRequest({ method: 'GET', path: '/orders/123' })
    .willRespondWith({
      status: 200,
      body: { 
        id: MatchersV3.like('123'), 
        status: MatchersV3.term({ generate: 'confirmed', matcher: '^(pending|confirmed)$' }),
      },
    });

  await provider.executeTest(async (mockServer) => {
    const result = await fetch(`${mockServer.url}/orders/123`);
    expect(result.status).toBe(200);
  });
});
```

### CI集成Contract Test

```yaml
# .github/workflows/contract-tests.yml
name: Consumer Contract Tests

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:contract  # Pact tests
      - name: Publish to Broker
        if: github.ref == 'refs/heads/main'
        run: npm run publish:pacts
        env:
          PACT_BROKER_URL: ${{ vars.PACT_BROKER_URL }}
```

> **完整Contract Testing指南**：见 `contract-testing` skill

---

## 性能测试（增强！）

### 性能测试类型

| 类型 | 目的 | 工具 |
|------|------|------|
| **Load Test** | 模拟预期负载 | k6, wrk, locust |
| **Stress Test** | 超出极限 | k6, Vegeta |
| **Endurance Test** | 长时间运行 | k6 (1h+) |
| **Spike Test** | 突发流量 | k6, locust |
| **Scalability Test** | 找到扩展曲线 | k6 (hpa调整) |

### k6快速入门

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '1m', target: 20 },     // Stay at 20
    { duration: '30s', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],    // 95% requests < 500ms
    http_req_failed: ['rate<0.01'],      // < 1% failure rate
  },
};

export default function () {
  const res = http.get('http://localhost:3000/api/health');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  sleep(1);
}
```

```bash
# Run k6 test
k6 run load-test.js
```

### CI集成性能测试

```yaml
test:performance:
  stage: test
  script:
    - k6 run load-test.js --out json=result.json
    - # Compare against baseline
    - node scripts/compare-perf.js result.json .perf-baseline.json
  artifacts:
    reports:
      performance: result.json
  only:
    - main
```

### 性能回归检测

```javascript
// scripts/compare-perf.js
const baseline = require('./.perf-baseline.json');
const current = require('./result.json');

const DEGRADATION_THRESHOLD = 0.10; // 10% degradation allowed

const currentP95 = current.metrics.http_req_duration.values['p(95)'];
const baselineP95 = baseline.metrics.http_req_duration.values['p(95)'];

const degradation = (currentP95 - baselineP95) / baselineP95;

if (degradation > DEGRADATION_THRESHOLD) {
  console.error(`❌ Performance regression: p95 ${baselineP95}ms → ${currentP95}ms`);
  process.exit(1);
}

console.log(`✅ Performance OK: p95 ${currentP95}ms vs baseline ${baselineP95}ms`);
new Baseline(current).save();
```

---

## 模糊测试 / Fuzz Testing（新增！）

### 什么是Fuzz Testing？

Fuzz Testing自动生成**随机/半随机输入**来测试程序，发现边界条件、安全漏洞和崩溃路径。

```
  Manual test:            f(-1)  is tested
  Fuzz test:             f(18446744073709551615) crashes!
  Fuzz test result:      Integer overflow → buffer overflow → security hole
```

### JavaScript/TypeScript (Jazzer.js)

```javascript
// fuzz/parse-user.test.js
import { fuzz } from '@jazzer.js/core';

describe('User Parser Fuzz Test', () => {
  it('should never crash on any JSON input', async () => {
    await fuzz(async (data) => {
      // This will be called 10,000s of times with random data
      const input = Buffer.from(data).toString('utf-8');
      
      // Wrap in try-catch — crashes are failures
      try {
        const result = parseUserJson(input);
        if (result !== null) {
          // If parsing succeeds, verify invariants
          expect(result.id).toBeDefined();
          expect(result.email).toMatch(/@/);
        }
      } catch (e) {
        // Expected errors (e.g., JSON parse error) are OK
        // Crashing with null pointer / memory error is NOT
        expect(e).toBeInstanceOf(ValidationError);
      }
    });
  });
});
```

### Python (Atheris)

```python
# fuzz/test_parse_user.py
import atheris

def TestOneInput(data):
    try:
        result = parse_user_json(data)
        if result:
            assert result.id > 0
            assert '@' in result.email
    except (ValueError, ValidationError):
        pass  # Expected
    except Exception as e:
        raise  # Unexpected — fuzz failed!

atheris.Setup([], TestOneInput)
atheris.Fuzz()
```

### Go Fuzz Testing (go-fuzz / native)

```go
// fuzz_test.go
package parser

import (
    "testing"
    "testing/fstest"
)

func FuzzParseUser(f *testing.F) {
    // Seed corpus (valid examples)
    f.Add([]byte(`{"id": 1, "email": "test@example.com"}`))
    
    f.Fuzz(func(t *testing.T, data []byte) {
        result, err := ParseUserJSON(data)
        
        if err != nil {
            // Error is OK, but must be a ValidationError, not a panic
            if _, ok := err.(*ValidationError); !ok {
                t.Errorf("unexpected error type: %v", err)
            }
            return
        }
        
        // If parsing succeeds, check invariants
        if result.ID <= 0 {
            t.Errorf("id must be positive, got %d", result.ID)
        }
        if !strings.Contains(result.Email, "@") {
            t.Errorf("email must contain @, got %s", result.Email)
        }
    })
}
```

```bash
# Go native fuzz (Go 1.18+)
go test -fuzz=. -fuzztime=30s ./parser/
```

### Fuzz Testing CI集成

```yaml
# .github/workflows/fuzz.yml
name: Fuzz Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Nightly fuzz
  workflow_dispatch:       # Manual trigger

jobs:
  fuzz:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v4
      
      - name: Run Go Fuzz (30 mins)
        run: |
          go test -fuzz=. -fuzztime=30m ./...
      
      - name: Run Jazzer.js Fuzz
        run: |
          npx jazzer fuzz/*.test.ts --fuzzTime=600
      
      - name: Upload crash reports
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: fuzz-crashes
          path: testdata/fuzz/
```

### Fuzz Testing覆盖优先级

```
  Priority 1: Input parsing (JSON, XML, protobuf)
  Priority 2: Network protocol handling
  Priority 3: Cryptographic/security functions
  Priority 4: File format parsing
  Priority 5: String manipulation / encoding
  
  Fuzz one module per CI run. Rotate daily.
```

---

## 并行测试执行

### 并行策略
```python
# pytest并行（pytest-xdist）
pytest -n auto

# 按模块分组并行
pytest -n 4 --dist loadgroup
```

```json
// Jest / Vitest并行
{
  "maxWorkers": "50%",
  "maxConcurrency": 5
}
```

### 并行执行问题解决
| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 数据库冲突 | 多个测试写同表 | 测试级数据库/Docker隔离 |
| 文件竞争 | 多个测试读写同文件 | 临时目录隔离（tempfile） |
| 端口冲突 | Mock服务端口被占 | 随机端口分配 |
| 共享状态 | 全局/静态变量污染 | 每个测试初始化/teardown |

## CI集成（增强版）

### 完整CI测试流水线

```yaml
name: Full Test Suite

on: [push, pull_request]

jobs:
  # 阶段1：快速反馈（< 2min）
  quick-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npm run test:unit -- --coverage
      - name: Mutation Testing (critical modules)
        run: npx stryker run --thresholds.break=60
        continue-on-error: true  # Don't block, just warn
  
  # 阶段2：服务验证（< 5min）
  service-tests:
    needs: quick-checks
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:integration
      - name: Contract Tests (Pact)
        run: npm run test:contract
      - run: npm run test:performance -- --baseline .perf-baseline.json
  
  # 阶段3：全量验证（< 15min）
  full-suite:
    needs: service-tests
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:e2e
      - run: npm run test:allure
```

### 构建时间目标

```
  ┌─────────────┬──────────────┬────────────────┐
  │ Stage       │ Target Time  │ Action if Exceed │
  ├─────────────┼──────────────┼─────────────────┤
  │ Quick       │ < 2 min     │ Add test slicing │
  │ Service     │ < 5 min     │ Parallelize      │
  │ Full        │ < 15 min    │ Reduce E2Es      │
  │ Fuzz        │ < 30 min    │ Nightly only     │
  └─────────────┴──────────────┴─────────────────┘
```

## 测试自动化Checklist（增强版）

- [ ] 框架选型确认
- [ ] 单元/Contract/集成/E2E分层
- [ ] Test Double规范（Fake/Stub/Mock/Dummy明确区分）
- [ ] Mutation Testing配置（目标>60%）
- [ ] Contract Testing框架选型（Pact/OpenAPI）
- [ ] Pact Broker部署
- [ ] Contract CI集成（Consumer + Provider）
- [ ] Can-I-Deploy gate
- [ ] 性能测试基线（k6脚本）
- [ ] CI性能回归检测
- [ ] Fuzz Testing配置（核心模块）
- [ ] Fuzz CI集成（nightly cron）
- [ ] 并行执行配置
- [ ] 报告生成配置（Allure/JUnit）
- [ ] 覆盖率门槛（≥ 80%）
- [ ] flaky测试自动标记+追踪
- [ ] 测试环境隔离
- [ ] CI时间 < 目标值
