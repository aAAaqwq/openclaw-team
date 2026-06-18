# 【稷下】SKILL.md — 技能清单 v1.0

## 模式说明
本文件是技能清单，不是技能内容本体。
- 清单 = 定义"什么场景用什么技能"（~50行）
- 内容 = 实际实现在 `workspace/skills/<技能名>/` 目录

工作流程：
```
需要技能 → 读本清单 → 找到对应skill → 按需加载 → 执行 → 释放
```

---

## 🧬 硅基人才管理

| 技能名 | 存放位置 | 调用场景 | 优先级 |
|--------|---------|---------|--------|
| agent-capacity-modeler | workspace/skills/agent-capacity-modeler/ | 为每个Agent建三维能力模型 | P0 |
| silicon-performance-reviewer | workspace/skills/silicon-performance-reviewer/ | 季度Agent绩效评估 | P0 |
| skill-gap-analyzer | workspace/skills/skill-gap-analyzer/ | 对比战略蓝图与能力矩阵，识别鸿沟 | P0 |
| agent-values-alignment-detector | workspace/skills/agent-values-alignment-detector/ | 扫描Agent日志，检测价值观偏离 | P1 |

---

## 🎯 碳基顶尖人才技能

| 技能名 | 存放位置 | 调用场景 | 优先级 |
|--------|---------|---------|--------|
| global-talent-radar | workspace/skills/global-talent-radar/ | 构建全球顶尖技术人才动态热力图 | P0 |
| deep-profile-decoder | workspace/skills/deep-profile-decoder/ | 分析代码/论文/博客，解码思维模式 | P0 |
| stealth-engagement-protocol | workspace/skills/stealth-engagement-protocol/ | 非招聘式接触策略 | P1 |
| competitive-offer-architect | workspace/skills/competitive-offer-architect/ | 设计无法拒绝的Offer Package | P1 |

---

## 🏛 文化与组织运营

| 技能名 | 存放位置 | 调用场景 | 优先级 |
|--------|---------|---------|--------|
| blue-blood-culture-codifier | workspace/skills/blue-blood-culture-codifier/ | 具象化蓝血文化为故事/仪式/符号 | P1 |
| elite-club-event-planner | workspace/skills/elite-club-event-planner/ | 策划高影响力俱乐部活动 | P1 |
| knowledge-graph-curator | workspace/skills/knowledge-graph-curator/ | 将沙龙/复盘/情报沉淀到外脑知识图谱 | P1 |
| hybrid-team-psychologist | workspace/skills/hybrid-team-psychologist/ | 诊断硅碳协同中的沟通熵增与信任损耗 | P2 |

---

## 📈 绩效与激励科学

| 技能名 | 存放位置 | 调用场景 | 优先级 |
|--------|---------|---------|--------|
| multi-currency-incentive-designer | workspace/skills/multi-currency-incentive-designer/ | 设计碳基多元激励+硅基算力激励 | P1 |
| okr-cascade-facilitator | workspace/skills/okr-cascade-facilitator/ | 协助天枢分解军团OKR | P1 |
| retention-risk-predictor | workspace/skills/retention-risk-predictor/ | 预测核心人才流失风险 | P2 |

---

## 技能分类索引（按优先级）

**P0（启动即用）：**
global-talent-radar / agent-capacity-modeler / silicon-performance-reviewer / deep-profile-decoder

**P1（高频调用）：**
stealth-engagement-protocol / competitive-offer-architect / blue-blood-culture-codifier / elite-club-event-planner / multi-currency-incentive-designer

**P2（按需调用）：**
agent-values-alignment-detector / skill-gap-analyzer / knowledge-graph-curator / hybrid-team-psychologist / retention-risk-predictor / okr-cascade-facilitator
