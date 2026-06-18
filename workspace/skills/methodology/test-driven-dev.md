# TDD — 测试驱动开发 (增强版)

Red-Green-Refactor周期、Test Doubles规范、Mutation Testing与Google级测试实践。

## Red-Green-Refactor周期

### 核心流程
```
1. RED：写一个会失败的测试（先定义行为）
2. GREEN：用最简代码让测试通过（不追求优雅）
3. REFACTOR：重构代码，保持测试绿色
4. 重复 → 直到所有功能完成
```

### 每一步的具体操作
```python
# RED — 写测试
def test_calculate_discount_with_vip():
    order = Order(total=100, customer_type="vip")
    discount = order.calculate_discount()
    assert discount == 20  # VIP打8折

# GREEN — 最简实现
class Order:
    def calculate_discount(self):
        if self.customer_type == "vip":
            return self.total * 0.2
        return 0  # 只让测试通过

# REFACTOR — 优化结构
class Order:
    def calculate_discount(self):
        rate = DISCOUNT_RATES.get(self.customer_type, 1.0)
        return self.total * rate
```

### 节奏控制
```
- 每个RED-GREEN-REFACTOR周期 ≤ 5分钟
- 测试失败时 → 只做让测试通过的最小改动
- 所有测试通过后 → 才有权限重构
- 重构后 → 确认所有测试仍然绿色
```

## Test Doubles 规范（增强）

### Google Test Double 分类法（严格区分）

| 类型 | 定义 | 示例 | 何时使用 |
|------|------|------|----------|
| **Dummy** | 传参但从未使用 | `null`, `empty string`, 占位对象 | 填充参数列表 |
| **Fake** | 功能简化版实现 | 内存数据库、假邮件发送器 | **内部依赖首选**——跑真实逻辑 |
| **Stub** | 返回预设值 | `getConfig()` → `{ env: "test" }` | 不确定行为（时间、随机数） |
| **Mock** | 预设值+验证交互 | `expect(email.send).toHaveBeenCalled()` | **仅用于外部边界**（跨服务调用、发送通知） |
| **Spy** | 真实对象+记录调用 | 监控日志输出 | 仅用于可观测性测试 |

### 选择策略

```
  Internal domain logic    → Test with real code (no double needed)
  External service boundary → Fake (in-memory implementation)
  Indeterministic behavior → Stub (time, random, network)
  Cross-cutting concern     → Mock ONLY at external boundaries
  NEVER mock what you don't own → ⛔ Use integration test instead
```

### Bad Mock vs Good Fake

```python
# ❌ BAD: Mocking internal domain logic
def test_order_total():
    order = Mock()
    order.items = []
    order.calculate_total()
    # This tests NOTHING meaningful
    # It only proves you can call a method

# ✅ GOOD: Testing real domain logic
def test_order_empty_total():
    order = Order(items=[])
    assert order.calculate_total() == 0

def test_order_with_items_total():
    order = Order(items=[Item(price=10), Item(price=20)])
    assert order.calculate_total() == 30

# ✅ GOOD: Using FAKE for external dependency
class FakePaymentGateway(PaymentGateway):
    def __init__(self):
        self.charged = []
    
    def charge(self, amount, card):
        self.charged.append((amount, card))
        return ChargeResult(success=True)

class FakeEmailSender(EmailSender):
    def __init__(self):
        this.sent = []
    
    def send(self, to, subject, body):
        this.sent.append({'to': to, 'subject': subject})

def test_order_payment_notifies_customer():
    gateway = FakePaymentGateway()
    emailer = FakeEmailSender()
    service = PaymentService(gateway, emailer)
    
    service.process_order(Order(amount=100, customer_email="test@x.com"))
    
    assert len(gateway.charged) == 1
    assert gateway.charged[0][0] == 100
    assert emailer.sent[0]['to'] == "test@x.com"
```

## Mutation Testing （新增）

### 什么是 Mutation Testing？

Mutation Testing 主动**修改你的代码**（比如把 `>` 变成 `<`，把 `true` 变成 `false`），然后跑测试。
如果测试全部通过 → 说明修改没被捕获 → **测试质量有问题**。

```
  Original code:         if (age >= 18) { return "adult"; }
  
  Mutant 1:              if (age > 18)  { return "adult"; }
  Mutant 2:              if (age < 18)  { return "adult"; }
  Mutant 3:              if (true)      { return "adult"; }
  Mutant 4:              if (age >= 18) { return null; }
  
  Result:
  ✅ Mutant 1 caught (test has age=18 case)
  ✅ Mutant 2 caught (test has age=17 case)
  ✅ Mutant 3 caught (test has age=5 case)
  ❌ Mutant 4 SURVIVED → return value is NEVER checked!
```

### Mutation Testing Tools

