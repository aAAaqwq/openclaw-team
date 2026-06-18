# 🎯 Polymarket 执行协议 V1
## Polymarket Execution Protocol — Full Process

> **版本**：V1 | **生成**：2026-05-04
> **核心流程**：消息监测 → 概率量化 → 下单执行 → 止损止盈 → 复盘闭环
> **执行节奏**：扫描引擎 24×7 运行 | 人工决策 08:00-23:00 | 自动化交易 24×7

---

## 一、执行总纲

```
┌──────────────────────────────────────────────────────────────────┐
│                    POLYMARKET 执行流水线                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📡 第1层：信息采集 (24×7)                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ RSS/Webhook  │  │API主动扫描   │  │ 人工阅读     │              │
│  │ 自动推送     │  │ 每30分钟     │  │ 关键源       │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         └────────────────┼────────────────┘                     │
│                          ▼                                       │
│  🔍 第2层：市场扫描 (每30分钟)                                   │
│  ┌────────────────────────────────────────────────────┐          │
│  │ • 新市场检测    • 概率偏差扫描 (>15%)              │          │
│  │ • 大户检测      • 异常波动检测                     │          │
│  └──────────────────────┬─────────────────────────────┘          │
│                          ▼                                       │
│  🧠 第3层：决策引擎                                             │
│  ┌────────────────────────────────────────────────────┐          │
│  │ • 信号验证 (≥2独立信源)   • 策略类型匹配          │          │
│  │ • 仓位计算 (Kelly公式)     • 风险检查             │          │
│  └──────────────────────┬─────────────────────────────┘          │
│                          ▼                                       │
│  ⚡ 第4层：执行引擎                                              │
│  ┌────────────────────────────────────────────────────┐          │
│  │ • 限价单/市价单选择  • 拆单(Babysize)             │          │
│  │ • 止盈止损预设        • 事件后自动平仓            │          │
│  └──────────────────────┬─────────────────────────────┘          │
│                          ▼                                       │
│  📊 第5层：复盘 (每日)                                          │
│  ┌────────────────────────────────────────────────────┐          │
│  │ • 交易日志    • 概率偏差命中率                    │          │
│  │ • 策略归因    • 领域专注度评估                    │          │
│  └────────────────────────────────────────────────────┘          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 二、第1层：信息采集协议 (24×7)

### 2.1 自动化信息采集

#### 2.1.1 RSS/Webhook 推送配置

```python
# 配置示例
INFO_SOURCES = {
    "macro": {
        "rss": [
            "https://www.bls.gov/feed/",           # BLS 数据发布
            "https://www.federalreserve.gov/rss/",  # Fed 公告
            "https://www.bea.gov/rss/",             # BEA GDP/PCE
        ],
        "webhook": [
            "https://hooks.example.com/fomc",       # FOMC 日历
        ]
    },
    "politics": {
        "rss": [
            "https://www.270towin.com/rss/",         # 选举民调
            "https://www.realclearpolitics.com/rss/", # RCP 民调聚合
        ]
    },
    "crypto": {
        "rss": [
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://theblock.co/rss.xml",
        ]
    },
    "sports": {
        "rss": [
            "https://www.espn.com/espn/rss/news",
            "https://theathletic.com/feed/",
        ]
    }
}
```

#### 2.1.2 关键信息源分类监控表

| 类别 | 信息源 | 监控手段 | 优先级 |
|------|--------|---------|--------|
| **宏观数据** | BLS/BEA/Fed/ECB/BOJ | RSS + 日历抓取 | S |
| **政治民调** | 270toWin/RCP/538/Politico | RSS + 网页抓取 | S |
| **地缘事件** | Reuters/AP/ISW | RSS + 关键词过滤 | A |
| **体育数据** | ESPN/Odds Shark/Transfermarkt | API + RSS | A |
| **加密数据** | CoinDesk/Glassnode/The Block | RSS + API | A |
| **科技动态** | TechCrunch/The Verge/ArXiv | RSS | B |

### 2.2 人工阅读流程

```
每日 08:00-08:30：快速扫描关键信息源（15分钟）
     → 检查信息队列中是否有新推送
     → 快速浏览各领域标题
     → 标记3-5条需要深度阅读的内容

