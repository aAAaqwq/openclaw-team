#!/usr/bin/env python3
"""
河图 · 紫微/奇门维度分析器 v1.0
完善三重交叉验证中的紫微和奇门评分能力

核心思路：
  紫微 → 十二宫星曜组合 → 五维评分
  奇门 → 用神/旺衰/门星神 → 五维评分

对接外部引擎：
  - ~/.agents/skills/ziwei-doushu/scripts/ziwei_v3.py → paipan() (v3增强)
  - ~/.agents/skills/qimen-dunjia/scripts/qimen_calc.py → full_qimen_calculation()

版本历史：
v1.0: 基础星曜吉凶累加
v2.0 (本次): 使用 ziwei_v3 引擎，整合格局自动判定+庙旺利陷+四化演绎+空宫借星
"""

from typing import Dict, List, Optional, Tuple, Any
import sys, os

# ============================================================
# 紫微维度分析 v2.0（整合 v3 引擎）
# ============================================================

ZIWEI_PATH = os.path.expanduser("~/.agents/skills/ziwei-doushu/scripts")
if ZIWEI_PATH not in sys.path:
    sys.path.insert(0, ZIWEI_PATH)

try:
    from ziwei_v3 import paipan as ziwei_paipan_v2  # v2兼容
    from ziwei_v3 import paipan_v3 as ziwei_paipan_v3  # v3增强
    ZIWEI_OK = True
except ImportError:
    try:
        from ziwei_v2 import paipan as ziwei_paipan_v2
        ZIWEI_OK = True
        ziwei_paipan_v3 = None
    except ImportError:
        ZIWEI_OK = False
        ziwei_paipan_v3 = None

# ── 星曜吉凶基准 + 庙旺利陷权重系数 ──
ZHU_XING_MIAOXIAN = {
    # 14主星在12地支的庙旺利陷（数值化：5庙/4旺/3得地/2利益/1平和/0不得地/-1陷）
    # 格式: {星名: {地支索引: 等级}}
}

# 简化版：主星基础吉凶分 + 默认庙旺系数
ZHU_XING_BASE = {
    "紫微": 8, "天机": 7, "太阳": 8, "武曲": 8, "天同": 7, "廉贞": 6,
    "天府": 8, "太阴": 7, "贪狼": 5, "巨门": 4, "天相": 7, "天梁": 7,
    "七杀": 5, "破军": 4,
    "左辅": 6, "右弼": 6, "文昌": 7, "文曲": 7,
    "天魁": 8, "天钺": 7, "禄存": 7,
    "火星": 3, "铃星": 3, "擎羊": 2, "陀罗": 2,
    "地空": 3, "地劫": 3,
}

STAR_TO_DIM = {
    "紫微": "事业", "天机": "事业", "太阳": "人际", "武曲": "财运",
    "天同": "健康", "廉贞": "事业", "天府": "财运", "太阴": "婚姻",
    "贪狼": "人际", "巨门": "人际", "天相": "婚姻", "天梁": "健康",
    "七杀": "事业", "破军": "事业",
    "左辅": "人际", "右弼": "人际", "文昌": "事业", "文曲": "事业",
    "天魁": "人际", "天钺": "人际", "禄存": "财运",
    "火星": "健康", "铃星": "健康", "擎羊": "事业", "陀罗": "事业",
    "地空": "财运", "地劫": "财运",
}

# 四化对维度的增益
SIHUA_DIM = {"禄": "财运", "权": "事业", "科": "事业", "忌": "健康"}


def _get_star_miaoxian_coeff(star_name: str, zhi_index: int) -> float:
    """获取星曜在某一地支的庙旺利陷系数"""
    mf_map = {
        "紫微": [5,5,3,3,5,1,5,3,3,3,3,1],
        "天机": [3,1,5,3,3,5,3,5,3,1,3,5],
        "太阳": [5,1,3,3,3,3,5,1,1,3,3,3],
        "武曲": [3,3,3,5,3,5,5,1,3,3,3,5],
        "天同": [3,5,3,5,3,5,1,3,3,5,3,3],
        "廉贞": [3,5,3,3,5,3,5,3,5,3,3,5],
        "天府": [5,5,3,3,3,1,5,3,3,3,3,1],
        "太阴": [3,5,3,5,3,5,1,3,3,5,3,3],
        "贪狼": [3,5,3,1,5,3,1,3,5,1,1,5],
        "巨门": [3,1,3,5,3,3,3,5,1,3,3,3],
        "天相": [3,3,1,3,3,5,3,5,3,3,3,3],
        "天梁": [3,5,3,5,3,5,1,3,3,5,3,3],
        "七杀": [5,3,3,3,5,3,3,3,5,3,1,5],
        "破军": [5,3,1,3,5,1,3,5,3,5,3,1],
    }
    coeffs = mf_map.get(star_name, [3]*12)
    idx = zhi_index % 12
    return coeffs[idx] / 3.0  # 归一化: 5庙→1.67, 3得地→1.0, 1平和→0.33, -1陷→-0.33


