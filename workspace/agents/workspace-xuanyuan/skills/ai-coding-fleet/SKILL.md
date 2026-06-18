---
name: ai-coding-fleet
description: "轩辕AI编码舰队——OpenClaw作为大脑，指挥Claude Code/Cursor/Windsurf/Trae/Codex CLI集群并行开发。覆盖：ACP配置、IDE接入、权限管理、任务分发、windsurf+cursor双IDE调度、worktree隔离、舰队看板。触发词：IDE舰队、编码集群、AI IDE、多工具编排、ACP配置、Cursor舰队、Windsurf集群、Trae接入、IDE调度、并行编码、AI编码引擎、IDE编排、coding fleet"
---

# 🚀 轩辕AI编码舰队 — AI Coding Fleet

> **版本**：v1.0 | **角色**：轩辕 CTO | **目标**：OpenClaw作为舰队指挥中心，调度多AI IDE集群并行开发
>
> "大脑指挥双手"架构：轩辕(OpenClaw) = 舰队司令，Claude Code/Cursor/Windsurf/Trae/Codex = 各司其职的战士

---

## 一、核心架构

### 1.1 指挥链拓扑

```
┌─────────────────────────────────────────────────────────┐
│                  轩辕 CTO (OpenClaw)                      │
│  舰队司令 · 任务分解 · 进度追踪 · 质量门禁              │
│  (通过Telegram/Slack/Web与创始人交互)                      │
└────┬──────────┬──────────┬──────────┬──────────┬────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Claude  │ │Cursor  │ │Windsurf│ │Trae    │ │Codex   │
│Code    │ │Agent   │ │Cascade │ │Agent   │ │CLI     │
│(主力)  │ │(IDE)   │ │(IDE)   │ │(IDE)   │ │(云端)  │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │          │
    └──────────┴─────┬────┴──────────┴──────────┘
                     │
          ┌──────────▼──────────┐
          │  Git Worktree 隔离层  │
          │  每个Agent一个独立分支 │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │    代码仓库 (Git)     │
          │  (PR/Merge队列)      │
          └─────────────────────┘
```

### 1.2 每个工具的定位

| 工具 | 定位 | 适用场景 | 接入方式 | 推荐模型 |
|------|------|---------|---------|---------|
| **Claude Code** 🎯 | 主力编码引擎 | 复杂重构、多文件修改、代码审计 | OpenClaw ACP (`agentId: "claude"`) | Claude Sonnet/Opus |
| **Cursor** 🖥️ | 交互式IDE | 手动调试、UI开发、小步迭代 | ACP (`agentId: "cursor"`) + GUI | Claude Sonnet |
| **Windsurf** 🌊 | 推理型IDE | 复杂分析、长上下文任务、Cascade模式 | `/Applications/Windsurf.app` + CLI | Claude Sonnet |
| **Trae** 🦋 | 字节IDE（中国区） | 前后端原型、低延迟需求 | ACP接入 | 默认(Claude/GPT) |
| **Codex CLI** 🤖 | 云端并行编码 | 隔离环境、快速原型、GPT-5专属 | ACP (`agentId: "codex"`) + Worktree | GPT-5.3-Codex |
| **MCO** 🔗 | 编排层（可选） | 跨Agent结果聚合、多Agent协同 | npm包 `mco` | 依赖子Agent |

---

## 二、安装配置

### 2.1 一键安装脚本

```bash
# 运行轩辕AI编码舰队安装脚本
bash skills/ai-coding-fleet/install.sh
```

该脚本自动：
- ✅ 安装Claude Code (`npm i -g @anthropic-ai/claude-code`)
- ✅ 安装Codex CLI (`npm i -g @openai/codex`，如果有OpenAI key)
- ✅ 安装MCO编排层 (`npm i -g mco`)
- ✅ 配置OpenClaw ACP (`acp.enabled=true`)
- ✅ 安装acpx插件
- ✅ 配置vscode IDE集成
- ✅ 验证所有连接
- ✅ 生成舰队看板

### 2.2 手动安装

#### Step 1: 安装核心引擎

```bash
# Claude Code - 主力
npm install -g @anthropic-ai/claude-code

# 验证
claude --version

# 授权
claude login  # 用Anthropic账号登录
```

```bash
# Codex CLI - 云端并行 (需要OpenAI API Key + Codex权限)
npm install -g @openai/codex
codex --version
```

```bash
# MCO - 编排层 (可选)
npm install -g mco
mco --version
```

#### Step 2: 安装IDE工具

```bash
# Cursor (GUI IDE)
brew install --cask cursor

# Windsurf (GUI IDE) - 已安装在 /Applications
# Trae - 从 https://www.trae.ai 下载
```

#### Step 3: 配置OpenClaw ACP

在 `~/.openclaw/openclaw.json` 中添加ACP配置：

```json5
{
  "acp": {
    "enabled": true,
    "dispatch": { "enabled": true },
    "backend": "acpx",
    "defaultAgent": "claude",
    "allowedAgents": [
      "claude",
      "codex",
      "cursor"
    ],
    "maxConcurrentSessions": 8,
    "stream": {
      "coalesceIdleMs": 300,
      "maxChunkChars": 1200
    },
    "runtime": {
      "ttlMinutes": 120
    }
  }
}
```

