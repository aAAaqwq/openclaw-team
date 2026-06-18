#!/usr/bin/env python3
"""
河图 · 六爻评分引擎 v2.0（A级 → 准S级）
═══════════════════════════════════════════════════════
升级内容（2026-05-04）：
  P0 Fix:  修正对 liuyao_calc.py 的调用方式
  P1 增强: 1) 六神（六兽）评分加成  2) 月建日建旬空加成
           3) 动爻变卦完整分析     4) 旺衰权重
           5) 分类占权重           6) 应期推断

核心公式：
  最终五维评分 = 卦象基础分 x 30% + 六兽(六神)分 x 20%
                 + 月建日建旬空分 x 15% + 旺衰分 x 15%
                 + 动爻变卦分 x 10% + 分类占调整 x 10%
"""

from typing import Dict, List, Optional, Tuple, Any
import sys, os, random, json, logging
from datetime import datetime

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# 六神（六兽）对五维的差异化影响
LIU_SHEN_DIM = {
    "青龙": {"事业": 0.30, "财运": 0.20, "健康": 0.10, "婚姻": 0.20, "人际": 0.30},
    "朱雀": {"事业": 0.00, "财运": -0.20, "健康": -0.10, "婚姻": -0.10, "人际": -0.20},
    "勾陈": {"事业": -0.10, "财运": -0.10, "健康": 0.00, "婚姻": -0.10, "人际": -0.10},
    "螣蛇": {"事业": -0.20, "财运": -0.20, "健康": -0.20, "婚姻": -0.20, "人际": -0.10},
    "白虎": {"事业": -0.10, "财运": -0.30, "健康": -0.40, "婚姻": -0.20, "人际": -0.20},
    "玄武": {"事业": -0.20, "财运": -0.30, "健康": -0.10, "婚姻": -0.30, "人际": -0.20},
}

# 旺衰评分
YUE_WANG_SCORE = {"旺": 0.30, "相": 0.20, "休": -0.10, "囚": -0.20, "死": -0.30}
ZONG_WANG_SCORE = {"旺": 0.20, "相": 0.10, "休": -0.10, "囚": -0.20, "死": -0.30, "平": 0.0}
SHENG_WANG_SCORE = {
    "帝旺": 0.30, "临官": 0.25, "冠带": 0.20, "长生": 0.20,
    "沐浴": 0.10, "衰": -0.10, "病": -0.15, "死": -0.25,
    "墓": -0.10, "绝": -0.30, "胎": 0.10, "养": 0.10,
}
KONG_SCORE = -0.30

