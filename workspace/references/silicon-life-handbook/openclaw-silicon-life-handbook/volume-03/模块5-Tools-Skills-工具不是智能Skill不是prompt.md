# 卷三｜系统骨架：OpenClaw 官方文档深度解剖
## 模块5｜Tools / Skills
### ——工具不是智能，Skill 不是 prompt；真正拉开差距的是：工具设计、Skill 设计、Skill 管理、Skill 运营

> 本模块定位：
> 这一章不是“工具清单说明书”，也不是“Skill 怎么写的入门帖子”。
> 它要解决的是更深一层的问题：
>
> **为什么很多人装了一堆工具、写了一堆 Skills，Agent 还是不稳定、不聪明、不好管；以及怎样把 Tools / Skills 真正变成可复制、可治理、可进化的系统能力。**

---

## 证据链

### OpenClaw 官方依据
- `tools/index.md`
- `tools/skills.md`
- `tools/creating-skills.md`
- `tools/skills-config.md`
- `cli/skills.md`
- `tools/exec.md`
- `tools/browser.md`
- `reference/templates/TOOLS.md`
- 以及本卷前文相关：`concepts/context.md`、`concepts/session-tool.md`、`concepts/messages.md`

### 外部高口碑资料（仅吸收与官方机制可对齐的部分）
#### 一线工程文章 / 官方文档
- Anthropic Engineering：**Writing effective tools for agents — with agents**
- Anthropic Engineering：**Introducing advanced tool use on the Claude Developer Platform**
- Claude Docs：**Agent Skills / Best practices**
- Claude Docs：**Tool use / implement tool use**
- VS Code：**Use Agent Skills in VS Code**

#### GitHub / 社区最佳实践
- GitHub：**mgechev/skills-best-practices**
- GitHub：**vercel-labs/agent-skills**（技能样板价值很高）

#### 可作为延伸阅读/课程感材料的资源
- DigitalOcean：**How to Write and Implement Agent Skills**
- DEV Community：**How to Build an Agent Skill: A Practical Guide**
- YouTube：**The complete guide to Agent Skills**
- YouTube：**You're likely missing out on agent skills true potential!**

> 注意：本章不会机械搬运这些资料，而是做“官方机制 × 外部标杆实践”的交叉消化。

---

