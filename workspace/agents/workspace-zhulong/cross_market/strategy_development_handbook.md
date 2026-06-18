# 量化策略开发实战手册
## 从0到实盘的完整开发经验

> **版本**：v1.0 实战版  
> **适用**：A股/港股/美股/加密货币/预测市场  
> **核心原则**：先算风险，再算收益；用概率说话，用代码证明

---

## 第一部分：因子开发实战

### 1.1 因子选择方法论

#### 因子来源分类

| 因子大类 | 具体因子示例 | 适用市场 | 衰减周期 |
|---------|-------------|---------|---------|
| **价值因子** | PE_TTM、PB、PS、股息率、EV/EBITDA | A股/美股 | 12-24月 |
| **质量因子** | ROE稳定性、毛利率稳定性、现金流质量 | 全市场 | 18-36月 |
| **动量因子** | 20日/60日/120日收益率、行业动量 | 全市场 | 3-9月 |
| **反转因子** | 1月反转、3月反转、极端收益反转 | A股/加密 | 1-3月 |
| **情绪因子** | 换手率异常、融资余额变化、期权PCR | A股/美股 | 1-6月 |
| **资金行为** | 主力资金流向、大单净流入、北向资金 | A股/港股 | 1-3月 |
| **宏观切换** | 利率周期、信用周期、库存周期 | 全市场 | 6-18月 |
| **波动率状态** | 已实现波动率、IV-HV差、波动率锥 | 美股/加密 | 1-3月 |

#### 单因子测试完整流程

**步骤1：IC值计算（Spearman Rank IC）**

```python
def calculate_ic(factor_values, forward_returns):
    """
    计算Spearman Rank IC
    - factor_values: 因子值序列 (n,)
    - forward_returns: 未来N期收益 (n,) 通常N=1,5,10,20日
    - 返回：IC值（-1到1），p值
    """
    from scipy.stats import spearmanr
    ic, p_value = spearmanr(factor_values, forward_returns)
    return ic, p_value

# 执行标准
# - 计算频率：日频/周频
# - 回看周期：至少36个月（A股）/ 60个月（美股）
# - IC阈值：|IC| > 0.03 且 p-value < 0.05
# - 方向判断：IC>0为正向因子，IC<0为反向因子
```

**步骤2：分组收益测试（5组或10组）**

```python
def quintile_test(factor_df, forward_return_col='return_5d'):
    """
    五分位测试
    1. 每期按因子值排序，等分为5组（Q1最低，Q5最高）
    2. 计算每组下期平均收益
    3. 计算多空对冲收益（Q5-Q1或Q1-Q5，取决于IC方向）
    
    验收标准：
    - 单调性：Q1<Q2<Q3<Q4<Q5（或反向）
    - 多空收益：年化>5%
    - 最大回撤：<15%
    """
    factor_df['group'] = pd.qcut(factor_df['factor'], 5, labels=['Q1','Q2','Q3','Q4','Q5'])
    group_returns = factor_df.groupby(['date','group'])[forward_return_col].mean()
    long_short = group_returns.xs('Q5', level='group') - group_returns.xs('Q1', level='group')
    return group_returns, long_short
```

**步骤3：IC监控指标体系**

| 指标 | 计算公式 | 健康阈值 | 预警阈值 |
|-----|---------|---------|---------|
| **IC均值** | mean(IC_t) | >0.03 | <0.02 |
| **IC标准差** | std(IC_t) | <0.15 | >0.20 |
| **ICIR** | mean(IC) / std(IC) | >0.3 | <0.2 |
| **IC胜率** | count(IC>0)/total | >55% | <50% |
| **IC半衰期** | -ln(2)/ln(ρ) | 3-12月 | <2月或>18月 |

```python
def ic_half_life(ic_series):
    """IC序列半衰期：IC_t = ρ*IC_{t-1} + ε, 半衰期=-ln(2)/ln(ρ)"""
    from statsmodels.tsa.ar_model import AutoReg
    ic_clean = ic_series.dropna()
    model = AutoReg(ic_clean, lags=1).fit()
    rho = model.params[1]
    half_life = -np.log(2) / np.log(abs(rho))
    return half_life
```

**步骤4：P值检验（统计显著性）**

```python
def significance_test(ic_series):
    """t检验 H0: mean(IC)=0, p<0.05为显著"""
    from scipy import stats
    t_stat, p_value = stats.ttest_1samp(ic_series.dropna(), 0)
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'is_significant': p_value < 0.05,
        'confidence_95': (ic_series.mean() - 1.96*ic_series.std(), 
                         ic_series.mean() + 1.96*ic_series.std())
    }
```

### 1.2 过拟合检测

#### 数据集划分（时间序列专用）

```
[========训练集70%=======][==验证集15%==][==测试集15%==]
2018-01    2021-06        2022-06        2023-06      2024-06

关键原则：
1. 严格按时间划分，禁止随机打乱
2. 训练集用于模型拟合，验证集用于超参调优
3. 测试集仅用于最终评估（只能用一次）
```

#### 时间序列交叉验证

**方法A：滚动窗口（Rolling Window）**

