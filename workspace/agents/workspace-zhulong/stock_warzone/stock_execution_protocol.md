# A股执行协议 (Stock Execution Protocol)

> **版本**: V1.0 实战版  
> **目标**: 从回测到虚拟盘到实盘的完整流程  
> **券商**: 华泰证券接入方案

---

## 一、执行流程总览

```
┌─────────────────────────────────────────────────────────────┐
│                    策略开发 → 实盘上线                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: 研究阶段                                           │
│  ├── 因子挖掘 → 信号验证 → 原型构建                           │
│  └── 输出: 策略原型文档                                       │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: 回测阶段                                           │
│  ├── 历史回测 → 参数优化 → 稳健性检验                         │
│  └── 输出: 回测报告 (夏普>1.0, 最大回撤<30%)                  │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: 影子战法                                           │
│  ├── 模拟信号 → 跟踪验证 → 偏差分析                           │
│  └── 输出: 影子跟踪报告 (信号一致性>95%)                      │
├─────────────────────────────────────────────────────────────┤
│  Phase 4: 虚拟盘                                             │
│  ├── 模拟交易 → 滑点检验 → 心理训练                           │
│  └── 输出: 虚拟盘报告 (运行>1个月, 收益符合预期)               │
├─────────────────────────────────────────────────────────────┤
│  Phase 5: 实盘上线                                           │
│  ├── 小资金试运行 → 逐步加仓 → 全仓运行                       │
│  └── 输出: 实盘运行报告                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、三账本体系

### 2.1 账本定义

| 账本 | 目的 | 资金规模 | 验证重点 | 升级条件 |
|------|------|----------|----------|----------|
| **回测账本** | 验证策略逻辑 | 模拟 | 历史表现、参数稳健性 | 夏普>1.0 |
| **虚拟盘账本** | 验证执行可行性 | 100万(虚拟) | 滑点、延迟、心理 | 运行>1月, 收益符合预期 |
| **实盘账本** | 真实盈利 | 实际资金 | 全流程、风控、心态 | 虚拟盘验证通过 |

### 2.2 账本映射关系

```
回测账本 ──验证通过──→ 虚拟盘账本 ──验证通过──→ 实盘账本
    │                       │                       │
    ▼                       ▼                       ▼
 历史数据                实时行情+模拟成交        真实资金+真实成交
 理想滑点                实际滑点估计             真实滑点
 无情绪干扰              模拟情绪训练             真实情绪管理
```

---

## 三、Phase 1: 研究阶段

### 3.1 策略原型文档模板

```markdown
# 策略原型: [策略名称]

## 1. 策略概述
- 策略类型: [趋势/反转/套利/多因子]
- 交易标的: [股票/ETF/期货]
- 调仓频率: [日频/周频/月频]
- 预期夏普: [>1.5]
- 最大回撤: [<20%]

## 2. Alpha来源
- 核心逻辑: [为什么这个策略能赚钱]
- 经济学解释: [行为金融/制度套利/风险补偿]
- 失效条件: [什么情况下会亏钱]

## 3. 信号构建
- 选股逻辑: [如何选股票]
- 择时逻辑: [何时买卖]
- 权重分配: [等权/风险平价/市值加权]

## 4. 风控设计
- 个股止损: [8%固定/ATR跟踪]
- 账户止损: [单日2%/累计15%]
- 仓位上限: [单票20%/行业30%]

## 5. 执行方案
- 调仓时间: [开盘/收盘/盘中]
- 订单类型: [市价/限价]
- 滑点估计: [0.1%]