## 目录
- [1）为什么模块5值得单独出一本书](#1为什么模块5值得单独出一本书)
- [2）先立五条底线](#2先立五条底线)
- [3）OpenClaw 里的 Tools 与 Skills 各自负责什么](#3openclaw-里的-tools-与-skills-各自负责什么)
- [4）Tool 的本质：给模型一个受约束的动作空间](#4tool-的本质给模型一个受约束的动作空间)
- [5）Skill 的本质：给模型一份按需加载的领域作战手册](#5skill-的本质给模型一份按需加载的领域作战手册)
- [6）为什么 Skill 不是 system prompt 的替代品](#6为什么-skill-不是-system-prompt-的替代品)
- [7）市面上最常见的三种误解](#7市面上最常见的三种误解)
- [8）Tool 设计：Anthropic 一线实践给我们的真正启发](#8tool-设计anthropic-一线实践给我们的真正启发)
- [9）Skill 设计：从“会写 SKILL.md”到“会做能力包”](#9skill-设计从会写-skillmd到会做能力包)
- [10）Skill 标准结构：SKILL.md / scripts / references / assets](#10skill-标准结构skillmd--scripts--references--assets)
- [11）如何写一个真正会被触发的 description](#11如何写一个真正会被触发的-description)
- [12）Progressive Disclosure：为什么薄 SKILL.md 比厚 prompt 更高级](#12progressive-disclosure为什么薄-skillmd-比厚-prompt-更高级)
- [13）Skill 的四层自由度设计](#13skill-的四层自由度设计)
- [14）标杆案例：好 Skill 与坏 Skill 的差别到底在哪](#14标杆案例好-skill-与坏-skill-的差别到底在哪)
- [15）Skill 不只是写法，更是管理问题](#15skill-不只是写法更是管理问题)
- [16）OpenClaw 官方 Skill 管理机制：位置、优先级、覆盖、门控](#16openclaw-官方-skill-管理机制位置优先级覆盖门控)
- [17）Skill Ops：版本、测试、验收、分发、淘汰、审计](#17skill-ops版本测试验收分发淘汰审计)
- [18）为什么很多团队写了很多 Skill 效果还是差](#18为什么很多团队写了很多-skill-效果还是差)
- [19）从单个 Skill 到 Skill Library，再到 Skill Platform](#19从单个-skill-到-skill-library再到-skill-platform)
- [20）适合 OPEN CAIO 的 Skill 体系架构](#20适合-open-caio-的-skill-体系架构)
- [21）Skill 成熟度模型：L0 到 L5](#21skill-成熟度模型l0-到-l5)
- [22）推荐深挖的教程 / 课程 / GitHub 文档清单](#22推荐深挖的教程--课程--github-文档清单)
- [23）模块5训练模板 / 检查清单 / 验收口径](#23模块5训练模板--检查清单--验收口径)
- [24）本模块一句话结论](#24本模块一句话结论)

---

## 1）为什么模块5值得单独出一本书
如果说卷三前几章解决的是：
- Agent 作为什么运行单元存在
- Workspace 如何承载长期记忆与规则
- Session / Context / Queue 如何维持长期对话稳定
- Routing / Bindings 如何决定“谁来答”

那么模块5解决的是另一个更致命的问题：

> **Agent 到底靠什么把“会说”升级成“会做”，又靠什么把“偶尔会做”升级成“稳定会做”。**

很多人把这一层想浅了，通常有三种表现：

1. 觉得 Tools 只是外设，主角还是模型。
2. 觉得 Skill 只是“多写一段 prompt”。
3. 觉得工具越多、Skill 越多，Agent 就越强。

这三种判断都不对。

Anthropic 的工程文章给出的答案很清楚：
- 工具设计不对，Agent 就会选错工具、输错参数、上下文爆炸。
- Skill 设计不对，Agent 就会召不出来、召错、读不进重点、维护越来越乱。
- 当工具和技能库扩张到几十、上百个时，问题不再是“有没有能力”，而是：
  - **如何发现能力**
  - **如何延迟加载**
  - **如何防止噪音压死上下文**
  - **如何治理能力库，而不是让它失控**

所以模块5不是“辅助章节”。
它本质上是：

> **从 prompt 时代走向 capability engineering 时代的分水岭。**

---

## 2）先立五条底线

### 底线1：工具不是智能
工具只负责动作，不负责判断。

- `read` 负责读，不负责理解
- `browser` 负责交互，不负责判断值不值得交互
- `exec` 负责运行，不负责判断命令是否必要或安全
- `message` 负责投递，不负责判断结论是否已经成熟

所以：

> **工具解决的是“能不能动”，不是“该不该动”。**

### 底线2：Skill 不是 prompt
Skill 在 OpenClaw 官方机制里是一个目录，而不是一句“补充提示词”。
它至少包含：
- `SKILL.md`
- `name`
- `description`

更完整时还可能包含：
- `scripts/`
- `references/`
- `assets/`

Skill 的关键不在于“有一段 instructions”，而在于：

> **它是一个可发现、可触发、可维护、可覆盖、可按需展开的能力包。**

### 底线3：工具多不等于强
Anthropic 的 advanced tool use 文章已经讲得很透：
- 工具定义本身会吃掉上下文
- 工具越多，选错的概率越大
- 同名近义的工具会大幅恶化选择质量

所以：

> 工具不是越多越强，而是越多越需要搜索、命名空间、门控和收敛。

### 底线4：Skill 多不等于体系
一个目录里有 100 个 skill，不叫平台，可能只是垃圾堆。

真正的 Skill 体系至少要有：
- 命名规范
- 触发规则
- 管理方式
- 测试机制
- 生命周期
- 淘汰与升级机制

### 底线5：会写 Skill，不等于会运营 Skill
Skill 真正难的不是 authoring，而是后面的：
- 召回率
- 误触发率
- 上下文成本
- 版本维护
- 权限边界
- 分发与共享

也就是说：

> **Skill 最大的难点，不是“写出来”，而是“长期好用”。**

---

## 3）OpenClaw 里的 Tools 与 Skills 各自负责什么
要真正学透这一层，必须把两者职责切开。

### 3.1 Tools 负责动作接口标准化
OpenClaw 的一流工具机制，本质是在做：
- 参数结构化
- 动作类型化
- 权限边界化
- 运行路径可治理化

也就是把“自然语言想做点事”压缩成“受控的动作接口”。

### 3.2 Skills 负责能力组织与调用指导
OpenClaw 的 Skills 机制，本质是在做：
- 能力模块化
- 知识按需加载
- 领域工作流沉淀
- 脚本/模板/资料封装

### 3.3 两者之间的关系
一句话：

> **Tool 是手，Skill 是手册；Tool 定义动作边界，Skill 定义使用策略。**

再说得更硬一点：
- 没有 Tool，Skill 只有嘴，没有手。
- 没有 Skill，Tool 只有手，没有方法。

---

## 4）Tool 的本质：给模型一个受约束的动作空间
Anthropic 在工具工程文章里有一个很重要的工程视角：

> 工具不是写给 deterministic system 的函数接口，而是写给 non-deterministic agent 的动作契约。

这句话特别重要。
因为传统 API 设计，考虑的是“程序员知不知道怎么调用”；
而 Agent Tool 设计，考虑的是“模型会不会误解、误选、误填、误用”。

所以好工具的关键，不只是“能调用”，而是：

### 4.1 名字要可区分
名字一旦模糊，模型就会选错。

坏例子：
- `notify`
- `send`
- `message_user`
- `push_msg`

好例子：
- `slack_send_message`
- `github_create_pr`
- `feishu_doc_read`
- `feishu_doc_write`

### 4.2 描述要写清“何时用 / 何时不用”
Claude 的 tool 文档强调得非常明确：
- 详细 description 是工具表现最重要的因素
- 要写：
  - 它干什么
  - 什么时候该用
  - 什么时候不该用
  - 参数代表什么
  - 返回里不包含什么
  - 有什么 caveat

### 4.3 参数要可理解，而不是只可校验
JSON Schema 只能约束结构，不能教会模型“惯用法”。
所以 Anthropic 后来加了 `input_examples`，本质上是在补这块缺口。

### 4.4 返回结果要高信号、低噪音
不是返回越多越好。

好返回：
- 稳定 ID
- 关键字段
- 下一步决策需要的信息

差返回：
- 一堆内部字段
- 大量重复对象
- 模型根本不需要的调试信息

### 4.5 工具表面要收敛，不要碎片化
Claude 官方文档明确建议：
- 不要 create/update/delete 全拆成碎片工具
- 可以通过 `action` 参数合并相关动作

这其实是一个极重要的工程原则：

> **工具切得越碎，模型越难学会“什么时候选哪一个”。**

---

## 5）Skill 的本质：给模型一份按需加载的领域作战手册
Claude Skills 文档最有价值的地方，是把 Skill 彻底从“提示词补丁”里解放了出来。

它告诉你：
- metadata 永远会在上下文里
- `SKILL.md` 只会在相关时读
- 其他资源按需再读

这几条叠在一起，已经足够定义 Skill 的本质：

> **Skill 不是“我再给模型强调一遍”，而是“我把某类任务的打法、资源和约束，封装成一个可调用、可维护的专业能力包”。**

所以 Skill 真正的价值不只是 instruction，而是：

### 5.1 能力模块化
让一类经验从聊天中抽离出来。

### 5.2 知识可迁移
同样的打法可以在多个任务里复用。

### 5.3 上下文可控
不必每次把所有知识都塞进 prompt。

### 5.4 组织可治理
能力不再只存在于“某个 Agent 比较会”，而是沉淀成系统资产。

---

## 6）为什么 Skill 不是 system prompt 的替代品
这是很多人最容易混淆的地方。

### 6.1 system prompt 适合承载什么
system prompt 更适合承载：
- 全局规则
- 安全边界
- 运行时约束
- 权限说明
- 回复风格
- 工具列表与使用总则

### 6.2 Skill 适合承载什么
Skill 适合承载：
- 某领域工作流
- 某类任务的资源索引
- 某类任务的模板、样例、脚本
- 触发条件与不适用条件

### 6.3 为什么不能混
如果把大量 Skill 内容塞进 system prompt，会有四个问题：
1. 上下文爆炸
2. 所有任务都背无关知识
3. 无法按需触发
4. 维护成本极高

所以可以这样理解：

> system prompt 是宪法；Skill 是兵法。

---

## 7）市面上最常见的三种误解

### 误解1：Skill 就是长 prompt
这是最常见的低阶理解。
结果通常是：
- `SKILL.md` 写成散文
- 什么都往里塞
- 没有 references
- 没有 scripts
- 最后一加载就把上下文打爆

### 误解2：Skill 就是文档仓库
有些人把 skill 文件夹写成这样：
- README
- INSTALL
- CHANGELOG
- EXAMPLES
- NOTES
- FAQ
- 各种副文档

结果是：
- 模型读不出主路径
- 维护成本飙升
- 目录结构像人类项目，不像 agent skill

### 误解3：Skill 越多越高级
Skill 目录多，不代表能力强。
如果没有：
- discoverability
- negative triggers
- versioning
- testing
- pruning

那只会越来越乱。

---

## 8）Tool 设计：Anthropic 一线实践给我们的真正启发
Anthropic 的《Writing effective tools for agents》这篇文章，不只是讲“工具要写好”，它其实给了整个 Agent 能力设计的底层方法论。

### 8.1 不要急着全量做工具，先做 prototype
先快速搭原型，再让 agent 真跑，看它卡在哪里。
这比主观想象要可靠得多。

### 8.2 必须做 evaluation
他们强调：
- 不只是看能不能调用
- 要用真实任务评估成功率
- 记录：
  - tool call 数量
  - tokens
  - runtime
  - tool error
  - 失败 transcript

这对 OpenClaw 的 Skills 同样适用。

### 8.3 用 transcript 反推设计缺陷
不是只看模型说了什么，而是看：
- 它为什么没调工具
- 为什么调错工具
- 为什么参数填错
- 为什么重复调用

### 8.4 让 agent 帮你改工具和 Skill
Anthropic 甚至直接用 agent 分析 transcript，再反过来优化 tools。
这给我们的启发非常大：

> Skill 不是一次性设计产物，而是“评估—改写—再评估”的循环产物。

---

## 9）Skill 设计：从“会写 SKILL.md”到“会做能力包”
一个真正好的 Skill，绝对不只是会写 frontmatter。
它至少要解决五个问题：

1. **会不会被召回**
2. **被召回后会不会读到重点**
3. **会不会产生稳定结果**
4. **会不会拖累上下文**
5. **后续容不容易维护**

所以 Skill 设计要分五层看：

### 9.1 路由层：会不会被触发
靠的是 `name` + `description`。

### 9.2 指挥层：会不会按正确路径工作
靠的是 `SKILL.md` 主流程。

### 9.3 资源层：需要时能不能读到正确资料
靠的是 `references/`。

### 9.4 执行层：脆弱动作能不能稳定跑
靠的是 `scripts/`。

### 9.5 产物层：最终输出能不能像样
靠的是 `assets/` + 输出要求。

---

## 10）Skill 标准结构：SKILL.md / scripts / references / assets
综合 OpenClaw、Claude、VS Code 和 GitHub 社区最佳实践，最稳的结构就是：

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

### 10.1 `SKILL.md`：大脑，不是仓库
它应该承担：
- 触发说明
- 工作流
- 文件导航
- 输出规范
- 边界条件

它不应该承担：
- 大量背景科普
- 大段模板正文
- 大量 schema 原文
- 没有动作意义的长篇解释

### 10.2 `scripts/`：小而专的 deterministic 动作
放这里的脚本，应该满足至少一个条件：
- 高频重复
- 临场写容易出错
- 强一致性要求
- 需要批处理
- 安全性高于灵活性

### 10.3 `references/`：按需读的大知识块
适合放：
- API 说明
- 业务规则
- 评分标准
- 域知识手册
- 结构 schema
- 真实样例说明

### 10.4 `assets/`：最终输出的脚手架
适合放：
- 文档模板
- HTML 模板
- JSON 样板
- PPTX / 图片 / 图标
- boilerplate

---

## 11）如何写一个真正会被触发的 description
这是 Skill 成败最关键的一行。

因为在触发前，模型最稳定看到的只有：
- `name`
- `description`

一个强 description 至少要包含四类信息：

### 11.1 任务类型
比如：
- 公众号文章
- SEO 审计
- 会议纪要
- 合同审查
- 回测报告

### 11.2 用户触发表达
比如：
- “帮我写公众号”
- “做个 SEO audit”
- “整理成会议纪要”
- “看看合同风险”

### 11.3 适用边界
告诉模型：
- 什么场景一定该用

### 11.4 不适用边界（negative triggers）
告诉模型：
- 什么场景不要乱用

#### 坏 description
```md
description: 用来写内容
```

#### 好 description
```md
description: 当用户要求写公众号文章、把长文改成微信生态风格、降低AI味、优化标题和导语、输出适合公众号发布的结构化内容时使用。适用于“公众号”“微信长文”“公号改写”“去AI味重写”等表达。不用于法律文书、短视频口播稿或纯社媒短帖。
```

差距就在这里。

---

## 12）Progressive Disclosure：为什么薄 SKILL.md 比厚 prompt 更高级
这是模块5最重要的设计思想之一。

所谓 Progressive Disclosure，就是：
- metadata 永远可见
- 主说明按需读
- 大资料按需再展开
- 不把无关信息提前压进上下文

### 12.1 为什么它比厚 prompt 更高级
因为它同时解决了：
1. 上下文成本
2. 触发精度
3. 维护难度
4. 组合能力

### 12.2 薄 SKILL.md 的正确姿势
SKILL.md 不应该是百科，而应该是：
- 指挥图
- 路由表
- 决策树
- 资源索引
- 输出要求

### 12.3 厚信息放哪里
- 业务规则 → `references/`
- 结构定义 → `references/`
- 标准样例 → `references/`
- 重复动作 → `scripts/`
- 模板 → `assets/`

这是 Skill 从“会写”升级到“会设计”的关键标志。

---

## 13）Skill 的四层自由度设计
Claude 官方 best practices 给出一个非常值得直接吸收的框架：
**Set appropriate degrees of freedom**。

### 13.1 高自由：文本规则
适合：
- 多路径都成立
- 判断依赖上下文
- 需要创造性或分析能力

例子：
- 商业策略分析
- 品牌叙事改写
- 竞争对手拆解

### 13.2 中自由：模板化步骤 / 伪代码
适合：
- 有主路径
- 允许少量变化
- 结构比细节更重要

例子：
- 周报生成
- SEO 审计
- 会议纪要

### 13.3 低自由：严格序列
适合：
- 只要乱一点就容易翻车
- 必须按顺序执行

例子：
- 数据导入
- 审批归档
- 账本更新

### 13.4 固定脚本：把变动降到最低
适合：
- Variation 就是 bug
- 稳定性远比灵活性重要

例子：
- CSV 清洗
- PDF 批量处理
- 指定格式导出

真正的高手不是永远给模型高自由，
而是知道：

> **哪里该让模型想，哪里该让脚本接管。**

---

## 14）标杆案例：好 Skill 与坏 Skill 的差别到底在哪

### 14.1 差 Skill 示例
```md
---
name: writing
description: 写作相关
---

帮用户写东西，尽量写好一点。
```

问题：
- 不可发现
- 不可路由
- 无流程
- 无边界
- 无资源索引
- 无输出规范

### 14.2 合格 Skill 示例
```md
---
name: wechat-article-pro
description: 当用户要求写公众号文章、把长文改成微信风格、优化标题和导语、降低AI味时使用。不用于法律文书、短视频脚本或技术文档。
---

1. 先判断任务属于：从零写、旧稿改写、标题优化、排版整理。
2. 如果是公众号改写，读取 `references/style.md`。
3. 如果强调爆款标题，读取 `references/titles.md`。
4. 输出：标题候选、导语、正文、摘要、配图建议。
```

### 14.3 优秀 Skill 示例
优秀 Skill 会进一步补齐：
- `references/brand-voice.md`
- `references/de-ai-tone.md`
- `assets/article-template.md`
- `scripts/clean_ai_tone.py`

这时它已经不是一段说明，而是完整能力包了。

---

## 15）Skill 不只是写法，更是管理问题
很多人学 Skill，只停在 authoring。
但真正把 Agent 拉开差距的，是 Skill 管理。

为什么？
因为当 skill 数量到 20、50、100 时，真正的问题就不是“有没有 skill”，而是：
- 怎么发现
- 怎么命名
- 怎么分层
- 怎么禁用
- 怎么覆盖
- 怎么升级
- 怎么淘汰

所以 Skill 从 1 个走到 100 个，会经历一个视角变化：

> 一开始它是写作问题；后来它变成架构问题；最后它一定变成运营问题。

---

## 16）OpenClaw 官方 Skill 管理机制：位置、优先级、覆盖、门控
这是 OpenClaw 很有价值但很容易被低估的一层。

### 16.1 三个主要加载位置
官方支持：
1. 内置 Skills
2. `~/.openclaw/skills`
3. `<workspace>/skills`

### 16.2 优先级规则
优先级是：
- workspace 最高
- host/global 次之
- bundled 最低

这意味着你可以：
- 用工作区 skill 覆盖系统 skill
- 不改官方文件，仍然实现定制

### 16.3 extraDirs
官方还支持在 `openclaw.json` 里通过 `skills.load.extraDirs` 增加共享 skill 目录。
这特别适合：
- Git 仓库统一管理 skill pack
- 多 workspace 共享一批技能
- 团队级同步

### 16.4 门控（gating）
OpenClaw 的 `metadata.openclaw` 支持按以下条件过滤：
- OS
- bins
- env
- config

这意味着：

> 一个 Skill 不应该“只要存在就可用”，而应该“满足环境条件才暴露”。

### 16.5 per-skill 配置注入
`skills.entries.<skillKey>` 支持：
- `enabled`
- `env`
- `apiKey`
- `config`

这就把 Skill 从“静态说明”升级成了“可配置能力单元”。

### 16.6 官方检查命令
- `openclaw skills list`
- `openclaw skills info <name>`
- `openclaw skills check`

这几条命令其实就是最基础的 Skill 治理入口。

---

## 17）Skill Ops：版本、测试、验收、分发、淘汰、审计
这部分是市面教程最缺，但恰恰最值钱的内容。

### 17.1 版本管理
最少要做到：
- Skill 目录纳入 Git
- 重要变更写明“为什么改”
- 关键 Skill 有 review

### 17.2 测试
Skill 的测试至少分三类：

#### 触发测试
- 该触发时是否触发
- 相关表达能否召回

#### 边界测试
- 不该触发时是否误触发
- 近义请求是否误召回

#### 产物测试
- 调用后结果是否比无 skill 更稳
- 是否减少遗漏、返工、漂移

### 17.3 transcript 回放
最好的 Skill 优化方式之一，就是回放真实 transcript：
- 为什么没触发？
- 为什么误触发？
- 触发后为什么结果差？
- 是 description 问题，还是流程问题，还是 references 问题？

### 17.4 验收
一个 Skill 是否合格，不应该只看“写出来没有”，而应该看：
- 召回率
- 精准率
- token 成本
- 产物质量
- 稳定性
- 维护成本

### 17.5 分发
Skill 的分发应分层：
- Agent 私有
- 项目私有
- 军团共享
- 插件级共享
- ClawHub 发布

### 17.6 淘汰
长期：
- 不触发
- 误触发
- 价值被别的 skill 吸收
- 维护成本过高

那就该删。

### 17.7 审计
高风险 Skill 必须审计：
- 是否依赖 exec
- 是否需要 secrets
- 是否可能外发错误信息
- 是否可能越权
- 是否存在 prompt injection 面

这部分不做，Skill 多了之后一定出事故。

---

## 18）为什么很多团队写了很多 Skill 效果还是差
这是最现实的问题。

### 原因1：description 写得太泛
模型根本召不出来。

### 原因2：SKILL.md 太厚太散
一读就把上下文吃掉，还抓不到重点。

### 原因3：没有把稳定动作脚本化
导致模型每次临场发挥，结果漂移。

### 原因4：没有 negative triggers
于是误触发一堆。

### 原因5：references 放了，但没写“什么时候读”
结果资源虽然在，模型用不上。

### 原因6：没有评估机制
写完就算完工，没有 transcript 回放，没有触发测试。

### 原因7：没有生命周期管理
旧 skill 不删，新 skill 乱长，最后路由越来越差。

所以问题通常不在“模型不够聪明”，而在：

> **你并没有真正运营 Skill。**

---

## 19）从单个 Skill 到 Skill Library，再到 Skill Platform
这是能力体系化的关键视角。

### 19.1 单个 Skill
关注点：
- 能不能用
- 会不会触发
- 结果像不像样

### 19.2 Skill Library
关注点：
- 目录结构
- 命名一致性
- 冲突与覆盖
- 共享与私有边界

### 19.3 Skill Platform
关注点：
- 分层治理
- 环境门控
- 版本升级
- 审计与审批
- 评估体系
- 生命周期管理

大多数团队其实还停在第一阶段，却误以为自己已经在做平台。

---

## 20）适合 OPEN CAIO 的 Skill 体系架构
对于你这种军团化、多 Agent、强业务线、多治理需求的体系，最合理的 Skill 架构不是随便堆，而是四层。

### 20.1 通用基础层
全军共用：
- research
- summarize
- report-writing
- meeting-minutes
- file-organizer
- html-prototype

### 20.2 角色专属层
按 agent 职能分：
- 昆仑：战略拆解、资源裁决、晨会控场
- 明镜：审计、合同、风控、红队
- 天枢：任务卡、督办、巡检、升级
- 轩辕：开发、部署、修复、原型
- 凤凰：内容、公众号、品牌叙事
- 烛龙：回测、信号、交易日志

### 20.3 业务线层
按业务场景分：
- GEO
- 企业私有脑
- 数字员工
- 城市合伙人
- 自媒体矩阵
- AI 电商

### 20.4 组织治理层
这是最关键也最容易被忽略的一层：
- OKR
- 日报
- 晨会纪要
- 信誉分
- 整改单
- 验收模板
- 失败升级机制

如果这层不做，军团最终一定会变成：
- 业务 Skill 很多
- 治理 Skill 很少
- 系统越来越乱

---

## 21）Skill 成熟度模型：L0 到 L5
这个模型是为了把“有没有 Skill”升级成“Skill 现在处于什么阶段”。

### L0：口头能力
只有某个 Agent 或某个人“会”，但没有任何显式沉淀。

### L1：说明型 Skill
有 `SKILL.md`，能讲流程，但没有资源分层、没有脚本、没有验证。

### L2：可用型 Skill
具备：
- 清晰 description
- 基本工作流
- references 拆分
- 输出要求
- 基本 negative triggers

### L3：工程型 Skill
进一步具备：
- scripts
- assets
- 更稳定的路径设计
- 环境门控
- 基础测试

### L4：运营型 Skill
进一步具备：
- 版本管理
- transcript 回放
- 召回/误触发优化
- 验收标准
- 生命周期管理

### L5：平台型 Skill
进一步具备：
- 大规模共享
- 插件化/注册化分发
- 安全审计
- 自动评估
- 组织级治理

很多团队看似“有很多 skill”，其实大部分还停在 L1。

---

## 22）推荐深挖的教程 / 课程 / GitHub 文档清单
如果你要把这一块真正吃透，我建议不是看一篇，而是按层次看。

### 第一层：先看官方底层逻辑
1. OpenClaw：`tools/skills.md`
2. OpenClaw：`tools/skills-config.md`
3. OpenClaw：`tools/creating-skills.md`
4. OpenClaw：`cli/skills.md`

目的：
- 先搞清楚 OpenClaw 自己的机制边界
- 先别凭感觉“发明” Skill

### 第二层：看 Claude / Anthropic 的一线方法论
5. Anthropic：**Writing effective tools for agents — with agents**
6. Anthropic：**Introducing advanced tool use on the Claude Developer Platform**
7. Claude Docs：**Agent Skills / Best practices**
8. Claude Docs：**Tool use / implement tool use**

目的：
- 学工具设计
- 学 discoverability
- 学延迟加载
- 学 evaluation
- 学为什么 action space 会反噬系统

### 第三层：看平台型实现与跨生态落地
9. VS Code：**Use Agent Skills in VS Code**
10. GitHub：**mgechev/skills-best-practices**
11. GitHub：**vercel-labs/agent-skills**

目的：
- 学跨平台 Skill 的共同结构
- 学社区对目录、命名、层级、脚本的共识

### 第四层：看更易消化的教程型材料
12. DigitalOcean：**How to Write and Implement Agent Skills**
13. DEV Community：**How to Build an Agent Skill: A Practical Guide**
14. YouTube：**The complete guide to Agent Skills**
15. YouTube：**You're likely missing out on agent skills true potential!**

目的：
- 看别人怎么把复杂概念解释得更顺
- 用于训练军团内部其他 Agent 或碳基成员

### 推荐的阅读顺序
官方机制 → Anthropic 方法论 → GitHub 实例 → 教程/课程感材料

不要反过来。
否则很容易学成“会说不会做”。

---

## 23）模块5训练模板 / 检查清单 / 验收口径

### 23.1 写 Skill 前，先问自己 10 个问题
1. 这类任务是否高频反复出现？
2. 是否存在稳定工作流？
3. 是否需要领域知识？
4. 是否需要脚本化动作？
5. 是否需要模板资产？
6. 它的典型触发词是什么？
7. 它的不适用边界是什么？
8. 它是 agent 私有、团队共享还是插件级能力？
9. 它的成功标准是什么？
10. 它以后怎么测试、升级、淘汰？

### 23.2 一个合格 Skill 的 15 项检查清单
- [ ] name 清晰
- [ ] description 可发现
- [ ] 写了适用边界
- [ ] 写了 negative triggers
- [ ] SKILL.md 是流程，不是散文
- [ ] 明确写了何时读 references
- [ ] 明确写了何时跑 scripts
- [ ] 输出要求清晰
- [ ] `references/` 扁平
- [ ] `scripts/` 小而专
- [ ] `assets/` 与说明分离
- [ ] 已做至少一次真实 transcript 回放
- [ ] 已做至少一轮误触发检查
- [ ] 已通过 `openclaw skills check` 思维验证
- [ ] 已定义淘汰/升级条件

### 23.3 模块5的真正验收标准
学完这章，真正的验收不是“你会不会创建一个目录”。
而是你是否能回答：

1. 什么时候应该做成 Tool，什么时候做成 Skill？
2. 为什么 Skill 不能等于长 prompt？
3. 为什么 Skill 一定要做 progressive disclosure？
4. 如何管理几十个 Skill，而不是越堆越乱？
5. 如何把 Skill 从个人经验升级成组织资产？

如果这五个问题答不清，这一章就还没真正吃透。

---

## 24）本模块一句话结论
> **Tools 决定 Agent 能做哪些动作，Skills 决定 Agent 以什么方法做这些动作；而真正决定上限的，不是“装了多少能力”，而是“你是否把它们设计成可发现、可收敛、可验证、可治理、可进化的能力系统”。**

---

## 附录：如果把模块5继续往下拆，最值得拆出的三个独立专题
### 专题一：《Tool 设计手册》
- schema
- examples
- 命名空间
- 高信号返回
- action space 收敛
- defer loading / tool search

### 专题二：《Skill 设计手册》
- discoverability
- progressive disclosure
- scripts / references / assets 设计
- negative triggers
- output contracts

### 专题三：《Skill Ops 运营手册》
- registry
- review
- test
- rollout
- deprecate
- audit

如果卷三要继续加深，这三个都足够单独成册。
