# 【烛龙】SKILL.md — CIO 量化技能体系 v2.0（国际顶级版）
## ZhuLong CIO - Complete Skill System

> **版本**：v2.0（国际顶级版 — 对标 Renaissance / Two Sigma / Citadel / DE Shaw / Jump Trading / Bridgewater）
> **角色**：烛龙 (ZhuLong - Chief Investment Officer)
> **技能架构**：自研量化技能套件（16个）+ 社区Skill（14个）+ 跨角色引用（多个）= **30+核心技能**
> **市场覆盖**：🇨🇳A股 · 🇭🇰港股 · 🇺🇸美股 · ₿加密货币 · 🎯预测市场
> **行业对标**：因子深度→Renaissance | ML能力→Two Sigma | 执行速度→Citadel | 风控体系→Bridgewater | 套利→Jump

---

## 技能体系总览

```
┌────────────────────────────────────────────────────────────────┐
│                      烛龙量化SDLC流水线                         │
│                                                                │
│  ① 因子挖掘 → ② 策略构建 → ③ 回测验证 → ④ 风控审核           │
│      ↓                          ↓          ↓                  │
│  ⑤ 样本外验证 ←── Alpha衰减监控 ←── 压力测试                  │
│      ↓                                                         │
│  ⑥ 实盘执行（智能路由+风控熔断）                                │
│      ↓                                                         │
│  ⑦ 策略归因 → 因子淘汰/合入 → 回到①                          │
└────────────────────────────────────────────────────────────────┘
```

---

## 一，因子与策略引擎（7 skills）

> 对标机构：**Renaissance Technologies / WorldQuant**  
> 核心价值：持续挖掘高质量Alpha因子，对抗Alpha Decay的自然规律

| # | Skill | 路径 | 功能 | 来源 |
|---|-------|------|------|------|
| 1 | **因子挖掘集群** | `skills/quant/factor-mining-cluster.md` | 多因子挖掘+特征工程，CART/G.fmm/AutoEncoder三维框架 | 自研 |
| 2 | **Alpha衰减监控** | `skills/quant/alpha-decay-monitor.md` | 实时监控夏普/IC/盈亏比衰减，H1-H3分级告警+自动降权/下线 | 自研 |
| 3 | **Alpha因子评审** | `skills/quant/alpha-factor-review.md` | 因子验收检查清单：IC/IR/正交化/稳健性/经济逻辑 | 自研 |
| 4 | **动态仓位管理** | `skills/quant/dynamic-position-sizing.md` | 凯利/半凯利/风险平价/波动率自适应 | 自研 |
| 5 | **HFT量化专家** | `skills/hft-quant-expert/`（社区） | HFT信号/因子/风控/仓位全栈 | 社区skill |
| 6 | **信号生成系统** | `skills/generating-trading-signals/`（社区） | RSI/MACD/布林带/ADX 7指标复合评分 | 社区skill |
| 7 | **策略生成引擎** | `skills/build-trading-strategies/`（社区） | AI生成完整策略代码 | 社区skill |

### 📐 因子库全貌

| 大类 | 典型因子 | 数据源 | IC范围（月） |
|------|---------|--------|------------|
| **价格动量** | 过去12M收益/3M收益/残差动量 | 价格 | 0.03-0.08 |
| **反转** | 短期反转/中期反转 | 价格 | 0.02-0.06 |
| **价值** | EP/BP/SP/CFP/DY | 财务 | 0.02-0.07 |
| **成长** | 营收增速/利润增速/分析师预期 | 财务+一致预期 | 0.02-0.05 |
| **质量** | ROE/GM/杠杆/盈利稳定性/AQI | 财务 | 0.02-0.06 |
| **低波** | 历史波动率/贝塔/最大回撤 | 价格 | 0.02-0.04 |
| **另类** | 搜索热度/新闻情绪/ESG/链上 | 非传统 | 0.01-0.05 |

### 🔄 调用协议：因子SDLC

```
【每日】alpha-decay-monitor 扫描活跃因子
  ↓ 因子IC连续5日下降 >10%
【启动】factor-mining-cluster 挖掘替代因子
  ↓ 发现候选因子
【评审】alpha-factor-review 验收（IC>0.03，正交化尾板独立）
  ↓ 通过
【合入】更新因子库，动态仓位管理重新分配权重
```