每日 08:30-09:30：深度阅读（60分钟）
     → 精读已标记的内容
     → 判断是否与任何活跃Polymarket市场相关
     → 如相关 → 评估概率偏差

每日⚠️ 关键提醒：
     → 数据发布（CPI/NFP/FOMC）前48小时 → 高度警惕
     → 突发事件 → 立即进入扫描模式
```

### 2.3 信息优先级排序

信息到达时按以下公式排序：

```
优先级 = 事件重要性 × 时间紧迫性 × 与活跃市场的相关性

其中：
  事件重要性 = 1（普通）| 2（重要）| 3（关键）
  时间紧迫性 = 1（周内）| 2（48h内）| 3（24h内）
  市场相关性 = 0（无市场）| 1（有相关市场）| 2（市场活跃交易中）

排序规则：
  总分 ≥ 6 → 立即处理
  总分 4-5 → 30分钟内处理
  总分 ≤ 3 → 加入日常队列
```

---

## 三、第2层：市场扫描协议 (每30分钟)

### 3.1 自动扫描脚本逻辑

```python
def scan_polymarket():
    """
    每30分钟执行一次
    """
    # 1. 获取所有活跃市场
    new_markets = get_new_markets()
    active_markets = get_active_markets()
    
    # 2. 检查新市场（是否有领域匹配）
    for m in new_markets:
        area = classify_market(m)
        if area in MY_52_DOMAINS:
            add_to_watchlist(m)
    
    # 3. 概率偏差扫描
    for m in watchlist:
        current_prob = m['best_offer']['price']  # 当前价格 ≈ 市场概率
        fair_prob = estimate_fair_prob(m)          # 基于知识的合理概率
        deviation = abs(current_prob - fair_prob)
        
        if deviation > 0.15:  # 偏差大于15%
            flag_opportunity(m, deviation)
    
    # 4. 异常波动检测（5分钟内价格变动 > 10%）
    for m in active_markets:
        volatility = check_volatility(m, window=5)
        if volatility > 0.10:
            alert_volatility(m, volatility)
    
    # 5. 大户检测（单笔 > 10K U）
    big_trades = check_big_trades(threshold=10000)
    for t in big_trades:
        if t['market'] in watchlist:
            update_sentiment(t['market'], t['direction'])
```

### 3.2 概率偏差评分标准

| 偏差范围 | 评级 | 动作 |
|---------|------|------|
| 0-5% | 🟢 正常 | 继续监控 |
| 5-10% | 🟡 关注 | 标记观察，手动验证 |
| 10-15% | 🟠 候选 | 深度分析，准备出手 |
| 15-25% | 🔴 机会 | 确认后出手（仓位=中） |
| >25% | 🔴🔥 大机会 | 确认后出手（仓位=重） |

### 3.3 合理概率估算模板

```python
def estimate_fair_prob(market):
    """
    基于当前掌握的专业知识估算合理概率
    """
    domain = market['domain']
    if domain == 'FOMC':
        # 基于FedWatch工具 + 鲍威尔讲话倾向 + 经济数据
        fair = calculate_fomc_prob(market['outcome'])
    elif domain == 'CPI':
        # 基于Bloomberg共识 + 汽油价格 + 房租趋势
        fair = calculate_cpi_prob(market['outcome'], market['threshold'])
    elif domain == 'sports':
        # 基于BPI/ELO + 伤病报告 + 赔率模型
        fair = calculate_sports_prob(market['outcome'])
    else:
        # 领域专精人工评估
        fair = manual_estimate(market)
    
    # 保守偏差调整（避免过度自信）
    fair = apply_bayesian_shrinkage(fair)
    
    return fair
