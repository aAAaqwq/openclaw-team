#!/usr/bin/env python3
"""
河图 · 三重交叉验证校准器 v1.0

校准方法：
  1. 选取20个有客观人生轨迹的名人案例
  2. 为每个案例的五维（事业/财运/健康/婚姻/人际）打客观标签
  3. 三个体系各跑一次评分
  4. 计算每个体系各维度的偏差、均方根误差(RMSE)
  5. 自动调整每个体系每个维度的评分函数参数
  6. 输出校准参数集，供 triple_cross.py 使用

校准目标：
  三个体系输出到同一刻度后，一致性应 > 60%
"""

import sys, os, json, math
from typing import Dict, List, Tuple, Optional

# 加入 paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/.agents/skills/bazi-mingli/scripts"))
sys.path.insert(0, os.path.expanduser("~/.agents/skills/ziwei-doushu/scripts"))
sys.path.insert(0, os.path.expanduser("~/.agents/skills/qimen-dunjia/scripts"))

# ============================================================
# 1. 校准案例集（20个黄金案例 + 客观标签）
# ============================================================
# 标签格式：{维度: 客观评分(1-10)}
# 标签标准：基于真实人生事件，而非命理
#   1-3 = 极差 / 4-5 = 偏弱 / 6-7 = 中上 / 8-9 = 优秀 / 10 = 顶级

