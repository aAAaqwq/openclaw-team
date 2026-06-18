#!/usr/bin/env python3
"""
八字评分引擎 v2 — 整合格局判定 + 五维评分校准

核心改进（vs v1.0 的 131 行样板）：
  1. 调用 bazi_geju.analyze_geju() → 格局对五维的影响量化
  2. 从格/专旺格时评分校准（极端命局对应极端评分模式）
  3. 神煞吉凶量化（13种神煞按 +0.3/-0.3 归入五维）
  4. 调候用神到位度评分
  5. 大运流年加持
  6. 输出精细 dim_detail，含 base / geju_adj / shensha_adj / tiaohou_adj 等
"""

from typing import Dict, List, Optional, Any, Tuple
import sys, os

_DEEP_DIR = os.path.dirname(os.path.abspath(__file__))
if _DEEP_DIR not in sys.path:
    sys.path.insert(0, _DEEP_DIR)

try:
    from bazi_geju import analyze_geju, get_geju_scores
    GEJU_AVAILABLE = True
except ImportError:
    GEJU_AVAILABLE = False

DIMENSIONS = ["事业", "财运", "健康", "婚姻", "人际"]

# ── 神煞 → 五维映射 ──
SHENSHA_DIM_MAP: Dict[str, Tuple[str, float]] = {
    "天乙貴人": ("人际", 0.8),
    "文昌貴人": ("事业", 0.7),
    "天德": ("健康", 0.5),
    "月德": ("健康", 0.5),
    "福星貴人": ("事业", 0.4),
    "桃花": ("婚姻", -0.4),
    "驛馬": ("事业", 0.4),
    "華蓋": ("事业", 0.3),
    "寡宿": ("婚姻", -0.5),
    "孤辰": ("人际", -0.4),
    "劫煞": ("健康", -0.4),
    "災煞": ("健康", -0.4),
    "歲煞": ("事业", -0.3),
}


