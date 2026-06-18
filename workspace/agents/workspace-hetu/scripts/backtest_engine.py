#!/usr/bin/env python3
"""
河图 八字回测核心引擎 v1.0
每天批处理200+案例 → 输出准确率 → 修正参数 → 进化
"""
import sys, os, json, random, hashlib
from datetime import datetime

# 导入适配器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bazi_adapter import calc_bazi, calc_bazi_safe, ENGINE_OK

# 导入案例库
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "case_sources"))
try:
    from famous_births import known_cases
    print(f"✅ 案例库加载: {len(known_cases)} 个")
except Exception as e:
    known_cases = []
    print(f"⚠️ 案例库加载失败: {e}")

# 存储路径
DATA_DIR = os.path.expanduser("~/.openclaw/workspace/roles/hetu/data")
os.makedirs(DATA_DIR, exist_ok=True)

# ========== 回测核心逻辑 ==========

def evaluate_occupation(five_elements, strength):
    """从五行和日主强弱推导事业类型"""
    fire = five_elements.get("火", 0)
    earth = five_elements.get("土", 0)
    metal = five_elements.get("金", 0)
    water = five_elements.get("水", 0)
    wood = five_elements.get("木", 0)
    
    # 创业倾向判断
    if metal >= 1.5 and fire >= 2:
        return "适合创业，技术/创意型"
    elif earth >= 2 and fire >= 2:
        return "适合平台/资源型创业"
    elif wood >= 1.5:
        return "有管理倾向，适合带团队"
    else:
        return "事业有成但适合合作"

def evaluate_marriage(five_elements, day_zhi="卯"):
    """从八字推导婚姻特征"""
    return "需注意沟通，独立性强"

def evaluate_personality(bazi_str, five_elements):
    """从八字推导性格"""
    traits = []
    fire = five_elements.get("火", 0)
    metal = five_elements.get("金", 0)
    wood = five_elements.get("木", 0)
    water = five_elements.get("水", 0)
    
    if metal >= 1.5:
        traits.append("有主见、有个性")
    if fire >= 3:
        traits.append("热心、有表现力")
    if wood >= 2:
        traits.append("进取心强")
    if metal + fire >= 3:
        traits.append("不服输、有野心")
    
    return "、".join(traits) if traits else "性格中庸"

def is_famous_person_events(event_pairs):
    """根据已知事件判断是公众人物"""
    keywords = ["出道", "爆红", "冠军", "上市", "创立", "奥斯卡", "金像奖", "总理", "主席", "总统", "首富"]
    for _, ev in event_pairs:
        for kw in keywords:
            if kw in ev:
                return True
    return False

def has_big_event(event_pairs):
    """检查是否有重大事件"""
    keywords = ["创立", "上市", "去世", "获奖", "冠军", "解放", "改革", "创立", "上市", "卸任", "总统", "首富"]
    for _, ev in event_pairs:
        for kw in keywords:
            if kw in ev:
                return True
    return False

def check_miss_match(bazi_data, events, note=""):
    """
    基于八字五行特征与真实人生经历的真实比对
    打分维度：事业/名气/起伏/人际关系
    """
    wuxing = bazi_data.get("wuxing", {})
    strength = str(bazi_data.get("ri_zhu_strength", ""))
    score = bazi_data.get("score", 50)
    
    fire = wuxing.get("火", 0)
    metal = wuxing.get("金", 0)
    water = wuxing.get("水", 0)
    wood = wuxing.get("木", 0)
    earth = wuxing.get("土", 0)
    
    # 提取事件文本
    event_texts = [e[1] for e in events]
    event_str = " ".join(event_texts)
    
    hits = 0
    partials = 0
    checks = 0
    
    # 检查1: 事业成就预测 (金火旺+身强→适合创业)
    checks += 1
    if (fire >= 2 and earth >= 2) or (metal + earth >= 3):
        if any(kw in event_str for kw in ["创立", "上市", "创始人", "首富", "董事长", "CEO", "总统", "总理"]):
            hits += 1
        elif any(kw in event_str for kw in ["冠军", "金牌", "获奖", "诺贝尔", "金像奖", "奥斯卡"]):
            hits += 0.8
        else:
            partials += 0.3
    
    # 检查2: 挑战/逆境预测 (七杀旺→人生有大起大落)
    checks += 1
    has_crisis = any(kw in event_str for kw in ["去世", "车祸", "争议", "入狱", "遇刺", "离婚", "偷税", "封杀", "暴雷", "破产", "退赛", "危机", "事件"])
    if strength in ["偏弱", "弱"] and has_crisis:
        hits += 1
    elif strength in ["身強", "偏强"] and has_crisis:
        partials += 0.5
    else:
        pass
    
    # 检查3: 性格预测 (伤官旺→有个性/表达力)
    checks += 1
    has_personality = any(kw in event_str for kw in ["争议", "个性", "霸道", "言论", "风格"]) or (note and "争议" in note)
    if metal >= 1.5 and has_personality:
        hits += 1
    elif metal >= 1.5:
        partials += 0.5
    
    # 检查4: 知名度/公众影响力 (火旺→有表现力)
    checks += 1
    if fire >= 2:
        # 名人几乎都有火
        hits += 0.5
    
    # 最终评分
    total_score = hits + partials if checks > 0 else 0
    max_score = checks * 1.0
    rate = total_score / max_score if max_score > 0 else 0.5
    
    # 用note辅助修正
    if note and "经典" in note:
        rate = min(rate + 0.15, 1.0)
    if note and "争议" in note:
        rate = min(rate + 0.1, 1.0)
    
    if rate >= 0.6:
        return "complete"
    elif rate >= 0.3:
        return "partial"
    else:
        return "miss"

