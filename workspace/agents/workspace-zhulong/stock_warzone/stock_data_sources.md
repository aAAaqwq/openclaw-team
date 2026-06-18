# A股数据源手册 (Stock Data Sources)

> **版本**: V1.0 实战版  
> **目标**: A股量化交易数据获取完全指南  
> **覆盖**: 免费数据源、付费数据源、本地数据、实盘数据

---

## 一、数据源总览

### 1.1 数据源分类

| 类别 | 数据源 | 成本 | 适用场景 | 推荐指数 |
|------|--------|------|----------|----------|
| **免费API** | AKShare | 免费 | 研究/回测 | ⭐⭐⭐⭐⭐ |
| **免费API** | Tushare | 免费(积分制) | 研究/回测 | ⭐⭐⭐⭐ |
| **平台数据** | 聚宽 | 免费(平台内) | 回测/模拟 | ⭐⭐⭐⭐⭐ |
| **平台数据** | 掘金 | 免费(平台内) | 回测/实盘 | ⭐⭐⭐⭐ |
| **券商接口** | 华泰API | 免费(客户) | 实盘交易 | ⭐⭐⭐⭐⭐ |
| **付费数据** | Wind | 付费 | 机构研究 | ⭐⭐⭐⭐⭐ |
| **付费数据** | 东方财富Choice | 付费 | 专业研究 | ⭐⭐⭐⭐ |

---

## 二、免费数据源详解

### 2.1 AKShare (推荐)

**安装**:
```bash
pip install akshare
```

**核心接口**:

```python
import akshare as ak

# 1. A股股票列表
stock_list = ak.stock_zh_a_spot_em()
# 返回: 代码、名称、最新价、涨跌幅、成交量等

# 2. 历史K线数据
stock_hist = ak.stock_zh_a_hist(
    symbol="000001", 
    period="daily", 
    start_date="20200101",
    end_date="20260101",
    adjust="qfq"  # 前复权
)

# 3. 实时行情
realtime = ak.stock_zh_a_spot_em()

# 4. 财务数据
finance = ak.stock_financial_analysis_indicator(symbol="000001")

# 5. 指数数据
index_data = ak.stock_zh_index_daily(symbol="sh000001")

# 6. 北向资金
north_flow = ak.stock_hsgt_north_net_flow_in_em()

# 7. 龙虎榜
long_hu = ak.stock_lhb_detail_em(start_date="20260101", end_date="20260110")

# 8. 融资融券
margin_data = ak.stock_margin_detail_szse(date="20260101")
```

**注意事项**:
- 海外访问可能受限制(东方财富API需国内IP)
- 有请求频率限制，建议加延时
- 数据更新时间为交易日收盘后

### 2.2 Tushare

**安装与注册**:
```bash
pip install tushare
# 注册获取token: https://tushare.pro
```

**核心接口**:

```python
import tushare as ts
ts.set_token('your_token')
pro = ts.pro_api()

# 1. 股票列表
stock_list = pro.stock_basic(exchange='', list_status='L')

# 2. 日线行情
daily = pro.daily(ts_code='000001.SZ', start_date='20200101', end_date='20260101')

# 3. 复权数据
adj_factor = pro.adj_factor(ts_code='000001.SZ')

# 4. 财务数据
income = pro.income(ts_code='000001.SZ', start_date='20200101')
balance = pro.balancesheet(ts_code='000001.SZ')
cashflow = pro.cashflow(ts_code='000001.SZ')

# 5. 指数数据
index_daily = pro.index_daily(ts_code='000001.SH')

# 6. 技术指标
cyq_perf = pro.cyq_perf(ts_code='000001.SZ')  # 筹码分布
```

**积分制度**:
- 基础接口免费，高级接口需积分
- 每日请求次数有限制
- 建议: 研究阶段使用，生产环境考虑付费

---

## 三、回测平台数据

### 3.1 聚宽 (JoinQuant)

**数据接口**:

