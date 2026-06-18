#!/usr/bin/env python3
"""
河图 · 命理预测回测引擎 v1.0
══════════════════════════════════════════════════

功能：
  1. 批量运行历史案例预测
  2. 对比预测结果与客观标签
  3. 统计准确率、召回率、F1
  4. 生成回测报告和可视化数据
  5. 输出 latest_results.json 供每日日报使用

运行方式：
  python3 backtest_engine.py --count 200          # 跑200个案例
  python3 backtest_engine.py --case 马云          # 跑单个案例
  python3 backtest_engine.py --validate           # 验证所有校准案例
"""

import sys, os, json, math, argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

_DEEP_DIR = os.path.dirname(os.path.abspath(__file__))
if _DEEP_DIR not in sys.path:
    sys.path.insert(0, _DEEP_DIR)

# 导入六合交叉验证
from triple_cross import cross_validate, get_available_systems

# ════════════════════════════════════════
# 回测案例库
# ════════════════════════════════════════

@dataclass
class TestCase:
    name: str
    birth: Tuple[int, int, int]
    hour: int
    gender: str
    labels: Dict[str, int]  # 五维客观标签 1-10
    category: str  # 企业家/政治家/科学家/艺术家/运动员/其他
    note: str
    events: Optional[List[Dict]] = None

# 核心校准案例
CALIBRATION_CASES = [
    TestCase("马云", (1964, 9, 10), 12, "男",
             {"事业": 10, "财运": 10, "健康": 8, "婚姻": 7, "人际": 9},
             "企业家", "阿里创始人，顶级事业和财富"),
    TestCase("任正非", (1944, 10, 25), 12, "男",
             {"事业": 10, "财运": 9, "健康": 8, "婚姻": 4, "人际": 8},
             "企业家", "华为天花板级别事业；婚姻两次不顺"),
    TestCase("马化腾", (1971, 10, 29), 12, "男",
             {"事业": 10, "财运": 10, "健康": 7, "婚姻": 8, "人际": 6},
             "企业家", "腾讯创始人；低调婚姻；性格偏内向"),
    TestCase("雷军", (1969, 12, 16), 12, "男",
             {"事业": 10, "财运": 9, "健康": 8, "婚姻": 8, "人际": 8},
             "企业家", "小米+金山；劳模型事业节奏"),
    TestCase("马斯克", (1971, 6, 28), 7, "男",
             {"事业": 10, "财运": 10, "健康": 7, "婚姻": 3, "人际": 5},
             "企业家", "特斯拉+SpaceX；多次婚姻"),
    TestCase("巴菲特", (1930, 8, 30), 3, "男",
             {"事业": 10, "财运": 10, "健康": 8, "婚姻": 6, "人际": 7},
             "企业家", "股神；两次婚姻"),
    TestCase("毛泽东", (1893, 12, 26), 8, "男",
             {"事业": 10, "财运": 1, "健康": 5, "婚姻": 3, "人际": 7},
             "政治家", "建党建国；个人财富极微；婚姻三段坎坷"),
    TestCase("周恩来", (1898, 3, 5), 8, "男",
             {"事业": 9, "财运": 4, "健康": 4, "婚姻": 8, "人际": 10},
             "政治家", "总理级事业；清廉；人际关系顶级"),
    TestCase("邓小平", (1904, 8, 22), 8, "男",
             {"事业": 10, "财运": 2, "健康": 6, "婚姻": 7, "人际": 8},
             "政治家", "改革开放核心；三起三落"),
    TestCase("爱因斯坦", (1879, 3, 14), 11, "男",
             {"事业": 10, "财运": 5, "健康": 6, "婚姻": 3, "人际": 5},
             "科学家", "物理革命；婚姻两段皆不顺"),
    TestCase("霍金", (1942, 1, 8), 8, "男",
             {"事业": 9, "财运": 6, "健康": 1, "婚姻": 5, "人际": 6},
             "科学家", "理论物理巨匠；ALS身体极差"),
    TestCase("屠呦呦", (1930, 12, 30), 8, "女",
             {"事业": 9, "财运": 4, "健康": 6, "婚姻": 7, "人际": 5},
             "科学家", "诺奖级科学成就；清贫学者"),
    TestCase("牛顿", (1643, 1, 4), 8, "男",
             {"事业": 10, "财运": 7, "健康": 7, "婚姻": 0, "人际": 2},
             "科学家", "物理+数学双革命；终身未婚"),
    TestCase("李白", (701, 2, 28), 12, "男",
             {"事业": 9, "财运": 3, "健康": 6, "婚姻": 5, "人际": 9},
             "艺术家", "诗仙级文才；一生潦倒；交游极广"),
    TestCase("梵高", (1853, 3, 30), 11, "男",
             {"事业": 9, "财运": 1, "健康": 2, "婚姻": 2, "人际": 3},
             "艺术家", "后印象派大师；生前贫困；37岁自杀"),
    TestCase("毕加索", (1881, 10, 25), 23, "男",
             {"事业": 10, "财运": 9, "健康": 7, "婚姻": 3, "人际": 6},
             "艺术家", "现代艺术之父；多段婚姻"),
    TestCase("迈克尔·杰克逊", (1958, 8, 29), 12, "男",
             {"事业": 10, "财运": 9, "健康": 3, "婚姻": 2, "人际": 4},
             "演艺", "流行之王；健康差；两段婚姻失败"),
    TestCase("奥普拉", (1954, 1, 29), 4, "女",
             {"事业": 10, "财运": 10, "健康": 7, "婚姻": 7, "人际": 10},
             "演艺", "传媒女王；亿万富豪；人脉极广"),
    TestCase("乔丹", (1963, 2, 17), 14, "男",
             {"事业": 10, "财运": 10, "健康": 8, "婚姻": 5, "人际": 7},
             "运动员", "篮球之神；两次离婚"),
    TestCase("姚明", (1980, 9, 12), 14, "男",
             {"事业": 9, "财运": 9, "健康": 4, "婚姻": 9, "人际": 9},
             "运动员", "NBA球星；脚伤终结生涯；婚姻幸福"),
    TestCase("C罗", (1985, 2, 5), 10, "男",
             {"事业": 10, "财运": 9, "健康": 9, "婚姻": 4, "人际": 6},
             "运动员", "顶级足球运动员；未婚有子"),
    TestCase("梅西", (1987, 6, 24), 20, "男",
             {"事业": 10, "财运": 9, "健康": 8, "婚姻": 9, "人际": 7},
             "运动员", "足球GOAT；低调内敛"),
    TestCase("乔布斯", (1955, 2, 24), 19, "男",
             {"事业": 10, "财运": 10, "健康": 2, "婚姻": 5, "人际": 3},
             "企业家", "苹果神话；56岁胰腺癌逝"),
    TestCase("张国荣", (1956, 9, 12), 12, "男",
             {"事业": 9, "财运": 8, "健康": 2, "婚姻": 5, "人际": 8},
             "演艺", "香港巨星；抑郁症；46岁跳楼"),
    TestCase("丘吉尔", (1874, 11, 30), 1, "男",
             {"事业": 10, "财运": 6, "健康": 5, "婚姻": 8, "人际": 7},
             "政治家", "二战领袖；诺贝尔文学奖"),
]

