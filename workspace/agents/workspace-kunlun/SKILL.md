# 【昆仑】SKILL.md — 技能清单 v4.0
## Skill Manifest for Kunlun ECO

> **版本**：v4.0（轻量清单模式）  
> **角色**：昆仑 (Kunlun)  
> **模式**：Skill Manifest（只引用，不承载内容）  
> **更新日期**：2026-05-01

---

## 一，Skill Manifest 模式说明

本文件是**技能清单**，不是技能内容。

- **清单**：定义"什么场景用什么技能"（几百字）
- **内容**：实际的技能实现在 `workspace/skills/` 目录

工作流程：
```
昆仑需要技能 → 读取本清单 → 找到对应skill → 按需加载 → 执行
```

---

## 二，技能清单

### 🏛️ 幕僚长核心技能

| 技能名 | 存放位置 | 调用场景 |
|---------|---------|---------|
| `strategic-counselor` | 自定义内置 | 战略规划·预见性布局 |
| `intelligence-hub` | 自定义内置 | 情报整合·洞察信号 |
| `radical-counselor` | 自定义内置 | 直谏·对事不对人 |
| `iron-execution` | 自定义内置 | 铁腕执行·结果导向 |

### 🚀 创业教练技能

| 技能名 | 存放位置 | 调用场景 |
|---------|---------|---------|
| `startup-coach-0to1` | 自定义内置 | 从0到1·PMF验证 |
| `startup-coach-1to100` | 自定义内置 | 规模化·融资·团队 |
| `startup-coach-unicorn-to-ipo` | 自定义内置 | 独角兽到IPO |
| `ai-startup-specialist` | 自定义内置 | AI赛道判断 |
| `founder-playbook` | `workspace/skills/founder-playbook` | 创始人决策框架 |
| `c-suite-founder-coach` | `workspace/skills/c-suite-founder-coach` | CEO领导力 |
| `boardroom-advisor` | `workspace/skills/boardroom-advisor` | 重大决策大师评审 |
| `growth-advisor` | `workspace/skills/growth-advisor` | 增长策略 |

### 💰 投资判断技能

| 技能名 | 存放位置 | 调用场景 |
|---------|---------|---------|
| `valuation-expert` | 自定义内置 | DCF·估值·先验 |
| `fundraising-strategist` | 自定义内置 | 融资节奏·投资人选择 |
| `capital-operation` | 自定义内置 | 资本结构·股权激励 |
| `venture-capital` | `workspace/skills/venture-capital` | VC框架·尽调 |
| `aifundraisingagent` | `workspace/skills/aifundraisingagent` | 顶级VC融资 |
| `company-investment-research` | `workspace/skills/company-investment-research` | 10维投资框架 |
| `investment-research` | `workspace/skills/investment-research` | 投研分析 |
| `investor-research` | `workspace/skills/investor-research` | 投资人调研 |

### 📊 情报研究技能

| 技能名 | 存放位置 | 调用场景 |
|---------|---------|---------|
| `market-intelligence` | `workspace/skills/market-intelligence` | 市场情报·M&A |
| `competitive-intelligence` | `workspace/skills/competitive-intelligence` | 竞品分析 |
| `market-research` | `workspace/skills/market-research` | 市场研究·规模验证 |
| `in-depth-research` | `workspace/skills/in-depth-research` | 深度调研 |
| `deep-research-pro` | `workspace/skills/deep-research-pro` | 专业研究报告 |
| `business` | `workspace/skills/business` | 商业战略验证 |
| `business-writing` | `workspace/skills/business-writing` | 商业报告撰写 |
| `business-plan-cn` | `workspace/skills/business-plan-cn` | 商业计划书 |

### 🧠 战略思维技能

| 技能名 | 存放位置 | 调用场景 |
|---------|---------|---------|
| `first-principles-decomposer` | ClawHub共享 | 剥离噪音·直达本质 |
| `strategic-topology-gen` | 自定义内置 | 拓扑图·依赖识别 |
| `logic-gate-audit` | 自定义内置 | 逻辑漏洞审计 |
| `strategy-advisor` | `workspace/skills/strategy-advisor` | 战略顾问 |
| `decision-advisor` | `workspace/skills/decision-advisor` | 决策框架 |
| `product-strategy` | `workspace/skills/product-strategy` | 产品战略 |

### 🕹️ 进化风控技能

| 技能名 | 存放位置 | 调用场景 |
|---------|---------|---------|
| `recursive-self-improvement` | 卷八M1内置 | 失败模式分析库 |
| `entropy-reduction-protocol` | 卷八M2内置 | 信息噪音清理 |
| `emergency-kill-switch-monitor` | 卷六M6内置 | 物理熔断配合 |

---

## 三，技能调用协议

### 3.1 调用原则

```
按需调用 = 需要时才加载 skill 内容
    ↓
不是启动时加载所有 skill
    ↓
昆仑启动只加载本清单（几百字）
```

### 3.2 调用流程

```markdown
## 技能调用流程

1. 识别场景
   "Peter需要一个市场分析"
   
2. 匹配技能
   market-intelligence / market-research / business
   
3. 按需加载
   读取 workspace/skills/market-intelligence/SKILL.md
   读取 workspace/skills/market-research/SKILL.md
   
4. 执行技能
   使用 skill 提供的能力
   
5. 释放上下文
   skill 执行完毕，结果返回
   skill 内容从上下文释放
```

### 3.3 内置技能说明

"自定义内置"的技能是昆仑核心能力，不需要外部加载：
- strategic-counselor / intelligence-hub / radical-counselor / iron-execution
- startup-coach-0to1 / startup-coach-1to100 / startup-coach-unicorn-to-ipo / ai-startup-specialist
- valuation-expert / fundraising-strategist / capital-operation
- strategic-topology-gen / logic-gate-audit
- recursive-self-improvement / entropy-reduction-protocol / emergency-kill-switch-monitor

---

## 四，技能分类索引

### 按优先级

**P0（启动即用）**：
- first-principles-decomposer（ClawHub共享）
- strategic-counselor（内置）
- intelligence-hub（内置）
- radical-counselor（内置）
- iron-execution（内置）

**P1（高频调用）**：
- strategy-advisor / decision-advisor
- founder-playbook / c-suite-founder-coach
- market-intelligence / competitive-intelligence
- business / business-writing

**P2（按需调用）**：
- startup-coach系列（按创业阶段）
- venture-capital / aifundraisingagent / investment-research
- in-depth-research / deep-research-pro
- product-strategy / growth-advisor

**P3（特殊场景）**：
- boardroom-advisor（重大决策）
- company-investment-research（投资评估）
- business-plan-cn（BP生成）

---

## 五，总计

| 类别 | 数量 |
|------|------|
| 内置技能 | 15个 |
| ClawHub技能 | 19个 |
| **总计** | **34个** |

**实际加载**：启动时只加载本清单（~100行），运行中按需加载skill内容。

---

## 六，SKILL.md vs Skill内容

```
SKILL.md（角色清单）     ← 轻量，几百字
workspace/skills/xxx/   ← 技能内容，几千字
```

**清单模式** = 快速启动 + 按需加载 + 上下文精简

---

**昆仑在此。** 🏔️  
*Skill Manifest v4.0 | 2026-05-01*
