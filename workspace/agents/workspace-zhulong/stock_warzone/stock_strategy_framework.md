# A股策略开发框架 (Stock Strategy Framework)

> **版本**: V1.0 实战版  
> **目标**: 从想法到实盘的标准化流水线  
> **适用**: A股量化策略全生命周期管理

---

## 一、策略分层架构

### 六层标准化结构

```
┌─────────────────────────────────────────┐
│  Layer 6: 执行层 (Execution)            │  ← 下单、滑点、成交确认
├─────────────────────────────────────────┤
│  Layer 5: 风控层 (Risk Control)         │  ← 止损、仓位、熔断
├─────────────────────────────────────────┤
│  Layer 4: 仓位层 (Position Sizing)       │  ← 资金分配、杠杆控制
├─────────────────────────────────────────┤
│  Layer 3: 择时层 (Timing)                │  ← 入场/出场时机
├─────────────────────────────────────────┤
│  Layer 2: 选股层 (Selection)             │  ← 股票池构建、排序
├─────────────────────────────────────────┤
│  Layer 1: 数据层 (Data)                  │  ← 清洗、对齐、特征工程
└─────────────────────────────────────────┘
```

---

## 二、选股逻辑框架

### 2.1 股票池构建流程

```python
# 标准选股流程模板
def build_stock_pool(context):
    # Step 1: 基础过滤 (全市场 → 可交易池)
    universe = get_all_securities(types=['stock'], date=context.current_dt)
    
    # 剔除ST/*ST
    universe = universe[~universe.is_st]
    
    # 剔除停牌
    universe = universe[universe.is_trade]
    
    # 剔除次新股 (上市<60天)
    universe = universe[universe.days_listed > 60]
    
    # Step 2: 流动性过滤
    # 日均成交额 > 5000万
    avg_amount = history(20, '1d', 'amount', universe.index).mean()
    universe = universe[avg_amount > 50e6]
    
    # Step 3: 基本面过滤 (可选)
    # 市值范围
    market_cap = get_fundamentals(query(valuation.market_cap)
                                   .filter(valuation.code.in_(universe.index)))
    universe = universe[(market_cap > 10) & (market_cap < 1000)]  # 10亿-1000亿
    
    # Step 4: 因子评分
    scores = calculate_factor_scores(universe.index)
    
    # Step 5: 排序选股
    selected = scores.sort_values(ascending=False).head(20)
    
    return selected.index.tolist()
```

### 2.2 多因子评分模型

| 因子类别 | 代表因子 | 权重建议 | 计算方式 |
|----------|----------|----------|----------|
| **价值** | PE_TTM, PB, PS | 20% | 倒数排名 |
| **质量** | ROE, GP, 资产负债率 | 25% | 正态化排名 |
| **动量** | 20日收益, 60日收益 | 20% | 直接排名 |
| **波动** | 20日波动率, ATR | 15% | 倒数排名 |
| **流动性** | 换手率, 成交额 | 10% | 适中区间 |
| **技术** | MACD, RSI偏离 | 10% | 信号强度 |

### 2.3 行业中性化

```python
def industry_neutralize(scores, stocks):
    """行业中性化: 每个行业内独立排名"""
    industries = get_industry(stocks)
    neutral_scores = pd.Series(index=stocks)
    
    for industry in industries.unique():
        industry_stocks = industries[industries == industry].index
        industry_scores = scores[industry_stocks]
        # 行业内z-score标准化
        neutral_scores[industry_stocks] = (
            industry_scores - industry_scores.mean()
        ) / industry_scores.std()
    
    return neutral_scores
```

---

## 三、择时逻辑框架

### 3.1 择时信号类型

| 信号类型 | 适用策略 | 典型实现 | 优缺点 |
|----------|----------|----------|--------|
| **趋势确认** | 动量策略 | 价格>MA20且斜率>0 | 顺势，滞后 |
| **均值回归** | 反转策略 | RSI<30或价格<布林带下轨 | 逆势，假信号多 |
| **突破确认** | 趋势启动 | 价格突破20日高点 | 及时，假突破 |
| **波动率过滤** | 全策略 | VIX>30减仓 | 避灾，错过反弹 |
| **宏观择时** | 配置策略 | 股债收益差<均值-2σ | 长期有效，低频 |

### 3.2 标准择时模板

```python
# 趋势择时示例
def trend_timing(context):
    # 大盘指数
    index_data = get_price('000001.XSHG', count=60, end_date=context.current_dt)
    
    # 计算均线
    ma20 = index_data['close'].rolling(20).mean().iloc[-1]
    ma60 = index_data['close'].rolling(60).mean().iloc[-1]
    current = index_data['close'].iloc[-1]
    
    # 趋势判断
    if current > ma20 > ma60:
        return 'bull'      # 多头
    elif current < ma20 < ma60:
        return 'bear'      # 空头
    else:
        return 'neutral'   # 震荡

# 波动率择时示例  
def volatility_timing(context):
    # 计算市场波动率
    index_data = get_price('000001.XSHG', count=20, end_date=context.current_dt)
    returns = index_data['close'].pct_change().dropna()
    vol = returns.std() * np.sqrt(252)  # 年化波动率
    
    if vol > 0.30:  # 波动率>30%
        return 'high_vol'  # 减仓/空仓
    elif vol < 0.15:
        return 'low_vol'   # 加仓
    else:
        return 'normal'
```