DIMENSIONS = ["事业", "财运", "健康", "婚姻", "人际"]

# ════════════════════════════════════════
# 回测核心逻辑
# ════════════════════════════════════════

def run_single_case(case: TestCase, verbose: bool = False) -> Dict:
    """运行单个案例的完整预测"""
    year, month, day = case.birth
    
    result = cross_validate(
        person_name=case.name,
        year=year,
        month=month,
        day=day,
        hour=case.hour,
        gender=case.gender,
        query_type="general"
    )
    
    # 提取预测评分
    predictions = {}
    for dim in DIMENSIONS:
        predictions[dim] = result.get("dimensions", {}).get(dim, {}).get("综合评分", 5.0)
    
    # 计算偏差
    errors = {}
    for dim in DIMENSIONS:
        pred = predictions.get(dim, 5.0)
        truth = case.labels.get(dim, 5)
        errors[dim] = round(pred - truth, 2)
    
    # 计算准确度（误差在±1.5内视为准确）
    hits = {}
    for dim in DIMENSIONS:
        hits[dim] = abs(errors[dim]) <= 1.5
    
    # 计算MAE和RMSE
    mae = sum(abs(e) for e in errors.values()) / len(errors)
    rmse = math.sqrt(sum(e**2 for e in errors.values()) / len(errors))
    
    # 收敛度解析
    conv_str = result.get("overall_convergence", "0%")
    convergence = float(conv_str.replace("%", "")) if "%" in conv_str else 0
    
    return {
        "name": case.name,
        "birth": f"{year}-{month:02d}-{day:02d} {case.hour:02d}时",
        "category": case.category,
        "labels": case.labels,
        "predictions": predictions,
        "errors": errors,
        "hits": hits,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "convergence": convergence,
        "available_systems": result.get("available_systems", {}),
        "note": case.note,
    }