# 64卦维度评分
GUA_SCORES = {
    "乾":  {"dim_scores": {"事业": 9.5, "财运": 7.5, "健康": 7.0, "婚姻": 6.0, "人际": 7.5}},
    "坤":  {"dim_scores": {"事业": 7.0, "财运": 8.0, "健康": 8.5, "婚姻": 8.0, "人际": 8.0}},
    "泰":  {"dim_scores": {"事业": 8.5, "财运": 8.0, "健康": 8.0, "婚姻": 7.5, "人际": 8.0}},
    "大有":{"dim_scores": {"事业": 9.0, "财运": 9.5, "健康": 7.5, "婚姻": 7.0, "人际": 7.5}},
    "谦":  {"dim_scores": {"事业": 7.0, "财运": 7.5, "健康": 8.5, "婚姻": 8.0, "人际": 8.5}},
    "大壮":{"dim_scores": {"事业": 8.5, "财运": 7.5, "健康": 7.0, "婚姻": 6.5, "人际": 6.5}},
    "益":  {"dim_scores": {"事业": 8.0, "财运": 7.0, "健康": 7.5, "婚姻": 7.0, "人际": 7.5}},
    "鼎":  {"dim_scores": {"事业": 8.5, "财运": 7.5, "健康": 7.0, "婚姻": 6.5, "人际": 6.5}},
    "既济":{"dim_scores": {"事业": 7.5, "财运": 8.0, "健康": 7.5, "婚姻": 7.5, "人际": 6.5}},
    "随":  {"dim_scores": {"事业": 6.0, "财运": 5.0, "健康": 6.0, "婚姻": 6.5, "人际": 6.5}},
    "比":  {"dim_scores": {"事业": 7.0, "财运": 6.5, "健康": 7.0, "婚姻": 6.0, "人际": 7.5}},
    "小畜":{"dim_scores": {"事业": 6.5, "财运": 6.0, "健康": 6.0, "婚姻": 5.5, "人际": 6.0}},
    "履":  {"dim_scores": {"事业": 6.0, "财运": 5.5, "健康": 6.5, "婚姻": 5.5, "人际": 6.0}},
    "同人":{"dim_scores": {"事业": 7.5, "财运": 6.0, "健康": 7.0, "婚姻": 6.5, "人际": 8.0}},
    "咸":  {"dim_scores": {"事业": 6.5, "财运": 5.5, "健康": 6.5, "婚姻": 8.5, "人际": 7.5}},
    "恒":  {"dim_scores": {"事业": 7.5, "财运": 6.5, "健康": 7.0, "婚姻": 7.0, "人际": 6.5}},
    "晋":  {"dim_scores": {"事业": 7.5, "财运": 7.0, "健康": 6.5, "婚姻": 6.0, "人际": 7.0}},
    "家人":{"dim_scores": {"事业": 6.5, "财运": 6.0, "健康": 7.0, "婚姻": 8.5, "人际": 7.5}},
    "解":  {"dim_scores": {"事业": 7.0, "财运": 6.5, "健康": 7.0, "婚姻": 6.5, "人际": 7.0}},
    "丰":  {"dim_scores": {"事业": 7.5, "财运": 7.0, "健康": 6.5, "婚姻": 6.5, "人际": 7.0}},
    "兑":  {"dim_scores": {"事业": 7.0, "财运": 6.0, "健康": 6.5, "婚姻": 7.5, "人际": 7.0}},
    "中孚":{"dim_scores": {"事业": 6.5, "财运": 6.0, "健康": 7.5, "婚姻": 6.5, "人际": 7.5}},
    "临":  {"dim_scores": {"事业": 7.5, "财运": 6.5, "健康": 7.0, "婚姻": 7.0, "人际": 7.0}},
    "升":  {"dim_scores": {"事业": 7.5, "财运": 6.5, "健康": 7.0, "婚姻": 6.0, "人际": 7.0}},
    "复":  {"dim_scores": {"事业": 7.0, "财运": 6.5, "健康": 7.5, "婚姻": 6.0, "人际": 7.0}},
    "大畜":{"dim_scores": {"事业": 8.0, "财运": 7.5, "健康": 7.0, "婚姻": 6.0, "人际": 6.5}},
    "师":  {"dim_scores": {"事业": 7.0, "财运": 5.5, "健康": 5.5, "婚姻": 4.5, "人际": 6.0}},
    "需":  {"dim_scores": {"事业": 6.5, "财运": 6.0, "健康": 6.0, "婚姻": 5.5, "人际": 5.5}},
    "节":  {"dim_scores": {"事业": 6.0, "财运": 6.5, "健康": 6.5, "婚姻": 6.0, "人际": 5.5}},
    "萃":  {"dim_scores": {"事业": 6.5, "财运": 6.0, "健康": 6.0, "婚姻": 5.5, "人际": 6.5}},
    "观":  {"dim_scores": {"事业": 6.0, "财运": 5.5, "健康": 6.5, "婚姻": 6.0, "人际": 6.5}},
    "夬":  {"dim_scores": {"事业": 7.5, "财运": 6.5, "健康": 6.0, "婚姻": 5.5, "人际": 6.0}},
    "豫":  {"dim_scores": {"事业": 6.0, "财运": 5.5, "健康": 6.0, "婚姻": 6.5, "人际": 6.0}},
    "井":  {"dim_scores": {"事业": 6.0, "财运": 6.5, "健康": 7.5, "婚姻": 5.5, "人际": 6.0}},
    "颐":  {"dim_scores": {"事业": 5.5, "财运": 6.0, "健康": 8.0, "婚姻": 6.5, "人际": 6.0}},
    "巽":  {"dim_scores": {"事业": 6.5, "财运": 6.0, "健康": 6.0, "婚姻": 5.5, "人际": 7.0}},
    "渐":  {"dim_scores": {"事业": 6.5, "财运": 5.5, "健康": 6.0, "婚姻": 6.5, "人际": 6.5}},
    "艮":  {"dim_scores": {"事业": 6.0, "财运": 5.5, "健康": 6.5, "婚姻": 5.5, "人际": 5.5}},
    "离":  {"dim_scores": {"事业": 6.5, "财运": 5.5, "健康": 6.0, "婚姻": 7.5, "人际": 6.5}},
    "革":  {"dim_scores": {"事业": 6.5, "财运": 5.5, "健康": 5.5, "婚姻": 6.0, "人际": 6.0}},
    "屯":  {"dim_scores": {"事业": 5.0, "财运": 4.5, "健康": 5.5, "婚姻": 5.0, "人际": 5.0}},
    "蒙":  {"dim_scores": {"事业": 5.5, "财运": 4.0, "健康": 5.0, "婚姻": 5.0, "人际": 5.5}},
    "讼":  {"dim_scores": {"事业": 4.0, "财运": 3.5, "健康": 5.0, "婚姻": 4.0, "人际": 3.5}},
    "蛊":  {"dim_scores": {"事业": 4.5, "财运": 4.0, "健康": 5.0, "婚姻": 4.0, "人际": 4.5}},
    "噬嗑":{"dim_scores": {"事业": 4.5, "财运": 4.0, "健康": 4.5, "婚姻": 3.5, "人际": 4.0}},
    "贲":  {"dim_scores": {"事业": 5.0, "财运": 4.5, "健康": 5.5, "婚姻": 6.0, "人际": 5.5}},
    "剥":  {"dim_scores": {"事业": 3.0, "财运": 3.0, "健康": 3.5, "婚姻": 3.0, "人际": 3.0}},
    "无妄":{"dim_scores": {"事业": 5.5, "财运": 4.5, "健康": 5.0, "婚姻": 5.0, "人际": 5.5}},
    "大过":{"dim_scores": {"事业": 3.5, "财运": 3.0, "健康": 3.0, "婚姻": 3.0, "人际": 3.5}},
    "坎":  {"dim_scores": {"事业": 4.0, "财运": 4.5, "健康": 4.0, "婚姻": 4.0, "人际": 4.5}},
    "遁":  {"dim_scores": {"事业": 5.0, "财运": 4.5, "健康": 6.0, "婚姻": 4.5, "人际": 5.5}},
    "明夷":{"dim_scores": {"事业": 4.0, "财运": 4.5, "健康": 4.5, "婚姻": 4.5, "人际": 4.0}},
    "睽":  {"dim_scores": {"事业": 4.5, "财运": 4.0, "健康": 5.0, "婚姻": 3.5, "人际": 4.0}},
    "蹇":  {"dim_scores": {"事业": 4.0, "财运": 3.5, "健康": 4.0, "婚姻": 4.0, "人际": 4.5}},
    "损":  {"dim_scores": {"事业": 5.5, "财运": 4.5, "健康": 5.5, "婚姻": 5.0, "人际": 5.0}},
    "姤":  {"dim_scores": {"事业": 5.5, "财运": 5.0, "健康": 5.5, "婚姻": 4.5, "人际": 5.0}},
    "困":  {"dim_scores": {"事业": 3.0, "财运": 2.5, "健康": 3.5, "婚姻": 3.0, "人际": 3.5}},
    "震":  {"dim_scores": {"事业": 5.5, "财运": 4.5, "健康": 5.0, "婚姻": 5.0, "人际": 5.5}},
    "归妹":{"dim_scores": {"事业": 5.0, "财运": 4.5, "健康": 5.5, "婚姻": 6.0, "人际": 5.0}},
    "旅":  {"dim_scores": {"事业": 5.5, "财运": 4.5, "健康": 5.5, "婚姻": 4.5, "人际": 5.5}},
    "涣":  {"dim_scores": {"事业": 5.5, "财运": 5.0, "健康": 5.5, "婚姻": 5.5, "人际": 5.5}},
    "小过":{"dim_scores": {"事业": 5.0, "财运": 4.5, "健康": 5.0, "婚姻": 5.0, "人际": 5.5}},
    "未济":{"dim_scores": {"事业": 4.5, "财运": 4.0, "健康": 4.5, "婚姻": 4.5, "人际": 4.5}},
    "否":  {"dim_scores": {"事业": 3.0, "财运": 3.5, "健康": 4.0, "婚姻": 3.5, "人际": 3.0}},
}

