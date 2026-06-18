# 悬赏验收

Bounty任务验收标准定义与执行指南。

## 验收标准定义框架

### 验收标准组成
```
每个Bounty任务验收标准包含三部分：
1. 功能验收 → 是否按规格实现
2. 质量验收 → 代码/测试/文档标准
3. 过程验收 → 提交/沟通/响应规范
```

### 标准模板
```markdown
## 验收标准

### 功能验收（Must Pass）
- [ ] 功能A：输入X → 输出Y
- [ ] 功能B：异常场景 → 正确处理
- [ ] 边界C：空值/零值/NULL处理
- [ ] 集成D：与现有模块兼容

### 质量验收
- [ ] 代码通过Lint检查（无Error/Warning）
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试通过率 100%
- [ ] 无安全隐患（SQL注入/XSS等）

### 过程验收
- [ ] PR描述清晰完整
- [ ] 变更日志更新
- [ ] 文档/注释更新
- [ ] 提交信息规范
- [ ] 24h内回应Review
```

### 可测量原则
```
❌ 模糊标准：
"代码质量良好"
"用户界面友好"

✅ 可测量标准：
"Lint检查零Error，零Warning"
"页面加载时间 < 2s (Fast 3G)"
"表单提交成功率 100% (Puppeteer自动化测试)"
"代码覆盖率 ≥ 80%（排除生成代码）"
```

## 自动化测试验证

### CI验收流程
```yaml
# .github/workflows/bounty-acceptance.yml
name: Bounty Acceptance
on: [pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Lint
        run: npx eslint . --max-warnings=0
      
      - name: Unit Tests
        run: npx jest --coverage --coverageThreshold='{"global":{"lines":80}}'
      
      - name: Integration Tests
        run: npm run test:integration
      
      - name: E2E Tests
        run: npm run test:e2e
      
      - name: Security Scan
        uses: github/codeql-action/analyze@v3
```

### 自动化验收清单
```python
# acceptance_checklist.py
def run_acceptance_checks(pr_url):
    checks = {
        "lint_pass": run_lint(pr_url),
        "unit_tests": run_unit_tests(pr_url),
        "coverage_80": get_coverage(pr_url) >= 80,
        "integration_pass": run_integration_tests(pr_url),
        "security_scan": run_security_scan(pr_url),
    }
    
    results = {k: v for k, v in checks.items()}
    results["pass"] = all(v for v in checks.values())
    return results
```

## 人工Review检查清单

### Review维度

| 维度 | 检查项 | 权重 |
|------|--------|------|
| 功能正确性 | 是否满足需求规格 | 40% |
| 代码质量 | 可读性/架构/安全 | 30% |
| 测试覆盖 | 测试完整性 | 20% |
| 文档与提交 | 文档/注释/提交信息 | 10% |

### Review检查项
```
功能正确性（40分）
▢ 所有功能场景覆盖（20分）
▢ 边界条件处理（10分）
▢ 错误处理完整（10分）

代码质量（30分）
▢ 符合编码规范（10分）
▢ 架构合理（5分）
▢ 无安全漏洞（10分）
▢ 无性能问题（5分）

测试覆盖（20分）
▢ 单元测试覆盖核心逻辑（10分）
▢ 集成测试覆盖关键场景（5分）
▢ 无flaky测试（5分）

文档与提交（10分）
▢ 代码注释合理（3分）
▢ 变更日志更新（3分）
▢ 提交信息规范（4分）

评分：≥ 85分 → 优秀 (Full Reward)
      70-84分 → 良好 (90% Reward)
      60-69分 → 及格 (70% Reward)
      < 60分 → 不通过 (需修改)
```

## 验收结果分级

### 结果分类
```
✅ PASS：所有标准通过 → 全额发放悬赏
⚠️ CONDITIONAL：轻微问题 → 修复后发放
❌ FAIL：重大问题 → 退回修改，不发放悬赏
```

### 具体标准
| 等级 | 要求 | 处理 |
|------|------|------|
| PASS | 所有验收标准100%通过 | 24h内发放悬赏 |
| CONDITIONAL | 非阻塞性问题 ≤ 3个 | 作者48h修复，复验通过后发放 |
| FAIL | 功能缺失/阻塞问题/严重安全漏洞 | 退回，可重新提交（计入历史） |

### 非通过处理流程
```
CONDITIONAL流：
Review反馈问题 → 作者修复（48h）→ 复验通过 → 发放
                                      ↓
                                  超时未修复 → 自动降为FAIL

FAIL流：
退回 → 作者重新提交 → 重新评估
       ↓
   连续3次FAIL → 该Bounty收回重新挂牌
```

## 验收执行Checklist

- [ ] 验收标准在Bounty发布时明确
- [ ] 自动化验收CI集成
- [ ] 人工Review在24h内完成
- [ ] 不符合标准及时反馈
- [ ] 验收结果记录归档
- [ ] 悬赏发放流程清晰
- [ ] 历史记录追踪（贡献者信用）
