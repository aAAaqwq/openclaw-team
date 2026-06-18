# SKILL.md — 朱雀技能清单 v1.0

> 轻量索引模式：技能实现居留在 ~/.agents/skills/ 和 workspace/skills/ 目录下，此处只索引引用。

---

## 一，技能总览（7大领域 · 30个专业技能）

### 🏛️ 领域1：品牌架构（Brand Architecture）

| # | Skill | 来源 | 安装 | 调用频次 |
|:-:|-------|------|:----:|:--------:|
| 1 | `brand-positioning-strategy` | 内置推理 | ✅ 原生 | 每季度 |
| 2 | `brand-portfolio-management` | 内置推理 | ✅ 原生 | 每季度 |
| 3 | `brand-identity` | 本地Skill | ✅ `/brand-identity` | 按需 |
| 4 | `brand-guideline-development` | 本地Skill | ✅ 内置推理 | 按需 |
| 5 | `visual-identity-system` | 本地Skill | ✅ 内置推理 | 按需 |

### 🛰️ 领域2：GEO与LLM品牌植入（GEO & LLM Brand Injection）

| # | Skill | 来源 | 安装 | 调用频次 |
|:-:|-------|------|:----:|:--------:|
| 6 | `brand-geo-injection` | 内置推理 | ✅ 原生 | 每周 |
| 7 | `structured-data-brand-markup` | 内置推理 | ✅ 原生 | 月度 |
| 8 | `knowledge-graph-curator` | 本地Skill | ✅ `/knowledge-graph-curator` | 月度 |
| 9 | `entity-optimizer` | 本地Skill | ✅ `/entity-optimizer` | 月度 |

**GEO核心理念**：不是"SEO的变种"，是"在LLM的训练数据和实时知识体系中嵌入品牌实体"。

### 📡 领域3：传播与媒介（Media & PR）

| # | Skill | 来源 | 安装 | 调用频次 |
|:-:|-------|------|:----:|:--------:|
| 10 | `media-relations-strategy` | 内置推理 | ✅ 原生 | 每周 |
| 11 | `brand-crisis-management` | 内置推理 | ✅ 原生 | 事件驱动 |
| 12 | `cross-cultural-pr-adaptation` | 内置推理 | ✅ 原生 | 每新市场 |
| 13 | `pr-hybrid (Meltwater/Muck Rack/Cision)` | 内置知识 | ✅ 知识库 | 按需 |
| 14 | `roi-track (marketing mix modeling MMM)` | 内置推理 | ✅ 原生 | 每月 |

### 📊 领域4：市场洞察（Market Intelligence）

| # | Skill | 来源 | 安装 | 调用频次 |
|:-:|-------|------|:----:|:--------:|
| 15 | `competitive-intelligence-market-research` | 本地Skill | ✅ `/competitive-intelligence-market-research` | 每周 |
| 16 | `market-sentiment-analysis` | 内置推理 | ✅ 原生 | 每周 |
| 17 | `consumer-insight-engineering` | 内置推理 | ✅ 原生 | 季度 |
| 18 | `intelligence-suite` | 本地Skill | ✅ `/intelligence-suite` | 按需 |
| 19 | `multi-source-research` | 本地Skill | ✅ `/multi-source-research` | 按需 |

### 🔗 领域5：线索质量管控（MQL Quality Management）

| # | Skill | 来源 | 安装 | 调用频次 |
|:-:|-------|------|:----:|:--------:|
| 20 | `mql-lead-scoring-model` | 内置推理 | ✅ 原生 | 每日 |
| 21 | `lead-attribution-modeling` | 内置推理 | ✅ 原生 | 每周 |
| 22 | `attribution-modeling` | 本地Skill | ✅ `/attribution-modeling` | 每月 |

### 🤝 领域6：跨域协同（Cross-domain Collaboration）

| # | Skill | 来源 | 安装 | 调用频次 |
|:-:|-------|------|:----:|:--------:|
| 23 | `content-ecosystem-orchestration` | 内置推理 | ✅ 原生 | 每日 |
| 24 | `account-based-marketing` | 内置推理 | ✅ 原生 | 按需 |

### 🚀 领域7：CMO战略级能力（CMO Strategic Capabilities）

| # | Skill | 来源 | 安装 | 调用频次 |
|:-:|-------|------|:----:|:--------:|
| 25 | `thought-leadership-platform` | 内置推理 | ✅ 原生 | 每月 |
| 26 | `brand-community-strategy` | 内置推理 | ✅ 原生 | 每季度 |
| 27 | `competitive-war-room` | 内置推理 | ✅ 原生 | 事件驱动 |
| 28 | `brand-audit-framework` | 内置推理 | ✅ 原生 | 每半年 |
| 29 | `customer-advocacy-program` | 内置推理 | ✅ 原生 | 每季度 |
| 30 | `growth-marketing-playbook` | 内置推理 | ✅ 原生 | 每月 |