```python
def rolling_window_cv(data, train_window=756, val_window=63):
    """滚动窗口交叉验证，训练窗口3年（756日），验证窗口1季度（63日）"""
    results = []
    for i in range(0, len(data) - train_window - val_window, val_window):
        train = data.iloc[i:i+train_window]
        val = data.iloc[i+train_window:i+train_window+val_window]
        model = train_strategy(train)
        sharpe = evaluate_sharpe(model, val)
        results.append(sharpe)
    return np.mean(results), np.std(results)
```

**方法B：扩展窗口（Expanding Window）**

```python
def expanding_window_cv(data, min_train=756, step=63):
    """扩展窗口：训练集逐步扩大，更接近实盘场景"""
    results = []
    for end_idx in range(min_train, len(data)-63, step):
        train = data.iloc[:end_idx]
        val = data.iloc[end_idx:end_idx+63]
        model = train_strategy(train)
        sharpe = evaluate_sharpe(model, val)
        results.append(sharpe)
    return results
```

#### 参数扰动测试（敏感度分析）

```python
def parameter_perturbation_test(strategy, base_params, perturb_pct=0.1):
    """
    对每个参数±10%，检查夏普变化
    验收标准：
    - 夏普变化<20%：稳定
    - 夏普变化>50%：过拟合嫌疑
    """
    base_sharpe = backtest(strategy, base_params)
    sensitivity = {}
    for param_name, param_value in base_params.items():
        perturbed = base_params.copy()
        perturbed[param_name] = param_value * (1 + perturb_pct)
        sharpe_plus = backtest(strategy, perturbed)
        perturbed[param_name] = param_value * (1 - perturb_pct)
        sharpe_minus = backtest(strategy, perturbed)
        sens = abs((sharpe_plus - sharpe_minus) / base_sharpe) / (2 * perturb_pct)
        sensitivity[param_name] = sens
    return sensitivity
```

#### DSR校正（Deflated Sharpe Ratio）

```python
def calculate_dsr(sharpe, T, skewness, kurtosis, N_trials=1):
    """
    DSR > 0.5：策略有效
    DSR < 0：策略无效（纯运气）
    考虑：样本长度T、收益偏度峰度、多重试验次数N
    """
    var_sr = (1 - skewness * sharpe + (kurtosis - 1) * sharpe**2 / 4) / (T - 1)
    if N_trials > 1:
        var_sr += np.log(N_trials) / T  # 多重试验Bonferroni校正
    dsr = sharpe * (1 - var_sr / sharpe**2) if sharpe != 0 else 0
    return dsr
```

#### PBO计算（Probability of Backtest Overfitting）

```python
def calculate_pbo(returns_matrix, S=16):
    """
    CSCV方法：PBO < 0.1 过拟合风险低；PBO > 0.5 严重过拟合
    returns_matrix: (n_periods, n_strategies)
    """
    from itertools import combinations
    n_periods, n_strategies = returns_matrix.shape
    group_size = n_periods // S
    rankings = []
    for test_groups in combinations(range(S), S//2):
        train_groups = [i for i in range(S) if i not in test_groups]
        train_mask = np.isin(np.arange(n_periods)//group_size, train_groups)
        test_mask = ~train_mask
        train_ret = returns_matrix[train_mask]
        test_ret = returns_matrix[test_mask]
        train_sharpe = np.mean(train_ret, axis=0) / np.std(train_ret, axis=0)
        best_idx = np.argmax(train_sharpe)
        test_sharpe = np.mean(test_ret, axis=0) / np.std(test_ret, axis=0)
        test_rank = np.sum(test_sharpe[best_idx] < test_sharpe) / n_strategies
        rankings.append(test_rank)
    return np.mean(rankings)
```

### 1.3 因子组合

#### 因子相关性监控

```python
def factor_correlation_monitor(factor_returns_df):
    """
    月频计算因子相关系数
    监控规则：
    - 平均相关性>0.6：需要合并或淘汰
    - 相关性>0.8：必须合并
    - 相关性<-0.6：反转配置
    """
    rolling_corr = factor_returns_df.rolling(60).corr()
    avg_corr = rolling_corr.groupby(level=0).apply(
        lambda x: (x.values.sum() - len(x)) / (len(x)-1) / len(x)
    )
    return avg_corr
```

#### 因子权重分配方法

| 方法 | 原理 | 适用场景 | 注意事项 |
|------|------|---------|---------|
| **等权** | 所有因子权重相同 | 起步阶段 | 简单但忽略表现差异 |
| **ICIR加权** | 权重∝ICIR | 因子稳定期 | IR低的因子被严重压制 |
| **最优化** | 最大化组合ICIR | 策略成熟期 | 可能过度集中 |
| **滚动ICIR** | 12个月滚动窗口 | 动态环境 | 窗口期选择敏感 |
| **机器学习** | XGBoost/Transformer | 非线性关系 | 过拟合风险高 |

```python
def icir_weighting(factor_ics, window=12):
    """ICIR加权：权重 = max(ICIR,0)/sum(max(ICIR,0))，月频再平衡"""
    icir = factor_ics.rolling(window).mean() / factor_ics.rolling(window).std()
    weights = icir.clip(lower=0)
    weights = weights.div(weights.sum(axis=1), axis=0)
    return weights
```

#### 因子衰减后的替补机制