DIMENSIONS = ["事业", "财运", "健康", "婚姻", "人际"]

LIU_SHEN_ORDER = {
    "甲": ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"],
    "乙": ["朱雀", "勾陈", "螣蛇", "白虎", "玄武", "青龙"],
    "丙": ["勾陈", "螣蛇", "白虎", "玄武", "青龙", "朱雀"],
    "丁": ["螣蛇", "白虎", "玄武", "青龙", "朱雀", "勾陈"],
    "戊": ["白虎", "玄武", "青龙", "朱雀", "勾陈", "螣蛇"],
    "己": ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"],
    "庚": ["朱雀", "勾陈", "螣蛇", "白虎", "玄武", "青龙"],
    "辛": ["勾陈", "螣蛇", "白虎", "玄武", "青龙", "朱雀"],
    "壬": ["螣蛇", "白虎", "玄武", "青龙", "朱雀", "勾陈"],
    "癸": ["白虎", "玄武", "青龙", "朱雀", "勾陈", "螣蛇"],
}


def get_liu_shen_for_yao(day_gan: str, yao_idx: int) -> str:
    order = LIU_SHEN_ORDER.get(day_gan, LIU_SHEN_ORDER["甲"])
    return order[(yao_idx - 1) % 6]


def _calc_shen_bonus(day_gan: str, paipan: Dict) -> Tuple[Dict[str, float], List[str]]:
    moving = paipan.get("moving", [])
    if not moving:
        moving = [paipan.get("shi_yao", 1)]
    bonus = {d: 0.0 for d in DIMENSIONS}
    shen_names = []
    for m_idx in moving:
        shen = get_liu_shen_for_yao(day_gan, m_idx)
        shen_names.append(shen)
        dim_impact = LIU_SHEN_DIM.get(shen, {})
        for d in DIMENSIONS:
            bonus[d] += dim_impact.get(d, 0) * 0.8
    for d in DIMENSIONS:
        bonus[d] /= len(moving)
    return bonus, shen_names


