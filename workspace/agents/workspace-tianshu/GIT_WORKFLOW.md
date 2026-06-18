# 【天枢】GIT_WORKFLOW.md — 代码化运营工作流
## Git-based Operations Workflow for Tianshu COO

> **版本**：v1.0  
> **角色**：天枢 (Tianshu)  
> **对标**：GitHub / Git Flow 最佳实践 + 文档即代码(Docs-as-Code)  
> **技能引用**：`git-workflow`

---

## 一，天枢的Git工作空间

### 1.1 仓库结构

```
tianshu/                          # 天枢工作空间（Git仓库）
├── AGENTS.md                     # 工作空间规则（核心宪章）
├── SOUL.md                       # 身份与人格
├── IDENTITY.md                   # 身份卡
├── USER.md                       # 服务对象
├── MEMORY.md                     # 长期记忆
├── HEARTBEAT.md                  # 心跳节律
├── EVOLUTION.md                  # 进化配置
├── SKILL.md                      # 技能清单
├── TOOLS.md                      # 工具环境
│
├── DASHBOARD.md                  # 运营指标看板 (Phase 1)
├── AGENT_PROFILES.md             # Agent能力画像 (Phase 1)
├── REVIEW_TEMPLATE.md            # 复盘模板 (Phase 1)
├── GIT_WORKFLOW.md               # 本文件 (Phase 1)
│
├── archive/                      # 归档存储
│   ├── reviews/                  # 复盘记录
│   ├── battle-logs/              # 战役日志
│   └── reports/                  # 报告存档
│
├── memory/                       # 内存存储
│   ├── okr.md                    # OKR追踪
│   └── kpi.md                    # KPI追踪
│
└── skills/                       # 技能目录（ClawHub安装）
    ├── executive-dashboard/
    ├── business-intelligence/
    └── ...
```

### 1.2 文件命名规范

- **语言**：全大写文件名 + 下划线（如 `REVIEW_TEMPLATE.md`）
- **版本**：文件头部标注 `> **版本**：v1.0`
- **日期**：所有日期使用 `YYYY-MM-DD` ISO格式
- **编码**：UTF-8
- **换行**：Unix LF

---

## 二，Git Flow 基础规范

### 2.1 分支策略

```
main                    # 🟢 稳定版本，仅合并已完成战役
  │
  ├── develop            # 🟡 开发分支，日常作战集成
  │     │
  │     ├── feature/xxx  # 🔵 新战役/任务分支
  │     └── fix/xxx      # 🔴 修复分支
  │
  ├── release/v1.x      # 🟣 发布候选
  │
  └── hotfix/xxx        # 🔥 紧急修复（从main切出）
```

### 2.2 分支命名

```
feature/<战役名称>      # 如 feature/phase1-dashboard
fix/<修复内容>           # 如 fix/review-template-format
hotfix/<紧急修复>        # 如 hotfix/critical-bug
release/v<版本>         # 如 release/v1.0
docs/<文档内容>          # 如 docs/git-workflow
```

### 2.3 Commit Message 规范

格式：`<类型>(<范围>): <描述>`

| 类型 | 含义 | 示例 |
|:----:|------|------|
| feat | 新功能 | `feat(dashboard): 新增12项KPI追踪` |
| fix | 修复 | `fix(template): 修复复盘评分格式` |
| docs | 文档 | `docs(git): 新增Git工作流规范` |
| perf | 性能 | `perf(agent): 优化Agent调度响应时间` |
| refactor | 重构 | `refactor(memory): 重构记忆存储结构` |
| chore | 运维 | `chore(cron): 调整心跳频率` |
| review | 复盘 | `review(battle): 完成Phase1战役复盘` |

---

## 三，版本管理

### 3.1 版本号规则

遵循 **SemVer**（语义化版本）：`MAJOR.MINOR.PATCH`

| 位 | 变更类型 | 示例 |
|:-:|---------|:----:|
| **MAJOR** | 不兼容的架构变更 | v2.0.0 |
| **MINOR** | 向下兼容的新功能 | v1.1.0 |
| **PATCH** | 向下兼容的修补 | v1.0.1 |

### 3.2 Release 流程