```

---

## 四、第3层：决策引擎协议

### 4.1 信号验证清单

**每条交易信号需通过以下所有检查才能出手：**

```
□ 概率偏差 > 15%
□ 信息源验证（≥2个独立信源确认）
□ 策略类型已匹配
□ 仓位上限未超
□ 风险检查通过
□ 流动性检查通过（买卖价差<5%）
□ 与当前持仓无不当对冲
```

### 4.2 仓位计算 (Kelly公式)

```python
def calculate_position(win_prob, odds):
    """
    Kelly 公式计算最优仓位
    """
    # 标准Kelly: f = (p*b - q) / b
    # p = 盈利概率（我们估算的合理概率）
    # q = 亏损概率 = 1-p
    # b = 赔率（市价隐含赔率）
    
    p = win_prob        # 我们估算的合理概率
    market_price = 1 - odds  # 市价概率
    b = (1 / market_price) - 1  # 净赔率
    q = 1 - p
    
    f = (p * b - q) / b
    
    # 阻尼因子（避免过度重仓）
    if p > 0.85:
        damping = 0.25    # 高概率 → 保守
    elif p > 0.70:
        damping = 0.35
    elif p > 0.50:
        damping = 0.45
    else:
        damping = 0.30    # 低概率 → 极其保守
    
    position = f * damping
    
    # 仓位上限硬约束
    max_position = 0.20  # 单一市场 ≤ 20%
    position = min(position, max_position)
    
    return position
```

### 4.3 交易信号处理流程

```
收到信号
    │
    ▼
┌─────────────────────────────┐
│ 信号有效性检查               │
│ • 信息源独立验证 ≥2个        │
│ • 概率偏差 >15%              │
│ • 不是旧信息/已被市场消化     │
└─────────┬───────────────────┘
          │ 有效
          ▼
┌─────────────────────────────┐
│ 策略匹配                    │
│ 该信号属于哪种策略类型？     │
│ 1. 数学套利                  │
│ 2. 高概率债券                │
│ 3. 恐慌错杀                  │
│ 4. 信息优势套利              │
│ 5. 事件驱动                  │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 仓位计算 (Kelly+damping)    │
│ 检查仓位上限                │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 风险检查                    │
│ • 单市场≤20%                │
│ • CVaR占用<75%              │
│ • 当日亏损<5%               │
└─────────┬───────────────────┘
          │ 通过
          ▼
┌─────────────────────────────┐
│ 执行                        │
│ 下单 + 止损设置 + 止盈设置  │
└─────────────────────────────┘
```

---

## 五、第4层：执行协议

### 5.1 下单规则

#### 5.1.1 订单类型选择

| 场景 | 订单类型 | 理由 |
|------|---------|------|
| 概率偏差 > 20%（深折价） | 市价单 | 快速捕捉，机会窗口短 |
| 概率偏差 15-20% | 限价单（折价2-5%） | 争取更好价格 |
| 数学套利(YES+NO<1) | 限价单 | 追求精确价差 |
| 高概率债券 | 市价单 | 流动性好，价差小 |
| 恐慌错杀 | 限价单（折价5-10%） | 恐慌时总是有更恐慌的卖家 |

#### 5.1.2 拆单策略

```python
def execute_order(market, size, order_type='limit'):
    """
    大单拆小执行，减少滑点
    """
    if size <= 100:  # 小单直接执行
        return place_order(market, size, order_type)
    
    # 大单拆成小份
    babychunk = min(size * 0.2, 200)  # 每份 ≤ 20% 或 200U
    chunks = split_into_chunks(size, babychunk)
    
    orders = []
    for chunk in chunks:
        # 时间切片：每30-60秒下一份
        if order_type == 'limit':
            price = market['best_ask'] * (1 - 0.02)  # 折价2%
        else:
            price = None  # 市价
        
        order = place_order(market, chunk, order_type, price)
        orders.append(order)
        time.sleep(random.uniform(30, 60))  # 避免被反检测
    
    return orders
