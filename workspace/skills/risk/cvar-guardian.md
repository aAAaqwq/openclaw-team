# CVaR守护者

条件风险价值（CVaR）驱动的实时风控系统，逐笔监控交易风险并触发分级熔断。

## CVaR计算

### 计算方法

| 方法 | 原理 | 精度 | 计算速度 |
|------|------|------|---------|
| **历史模拟** | 过去N日收益率排序 | 中 | 快 |
| **参数化** | 假设正态分布 | 低 | 极快 |
| **蒙特卡洛** | 随机路径模拟 | 高 | 慢 |
| **极值理论(EVT)** | 尾部建模 | 高 | 中 |

### CVaR vs VaR

```
VaR_95% = 过去95%分位损失（只关注阈值）
CVaR_95% = 超过VaR部分的平均损失（关注尾部）
```

| 置信水平 | VaR 95% | CVaR 95% |
|---------|---------|----------|
| 常规市场 | -2.5% | -4.0% |
| 波动市场 | -5.0% | -8.5% |
| 极端行情 | -12.0% | -20.0% |

### 实时计算公式

```python
def calculate_cvar(returns, confidence=0.95):
    """历史法CVaR"""
    sorted_returns = sorted(returns)
    var_idx = int(len(sorted_returns) * (1 - confidence))
    var = sorted_returns[var_idx]
    cvar = sum(sorted_returns[:var_idx]) / var_idx
    return var, cvar
```

## 逐笔风控监控框架

### 监控层级

| 层级 | 粒度 | 触发频率 | 处理方式 |
|------|------|---------|---------|
| **L1_交易级** | 单笔订单 | 实时 | 检查限价/数量 |
| **L2_头寸级** | 单个头寸 | 秒级 | 检查止损/回撤 |
| **L3_组合级** | 总组合 | 分钟级 | 检查CVaR/VaR |
| **L4_全局级** | 全局限制 | 分钟级 | 检查总敞口 |

### L1 交易级检查清单

- [ ] 限价是否在市场合理范围内
- [ ] 数量是否超过单笔最大限制
- [ ] 方向是否与当前趋势冲突
- [ ] 是否有足够保证金
- [ ] 该资产是否被暂停/限制交易

### L2 头寸级检查清单

- [ ] 当前浮亏是否触发止损线
- [ ] 当前持仓时间是否超过最大持有时间
- [ ] 该头寸CVaR是否超标
- [ ] 头寸成本vs市场价偏差

## 熔断触发规则

### 三色牌系统

```
🟢 绿灯: 正常运作
    ↓ 触发L1或L2条件
🟡 黄牌: 预警，交易需双重确认
    ↓ 持续恶化或触发L3条件
🔴 红牌: 强制暂停，冻结所有仓位
    ↓ 极端情况
⚫ 物理: 系统级熔断，切断API
```

### 触发条件矩阵

| 熔断等级 | CVaR占用 | 日亏损 | 触发行为 |
|---------|---------|--------|---------|
| 🟢 正常 | < 50% | < 2% | 正常交易 |
| 🟡 黄牌 | 50-75% | 2-5% | 新交易需确认 |
| 🔴 红牌 | 75-90% | 5-8% | 暂停新交易 |
| ⚫ 物理 | > 90% | > 8% | 全部平仓冻结 |

## 熔断后恢复流程

### 分级恢复

```
⚫ 物理熔断: 6小时后，人工确认 → 恢复
🔴 红牌熔断: 3小时后，自动检查指标 → 恢复
🟡 黄牌熔断: 1小时后，指标改善 → 恢复
```

### 恢复条件

- CVaR占用 < 30%
- 连续30分钟无新告警
- 当前未持仓或已大幅减仓
- 风控经理确认（物理熔断需要）

## 与stress-test-simulator联动

```
stress-test-simulator
    ↓ 生成极端场景CVaR
cvar-guardian
    ↓ 实时对比场景CVaR vs 实际CVaR
    ↓ 触发熔断时调用stress-test模拟恢复路径
dynamic-position-sizing
    ↓ 按当前CVaR确定安全仓位
```

## 相关技能

- [stress-test-simulator](../skills/quant/stress-test-simulator.md) — 压力测试模拟器
- [dynamic-position-sizing (risk版)](../skills/risk/dynamic-position-sizing.md) — 仓位管理
- [alpha-decay-monitor](../skills/quant/alpha-decay-monitor.md) — Alpha衰减监控
- [risk-metrics-calculation](../skills/risk-metrics-calculation/) — 风险指标计算
