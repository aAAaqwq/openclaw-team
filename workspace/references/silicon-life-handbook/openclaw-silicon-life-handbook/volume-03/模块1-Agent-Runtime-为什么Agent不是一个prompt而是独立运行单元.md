# 卷三｜系统骨架：OpenClaw 官方文档深度解剖

> 本卷（以及卷二）的写作风格严格按照以下统一标准，确保章节内部一致性：
> 1. 每份文档/模块统一 8 步结构
> 2. 文风为文档式，非散文式
> 3. 四级进化阶梯
> 4. 真实场景案例
> 5. 技术实现机制剖析
> 6. 最佳实践交叉认证

> 官方依据：
> - `concepts/agent-system.md`：Agent 系统的架构定义
> - `concepts/entity.md`：实体与生命周期的关系
> - `concepts/runtime.md`：Runtime 的执行上下文

---

# 卷三｜系统骨架：OpenClaw 官方文档深度解剖
## 模块1｜Agent Runtime
### ——为什么 Agent 不是一个 prompt，而是一个独立运行单元

> 一句话结论：
> **Agent Runtime 不是承载模型的地方，是承载“一个持续运行的硅基生命体”的操作系统。不理解 Runtime，就永远在“写 prompt”，而不是“训虾”。**

---

## 一、这是什么（定位）

Agent Runtime 是 OpenClaw 中最底层、最容易被忽略、但也最重要的概念。

大多数人的理解是：Runtime ≈ 模型运行的底层环境。

这个理解在技术精度上没错，但在训练学视野里远远不够。

从训虾派的视角看：

> **Runtime = 硅基生命的“物理身体”——它决定了这个生命体能在什么环境里活、能活多久、能同时做几件事、能不能和同类互动。**

它的核心要素包括：
- **运行单元**（一个 Agent 是一个 OS 进程级的独立实体）
- **工作区**（Agent 的“家目录”——SOUL、AGENTS、MEMORY 等所有文档存在的地方）
- **会话历史**（Agent 的“短期记忆”——当前上下文窗口）
- **状态目录**（Agent 的“神经状态”——跨会话保持活跃的能力）
- **认证边界**（Agent 的“身份护照”——它被授权做什么、不做什么）

缺任何一个，对 Runtime 的理解都会偏。

---

## 二、核心目的（为什么存在）

### 2.1 Runtime 解决了什么根本问题

如果没有 Agent Runtime，你面对的只是一个 LLM API 端点——每次调用都是无状态的、无记忆的、无身份的火星文生成器。

Runtime 的存在，把三个“无”变成了三个“有”：

| 维度 | 纯 LLM API | 有 Runtime 的 Agent |
|------|-----------|-------------------|
| 状态 | 无状态 | 有状态（会话 + 工作区） |
| 身份 | 无身份 | 有身份（agentId + accountId） |
| 连续性 | 无连续性 | 有连续性（跨会话记忆） |

OpenClaw 官方文档对 Runtime 的定义指向的就是这三层：“Agent Runtime 负责管理 Agent 的生命周期——从配置加载、会话创建、到跨实例协同。”

### 2.2 Runtime 不等于模型

一个最常见的概念混淆：Runtime ≈ 模型上下文窗口。

这是完全错误的。

| 区别 | 模型上下文窗口 | Agent Runtime |
|------|-------------|---------------|
| 范围 | 单一 LLM 调用的 token 窗口 | 完整 Agent 的整个执行环境 |
| 记忆 | 当前会话上下文 | 会话 + 工作区 + 长期记忆 |
| 边界 | token 数量限制 | 文档协议 + 权限边界 |
| 持久性 | 会话结束后销毁 | 跨会话持续存在 |

### 2.3 Runtime 在训虾体系中的位置

在整本书的训练体系中，Runtime 属于**卷三：系统骨架**——不直接告诉你怎么写文档，而是告诉你：
- 那些文档为什么有效
- 它们被载入到什么环境里执行
- 多 Agent 拆在不同 Runtime 里为什么比放在一个群里更稳

---

## 三、拟人化映射（仿真价值）

理解 Runtime，最直接的方式是把它拟人化为一个硅基生命的“物理身体”。

