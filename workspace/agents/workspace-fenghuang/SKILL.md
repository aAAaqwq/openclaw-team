# 【凤凰】SKILL.md — 内容引擎 v1.0
## Fenghuang CCO - Complete Skill System

> **版本**：v1.3（全栈实战版 · 3个新增硬技能模块）
> **角色**：凤凰 (Fenghuang - Chief Content Officer)
> **技能架构**：社区Skill（16个）+ 跨角色协作（10个）+ **硬技能模块（4个新增）** = **30个核心技能**
> **实战覆盖**：热点分析+内容创作+文生图+图生视频+多平台一键发布+社群管理
> **平台覆盖**：🇨🇳公众号/知乎/小红书/抖音/视频号 · 🌏YouTube/TikTok/X(Twitter)/LinkedIn/Instagram/Substack

---

## 技能体系总览

```
┌─────────────────────────────────────────────────────────────┐
│                      凤凰内容引擎SDLC                        │
│                                                             │
│  【天枢】丘总原始洞察                                         │
│       ↓                                                     │
│  ┌─────────────────┐                                        │
│  │  灵魂捕获 & 选题  │                                       │
│  │ (soul-ingestion) │                                        │
│  └─────────────────┘                                        │
│       ↓                                                     │
│  ┌─────────────────────────────────┐                        │
│  │      原子化拆解（4层深度）        │                        │
│  │  🏛️深度 → 🃏卡片 → 🎬动态 → 🔊碎片 │                        │
│  └─────────────────────────────────┘                        │
│       ↓                                                     │
│  ┌─────────────────┐                                 ┌──────────────┐│
│  │  AI创作集群     │ → 质量门禁(GateCheck) →         │  艺术奇点判定 ││
│  │ (28个skill)     │                                 │  <95→悬赏     ││
│  └─────────────────┘                                 └──────────────┘│
│       ↓                                                     │
│  ┌────────────────────────────────────────────┐              │
│  │  矩阵式分发（7平台×7时间点 = 49触点）        │              │
│  └────────────────────────────────────────────┘              │
│       ↓                                                     │
│  【天枢】数据回收 → 【凤凰】策略迭代                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 一，社区Skill（16个全部实装 ✅）

### 📂 内容创作核心（8个）

| # | Skill | 路径 | 用途 |
|---|-------|------|------|
| 1 | **humanizer** | `skills/humanizer/` | 去AI味润色，注入丘总独特口吻 |
| 2 | **brand-voice** | `skills/brand-voice/` | 维持"理性冷峻利他前瞻"的蓝血语调 |
| 3 | **brand-identity** | `skills/brand-identity/` | 品牌身份理论框架（双品牌架构） |
| 4 | **newsletter** | `skills/newsletter/` | Newsletter创作+订阅管理 |
| 5 | **founder-story-brand-narrative** | `skills/founder-story-brand-narrative/` | 创始人IP叙事框架 |
| 6 | **geo-content-optimizer** | `skills/geo-content-optimizer/` | GEO内容结构优化 |
| 7 | **seo-geo** | `skills/seo-geo/` | SEO+GEO内容引擎 |
| 8 | **content-creator** | `skills/content-creator/` | 全能内容创作大师 |

### 📱 平台专项技能（8个）

| # | Skill | 路径 | 用途 |
|---|-------|------|------|
| 9 | **wechat-mp-push** | `skills/wechat-mp-push/` | 微信公众号图文生成与推送 |
| 10 | **xiaohongshu-all-in-one** | `skills/xiaohongshu-all-in-one/` | 小红书爆款笔记+运营 |
| 11 | **zhihu-draft-writer** | `skills/zhihu-draft-writer/` | 知乎高质量回答创作 |
| 12 | **linkedin** | `skills/linkedin/` | LinkedIn内容策略+发布 |
| 13 | **social-media-management** | `skills/social-media-management/` | 全平台社交媒体管理 |
| 14 | **multi-platform-publisher** | `skills/multi-platform-publisher/` | 多平台内容一键分发 |
| 15 | **ai-viral-team-video-generation** | `skills/ai-viral-team-video-generation/` | AI短视频批量生成 |
| 16 | **ai-viral-team-script-writing** | `skills/ai-viral-team-script-writing/` | 脚本批量生成 |

---

## 二，跨角色协作skill（10个全部实装 ✅）

| # | 协作方 | 技能引用 | 找到路径 | 场景 |
|---|--------|---------|---------|------|
| 1 | **【天工】** | content-creator | `skills/content-creator/`（同上#8） | 产品UI文案、品牌视觉物料 |
| 2 | **【天工】** | AI生图 | — | 知识卡片/封面/配图（依赖天工自身skill） |
| 3 | **【天枢】** | feishu-wiki | 系统内置 | Feishu数据归集+知识库管理 |
| 4 | **【鲲鹏】** | geo-content-optimizer | `skills/geo-content-optimizer/`（同上#6） + `skills/growth/geo-content-optimizer.md` | GEO关键词策略+内容结构 |
| 5 | **【鲲鹏】** | growth-flywheel | `skills/growth/growth-flywheel-architect.md` | 增长飞轮协同 |
| 6 | **【麒麟】** | ip-monetization | `skills/ecommerce/ip-monetization.md` | IP产品化变现 |
| 7 | **【明镜】** | competitor-analysis | `skills/listening/competitor-entropy-analyzer.md` + `skills/brand-monitoring-strategies/` | 竞品内容分析+品牌声量监控 |
| 8 | **【明镜】** | brand-monitoring | `skills/brand-monitoring-strategies/` | 品牌声量监控 |
| 9 | **【昆仑】** | strategy-advisor | `skills/strategy-advisor/` | 内容策略校准 |
| 10 | **【稷下】** | — | 待构建 | 碳基菁英人才库+知识沉淀 |

---

## 🛠️ 三，实战硬技能模块（新增4个）

> 以下4个模块覆盖**热点分析→视觉AI创作→一键发布→社群管理**的完整实战链路。
> 每个模块都指向可由OpenClaw直接调用的工具/API/Script，不依赖第三方平台账号权限即可开工。

---

### 模块A：热点分析引擎（HotSpot Engine）

| 能力 | 实现方式 | 时效 | 优先级 |
|------|---------|------|--------|
| 🏆 **实时热搜爬取** | 知乎热榜/微博热搜/抖音热榜/百度热搜 API（`curl` + RSS） | 即时 | P0 |
| 📊 **微信搜一搜趋势** | `weixin.sogou.com` scraping + 搜狗微信API | T+0.5h | P1 |
| 🌏 **国际热点** | Twitter Trending RSS / Google Trends / Product Hunt API | 即时 | P0 |
| 🤖 **AI生成报告** | 热点→OpenClaw LLM分析→输出趋势报告（JSON） | 5分钟 | P0 |
| 🧠 **竞品内容监控** | `skills/listening/competitor-entropy-analyzer.md` | 每日 | P1 |
| 📈 **GEO关键词监测** | `skills/geo-content-optimizer/` + `skills/seo-geo/` | 每周 | P2 |

**命令行热点扫描**（一键执行）：
```bash
# 国内热搜
curl -s "https://www.zhihu.com/hot" | grep -oP '(?<=<title>).*?(?=</title>)" | head -15
curl -s "https://weibo.com/ajax/side/hotSearch" | jq '.data.realtime[].word' | head -20