```

### 5.2 止盈止损规则表

#### 5.2.1 分策略止盈止损设定

| 策略类型 | 止损线 | 止盈线 | 持有期上限 | 说明 |
|---------|--------|--------|-----------|------|
| **数学套利** | 不设止损 | YES+NO≥0.98 | 7天 | 持有至到期或价差回归 |
| **高概率债券** | 概率跌破80% | ≥97%或到期 | 至事件结束 | 到期是最好结果 |
| **恐慌错杀** | -30% | +40% 或 回归合理的80% | 72小时 | 恐慌后72小时未回归→认错 |
| **信息优势套利** | -25% | +50% 或 事件落地 | 至事件结束 | 信息落地即平，不贪 |
| **事件驱动** | -15% | +20% 或 事件后30分钟 | 事件后30分钟 | 事件公布后无条件平仓 |

#### 5.2.2 通用止损执行流程

```
触发止损条件（任一）：
    ┌───────────────────────────┐
    │ • 价格跌破预设止损线      │
    │ • 概率与我们方向背离>25%  │
    │ • 核心逻辑被推翻          │
    │ • 事件已发生但结果与预期  │
    │   相反                   │
    └───────────┬───────────────┘
                ▼
    ┌───────────────────────────┐
    │ 立即平仓，不容忍！         │
    │ ① 改限价为市价            │
    │ ② 全仓一次平             │
    │ ③ 记录止损原因            │
    └───────────┬───────────────┘
                ▼
    ┌───────────────────────────┐
    │ 复盘：                     │
    │ • 为什么判断错了？         │
    │ • 信息源是否可靠？        │
    │ • 下次如何避免？          │
    └───────────────────────────┘
```

### 5.3 自动化执行引擎设计

```python
class PolymarketBot:
    """
    Polymarket 自动交易机器人
    """
    def __init__(self, private_key, wallet_address):
        self.private_key = private_key
        self.wallet = wallet_address
        self.client = CLOBClient()
        self.active_positions = {}
        self.stop_limits = {}
    
    def scan_and_trade(self):
        """主循环：每30分钟执行一次"""
        while True:
            # 1. 扫描市场
            opportunities = self.scan_probability_deviations()
            
            # 2. 处理信号
            for opp in opportunities:
                if self.validate_signal(opp):
                    self.execute_trade(opp)
            
            # 3. 检查止损
            self.check_stop_limits()
            
            # 4. 检查止盈
            self.check_take_profits()
            
            # 5. 事件后平仓
            self.check_event_resolution()
            
            time.sleep(1800)  # 30分钟
    
    def validate_signal(self, opportunity):
        """信号验证"""
        checks = [
            opportunity['deviation'] > 0.15,
            opportunity['liquidity'] > 100,  # 最小流动性
            opportunity['spread'] < 0.05,     # 最大价差
            self.check_position_limit(opportunity),
            self.check_daily_loss_limit(),
        ]
        return all(checks)
    
    def execute_trade(self, opportunity):
        """执行交易"""
        position = self.calculate_position(opportunity)
        
        # 设置止盈止损
        stop_loss = self.get_stop_loss(opportunity)
        take_profit = self.get_take_profit(opportunity)
        
        # 下单
        order = self.client.create_order(
            market=opportunity['market'],
            side=opportunity['side'],
            size=position,
            price=opportunity['price'],
            order_type='LIMIT'
        )
        
        # 记录持仓
        self.active_positions[opportunity['market']] = {
            'entry_price': order['price'],
            'size': position,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': datetime.now(),
            'strategy_type': opportunity['strategy_type'],
        }
```

---

## 六、第5层：复盘协议 (每日)

### 6.1 每日复盘模板

```markdown
# 🎯 Polymarket 交易日志
## YYYY-MM-DD

### 📊 当日总览
| 指标 | 数值 |
|------|------|
| 当日PnL | +$XXX / -$XXX |
| 交易次数 | N |
| 胜率 | XX% |
| 最大回撤 | XX% |
| 当前持仓数 | N |
| 资金利用率 | XX% |

### 📝 交易记录
| 时间 | 市场 | 方向 | 入场价 | 出场价 | PnL | 策略类型 | 备注 |
|------|------|------|--------|--------|-----|---------|------|
| HH:MM | XXX | YES/NO | X.XX | X.XX | +$XX | 信息优势 | 确认民调偏差 |