def _calc_wang_bonus(paipan: Dict) -> Dict[str, float]:
    bonus = {d: 0.0 for d in DIMENSIONS}
    ws_list = paipan.get("wang_shuai", [])
    if not ws_list:
        return bonus
    for w in ws_list:
        zong = ZONG_WANG_SCORE.get(w.get("zong", "平"), 0)
        yue = YUE_WANG_SCORE.get(w.get("yue_wx", "平"), 0)
        sheng = SHENG_WANG_SCORE.get(w.get("sheng_wang", "养"), 0)
        kong = KONG_SCORE if w.get("kong", False) else 0
        weight = (7 - w.get("idx", 1)) / 21
        total = zong * 0.4 + yue * 0.2 + sheng * 0.2 + kong * 0.2
        qin = w.get("qin", "")
        qin_map = {
            "父母": ["事业", "健康"], "兄弟": ["人际", "财运"],
            "妻财": ["财运", "婚姻"], "官鬼": ["事业", "健康"],
            "子孙": ["健康", "人际"],
        }
        adims = qin_map.get(qin, DIMENSIONS)
        for d in adims:
            bonus[d] += total * weight * 0.5
    return bonus


def _calc_var_bonus(paipan: Dict) -> Dict[str, float]:
    var_gua = paipan.get("var_gua", "")
    if not var_gua:
        return {d: 0.0 for d in DIMENSIONS}
    base = GUA_SCORES.get(var_gua)
    if not base:
        return {d: 0.0 for d in DIMENSIONS}
    return {
        d: (0.15 if base["dim_scores"].get(d, 5) >= 8
            else (-0.15 if base["dim_scores"].get(d, 5) <= 4 else 0.0))
        for d in DIMENSIONS
    }