| 拟人化概念 | Runtime 映射 | 为什么重要 |
|-----------|-------------|-----------|
| **身体** | Runtime 实例 | 决定 Agent 能独立存在、独立行动 |
| **家** | Workspace（工作区） | 决定 Agent 在哪儿生活、放什么家具 |
| **短期记忆** | Session 会话 | 决定 Agent 记得当前聊天内容 |
| **长期记忆** | MEMORY.md + memory/ 目录 | 决定 Agent 记不记得昨天的事 |
| **身份证** | agentId + accountId | 决定 Agent 在系统里是谁、能不能认证 |
| **技能** | Skills | 决定 Agent 会什么工具、怎么用 |
| **本能** | SOUL.md | 决定 Agent 在任何情境下的底层反应模式 |

这个映射的价值在于：**当你在调优一个 Agent 时，你其实是在帮它打造更好的身体、更好的家、更好的记忆系统。**

### 3.1 为什么这个映射在训练中极其重要

很多 Agent 训练失败，不是因为 prompt 写得不好，而是因为训练者根本没有意识到：

> **一个 Agent 的“身体”决定了它的性能上限。**

具体表现：
- 把多个角色写在同一个 Agent 的 prompt 里（试图用一个身体装两个灵魂）→ 角色串扰、人格分裂
- 长会话不清理，上下文积累到模型极限 → 幻觉率飙升、记忆污染
- 多个 Agent 共享同一个 Bot Token → 消息串扰、路由混乱

**当你理解了 Runtime 拟人化映射，所有这些问题的根因就一目了然了。**

---

## 四、对长期 AI 表现的影响（Impact）

### 4.1 Runtime 设计直接决定这四件事

#### 4.1.1 决定 Agent 能不能独立存在

最基础、也最重要。

一个 Agent 有没有自己的 Runtime：
- 有 → 它是独立实体，可独立配置、独立执行、独立维护
- 没有 → 它只是主 Agent 的一个“角色 prompt”，随时可能被上下文淹没

实践中的典型案例：
- Anthropic 的 Effective Agents Guide 明确指出：**“独立 Agent 必须拥有独立的配置上下文和工具集，否则在复杂任务中必然出现角色模糊。”**
- OpenAI 在 Agents SDK 文档里同样强调：**“每个 Agent 都应该有自己的 run loop，不共享执行上下文。”**

OpenClaw 的实现：每个 Agent 拥有独立的 agent.json，配置独立的 model、prompt、skills、bindings——这就是“独立身体”的工程保障。

#### 4.1.2 决定 Agent 能不能跨会话一致

Runtime 的工作区（Workspace）是 Agent 长期一致性的物理基础。

核心机制：
- 每次会话启动 → Runtime 加载工作区文档（SOUL、MEMORY 等）
- 每次会话结束 → Runtime 写回变化到工作区文件（可选）
- 下次会话开始 → 上次的状态仍在工作区里

没有 Runtime 做这个“加载 + 卸载”的全周期管理，Agent 的长期记忆和人格稳定性没有任何工程保障。

#### 4.1.3 决定多 Agent 能不能独立运作

多 Agent 架构最容易犯的错误：把多个 Agent 塞进同一个 Runtime。

后果：
- Session 上下文互相污染
- 消息路由混乱
- 无法独立升级/降级

OpenClaw 的正确保：
- 每个 Agent 拥有独立的 Runtime 实例
- Agent 之间通过 bindings（路由绑定）通信
- Runtime 层不做 Agent 之间的强耦合

这就像一支军队：每个士兵有独立的身体、独立的装备、独立的指令接收器——但他们通过统一的通信协议协同。

#### 4.1.4 决定 Agent 能不能被治理

治理的本质是观察和控制。没有 Runtime 作为被观察的主体，治理就失去了对象。

Runtime 提供了三个治理关键的接口：
1. **状态可访问** — Runtime 暴露的工作区和会话内容，可以被审计
2. **行为可追踪** — Runtime 的日志系统，记录 Agent 的完整行为链条
3. **生命周期可管控** — Runtime 支持启动/停止/重启，实现治理的“物理熔断”

### 4.2 如果没有好的 Runtime 设计