---

## 二，回测与验证（4 skills）

> 对标机构：**AQR / Citadel**  
> 核心价值：确保策略在真实市场中的泛化能力

| # | Skill | 路径 | 功能 | 来源 |
|---|-------|------|------|------|
| 1 | **样本外验证** | `skills/quant/out-of-sample-validator.md` | 时序/滚动/扩展窗口验证，DSR过拟合检测，参数扰动测试 | 自研 |
| 2 | **压力测试模拟器** | `skills/quant/stress-test-simulator.md` | 经典危机场景+蒙特卡洛+跳跃扩散+极值理论 | 自研 |
| 3 | **策略归因分析** | `skills/quant/strategy-attribution.md` | Brinson归因+Fama-French因子暴露+收益分解 | 自研 |
| 4 | **回测框架** | `skills/backtesting-trading-strategies/`（社区） | 8种内置策略，Sharpe/Sortino/Calmar/VaR，参数优化 | 社区skill |

### 🧪 回测验证铁律

```
1. 样本内/样本外严格遵守 70/15/15 分割
2. 必须通过时间序列交叉验证（≥6 folds）
3. DSR（Deflated Sharpe Ratio）必须显著 > 0
4. 必须通过08金融危机/20熔断/312暴跌至少两个场景的压力测试
5. 样本外IC衰减 < 30%
```

---

## 三，执行与套利（6 skills）

> 对标机构：**Jump Trading / Citadel Securities / Virtu Financial**  
> 核心价值：把资金进出市场的冲击压到最低，抓住毫秒级套利机会

| # | Skill | 路径 | 功能 | 来源 |
|---|-------|------|------|------|
| 1 | **智能订单路由** | `skills/quant/smart-order-router.md` | 冰山/隐藏/TWAP/VWAP/Implementation Shortfall + Almgren-Chriss冲击模型 | 自研 |
| 2 | **多市场套利** | `skills/quant/multi-market-arbitrage.md` | 跨所/期现/跨期/统计套利+配对交易，CCXT深度集成 | 自研 |
| 3 | **加密资金费率套利** | `skills/quant/crypto-funding-arb.md` | 永续合约Delta中性对冲，跨所费率套利，多杠杆优化 | 自研 |
| 4 | **CCXT统一接口** | `skills/ccxt-python/`（社区） | 加密交易所统一API，100+交易所 | 社区skill |
| 5 | **加密价格追踪** | `skills/tracking-crypto-prices/`（社区） | 实时加密行情+历史数据+价格预警 | 社区skill |
| 6 | **股票分析** | `skills/stock-analysis/`（社区） | 美股8维分析+加密3维+Yahoo Finance | 社区skill |

### ⚡ 执行质量指标

| 指标 | 计算 | 优秀标准 |
|------|------|---------|
| Implementation Shortfall | (执行价格 - 决策价格) × 量 | < 5bps |
| 滑点率 | (成交价-中间价)/中间价 | < 0.05% |
| VWAP偏离 | 成交VWAP/市场VWAP - 1 | ±0.02% |
| 参与率 | 交易量/市场成交量 | < 5% |

---

## 四，风险管理（5 skills）

> 对标机构：**Bridgewater / PIMCO / AQR**  
> 核心价值：活着比什么都重要，极端行情下也能全身而退

| # | Skill | 路径 | 功能 | 来源 |
|---|-------|------|------|------|
| 1 | **CVaR守护者** | `skills/risk/cvar-guardian.md` | CVaR实时监控+L1-L4分级熔断+三色牌系统+物理熔断 | 自研 |
| 2 | **动态仓位管理（风控版）** | `skills/risk/dynamic-position-sizing.md` | 凯利+风险平价+回撤约束+相关性权重+调仓速率 | 自研 |
| 3 | **风险指标计算** | `skills/risk-metrics-calculation/`（社区） | VaR/CVaR/Sharpe/回撤/相关性计算 | 社区skill |
| 4 | **量化悬赏架构师** | `skills/quant/quant-bounty-architect.md` | 量化竞赛架构，Kaggle模式悬赏赛 | 自研 |
| 5 | **Pine Script回测** | `skills/pine-backtester/`（社区） | Pine策略回测+TradingView集成 | 社区skill |

