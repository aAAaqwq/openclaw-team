#!/usr/bin/env python3
"""
河图 · 六合交叉验证引擎 v1.2（高阶版）
══════════════════════════════════════════════════

从 v1.1 升级（2026-05-04）：

  ✅ 权重可配置 —— 支持外部传入 SYSTEM_WEIGHTS 覆盖
  ✅ 细粒度一致性算法 —— 基于标准差 + 收敛度 + 离群检测
  ✅ 小六壬 v2.1 适配 —— 读取 trend/rijian_summary/huo_shen
  ✅ 校准偏移可配置 —— 支持外部传入 CALIBRATION_OFFSETS
  ✅ 体系可用性自动检测 —— 失败时优雅降级

方法论：
  多个独立体系对一个问题的分析应该趋同。
  四个以上一致 → 极高概率
  三个一致一个相悖 → 深度分析相悖原因
  半数以下一致 → 信息不足或命局本身矛盾

评估维度（每个 0-10 分）：
  事业 / 财运 / 健康 / 婚姻 / 人际

最终输出：
  - 收敛度（0-100%） 
  - 综合评分（0-10）
  - 高概率事件（多数体系指向）
  - 需警惕事件（至少两个体系交叉确认）
  - 相悖体系（识别离群体系）
  - 不确定性区域
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
import sys, os, json
from datetime import datetime
import math

_DEEP_DIR = os.path.dirname(os.path.abspath(__file__))
if _DEEP_DIR not in sys.path:
    sys.path.insert(0, _DEEP_DIR)

# ── 体系引擎导入 ──

# 八字
try:
    sys.path.insert(0, os.path.expanduser("~/.agents/skills/bazi-mingli/scripts"))
    from bazi_calc_v2 import paipan_v2
    BAZI_AVAILABLE = True
except ImportError:
    BAZI_AVAILABLE = False

# 紫微
try:
    sys.path.insert(0, os.path.expanduser("~/.agents/skills/ziwei-doushu/scripts"))
    from ziwei_v2 import paipan as _ziwei_paipan
    ZIWEI_AVAILABLE = True
except ImportError:
    ZIWEI_AVAILABLE = False

# 奇门
try:
    sys.path.insert(0, os.path.expanduser("~/.agents/skills/qimen-dunjia/scripts"))
    from qimen_calc import full_qimen_calculation as _qimen_calc
    QIMEN_AVAILABLE = True
except ImportError:
    QIMEN_AVAILABLE = False

# 六爻
try:
    from liuyao_scores import score_liuyao_dimensions as _liuyao_scores
    LIUYAO_AVAILABLE = True
except ImportError:
    LIUYAO_AVAILABLE = False

# 大六壬 v3.0（完整打通版）
try:
    from daliuren_v3 import score_daliuren_v3 as _daliuren_scores
    DALIUREN_AVAILABLE = True
except ImportError:
    DALIUREN_AVAILABLE = False

# 小六壬
try:
    from xiaoliu_scores import score_dimensions as _xiaoliu_scores
    XIAOLIU_AVAILABLE = True
except ImportError:
    XIAOLIU_AVAILABLE = False

# 数字能量
NUMEROLOGY_AVAILABLE = True
try:
    from numerology_scores import get_all_scores as _numerology_scores
    NUMEROLOGY_AVAILABLE = True
except ImportError:
    NUMEROLOGY_AVAILABLE = False

# 星座
ZODIAC_AVAILABLE = True
try:
    from zodiac_scores import get_all_scores as _zodiac_scores
    ZODIAC_AVAILABLE = True
except ImportError:
    ZODIAC_AVAILABLE = False


# ════════════════════════════════════════
# 默认权重表（外部可通过 weight_overrides 覆盖）
# ════════════════════════════════════════

DEFAULT_SYSTEM_WEIGHTS = {
    "八字": {"事业": 0.35, "财运": 0.35, "健康": 0.30, "婚姻": 0.30, "人际": 0.25},
    "紫微": {"事业": 0.25, "财运": 0.25, "健康": 0.20, "婚姻": 0.20, "人际": 0.25},
    "奇门": {"事业": 0.20, "财运": 0.20, "健康": 0.25, "婚姻": 0.20, "人际": 0.25},
    "六爻": {"事业": 0.08, "财运": 0.08, "健康": 0.10, "婚姻": 0.10, "人际": 0.10},
    "大六壬": {"事业": 0.07, "财运": 0.07, "健康": 0.08, "婚姻": 0.10, "人际": 0.08},
    "小六壬": {"事业": 0.05, "财运": 0.05, "健康": 0.07, "婚姻": 0.10, "人际": 0.07},
}

# 默认校准偏移（外部可通过 cal_overrides 覆盖）
# 校准偏移（v2评分引擎校准）
# 注意：v2评分引擎已含格局/调候/神煞校准，分数区间接近真实分布
# 此处保留微小偏移仅做经验修正
DEFAULT_CALIBRATION_OFFSETS = {
    "八字": {"事业": 0.0, "财运": 0.0, "健康": 0.0, "婚姻": 0.0, "人际": 0.0},
    "紫微": {"事业": 0.0, "财运": 0.0, "健康": 0.0, "婚姻": 0.0, "人际": 0.0},
    "奇门": {"事业": 0.0, "财运": 0.0, "健康": 0.0, "婚姻": 0.0, "人际": 0.0},
    "六爻": {"事业": 0.0, "财运": 0.0, "健康": 0.0, "婚姻": 0.0, "人际": 0.0},
    "大六壬": {"事业": 0.0, "财运": 0.0, "健康": 0.0, "婚姻": 0.0, "人际": 0.0},
    "小六壬": {"事业": 0.0, "财运": 0.0, "健康": 0.0, "婚姻": 0.0, "人际": 0.0},
}

# v2.0 新增：数字能量、星座体系权重
DEFAULT_SYSTEM_WEIGHTS.update({
    "数字能量": {"事业": 0.05, "财运": 0.05, "健康": 0.05, "婚姻": 0.05, "人际": 0.05},
    "星座": {"事业": 0.05, "财运": 0.05, "健康": 0.05, "婚姻": 0.05, "人际": 0.05},
})

DIMENSION_KEYS = ["事业", "财运", "健康", "婚姻", "人际"]

# 体系可用性自动检测
AVAILABILITY_MAP = {
    "八字": BAZI_AVAILABLE,
    "紫微": ZIWEI_AVAILABLE,
    "奇门": QIMEN_AVAILABLE,
    "六爻": LIUYAO_AVAILABLE,
    "大六壬": DALIUREN_AVAILABLE,
    "小六壬": XIAOLIU_AVAILABLE,
    "数字能量": NUMEROLOGY_AVAILABLE,
    "星座": ZODIAC_AVAILABLE,
}


# ════════════════════════════════════════
# 一致性算法（替换 v1.1 的简单极差）
# ════════════════════════════════════════

def calc_convergence(scores: List[float]) -> Dict[str, float]:
    """
    计算一组分数的收敛度
    
    Returns:
        {
            "mean": 均值,
            "std": 标准差,
            "max_dev": 最大偏差,
            "convergence": 收敛度 (0-100%),
            "outliers": [离群值列表],
            "n": 样本数,
        }
    """
    n = len(scores)
    if n == 0:
        return {"mean": 0, "std": 0, "max_dev": 0, "convergence": 0, "outliers": [], "n": 0}
    if n == 1:
        return {"mean": scores[0], "std": 0, "max_dev": 0, "convergence": 100, "outliers": [], "n": 1}

    mean = sum(scores) / n
    variance = sum((s - mean) ** 2 for s in scores) / n
    std = math.sqrt(variance)

    max_dev = max(abs(s - mean) for s in scores)

    # 收敛度：基于标准差相对于满分范围10的归一化
    # std=0 → 100%, std=3 → ~40%, std=5 → ~0%
    convergence = max(0, 100 - (std / 5) * 100)

    # 离群检测：超过 2 个标准差
    outlier_threshold = std * 2 if std > 0.3 else 2.0  # 最小阈值 2.0
    outliers = [s for s in scores if abs(s - mean) > outlier_threshold]

    return {
        "mean": round(mean, 2),
        "std": round(std, 2),
        "max_dev": round(max_dev, 1),
        "convergence": round(convergence, 1),
        "outliers": outliers,
        "n": n,
    }


def detect_outlier_system(scores_with_system: List[Tuple[str, float]],
                          mean: float, std: float) -> List[str]:
    """
    检测哪个体系是离群体系
    如果某个体系的分数偏离均值超过 2 个标准差（或至少 2.0 分），标记为离群
    """
    if len(scores_with_system) < 3:
        return []
    outliers = []
    threshold = max(std * 2, 2.0)
    for sys_name, s in scores_with_system:
        if abs(s - mean) > threshold:
            outliers.append(f"{sys_name}({s:.1f}分,偏差{abs(s-mean):.1f})")
    return outliers


# ════════════════════════════════════════
# 八字分析
# ════════════════════════════════════════

def _analyze_wuxing_balance(wuxing: Dict) -> Dict:
    try:
        if isinstance(wuxing, dict):
            values = {k: int(v) if str(v).isdigit() else 0 for k, v in wuxing.items() if k in "金木水火土"}
            total = sum(values.values()) or 1
            max_pct = max(values.values()) / total * 100 if total > 0 else 25
            min_pct = min(v for v in values.values() if v > 0) / total * 100 if total > 0 else 25
            return {
                "values": values,
                "balance": "均衡" if max_pct - min_pct < 20 else "偏枯" if max_pct > 50 else "略偏",
                "most": max(values, key=values.get),
                "least": min(values, key=values.get),
            }
    except: pass
    return {"balance": "未知", "values": {}}


def _bazi_trend_analysis(result: Dict) -> Dict:
    liunian = result.get("流年分析", {})
    dayun_list = result.get("大運排列", [])
    if dayun_list and len(dayun_list) > 0:
        first_dayun = dayun_list[0]
        if isinstance(first_dayun, dict):
            current_dayun = f"{first_dayun.get('天干','?')}{first_dayun.get('地支','?')}"
        else:
            current_dayun = str(first_dayun)[:2]
    else:
        current_dayun = "?"
    return {
        "current_dayun": current_dayun,
        "trend_text": "当前大运配合得当，" if result.get("日主分析",{}).get("總評分",50) > 40 else "当前大运略显压力，",
    }


def analyze_bazi(year: int, month: int, day: int, hour: int = 12,
                  gender: str = "男", day_zhi: str = None) -> Dict:
    """八字维度分析 v2（整合格局判定+评分v2）"""
    if not BAZI_AVAILABLE:
        return {"available": False, "error": "八字引擎未加载"}
    try:
        result = paipan_v2(year, month, day, hour, gender, 2026)
    except Exception as e:
        return {"available": False, "error": str(e)}

    pillars = result.get("四柱八字", {})
    rizhu = result.get("日主分析", {})
    yongshen = result.get("用神喜忌", {})
    bazi_str = f"{pillars.get('年柱',{}).get('干支','?')} {pillars.get('月柱',{}).get('干支','?')} {pillars.get('日柱',{}).get('干支','?')} {pillars.get('時柱',{}).get('干支','?')}"
    ri_zhu = rizhu.get("日主", "?") if isinstance(rizhu, dict) else "?"
    strength = rizhu.get("綜合判斷", "中和") if isinstance(rizhu, dict) else "?"
    score = rizhu.get("總評分", 50) if isinstance(rizhu, dict) else 50
    yong_shen = yongshen.get("喜用神", yongshen.get("用神", "?"))
    wuxing = result.get("五行統計", {})
    wuxing_balance = _analyze_wuxing_balance(wuxing)

    # ── v2: 使用 bazi_scores_v2 评分引擎（含格局）──
    dims = {}
    geju_name = ""
    try:
        from bazi_scores_v2 import score_bazi_dimensions_v2
        v2_result = score_bazi_dimensions_v2(result)
        dims = v2_result.get("dim_detail", {})
        geju_name = v2_result.get("geju", {}).get("primary_geju", "")
    except Exception:
        try:
            from bazi_scores_v2 import score_bazi_dimensions
            dims = score_bazi_dimensions(result)
        except Exception:
            pass
    
    # 统一 dims 格式为 {dim: {"score": float, "level": str}}
    normalized_dims = {}
    if not dims:
        for dim in DIMENSION_KEYS:
            s = min(10, score // 10 + 2) if dim == "事业" else 6
            normalized_dims[dim] = {"score": s, "level": "高" if s >= 7 else ("中" if s >= 4 else "低")}
    else:
        for dim in DIMENSION_KEYS:
            v = dims.get(dim)
            if isinstance(v, dict):
                s = v.get("score", v.get("raw", 5.0))
            elif isinstance(v, (int, float)):
                s = float(v)
            else:
                s = 5.0
            s = max(1, min(10, round(s, 1)))
            normalized_dims[dim] = {"score": s, "level": "高" if s >= 7 else ("中" if s >= 4 else "低")}
    dims = normalized_dims

    trend = _bazi_trend_analysis(result)

    # 提取日干日支（给小六壬日建用）
    ri_zhi_str = pillars.get("日柱", {}).get("地支", None)
    if ri_zhi_str == "?":
        ri_zhi_str = None

    return {
        "available": True,
        "bazi": bazi_str,
        "ri_zhu": ri_zhu,
        "ri_zhi": ri_zhi_str,
        "strength": strength,
        "score": score,
        "yong_shen": yong_shen,
        "wuxing": wuxing,
        "wuxing_balance": wuxing_balance,
        "geju": geju_name,
        "dimensions": dims,
        "trend": trend,
    }


# ════════════════════════════════════════
# 紫微分析
# ════════════════════════════════════════

def analyze_ziwei(year: int, month: int, day: int, hour: int = 12,
                   gender: str = "男") -> Dict:
    """紫微维度分析 v2（整合 v3 引擎 + 格局自动判定 + 庙旺利陷）"""
    try:
        # 使用最新的 analyze_ziwei_dimension（v2.0，v3引擎优先）
        from ziwei_qimen_scores import analyze_ziwei_dimension
        scores = analyze_ziwei_dimension(year, month, day, hour, gender)
        if scores.get("available"):
            return {
                "available": True,
                "result_summary": f"紫微命宫{scores.get('ming_gong','?')}，四化{scores.get('sihua','')}",
                "geju": scores.get("geju", ""),
                "dimensions": scores.get("dimensions", {}),
                "trend": scores.get("trend", {"trend_text": "紫微盘面分析完成"}),
            }
    except Exception as e:
        pass
    # fallback: 使用旧的 get_ziwei_scores
    try:
        from ziwei_qimen_scores import get_ziwei_scores
        scores = get_ziwei_scores(year, month, day, hour, gender)
        if scores.get("available"):
            return {
                "available": True,
                "result_summary": f"紫微命宫{scores.get('ming_gong','?')}，四化{scores.get('sihua','')}",
                "dimensions": scores.get("dim_detail", {}),
                "trend": scores.get("trend", {"trend_text": "紫微盘面分析完成"}),
            }
    except Exception: pass
    return {"available": False, "error": "紫微评分加载失败"}


# ════════════════════════════════════════
# 奇门分析
# ════════════════════════════════════════

def analyze_qimen(year: int, month: int, day: int, hour: int = 8) -> Dict:
    try:
        from ziwei_qimen_scores import get_qimen_scores
        scores = get_qimen_scores(year, month, day, hour, 0)
        if scores.get("available"):
            return {
                "available": True,
                "result_summary": f"奇门{scores.get('method','?')}，干支{scores.get('gan_zhi','')}",
                "dimensions": scores.get("dim_detail", {}),
                "trend": scores.get("trend", {"trend_text": "奇门时空分析完成"}),
            }
    except Exception: pass
    return {"available": False, "error": "奇门评分加载失败"}


# ════════════════════════════════════════
# 六爻分析
# ════════════════════════════════════════

def analyze_liuyao(year: int, month: int, day: int, hour: int = 12,
                    query_type: str = "general") -> Dict:
    if not LIUYAO_AVAILABLE:
        return {"available": False, "error": "六爻引擎未加载"}
    try:
        scores = _liuyao_scores(year, month, day, hour, query_type)
        if scores.get("available"):
            return {
                "available": True,
                "result_summary": scores.get("result_summary", f"六爻{scores.get('gua_ming','?')}卦"),
                "dimensions": scores.get("dimensions", {}),
                "trend": {"trend_text": scores.get("result_summary", "六爻分析完成")},
            }
    except Exception as e:
        return {"available": False, "error": str(e)}
    return {"available": False, "error": "六爻评分无返回"}


# ════════════════════════════════════════
# 大六壬分析
# ════════════════════════════════════════

def analyze_daliuren(year: int, month: int, day: int, hour: int = 12) -> Dict:
    """大六壬 v3.0 分析（完整打通版）"""
    if not DALIUREN_AVAILABLE:
        return {"available": False, "error": "大六壬引擎未加载"}
    try:
        scores = _daliuren_scores(year, month, day, hour)
        if scores.get("available"):
            dims = {}
            for d, info in scores.get("dimensions", {}).items():
                dims[d] = {"score": info["score"], "level": info["level"], "note": info["note"]}
            return {
                "available": True,
                "result_summary": f"课体{scores.get('ke_ti','')}，应期{scores.get('yingshen',{}).get('period','')}",
                "dimensions": dims,
                "trend": {
                    "trend_text": f"大六壬{scores.get('ke_ti','')}课，"
                                  f"五维均值{sum(info['score'] for info in dims.values())/len(dims):.1f}/10"
                },
                "ke_ti": scores.get("ke_ti", ""),
                "sanchuan": scores.get("sanchuan", {}),
                "yingshen": scores.get("yingshen", {}),
                "reading": scores.get("reading", {}),
            }
    except Exception as e:
        return {"available": False, "error": str(e)}
    return {"available": False, "error": "大六壬评分无返回"}


# ════════════════════════════════════════
# 小六壬分析（v2.1 适配）
# ════════════════════════════════════════

def analyze_xiaoliu(month: int = None, day: int = None, hour_24: Optional[int] = None,
                     day_zhi: str = None) -> Dict:
    if not XIAOLIU_AVAILABLE:
        return {"available": False, "error": "小六壬引擎未加载"}
    try:
        scores = _xiaoliu_scores(month=month, day=day, hour_24=hour_24, day_zhi=day_zhi)
        if scores.get("available"):
            extra = {}
            if "trend" in scores:
                extra["trend_text"] = f"小六壬{scores.get('divination',{}).get('gong_name','?')}宫，趋势{scores.get('trend','横盘')}"
            else:
                extra["trend_text"] = f"小六壬{scores.get('divination',{}).get('gong_name','?')}宫"
            return {
                "available": True,
                "result_summary": scores.get("divination", {}).get("description", ""),
                "dimensions": scores.get("dimensions", {}),
                "trend": extra,
            }
    except Exception as e:
        return {"available": False, "error": str(e)}
    return {"available": False, "error": "小六壬评分无返回"}


# ════════════════════════════════════════
# 数字能量分析
# ════════════════════════════════════════

def analyze_numerology(full_name: str = '', year: int = 1990, month: int = 1, day: int = 1) -> Dict:
    """分析数字能量"""
    if not NUMEROLOGY_AVAILABLE:
        return {"available": False, "error": "数字能量引擎未加载"}
    try:
        scores, details = _numerology_scores(full_name=full_name, year=year, month=month, day=day)
        dims = {}
        for d in DIMENSION_KEYS:
            if d in scores:
                dims[d] = {"score": scores[d], "source": "numerology_v2.0", "raw_value": scores[d]}
        return {
            "available": True,
            "result_summary": f"数字能量 LifePath={details.get('life_path_info',{}).get('value','?')}, 五行={details.get('life_path_info',{}).get('wu_xing','?')}",
            "dimensions": dims,
            "trend": {"trend_text": f"数字能量{details.get('life_path_info',{}).get('persona','?')}·{details.get('life_path_info',{}).get('wu_xing','?')}"}
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ════════════════════════════════════════
# 星座分析
# ════════════════════════════════════════

def analyze_zodiac(year: int = 1990, month: int = 1, day: int = 1,
                    hour: int = 12, minute: int = 0,
                    lng: float = 116.4, lat: float = 39.9,
                    tz_str: str = 'Asia/Shanghai') -> Dict:
    """分析星座"""
    if not ZODIAC_AVAILABLE:
        return {"available": False, "error": "星座引擎未加载"}
    try:
        scores, details = _zodiac_scores(year=year, month=month, day=day,
                                           hour=hour, minute=minute,
                                           lng=lng, lat=lat, tz_str=tz_str)
        dims = {}
        for d in DIMENSION_KEYS:
            if d in scores:
                dims[d] = {"score": scores[d], "source": "zodiac_v2.0", "raw_value": scores[d]}
        raw = details.get('raw_data', {})
        # 提取行星基础信息
        planets = details.get('planets', [])[:3]
        trend_text = f"星座 太阳{raw.get('sun_sign','?')} 月亮{raw.get('moon_sign','?')} 上升{raw.get('ascendant_sign','?')}"
        aspects_count = len(details.get('aspects', []))
        return {
            "available": True,
            "result_summary": trend_text,
            "dimensions": dims,
            "trend": {"trend_text": trend_text, "aspects": aspects_count}
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ════════════════════════════════════════
# 校准偏移应用
# ════════════════════════════════════════

def apply_calibration(system_dim_scores: dict,
                       cal_overrides: Optional[Dict] = None) -> dict:
    """应用校准偏移到原始评分"""
    offsets = DEFAULT_CALIBRATION_OFFSETS.copy()
    if cal_overrides:
        for sys_name, dim_offs in cal_overrides.items():
            if sys_name in offsets:
                offsets[sys_name].update(dim_offs)
            else:
                offsets[sys_name] = dim_offs

    calibrated = {}
    for sys_name, dim_scores in system_dim_scores.items():
        cal = {}
        sys_offs = offsets.get(sys_name, {})
        for dim, raw_val in dim_scores.items():
            if isinstance(raw_val, (int, float)):
                offset = sys_offs.get(dim, 0)
                cal[dim] = max(1, min(10, round(raw_val + offset, 1)))
            else:
                cal[dim] = raw_val
        calibrated[sys_name] = cal
    return calibrated


# ════════════════════════════════════════
# 主交叉验证函数
# ════════════════════════════════════════

def cross_validate(person_name: str, year: int, month: int, day: int,
                    hour: int = 12, gender: str = "男",
                    query_type: str = "general",
                    weight_overrides: Optional[Dict] = None,
                    cal_overrides: Optional[Dict] = None,
                    verbose: bool = False) -> Dict:
    """
    六合交叉验证 v1.2（高阶版）

    Args:
        person_name: 对象名称
        year/month/day/hour: 出生时间
        gender: 性别
        query_type: 问题类型
        weight_overrides: 权重覆盖 {系统: {维度: 权重}}
        cal_overrides: 校准偏移覆盖 {系统: {维度: 偏移值}}
        verbose: 是否输出调试信息

    Returns:
        完整交叉验证结果
    """
    # 1. 运行所有体系
    bazi_res = analyze_bazi(year, month, day, hour, gender)
    ziwei_res = analyze_ziwei(year, month, day, hour, gender)
    qimen_res = analyze_qimen(year, month, day, 8)
    liuyao_res = analyze_liuyao(year, month, day, hour, query_type)
    daliuren_res = analyze_daliuren(year, month, day, hour)

    # 小六壬：从八字获取日支
    ri_zhi = bazi_res.get("ri_zhi", None) if bazi_res.get("available") else None
    xiaoliu_res = analyze_xiaoliu(month=month, day=day, hour_24=hour, day_zhi=ri_zhi)
    
    # 数字能量 & 星座（v2.0 新增）
    numerology_res = analyze_numerology(full_name=person_name, year=year, month=month, day=day)
    zodiac_res = analyze_zodiac(year=year, month=month, day=day, hour=hour)

    available_systems = {
        "八字": bazi_res.get("available", False),
        "紫微": ziwei_res.get("available", False),
        "奇门": qimen_res.get("available", False),
        "六爻": liuyao_res.get("available", False),
        "大六壬": daliuren_res.get("available", False),
        "小六壬": xiaoliu_res.get("available", False),
        "数字能量": numerology_res.get("available", False),
        "星座": zodiac_res.get("available", False),
    }

    sys_list = [
        ("八字", bazi_res),
        ("紫微", ziwei_res),
        ("奇门", qimen_res),
        ("六爻", liuyao_res),
        ("大六壬", daliuren_res),
        ("小六壬", xiaoliu_res),
        ("数字能量", numerology_res),
        ("星座", zodiac_res),
    ]

    # 2. 收集原始评分
    raw_scores = {}
    for sys_name, sys_res in sys_list:
        if sys_res.get("available") and "dimensions" in sys_res:
            dims = {}
            for d in DIMENSION_KEYS:
                if d in sys_res["dimensions"]:
                    dims[d] = sys_res["dimensions"][d].get("score", 5.0)
            if dims:
                raw_scores[sys_name] = dims

    # 3. 应用校准
    cal_scores = apply_calibration(raw_scores, cal_overrides)

    # 4. 权重表
    weights = DEFAULT_SYSTEM_WEIGHTS.copy()
    if weight_overrides:
        for sys_name, dim_ws in weight_overrides.items():
            if sys_name in weights:
                weights[sys_name].update(dim_ws)
            else:
                weights[sys_name] = dim_ws

    # 5. 每个维度的细粒度交叉评分
    dim_results = {}
    for dim in DIMENSION_KEYS:
        scores_with_system = []
        for sys_name in raw_scores:
            if dim in cal_scores.get(sys_name, {}):
                scores_with_system.append((sys_name, cal_scores[sys_name][dim]))

        # 收敛度分析
        if len(scores_with_system) >= 2:
            sv = [s[1] for s in scores_with_system]
            conv_info = calc_convergence(sv)
            outlier_systems = detect_outlier_system(scores_with_system,
                                                     conv_info["mean"],
                                                     conv_info["std"])
        elif len(scores_with_system) == 1:
            conv_info = calc_convergence([s[1] for s in scores_with_system])
            outlier_systems = []
        else:
            conv_info = {"mean": 5.0, "std": 0, "max_dev": 0,
                         "convergence": 0, "outliers": [], "n": 0}
            outlier_systems = []

        # 综合评分（加权平均）
        if scores_with_system:
            wsum = 0
            wtotal = 0
            for sys_name, s_val in scores_with_system:
                w = weights.get(sys_name, {}).get(dim, 0.1)
                wsum += s_val * w
                wtotal += w
            composite = round(wsum / wtotal, 1) if wtotal > 0 else 5.0
        else:
            composite = 5.0

        dim_results[dim] = {
            "综合评分": composite,
            "等级": "高" if composite >= 7 else ("中" if composite >= 4 else "低"),
            "收敛度": f"{conv_info['convergence']:.0f}%",
            "标准差": conv_info["std"],
            "最大偏差": conv_info["max_dev"],
            "离群体系": outlier_systems,
            "参与体系数": len(scores_with_system),
            "参与体系": [s[0] for s in scores_with_system],
            "各体系原始分": {s[0]: s[1] for s in scores_with_system},
        }

    # 6. 整体收敛度
    all_conv = [float(dim_results[d]["收敛度"].replace("%", ""))
                for d in DIMENSION_KEYS if dim_results[d]["参与体系数"] >= 2]
    overall_convergence = sum(all_conv) / len(all_conv) if all_conv else 0

    # 7. 趋势汇总
    trends = []
    for sys_name, sys_res in sys_list:
        if sys_res.get("available") and "trend" in sys_res:
            t = sys_res["trend"].get("trend_text", "")
            if t:
                trends.append(f"{sys_name}: {t}")
    trend_text = "；".join(trends) if trends else "数据不足"

    # 8. 高概率 & 需警惕 & 相悖检测
    high_prob_events = []
    caution_events = []
    all_outlier_systems = set()

    for dim, data in dim_results.items():
        comp = data["综合评分"]
        conv_pct = float(data["收敛度"].replace("%", ""))
        n_sys = data["参与体系数"]

        for outlier in data.get("离群体系", []):
            all_outlier_systems.add(outlier)

        # 高概率：高评分 + 高收敛度 + 多体系
        if comp >= 7 and n_sys >= 4 and conv_pct >= 80:
            high_prob_events.append(
                f"{dim}方面运势良好，{n_sys}体系高度收敛（评分{comp}/收敛度{data['收敛度']}）")
        elif comp >= 7 and conv_pct >= 60:
            high_prob_events.append(
                f"{dim}方面偏好（评分{comp}，收敛度{data['收敛度']}）")

        # 需关注：低评分
        if comp < 4:
            caution_events.append(
                f"{dim}方面需关注（评分{comp}，收敛度{data['收敛度']}）")
        elif comp < 4.5 and conv_pct < 50:
            caution_events.append(
                f"{dim}方面略低且有分歧（评分{comp}，收敛度{data['收敛度']}，离群={data['离群体系']}）")

    # 9. 评分一致性校验（八字 vs 紫微 同维度差异 >2.0 标记）
    consistency_warnings = []
    bazi_dims = raw_scores.get("八字", {})
    ziwei_dims = raw_scores.get("紫微", {})
    if bazi_dims and ziwei_dims:
        for dim in DIMENSION_KEYS:
            bd = bazi_dims.get(dim)
            zd = ziwei_dims.get(dim)
            if bd is not None and zd is not None:
                diff = abs(bd - zd)
                if diff > 2.0:
                    consistency_warnings.append(f"{dim}：八字{bd} vs 紫微{zd}（差异{diff:.1f}，需人工复核）")
    
    # 10. 综合评分
    overall_score = round(
        sum(dim_results[d]["综合评分"] for d in DIMENSION_KEYS) / len(DIMENSION_KEYS), 1)

    return {
        "cross_validate_schema": "v1.2",
        "name": person_name,
        "bazi": bazi_res.get("bazi", "?"),
        "ri_zhu": bazi_res.get("ri_zhu", "?"),
        "strength": bazi_res.get("strength", "?"),
        "yong_shen": bazi_res.get("yong_shen", "?"),
        "available_systems": available_systems,
        "systems_trend": trend_text,
        "dimensions": dim_results,
        "overall_convergence": f"{overall_convergence:.0f}%",
        "overall_score": overall_score,
        "high_probability": high_prob_events,
        "caution_events": caution_events,
        "outlier_systems": list(all_outlier_systems) if all_outlier_systems else [],
        "consistency_warnings": consistency_warnings,
    }


def get_available_systems() -> Dict[str, bool]:
    """获取所有体系的可用性状态"""
    return dict(AVAILABILITY_MAP)


def cross_validate_report(person_name: str, year: int, month: int, day: int,
                           hour: int = 12, gender: str = "男",
                           query_type: str = "general",
                           weight_overrides: Optional[Dict] = None,
                           cal_overrides: Optional[Dict] = None) -> str:
    """
    六合交叉验证完整报告（v1.2）
    """
    result = cross_validate(person_name, year, month, day, hour, gender,
                             query_type, weight_overrides, cal_overrides)

    n_available = sum(1 for v in result["available_systems"].values() if v)
    sys_names = [k for k, v in result["available_systems"].items() if v]

    lines = [
        "═══ 河图六合交叉验证报告 v1.2 ═══",
        f"对象: {person_name}",
        f"出生: {year}年{month}月{day}日{hour:02d}时 ({gender})",
        f"查询类型: {query_type}",
        "",
    ]

    if result.get("bazi"):
        lines.append(f"八字: {result['bazi']}")
        lines.append(f"日主: {result['ri_zhu']} | 强弱: {result['strength']} | 用神: {result['yong_shen']}")
    lines.append("")
    lines.append(f"可用体系: {'、'.join(sys_names)}（{n_available}/6）")
    if result.get("systems_trend"):
        lines.append(f"趋势汇总: {result['systems_trend']}")
    lines.append("")

    # 维度对比表
    lines.append("【五维对比】")
    for dim, data in result["dimensions"].items():
        parts = []
        parts.append(f"{dim:<4} {data['综合评分']:>4}/10")
        parts.append(f"收敛度{data['收敛度']:>5}")
        parts.append(f"({data['等级']})")
        parts.append(f"[{data['参与体系数']}体系]")
        if data.get("离群体系"):
            parts.append(f"⚠离群:{','.join(data['离群体系'])}")
        lines.append("  " + " ".join(parts))
    lines.append("")

    # 整体统计
    lines.append(f"【综合得分】{result['overall_score']}/10 · 整体收敛度 {result['overall_convergence']}")
    if result.get("outlier_systems"):
        lines.append(f"【相悖体系】{', '.join(result['outlier_systems'])}")
    lines.append("")

    # 高概率
    if result.get("high_probability"):
        lines.append("✅ 高概率事件")
        for evt in result["high_probability"]:
            lines.append(f"  · {evt}")
        lines.append("")
    # 需关注
    if result.get("caution_events"):
        lines.append("⚠️ 需关注区域")
        for evt in result["caution_events"]:
            lines.append(f"  · {evt}")
        lines.append("")

    # 结论
    conv_pct_val = 0
    conv_str = str(result.get("overall_convergence", "0%"))
    if "%" in conv_str:
        conv_pct_val = int(conv_str.replace("%", ""))

    score = result.get("overall_score", 0)
    n_outliers = len(result.get("outlier_systems", []))

    if n_available >= 4 and conv_pct_val >= 80 and score >= 7 and n_outliers == 0:
        lines.append("【河图结论】多重印证，高度收敛，建议参考。")
    elif conv_pct_val >= 60 and n_available >= 3:
        lines.append("【河图结论】多体系趋势一致，方向较明确。")
    elif n_outliers > 0 and n_available >= 4:
        lines.append(f"【河图结论】存在离群体系({', '.join(result['outlier_systems'])})，建议深入排查分歧原因。")
    elif conv_pct_val >= 40:
        lines.append("【河图结论】存在分歧，建议择日重测或聚焦单一维度深入。")
    else:
        lines.append("【河图结论】数据量不足或命局本身矛盾，建议结合现实决策。")
    lines.append("")
    lines.append(f"【说明】{n_available}体系交叉验证，基于加权均值+标准差收敛度。权重可通过 weight_overrides 自定义。")

    return "\n".join(lines)


# ════════════════════════════════════════
# 兼容性入口（v1.1 接口保持可用）
# ════════════════════════════════════════

# 将 cross_validate 和 cross_validate_report 保持为顶层函数
# 外部调用 `from triple_cross import cross_validate, cross_validate_report` 仍然可用


if __name__ == "__main__":
    print("═══ 河图六合交叉验证引擎 v1.2 (高阶版) ═══\n")

    # 测试1：丘总
    print("【测试1：丘总 (1990-11-10 10时)】")
    r1 = cross_validate_report("丘总", 1990, 11, 10, 10, "男")
    print(r1)
    print()

    # 测试2：丘总伴侣
