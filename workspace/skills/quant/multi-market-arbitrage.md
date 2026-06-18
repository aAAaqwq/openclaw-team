# 多市场套利

跨交易所、跨品种、跨期限的套利交易策略框架，与ccxt-python深度集成。

## 套利类型

### 跨交易所套利

- **原理**: 同一资产在不同交易所存在价差
- **信号**: 价差 > 手续费+滑点 → 买入低价/卖空高价
- **风险**: 延迟风险/交易所风险/资金转移时间

| 参数 | 说明 |
|------|------|
| 价差阈值 | 0.1%-0.5%（视流动性而定） |
| 延迟容忍 | < 500ms 价差窗口 |
| 最大敞口 | 单笔资金的10% |
| 滑点模型 | 线性滑点 + 参与率模型 |

### 期现套利

- **原理**: 永续合约资金费率 vs 现货价格
- **策略**: 做多现货 + 做空永续 = 吃资金费率
- **Delta中性**: 1:1对冲消除方向风险

| 参数 | 说明 |
|------|------|
| 入场资金费率 | ≥ 0.01%/8h |
| 出场资金费率 | ≤ 0.005%/8h |
| 最大仓位 | 总资金的30% |
| 对冲偏差 | ±0.5% |

### 跨期套利

- **原理**: 不同交割月份合约价差
- **牛市价差**: 近月 > 远月 → 做多价差
- **熊市价差**: 近月 < 远月 → 做空价差

### 统计套利（配对交易）

- **协整检验**: Engle-Granger / Johansen 检验
- **Z-score信号**: 价差z-score > 2入场，< 0.5出场
- **止损**: z-score > 3 止损

## 与ccxt-python集成

```python
# 示例: 跨交易所套利
import ccxt
from ccxt import pro as ccxtpro

binance = ccxt.binance()
okx = ccxt.okx()

# 获取两个交易所的订单簿
bid_binance = binance.fetch_order_book('BTC/USDT')['bids'][0][0]
ask_okx = okx.fetch_order_book('BTC/USDT')['asks'][0][0]

# 价差计算
spread = ask_okx - bid_binance
spread_pct = spread / bid_binance * 100
```

## 相关技能

- [ccxt-python](../skills/ccxt-python/) — ccxt连接器
- [crypto-funding-arb](../skills/quant/crypto-funding-arb.md) — 资金费率套利
- [a-share-t0](../skills/quant/a-share-t0.md) — A股融券T+0
