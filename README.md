# 🦞 龙虾军团 · OpenClaw Team

> **一人能敌千军，一钳可定乾坤。**
>
> 从 OpenClaw 开源项目孵化而来的多Agent协作系统，焕新重命名而来。

---

## 📋 概览

龙虾军团是一套完整的 **多Agent协作框架**，基于 OpenClaw 构建，包含：

- **17个Agent工作区** — 每个Agent拥有独立的身份、记忆、技能栈
- **236+ 实装Skill** — 覆盖产品、工程、量化、法务、增长、内容等全领域
- **三省六部制组织架构** — 中书省(战略)、门下省(风控)、尚书省(执行) + 六部分工
- **共享基础设施** — 搜索、邮件、浏览器RPA、协作等基建Skill全部就绪

---

## 🏛️ 组织架构

### 三省（核心决策层）

| ID | 名称 | 定位 | 部门 |
|----|------|------|------|
| `kunlun` | 🏔️ 昆仑 | 首席幕僚长·战略奇点 | 中书省 |
| `mingjing` | 🔍 明镜 | 合规风控官·审计守护者 | 门下省 |
| `tianshu` | ⚙️ 天枢 | 项目指挥官·执行中枢 | 尚书省 |

### 六部（执行层）

**工部** — 产品与技术
| ID | 名称 | 定位 |
|----|------|------|
| `tiangong` | 🎨 天工 | 产品设计官·美学匠人 |
| `xuanyuan` | 💻 轩辕 | 技术架构师·代码之神 |

**礼部** — 内容与品牌
| ID | 名称 | 定位 |
|----|------|------|
| `fenghuang` | 🔥 凤凰 | 内容创作官·叙事大师 |
| `mobai` | 🖌️ 墨白 | 设计视觉官 |
| `zhuque` | 🦜 朱雀 | 品牌传播官 |

**兵部** — 增长与情报
| ID | 名称 | 定位 |
|----|------|------|
| `kunpeng` | 🚀 鲲鹏 | 增长黑客·获客引擎 |
| `fengniao` | 🐦 蜂鸟 | 情报分析官 |
| `baxia` | 🐢 霸下 | 销售谈判官 |

**量化神殿**
| ID | 名称 | 定位 |
|----|------|------|
| `zhulong` | 📊 烛龙 | 量化交易官·数据先知 |

**吏部**
| ID | 名称 | 定位 |
|----|------|------|
| `jixia` | 👥 稷下 | 人才猎手·组织建设者 |

**沙盒**
| ID | 名称 | 定位 |
|----|------|------|
| `qilin` | 🦋 麒麟 | AI电商官 |
| `hetu` | 🏮 河图 | 东方智慧官 |

**户部**
| ID | 名称 | 定位 |
|----|------|------|
| `siku` | 💰 司库 | 财务核算官 |

---

## 🧠 Skill 体系

> 总计 **236个** 实装Skill，按领域分类：

| 分类 | Skill数 | 覆盖 |
|------|---------|------|
| 🏗️ 工程技术 | 12+ | 全栈、云原生、API设计、数据库、容器化、CI/CD |
| 🤖 AI基础设施 | 5+ | 大模型训练、推理优化、RAG、Agent框架 |
| 📊 数据驱动 | 7+ | 实验设计、验收标准、用户故事、优先级排序 |
| 💼 商业化 | 9+ | PMF、PLG、精益画布、产品定位、路线图 |
| 📈 增长引擎 | 6+ | 飞轮架构、病毒循环、线索自动化、转化优化 |
| 🕵️ 情报监听 | 4+ | 社交情绪、竞品熵值、全球市场拓扑、热点扫描 |
| 🔍 法务合规 | 20+ | 合同审查、GDPR、合规审计、风险矩阵 |
| 💰 量化交易 | 10+ | 回测、TradingView Pine、加密追踪 |
| 🎨 内容创作 | 15+ | 小红书、知乎、公众号、视频脚本、品牌叙事 |
| 🧪 方法论 | 6+ | DDD、TDD、安全审计、可观测性 |

> 完整索引见 [`workspace/skills/skills-index.md`](workspace/skills/skills-index.md)

---

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/aaaAqwq/openclaw-team.git
cd openclaw-team

# 安装 OpenClaw（如果未安装）
# https://github.com/shenjj2025-oss/openclaw

# 配置基础模型
cp config.yaml.example config.yaml
# 编辑 config.yaml 填入模型配置

# 启动
openclaw agent start
```

---

## 📂 目录结构

```
openclaw-team/
├── config.yaml                  # 网关与模型配置
├── agents/                      # 15个Agent配置文件
│   ├── kunlun/                  # 昆仑
│   ├── fenghuang/               # 凤凰
│   └── ...
├── skills/                      # 全局Skill定义
│   ├── silicon-life-handbook/   # 硅基生命训练学
│   └── xhs-skill/               # 小红书Skill
└── workspace/
    ├── agents/                  # 17个Agent工作区
    │   ├── workspace-kunlun/    # 昆仑工作区
    │   ├── workspace-fenghuang/ # 凤凰工作区
    │   └── ...
    ├── skills/                  # 236个实装Skill
    │   ├── product-strategy/    # 产品策略
    │   ├── engineering/         # 工程技术
    │   └── ...
    ├── SHARED/                  # 共享配置
    ├── infrastructure/          # 基础设施文档
    └── references/              # 引用资料
```

---

## 🦞 关于"龙虾军团"

龙虾，甲壳类中的战斗民族：
- 🛡️ **坚硬甲壳** — 系统稳固，安全合规
- ✂️ **一双巨钳** — 左右开工，高效执行
- 🔄 **断肢再生** — 容错自愈，持续进化
- 👁️ **双目如炬** — 洞察先机，数据驱动

**前身**: [龙虾军团](https://github.com/shenjj2025-oss/openclaw-team)（OpenClaw 开源项目）

---

## 📜 许可

本项目基于上游 OpenClaw 开源项目衍生的配置与技能集合，遵循原始项目的开源协议。
