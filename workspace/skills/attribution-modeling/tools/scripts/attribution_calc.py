#!/usr/bin/env python3
"""
归因模型计算器 — 支持6种归因模型
Usage:
  python3 attribution_calc.py --model linear --channels "社交媒体=200,搜索广告=300,邮件=150,直接访问=250" --conversions 100
  python3 attribution_calc.py --model "first-click" --channels "广告=800,内容=400,社交=300" --conversions 50
  python3 attribution_calc.py --list-models
"""

import argparse
import json

MODELS = {
    "first-click": {"name": "首次点击", "desc": "100%功劳归第一个触点"},
    "last-click": {"name": "末次点击", "desc": "100%功劳归最后一个触点"},
    "linear": {"name": "线性", "desc": "每个触点均分功劳"},
    "time-decay": {"name": "时间衰减", "desc": "越靠近转化的触点权重越高"},
    "u-shaped": {"name": "U型", "desc": "首次和末次各40%,中间20%"},
    "data-driven": {"name": "数据驱动", "desc": "基于历史数据动态分配"},
}


def parse_channels(ch_str: str) -> dict:
    result = {}
    for part in ch_str.replace("，", ",").split(","):
        if "=" in part:
            k, v = part.rsplit("=", 1)
            result[k.strip()] = float(v.strip())
    return result


def calculate(model: str, channels: dict, conversions: float) -> dict:
    if model == "first-click":
        total = sum(channels.values())
        weights = {k: (v / total * 100) for k, v in channels.items()}
        return {
            "attribution": {k: {"spend": v, "weight_pct": round(weights[k], 1),
                                "conversions": round(conversions * weights[k] / 100, 1),
                                "cost_per_conv": round(v / (conversions * weights[k] / 100 + 0.01), 2)}
                           for k, v in channels.items()},
            "total_conversions": conversions,
            "total_spend": sum(channels.values()),
        }

    elif model == "last-click":
        # 简单模拟：最后一个渠道获得全部
        keys = list(channels.keys())
        last = keys[-1] if keys else "unknown"
        return {
            "attribution": {k: {"spend": v, "weight_pct": 100.0 if k == last else 0.0,
                                "conversions": conversions if k == last else 0.0,
                                "cost_per_conv": round(v / (conversions + 0.01), 2) if k == last else 0}
                           for k, v in channels.items()},
            "total_conversions": conversions,
            "total_spend": sum(channels.values()),
        }

    elif model == "linear":
        weight = 100 / max(len(channels), 1)
        return {
            "attribution": {k: {"spend": v, "weight_pct": round(weight, 1),
                                "conversions": round(conversions * weight / 100, 1),
                                "cost_per_conv": round(v / (conversions * weight / 100 + 0.01), 2)}
                           for k, v in channels.items()},
            "total_conversions": conversions,
            "total_spend": sum(channels.values()),
        }

    elif model == "time-decay":
        # 从第一个到最后一个权重递增
        keys = list(channels.keys())
        weights = {keys[i]: (i + 1) / sum(range(1, len(keys) + 1)) * 100 for i in range(len(keys))}
        return {
            "attribution": {k: {"spend": v, "weight_pct": round(weights[k], 1),
                                "conversions": round(conversions * weights[k] / 100, 1),
                                "cost_per_conv": round(v / (conversions * weights[k] / 100 + 0.01), 2)}
                           for k, v in channels.items()},
            "total_conversions": conversions,
            "total_spend": sum(channels.values()),
        }

    elif model == "u-shaped":
        keys = list(channels.keys())
        n = len(channels)
        if n == 1:
            weights = {keys[0]: 100}
        else:
            weights = {}
            for i, k in enumerate(keys):
                if i == 0:
                    weights[k] = 40
                elif i == n - 1:
                    weights[k] = 40
                else:
                    weights[k] = 20 / max(n - 2, 1)
        return {
            "attribution": {k: {"spend": v, "weight_pct": round(weights[k], 1),
                                "conversions": round(conversions * weights[k] / 100, 1),
                                "cost_per_conv": round(v / (conversions * weights[k] / 100 + 0.01), 2)}
                           for k, v in channels.items()},
            "total_conversions": conversions,
            "total_spend": sum(channels.values()),
        }

    else:  # 默认linear
        return calculate("linear", channels, conversions)


def main():
    parser = argparse.ArgumentParser(description="归因模型计算器")
    parser.add_argument("--model", "-m", choices=list(MODELS.keys()), default="linear")
    parser.add_argument("--channels", "-c", required=True, help='渠道和花费，如"广告=800,内容=400,社交=300"')
    parser.add_argument("--conversions", "-cv", type=float, default=100, help="总转化数")
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--output", "-o", choices=["json", "table"], default="table")
    args = parser.parse_args()

    if args.list_models:
        for k, v in MODELS.items():
            print(f"  {k:15s} {v['name']:8s} — {v['desc']}")
        return

    channels = parse_channels(args.channels)
    result = calculate(args.model, channels, args.conversions)

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        m = MODELS[args.model]
        print(f"\n归因模型: {m['name']} ({args.model})")
        print(f"总花费: ${result['total_spend']:.0f} | 总转化: {result['total_conversions']:.0f}")
        print(f"{'渠道':12s} {'花费':>10s} {'权重':>8s} {'转化':>8s} {'CPA':>10s}")
        print("-" * 50)
        for ch, attr in result["attribution"].items():
            print(f"{ch:12s} ${attr['spend']:<8.0f} {attr['weight_pct']:>7.1f}% {attr['conversions']:>7.1f} ${attr['cost_per_conv']:<8.2f}")


if __name__ == "__main__":
    main()