```python
# 在聚宽平台内使用

# 1. 获取股票列表
get_all_securities(types=['stock'], date=None)

# 2. 历史数据
get_price(security, start_date=None, end_date=None, frequency='daily', fields=None, count=None)

# 3. 历史 bars
history(count, frequency, fields, security_list)

# 4. 财务数据
get_fundamentals(query_object, date=None)

# 5. 实时数据
current_data[security].field_name

# 6. 停牌股票
get_all_securities(types=['stock'], date=current_dt).is_trade
```

**数据字段**:

| 字段 | 说明 | 示例 |
|------|------|------|
| open | 开盘价 | 10.50 |
| close | 收盘价 | 10.80 |
| high | 最高价 | 10.95 |
| low | 最低价 | 10.45 |
| volume | 成交量(股) | 1000000 |
| money | 成交额(元) | 10800000 |

**财务数据表**:

| 表名 | 内容 | 常用字段 |
|------|------|----------|
| valuation | 估值数据 | market_cap, pe_ratio, pb_ratio |
| indicator | 财务指标 | roe, net_profit_margin |
| income | 利润表 | revenue, net_profit |
| balance | 资产负债表 | total_assets, total_liability |
| cash_flow | 现金流表 | net_cash_flow |

### 3.2 掘金量化

**数据接口**:

```python
from gm.api import *

# 1. 订阅数据
subscribe(symbols='SHSE.000001', frequency='1d', count=100)

# 2. 历史数据
history(symbol='SHSE.000001', frequency='1d', start_time='2020-01-01', end_time='2026-01-01')

# 3. 实时数据
current(symbols='SHSE.000001')

# 4. 财务数据
get_financial_data(symbols='SHSE.000001', fields='roe,pe_ratio')
```

---

## 四、实盘交易数据 (华泰证券)

### 4.1 华泰API接入

**前置条件**:
- 华泰证券账户
- 开通量化交易权限
- 安装华泰客户端

**接入方式**:

| 方式 | 说明 | 适用场景 |
|------|------|----------|
| **PTrade** | 华泰官方量化平台 | 专业交易 |
| **迅投QMT** | 华泰支持的第三方 | 高频交易 |
| **Easytrader** | 开源封装库 | 小资金 |

### 4.2 Easytrader示例

```python
import easytrader
from easytrader import grid_strategies

# 连接华泰
user = easytrader.use('ht_client')
user.connect(
    r'C:\ht_client\xiadan.exe',  # 华泰客户端路径
    'your_account', 
    'your_password'
)

# 获取持仓
position = user.position

# 获取余额
balance = user.balance

# 买入
user.buy('000001', price=10.50, amount=100)

# 卖出
user.sell('000001', price=10.80, amount=100)

# 撤单
user.cancel_entrust(entrust_no='123456')
```

### 4.3 注意事项

**时间对齐**:
```python
# 交易日历
trade_days = get_trade_days(start='2020-01-01', end='2026-12-31')

# 交易时间
# 9:15-9:25  集合竞价
# 9:30-11:30 上午连续竞价
# 13:00-15:00 下午连续竞价
```

**数据延迟**:
- 实盘行情可能有1-3秒延迟
- 建议使用券商推送行情而非第三方

---

## 五、数据质量检查

### 5.1 常见数据问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **缺失数据** | NaN或空值 | 前值填充/线性插值 |
| **异常值** | 价格突跳>20% | 检查复权/剔除异常 |
| **时间戳对齐** | 未来函数 | 使用shift(1)滞后 |
| **幸存者偏差** | 缺少退市股 | 使用历史全量列表 |
| **停牌数据** | 成交量为0 | 检查is_trade字段 |

### 5.2 数据清洗模板

