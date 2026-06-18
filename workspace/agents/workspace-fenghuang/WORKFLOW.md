# 🕊️ 凤凰 WORKFLOW.md — 内容生产流水线集成

> 最后更新：2026-05-05 10:30 CST
> 集成了 xhs-skill + browser-automation + mediaclaw（TikTok）

---

## 一，xhs-skill 内容生产流水线（小红书创作者中心）

### 安装位置
```
~/.agents/skills/xhs-skill/
```

### 核心能力

| 模块 | 功能 | 依赖 |
|------|------|------|
| 扫码登录 | 小红书创作者中心扫码登录 + cookies 归一化 | agent-browser-stealth |
| 发布笔记 | 图文/视频笔记发布，含门禁校验 | agent-browser-stealth |
| 数据导出 | 创作者中心数据导出（CSV/截图） | agent-browser-stealth |
| 本地CLI | 二维码解码、cookies管理、门禁校验 | Node.js |

### 完整工作流

#### A. 登录流程

```bash
# 1. 打开浏览器登录页
agent-browser-stealth open https://creator.xiaohongshu.com/login

# 2. 截图二维码
# (browser tool screenshot → data/xhs_login_qr.png)

# 3. 解码二维码（发送给用户扫码）
node ./skills/xhs-skill/bin/xhs-skill.mjs qr show --in ./skills/xhs-skill/data/xhs_login_qr.png

# 4. 扫码后导出cookies
agent-browser-stealth cookies --json > ./skills/xhs-skill/data/raw_cookies.json

# 5. 归一化
node ./skills/xhs-skill/bin/xhs-skill.mjs cookies normalize \
  --in ./skills/xhs-skill/data/raw_cookies.json \
  --out ./skills/xhs-skill/data/xhs_cookies.json

# 6. 后验校验
CURRENT_URL="$(agent-browser-stealth get url)"
agent-browser-stealth open https://creator.xiaohongshu.com/creator/home
PROBE_FINAL_URL="$(agent-browser-stealth get url)"
node ./scripts/verify_login.mjs \
  --cookies ./skills/xhs-skill/data/xhs_cookies.json \
  --current-url "$CURRENT_URL" \
  --probe-final-url "$PROBE_FINAL_URL" \
  --json
```

#### B. 发布笔记（图文/视频）

```bash
# 1. 准备发布数据
# 写入 ./skills/xhs-skill/data/publish_payload.json

# 2. 发布门禁校验
node ./skills/xhs-skill/scripts/verify_publish_payload.mjs \
  --in ./skills/xhs-skill/data/publish_payload.json \
  --policy ./skills/xhs-skill/config/verify_publish_policy.json \
  --tag-registry ./skills/xhs-skill/data/tag_registry.json \
  --min-registry-tags 12 \
  --require-source-evidence on \
  --strict-anti-ai on \
  --json

# 3. 内容审核
node ./skills/xhs-skill/scripts/review_publish_payload.mjs \
  --in ./skills/xhs-skill/data/publish_payload.json \
  --policy ./skills/xhs-skill/config/review_policy.json \
  --taxonomy ./skills/xhs-skill/config/review_taxonomy.json \
  --ai-provider auto \
  --require-ai off \
  --json

# 4. browser 执行发布（仅当前两步 ok=true）
# agent-browser-stealth 打开 → 填充 → 读回校验 → 发布 → 双重确认
```

#### C. 导出数据

```bash
# 进入创作者中心 → 截图/导出到 data/exports/<YYYY-MM-DD>/
```

### 防封规范

- 🔴 每天同一profile最多3篇，间隔≥30分钟
- 🔴 禁止连续无停顿操作，动作间随机停顿1.2s-7s
- 🔴 不机房IP，优先家庭网络/手机热点
- 🔴 发布前必须有预热行为（浏览首页+滚动）

---

## 二，browser-automation + 抖音创作者中心截图复盘

### 准备工作

1. browser 工具已启用（cdpPort: 18800, Chrome）
2. 手动登录抖音创作者中心（https://creator.douyin.com）并保持登录态
3. 使用 `profile="user"` 复用现有浏览器登录态

### 截图复盘流程