> ⚡ 添加后重启OpenClaw: `openclaw gateway restart`

#### Step 4: 验证ACP就绪

```bash
# 在OpenClaw中
/acp doctor
# 应返回: ✅ ACP backend healthy, allowed agents: claude, codex, cursor
```

---

## 三、舰队工作流

### 3.1 任务分派策略

```
任务复杂度判定 → 匹配最佳工具 → 并行执行 → 结果聚合
```

| 任务类型 | 分派给谁 | 为什么 |
|---------|---------|-------|
| 前端UI组件 (React/Vue) | **Cursor IDE** | GUI调试+实时预览 |
| 后端API/REST端点 | **Claude Code** | 文件级Agent，最强大 |
| 数据库脚本/迁移 | **Claude Code** | 需要精确的文件操作 |
| 代码重构/审计 | **Claude Code + Windsurf** | Windsurf做分析+Claude执行 |
| 快速原型/实验 | **Codex CLI** | 云端隔离，不影响本地 |
| 中国区项目/字节生态 | **Trae** | 字节专属优化 |
| 多Agent协同 | **轩辕调度 → MCO编排** | 任务分解+结果聚合 |

### 3.2 轩辕调度示例

**场景**：收到"实现用户管理系统CRUD API + 前端页面"

```
轩辕：分析任务复杂度

[任务分解]
┌─ 子任务1: User Model + DB Schema
│   → Agent: Claude Code → /acp spawn claude {task: "创建User模型..."}
│
┌─ 子任务2: User CRUD API (6个端点)
│   → Agent: Claude Code → /acp spawn claude {task: "实现REST API..."}
│
┌─ 子任务3: 前端User页面 (list/detail/form)
│   → Agent: Cursor → /acp spawn cursor {task: "实现前端页面..."}
│
┌─ 子任务4: 单元测试
│   → Agent: Codex CLI → /acp spawn codex {task: "编写测试..."}

[并行执行]
→ 4个子Agent同时工作
→ 每个在自己的worktree/branch上

[结果聚合]
→ 自动PR创建
→ 冲突检测
→ 质量门禁通过 → 通知交付
```

### 3.3 在Telegram中操作/acp

当你在Telegram和轩辕对话时：

```
你：帮我实现一个用户登录页面（前后端）
轩辕：收到，分解为3个子任务并行执行...

/acp spawn claude {task: "后端JWT认证API", cwd: "/project"}
  → ✅ 完成：创建 auth.js + middleware + test

/acp spawn cursor {task: "前端Login组件", cwd: "/project"}
  → ✅ 完成：创建 Login.tsx + validation + styles

/acp spawn codex {task: "集成测试用例", cwd: "/project"}
  → ✅ 完成：创建 e2e test

轩辕：全部完成，3个PR已创建，覆盖率92%
```

---

## 四、IDE工具详细配置

### 4.1 Cursor配置

**安装**：
```bash
brew install --cask cursor
```

**Cursor CLI ACP配置**（Cursor 0.48+内置ACP支持）：
```bash
# 验证cursor CLI
cursor --version

# 通过ACP启动
/acp spawn cursor
```

**Cursor设置建议**：
- 在Settings → Models中，选择Claude Sonnet作为默认Agent模型
- 启用Agent Mode (Cmd+I)
- 设置 `.cursorrules` 项目根目录规则

### 4.2 Windsurf配置

**安装**（已在 `/Applications/Windsurf.app`）：
```bash
# 创建命令行别名
echo 'alias windsurf="/Applications/Windsurf.app/Contents/Resources/app/bin/windsurf"' >> ~/.zshrc
source ~/.zshrc
```

**Windsurf CLI功能**：
```bash
# 打开项目
windsurf /path/to/project

# Cascade模式（Windsurf的Agent）
# 在Windsurf中按 Cmd+I → Cascade模式
```

**Windsurf在舰队中的角色**：
- 适合长上下文、复杂分析任务
- Cascade模式在复杂推理场景表现优异
- 与Cursor互补使用

### 4.3 WindSurf + Cursor 双IDE调度策略

| 策略 | 谁用Windsurf | 谁用Cursor | 说明 |
|------|------------|-----------|------|
| 分析→执行 | Windsurf分析架构 | Cursor执行编码 | Windsurf擅长深度推理，Cursor擅长精确修改 |
| 前端→后端 | Cursor做前端(调试) | Claude Code做后端(files) | IDE适合UI调试，CLI文件操作更快 |
| 评审→修复 | Windsurf做Code Review | Cursor修复 | Windsurf审查更全面，Cursor修复更精确 |
| 长→短 | Windsurf处理大文件 | Cursor处理小文件 | Windsurf上下文更长 |
| 中国区 | Trae | — | 字节生态专属 |

### 4.4 Claude Code高级配置

