# 📖 硅基生命手册 Silicon Life Handbook

> 一套系统化的 AI Agent 训练方法论 — 从单体到军团，从配置到治理。

## 这本书讲什么

本手册探讨如何将 AI Agent（"硅基生命"）从简单的聊天工具，训练成长期稳定、可协作、可治理的硅基团队成员。内容基于 [OpenClaw](https://github.com/openclaw/openclaw) 框架实践，但方法论适用于任何 AI Agent 系统。

**核心理念**：Agent 不是 prompt，是生命体。它的长期表现由文档体系、训练流程、治理制度共同决定。

## 全书结构

| 卷 | 主题 | 核心问题 | 篇数 |
|:--:|------|---------|:----:|
| **卷一** | 为什么训虾 | 为什么要系统化训练 AI Agent | — |
| **卷二** | 生命协议 | SOUL/USER/AGENTS/MEMORY 等七大文档怎么写、为什么这么写 | 8 |
| **卷三** | 系统骨架 | Runtime、Session、Workspace、Skills、Multi-Agent 底层机制 | 12 |
| **卷四** | 训练流程 | 从零训到专家的完整阶梯、教练虾机制、双三角模型 | 8 |
| **卷五** | 长期表现 | 记忆管理、心跳策略、会话污染、文档漂移、稳定性检查 | 8 |
| **卷六** | 治理系统 | 任务卡、验收口径 — 防止军团失真、甩锅、造假 | 3 |
| **卷七** | 军团协同 | 路由系统、Handoff 协议、让位协议、治理账本、信任体系 | 10 |

**总计**：52 篇，21,000+ 行

## 目录导航

### 卷二：生命协议
- [总引言 — 七大核心文档](openclaw-silicon-life-handbook/volume-02/卷二-生命协议-总引言与USER文档.md)
- [SOUL 文档 — 人格边界与元灵魂协议](openclaw-silicon-life-handbook/volume-02/第2章-SOUL文档-人格边界与元灵魂协议.md)
- [AGENTS 文档 — 操作纪律与治理协议](openclaw-silicon-life-handbook/volume-02/第3章-AGENTS文档-操作纪律与治理协议.md)
- [TOOLS 文档 — 工具边界与环境适配](openclaw-silicon-life-handbook/volume-02/第4章-TOOLS文档-工具边界环境适配与工作习惯协议.md)
- [HEARTBEAT 文档 — 主动性节律与熔断边界](openclaw-silicon-life-handbook/volume-02/第5章-HEARTBEAT文档-主动性节律周期检查与熔断边界.md)
- [IDENTITY 文档 — 身份锚点与协同接口](openclaw-silicon-life-handbook/volume-02/第6章-IDENTITY文档-身份锚点识别系统与协同接口.md)
- [MEMORY 体系 — 长期记忆如何塑造硅基生命](openclaw-silicon-life-handbook/volume-02/第7章-MEMORY体系-长期记忆如何塑造硅基生命.md)
- [总复盘 — 七大生命协议如何共同塑造硅基生命](openclaw-silicon-life-handbook/volume-02/卷二总复盘-七大生命协议如何共同塑造硅基生命.md)

### 卷三：系统骨架
- [总纲与模块导航](openclaw-silicon-life-handbook/volume-03/卷三-系统骨架-总纲与模块导航.md)
- [模块1 — Agent Runtime](openclaw-silicon-life-handbook/volume-03/模块1-Agent-Runtime-为什么Agent不是一个prompt而是独立运行单元.md)
- [模块2 — Agent Workspace](openclaw-silicon-life-handbook/volume-03/模块2-Agent-Workspace-为什么工作区不是文件夹而是生命容器.md)
- [模块3 — Session Context Queue](openclaw-silicon-life-handbook/volume-03/模块3-Session-Context-Queue-长会话为什么会污染与如何治理.md)
- [模块4 — Routing & Bindings](openclaw-silicon-life-handbook/volume-03/模块4-Routing-Bindings-为什么谁该答是系统路由问题.md)
- [模块5 — Tools & Skills](openclaw-silicon-life-handbook/volume-03/模块5-Tools-Skills-工具不是智能Skill不是prompt.md)
- [模块5上 — Tool Engineering](openclaw-silicon-life-handbook/volume-03/模块5上-Tool-Engineering-为什么工具设计决定Agent上限.md)
- [模块5下 — Skill Engineering & Ops](openclaw-silicon-life-handbook/volume-03/模块5下-Skill-Engineering-and-Skill-Ops-从写法到治理.md)
- [模块6 — Heartbeat/Cron/Compaction](openclaw-silicon-life-handbook/volume-03/模块6-Heartbeat-Cron-Compaction-为什么主动性离不开节律记忆与压缩.md)
- [模块7 — 多 Agent 协同基础](openclaw-silicon-life-handbook/volume-03/模块7-多Agent-协同基础-为什么军团不是多开几个bot而是组织系统.md)
- [OpenClaw 官方文档深度解剖](openclaw-silicon-life-handbook/volume-03/卷三-系统骨架-OpenClaw官方文档深度解剖.md)
- [总复盘 — 从 Runtime 到军团协同](openclaw-silicon-life-handbook/volume-03/卷三总结-从Runtime到军团协同的系统骨架总图.md)

### 卷四：训练流程
- [总引言 — 从普通龙虾到专业专家](openclaw-silicon-life-handbook/volume-04/卷四总引言-训练流程-从一只普通龙虾到专业专家.md)
- [模块1 — 进化阶梯](openclaw-silicon-life-handbook/volume-04/模块1-从入门到业内最佳实践的进化阶梯.md)
- [模块2 — 训练前准备清单](openclaw-silicon-life-handbook/volume-04/模块2-训练前的准备清单.md)
- [模块3 — 教练虾机制](openclaw-silicon-life-handbook/volume-04/模块3-教练虾机制.md)
- [模块4 — 训练轮次设计](openclaw-silicon-life-handbook/volume-04/模块4-训练轮次设计.md)
- [模块5 — 双三角模型](openclaw-silicon-life-handbook/volume-04/模块5-双三角模型.md)
- [模块6 — 实验方案设计](openclaw-silicon-life-handbook/volume-04/模块6-实验方案设计.md)
- [模块7 — 新人到专家完整路径](openclaw-silicon-life-handbook/volume-04/模块7-从新人虾到专家虾的完整路径.md)
- [总复盘 — 完整训练体系](openclaw-silicon-life-handbook/volume-04/卷四总复盘-从会聊到能战的完整训练体系.md)

### 卷五：长期表现
- [总引言 — 越跑越稳还是越跑越差](openclaw-silicon-life-handbook/volume-05/卷五总引言-长期表现-越跑越稳还是越跑越差.md)
- [模块1 — 记忆管理](openclaw-silicon-life-handbook/volume-05/模块1-记忆管理-为什么agent会忘记你是谁.md)
- [模块2 — 心跳接入策略](openclaw-silicon-life-handbook/volume-05/模块2-心跳接入策略-主动性不是自然有而是必须设计.md)
- [模块3 — 会话污染与清理](openclaw-silicon-life-handbook/volume-05/模块3-会话污染与清理-为什么agent会越说越乱.md)
- [模块4 — 文档漂移与人格漂移](openclaw-silicon-life-handbook/volume-05/模块4-文档漂移与人格漂移-为什么agent会不认识自己.md)
- [模块5 — 主动性边界](openclaw-silicon-life-handbook/volume-05/模块5-主动性边界-越主动不等于越好.md)
- [模块6 — 长期稳定性检查清单](openclaw-silicon-life-handbook/volume-05/模块6-长期稳定性检查清单-如何每周给agent做体检.md)
- [总复盘 — 系统闭环与维护总纲](openclaw-silicon-life-handbook/volume-05/卷五总复盘-长期表现系统闭环与维护总纲.md)

### 卷六：治理系统
- [总引言 — 如何防止军团失真](openclaw-silicon-life-handbook/volume-06/卷六总引言-治理系统-如何防止军团失真.md)
- [模块1 — 任务卡制度](openclaw-silicon-life-handbook/volume-06/模块1-任务卡-没有任务卡就没有接单.md)
- [模块2 — 验收口径](openclaw-silicon-life-handbook/volume-06/模块2-验收口径-没有验收口径就没有完成.md)

### 卷七：军团协同
- [总引言 — 从单体到组织的跃迁](openclaw-silicon-life-handbook/volume-07/卷五总引言-军团协同-从单体到组织的跃迁.md)
- [模块1 — 路由系统](openclaw-silicon-life-handbook/volume-07/模块1-路由系统-谁该答的第一道闸门.md)
- [模块2 — Handoff 协议](openclaw-silicon-life-handbook/volume-07/模块2-Handoff协议-交接棒比谁跑得快更重要.md)
- [模块3 — 让位协议](openclaw-silicon-life-handbook/volume-07/模块3-让位协议-不抢答比能回答更重要.md)
- [模块4 — 治理账本](openclaw-silicon-life-handbook/volume-07/模块4-治理账本-没有账本就没有真正的治理.md)
- [模块5 — 信任体系](openclaw-silicon-life-handbook/volume-07/模块5-信任体系-相信它比它会做更重要.md)
- [模块6 — 军团原型](openclaw-silicon-life-handbook/volume-07/模块6-军团原型-最小军团设计模板.md)
- [模块7 — 军团进化](openclaw-silicon-life-handbook/volume-07/模块7-军团进化-建完只是开始.md)
- [总复盘 — 从单体到组织](openclaw-silicon-life-handbook/volume-07/卷五总复盘-从单体到组织的跃迁.md)

## 附件资源

### 卷三 — Skill 工程模板
- [Skill Review Checklist](openclaw-silicon-life-handbook/volume-03/模块5-附件/Skill-Review-Checklist.md)
- [Skill Registry Template](openclaw-silicon-life-handbook/volume-03/模块5-附件/Skill-Registry-Template.md)
- [Skill Evaluation Testset Template](openclaw-silicon-life-handbook/volume-03/模块5-附件/Skill-Evaluation-Testset-Template.md)

## 核心概念速查

| 概念 | 一句话解释 |
|------|-----------|
| **硅基生命** | AI Agent 不是工具，是有身份/记忆/职责/成长路径的生命体 |
| **生命协议** | 7 个核心文件（SOUL/USER/AGENTS/TOOLS/IDENTITY/HEARTBEAT/MEMORY）构成的 Agent 人格系统 |
| **任务卡** | 每次接活前必须确认的 5 要素：目标/范围/格式/验收/截止 |
| **验收口径** | 没有验收口径就没有完成 — 做完 ≠ 做好 |
| **让位协议** | 不抢答比能回答更重要 — 群聊中按职责路由响应 |
| **Handoff 协议** | 任务交接必须包含：已完成/未完成/阻塞项/下一步 |
| **治理账本** | 每个 Agent 的表现可追溯、可审计、可复盘 |
| **信任等级** | 🔴 新人 → 🟡 成员 → 🟢 核心，影响权限和任务分配 |
| **双三角模型** | 训练中的期望-实际-反馈闭环 |
| **文档漂移** | Agent 的核心文档随时间偏离原始设计，需定期校准 |

## 适合谁读

- 🔧 **AI Agent 开发者** — 想让 Agent 长期稳定运行，不只是 demo
- 🏢 **AI 团队管理者** — 想建多 Agent 军团，不是多开几个 bot
- 🧠 **AI 训练师** — 想系统化训练方法论，不是反复堆 prompt
- 📚 **AI 爱好者** — 想理解 AI Agent 的底层逻辑和长期治理

## 快速开始

1. 从 **卷二总引言** 开始，理解为什么需要"生命协议"
2. 按 **卷四训练流程** 实操，用任务卡+验收口径训练你的第一个 Agent
3. 用 **卷五长期稳定性检查清单** 做每周体检
4. 多 Agent 时参考 **卷七军团协同** 的路由和让位协议

## License

MIT

---

*如果你觉得这本手册有价值，欢迎 ⭐ Star 和分享。*