def analyze_ziwei_dimension(year: int, month: int, day: int, 
                              hour: int = 12, gender: str = "男") -> Dict:
    """
    紫微斗数五维评分分析 v2.0
    
    使用 v3 引擎（若可用），整合：
      - 星曜+庙旺利陷
      - 格局自动判定
      - 四化演绎
      - 空宫借星
    """
    if not ZIWEI_OK:
        return {"available": False, "error": "紫微引擎未加载"}
    
    # 优先使用 v3 引擎
    try:
        if ziwei_paipan_v3:
            result = ziwei_paipan_v3(year, month, day, hour, gender)
        else:
            result = ziwei_paipan_v2(year, month, day, hour, gender)
        v3_mode = bool(ziwei_paipan_v3 and '格局列表' in result)
    except Exception as e:
        return {"available": False, "error": str(e)}
    
    gongs = result.get("十二宫", [])
    dizhi_map = {"子":0,"丑":1,"寅":2,"卯":3,"辰":4,"巳":5,
                 "午":6,"未":7,"申":8,"酉":9,"戌":10,"亥":11}
    
    # ── 维度累计器 ──
    dim_scores = {"事业": 5.0, "财运": 5.0, "健康": 5.0, "婚姻": 5.0, "人际": 5.0}
    adj_log = {"事业": [], "财运": [], "健康": [], "婚姻": [], "人际": []}
    
    # ① 十二宫星曜评分（含庙旺利陷）
    for gong in gongs:
        gong_name = gong.get("宫位", "")
        dizhi_str = gong.get("地支", "子")
        zhi_idx = dizhi_map.get(dizhi_str, 0)
        
        gw_map = {
            "命宫": 1.5, "财帛宫": 1.5, "官禄宫": 1.5,
            "夫妻宫": 1.5, "疾厄宫": 1.3,
            "迁移宫": 1.0, "交友宫": 1.0, "田宅宫": 1.0,
            "福德宫": 1.0, "父母宫": 0.8, "兄弟宫": 0.8, "子女宫": 0.8,
        }
        gw = gw_map.get(gong_name, 1.0)
        
        for star_type in ["主星", "辅星", "杂星"]:
            stars = gong.get(star_type, [])
            for s in stars:
                clean = s.split("(")[0].strip()
                base = ZHU_XING_BASE.get(clean, 5)
                dim = STAR_TO_DIM.get(clean, "事业")
                # 庙旺系数
                mf = _get_star_miaoxian_coeff(clean, zhi_idx) if star_type == "主星" else 1.0
                star_w = 1.0 if star_type == "主星" else (0.7 if star_type == "辅星" else 0.4)
                delta = (base - 5) * gw * star_w * mf
                dim_scores[dim] += delta
                if abs(delta) > 0.1:
                    adj_log[dim].append((f"star:{clean}({dizhi_str})", round(delta, 2)))
    
    # ② 格局校准（仅v3）
    if v3_mode:
        geju_list = result.get("格局列表", [])
        geju_dim_map = {
            "君臣庆会": {"事业": 1.5, "人际": 1.0},
            "日月并明": {"事业": 1.0, "人际": 0.8},
            "紫府朝垣": {"事业": 1.2},
            "巨日同宫": {"事业": 1.0, "人际": 0.5},
            "武曲金格": {"财运": 1.5},
            "武曲守财": {"财运": 1.2},
            "廉贞杀格": {"事业": 1.0},
            "贪狼桃花": {"婚姻": -0.5, "人际": -0.5},
            "文星拱命": {"事业": 1.0},
            "日月反背": {"事业": -0.5},
            "杀破狼": {"事业": 1.0, "健康": -0.3},
            "煞星会照": {"健康": -0.5, "事业": -0.3},
            "空劫夹命": {"财运": -0.5},
            "火铃冲照": {"健康": -0.8},
            "刑囚夹印": {"事业": -0.5},
            "府相朝垣": {"事业": 0.8, "财运": 0.8},
            "月朗天门": {"婚姻": 1.0, "健康": 0.5},
            "机月同梁": {"事业": 0.5, "人际": 0.3},
        }
        for g in geju_list:
            g_name = g.get("名称", "")
            if g_name in geju_dim_map:
                for dim, val in geju_dim_map[g_name].items():
                    dim_scores[dim] += val
                    adj_log[dim].append((f"geju:{g_name}", val))
    
    # ③ 四化演绎（仅v3有）
    if v3_mode:
        sihua_evol = result.get("四化演绎", {})
        for hua_type, paths in sihua_evol.items():
            hua_dim = SIHUA_DIM.get(hua_type, "事业")
            if hua_type == "忌":
                dim_scores[hua_dim] -= 0.8 * len(paths) if isinstance(paths, list) else 0.8
                adj_log[hua_dim].append((f"sihua:{hua_type}({len(paths) if isinstance(paths, list) else 1}条)", -0.8))
            elif hua_type == "禄":
                dim_scores[hua_dim] += 0.8 * len(paths) if isinstance(paths, list) else 0.8
                adj_log[hua_dim].append((f"sihua:{hua_type}", 0.8))
            elif hua_type == "权":
                dim_scores["事业"] += 0.6
                adj_log["事业"].append(("sihua:权", 0.6))
            elif hua_type == "科":
                dim_scores["事业"] += 0.4
                adj_log["事业"].append(("sihua:科", 0.4))
    
    # ④ 星曜强度（仅v3）
    if v3_mode:
        strength = result.get("星曜强度", {})
        for star, s in strength.items():
            if isinstance(s, (int, float)):
                dim = STAR_TO_DIM.get(star, "事业")
                if s < 3:  # 弱星
                    dim_scores[dim] -= 0.3
                    adj_log[dim].append((f"weak:{star}({s})", -0.3))
                elif s > 7:  # 强星
                    dim_scores[dim] += 0.3
                    adj_log[dim].append((f"strong:{star}({s})", 0.3))
    
    # 归一化到 1-10（收敛映射，防止v3格局导致暴分）
    # 映射函数：5.0+(raw-5)*0.35，raw约11→7.1，raw约16→8.9，raw约20→10.25→收敛10
    dim_results = {}
    for dim in ["事业", "财运", "健康", "婚姻", "人际"]:
        raw = dim_scores[dim]
        # 以5.0为中心，超过5的部分以35%速率映射到10
        if raw <= 5:
            mapped = max(1, raw * 1.0)
        else:
            mapped = min(10, 5.0 + (raw - 5.0) * 0.35 + (raw - 5.0) * 0.02 * (1 if dim in ["事业","财运"] else 0))
        score = max(1, min(10, round(mapped, 1)))
        level = "高" if score >= 7 else ("中" if score >= 4 else "低")
        dim_results[dim] = {"score": score, "level": level, "raw": round(raw, 2), "adj": adj_log.get(dim, [])}
    
    ming_gong = result.get("命盘结构", {}).get("命宫", "?")
    sihua = result.get("四化", {})
    sihua_str = ", ".join(f"{s}({h})" for h, s in sihua.items()) if sihua else "无"
    
    # 格局字符串
    geju_str = ""
    if v3_mode:
        geju_names = [g.get("名称", "") for g in result.get("格局列表", [])[:5]]
        geju_str = ", ".join(geju_names) if geju_names else "无特殊格局"
    
    return {
        "available": True,
        "ming_gong": ming_gong,
        "sihua": sihua_str,
        "geju": geju_str,
        "dimensions": dim_results,
        "v3_mode": v3_mode,
        "trend": {
            "trend_text": f"紫微命宫{ming_gong}，四化{sihua_str}",
        },
    }


