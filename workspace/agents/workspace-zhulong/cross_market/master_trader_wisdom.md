# 交易大师智慧体系实战文档

> **版本**：v1.0  
> **创建日期**：2026-05-04  
> **适用系统**：烛龙量化交易系统  
> **核心理念**：将人类顶级交易智慧转化为可编码、可回测、可执行的量化规则

---

## 目录

1. [Jim Simons——因子挖掘与极致执行](#1-jim-simons西蒙斯文艺复兴)
2. [Jesse Livermore——关键点与金字塔加仓](#2-jesse-livermore利弗莫尔)
3. [Ray Dalio——原则体系与风险平价](#3-ray-dalio达利欧)
4. [George Soros——反身性与试仓确认](#4-george-soros索罗斯)
5. [Howard Marks——钟摆与第二层思维](#5-howard-marks霍华德马克斯)
6. [Nassim Taleb——黑天鹅与反脆弱](#6-nassim-taleb塔勒布)
7. [Paul Tudor Jones——宏观交易与资本保护](#7-paul-tudor-jones)
8. [Mark Minervini——VCP与SEPA策略](#8-mark-minervini)
9. [Peter Lynch——生活投资与六种股票](#9-peter-lynch)
10. [Buffett & Munger——安全边际与能力圈](#10-warren-buffett--charlie-munger)
11. [Ed Seykota——趋势跟踪与系统化](#11-ed-seykota)
12. [Richard Dennis——海龟法则与头寸规模](#12-richard-dennis海龟)
13. [Bruce Kovner——风险管理与快速认错](#13-bruce-kovner)
14. [Larry Williams——短线与季节性模式](#14-larry-williams)
15. [中国大师（Butian/FengLiu）——弱者体系与确定性](#15-中国大师butianfengliu)
16. [智慧速查表](#智慧速查表)

---

## 1. Jim Simons（西蒙斯/文艺复兴）

### 核心理念
> **"寻找微小的统计优势，通过高频交易和极致执行力，让概率成为你的朋友。"**

### 实战转化规则

1. **小优势复利法则**：任何因子只要IC>0.02且夏普>0.5，就值得交易，通过高换手放大收益
2. **因子正交化**：每个新因子必须与现有因子库相关性<0.3才能入库
3. **日度迭代机制**：每日检查因子衰减，每周淘汰IC下降>20%的因子
4. **执行成本最小化**：滑点容忍度<5bps，大单必须拆分（VWAP/TWAP）
5. **多时间框架套利**：同一标的在秒级/分钟级/小时级可能存在不同信号，全部捕捉

### 烛龙量化编码实现

```python
# 因子入库标准检查
def factor_admission_check(factor_ic, factor_sharpe, correlation_with_existing):
    return (
        factor_ic > 0.02 and 
        factor_sharpe > 0.5 and 
        correlation_with_existing < 0.3
    )

# 每日因子衰减扫描
def daily_factor_decay_scan(factor_library):
    decayed_factors = []
    for factor in factor_library:
        ic_change = (factor.current_ic - factor.historical_ic_mean) / factor.historical_ic_mean
        if ic_change < -0.2:
            decayed_factors.append(factor)
    return decayed_factors
```

---

## 2. Jesse Livermore（利弗莫尔）

### 核心理念
> **"等待关键点突破，做对了再加仓，让利润奔跑，截断亏损。"**

### 实战转化规则

1. **关键点突破确认**：价格突破前高/前低必须放量（成交量>20日均量1.5倍）
2. **金字塔加仓规则**：盈利后加仓，每次加仓量为前一次的50%，成本线移动至止损位
3. **Pivot Point识别**：关键点=历史支撑/阻力+整数关口+波动率收缩后的突破
4. **时间止损**：突破后3日内未延续趋势，平仓50%；5日内确认失败，全部平仓
5. **情绪极值逆向**：当市场情绪指标（恐慌/贪婪）达到极值时，准备反向操作

### 烛龙量化编码实现

```python
# 关键点突破检测
def pivot_breakout_detection(price, volume, lookback=20):
    pivot_high = price.rolling(lookback).max()
    volume_ma = volume.rolling(lookback).mean()
    
    breakout = (
        (price > pivot_high.shift(1)) & 
        (volume > volume_ma * 1.5)
    )
    return breakout

# 金字塔加仓计算
def pyramid_position_sizing(entry_price, current_price, base_position, add_ratio=0.5):
    profit_pct = (current_price - entry_price) / entry_price
    if profit_pct > 0.05:  # 盈利5%后开始加仓
        add_position = base_position * add_ratio ** ((profit_pct / 0.05) - 1)
        return min(add_position, base_position * 2)  # 最大加仓不超过初始2倍
    return 0
```

---

## 3. Ray Dalio（达利欧）

### 核心理念
> **"构建全天候投资组合，用风险平价而非资金平价，从错误中学习并系统化。"**

### 实战转化规则

1. **风险平价配置**：每个策略贡献的风险相等，而非资金相等
2. **全天候四象限**：增长↑通胀↑ / 增长↑通胀↓ / 增长↓通胀↑ / 增长↓通胀↓，各配置25%风险预算
3. **错误日志机制**：每笔亏损交易必须归档，标注错误类型（择时/选股/仓位/执行）
4. **压力测试常态化**：每周模拟2008/2020/2022三次危机场景，检查组合韧性
5. **相关性动态监控**：策略间相关性>0.6时触发预警，>0.7时强制降低权重

### 烛龙量化编码实现

```python
# 风险平价权重计算
def risk_parity_allocation(strategy_volatilities):
    inv_vol = [1/vol for vol in strategy_volatilities]
    total_inv_vol = sum(inv_vol)
    weights = [iv/total_inv_vol for iv in inv_vol]
    return weights

# 全天候四象限检测
def all_weather_regime_detection(gdp_growth, cpi_change):
    regime = None
    if gdp_growth > 0 and cpi_change > 0:
        regime = "growth_up_inflation_up"
    elif gdp_growth > 0 and cpi_change < 0:
        regime = "growth_up_inflation_down"
    elif gdp_growth < 0 and cpi_change > 0:
        regime = "growth_down_inflation_up"
    else:
        regime = "growth_down_inflation_down"
    return regime
```

---

## 4. George Soros（索罗斯）

### 核心理念
> **"市场参与者的偏见会改变基本面，在偏见极端时反向押注，用小仓位试探确认后重仓。"**

### 实战转化规则

1. **反身性监测指标**：构建"价格-基本面偏离度"指标，偏离>2σ时标记潜在反身性机会
2. **试仓-确认-加仓流程**：初始仓位5%，趋势确认（价格延续3日）后加至20%，逻辑验证后满仓
3. **情绪极端识别**：利用期权Put/Call比率、VIX、融资余额等构建情绪综合指数
4. **偏见跟踪框架**：持续跟踪市场叙事与实际数据的分歧，分歧扩大时加仓
5. **止损严格纪律**：试仓失败立即止损，不加仓摊平，最大单笔亏损<2%

### 烛龙量化编码实现

```python
# 反身性偏离度计算
def reflexivity_deviation(price, fundamental_value, lookback=60):
    price_fundamental_ratio = price / fundamental_value
    mean_ratio = price_fundamental_ratio.rolling(lookback).mean()
    std_ratio = price_fundamental_ratio.rolling(lookback).std()
    deviation_zscore = (price_fundamental_ratio - mean_ratio) / std_ratio
    return deviation_zscore

# 试仓-确认-加仓流程
def soros_position_scaling(deviation_zscore, confirmation_days, max_position):
    if abs(deviation_zscore) > 2.0:
        trial_position = max_position * 0.05  # 试仓5%
        if confirmation_days >= 3:
            return max_position * 0.2  # 确认后加至20%
        if confirmation_days >= 7:
            return max_position  # 逻辑验证后满仓
    return 0
```

---

## 5. Howard Marks（霍华德·马克斯）

### 核心理念
> **"市场如钟摆，在极端乐观与悲观之间摆动，用第二层思维在极端时逆向行动。"**

### 实战转化规则

1. **钟摆位置量化**：构建估值分位数+情绪分位数+流动性分位数的综合钟摆指数
2. **极端识别阈值**：钟摆指数>80%分位（贪婪）准备做空，<20%分位（恐惧）准备做多
3. **第二层思维清单**：每次交易前回答"市场共识是什么？我的看法有何不同？我为何正确？"
4. **周期位置判断**：识别当前处于牛市早期/中期/晚期或熊市早期/中期/晚期
5. **风险定价框架**：高风险资产在恐惧期被低估时才买入，低风险资产在贪婪期高估时卖出

### 烛龙量化编码实现

```python
# 钟摆指数构建
def pendulum_index(valuation_percentile, sentiment_percentile, liquidity_percentile):
    # 三个分位数加权平均（可调整权重）
    pendulum = (
        valuation_percentile * 0.4 + 
        sentiment_percentile * 0.35 + 
        liquidity_percentile * 0.25
    )
    return pendulum

# 第二层思维决策树
def second_level_thinking(market_consensus, my_view, confidence_level):
    """
    market_consensus: 市场共识观点
    my_view: 我的相反观点
    confidence_level: 信心等级（1-5）
    """
    if market_consensus == "极度乐观" and my_view == "谨慎悲观":
        action = "做空" if confidence_level >= 4 else "减仓"
    elif market_consensus == "极度悲观" and my_view == "谨慎乐观":
        action = "做多" if confidence_level >= 4 else "加仓"
    else:
        action = "观望"
    return action
```

---

## 6. Nassim Taleb（塔勒布）

### 核心理念
> **"黑天鹅不可预测但可准备，用杠铃策略在极端风险中获益，构建反脆弱系统。"**

### 实战转化规则

1. **杠铃配置**：90%资金在安全资产（国债/现金），10%在高赔率资产（期权/加密货币）
2. **尾部风险对冲**：每月用1-2%资产购买深度虚值看跌期权（VIX看涨/指数看跌）
3. **反脆弱性测试**：压力测试必须包含"历史上从未发生但可能发生"的场景
4. **凸性仓位**：只在盈亏比>3:1时下注，确保下跌有限、上涨无限
5. **冗余设计**：关键系统至少三重冗余，交易所账户分散至少3家

### 烛龙量化编码实现

```python
# 杠铃配置权重
def barbell_allocation(total_capital, safe_asset_pct=0.9, tail_hedge_pct=0.1):
    safe_allocation = total_capital * safe_asset_pct
    tail_hedge_allocation = total_capital * tail_hedge_pct
    return {
        "safe": safe_allocation,
        "tail_hedge": tail_hedge_allocation
    }

# 尾部风险对冲成本预算
def tail_hedge_budget(monthly_pnl, hedge_budget_pct=0.02):
    return abs(monthly_pNL) * hedge_budget_pct

# 凸性检查（盈亏比）
def convexity_check(potential_profit, potential_loss, min_ratio=3.0):
    return (potential_profit / potential_loss) >= min_ratio
```

---

## 7. Paul Tudor Jones

### 核心理念
> **"保护资本是第一原则，不等市场证明你错了就先撤退，宏观判断指导方向。"**

### 实战转化规则

1. **2%单笔止损铁律**：任何单笔交易亏损不超过总资金2%
2. **快速认错机制**：开仓后立即设置止损单，亏损触及1%时减仓50%
3. **宏观趋势确认**：必须在周线级别趋势方向上交易，不顺大势做短线
4. **进攻与防守切换**：胜率<40%时转为防守（降低仓位至半仓），胜率>60%时转为进攻
5. **每日损益监控**：单日亏损>1.5%停止开新仓，单日亏损>3%清仓观望

### 烛龙量化编码实现

```python
# 单笔止损检查
def single_trade_stop_loss(entry_value, current_loss_pct, max_loss_pct=0.02):
    return current_loss_pct >= max_loss_pct

# 每日损益熔断
def daily_pnl_circuit_breaker(daily_pnl_pct, warning_level=0.015, stop_level=0.03):
    if daily_pnl_pct <= -stop_level:
        return "FULL_STOP"
    elif daily_pnl_pct <= -warning_level:
        return "NO_NEW_POSITIONS"
    return "NORMAL"

# 宏观趋势确认
def macro_trend_confirmation(weekly_trend, trade_direction):
    return weekly_trend == trade_direction
```

---

## 8. Mark Minervini

### 核心理念
> **"寻找VCP（波动收缩形态）突破，用SEPA选股系统捕捉超级业绩股。"**

### 实战转化规则

1. **VCP形态识别**：波动幅度逐次收缩至少3次，最后一次收缩幅度<前次的50%
2. **SEPA选股标准**：EPS增长率>25% + 相对强度RS>80 + 行业领涨 + 机构持仓增加
3. **买点精确化**：突破 pivot point 时成交量必须放大150%以上
4. **止损位设定**：买入价下方8%为止损位，跌破 pivot point 立即止损
5. **持仓周期**：正确持仓平均4-8周，错误持仓平均2-5天

### 烛龙量化编码实现

```python
# VCP形态识别
def vcp_pattern_detection(price_data, min_contractions=3):
    swing_highs = find_swing_highs(price_data)
    swing_lows = find_swing_lows(price_data)
    
    contractions = []
    for i in range(1, len(swing_highs)):
        amplitude = (swing_highs[i] - swing_lows[i-1]) / swing_lows[i-1]
        if i > 0:
            prev_amplitude = contractions[-1]
            if amplitude < prev_amplitude * 0.5:  # 收缩50%以上
                contractions.append(amplitude)
    
    return len(contractions) >= min_contractions

# SEPA选股评分
def sepa_scoring(eps_growth, relative_strength, sector_rank, inst_ownership_change):
    score = 0
    if eps_growth > 0.25: score += 25
    if relative_strength > 80: score += 25
    if sector_rank <= 3: score += 25
    if inst_ownership_change > 0: score += 25
    return score  # 100分满分
```

---

## 9. Peter Lynch

### 核心理念
> **"投资你了解的东西，在生活中发现十倍股，用常识战胜华尔街。"**

### 实战转化规则

1. **六种股票分类**：
   - 缓慢增长型（分红>4%，市值>1000亿）→ 吃股息
   - 稳健增长型（增长10-12%，估值合理）→ 核心持仓
   - 快速增长型（增长20%+，PEG<1）→ 主攻方向
   - 周期型（业绩随经济周期）→ 择时交易
   - 资产隐蔽型（资产价值被低估）→ 深度研究
   - 困境反转型（危机中的好公司）→ 高赔率博弈

2. **PEG估值法**：PEG = PE/增长率，PEG<1低估，PEG>2高估
3. **生活中发现股票**：消费品牌、流行产品、身边热门产品→研究→投资
4. **不买不懂的东西**：每只股票必须有清晰的"投资故事"（为什么买、预期多少）
5. **持仓观察规则**：持仓股票每季度检查一次"故事是否还成立"

### 烛龙量化编码实现

```python
# PEG估值检查
def peg_valuation(pe_ratio, earnings_growth_rate):
    peg = pe_ratio / earnings_growth_rate
    if peg < 1:
        return "UNDERVALUED"
    elif peg > 2:
        return "OVERVALUED"
    else:
        return "FAIR"

# 六种股票分类
def lynch_stock_classification(eps_growth, dividend_yield, market_cap, pe_ratio):
    if dividend_yield > 0.04 and market_cap > 100e9:
        return "SLOW_GROWTH"
    elif 0.10 <= eps_growth <= 0.12:
        return "STALWART"
    elif eps_growth > 0.20 and pe_ratio / eps_growth < 1:
        return "FAST_GROWTH"
    # ... 其他分类逻辑
```

---

## 10. Warren Buffett & Charlie Munger

### 核心理念
> **"用安全边际买入优秀公司，在能力圈内下重注，时间是优质企业的朋友。"**

### 实战转化规则

1. **安全边际计算**：内在价值-价格 ≥ 30%折扣才买入
2. **能力圈边界**：只投资"看得懂"的行业，不懂的行业坚决不碰
3. **护城河评估**：
   - 品牌护城河（定价权）
   - 网络效应（用户越多越强）
   - 成本优势（规模经济）
   - 转换成本（客户难离开）
4. **集中持仓**：看懂的顶级机会可以集中到30%仓位
5. **永久持有清单**：护城河持续扩大+管理层优秀+合理估值→不卖

### 烛龙量化编码实现

```python
# 安全边际检查
def margin_of_safety(intrinsic_value, market_price, min_margin=0.30):
    discount = (intrinsic_value - market_price) / intrinsic_value
    return discount >= min_margin

# 护城河评分
def moat_scoring(brand_power, network_effect, cost_advantage, switching_cost):
    score = (
        brand_power * 0.25 + 
        network_effect * 0.25 + 
        cost_advantage * 0.25 + 
        switching_cost * 0.25
    )
    return score  # 0-100分

# 能力圈检查
def circle_of_competence_check(ticker, understood_sectors):
    sector = get_sector(ticker)
    return sector in understood_sectors
```

---

## 11. Ed Seykota

### 核心理念
> **"趋势是你的朋友，输得起小钱才能留住大趋势，情绪管理比策略更重要。"**

### 实战转化规则

1. **趋势跟踪系统**：只做多或做空当前趋势方向，不抄底不摸顶
2. **小止损大止盈**：止损<5%，止盈跟踪至趋势反转
3. **系统化执行**：交易规则写进代码，人为干预仅在极端情况
4. **情绪日记**：每日记录交易时的情绪状态（恐惧/贪婪/平静）
5. **仓位与风险匹配**：亏损时自动降低仓位，盈利时适当增加

### 烛龙量化编码实现

```python
# 趋势方向判断
def trend_direction(price, ma_short=50, ma_long=200):
    return "UP" if price[-ma_short:].mean() > price[-ma_long:].mean() else "DOWN"

# 动态仓位调整
def dynamic_position_sizing(current_capital, initial_capital, base_risk=0.02):
    drawdown = (initial_capital - current_capital) / initial_capital
    if drawdown > 0.10:
        return base_risk * 0.5  # 回撤超10%，仓位减半
    elif drawdown > 0.20:
        return base_risk * 0.25  # 回撤超20%，仓位四分之一
    return base_risk

# 情绪状态记录
def log_emotional_state(date, pre_trade_emotion, post_trade_emotion, pnl):
    emotion_log = {
        "date": date,
        "pre_emotion": pre_trade_emotion,  # 1-10
        "post_emotion": post_trade_emotion,
        "pnl": pnl
    }
    return emotion_log
```

---

## 12. Richard Dennis（海龟）

### 核心理念
> **"交易是可以教授的，机械系统化执行，头寸规模决定成败。"**

### 实战转化规则

1. **N值波动率**：N = (最高-最低)/收盘价的20日指数平均，用于衡量波动
2. **头寸单位**：1单位 = 1%总资金/N，单市场最多4单位，高度相关市场最多6单位
3. **突破系统**：
   - 系统1：20日高点突破买入，10日低点突破卖出（短期）
   - 系统2：55日高点突破买入，20日低点突破卖出（长期）
4. **金字塔加仓**：盈利0.5N后加仓，每次加仓不超过1单位，最多加仓3次
5. **止损硬规则**：止损位=买入价-2N，严格执行，不加仓摊平

### 烛龙量化编码实现

```python
# N值计算（海龟波动率）
def calculate_n(high, low, close, lookback=20):
    true_range = max(high - low, abs(high - close.shift(1)), abs(low - close.shift(1)))
    n = true_range.ewm(span=lookback).mean()
    return n

# 头寸单位计算
def position_unit(total_capital, n, risk_pct=0.01):
    return (total_capital * risk_pct) / n

# 突破信号检测
def turtle_breakout_signal(price, system=1):
    if system == 1:
        entry_signal = price == price.rolling(20).max()
        exit_signal = price == price.rolling(10).min()
    else:  # system == 2
        entry_signal = price == price.rolling(55).max()
        exit_signal = price == price.rolling(20).min()
    return entry_signal, exit_signal
```

---

## 13. Bruce Kovner

### 核心理念
> **"风险管理是交易的全部，快速认错比坚持正确更重要，永远要有Plan B。"**

### 实战转化规则

1. **风险预算制度**：每日最大亏损预算=总资金的1%，触及即停止交易
2. **快速认错标准**：开仓理由消失或亏损触及止损，立即平仓，不犹豫
3. **相关性检查**：新增仓位前检查与现有持仓的相关性，相关>0.5则降低权重
4. **Plan B清单**：每笔交易开仓前必须制定3种情况的应对方案
5. **杠杆控制**：最大杠杆倍数不超过3倍，极端行情下降至1倍

### 烛龙量化编码实现

```python
# 风险预算检查
def risk_budget_check(daily_pnl, max_daily_loss_pct=0.01):
    return daily_pnl >= -max_daily_loss_pct

# 快速认错触发
def quick_exit_check(entry_reason_valid, current_loss_pct, max_loss_pct=0.02):
    return (not entry_reason_valid) or (current_loss_pct >= max_loss_pct)

# 相关性检查
def correlation_check(new_position, existing_portfolio, max_correlation=0.5):
    for position in existing_portfolio:
        corr = calculate_correlation(new_position, position)
        if corr > max_correlation:
            return False
    return True
```

---

## 14. Larry Williams

### 核心理念
> **"短线交易需要精确的时机，利用季节性模式和波动率突破捕捉快速移动。"**

### 实战转化规则

1. **威廉指标应用**：%R超买（>-20）卖出信号，%R超卖（<-80）买入信号
2. **季节性模式**：
   - 月初效应：每月前5个交易日倾向做多
   - 周末效应：周五收盘前买入，周一开盘卖出
   - 年末效应：12月最后5个交易日买入
3. **波动率突破**：价格突破昨日波动范围（最高-最低）的某个比例时入场
4. **快速止盈止损**：目标盈利2-5%，止损1-2%，持仓时间<5天
5. **资金管理**：单笔风险不超过总资金1%

### 烛龙量化编码实现

```python
# 威廉%R指标
def williams_pct_r(high, low, close, lookback=14):
    highest_high = high.rolling(lookback).max()
    lowest_low = low.rolling(lookback).min()
    pct_r = (highest_high - close) / (highest_high - lowest_low) * -100
    return pct_r

# 季节性模式检测
def seasonal_pattern_check(date):
    day_of_month = date.day
    day_of_week = date.weekday()
    month = date.month
    
    signals = []
    if day_of_month <= 5:  # 月初效应
        signals.append("MONTH_START_BULLISH")
    if day_of_week == 4:  # 周五（周末效应）
        signals.append("WEEKEND_EFFECT")
    if month == 12 and day_of_month >= 27:  # 年末效应
        signals.append("YEAR_END_RALLY")
    return signals

# 波动率突破
def volatility_breakout(today_open, yesterday_range, breakout_pct=0.5):
    upper_breakout = today_open + yesterday_range * breakout_pct
    lower_breakout = today_open - yesterday_range * breakout_pct
    return upper_breakout, lower_breakout
```

---

## 15. 中国大师（Butian/FengLiu）

### 核心理念
> **"承认自己的弱者地位，只做高确定性机会，用极致耐心等待击球区。"**

### 实战转化规则

1. **弱者体系构建**：
   - 承认信息劣势（相对机构）
   - 承认研究劣势（相对专业团队）
   - 承认速度劣势（相对高频）
   - → 只在自己有优势的地方出手

2. **确定性评分**：每次交易前评分（1-10），只有≥8分才出手
   - 信息确定性（理解程度）
   - 估值确定性（安全边际）
   - 时间确定性（催化剂明确）
   - 趋势确定性（技术面支持）

3. **击球区等待**：好公司+好价格+好时机三要素齐全才出手，否则空仓

4. **仓位与确定性匹配**：
   - 确定性10分：满仓
   - 确定性9分：半仓
   - 确定性8分：轻仓
   - 确定性<8分：空仓

5. **极致耐心**：宁可错过100次机会，不错误出手1次

### 烛龙量化编码实现

```python
# 确定性评分系统
def certainty_scoring(understanding_score, valuation_score, catalyst_score, technical_score):
    total_score = (
        understanding_score * 0.3 + 
        valuation_score * 0.3 + 
        catalyst_score * 0.2 + 
        technical_score * 0.2
    )
    return total_score  # 1-10分

# 击球区判断
def strike_zone_check(good_company, good_price, good_timing):
    return good_company and good_price and good_timing

# 确定性匹配仓位
def certainty_based_position(certainty_score, max_position):
    if certainty_score >= 10:
        return max_position
    elif certainty_score >= 9:
        return max_position * 0.5
    elif certainty_score >= 8:
        return max_position * 0.25
    else:
        return 0  # 空仓
```

---

## 智慧速查表

| 大师 | 一句话精华 | 核心实战规则 |
|------|-----------|-------------|
| **Jim Simons** | 小优势×高频×极致执行 | IC>0.02即可交易，因子相关性<0.3，日度迭代 |
| **Jesse Livermore** | 关键点突破+金字塔加仓 | 放量突破进场，盈利5%加仓，止损移动 |
| **Ray Dalio** | 风险平价+全天候+原则化 | 策略风险贡献相等，四象限配置，错误归档 |
| **George Soros** | 反身性+试仓确认+重仓 | 偏离>2σ试仓，确认后加仓，情绪极端反向 |
| **Howard Marks** | 钟摆极端+第二层思维 | 钟摆指数<20%做多，>80%做空，逆向共识 |
| **Nassim Taleb** | 杠铃+反脆弱+尾部对冲 | 90%安全+10%高风险，每月买虚值期权 |
| **Paul Tudor Jones** | 保护资本+快速认错+宏观 | 单笔止损2%，日亏1.5%停仓，顺大势交易 |
| **Mark Minervini** | VCP突破+SEPA选股 | 波动收缩≥3次，RS>80，突破放量150% |
| **Peter Lynch** | 生活中发现+PEG<1 | 六种分类法，PEG估值，每季检查"故事" |
| **Buffett & Munger** | 安全边际+能力圈+护城河 | 30%折扣买入，护城河评分，集中持仓 |
| **Ed Seykota** | 趋势跟踪+系统化+情绪管理 | 只做趋势方向，小止损大止盈，情绪日记 |
| **Richard Dennis** | 机械系统+N值头寸规模 | 20/55日突破，1单位=1%资金/N，止损2N |
| **Bruce Kovner** | 风险管理+快速认错+Plan B | 日亏1%停止，开仓前3种方案，相关性<0.5 |
| **Larry Williams** | 短线时机+季节性+波动突破 | %R超买卖信号，月初/周末效应，持仓<5天 |
| **Butian/FengLiu** | 弱者体系+确定性+耐心 | 确定性≥8分才出手，仓位匹配确定性 |

---

> **文档结束**  
> *创建日期：2026-05-04*  
> *版本：v1.0*  
> *适用于：烛龙量化交易系统*
