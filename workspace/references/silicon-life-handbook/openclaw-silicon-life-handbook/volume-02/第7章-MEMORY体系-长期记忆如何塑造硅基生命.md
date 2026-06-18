# 第7章｜IDENTITY / MEMORY / BOOTSTRAP：辅助作用
## ——为什么这三份“看似辅助”的协议，决定硅基生命能否跨时间持续存在、跨会话保持一致、跨军团保持秩序

> 你指出的问题是对的：卷二的模块7如果只讲 MEMORY，会变成“少一条腿”。
>
> 因为在 OpenClaw 的设计里，真正能把硅基生命从“一次性对话”推进到“长期可持续运行”的，不只有记忆，还有：
> - **IDENTITY**：身份锚点（可识别、可路由、可追责）
> - **MEMORY**：长期记忆（可沉淀、可检索、可进化）
> - **BOOTSTRAP**：一次性启动仪式（把工作区从空白初始化成可运行生命容器）
>
> 所以本章将“模块7：IDENTITY / MEMORY / BOOTSTRAP 的辅助作用”补齐为完整章。

---

## 官方依据（本章主证据链）
- `concepts/agent-workspace.md`
  - 工作区标准文件映射包含：`IDENTITY.md`、`BOOTSTRAP.md`、`memory/YYYY-MM-DD.md`、`MEMORY.md`。
  - `BOOTSTRAP.md`：一次性的首次运行仪式；仅为全新的工作区创建；完成后应删除。
  - 可通过 `agent.skipBootstrap: true` 禁用引导文件创建。
- `concepts/memory.md`
  - OpenClaw 记忆是**工作空间中的纯 Markdown 文件**；模型只“记住”写入磁盘的内容。
  - 默认两层结构：`memory/YYYY-MM-DD.md`（每日日志，仅追加）与 `MEMORY.md`（精选长期记忆）。
  - `MEMORY.md` 仅在主要私人会话中加载，不在群组上下文中加载。
  - 接近 compaction 前可触发静默 memory flush，将 durable notes 写入 `memory/YYYY-MM-DD.md`。
- `concepts/compaction.md`
  - 长会话接近上下文窗口时会触发压缩；压缩前可进行静默记忆刷写。

> 补充说明：第6章已对 `IDENTITY.md` 做了“身份锚点协议”的完整深拆。本章不重复第6章全部内容，而是把 **IDENTITY 与 MEMORY/BOOTSTRAP 的系统联动**讲透。

---