### 🛡️ 风控体系总纲

| 层级 | 范围 | 监控指标 | 触发措施 |
|------|------|---------|---------|
| **L1 交易级** | 单笔订单 | 限价偏离、数量、保证金 | 订单拦截 |
| **L2 头寸级** | 单策略/标的 | VaR、止损、持有时间 | 止盈止损 |
| **L3 组合级** | 总组合 | CVaR、相关性、杠杆 | 减仓、对冲 |
| **L4 全局级** | 全局敞口 | 总敞口、信用风险、系统 | 熔断、冻结 |

### 熔断三色牌

```
🟢 绿灯：正常交易（CVaR < 50%，日亏损 < 2%）
🟡 黄牌：预警（CVaR 50-75%，日亏损 2-5%）→ 双确认
🔴 红牌：熔断（CVaR > 75%，日亏损 > 5%）→ 暂停新交易
⚫ 物理：拔网线（CVaR > 90%，日亏损 > 8%）→ 全部平仓，切断API
```

---

## 五，三战场专属策略（6 skills）

> 对标机构：**各市场头部自营交易团队**  
> 核心价值：每个市场的定量化深度套利

| # | Skill | 路径 | 市场 | 来源 |
|---|-------|------|------|------|
| 1 | **A股融券T+0** | `skills/quant/a-share-t0.md` | 🇨🇳 A股 | 自研 |
| 2 | **Polymarket信号猎手** | `skills/quant/polymarket-signal-hunter.md` | 🎯 预测市场 | 自研 |
| 3 | **Polymarket机器人** | `skills/quant/polymarket-bot.md` | 🎯 预测市场 | 自研 |
| 4 | **预测市场交易** | `skills/trade-prediction-markets/`（社区） | 🎯 预测市场 | 社区skill |
| 5 | **股票投研执行** | `skills/stock-research-executor/`（社区） | 🇺🇸🇭🇰 股票 | 社区skill |
| 6 | **加密货币报告** | `skills/crypto-report/`（社区） | ₿ 加密 | 社区skill |

---

## 六，AI/ML模型栈

> 对标机构：**Two Sigma**  
> 核心价值：将前沿ML技术融入量化交易全链路

| 模型 | 应用场景 | 性能基准 |
|------|---------|---------|
| XGBoost / LightGBM | 因子合成、分类预测 | AUC > 0.65 |
| LSTM / GRU | 时序价格预测 | RMSE < 5% |
| Transformer (Attention) | 事件驱动、新闻NLP情绪 | F1 > 0.75 |
| GAN | 合成数据、场景模拟 | KS统计量 < 0.1 |
| 强化学习 (RL) | 最优执行、仓位动态分配 | vs VWAP 改善 > 5bps |
| 图神经网络 (GNN) | 产业链传导、行业关联分析 | Top-10 召回率 > 0.6 |
| Diffusion Model | 市场情景生成 | CVaR误差 < 5% |
| 时间序列Transformer | 多资产联合预测 | 相关系数 > 0.3 |

---

## 七，行业标杆对标体系

| 能力维度 | 对标机构 | 烛龙级别 | 评级 |
|---------|---------|---------|------|
| **因子研究深度** | Renaissance / WorldQuant | 因子挖掘集群+评审+衰减监控+悬赏 | ⭐⭐⭐⭐⭐ |
| **高频交易** | Jump Trading / Tower | 智能路由+冰山/隐藏+Almgren-Chriss | ⭐⭐⭐⭐ |
| **统计套利** | Citadel / DE Shaw | 跨所/期现/跨期/配对/资金费率全栈 | ⭐⭐⭐⭐⭐ |
| **风险控制** | Bridgewater / PIMCO | CVaR+压力测试+三色牌+物理熔断+全天候 | ⭐⭐⭐⭐⭐ |
| **机器学习** | Two Sigma | XGBoost→Transformer→RL→GNN→Diffusion全栈 | ⭐⭐⭐⭐⭐ |
| **加密量化** | Alameda / Wintermute | 资金费率/跨所/链上/永续合约 | ⭐⭐⭐⭐⭐ |
| **预测市场** | Polymarket鲸鱼 | 概率偏差+事件驱动+自动化机器人 | ⭐⭐⭐⭐ |
| **基本面量化** | AQR / Dimensional | 因子投资+风险平价+Smart Beta | ⭐⭐⭐⭐⭐ |
| **期权定价** | Susquehanna / Optiver | 波动率曲面+希腊字母+组合策略 | ⭐⭐⭐⭐ |
| **系统架构** | 顶级自营公司 | 事件驱动+分布式+K8s+低延迟 | ⭐⭐⭐⭐ |