```
H1因子（核心，IC均值>0.05, ICIR>0.5）
  → 满权重，周频IC监测
  → 降级条件：连续2个月IC<0.02

H2因子（辅助，IC>0.03, ICIR>0.3）
  → 半权重，双周监测
  → 升级条件：连续3个月IC>0.04

H3因子（备选，IC>0.01, ICIR>0.15）
  → 1/4权重或研究池，月频监测
  → 激活条件：H1降级时替补

替补流程：
1. H1触发降级条件 → 2. H2/H3池中ICIR最高替补
3. 替补因子先1倍权重运行 → 4. 原H1降为H3观察3个月
5. 若3个月后IC恢复，重新升级
```

---

## 第二部分：回测实战检查清单

### 前置检查（数据准备阶段）

```
□ 【数据范围确认】
   - 数据覆盖区间：至少5年（A股）/ 10年（美股）
   - 覆盖完整市场周期：至少1次牛市+1次熊市
   - 包含极端行情：2020熔断、2022LUNA崩盘、2024日元carry trade
   - 操作：拉取数据后检查start_date~end_date区间完整性

□ 【数据质量检查】
   - 缺失值比例：<1%（时间序列数据）
   - 异常值处理：超过5σ的极值标记后决定剔除或winsorize
   - 时间序列对齐：多源数据时间戳精确到秒级对齐
   - 操作：df.isnull().sum()/len(df)，df.describe()检查极值

□ 【上市状态确认】
   - 只保留正常交易状态股票
   - 剔除ST/*ST（A股）/低于$1（美股）/停牌>20交易日
   - 操作：filter(status='正常交易')
```

### 核心偏差检查

```
□ 【未来函数检查】—— 最致命的bug
   - 检查点：是否使用了"未来才能知道"的数据
   - 常见陷阱：
     ✓ 用当天收盘价计算开仓信号（实盘中信号应在收盘后生成）
     ✓ 使用未来财报数据（财报发布日期vs覆盖期混淆）
     ✓ 使用复权因子计算历史收益（复权因子本身是未来函数）
   - 防御方法：
     1. 所有信号使用T-1日收盘后数据计算
     2. 数据用.shift(1)前移一天
     3. 回测循环中显式：signal_time < trade_time

□ 【前视偏差检查】—— Future Look-Ahead Bias
   - 检查点：计算因子时是否"偷看"了未来价格信息
   - 常见陷阱：
     ✓ 计算20日收益率时混入未来数据
     ✓ 用t+1到t+21的close计算20日收益作为t日因子值
     ✓ 使用rolling窗口时默认包含当前值
   - 防御方法：
     1. 所有因子计算用.shift(1)确保不含当前信息
     2. forward_returns = (future_price / current_price) - 1
     3. 回测框架中用shift(滞后)统一处理

□ 【幸存者偏差检查】—— Survivorship Bias
   - 检查点：回测池是否包含历史中退市/摘牌的股票
   - 常见陷阱：只用了当前还在交易的股票集合
   - 防御方法：
     1. 回测开始日的股票池必须是当时真实存在的全部股票
     2. 使用退市公司数据库补全历史数据
     3. 无法实现时，额外扣除1-2%作为幸存者偏差惩罚

□ 【时间戳对齐检查】
   - 常见陷阱：
     ✓ A股收盘价(15:00)和期货结算价时间不一致
     ✓ 财报发布日期和数据供应商标注日期有1-2天漂移
     ✓ 跨市场数据时区未校准（美股vsA股跨夜）
   - 防御方法：
     1. 所有时间戳统一为UTC+8(A股)/UTC-5(美股)
     2. 使用pd.merge_asof进行非精确时间对齐
     3. 日频数据统一使用date类型，不接受datetime混用
```

### 交易成本检查

```
□ 【手续费设置】
   - A股：万1.0-万1.5（含规费），卖出印花税万10
   - 港股：千1.0-千2.5+印花税万10+结算费万2
   - 美股：$0.005/股或$1/笔取大值，期权$0.5-1.5/张
   - 加密现货：万5吃单、免手续费挂单（按VIP等级）
   - 加密永续：万2.5-万4吃单、万1.5-万2.5挂单
   - 误区：用"平均费率"而非"最低费率"

□ 【滑点预估（按市值分档）】
   - A股<500万：0.05-0.10%(约1-2跳) | 500万-2000万：0.10-0.25%
   - A股2000万-1亿：0.25-0.50% | >1亿：0.50-1.00%
   - 加密BTC/ETH：0.02-0.05% | 山寨币：0.10-0.50%
   - 美股大盘股：0.03-0.08% | 小盘股：0.15-0.40%
   - 实操：至少用"买卖价差的1.5倍"作为保守估计

□ 【冲击成本（Almgren-Chriss简化版）】
   - 冲击成本 = 固定冲击 + 临时冲击
   - 固定冲击系数：A股0.01-0.05，加密0.02-0.10
   - 临时冲击系数：A股0.005-0.02，加密0.01-0.05
   - 交易量占比日成交量<5%：冲击可忽略
   - 占比5-15%：冲击约0.1-0.3%
   - 占比>15%：冲击可能>0.5%

□ 【总交易成本=手续费×2+滑点×1.5+冲击×0.5】
   回测中统一用保守方案，宁可高估不要低估
```

