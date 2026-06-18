# API设计

REST/GraphQL/gRPC API 全栈设计规范与实践。

## 协议选型矩阵

### REST
| 场景 | 推荐 | 不推荐 |
|------|------|--------|
| CRUD资源操作 | ✅ 天然匹配 | — |
| 客户端多样（Web/iOS/Android） | ✅ 生态最好 | — |
| 复杂查询/聚合 | ❌ N+1问题 | — |
| 实时双向通信 | ❌ 需额外WebSocket | — |

### GraphQL
| 场景 | 推荐 | 不推荐 |
|------|------|--------|
| 前端需要灵活数据组合 | ✅ 完美 | — |
| 多数据源聚合 | ✅ 单入口 | — |
| 性能敏感（缓存难） | — | ❌ 细粒度控制困难 |
| 文件上传 | — | ❌ 原生支持弱 |

### gRPC
| 场景 | 推荐 | 不推荐 |
|------|------|--------|
| 微服务间通信 | ✅ 高性能 | — |
| 流式数据（监控/事件） | ✅ 原生流 | — |
| 移动客户端 | — | ❌ HTTP/2适配复杂 |
| 浏览器端 | — | ❌ 需gRPC-Web |

## OpenAPI 3.1规范

### 核心实践
```
openapi: 3.1.0
info:
  title: 用户服务
  version: 1.2.0
paths:
  /users/{id}:
    get:
      operationId: getUser
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 用户详情
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

### 规范要点
- **operationId唯一**：生成客户端方法名
- **语义化HTTP方法**：GET查 POST创 PUT替 PATCH改 DELETE删
- **统一错误响应**：`{code, message, details}`
- **分页规范**：`?page=1&size=20` + 响应带 `total/pages`

## API版本策略

| 策略 | 例子 | 评价 |
|------|------|------|
| URL路径 | `/v1/users` | 简单直观，推荐 |
| Header | `Accept: app.v2+json` | 干净URL，客户端复杂 |
| 参数 | `?version=2` | 缓存不友好 |
| 无版本 | 向后兼容演进 | 理想但难实现 |

> **建议**：URL路径版本 + 内部兼容层。V1保持稳定，V2可做破坏变更。

## 速率限制/认证/授权

### 速率限制策略
- **Token Bucket**：突发友好，推荐
- **Sliding Window**：精确控制
- **Fixed Window**：简单但边界有尖峰

### 认证标准
- **JWT**：无状态，适用于微服务
- **OAuth 2.0**：授权委托，第三方登录
- **API Key**：简单服务，非敏感场景

### 授权模型
- **RBAC**：角色基础，企业常见
- **ABAC**：属性基础，精细控制
- **ReBAC**：关系基础，社交图谱
- **OpenFGA/Google Zanzibar**：大规模关系授权

## API设计检查清单

- [ ] 资源命名合理（名词复数）
- [ ] HTTP方法语义正确
- [ ] 版本策略明确
- [ ] 错误格式统一
- [ ] 认证鉴权覆盖全部端点
- [ ] 速率限制已配置
- [ ] 分页/排序/过滤支持
- [ ] 版本Changelog维护
- [ ] 文档自动生成（Swagger/Stoplight）
- [ ] 无冗余字段（按需返回）
- [ ] 幂等性保证（POST创建可重入）
- [ ] 安全头（CORS/HSTS/CSP）