```bash
# Claude Code配置文件 ~/.claude/settings.json
{
  "permissions": {
    "allow": [
      "Write",
      "Read",
      "Edit",
      "RunTerminalCommand",
      "CreateFile",
      "DeleteFile"
    ]
  },
  "projectSettings": {
    "timeoutMs": 300000
  }
}

# Claude Code Agent Teams (v2.1.126+)
claude --agents '{
  "frontend": {
    "description": "前端开发者",
    "prompt": "你是专业前端工程师",
    "tools": ["Read", "Write", "Edit", "RunTerminalCommand"],
    "model": "claude-sonnet-4-20260502"
  },
  "backend": {
    "description": "后端开发者", 
    "prompt": "你是专业后端工程师",
    "tools": ["Read", "Write", "Edit", "RunTerminalCommand"],
    "model": "claude-sonnet-4-20260502"
  }
}'
```

### 4.5 Codex CLI配置

```bash
# 安装
npm install -g @openai/codex

# 认证
export OPENAI_API_KEY="sk-..."

# 使用
codex "实现一个REST API"

# Worktree模式 - 每个任务独立目录
codex --worktree "实现用户模块"

# 并行子Agent (Codex专属)
codex --parallel 3 "分解并实现3个独立模块"
```

---

## 五、MCO编排层（可选增强）

MCO (`mco-org/mco`) 是一个中立的编排层，可在多种Agent间调度任务：

```bash
# 安装
npm install -g mco

# 基本使用
mco run \
  --repo . \
  --prompt "分析项目架构" \
  --providers claude,codex

# 多Agent并行
mco run \
  --repo . \
  --prompt "分解任务并在2个Agent上并行执行" \
  --providers claude,cursor \
  --parallel

# 保存产出物
mco run \
  --repo . \
  --prompt "生成API文档" \
  --providers claude \
  --save-artifacts
```

> 💡 **何时用MCO**：当需要跨Agent联合分析、结果聚合时。日常任务直接走ACP更快。

---

## 六、Git Worktree隔离策略

避免多个Agent同时修改仓库时产生冲突：

```bash
# 每个子任务创建工作树
git worktree add ../project-module-auth feature/auth
git worktree add ../project-module-ui feature/user-ui
git worktree add ../project-module-tests feature/tests

# 每个Agent在自己的工作树中工作
claude --cwd ../project-module-auth "实现认证模块"
cursor ../project-module-ui

# 完成后，在主仓库合并
cd /project
git merge feature/auth
git merge feature/user-ui
git merge feature/tests

# 清理工作树
git worktree remove ../project-module-auth
git worktree remove ../project-module-ui
git worktree remove ../project-module-tests
```

---

## 七、舰队状态看板

配置OpenClaw的 `/acp` 命令监控舰队状态：

```bash
# 查看ACP状态
/acp doctor

# 查看活跃session
/acp sessions

# 停止session
/acp stop <session-id>

# 查看agent状态
/acp status --all
```

### 生产力预估

| 工具 | 单人效率 | 舰队并行效率 | 适合规模 |
|------|---------|------------|---------|
| Claude Code单独 | 1x | 1x | 小项目(<5000行) |
| + Cursor | 1.8x | 2x | 前端+后端分开 |
| + Windsurf | 2.2x | 3x | 分析+执行解耦 |
| + Codex CLI | 3x | 5x | 云端隔离并行 |
| + MCO编排 | 3.5x | 8x | 大规模(10+模块) |
| **完全体舰队** | **4-6x** | **8-12x** | **千人项目规模化** |

---

## 八、故障排除

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `/acp doctor` 报错 | acpx未安装或未启用 | `openclaw plugins install acpx` |
| Cannot find claude | Claude Code未安装 | `npm i -g @anthropic-ai/claude-code` |
| ACP session超时 | 模型响应慢 | 提高 `acp.runtime.ttlMinutes` |
| Worktree冲突 | 多个Agent修改同文件 | 更细致的任务分解 |
| Windsurf CLI找不到 | 路径不对 | 用 `find /Applications/Windsurf.app -name 'windsurf'` 查找 |
| Cursor ACP失败 | Cursor版本不支持 | 升级Cursor到0.48+ |
| Codex需要GPT-5权限 | OpenAI API key权限不足 | 联系OpenAI升级 |

### 诊断命令

```bash
# 一站式诊断
/acp doctor          # ACP健康检查
claude --version     # Claude Code版本
cursor --version     # Cursor版本
codex --version      # Codex版本
mco --version        # MCO版本
```

---

## 九、安全与权限

### ACP权限模式

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| `normal` | 每个操作需要确认 | 新手/重要项目 |
| `bypass` | 自动允许所有操作 | 经验用户/CI |
| `ack` | 仅危险操作确认 | 平衡模式 |

```json5
{
  "acp": {
    "permissionMode": "bypass", // 舰队模式建议bypass
    "permissionBypassCommands": ["Write", "Read", "Edit", "RunTerminalCommand"]
  }
}
```

---

> **轩辕在此。**
> *你的AI编码舰队已就绪——司令塔+6种特战AI工具，随时投入战斗。*