### 市场约束检查

```
□ 【成交量限制检查】
   - 单笔交易量 < 日均成交量的5%(A股)/10%(美股)
   - 单笔交易量 < 卖一挂单量的30%
   - 实操：成交额<500万的股票禁用

□ 【涨跌停限制检查（A股）】
   - 主板±10%，创业板/科创板±20%
   - 涨停无法买入，跌停无法卖出
   - 实操：涨停标记为"无法买入"，跌停计提潜在损失

□ 【停牌处理检查】
   - 停牌期间无法交易
   - 复牌后可能补跌/补涨
   - 实操：停牌>20交易日强制移出持仓

□ 【最小交易单位检查】
   - A股：100股（一手），科创板200股起
   - 美股：1股起
   - 加密：取决于交易所最小合约单位
   - 实操：回测中必须整数手交易

□ 【权重再平衡检查】
   - 平衡频率：日频/周频/月频
   - 允许漂移：通常±1%
   - 每次再平衡扣除换手成本
   - 用组合再平衡表记录每次换手成本和理由

□ 【分红/送股/拆股处理检查】
   - 因子计算用后复权，收益计算用前复权
   - 维护两套价格体系
```

### 回测报告输出标准

```
□ 年化收益率
□ 年化波动率
□ 夏普比率
□ 最大回撤（MDD）
□ 卡尔玛比率（年化收益/最大回撤）
□ 胜率（盈利交易数/总交易数）
□ 盈亏比（平均盈利/平均亏损）
□ 换手率（年化）
□ 交易总成本（占总收益百分比）
□ 月度/季度正收益占比
□ 收益分布偏度&峰度
□ 策略与市场的Beta
□ 滚动12月夏普序列
```

---

## 第三部分：参数优化方法论

### 3.1 参数优化的正确目的

**核心认知**：不是找"最优参数"，而是找**参数稳定区域**。

```
误区                   正解
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
找最优参数值          找稳定的参数值组
追求最高夏普          追求稳健夏普
一次优化终身受用      Walk Forward循环
只看训练集结果       验证+测试双重把关
```

### 3.2 三种优化方法对比

| 方法 | 原理 | 适用场景 | 搜索效率 | 过拟合风险 |
|------|------|---------|---------|-----------|
| **网格搜索** | 穷举笛卡尔积 | 参数≤3个 | O(k^n) 极低 | 高 |
| **随机搜索** | 随机采样分布空间 | 参数3-6个 | O(m) 中等 | 中 |
| **贝叶斯优化** | 高斯过程建模+探索 | 参数>5个 | O(log m) 高 | 低 |

```python
# 网格搜索（参数≥2个时效率极低）
def grid_search(strategy, param_grid):
    from itertools import product
    best = {'sharpe': -np.inf}
    for params in product(*param_grid.values()):
        param_dict = dict(zip(param_grid.keys(), params))
        sharpe = cross_val_score(strategy, param_dict)
        if sharpe > best['sharpe']:
            best = {'sharpe': sharpe, 'params': param_dict}
    return best

# 随机搜索（推荐参数3-6个时使用）
def random_search(strategy, param_dists, n_iter=1000):
    best = {'sharpe': -np.inf}
    for _ in range(n_iter):
        params = {}
        for name, dist in param_dists.items():
            if dist['type'] == 'int':
                params[name] = np.random.randint(dist['low'], dist['high'])
            else:
                params[name] = np.random.uniform(dist['low'], dist['high'])
        sharpe = cross_val_score(strategy, params)
        if sharpe > best['sharpe']:
            best = {'sharpe': sharpe, 'params': params}
    return best

# 贝叶斯优化（参数>5个时优先使用）
def bayesian_optimize(strategy, bounds, n_calls=200):
    from skopt import gp_minimize
    def objective(params):
        param_dict = {'ma_short': int(params[0]),
                      'stop_loss': float(params[1]),
                      'lookback': int(params[2])}
        return -cross_val_score(strategy, param_dict)
    result = gp_minimize(objective, bounds, n_calls=n_calls, random_state=42)
    return result
```

### 3.3 参数稳定性热力图

```python
def parameter_stability_heatmap(strategy, param_name, param_range,
                                 secondary_param=None, secondary_range=None):
    """
    检查参数值的"敏感区域"
    - 夏普在±10%波动<10% → 稳定
    - 夏普在±5%波动>20% → 敏感，标记不稳定
    """
    results = []
    if secondary_param:
        for p in param_range:
            for sp in secondary_range:
                sharpe = cross_val_score(strategy, {param_name: p, secondary_param: sp})
                results.append({'p': p, 'sp': sp, 'sharpe': sharpe})
    else:
        for p in param_range:
            sharpe = cross_val_score(strategy, {param_name: p})
            results.append({'p': p, 'sharpe': sharpe})
    stable_region = find_stable_plateau(results, tolerance=0.1)
    return results, stable_region
```

### 3.4 Walk Forward Analysis (WFA) 完整流程

