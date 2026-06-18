# 容器化

Docker生产级最佳实践与容器安全指南。

## Dockerfile最佳实践

### 多阶段构建
```dockerfile
# 构建阶段
FROM golang:1.22 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o server .

# 运行阶段（最小镜像）
FROM alpine:3.19
RUN apk --no-cache add ca-certificates tzdata
COPY --from=builder /app/server /server
USER nobody
EXPOSE 8080
ENTRYPOINT ["/server"]
```

### 安全扫描集成
```dockerfile
# 构建后扫描（Docker Scout / Trivy）
# docker build --provenance=true .
# docker scout quickview <image>
```

## Compose编排

### 生产级Compose模板
```yaml
version: '3.8'
services:
  app:
    build: .
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - DB_URL=postgres://user:pass@db:5432/app
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    depends_on:
      db:
        condition: service_healthy
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 10s
    secrets:
      - db_pass

volumes:
  pgdata:

secrets:
  db_pass:
    file: ./secrets/db_password.txt
```

## 镜像优化

### 大小优化
| 策略 | 效果 | 方法 |
|------|------|------|
| 多阶段构建 | 减少90% | 构建依赖不带到运行层 |
| 选择Alpine | 减少80% | musl libc替代glibc |
| 合并RUN命令 | 减少层数 | `RUN cmd1 && cmd2 && cmd3` |
| .dockerignore | 减少上下文 | 排除node_modules/.git |
| 缓存利用 | 加速构建 | 先COPY依赖声明文件，后源码 |

### 层缓存策略
```dockerfile
# 好：依赖层单独缓存
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .

# 坏：每次改代码都要重装依赖
COPY . .
RUN yarn install
```

## 容器安全

### 非root运行
```dockerfile
# 必须设置
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

### 只读文件系统
```yaml
# docker-compose.yml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
```

### Seccomp安全配置
```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {"names": ["read", "write", "exit", "exit_group"], "action": "SCMP_ACT_ALLOW"}
  ]
}
```

### 安全Checklist
- [ ] 不使用 `latest` 标签（用具体版本号）
- [ ] 镜像每周扫描漏洞
- [ ] 运行用户非root
- [ ] 文件系统read_only
- [ ] 限制能力（`--cap-drop ALL --cap-add NET_BIND_SERVICE`）
- [ ] 启用Seccomp/AppArmor
- [ ] 不存储密钥在镜像中
- [ ] 容器内无SSH守护进程
- [ ] 日志限制防止磁盘爆满
- [ ] 资源限制（CPU/Memory）