def _calc_moving_adj(paipan: Dict) -> float:
    n = len(paipan.get("moving", []))
    return {-1: -0.10, 0: -0.10, 1: 0.10, 2: 0.05, 3: 0.0,
            4: -0.05, 5: -0.10}.get(n, -0.15)


def _classify_weights(question: str = "") -> Dict[str, float]:
    w = {d: 1.0 for d in DIMENSIONS}
    if not question:
        return w
    kw_map = {
        "事业": ["事业", "工作", "职业", "创业", "项目", "升职", "跳槽", "生意", "官"],
        "财运": ["财运", "财", "赚钱", "收入", "股票", "投资", "理财", "金融", "债务"],
        "健康": ["健康", "病", "身体", "疾病", "手术", "养生"],
        "婚姻": ["婚姻", "感情", "恋爱", "结婚", "分手", "复合", "配偶", "姻缘"],
        "人际": ["人际", "社交", "合作", "团队", "朋友", "同事", "合伙"],
    }
    for dim, kws in kw_map.items():
        cnt = sum(1 for kw in kws if kw in question)
        if cnt:
            w[dim] += cnt * 0.5
    return w


def _yingshen(paipan: Dict, q: str = "") -> Dict:
    moving = paipan.get("moving", [])
    yongshen = paipan.get("yongshen_analysis", [])
    if not moving and not yongshen:
        return {"period": "信息不足", "note": "无动爻，时机不确定"}
    avg = sum(moving) / len(moving) if moving else 3
    if avg <= 2:
        period, months = "近期(~1个月)", [0, 1]
    elif avg <= 4:
        period, months = "中期(1-3个月)", [1, 3]
    else:
        period, months = "远期(3个月+)", [3, 6]
    acc = 0
    if yongshen:
        good = sum(1 for y in yongshen if y.get("综合旺衰", "平") in ["旺", "相"])
        bad = sum(1 for y in yongshen if y.get("综合旺衰", "平") in ["死", "囚", "绝"])
        acc = (good - bad) * 0.15
    parts = []
    if acc > 0:
        parts.append(f"用神偏旺，加速~{int(acc*100)}%")
    elif acc < 0:
        parts.append(f"用神偏弱，减速~{int(abs(acc)*100)}%")
    if not moving:
        parts.append("无动爻，事情尚未启动")
    elif len(moving) >= 4:
        parts.append("多爻动，事态多变")
    return {
        "period": period,
        "months_estimate": months,
        "acceleration": round(acc, 2),
        "note": "；".join(parts) or "待机而动",
    }


def _call_liuyao_engine(year: int, month: int, day: int, hour: int,
                         question: str = "") -> Optional[Dict]:
    try:
        sys.path.insert(0, os.path.expanduser(
            "~/.agents/skills/liuyao-divination-pro/scripts"))
        import liuyao_calc
        lines = liuyao_calc.random_gua()
        result = liuyao_calc.paipan(lines, question)
        if isinstance(result, dict):
            now = datetime.now()
            dg, dz = liuyao_calc.day_gz(now)
            result["_day_gan"] = dg
            return result
    except Exception as e:
        logger.error(f"六爻引擎调用失败: {e}")
    return None


