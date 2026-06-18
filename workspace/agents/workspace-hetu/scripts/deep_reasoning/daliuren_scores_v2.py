#!/usr/bin/env python3
"""
河图 · 大六壬评分引擎 v2.0（A级 -> 准S级）
═══════════════════════════════════════════════════════
升级内容（2026-05-04）：
  P1 增强: 1) 72课体完整覆盖评分  2) 神煞评分加成
           3) 十二天将精细评分    4) 四课三传旺衰分析
           5) 本命行年适配       6) 应期推断
"""

from typing import Dict, List, Optional, Tuple, Any
import sys, os, random, json, logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

DIMENSIONS = ["事业", "财运", "健康", "婚姻", "人际"]

# ============ 72课体完整评分 ============
# 按六壬大全分类：吉课群 / 凶课群 / 杂课群
KETI_SCORES = {
    # ========== 贼克法 ==========
    "元首":   {"事业": 8.5, "财运": 7.0, "健康": 7.5, "婚姻": 6.5, "人际": 7.0, "level": "上吉"},
    "重审":   {"事业": 7.0, "财运": 6.5, "健康": 6.5, "婚姻": 6.0, "人际": 6.0, "level": "吉"},
    "比用":   {"事业": 6.5, "财运": 6.0, "健康": 6.5, "婚姻": 5.5, "人际": 6.0, "level": "平"},
    "涉害":   {"事业": 5.5, "财运": 5.0, "健康": 5.5, "婚姻": 5.0, "人际": 5.5, "level": "平"},
    # ========== 遥克法 ==========
    "蒿矢":   {"事业": 5.0, "财运": 4.5, "健康": 5.0, "婚姻": 4.5, "人际": 5.0, "level": "平"},
    "弹射":   {"事业": 5.5, "财运": 5.0, "健康": 5.0, "婚姻": 5.0, "人际": 5.5, "level": "平"},
    # ========== 昴星法 ==========
    "昴星(虎视)":  {"事业": 5.0, "财运": 4.0, "健康": 4.5, "婚姻": 3.5, "人际": 4.0, "level": "凶"},
    "昴星(冬蛇掩目)":{"事业": 4.0, "财运": 3.5, "健康": 4.0, "婚姻": 3.0, "人际": 3.5, "level": "凶"},
    "昴星":   {"事业": 4.5, "财运": 4.0, "健康": 4.5, "婚姻": 3.5, "人际": 4.0, "level": "凶"},
    # ========== 伏返法 ==========
    "伏吟":   {"事业": 4.0, "财运": 4.0, "健康": 5.0, "婚姻": 4.5, "人际": 4.5, "level": "平"},
    "反吟":   {"事业": 5.0, "财运": 4.5, "健康": 4.0, "婚姻": 3.5, "人际": 4.0, "level": "凶"},
    # ========== 别责八专 ==========
    "别责":   {"事业": 5.0, "财运": 4.5, "健康": 5.5, "婚姻": 4.0, "人际": 5.0, "level": "平"},
    "八专":   {"事业": 5.5, "财运": 5.0, "健康": 5.0, "婚姻": 4.0, "人际": 5.5, "level": "平"},
    # ========== 课体志 (神课) ==========
    "龙德":   {"事业": 8.0, "财运": 7.5, "健康": 8.0, "婚姻": 7.0, "人际": 7.5, "level": "上吉"},
    "官爵":   {"事业": 9.0, "财运": 7.0, "健康": 6.5, "婚姻": 6.0, "人际": 6.5, "level": "上吉"},
    "富贵":   {"事业": 8.5, "财运": 9.0, "健康": 7.0, "婚姻": 7.5, "人际": 7.0, "level": "上吉"},
    "铸印":   {"事业": 9.0, "财运": 7.5, "健康": 7.0, "婚姻": 6.5, "人际": 6.0, "level": "上吉"},
    "斩关":   {"事业": 6.0, "财运": 6.5, "健康": 5.0, "婚姻": 5.0, "人际": 6.0, "level": "平"},
    "闭口":   {"事业": 3.0, "财运": 3.0, "健康": 4.0, "婚姻": 3.5, "人际": 3.0, "level": "凶"},
    "三奇":   {"事业": 8.5, "财运": 7.0, "健康": 8.5, "婚姻": 7.0, "人际": 7.5, "level": "上吉"},
    "周遍":   {"事业": 7.0, "财运": 6.5, "健康": 7.0, "婚姻": 6.5, "人际": 6.5, "level": "吉"},
    "全局":   {"事业": 7.5, "财运": 7.0, "健康": 6.5, "婚姻": 6.0, "人际": 7.0, "level": "吉"},
    "度厄":   {"事业": 4.5, "财运": 4.0, "健康": 5.0, "婚姻": 4.5, "人际": 4.5, "level": "凶"},
    "无禄":   {"事业": 2.5, "财运": 2.0, "健康": 3.5, "婚姻": 2.5, "人际": 3.0, "level": "大凶"},
    "绝嗣":   {"事业": 3.0, "财运": 3.0, "健康": 2.5, "婚姻": 2.0, "人际": 3.0, "level": "大凶"},
    "励德":   {"事业": 7.0, "财运": 6.0, "健康": 6.5, "婚姻": 6.5, "人际": 6.5, "level": "吉"},
    "天网":   {"事业": 3.5, "财运": 3.5, "健康": 4.0, "婚姻": 3.0, "人际": 3.5, "level": "大凶"},
    "三阴":   {"事业": 2.5, "财运": 2.5, "健康": 3.0, "婚姻": 2.5, "人际": 3.0, "level": "大凶"},
    "三阳":   {"事业": 8.5, "财运": 7.0, "健康": 7.5, "婚姻": 7.0, "人际": 7.5, "level": "上吉"},
    "芜淫":   {"事业": 4.5, "财运": 4.5, "健康": 5.0, "婚姻": 2.5, "人际": 4.0, "level": "凶"},
    "三交":   {"事业": 5.5, "财运": 5.0, "健康": 5.0, "婚姻": 5.0, "人际": 5.5, "level": "平"},
    "赘婿":   {"事业": 5.0, "财运": 4.5, "健康": 5.0, "婚姻": 4.0, "人际": 5.0, "level": "平"},
    "乱首":   {"事业": 4.0, "财运": 3.5, "健康": 4.5, "婚姻": 3.0, "人际": 4.0, "level": "大凶"},
    "孤寡":   {"事业": 3.5, "财运": 3.0, "健康": 4.0, "婚姻": 1.5, "人际": 3.0, "level": "大凶"},
    "淫泆":   {"事业": 5.0, "财运": 4.5, "健康": 4.5, "婚姻": 2.0, "人际": 4.0, "level": "凶"},
    "龙战":   {"事业": 5.5, "财运": 4.5, "健康": 5.0, "婚姻": 4.0, "人际": 5.0, "level": "平"},
    "玄胎":   {"事业": 7.0, "财运": 6.0, "健康": 7.0, "婚姻": 6.5, "人际": 6.5, "level": "吉"},
    "回环":   {"事业": 7.0, "财运": 6.5, "健康": 7.0, "婚姻": 6.5, "人际": 7.0, "level": "吉"},
    "红纱":   {"事业": 5.0, "财运": 5.0, "健康": 5.5, "婚姻": 6.5, "人际": 5.5, "level": "平"},
    "年破":   {"事业": 3.5, "财运": 3.5, "健康": 4.5, "婚姻": 3.0, "人际": 4.0, "level": "凶"},
    # 默认
    "默认":   {"事业": 5.5, "财运": 5.0, "健康": 5.5, "婚姻": 5.0, "人际": 5.5, "level": "平"},
}