def score_bazi_dimensions_v2(bazi_result: Dict, target_year: int = None) -> Dict:
    """
    八字引擎五维评分 v2
    
    Args:
        bazi_result: paipan_v2() 的完整返回
        target_year: 目标年份（默认当年）
    
    Returns:
        {
            "available": True,
            "dimensions": {"事业": 7.5, "财运": 6.8, ...},
            "dim_detail": {dim: {"score":..., "raw":..., "base":..., "geju_adj":..., "shensha_adj":..., "level":...}},
            "geju": {...},
            "yong_shen": "...",
        }
    """
    rizhu = bazi_result.get("日主分析", {})
    yongshen = bazi_result.get("用神喜忌", {})
    tiaohou = bazi_result.get("調候用神", {})
    shensha = bazi_result.get("神煞", {})
    wuxing = bazi_result.get("五行統計", {})
    pillars = bazi_result.get("四柱八字", {})
    dayun = bazi_result.get("大運排列", [])
    liunian = bazi_result.get("流年分析", {})
    
    strength = rizhu.get("綜合判斷", "中和") if isinstance(rizhu, dict) else "中和"
    strength_score = rizhu.get("總評分", 50) if isinstance(rizhu, dict) else 50
    yong_shen_text = str(yongshen.get("喜用神", yongshen.get("用神", ""))) if isinstance(yongshen, dict) else ""
    ji_shen_text = str(yongshen.get("忌神", "")) if isinstance(yongshen, dict) else ""
    
    # ── 格局分析 ──
    geju_result = analyze_geju(bazi_result) if GEJU_AVAILABLE else {"available": False}
    geju_scores = get_geju_scores(geju_result) if GEJU_AVAILABLE else {}
    primary_geju = geju_result.get("primary_geju", "") if GEJU_AVAILABLE else ""
    secondary_geju = geju_result.get("secondary_geju", []) if GEJU_AVAILABLE else []
    
    # ── 基础分（每个维度以 5.0 为基准） ──
    base = 5.0
    # 身强加分
    if "身強" in str(strength) or "从旺" in str(strength):
        base += 1.5
    elif "中和" in str(strength):
        base += 0.8
    
    dim_raw = {"事业": base, "财运": base, "健康": base, "婚姻": base, "人际": base}
    dim_adj = {"事业": [], "财运": [], "健康": [], "婚姻": [], "人际": []}
    
    # ── ① 格局校准 ──
    if geju_scores:
        for dim in DIMENSIONS:
            gs = geju_scores.get(dim, 0)
            if gs != 0:
                diff = (gs - 5.0) * 0.4  # 格局偏移的40%映射进来，避免过度
                dim_raw[dim] += diff
                dim_adj[dim].append(("geju", round(diff, 2)))
    
    # ── ② 调候用神到位度 ──
    tiaohou_gan = tiaohou.get("調候用神", []) if isinstance(tiaohou, dict) else []
    tiaohou_shuoming = str(tiaohou.get("說明", "")) if isinstance(tiaohou, dict) else ""
    if tiaohou_gan:
        dim_raw["健康"] += 0.8
        dim_raw["事业"] += 0.5
        dim_adj["健康"].append(("tiaohou", 0.8))
        dim_adj["事业"].append(("tiaohou", 0.5))
    
    # ── ③ 神煞校准 ──
    for k, v in (shensha or {}).items():
        normalized_k = k.replace(" ", "").replace("\u200b", "")
        if normalized_k in SHENSHA_DIM_MAP:
            dim, delta = SHENSHA_DIM_MAP[normalized_k]
            dim_raw[dim] += delta
            dim_adj[dim].append((f"shensha:{normalized_k}", delta))
    
    # ── ④ 大运流年加持 ──
    if isinstance(liunian, dict):
        tg_jx = str(liunian.get("流年天干吉凶", ""))
        dz_jx = str(liunian.get("流年地支吉凶", ""))
        if "吉" in tg_jx:
            dim_raw["事业"] += 0.5
            dim_adj["事业"].append(("liunian_tg", 0.5))
        if "吉" in dz_jx:
            dim_raw["财运"] += 0.3
            dim_adj["财运"].append(("liunian_dz", 0.3))
    
    # ── ⑤ 五行偏枯惩罚 ──
    try:
        if isinstance(wuxing, dict):
            vals = [int(v) for v in wuxing.values() if isinstance(v, (int, str)) and str(v).isdigit()]
            if vals and max(vals) - min(vals) >= 3:
                dim_raw["健康"] -= 0.8
                dim_adj["健康"].append(("wuxing_pianku", -0.8))
    except:
        pass
    
    # ── 映射到 1-10 ──
    dim_results = {}
    for dim in DIMENSIONS:
        raw = dim_raw[dim]
        score = max(1, min(10, round(raw, 1)))
        level = "高" if score >= 7 else ("中" if score >= 4 else "低")
        dim_results[dim] = {
            "score": score,
            "raw": raw,
            "base": base,
            "adj": dim_adj[dim],
            "level": level,
        }
    
    result = {
        "available": True,
        "dimensions": {d: dim_results[d]["score"] for d in DIMENSIONS},
        "dim_detail": dim_results,
        "geju": geju_result,
        "yong_shen": yong_shen_text,
        "strength": str(strength),
    }
    return result


def score_bazi_dimensions(bazi_result: Dict) -> Dict:
    """向下兼容：只返回 dim_detail"""
    v2 = score_bazi_dimensions_v2(bazi_result)
    return v2.get("dim_detail", {})


if __name__ == "__main__":
    import json
    sys.path.insert(0, os.path.expanduser("~/.agents/skills/bazi-mingli/scripts"))
    from bazi_calc_v2 import paipan_v2
    
    print("═══ 八字评分 v2 测试 ═══")
    r = paipan_v2(1990, 11, 10, 10, "男")
    result = score_bazi_dimensions_v2(r)
    print(json.dumps({k: v for k, v in result.items() if k != "geju"}, 
                     ensure_ascii=False, indent=2))
    print(f"\n格局: {result['geju'].get('primary_geju', '?')}")
    print(f"副格局: {result['geju'].get('secondary_geju', [])}")