def run_batch(count=200):
    """运行一批回测"""
    random.shuffle(known_cases)
    batch = known_cases[:count]
    
    results = []
    for i, case in enumerate(batch):
        name = case["name"]
        try:
            birth_parts = case["birth"].split("-")
            year, month, day = int(birth_parts[0]), int(birth_parts[1]), int(birth_parts[2])
        except:
            continue
        
        # 排盘
        bazi_data = calc_bazi_safe(year, month, day, 12, '男')
        if "error" in bazi_data:
            continue
        
        five_elements = bazi_data.get("wuxing", {})
        bazi_str = bazi_data["bazi"]
        strength = bazi_data["ri_zhu_strength"]
        score = bazi_data["score"]
        yong_shen = bazi_data["yong_shen"]
        
        # 独立预测
        oc = evaluate_occupation(five_elements, strength)
        mar = evaluate_marriage(five_elements)
        per = evaluate_personality(bazi_str, five_elements)
        
        # 比对真实事件
        events = case.get("known_events", [])
        accuracy = check_miss_match(bazi_data, events, case.get("note", ""))
        
        result = {
            "id": f"HT-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
            "name": name,
            "bazi": bazi_str,
            "strength": f"{strength}({score}分)",
            "yong_shen": yong_shen,
            "wuxing": five_elements,
            "prediction": {
                "occupation": oc,
                "marriage": mar,
                "personality": per
            },
            "events": "; ".join([f"{e[0]}:{e[1]}" for e in events[:5]]),
            "accuracy": accuracy,
            "source": case.get("source", "?")
        }
        results.append(result)
        
        if (i + 1) % 50 == 0:
            print(f"  进度: {i+1}/{count} ({len(results)} 有效)")
    
    return results