```
WFA流程：
第1轮：[训练期·36月] → [选最优参数] → [验证期·3月] → [测试期·3月]
第2轮：           [训练期·36月] → ... (窗口前移3个月)
第N轮：                               [训练期·36月] → ...

参数：训练窗口36月，步进3月，验证3月，外推测试3月
总计至少36个月以上（12轮）

判断标准：
- WFA外推夏普均值 > 1.0
- WFA外推夏普标准差 < 0.5
- 取胜率（最优参数在外推期排名前30%的比例）> 60%
```

```python
def walk_forward_analysis(strategy, data, train_months=36, step_months=3,
                          test_months=3):
    oos_sharpes = []
    params_history = []
    start, end = data.index[0], data.index[-1]
    cur_start = start
    cur_end = shift_months(cur_start, train_months + step_months)
    while cur_end <= end:
        train_end = shift_months(cur_start, train_months)
        test_start = train_end
        test_end = min(shift_months(test_start, test_months), cur_end)
        train_data = data[cur_start:train_end]
        test_data = data[test_start:test_end]
        best_params = optimize_strategy(strategy, train_data)
        oos_sharpe = backtest(strategy, best_params, test_data)
        oos_sharpes.append(oos_sharpe)
        params_history.append(best_params)
        cur_start = shift_months(cur_start, step_months)
        cur_end = shift_months(cur_start, train_months + step_months)
    return {'avg_oos_sharpe': np.mean(oos_sharpes),
            'std_oos_sharpe': np.std(oos_sharpes),
            'params_history': params_history,
            'sharpe_series': oos_sharpes}
```

### 3.5 避免过拟合的7种方法

```
1. 严格时间外推验证
   25%数据留作"从未使用"的外推样本，分析次数越多外推样本越大

2. 参数缩减（减少自由度）
   参数数量 < sqrt(样本量/200)
   示例：3000个交易日 → 最多3-4个调参参数

3. 正则化
   L1(Lasso)强制稀疏，L2(Ridge)约束幅度
   λ ∈ [0.01, 0.1, 0.5, 1.0, 5.0]

4. 组合路径交叉验证
   如果组合夏普=1.8但每个子策略夏普<0.5 → 过拟合

5. 多市场/多周期验证
   一个市场优化的参数能否在另一市场工作？
   跨市场验证不过关 → 过拟合

6. 经济逻辑约束
   每个参数必须有经济含义，不能纯统计发现
   反转期设置（5天/10天）要有行为金融学解释

7. 模拟交易后冻结
   最优参数确定后固定3个月不允许修改
   强制"拥抱次优但稳定"的配置
```

---

## 第四部分：回测→实盘过渡

### 4.1 偏差校正（回测收益通常高估20-50%）

```
| 偏差来源 | 典型高估 | 校正方法 |
|---------|---------|---------|
| 滑点低估 | 5-15% | 买卖价差×2保守滑点 |
| 手续费偏差 | 2-5% | 用"吃单费率"非"挂单费率" |
| 冲击成本 | 3-10% | 按日均成交量5%设上限 |
| 幸存者偏差 | 2-8% | 加入退市股票或扣除惩罚 |
| 前视偏差 | 5-20% | 显式shift+时间对齐 |
| 过度优化 | 5-25% | DSR校正+PBO检验 |
| 流动性限制 | 3-10% | 剔除低流动性标的 |

总计高估：约20-50%

实操校正公式：
  预期实盘收益 = 回测收益 × (1 - 高估比例)
  或更保守：预期实盘收益 = 回测收益 - 回测收益的标准差
```

### 4.2 滑点预估的真实计算方法

```python
def estimate_slippage(symbol, volume, price, market_depth_data):
    """
    基于买卖盘口数据的真实滑点计算
    
    输入：symbol(标的), volume(交易量), price(当前价), depth_data(深度数据)
    输出：expected_slippage(预期滑点百分比), slippage_detail(逐档明细)
    
    计算逻辑：
    1. 从卖一到卖十叠加挂单量
    2. 看买单量穿透多少档
    3. VWAP = 加权平均成交价格
    4. 滑点 = (VWAP - 当前价) / 当前价 × 100%
    
    实操参数：
    - 10档深度数据（A股L2行情标配）
    - 无深度数据：用历史买卖价差的1.5倍作为保守估计
    """
    remaining = volume
    total_cost = 0
    total_filled = 0
    slippage_detail = []
    
    for ask_level in market_depth_data['asks']:
        if remaining <= 0:
            break
        
        ask_price = ask_level['price']
        ask_volume = ask_level['volume']
        fill_volume = min(remaining, ask_volume)
        
        cost = fill_volume * ask_price
        total_cost += cost
        total_filled += fill_volume
        
        slippage_detail.append({
            'level': len(slippage_detail) + 1,
            'price': ask_price,
            'volume': fill_volume,
            'cumulative': total_filled
        })
        
        remaining -= fill_volume
    
    if total_filled == 0:
        return None, []
    
    vwap = total_cost / total_filled
    slippage_bps = (vwap - price) / price * 100  # 百分比
    
    return slippage_bps, slippage_detail


def estimate_slippage_without_depth(symbol, avg_spread_bps, volume_factor=1):
    """
    无深度数据时的经验滑点估算
    
    volume_factor: 交易量相对于日均成交量的比例
    滑点 = 买卖价差 × 1.5 + 冲击项
    冲击项 = 0.01 * volume_factor^0.5
    """
    base_slippage = avg_spread_bps * 1.5
    impact = 0.01 * (volume_factor ** 0.5)
    return base_slippage + impact
```

