#!/usr/bin/env python3
"""
zhuque.py — 朱雀：统一排盘入口 v2.0

一键输出八字+紫微斗数，带交叉分析。

用法:
    python3 zhuque.py                         # 当前时间
    python3 zhuque.py 2026 5 2 14 4           # 指定时间
    python3 zhuque.py 2026 5 2 14 4 1         # 指定时间+性别(1男0女)

Python:
    from zhuque import horoscope
    result = horoscope(2026, 5, 2, 14, 0, gender=1)
    print(result['bazi']['summary'])
    print(result['ziwei']['summary'])
"""

import sys
from datetime import datetime
from bazi_engine import BaziEngine
from ziwei_engine import ZiweiEngine

try:
    from qimen_engine import QimenEngine
    from liuyao_engine import LiuyaoEngine
    from daliuren_engine import DaliurenEngine
    QIMEN_AVAILABLE = True
except ImportError:
    QIMEN_AVAILABLE = False


def horoscope(year: int, month: int, day: int,
              hour: int, minute: int = 0,
              gender: int = 1) -> dict:
    """一键排盘：返回八字+紫微"""
    eng_bazi = BaziEngine(year, month, day, hour, minute, gender=gender)
    eng_ziwei = ZiweiEngine(year, month, day, hour, minute, gender=gender)

    bazi = eng_bazi.compute()
    ziwei = eng_ziwei.compute()

    bazi_summary = eng_bazi.summary()
    ziwei_summary = eng_ziwei.summary()

    return {
        'input': {
            'datetime': f'{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}',
            'gender': '男' if gender == 1 else '女',
            'gender_code': gender,
        },
        'bazi': {
            'summary': bazi_summary,
            'data': eng_bazi.dict(),
            'pillars': {
                'year': f'{bazi.year.ganzhi}({bazi.year.nayin})',
                'month': f'{bazi.month.ganzhi}({bazi.month.nayin})',
                'day': f'{bazi.day.ganzhi}({bazi.day.nayin})',
                'hour': f'{bazi.hour.ganzhi}({bazi.hour.nayin})',
            }
        },
        'ziwei': {
            'summary': ziwei_summary,
            'data': eng_ziwei.dict(),
            'five_elements': ziwei.five_elements_class,
            'soul': f'{ziwei.soul}({ziwei.soul_branch})',
            'body': f'{ziwei.body}({ziwei.body_branch})',
        }
    }


def format_full_report(result: dict) -> str:
    """完整报告格式"""
    inp = result['input']
    lines = []
    lines.append("=" * 52)
    lines.append(f"  河图 · 朱雀排盘报告")
    lines.append(f"  {inp['datetime']}  {'男' if inp['gender_code'] == 1 else '女'}")
    lines.append("=" * 52)
    lines.append("")
    lines.append("【八字排盘】")
    lines.append("-" * 40)
    lines.append(result['bazi']['summary'])
    lines.append("")
    lines.append("【紫微斗数】")
    lines.append("-" * 40)
    lines.append(result['ziwei']['summary'])
    lines.append("")
    lines.append("【交叉分析】")
    lines.append("-" * 40)
    b = result['bazi']['data']
    z = result['ziwei']['data']

    # 日干 + 五行局
    lines.append(f"日干: {b['day_gan']}  五行局: {z['five_elements_class']}")

    # 命主/身主
    lines.append(f"命主: {z['soul']}  身主: {z['body']}")

    # 大运概要
    dayun_info = b['dayun']
    current_age_count = len(dayun_info)
    if current_age_count > 1:
        # 粗略估算当前大运
        import calendar
        now = datetime.now()
        this_year = now.year
        inp_year = inp['datetime'].split()[0].split('-')[0]
        try:
            birth_year = int(inp_year)
        except:
            birth_year = now.year
        age = this_year - birth_year
        for d in dayun_info:
            if d['start_age'] <= age <= d['end_age']:
                lines.append(f"当前大运: {d['ganzhi']} ({d['start_age']}~{d['end_age']}岁)")
                break

    # 四化
    if z.get('transformations'):
        for h in z['transformations']:
            lines.append(f"四化: {h['palace']}宫→{h['star']}({h['mutagen']})")

    lines.append("")
    lines.append("=" * 52)
    lines.append("  河图在此 🐢 | 仅供决策参考")
    lines.append("=" * 52)

    return '\n'.join(lines)


# ── CLI ──────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) >= 5:
        y, m, d, h = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        mi = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        g = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    else:
        now = datetime.now()
        y, m, d, h, mi = now.year, now.month, now.day, now.hour, now.minute
        g = 1

    result = horoscope(y, m, d, h, mi, gender=g)
    print(format_full_report(result))