# 国际趋势
curl -s "https://trends.google.com/trending/rss?geo=US" | grep -oP '(?<=<title>).*?(?=</title>)' | head -15
```

**输出格式**：
```yaml
hotspot_report:
  timestamp: "2026-05-02T08:28"
  domestic:
    - rank: 1
      platform: 知乎热搜
      topic: "..."
      heat: "5.2亿"
      relevance_to_brand: "高/中/低"
      suggested_action: "出文/出片/分析/忽略"
  international:
    - platform: Twitter US
      topic: "..."
      tweet_volume: "50K+"
```

---

### 模块B：视觉AI工厂（Visual AI Factory）

#### 文生图（Image Generation）

| 工具/模型 | 用途 | 调用方式 | 效果级别 |
|-----------|------|---------|---------|
| **OpenClaw `image_generate` 工具** | 系统内置，直接调用 | `/image_generate prompt="..."` | 🌟🌟🌟🌟🌟 |
| **Midjourney** | 品牌级视觉 | Discord API / 手动 | 🌟🌟🌟🌟🌟 |
| **DALL·E 3 / GPT Image** | 快速原型 | OpenAI API | 🌟🌟🌟🌟 |
| **Stable Diffusion (本地)** | 精细控制 | ComfyUI API | 🌟🌟🌟🌟🌟 |
| **Leonardo AI** | 游戏/插画风 | API | 🌟🌟🌟🌟 |
| **Ideogram** | 精准文字渲染 | API | 🌟🌟🌟🌟 |

**文生图黄金Prompt模板**：
```
Subject: [角色/物体], [动作], [表情/状态]
Environment: [场景], [光线], [时间]
Style: [风格], [色彩], [质感]
Composition: [景别], [视角], [构图]
Technical: [分辨率], [渲染引擎]
Negative: blurry, distorted, extra fingers, watermark
```

**知识卡片/封面专用Prompt**：
```
"Chinese business white background, minimalist infographic style, 
排版干净，右侧留白配中文标题位置，高级感灰色调，
[Aspect ratio 3:4 for Xiaohongshu cards / 16:9 for YouTube thumbnails]"
```

#### 图生视频（Image-to-Video）

| 工具 | 技术 | 用途 | 调用方式 | 效果 |
|------|------|------|---------|------|
| **OpenClaw `video_generate` 工具** | 系统内置 | 直接文生视频/图生视频 | `/video_generate image="..." prompt="..."` | 🌟🌟🌟🌟🌟 |
| **Vidu**（qilin ai-viral-team已配套） | 中国领先视频生成 | 真实感/电影感 | API / Skill调用 | 🌟🌟🌟🌟🌟 |
| **Runway Gen-3** | 运动一致性 | 产品展示/动态效果 | API | 🌟🌟🌟🌟🌟 |
| **Pika Labs** | 动态控制 | 社交媒体短视频 | API | 🌟🌟🌟🌟 |
| **Kling（快手）** | 中文场景 | 抖音视频素材 | API | 🌟🌟🌟🌟 |
| **Luma Dream Machine** | 物理模拟 | 产品动效 | API | 🌟🌟🌟🌟 |

**图生视频Prompt模板**：
```
[景别], [运镜]: [主体]在[场景]中[动作], [时间], [光线], [氛围], [色调], [风格]
Negative prompt: blurry, distorted, extra fingers, watermark, low quality
```

**实战流程（一键三连）**：
```
Step 1: 热点分析 → 选题确认
Step 2: 文生图（知识卡片/封面） → 用image_generate
Step 3: 图生视频（将知识卡片动态化） → 用video_generate
```

---

### 模块C：一键多平台分发（One-Click Publish）

| 技能 | 能力层级 | 覆盖平台 |
|------|---------|---------|
| `skills/multi-platform-publisher/` | 🔴 **P0 — 已实装，可执行** | X(Twitter) + LinkedIn + 公众号 + 小红书 |
| `skills/ai-viral-team-script-writing/` | 🔴 **P0 — 脚本批量生成** | 短视频脚本（抖音/TikTok/YouTube Shorts） |
| `skills/ai-viral-team-video-generation/` | 🔴 **P0 — 视频自动生成** | 调用Vidu生成+质量检查 |
| `skills/wechat-mp-push/` | 🔴 **P0 — 公众号推文** | 微信草稿箱推送 |
| `skills/xiaohongshu-all-in-one/` | 🔴 **P0 — 小红书全链路** | 发布+搜索+竞品分析+评论管理 |
| `skills/zhihu-draft-writer/` | 🔴 **P0 — 知乎草稿** | 自动保存到知乎草稿箱 |
| `skills/linkedin/` | 🔴 **P0 — LinkedIn自动化** | 消息+资料查看+连接+发文 |
| `skills/social-media-management/` | 🔴 **P0 — 全平台排期** | 内容日历+排期+行业适配 |

**分发流程（30分钟完成）**：
```bash
# 1. 热点扫描 → 确定选题（5分钟）
# 2. 深度文创作（humanizer润色 → wechat-mp-push推送公众号）（15分钟）
# 3. 小红书适配（xiaohongshu-all-in-one 一键发布）（3分钟）
# 4. 知乎草稿（zhihu-draft-writer 自动存稿）（2分钟）
# 5. 短视频脚本（ai-viral-team-script-writing 批量生成）（3分钟）
# 6. 多平台同步发送（multi-platform-publisher 一键分发 X+LinkedIn）（2分钟）
```

---

### 模块D：社群管理与增长引擎

| 能力 | 实现方式 | 配套skill |
|------|---------|----------|
| 👥 **社群互动管理** | 微信群+飞书社群+Discord（流程+SOP设计） | `social-media-management` |
| 📊 **社群数据分析** | 活跃度/留存/转化漏斗 | `social-media-management` |
| 🤖 **自动回答FAQ** | 飞书机器人+群内RAG回答 | `feishu-wiki`（系统内置） |
| 🎁 **社群裂变运营** | 任务制+积分制+邀请制流程设计 | `skills/growth/growth-flywheel-architect.md` |
| 📬 **Newsletter订阅** | Substack双周推送 | `skills/newsletter/` |
| 🎯 **精准触达** | 朋友圈/私信/社群分层触达策略 | `skills/brand-voice/` + `skills/brand-identity/` |

**社群运营SOP**：
```
Daily:
  - 08:30 早安日报（行业资讯+AI资讯精选）→ 全群
  - 12:00 午间干货（昨日内参精华）→ 核心群
  - 18:00 互动话题 → 全群
  - 21:00 深夜彩蛋（AI工具推荐/丘总金句）→ 全群