```
1. 将所有feature分支合并到 develop
2. 创建 release/vX.Y 分支
3. 在release分支上只做bug修复
4. 标记 Release Tag
5. 合并到 main + develop
```

### 3.3 版本历史记录

在文件头部使用changelog：

```markdown
> **版本**：v1.0  
> **变更**：
> - [YYYY-MM-DD] v1.0 初始版本
> - [YYYY-MM-DD] v1.1 新增XX功能
```

---

## 四，文档即代码（Docs-as-Code）

### 4.1 文档标准

每个文档文件必须包含：

```markdown
# 【天枢】[文件名] — [标题]
## [副标题]

> **版本**：v1.0  
> **角色**：天枢 (Tianshu)  
> **更新方式**：[更新频率]
> **对标**：[对标来源]

---

[正文内容]

---

**天枢在此。** ⚔️  
*[文件名] v[版本]*
```

### 4.2 文档分类

| 类别 | 前缀 | 特性 | 示例 |
|:----:|:----:|------|:----:|
| **核心配置** | 无前缀 | 不常变更 | `SOUL.md`, `AGENTS.md` |
| **运营资产** | 无前缀 | 定期更新 | `DASHBOARD.md`, `AGENT_PROFILES.md` |
| **模板** | 以TEMPLATE结尾 | 填充使用 | `REVIEW_TEMPLATE.md` |
| **归档** | 存于archive/ | 只读历史 | `archive/reviews/` |
| **内存** | 存于memory/ | 程序读写 | `memory/okr.md` |

### 4.3 文档生命周期

```
创建 → 首次审核 → 日常更新 → 版本标记 → 归档/退役
  ↑                                         │
  └─────────────────────────────────────────┘
              (重大变更时重新创建)
```

---

## 五，协作规范

### 5.1 PR（Pull Request）规范

每次重大变更需要通过PR合并：

```
PR标题：<类型>(<范围>): <描述>

PR模板：
## 变更内容
- [变更1]
- [变更2]

## 原因
[为什么做这个变更]

## 影响范围
[涉及的文件列表]

## 验证
- [ ] 文档格式检查通过
- [ ] 关联文件引用已更新
- [ ] INDEX文件已同步
```

### 5.2 Code Review 清单

```
[ ] 文件名是否符合规范
[ ] 版本号是否已更新
[ ] 日期格式是否正确
[ ] 引用链接是否有效
[ ] 格式是否一致（Markdown）
[ ] 内容是否有事实错误
[ ] 是否与已有资产冲突
[ ] 是否遵循模板标准
```

---

## 六，自动化目标（Phase 2+）

### 6.1 计划中的自动化

| 自动化项 | 目标Phase | 实现方式 | 状态 |
|---------|:---------:|---------|:----:|
| 提交前格式检查 | Phase 2 | Git Hook + lint | ⏳ 计划中 |
| 自动版本号 | Phase 2 | CI Pipeline | ⏳ 计划中 |
| DASHBOARD自动更新 | Phase 3 | 数据管道 | ⏳ 计划中 |
| 复盘报告自动生成 | Phase 3 | Agent自动化 | ⏳ 计划中 |
| Release自动打包 | Phase 3 | GitHub Actions | ⏳ 计划中 |

### 6.2 Git Hook 预配置

```bash
# pre-commit: 检查文件名规范
# pre-push: 检查引用完整性
# commit-msg: 检查commit格式
```

---

## 七，快速参考

### 7.1 日常命令速查

```bash
# 创建新战役分支
git checkout -b feature/<战役名称> develop

# 提交变更
git add <文件>
git commit -m "feat(<范围>): <描述>"

# 合并到develop
git checkout develop
git merge --no-ff feature/<战役名称>

# 创建Release
git checkout -b release/v1.0 develop
git tag v1.0.0
```

### 7.2 常见问题

| 问题 | 解决方法 |
|------|---------|
| 提交错了分支 | `git reset HEAD~1` 后切分支 |
| 误删了文件 | `git checkout -- <文件>` |
| 想要恢复历史版本 | `git reflog` 找到SHA |
| 合并冲突 | 手动解决后 `git add` + `git commit` |

---

**天枢在此。** ⚔️  
*Phase 1 交付物 #4 · Git工作流规范 v1.0*  
*对标：GitHub Flow + SemVer + Docs-as-Code*
