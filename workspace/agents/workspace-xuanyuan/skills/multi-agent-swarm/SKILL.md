---
name: multi-agent-swarm
description: "工业级多Agent蜂群系统——指挥10+ Agent并行开发的完整框架。覆盖：Agent角色定义、任务分解协议、蜂群调度算法、子Agent通信、冲突消解、质量门禁、OpenClaw原生集成。触发词：蜂群、swarm、多Agent调度、并行开发、Agent集群、任务分解、AI并行开发、swarm intelligence、agent orchestration"
---

# 🐝 多Agent蜂群系统 — Multi-Agent Swarm

> **版本**：v1.0 | **角色**：轩辕 CTO | **适用**：AI集群并行开发
>
> 将CMU蜂群智能理念 + AutoGen/CrewAI模式 + OpenClaw原生API融合为一个可执行框架

---

## 一、核心架构

### 1.1 蜂群拓扑

```
┌──────────────────────────────────────────────────┐
│              蜂王 (Queen Orchestrator)              │
│  轩辕CTO · 任务分解 · 结果聚合 · 质量门禁        │
└──────┬──────────┬──────────┬──────────┬───────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 工蜂-A   │ │ 工蜂-B   │ │ 工蜂-C   │ │ 工蜂-D   │
│ 前端Agent│ │ 后端Agent│ │ 测试Agent│ │ DB Agent │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │
     └────────────┴──────┬─────┴────────────┘
                         ▼
               ┌──────────────────┐
               │   仲裁蜂 (Review) │
               │   质量门禁+冲突消解│
               └──────────────────┘
```

### 1.2 Agent角色模板

| 角色 | 职责 | 工具集 | 模型推荐 | 并发数 |
|------|------|--------|----------|--------|
| **🐝 蜂王 (Queen)** | 任务分解、调度、聚合、汇报 | sessions_spawn, sessions_send, sessions_yield | 顶级推理模型 | 1 |
| **🔧 工蜂-A (Builder-Frontend)** | 前端代码、UI组件、样式 | coding-agent, fullstack-developer | 中高模型 | 1-3 |
| **⚙️ 工蜂-B (Builder-Backend)** | API、业务逻辑、中间件 | backend-architect, api-design | 中高模型 | 1-3 |
| **🧪 工蜂-C (Builder-Test)** | UT/IT/E2E测试 | test-automation, test-driven-dev | 中低模型 | 1-2 |
| **🗄️ 工蜂-D (Builder-DB)** | Schema、迁移、查询优化 | database-master | 中低模型 | 1 |
| **🔍 仲裁蜂 (Reviewer)** | Code Review、冲突消解、质量门禁 | code-reviewer, github-pr-review | 顶级推理模型 | 1 |
| **📡 哨兵蜂 (Ops)** | 进度追踪、健康检查、状态汇报 | project-sdlc-tracker | 基础模型 | 1 |

---

## 二、任务分解协议

### 2.1 分解规则

将大任务按以下维度拆分为并行子任务：

```
输入：PRD / 功能描述 / 用户故事

Step 1 — 层级分解
┌─────────────────────────────────────┐
│ Epic: [功能名]                       │
│  ├── Story-1: 前端页面              │
│  │    ├── Task-1.1: HTML骨架        │
│  │    ├── Task-1.2: CSS样式         │
│  │    └── Task-1.3: JS交互逻辑      │
│  ├── Story-2: 后端API               │
│  │    ├── Task-2.1: 路由定义        │
│  │    ├── Task-2.2: 业务逻辑        │
│  │    └── Task-2.3: 数据验证        │
│  └── Story-3: 数据库                │
│       ├── Task-3.1: Schema设计      │
│       ├── Task-3.2: 迁移脚本        │
│       └── Task-3.3: 查询优化        │
└─────────────────────────────────────┘

Step 2 — 依赖图构建
   A ──→ B ──→ C     (串行：A做完才能B)
   D ──→ E            (并行：D和A可同时开始)
   F ──→ G ──→ H     (条件：C和E都完成才能F开始)

Step 3 — 并行度判定
   - 无依赖 → 立即分发
   - 有依赖 → 等待上游完成
   - 条件依赖 → 上游全部完成后触发
```

### 2.2 任务卡模板

```markdown
## 🎯 Task-[ID]: [任务标题]

**状态**: ⏳ 待分配 | 🏗️ 进行中 | ✅ 完成 | ❌ 失败
**分配至**: @Agent-[name]
**优先级**: P0/P1/P2
**ETA**: [预估小时数]

### 输入
- 上游依赖: Task-[依赖IDs]
- 契约(Schema/接口定义): [链接/内联]
- 参考文件: [路径]

### 验收标准
- [ ] 标准1: 代码无语法错误
- [ ] 标准2: 单元测试通过率>90%
- [ ] 标准3: 接口契约一致
- [ ] 标准4: 无安全漏洞

### 输出路径
- 代码: `/shared/artifacts/[task-id]/`
- 测试: `/shared/artifacts/[task-id]/tests/`
- 文档: `/shared/artifacts/[task-id]/docs/`
```

