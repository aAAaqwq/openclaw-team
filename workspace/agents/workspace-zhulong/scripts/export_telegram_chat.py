#!/usr/bin/env python3
"""
Telegram Desktop 聊天记录导出工具
支持两种模式：
1. 使用 Telegram 内置导出功能 (推荐)
2. 使用 AppleScript 自动化 UI 操作

使用方法：
    python3 export_telegram_chat.py
"""

import os
import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

# 配置
TELEGRAM_APP = "/Applications/Telegram.app"
EXPORT_DIR = Path.home() / "Desktop" / "zhulong_export"
TARGET_CHAT = "zhulong"  # 聊天名称


def run_applescript(script_path):
    """运行 AppleScript"""
    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Script timed out"
    except Exception as e:
        return False, "", str(e)


def check_telegram_running():
    """检查 Telegram 是否运行"""
    try:
        result = subprocess.run(
            ["pgrep", "-x", "Telegram"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def manual_export_guide():
    """提供手动导出指南"""
    guide = """
╔══════════════════════════════════════════════════════════════════╗
║           Telegram 聊天记录手动导出指南                          ║
╠══════════════════════════════════════════════════════════════════╣

📱 方法一：Telegram Desktop 内置导出（推荐）

1. 打开 Telegram Desktop
2. 找到并点击 @zhulong 聊天
3. 点击右上角 ⋮ (三个点) → "导出聊天记录"
   或者：设置 → 高级 → 导出 Telegram 数据
4. 配置选项：
   ☑ 选择聊天：zhulong
   ☑ 格式：JSON (机器可读)
   ☐ 照片/视频/文件 (取消勾选，只导出文本)
   ☑ 时间范围：全部历史
5. 选择保存位置：~/Desktop/zhulong_export/
6. 点击导出

📱 方法二：快速滚动截图（备用）

如果导出功能受限，可以使用此脚本自动滚动：

    osascript -e '
    tell application "Telegram" to activate
    tell application "System Events"
        tell process "Telegram"
            -- 滚动到顶部
            key code 126 using command down
            delay 0.5
            -- 持续向下滚动
            repeat 200 times
                key code 121
                delay 0.2
            end repeat
        end tell
    end tell
    '

📁 导出后的处理

导出完成后，运行以下命令解析：

    python3 parse_telegram_export.py ~/Desktop/zhulong_export/

╚══════════════════════════════════════════════════════════════════╝
"""
    print(guide)


def create_export_directory():
    """创建导出目录"""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ 导出目录已创建: {EXPORT_DIR}")
    return EXPORT_DIR


def scan_existing_exports():
    """扫描已有的导出文件"""
    desktop = Path.home() / "Desktop"
    possible_paths = [
        desktop / "Telegram Export",
        desktop / "zhulong_export",
        desktop / "export",
    ]
    
    found = []
    for path in possible_paths:
        if path.exists():
            files = list(path.glob("**/*.json")) + list(path.glob("**/*.html"))
            if files:
                found.append((path, files))
    
    return found


def main():
    """主函数"""
    print("=" * 60)
    print("🔥 烛龙 Telegram 聊天记录恢复工具")
    print("=" * 60)
    print()
    
    # 1. 检查是否已有导出文件
    print("🔍 检查是否已有导出的聊天记录...")
    existing = scan_existing_exports()
    
    if existing:
        print(f"✅ 发现 {len(existing)} 个已有导出目录:")
        for path, files in existing:
            print(f"   📁 {path} ({len(files)} 个文件)")
        print()
        print("💡 如果这是之前的导出，可以直接解析这些文件")
        response = input("是否解析已有导出? (y/n): ").lower()
        if response == 'y':
            print(f"请运行: python3 parse_telegram_export.py '{existing[0][0]}'")
            return
    
    # 2. 检查 Telegram 是否运行
    print()
    print("🔍 检查 Telegram Desktop 状态...")
    if check_telegram_running():
        print("✅ Telegram Desktop 正在运行")
    else:
        print("⚠️ Telegram Desktop 未运行")
        print("   请先启动 Telegram Desktop")
        response = input("是否现在启动? (y/n): ").lower()
        if response == 'y':
            subprocess.run(["open", "-a", "Telegram"])
            print("   请等待 Telegram 启动后按回车继续...")
            input()
    
    # 3. 显示导出指南
    print()
    manual_export_guide()
    
    # 4. 创建导出目录
    print()
    create_export_directory()
    
    # 5. 询问是否运行自动化脚本
    print()
    print("🤖 是否尝试运行 AppleScript 自动化?")
    print("   (需要授予辅助功能权限)")
    response = input("运行自动化脚本? (y/n): ").lower()
    
    if response == 'y':
        script_path = Path(__file__).parent / "export_telegram_chat.applescript"
        if script_path.exists():
            print("🚀 运行自动化脚本...