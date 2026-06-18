#!/usr/bin/env python3
"""
解析 Telegram 导出的聊天记录
提取烛龙相关的配置、策略、参数等信息
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class TelegramChatParser:
    """Telegram 聊天记录解析器"""
    
    def __init__(self, export_dir):
        self.export_dir = Path(export_dir)
        self.messages = []
        self.configs = defaultdict(list)
        self.strategies = []
        self.risk_params = {}
        self.capital_info = {}
        
    def find_export_files(self):
        """查找导出文件"""
        json_files = list(self.export_dir.glob("**/*.json"))
        html_files = list(self.export_dir.glob("**/*.html"))
        
        print(f"📁 扫描目录: {self.export_dir}")
        print(f"   发现 {len(json_files)} 个 JSON 文件")
        print(f"   发现 {len(html_files)} 个 HTML 文件")
        
        return json_files, html_files
    
    def parse_json_export(self, json_file):
        """解析 JSON 格式的导出文件"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'messages' in data:
                return data['messages']
            elif isinstance(data, list):
                return data
            else:
                return [data]
        except Exception as e:
            print(f"   ⚠️ 解析失败 {json_file}: {e}")
            return []
    
    def extract_zhulong_content(self, messages):
        """提取烛龙相关的内容"""
        zhulong_msgs = []
        
        for msg in messages:
            if isinstance(msg, dict):
                text = msg.get('text', '')
                if isinstance(text, list):
                    text = ' '.join(str(t) for t in text)
                
                # 检查是否包含烛龙相关内容
                if any(keyword in text.lower() for keyword in [
                    '烛龙', 'zhulong', '量化', '策略', '因子', '仓位', 
                    '风险', 'cvar', '夏普', '收益', '熔断', '资金',
                    'a股', '港股', '美股', '加密', 'polymarket'
                ]):
                    zhulong_msgs.append({
                        'date': msg.get('date', ''),
                        'text': text,
                        'from': msg.get('from', 'Unknown'),
                        'type': msg.get('type', 'message')
                    })
        
        return zhulong_msgs
    
    def analyze_config_patterns(self, messages):
        """分析配置模式"""
        patterns = {
            'capital': r'(资金|本金|规模)[：:]\s*([\d,\.]+)\s*(万|亿|USD|CNY|¥|\$)?',
            'allocation': r'(A股|港股|美股|加密|预测市场)[：:]\s*(\d+)%?',
            'risk_limit': r'(CVaR|风险上限|止损)[：:]\s*(\d+\.?\d*)%?',
            'leverage': r'(杠杆|倍数)[：:]\s*(\d+)x?',
            'sharpe': r'(夏普|Sharpe)[：:]\s*(\d+\.?\d*)',
            'factor': r'(因子|策略)[：:]\s*(\S+)',
        }
        
        extracted = defaultdict(list)
        
        for msg in messages:
            text = msg.get('text', '')
            for category, pattern in patterns.items():
                matches = re.findall(pattern, text)
                if matches:
                    extracted[category].extend(matches)
        
        return extracted
    
    def generate_recovery_report(self, messages, patterns):
        """生成恢复报告"""
        report = []
        report.append("=" * 70)
        report.append("🔥 烛龙配置恢复报告")
        report.append("=" * 70)
        report.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📊 分析消息数: {len(messages)}")
        report.append("")
        
        # 资金配置
        report.append("💰 资金配置信息")
        report.append("-" * 70)
        if patterns['capital']:
            for match in patterns['capital'][:5]:  # 取前5个
                report.append(f"   • {match[0]}: {match[1]} {match[2] if len(match) > 2 else ''}")
        else:
            report.append("   ⚠️ 未找到资金配置信息")
        report.append("")
        
        # 市场分配
        report.append("📈 市场资金分配")
        report.append("-" * 70)
        if patterns['allocation']:
            for match in patterns['allocation']:
                report.append(f"   • {match[0]}: {match[1]}%")
        else:
            report.append("   ⚠️ 未找到市场分配信息")
        report.append("")
        
        # 风险参数
        report.append("🛡️ 风险参数")
        report.append("-" * 70)
        if patterns['risk_limit']:
            for match in patterns['risk_limit'][:5]:
                report.append(f"   • {match[0]}: {match[1]}%")
        else:
            report.append("   ⚠️ 未找到风险参数")
        report.append("")
        
        # 杠杆设置
        report.append("⚡ 杠杆配置")
        report.append("-" * 70)
        if patterns['leverage']:
            for match in patterns['leverage'][:3]:
                report.append(f"   • 杠杆倍数: {match[1]}x")
        else:
            report.append("   ⚠️ 未找到杠杆配置")
        report.append("")
        
        # 夏普比率
        report.append("📊 绩效指标")
        report.append("-" * 70)
        if patterns['sharpe']:
            for match in patterns['sharpe'][:3]:
                report.append(f"   • {match[0]}: {match[1]}")
        else:
            report.append("   ⚠️ 未找到夏普比率数据")
        report.append("")
        
        # 因子/策略
        report.append("🧬 因子与策略")
        report.append("-" * 70)
        if patterns['factor']:
            unique_factors = list(set([m[1] for m in patterns['factor']]))[:10]
            for factor in unique_factors:
                report.append(f"   • {factor}")
        else:
            report.append("   ⚠️ 未找到因子信息")
        report.append("")
        
        # 关键消息时间线
        report.append("📅 关键消息时间线 (最近10条)")
        report.append("-" * 70)
        sorted_msgs = sorted(messages, key=lambda x: x.get('date', ''), reverse=True)[:10]
        for msg in sorted_msgs:
            date = msg.get('date', 'Unknown')[:10] if msg.get('date') else 'Unknown'
            text = msg.get('text', '')[:50] + "..." if len(msg.get('text', '')) > 50 else msg.get('text', '')
            report.append(f"   [{date}] {text}")
        report.append("")
        
        # 建议
        report.append("🎯 恢复建议")
        report.append("-" * 70)
        report.append("基于分析结果，建议按以下优先级恢复:")
        report.append("")
        
        if not patterns['capital']:
            report.append("   🔴 高优先级: 需要重新配置资金规模")
        if not patterns['allocation']:
            report.append("   🔴 高优先级: 需要重新配置市场分配比例")
        if not patterns['risk_limit']:
            report.append("   🟡 中优先级: 需要重新设置风险参数")
        if not patterns['factor']:
            report.append("   🟢 低优先级: 需要重新训练因子策略")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run(self):
        """运行解析流程"""
        print("🔥 烛龙 Telegram 聊天记录解析器")
        print("=" * 70)
        print()
        
        # 1. 查找文件
        json_files, html_files = self.find_export_files()
        
        if not json_files and not html_files:
            print("❌ 未找到导出文件")
            print(f"   请确保已将 Telegram 聊天记录导出到: {self.export_dir}")
            return False
        
        # 2. 解析 JSON 文件
        all_messages = []
        for json_file in json_files:
            print(f"📄 解析: {json_file.name}")
            msgs = self.parse_json_export(json_file)
            all_messages.extend(msgs)
        
        print(f"\n✅ 共解析 {len(all_messages)} 条消息")
        
        # 3. 提取烛龙相关内容
        print("🔍 提取烛龙相关内容...")
        zhulong_msgs = self.extract_zhulong_content(all_messages)
        print(f"✅ 找到 {len(zhulong_msgs)} 条相关消息")
        
        # 4. 分析配置模式
        print("🧠 分析配置模式...")
        patterns = self.analyze_config_patterns(zhulong_msgs)
        
        # 5. 生成报告
        print("📊 生成恢复报告...")
        report = self.generate_recovery_report(zhulong_msgs, patterns)
        
        # 6. 保存报告
        report_file = self.export_dir / "zhulong_recovery_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 报告已保存: {report_file}")
        print()
        print(report)
        
        return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 parse_telegram_export.py <导出目录>")
        print()
        print("示例:")
        print("  python3 parse_telegram_export.py ~/Desktop/Telegram\\ Export")
        print("  python3 parse_telegram_export.py ~/Desktop/zhulong_export")
        sys.exit(1)
    
    export_dir = sys.argv[1]
    
    if not Path(export_dir).exists():
        print(f"❌ 目录不存在: {export_dir}")
        sys.exit(1)
    
    parser = TelegramChatParser(export_dir)
    success = parser.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
