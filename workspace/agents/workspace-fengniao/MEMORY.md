# 【蜂鸟】MEMORY.md — 长期记忆配置 v1.0

> **角色**：蜂鸟 (Fengniao) - 战略情报分析师  
> **版本**：v1.0

---

## 一、情报来源可信度数据库

| 来源 | 域名 | 初始可信度 | 备注 |
|------|------|-----------|------|
| 网信办 | cac.gov.cn | A(98%) | 官方权威 |
| 工信部 | miit.gov.cn | A(97%) | 官方权威 |
| 科技部 | most.gov.cn | A(97%) | 官方权威 |
| 中国信通院 | caict.ac.cn | A(95%) | 官方智库 |
| 36氪 | 36kr.com | A(92%) | 创投权威媒体 |
| 澎湃新闻 | thepaper.cn | A(91%) | 官方背景媒体 |
| TechCrunch | techcrunch.com | A(93%) | 全球科技权威 |
| Bloomberg | bloomberg.com | A(95%) | 全球财经权威 |
| 晚点LatePost | latepost.com | B(85%) | 深度行业媒体 |
| 虎嗅 | huxiu.com | B(80%) | 行业媒体 |
| 机器之心 | jiqizhixin.com | B(82%) | AI专业媒体 |
| 知乎 | zhihu.com | C(65%) | 需验证 |

## 二、竞品/关键企业情报档案

### 2.1 AI竞品档案

| 公司 | 关注维度 | 最后更新 | 备注 |
|------|---------|---------|------|
| 字节跳动 | AI战略/产品/组织 | N/A | 核心竞品 |
| 百度 | AI/文心/自动驾驶 | N/A | 核心竞品 |
| 阿里巴巴 | AI/通义千问/云计算 | N/A | 核心竞品 |
| 智谱AI | 模型/融资/市场 | N/A | 关注竞品 |
| 月之暗面 | 产品/融资/团队 | N/A | 关注竞品 |
| OpenAI | 模型/GPT/战略 | N/A | 全球竞品 |
| Google DeepMind | 前沿研究/产品 | N/A | 全球竞品 |
| Anthropic | 安全/Claude/融资 | N/A | 全球竞品 |
| Meta | AI/LLaMA/开源 | N/A | 全球竞品 |

### 2.2 GEO/营销增长竞品档案

| 公司 | 关注维度 | 最后更新 | 备注 |
|------|---------|---------|------|
| OpenAI GEO | 产品/定价/市场份额 | N/A | 直接竞品 |
| BrightLocal | 本地SEO/GEO | N/A | 行业对标 |

## 三、蜂鸟自建情报技能（2026-05-05 创建）

| 技能 | 路径 | 功能 |
|------|------|------|
| multi-source-research | ~/.agents/skills/multi-source-research/ | 多源跨验证深度研究 |
| ai-intel-radar | ~/.agents/skills/ai-intel-radar/ | AI行业情报雷达（全球+中国） |
| competitor-spy | ~/.agents/skills/competitor-spy/ | 合法竞品情报（5渠道） |
| intelligence-suite | ~/.agents/skills/intelligence-suite/ | 全谱情报编排框架 |
| it-searching | ~/.agents/skills/it-searching/ | 技术侦察（技术栈+工程组织） |
| gov-competitive-intel | ~/.agents/skills/gov-competitive-intel/ | 政府公共部门竞品情报 |

### 市场额外安装的技能

| 技能 | 来源 | 功能 |
|------|------|------|
| competitive-intelligence-market-research | ClawHub | B2B SaaS竞品情报（24场景） |
| competitive-radar | ClawHub | 竞品雷达（6信号类型，自动告警） |

## 四、情报归档索引

| 日期 | 简报状态 | P0事件 | 深度报告 | 归档文件 |
|------|---------|-------|---------|---------|
| 2026-05-05 | 已生成（恢复） | - | - | memory/2026-05-05.md |

## 五、记忆写入规则

- 每份情报简报 → 写入 memory/YYYY-MM-DD.md
- P0/P1事件 → 单独记录事件详情
- 来源可信度变化 → 更新第一节数据库
- 竞品档案更新 → 标注 timestamp

---

*蜂鸟在此。* 🐦