```bash
# JavaScript / TypeScript: Stryker
npx stryker run

# Python: mutmut
pip install mutmut
mutmut run --paths-to-mutate src/

# Go: go-mutesting
go install github.com/zimmski/go-mutesting/cmd/go-mutesting@latest
go-mutesting ./...

# Rust: cargo-mutants
cargo install cargo-mutants
cargo mutants
```

### Stryker Configuration (JavaScript/TypeScript)

```json
// stryker.conf.json
{
  "$schema": "./node_modules/@stryker-mutator/core/schema/stryker-schema.json",
  "packageManager": "npm",
  "mutate": ["src/**/*.ts", "!src/**/*.test.ts"],
  "testRunner": "vitest",
  "coverageAnalysis": "perTest",
  "thresholds": {
    "high": 80,
    "low": 60,
    "break": 50  // < 50% mutation score → CI fails
  },
  "reporters": ["html", "clear-text", "progress"],
  "timeoutMS": 5000
}
```

```bash
# Run in CI
npx stryker run --thresholds.break=50
```

### Mutation Score Targets

```
  ┌──────────────┬──────────────────────────────────────┐
  │ Score        │ Meaning                              │
  ├──────────────┼──────────────────────────────────────┤
  │ < 40%        │ Tests are mostly smoke tests         │
  │ 40-60%       │ Core paths tested, edges uncovered  │
  │ 60-80%       │ Good coverage — most mutants caught │
  │ 80-95%       │ Excellent — few surviving mutants   │
  │ > 95%        │ Exceptional — may be over-testing   │
  └──────────────┴──────────────────────────────────────┘

  Target: > 60% mutation score for all modules
  Target: > 80% mutation score for critical business logic
```

### Surviving Mutant Diagnosis

When a mutant survives, it tells you something specific:

| Surviving Mutant | What It Reveals |
|-----------------|-----------------|
| Condition boundary (>= → >) | Missing boundary test case |
| Boolean flip (true → false) | Missing error/corner case test |
| Return value replaced | Return value not being asserted |
| Exception swallowed | Error path not tested |
| Method call removed | Side effect not verified |

## 测试金字塔（升级版）

### 从 Pyramind 到 Trophy

```typescript
// Google's Testing Trophy — production-tested model
|   E2E      |  Few: 5-10 critical user journeys (Plaid/Playwright)
| Integration |  More: service-level, real dependencies  
| Contract    |  Many: Pact-based, consumer-driven (新增！)
| Unit        |  Most: isolated, pure function testing
```

## 遗留代码TDD套路

### 接缝（Seam）技术
```
在不改变已有代码外观的情况下，
找到可以注入测试的点。
```

### 遗留代码工作流
```python
# 1. 找到测试点（Seam）
class LegacyPaymentProcessor:
    def process(self, order):
        # 隐藏内部调用payment_gateway
        result = payment_gateway.charge(order.amount)
        return result

# 2. 提取接口
class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
    def process(self, order):
        result = self.gateway.charge(order.amount)
        return result

# 3. 编写特性测试
def test_legacy_payment():
    gateway = Mock()
    processor = PaymentProcessor(gateway)
    order = Order(amount=100)
    result = processor.process(order)
    assert result.is_success
```

### 遗留代码改造步骤
1. **覆盖测试**：为现有行为写特性测试
2. **拆分接缝**：提取接口/抽象依赖
3. **逐块重构**：一次改一小块，保持测试通过
4. **持续集成**：每次提交都跑所有测试

## TDD常用命令/脚本

```bash
# 持续执行测试（文件变化自动重跑）
npx jest --watch                  # JavaScript
pytest -f                         # Python
go test -v ./... -count=1        # Go

# Mutation Testing
npx stryker run                   # JavaScript/TS
mutmut run --paths-to-mutate src/ # Python
go-mutesting ./...                # Go

# 覆盖率报告
npx jest --coverage               # JS
pytest --cov=src --cov-report=html  # Python
go test -coverprofile=cover.out   # Go
```

## TDD检查清单（增强版）

- [ ] 测试先写（RED），后写实现（GREEN）
- [ ] 每个测试一个断言（或强相关一组）
- [ ] 测试命名 > 测试描述（`test_X_when_Y`）
- [ ] 测试独立可重复（不依赖顺序）
- [ ] 测试速度快（<1s/测试）
- [ ] Fake内部依赖，Mock在外部边界（不Mock内部逻辑）
- [ ] Mutation Score > 60%（核心模块 > 80%）
- [ ] 不测试私有方法（只测公共行为）
- [ ] 不为覆盖率而测试——写有意义的测试
- [ ] 每个bug fix至少附加大一个regression测试
- [ ] CI/CD包含 mutation testing stage
- [ ] Flaky test自动标记+修复优先级
