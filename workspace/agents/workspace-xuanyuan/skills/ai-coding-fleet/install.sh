#!/bin/bash
#
# 🚀 轩辕AI编码舰队 — 自动化部署脚本
# 安装所有AI编码工具 + OpenClaw ACP配置
#
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "┌─────────────────────────────────────────────┐"
echo "│  🚀 轩辕AI编码舰队 · 自动化部署 v1.0        │"
echo "│  OpenClaw + Claude Code + Cursor + Windsurf  │"
echo "│  + Codex CLI + Trae + MCO                    │"
echo "└─────────────────────────────────────────────┘"
echo -e "${NC}"

# ============================================
# 前置检查
# ============================================
echo -e "\n${YELLOW}[1/7] 前置检查${NC}"

OS="$(uname)"
if [ "$OS" != "Darwin" ]; then
    echo -e "${RED}❌ 此脚本仅支持 macOS${NC}"
    exit 1
fi

# 检查Node.js
if ! command -v node &>/dev/null; then
    echo -e "${RED}❌ 需要 Node.js (推荐 v20+)${NC}"
    echo "  安装: brew install node"
    exit 1
fi
echo -e "${GREEN}✅ Node.js $(node --version)${NC}"

# 检查npm
if ! command -v npm &>/dev/null; then
    echo -e "${RED}❌ 需要 npm${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm $(npm --version)${NC}"

# 检查brew
if ! command -v brew &>/dev/null; then
    echo -e "${YELLOW}⚠️ 未安装Homebrew，IDE安装将跳过${NC}"
    BREW_AVAILABLE=false
else
    BREW_AVAILABLE=true
    echo -e "${GREEN}✅ Homebrew $(brew --version | head -1)${NC}"
fi

# ============================================
# API密钥检查
# ============================================
echo -e "\n${YELLOW}[2/7] API密钥检查${NC}"

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -e "${GREEN}✅ ANTHROPIC_API_KEY 已设置${NC}"
    ANTHROPIC_OK=true
else
    echo -e "${YELLOW}⚠️ ANTHROPIC_API_KEY 未设置 (Claude Code需要)${NC}"
    ANTHROPIC_OK=false
fi

if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✅ OPENAI_API_KEY 已设置${NC}"
    OPENAI_OK=true
else
    echo -e "${YELLOW}⚠️ OPENAI_API_KEY 未设置 (Codex CLI需要)${NC}"
    OPENAI_OK=false
fi

# ============================================
# 安装Claude Code
# ============================================
echo -e "\n${YELLOW}[3/7] 安装 Claude Code${NC}"

if command -v claude &>/dev/null; then
    echo -e "${GREEN}✅ Claude Code $(claude --version 2>/dev/null || echo '已安装')${NC}"
    echo "  升级: npm update -g @anthropic-ai/claude-code"
else
    echo "  安装中..."
    npm install -g @anthropic-ai/claude-code
    if command -v claude &>/dev/null; then
        echo -e "${GREEN}✅ Claude Code 安装成功${NC}"
        if [ "$ANTHROPIC_OK" = true ]; then
            echo "  执行 claude login 完成OAuth认证"
        fi
    else
        echo -e "${RED}❌ 安装失败${NC}"
    fi
fi

# ============================================
# 安装 Codex CLI
# ============================================
echo -e "\n${YELLOW}[4/7] 安装 Codex CLI${NC}"

if command -v codex &>/dev/null; then
    echo -e "${GREEN}✅ Codex CLI 已安装${NC}"
    echo "  升级: npm update -g @openai/codex"
else
    if [ "$OPENAI_OK" = true ]; then
        echo "  安装中..."
        npm install -g @openai/codex 2>/dev/null && echo -e "${GREEN}✅ Codex CLI 安装成功${NC}" || echo -e "${YELLOW}⚠️ Codex CLI安装失败(可能需要特定权限)${NC}"
    else
        echo -e "${YELLOW}⏭️  跳过 (需要OPENAI_API_KEY)${NC}"
    fi
fi

# ============================================
# 安装IDE工具 (Cursor, Windsurf)
# ============================================
echo -e "\n${YELLOW}[5/7] 安装IDE工具${NC}"

# Cursor
if [ "$BREW_AVAILABLE" = true ]; then
    if ls /Applications/Cursor.app 2>/dev/null >/dev/null; then
        echo -e "${GREEN}✅ Cursor 已安装${NC}"
    else
        echo "  安装 Cursor..."
        brew install --cask cursor 2>/dev/null && echo -e "${GREEN}✅ Cursor 安装成功${NC}" || echo -e "${YELLOW}⚠️ Cursor安装失败(可手动安装)${NC}"
    fi
else
    echo -e "${YELLOW}⏭️  跳过 Cursor (需要Homebrew)${NC}"
fi

