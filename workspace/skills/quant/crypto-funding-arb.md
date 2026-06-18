# 加密资金费率套利

利用永续合约资金费率机制，通过Delta中性对冲实现稳定套利收益。

## 资金费率套利原理

### 永续合约机制

永续合约没有交割日，通过**资金费率**维持价格锚定现货：

```
资金费率 > 0 → 多头支付空头（看涨情绪高）
资金费率 < 0 → 空头支付多头（看跌情绪高）
```

### 套利逻辑

```
做多现货 + 做空永续 = Delta中性
    ↑              ↑
收取多头资金费率   支付空头资金费率
          ↓
净收益 = 收集的资金费率 - 持仓成本
```

### 收益计算

```
日收益率 = (资金费率(%) × 3 × 杠杆) - 资金成本

例如:
- 年化资金费率: 15% (平均0.042%/8h)
- 资金成本: 5% 年化
- 净年化: 10%
```

| 费率水平 | 年化收益 | 风险等级 |
|---------|---------|---------|
| 0.005%/8h | 5.5% | 低 |
| 0.01%/8h | 11% | 低 |
| 0.02%/8h | 22% | 中 |
| 0.05%/8h | 55% | 高 |

## 多交易所费率监控

### 监控指标

| 指标 | 说明 |
|------|------|
| 当前费率 | 各交易所实时资金费率 |
| 费率趋势 | 过去24h费率均值方向 |
| 费率差异 | 跨交易所费率差 |
| 费率时间 | 每8小时结算时间 |

### 套利机会

```
交易所A: 0.015%/8h (多付空)
交易所B: 0.008%/8h (多付空)
交易所C: -0.005%/8h (空付多)

策略: 交易所C做多 + 交易所A做空
      收取0.005% + 收取0.005% = 0.01%/8h
```

## Delta中性对冲

### 基础对冲

```
现货1X = 永续1X
资金量: $10,000 BTC现货
        $10,000 BTC永续空单
净风险暴露: 0 (价格涨跌不影响净值)
```

### 杠杆对冲

```
使用杠杆优化资金效率:
- $2,000 资金 → 5x做多现货
- $2,000 资金 → 5x做空永续
总投入: $4,000
总敞口: $20,000
资金效率: 5x
```

### 再平衡

| 触发条件 | 操作 |
|---------|------|
| 偏差 > 0.5% | 调整仓位恢复中性 |
| 每8小时结算后 | 检查仓位平衡 |
| 资金费率方向突变 | 评估是否继续套利 |

## 与ccxt-python集成

```python
import ccxt

def get_funding_rate(exchange_id, symbol):
    """获取资金费率"""
    ex = getattr(ccxt, exchange_id)()
    funding = ex.fetch_funding_rate(symbol)
    return {
        'exchange': exchange_id,
        'symbol': symbol,
        'rate': funding['fundingRate'],
        'next_funding_time': funding['fundingTimestamp']
    }

def arb_opportunity(symbol, min_rate=0.0001):
    """扫描套利机会"""
    exchanges = ['binance', 'okx', 'bybit', 'bitget']
    rates = []
    
    for ex in exchanges:
        try:
            rate = get_funding_rate(ex, symbol)
            rates.append(rate)
        except:
            continue
    
    # 找最高和最低费率
    rates.sort(key=lambda x: x['rate'])
    best = rates[-1]  # 最高费率(多付空)
    worst = rates[0]  # 最低费率(空付多)
    
    return {
        'long_on': worst['exchange'],
        'short_on': best['exchange'],
        'spread': best['rate'] - worst['rate']
    }
```

## 风险清单

- [ ] **爆仓风险**: 极端行情下单边被爆
- [ ] **资金费率突变**: 单次极端费率吞噬收益
- [ ] **交易所风险**: 交易所暂停/限制功能
- [ ] **滑点成本**: 大额下单影响
- [ ] **资金成本**: 借贷利率高于费率收益
- [ ] **网络延迟**: 对冲不及时导致暴露

## 相关技能

- [ccxt-python](../skills/ccxt-python/) — ccxt连接器
- [multi-market-arbitrage](../skills/quant/multi-market-arbitrage.md) — 多市场套利
- [dynamic-position-sizing](../skills/quant/dynamic-position-sizing.md) — 仓位管理