### 4.3 Almgren-Chriss冲击模型基础版

```python
def almgren_chriss_impact(volume, adv, price, sigma, spread_bps, gamma=0.1, eta=0.1):
    """
    简化版Almgren-Chriss冲击模型
    
    参数：
    - volume: 我的交易量
    - adv: 日均成交量
    - price: 当前价格
    - sigma: 日波动率（百分比）
    - spread_bps: 买卖价差（基点）
    - gamma: 固定冲击系数（默认0.1）
    - eta: 临时冲击系数（默认0.1）
    
    计算：
    - 临时冲击 = gamma * sigma * (volume/adv)^(0.5)
    - 固定冲击 = 0.5 * spread_bps * sign(volume)
    - 总冲击成本 = 固定冲击 + 临时冲击
    
    输出：冲击成本（基点）
    """
    participation_rate = volume / adv
    
    # 永久冲击（对价格的影响）
    permanent_impact = gamma * sigma * (participation_rate ** 0.5)
    
    # 临时冲击（执行过程中的滑点）
    temporary_impact = eta * sigma * (participation_rate ** 0.5)
    
    # 固定冲击（买卖价差的一半）
    fixed_impact = 0.5 * spread_bps
    
    total_impact_bps = fixed_impact + permanent_impact + temporary_impact
    
    return total_impact_bps
```

### 4.4 回测差异清单

```
数据差异：
  □ 回测用的数据精度是否与实盘API输出一致？
  □ A股：回测用收盘价，实盘实时变动，日内信号精度差异
  □ 加密：回测用分钟级别的OHLCV，实盘是逐笔成交
  □ 数据延迟：回测0延迟，实盘API有100-500ms延迟

执行差异：
  □ 回测假设立即成交，实盘有撮合等待时间
  □ 回测假设卖一价可买满，实盘有挂单量限制
  □ 回测忽略网络延迟和API限频
  □ 回测忽略交易所维护/故障/异常

环境差异：
  □ 回测是确定性的，实盘有随机性和对手方博弈
  □ 回测假设"市场价格不变"，实盘中你本身就是市场影响者
  □ 回测可以无限次调参，实盘一旦定参就要跑一段时间
```

### 4.5 实盘监控清单

```
每日检查项：
□ 策略持仓是否与信号表一致（仓位偏差检查）
□ 当日成交回报是否正常（无异常撤销/滚单）
□ 账户权益与策略预期是否匹配（利润归因）
□ 交易所API连接状态正常
□ 网络延迟在容忍范围内
□ 策略信号生成时间在允许窗口内

每周检查项：
□ 滚动1周夏普 > 0.5（否则检查策略是否失效）
□ 实盘vs回测偏差在预期范围内（偏差应<30%）
□ 最大回撤未触发熔断阈值
□ 交易成本vs回测假设偏差<20%

每月检查项：
□ 因子IC序列：本月IC vs 历史IC分布
□ 策略归因分析：收益分解为Alpha、Beta、择时
□ 参数是否需要Walk Forward更新
□ 实盘收益vs回测外推收益偏差趋势分析
```

---

## 第五部分：策略生命周期管理

### 5.1 六级生命周期体系

```
研究 → 回测 → 模拟 → 实盘 → 休眠 → 废弃

                   ┌── 升级 ──┐
                   ↓          ↑
    研究 ──→ 回测 ──→ 模拟 ──→ 实盘
                   ↑          │
                   │          ├──→ 休眠 ──→ 废弃
                   │          │
                   └── 降级 ──┘
```

### 5.2 每一级的升级门槛

**L1：研究阶段**
```
特征：因子想法、论文阅读、数据探索
最低停留时间：1周
升级门槛：
□ 因子有经济逻辑支撑
□ 初步IC检验 |IC| > 0.02
□ 数据可获取且可持续更新
□ 有可执行的回测方案
```

**L2：回测阶段**
```
特征：完整回测框架、参数探索、过拟合检测
最低停留时间：2周
升级门槛：
□ 回测夏普 > 1.5（保守估计）
□ 最大回撤 < 20%
□ 通过DSR校正（DSR > 0.5）
□ PBO < 0.1
□ 通过参数扰动测试（敏感度<0.5）
□ 覆盖极端行情测试（2020熔断/2022LUNA/2024carry trade）
□ 交易成本扣除完善
```

**L3：模拟交易阶段**
```
特征：用实盘API但仅模拟下单（Paper Trading）
最低停留时间：1个月
升级门槛：
□ 模拟期间夏普 > 1.0
□ 模拟期间最大回撤 < 实盘预期的1.5倍
□ 实际滑点vs回测滑点偏差 < 30%
□ 每日信号稳定生成（无异常缺失）
□ 与实盘环境的兼容性验证通过
□ 风控逻辑运行时验证通过
```

**L4：实盘阶段**
```
特征：真金白银运行
最低仓位：全战场的5%以下起步
逐步加仓门槛（按顺序）：
  1. 首月表现正常 → 加至10%
  2. 连续2个月盈利 → 加至15%
  3. 连续3个月夏普>1.0 → 加至20%（上限）
  4. 任何一个月亏损超过3% → 立即减回10%
```