# ============================================================
# 奇门维度分析
# ============================================================

QIMEN_PATH = os.path.expanduser("~/.agents/skills/qimen-dunjia/scripts")
if QIMEN_PATH not in sys.path:
    sys.path.insert(0, QIMEN_PATH)

try:
    from qimen_calc import full_qimen_calculation
    QIMEN_OK = True
except ImportError:
    QIMEN_OK = False

# 八门吉凶属性
MEN_JIXIONG = {
    "休门": {"score": 8, "dim": "婚姻", "note": "休养生息，婚姻吉"},
    "生门": {"score": 9, "dim": "财运", "note": "生长之门，财运大吉"},
    "伤门": {"score": 3, "dim": "事业", "note": "伤害之门，事业受阻"},
    "杜门": {"score": 4, "dim": "事业", "note": "杜塞不通，需避让"},
    "景门": {"score": 6, "dim": "人际", "note": "文书口舌，中性偏阳"},
    "死门": {"score": 2, "dim": "健康", "note": "大凶之门，健康损"},
    "惊门": {"score": 3, "dim": "人际", "note": "惊恐之门，人际失和"},
    "开门": {"score": 9, "dim": "事业", "note": "开启之门，事业通顺"},
}

# 九星吉凶
XING_JIXIONG = {
    "天心": {"score": 8, "dim": "健康", "note": "医星，健康福"},
    "天蓬": {"score": 4, "dim": "财运", "note": "盗星，财损"},
    "天芮": {"score": 3, "dim": "健康", "note": "病星，健康损"},
    "天冲": {"score": 6, "dim": "事业", "note": "冲劲星，有行动力"},
    "天辅": {"score": 8, "dim": "人际", "note": "文星，贵人助"},
    "天禽": {"score": 7, "dim": "健康", "note": "中正之星，平稳"},
    "天英": {"score": 5, "dim": "人际", "note": "火爆之星，口舌"},
    "天柱": {"score": 4, "dim": "事业", "note": "破坏之星，不吉"},
    "天任": {"score": 7, "dim": "财运", "note": "包容之星，稳妥"},
}