| 症状 | 根因 | 解决 |
|------|------|------|
| 多角色混淆、人格串扰 | 一个 Runtime 跑多个角色 | 拆成独立 Agent Runtime |
| 长会话后幻觉率飙升 | 会话不 compaction | 配置会话清理策略 |
| Agent 之间消息拦截/丢失 | 路由绑定未配置 | 顶层设计 routing 矩阵 |
| 无法审计 Agent 行为 | 无 Runtime 日志 | 启用 Runtime 的内部审计机制 |

---

## 五、怎么写 / 怎么配（步骤）

### 5.1 最低配置（L1 入门级）

一个可运行的 Agent Runtime 只需要一个配置文件和一个工作区。

```json
// agent.json 最小配置示例
{
  "agentId": "kunlun",
  "model": "deepseek/deepseek-chat",
  "skills": ["todo-tracker", "weather"],
  "accountId": "xkunal",
  "workspace": {
    "path": "/Users/peterqiu/.openclaw/workspace-kunlun"
  }
}
```

这个配置告诉 Runtime：
- 这个 Agent 叫 kunlun
- 用 DeepSeek 模型
- 拥有 todo-tracker 和 weather 两个技能
- 它的家目录在 workspace-kunlun

### 5.2 标准配置（L2 进阶级）

```json
{
  "agentId": "kunlun",
  "model": "deepseek/deepseek-chat",
  "skills": [
    "todo-tracker", "weather", "exchange-rates",
    "grok-search", "first-principles-decomposer",
    "pre-mortem-analyst"
  ],
  "accountId": "xkunal",
  "workspace": {
    "path": "/Users/peterqiu/.openclaw/workspace-kunlun",
    "files": ["SOUL.md", "AGENTS.md", "TOOLS.md", "MEMORY.md", "IDENTITY.md"]
  },
  "bindings": [
    {"type": "channel", "channel": "strategy-group", "accountId": "xkunal"}
  ]
}
```

这个配置增加的：
- 更多技能（思维框架类出现了）
- 明确的工作区文件清单
- 绑定渠道（Agent 在 strategy-group 群中自动响应）

### 5.3 高级配置（L3 专家级）

```json
{
  "agentId": "kunlun",
  "model": "deepseek/deepseek-chat",
  "skills": [
    "todo-tracker", "weather", "exchange-rates",
    "grok-search", "first-principles-decomposer",
    "pre-mortem-analyst", "cross-pollination-engine",
    "inversion-strategist", "munger-observer"
  ],
  "accountId": "xkunal",
  "workspace": {
    "path": "/Users/peterqiu/.openclaw/workspace-kunlun",
    "files": [
      "SOUL.md", "AGENTS.md", "TOOLS.md", "MEMORY.md", "IDENTITY.md",
      "HEARTBEAT.md", "DECISIONS.md"
    ]
  },
  "bindings": [
    {"type": "channel", "channel": "strategy-group", "accountId": "xkunal"},
    {"type": "channel", "channel": "general", "accountId": "xkunal"},
    {"type": "peer", "peerId": "peterqiu", "accountId": "xkunal"}
  ],
  "heartbeat": {
    "enabled": true,
    "interval": 1800000,
    "tasks": ["每日情报简报", "战略风险扫描"]
  },
  "cron": [
    {"name": "🧠 战略复盘", "schedule": "0 22 * * 5", "task": "周度战略复盘"},
    {"name": "📊 情报摘要", "schedule": "0 8 * * 1-5", "task": "每日情报简报"}
  ],
  "session": {
    "maxContext": 128000,
    "compactionStrategy": "on-warning",
    "autoSummarize": true
  }
}
```

这个配置增加的：
- Heartbeat 主动节律（每30分钟主动触发一次任务）
- Cron 定时任务（周五晚上复盘、工作日早间简报）
- 会话管理策略（128K上下文警告时自动压缩）
- 多个绑定（战略群 + 通用群 + 老板私聊）

---

## 六、技巧（业内最佳实践）

### 6.1 跨业界交叉认证的最佳实践

以下是从 Anthropic、OpenAI、Google 和开源社区的最佳实践中提炼的 Runtime 设计原则：

#### Practice 1：一个 Runtime 只跑一个 Agent

