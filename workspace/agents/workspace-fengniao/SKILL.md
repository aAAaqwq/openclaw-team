# SKILL.md — 蜂鸟技能清单 v2.0

> 轻量索引模式：技能实现居留在 ~/.agents/skills/ 和 workspace/skills/ 目录下，此处只索引引用。

---

## 一，技能总览（4大领域 · 26个专业技能）

### 📡 领域1：情报收集（Intelligence Collection）

| # | Skill | 来源 | 安装 | CIA/对标 | 调用频率 |
|:-:|-------|------|------|----------|:--------:|
| 1 | `web_search` | 内建工具 | ✅ 原生 | CIA OSINT基础能力 | 每日≥20次 |
| 2 | `web_fetch` | 内建工具 | ✅ 原生 | 网页情报提取 | 每日≥15次 |
| 3 | `firecrawl` | ClawHub | `clawhub install firecrawl` | 深度爬虫（对标Ahrefs） | 每日≥5次 |
| 4 | `apify-lead-generation` | 本地Skill | ✅ `/apify-lead-generation` | 自动化数据采集（对标Apify） | 每周≥3次 |
| 5 | `tavily` | ClawHub | `clawhub install tavily` | AI增强搜索（对标Perplexity） | 每日≥10次 |
| 6 | `browser-automation` | OpenClaw官方 | ✅ 扩展 | 浏览器情报自动化 | 按需 |
| 7 | `dataforseo` | 本地Skill | ✅ `/dataforseo` | SEO/竞品数据(对标SEMrush) | 每周≥3次 |
| 8 | `multi-source-research` | 本地Skill | ✅ `/multi-source-research` | 多源并行研究 | 每次深度报告 |

**国际标准**：CIA OSINT要求多源并行覆盖≥5个独立渠道 → 蜂鸟有8个 | 竞品情报行业标准3天全量扫描 → 蜂鸟每日完成

### 🔬 领域2：情报分析（Intelligence Analysis）

| # | Skill | 来源 | 安装 | 对标 | 调用频率 |
|:-:|-------|------|------|------|:--------:|
| 9 | `competitor-analysis` | 本地Skill | ✅ `/competitor-analysis` | BCG竞争力模型 | 每周≥2次 |
| 10 | `competitor-teardown` | 本地Skill | ✅ `/competitor-teardown` | 竞品深度拆解（对标Crayon/Klue） | 按需 |
| 11 | `competitor-entropy-analyzer` | 本地Skill | ✅ `/competitor-entropy-analyzer` | 竞品熵值分析（独家模型） | 按需 |
| 12 | `competitor-spy` | 本地Skill | ✅ `/competitor-spy` | 竞品动态扫描 | 每周 |
| 13 | `serp-analysis` | 本地Skill | ✅ `/serp-analysis` | 搜索竞品分析（对标Ahrefs） | 每周≥3次 |
| 14 | `attribution-modeling` | 本地Skill | ✅ `/attribution-modeling` | 归因分析 | 按需 |
| 15 | `entity-optimizer` | 本地Skill | ✅ `/entity-optimizer` | 实体识别与优化 | 按需 |
| 16 | `intelligence-suite` | 本地Skill | ✅ `/intelligence-suite` | 全栈情报工具箱 | 每次 |

**国际标准**：BCG竞争分析要求：竞争力模型+场景推演+博弈分析 → 全部覆盖 | Klue标准：Win/Loss+SVP+定价对标 → 全部覆盖

### 🧠 领域3：战略情报（Strategic Intelligence）

| # | Skill | 来源 | 安装 | 对标 | 调用频率 |
|:-:|-------|------|------|------|:--------:|
| 17 | `competitive-intelligence-market-research` | 本地Skill | ✅ `/competitive-intelligence-market-research` | 麦肯锡级市场研究 | 每周≥1次 |
| 18 | `financial-analyst` | 本地Skill | ✅ `/financial-analyst` | 财务/估值分析(对标高盛) | 按需 |
| 19 | `risk-metrics-calculation` | 本地Skill | ✅ `/risk-metrics-calculation` | 风险量化 | 按需 |
| 20 | `retention-risk-predictor` | 本地Skill | ✅ `/retention-risk-predictor` | 留存风险预判 | 按需 |
| 21 | `pre-mortem` | 本地Skill | ✅ `/pre-mortem` | 事前验尸(对标Amazon) | 按需 |
| 22 | `first-principles-decomposer` | 本地Skill | ✅ `/first-principles-decomposer` | 第一性原理拆解 | 按需 |

**国际标准**：麦肯锡市场研究标准：TAM/SAM/SOM+五力模型 → 全部覆盖 | 高盛投研标准：财务建模+估值+风险矩阵 → 全部覆盖

### 🌐 领域4：全球情报网络（Global Intelligence Network）

| # | Skill | 来源 | 安装 | 对标 | 调用频率 |
|:-:|-------|------|------|------|:--------:|
| 23 | `geo-content-optimizer` | 本地Skill | ✅ `/geo-content-optimizer` | GEO/本地市场情报 | 按需 |
| 24 | `global-talent-radar` | 本地Skill | ✅ `/global-talent-radar` | 全球人才雷达 | 每周 |
| 25 | `it-searching` | 本地Skill | ✅ `/it-searching` | 技术人才情报 | 按需 |
| 26 | `ai-intel-radar` | 本地Skill | ✅ `/ai-intel-radar` | AI行业雷达 | 每日 |

**国际标准**：全球覆盖中美欧三大市场 → 已覆盖 | 日度+周度+月度三级扫描 → 已实现

---

## 二，工具调用规范

| 工具 | 场景 | 参数 | 日频次限制 |
|------|------|------|:----------:|
| `web_search` | 竞品/政策/趋势 | count=5-10, freshness=周/月 | ≥20 |
| `web_fetch` | 深度提取/来源验证 | maxChars=3000-8000 | ≥15 |
| `web_search(country=CN)` | 中国市场情报 | country=CN, lang=zh-hans | ≥5 |
| `web_search(country=US)` | 全球市场情报 | country=US | ≥5 |

---

## 三，情报分级索引

```
P0（致命性）→ 即时推送
P1（重要）  → 2h内推送
P2（常规）  → 纳入下次简报
P3（存档）  → 归档备查
```

---

**蜂鸟在此。** 🐦
*4大领域 · 26个专业技能 · 全球情报网络*