```yaml
步骤:
  - 1️⃣ 打开抖音创作者中心
    浏览器: open "https://creator.douyin.com/" 标签名: douyin-creator
  
  - 2️⃣ 数据概览页截图
    导航到: 数据概览/数据中心
    截图: 核心指标卡片（播放量/粉丝增长/互动率）
    保存: skills/xhs-skill/data/exports/<YYYY-MM-DD>/douyin_overview.png
  
  - 3️⃣ 内容分析页截图
    导航到: 内容管理/作品数据
    截图: 近7天作品表现TOP5
    保存: skills/xhs-skill/data/exports/<YYYY-MM-DD>/douyin_content.png
  
  - 4️⃣ 粉丝分析页截图
    导航到: 粉丝数据
    截图: 粉丝画像/增长趋势
    保存: skills/xhs-skill/data/exports/<YYYY-MM-DD>/douyin_fans.png
  
  - 5️⃣ 记录输出
    文件: skills/xhs-skill/data/exports/<YYYY-MM-DD>/douyin_report.txt
    内容: 时间范围 + 关键指标 + 截图路径
```

### 命令速查

```bash
# 浏览器工具（通过 OpenClaw browser tool）
action="open" url="https://creator.douyin.com/" label="douyin-creator"
action="snapshot" targetId="douyin-creator"
action="screenshot" targetId="douyin-creator"

# 注意：抖音对自动化检测严格，优先使用 profile="user" 复用已登录浏览器
```

---

## 三，mediaclaw（TikTok 出海内容生产工具）

### 安装

```bash
# 从 ClawHub 安装
clawhub install mediaclaw
# 或
openclaw skills install mediaclaw
```

### 功能

mediaclaw 是一个 OpenClaw 技能，用于：
- 品牌内容批量适配（TikTok/Reels/Shorts/XHS）
- 多平台视频变体生成（替换品牌元素、颜色分级）
- 自动生成适配文案 + 钩子
- 性能追踪仪表盘

### 典型场景

| 场景 | 输入 | mediaclaw 输出 |
|------|------|---------------|
| 产品视频多平台适配 | 1条产品视频 + 品牌素材 | 15条平台定制视频 + 文案 |
| 品牌焕新 | 新旧品牌素材 | 全平台品牌更新 |
| 批量内容生产 | 原始素材 | 各平台变体 + 优化版文案 |

### 与凤凰工作流集成

```
凤凰内容 → mediaclaw → TikTok/Reels/Shorts/XHS 多平台变体
              ↓
        性能追踪 ← 各平台数据回传
```

---

## 四，流水线集成架构

```
┌─────────────────────────────────────────┐
│           凤凰 CCO 内容引擎              │
├──────────┬──────────┬──────────┬─────────┤
│ 公众号    │ 小红书    │ 抖音      │ TikTok  │
│ wechat   │ xhs-skill│ browser  │ media-  │
│ -push    │ +扫码登录 │ +截图复盘 │ claw    │
│          │ +门禁发布 │          │ +多平台 │
│          │ +数据导出 │          │ +变体   │
├──────────┼──────────┼──────────┼─────────┤
│ 知乎      │ 视频号    │ X/Linked │ Substack│
│ draft    │ (待集成)  │ In       │ letter  │
│ -writer  │          │ multi-   │ news-   │
│          │          │ platform │ letter  │
├──────────┴──────────┴──────────┴─────────┤
│              数据回传                     │
│  GA4 + GSC + 各平台原生数据 → 凤凰日报     │
└──────────────────────────────────────────┘
```

---

## 五，快速启动命令

### 小红书登录 + 发布

```bash
cd ~/.agents/skills/xhs-skill

# 1. 登录
agent-browser-stealth open https://creator.xiaohongshu.com/login
# → 截图二维码 → 解码 → 扫码 → 导出cookies

# 2. 校验 + 发布
agent-browser-stealth open https://creator.xiaohongshu.com/publish/publish
# → 门禁校验 → AI审核 → 填充 → 发布
```

### 抖音复盘

```bash
# 打开抖音创作者中心（需要先手动登录）
browser action=open url=https://creator.douyin.com/ label=douyin-creator
browser action=screenshot targetId=douyin-creator
```

### TikTok 出海

```bash
clawhub install mediaclaw
# 然后按照 mediaclaw 技能文档使用
```
