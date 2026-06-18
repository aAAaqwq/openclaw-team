#!/usr/bin/env python3
"""
engine_runner.py — 河图起卦引擎统一入口 v1.0

支持：六爻纳甲排盘 / 大六壬排盘 / 时间起梅花

用法：
    python engine_runner.py liuyao --year 2026 --month 5 --day 2 --hour 14 --coins 2,1,3,0,2,1
    python engine_runner.py liuyao --year 2026 --month 5 --day 2 --hour 14 --random
    python engine_runner.py liuyao --gua 111000 --dong 1,4
    python engine_runner.py daliuren --year 1990 --month 11 --day 10 --hour 10
    python engine_runner.py meihua --year 2026 --month 5 --day 2 --hour 14
"""

import json
import sys
import argparse


def cmd_liuyao(args):
    from liuyao_calc import LiuyaoEngine
    eng = LiuyaoEngine(args.year, args.month, args.day, args.hour, args.minute, args.gender)

    if args.coins:
        coins = [int(c) for c in args.coins.split(',')]
        eng.set_params_from_coins(coins)
    elif args.gua:
        dong = [int(x) for x in args.dong.split(',')] if args.dong else None
        eng.set_params_from_gua(args.gua, dong)
    else:
        eng.set_params_random()

    if args.json:
        print(json.dumps(eng.dict(), ensure_ascii=False, indent=2))
    else:
        print(eng.summary())


def cmd_daliuren(args):
    from daliuren_calc import DaLiuRenEngine
    eng = DaLiuRenEngine(args.year, args.month, args.day, args.hour, args.minute, args.gender)
    if args.json:
        print(json.dumps(eng.dict(), ensure_ascii=False, indent=2))
    else:
        print(eng.summary())


def cmd_meihua(args):
    """梅花易数：用时间起卦"""
    from liuyao_calc import LiuyaoEngine
    # 以当前时间数字起卦
    import random
    random.seed(args.year * 10000 + args.month * 100 + args.day)
    eng = LiuyaoEngine(args.year, args.month, args.day, args.hour, args.minute, args.gender)
    eng.set_params_random()
    print(f"🦋 梅花易数 · 时间起卦")
    print(f"  时间: {args.year}-{args.month:02d}-{args.day:02d} {args.hour:02d}:{args.minute:02d}")
    print()
    print(eng.summary())


def main():
    parser = argparse.ArgumentParser(description='河图起卦引擎')
    parser.add_argument('command', choices=['liuyao', 'daliuren', 'meihua'],
                        help='起卦类型')
    parser.add_argument('--year', type=int, default=2026)
    parser.add_argument('--month', type=int, default=5)
    parser.add_argument('--day', type=int, default=2)
    parser.add_argument('--hour', type=int, default=12)
    parser.add_argument('--minute', type=int, default=0)
    parser.add_argument('--gender', type=int, default=1, help='0=女, 1=男')
    parser.add_argument('--coins', help='六爻掷币结果，逗号分隔6个0~3的数字')
    parser.add_argument('--random', action='store_true', help='六爻随机起卦')
    parser.add_argument('--gua', help='六爻从卦象起卦，如"111000"')
    parser.add_argument('--dong', help='六爻动爻位置，如"1,4"')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')

    args = parser.parse_args()

    if args.command == 'liuyao':
        cmd_liuyao(args)
    elif args.command == 'daliuren':
        cmd_daliuren(args)
    elif args.command == 'meihua':
        cmd_meihua(args)


if __name__ == '__main__':
    main()