### 🔬 概率偏差命中率
| 扫描总次数 | 标记机会 | 实际出手 | 命中 | 命中率 |
|-----------|---------|---------|------|--------|
| N | N | N | N | XX% |

### 📈 策略归因
| 策略类型 | 交易次数 | 总PnL | 胜率 | 平均盈亏比 |
|---------|---------|-------|------|-----------|
| 数学套利 | N | +$XXX | XX% | X.X |
| 高概率债券 | N | +$XXX | XX% | X.X |
| 信息优势 | N | +$XXX | XX% | X.X |
| ... | ... | ... | ... | ... |

### 💡 今日教训
1. ...
2. ...

### 📋 明日计划
- 关注事件：...
- 待扫描新市场：...
- 学习领域：...
```

### 6.2 每周复盘协议（周五）

```markdown
# 🎯 Polymarket 周报
## YYYY-MM-DD ~ YYYY-MM-DD

### 📊 本周总览
| 指标 | 本周 | 上周 | 环比变化 |
|------|------|------|---------|
| 周PnL | +$XXX | +$XXX | +XX% |
| 交易次数 | N | N | +N |
| 胜率 | XX% | XX% | +X% |
| 最大回撤 | XX% | XX% | +X% |

### 🎯 本周领域进度
本周领域：[领域名称]
进度评分：[1-10]
关键学习：[3-5条要点]
信息源新增：[N个]
专家卡状态：[新建/更新/未完成]

### 📋 52周计划进度
已完成：N/52周
当前周：WX

### ⚠️ 问题与调整
1. ...
2. ...

### 🔜 下周计划
领域：[领域名称]
备战重点：[3-5个关键问题]
可交易市场预判：[市场列表]
```

---

## 七、熔断与应急协议

### 7.1 熔断等级

| 等级 | 触发条件 | 动作 |
|------|---------|------|
| 🟢 **正常** | 一切正常 | 继续交易 |
| 🟡 **黄牌预警** | 单日亏损 > 总资金 3% | 停止新开仓，持有至到期或止损 |
| 🔴 **红牌熔断** | 单日亏损 > 总资金 5% | 停止所有交易24小时，强制平所有浮亏>20%的头寸 |
| ⚫ **物理熔断** | 连续3日亏损 | 清空所有仓位，锁定钱包72小时 |

### 7.2 突发事件应急流程

```
收到突发事件报告
    │
    ▼
┌─────────────────────────────┐
│ 1. 确认消息真实性            │
│    • 至少2个独立信源核实    │
│    • 排除谣言/误导信息      │
│    • 评估事件严重等级       │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 2. 检查持仓暴露             │
│    • 是否有相关市场持仓     │
│    • 当前浮盈/浮亏状态      │
│    • 事件是好是坏           │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 3. 决策                     │
│    • 利好 → 设置移动止盈    │
│    • 利空 → 立即止损        │
│    • 不确定 → 减半仓位       │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 4. 事件后处理               │
│    • 记录突发事件处理经过   │
│    • 评估信息源时效性       │
│    • 优化预警机制           │
└─────────────────────────────┘
```

### 7.3 安全隔离规则

```
L0: 主钱包（冷存储）
    • 永不连接任何DeFi/Prediction Market
    • 定期（每月）向热钱包补充资金
    • 仅通过硬件钱包签名

L1: 操作热钱包
    • 仅存放可承受亏损金额（≤总加密资产20%）
    • 每次操作完成后断开连接
    • 每日检查余额与授权

L2: 策略隔离
    • 每个独立策略使用独立子钱包
    • 跨策略资金不混用
    • 每季度清理未使用授权

L3: API安全
    • 私钥永不存储于明文
    • 使用环境变量加密存储
    • API连接仅使用智能订单路由