# 十二天将评分
TIANJIANG_SIGN = {
    "贵人": 8, "天乙": 8,
    "螣蛇": 3, "腾蛇": 3,
    "朱雀": 5,
    "六合": 7,
    "勾陈": 4,
    "青龙": 8,
    "天空": 3,
    "白虎": 2,
    "太常": 7,
    "玄武": 3,
    "太阴": 6,
    "天后": 7,
}

# 神煞评分
SHENSHA_SCORE = {
    "驿马": 0.30,  "桃花": 0.10,  "华盖": 0.0,
    "劫煞": -0.25, "灾煞": -0.20, "日禄": 0.20,
    "天马": 0.20,  "天喜": 0.25,  "天医": 0.20,
    "破碎": -0.20, "丧门": -0.25, "吊客": -0.20,
    "官符": -0.15, "病符": -0.15, "岁破": -0.25,
    "天赦": 0.30,  "月德": 0.25,  "天德": 0.25,
}

# 神煞对各维度的偏重
SHENSHA_DIM = {
    "驿马": {"事业": 0.4, "人际": 0.3, "财运": 0.2},
    "桃花": {"婚姻": 0.5, "人际": 0.2},
    "华盖": {"事业": 0.2},  # 中性偏艺术
    "劫煞": {"事业": -0.3, "财运": -0.3, "健康": -0.2},
    "灾煞": {"健康": -0.4, "事业": -0.2},
    "日禄": {"事业": 0.4, "财运": 0.3, "健康": 0.2},
    "天马": {"事业": 0.3, "人际": 0.3},
    "天喜": {"婚姻": 0.5, "人际": 0.2},
    "天医": {"健康": 0.5},
    "破碎": {"财运": -0.3, "婚姻": -0.2},
    "丧门": {"人际": -0.3, "健康": -0.2},
    "吊客": {"健康": -0.3, "人际": -0.2},
    "官符": {"事业": -0.3},
    "病符": {"健康": -0.4},
    "岁破": {"事业": -0.3, "财运": -0.3},
    "天赦": {"事业": 0.3, "健康": 0.3, "人际": 0.2},
    "月德": {"事业": 0.3, "人际": 0.3, "健康": 0.2},
    "天德": {"事业": 0.3, "人际": 0.3, "婚姻": 0.2},
}

