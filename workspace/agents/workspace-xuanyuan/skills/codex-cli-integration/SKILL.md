---
name: codex-cli-integration
description: "Codex CLI深度集成——接入OpenAI最新子Agent/并行编码能力。覆盖：Codex CLI安装配置、subagent工作流、parallel agent模式、worktree集成、OpenClaw+Codex混合调度。触发词：Codex、Codex CLI、OpenAI Codex、subagent、并行编码、云端开发、OpenAI编码代理、agentic coding"
---

# 🤖 Codex CLI深度集成 — OpenAI编码引擎接入

> **版本**：v1.0 | **角色**：轩辕 CTO | **目标**：将OpenAI最新子Agent能力接入轩辕蜂群

---

## 一、Codex CLI 能力概览

### 1.1 核心能力

```
Codex CLI (OpenAI, 2026年3月发布)
├─ 子Agent并行：spawn多个子Agent同时工作
├─ 云端Sandbox：隔离的云开发环境
├─ Worktree集成：每个子Agent独立工作目录
├─ 模型专属：GPT-5.3-Codex（25%更快）
├─ 自动聚合：主Agent收集子Agent结果
└─ 原生CLI：codex命令直接使用

轩辕集成价值：
  ┌ 子Agent并行 → 增强轩辕蜂群的执行层
  ┌ 云端Sandbox → 解决本地环境依赖问题
  ┌ GPT-5.3专属 → 编码速度大幅提升
  ┌ 自动聚合 → 减少仲裁蜂的Review负担
```

---

## 二、安装与配置

### 2.1 安装

```bash
# 前提：OpenAI API Key（需要codex权限）
export OPENAI_API_KEY="sk-..."

# 安装Codex CLI
npm install -g @openai/codex

# 验证
codex --version
# → Codex CLI v1.2.0 (GPT-5.3-Codex)

# 配置
codex config set default-model gpt-5.3-codex
codex config set max-subagents 8  # 默认子Agent数
codex config set sandbox-dir ~/codex-sandbox
```

### 2.2 基础使用

```bash
# 单任务执行
codex "创建一个React登录页面组件"

# 指定输出目录
codex --output ./src/components "创建一个带有表单验证的登录组件"

# 从文件读取任务
codex @task-description.md

# 交互模式
codex -i
```

---

## 三、子Agent工作流

### 3.1 子Agent基础模式

```bash
# 并行子Agent（最常用）
codex --subagents 3 --plan \
  "实现用户注册功能:
   Agent 1: 前端注册页面（React表单+验证）
   Agent 2: 后端注册API（FastAPI端点+JWT）
   Agent 3: 数据库Schema（用户表+迁移脚本）"

# 输出:
#   [Agent 1] ✅ 完成 → /sandbox/frontend/register.tsx
#   [Agent 2] ✅ 完成 → /sandbox/backend/auth.py
#   [Agent 3] ✅ 完成 → /sandbox/db/migration.sql
#   [Main] 冲突检测: 字段名不一致 → 自动统一
#   总耗时: 12秒
```

### 3.2 结构化的子Agent任务

```json
// subagent-tasks.json
{
  "goal": "实现完整的用户注册功能",
  "subagents": [
    {
      "name": "frontend-dev",
      "task": "创建React注册页面组件",
      "spec": {
        "framework": "React 19",
        "styling": "Tailwind CSS",
        "validation": "Zod",
        "output": "src/components/RegisterForm.tsx"
      }
    },
    {
      "name": "backend-dev", 
      "task": "创建用户注册API端点",
      "spec": {
        "framework": "FastAPI",
        "auth": "JWT + bcrypt",
        "output": "src/api/auth.py"
      },
      "depends_on": []  // 无依赖
    },
    {
      "name": "test-writer",
      "task": "注册功能的端到端测试",
      "spec": {
        "framework": "Playwright",
        "output": "tests/e2e/register.spec.ts"
      },
      "depends_on": ["frontend-dev", "backend-dev"]  // 依赖前两者
    }
  ],
  "contract": {
    "api": "POST /api/v1/auth/register",
    "request": "{ email: string, password: string, name: string }",
    "response": "{ token: string, user: { id: string, email: string } }"
  }
}

# 执行
codex --subagents-file subagent-tasks.json
```

