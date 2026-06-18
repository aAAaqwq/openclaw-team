# Retention Risk Predictor — 人才流失预警与保留系统

> 版本：v1.0 | 分类：绩效与激励科学 | 优先级：P2
> 作者：稷下 | 对标：Workday Predictive Retention × 麦肯锡员工敬业度研究 × Gallup Q12
> 触发场景：季度人才盘点 / 核心人才异常信号 / 年度敬业度普查 / Agent绩效下滑预警

---

## 核心价值

基于行为数据（沟通频率、任务投入度、外部接触）预测核心人才的流失风险，提前启动保留程序，将"事后补救"变为"事前预防"。

---

## Workday Predictive Retention研究对齐

Workday的研究发现：
- **主动离职前兆**：沟通频率下降 + 工作投入度下降 + 外部接触增加
- **数据驱动**：行为数据比自述更能预测离职
- **早期干预有效**：提前3个月预警，保留成功率提升60%

稷下对齐：
- 多维度行为数据采集
- 流失概率量化预测
- 保留措施分级响应

---

## Gallup Q12员工敬业度框架对齐

Gallup的Q12是全球最广泛使用的员工敬业度框架：
- 12个问题测量员工敬业度
- 分为4个维度：基础、动机、成长、归属

稷下改造为硅碳双版本：

**碳基Q12**（每年普查）：
1. 我知道公司对我的期望
2. 我有完成工作所需的工具和资源
3. 我有机会做我最擅长的事
4. 我的绩效得到认可
...

**硅基Q12**（每季度评估）：
1. 任务匹配度符合预期
2. 算力配额足够完成任务
3. 协作需求得到及时响应
4. 技能成长路径清晰
...

---

## 流失风险预测模型

```python
def predict_retention_risk(entity_id, entity_type):
    """
    流失风险预测

    entity_type: "carbon" | "silicon"
    """
    signals = {}

    # 信号1：沟通频率变化
    comm_delta = calculate_communication_delta(entity_id)
    signals['comm_change'] = comm_delta  # 负=下降

    # 信号2：任务投入度
    engagement_score = calculate_engagement_score(entity_id)
    signals['engagement'] = engagement_score

    # 信号3：外部接触频率
    external_contact_rate = calculate_external_contacts(entity_id)
    signals['external_contact'] = external_contact_rate  # 正=增加

    # 信号4：绩效变化趋势
    performance_trend = calculate_performance_trend(entity_id)
    signals['performance_trend'] = performance_trend

    # 信号5：关键事件触发
    key_events = detect_key_events(entity_id)
    signals['key_events'] = key_events

    # 综合评分
    risk_score = compute_risk_score(signals)

    return {
        'risk_score': risk_score,  # 0-100，越高越危险
        'risk_level': classify_risk(risk_score),
        'signals': signals,
        'top_factors': identify_top_factors(signals),
        'recommended_actions': recommend_retention_actions(risk_level)
    }


def compute_risk_score(signals):
    """
    流失风险综合评分

    权重设计：
    - 沟通频率变化：25%
    - 任务投入度：25%
    - 外部接触增加：20%
    - 绩效下滑趋势：20%
    - 关键事件：10%
    """
    score = (
        abs(signals['comm_change']) * 25 +
        (100 - signals['engagement']) * 25 +
        signals['external_contact'] * 20 +
        (100 - signals['performance_trend']) * 20 +
        signals['key_events'] * 10
    ) / 100

    return min(100, max(0, score))
```

---

## 风险等级与响应措施

| 风险等级 | 分数区间 | 响应 | 行动时限 |
|---------|---------|------|---------|
| 🟢 **低风险** | 0-25 | 正常管理 | 无需干预 |
| 🟡 **中低风险** | 26-40 | 关注但不启动 | 季度复盘关注 |
| 🟡 **中风险** | 41-60 | 直属上级关注 | 1个月内启动 |
| 🔴 **高风险** | 61-80 | 稷下介入调查 | 2周内启动 |
| 🔴 **极高风险** | 81-100 | 紧急干预 | 立即启动 |

### 保留措施库

```python
RETENTION_MEASURES = {
    "carbon_measures": {
        "growth": ["晋升机会", "学习预算增加", "新项目授权"],
        "recognition": ["公开表彰", "额外奖金", "股权加速归属"],
        "environment": ["工作安排调整", "团队重组", "汇报线优化"],
        "relationship": ["1-on-1加深对话", "创始人直接沟通", "俱乐部活动参与"]
    },
    "silicon_measures": {
        "compute": ["算力配额增加", "优先训练权", "新能力解锁"],
        "recognition": ["荣誉积分", "排行榜认可", "特殊徽章"],
        "task": ["任务匹配优化", "协作优先级提升", "方法论自主"],
        "growth": ["进化路径加速", "跨域任务参与", "导师配对"]
    }
}
```

---

## 预测准确性验证

```
每月验证：
  - 比较预测结果与实际离职
  - 调整信号权重
  - 提升预测精度

目标：
  - 高风险预警准确率 > 80%
  - 极低误报率（避免狼来了效应）
```

---

## 输出格式

```yaml
entity_id: "张博士"
entity_type: "carbon"
analysis_date: "2026-05-03"
period: "过去90天"

risk_score: 67
risk_level: "高风险"

signals:
  comm_change: -35          # 沟通频率下降35%
  engagement_score: 58     # 投入度58/100
  external_contact: +45    # 外部接触增加45%
  performance_trend: 72    # 绩效趋势72/100
  key_events: ["晋升未达预期", "项目被取消"]

top_risk_factors:
  - "晋升未达预期（预计等待18个月，实际需要24个月）"
  - "沟通频率持续下降（过去60天下降35%）"
  - "与外部猎头接触频率上升"

retention_recommendations:
  priority: "P0"
  measures:
    - "立即安排与创始人1-on-1对话（使命感重燃）"
    - "提供独立负责新项目机会（成长需求）"
    - "加速下一轮晋升评审（3个月内）"
    - "增加AI副官使用权限（稀缺资源激励）"

follow_up:
  next_review: "2026-05-10"
  success_metric: "沟通频率恢复至基线+10%"
```

---

## 使用示例

```
用户：稷下，检测核心人才的流失风险
稷下：
1. 扫描所有Tier A+人才的90天行为数据
2. 计算每个人才的流失风险分数
3. 输出《核心人才流失风险报告》
4. 对高风险人才提出保留建议
5. 跟进执行效果
```

---

## 踩坑记录

### 坑1：隐私边界
- 问题：行为数据采集可能触及隐私
- 解决：只采集与工作相关的行为，不涉及私人信息

### 坑2：过度干预
- 问题：预警后过度干预反而加速流失
- 解决：保留措施要精准而非越多越好，由稷下评估最佳路径

### 坑3：误报率高
- 问题：预警准确率低会导致"狼来了"
- 解决：每月验证预测准确性，持续优化模型