**L5：休眠阶段**
```
特征：已证明失效但保留重新激活的可能性
触发条件（任一即可）：
□ 连续3个月IC < 0（因子失效）
□ 夏普连续2个月 < 0.5
□ 最大回撤突破30%
□ 市场结构发生根本性变化（如A股注册制改革）

休眠期间：
□ 不占实盘资金
□ 每个月自动跑一次回测检查
□ 标记休眠原因和时间
□ 保留完整的历史记录
```

**L6：废弃阶段**
```
特征：永久失效
触发条件：
□ 休眠超过12个月仍无复苏迹象
□ 市场底层逻辑彻底改变（如废除涨停板制度）
□ 数据源中断超过6个月
□ 被更优策略完全替代

废弃后：
□ 移出主因子库
□ 归档至历史策略库（方便后续复盘）
□ 在月报中注明废弃原因
```

### 5.3 衰减监控指标

```python
def strategy_decay_monitor(strategy_returns, benchmark_returns=None):
    """
    策略衰减监控指标
    
    监控频率：周频
    滚动窗口：12周（短期）、52周（长期）
    
    衰减信号：
    1. 滚动12周夏普 < 0.5（短期预警）
    2. 滚动52周夏普 < 1.0（长期预警）
    3. IC均值连续4周下降（因子衰减）
    4. 超额收益接近0（统计不显著）
    5. 换手率显著下降（信号失效）
    """
    metrics = {}
    
    # 滚动夏普
    metrics['roll_12w_sharpe'] = strategy_returns.rolling(60).mean() / strategy_returns.rolling(60).std() * np.sqrt(252)
    metrics['roll_52w_sharpe'] = strategy_returns.rolling(252).mean() / strategy_returns.rolling(252).std() * np.sqrt(252)
    
    # 超额收益
    if benchmark_returns is not None:
        excess = strategy_returns - benchmark_returns
        metrics['excess_sharpe'] = (excess.mean() / excess.std()) * np.sqrt(252)
    
    # 收益显著性
    t_stat = strategy_returns.mean() / (strategy_returns.std() / np.sqrt(len(strategy_returns)))
    metrics['t_stat'] = t_stat
    metrics['p_value'] = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    
    return metrics
```

### 5.4 策略退役标准

```
硬性退役条件（任一触发即执行）：
1. 单月亏损 > 10%
2. 连续3个月亏损
3. 最大回撤 > 25%
4. 实盘超过6个月仍夏普 < 0.5
5. 因子IC连续3个月 < 0（且无复苏迹象）
6. 策略逻辑的底层假设被证伪

软性退役条件（建议执行）：
1. 夏普从高点回撤 > 50%
2. 策略容量见顶（资金规模触及上限）
3. 被更优策略全面替代
4. 监管/市场规则发生重大变化
5. 数据源不可用或质量大幅下降
```

### 5.5 策略归档制度

```
归档内容包括：
□ 策略源代码（标记版本号）
□ 因子定义和计算代码
□ 回测报告完整PDF
□ 回测原始数据（脱敏）
□ 实盘交易记录完整CSV
□ 实盘期间的所有监控日志
□ 归因分析报告
□ 退役/废弃原因文档
□ 可复现的完整环境配置（Docker/requirements.txt）

归档路径规范：
/strategy_archive/{category}/{strategy_name}_{yyyy_mm}/

保留期限：永久保留（硬盘空间便宜，但复盘经验无价）
```

---

## 第六部分：常见陷阱与避坑指南

### 6.1 过度拟合——量化交易的第一杀手

**症状表现：**
- 回测夏普3.5，实盘夏普-0.3
- 训练集表现完美，测试集一塌糊涂
- 参数稍微变动，表现大幅下降
- 每年调整参数时"发现新规律"

**典型场景复盘：**
```
案例1：过多参数
问题：一个移动平均线策略调了8个参数
      (快线/慢线/止损/止盈/仓位比例/入场过滤/出场过滤/时间过滤)
真相：3000个交易日数据，8个参数，自由度过高
      参数组合数 = 10^8 = 1亿，总起在拟合噪音
根治：参数数量 < sqrt(3000/200) ≈ 3.8，最多3个参数

案例2：过度挖掘
问题：测试了500个因子，选出了5个"最好"的
真相：在5%显著性水平下，500次测试中期望有25个伪显著
      选出的5个可能全是噪音
根治：多重假设检验校正（Bonferroni/FDR），DSR校正
```

**解决方法：**
```
1. 强制外推验证：保留25%数据从未使用
2. 减少参数：每个策略不超过3个调参参数
3. Walk Forward Analysis：至少12轮验证
4. DSR+PBO双重检验：DSR<0.5或PBO>0.1的淘汰
5. 原理驱动：参数必须有经济学解释
```

### 6.2 数据挖掘偏差——你找到的不是规律，是巧合

**根源：**
- 在大量数据中反复搜索，"总会找到一些模式"
- 这些模式是统计噪音，不是真实规律

**典型场景：**
```
- 发现"每月第一天的上午10:30"有特定交易信号
- 发现"穿粉色衣服的CEO的公司"表现更好
- 发现"代码以8结尾的股票"波动率更低
```