### 3.3 复合择时规则

```python
def composite_timing(context):
    """多因子复合择时"""
    signals = {
        'trend': trend_timing(context),      # 趋势信号
        'vol': volatility_timing(context),   # 波动信号
        'sentiment': sentiment_timing(context),  # 情绪信号
    }
    
    # 投票机制
    bull_votes = sum([s in ['bull', 'low_vol', 'greedy'] for s in signals.values()])
    bear_votes = sum([s in ['bear', 'high_vol', 'fear'] for s in signals.values()])
    
    if bull_votes >= 2:
        return 1.0   # 满仓
    elif bear_votes >= 2:
        return 0.0   # 空仓
    else:
        return 0.5   # 半仓
```

---

## 四、风控框架

### 4.1 三层风控体系

```
┌────────────────────────────────────────┐
│  L1: 账户级风控 (Account Level)        │
│  - 总回撤限制 (如: 单日<2%, 累计<15%)   │
├────────────────────────────────────────┤
│  L2: 策略级风控 (Strategy Level)       │
│  - 策略最大回撤、夏普<1.5暂停           │
├────────────────────────────────────────┤
│  L3: 个股级风控 (Position Level)       │
│  - 单票止损、行业集中度                  │
└────────────────────────────────────────┘
```

### 4.2 标准风控实现

```python
# 个股止损
def check_stop_loss(context, stock, stop_pct=0.08):
    """固定百分比止损"""
    position = context.portfolio.positions[stock]
    if position.value > 0:
        avg_cost = position.avg_cost
        current_price = position.price
        
        if current_price < avg_cost * (1 - stop_pct):
            order_target(stock, 0)
            log.info(f"止损卖出 {stock}, 亏损 {(1-current_price/avg_cost)*100:.1f}%")

# 跟踪止损
def check_trailing_stop(context, stock, atr_multiple=2):
    """ATR跟踪止损"""
    position = context.portfolio.positions[stock]
    if position.value > 0:
        highs = attribute_history(stock, 20, '1d', ['high'])['high']
        highest = highs.max()
        atr = calculate_atr(stock, 14)
        
        stop_price = highest - atr_multiple * atr
        current = position.price
        
        if current < stop_price:
            order_target(stock, 0)
            log.info(f"跟踪止损 {stock}, 价格 {current:.2f} < 止损线 {stop_price:.2f}")

# 账户熔断
def check_account_circuit_breaker(context):
    """账户级熔断"""
    total_value = context.portfolio.total_value
    initial_value = context.initial_value
    
    # 单日回撤检查
    daily_return = (total_value - context.previous_value) / context.previous_value
    if daily_return < -0.05:  # 单日亏损>5%
        log.warning("单日回撤>5%, 暂停新开仓")
        context.pause_trading = True
    
    # 累计回撤检查
    max_drawdown = (initial_value - total_value) / initial_value
    if max_drawdown > 0.15:  # 累计回撤>15%
        log.error("累计回撤>15%, 清仓观望")
        for stock in list(context.portfolio.positions.keys()):
            order_target(stock, 0)
```

### 4.3 仓位风控

| 风控项 | 阈值 | 动作 |
|--------|------|------|
| 单票仓位上限 | 20% | 禁止超配 |
| 行业集中度 | 30% | 告警/限制 |
| 总仓位上限 | 100% | 禁止超仓 |
| 现金最低比例 | 10% | 强制保留 |
| 杠杆上限 | 1.5x | 禁止加杠杆 |

---

## 五、执行框架

### 5.1 调仓执行流程

```python
def rebalance(context, target_stocks):
    """标准调仓流程"""
    # 1. 检查择时信号
    market_signal = composite_timing(context)
    if market_signal == 0:
        log.info("择时信号为空仓，跳过调仓")
        return
    
    # 2. 计算目标仓位
    target_positions = {}
    total_weight = market_signal  # 根据择时调整总仓位
    
    for stock in target_stocks:
        target_positions[stock] = total_weight / len(target_stocks)
    
    # 3. 清仓不在目标池的
    for stock in list(context.portfolio.positions.keys()):
        if stock not in target_positions:
            order_target(stock, 0)
    
    # 4. 调整目标持仓
    for stock, weight in target_positions.items():
        target_value = context.portfolio.total_value * weight
        order_target_value(stock, target_value)
```

### 5.2 订单类型选择

| 场景 | 订单类型 | 说明 |
|------|----------|------|
| 开盘调仓 | 市价单 | 集合竞价后第一时间成交 |
| 尾盘调仓 | 限价单 | 14:55定价，避免冲击 |
| 大额交易 | TWAP/VWAP | 拆单执行，降低冲击 |
| 紧急止损 | 市价单 | 立即成交优先