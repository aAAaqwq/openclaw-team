#!/bin/bash
# =============================================================================
# 【天枢】DASHBOARD 自动更新器
# Dashboard Auto-Updater for Tianshu COO
# =============================================================================
# 用途：从memory/和archive/提取数据，更新DASHBOARD.md的12项KPI
# 运行方式：bash scripts/dashboard-updater.sh
# 对标：自动化BI看板刷新
# =============================================================================

WORKSPACE="/Users/peterqiu/.openclaw/workspace/tianshu"
DATE=$(date +%Y-%m-%d)
DASHBOARD="${WORKSPACE}/DASHBOARD.md"

echo "🔄 更新DASHBOARD: ${DATE}"

# ===== 从战报提取数据 =====
LATEST_REPORT=$(ls -t ${WORKSPACE}/archive/reports/battle-report-*.md 2>/dev/null | head -1)
if [ -n "$LATEST_REPORT" ]; then
    echo "  从战报读取数据: ${LATEST_REPORT}"
    
    # 读取战报中的KPI值
    TASK_RATE=$(grep "任务完成率" "$LATEST_REPORT" | grep -oP '\d+%' | head -1)
    RATE_72H=$(grep "72h达标率" "$LATEST_REPORT" | grep -oP '\d+%' | head -1)
    BLOCKED=$(grep "阻塞任务" "$LATEST_REPORT" | grep -oP '\d+' | head -1)
    ROI=$(grep "资源ROI" "$LATEST_REPORT" | grep -oP '[\d.]+x' | head -1)
fi

echo "  任务完成率: ${TASK_RATE:-—}"
echo "  72h达标率: ${RATE_72H:-—}"
echo "  阻塞任务: ${BLOCKED:-0}"
echo "  资源ROI: ${ROI:-—}"
echo "✅ DASHBOARD 数据提取完成"
echo ""
echo "⚠️  当前为半自动化模式，需要手动将数据填入 DASHBOARD.md"
echo "   全自动化需要 Phase 3 的CI/CD支持"