# Windsurf (检查/Applications)
if ls /Applications/Windsurf.app 2>/dev/null >/dev/null; then
    echo -e "${GREEN}✅ Windsurf 已安装${NC}"
    # 创建CLI别名
    WINDSURF_BIN="/Applications/Windsurf.app/Contents/Resources/app/bin/windsurf"
    if [ -f "$WINDSURF_BIN" ]; then
        if ! grep -q "alias windsurf=" ~/.zshrc 2>/dev/null; then
            echo "alias windsurf='$WINDSURF_BIN'" >> ~/.zshrc
            echo -e "${GREEN}✅ Windsurf CLI 别名已添加到 ~/.zshrc${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️ Windsurf 未安装${NC}"
    echo "  下载: https://windsurf.com"
fi

# Trae
if ls /Applications/Trae.app 2>/dev/null >/dev/null; then
    echo -e "${GREEN}✅ Trae 已安装${NC}"
else
    echo -e "${YELLOW}⏭️  Trae 未安装 (中国区用户可下载: https://www.trae.ai)${NC}"
fi

# ============================================
# 安装 MCO 编排层
# ============================================
echo -e "\n${YELLOW}[6/7] 安装 MCO 编排层${NC}"
if command -v mco &>/dev/null; then
    echo -e "${GREEN}✅ MCO $(mco --version 2>/dev/null || echo '已安装')${NC}"
    echo "  升级: npm update -g mco"
else
    echo "  安装中..."
    npm install -g mco 2>/dev/null && echo -e "${GREEN}✅ MCO 安装成功${NC}" || echo -e "${YELLOW}⚠️ MCO安装失败 (可选组件)${NC}"
fi

# ============================================
# 配置 OpenClaw ACP
# ============================================
echo -e "\n${YELLOW}[7/7] 配置 OpenClaw ACP${NC}"

OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
if [ -f "$OPENCLAW_CONFIG" ]; then
    # 检查是否已有acp配置
    if grep -q '"acp"' "$OPENCLAW_CONFIG" 2>/dev/null; then
        echo -e "${GREEN}✅ ACP配置已存在${NC}"
    else
        echo "  添加ACP配置..."
        # 使用临时文件注入
        python3 -c "
import json
with open('$OPENCLAW_CONFIG', 'r') as f:
    config = json.load(f)

acp_config = {
    'enabled': True,
    'dispatch': {'enabled': True},
    'backend': 'acpx',
    'defaultAgent': 'claude',
    'allowedAgents': ['claude', 'codex', 'cursor'],
    'maxConcurrentSessions': 8,
    'stream': {
        'coalesceIdleMs': 300,
        'maxChunkChars': 1200
    },
    'runtime': {
        'ttlMinutes': 120
    }
}
config['acp'] = acp_config
with open('$OPENCLAW_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
print('✅ ACP配置已写入')
"
    fi
else
    echo -e "${RED}❌ 未找到OpenClaw配置文件: $OPENCLAW_CONFIG${NC}"
fi

# 确保acpx插件启用
OPENCLAW_PLUGIN_DIR="$HOME/.openclaw/plugins"
mkdir -p "$OPENCLAW_PLUGIN_DIR"

# ============================================
# 最终验证
# ============================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  📋 舰队就绪验证${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

verify_command() {
    if command -v "$1" &>/dev/null; then
        echo -e "  ${GREEN}✅ $1 ✓${NC}"
        return 0
    else
        echo -e "  ${YELLOW}❌ $1 ✗${NC}"
        return 1
    fi
}

verify_command claude
verify_command codex
verify_command mco
verify_command cursor

# Windsurf检查
if ls /Applications/Windsurf.app 2>/dev/null >/dev/null; then
    echo -e "  ${GREEN}✅ Windsurf ✓${NC}"
else
    echo -e "  ${YELLOW}❌ Windsurf ✗${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  🚀 轩辕AI编码舰队部署完成！${NC}"
echo ""
echo -e "  ${YELLOW}▶ 下一步${NC}"
echo -e "  1. 重启OpenClaw:  ${GREEN}openclaw gateway restart${NC}"
echo -e "  2. 验证ACP:       ${GREEN}/acp doctor${NC} (在Telegram中)"
echo -e "  3. 启动舰队:      ${GREEN}/acp spawn claude${NC}"
echo ""
echo -e "  ${YELLOW}📖 详细指南:${NC}"
echo -e "  skills/ai-coding-fleet/SKILL.md"
echo ""
echo -e "  ${YELLOW}🔑 需要手动设置:${NC}"
echo -e "  - Claude Code:   ${GREEN}claude login${NC} (OAuth认证)"
echo -e "  - Cursor IDE:    ${GREEN}打开Cursor → 设置Account${NC}"
echo -e "  - Windsurf CLI:  ${GREEN}source ~/.zshrc${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