---

## 三、蜂群调度算法

### 3.1 调度策略

```
调度引擎根据以下规则分配任务：

1. 能力匹配度 — Agent的技能与任务要求相匹配
   match_score = cosine_sim(task_skills_vector, agent_skills_vector)

2. 负载均衡 — 避免某个Agent过载
   load_score = 1 / (current_assigned_tasks + 1)

3. 依赖优先级 — 关键路径上的任务优先
   priority = depth_in_critical_path + upstream_blocked_count * 2

4. 亲和度 — 同一Story的任务尽量分配给同一Agent
   affinity = previous_successful_tasks_by_this_agent / total_tasks_in_story

最终权重: score = 0.4 * match + 0.3 * load + 0.2 * priority + 0.1 * affinity
```

### 3.2 OpenClaw原生调度实现

```python
# 调度伪代码（实际用OpenClaw工具链实现）
class SwarmOrchestrator:
    def decompose(self, epic_task):
        stories = self.break_down(epic_task)
        tasks = self.to_tasks_with_dependencies(stories)
        return DependencyGraph(tasks)

    def schedule(self, graph, agent_pool):
        ready = graph.get_ready_tasks()  # 无阻塞依赖的任务
        for task in ready:
            agent = self.select_best_agent(task, agent_pool)
            self.dispatch(agent, task)
    
    def dispatch(self, agent, task):
        # 使用sessions_spawn启动子Agent
        spawned = sessions_spawn(
            task=self.build_prompt(task),
            label=f"swarm-{task.id}",
            agentId=agent.id,
            mode="run"
        )
        task.session_key = spawned.childSessionKey
    
    def aggregate(self, completed_tasks):
        # 收集所有已完成任务的产出
        results = {}
        for task in completed_tasks:
            results[task.id] = self.verify_deliverable(task)
        
        # 检测冲突
        conflicts = self.detect_conflicts(results)
        if conflicts:
            self.resolve_via_arbiter(conflicts)
        
        return self.merge_results(results)
```

### 3.3 实际调用模板（直接可用）

```markdown
# 蜂王调度模板

## Step 1: 任务分解
「天工PRD已完成分解。任务拓扑如下：
  - Task-001: 前端登录页面（@工蜂-A，3h，无依赖）
  - Task-002: 后端Auth API（@工蜂-B，2h，无依赖）
  - Task-003: 用户数据库Schema（@工蜂-D，1h，无依赖）
  - Task-004: 端到端测试（@工蜂-C，2h，依赖001&002）
  预期3h后全部完成。」

## Step 2: 并行分发
sessions_spawn:
  - task: "实现Task-001: React登录页面，含表单验证..."
    label: swarm-T001
  - task: "实现Task-002: FastAPI Auth端点，JWT签发..."
    label: swarm-T002
  - task: "实现Task-003: PostgreSQL用户表，含迁移脚本..."
    label: swarm-T003
  # Task-004等待001和002完成后再触发

## Step 3: 聚合验收
「Task-001,002,003已完成。仲裁蜂开始Review。
  检测到冲突：前端期望的login API路径与后端实现不一致。
  仲裁蜂已自动消解：统一为 /api/v1/auth/login。」
```

---

## 四、子Agent通信协议

### 4.1 消息格式

```json
{
  "protocol": "swarm/v1",
  "messageId": "msg-001",
  "from": "agent-builder-frontend-1",
  "to": ["agent-builder-backend-1", "queen"],
  "type": "deliverable | dependency_request | conflict | status_update",
  "payload": {
    "taskId": "T001",
    "artifactPath": "/shared/artifacts/T001/",
    "contract": { "api": "POST /api/v1/login", "body": {"email", "password"} },
    "status": "completed",
    "issues": []
  },
  "timestamp": "2026-05-04T08:00:00Z"
}
```

### 4.2 状态同步

```
状态枚举:
  ┌─────────────┐
  │ ASSIGNED    │ ← 已分配
  │ IN_PROGRESS │ ← 进行中
  │ BLOCKED     │ ← 阻塞（需蜂王介入）
  │ REVIEW      │ ← 待评审
  │ COMPLETED   │ ← 完成
  │ FAILED      │ ← 失败（自动通知蜂王）
  └─────────────┘

同步机制:
  1. 子Agent每完成一个里程碑 → 自动sessions_send汇报给蜂王
  2. 蜂王每10分钟轮询一次整体进度
  3. BLOCKED状态自动触发升级通知
```

---

## 五、冲突消解机制