**解决方案：**
```
1. 只研究有经济学逻辑的因子（先有理论，后有数据）
2. 样本外验证（时间上、市场上）
3. 相关性≠因果性（高度警惕"发现"）
4. 复现性检查：在不同时间段重复出现才算真
```

### 6.3 策略"看起来很美"但实际不行的7个原因

```
1. 幸存者偏差：回测只用存活股票，未计入退市损失
   → 每年扣除1-2%惩罚因子

2. 前视偏差：不小心用了未来数据
   → shift(1)是量化人的好习惯

3. 忽略交易成本：回测假设零成本交易
   → A股T+0策略单趟成本0.1%，年化换手100倍就是-10%

4. 忽略流动性：假设小盘股有大盘股一样的流动性
   → 按成交量分档设置滑点

5. 参数自适应：做了1000次回测选最好的一次
   → 用Walk Forward替代一次过优化

6. 市场机制变化：用2016-2018的数据预测2024年
   → 市场规则变了，旧规律失效（如科创板、注册制）

7. 规模效应：小资金效果好，大资金效果差
   → 100万策略做1000万效果可能差3倍
   → 回测时就按目标资金规模的滑点设置
```

### 6.4 不要爱上一个策略——市场变了就是变了

**心理陷阱警示：**
```
"这个策略在15年前就开始盈利了，不可能突然失效"
→ 15年持续有效→所有人都发现了→因子已出尽→失效

"再给它一点时间，肯定会恢复的"
→ 已经亏了6个月，还会再亏6个月

"这次不一样，是市场错了"
→ 市场永远是对的，是你错了

"我把参数微调一下就又赚钱了"
→ 调整参数只是低配版过度拟合
```

**实操纪律：**
```
1. 每个策略预设"观察期"（3个月）和"冷宫期"（2年）
2. 明确写清退役条件，达到就执行（不纠结）
3. 不因为过去赚钱就增加权重
4. 每季度做一次策略"陌生人审核"：
   假装你是第一次看到这个策略，
   它会通过你的审核标准吗？
5. 多策略并行，单策略上限20%
   一个策略挂了不影响全局
```

### 6.5 实盘中常见Bug检查清单

```
□ 价格序列的NaN未处理 → 信号被跳过或错误填充
□ 除零错误（波动率为0时） → 日内停牌股票当天波动率为0
□ 未考虑节假日 → A股春节停牌1周，信号延迟
□ 数据库连接超时未重试 → 导致漏单
□ API限频未处理 → 订单超时或拒单
□ 未处理撤单返回码 → 订单状态不同步
□ 账户余额检查不充分 → 开仓时保证金不足
□ 杠杆计算错误 → 仓位超出风控范围
□ 分红除权日未处理 → 持仓价格突变
□ 夏令时/冬令时切换 → 美股开盘时间偏移1小时
□ 时区转换错误 → 跨市场信号对应时间错位
□ HTTP请求超时未设置重试/降级 → 策略空转漏单
```

---

## 附录：快速参考

### 回测基础参数速查表

| 参数 | A股 | 加密永续 | 美股 |
|------|-----|---------|-----|
| 手续费（吃单） | 万1.2 | 万3.5 | $0.005/股 |
| 滑点（保守） | 0.15% | 0.05% | 0.10% |
| 最小回测期 | 5年 | 2年 | 10年 |
| 数据频率 | 日频 | 1小时 | 日频 |
| 停牌处理 | 超出20日强制平仓 | 无 | 超出5日强制平仓 |
| 牛熊周期 | 3-5年 | 0.5-2年 | 5-8年 |
| 最大仓位限制 | 单票≤20% | 单币≤30% | 单股≤15% |

### 关键代码片段速查

```python
# 1. 滚动夏普计算
def rolling_sharpe(returns, window=252):
    return returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)

# 2. 最大回撤计算
def max_drawdown(equity_curve):
    rolling_max = equity_curve.expanding().max()
    drawdown = (equity_curve - rolling_max) / rolling_max
    return drawdown.min()

# 3. Calmar比率
def calmar_ratio(returns, equity_curve):
    annualized_return = returns.mean() * 252
    mdd = max_drawdown(equity_curve)
    return annualized_return / abs(mdd) if mdd != 0 else np.inf

# 4. IC序列计算
def factor_ic_series(factor_df, forward_return_col, date_col='date'):
    ics = []
    for date, group in factor_df.groupby(date_col):
        ic, _ = spearmanr(group['factor'], group[forward_return_col])
        ics.append({'date': date, 'IC': ic})
    return pd.DataFrame(ics).set_index('date')

# 5. 因子RankIC（横截面）
def rank_ic_cross_sectional(factor_values, forward_returns):
    """横截面Rank IC：同一时间截面上的因子排序与收益排序的相关性"""
    return spearmanr(factor_values, forward_returns)[0]
```

---

> **烛龙在此。** 🐉  
> *本手册从实战中来，到实战中去。每一条经验都是真金白银换来的教训。*  
> *永远记住：市场不欠你任何收益，但它会惩罚每一个不尊重风险的人。*  
> *版本：v1.0 | 最后更新：2026-05-04*