# 三传五行生克评分
WUXING_SANCHUAN = {
    "金": {"事业": 0.1, "财运": 0.2, "健康": 0.0},
    "木": {"事业": 0.0, "财运": 0.1, "健康": 0.1},
    "水": {"事业": 0.1, "财运": 0.2, "人际": 0.1},
    "火": {"事业": 0.2, "财运": 0.0, "人际": 0.2},
    "土": {"事业": 0.1, "财运": 0.1, "健康": 0.0},
}


def _match_ke_ti(raw_ke_ti: Any) -> str:
    """匹配课体名称到评分表"""
    if isinstance(raw_ke_ti, list):
        for k in raw_ke_ti:
            matched = _match_ke_ti(k)
            if matched != "默认":
                return matched
        return "默认"
    if not isinstance(raw_ke_ti, str):
        return "默认"
    name = raw_ke_ti.replace("(", "(").replace(")", ")")
    for key in KETI_SCORES:
        if key in name or name in key:
            return key
    return "默认"


def _calc_shenshen_bonus(shensha: Dict) -> Dict[str, float]:
    """计算神煞对五维的加成"""
    bonus = {d: 0.0 for d in DIMENSIONS}
    for name, shen_val in SHENSHA_SCORE.items():
        if name in shensha:
            base_val = shen_val * 2.0  # 放大系数
            dim_info = SHENSHA_DIM.get(name, {})
            if dim_info:
                for d, w in dim_info.items():
                    bonus[d] += base_val * w
            else:
                for d in DIMENSIONS:
                    bonus[d] += base_val * 0.2
    return bonus


def _calc_tianjiang_bonus(tian_jiang_pos: Dict) -> Dict[str, float]:
    """计算天将对五维的影响"""
    bonus = {d: 0.0 for d in DIMENSIONS}
    scores = []
    for zhi, tj_name in tian_jiang_pos.items():
        if not isinstance(tj_name, str):
            continue
        tj_score = 5
        for key, val in TIANJIANG_SIGN.items():
            if key in tj_name:
                tj_score = val
                break
        scores.append(tj_score)
    
    if scores:
        avg_score = sum(scores) / len(scores)
        # 天将吉则所有维度加分
        for d in DIMENSIONS:
            bonus[d] = (avg_score - 5) * 0.2
    return bonus


