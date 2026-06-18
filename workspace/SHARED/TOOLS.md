# SHARED/TOOLS.md — 军团全局工具配置
## Global Tool & Environment Configuration for All Agents

> **最后更新**：2026-05-05  
> **作用**：所有Agent共享的本地环境信息。Agent特有配置（如河图的Python引擎路径）在各Agent的SKILL.md中引用。

---

## 系统环境

| 项目 | 值 | 说明 |
|------|-----|------|
| 宿主机 | PeterQ的Mac mini | Apple Silicon (M系列) |
| OS | macOS (Darwin) | — |
| Shell | zsh | 默认 |
| Node | v22.22.0 | — |
| OpenClaw | 2026.5.3-1 | — |
| 时区 | Asia/Shanghai (UTC+8) | — |

---

## 文件系统

| 路径 | 用途 | 说明 |
|------|------|------|
| `~/.openclaw/workspace/` | 工作区根目录 | 所有Agent的工作区入口 |
| `~/.openclaw/workspace/agents/` | Agent灵魂文件 | 每个Agent的SOUL/AGENTS/MEMORY |
| `~/.openclaw/workspace/SHARED/` | 全局共享知识库 | 宪章/知识/模板 |
| `~/.openclaw/workspace/SHARED/TOOLS.md` | ⬅️ 本文件 | 全局工具配置 |
| `~/.openclaw/agents/<id>/` | Agent运行时数据 | sessions+auth，框架自动管理 |
| `~/.openclaw/skills/` | 全局技能库 | 199个技能 (OpenClaw内置) |
| `~/.agents/skills/` | 用户技能库 | 209个自定义skill |

---

## Agent特有配置索引

以下配置在各自Agent的SKILL.md中详细引用，此处只列索引：

| Agent | 特有配置 | 说明 |
|-------|---------|------|
| 河图 (hetu) | Python 命理引擎 (bazi/daliuren/liuyao/ziwei) | 6个独立engine脚本 |
| 烛龙 (zhulong) | Telegram 导出脚本 | 4个py脚本 |
| 轩辕 (xuanyuan) | CI/CD流水线 | Git Workflow SDE |
| 天枢 (tianshu) | 架构文档体系 | 15个架构文档 + 3个pipeline |

---

## 通用命令

```bash
# Gateway 管理
openclaw gateway status      # 查看Gateway状态
openclaw gateway restart     # 重启Gateway

# 文件操作
rsync -a src/ dst/           # 保持属性的递归同步
diff -rq dir1/ dir2/         # 递归比较目录差异
```

---

## 变更历史

| 日期 | 变更 | 操作人 |
|------|------|--------|
| 2026-05-05 | 创建全局TOOLS.md，取代原16个Agent各自的副本 | 昆仑 |