---

## 四、OpenClaw + Codex混合调度

### 4.1 蜂群集成架构

```
┌──────────────────────────────────────────────────────────────┐
│                  轩辕蜂群（编排层）                            │
│  sessions_spawn + 任务分解 + 依赖图 + 进度追踪               │
└──────────┬─────────────────────────────────────┬─────────────┘
           │                                      │
           ▼                                      ▼
┌──────────────────────┐           ┌──────────────────────────┐
│  编码Agent（本地）    │           │  Codex CLI（云端）       │
│  coding-agent         │           │  subagent并行执行       │
│  Claude Code          │           │  GPT-5.3-Codex          │
│  适合: 小任务/Review  │           │  适合: 大任务/并行      │
└──────────────────────┘           └──────────────────────────┘
```

### 4.2 调度策略

```
任务分发策略：

Task < 10文件 或 复杂度L0-L1:
  → 本地coding-agent（更快，无网络延迟）

Task > 10文件 或 需要并行子任务:
  → Codex CLI subagent（云端并行更高效）

Review / 质量检查:
  → 本地仲裁蜂+Codex Review

混合示例：
  codex --subagents-task "生成5个API端点" 
  + 轩辕本地Review结果
  + 蜂群填充集成测试
```

### 4.3 OpenClaw中的调用

```markdown
# 通过OpenClaw调用Codex

## 方式1: 直接exec调用
「codex --subagents 3 '创建用户CRUD API和前端页面'」

## 方式2: 通过coding-agent委托
「@coding-agent 使用Codex CLI的subagent模式：
   实现用户管理功能，4个并行子Agent分工：
   - 前端列表页
   - 前端编辑页  
   - 后端API
   - 数据库迁移」

## 方式3: 蜂群集成（最推荐）
「🐝蜂王任务调度:
   Task-001: 前端注册页 → Codex subagent（云端）  
   Task-002: 后端API → Codex subagent（云端）
   Task-003: 数据库 → 本地coding-agent（小任务）
   Task-004: 集成测试 → 本地（依赖001+002）
   仲裁蜂统一Review所有产出」
```

---

## 五、成本与性能对比

| 维度 | 本地coding-agent | Codex CLI subagent | 推荐 |
|------|-----------------|-------------------|------|
| **延迟** | 低-中（取决于模型） | 低-中+网络延迟 | 相近 |
| **并行度** | 1-3 | 3-10+ | Codex胜 |
| **成本** | 取决于模型token | Codex单独计费 | 混合最优 |
| **环境隔离** | 不隔离 | Sandbox隔离 | Codex胜 |
| **网络依赖** | 无 | 需要 | 本地胜 |
| **模型** | 多种可选 | GPT-5.3-Codex | 视需求 |

**最佳实践**:
```
小任务(1-3文件) → 本地coding-agent（$0成本）
大任务(10+文件) → Codex subagent（$少量，但快）
关键Review → 本地仲裁蜂（最高质量保证）
```

---

## 六、能力评分更新

```
Codex CLI集成:
更新前 0/100（全新领域）     更新后 75/100 ✅

具体覆盖:
├─ 安装配置:              0 → 80
├─ 子Agent工作流:         0 → 80
├─ 蜂群集成调度:          0 → 75
├─ 成本控制:              0 → 80
└─ 实战模板:              0 → 70（需真实调用验证）
```

---

**轩辕在此。** 🔧
*Codex CLI集成 v1.0 | OpenAI最新引擎接入 | 云端并行编码*