CALIBRATION_CASES = [
    # ═══ 企业家 ═══
    {
        "name": "马云",
        "birth": (1964, 9, 10), "hour": 12, "gender": "男",
        "label": {"事业": 10, "财运": 10, "健康": 8, "婚姻": 7, "人际": 9},
        "note": "阿里创始人，顶级事业和财富；婚姻稳定但退居二线后低调",
    },
    {
        "name": "任正非",
        "birth": (1944, 10, 25), "hour": 12, "gender": "男",
        "label": {"事业": 10, "财运": 9, "健康": 8, "婚姻": 4, "人际": 8},
        "note": "华为天花板级别事业；婚姻两次不顺；中年患抑郁但挺过来",
    },
    {
        "name": "马化腾",
        "birth": (1971, 10, 29), "hour": 12, "gender": "男",
        "label": {"事业": 10, "财运": 10, "健康": 7, "婚姻": 8, "人际": 6},
        "note": "腾讯创始人；低调婚姻；性格偏内向",
    },
    {
        "name": "雷军",
        "birth": (1969, 12, 16), "hour": 12, "gender": "男",
        "label": {"事业": 10, "财运": 9, "健康": 8, "婚姻": 8, "人际": 8},
        "note": "小米+金山；劳模型事业节奏；婚姻平稳",
    },
    # ═══ 政治家 ═══
    {
        "name": "毛泽东",
        "birth": (1893, 12, 26), "hour": 8, "gender": "男",
        "label": {"事业": 10, "财运": 1, "健康": 5, "婚姻": 3, "人际": 7},
        "note": "建党建国，顶级政治成就；个人财富极微；一生多次长征重伤；婚姻三段坎坷",
    },
    {
        "name": "周恩来",
        "birth": (1898, 3, 5), "hour": 8, "gender": "男",
        "label": {"事业": 9, "财运": 4, "健康": 4, "婚姻": 8, "人际": 10},
        "note": "总理级事业但非一把手；清廉；患膀胱癌；婚姻稳（邓颖超）；人际关系顶级",
    },
    {
        "name": "邓小平",
        "birth": (1904, 8, 22), "hour": 8, "gender": "男",
        "label": {"事业": 10, "财运": 2, "health": 6, "婚姻": 7, "人际": 8},
        "note": "改革开放核心；个人极简；三起三落；两段婚姻",
    },
    # ═══ 科学家 ═══
    {
        "name": "爱因斯坦",
        "birth": (1879, 3, 14), "hour": 11, "gender": "男",
        "label": {"事业": 10, "财运": 5, "健康": 6, "婚姻": 3, "人际": 5},
        "note": "物理革命；诺贝尔奖金维持生活；腹主动脉瘤；婚姻两段皆不顺；性格孤僻",
    },
    {
        "name": "史蒂芬·霍金",
        "birth": (1942, 1, 8), "hour": 8, "gender": "男",
        "label": {"事业": 9, "财运": 6, "健康": 1, "婚姻": 5, "人际": 6},
        "note": "理论物理巨匠，但身体ALS极差；经济尚可；婚姻出现裂痕",
    },
    {
        "name": "屠呦呦",
        "birth": (1930, 12, 30), "hour": 8, "gender": "女",
        "label": {"事业": 9, "财运": 4, "健康": 6, "婚姻": 7, "人际": 5},
        "note": "诺奖级科学成就；清贫学者；婚姻稳定；性格专注低调",
    },
    {
        "name": "牛顿",
        "birth": (1643, 1, 4), "hour": 8, "gender": "男",
        "label": {"事业": 10, "财运": 7, "健康": 7, "婚姻": 0, "人际": 2},
        "note": "物理+数学双革命；皇家铸币局长有钱；终身未婚；性格孤僻好斗",
    },
    # ═══ 文学/艺术 ═══
    {
        "name": "李白",
        "birth": (701, 2, 28), "hour": 12, "gender": "男",
        "label": {"事业": 9, "财运": 3, "健康": 6, "婚姻": 5, "人际": 9},
        "note": "诗仙级文才；一生潦倒；嗜酒影响健康；婚姻一般；交游极广",
    },
    {
        "name": "莎士比亚",
        "birth": (1564, 4, 23), "hour": 8, "gender": "男",
        "label": {"事业": 10, "财运": 8, "健康": 5, "婚姻": 5, "人际": 8},
        "note": "文学巅峰；剧院投资成功；52岁病逝；婚姻中年分居",
    },
    {
        "name": "杜甫",
        "birth": (712, 2, 12), "hour": 12, "gender": "男",
        "label": {"事业": 9, "财运": 2, "健康": 3, "婚姻": 7, "人际": 7},
        "note": "诗圣级文才；穷困潦倒流浪；58岁病逝；对妻子忠贞",
    },
    # ═══ 演艺 ═══
    {
        "name": "迈克尔·杰克逊",
        "birth": (1958, 8, 29), "hour": 12, "gender": "男",
        "label": {"事业": 10, "财运": 9, "健康": 3, "婚姻": 2, "人际": 4},
        "note": "流行之王；亿万身家但后期债务缠身；白癜风/健康差；两段婚姻失败；朋友少",
    },
    {
        "name": "奥普拉",
        "birth": (1954, 1, 29), "hour": 4, "gender": "女",
        "label": {"事业": 10, "财运": 10, "健康": 7, "婚姻": 7, "人际": 10},
        "note": "传媒女王；亿万富豪；中年健康问题；与男友长期未婚；人脉极广",
    },
    # ═══ 运动员 ═══
    {
        "name": "迈克尔·乔丹",
        "birth": (1963, 2, 17), "hour": 14, "gender": "男",
        "label": {"事业": 10, "财运": 10, "健康": 8, "婚姻": 5, "人际": 7},
        "note": "篮球之神；品牌年收入过亿；早年健康顶级；两次离婚",
    },
    {
        "name": "姚明",
        "birth": (1980, 9, 12), "hour": 14, "gender": "男",
        "label": {"事业": 9, "财运": 9, "健康": 4, "婚姻": 9, "人际": 9},
        "note": "NBA球星+姚主席；商业价值高；脚伤终结生涯；婚姻幸福；人缘极好",
    },
    {
        "name": "C罗",
        "birth": (1985, 2, 5), "hour": 10, "gender": "男",
        "label": {"事业": 10, "财运": 9, "健康": 9, "婚姻": 4, "人际": 6},
        "note": "顶级足球运动员；商业帝国；自律健康顶级；未婚有子；争议性性格",
    },
    # ═══ 高争议/特殊性 ═══
    {
        "name": "乔布斯",
        "birth": (1955, 2, 24), "hour": 19, "gender": "男",
        "label": {"事业": 10, "财运": 10, "健康": 2, "婚姻": 5, "人际": 3},
        "note": "苹果神话；被赶出自己公司又王者归来；56岁胰腺癌逝；私生女事件；人际关系差",
    },
]

# ============================================================
# 2. 评分运行器
# ============================================================