## 6. 验证清单
- [ ] 无未来函数
- [ ] 样本量>200次交易
- [ ] 滚动回测稳健
- [ ] 参数不敏感
```

---

## 四、Phase 2: 回测阶段

### 4.1 回测配置标准

```python
# 聚宽回测标准配置
def initialize(context):
    # 设置基准
    set_benchmark('000001.XSHG')
    
    # 设置佣金 (华泰标准)
    set_order_cost(
        OrderCost(
            open_tax=0,                    # 买入印花税
            close_tax=0.001,               # 卖出印花税 0.1%
            open_commission=0.0003,        # 买入佣金 0.03%
            close_commission=0.0003,       # 卖出佣金 0.03%
            close_today_commission=0,      # 平今佣金
            min_commission=5               # 最低佣金5元
        ),
        type='stock'
    )
    
    # 设置滑点 (双边0.2%)
    set_slippage(FixedSlippage(0.002))
    
    # 设置最大持仓比例
    set_max_total_value(1.0)  # 100%仓位
    
    # 设置日志
    log.set_level('order', 'error')
```

### 4.2 回测检查清单

| 检查项 | 标准 | 工具/方法 |
|--------|------|-----------|
| **未来函数** | 无 | 检查信号计算是否使用未来数据 |
| **幸存者偏差** | 无 | 使用历史全量股票列表 |
| **停牌处理** | 正确处理 | 检查is_trade字段 |
| **复权处理** | 前复权 | 使用adjust='qfq' |
| **手续费** |  realistic | 包含印花税+佣金+滑点 |
| **样本量** | >200次交易 | 统计显著性 |
| **过拟合** | 参数不敏感 | 参数扰动测试 |

### 4.3 回测报告模板

```markdown
# 回测报告: [策略名称]

## 回测设置
- 回测区间: 2020-01-01 ~ 2026-01-01
- 初始资金: 1,000,000
- 基准指数: 沪深300

## 绩效指标
| 指标 | 策略 | 基准 | 评价 |
|------|------|------|------|
| 年化收益 | 15.2% | 8.5% | ✅ 跑赢 |
| 夏普比率 | 1.35 | 0.65 | ✅ 优秀 |
| 最大回撤 | 18.5% | 25.3% | ✅ 控制好 |
| 胜率 | 52% | - | ✅ 正期望 |
| 盈亏比 | 1.8 | - | ✅ 合理 |

## 年度表现
| 年份 | 策略收益 | 基准收益 | 超额收益 |
|------|----------|----------|----------|
| 2020 | 25% | 20% | +5% |
| 2021 | 12% | 5% | +7% |
| ... | ... | ... | ... |

## 风险分析
- 最大回撤发生时间: 2022-03 ~ 2022-04
- 回撤原因分析: 市场系统性下跌
- 恢复时间: 2个月

## 结论
- [ ] 通过回测，进入影子战法
- [ ] 需优化，重新回测
- [ ] 不通过，放弃
```

---

## 五、Phase 3: 影子战法

### 5.1 影子战法定义

**目的**: 验证回测信号与实盘信号的一致性

**方法**:
1. 每日收盘后生成次日交易信号
2. 次日开盘前记录信号
3. 次日收盘后对比实际走势与信号预期
4. 统计信号准确率

### 5.2 影子跟踪模板

```python
# 影子战法实现
class ShadowTrading:
    def __init__(self):
        self.signals = []  # 记录信号
        self.tracking = []  # 记录跟踪结果
    
    def generate_signal(self, date, stock_pool):
        """生成交易信号"""
        signal = {
            'date': date,
            'buy_list': [],  # 买入列表
            'sell_list': [],  # 卖出列表
            'reason': ''     # 信号理由
        }
        # ... 信号生成逻辑
        self.signals.append(signal)
        return signal
    
    def track_result(self, date, actual_data):
        """跟踪信号结果"""
        yesterday_signal = self.get_signal(date - 1)
        
        for stock in yesterday_signal['buy_list']:
            expected_return = self.calculate_expected(stock)
            actual_return = actual_data[stock]['return']
            
            self.tracking.append({
                'date': date,
                'stock': stock,
                'signal': 'buy',
                'expected': expected_return,
                'actual': actual_return,
                'deviation': actual_return - expected_return
            })
    
    def consistency_report(self):
        """一致性报告"""
        df = pd.DataFrame(self.tracking)
        
        consistency = (df['deviation'].abs() < 0.01).mean()
        
        print(f"信号一致性: {consistency*100:.1f}%")
        print(f"平均偏差: {df['deviation'].mean()*100:.2f}%")
        
        return consistency > 0.95