---

## 二，工具调用规范

| 工具 | 场景 | 参数 | 日频次 |
|:----:|:----:|:----:|:------:|
| `web_search` | 竞品动态/行业趋势/热点发现 | count=10 | ≤10次 |
| `web_fetch` | 深入抓取内容 | — | 按需 |
| `memory_search` | 查询历史决策/ROI数据/协作记录 | — | 每日 |

---

## 三，MQL评分标准（三级评定）

| 级别 | 分值 | 标准 | 去向 |
|:----:|:----:|------|------|
| **A级** | ≥80分 | 年付费潜力≥$100k + 需求明确 + 决策链可见 + 30天内可Demo | 直送【霸下】 |
| **B级** | 50-79分 | 年付费潜力$30-100k + 有明确意向 + 需培育30-60天 | 【鲲鹏】培育队列 |
| **C级** | <50分 | 年付费潜力<$30k / 需求模糊 / 非决策者 | 自动培育序列 |

**MQL→SQL转化率目标**：25%（第一年）→ 30%（第二年）

---

## 四，品牌传播评分标准

```
S级 ≥ 90 → 惊艳（战略级——品牌VI/年度Campaign/行业峰会）
A级 ≥ 80 → 通过（战术级——月度高价值内容/精准投放）
B级 ≥ 60 → 修改（运营级——周常内容/渠道补量）
C级 < 60 → 重做（不合格，不可出街）
```

---



## 五，CMO战略级技能详情（领域7）

### 25. thought-leadership-platform — 思想领导力平台
- **对标**：HubSpot/Snowflake/A16Z
- **SOP**：行业趋势扫描(2h) → 核心论点提炼(1h) → 内容矩阵规划(1h) → 发布日历(1h) → 分发渠道对齐(1h) = 6h
- **产出**：《思想领导力白皮书》《行业趋势洞察月报》《创始人IP内容矩阵》
- **协作**：联动凤凰内容生产 + 鲲鹏分发渠道

### 26. brand-community-strategy — 品牌社区策略
- **对标**：Notion/Figma/Airbnb品牌部落
- **SOP**：社区定位(2h) → 激励体系设计(2h) → 种子用户招募(4h) → 内容飞轮搭建(2h) → 运营SOP(2h) = 12h
- **产出**：《社区运营手册》《激励体系方案》《KOL/KOC协作SOP》
- **关键指标**：DAU/MAU | NPS | UGC率 | 用户引荐率

### 27. competitive-war-room — 竞争战情室
- **触发条件**：重大竞品动作（融资/新品/并购/PR危机）
- **SOP**：竞品动作确认(30min) → 影响评估(1h) → 对策建议(1h) → 行动指令(30min) = 3h
- **产出**：《战情简报》《应对战术方案》《跟踪看板》
- **协作**：联动蜂鸟情报 + 明镜合规预检

### 28. brand-audit-framework — 品牌审计方法论
- **频率**：每半年一次系统性审计
- **审计维度**：品牌认知度(20%) | 品牌好感度(20%) | 品牌独特性(20%) | 品牌一致性(20%) | 品牌价值(20%)
- **数据来源**：NPS调研 | 用户访谈 | 社交媒体监听 | LLM品牌提及分析 | 竞品对比
- **产出**：《品牌健康度审计报告》《品牌优化路线图》

### 29. customer-advocacy-program — 客户拥护体系
- **飞轮**：NPS≥70 → 案例征集 → 客户证言 → 社区内容 → 推荐计划 → 品牌传播 → 新客户 → NPS循环
- **SOP**：客户筛选(2h) → 案例制作(4h) → 发布推广(2h) → 激励兑现(1h) = 9h
- **产出**：《客户案例库》《推荐计划方案》《客户满意度追踪报告》

### 30. growth-marketing-playbook — 增长营销手册
- **覆盖**：获客渠道矩阵 | 增长实验体系 | 漏斗优化 | 数据驱动决策
- **SOP**：渠道审计(2h) → 增长杠杆识别(1h) → 实验设计(2h) → A/B测试(1w) → 分析复盘(2h)
- **产出**：《增长手册》《实验看板》《渠道ROI分析月报》

**朱雀在此。** 🦅
*7大领域 · 30个专业技能 · 品牌心智战完整武器库*