### 5.1 冲突类型与消解策略

| 冲突类型 | 典型场景 | 自动消解策略 | 人工介入条件 |
|----------|----------|-------------|-------------|
| **接口冲突** | 前端期望字段名与后端不一致 | 仲裁蜂统一协调，取最优命名 | 双方争议超过3轮 |
| **数据冲突** | 两个模块同时修改同一表 | 按Task依赖顺序合并 | 数据完整性受损 |
| **逻辑冲突** | 同一功能的不同实现方式 | A/B方案对比，取性能更优 | 两种方案无显著优劣 |
| **约定冲突** | 代码风格/命名规范不一致 | 强制使用BEER编码规则格式化 | — |
| **资源冲突** | 两个Agent竞争同一端口/文件 | 蜂王重新分配互斥资源 | 冲突无可避免时 |

### 5.2 仲裁流程

```
1. 冲突检测 → 自动识别冲突类型
2. 仲裁蜂分析 → 生成合并方案
3. 双方Agent确认 → 自动执行合并
4. 回归验证 → 确认合并后无副作用

仲裁蜂裁决示例：
「检测到冲突：前端Task-001使用"user_name"，后端Task-002使用"username"。
 仲裁决定：统一使用"username"（符合BEER简短命名原则）。
 后端保持不变，前端Task-001需更新，预计耗时15分钟。」
```

---

## 六、质量门禁

### 6.1 子任务验收标准

```
┌─────────────────────────────────────┐
│          质量门禁矩阵                 │
├─────────────────────────────────────┤
│ ① 编译/语法检查     ████████░░ 80%  │
│ ② 单元测试覆盖率    ████████░░ 80%  │
│ ③ 接口契约一致      ██████████ 100% │
│ ④ 代码风格(BEER)    ██████░░░░ 60%  │
│ ⑤ 安全漏洞(Trivy)   ██████████ 100% │
│ ⑥ 文档完整性        ████░░░░░░ 40%  │
│                                   │
│ 通过阈值: 所有项≥80% ✅             │
└─────────────────────────────────────┘
```

### 6.2 OpenClaw集成

```markdown
# 实战：使用swarm构建用户系统

## 蜂王部署
「收到天工PRD：用户注册/登录/权限系统」

## 任务分解（2分钟）
「复杂度评估: Medium（3个Story, 8个Task）
 依赖图:
   T001(前端注册页) ─┐
   T002(后端注册API) ├──→ T004(集成测试)
   T003(用户数据库) ─┘

 并行分配:
   @工蜂-A → T001 (前端)
   @工蜂-B → T002 (后端)
   @工蜂-D → T003 (DB)」

## 蜂群执行
sessions_spawn(task="T001: 注册页...", label="swarm-T001")
sessions_spawn(task="T002: 注册API...", label="swarm-T002")
sessions_spawn(task="T003: 用户表...", label="swarm-T003")

## 结果聚合（3小时后）
「Task-001 ✅ 前端注册页完成
 Task-002 ✅ 后端API完成
 Task-003 ✅ 数据库完成

 仲裁蜂Review:
   ✅ 接口契约一致 (POST /api/v1/auth/register)
   ✅ 测试覆盖92%
   ⚠️ 冲突已消解：前端期待的响应格式与后端修正一致

 质量门禁: 95% ✅ 通过」
```

---

## 七、与轩辕现有体系的集成

### 7.1 与AGENTS.md的SDLC 4.0对接

```
SDLC 4.0 Step 2 (并行开发) → 直接调用本蜂群系统
SDLC 4.0 Step 3 (自愈循环) → 仲裁蜂自动处理
SDLC 4.0 Step 4 (部署)     → 结果聚合后交给CI/CD流水线
```

### 7.2 能力依赖

本skill依赖以下现有技能：
- `sessions_spawn` / `sessions_yield` (OpenClaw原生)
- `coding-agent` (执行编码)
- `code-reviewer` (评审)
- `project-sdlc-tracker` (进度追踪 — 配套P0技能)

---

## 八、常见陷阱

| 陷阱 | 后果 | 解决方法 |
|------|------|----------|
| 任务分解太粗 | Agent串行化，无并行收益 | 粒度控制在每个Task<4小时 |
| 通信过于频繁 | 上下文膨胀，token浪费 | 只在里程碑事件时通信 |
| 忽略依赖图 | 下游Agent空转等待 | 先画依赖图再分配 |
| 仲裁蜂不独立 | 所有Agent互相包庇 | 仲裁蜂必须用顶级模型独立运行 |
| 没有超时机制 | 某个Agent死循环拖慢全队 | 设置任务超时（默认4h，可配置） |

---

**轩辕在此。** 🔧
*多Agent蜂群系统 v1.0 | 蜂王调度 + 仲裁消解 + 质量门禁*