```

### 5.3 影子战法通过标准

| 指标 | 标准 | 说明 |
|------|------|------|
| 信号一致性 | >95% | 实际走势与预期一致的比例 |
| 平均偏差 | <1% | 预期收益与实际收益的平均差异 |
| 最大偏差 | <5% | 单次最大偏差 |
| 跟踪时长 | >1个月 | 至少跟踪20个交易日 |

---

## 六、Phase 4: 虚拟盘

### 6.1 虚拟盘配置 (100万)

| 战区 | 分配比例 | 金额 |
|------|----------|------|
| A股(华泰映射) | 20% | 20万 |
| 加密(Bitget映射) | 40% | 40万 |
| Polymarket | 40% | 40万 |

### 6.2 虚拟盘账户类

```python
class VirtualAccount:
    def __init__(self, initial_cash=200000):
        self.cash = initial_cash
        self.positions = {}
        self.trades = []
        self.daily_values = []
    
    def buy(self, stock, price, amount):
        """买入 (含佣金)"""
        cost = price * amount * 1.0003
        if cost <= self.cash:
            self.cash -= cost
            self.positions[stock] = self.positions.get(stock, 0) + amount
            return True
        return False
    
    def sell(self, stock, price, amount):
        """卖出 (含印花税+佣金)"""
        if self.positions.get(stock, 0) >= amount:
            revenue = price * amount * 0.9987
            self.cash += revenue
            self.positions[stock] -= amount
            if self.positions[stock] == 0:
                del self.positions[stock]
            return True
        return False
    
    def update_value(self, prices):
        """更新账户价值"""
        position_value = sum(
            self.positions[stock] * prices.get(stock, 0)
            for stock in self.positions
        )
        total = self.cash + position_value
        self.daily_values.append(total)
        return total
    
    def sharpe(self):
        """计算夏普比率"""
        if len(self.daily_values) < 2:
            return 0
        returns = pd.Series(self.daily_values).pct_change().dropna()
        if returns.std() == 0:
            return 0
        return returns.mean() / returns.std() * np.sqrt(252)
    
    def max_drawdown(self):
        """计算最大回撤"""
        if not self.daily_values:
            return 0
        series = pd.Series(self.daily_values)
        rolling_max = series.expanding().max()
        drawdown = (series - rolling_max) / rolling_max
        return drawdown.min()
```

---

## 七、Phase 5: 实盘上线

### 7.1 实盘上线流程

```
第1周: 最小资金测试
  资金: 实际总资金的10%
  目标: 验证API连通、订单执行、数据同步

第2-3周: 半仓运行
  资金: 实际总资金的50%
  目标: 验证策略收益、滑点控制、风控触发

第4周+: 全仓运行
  资金: 实际总资金的100%
  目标: 稳定盈利，持续监控
```

### 7.2 华泰证券接入方案

#### 7.2.1 接入方案对比

| 方案 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **PTrade** | 官方稳定, 策略库 | 功能有限 | 中低频策略 |
| **迅投QMT** | 速度快, 功能全 | 接入复杂 | 高频,复杂策略 |
| **Easytrader** | 免费, 开源 | 非官方, 稳定性差 | 小资金,研究 |
| **聚宽对接** | 一键迁移 | 需聚宽会员 | 聚宽回测→实盘 |

#### 7.2.2 Easytrader接入示例

```python
import easytrader

# 连接华泰客户端
user = easytrader.use('ht_client')
user.connect(
    r'C:\ht_client\xiadan.exe',  # 华泰客户端路径
    'your_account', 
    'your_password'
)