# 目录
- [0）本章一句话结论](#0本章一句话结论)
- [1）这三份“辅助协议”到底是什么](#1这三份辅助协议到底是什么)
- [2）为什么它们必须合在一起看](#2为什么它们必须合在一起看)
- [3）在硅基生命里对应什么（拟人化映射/仿真价值）](#3在硅基生命里对应什么拟人化映射仿真价值)
- [4）对长期 AI 表现的决定性作用（Impact）](#4对长期-ai-表现的决定性作用impact)
- [5）BOOTSTRAP：一次性启动仪式（把空工作区变成生命容器）](#5bootstrap一次性启动仪式把空工作区变成生命容器)
- [6）IDENTITY：身份锚点（把生命“识别出来、路由对、追责得了”）](#6identity身份锚点把生命识别出来路由对追责得了)
- [7）MEMORY：长期记忆（把经验与决策沉淀为可检索资产）](#7memory长期记忆把经验与决策沉淀为可检索资产)
- [8）三者联动：从“第一次启动”到“长期稳定运行”的闭环](#8三者联动从第一次启动到长期稳定运行的闭环)
- [9）边界：它们与 USER/SOUL/AGENTS/TOOLS/HEARTBEAT 的关系](#9边界它们与-usersoulagentstoolsheartbeat-的关系)
- [10）常见反模式](#10常见反模式)
- [11）最佳实践（从入门到业内最佳实践）](#11最佳实践从入门到业内最佳实践)
- [12）模板 / 示例 / 训练题 / 验收口径](#12模板--示例--训练题--验收口径)

---

## 0）本章一句话结论
> **BOOTSTRAP 负责“第一次把生命容器搭起来”；IDENTITY 负责“让系统持续识别这是谁”；MEMORY 负责“让这只生命跨时间持续进化”。三者共同决定：硅基生命能否长期稳定存在，以及军团协同能否不失真。**

---

## 1）这三份“辅助协议”到底是什么

### 1.1 BOOTSTRAP.md：一次性首次运行仪式
官方定义非常直接：
- **仅为全新的工作区创建**
- **完成后应删除**

它不是长期运行规则，而是“开荒脚本/起手式”。

### 1.2 IDENTITY.md：身份锚点
官方描述很轻：名称、风格、emoji；但第6章已经证明它的系统意义是：
- 可识别
- 可路由
- 可追责
- 可让位
- 可形成长期人格连续性感知

### 1.3 MEMORY.md + memory/YYYY-MM-DD.md：长期记忆体系
官方给出了两层结构：
- `memory/YYYY-MM-DD.md`：每日记忆日志（append-only）
- `MEMORY.md`：精选长期记忆（主私聊加载；群聊不加载）

并提供：
- `memory_search` / `memory_get` 检索
- 接近 compaction 时的静默 memory flush

---

## 2）为什么它们必须合在一起看
如果只看 MEMORY，你会以为：
- 把重要信息写下来就行

但长期系统会在三处失败：

### 2.1 没有 BOOTSTRAP：你连“第一套稳定地基”都没铺好
没有启动仪式，工作区往往会出现：
- 文件结构不完整
- 关键协议缺失
- 初始约束没有写入
- 习惯/工具/边界没有统一

结果是：
> 记忆写得再好，也是在一个“没有完工的容器”里跑。

### 2.2 没有 IDENTITY：你无法稳定识别“到底是哪只虾在工作”
尤其在：
- 多会话
- 多渠道
- 多 Agent
- 群聊协同

没有身份锚点，协作会迅速退化为：
- 谁都像
- 谁都能答
- 谁都抢答
- 谁都不背责

### 2.3 没有 MEMORY：你永远只能“当场像”，无法跨时间稳定
没有长期记忆沉淀：
- 决策会反复重议
- 偏好会反复踩雷
- 错误会反复再犯

**所以：BOOTSTRAP 解决“起手式正确”，IDENTITY 解决“角色连续性正确”，MEMORY 解决“跨时间连续性正确”。**

---

## 3）在硅基生命里对应什么（拟人化映射/仿真价值）

- **BOOTSTRAP**：新员工入职的“第一天 onboarding + 电脑环境初始化 + 规矩宣导”。
- **IDENTITY**：工牌/名片/岗位名（让组织知道“谁在说话、谁负责什么”）。
- **MEMORY**：工作日志 + 经验簿 + 可检索的第二大脑（让人跨时间持续成长）。

仿真价值在于：
> 不是“像一个人说话”，而是“像一个组织里的角色在持续存在”。

---

## 4）对长期 AI 表现的决定性作用（Impact）

### 4.1 稳定性
- BOOTSTRAP 让初始协议与结构正确，减少早期漂移。
- MEMORY 让关键决策沉淀，减少重复争论。

### 4.2 一致性
- IDENTITY 让对外呈现稳定。
- MEMORY 让对内规则稳定。

### 4.3 主动性（可控的主动，而非噪音）
- MEMORY flush + compaction 机制让主动系统不会因长会话崩坏。

### 4.4 协同能力
- IDENTITY 是协同秩序的可见边界。
- MEMORY 是协同共识的可检索底盘。

### 4.5 可治理性
- IDENTITY 支持责任归属。
- MEMORY 支持审计与复盘。
- BOOTSTRAP 支持“工作区标准化”，让治理可复制。

---

## 5）BOOTSTRAP：一次性启动仪式（把空工作区变成生命容器）

### 5.1 BOOTSTRAP 的官方定位
来自官方工作区映射：
- `BOOTSTRAP.md`：一次性的首次运行仪式
- 仅为全新的工作区创建
- 仪式完成后请将其删除

这句话意味着：
- 它不是日常规则库
- 它不是长期记忆
- 它是“初始化动作清单”

### 5.2 它到底应该写什么
BOOTSTRAP 的最佳内容结构：
1. **环境确认**：当前工作区路径、关键目录是否存在
2. **协议落地**：USER/SOUL/AGENTS/TOOLS/IDENTITY/MEMORY/HEARTBEAT 是否齐全
3. **危险项清单**：哪些内容不该写（密钥、隐私数据）
4. **首次演练**：跑一次“任务卡—工具调用—证据回执—记忆落盘”闭环
5. **删除条件**：当哪些条件满足，即可删除 BOOTSTRAP.md

### 5.3 BOOTSTRAP 与 skipBootstrap
官方给出：可通过配置 `agent.skipBootstrap: true` 禁用引导文件创建。
含义：
- 如果你有预置工作区或仓库化工作区，BOOTSTRAP 可以不自动生成。
- 但你必须自己承担“初始化正确性”的责任。

### 5.4 BOOTSTRAP vs BOOT
官方工作区映射里还有 `BOOT.md`：
- 可选启动检查清单（配合内部 hooks 可在 gateway 重启时执行）

简化理解：
- **BOOTSTRAP**：第一次启动的仪式（一次性）
- **BOOT**：每次 gateway 启动时可运行的检查清单（可重复）

---

## 6）IDENTITY：身份锚点（把生命“识别出来、路由对、追责得了”）

### 6.1 为什么模块7仍要讲 IDENTITY
第6章已经深拆 IDENTITY，但模块7必须补这一段，是因为：

> 你要的“辅助作用”不是讲文件内容，而是讲它如何和 MEMORY/BOOTSTRAP 形成闭环。

### 6.2 IDENTITY 在三件事上起硬作用
1) **把协作从“匿名模型”变成“可识别角色”**
2) **把治理从“感觉谁做的”变成“能追到责任人”**
3) **把路由从“碰运气”变成“可解释的秩序”**

### 6.3 IDENTITY 与 MEMORY 的关系
- IDENTITY 定义“这只虾是谁”（名字/角色/标识）。
- MEMORY 记录“这只虾经历了什么、定了什么、承诺了什么”。

没有 IDENTITY，MEMORY 会变成：
- 记住了信息，但不知道归属哪个角色

没有 MEMORY，IDENTITY 会变成：
- 看起来像角色，但经不起跨时间考验

### 6.4 IDENTITY 与 BOOTSTRAP 的关系
BOOTSTRAP 是最适合“写入/校准身份锚点”的阶段：
- 初始命名
- 角色定位
- emoji / 风格
- 组织里的位置

也就是说：
> **BOOTSTRAP 把 IDENTITY 固化为“第一锚点”，后续 MEMORY 负责把这锚点变成“有历史的角色”。**

---

## 7）MEMORY：长期记忆（把经验与决策沉淀为可检索资产）

> 以下内容保留原第7章 MEMORY 深拆的主体结构，并在本章语境下补齐与 IDENTITY/BOOTSTRAP 的联动。

### 7.1 官方一句话定义（必须刻进肌肉记忆）
> **OpenClaw 记忆是工作空间里的纯 Markdown 文件，这些文件是唯一事实来源；模型只“记住”写入磁盘的内容。**

含义：
- 不写入磁盘 = 不算记住
- 会话里“看起来记得”= 只是暂存幻觉

### 7.2 两层记忆结构：daily vs curated
- `memory/YYYY-MM-DD.md`：事件层（append-only）
- `MEMORY.md`：长期精选层（主私聊加载）

对应行业共识：
- episodic / event log
- curated semantic memory

### 7.3 Memory 搜索与审计
官方提供：
- `memory_search`：语义检索
- `memory_get`：安全读取片段

这保证记忆不是“堆”，而是未来可找回。

### 7.4 Compaction 前的 memory flush
官方明确：会话接近 compaction 时，可触发静默 memory flush。

这一步解决一个关键难题：
> 上下文要压缩了，哪些东西必须从“临时脑内”转存为“外部持久记忆”？

### 7.5 MEMORY 与 IDENTITY/BOOTSTRAP 的联动补齐
- BOOTSTRAP：负责把“记忆结构”创建出来，并建立写入纪律。
- IDENTITY：负责给记忆提供稳定归属（这是谁的记忆）。
- MEMORY：负责把运行结果沉淀为可复用资产。

---

## 8）三者联动：从“第一次启动”到“长期稳定运行”的闭环
用一条链路把它们收束：

1. **BOOTSTRAP**（一次性）
   - 初始化工作区文件与规则
   - 建立写入纪律
   - 固化 IDENTITY 初始锚点

2. **IDENTITY**（长期稳定）
   - 让系统识别角色
   - 让路由与治理具备可解释性

3. **MEMORY**（持续沉淀）
   - 把关键决策、偏好、事实写入磁盘
   - 使用 daily 与 curated 分层

4. **Compaction + memory flush**（长期生存）
   - 上下文爆炸时压缩
   - 压缩前先落盘 durable notes

这条闭环的结果是：
> 硅基生命不再是一次性回答器，而是具备“可持续存在”的系统实体。

---

## 9）边界：它们与 USER/SOUL/AGENTS/TOOLS/HEARTBEAT 的关系

- **BOOTSTRAP vs USER/SOUL/AGENTS**：BOOTSTRAP 是一次性初始化，不应承载长期人格与治理规则本体。
- **IDENTITY vs SOUL**：IDENTITY 是可见身份锚点；SOUL 是人格内核。
- **MEMORY vs Session**：MEMORY 是磁盘事实层；session 是对话运行上下文。
- **MEMORY vs HEARTBEAT**：HEARTBEAT 负责节律巡检；MEMORY 负责跨时间沉淀。
- **TOOLS vs MEMORY**：TOOLS 是环境映射与工具说明；MEMORY 是事实/决策/偏好沉淀。

---

## 10）常见反模式

### 反模式1：把 BOOTSTRAP 当长期规则库
结果：启动仪式永远不结束，工作区永远处于“未完工状态”。

### 反模式2：把 IDENTITY 当装饰页
结果：协同失序、责任无法归属、用户难以识别角色。

### 反模式3：把会话当记忆
结果：一次 compaction 或一次 reset，关键决策丢失。

### 反模式4：把所有东西都写进 MEMORY.md
结果：长期记忆被噪音污染，检索失真。

### 反模式5：没有“写入纪律”与“验收口径”
结果：口头说记住了，但从未写入磁盘；系统以为完成，实际没沉淀。

---

## 11）最佳实践（从入门到业内最佳实践）

### 11.1 入门（最低可用）
- BOOTSTRAP：一次性完成并删除
- IDENTITY：名称+角色定位+emoji
- MEMORY：daily append-only，记录关键决策与状态

### 11.2 进阶（双层记忆 + 协同锚点）
- daily 作为事件层
- MEMORY.md 作为精选长期层
- IDENTITY 与军团编制/路由规则一致

### 11.3 最佳实践（可治理、可审计、可进化）
- 有记忆卫生：什么能进长期、什么只能进 daily
- 有检索策略：memory_search 用于事实回忆
- 有 compaction 前刷写纪律
- 有治理口径：无证据不入账、无 owner 不固化

---

## 12）模板 / 示例 / 训练题 / 验收口径

### 12.1 BOOTSTRAP.md 模板（一次性）
```md
# BOOTSTRAP — 首次运行仪式（完成后删除）

## 1) 环境确认
- workspace 路径：
- 是否存在 AGENTS/SOUL/USER/TOOLS/IDENTITY/HEARTBEAT/MEMORY：

## 2) 身份锚点确认（IDENTITY）
- 名称：
- 角色：
- emoji：

## 3) 记忆结构初始化（MEMORY）
- 确认存在 memory/ 目录
- 今天的 daily memory 文件是否创建

## 4) 首次演练（必须产出证据）
- 演练任务：
- 交付物路径：
- 验收口径：
- 写入 daily memory 的条目：

## 5) 删除条件
- 上述 1~4 完成且验收通过 → 删除本文件
```

### 12.2 IDENTITY.md 最小模板
```md
# Name: 
# Role: 
# Emoji: 
# Vibe: 
```

### 12.3 MEMORY 写入最小规则
- 决策/偏好/持久事实 → 先写 daily，再提纯进 MEMORY.md
- 模糊信息不固化
- 敏感信息不入库

### 12.4 训练题
1) 为什么 BOOTSTRAP 必须“一次性完成并删除”？
2) 为什么 IDENTITY 是协同系统的“工牌”，而不是装饰？
3) 为什么“会话摘要/compaction”不能替代 MEMORY.md？
4) daily memory 与 MEMORY.md 的边界是什么？

### 12.5 验收口径
你要验收本章是否真正补齐，只看三件事：
1. 读者是否能说清 BOOTSTRAP/IDENTITY/MEMORY 各自负责什么、边界是什么。
2. 是否能画出“三者联动闭环”（第一次启动→身份锚点→记忆沉淀→压缩前刷写）。
3. 是否能写出可用模板（BOOTSTRAP/IDENTITY/MEMORY 最小可用）。

---

# 本章一句话收口
**BOOTSTRAP 把生命容器从空白初始化成可运行；IDENTITY 让系统持续识别这是谁、该谁答、该谁背责；MEMORY 让这只生命跨时间持续进化并可被检索审计。三者看似辅助，实则是硅基生命从“会聊”到“能长期作战”的关键基础设施。**
