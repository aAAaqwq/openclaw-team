# Skills Index — 蓝血军团技能全局索引

> **版本**：v1.2
> **更新日期**：2026-05-01
> **总技能数**：125（天工28 + 轩辕28 + 鲲鹏25 + 烛龙30 + 稷下14）
> **索引维护者：河图（CKO）**

---

## 技能分类导航

| 分类 | 技能数 | 涵盖 |
|------|--------|------|
| [产品策略](#1-产品策略-product-strategy) | 9 | 假设定义、PRD、竞品分析、JTBD、机会树等 |
| [用户研究](#2-用户研究-user-research) | 4 | 用户访谈、访谈综合、人物画像、JTBD分析 |
| [数据驱动](#3-数据驱动-data-driven) | 7 | 实验设计、验收标准、用户故事、优先级排序 |
| [商业化](#4-商业化) | 9 | PMF、PLG、精益画布、产品定位、路线图等 |
| [工程技术](#5-工程技术-engineering) | 12 | 全栈开发、云原生、API设计、数据库、容器化等 |
| [AI基础设施](#6-ai基础设施-ai-infrastructure) | 5 | 大模型训练、推理优化、RAG、Agent框架等 |
| [方法论](#7-方法论-methodology) | 6 | DDD、TDD、安全审计、CI/CD、可观测性、悬赏包 |
| [自动化工具链](#8-自动化工具链-tools) | 5 | 编码Agent、PR审查、测试自动化等 |
| [GEO & SEO](#9-geo--seo) | 6 | GEO优化、关键词研究、实体优化、Schema标记 |
| [增长引擎](#10-增长引擎) | 6 | 飞轮架构、病毒循环、PLG、线索自动化、转化优化 |
| [情报监听](#11-情报监听) | 4 | 社交情绪、竞品熵值、全球市场拓扑、热点扫描 |
| [增长悬赏](#12-增长悬赏) | 2 | 悬赏包生成、伙伴验证 |

---

## 1. 产品策略 (Product Strategy)

| # | Skill名 | 文件路径 | 来源 | 适用角色 |
|---|---------|---------|------|----------|
| 1 | hypothesis-definition | `product-strategy/hypothesis-definition.md` | pm-skills | 天工 |
| 2 | prd-writing | `product-strategy/prd-writing.md` | pm-skills | 天工 |
| 3 | competitive-analysis | `product-strategy/competitive-analysis.md` | pm-skills | 天工/鲲鹏 |
| 4 | solution-brief | `product-strategy/solution-brief.md` | pm-skills | 天工 |
| 5 | jtbd-canvas | `product-strategy/jtbd-canvas.md` | pm-skills | 天工 |
| 6 | opportunity-solution-tree | `product-strategy/opportunity-solution-tree.md` | pm-skills | 天工 |
| 7 | adr | `product-strategy/adr.md` | pm-skills | 天工/轩辕 |
| 8 | problem-statement | `product-strategy/problem-statement.md` | pm-skills | 天工 |
| 9 | design-rationale | `product-strategy/design-rationale.md` | pm-skills | 天工 |

## 2. 用户研究 (User Research)

| # | Skill名 | 文件路径 | 来源 | 适用角色 |
|---|---------|---------|------|----------|
| 1 | user-interview | `user-research/user-interview.md` | productskills | 天工/烛龙 |
| 2 | interview-synthesis | `user-research/interview-synthesis.md` | pm-skills | 天工/烛龙 |
| 3 | persona-builder | `user-research/persona-builder.md` | pm-skills | 天工/鲲鹏 |
| 4 | jtbd-analysis | `user-research/jtbd-analysis.md` | productskills | 天工 |

## 3. 数据驱动 (Data-Driven)

| # | Skill名 | 文件路径 | 来源 | 适用角色 |
|---|---------|---------|------|----------|
| 1 | experiment-design | `data-driven/experiment-design.md` | pm-skills | 天工/烛龙 |
| 2 | experiment-results | `data-driven/experiment-results.md` | pm-skills | 天工/烛龙 |
| 3 | acceptance-criteria | `data-driven/acceptance-criteria.md` | pm-skills | 天工/明镜 |
| 4 | user-stories | `data-driven/user-stories.md` | pm-skills | 天工/轩辕 |
| 5 | prioritization-advisor | `data-driven/prioritization-advisor.md` | Product-Manager-Skills | 天工/天枢 |
| 6 | feature-prioritization | `data-driven/feature-prioritization.md` | productskills | 天工 |
| 7 | user-story-writing | `data-driven/user-story-writing.md` | Product-Manager-Skills | 天工/轩辕 |

## 4. 商业化 (商业化)

| # | Skill名 | 文件路径 | 来源 | 适用角色 |
|---|---------|---------|------|----------|
| 1 | pmf-survey | `commercialization/pmf-survey.md` | product-skills | 天工/烛龙 |
| 2 | product-led-growth | `commercialization/product-led-growth.md` | product-skills | 天工/鲲鹏 |
| 3 | working-backwards | `commercialization/working-backwards.md` | product-skills | 天工 |
| 4 | lean-canvas | `commercialization/lean-canvas.md` | pm-skills | 天工/司库 |
| 5 | product-positioning | `commercialization/product-positioning.md` | productskills | 天工/鲲鹏 |
| 6 | roadmpa-planning | `commercialization/roadmap-planning.md` | productskills | 天工/天枢 |
| 7 | launch-checklist | `commercialization/launch-checklist.md` | pm-skills | 天工/明镜 |
| 8 | scope-cutting | `commercialization/scope-cutting.md` | productskills | 天工 |
| 9 | bet-sizing | `commercialization/bet-sizing.md` | productskills | 天工/司库 |

---

## 如何新增Skill

1. 将skill文件放入 `workspace/skills/<角色名>/<分类>/` 下
2. 更新此索引文件，加入新条目
3. 更新角色的 SKILL.md（引用关系）
4. 通知河图（CKO）做全局同步

---

## 5. 工程技术 (Engineering)

| # | Skill名 | 文件路径 | 来源 | 适用角色 |
|---|---------|---------|------|----------|
| 1 | fullstack-master | `engineering/fullstack-master.md` | open-claw整合 | 轩辕 |
| 2 | cloud-native-ops | `engineering/cloud-native-ops.md` | 本体内置 | 轩辕 |
| 3 | api-design | `engineering/api-design.md` | 本体内置 | 轩辕/天工 |
| 4 | database-master | `engineering/database-master.md` | 本体内置 | 轩辕 |
| 5 | docker-essentials | `infrastructure/docker-essentials.md` | open-claw整合 | 轩辕 |
| 6 | cicd-pipeline | `infrastructure/cicd-pipeline.md` | open-claw整合 | 轩辕 |
| 7 | security-sentinel | `infrastructure/security-sentinel.md` | 本体内置 | 轩辕/明镜 |
| 8 | monitoring-observability | `infrastructure/monitoring-observability.md` | 本体内置 | 轩辕 |
| 9 | coding-agent | 系统内置 | OpenClaw官方 | 轩辕（系统级） |
| 10 | github | 系统内置 | OpenClaw官方 | 轩辕/全体 |
| 11 | distributed-systems | `architecture/distributed-systems.md` | 本体内置 | 轩辕 |
| 12 | rag-expert | `ai-infra/rag-expert.md` | 本体内置 | 轩辕 |

## 6. AI基础设施 (AI Infrastructure)

| # | Skill名 | 文件路径 | 适用角色 |
|---|---------|---------|----------|
| 1 | llm-training-optimization | `ai-infra/llm-training-optimization.md` | 轩辕 |
| 2 | inference-optimization | `ai-infra/inference-optimization.md` | 轩辕 |
| 3 | model-quantization | `ai-infra/model-quantization.md` | 轩辕 |
| 4 | rag-system-design | `ai-infra/rag-system-design.md` | 轩辕 |
| 5 | agent-framework | `ai-infra/agent-framework.md` | 轩辕/全体 |

## 7. 方法论 (Methodology)

| # | Skill名 | 文件路径 | 适用角色 |
|---|---------|---------|----------|
| 1 | ddd-practitioner | `methodology/ddd-practitioner.md` | 轩辕/天工 |
| 2 | beer-code | `methodology/beer-code.md` | 轩辕 |
| 3 | test-driven-dev | `methodology/test-driven-dev.md` | 轩辕 |
| 4 | code-reviewer | `methodology/code-reviewer.md` | 轩辕/明镜 |
| 5 | technical-debt-manager | `methodology/technical-debt-manager.md` | 轩辕 |
| 6 | bounty-spec-writer | `methodology/bounty-spec-writer.md` | 轩辕 |

## 8. 自动化工具链 (Tools)

| # | Skill名 | 文件路径 | 适用角色 |
|---|---------|---------|----------|
| 1 | coding-agent | 系统内置 | 轩辕 |
| 2 | pr-reviewer | `tools/pr-reviewer.md` | 轩辕 |
| 3 | web-scraper | `tools/web-scraper.md` | 轩辕 |
| 4 | technical-blog-writing | `tools/technical-blog-writing.md` | 轩辕/凤凰 |
| 5 | test-automation | `tools/test-automation.md` | 轩辕 |

## 9. GEO & SEO

| # | Skill名 | 文件路径 | 适用角色 |
|---|---------|---------|----------|
| 1 | geo-optimization-pro | `geo/geo-optimization-pro.md` | 鲲鹏 |
| 2 | keyword-research | `growth/keyword-research.md` | 鲲鹏/全体 |
| 3 | geo-content-optimizer | `growth/geo-content-optimizer.md` | 鲲鹏/凤凰 |
| 4 | entity-optimizer | `geo/entity-optimizer.md` | 鲲鹏 |
| 5 | schema-markup-generator | `geo/schema-markup-generator.md` | 鲲鹏/轩辕 |
| 6 | seo-content-writer | `growth/seo-content-writer.md` | 鲲鹏/凤凰 |

## 10. 增长引擎

| # | Skill名 | 文件路径 | 适用角色 |
|---|---------|---------|----------|
| 1 | growth-flywheel-architect | `growth/growth-flywheel-architect.md` | 鲲鹏 |
| 2 | product-led-growth | `commercialization/product-led-growth.md` | 鲲鹏/天工 |
| 3 | viral-loop-designer | `growth/viral-loop-designer.md` | 鲲鹏 |
| 4 | lead-gen-automation | `automation/lead-gen-automation.md` | 鲲鹏 |
| 5 | a-b-testing-auto | `automation/a-b-testing-auto.md` | 鲲鹏/烛龙 |
| 6 | conversion-rate-optimizer | `automation/conversion-rate-optimizer.md` | 鲲鹏 |
| 7 | growth-marketing | `commercialization/marketing-ideas.md` | 鲲鹏 |
| 8 | pricing-strategy | `commercialization/pricing-strategy-designer.md` | 鲲鹏/天工 |

## 11. 情报监听

| # | Skill名 | 文件路径 | 适用角色 |
|---|---------|---------|----------|
| 1 | social-sentiment-sentinel | `listening/social-sentiment-sentinel.md` | 鲲鹏 |
| 2 | competitor-entropy-analyzer | `listening/competitor-entropy-analyzer.md` | 鲲鹏/烛龙 |
| 3 | global-market-topology | `listening/global-market-topology.md` | 鲲鹏 |
| 4 | hotspot-scanner | `listening/hotspot-scanner.md` | 鲲鹏 |

## 12. 增长悬赏

| # | Skill名 | 文件路径 | 适用角色 |
|---|---------|---------|----------|
| 1 | bounty-growth-pack-gen | `automation/bounty-growth-pack-gen.md` | 鲲鹏 |
| 2 | bounty-partner-verification | `automation/bounty-partner-verification.md` | 鲲鹏 |

---

> 维护者：河图 (CKO) | 最后更新：2026-05-01

---

## 烛龙 (CIO) — 30 skills

### 一、因子与策略引擎 (6 skills) → `skills/quant/` + 社区引用

| # | Skill | 文件路径 | 来源 | 子Agent |
|---|-------|---------|------|---------|
| 1 | factor-mining-cluster | `quant/factor-mining-cluster.md` | 本体内置 | 烛龙 |
| 2 | build-trading-strategies | `workspace/skills/build-trading-strategies/SKILL.md` | 社区skill | 烛龙 |
| 3 | hft-quant-expert | `workspace/skills/hft-quant-expert/SKILL.md` | 社区skill | 烛龙 |
| 4 | generating-trading-signals | `workspace/skills/generating-trading-signals/SKILL.md` | 社区skill | 烛龙 |
| 5 | backtesting-trading-strategies | `workspace/skills/backtesting-trading-strategies/SKILL.md` | 社区skill | 烛龙 |
| 6 | alpha-decay-monitor | `quant/alpha-decay-monitor.md` | 本体内置 | 烛龙 |

### 二、回测与风控 (6 skills) → `skills/risk/` + `skills/quant/` + 社区引用

| # | Skill | 文件路径 | 来源 | 子Agent |
|---|-------|---------|------|---------|
| 1 | stress-test-simulator | `quant/stress-test-simulator.md` | 本体内置 | 烛龙 |
| 2 | dynamic-position-sizing | `quant/dynamic-position-sizing.md` | 本体内置 | 烛龙 |
| 3 | cvar-guardian | `risk/cvar-guardian.md` | 本体内置 | 烛龙 |
| 4 | risk-metrics-calculation | `workspace/skills/risk-metrics-calculation/SKILL.md` | 社区skill | 烛龙 |
| 5 | multi-market-arbitrage | `quant/multi-market-arbitrage.md` | 本体内置 | 烛龙 |
| 6 | strategy-attribution | `quant/strategy-attribution.md` | 本体内置 | 烛龙 |

### 三、极速执行与基建 (4 skills) → 社区引用

| # | Skill | 文件路径 | 来源 | 子Agent |
|---|-------|---------|------|---------|
| 1 | smart-order-router | `quant/smart-order-router.md` | 本体内置 | 烛龙 |
| 2 | ccxt-python | `workspace/skills/ccxt-python/SKILL.md` | 社区skill | 烛龙 |
| 3 | tracking-crypto-prices | `workspace/skills/tracking-crypto-prices/SKILL.md` | 社区skill | 烛龙 |
| 4 | stock-analysis | `workspace/skills/stock-analysis/SKILL.md` | 社区skill | 烛龙 |

### 四、市场情报 (4 skills) → 社区引用

| # | Skill | 文件路径 | 来源 | 子Agent |
|---|-------|---------|------|---------|
| 1 | crypto-report | `workspace/skills/crypto-report/SKILL.md` | 社区skill | 烛龙 |
| 2 | stock-research-executor | `workspace/skills/stock-research-executor/SKILL.md` | 社区skill | 烛龙 |
| 3 | pine-developer | `workspace/skills/pine-developer/SKILL.md` | 社区skill | 烛龙 |
| 4 | pine-optimizer | `workspace/skills/pine-optimizer/SKILL.md` | 社区skill | 烛龙 |

### 五、Alpha因子悬赏 (4 skills) → `skills/quant/` + 社区引用

| # | Skill | 文件路径 | 来源 | 子Agent |
|---|-------|---------|------|---------|
| 1 | quant-bounty-architect | `quant/quant-bounty-architect.md` | 本体内置 | 烛龙/稷下 |
| 2 | trade-prediction-markets | `workspace/skills/trade-prediction-markets/SKILL.md` | 社区skill | 烛龙 |
| 3 | alpha-factor-review | `quant/alpha-factor-review.md` | 本体内置 | 烛龙 |
| 4 | out-of-sample-validator | `quant/out-of-sample-validator.md` | 本体内置 | 烛龙 |

### 六、三战场部署 (6 skills) → `skills/quant/` + 社区引用

| # | Skill | 文件路径 | 来源 | 子Agent |
|---|-------|---------|------|---------|
| 1 | polymarket-signal-hunter | `quant/polymarket-signal-hunter.md` | 自定义内置 | 烛龙 |
| 2 | polymarket-bot | `quant/polymarket-bot.md` | 自定义内置 | 烛龙 |
| 3 | a-share-t0 | `quant/a-share-t0.md` | 本体内置 | 烛龙 |
| 4 | crypto-funding-arb | `quant/crypto-funding-arb.md` | 本体内置 | 烛龙 |
| 5 | pine-backtester | `workspace/skills/pine-backtester/SKILL.md` | 社区skill | 烛龙 |
| 6 | pine-debugger | `workspace/skills/pine-debugger/SKILL.md` | 社区skill | 烛龙 |

---

## 稷下人才与俱乐部技能 (14 skills) → `workspace/skills/`

### 一、硅基人才管理 (4 skills)

| # | Skill | 文件路径 | 来源 | 适用角色 |
|---|-------|---------|------|----------|
| 1 | agent-capacity-modeler | `agent-capacity-modeler/SKILL.md` | 自建 | 稷下/天枢 |
| 2 | silicon-performance-reviewer | `silicon-performance-reviewer/SKILL.md` | 自建 | 稷下/明镜 |
| 3 | skill-gap-analyzer | `skill-gap-analyzer/SKILL.md` | 自建 | 稷下/昆仑 |
| 4 | agent-values-alignment-detector | `agent-values-alignment-detector/SKILL.md` | 自建 | 稷下/明镜 |

### 二、碳基人才猎取 (4 skills)

| # | Skill | 文件路径 | 来源 | 适用角色 |
|---|-------|---------|------|----------|
| 1 | global-talent-radar | `global-talent-radar/SKILL.md` | 自建 | 稷下 |
| 2 | deep-profile-decoder | `deep-profile-decoder/SKILL.md` | 自建 | 稷下 |
| 3 | stealth-engagement-protocol | `stealth-engagement-protocol/SKILL.md` | 自建 | 稷下 |
| 4 | competitive-offer-architect | `competitive-offer-architect/SKILL.md` | 自建 | 稷下/司库 |

### 三、文化与组织运营 (4 skills)

| # | Skill | 文件路径 | 来源 | 适用角色 |
|---|-------|---------|------|----------|
| 1 | blue-blood-culture-codifier | `blue-blood-culture-codifier/SKILL.md` | 自建 | 稷下/昆仑 |
| 2 | elite-club-event-planner | `elite-club-event-planner/SKILL.md` | 自建 | 稷下 |
| 3 | knowledge-graph-curator | `knowledge-graph-curator/SKILL.md` | 自建 | 稷下/河图 |
| 4 | hybrid-team-psychologist | `hybrid-team-psychologist/SKILL.md` | 自建 | 稷下/天枢 |

### 四、绩效与激励科学 (2 skills)

| # | Skill | 文件路径 | 来源 | 适用角色 |
|---|-------|---------|------|----------|
| 1 | multi-currency-incentive-designer | `multi-currency-incentive-designer/SKILL.md` | 自建 | 稷下/司库 |
| 2 | retention-risk-predictor | `retention-risk-predictor/SKILL.md` | 自建 | 稷下/天枢 |