# 八神吉凶
SHEN_JIXIONG = {
    "值符": {"score": 9, "dim": "事业", "note": "最吉之神，领袖格局"},
    "腾蛇": {"score": 4, "dim": "人际", "note": "虚诈之神，口舌"},
    "太阴": {"score": 7, "dim": "事业", "note": "荫护之神，暗中得助"},
    "六合": {"score": 8, "dim": "婚姻", "note": "和合之神，婚姻吉"},
    "白虎": {"score": 2, "dim": "健康", "note": "凶煞之神，血光"},
    "玄武": {"score": 3, "dim": "财运", "note": "偷盗之神，财损"},
    "九地": {"score": 6, "dim": "事业", "note": "稳厚之神，持久力"},
    "九天": {"score": 7, "dim": "事业", "note": "高远之神，发展前景大"},
}


def analyze_qimen_dimension(year: int, month: int, day: int,
                              hour: int = 8, minute: int = 0) -> Dict:
    """
    奇门遁甲五维评分分析
    
    方法：从奇门排盘中提取八门/九星/八神/地支等信息，
    按属性评分后归入五维。
    """
    if not QIMEN_OK:
        return {"available": False, "error": "奇门引擎未加载"}
    
    try:
        result = full_qimen_calculation(year, month, day, hour, minute)
    except Exception as e:
        return {"available": False, "error": str(e)}
    
    dim_scores = {"事业": 0, "财运": 0, "健康": 0, "婚姻": 0, "人际": 0}
    dim_weights = {"事业": 0, "财运": 0, "健康": 0, "婚姻": 0, "人际": 0}
    
    # 1. 八门评分
    men_pan = result.get("ren_pan", {})
    for gong_num, men_data in men_pan.items():
        try:
            _ = int(gong_num)
        except (ValueError, TypeError):
            continue
        if isinstance(men_data, dict):
            men_name = men_data.get("men", "")
            men_info = MEN_JIXIONG.get(men_name)
            if men_info:
                dim = men_info["dim"]
                dim_scores[dim] += men_info["score"]
                dim_weights[dim] += 2.0  # 八门权重高
    
    # 2. 九星评分
    star_pan = result.get("tian_pan", {}).get("star", {})
    for gong_num, star_data in star_pan.items():
        if isinstance(star_data, dict):
            star_name = star_data.get("star", "")
            xing_info = XING_JIXIONG.get(star_name)
            if xing_info:
                dim = xing_info["dim"]
                dim_scores[dim] += xing_info["score"]
                dim_weights[dim] += 1.5
    
    # 3. 八神评分
    shen_pan = result.get("shen_pan", {})
    for gong_num, shen_data in shen_pan.items():
        if isinstance(shen_data, str):
            shen_info = SHEN_JIXIONG.get(shen_data)
            if shen_info:
                dim = shen_info["dim"]
                dim_scores[dim] += shen_info["score"]
                dim_weights[dim] += 1.0
    
    # 4. 旺衰分析
    wang_shuai = result.get("wang_shuai", {})
    for gong, ws in wang_shuai.items():
        if isinstance(ws, dict) and isinstance(gong, int):
            level = ws.get("level", 5)
            if level < 3:
                # 衰则各维扣分
                for d in dim_scores:
                    dim_scores[d] -= 1
            elif level > 7:
                for d in dim_scores:
                    dim_scores[d] += 1
    
    # 归一化到0-10分（校准版 v3 — 针对奇门低估）
    # 奇门原始值：事业5-15、财运2-10、健康2-8、婚姻1-6、人际2-8
    # 权重确保事业/财运维度有足够提升
    for dim in ["健康", "婚姻", "人际"]:
        if dim_weights.get(dim, 0) < 1:
            dim_weights[dim] = 1.0
    # 保证事业/财运权重至少2.0
    if dim_weights.get("事业", 0) < 2.0:
        dim_weights["事业"] = 2.0
    if dim_weights.get("财运", 0) < 2.0:
        dim_weights["财运"] = 2.0
    
    dim_results = {}
    for dim in ["事业", "财运", "健康", "婚姻", "人际"]:
        w = max(dim_weights.get(dim, 1), 0.1)
        raw = dim_scores.get(dim, 0)
        avg = raw / w
        # 修正映射（更激进的上拉）
        if avg <= 1:
            score = 2.5
        elif avg < 3:
            score = 2.5 + avg * 0.83  # 1-3 → 3.3-5
        elif avg < 7:
            score = 5.0 + (avg - 3) * 0.75  # 3-7 → 5-8
        elif avg < 12:
            score = 8.0 + (avg - 7) * 0.4  # 7-12 → 8-10
        else:
            score = 10.0
        score = max(1, min(10, round(score, 1)))
        dim_results[dim] = {"score": score, "level": "高" if score >= 7 else ("中" if score >= 4 else "低")}
    
    # 综合判断
    gan_zhi = result.get("gan_zhi", {})
    ju_info = result.get("ju_info", {})
    yang_dun = ju_info.get("yang_dun", True)
    ju_num = ju_info.get("ju_num", 1)
    method = f"{'阳' if yang_dun else '阴'}遁{ju_num}局"
    
    # 构建干支字符串
    day_gan = gan_zhi.get('day', ['', ''])[0] if isinstance(gan_zhi.get('day'), (list,tuple)) else ''
    day_zhi = gan_zhi.get('day', ['', ''])[1] if isinstance(gan_zhi.get('day'), (list,tuple)) else ''
    hour_gan_zhi = gan_zhi.get('hour_str', '')
    gan_zhi_str = f"{day_gan}{day_zhi} {hour_gan_zhi}" if day_gan else day_gan_zhi
    
    return {
        "available": True,
        "method": method,
        "gan_zhi": gan_zhi_str,
        "dimensions": dim_results,
        "trend": {
            "trend_text": f"奇门{method}，时空能量分析完成",
        },
    }