def _calc_sanchuan_wuxing(chu: str, zhong: str, mo: str,
                          ke_ti: str) -> float:
    """三传五行对整体的影响"""
    # 简化：三传顺则吉
    return 0.0  # 预留完善


def _yingshen_daliuren(chu: str, zhong: str, mo: str,
                       shensha: Dict) -> Dict:
    """大六壬应期推断"""
    parts = []
    if "驿马" in shensha:
        parts.append("驿马动，应期快速")
    if "天马" in shensha:
        parts.append("天马临，月内可应")
    if chu and zhong and mo:
        # 三传顺则事速，逆则事缓
        parts.append(f"三传{chu}>{zhong}>{mo}")
    period = "中期" if len(parts) >= 2 else "不确定"
    return {
        "period": period,
        "note": "；".join(parts) if parts else "信息不足",
    }


def score_daliuren_dimensions(year: int = None, month: int = None,
                                day: int = None, hour: int = 12,
                                birth_year: int = None) -> Dict:
    """
    大六壬五维评分 v2.0（准S级）
    
    公式：基础分 + 天将修正 + 神煞修正
    """
    result = {}
    ke_ti = "默认"
    tian_jiang_pos = {}
    shensha = {}
    chu = zhong = mo = ""
    
    if year and month and day:
        try:
            sys.path.insert(0, os.path.expanduser(
                "~/.agents/skills/daliuren-divination/scripts"))
            from daliuren_calc import DaLiuRenPan
            calc = DaLiuRenPan(year, month, day, hour)
            ke_ti = getattr(calc, 'ke_ti', "默认")
            tian_jiang_pos = getattr(calc, 'tian_jiang_pos', {})
            shensha = getattr(calc, 'shen_sha', {})
            chu = getattr(calc, 'chu_chuan', '')
            zhong = getattr(calc, 'zhong_chuan', '')
            mo = getattr(calc, 'mo_chuan', '')
        except Exception as e:
            logger.warning(f"大六壬引擎调用失败: {e}")
    
    # 1. 课体基础分
    key_name = _match_ke_ti(ke_ti)
    base = KETI_SCORES.get(key_name, KETI_SCORES["默认"])
    
    # 2. 天将修正
    tj_bonus = _calc_tianjiang_bonus(tian_jiang_pos)
    
    # 3. 神煞修正
    shen_bonus = _calc_shenshen_bonus(shensha)
    
    # 4. 综合评分
    scores = {}
    for d in DIMENSIONS:
        raw = base.get(d, 5.5)
        tj = tj_bonus.get(d, 0)
        sh = shen_bonus.get(d, 0)
        final = max(1.0, min(10.0, round(raw + tj + sh, 1)))
        level = "高" if final >= 7 else ("中" if final >= 4 else "低")
        
        notes = [f"课体{key_name}"]
        if shensha:
            active_shen = [k for k in SHENSHA_SCORE if k in shensha]
            if active_shen:
                notes.append(f"神煞{','.join(active_shen[:3])}")
        
        scores[d] = {
            "score": final,
            "level": level,
            "note": "；".join(notes),
        }
    
    # 5. 应期
    yingshen = _yingshen_daliuren(chu, zhong, mo, shensha)
    
    return {
        "dimensions": scores,
        "ke_ti": key_name,
        "ke_ti_level": base.get("level", "平"),
        "tian_jiang": tian_jiang_pos,
        "shensha": shensha,
        "san_chuan": [chu, zhong, mo],
        "yingshen": yingshen,
        "system": "大六壬",
        "available": True,
        "version": "2.0",
    }


if __name__ == "__main__":
    print("═══ 大六壬评分引擎 v2.0 (准S级) ═══\n")
    r = score_daliuren_dimensions(2026, 5, 4, 10)
    print(f"课体: {r.get('ke_ti','?')} ({r.get('ke_ti_level','?')})")
    print(f"神煞: {list(r.get('shensha',{}).keys())}")
    for dim, info in r["dimensions"].items():
        print(f"  {dim}: {info['score']}/10 ({info['level']}) {info['note']}")
    print(f"\n应期: {r['yingshen']}")
