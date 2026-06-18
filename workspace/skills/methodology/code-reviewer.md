# Code Review

代码审查规范与实践指南。

## Review检查清单

### 安全性
- [ ] SQL注入防护（参数化查询/ORM）
- [ ] XSS防护（输出转义）
- [ ] CSRF防护
- [ ] 认证鉴权检查（接口权限验证）
- [ ] 敏感信息泄露（密钥/Token/日志）
- [ ] 文件上传安全（类型/大小检查）
- [ ] 速率限制/资源过度使用

### 性能
- [ ] N+1查询检测
- [ ] 不必要的循环内数据库调用
- [ ] 大对象/大列表处理（分页/流式）
- [ ] 缓存策略合理性
- [ ] 锁竞争/死锁风险
- [ ] 资源释放（文件句柄/数据库连接）
- [ ] 前端资源加载优化

### 可读性与维护性
- [ ] 命名清晰（变量/函数/类）
- [ ] 函数单一职责（≤50行）
- [ ] 注释合理（解释Why而非What）
- [ ] 断言/错误处理全面
- [ ] 日志级别合适（Error/Warn/Info）
- [ ] 魔法数字提取为常量
- [ ] 复杂逻辑有代码注释

### 架构与设计
- [ ] 遵循当前架构模式（DDD/MVC/分层）
- [ ] 不引入不必要的新依赖
- [ ] 接口抽象合理
- [ ] 模块间解耦
- [ ] 数据流清晰
- [ ] 扩展性考虑（配置化/插件化）

## 自动化审查工具集成

### 提交前（Pre-commit Hook）
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
      - id: ruff-format
```

### CI自动审查
```yaml
# GitHub Actions
name: Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint
        run: npx eslint . --max-warnings=0
      - name: Type Check
        run: npx tsc --noEmit
      - name: Test
        run: npm test -- --coverage
      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v3
```

### 常用Lint工具
| 语言 | Linter | 安全扫描 |
|------|--------|----------|
| JavaScript/TS | ESLint + Prettier | eslint-plugin-security |
| Python | Ruff / pylint | bandit / safety |
| Go | golangci-lint | gosec |
| Rust | clippy | cargo-audit |
| Java | Checkstyle / SpotBugs | FindSecBugs |

## 反馈最佳实践

### 三种反馈级别
```
必须改（Blocking）：安全漏洞、逻辑错误、数据丢失风险
建议改（Non-blocking）：性能优化、代码风格、重构建议
可选改（Nitpick）：小优化、个人偏好

规则：
- 一次Review至少包含1条Must Fix
- Must Fix不超过代码行数10%
- 每条反馈必须有理由
```

### 反馈示例
```markdown
## 反馈

### Must Fix 🔴

1. **SQL注入风险**（line 42）
   ```python
   # ❌ 字符串拼接
   cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
   
   # ✅ 参数化查询
   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   ```

2. **缺少认证**（line 78）
   接口`/admin/users`未检查管理员权限

### Suggested 🔵

1. **日志级别太高**（line 15）
   `print()` → `logger.info()` 或 `logger.debug()`

### Nitpick ⚪

1. 函数命名建议用动词开头：`user_process` → `process_user`
```

### Review流程规范
```
紧急Review（Hotfix/生产问题）：
1. 直接找作者Pair Review
2. 修复后补正式Review

常规Review：
1. Reviewer 24h内完成首次review
2. 作者48h内回应所有反馈
3. 再次review在24h内
4. 三次循环后仍未解决 → 升级到团队讨论

Review速度目标：
- <200行变更：30分钟内
- <500行变更：1小时内
- >500行变更：拆分为多次PR
```

## Code Review流程模板

```markdown
## PR概览
**变更说明**: 
**影响范围**: 
**测试覆盖**: 
**风险等级**: ⚪低 / 🔵中 / 🔴高

## 审查结果
- [ ] 无严重问题，批准合并
- [ ] 有建议修改，改后可合并
- [ ] 有必须修改的问题

## 备注
```

## 检查清单总结

### 作者提交前自查
- [ ] 代码编译通过，测试全绿
- [ ] 无TODO/FIXME遗留
- [ ] 无调试代码（console.log/print）
- [ ] 遵循当前的编码规范
- [ ] 已更新文档/注释
- [ ] PR描述完整
- [ ] 变更范围最小（单一职责）

### Reviewer核心检查
- [ ] 不过分解读格式（交给自动化工具）
- [ ] 关注逻辑正确性和安全性
- [ ] 关注可测试性
- [ ] 及时反馈（24h内）
- [ ] 态度友善，对事不对人