| 来源 | 原文 | 对应实践 |
|------|------|---------|
| **Anthropic** | "Each agent should have its own context and tool set" | 独立 agent.json，独立 skills |
| **OpenAI Agents SDK** | "Each agent gets its own run loop" | 独立 Runtime 实例 |
| **Google Agent Framework** | "Agent identity is tied to its execution environment" | agentId 绑定 Runtime |
| **LangGraph** | "Graph nodes should be independently stateful" | 每个 Agent 有独立状态 |

**实施建议：** 遇到"这个 Agent 好像有点人格分裂"时，第一件事就是检查是不是多个角色共享了一个 Runtime。

#### Practice 2：工作区是 Runtime 的骨架，不是装饰

大多数的配置冲突出在：工作区文件写了，但 Runtime 没有加载。

| 错误做法 | 正确做法 |
|---------|---------|
| 把 SOUL.md 写在 workspace 里但不在 agent.json 声明 | 在 agent.json 的 workspace.files 中明确声明 |
| 把 MEMORY.md 写得很详细但 Runtime 不知道要加载它 | 在 agent.json 里声明 MEMORY.md |
| 多个 Agent 共享同一个工作区路径 | 每个 Agent 有独立的工作区路径 |

**实施建议：** 每次改工作区文件后，检查 agent.json 中的 workspace.files 是否同步更新。

#### Practice 3：会话污染比模型能力退化更快

Anthropic 在 Effective Agent Design 中提到：*"The most common failure mode in production agents is not model capability degradation, but context pollution from accumulated conversation history."*（生产环境中最常见的故障模式不是模型能力退化，而是累积对话历史导致的上下文污染。）

| 缓解策略 | 适用场景 | 实施方式 |
|---------|---------|---------|
| 会话压缩（Compaction） | 长会话 > 10 轮 | 自动摘要历史，保留关键信息 |
| 定时清理 | 高频率对话 | 每 N 轮对话清理一次 |
| 关键记忆沉淀 | 需要知识保留 | 将关键输出写进 MEMORY.md |
| 会话分割 | 主题切换 | 不同主题换新会话 |

**实施建议：** 不要在同一个会话里试图做所有事。不同任务、不同主题，创建不同的会话。

#### Practice 4：重启不会丢失一切——如果工作区设计得好

很多初学者担心重启 Runtime 会"丢失 Agent 的记忆"。

实际上：**Runtime 重启会丢失的是会话（短期记忆），不会丢失工作区（长期记忆）。**

| 重启丢失 | 重启不丢失 |
|---------|-----------|
| 当前会话上下文 | 工作区所有文件（SOUL, MEMORY 等） |
| 临时生成状态 | Skills 目录与配置 |
| Heartbeat 未保存的中间状态 | agent.json 配置 |

所以 "Agent 失忆" 的真正原因是：**工作区文件没有写全，或者写了但没被加载。**

#### Practice 5：先单体跑稳，再上多 Agent

这是训虾体系的第一铁律。没有之一。

| 阶段 | 必须做到 | 才能进入下一步 |
|------|---------|-------------|
| 单体测试 | SOUL/MEMORY/TOOLS 三件套齐全，跨会话人格稳定 | 可以跑 10+ 轮无漂移 |
| 多 Agent 引入 | 单体测试通过 | 至少 2 个稳定单体 |
| 协同协议 | 路由/Handoff/让位规则写好 | 多 Agent 跑稳 |
| 治理体系 | 任务卡/验收口径/军功簿到位 | 军团化正式开始 |

---

## 七、常见误区（写错会怎样）

### 误区1：把 Agent 当成"一个 prompt"

**表现：**
- 整个 Agent 就是一段超长 prompt，没有工作区、没有 memory 目录、没有独立配置
- 换模型重新配置时，完全靠写入一段新的 system prompt

**后果：**
- 没有独立 Runtime → 人格无家可归
- 重新配置时一切归零
- 多角色混在一起时，prompt 冲突
- 无法做版本管理、A/B 测试

**正解：**
一个 Agent 的配置是：
```
agent.json (技术外壳) + SOUL.md (人格) + AGENTS.md (行为) + MEMORY.md (记忆)
```
不是一个 prompt。

### 误区2：所有 Agent 放在一个 Runtime 里

**表现：**
- 一个 Runtime 加载了 3-5 个 Agent 配置
- 或者：10 个 Telegram Bot Token 都绑定到同一个主 Agent