def run_batch_cases(cases: List[TestCase], verbose: bool = False) -> Dict:
    """批量运行回测"""
    results = []
    
    print(f"\n{'='*70}")
    print(f"  河图命理回测引擎 v1.0")
    print(f"{'='*70}")
    print(f"  案例数: {len(cases)}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    for i, case in enumerate(cases):
        if verbose or (i + 1) % 5 == 0:
            print(f"[{i+1}/{len(cases)}] {case.name}...", end=" ", flush=True)
        
        try:
            r = run_single_case(case, verbose)
            results.append(r)
            if verbose or (i + 1) % 5 == 0:
                status = "✓" if r["mae"] <= 1.5 else "△"
                print(f"{status} MAE={r['mae']:.2f} RMSE={r['rmse']:.2f}")
        except Exception as e:
            print(f"✗ 错误: {e}")
            results.append({
                "name": case.name,
                "error": str(e),
            })
    
    return aggregate_results(results)


def aggregate_results(results: List[Dict]) -> Dict:
    """聚合回测结果"""
    valid_results = [r for r in results if "error" not in r]
    
    if not valid_results:
        return {"error": "无有效结果", "total": 0}
    
    # 各维度统计
    dim_stats = {}
    for dim in DIMENSIONS:
        preds = [r["predictions"].get(dim, 5) for r in valid_results]
        truths = [r["labels"].get(dim, 5) for r in valid_results]
        errors = [r["errors"].get(dim, 0) for r in valid_results]
        hits = [r["hits"].get(dim, False) for r in valid_results]
        
        mae = sum(abs(e) for e in errors) / len(errors) if errors else 0
        rmse = math.sqrt(sum(e**2 for e in errors) / len(errors)) if errors else 0
        accuracy = sum(1 for h in hits if h) / len(hits) * 100 if hits else 0
        
        # 相关系数
        if len(preds) > 1:
            mean_p = sum(preds) / len(preds)
            mean_t = sum(truths) / len(truths)
            cov = sum((p - mean_p) * (t - mean_t) for p, t in zip(preds, truths)) / len(preds)
            std_p = math.sqrt(sum((p - mean_p)**2 for p in preds) / len(preds))
            std_t = math.sqrt(sum((t - mean_t)**2 for t in truths) / len(truths))
            correlation = cov / (std_p * std_t) if std_p > 0 and std_t > 0 else 0
        else:
            correlation = 0
        
        dim_stats[dim] = {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "accuracy": round(accuracy, 1),
            "correlation": round(correlation, 3),
            "avg_pred": round(sum(preds) / len(preds), 2),
            "avg_truth": round(sum(truths) / len(truths), 2),
            "hit_count": sum(1 for h in hits if h),
        }
    
    # 整体统计
    all_mae = [r["mae"] for r in valid_results]
    all_rmse = [r["rmse"] for r in valid_results]
    all_conv = [r["convergence"] for r in valid_results]
    
    overall = {
        "total_cases": len(results),
        "valid_cases": len(valid_results),
        "avg_mae": round(sum(all_mae) / len(all_mae), 2),
        "avg_rmse": round(sum(all_rmse) / len(all_rmse), 2),
        "avg_convergence": round(sum(all_conv) / len(all_conv), 1),
        "overall_accuracy": round(sum(1 for r in valid_results if r["mae"] <= 1.5) / len(valid_results) * 100, 1),
    }
    
    # 分类统计
    category_stats = {}
    for r in valid_results:
        cat = r.get("category", "其他")
        if cat not in category_stats:
            category_stats[cat] = {"cases": [], "mae": []}
        category_stats[cat]["cases"].append(r["name"])
        category_stats[cat]["mae"].append(r["mae"])
    
    for cat in category_stats:
        mae_list = category_stats[cat]["mae"]
        category_stats[cat]["avg_mae"] = round(sum(mae_list) / len(mae_list), 2)
        category_stats[cat]["count"] = len(mae_list)
    
    return {
        "schema": "backtest_v1.0",
        "timestamp": datetime.now().isoformat(),
        "overall": overall,
        "dimensions": dim_stats,
        "categories": category_stats,
        "cases": valid_results,
    }


def generate_report(agg: Dict) -> str:
    """生成可读报告"""
    lines = [
        "═══════════════════════════════════════════════════════",
        "  河图命理回测报告",
        "═══════════════════════════════════════════════════════",
        "",
        f"回测时间: {agg['timestamp']}",
        f"有效案例: {agg['overall']['valid_cases']}/{agg['overall']['total_cases']}",
        "",
        "【整体表现】",
        f"  平均MAE: {agg['overall']['avg_mae']} (越小越好，理想值<1.5)",
        f"  平均RMSE: {agg['overall']['avg_rmse']} (越小越好)",
        f"  整体准确率: {agg['overall']['overall_accuracy']}% (误差≤1.5判定为准确)",
        f"  平均收敛度: {agg['overall']['avg_convergence']}%",
        "",
        "【各维度表现】",
    ]
    
    for dim, stats in agg.get("dimensions", {}).items():
        lines.append(f"  {dim:<4}: MAE={stats['mae']:.2f} | 准确率={stats['accuracy']:.1f}% | 相关={stats['correlation']:.3f}")
    
    lines.extend([
        "",
        "【分类表现】",
    ])
    
    for cat, stats in sorted(agg.get("categories", {}).items(), key=lambda x: x[1]["avg_mae"]):
        lines.append(f"  {cat:<8}: MAE={stats['avg_mae']:.2f} (n={stats['count']})")
    
    # 最佳/最差案例
    cases = agg.get("cases", [])
    if cases:
        sorted_by_mae = sorted(cases, key=lambda x: x.get("mae", 99))
        
        lines.extend([
            "",
            "【最佳预测TOP5】",
        ])
        for c in sorted_by_mae[:5]:
            lines.append(f"  {c['name']:<12} MAE={c['mae']:.2f} 收敛度={c['convergence']:.0f}%")
        
        lines.extend([
            "",
            "【需优化案例】",
        ])
        for c in sorted_by_mae[-3:]:
            lines.append(f"  {c['name']:<12} MAE={c['mae']:.2f} | 预测={c['predictions']} | 真实={c['labels']}")
    
    lines.extend([
        "",
        "═══════════════════════════════════════════════════════",
        "  河图出品 | 命理引擎持续进化中",
        "═══════════════════════════════════════════════════════",
    ])
    
    return "\n".join(lines)


def save_results(agg: Dict, output_dir: str = None):
    """保存结果到文件"""
    if output_dir is None:
        output_dir = _DEEP_DIR
    
    # 保存JSON
    json_path = os.path.join(output_dir, "latest_results.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(agg, f, ensure_ascii=False, indent=2)
    
    # 保存报告
    report = generate_report(agg)
    report_path = os.path.join(output_dir, "latest_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 结果已保存:")
    print(f"   JSON: {json_path}")
    print(f"   报告: {report_path}")
    
    return json_path, report_path


# ════════════════════════════════════════
# CLI入口
# ════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='河图命理回测引擎')
    parser.add_argument('--count', type=int, default=len(CALIBRATION_CASES),
                        help='回测案例数量')
    parser.add_argument('--case', type=str, default=None,
                        help='只跑指定案例')
    parser.add_argument('--validate', action='store_true',
                        help='验证所有校准案例')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细输出')
    
    args = parser.parse_args()
    
    # 检查体系可用性
    print("\n【体系状态】")
    avail = get_available_systems()
    for sys_name, is_avail in avail.items():
        status = "✓" if is_avail else "✗"
        print(f"  {sys_name}: {status}")
    print()
    
    # 选择案例
    if args.case:
        cases = [c for c in CALIBRATION_CASES if args.case in c.name]
        if not cases:
            print(f"未找到案例: {args.case}")
            return
    elif args.validate:
        cases = CALIBRATION_CASES
    else:
        cases = CALIBRATION_CASES[:args.count]
    
    # 运行回测
    agg = run_batch_cases(cases, args.verbose)
    
    # 输出报告
    print("\n" + generate_report(agg))
    
    # 保存结果
    save_results(agg)
    
    return agg


if __name__ == "__main__":
    main()