# ============================================================
# 导出接口
# ============================================================

def get_ziwei_scores(year: int, month: int, day: int, 
                       hour: int = 12, gender: str = "男") -> Dict:
    """简化的紫微评分，供三方交叉验证调用"""
    result = analyze_ziwei_dimension(year, month, day, hour, gender)
    if not result.get("available"):
        return result
    return {
        "available": True,
        "ming_gong": result.get("ming_gong", "?"),
        "sihua": result.get("sihua", ""),
        "dimensions": {k: v["score"] for k, v in result["dimensions"].items()},
        "dim_detail": result["dimensions"],
        "trend": result["trend"],
    }


def get_qimen_scores(year: int, month: int, day: int,
                      hour: int = 8, minute: int = 0) -> Dict:
    """简化的奇门评分，供三方交叉验证调用"""
    result = analyze_qimen_dimension(year, month, day, hour, minute)
    if not result.get("available"):
        return result
    return {
        "available": True,
        "method": result.get("method", "?"),
        "gan_zhi": result.get("gan_zhi", ""),
        "dimensions": {k: v["score"] for k, v in result["dimensions"].items()},
        "dim_detail": result["dimensions"],
        "trend": result["trend"],
    }


if __name__ == "__main__":
    import json
    
    print("═══ 紫微维度测试：丘总 ═══")
    print(json.dumps(get_ziwei_scores(1990, 11, 10, 10, "男"), 
                     ensure_ascii=False, indent=2))
    print()
    print("═══ 奇门维度测试：2026-05-04 ═══")
    print(json.dumps(get_qimen_scores(2026, 5, 4, 8, 0), 
                     ensure_ascii=False, indent=2))