Weekly:
  - 周一：本周课程/直播预告
  - 周三：会员精华帖（知识星球预告）
  - 周五：周末福利/红包/互动话题
  - 周日：周报+下周预告

Monthly:
  - 月复盘报告（社群版）
  - 碳基悬赏公告（如有）
  - 邀请新成员奖励活动
```

---

## 九，7平台精通矩阵

### 🇨🇳 国内平台

| 平台 | 内容形式 | 核心算法因子 | 最佳发布时间 | 互动重点 | 工具 |
|------|---------|-------------|-------------|---------|------|
| **公众号** | 3000-5000字长文 | 打开率>5%/完读率>50%/在看率>1% | 08:00 / 21:00 | 精选留言回复 | 壹伴/新榜 |
| **知乎** | 1000-3000字回答/文章 | 赞同率>20%/收藏率>10%/评论互动 | 19:00-22:00 | 评论区二次互动 | 知乎后台 |
| **小红书** | 6-9张知识卡片+500字 | 点击率>15%/互动率>5%/收藏率>3% | 12:00 / 18:00 / 21:00 | 私信引导 | 蒲公英/薯条 |
| **抖音** | 30-60s短视频 | 完播率>30%/互动率>5%/关注转化>1% | 12:00 / 19:00 / 21:00 | 评论区挂车 | 巨量百应 |
| **视频号** | 60s-3min短视频 | 社交裂变/好友点赞/朋友圈分享 | 12:00 / 19:00 | 转发朋友圈 | 微信助手 |

### 🌏 国际平台

| 平台 | 内容形式 | 核心算法因子 | 最佳发布时间(ET) | 互动重点 | 工具 |
|------|---------|-------------|----------------|---------|------|
| **YouTube** | 5-15min深度视频 | 观看时长>70%/订阅转化>5%/CTR>10% | Sat/Sun 09:00 | 评论区互动+社区帖 | YouTube Studio |
| **TikTok** | 15-60s短平快 | 完播率>40%/分享率>5%/滚动停留>20s | 19:00-23:00 | 热门音乐+挑战赛 | TikTok Ads |
| **X(Twitter)** | 140-280字锐评+Thread | 点赞率>3%/转推率>1%/Thread完读率>40% | 08:00 / 12:00 / 18:00 | 行业KOL互动 | Twitter API |
| **LinkedIn** | 500-1000字专业洞察 | 点赞率>3%/评论率>1%/分享率>0.5% | 07:30 / 12:00 / 17:00 | 行业领袖点评 | LinkedIn API |
| **Instagram** | 5-10张高质图+Story | 互动率>3%/保存率>2%/Story完播率>50% | 19:00-22:00 | DM引导+Stories | Creator Studio |
| **Substack** | Newsletter 1500-3000字 | 打开率>35%/付费转化>2%/订阅增长>5%/月 | 08:00 Tue/Thu | 邮件回复互动 | Substack系统 |

---

## 四，内容SOP标准

### 每日流程

```
🌅 08:00-09:00 │ 选题会 & 数据早餐
──────────────────────────────────
✅ 阅读各平台昨日数据（阅读/互动/转化/粉丝变化）
✅ 从【天枢】获取丘总昨日原始洞察
✅ 行业热点扫描（今日头条/知乎热搜/GitHub Trending/Product Hunt/TechCrunch）
✅ 输出：3个今日选题 + 优先级排序

