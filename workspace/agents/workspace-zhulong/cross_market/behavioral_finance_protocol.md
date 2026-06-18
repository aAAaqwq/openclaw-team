# 🧠 认知偏差 → 可执行规则 · 实战手册

> **版本**：v1.0 | **适用**：烛龙量化系统/所有交易员
> **核心前提**：市场是亿万人类偏差的集合——认知偏差是Alpha来源，也是最大亏损根源
> **贴墙标语**：「偏差不可消灭，但可编码为规则」
> **更新**：2026-05-04

---

## 目录

- [第一部分：50种认知偏差的执行规则](#第一部分50种认知偏差的执行规则)
- [第二部分：情绪管理系统](#第二部分情绪管理系统)
- [第三部分：交易纪律铁律](#第三部分交易纪律铁律)
- [第四部分：旧烛龙心理篇精华提取](#第四部分旧烛龙心理篇精华提取)

---

<!-- ======================================================================= -->
<!--                         第一部分：50种认知偏差                            -->
<!-- ======================================================================= -->

# 第一部分：50种认知偏差的执行规则

每条规则格式：**偏差名称 → 交易表现 → 反制规则(R#) → 量化编码检测(M#)**

---

## 1. 确认偏误 (Confirmation Bias)

**定义**：只寻找/记住支持自己持仓的证据，忽视反面信息。

**交易表现**：
- 已买入后，只读看多研报，自动过滤看空信号
- 技术指标破位时自我合理化："这是洗盘"
- 把盈利归于能力，亏损归于运气

**反制规则 R-001**：
```
入场前必须写"反向论证"：
  □ 列出3个"这笔交易可能错"的理由
  □ 列出"如果我是空头，我会怎么攻击这个逻辑"
  □ 保存到交易笔记 → 出场时对照复盘
```

**量化检测 M-001**：
```python
def detect_confirmation_bias(trade_log):
    """检测：入场后是否系统性忽略反向信号"""
    for trade in trade_log:
        entry_signals = trade['pre_entry_signals']
        post_entry_signals = trade['post_entry_signals']
        # 计算入场后看空信号被忽略的比例
        ignored_bearish = sum(1 for s in post_entry_signals 
                            if s['direction']=='bearish' and s['ignored'])
        total_bearish = sum(1 for s in post_entry_signals if s['direction']=='bearish')
        if total_bearish > 0 and ignored_bearish / total_bearish > 0.7:
            trigger_alert("确认偏误超标：入场后忽略了{:.0%}的看空信号".format(
                ignored_bearish/total_bearish))
```

---

## 2. 锚定效应 (Anchoring)

**定义**：过度依赖第一眼看到的价格作为"参照物"。

**交易表现**：
- "这个币从100跌到50了，真便宜"（锚定在历史高点）
- 设定止盈在买入价+10%，不管走势强弱
- 等价格回到"我上次没买的价位"才进场

**反制规则 R-002**：
```
拒绝价格锚，只用估值/技术锚：
  □ 设止盈前，先问：当前价格相对于均线/ATR趋势如何？
  □ 拒绝"比最高点跌了X%"作为买入理由——改用"当前处于什么趋势阶段"
  □ 每次下单前，看30分钟K线和周线——打破短期锚定
```

**量化检测 M-002**：
```python
def detect_anchoring(orders, market_data):
    """检测：买入价是否与历史高点/低点过度锚定"""
    for order in orders:
        entry_price = order['price']
        high_52w = market_data['high_52w']
        low_52w = market_data['low_52w']
        # 如果买入理由是"从高点跌了很多"
        if order['note'] and '从' in order['note'] and '跌到' in order['note']:
            # 检查是否有其他技术逻辑
            if not order['has_technical_logic']:
                mark_anchoring_risk(order, severity='high')
    return anchoring_risk_score
```

---

## 3. 损失厌恶 (Loss Aversion)

**定义**：亏损的痛感远大于盈利的快感（约2~2.5倍）。

**交易表现**：
- 亏损5%死不卖，盈利5%赶紧跑
- 浮亏加仓摊平成本（而不是因为信号加强）
- 止损位到了却手动移除止损单

**反制规则 R-003**：
```
损失厌恶的克星是自动化止损：
  □ 入场同时挂好止损单——绝不依赖手动止损
  □ 浮亏加仓禁止令：除非信号再次确认，否则不因"摊平"加仓
  □ 盈亏比<1:2的交易不做（强迫用理性克服厌恶）
```

**量化检测 M-003**：
```python
def detect_loss_aversion(positions):
    """检测：浮亏持仓时间 vs 浮盈持仓时间"""
    for pos in positions:
        hold_time_loss = pos.get_hold_time_when_in_loss()
        hold_time_profit = pos.get_hold_time_when_in_profit()
        if hold_time_loss > hold_time_profit * 1.5:
            trigger_alert("损失厌恶：亏损持仓时间{:.1f}h >> 盈利持仓{:.1f}h".format(
                hold_time_loss, hold_time_profit))
            suggest_reduce_position(pos)
```

---

## 4. 处置效应 (Disposition Effect)

**定义**：过早卖出盈利资产，过久持有亏损资产。

**交易表现**：
- "先落袋为安"——盈利10%就卖，结果后面涨了100%
- 亏损的仓位一直扛着，"等回本再卖"
- 账户里全是亏损持仓，盈利的早卖光了

**反制规则 R-004**：
```
用移动止盈替代"固定止盈"：
  □ 盈利标的用跟踪止损（trailing stop），不让利润跑掉
  □ 亏损标的用固定时间止损（time stop）——持仓超过N天不盈利就清
  □ 每周审查：持仓超过1个月仍未盈利的，自动减半
```

**量化检测 M-004**：
```python
def detect_disposition_effect(portfolio):
    """检测：盈利持仓占比是否过低"""
    profit_positions = [p for p in portfolio if p.unrealized_pnl > 0]
    loss_positions = [p for p in portfolio if p.unrealized_pnl < 0]
    if len(profit_positions) < len(loss_positions) * 0.5:
        # 盈利的标的太少，亏损的太晚
        trigger_alert("处置效应警告：盈利持仓{}笔 vs 亏损持仓{}笔".format(
            len(profit_positions), len(loss_positions)))
        # 建议检查是否过早止盈
        for p in profit_positions:
            if p.hold_days < 3:
                mark_early_exit_risk(p)
```

---

## 5. 过度自信 (Overconfidence)

**定义**：高估自己的预测能力/交易水平。

**交易表现**：
- 连赚几笔后放大仓位
- 开始做杠杆/高风险品种（平时不做的）
- "这次不一样，我看到了别人没看到的"

**反制规则 R-005**：
```
连盈必减仓（反直觉但正确）：
  □ 连续盈利N笔 → 强制降低仓位20%
  □ 每天交易前读一遍"最近一次大亏是什么时候"
  □ 设"无交易日"——每周至少1天不看盘
  □ 每次放大仓位前，必须写"如果这次错了，最大亏损是多少，能否接受"
```

**量化检测 M-005**：
```python
def detect_overconfidence(trade_history, risk_params):
    """检测：连续盈利后仓位是否异常放大"""
    recent_trades = trade_history.last_n(20)
    consecutive_wins = 0
    for t in recent_trades:
        if t.pnl > 0: consecutive_wins += 1
        else: break
    
    current_position_ratio = risk_params.current_position / risk_params.base_position
    
    if consecutive_wins >= 5 and current_position_ratio > 1.2:
        trigger_alert("过度自信警告：连盈{}笔，仓位已放大{:.0%}".format(
            consecutive_wins, current_position_ratio))
        # 自动减仓信号
        suggest_position_reduce(by_percent=20)
    
    if consecutive_wins >= 3 and current_position_ratio > 1.5:
        lock_max_position("连盈强制降仓", max_ratio=1.0)
```

---

## 6. 后见之明 (Hindsight Bias)

**定义**：事后觉得"我早就知道会这样"——扭曲了对事前判断的记忆。

**交易表现**：
- "我就知道它会涨，可惜没买"
- 复盘时觉得"信号很明确"，但当时根本没看到
- 低估了自己的运气成分在盈利中的作用

**反制规则 R-006**：
```
事前记录 > 事后回忆：
  □ 每笔交易必须记录：入场前的预测(方向/目标位/止损位)
  □ 复盘时先看"事前记录"，再看"实际走势"
  □ 如果事前没有明确记录信号强度，复盘时不得评价"信号明显"
```

**量化检测 M-006**：
```python
def detect_hindsight_bias(notes):
    """检测：复盘评论中"早就知道"类语句频率"""
    hindsight_phrases = ['早就知道', '明显', '应该', '如果当时', '一看就是']
    count = sum(1 for phrase in hindsight_phrases if phrase in notes.review_text)
    if count >= 3:
        mark_bias_flag("后见之明：复盘使用了{}次事后话术".format(count))
        # 触发强制：下次必须先录预测再交易
```

---

## 7. 幸存者偏差 (Survivorship Bias)

**定义**：只看到成功者，忽略了大量失败者。

**交易表现**：
- "XX大神一个月翻倍"——没看到99个亏光的人
- 回测中只保留了还在交易的股票（忽略退市的）
- "这个策略历史年化50%"——没考虑参数过拟合

**反制规则 R-007**：
```
回测必须包含衰退股/退市股：
  □ 回测数据库必须包含退市、ST、暴跌标的
  □ 看任何人晒收益时，先问：总账户曲线呢？最大回撤呢？
  □ 样本外验证：至少25%的数据在训练集外
```

**量化检测 M-007**：
```python
def check_survivorship_bias(backtest_db):
    """检查回测数据集是否包含退市股票"""
    active_count = backtest_db.count_stocks(status='active')
    delisted_count = backtest_db.count_stocks(status='delisted')
    if delisted_count < active_count * 0.1:
        trigger_warning("幸存者偏差：退市股票仅{}/{}，需补充".format(
            delisted_count, active_count))
```

---

## 8. 近因效应 (Recency Bias)

**定义**：过分重视最近的数据而忽略长期趋势。

**交易表现**：
- 最近3天跌了就觉得熊市来了
- 因为昨天大涨而追高
- 用近1周的波动代替历史波动率做仓位管理

**反制规则 R-008**：
```
多个时间框架对照：
  □ 做决策前必须看：日K线 + 周K线 + 月K线
  □ 仓位大小与20日波动率挂钩，而非1日/3日
  □ 连跌/连涨后禁止做极端判断——等至少3根K线确认趋势反转
```

**量化检测 M-008**：
```python
def detect_recency_bias(signal, lookback_data):
    """检测：信号是否过度依赖近期数据"""
    # 检查信号的远期数据权重
    recent_weight = signal.weight_on_period(-5, 0)  # 最近5天
    long_weight = signal.weight_on_period(-60, -6)  # 之前55天
    if recent_weight > long_weight * 3:
        trigger_warning("近因效应：信号中近5天权重超过前期55天的3倍")
        # 自动用多时间框架验证
```

---

## 9. 沉没成本谬误 (Sunk Cost Fallacy)

**定义**：因为已经投入了时间和金钱，继续坚持错误的决策。

**交易表现**：
- "已经跌了这么多，现在卖就真亏了"
- "我研究了这个币3个月，不买就亏了"
- 扛单半年等回本——错过其他机会

**反制规则 R-009**：
```
沉没成本不是成本——只有未来走势才是：
  □ 清仓决策时：问"如果我现在空仓，还会买吗？"
  □ 如果答案是否定的 → 立即清仓
  □ 每月一次"清白审查"：假设刚继承100万现金，重置全部仓位
  □ 持仓累计N天不盈利 → 强制减半
```

**量化检测 M-009**：
```python
def detect_sunk_cost(positions, current_market):
    """检测：持仓是否因沉没成本而过长持有"""
    for pos in positions:
        if pos.hold_days > 60 and pos.unrealized_pnl < 0:
            # 持仓超过60天仍然亏损
            should_rebuy = should_buy_now(current_market, pos.asset)
            if not should_rebuy:
                trigger_alert("沉没成本：{}持仓{}天仍亏损，当前不会重新买入".format(
                    pos.asset, pos.hold_days))
                force_close_position(pos, reason="sunk_cost")
```

---

## 10. 羊群效应 (Herding / Herd Mentality)

**定义**：因为别人都在做所以跟着做。

**交易表现**：
- 看到群里/推特上都在吹某个币，忍不住追高
- "大家都在买，不买就错过了"
- 恐慌性抛售——别人卖我也卖

**反制规则 R-010**：
```
做第一个进场和最后一个出场的，而不是人群中的那一个：
  □ 社交媒体热度 > 阈值时（如推特趋势/群聊刷屏）→ 禁止买入
  □ 极度恐慌时（VIX > 30 / 群聊沉寂）→ 开始建仓
  □ 看任何"推荐"，先问：推荐它的有多少人已经上车了？
  □ 做空舆论高度一致的标的（共识=拥挤）
```

**量化检测 M-010**：
```python
def detect_herding(social_sentiment_data, order_book):
    """检测：交易是否与社交媒体情绪高度同步"""
    sentiment = social_sentiment_data.current_score()
    order_direction = get_recent_order_direction()
    
    if sentiment > 0.8 and order_direction == 'buy':
        # 极度看涨时买入 → 羊群信号
        mark_herd_bias_risk(trade, herd_score=0.9)
        trigger_stop("共識度過高，強制暫停買入")
    elif sentiment < 0.2 and order_direction == 'sell':
        # 极度看跌时卖出 → 恐慌甩售
        mark_herd_bias_risk(trade, herd_score=0.85)
```

---

## 11. 禀赋效应 (Endowment Effect)

**定义**：一旦拥有，就会高估它的价值。

**交易表现**：
- 自己手里的股票，估值总比没买的要高
- "我的持仓不一样，它基本面很好"
- 卖出的心理价位 > 市场的合理价位

**反制规则 R-011**：
```
没有"我的持仓"——只有"当前市场中的资产配置"：
  □ 持仓标的必须与未持仓标的用同一套估值模型打分
  □ 卖出决策参考外部评分，而非"我感觉它值多少"
  □ 每月做一次"盲评"：隐藏持仓标签后重新给每个标的价值打分
```

**量化检测 M-011**：
```python
def detect_endowment_effect(score_dict):
    """检测：自己持仓标的的评分是否系统性偏高"""
    held_scores = score_dict['held']
    unheld_scores = score_dict['unheld']
    if held_scores.mean() > unheld_scores.mean() * 1.2:
        trigger_alert("禀赋效应：持仓评分({:.2f}) > 非持仓({:.2f})x1.2".format(
            held_scores.mean(), unheld_scores.mean()))
```

---

## 12. 赌徒谬误 (Gambler's Fallacy)

**定义**：认为独立事件之间存在因果关系——"连开了10次大，该开小了"。

**交易表现**：
- "已经跌了5天了，肯定要反弹了"
- "连续止损3次了，下一次肯定赚"
- 在随机性较强的短线交易中过度使用反转策略

**反制规则 R-012**：
```
独立事件就是独立的：
  □ 连续亏损后 → 停止交易，不是加大仓位"回本"
  □ 连续盈利后 → 不认为"运气该用完了"而过早平仓
  □ 用统计检验：如果连亏后入场胜率没有显著差异，禁止反向押注
  □ 严格遵守信号：不要说"差不多了"，信号来了再动
```

**量化检测 M-012**：
```python
def detect_gamblers_fallacy(trades):
    """检测：连亏后是否系统性加大仓位试图"回本""""
    for i in range(3, len(trades)):
        recent = trades[i-3:i]
        if all(t.pnl < 0 for t in recent):
            # 连亏3笔
            if trades[i].position_size > trades[i-1].position_size * 1.5:
                trigger_alert("赌徒谬误：连亏后仓位放大{:.0%}".format(
                    trades[i].position_size / trades[i-1].position_size - 1))
```

---

## 13. 可得性启发 (Availability Heuristic)

**定义**：容易想到的事情更容易被高估概率。

**交易表现**：
- 因为最近听过一个"暴富故事"就买某个币
- 因为最近一个重大利空新闻就清仓所有同类资产
- 高估罕见事件（黑天鹅）的概率，低估常态

**反制规则 R-013**：
```
用概率代替记忆做决策：
  □ 每次因"最近听说"而交易 → 先查客观统计数据
  □ 决策前写：这件事的实际发生概率是多少？数据来源？
  □ 建立"常见错误决策库"——当触发已知的可用性模式时自动弹窗提醒
```

**量化检测 M-013**：
```python
def detect_availability_bias(decision_log, news_events):
    """检测：最近的重大新闻是否导致过度反应"""
    recent_big_news = [n for n in news_events if n.impact_score > 0.7]
    recent_decisions = decision_log.last_24h()
    if len(recent_big_news) > 0 and len(recent_decisions) > normal_volume * 2:
        # 重大新闻后交易量翻倍 → 可得性启发
        trigger_alert("可得性启发：重大事件后交易量异常{:.0f}笔".format(
            len(recent_decisions)))
```

---

## 14. 代表性启发 (Representativeness Heuristic)

**定义**：根据"像不像"而不是"概率是多少"来做判断。

**交易表现**：
- "这个走势图和上次暴涨前一模一样！"
- "连续3个月增长，肯定是个好公司"（样本太小）
- 看到少量相似特征就认为必然复制历史走势

**反制规则 R-014**：
```
像不等于就是——样本量决定置信度：
  □ 每次说"这个图形和上次一样"时 → 先问：统计上有多少类似形态？胜率？
  □ 拒绝"n=1"模式匹配——至少需要30个历史样本才能形成判断
  □ 用贝叶斯更新替代模式识别：先验概率 × 新证据 → 后验概率
```

**量化检测 M-014**：
```python
def detect_representativeness_bias(trade, pattern_db):
    """检测：是否基于小样本模式识别交易"""
    pattern_name = trade.get('pattern')
    if pattern_name and pattern_name in pattern_db:
        matches = pattern_db[pattern_name].total_matches
        hit_rate = pattern_db[pattern_name].win_rate
        if matches < 30:
            trigger_warning("代表性启发：'{}'仅{}个历史样本，胜率{:.0%}不可靠".format(
                pattern_name, matches, hit_rate))
```

---

## 15. 控制错觉 (Illusion of Control)

**定义**：高估自己对不可控事件的影响力。

**交易表现**：
- 反复刷新行情页面——仿佛多看两眼就会涨
- 不断调整止损止盈——感觉控制更精确
- 在根本由市场决定的事情上花费大量"操作"

**反制规则 R-015**：
```
你的控制范围只到"下单→止损→止盈"三步：
  □ 建立了策略 → 让策略运行 → 不要干扰
  □ 禁止在持仓期间反复查看行情（设定定时：每30分钟看一次）
  □ 止损止盈一旦设置，禁止盘中随意修改（除非有新的重要信息）
```

**量化检测 M-015**：
```python
def detect_control_illusion(operation_log):
    """检测：频繁修改止盈止损 → 控制错觉"""
    hourly_modifications = operation_log.count_modifications_per_hour()
    if hourly_modifications > 3:
        trigger_alert("控制错觉：1小时内修改止盈止损{}次，已强制锁定24h".format(
            hourly_modifications))
        lock_modifications(duration_hours=24)
```

---

## 16. 自利归因 (Self-Serving Bias)

**定义**：把成功归因于自己，把失败归因于外部因素。

**交易表现**：
- 赚了→"我的分析真准"；亏了→"庄家洗盘""黑天鹅"
- 从不承认自己是基本面决策错误
- 复盘时扭曲事实来保护自尊

**反制规则 R-016**：
```
统一的成功/失败归因框架：
  □ 每笔交易的复盘必须填写：盈利/亏损的具体原因（选择理由，非编辑框）
  □ 原因列表框固定：市场方向 / 技术信号 / 仓位管理 / 情绪 / 运气
  □ 当"运气"被选为唯一原因时，该笔盈利不计入"能力自信积分"
  □ 每季度统计"内外因比例"——如果外因>80%，警惕自利归因
```

**量化检测 M-016**：
```python
def detect_self_serving_bias(reviews):
    """检测：盈利交易归因于自身 vs 亏损归因于外部的比例"""
    internal_factors = ['技术', '分析', '策略', '判断']
    external_factors = ['市场', '庄家', '黑天鹅', '运气', '消息']
    
    for r in reviews:
        if r.pnl > 0 and any(f in r.attribution for f in internal_factors):
            self_credit += 1
        if r.pnl < 0 and any(f in r.attribution for f in external_factors):
            external_blame += 1
    
    if self_credit > 0 and external_blame > 0:
        ratio = self_credit / external_blame
        if ratio > 3:
            trigger_alert("自利归因：自夸/外部归因比例={:.1f}x".format(ratio))
```

---

## 17. 结果偏误 (Outcome Bias)

**定义**：根据结果的好坏而非决策过程的质量来评判。

**交易表现**：
- 赚了钱就觉得当时决策是对的（即使过程很烂）
- 亏了钱就觉得决策有问题（即使过程完全合理）
- 鼓励了"错误的正确"——鼓励了赌博行为

**反制规则 R-017**：
```
过程 > 结果——每次复盘先评决策质量，再看盈亏：
  □ 每次复盘先填"决策质量评分"，再填盈亏
  □ 建立一个"正确亏损"清单（决策对但结果差）→ 鼓励
  □ 建立一个"错误盈利"清单（决策差但运气好）→ 警惕
  □ 用预期价值(EV)替代盈亏作为评价标准
```

**量化检测 M-017**：
```python
def track_decision_quality(reviews):
    """追踪：决策质量评分与盈亏的关联"""
    correct_losses = 0  # 决策好但亏损
    wrong_profits = 0   # 决策差但盈利
    for r in reviews:
        if r.decision_score >= 7 and r.pnl < 0:
            correct_losses += 1
            add_to_correct_loss_list(r)
        if r.decision_score <= 3 and r.pnl > 0:
            wrong_profits += 1
            add_to_dangerous_profit_list(r)
    
    report = "正确亏损{}笔 | 错误盈利{}笔".format(correct_losses, wrong_profits)
    if wrong_profits > correct_losses:
        report += " ⚠️ 警惕错误盈利鼓励赌博行为"
```

---

## 18. 频数忽略 (Base Rate Neglect / Frequency Blindness)

**定义**：忽略事件的基础概率，只关注个例。

**交易表现**：
- "这个策略3个月赚了50%！"——忽略了统计上90%的类似策略都会亏
- 只盯着5%的暴富案例，忘了95%的亏损案例
- 追热点题材——只看到成功案例

**反制规则 R-018**：
```
先问基础概率，再问个例：
  □ 任何策略/推荐，先问：同类策略的历史成功率是多少？
  □ 下单前查看：该形态/信号的历史胜率和盈亏比
  □ 拒绝"大数据"——统计上显著才算数（p < 0.05）
```

**量化检测 M-018**：
```python
def check_base_rate(trade_type, strategy_db):
    """交易前检查基础概率"""
    base_rate = strategy_db.get_base_rate(trade_type)
    if base_rate < 0.35:  # 历史胜率低于35%
        trigger_stop("频数忽略：{}类交易基础胜率仅{:.0%}".format(
            trade_type.name, base_rate))
    return base_rate
```

---

## 19. 零风险偏差 (Zero-Risk Bias)

**定义**：偏好"绝对安全"的选项，即使收益微乎其微。

**交易表现**：
- 宁可年化2%的保本理财，也不做夏普2.0的策略
- 因为害怕微小亏损而错过大幅度盈利机会
- 过度对冲——花大量成本把尾部风险降到0

**反制规则 R-019**：
```
零风险=零收益——接受可控风险才能赚钱：
  □ 建立"可接受亏损预算"（如：月度-3%以内是正常的）
  □ 用夏普比率衡量策略，不用"会不会亏本金"
  □ 计算过度的机会成本：为了规避X风险，错过了多少收益？
```

**量化检测 M-019**：
```python
def detect_zero_risk_bias(portfolio):
    """检测：资金中是否过度配置在低收益/无风险资产"""
    risk_free_ratio = portfolio.risk_free_allocation / portfolio.total
    if risk_free_ratio > 0.5 and portfolio.expected_annual_return < 0.05:
        opportunity_cost = portfolio.opportunity_cost_estimation(target_sharpe=1.5)
        trigger_alert("零风险偏差：{}资金在无风险资产，年度机会成本约{:.2f}%".format(
            f"{risk_free_ratio:.0%}", opportunity_cost))
```

---

## 20. 时间贴现 (Temporal Discounting / Hyperbolic Discounting)

**定义**：低估未来收益，高估眼前快感。

**交易表现**：
- 选择日内短线而非中线趋势——即使中线的期望收益更高
- 因为"等不了"而过早止盈
- 频繁交易——用手续费换虚假的"参与感"

**反制规则 R-020**：
```
用延迟满足对抗冲动：
  □ 建立"冷却期"：买入前必须等15分钟（避免冲动入场）
  □ 区分"交易频率"和"盈利能力"——手续费算清后再决定
  □ 日内策略必须证明它的收益>时间成本+手续费成本
```

**量化检测 M-020**：
```python
def detect_time_discounting(trades):
    """检测：是否因过早止盈导致收益大幅缩水"""
    early_exits = 0
    profit_left = 0
    for t in trades:
        if t.is_early_exit:  # 被标记为过早退出
            early_exits += 1
            profit_left += t.max_unrealized_profit - t.actual_profit
    
    if early_exits > 5 and profit_left > 0:
        avg_left = profit_left / early_exits
        trigger_alert("时间贴现：{}笔过早止盈，平均每笔少赚{:.2f}".format(
            early_exits, avg_left))
        suggest_trailing_stop_review()
```

---

## 21. 框架效应 (Framing Effect)

**定义**：同一信息用不同方式表达，会影响判断。

**交易表现**：
- "上涨概率80%" vs "下跌概率20%"——偏向正面框架
- "保本" vs "可能亏损"——亏损框架更避讳
- 新闻标题语义偏差影响仓促决策

**反制规则 R-021**：
```
同一信息正反看两遍：
  □ 每次看信息时，问自己：如果反过来描述，我还会做同样决定吗？
  □ 把盈利说成"挽回损失"——看反应是否变化
  □ 对所有新闻/通知使用结构化提取（信号强度、置信度），而非原文
```

**量化检测 M-021**：
```python
def check_framing_effect(signals):
    """检测：信号表达方式是否改变决策"""
    positive_frame = signals.positive_frame()
    negative_frame = signals.negative_frame()
    
    pos_score = agent_evaluate(positive_frame)
    neg_score = agent_evaluate(negative_frame)
    
    if abs(pos_score - neg_score) > 0.3:
        trigger_warning("框架效应：正/反表述评分差{:.2f}".format(
            pos_score - neg_score))
```

---

## 22. 逆火效应 (Backfire Effect)

**定义**：面对反面证据时，信念反而更强了。

**交易表现**：
- 别人给反对意见时，不是重新思考，而是找更多理由坚持
- "你们不懂，这个币的潜力你们看不到"
- 越亏损越相信"马上就涨了"

**反制规则 R-022**：
```
强制倾听反面声音：
  □ 每买入一个标的，添加一个"看空"标签，自动推送看空理由
  □ 当持仓亏损超过5%时，自动推送该标的的利空新闻
  □ 每周有一个"质疑日"——专门找自己持仓的利空逻辑
```

**量化检测 M-022**：
```python
def detect_backfire_effect(conviction_scores):
    """检测：面对利空时是否反而加强信心"""
    for conviction in conviction_scores:
        if conviction.has_negative_news_triggered():
            before_news = conviction.score_before_news
            after_news = conviction.score_after_news
            if after_news > before_news * 1.2:
                trigger_alert("逆火效应：利空后信心反而提升{:.0%}".format(
                    after_news / before_news - 1))
```

---

## 23. 乌比冈湖效应 (Dunning-Kruger Effect / Lake Wobegon)

**定义**：低水平者高估自己，高水平者低估自己。

**交易表现**：
- 新手赚了几笔就以为自己是股神
- 老手越做越谦虚，反而对自己没信心
- 连亏时不敢止损——"我已经很厉害了，不可能判断错"

**反制规则 R-023**：
```
用客观指标代替自我评价：
  □ 不评判"我多厉害"—只看夏普比率、胜率、盈亏比
  □ 新手设置"自信指数缓冲期"：实盘前100笔视为"学习期"
  □ 禁用"我感觉""我觉得"——改用"信号强度XX""概率XX"
```

**量化检测 M-023**：
```python
def check_dunning_kruger(trade_stats, experience_level):
    """检测：新手是否过度自信"""
    win_rate = trade_stats.win_rate
    actual_sharpe = trade_stats.sharpe_ratio
    
    if experience_level == 'beginner' and trade_stats.trades < 50:
        if win_rate > 0.6:  # 新手胜率超过60%时
            # 模拟预期：可能是运气
            expected_sharpe_with_luck = simulate_expected_sharpe(n=50)
            if actual_sharpe < expected_sharpe_with_luck:
                trigger_warning("新手运气：实盘{}笔胜率{:.0%}，可能非能力所致".format(
                    trade_stats.trades, win_rate))
```

---

## 24. 承诺升级 (Escalation of Commitment)

**定义**：为了证明之前决策的正确性，不断加注已失败的策略。

**交易表现**：
- 越亏越加仓——"我就不信它不涨"
- 补仓已经不是基于分析，而是基于"不服气"
- "我已经亏了这么多，现在放弃前面的钱就白亏了"

**反制规则 R-024**：
```
设定"加仓→新分析"铁律：
  □ 加仓的唯一理由：新的买入信号出现——不是"摊平成本"
  □ 每加仓一次，必须独立评估——仿佛从未持有过
  □ 同一标的加仓不超过3次
  □ 建仓后亏损超过10%，禁止加仓（无论任何理由）
```

**量化检测 M-024**：
```python
def detect_commitment_escalation(positions):
    """检测：亏损后是否因'不服'而加仓"""
    for pos in positions:
        if pos.in_loss() and pos.additional_buys > 0:
            for add_buy in pos.additional_buys:
                if not add_buy.had_new_signal:
                    trigger_alert("承诺升级：{}亏损中加仓且无新信号".format(pos.asset))
                    flag_trade_review(add_buy)
```

---

## 25. 选择性知觉 (Selective Perception)

**定义**：用已有信念过滤输入信息——只能看到想看的。

**交易表现**：
- 看多的人只关注MACD金叉，忽略量价背离
- 看空的只看到阻力位，看不到支撑位
- 同一个K线图，不同立场看到不同故事

**反制规则 R-025**：
```
结构化分析模板——防止"跳过不想看的指标"：
  □ 使用固定的分析清单：技术面/基本面/资金面/情绪面必须全填
  □ 每次分析用同一套模板，不能跳过任一项目
  □ 先用反向立场筛选一遍信息——如果你是空头，你看什么
```

**量化检测 M-025**：
```python
def check_selective_perception(analysis_checklist):
    """检查分析模板完整性"""
    required_items = ['technical', 'fundamental', 'capital_flow', 'sentiment']
    missed = [item for item in required_items if not analysis_checklist.is_filled(item)]
    if len(missed) > 0:
        trigger_warning("选择性知觉：分析跳过{}项".format(missed))
    return len(missed) == 0
```

---

## 26. 权威偏误 (Authority Bias)

**定义**：过度信任权威人物的观点。

**交易表现**：
- "XX分析师说的，肯定没错"
- "知名机构买了这个币，我跟着买"
- 因为某大佬的一条推文而重仓

**反制规则 R-026**：
```
权威的观点也需要独立验证：
  □ 建立"权威信任度衰减机制"——每次跟随错误-30%信任分
  □ 抄任何大佬作业 → 必须用自己的逻辑再过一遍
  □ 区分"信息"和"决策"——大佬提供信息，你来决策
  □ 权威观点置信度自动衰减：首次有效+20分，首次无效-30分

**量化检测 M-026**：
```python
def check_authority_bias(follow_trades):
    """检测：是否过度跟随权威"""
    authority_score = {}
    for trade in follow_trades:
        authority = trade.get('followed_person')
        if not authority:
            continue
        if authority not in authority_score:
            authority_score[authority] = {'follows': 0, 'wins': 0}
        authority_score[authority]['follows'] += 1
        if trade['pnl'] > 0:
            authority_score[authority]['wins'] += 1
    
    for auth, stats in authority_score.items():
        # 首次权重高但惩罚也重
        win_rate = stats['wins'] / stats['follows'] if stats['follows'] > 0 else 0
        net_score = 20 + (win_rate - 0.5) * 100 - (1 - win_rate) * 60
        if net_score < -10:
            trigger_warning("权威偏误：{}净信任分{:.0f}，建议暂停跟随".format(auth, net_score))
```

---

## 27. 从众效应 (Bandwagon Effect)

**定义**：别人都在做，所以跟着做——忽视自己的独立判断。

**交易表现**：
- FOMO追高——"大家都在买这个币，我不买就亏了"
- 看到群里某人晒单盈利后立刻跟单
- 社交媒体上某个标的讨论爆棚时入场

**反制规则 R-027**：
```
从众检测机制：
  □ 任何"大家都在买"的信号 → 暂缓24h再入场
  □ 社交媒体热度超过阈值 → 反向思考：人声鼎沸处风险最高
  □ 建仓前自问：如果没人知道这个标的，我还会买吗？
  □ 记录"跟风交易"标签 → 复盘时统计胜率
```

**量化检测 M-027**：
```python
def detect_herding(social_heat, volume_surge, price_change):
    """检测潜在的从众行为"""
    if social_heat > 80 and volume_surge > 200:
        trigger_warning("从众效应：社交热度{}+成交量暴增{}%".format(social_heat, volume_surge))
        return {'risk': 'high', 'action': 'delay_24h'}
    if social_heat > 60 and price_change > 15:
        trigger_warning("从众效应：热度+涨幅双高")
        return {'risk': 'medium', 'action': 'halve_position'}
    return {'risk': 'low', 'action': 'normal'}
```

---

## 28. 对比效应 (Contrast Effect)

**定义**：事物的评价受同时出现的参照物影响，而非其本身价值。

**交易表现**：
- 先看一个涨100%的币，再看涨20%的币觉得"不够好"
- 连续大亏后看到小幅回本就急于平仓
- 用"之前的价位"来判断当前价格是否便宜

**反制规则 R-028**：
```
绝对估值优先：
  □ 每个标的独立做估值/技术分析，不做横向对比
  □ "从最高点跌了90%"不是买入理由——看它现在值不值
  □ 连续盈利后降低仓位标准——此时容易高估机会
  □ 连续亏损后不接受"将就"的交易——宁可空仓
```

**量化检测 M-028**：
```python
def detect_contrast_bias(portfolio, new_trade):
    """检测是否受对比效应影响"""
    recent_pnl = portfolio.recent_trades(10)
    avg_pnl = sum(t.pnl for t in recent_pnl) / len(recent_pnl)
    
    if avg_pnl > 5:  # 连续盈利
        if new_trade.confidence < 0.7:
            trigger_warning("对比效应：连续盈利后可能低估风险")
    elif avg_pnl < -5:  # 连续亏损
        if new_trade.confidence > 0.9:
            trigger_warning("对比效应：连续亏损后可能高估机会")
    return False
```

---

## 29. 邓宁-克鲁格效应 (Dunning-Kruger Effect)

**定义**：能力差的人高估自己，能力强的人低估自己。

**交易表现**：
- 新手刚盈利几笔就觉得自己是天才，开始加大仓位
- 老手连续亏损后怀疑整个系统
- "我就知道会涨"——盈利后把运气当能力
- 实盘前信心爆棚，实盘后才发现完全不一样

**反制规则 R-029**：
```
能力校准机制：
  □ 盈利20%以上时触发"过度自信检查"
  □ 连续盈利5笔 → 减仓20%（对抗膨胀）
  □ 保存所有交易记录 → 每周末复盘自己的"真实胜率"
  □ 不要用"最大盈利"来评估自己，用"夏普比率"
```

**量化检测 M-029**：
```python
def track_dunning_kruger(trade_log):
    """跟踪能力感知偏差"""
    recent_30 = trade_log.tail(30)
    win_rate = sum(1 for t in recent_30 if t.pnl > 0) / 30
    sharpe = calculate_sharpe(recent_30)
    avg_win = sum(t.pnl for t in recent_30 if t.pnl > 0) / max(1, sum(1 for t in recent_30 if t.pnl > 0))
    avg_loss = abs(sum(t.pnl for t in recent_30 if t.pnl < 0) / max(1, sum(1 for t in recent_30 if t.pnl < 0)))
    
    if sharpe < 0.5 and win_rate > 0.6:
        trigger_warning("DK偏差：夏普低但胜率高——可能伪胜率")
    if avg_win / max(1, avg_loss) < 1.2 and win_rate > 0.6:
        trigger_warning("DK偏差：小赚大亏胜率陷阱")
    return {'sharpe': sharpe, 'win_rate': win_rate, 'flag': sharpe < 1.0}
```

---

## 30. 期望偏差 (Expectation Bias)

**定义**：预期影响感知——你看到你想看到的。

**交易表现**：
- 因为"预期它会涨"，所以看到的一切信号都是看涨的
- 财报前已经预设立场，选择性解读数据
- "这个形态上次涨了，这次也一定涨"

**反制规则 R-030**：
```
盲点分析强制：
  □ 入场前写出"如果我是对手方，我为什么是对的"
  □ 用固定分析模板，不跳过任何一步
  □ 先分析"行情现在实际在干什么"，再说"我想要什么"
```

**量化检测 M-030**：
```python
def check_expectation_bias(analysis, position):
    """检查分析是否存在期望偏差"""
    bias_signals = []
    if position == 'long' and analysis.get('bearish_signals', 0) == 0:
        bias_signals.append("持多头但完全看不到空头信号")
    if position == 'short' and analysis.get('bullish_signals', 0) == 0:
        bias_signals.append("持空头但完全看不到多头信号")
    return bias_signals
```

---

## 31. 聚焦效应 (Focusing Effect)

**定义**：过度关注一个因素，忽略其他相关因素。

**交易表现**：
- 只看MACD金叉入场，忽略量价背离、压力位、市场环境
- 单一指标为王，其他信号全部忽视
- "因为PE低所以买"——忽视了成长性、负债率、行业前景

**反制规则 R-031**：
```
多维分析强制：
  □ 任何交易必须通过至少3个维度的交叉验证
  □ 每个分析的开始先列出"这个标的我要看哪些维度"
  □ 设置"最小分析深度"——不能只看两个指标就下单
```

**量化检测 M-031**：
```python
def detect_focusing_bias(decision_log):
    """检测：决策中单个维度是否过度主导"""
    dimension_weights = {'technical': 0, 'fundamental': 0,
                        'sentiment': 0, 'capital_flow': 0, 'macro': 0}
    for decision in decision_log:
        for dim in decision['dimensions_used']:
            dimension_weights[dim] += 1
    total = sum(dimension_weights.values())
    if total > 0:
        max_dim = max(dimension_weights, key=dimension_weights.get)
        max_weight = dimension_weights[max_dim] / total
        if max_weight > 0.6:
            trigger_warning("聚焦效应：{}维度权重{:.0%}，决策偏科严重".format(
                max_dim, max_weight))
```

---

## 32. 框架效应 (Framing Effect)

**定义**：同一个问题因表述方式不同而做出不同决策。

**交易表现**：
- "亏了20%"听起来比"之前盈利30%现在回撤到10%"更痛苦
- 浮亏时"这只是暂时调整" vs 浮盈时"赶紧止盈"
- 用百分比还是绝对值思考完全不同

**反制规则 R-032**：
```
统一决策框架：
  □ 所有交易决策统一用"R倍数"衡量（1R=初始风险）
  □ 不要用"浮亏"思考——用"当前价格是否符合入场逻辑"
  □ 固定止损不移、固定止盈不移——不受框架变化影响
```

**量化检测 M-032**：
```python
def check_framing_effect_v2(signals):
    """检测：同一信息不同框架下的决策一致性"""
    for signal in signals:
        pos_frame = format_signal(signal, frame='positive')
        neg_frame = format_signal(signal, frame='negative')
        score_pos = evaluate_signal(pos_frame)
        score_neg = evaluate_signal(neg_frame)
        variance = abs(score_pos - score_neg)
        if variance > 0.25:
            trigger_warning("框架效应敏感：正负框架评分差{:.2f}".format(variance))
```

---

## 33. 赌徒谬误 (Gambler's Fallacy)

**定义**：认为独立事件的概率会受到历史结果影响。

**交易表现**：
- "已经跌了5天了，今天该涨了吧"
- "连续3笔亏损了，下一笔肯定赢"
- 认为"这么久没出信号了，下一个信号一定好"

**反制规则 R-033**：
```
概率独立原则：
  □ 每一笔交易重新评估——不看过去连续结果
  □ 连亏后不"赌一把回本"——那是最危险的时刻
  □ 策略信号是独立事件——历史不影响下次概率
  □ 但注意：连亏可能是策略失效的信号（这不同）
```

---

## 34. 光环效应 (Halo Effect)

**定义**：一个方面的好印象影响对其他方面的判断。

**交易表现**：
- "这个公司CEO很厉害，所以股票一定好"
- "这个币技术很强，所以一定会涨"
- 因为某个指标好看就忽视了其他风险

**反制规则 R-034**：
```
分离评估原则：
  □ 基本面、技术面、资金面独立打分
  □ 好的CEO ≠ 好的入场时机
  □ 好的技术 ≠ 好的价格
  □ 每个维度独立评估，最后汇总
```

---

## 35. 意向性偏见 (Intentionality Bias)

**定义**：将随机事件归因于有意的操纵。

**交易表现**：
- "庄家在洗盘/拉升/打压我"
- "市场针对我的仓位"
- 给每一根K线都编一个"阴谋故事"

**反制规则 R-035**：
```
概率思维原则：
  □ 承认大部分价格波动是随机的，不是针对你
  □ 区分"市场行为"和"个人想象"
  □ 你的仓位对市场而言毫无意义——别把自己当中心
  □ 可以用"庄家思维"辅助理解，但别用它来决策
```

---

## 36. 损失厌恶深度版 (Loss Aversion - Extended)

**定义**：损失带来的痛苦约等于同等盈利带来的快乐的2倍。

**交易表现**：
- 浮亏仓提前死扛不割，浮盈仓早早止盈
- "不卖就不算亏"的鸵鸟心态
- 把止损位越移越远来"避免止损"
- 宁愿赌一把也不接受确定的损失

**反制规则 R-036**：
```
损失厌恶的4条铁律：
  □ 入场同时设止损，止损执行自动，不手动干预
  □ 止损不是在"亏钱"，是在"执行规则"——这是两件事
  □ 盈利时逐步上移止损（锁定利润），亏损时不后移止损
  □ 每季度做一次"止损执行率"审计——有多少次没执行
```

**量化检测 M-036**：
```python
def detect_loss_aversion(trades):
    """检测损失厌恶行为"""
    violations = []
    for t in trades:
        if t.stop_loss_moved_back:
            violations.append("止损后移：{} 从{}移到{}".format(t.symbol, t.original_sl, t.final_sl))
        if t.take_profit_moved_down:
            violations.append("止盈前移：{} 从{}移到{}".format(t.symbol, t.original_tp, t.final_tp))
    return violations
```

---

## 37. 消极偏见 (Negativity Bias)

**定义**：负面信息比正面信息更容易被记住和影响决策。

**交易表现**：
- 一次大亏之后好几个星期不敢交易
- 记不住10笔盈利，只记得1笔亏损
- "上次这个形态亏了，这次肯定也不行"

**反制规则 R-037**：
```
平衡记忆法则：
  □ 每周末只统计"总体表现"（夏普/胜率/盈亏比）不看单笔
  □ 建立"盈利交易"复盘集——记住你做对了什么
  □ 亏损后的冷静期严格限制——最多停3天，必须重启
```

---

## 38. 正常化偏见 (Normalcy Bias)

**定义**：低估灾难性事件发生的可能性以为一切正常。

**交易表现**：
- "312大跌不会再来一次"
- "这次LUNA崩盘是特例"
- 极端行情来了还以为是正常回调

**反制规则 R-038**：
```
黑天鹅准备原则：
  □ 每年至少做一次"极端行情模拟"
  □ 永远保留30%以上的现金/稳定币
  □ 极端行情来了不是"扛"，是先减仓再评估
  □ 正常化偏见的反制：假设"最坏情况每2年发生一次"
```

---

## 39. 乐观偏见 (Optimism Bias)

**定义**：高估好结果发生的概率，低估坏结果。

**交易表现**：
- "这次不一样"——每次都说服自己现在是特殊机会
- 高估自己选股/选币的能力
- "最大回撤不会超过20%"——但你入场时已经回撤15%

**反制规则 R-039**：
```
悲观压力测试：
  □ 每个策略入场前做"它亏50%我会怎么办"的推演
  □ 预设最坏情况，不是最好情况
  □ 盈利预期打对折——如果年化20%就按10%规划
```

---

## 40. 结果偏误 (Outcome Bias)

**定义**：根据结果好坏评判决策质量，而非决策过程。

**交易表现**：
- "赚了=做对了，亏了=做错了"
- 错误的决策因为"运气好赚钱了"而被重复使用
- 正确的决策因为"运气差亏钱了"而被放弃

**反制规则 R-040**：
```
过程评估系统：
  □ 每笔交易复盘分两部分：决策质量 + 运气因素
  □ 好的决策也可能亏钱（概率的必然），坏决策也可能赚钱
  □ 坚持用"决策质量评分"（纪律、逻辑、风险管理）
  □ 不因一次结果改变整个策略
```

---

## 41. 规划谬误 (Planning Fallacy)

**定义**：系统性地低估完成任务所需的时间和成本。

**交易表现**：
- "这个策略下个月就能稳定盈利"
- 开发新策略时过于乐观的时间估计
- "再优化一下参数就能更好了"

**反制规则 R-041**：
```
保守估计法则：
  □ 所有计划的时间乘以2、成本乘以1.5
  □ 策略开发到实盘至少3个月（非紧急情况）
  □ "再优化一下"往往是过拟合的开始——适可而止
```

---

## 42. 投射偏差 (Projection Bias)

**定义**：认为别人和自己有相同的想法/价值观/风险偏好。

**交易表现**：
- "这个价位我肯定不卖，所以别人也不卖"
- "我都看出来这是顶了，别人肯定也看出来了"
- 把自己的风险承受能力当作市场的"正常水平"

**反制规则 R-042**：
```
多样化思维原则：
  □ 市场由亿万不同目标的人组成，他们和你想的不一样
  □ 你恐惧时有人贪婪（你的卖盘是别人的买盘）
  □ 不要用自己的风险偏好推测市场行为
```

---

## 43. 近期偏差 (Recency Bias)

**定义**：最近发生的事对判断影响过大。

**交易表现**：
- 连续几天上涨后觉得"牛市来了"——其实可能是反弹
- 刚经历过暴跌就觉得"完了，熊市了"
- 用最近3天的行情推测未来3个月

**反制规则 R-043**：
```
长期视野框架：
  □ 决策至少参考3个时间框架（日/周/月或更高）
  □ 最近的3根K线不能决定方向——结构说了算
  □ 每周回头看一次——上周的恐慌/贪婪现在看是否合理
```

**量化检测 M-043**：
```python
def check_recency_bias(trades, days_back=60):
    """检查是否被近期信号过度影响"""
    recent = trades.tail(days_back)  # 最近60天
    older = trades.head(len(trades) - days_back)  # 之前
    if len(older) == 0: return
    recent_sharpe = calculate_sharpe(recent)
    older_sharpe = calculate_sharpe(older)
    if abs(recent_sharpe - older_sharpe) > 1.0:
        trigger_warning("近期偏差：近期表现与长期差异大")
```

---

## 44. 回归谬误 (Regression Fallacy)

**定义**：把回归均值误认为是某种趋势变化。

**交易表现**：
- 极端行情后以为"市场变了"——实际只是正常回归
- "这次不一样"——每次都信
- 连亏后以为系统坏了——实际上只是概率回归

**反制规则 R-044**：
```
回归均值原则：
  □ 极端表现后3次连续确认才能改变判断
  □ 理解"均值回归是统计必然"，不是市场给你信号
  □ 策略的评估周期至少20笔交易——不能以几笔定论
```

---

## 45. 自我服务偏差 (Self-Serving Bias)

**定义**：把成功归因于自己，把失败归因于外部。

**交易表现**：
- "我赚了因为我看得准" vs "亏了因为庄家太坏"
- 盈利时觉得是自己的能力，亏损时怪市场/怪消息
- 从不真正承认自己的错误

**反制规则 R-045**：
```
客观归因原则：
  □ 每笔交易归因分析必须写"自己犯了什么错"
  □ 盈利交易也要写"有没有运气成分"
  □ 亏损交易90%是自己的原因——先从这个假设出发
  □ 归因不客观 → 下一笔还会犯同样的错
```

---

## 46. 错误共识效应 (False Consensus Effect)

**定义**：高估他人与自己观点一致的程度。

**交易表现**：
- "大家都觉得会涨"——其实是你自己觉得
- 认为市场应该按照你的分析走
- 不理解为什么有人会在"这个价位"做相反操作

**反制规则 R-046**：
```
反对意见强制：
  □ 每次分析必须写出"做多和做空的理由"（各至少3条）
  □ 如果你找不到3条反向理由 → 说明你还不够理解
  □ 记住：每次成交就意味着买卖双方严重分歧
```

---

## 47. 现状偏差 (Status Quo Bias)

**定义**：偏好保持当前状态，不愿意改变。

**交易表现**：
- 明知策略在衰减还舍不得切换
- 仓位已经严重偏离计划还不想调整
- "一直这么做的"不是好理由

**反制规则 R-047**：
```
定期强制调整：
  □ 每月强制回顾：当前持仓各标的的理由是否还站得住
  □ 策略衰减到阈值就必须淘汰——不管过去多辉煌
  □ 每季度做"从零开始建仓"推演——如果现在空仓会买什么
```

---

## 48. 可得性启发 (Availability Heuristic)

**定义**：容易想到的例子被高估其概率。

**交易表现**：
- 因为最近有人靠XX翻倍了，就觉得这个策略胜率很高
- 媒体报道最多的币觉得"肯定涨"
- 刚学到一个新形态就觉得到处都是

**反制规则 R-048**：
```
统计数据高于案例：
  □ 不根据"个例"做决策——看统计数据
  □ 每个策略的评估基于至少100次交易样本
  □ 传奇故事（一个散户靠XX赚了100倍）没有统计意义
  □ 你记住的都是幸存者——那些亏了的人不会晒单
```

---

## 49. 沉没成本谬误深度版 (Sunk Cost Fallacy - Extended)

**定义**：因为已经投入了时间/金钱/精力而继续坚持错误决策。

**交易表现**：
- "我都研究这个股票研究了1个月，不能不买"
- "已经亏了这么多，现在卖就是真的亏了"
- "策略开发花了3个月，就算不好也得用"

**反制规则 R-049**：
```
沉没成本铁律：
  □ 过去投入的每一分钱/时间都与当前决策无关
  □ 唯一的问题：如果不持有，现在会买吗？不会→卖出
  □ 策略评估只看未来——过去的开发成本是沉没成本
  □ "已经亏了"是放弃的好理由——别因为亏得多而加仓
```

---

## 50. 时间贴现 (Temporal Discounting)

**定义**：倾向于选择小额的立即回报而非大额的延迟回报。

**交易表现**：
- 做短线赚小钱比持有等待大行情更"安心"
- 频繁交易——"我觉得日内波动就能赚钱"
- 不愿意等待策略信号出现，想"先进场再说"
- 过早止盈——因为"现在赚总比以后亏好"

**反制规则 R-050**：
```
延迟满足训练：
  □ 设置"最小持仓时间"——入场后不到4h不允许手动平仓
  □ 耐心回报：统计提前止盈和持有到目标的差异
  □ 每减少一次无效交易 → 奖励自己
  □ 记住：高频≠高利润，交易越少的人往往赚得越多
```

---

<!-- ======================================================================= -->
<!--                     第二部分：情绪管理系统                              -->
<!-- ======================================================================= -->

# 第二部分：情绪管理系统

## 一、情绪识别引擎

交易者在不同情绪状态下的决策质量差异巨大。以下是通过交易数据反推情绪状态的检测器：

### ER-1: 基于交易行为的情绪诊断

```python
def diagnose_emotion(trade_log, window=10):
    """通过最近N笔交易推断情绪状态"""
    recent = trade_log.tail(window)
    
    # 检测指标
    frequency = window / (recent.iloc[-1]['timestamp'] - recent.iloc[0]['timestamp']).total_seconds() * 86400
    avg_position_size = recent['size'].mean() / trade_log['size'].mean()
    win_streak = 0
    loss_streak = 0
    tmp_w, tmp_l = 0, 0
    for _, t in recent.iterrows():
        if t.pnl > 0:
            tmp_w += 1
            tmp_l = 0
        else:
            tmp_l += 1
            tmp_w = 0
        win_streak = max(win_streak, tmp_w)
        loss_streak = max(loss_streak, tmp_l)
    
    diagnosis = {'emotion': 'normal', 'actions': []}
    
    # 恐惧检测
    if loss_streak >= 3 and avg_position_size < 0.7:
        diagnosis = {'emotion': 'fear', 'actions': ['force_stop_24h', 'reduce_size_50%']}
    
    # 贪婪检测
    if win_streak >= 5 and avg_position_size > 1.3:
        diagnosis = {'emotion': 'greed', 'actions': ['force_reduce_20%', 'check_all_stops']}
    
    # 复仇交易
    if loss_streak >= 2 and frequency > 20:
        diagnosis = {'emotion': 'revenge', 'actions': ['force_stop_48h', 'disable_trading']}
    
    # 绝望/麻木
    if loss_streak >= 5 and frequency < 1:
        diagnosis = {'emotion': 'despair', 'actions': ['review_strategy', 'talk_to_partner']}
    
    # 过度自信
    if win_streak >= 8 and avg_position_size > 1.5:
        diagnosis = {'emotion': 'overconfidence', 'actions': ['force_reduce_30%', 'increase_stops']}
    
    return diagnosis
```

### ER-2: 情绪状态速查

| 情绪 | 表现 | 正确操作 |
|------|------|---------|
| 😨 恐惧 | 不敢入场/过早止盈/不敢持仓 | 检查系统规则是否触发，未触发就执行 |
| 🤑 贪婪 | 追涨/仓位过大/不顾信号 | 减仓20%+检查所有止损 |
| 😤 复仇 | 连续重仓/不止损/追回亏损 | 强制停48小时 |
| 😌 过度自信 | 仓位过大/不复盘/听不进反对意见 | 减仓30%+写反向分析 |
| 😩 疲惫 | 交易频率下降/分析质量下降 | 停24h+休息 |
| 🫥 绝望 | 连续亏损后不敢交易 | 检查策略是否失效 + 寻求外部意见 |

## 二、情绪管理规则

### 规则组E：自动情绪规则

```
E-001 [连亏强制停] 连续3笔亏损 → 强制停止交易24h
  → 期间做：复盘前3笔亏损 + 重新检查市场环境
  → 24h后：半仓重新开始（恢复前不扩仓）

E-002 [连盈强制减仓] 连续5笔盈利 → 减仓20%保护利润
  → 对抗过度自信：盈利期最容易犯大错
  → 同时检查：止损设置是否还合理

E-003 [日亏损限制] 单日总亏损 > 总资金2% → 当日强制停止
  → 按风险管理系统触发黄牌
  → 次日只能以50%仓位开始

E-004 [周亏损限制] 本周总亏损 > 总资金5% → 本周停止交易
  → 全面复盘本周所有交易
  → 检查策略是否失效
  → 下周一从半仓开始

E-005 [早盘冷静期] 开盘前30分钟不进行任何新交易
  → 只处理已有仓位的止损调整
  → 30分钟后正式评估信号，再做决策

E-006 [极端行情规则] 单日振幅 > 5%（A股）或 > 10%（加密）
  → 暂停所有新交易
  → 检查所有止损
  → 考虑是否需要减仓
  → 等待振幅缩小后再操作

E-007 [心态检查] 每次下单前自问：
  □ 这笔交易是因为信号还是因为情绪？
  □ 如果空仓，我会不会在这个位置入场？
  □ 我是不是在为了"回本"而交易？
  □ 我的仓位是不是和平时一样大？（太大→警惕）
```

## 三、盘前自检清单

```
╔══════════════════════════════════════════╗
║        盘前心理状态自检清单                ║
╠══════════════════════════════════════════╣
║                                          ║
║ □ 我睡了至少7小时                         ║
║ □ 今天没有重要外部压力（工作/家庭/健康）    ║
║ □ 昨天的亏损/盈利已经被消化，不影响今天     ║
║ □ 我清楚地知道今天要执行哪些策略信号        ║
║ □ 我已经设置好今天的最大亏损限额            ║
║ □ 我不是为了"回本"而交易                   ║
║ □ 我知道如果今天亏损会是什么感觉            ║
║ □ 我有足够的耐心等待信号，不强求交易        ║
║                                          ║
║ 全部✅ → 可以开盘                         ║
║ 有❌   → 减少仓位至50% + 仅执行机械信号   ║
╚══════════════════════════════════════════╝
```

## 四、盘中纠偏卡

```
╔══════════════════════════════════════════╗
║        盘中心理纠偏卡                      ║
╠══════════════════════════════════════════╣
║                                          ║
║ 感觉不对时的自我提问：                     ║
║                                          ║
║ □ 我现在的情绪是？________________        ║
║ □ 我有没有遵守入场时的交易计划？ 是/否      ║
║ □ 我是不是在看新的信号？ 是/否 (坚持原计划) ║
║ □ 我是不是在移动止损？ 是/否 (坚持原止损)  ║
║ □ 现在的价格波动在我的计划内吗？           ║
║   → 在计划内 → 持仓不动                  ║
║   → 突破计划 → 先减仓，再评估            ║
║                                          ║
║ 记住：不要在市场剧烈波动时做任何决定        ║
║ 永远等5分钟再决定                        ║
╚══════════════════════════════════════════╝
```

---

<!-- ======================================================================= -->
<!--                       第三部分：交易纪律铁律                            -->
<!-- ======================================================================= -->

# 第三部分：交易纪律铁律

## 一、入场纪律 ⚔️

```
D-001 不追涨追跌：错过就错过，不弥补
  → 错过入场点后最少等1根K线（震荡后再考虑）

D-002 不听消息交易：任何"内幕""小道""群里说的"都不做入场依据
  → 消息只用来触发研究，不触发交易

D-003 不"感觉"入场：所有入场必须有系统信号触发
  → 盘感是大量经验的直觉化输出，但新手没有盘感

D-004 不"先入场再说"：没有计划就不入场
  → 入场前必须写清楚：入场价/止损/止盈/仓位/逻辑（最少3句话）

D-005 不重仓单一标的：单一标的 < 总资金的20%
  → 再看好也不能突破这个限制
```

## 二、持仓纪律 ⚔️

```
D-006 不移动止损向反方向：止损只能上移（做多）或下移（做空）
  → 违反一次 → 停1天交易
  → 违反两次 → 停1周

D-007 不加死仓：亏损中的仓位绝不加仓摊平
  → 亏损加仓 = 在错误上面再叠加错误

D-008 不"再看看"：信号反转就出场，不等
  → 技术破位 = 出场，不管盈亏
  → 犹豫的时候减仓

D-009 不只关注浮盈浮亏：持仓期间只关注信号是否还成立
  → 浮盈是未实现的，账面浮亏也不代表真的亏了
  → 唯一可以决定持仓的是：入场逻辑是否还在

D-010 不"锁仓"逃避：锁仓是伪风控，实质是不认错
  → 如果方向错了 → 出场，重新评估
```

## 三、出场纪律 ⚔️

```
D-011 不贪最后一分钱：接近目标位 + 信号减弱 = 提前出场
  → "最高/最低是别人的，中间是我的"

D-012 不止盈过早：达到目标前不移止盈
  → 除非出现反向结构信号

D-013 不止损过晚：止损严格执行，不幻想
  → 止损是纪律，不准违反
  → 止损触发后24h内不重新入场同一个标的

D-014 不平所有仓位：分批出场，不一次性全平
  → 第一次：50%在目标1（1:1R）
  → 第二次：30%在目标2（1:2R）
  → 第三次：20%移动止盈（博取更大空间）
```

## 四、资金纪律 ⚔️

```
D-015 不挪用备用金：风险预算就是上限，不加钱
  → 亏完今天的预算 → 今天停止
  → 亏完本周的预算 → 本周停止

D-016 不借贷交易：永远用自有资金
  → 杠杆是工具，不是借钱的理由

D-017 不提盈利消费：30%收益提取到安全账户，70%继续复利
  → 提取规则：月收益 > 10%时执行
```

## 五、复盘纪律 ⚔️

```
D-018 每笔交易都要复盘：没有复盘的交易 = 没做过的交易
  → 胜了：为什么赢（能力/运气各占多少）
  → 败了：为什么输（哪一步做错了）

D-019 每日必须做复盘：当日不复盘 → 次日不交易
  → 复盘时间：收盘后30分钟内必须完成

D-020 不找借口：亏损只归因于自己
  → 市场永远是对的
  → "庄家/运气/消息/别人" 都不是失败的原因
  → 只有"我判断错了/执行错了"才是真正原因
```

---

<!-- ======================================================================= -->
<!--                   第四部分：旧烛龙心理篇精华提取                       -->
<!-- ======================================================================= -->

# 第四部分：旧烛龙心理篇精华提取

> 以下内容来自旧烛龙在熊猫交易学社课程中的心理篇、系统篇吸收整理

## 一、交易心理四大关卡

### 关卡1：恐惧（Fear）
**表现**：
- 信号来了不敢入场
- 持仓中一点波动就坐立不安
- 提前止盈怕亏回去

**对策**：
- 没有系统的恐惧是噪音，有系统的恐惧是保护
- 按系统信号执行 — 系统不关你的事
- 用"最小仓位测试"来降低心理负担

### 关卡2：贪婪（Greed）
**表现**：
- 盈利后想"多赚一点"
- 追涨、重仓
- 不舍得止盈

**对策**：
- 贪婪不是一个错误，它是让你追求更高收益的动力
- 问题在于贪婪让你失去纪律
- 解决：用规则限制贪婪（最高仓位限制、止盈规则、加仓规则）

### 关卡3：希望（Hope）
**表现**：
- 亏损时希望"能涨回来的"
- 止损前希望"再等一下"
- "明天应该会好转"

**对策**：
- 希望是最危险的交易情绪
- 希望不等于分析 — 用数据替代希望
- 当你在"希望"时 — 马上减仓

### 关卡4：悔恨（Regret）
**表现**：
- "早知道就不卖了"
- "早知道就重仓了"
- 后见之明让自己陷入懊悔

**对策**：
- 后见之明是交易者最大的敌人
- 按照当时的决策条件复盘，而不是"现在看回去"
- 学会放下：每一笔交易都是独立的

## 二、赚钱后的自我膨胀

**旧烛龙提炼**：赚钱后最危险的阶段

```
赚钱后的心理变化路径：
  盈利 → 自信心上升 → 风险判断力下降 → 仓位加大 → 市场变化 → 大亏

检测信号：
  □ 开始看不上小的信号
  □ 觉得"这次和以往不一样"
  □ 仓位不自觉变大了
  □ 止损设置越来越松了
  □ 不愿意做盘前/盘后分析了

应对：
  □ 最大盈利日之后减仓30%
  □ 5连胜后强制暂停12h
  □ 每月"从零开始"审视自己的仓位和策略
```

## 三、亏钱后的报复交易

**旧烛龙提炼**：亏损后最致命的操作 

```
报复交易的特征：
  □ 亏损后马上找下一个机会"回本"
  □ 仓位比平时大（想一笔赚回来）
  □ 止损设得比平时宽（怕被震出来）
  □ 入场理由不充分（"总该轮到我赚了吧"）

应对：
  □ 亏损 → 立刻关电脑离开屏幕15分钟
  □ 任何亏损后——最小仓位交易2笔
  □ 连续3笔亏损 → 强制停24h
  □ 连续5笔亏损 → 检查策略是否失效
  □ 不要认为"市场欠你钱"——市场不欠任何人
```

## 四、交易系统的"反人性"设计原则

旧烛龙从熊猫系统中提炼的核心原则：

```
原则1：系统的核心不是"让盈利最大化"
  而是"让人犯的错误最小化"

原则2：止损不应该需要勇气
  应该由系统自动执行，根本不需要"勇气"

原则3：好系统让你在"该赚"的时候在场
  在"该亏"的时候亏得比市场少

原则4：纪律不是"坚持信号"
  纪律是"信号没来的时候什么都不做"

原则5：交易系统的终极目标不是战胜市场
  是战胜自己
```