# 交易函数
def execute_trade(user, stock, price, amount, direction):
    """执行交易"""
    if direction == 'buy':
        try:
            result = user.buy(stock, price=price, amount=amount)
            log.info(f"买入 {stock}, 价格 {price}, 数量 {amount}")
            return result
        except Exception as e:
            log.error(f"买入失败 {stock}: {e}")
            return None
    elif direction == 'sell':
        try:
            result = user.sell(stock, price=price, amount=amount)
            log.info(f"卖出 {stock}, 价格 {price}, 数量 {amount}")
            return result
        except Exception as e:
            log.error(f"卖出失败 {stock}: {e}")
            return None
```

### 7.3 实盘监控

```python
class LiveMonitor:
    """实盘监控器"""
    def __init__(self):
        self.drawdowns = []
        self.trades = []
        self.alerts = []
    
    def check_drawdown(self, current_value, peak_value):
        """检查回撤"""
        dd = (peak_value - current_value) / peak_value
        self.drawdowns.append(dd)
        
        if dd > 0.05:   # 5%: 告警
            self.send_alert(f"回撤达到 {dd*100:.1f}%")
        if dd > 0.10:   # 10%: 强警告
            self.send_alert(f"回撤超过 {dd*100:.1f}%, 建议减仓")
        if dd > 0.15:   # 15%: 熔断
            self.send_alert("熔断触发! 清仓操作!")
            self.execute_emergency_close()
    
    def send_alert(self, message):
        """发送告警 (Telegram/邮件)"""
        self.alerts.append({
            'time': datetime.now(),
            'message': message
        })
        print(f"[ALERT] {message}")
    
    def execute_emergency_close(self):
        """紧急清仓"""
        for stock in list(self.positions.keys()):
            self.sell(stock, self.prices[stock], self.positions[stock])
        self.cash = self.total_value()
```

---

## 八、执行策略开发流程

### 8.1 策略推进状态跟踪表

| 策略名称 | 研究 | 回测 | 影子战法 | 虚拟盘 | 实盘 | 状态 |
|----------|------|------|----------|--------|------|------|
| ETF轮动+RSRS | ✅ | ✅ | ✅ | ✅ | ▶️ | 运行中 |
| 可转债双低 | ✅ | ✅ | ✅ | ⏳ | - | 开发中 |
| 小市值基本面 | ✅ | ✅ | ⏳ | - | - | 研究中 |
| ... | ... | ... | ... | ... | ... | ... |

### 8.2 日度工作流

```
06:00-08:00 │ 检查前日收益 + 风控指标
08:00-09:00 │ 扫描今日信号 + 生成交易计划
09:30-15:00 │ A股盘面执行 + 监控
15:00-17:00 │ 收盘归因 + 日志记录
17:00-18:00 │ 向丘总汇报日报
18:00-06:00 │ 加密/美股策略 + 研究/回测
```

---

## 九、实盘API密钥安全规则

### 9.1 密钥管理

```bash
# 禁止将API Key写入代码或配置文件
# 使用环境变量存储

# .env文件示例 (禁止提交到git)
HUATAI_ACCOUNT=xxxxxx
HUATAI_PASSWORD=xxxxxx
BITGET_API_KEY=xxxxxx
BITGET_SECRET_KEY=xxxxxx

# 加载方式
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('BITGET_API_KEY')
```

### 9.2 安全规则清单

| 规则 | 说明 |
|------|------|
| 密钥不写死 | API Key 必须来自环境变量或密钥服务 |
| 最小权限 | API Key 只开交易权限，不开提币权限 |
| IP白名单 | 只允许烛龙服务器IP访问 |
| 金额限制 | 单笔交易上限、日交易总额上限 |
| 日志审计 | 所有交易操作记录日志 |
| 双重确认 | 实盘大额交易需丘总确认 |

---

> **烛龙量化神殿** 🐉  
> *先算风险，再算收益；用概率说话，用代码证明*