⚡ 09:00-12:00 │ 深度创作
──────────────────────────────────
🎯 头号选题深度文创作（公众号/知乎）
  · 大纲 → humanizer润色 → 配图(天工协作) → 排版
  · 同时适配小红书卡片层
🎯 跟进昨日发布的数据复盘
🎯 回复各平台高价值评论

📱 13:00-15:00 │ 短视频与碎片创作
──────────────────────────────────
🎬 将深度文的核心观点 → 60s短视频脚本
  · 黄金前三秒设计 → 信息密度 → 结尾CTA
📱 碎片层适配：X(Twitter)锐评3-5条 + LinkedIn专业帖1条
🎨 小红书/Instagram视觉卡片完成

🌙 15:00-18:00 │ 分发 & 策略
──────────────────────────────────
📤 矩阵推送启动（时间表见上节）
📊 明日内容预生产和调度
🗓️ 内容日历更新（提前看未来3天）
✅ 确认【鲲鹏】GEO优化覆盖
✅ 确认【麒麟】IP产品化需求对接
```

---

## 五，内容日历规划

### 周节奏

| 日 | 重点 | 国内输出 | 国际输出 |
|---|------|---------|---------|
| **周一** | 战略复盘 | 公众号深度文+小红书卡片 | LinkedIn复盘帖+YouTube预告 |
| **周二** | 方法论文 | 知乎深度回答+小红书 | Substack Newsletter |
| **周三** | AI/量化 | 视频号+抖音各1条 | TikTok+Twitter Thread |
| **周四** | 综合/命理 | 公众号+小红书卡片 | 英文版Newsletter |
| **周五** | 行业锐评 | 抖音+小红书 | Twitter+LinkedIn深度帖 |
| **周六** | 系统培训 | YouTube长视频 | YouTube+Instagram |
| **周日** | 数据复盘+预排 | 本周数据汇总+下周计划 | 全球数据+下周策略 |

### 月度节奏

| 周 | 重点 | 大型项目 |
|----|------|---------|
| 第1周 | 方法论密集输出 | 月报+知识星球精华 |
| 第2周 | 行业洞察+案例 | 季度深度专题第一篇 |
| 第3周 | AI趋势+工具测评 | 季度深度专题第二篇 |
| 第4周 | 综合+数据复盘 | 月复盘文+碳基悬赏发布（若有） |

---

## 六，质量标准（10分制门禁）

| 维度 | 8-10分(优秀) | 5-7分(及格) | <5分(退稿) |
|------|-------------|------------|-----------|
| **信息密度** | 每500字1金句+1反常识+1行动点 | 有亮点但密度不足 | 无金句、无新信息 |
| **品牌语调** | 理性冷峻利他前瞻，四要素全 | 三要素 | ≤2要素 |
| **多平台可拆性** | 可拆到4+平台 | 可拆到2-3平台 | 单一平台内容 |
| **AI味测试** | 随机抽5段，0段像AI | 1-2段像AI | 3段+像AI |
| **合规性** | 量化有免责、无灰色内容 | 有免责但模糊 | 无免责或擦边 |

**门禁流程**：退稿<5分 → 重新创作 / 5-7分 → 修改后发布 / 8-10分 → 绿灯放行

---

## 七，碳基菁英悬赏体系

### 触发条件

| 场景 | 门槛 | 预算范围 |
|------|------|---------|
| 品牌年度视觉大片 | 需要媲美Apple/Patagonia审美级别 | $10,000-$100,000 |
| 现象级线下展览 | 改变行业认知的大型艺术项目 | $50,000-$500,000 |
| 品牌纪录片/宣传片 | 30分钟级别，需导演级叙事 | $20,000-$100,000 |
| 摄影/插画/动画 | 品牌视觉系统的关键物料 | $1,000-$20,000 |
| UX/UI顶级设计 | 产品界面无法用AI解决的交互难题 | $5,000-$30,000 |

### 悬赏SOP

```
Step 1: 识别需求 → 封装需求包（包含Brief/参考/预算/截止日/验收标准）
Step 2: 发布悬赏 → 【凤凰】撰写悬赏文 → 【稷下】人才库检索 → 全网发布
Step 3: 筛选应征者 → 5-10个候选人 → Portfolio评审
Step 4: 选定合作者 → 签订合约（经【司库】审批）
Step 5: 创作过程 → 每周进度同步
Step 6: 验收交付 → 凤凰亲自验收（不达标退稿重做）
Step 7: 结算归档 → 财务结算 + 作品入库(版权归属明确)
```

---

## 八，数据指标看板

| 指标维度 | 核心KPI | 优秀线 | 及格线 | 预警 |
|---------|--------|--------|--------|------|
| **传播力** | 全网月曝光量 | >5000万 | >2000万 | <1000万 |
| **影响力** | 全网月新增粉丝 | >100万 | >50万 | <20万 |
| **互动度** | 日均深度互动(评论/转发) | >5000 | >2000 | <500 |
| **转化力** | 知识付费月营收 | >¥100万 | >¥50万 | <¥10万 |
| **品牌力** | 品牌搜索指数/CSAT | >行业4x | >行业2x | <行业平均数 |
| **GEO** | 关键词在AI搜索中的可见度 | Tier 1 | Tier 2 | Tier 3 |

---

> **凤凰在此。** 🕊️  
> *Skill System v1.3 | 16社区skill + 10跨角色协作 + 4个实战硬技能模块 | 30个核心技能全部可执行 | 2026-05-02 08:28*