def run_all_systems(name: str, birth: Tuple, hour: int, gender: str) -> Dict:
    """对一个案例跑三个体系的完整评分"""
    year, month, day = birth
    result = {}

    # 八字
    try:
        from bazi_calc_v2 import paipan_v2
        r = paipan_v2(year, month, day, hour, gender, 2026)
        rizhu = r.get("日主分析", {})
        score = rizhu.get("總評分", 50) if isinstance(rizhu, dict) else 50
        dims = {}
        for d in ["事业", "财运", "健康", "婚姻", "人际"]:
            dims[d] = min(10, score // 10 + 2)
        result["八字"] = dims
    except Exception as e:
        result["八字"] = {"error": str(e)}

    # 紫微
    try:
        from ziwei_qimen_scores import get_ziwei_scores
        zws = get_ziwei_scores(year, month, day, hour, gender)
        if zws.get("available"):
            result["紫微"] = {k: v["score"] for k, v in zws.get("dim_detail", {}).items()}
        else:
            result["紫微"] = {"error": zws.get("error", "?")}
    except Exception as e:
        result["紫微"] = {"error": str(e)}

    # 奇门
    try:
        from ziwei_qimen_scores import get_qimen_scores
        qms = get_qimen_scores(year, month, day, 8, 0)
        if qms.get("available"):
            result["奇门"] = {k: v["score"] for k, v in qms.get("dim_detail", {}).items()}
        else:
            result["奇门"] = {"error": qms.get("error", "?")}
    except Exception as e:
        result["奇门"] = {"error": str(e)}

    return result


# ============================================================
# 3. 偏差计算
# ============================================================

DIMENSIONS = ["事业", "财运", "健康", "婚姻", "人际"]
SYSTEMS = ["八字", "紫微", "奇门"]


def calc_bias(label: Dict, systems_score: Dict) -> Dict:
    """
    计算每个体系每个维度的偏差（预测 - 标签），以及RMSE
    """
    biases = {}
    for sys_name in SYSTEMS:
        sys_result = systems_score.get(sys_name, {})
        biases[sys_name] = {}
        for dim in DIMENSIONS:
            pred = sys_result.get(dim)
            truth = label.get(dim, 5)
            if pred is not None:
                biases[sys_name][dim] = round(pred - truth, 2)
            else:
                biases[sys_name][dim] = None
    
    # 计算每个体系的RMSE
    rmse = {}
    for sys_name in SYSTEMS:
        errs = [v**2 for v in biases[sys_name].values() if v is not None]
        rmse[sys_name] = round(math.sqrt(sum(errs) / len(errs)) if errs else 99.9, 2)
    
    return {"biases": biases, "rmse": rmse}


def calc_consistency(systems_score: Dict) -> float:
    """计算三个体系一致性（当前算法）"""
    scores_by_dim = {}
    for dim in DIMENSIONS:
        vals = []
        for s in SYSTEMS:
            v = systems_score.get(s, {}).get(dim)
            if v is not None:
                vals.append(v)
        if len(vals) >= 2:
            scores_by_dim[dim] = max(0, 100 - (max(vals) - min(vals)) * 20)
        else:
            scores_by_dim[dim] = 50
    return round(sum(scores_by_dim.values()) / len(scores_by_dim), 1)


# ============================================================
# 4. 校准运行器
# ============================================================

def run_calibration():
    """主校准流程"""
    all_results = []
    all_biases = {s: {d: [] for d in DIMENSIONS} for s in SYSTEMS}
    all_system_scores = {s: {d: [] for d in DIMENSIONS} for s in SYSTEMS}
    all_labels = {d: [] for d in DIMENSIONS}
    consistencies = []
    
    print(f"═══ 三重交叉验证校准 ═══")
    print(f"校准案例: {len(CALIBRATION_CASES)} 个")
    print()
    
    for case in CALIBRATION_CASES:
        name = case["name"]
        label = case["label"]
        birth = case["birth"]
        hour = case["hour"]
        gender = case["gender"]
        note = case.get("note", "")
        
        score = run_all_systems(name, birth, hour, gender)
        bias_data = calc_bias(label, score)
        consistency = calc_consistency(score)
        consistencies.append(consistency)
        
        all_results.append({
            "name": name,
            "label": label,
            "scores": score,
            "biases": bias_data["biases"],
            "rmse": bias_data["rmse"],
            "consistency": consistency,
        })
        
        # 累加偏差数据
        for s in SYSTEMS:
            for dim in DIMENSIONS:
                b = bias_data["biases"].get(s, {}).get(dim)
                sv = score.get(s, {}).get(dim)
                if b is not None:
                    all_biases[s][dim].append(b)
                if sv is not None:
                    all_system_scores[s][dim].append(sv)
        
        for dim in DIMENSIONS:
            all_labels[dim].append(label.get(dim, 5))
    
    # 聚合分析
    print("【每案例偏差表】")
    print(f"{'人物':<12} {'一致性':<8} {'八字RMSE':<10} {'紫微RMSE':<10} {'奇门RMSE':<10} {'备注'}")
    print("-" * 70)
    for r in all_results:
        rmse = r["rmse"]
        note = CALIBRATION_CASES[[c["name"] for c in CALIBRATION_CASES].index(r["name"])].get("note", "")
        print(f"{r['name']:<12} {r['consistency']:<8}%  {rmse.get('八字',99):<10}  {rmse.get('紫微',99):<10}  {rmse.get('奇门',99):<10}  {note[:20]}")
    
    print()
    
    # 整体偏差统计
    print("【各体系各维度平均偏差（偏正=高估，偏负=低估）】")
    print(f"{'':12} ", end="")
    for dim in DIMENSIONS:
        print(f"{dim:>8}", end="")
    print()
    
    for s in SYSTEMS:
        print(f"{s:<8} ", end="")
        for dim in DIMENSIONS:
            vals = all_biases[s][dim]
            if vals:
                avg_bias = round(sum(vals) / len(vals), 2)
                print(f"{avg_bias:>8}", end="")
            else:
                print(f"{'N/A':>8}", end="")
        print()
    
    print()
    
    # 整体RMSE
    print("【整体RMSE（均方根误差）】")
    for s in SYSTEMS:
        all_vals = [v for vv in all_biases[s].values() for v in vv]
        rmse = round(math.sqrt(sum(v**2 for v in all_vals) / len(all_vals)), 2) if all_vals else 99
        print(f"{s}: RMSE = {rmse}")
    
    avg_consistency = round(sum(consistencies) / len(consistencies), 1) if consistencies else 0
    print(f"\n平均一致性: {avg_consistency}%")
    
    # 分析偏差模式，生成校准参数建议
    print()
    print("【校准参数建议（基于平均偏差）】")
    print("# 使用方法：将每个体系每个维度的评分做线性变换 y = a*x + b")
    print(f"# a = 1.0 (暂不调整斜率), b = -avg_bias (纠偏)")
    params = {}
    for s in SYSTEMS:
        params[s] = {}
        for dim in DIMENSIONS:
            vals = all_biases[s][dim]
            if vals:
                avg_bias = round(sum(vals) / len(vals), 2)
                # 补偿量 = -avg_bias
                params[s][dim] = {"b补偿": round(-avg_bias, 2)}
                print(f"  {s}-{dim}: y = x + ({-avg_bias:+.2f})  平均偏差 {avg_bias:+.2f}")
    
    # 导出 params
    print()
    print(f"# 校准参数JSON:")
    print(json.dumps(params, ensure_ascii=False, indent=2))
    
    return all_results, params


# ============================================================
# 5. 将校准参数写入 triple_cross.py
# ============================================================

def apply_calibration_to_triple_cross():
    """读取校准参数并嵌入triple_cross.py"""
    _, params = run_calibration()
    
    tc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "triple_cross.py")
    with open(tc_path, 'r') as f:
        content = f.read()
    
    # 构建参数块
    param_code = f"""

# ============================================================
# 【校准参数】自动生成于 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
# 使用方法：每个体系每个维度的原始评分经过校准后：
#   calibrated_score = min(10, max(1, raw_score + CALIBRATION_OFFSETS['体系']['维度']))
# ============================================================

CALIBRATION_OFFSETS = {json.dumps(params, ensure_ascii=False, indent=4)}

def apply_calibration(system_scores: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    \"\"\"将校准偏移应用到体系评分上\"\"\"
    calibrated = {{}}
    for sys_name, dims in system_scores.items():
        calibrated[sys_name] = {{}}
        offsets = CALIBRATION_OFFSETS.get(sys_name, {{}})
        for dim, raw_val in dims.items():
            offset = offsets.get(dim, {{}}).get('b补偿', 0)
            calibrated[sys_name][dim] = max(1, min(10, round(raw_val + offset, 1)))
    return calibrated

"""
    
    # 检查是否已有校准参数
    if "# 校准参数" in content or "CALIBRATION_OFFSETS" in content:
        print("⚠️ triple_cross.py 已有校准参数，将覆盖更新")
    
    # 找到import之后、分析函数之前的插入点
    insert_pos = content.find("# ============================================================\n# 最终交叉验证")
    if insert_pos == -1:
        insert_pos = content.rfind("# ============================================================\n")
    
    # 在最终交叉验证之前插入校准模块
    new_content = content[:insert_pos] + param_code + "\n\n" + content[insert_pos:]
    
    with open(tc_path, 'w') as f:
        f.write(new_content)
    
    print(f"\n✅ 校准参数已写入 {tc_path}")
    return True


if __name__ == "__main__":
    print("═" * 60)
    print("  河图·三重交叉验证 校准器 v1.0")
    print("═" * 60)
    print()
    run_calibration()
    print()
    print("═══════════════════════════════════════════════════════")
    print("  校准建议: 分析偏差模式后，调整评分函数或嵌入偏移")
    print("═══════════════════════════════════════════════════════")