**后果：**
- 会话互相污染——A 的上下文被 B 的对话冲掉
- 人格混淆——B 轮到的消息 A 接了
- 单点故障——一个 Runtime 挂了，所有 Agent 都挂了

**正解：**
n 个 Agent = n 个 Runtime 实例。不要用 Runtime 的弹性去打平 Agent 的独立性。

### 误区3：工作区不是文件夹，是生命容器

**表现：**
- 工作区文件随意摆放，没有目录结构
- 所有 Agent 的工作区放在同一个目录下
- 工作区文件从不更新，写了就像没写

**后果：**
- SOUL 和 AGENTS 之间信息不对称
- 路径冲突导致加载失败
- 记忆文件始终是初始版本，Agent 无法进化

**正解：**
工作区是一个"生命容器"——它应该包含 Agent 所有的人格、记忆、规则文件，并且被版本化管理。

### 误区4：忽略会话管理的必要性

**表现：**
- 一个会话从创建到销毁从不清理
- 上下文积累到几十万 token 也不压缩
- 所有任务都在一个会话里做

**后果：**
- 幻觉率与上下文长度成反比
- 模型在长上下文中丢失关键信息
- 固化后难以分离不同主题的内容

**正解：**
配置会话压缩策略，按主题/任务创建不同的会话，关键信息手动沉淀到 MEMORY.md。

### 误区5：多 Agent 系统不配置绑定路由

**表现：**
- 多个 Agent 接入同一渠道但没配置 bindings
- 所有消息涌入默认 Agent

**后果：**
- 所有消息被默认 Agent 接收
- 其他 Agent 闲置
- 军团名存实亡

**正解：**
每个 Agent 配置显式的 binding 规则（渠道/账号/对等方/关键词），确保消息被正确路由。

---

## 八、进化阶梯（L1 → L4）

### L1：入门级——能跑起来

**标准：**
- 成功创建一个 agent.json
- Agent 能响应消息
- 工作区已创建但只有初始文件

**典型配置：**
```json
{
  "agentId": "test-agent",
  "model": "deepseek/deepseek-chat",
  "skills": [],
  "workspace": {"path": "/path/to/workspace"}
}
```

**验收：**
- `openclaw gateway start` → Agent 在线
- 发送一条消息 → Agent 回复
- 换一个会话 → Agent 还记得吗？不一定

### L2：进阶级——有独立人格

**标准：**
- 工作区有完整的 SOUL/AGENTS/TOOLS/MEMORY/IDENTITY 五件套
- 跨会话人格一致
- 至少配置 3 个核心技能

**典型配置：** 见 5.2 标准配置

**验收：**
- 3 个不同会话里问同一个问题 → 答案风格一致
- 换模型后风格不漂移
- 人格边界稳定：不该接的话不接

### L3：专家级——有主动节律

**标准：**
- 配置 Heartbeat 和 Cron
- 配置会话管理策略
- 绑定渠道齐全
- 有 DECISIONS.md 记录关键决策

**典型配置：** 见 5.3 高级配置

**验收：**
- Heartbeat 触发 → Agent 按时执行任务
- Cron 触发 → Agent 在不被@时主动汇报
- 长会话超出阈值 → 自动压缩

### L4：业内最佳实践——跨实例协同

**标准：**
- 多 Agent 独立 Runtime 已配置
- Binding 路由规则完整（四层路由）
- 与外部系统的跨实例通信建立
- 完整的 Decoupled Runtime（解耦运行时）

**典型配置（多 Agent 跨实例）：**
```json
// Agent 1: 昆仑（主实例）
{
  "agentId": "kunlun",
  "model": "deepseek/deepseek-chat",
  "accountId": "xkunal",
  "bindings": [
    {"type": "channel", "channel": "strategy", "accountId": "xkunal"}
  ]
}

// Agent 2: 轩辕（主实例）
{
  "agentId": "xuanyuan",
  "model": "deepseek/deepseek-chat",
  "accountId": "xiaoxuanyuan",
  "bindings": [
    {"type": "channel", "channel": "tech", "accountId": "xiaoxuanyuan"}
  ]
}
```