```python
def clean_data(df):
    """数据清洗标准流程"""
    # 1. 处理缺失值
    df = df.fillna(method='ffill')  # 前值填充
    
    # 2. 处理异常值
    for col in ['open', 'high', 'low', 'close']:
        zscore = (df[col] - df[col].mean()) / df[col].std()
        df.loc[zscore.abs() > 5, col] = np.nan
    
    # 3. 检查停牌
    if 'volume' in df.columns:
        df['is_suspend'] = df['volume'] == 0
    
    # 4. 复权处理
    if 'adj_factor' in df.columns:
        df['close_adj'] = df['close'] * df['adj_factor']
    
    return df
```

### 5.3 未来函数检查

```python
def check_lookahead_bias(df, column):
    """检查是否使用了未来数据"""
    # 错误示例: 使用当日收盘价作为当日买入价
    # 正确做法: 使用昨日收盘价或今日开盘价
    
    # 检查方法: 打印信号日和交易日
    df['signal_date'] = df.index
    df['trade_date'] = df.index.shift(1)  # 信号次日交易
    
    # 检查是否使用了信号日的收盘价
    if df['signal_date'].equals(df['trade_date']):
        print("警告: 可能存在未来函数!")
```

---

## 六、数据存储方案

### 6.1 本地存储

```python
import pandas as pd
import os

# CSV存储
def save_to_csv(df, filename, data_dir='~/stock_data'):
    os.makedirs(data_dir, exist_ok=True)
    df.to_csv(f'{data_dir}/{filename}.csv', index=True)

# Parquet存储 (推荐,更高效)
def save_to_parquet(df, filename, data_dir='~/stock_data'):
    os.makedirs(data_dir, exist_ok=True)
    df.to_parquet(f'{data_dir}/{filename}.parquet')

# 读取
def load_data(filename, data_dir='~/stock_data'):
    if os.path.exists(f'{data_dir}/{filename}.parquet'):
        return pd.read_parquet(f'{data_dir}/{filename}.parquet')
    elif os.path.exists(f'{data_dir}/{filename}.csv'):
        return pd.read_csv(f'{data_dir}/{filename}.csv', index_col=0)
    else:
        return None
```

### 6.2 数据更新策略

| 频率 | 数据类型 | 更新时间 |
|------|----------|----------|
| **每日** | 日线数据 | 收盘后18:00 |
| **每日** | 财务数据 | 披露日次日 |
| **实时** | 实时行情 | 开盘期间 |
| **每周** | 龙虎榜 | 次日盘后 |
| **每月** | 指数成分股 | 调整生效日 |

---

## 七、数据获取最佳实践

### 7.1 研究阶段

```python
# 推荐: AKShare + 本地存储
import akshare as ak

def download_stock_data(stock_code, start_date, end_date):
    """下载并保存股票数据"""
    try:
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        save_to_parquet(df, f'{stock_code}_daily')
        return df
    except Exception as e:
        print(f"下载失败: {stock_code}, 错误: {e}")
        return None

# 批量下载
stock_list = ak.stock_zh_a_spot_em()['代码'].tolist()
for stock in stock_list[:100]:  # 先下载100只测试
    download_stock_data(stock, '20200101', '20260101')
    time.sleep(0.5)  # 避免请求过快
```

### 7.2 回测阶段

```python
# 推荐: 聚宽平台
# 直接使用平台数据，无需下载

def initialize(context):
    # 设置基准
    set_benchmark('000001.XSHG')
    # 设置佣金
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, close_today_commission=0, min_commission=5), type='stock')
    # 设置滑点
    set_slippage(FixedSlippage(0.002))
```

### 7.3 实盘阶段

```python
# 推荐: 华泰API + Easytrader
# 实盘时使用券商实时数据

def get_realtime_data(stock_code):
    """获取实时数据"""
    # 从券商API获取
    quote = user.get_quote(stock_code)
    return {
        'open': quote.open,
        'high': quote.high,
        'low': quote.low,
        'close': quote.current,
        'volume': quote.volume,
        'amount': quote.amount
    }
```

---

> **烛龙量化神殿** 🐉  
> *数据质量决定策略上限*
