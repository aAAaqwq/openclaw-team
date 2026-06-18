# PR审查

Pull Request审查规范与效率优化指南。

## PR模板设计

### 标准PR模板
```markdown
## 概述
**功能**: [功能名称]
**关联Issue**: #[issue_number]
**优先级**: 🔴紧急 / 🔵高 / 🟡中 / 🟢低

## 变更内容
- [x] 新增功能A
- [ ] 修复Bug B
- [ ] 重构模块C
- [ ] 更新文档

## 自测清单
- [ ] 本地测试通过
- [ ] 无新Lint Warning
- [ ] 测试覆盖率 ≥ 80%
- [ ] 人工验证过变更场景
- [ ] 无调试代码遗留

## 影响范围
- [ ] 数据库变更（需Migrations）
- [ ] API变更（需更新文档）
- [ ] UI变更（需截图）
- [ ] 配置文件变更
- [ ] 依赖变更

## 部署注意事项
- [ ] 需要滚动重启
- [ ] 需要数据库迁移
- [ ] 需要更新配置
- [ ] 存在向后兼容问题

## Review重点
_请Review者重点关注以下部分的逻辑正确性_：
```

## 自动CI/CD集成

### GitHub Actions配置
```yaml
name: PR Checks
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Lint
        run: npm run lint
      
      - name: Type Check
        run: npm run type-check
      
      - name: Unit Tests
        run: npm run test -- --coverage
      
      - name: Bundle Size
        run: npx bundlesize
      
      - name: E2E Tests (Smoke)
        run: npm run test:e2e:smoke

  draft-label-check:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'draft')
    steps:
      - name: Block merge for draft PRs
        run: exit 1  # 阻止合并WIP PR
```

### CI检查状态集成
| 检查项 | 阻塞 | 非阻塞 | 超时 |
|--------|------|--------|------|
| Lint | ✅ | — | 2min |
| Type Check | ✅ | — | 3min |
| Unit Tests | ✅ | — | 5min |
| Integration Tests | ✅ | — | 10min |
| E2E Tests | — | ✅ | 15min |
| Security Scan | ✅ | — | 5min |
| Bundle Size | ✅ | — | 1min |

## 变更范围分析

### 变更类型评估
```python
def analyze_pr_changes(pr):
    changes = {
        "total_lines": pr.additions + pr.deletions,
        "files_changed": len(pr.files),
        "complexity": 0,
        "risk": "low"
    }
    
    # 复杂度评估
    if changes["total_lines"] > 500:
        changes["complexity"] += 3
    elif changes["total_lines"] > 200:
        changes["complexity"] += 1
    
    # 高敏感路径变更
    high_risk_patterns = [
        "payment", "auth", "security", "migration"
    ]
    for file in pr.files:
        if any(p in file for p in high_risk_patterns):
            changes["complexity"] += 2
    
    # 风险等级
    if changes["complexity"] >= 5:
        changes["risk"] = "high"
    elif changes["complexity"] >= 3:
        changes["risk"] = "medium"
    
    return changes
```

### PR拆分建议
```
大PR（> 500行变更）建议拆分为：

1. 基础设施 → 配置/依赖/工具类（小修改）
2. 核心逻辑 → 业务逻辑变更（核心）
3. 界面/展示 → 前端/视图层
4. 测试 → 单元测试/集成测试
5. 文档 → README/API文档/Changelog

最佳单PR大小：100-300行变更
一个PR解决一个问题
```

## 审查效率优化

### 批量审查技术
```
1. 阅读模式：只看逻辑主干，忽略格式
2. 差异模式：对比修改前后，理解意图
3. 抽样模式：随机抽样10%代码，评估整体质量（适合大PR）
4. 焦点模式：集中审查高风险变更（安全/支付）
```

### 快捷键与工具
| 工具 | 快捷键/技巧 | 效果 |
|------|------------|------|
| GitHub | `t` → 文件搜索 | 快速定位 |
| GitHub | `SHIFT+.` → 代码编辑器 | 直接编辑 |
| VS Code | GitHub Pull Request插件 | 本地Review |
| VS Code | 文件对比 | Split Diff |

### 分阶段审查策略
```
第一阶段（5min）：概览
- 阅读PR描述
- 检查CI状态
- 浏览变更文件列表

第二阶段（15min）：核心逻辑
- 审查主要功能变更
- 检查安全风险
- 验证测试用例

第三阶段（10min）：细节
- 检查命名/格式（交给Lint）
- 检查边界条件
- 检查文档

总时间目标：
- <200行：20min
- 200-500行：30min
- >500行：拆分后Review
```

## PR审查Checklist

- [ ] PR描述完整
- [ ] CI全部通过
- [ ] 无安全风险
- [ ] 无性能退化
- [ ] 测试覆盖合理
- [ ] 文档同步更新
- [ ] 变更范围合理
- [ ] 24h内完成Review
- [ ] 反馈明确分级（Must Fix / Suggestion / Nitpick）
- [ ] 标识风险等级