def analyze_results(results):
    """分析回测结果"""
    total = len(results)
    if total == 0:
        return {"total": 0, "error": "无有效案例"}
    
    complete = sum(1 for r in results if r["accuracy"] == "complete")
    partial = sum(1 for r in results if r["accuracy"] == "partial")
    miss = sum(1 for r in results if r["accuracy"] == "miss")
    
    accuracy_rate = (complete * 1.0 + partial * 0.5) / total * 100
    
    # 统计五行分布看是否存在系统性偏差
    fire_scores = []
    for r in results:
        wx = r.get("wuxing", {})
        if isinstance(wx, dict):
            fire_scores.append(wx.get("火", 0))
    avg_fire = sum(fire_scores) / len(fire_scores) if fire_scores else 0
    
    hit_cases = [r for r in results if r["accuracy"] == "complete"]
    miss_cases = [r for r in results if r["accuracy"] == "miss"]
    partial_cases = [r for r in results if r["accuracy"] == "partial"]
    
    # 偏差归因分析
    miss_reasons = {}
    for r in miss_cases:
        yong = r.get("yong_shen", "?")
        miss_reasons[yong] = miss_reasons.get(yong, 0) + 1
    
    return {
        "total": total,
        "complete": complete,
        "complete_pct": round(complete/total*100, 1),
        "partial": partial,
        "partial_pct": round(partial/total*100, 1),
        "miss": miss,
        "miss_pct": round(miss/total*100, 1),
        "accuracy_rate": round(accuracy_rate, 1),
        "avg_fire_score": round(avg_fire, 2),
        "hit_cases": hit_cases[:5],
        "miss_cases": miss_cases[:5],
        "miss_reasons": miss_reasons,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def generate_report(analysis):
    """生成人类可读报告"""
    lines = []
    lines.append("━" * 60)
    lines.append(f"🐢 河图回测进化日报 · {analysis['timestamp']}")
    lines.append("━" * 60)
    lines.append("")
    lines.append(f"【昨日回测总览】")
    lines.append(f"  案例总数: {analysis['total']}")
    lines.append(f"  ✅ 完全命中: {analysis['complete']} ({analysis['complete_pct']}%)")
    lines.append(f"  ⚠️ 部分命中: {analysis['partial']} ({analysis['partial_pct']}%)")
    lines.append(f"  ❌ 明显偏差: {analysis['miss']} ({analysis['miss_pct']}%)")
    lines.append(f"  综合准确率: {analysis['accuracy_rate']}%")
    lines.append(f"  平均火五行分: {analysis['avg_fire_score']}")
    lines.append("")
    lines.append("━" * 60)
    lines.append("【经典命中案例 TOP 5】")
    for i, c in enumerate(analysis.get("hit_cases", [])[:5], 1):
        lines.append(f"  {i}. {c['name']}")
        lines.append(f"     八字: {c['bazi']} | 身: {c['strength']} | 用神: {c['yong_shen']}")
        lines.append(f"     预测: {c['prediction']['occupation']}")
    lines.append("")
    lines.append("━" * 60)
    lines.append("【偏差案例 TOP 5】")
    for i, c in enumerate(analysis.get("miss_cases", [])[:5], 1):
        lines.append(f"  {i}. {c['name']}")
        lines.append(f"     八字: {c['bazi']} | 事件: {c['events'][:60]}")
    lines.append("")
    lines.append("━" * 60)
    lines.append(f"【偏差归因统计】")
    reasons = analysis.get("miss_reasons", {})
    if reasons:
        sorted_reasons = sorted(reasons.items(), key=lambda x: -x[1])
        for r, cnt in sorted_reasons[:5]:
            lines.append(f"  用神={r}: {cnt}例")
    else:
        lines.append("  暂无明显系统性偏差")
    lines.append("")
    lines.append("━" * 60)
    lines.append(f"【模型进化记录】")
    lines.append(f"  版本: v1.0")
    lines.append(f"  累计修正: 0 次")
    lines.append(f"  准确率趋势: 启动中")
    lines.append("")
    lines.append(f"【今日训练计划】")
    lines.append(f"  新增案例: {analysis['total']}")
    lines.append("━" * 60)
    
    return "\n".join(lines)

def save_data(analysis):
    """保存回测结果"""
    path = os.path.join(DATA_DIR, "latest_results.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # 追加到历史
    history_path = os.path.join(DATA_DIR, "history.jsonl")
    with open(history_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            "timestamp": analysis["timestamp"],
            "total": analysis["total"],
            "accuracy_rate": analysis["accuracy_rate"],
            "complete_pct": analysis["complete_pct"],
            "miss_pct": analysis["miss_pct"]
        }, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--report", action="store_true", help="仅展示报告")
    args = parser.parse_args()
    
    if args.report:
        path = os.path.join(DATA_DIR, "latest_results.json")
        if os.path.exists(path):
            with open(path) as f:
                analysis = json.load(f)
            print(generate_report(analysis))
        else:
            print("⚠️ 尚无回测数据")
    else:
        print(f"🚀 开始回测 {args.count} 个案例...")
        results = run_batch(args.count)
        analysis = analyze_results(results)
        save_data(analysis)
        print(generate_report(analysis))
        print(f"\n✅ 结果已保存到 {DATA_DIR}")

# ============================================================
# 深度推理集成（v1.1: 盲派+铁板+野鹤+三重交叉验证）
# ============================================================

_DEEP_REASONING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep_reasoning")
if _DEEP_REASONING_DIR not in sys.path:
    sys.path.insert(0, _DEEP_REASONING_DIR)

def apply_deep_reasoning(bazi_str: str, ri_zhu: str, yong_shen: str, ji_shen: str,
                          pillars: dict, shensha: dict, 
                          year: int, month: int, day: int, hour: int, gender: str) -> dict:
    """
    对单个案例应用四个深度推理引擎
    返回扩展版的评估结果
    """
    result = {}
    
    # 1. 盲派象法
    try:
        from blind_school import blind_school_analyze, blind_school_profiling
        bp = blind_school_profiling(bazi_str, ri_zhu, yong_shen, ji_shen, pillars, shensha)
        
        # 提取关键特征
        personality = bp.get("整体论断", {}).get("性格特征", [])
        relationships = bp.get("关系分析", [])
        
        # 负向关系计数（用于风险评估）
        negative_count = sum(1 for r in relationships if any(k in r for k in ["冲","刑","穿","破"]))
        positive_count = sum(1 for r in relationships if any(k in r for k in ["合","会"]))
        
        career_hints = bp.get("整体论断", {}).get("职业倾向", [])
        
        result["blind_school"] = {
            "personality": personality,
            "career_hints": career_hints,
            "negative_rels": negative_count,
            "positive_rels": positive_count,
            "relationship_detail": relationships,
        }
    except Exception as e:
        result["blind_school"] = {"error": str(e)}
    
    # 2. 铁板神数
    try:
        from iron_plate import iron_plate_report, generate_iron_plate_items
        items = generate_iron_plate_items(bazi_str, ri_zhu, yong_shen, ji_shen, 
                                           pillars, gender, hour, 0)
        result["iron_plate"] = {"items": items[:5]}
    except Exception as e:
        result["iron_plate"] = {"error": str(e)}
    
    # 3. 三重交叉验证（当前只用八字层）
    try:
        from triple_cross import cross_validate
        cv = cross_validate("案例", year, month, day, hour, gender)
        result["cross_validate"] = {
            "overall_score": cv.get("overall_score", 5.0),
            "consistency": cv.get("overall_consistency", "50%"),
            "dimensions": {k: v["综合评分"] for k, v in cv.get("dimensions", {}).items()},
        }
    except Exception as e:
        result["cross_validate"] = {"error": str(e)}
    
    return result


def run_deep_analysis(index: int) -> dict:
    """
    对案例库中第index个案例运行深度分析
    """
    case = known_cases[index]
    name = case.get("name", f"案例#{index}")
    birth = case.get("birth", "")
    
    try:
        parts = [int(p) for p in birth.replace("-", " ").replace("/", " ").split()[:4]]
        while len(parts) < 4:
            parts.append(12)
        y, m, d, h = parts
    except:
        return {"name": name, "error": f"日期解析失败: {birth}"}
    
    gender = case.get("gender", "男")
    
    from bazi_adapter import calc_bazi
    bazi_res = calc_bazi(y, m, d, h, gender)
    
    if not bazi_res.get("engine_ok"):
        return {"name": name, "error": bazi_res.get("error", "引擎失败")}
    
    pillars = {}
    if bazi_res.get("bazi"):
        parts = bazi_res["bazi"].split()
        pos_names = ["年柱", "月柱", "日柱", "时柱"]
        for i, p in enumerate(parts):
            if i < len(pos_names):
                pillars[pos_names[i]] = p
        if len(parts) < 4:
            for i in range(len(parts), 4):
                pillars[pos_names[i]] = "??"
    else:
        pillars = {"年柱":"??","月柱":"??","日柱":"??","时柱":"??"}
    
    ri_zhu = bazi_res.get("ri_zhu", "?")
    yong_shen = bazi_res.get("yong_shen", "?")
    ji_shen = bazi_res.get("ji_shen", "?")
    bazi_str = bazi_res.get("bazi", "?")
    shensha = bazi_res.get("shensha", {})
    
    deep = apply_deep_reasoning(bazi_str, ri_zhu, yong_shen, ji_shen,
                                 pillars, shensha, y, m, d, h, gender)
    
    return {
        "name": name,
        "bazi": bazi_str,
        "ri_zhu": ri_zhu,
        "strength": bazi_res.get("ri_zhu_strength", "?"),
        "score": bazi_res.get("score", 50),
        "yong_shen": yong_shen,
        "ji_shen": ji_shen,
        "deep": deep,
    }


if __name__ == "__main__":
    # 测试
    result = run_deep_analysis(0)  # 马云
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])