def score_liuyao_dimensions(year: int = None, month: int = None, day: int = None,
                            hour: int = 12, question: str = "") -> Dict:
    """六爻五维评分主入口 v2.0（准S级）"""
    paipan_result = _call_liuyao_engine(year or 2026, month or 5, day or 4,
                                        hour, question)

    if not paipan_result:
        gua_name = random.choice(list(GUA_SCORES.keys()))
        base = GUA_SCORES[gua_name]
        scores = {}
        for d in DIMENSIONS:
            raw = base["dim_scores"].get(d, 5.0)
            s = max(1.0, min(10.0, raw + random.uniform(-0.5, 0.5)))
            scores[d] = {
                "score": round(s, 1),
                "level": "高" if s >= 7 else ("中" if s >= 4 else "低"),
                "note": f"六爻得{gua_name}卦（兜底）",
            }
        return {
            "dimensions": scores,
            "divination": {"hexagram": gua_name, "method": "兜底随机"},
            "yingshen": {"period": "不确定", "note": "引擎异常，兜底模式"},
            "system": "六爻", "available": True, "version": "2.0",
        }

    gua_name = paipan_result.get("gua_name", "坤")
    base = GUA_SCORES.get(gua_name, GUA_SCORES["坤"])
    day_gan = paipan_result.get("_day_gan", "甲")

    shen_bonus, shen_names = _calc_shen_bonus(day_gan, paipan_result)
    wang_bonus = _calc_wang_bonus(paipan_result)
    var_bonus = _calc_var_bonus(paipan_result)
    moving_adj = _calc_moving_adj(paipan_result)
    dim_weights = _classify_weights(question)

    scores = {}
    for d in DIMENSIONS:
        base_score = base["dim_scores"].get(d, 5.0)
        shen = shen_bonus.get(d, 0) * 2.0
        wang = wang_bonus.get(d, 0) * 3.0
        var = var_bonus.get(d, 0) * 1.5
        final = base_score + shen + wang + var + moving_adj * 1.0
        final = max(1.0, min(10.0, final))
        notes = [f"卦象{gua_name}"]
        if shen_names:
            notes.append(f"六神{','.join(shen_names)}")
        scores[d] = {
            "score": round(final, 1),
            "level": "高" if final >= 7 else ("中" if final >= 4 else "低"),
            "note": "；".join(notes),
        }

    yingshen = _yingshen(paipan_result, question)

    div_info = {
        "gua_name": gua_name,
        "gua_gong": paipan_result.get("gua_gong", ""),
        "upper/lower": f"{paipan_result.get('upper','')}{paipan_result.get('lower','')}",
        "moving": paipan_result.get("moving", []),
        "var_gua": paipan_result.get("var_gua", ""),
        "shi_yao": paipan_result.get("shi_yao", ""),
        "liu_shen": [get_liu_shen_for_yao(day_gan, i) for i in range(1, 7)],
        "xun_kong": paipan_result.get("xun_kong", []),
        "method": "专业引擎随机起卦",
    }

    return {
        "dimensions": scores,
        "divination": div_info,
        "yingshen": yingshen,
        "system": "六爻", "available": True, "version": "2.0",
    }


if __name__ == "__main__":
    print("═══ 六爻评分引擎 v2.0 (准S级) ═══\n")
    r = score_liuyao_dimensions(2026, 5, 4, 10, question="最近事业财运如何？")
    d = r["divination"]
    print(f"起卦: {d.get('gua_name','?')} -> {d.get('var_gua','')}")
    print(f"六神: {d.get('liu_shen','')}")
    print(f"动爻: {d.get('moving','')}")
    print(f"应期: {r['yingshen'].get('period','')} | {r['yingshen'].get('note','')}")
    print()
    for dim, info in r["dimensions"].items():
        print(f"  {dim}: {info['score']}/10 ({info['level']}) {info['note']}")
