# 蓝血军团群聊响应修复方案

## 问题诊断

所有 agent（凤凰/天枢/天工/麒麟/昆仑）均存在以下问题：
1. 能**接收**群消息
2. 能**理解**群消息
3. 但无法**群内可见**回复（回复默认走 private final answer，未发出群消息）

## 修复原理

OpenClaw agent 在群聊中收到 @mention 后，默认的 final answer 是**私有回复**（仅发送者可见或仅私聊）。要让回复对全群可见，必须显式调用 `message(action=send)`。

## 修复方案

### 方案 A：修改 AGENTS.md（推荐，最快）

在每个 agent 的 AGENTS.md 里加入以下规则：

```markdown
### 群聊响应协议

当在 Telegram 群聊中被 @mention 时：
1. 必须调用 message(action=send, message="你的回复") 将回复发到群内可见
2. 被昆仑明确路由时，使用 reply_to_current 标记回复位置
3. 不得仅以 final answer（私聊）形式回复群内 @mention
```

### 方案 B：修改每个 agent 的 config

在每个 agent 的 config 中添加 authorized_senders 含丘总 ID：

```yaml
# 在 ~/.openclaw/config.yaml 的每个 agent 条目中添加
agents:
  fenghuang:
    authorized_senders: [8328029665, "kunlun_opencaio_bot"]
    # ... 其他配置
  tianshu:
    authorized_senders: [8328029665, "kunlun_opencaio_bot"]
    # ... 其他配置
  # ... 以此类推
```

### 方案 C（终极）：自定义群聊路由 handler

如果系统支持路由插件，写一个统一的路由 handler 接管所有群消息可见性。

## 立刻执行步骤

```bash
# 1. 查当前 config 文件位置
openclaw status

# 2. 检查每个 agent 的 authorized_senders 配置
# 需要看 config.yaml

# 3. 如果 config 不支持，走方案 A——改 AGENTS.md
# 直接在文件里嵌入群聊响应协议
```

要不要我现在就逐个检查 config 并直接修改？