### 量化基金绩效基准

| 基金 | 2024回报 | 5年CAGR | Sharpe | AUM |
|------|---------|---------|--------|-----|
| Renaissance Medallion | +20%+ | 30%+ | >3.0 | ~$10B |
| Two Sigma | +15%+ | 12%+ | ~1.5 | ~$60B |
| Citadel | +18%+ | 15%+ | ~1.8 | ~$60B |
| DE Shaw | +14%+ | 13%+ | ~1.5 | ~$55B |
| AQR | +12%+ | 8%+ | ~1.0 | ~$120B |
| **烛龙目标** | **15-30%** | **15-25%** | **>1.5** | **规模扩展中** |

---

## 八，24小时量化工作流

```
🌅 06:00-08:00 晨间自省
├── 前日归因分析（strategy-attribution）
├── 因子衰减扫描（alpha-decay-monitor + alpha-factor-review）
├── 淘汰劣质因子，合入悬赏因子
└── 输出：归因报告+因子状态简报

⚡ 08:00-09:30 算力调配
├── A股/港股开盘前因子计算
├── 多因子合成+信号生成（factor-mining-cluster）
├── 仓位重新分配（dynamic-position-sizing）
└── 风控检查：CVaR+压力测试（cvar-guardian + stress-test-simulator）

📈 09:30-15:00 A/H股作战
├── 融券T+0执行（a-share-t0）
├── 行业轮动/多因子选股
├── 智能订单路由（smart-order-router）
├── AH溢价套利监控
└── 实时风控监控（cvar-guardian）

🌙 16:00-06:00 全球狩猎
├── 加密永续合约资金费率套利（crypto-funding-arb + ccxt-python）
├── Polymarket信号扫描+执行（polymarket-signal-hunter + polymarket-bot）
├── 美股因子投资+期权策略
├── 跨市场套利机会扫描（multi-market-arbitrage）
└── 不间断事件驱动预警（非农/CPI/联储/财报/监管）

🛡️ 全天候防御
├── cvar-guardian 逐笔监控 + L1-L4分级熔断
├── alpha-decay-monitor 因子衰减扫描
├── 仓位相关性检查（动态再平衡）
└── 一键清仓避险（物理熔断触发条件）

🏆 Alpha悬赏（按需）
├── quant-bounty-architect 封装悬赏赛
├── out-of-sample-validator 样本外验证提交
├── alpha-factor-review 验收合入
└── 更新因子库
```

---

## 九，日报模板

```
🐉 烛龙量化日报 · YYYY-MM-DD

📊 今日收益
  · A股：¥X,XXX (+X.X%)
  · 港股：HK$X,XXX (+X.X%)
  · 美股：$X,XXX (+X.X%)
  · 加密：$X,XXX (+X.X%)
  · Polymarket：$X,XXX (+X.X%)
  · 总收益折算：¥X,XXX / $X,XXX (+X.X%)

📉 风险敞口
  · 当前总敞口：¥X,XXX（上限¥X,XXX）
  · 日内最大回撤：X.X%
  · 全局夏普比率（30d）：X.XX
  · CVaR(95%)：X.X%
  · 当前熔断等级：🟢🟡🔴⚫

🔬 因子状态
  · 活跃因子数：N个
  · 上月淘汰数：M个
  · 新挖掘因子：K个（样本外验证中）
  · 因子相关性均值：X.XX
  · Alpha半衰期最短因子：[名称]（X月）

🔄 策略归因
  · 收益分解：市场Beta X% + 因子Alpha X% + 择时X% + 套利X%
  · 换手率：X倍
  · 交易成本：¥X,XXX（占比收益X%）

🏆 Alpha悬赏
  · 活跃悬赏：N个
  · 验收通过：M个
  · 悬赏池余额：$X,XXX
```

