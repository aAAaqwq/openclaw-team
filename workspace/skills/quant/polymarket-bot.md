# Polymarket机器人

实盘执行Polymarket预测市场交易策略，集成风险引擎与自动化操作。

## 实盘交易执行器

### 核心功能

- **自动下单**: 基于信号执行买入/卖出
- **限价单**: 指定价格，避免滑点损失
- **分批执行**: 大额订单分拆执行
- **止损止盈**: 自动平仓规则

### 执行流程

```
信号进入
    ↓
风险引擎检查(最大仓位/止损)
    ↓
下单执行(限价单)
    ↓
持仓监控(持续跟踪)
    ↓
止盈止损触发(自动平仓)
```

## 风险引擎

### 最大仓位控制

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 单笔最大 | 单个信号最大投入 | 总资金5% |
| 总敞口 | 所有活跃订单总额 | 总资金40% |
| 最大持仓数 | 同时持有的头寸数 | 10个 |
| 同事件 | 同一事件双向持仓 | 禁止 |

### 止损规则

- **硬止损**: 亏损达到阈值 → 强制平仓
- **时间止损**: 到期前X天自动退出
- **概率止损**: 概率突破阈值范围退出

### 滑点容忍

| 市场深度 | 滑点容忍 | 说明 |
|---------|---------|------|
| >$100K | 1% | 深水市场 |
| $10K-$100K | 3% | 中等市场 |
| <$10K | 买不到 | 跳过 |

## 策略配置模板

```yaml
# polymarket-bot-config.yaml
bot:
  name: "polymarket-trader"
  api_endpoint: "https://clob.polymarket.com"

risk:
  max_per_position: 0.05    # 单笔5%
  max_total_exposure: 0.40  # 总敞口40%
  max_positions: 10
  stop_loss: 0.30           # 止损30%
  take_profit: [0.50, 0.75] # 止盈50%/75%两档
  min_confidence: 2         # 最低置信度评分

strategy:
  min_bias: 0.15           # 最低偏差15%
  min_liquidity: 10000     # 最低流动性$10K
  max_days_to_expiry: 30   # 最长30天到期
  position_sizing: "kelly" # 凯利公式仓位

notification:
  telegram: true
  telegram_channel: "@myChannel"
  push_every_trade: true
```

## 集成trade-prediction-markets

```python
# 集成示例
from polmarket_bot import Bot
from signal_hunter import SignalHunter

hunter = SignalHunter(min_bias=0.15)
bot = Bot(config_path="config.yaml")

while True:
    signals = hunter.scan()
    for signal in signals:
        if signal.confidence >= bot.config.risk.min_confidence:
            order = bot.execute(
                market=signal.market,
                side="buy",
                price=signal.entry_price,
                size=signal.kelly_size
            )
            bot.monitor(order)
```

## 相关技能

- [polymarket-signal-hunter](../skills/quant/polymarket-signal-hunter.md) — 信号猎手
- [trade-prediction-markets](../skills/trade-prediction-markets/) — 预测市场交易
- [dynamic-position-sizing](../skills/quant/dynamic-position-sizing.md) — 仓位管理