```

---

## 八、机器人部署方案

### 8.1 架构总览

```
┌─────────────────────────────────────────────────────┐
│                  部署架构                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📱 监控层 (24×7)                                   │
│  ┌─────────────────────────────────────────────┐    │
│  │ • Polymarket CLOB API 轮询（30分钟/次）     │    │
│  │ • RSS 订阅推送                               │    │
│  │ • Webhook 接收                               │    │
│  │ • 关键数据日历（BLS/FOMC/NFP）              │    │
│  └──────────────┬──────────────────────────────┘    │
│                  ▼                                    │
│  🧠 决策层 (事件驱动)                                  │
│  ┌─────────────────────────────────────────────┐    │
│  │ • 概率偏差计算引擎                           │    │
│  │ • 信号验证器                                 │    │
│  │ • 仓位计算器 (Kelly)                        │    │
│  │ • 风险过滤器                                 │    │
│  └──────────────┬──────────────────────────────┘    │
│                  ▼                                    │
│  ⚡ 执行层 (事件驱动)                                  │
│  ┌─────────────────────────────────────────────┐    │
│  │ • 限价单/市价单路由器                       │    │
│  │ • 拆单器                                   │    │
│  │ • 止损管理器                               │    │
│  │ • 止盈管理器                               │    │
│  └──────────────┬──────────────────────────────┘    │
│                  ▼                                    │
│  💾 数据层 (每日批处理)                                │
│  ┌─────────────────────────────────────────────┐    │
│  │ • SQLite 数据库（交易记录）                  │    │
│  │ • CSV 日志（全量交易明细）                   │    │
│  │ • JSON 快照（每日状态）                     │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 8.2 技术要求

| 组件 | 要求 | 推荐方案 |
|------|------|---------|
| **运行环境** | Linux / macOS | 服务器或Mac Mini |
| **Python版本** | ≥3.10 | 3.11+ |
| **API连接** | Polymarket CLOB API | websocket + REST |
| **数据存储** | SQLite + CSV | 本地轻量 |
| **定时任务** | cron / systemd timer | 30分钟间隔 |
| **监控告警** | Telegram Bot | 实时推送 |
| **私钥管理** | 加密环境变量 | 1Password / .env.gpg |

### 8.3 部署步骤

```bash
# 1. 环境准备
python -m venv polymarket_venv
source polymarket_venv/bin/activate
pip install requests pandas numpy python-dotenv polymarket-api

# 2. 配置文件
cat > .env << 'EOF'
POLYMARKET_PRIVATE_KEY=your_encrypted_private_key
POLYMARKET_WALLET=your_wallet_address
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
EOF

# 3. 主循环启动
python polymarket_bot.py

# 4. 设置定时任务
crontab -e
# 每30分钟运行一次
*/30 * * * * cd /path/to/bot && python scanner.py >> logs/scan_$(date +\\%Y\\%m\\%d).log 2>&1
```

### 8.4 部署清单

```
□ Python 环境配置完成
□ Polymarket CLOB API 连接成功
□ 私钥安全存储（加密）
□ Telegram Bot 配置完成
□ 初始钱包有操作资金
□ crontab/scheduler 配置完成
□ log 目录创建完成
□ 止损规则硬编码于代码中
□ 熔断机制已加载
□ 初始 watchlist 已设置
□ 第一个扫描周期已执行
```

---

## 九、执行检查清单（每日必做）

### 09:00 开盘检查
```
□ 自动扫描脚本是否正常运行（检查最后一次扫描时间戳）
□ 是否有新市场上线（领域匹配）
□ 是否有重要事件今日发生
□ 当前持仓是否正常
□ 每日亏损是否在允许范围内
```

### 12:00 午间检查
```
□ 概率偏差扫描结果（是否有 >15% 机会）
□ 大户动态跟踪（是否有 >10K U 大单）
□ 领域学习进度
□ 计划下午的交易
```

### 18:00 收盘检查
```
□ 当日交易复盘
□ 写入交易日志
□ 更新持仓状态
□ 准备明日计划
```

### 22:00 深度检查
```
□ 尾盘扫描（美国市场开盘后机会）
□ 止损检查
□ 概率偏差扫描
□ 明日事件准备
□ 更新领域专家卡
```

---

> **⚡ 这条协议不是参考建议，是硬性流程。**
> **每一层都有它的存在理由，跳过任何一层都可能让你亏钱。**
> **严格执行这套流程，Polymarket 会成为你最稳定的收益来源之一。**