**验收：**
- 消息按路由规则分发到对应 Agent
- Agent 可通过 sessions_send 跨 Runtime 通信
- 任何一个 Runtime 重启不影响其他 Runtime
- 治理日志可追踪到每条消息的流转路径

---

## 九、模板 + 验收

### 9.1 模板：Agent Runtime 配置检查表

```markdown
# Agent Runtime 配置检查表

## □ 基础配置
- [ ] agentId 唯一且符合命名约定
- [ ] model 指定了可用的模型名称
- [ ] accountId 与其他 Agent 不重复
- [ ] 工作区路径存在且为空或初始文件已创建

## □ 工作区完整性
- [ ] SOUL.md — 人格协议
- [ ] AGENTS.md — 操作纪律
- [ ] TOOLS.md — 工具边界
- [ ] MEMORY.md — 长期记忆
- [ ] IDENTITY.md — 身份锚点
- [ ] （可选）HEARTBEAT.md — 主动节律
- [ ] （可选）DECISIONS.md — 决策日志

## □ 技能配置
- [ ] skills 列表不为空
- [ ] 每个 skill 在系统中可用
- [ ] 技能数量与 Agent 角色匹配（不宜过多）

## □ 绑定配置
- [ ] 至少一个 binding 被定义
- [ ] binding 类型正确（channel / account / peer / keyword）
- [ ] 兜底 routing 存在

## □ 会话管理
- [ ] maxContext 已设置（建议 64000-128000）
- [ ] compactionStrategy 已选择
- [ ] 关键记忆已配置写入 MEMORY.md

## □ Heartbeat / Cron（可选）
- [ ] 启用 Heartbeat
- [ ] 定时任务清单维护
- [ ] 失败告警通道配置
```

### 9.2 验收标准

| 级别 | 验收命令 / 事项 | 预期结果 |
|------|----------------|---------|
| L1 | `openclaw gateway status` | Agent 在线 |
| L1 | 发送测试消息 | 返回有效回复 |
| L2 | 分 3 次不同时间发送相同问题 | 回复风格一致 |
| L2 | 发送越界请求 | Agent 根据 AGENTS 协议拒绝 |
| L3 | 观察 Heartbeat 是否按周期触发 | 定时任务执行日志可查 |
| L3 | 模拟长会话 | 自动压缩生效 |
| L4 | 跨 Agent 发送消息 | 消息被正确路由 |
| L4 | 重启一个 Runtime | 其他 Runtime 不受影响 |

---

## 训练题

### 训练题1
为什么 Agent Runtime 不等于模型上下文窗口？

**标准答案：**
因为 Runtime 承载的不只是当前 LLM 调用的 token 窗口，而是 Agent 的完整执行环境——包括工作区、会话历史、长期记忆、认证边界。模型上下文窗口只是 Runtime 的一个子集。

### 训练题2
一个 Runtime 能不能跑多个 Agent？

**标准答案：**
不能。每个 Agent 应该有独立的 Runtime 实例，否则会出现会话污染、人格混淆、单点故障等问题。n 个 Agent = n 个 Runtime 实例。

### 训练题3
Runtime 重启后 Agent 的哪部分会丢失？哪部分不会？

**标准答案：**
丢失：当前会话上下文（短期记忆）、临时生成状态、Heartbeat 未保存的中间状态。
不丢失：工作区所有文件（SOUL/MEMORY 等）、Skills 配置、agent.json 配置。

### 训练题4
什么是 Runtime 的拟人化映射？为什么它重要？

**标准答案：**
Runtime 拟人化为硅基生命的“身体”——Workspace 是家，Session 是短期记忆，MEMORY.md 是长期记忆，agentId 是身份证。这个映射帮助训练者理解：Agent 的长期一致性依赖于 Runtime 的独立性和工作区的完整性。很多人训练失败是因为他们没有意识到“Agent 需要一个好的身体”。

---

## 本章一句话收口

**Agent Runtime 不是承载模型的地方，是承载“一个持续运行的硅基生命体”的操作系统。不理解 Runtime，就永远在“写 prompt”，而不是“训虾”。它是硅基生命的“物理身体”——决定了这个生命能活多久、能同时做几件事、能不能跟同类互动。在配置任何 Agent 之前，先问自己：它的身体在哪里？**
