# 卷三｜系统骨架：OpenClaw 官方文档深度解剖
## 模块4｜Routing / Bindings
### ——为什么“谁该答”不是礼貌问题，而是系统路由问题


> 官方依据（本模块严格以官方路由规则为准，不靠猜）：
> - `channels/channel-routing.md`（渠道与路由：确定性路由、会话键格式、广播组）
> - `concepts/multi-agent.md`（多智能体隔离：workspace / agentDir / session store / auth profile）
> - `concepts/messages.md`（消息流程：入站→路由→会话键→队列→运行→出站）
> - `concepts/session-tool.md`（跨会话工具：sessions_* 的键模型与行为）

> 外部交叉验证（仅吸收可与官方机制对齐的行业共识）：
> - 多 Agent 系统的第一性原则：**先隔离，再路由，再协同**（否则必然抢答、串角色、责任不清）
> - 路由是一切治理的第一道门：谁收到消息 = 谁承诺交付 = 谁承担责任
> - “协同”不等于“群里谁想到谁回答”，协同必须基于确定性主责与受控的跨会话通信

---

## 目录
- [1）这个模块到底在讲什么](#1这个模块到底在讲什么)
- [2）官方一句话：模型不会选择渠道，路由是确定性的](#2官方一句话模型不会选择渠道路由是确定性的)
- [3）四个关键术语：Channel / AccountId / AgentId / SessionKey](#3四个关键术语channel--accountid--agentid--sessionkey)
- [4）官方路由规则：如何选择智能体（Bindings 优先级）](#4官方路由规则如何选择智能体bindings-优先级)
- [5）会话键格式：为什么同一条消息会落进不同桶](#5会话键格式为什么同一条消息会落进不同桶)
- [6）广播组（Broadcast groups）：同一条消息如何触发多个智能体](#6广播组broadcast-groups同一条消息如何触发多个智能体)
- [7）协同入口：Sessions 工具与“受控跨会话通信”](#7协同入口sessions-工具与受控跨会话通信)
- [8）拟人化映射：路由=军团编制的神经系统](#8拟人化映射路由军团编制的神经系统)
- [9）标杆案例：为什么群里@谁，必须谁答](#9标杆案例为什么群里谁必须谁答)
- [10）常见误区与反模式（对齐官方）](#10常见误区与反模式对齐官方)
- [11）模板 / 训练题 / 验收口径](#11模板--训练题--验收口径)
- [本模块一句话结论](#本模块一句话结论)

---

## 1）这个模块到底在讲什么
这个模块要训练一种非常关键、但很多团队永远训练不出来的能力：


> **“谁该答”是系统路由问题，不是组织礼貌问题。**

在龙虾军团训练里，最常见的协同失真就是：
- 群里有人 @ 了 A，结果 B 抢答
- 多个 agent 同时输出，用户不知道信谁
- 没有主责，最后也没有交付闭环

你会发现：
- 卷二解决的是“每只虾的生命协议”
- 卷三前面 1~3 模块解决的是“每只虾的运行与上下文治理”

而模块4要解决的是：


> **消息到底进哪个脑子？谁接单？谁负责？谁被授权？谁应该让位？**

这些问题，如果不落到 OpenClaw 的 bindings 路由机制上，就会永远停留在管理口号层。

---

## 2）官方一句话：模型不会选择渠道，路由是确定性的
官方在 `channels/channel-routing.md` 里把这句话说得很硬：

- OpenClaw 将回复路由回消息来源的渠道。
- **模型不会选择渠道；路由是确定性的，由主机配置控制。**

训练上的含义：
- 你不能指望“模型自己知道该去哪儿答”。
- 你必须把“谁接单”写进系统配置（bindings）或写进协同协议。

这句话会直接终结很多“以为模型会自己协同”的幻想。

---

## 3）四个关键术语：Channel / AccountId / AgentId / SessionKey
官方把路由讲清楚，离不开这四个术语：

### 3.1 Channel（渠道）
例如：whatsapp / telegram / discord / slack 等。

### 3.2 AccountId（账户实例）
同一渠道可能有多个账号（例如两个 WhatsApp）。AccountId 决定“来自哪个登录实例”。

### 3.3 AgentId（智能体）
这是“一个完全隔离的大脑”。每个 agentId 有：
- 独立 workspace
- 独立 agentDir（认证/配置）
- 独立 session store
（见 `concepts/multi-agent.md`）

### 3.4 SessionKey（会话桶）
用于存储上下文与控制并发的桶键。不同 chatType/线程/话题会映射到不同 sessionKey。（见 `channels/channel-routing.md`）

训练上的一句话：


> **Channel 决定入口，AccountId 决定账号实例，AgentId 决定大脑归属，SessionKey 决定状态桶。**

---

## 4）官方路由规则：如何选择智能体（Bindings 优先级）
官方路由优先级是确定性的、可推导的（`channels/channel-routing.md`）：

1. 精确对端匹配（bindings 的 `peer.kind` + `peer.id`）
2. Guild 匹配（Discord）`guildId`
3. Team 匹配（Slack）`teamId`
4. 账户匹配（渠道 `accountId`）
5. 渠道匹配（该渠道任意账户）
6. 默认智能体（`agents.list[].default`，否则列表第一项，兜底 main）

训练上的含义：

- 你想要“这个群永远由某只虾负责” → 用 peer 精确匹配绑定。
- 你想要“这个渠道默认由某只虾接” → 用 channel/accountId 绑定。
- 你想要“系统有兜底大脑” → 设置 default agent。

更关键的：


> **路由优先级越具体，主责越清晰；主责越清晰，协同越可治理。**

---

## 5）会话键格式：为什么同一条消息会落进不同桶
官方在路由文档里给出会话键格式（`channels/channel-routing.md`）：

- 私信：`agent:<agentId>:<mainKey>`（主会话）
- 群组：`agent:<agentId>:<channel>:group:<id>`
- 渠道/房间：`agent:<agentId>:<channel>:channel:<id>`

线程/话题：
- Slack/Discord：追加 `:thread:<threadId>`
- Telegram 论坛主题：嵌入 `:topic:<topicId>`

训练含义：
- “同一个人”在不同渠道可能落到不同会话桶（取决于 dmScope 与 identityLinks）。
- “同一个群”里的不同话题会被隔离成不同 sessionKey，避免互相污染。

这就是为什么你在军团训练里必须有“让位规则”：
- 因为系统已经在底层帮你做了隔离，你只需要在组织层做到主责明确。

---

## 6）广播组（Broadcast groups）：同一条消息如何触发多个智能体
官方提供 broadcast 机制：对同一对端可以运行多个智能体（在正常回复触发时）。（`channels/channel-routing.md`）

示例（官方）：
```json5
{
  broadcast: {
    strategy: "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"],
    "+15555550123": ["support", "logger"],
  },
}
```

训练含义（非常关键）：
- broadcast 是“系统级多脑并行”，不是“群里多嘴并行”。
- 它适合：一条消息需要多个视角（比如 support + logger），但必须有结果汇总策略。

如果你没有卷六/卷七的治理协议，broadcast 反而会把噪音放大。

---

## 7）协同入口：Sessions 工具与“受控跨会话通信”
当你需要 agent-to-agent 协同，官方提供的是会话工具集（`concepts/session-tool.md`）：
- sessions_list
- sessions_history
- sessions_send
- sessions_spawn

关键训练点：

### 7.1 协同的前提是“会话键清晰”
- 主私聊桶是字面键 `"main"`（解析为当前 agent 的主键）
- 群聊/频道需要完整 sessionKey

### 7.2 协同不是广播，而是受控投递
官方明确：工具设计目标是“小型、不易误用”。
这意味着：
- 你应该把 sessions_send 当成“点对点任务派发/接力”，而不是“群发通知”。

### 7.3 协同的组织含义
在军团里：
- bindings 决定“谁应该先答”（主责）
- sessions_* 决定“如何把任务交给另一个脑子处理”（协同）

这两个能力组合起来，才是“既不抢答，又能并行”的系统基础。

---

## 8）拟人化映射：路由=军团编制的神经系统
拟人化理解路由，会更容易训练运营与教练：

- bindings = 谁的工牌刷哪个门
- agentId = 哪个独立大脑
- accountId = 哪个手机号/登录身份
- sessionKey = 哪个工作线程/档案夹

所以路由的仿真价值是：


> **它让军团“按编制作战”，而不是按谁更吵作战。**

---

## 9）标杆案例：为什么群里@谁，必须谁答
这不是礼貌，是治理。

### 案例：群里@法务虾，运营虾先抢答
后果：
- 错误权威
- 责任漂移
- 用户信任坍塌

### 用 OpenClaw 官方骨架解释
- 路由层本质是在选择“哪个 agentId 接到这条消息”。
- 如果你在组织层允许抢答，那就等于绕过了路由层的“主责选择”。

### 正确做法（训练协议化）
- 群里 @ 到哪个 agent，哪个 agent 负责首答。
- 其他 agent 需要补充时，通过受控协同（sessions_send / sessions_spawn）走后台，不在前台抢答。

（这也是为什么我们在卷二/卷六要写“让位规则”的原因：它与官方路由机制是同一套哲学。）

---

## 10）常见误区与反模式（对齐官方）

### 10.1 误区：模型会自己选渠道/选脑子
官方反证：路由是确定性的，由配置控制。

### 10.2 误区：一个 agent = 一个账号
官方澄清：agent 是独立工作区+会话+状态目录；账号是 channel/accountId。

### 10.3 误区：多 agent = 群里同时发言
官方机制更接近：多 agent 是多隔离大脑，由 bindings 决定谁接入站；broadcast 也有明确配置。

### 10.4 误区：bindings 越少越省事
结果：所有消息都回落到默认智能体，主责模糊，协同崩坏。

### 10.5 误区：不理解 sessionKey 的隔离
结果：你以为“同一群就是同一会话”，但实际线程/话题会分桶；你做的治理动作会落空。

---

## 11）模板 / 训练题 / 验收口径

### 11.1 最小 bindings 设计模板（训练版）
- 渠道级默认：WhatsApp → chat 虾；Telegram → deepwork 虾
- 关键群/关键客户：peer 精确匹配 → 专家虾
- default agent：兜底（但尽量少触发）

### 11.2 训练题
**题1｜推导路由结果**
给定 3 条 bindings，推导一条来自 Telegram 群 topic 的消息会进哪个 agentId、哪个 sessionKey。

**题2｜主责与协同分离**
设计一套“群里不抢答、后台能并行”的协同流程：
- 谁首答
- 谁后台协助
- 如何回收结果
- 如何验收

**题3｜广播组的使用边界**
什么场景你会用 broadcast，什么场景坚决不用？为什么？

### 11.3 验收口径（DoD）
本模块验收标准：
- 能说清 Channel / AccountId / AgentId / SessionKey 的区别
- 能背出并解释官方 bindings 优先级（peer→guild→team→accountId→channel→default）
- 能解释 broadcast 的用途与风险
- 能把“让位/主责”落成路由与协同两条机制：bindings 决主责、sessions_* 做协同

---

## 本模块一句话结论

> **在 OpenClaw 里，“谁该答”首先是 bindings 的确定性路由结果；只有当主责由路由锁定、协同由 sessions_* 受控实现，龙虾军团才可能做到并行而不抢答、分工而不串角色、协作而可追责。**