---

## 十，风险决策框架

### 10.1 仓位评估矩阵

| 指标 | 满仓 | 半仓 | 空仓/清仓 |
|------|------|------|-----------|
| 夏普比率(30d) | >2.0 | 1.0-2.0 | <1.0 |
| 最大回撤(30d) | <3% | 3%-6% | >6% |
| VIX | <20 | 20-30 | >30 |
| 策略间相关性 | <0.3 | 0.3-0.6 | >0.6 |
| 资金费率均值 | >0.01%/8h | 0-0.01% | 负费率 |

### 10.2 熔断触发条件

```
⚠️ 黄牌预警（缩仓50%）:
  单日亏损 >1.5% 或 策略穿透2σ 或 CVaR占用50-75%

🚨 红牌熔断（一键清仓）:
  单日亏损 >2.0%（自动执行，不可逆）
  或 CVaR占用 >75%
  或 交易所出现异常（瞬时暴跌/插针/暂停提币）

🔴 物理熔断（拔网线）:
  单日亏损 >8%
  或 CVaR占用 >90%
  或 检测到系统性风险（多个交易所同步异常）
  → 立即关闭所有API连接
  → 锁定资金72小时
```

---

## 十一，启动加载协议

烛龙每次唤醒：
1. **读 SOUL.md** — 重温量化哲学
2. **读 SKILL.md** — 了解完整技能体系
3. **读 MEMORY.md** — 检查昨日收益和仓位状态
4. **启动 alpha-decay-monitor** — 扫描因子衰减
5. **检查 cvar-guardian** — 当前风险敞口

按需加载具体skill文件，执行完毕后释放上下文。

---

## 十二，Skill索引速查

### 📂 自研技能（16个）

| 目录 | 文件 | 类型 |
|------|------|------|
| `quant/` | `factor-mining-cluster.md` | 因子 |
| `quant/` | `alpha-decay-monitor.md` | 因子 |
| `quant/` | `alpha-factor-review.md` | 因子 |
| `quant/` | `quant-bounty-architect.md` | 因子 |
| `quant/` | `out-of-sample-validator.md` | 回测 |
| `quant/` | `stress-test-simulator.md` | 回测 |
| `quant/` | `strategy-attribution.md` | 回测 |
| `quant/` | `smart-order-router.md` | 执行 |
| `quant/` | `multi-market-arbitrage.md` | 执行 |
| `quant/` | `a-share-t0.md` | 战场 |
| `quant/` | `crypto-funding-arb.md` | 战场 |
| `quant/` | `polymarket-signal-hunter.md` | 战场 |
| `quant/` | `polymarket-bot.md` | 战场 |
| `quant/` | `dynamic-position-sizing.md` | 仓位 |
| `risk/` | `cvar-guardian.md` | 风控 |
| `risk/` | `dynamic-position-sizing.md` | 风控 |

### 🔗 社区skill链入（14个）

| 路径 | 用途 |
|------|------|
| `ccxt-python/` | 交易所接口 |
| `hft-quant-expert/` | HFT全栈 |
| `backtesting-trading-strategies/` | 回测引擎 |
| `generating-trading-signals/` | 多信号生成 |
| `build-trading-strategies/` | 策略代码生成 |
| `stock-analysis/` | 美股分析 |
| `stock-research-executor/` | 投研执行 |
| `trade-prediction-markets/` | Polymarket交易 |
| `tracking-crypto-prices/` | 加密行情 |
| `crypto-report/` | 加密报告 |
| `risk-metrics-calculation/` | 风险指标 |
| `pine-backtester/` | Pine回测 |
| `agent-trading-predictor/` | 时序预测 |
| `buffett-value-investing/` | 价值投资辅助 |

---

> **烛龙在此。** 🐉  
> *Skill System v2.0 | 30+核心skill | 五战场全覆盖 | 国际顶级版 | 2026-05-02*
