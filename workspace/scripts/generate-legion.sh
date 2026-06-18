#!/bin/bash
# ==========================================
# OPEN CAIO 军团角色批量生成器 v1.0
# 使用方式: bash scripts/generate-legion.sh
# ==========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
REGISTRY="$WORKSPACE_DIR/knowledge/ops/agent-registry.json"
TEMPLATE="$WORKSPACE_DIR/templates/SOUL.md.template"
OUT_BASE="$WORKSPACE_DIR/agents"

echo "=========================================="
echo "🚀 OPEN CAIO 军团角色生成器"
echo "=========================================="

if [[ ! -f "$TEMPLATE" ]]; then
    echo "❌ 模板文件不存在: $TEMPLATE"
    exit 1
fi

TEMPLATE_CONTENT=$(cat "$TEMPLATE")

# 获取Agent数量
AGENT_COUNT=$(jq '.agents | length' "$REGISTRY")

for i in $(seq 0 $((AGENT_COUNT - 1))); do
    ID=$(jq -r ".agents[$i].id" "$REGISTRY")
    NAME=$(jq -r ".agents[$i].name" "$REGISTRY")
    ROLE=$(jq -r ".agents[$i].role" "$REGISTRY")
    RANK=$(jq -r ".agents[$i].rank" "$REGISTRY")
    SPECIALTY=$(jq -r ".agents[$i].specialty" "$REGISTRY")
    MODEL=$(jq -r ".agents[$i].model" "$REGISTRY")
    MODEL_POOL=$(jq -r ".agents[$i].model_pool | join(\", \")" "$REGISTRY")
    DAILY_BUDGET=$(jq -r ".agents[$i].daily_budget" "$REGISTRY")
    CONCURRENCY=$(jq -r ".agents[$i].concurrency" "$REGISTRY")
    SUPERVISOR=$(jq -r ".agents[$i].supervisor" "$REGISTRY")
    PEERS=$(jq -r ".agents[$i].peers | join(\", \")" "$REGISTRY")

    AGENT_DIR="$OUT_BASE/$ID"
    mkdir -p "$AGENT_DIR/workspace" "$AGENT_DIR/logs"

    # 渲染SOUL.md
    SOUL_CONTENT=$(echo "$TEMPLATE_CONTENT" | \
        sed "s/{{NAME}}/$NAME/g" | \
        sed "s/{{ROLE}}/$ROLE/g" | \
        sed "s/{{RANK}}/$RANK/g" | \
        sed "s/{{SPECIALTY}}/$SPECIALTY/g" | \
        sed "s/{{MODEL}}/$MODEL/g" | \
        sed "s/{{MODEL_POOL}}/$MODEL_POOL/g" | \
        sed "s/{{DAILY_BUDGET}}/$DAILY_BUDGET/g" | \
        sed "s/{{CONCURRENCY}}/$CONCURRENCY/g" | \
        sed "s/{{SUPERVISOR}}/$SUPERVISOR/g" | \
        sed "s/{{PEERS}}/$PEERS/g")

    echo "$SOUL_CONTENT" > "$AGENT_DIR/SOUL.md"

    # 渲染AGENTS.md
    cat > "$AGENT_DIR/AGENTS.md" << AGENTS_EOF
# AGENTS.md — $NAME 本地规则

## 角色
- Agent ID: $ID
- 军功爵: $RANK
- 日限额: \$${DAILY_BUDGET}/日

## 本地工作区
- 产物目录: agents/$ID/workspace/
- 日志目录: agents/$ID/logs/

## 任务规则
1. 任务卡必须包含: deliverable / verifier / deadline / penalty
2. 交付物写入: shared/artifacts/{task_id}/
3. 每90分钟提交一次状态快照
4. 超时触发L1→L2→L3升级链
AGENTS_EOF

    # 渲染TOOLS.md
    cat > "$AGENT_DIR/TOOLS.md" << TOOLS_EOF
# TOOLS.md — $NAME 工具配置

## 可用工具
- 基础: read / write / edit / exec
- 团队: sessions_spawn / sessions_send
- 调度: cron / process
- Web: web_fetch / web_search

## 算力配置
- 模型: $MODEL
- 模型池: $MODEL_POOL
- 并发: ${CONCURRENCY}线程
TOOLS_EOF

    echo "✅ 生成完成: $NAME ($ID) — $RANK"
done

echo ""
echo "=========================================="
echo "✨ 军团角色批量生成完成!"
echo "📁 输出目录: $OUT_BASE"
echo "=========================================="
