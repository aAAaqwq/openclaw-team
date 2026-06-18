# 卷三｜系统骨架：OpenClaw 官方文档深度解剖
## 模块5下｜Skill Engineering & Skill Ops
### ——为什么 Skill 不是“会写 SKILL.md”，而是一整套可发现、可分层、可验证、可治理、可进化的能力系统

> 官方依据：
> - `tools/skills.md`
> - `tools/creating-skills.md`
> - `tools/skills-config.md`
> - `cli/skills.md`
>
> 外部交叉验证：
> - Claude Docs：`Agent Skills / Best practices`
> - VS Code：`Use Agent Skills in VS Code`
> - GitHub：`mgechev/skills-best-practices`
> - GitHub：`vercel-labs/agent-skills`
> - Anthropic Engineering：`Writing effective tools for agents — with agents`（将 evaluation / transcript / held-out test 的思想迁移到 Skill）
>
> 本章定位：
> 你真正要学会的不是“写一个 Skill”，而是：
>
> **把 Skill 当成系统资产来设计、管理、测试、发布与运营。**

---

## 目录
- [1）这章到底在解决什么问题](#1这章到底在解决什么问题)
- [2）Skill 的本质：按需加载的能力包](#2skill-的本质按需加载的能力包)
- [3）为什么 Skill 是大规模 Agent 的“能力组织单位”](#3为什么-skill-是大规模-agent-的能力组织单位)
- [4）Skill 与 prompt / Tool / system prompt / Memory 的边界](#4skill-与-prompt--tool--system-prompt--memory-的边界)
- [5）Skill 的标准结构与职责分工](#5skill-的标准结构与职责分工)
- [6）SKILL.md 写法：写给 agent，不是写给人](#6skillmd-写法写给-agent不是写给人)
- [7）description 的“召回工程”：如何写出高召回、低误触发](#7description-的召回工程如何写出高召回低误触发)
- [8）description 进阶：典型触发词、负触发词、近义表达、业务边界](#8description-进阶典型触发词负触发词近义表达业务边界)
- [9）Progressive Disclosure：薄 SKILL.md + 厚 references](#9progressive-disclosure薄-skillmd--厚-references)
- [10）references / scripts / assets 的组织法](#10referencesscriptsassets-的组织法)
- [11）四层自由度：什么时候给模型发挥，什么时候用脚本锁死](#11四层自由度什么时候给模型发挥什么时候用脚本锁死)
- [12）Skill 的负触发（negative triggers）与边界写法](#12skill-的负触发negative-triggers与边界写法)
- [13）从 1 个 Skill 到 Skill Library：分类、命名、冲突与覆盖](#13从-1-个-skill-到-skill-library分类命名冲突与覆盖)
- [14）OpenClaw 的 Skill 管理：位置、优先级、extraDirs、门控、配置](#14openclaw-的-skill-管理位置优先级extradirs门控配置)
- [15）Skill Registry：为什么要有技能台账，而不是靠目录裸奔](#15skill-registry为什么要有技能台账而不是靠目录裸奔)
- [16）Skill Review：为什么 Skill 也必须过审](#16skill-review为什么-skill-也必须过审)
- [17）Skill Evaluation：如何测试召回、误触发、结果质量](#17skill-evaluation如何测试召回误触发结果质量)
- [18）Skill Ops：版本、回放、发布、淘汰、审计](#18skill-ops版本回放发布淘汰审计)
- [19）为什么“写了很多 Skill 还是不强”](#19为什么写了很多-skill-还是不强)
- [20）面向军团的 Skill Platform 架构](#20面向军团的-skill-platform-架构)
- [21）适合 OPEN CAIO 的 Skill 分层体系](#21适合-open-caio-的-skill-分层体系)
- [22）Skill 成熟度模型 L0-L5](#22skill-成熟度模型-l0-l5)
- [23）标杆案例：从普通 Skill 到平台级 Skill 的分水岭](#23标杆案例从普通-skill-到平台级-skill-的分水岭)
- [24）Skill Engineering 训练模板 / 检查清单 / 验收口径](#24skill-engineering-训练模板--检查清单--验收口径)
- [25）本章一句话结论](#25本章一句话结论)

---

## 1）这章到底在解决什么问题
Skill 在市面上的误解太深。

很多人把 Skill 当成：
- 一段更长的 prompt
- 一份给人看的操作文档
- 一堆可复制粘贴的模板
- 甚至只是“我写了一个目录，里面放了点东西”

但在 OpenClaw / Claude / VS Code / AgentSkills 这条主流体系里，Skill 的真实定位是：

> **大规模 Agent 能力系统的组织单位。**

当你只有 1 个 agent、3 个工具、5 个 task 时，你感觉不到 Skill 管理的重要性。
但当你开始拥有：
- 多个 agent
- 多条业务线
- 很多重复任务
- 复杂的工作流
- 越来越长的上下文
- 多人协作写 skill

你马上就会遇到一系列问题：
- 该触发时不触发
- 不该触发时乱触发
- 相似 skill 互相打架
- skill 越写越厚，最后谁都不敢维护
- 没有测试，不知道 skill 到底有没有价值
- 没有版本，不知道哪次修改把系统搞坏了
- 没有淘汰机制，skill 越来越多，越来越像垃圾场

所以这章的真正任务，不是教你“会写一个 skill”，而是教你：

> **如何让 Skill 从个人经验升级为长期可用、组织可治理、系统可演化的能力资产。**

---

## 2）Skill 的本质：按需加载的能力包
从官方与标杆实践的共识来看，Skill 的本质可以归纳成一句话：

> **按需加载（progressive disclosure）的能力包。**

它至少包含：
- `name` / `description`：元信息，平时常驻，负责被发现
- `SKILL.md`：主工作流，触发后加载，负责指挥
- `references/`：大知识块，按需再读，负责补充
- `scripts/`：确定性动作，负责稳定执行
- `assets/`：模板与脚手架，负责提高最终产物质量

这意味着 Skill 的价值，不是“写了多少字”，而是：

> **是否能用更低的上下文成本，换来更高的任务稳定性、可复用性与组织效率。**

也就是说，Skill 的目标不是“多”，而是：
- 更容易被召回
- 更容易被正确使用
- 更不容易漂移
- 更容易维护
- 更容易被共享与治理

---

## 3）为什么 Skill 是大规模 Agent 的“能力组织单位”
Skill 之所以重要，不是因为它优雅，而是因为它解决了“能力如何组织”的问题。

### 3.1 元信息可召回
Skill 的 `description` 是能力发现层。
它决定模型是否能在成百上千个可能性里找到这个能力。

### 3.2 正文可指挥
`SKILL.md` 是主工作流层。
它决定模型被召回之后，是不是能沿着对的路径走。

### 3.3 资源可按需展开
`references/` 与 `assets/` 是资源层。
它决定模型在需要细节时，能不能拿到对的资料，而不是把所有资料都背在身上。

### 3.4 动作可锁死
`scripts/` 是确定性执行层。
它解决的是“模型判断没问题，但一到执行细节就漂”的问题。

所以 Skill 的真正意义，不是“多一个目录”，而是把能力拆成四层：

> **发现 → 指挥 → 资源 → 执行**

这四层一旦建立起来，Skill 就从“提示词片段”升级成“能力容器”。

---

## 4）Skill 与 prompt / Tool / system prompt / Memory 的边界
这四者最容易混，所以必须明确切开。

### 4.1 Skill vs prompt
prompt 更像一次性会话内强调；
Skill 更像可复用的、可按需加载的能力包。

### 4.2 Skill vs Tool
Tool 负责动作接口；
Skill 负责指导何时、如何、以何种流程和资料来使用这些动作。

一句话：
- Tool 是手
- Skill 是手册

### 4.3 Skill vs system prompt
system prompt 承载的是：
- 全局规则
- 安全边界
- 风格要求
- 运行时约束

Skill 承载的是：
- 某一类任务的专门工作流与资源包

一句话：
- system prompt 是宪法
- Skill 是兵法

### 4.4 Skill vs Memory
Memory 承载的是：
- 历史事实
- 持久偏好
- 过去决策与约束

Skill 承载的是：
- 某类任务的打法
- 某类任务的资源组织方式

一句话：
- Memory 是过去沉淀
- Skill 是当前可调用的方法论

如果把这四者混在一起，系统一定会越来越乱。

---

## 5）Skill 的标准结构与职责分工
推荐结构：

```text
skill-name/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

### 5.1 `SKILL.md`：大脑，不是仓库
职责：
- 说明何时使用
- 给出主工作流
- 指向 references
- 指向 scripts
- 规定输出要求
- 写清 negative triggers

它不该承担：
- 大量背景知识全文
- 大段模板正文
- 冗长的人类说明书
- 与动作无关的解释性废话

### 5.2 `references/`：大知识块
适合放：
- API 文档
- schema
- 域规则
- 评分标准
- 结构定义
- 真实案例说明

重点不是“有没有 references”，而是：
- 是否扁平
- 是否可定位
- 是否在 SKILL.md 里明确写了“什么时候读哪个”

### 5.3 `scripts/`：小而专的 deterministic 动作
适合放：
- 高频重复动作
- 临场重写容易出错的动作
- 批量处理
- 格式转换
- 校验器
- 生成器

关键原则：
- 小而专
- 像 tiny CLI
- 不要把 skill 目录写成软件工程大仓库

### 5.4 `assets/`：产物脚手架
适合放：
- 报告模板
- 页面模板
- JSON 模板
- 文档骨架
- HTML/PPT/图片资产

assets 的价值在于：
- 让输出结构更稳定
- 减少模型每次临场生成格式的漂移

---

## 6）SKILL.md 写法：写给 agent，不是写给人
这个原则听起来简单，但大多数 skill 都犯错在这里。

### 6.1 三个基本原则
1. **像 SOP，不像散文**
2. **像路由表，不像百科**
3. **像指挥单，不像培训教材**

### 6.2 好的 SKILL.md 常见特征
- 编号步骤
- 明确条件分支
- 文件索引清楚
- 何时读哪个 reference 写得明白
- 何时跑哪个 script 写得明白
- 输出合同（output contract）清楚
- negative triggers 清楚

### 6.3 坏的 SKILL.md 常见特征
- 写一大堆“概念解释”
- 没有真正的步骤结构
- references 放了，但正文没写怎么用
- scripts 放了，但正文没写何时调用
- 输出格式完全不规定

所以 SKILL.md 的核心不是“写得像文章”，而是：

> **写得像战术板。**

---

## 7）description 的“召回工程”：如何写出高召回、低误触发
触发前模型最稳定看到的只有：
- `name`
- `description`

所以 description 不是文案，它是路由规则。

### 7.1 description 至少要写四类信息
1. **任务类型**：到底处理哪一类请求
2. **典型触发表达**：用户可能怎么说
3. **适用边界**：哪些任务该用
4. **不适用边界**：哪些任务不要乱用

### 7.2 一个高质量 description 示例
```md
description: 当用户要求写公众号文章、把长文改成微信生态风格、降低AI味、优化标题与导语、输出可直接发布的结构化内容时使用。适用于“公众号”“微信长文”“公号改写”“去AI味重写”等表达。不用于法律文书、短视频口播稿、纯代码任务。
```

### 7.3 一个糟糕 description 示例
```md
description: 写作相关
```

问题在于：
- 不可发现
- 不可区分
- 没有边界
- 会导致低召回和高误触发并存

description 写得好不好，是 Skill 成败第一关。

---

## 8）description 进阶：典型触发词、负触发词、近义表达、业务边界
如果想把 description 做到真正稳定，不够只写一句“当用户要 XX 时使用”。

还要进一步考虑四层：

### 8.1 典型触发词
用户会怎么说？
- “写公众号”
- “改成公号风格”
- “做个会议纪要”
- “给我个日报模板”

### 8.2 近义表达
用户不会永远说你设想的标准句式。
要提前吸纳近义表达和真实语言。

### 8.3 负触发词
哪些词出现时，应该提醒模型：别乱触发。
例如公众号写作 skill：
- 不用于“合同”
- 不用于“短视频口播稿”
- 不用于“代码修复”

### 8.4 业务边界
同样是“写作”，但：
- 公众号长文
- 短视频脚本
- 法律条款
- PRD
其实是完全不同的任务世界。

description 的高级写法，本质上是在做：

> **召回工程（recall engineering）**

---

## 9）Progressive Disclosure：薄 SKILL.md + 厚 references
这是 Skill Engineering 的灵魂。

### 9.1 为什么必须做 progressive disclosure
因为 context window 是公共资源。
如果每个 skill 都把所有知识塞进 `SKILL.md`：
- 一旦触发，立刻把上下文打爆
- 模型很难抓重点
- 维护会变得极其痛苦

### 9.2 正确做法
- `SKILL.md` 保持薄
- references 存放大知识块
- scripts 承担稳定动作
- assets 提供产物模板

### 9.3 SKILL.md 应该保留什么
- 主工作流
- 决策树
- 文件索引
- 关键约束
- 输出要求

### 9.4 什么应该外移到 references
- 详细 schema
- 领域术语说明
- 真实案例长文
- API 参数文档
- 公司制度全文

一句话：

> **SKILL.md 负责导航，references 负责承重。**

---

## 10）references / scripts / assets 的组织法
这部分是很多教程一笔带过，但实战里极其关键。

### 10.1 references 的组织法
目标：
- 文件扁平
- 命名清楚
- 一眼能猜到用途

推荐：
```text
references/
├── style.md
├── schema.md
├── api.md
├── review-rubric.md
└── brand-voice.md
```

不推荐：
```text
references/
└── docs/
    └── internal/
        └── style/
            └── final-v2-latest.md
```

因为层级越深：
- 越难引用
- 越难维护
- 越容易迷路

### 10.2 scripts 的组织法
目标：
- 一个脚本做一件事
- 名字即用途
- 输入输出边界清晰

推荐：
```text
scripts/
├── clean_ai_tone.py
├── export_csv.py
├── validate_report.py
└── make_outline.sh
```

不推荐：
- 写一个几千行的“万能脚本库”塞在 skill 里

### 10.3 assets 的组织法
目标：
- 用于最终产物
- 不一定要读进上下文
- 更像脚手架

推荐：
```text
assets/
├── report-template.md
├── article-template.md
├── prototype.html
└── summary-schema.json
```

### 10.4 三者之间的关系
- references 负责知识
- scripts 负责动作
- assets 负责产物

这是 Skill 设计里最经典也最稳的一套职责分离。

---

## 11）四层自由度：什么时候给模型发挥，什么时候用脚本锁死
Claude 官方 best practices 给了一个极有价值的框架：
**Set appropriate degrees of freedom**。

这直接可以变成 Skill 设计方法论。

### 11.1 高自由：文本规则
适合：
- 任务开放性高
- 路径不唯一
- 需要分析与判断

例如：
- 品牌叙事
- 商业策略拆解
- 竞争对手研究

### 11.2 中自由：模板 / 伪代码 / 半结构化步骤
适合：
- 有主路径
- 有少量变化
- 结构重要于措辞

例如：
- 会议纪要
- SEO 审计
- 周报生成

### 11.3 低自由：严格步骤
适合：
- 易错
- 有强顺序依赖
- 一旦错就要返工

例如：
- 表单处理
- 审批流
- 归档流程

### 11.4 固定脚本：variation = bug
适合：
- 稳定性远高于灵活性
- 高频重复
- 只要自由发挥就会出事

例如：
- CSV 清洗
- JSON 转表格
- 批量校验

真正成熟的 Skill 不是一味让模型自由，也不是一味把一切写死。
而是：

> **自由度放在最值得发挥判断力的地方，其他地方尽量程序化。**

---

## 12）Skill 的负触发（negative triggers）与边界写法
negative triggers 是 Skill 设计里的刹车系统。

很多 skill 写得最大的问题不是“不强”，而是“太泛”。
泛意味着：
- 容易误触发
- 容易与其他 skill 冲突
- 容易让模型多读无关内容

### 12.1 negative triggers 应该写什么
- 不适用任务类型
- 不适用平台/输出形式
- 不适用输入性质
- 与近邻 skill 的分工边界

### 12.2 例子
对于 `wechat-article-pro`：
- 不用于法律文书
- 不用于短视频口播稿
- 不用于 PRD / 技术文档

对于 `meeting-minutes-pro`：
- 不用于日报
- 不用于合同摘要
- 不用于社交媒体贴文

negative triggers 的价值是：

> **防止 Skill 乱抢活。**

---

## 13）从 1 个 Skill 到 Skill Library：分类、命名、冲突与覆盖
当 Skill 数量到 10 个以内，很多问题还不明显。
超过 20、50 之后，最先出问题的不是内容，而是组织。

### 13.1 分类
建议至少分成四类：
- 通用基础
- 角色专属
- 业务线
- 组织治理

### 13.2 命名
命名建议：
- 动作 + 场景
- 短而清楚
- 避免口号化
- 避免两个 skill 名称语义过近

例如：
- `wechat-article-pro`
- `task-card-enforcer`
- `geo-audit`
- `contract-risk-review`

### 13.3 冲突
常见冲突方式：
- 两个 skill 都覆盖“写作”
- 两个 skill 都处理“分析”
- 一个 skill 太泛，把很多别的 skill 都吸进来

### 13.4 覆盖
OpenClaw 的优先级机制（workspace > global > bundled）其实天然支持治理：
- 项目内可以覆盖全局 skill
- 全局可以覆盖 bundled

这对迭代非常有用。

---

## 14）OpenClaw 的 Skill 管理：位置、优先级、extraDirs、门控、配置
这是 OpenClaw 官方机制里非常值钱的一层。

### 14.1 三层位置
- bundled skills
- `~/.openclaw/skills`
- `<workspace>/skills`

### 14.2 优先级
workspace > global > bundled。

### 14.3 extraDirs
通过 `skills.load.extraDirs` 引入共享 skill 仓库。
这非常适合：
- 团队技能仓库
- Git 化管理
- 多 workspace 共享

### 14.4 门控（gating）
通过 `metadata.openclaw.requires` 等机制做：
- OS 限定
- bin 限定
- env 限定
- config 限定

这意味着一个 skill 可以做到：
- 没装依赖 → 不暴露
- 没有 API key → 不暴露
- 环境不满足 → 不暴露

这比“假可用”强太多。

### 14.5 entries 配置
`skills.entries.*` 支持：
- enabled
- env
- apiKey
- config

也就是说 skill 可以被当成一个“可配置能力单元”，而不是纯静态文本。

### 14.6 官方 CLI
- `openclaw skills list`
- `openclaw skills info <name>`
- `openclaw skills check`

这是最基础的 Skill 运维入口。

---

## 15）Skill Registry：为什么要有技能台账，而不是靠目录裸奔
当 skill 变多，如果没有 registry，你一定会遇到：
- 不知道谁在维护
- 不知道最近改了什么
- 不知道它服务哪个 agent / 业务线
- 不知道它是否还在被用
- 不知道它已经到了什么成熟度

所以必须有一张 Skill 台账。

### 15.1 Registry 至少应包含的字段
- skill_name
- owner
- layer（通用/角色/业务/治理）
- location
- status（active / deprecated / experimental）
- trigger_summary
- negative_triggers
- required_bins/env
- last_reviewed_at
- maturity_level
- sample_tasks
- notes

### 15.2 Registry 的价值
它把“目录存在”升级成“能力被治理”。

### 15.3 没有 Registry 的后果
- skill 越来越多但没人敢删
- 重复 skill 到处长
- 触发冲突越来越严重
- 责任无法追溯

一句话：

> **Registry 是 Skill 从个人玩具走向组织资产的第一步。**

---

## 16）Skill Review：为什么 Skill 也必须过审
Skill 不是“写出来就上”，而应该有 review 机制。

### 16.1 为什么要 review
因为一个 skill 的问题，常常不是“文采差”，而是：
- 路由差
- 边界不清
- 容易误触发
- 依赖不完整
- 输出合同不清
- 安全风险未处理

### 16.2 Skill Review 至少看什么
1. description 是否清晰
2. 是否有 negative triggers
3. 是否做了 progressive disclosure
4. references 是否扁平
5. scripts 是否小而专
6. 输出要求是否清楚
7. 是否有测试样例
8. 是否与现有 skill 冲突
9. 是否需要门控
10. 是否有 owner

### 16.3 Skill Review 的本质
不是“挑错字”，而是：

> **防止低质量能力包污染整个技能生态。**

---

## 17）Skill Evaluation：如何测试召回、误触发、结果质量
Skill 只写不测，迟早失真。

Anthropic 工具工程最重要的思想之一，就是：
- 必须 evaluation
- 必须 transcript 回放
- 必须 held-out 验证

把这套思路迁移到 Skill，非常有价值。

### 17.1 Skill Evaluation 三类测试
#### A. 召回测试
该触发时是否能触发。

#### B. 误触发测试
不该触发时是否会乱触发。

#### C. 结果质量测试
触发后产物是否更稳、更像样、更少返工。

### 17.2 实用做法
你可以为每个关键 skill 写一个最小测试集：
- 10 条该触发样例
- 10 条不该触发样例
- 5 条边界样例

### 17.3 transcript 回放
真实 transcript 是最有价值的材料。
观察：
- 为什么没触发
- 为什么误触发
- 触发了为什么结果差
- 是 description 问题？还是 SKILL.md 路径问题？还是 references 不清？

### 17.4 held-out 思维
不要只拿你写 skill 时想象的样例测。
最好保留一组“未参与设计”的样例做 held-out 测试，防止自嗨。

---

## 18）Skill Ops：版本、回放、发布、淘汰、审计
Skill 一旦多起来，它就不再只是作者问题，而是运营问题。

### 18.1 版本
- skill 纳入 Git
- 重要 skill 改动有 review
- 每次大改说明为什么改

### 18.2 回放
- 定期检查 transcript
- 看召回与误触发
- 看结果是否真的提升

### 18.3 发布
最好分层发布：
- experimental
- stable
- deprecated

不要写完就全量铺开。

### 18.4 淘汰
长期：
- 不触发
- 误触发
- 价值被别的 skill 吸收
- 维护成本高于收益

那就该删。

### 18.5 审计
高风险 skill 必须审计：
- 是否需要 exec
- 是否依赖 secret
- 是否可能错误外发
- 是否会扩大 prompt injection 面
- 是否越权

Skill Ops 的本质，就是：

> **让能力库长期保持健康，而不是越积越脏。**

---

## 19）为什么“写了很多 Skill 还是不强”
这件事在很多团队里非常普遍。

常见原因有七个：
1. description 太泛，召回差
2. SKILL.md 太厚，触发后上下文炸了
3. references 放了，但没写读取路径
4. scripts 该有却没有，导致执行漂移
5. negative triggers 缺失，误触发高
6. 没有 evaluation，完全凭感觉
7. 没有 lifecycle，旧 skill 永远不退场

所以问题通常不在“模型不够聪明”，而在：

> **Skill 体系没有被运营。**

---

## 20）面向军团的 Skill Platform 架构
如果你是单 agent hobby 项目，skill 可能只是辅助功能。
但对 OPEN CAIO 这种军团体系，skill 应该上升为平台层。

### 20.1 平台层至少要回答的问题
- 谁能写 skill？
- skill 放哪？
- 谁负责 review？
- 谁维护 registry？
- 谁决定上线、下线、灰度？
- 谁负责高风险 skill 审计？
- 谁负责 transcript 回放与优化？

### 20.2 平台需要的最小设施
- 共享 skill 仓库
- skill registry 台账
- review 规则
- evaluation 样例库
- 生命周期状态
- owner 机制

### 20.3 平台化的价值
把“某个 agent 很会”升级成“军团可复用的能力”。

---

## 21）适合 OPEN CAIO 的 Skill 分层体系
建议至少四层：

### 21.1 通用基础层
- research
- summarize
- report-writing
- meeting-minutes
- file-organizer

### 21.2 角色专属层
- 昆仑：战略拆解、晨会控场、资源裁决
- 明镜：合同审计、风控、红队
- 天枢：任务卡、巡检、升级
- 轩辕：开发、部署、修复
- 凤凰：公众号、内容改写、品牌叙事
- 烛龙：回测、信号、交易日志

### 21.3 业务线层
- GEO
- 私有脑
- 数字员工
- 城市合伙人
- 自媒体矩阵
- AI 电商

### 21.4 组织治理层
这一层极其关键：
- OKR
- 日报
- 晨会纪要
- 信誉分
- 整改单
- 验收清单
- 升级与熔断机制

如果治理层不做，业务层做得越多，系统越容易失控。

---

## 22）Skill 成熟度模型 L0-L5
### L0：口头能力
只有某个 agent / 某个人“比较会”，没有显式沉淀。

### L1：说明型 Skill
有 `SKILL.md`，但还只是说明书。

### L2：可用型 Skill
有清晰 description、主工作流、基本 references、输出要求。

### L3：工程型 Skill
进一步具备：
- scripts
- assets
- negative triggers
- 门控
- 基础测试

### L4：运营型 Skill
进一步具备：
- registry
- review
- evaluation
- transcript 回放
- lifecycle 管理

### L5：平台型 Skill
进一步具备：
- 多 agent 共享
- 灰度与发布策略
- 安全审计
- 组织级 owner 机制
- 能力平台化治理

很多团队看似有很多 skill，其实大部分停在 L1/L2。

---

## 23）标杆案例：从普通 Skill 到平台级 Skill 的分水岭
### 23.1 普通 Skill
- 有目录
- 有 SKILL.md
- 大致能用

### 23.2 工程型 Skill
- references / scripts / assets 分层清晰
- 输出更稳定
- 误触发更少

### 23.3 平台级 Skill
- 有 registry
- 有 owner
- 有 review
- 有 evaluation
- 有 lifecycle
- 能多 agent 共享

分水岭不在于“写得多不多”，而在于：

> **有没有从写作逻辑切换到运营逻辑。**

---

## 24）Skill Engineering 训练模板 / 检查清单 / 验收口径
### 24.1 写 Skill 前 12 问
1. 这个任务是否高频？
2. 是否存在稳定 SOP？
3. 是否需要 references？
4. 是否需要 scripts？
5. 是否需要 assets？
6. 典型触发词是什么？
7. negative triggers 是什么？
8. 它归属哪一层（通用/角色/业务/治理）？
9. owner 是谁？
10. 怎么测试召回？
11. 怎么测试误触发？
12. 何时下线或升级？

### 24.2 合格 Skill 18 项检查清单
- [ ] name 清晰
- [ ] description 高召回
- [ ] 有近义触发词意识
- [ ] 有 negative triggers
- [ ] SKILL.md 是 SOP 不是散文
- [ ] 明确 references 读取时机
- [ ] 明确 scripts 调用时机
- [ ] 输出合同清晰
- [ ] references 扁平
- [ ] scripts 小而专
- [ ] assets 与说明分离
- [ ] 有 owner
- [ ] 有 layer 分类
- [ ] 可被 registry 管理
- [ ] 至少一次 transcript 回放
- [ ] 有召回测试
- [ ] 有误触发测试
- [ ] 有生命周期状态

### 24.3 本章真正的验收标准
学完这章，不是你能创建一个 `SKILL.md` 文件，而是你能清楚回答：
1. Skill 为什么是能力组织单位？
2. 为什么 description 是召回工程？
3. 为什么 progressive disclosure 必须做？
4. 为什么没有 registry / review / evaluation，skill 体系迟早会烂？
5. Skill 怎么从个人技巧升级成军团平台能力？

如果这五个问题答不清，这章就还没真正吃透。

---

## 25）本章一句话结论
> **Skill 不是写出来就结束；Skill 必须被发现、被触发、被验证、被治理、被运营，只有这样，它才配叫“系统能力资产”。**
