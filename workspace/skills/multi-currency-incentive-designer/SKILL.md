# Multi-Currency Incentive Designer — 多元激励设计引擎

> 版本：v1.0 | 分类：绩效与激励科学 | 优先级：P2
> 作者：稷下 × 司库联合 | 对标：华为获取分享 × 字节激励 × Netflix薪酬哲学 × 游戏化激励理论
> 触发场景：新员工入职激励设计 / 季度绩效激励 / Agent算力激励 / 俱乐部会员激励

---

## 核心价值

为碳基设计"货币、期权、影响力、认知提升"的多元激励组合；为硅基设计"算力奖励、数据权限、技能升级、任务自主权"的激励回路。让激励真正成为驱动行为的引擎，而非形式主义。

---

## 华为"获取分享"激励逻辑

华为的核心激励哲学：
- **获取分享**：贡献越大，回报越多
- **差异化**：拉开差距，激励顶尖
- **长期绑定**：期权+归属，确保稳定

稷下对齐：
- 碳基：薪酬+期权+非物质激励三层
- 硅基：算力配额+技能升级+荣誉积分三层

---

## 碳基多元激励模型

### 四维激励框架

```python
CARBON_INCENTIVES = {
    "货币层": {
        "base_salary": "市场竞争力保障",
        "performance_bonus": "季度/年度绩效奖金",
        "project_bonus": "项目里程碑奖金",
        "referral_bonus": "人才推荐奖金"
    },
    "股权层": {
        "stock_options": "期权（4年归属）",
        "rsu": "限制性股票单位",
        "profit_sharing": "利润分享计划"
    },
    "影响力层": {
        "club_equity": "俱乐部理事席位",
        "decision_voice": "战略决策参与权",
        "mentorship": "指导他人的权力"
    },
    "成长层": {
        "learning_budget": "年度学习预算",
        "ai_companion": "专属AI副官使用权限",
        "project_autonomy": "独立项目负责权"
    }
}
```

### 字节跳动激励对齐

字节的激励特点：
- **高base**：竞争激烈的薪酬base
- **大锅饭+小灶**：基础福利均等，核心人才特殊激励
- **快速晋升**：绩效好则晋升快，晋升带来薪酬大幅提升

稷下改造为蓝血版本：
- Tier S人才：超高base + 大量期权 + 俱乐部终身席位
- Tier A人才：P75 base + 正常期权 + 学习预算
- Tier B人才：市场基准base + 正常福利

---

## 硅基多元激励模型

### 三维激励框架

```python
SILICON_INCENTIVES = {
    "算力奖励": {
        "compute_budget": "基础算力配额",
        "priority_compute": "优先算力使用权",
        "burst_compute": "高峰算力借用权"
    },
    "技能升级": {
        "model_upgrade": "模型版本升级机会",
        "training_budget": "专项训练算力",
        "capability_unlock": "新能力解锁优先权"
    },
    "自主权": {
        "task_choice": "任务选择优先级",
        "schedule_flexibility": "执行时间弹性",
        "method_autonomy": "方法论自主权"
    }
}
```

### 游戏化激励（Gamification）

借鉴游戏化理论（Yu-kai Chou的Octalysis框架）：
- **成就系统**：完成任务获得"成就徽章"
- **排行榜**：绩效排名公开（自愿参与）
- **里程碑庆祝**：重大交付时的仪式感
- **技能树可视化**：看到自己的成长路径

---

## 激励方案设计流程

```python
def design_incentive_plan(candidate_type, tier, contribution_scope):
    """
    激励方案设计入口

    candidate_type: "carbon" | "silicon"
    tier: "S" | "A" | "B" | "C"
    contribution_scope: "strategic" | "tactical" | "operational"
    """
    if candidate_type == "carbon":
        return design_carbon_incentives(tier, contribution_scope)
    else:
        return design_silicon_incentives(tier, contribution_scope)
```

### 碳基激励设计流程

```
Step 1：候选人画像
├── deep-profile-decoder结果
├── 市场竞争分析
├── 职业阶段（早期/中期/晚期）
└── 激励敏感度分析（钱/成长/使命/自主）

Step 2：激励组合设计（与司库联合）
├── 基础层：市场竞争力base
├── 中间层：绩效奖金设计
├── 顶层：长期绑定（期权）+ 非物质激励

Step 3：差异化亮点
├── 蓝血独有的激励项（AI副官/俱乐部席位/独立项目）
└── 使命驱动的价值叙述

Step 4：沟通与谈判
├── 用competitive-offer-architect包装
└── 稷下主导沟通，司库提供数据支持
```

### 硅基激励设计流程

```
Step 1：Agent绩效评估
├── silicon-performance-reviewer结果
├── agent-capacity-modeler画像
└── 当前算力配额

Step 2：激励计算
├── 绩效等级 → 算力配额调整
├── 创新贡献 → 优先算力奖励
└── 价值观对齐 → 特殊能力解锁

Step 3：通知与执行
├── 稷下通知Agent激励结果
└── 司库执行算力配额调整
```

---

## 输出格式

```yaml
candidate_type: "carbon"
candidate: "张博士"
tier: "S"

incentive_package:
  物质层:
    base: "¥250万/年"
    signing: "¥80万"
    annual_bonus_ceiling: "6个月"
    equity: "0.5% 4年归属"

  非物质层:
    ai_companion: "专属AI副官（价值约¥50万/年）"
    club_equity: "蓝血俱乐部终身理事"
    project_autonomy: "独立负责AI战略方向"

  差异化亮点:
    headline: "与丘总共同定义下一个十年的AI战略"

total_annual_value: "约¥500万（含非物质）"
negotiation_leeway:
  base: "±5%"
  equity: "±0.1%"

communications_strategy:
  approach: "使命驱动，从使命共鸣入手"
  key_message: "这不只是工作，而是定义时代的机会"
```

---

## 踩坑记录

### 坑1：激励同质化
- 问题：所有候选人都给类似的Package
- 解决：必须基于candidate profile定制，每人有差异化

### 坑2：激励与绩效脱钩
- 问题：拿了激励后绩效下降
- 解决：设计"递延支付"机制（部分bonus与未来绩效挂钩）

### 坑3：硅基激励感知弱
- 问题：Agent对算力激励的感知不如碳基对薪酬敏感
- 解决：引入"即时反馈"机制（任务完成后立即显示算力奖励）

---

## 使用示例

```
用户：为新加入的碳基员工设计激励方案
稷下：
1. 获取候选人画像（deep-profile-decoder）
2. 与司库协同计算财务可行性
3. 设计三层激励包
4. 用差异化亮点包装
5. 与候选人沟通（使命驱动叙述）
```