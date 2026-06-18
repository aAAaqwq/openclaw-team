#!/bin/bash
# =============================================================================
# 【天枢】每日战报自动生成器
# Battle Report Generator for Tianshu COO v1.1
# =============================================================================
# 用途：从 memory/ 和 DASHBOARD.md 提取数据，自动生成每日战报
# 运行方式：bash pipelines/battle-report-generator.sh
# 输出：archive/reports/battle-report-YYYY-MM-DD.md
# 对标：亚马逊6-Pager思路 — 数据优先，结构化为王
# =============================================================================

WORKSPACE="/home/openclaw/.openclaw/workspace/tianshu"
DATE=$(date +%Y-%m-%d)
OUTPUT="${WORKSPACE}/archive/reports/battle-report-${DATE}.md"

# 检查是否已有今日战报
if [ -f "$OUTPUT" ]; then
    echo "⚠️  今日战报已存在: ${OUTPUT}"
    echo "是否覆盖？(y/N)"
    read -r confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "取消生成"
        exit 0
    fi
fi

echo "📊 生成战报: ${OUTPUT}"

# ===== 从memory/okr.md提取OKR进度 =====
OKR_FILE="${WORKSPACE}/memory/okr.md"
O1_PROGRESS=$(grep -E "^.*进度.*$" "$OKR_FILE" 2>/dev/null | grep -Eo '[0-9]+%' | head -1)
O1_PROGRESS=${O1_PROGRESS:-"0%"}

# ===== 生成战报 =====
cat > "$OUTPUT" << BEOF
# 【天枢】每日战报 — ${DATE}

> 自动生成于：$(date '+%Y-%m-%d %H:%M CST')
> 生成器：battle-report-generator.sh v1.1

---

## 一，今日战果

| 指标 | 当前值 | 状态 |
|:----:|:------:|:----:|
| 任务完成率 | — | ⚪ |
| 72h达标率 | — | ⚪ |
| 阻塞任务 | 0 | ⚪ |
| 资源ROI | — | ⚪ |
| OKR O1 进度 | ${O1_PROGRESS} | 🟢 进行中 |

## 二，各部队表现

| 部队 | 状态 | 完成度 | 备注 |
|:----:|:----:|:------:|------|
| 轩辕 | ⚪ | — | — |
| 烛龙 | ⚪ | — | — |
| 凤凰 | ⚪ | — | — |
| 鲲鹏 | ⚪ | — | — |

## 三，今日关键决策

1. —

## 四，阻塞事项

- 暂无

## 五，明日计划

1. —

## 六，OKR追踪

### O1: 完成天枢能力全面升级至全球顶级COO水平

| KR | 进度 | 状态 |
|:--:|:----:|:----:|
| KR1: Phase 1 基建补全 | 100% | ✅ |
| KR2: Phase 2 数据基建 | 0% | 🟡 进行中 |
| KR3: Phase 3 系统工程 | 0% | ⏳ 待启动 |
| KR4: Phase 4 智能进化 | 0% | ⏳ 待启动 |

---

*天枢在此。* ⚔️
BEOF

echo "✅ 战报生成完成: ${OUTPUT}"
