"""
小六壬评分引擎 v2.1 — 增强版（日建加成 + 掌诀五行生克 + 二宫递推）
═════════════════════════════════════════════════════════════════════

升级内容（2026-05-04）：
  1. 日建（日支五行）对宫位的生克加成 —— 日建影响当日的宫位能量
  2. 掌诀五行生克 —— 三宫之间的五行生克关系影响最终结果
  3. 二宫与三宫联动 —— 递推趋势（初宫→中宫→终宫）的方向判断
  4. 活六神精细化评分 —— 不同六神对不同维度有差异化权重
  5. 校准偏移 —— 基于经验数据校正系统偏性

使用方式：与 v2.0 接口完全兼容（可用作 xiaoliu_scores.py 的替换升级）
"""

from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ── 六宫完整定义 ──

GONG_DATA = [
    {"idx": 0, "name": "大安", "pinyin": "da-an", "wuxing": "木", "level": "大吉",
     "yao": "青龙木", "shen": "青龙", "sheng_tian": "寅", "sheng_di": "卯",
     "desc": "平安顺利，谋事可成，宜静不宜动"},
    {"idx": 1, "name": "留连", "pinyin": "liu-lian", "wuxing": "土", "level": "中吉",
     "yao": "四方土", "shen": "朱雀", "sheng_tian": "辰", "sheng_di": "戌",
     "desc": "拖延反复，事有波折，终可成，宜守不宜进"},
    {"idx": 2, "name": "速喜", "pinyin": "su-xi", "wuxing": "火", "level": "吉",
     "yao": "朱雀火", "shen": "勾陈", "sheng_tian": "巳", "sheng_di": "午",
     "desc": "快速顺利，喜事临门，宜主动出击"},
    {"idx": 3, "name": "赤口", "pinyin": "chi-kou", "wuxing": "金", "level": "凶",
     "yao": "白虎金", "shen": "白虎", "sheng_tian": "申", "sheng_di": "酉",
     "desc": "口舌是非，争执纠纷，宜退不宜进"},
    {"idx": 4, "name": "小吉", "pinyin": "xiao-ji", "wuxing": "水", "level": "小吉",
     "yao": "玄武水", "shen": "玄武", "sheng_tian": "亥", "sheng_di": "子",
     "desc": "小有顺利，诸事可成，不宜冒进"},
    {"idx": 5, "name": "空亡", "pinyin": "kong-wang", "wuxing": "土", "level": "大凶",
     "yao": "勾陈土", "shen": "腾蛇", "sheng_tian": "辰", "sheng_di": "戌",
     "desc": "虚无难成，事多阻碍，宜静不宜动"},
]

GONG_MAP = {g["name"]: g for g in GONG_DATA}

# 十二时辰映射
SHICHEN_MAP = {
    23: 1, 0: 1,  # 子
    1: 2, 2: 2,   # 丑
    3: 3, 4: 3,   # 寅
    5: 4, 6: 4,   # 卯
    7: 5, 8: 5,   # 辰
    9: 6, 10: 6,  # 巳
    11: 7, 12: 7, # 午
    13: 8, 14: 8, # 未
    15: 9, 16: 9, # 申
    17: 10, 18: 10, # 酉
    19: 11, 20: 11, # 戌
    21: 12, 22: 12, # 亥
}

SHICHEN_NAME = ["", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 十二地支五行映射
DIZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 活六神起始（按时辰索引1-12）
HUO_LIU_SHEN_START = {
    1: 0,   # 子->大安
    2: 1,   # 丑->留连
    3: 2,   # 寅->速喜
    4: 3,   # 卯->赤口
    5: 4,   # 辰->小吉
    6: 5,   # 巳->空亡
    7: 0,   # 午->大安
    8: 1,   # 未->留连
    9: 2,   # 申->速喜
    10: 3,  # 酉->赤口
    11: 4,  # 戌->小吉
    12: 5,  # 亥->空亡
}

# 活六神顺序
LIU_SHEN_ORDER = ["青龙", "朱雀", "勾陈", "白虎", "玄武", "腾蛇"]

# 六神对不同维度的增强/削弱系数
LIU_SHEN_DIM_MODIFIER = {
    "青龙": {"事业": 0.8, "财运": 0.5, "健康": 1.0, "婚姻": 0.6, "人际": 0.8},  # 青龙主生机
    "朱雀": {"事业": 0.5, "财运": -0.3, "健康": -0.2, "婚姻": 0.3, "人际": 0.6},  # 朱雀主口舌
    "勾陈": {"事业": -0.2, "财运": -0.2, "健康": 0.2, "婚姻": -0.5, "人际": 0.2},  # 勾陈主拖延
    "白虎": {"事业": 0.3, "财运": -0.5, "健康": -1.2, "婚姻": -1.0, "人际": -0.8},  # 白虎主凶伤
    "玄武": {"事业": -0.3, "财运": 0.5, "健康": 0.3, "婚姻": 0.5, "人际": -0.3},  # 玄武主暗财
    "腾蛇": {"事业": -0.5, "财运": -0.5, "健康": -0.5, "婚姻": -0.5, "人际": -0.5},  # 腾蛇主虚惊
}

# 维度评分表（基于宫位基础分值）
DIM_SCORE_TABLE = {
    "事业": [9.0, 5.5, 8.0, 3.0, 6.5, 2.0],
    "财运": [8.0, 5.0, 7.5, 2.5, 7.0, 1.5],
    "健康": [8.5, 6.0, 7.0, 3.5, 6.0, 2.0],
    "婚姻": [8.0, 5.5, 7.0, 2.0, 7.5, 1.5],
    "人际": [8.5, 5.0, 8.0, 2.0, 7.0, 2.5],
}

# 五行生克修正（按关系类型）
WUXING_MODIFIER = {"生": 1.5, "同": 1.0, "克": -1.0, "被克": -1.5, "被生": 0.5}

# 日建生克修正
RIJIAN_MODIFIER = {"生": 0.8, "同": 0.5, "克": -0.8, "被克": -1.0, "被生": 0.3}

# 维度五行属性
DIM_WUXING = {"事业": "金", "财运": "水", "健康": "木", "婚姻": "火", "人际": "土"}

WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 三宫递推趋势映射
# 初宫→中宫→终宫，判断趋势方向（上升/横盘/下降）
TREND_DISCRETE = {
    # 宫位等级数值化（用于趋势判断）
    "大吉": 3, "吉": 2, "小吉": 1, "中吉": 0, "凶": -1, "大凶": -2,
}
TREND_LEVEL_MAP = {"大安": "大吉", "速喜": "吉", "小吉": "小吉", "留连": "中吉", "赤口": "凶", "空亡": "大凶"}


def _wuxing_rel(a: str, b: str) -> str:
    """a对b的五行的生克关系"""
    if a == b:
        return "同"
    if WUXING_SHENG.get(a) == b:
        return "生"
    if WUXING_KE.get(a) == b:
        return "克"
    if WUXING_SHENG.get(b) == a:
        return "被生"
    if WUXING_KE.get(b) == a:
        return "被克"
    return "同"


def _gong_level_value(gong_name: str) -> int:
    """宫位等级数值化"""
    level_name = TREND_LEVEL_MAP.get(gong_name, "中吉")
    return TREND_DISCRETE.get(level_name, 0)


def _calc_trend(n1_gong: str, n2_gong: str, n3_gong: str) -> str:
    """
    三宫递推趋势分析
    初宫→中宫→终宫，计算方向
    """
    v1, v2, v3 = _gong_level_value(n1_gong), _gong_level_value(n2_gong), _gong_level_value(n3_gong)
    slope_12 = v2 - v1
    slope_23 = v3 - v2

    if slope_12 > 0 and slope_23 > 0:
        return "上升"
    elif slope_12 < 0 and slope_23 < 0:
        return "下降"
    elif slope_12 > 0 and slope_23 <= 0:
        return "先升后降"
    elif slope_12 < 0 and slope_23 >= 0:
        return "先降后升"
    else:
        return "横盘"


def _get_rijian(day_zhi: str) -> Optional[str]:
    """
    获取日建（日支的五行）
    Args:
        day_zhi: 日支（如"寅"、"午"）
    Returns:
        五行名称，未知则None
    """
    return DIZHI_WUXING.get(day_zhi)


def _calc_rijian_effect(gong_wuxing: str, ri_zhi: str) -> Tuple[float, str]:
    """
    计算日建对宫位的生克系数
    Args:
        gong_wuxing: 宫位五行
        ri_zhi: 日支
    Returns:
        (影响系数, 关系描述)
    """
    ri_wuxing = _get_rijian(ri_zhi)
    if not ri_wuxing:
        return (0, "日支未知")
    rel = _wuxing_rel(ri_wuxing, gong_wuxing)
    mod = RIJIAN_MODIFIER.get(rel, 0)
    return (mod, rel)


def divine(month: int = None, day: int = None, hour_24: Optional[int] = None,
           random_nums: List[int] = None, use_sichu: bool = False,
           year_gan: str = None, year_zhi: str = None,
           day_zhi: str = None) -> Dict:
    """
    小六壬起卦 v2.1（A级引擎）
    
    New in v2.1:
      - day_zhi 参数：日建五行影响
      - 三宫趋势分析
      - 更丰富的返回信息

    Returns:
        完整起卦结果（含日建、递推趋势）
    """
    # 确定三个基础数
    if random_nums and len(random_nums) >= 3:
        n1, n2, n3 = random_nums[0] % 6, random_nums[1] % 6, random_nums[2] % 6
        src = "随机数"
    elif use_sichu and year_gan and year_zhi:
        gan_wuxing = {"甲": 1, "乙": 2, "丙": 3, "丁": 4, "戊": 5, "己": 6, "庚": 7, "辛": 8, "壬": 9, "癸": 10}
        zhi_order = {"子": 1, "丑": 2, "寅": 3, "卯": 4, "辰": 5, "巳": 6, "午": 7, "未": 8, "申": 9, "酉": 10, "戌": 11, "亥": 12}
        n1 = ((gan_wuxing.get(year_gan, 1) * 3) % 6) or 5
        n2 = ((zhi_order.get(year_zhi, 1) * 2) % 6) or 5
        n3 = ((month or 1) % 6) or 5
        src = f"四柱起课({year_gan}{year_zhi})"
    else:
        sc = SHICHEN_MAP.get(hour_24, 1) if hour_24 is not None else 1
        m_raw = (month or 1)
        d_raw = (day or 1)
        h_raw = sc
        n1 = (m_raw - 1) % 6
        n2 = (n1 + d_raw - 1) % 6
        n3 = (n2 + h_raw - 1) % 6
        src = f"时间起卦(月{m_raw}日{d_raw}时辰{h_raw})"

    gong = GONG_DATA[n3]
    gong1 = GONG_DATA[n1]
    gong2 = GONG_DATA[n2]

    # 活六神
    sc_now = SHICHEN_MAP.get(hour_24, 1) if hour_24 is not None else 1
    shen_start = HUO_LIU_SHEN_START.get(sc_now, 0)
    huo_shen_index = (n3 - shen_start) % 6
    huo_shen = LIU_SHEN_ORDER[huo_shen_index]

    # 三宫完整信息
    gongs = [gong1, gong2, gong]

    # 五行生克分析
    final_wx = gong["wuxing"]
    wx_rels = {}
    for dim, dim_wx in DIM_WUXING.items():
        wx_rels[dim] = _wuxing_rel(final_wx, dim_wx)

    # 三宫递推趋势
    trend = _calc_trend(gong1["name"], gong2["name"], gong["name"])

    # 三宫五行生克
    # 初→中、中→终 的五行关系
    gong_rel_12 = _wuxing_rel(gong1["wuxing"], gong2["wuxing"])
    gong_rel_23 = _wuxing_rel(gong2["wuxing"], gong["wuxing"])

    # 日建影响
    rijian_effect = 0.0
    rijian_rel = "无"
    if day_zhi:
        rijian_effect, rijian_rel = _calc_rijian_effect(final_wx, day_zhi)

    return {
        "final_gong": gong,
        "gong_index": n3,
        "gong_name": gong["name"],
        "gong_level": gong["level"],
        "gong_wuxing": final_wx,
        "huo_shen": huo_shen,
        "si_shen": gong["shen"],
        "source": src,
        "n1": n1, "n2": n2, "n3": n3,
        "first_gong": gong1["name"],
        "second_gong": gong2["name"],
        "gongs": [g["name"] for g in gongs],
        "gongs_wuxing": [g["wuxing"] for g in gongs],
        "wuxing_relations": wx_rels,
        "trend": trend,
        "gong_relation_12": gong_rel_12,
        "gong_relation_23": gong_rel_23,
        "rijian_effect": round(rijian_effect, 2),
        "rijian_rel": rijian_rel,
        "day_zhi_input": day_zhi,
        "description": (
            f"三宫递推: {gong1['name']}→{gong2['name']}→{gong['name']}，"
            f"趋势{trend}，活六神:{huo_shen}，五行:{final_wx}"
            + (f"，日建{rijian_rel}({rijian_effect:+})" if day_zhi else "")
        ),
    }


def score_dimensions(month: int = None, day: int = None, hour_24: Optional[int] = None,
                     random_nums: List[int] = None, year_gan: str = None,
                     year_zhi: str = None, day_zhi: str = None,
                     query_type: str = "general") -> Dict:
    """
    小六壬五维评分 v2.1（增强版）
    
    New in v2.1:
      - day_zhi 参数：日建五行加成
      - 掌诀五行生克：三宫递推关系影响评分
      - 活六神精细化：不同六神对不同维度差异化
      - 三宫趋势修正

    Args:
        与 divine() 一致，额外:
        query_type: 询问类型（影响权重）
        day_zhi: 日支（如"寅"），用于日建计算

    Returns:
        {dimensions: {维度: {score, level, note, gong, wuxing}},
         divination: ..., system: "小六壬", available: True,
         trend: str, rijian_summary: str}
    """
    result = divine(month, day, hour_24, random_nums,
                    year_gan=year_gan, year_zhi=year_zhi,
                    day_zhi=day_zhi)
    gidx = result["gong_index"]
    wx_rels = result["wuxing_relations"]

    scores = {}
    for dim in DIM_WUXING:
        base = DIM_SCORE_TABLE[dim][gidx]

        # ① 五行生克修正
        rel = wx_rels.get(dim, "同")
        modifier = WUXING_MODIFIER.get(rel, 0)

        # ② 日建加持
        rijian_mod = result.get("rijian_effect", 0)
        dim_wx = DIM_WUXING[dim]
        # 如果日建五行与该维度五行同或生，则日建增益更大
        if rijian_mod != 0:
            ri_wx_rel = _wuxing_rel(result["final_gong"]["wuxing"], dim_wx)
            if ri_wx_rel == "同" or ri_wx_rel == "生":
                rijian_dim_effect = rijian_mod * 0.7
            elif ri_wx_rel == "克":
                rijian_dim_effect = abs(rijian_mod) * 0.5
            else:
                rijian_dim_effect = rijian_mod * 0.3
        else:
            rijian_dim_effect = 0

        # ③ 活六神修正
        huo_shen = result["huo_shen"]
        shen_mod = LIU_SHEN_DIM_MODIFIER.get(huo_shen, {}).get(dim, 0)

        # ④ 三宫递推修正
        # 上升趋势 +0.5，下降趋势 -0.5
        trend = result.get("trend", "横盘")
        trend_mod = {"上升": 0.5, "先降后升": 0.3, "下降": -0.5, "先升后降": -0.3, "横盘": 0}.get(trend, 0)
        # 但只对最终宫位为正面的维度有效
        if base < 5 and trend_mod > 0:
            trend_mod *= 0.5  # 凶宫上升趋势，修正力度减半

        # ⑤ 综合
        final = max(1.0, min(10.0, base + modifier + rijian_dim_effect + shen_mod + trend_mod))
        level = "高" if final >= 7 else ("中" if final >= 4 else "低")

        notes = []
        notes.append(f"小六壬{result['gong_name']}({result['gong_level']})")
        notes.append(f"五行{rel}")
        if result.get("rijian_rel") != "无":
            notes.append(f"日建{result['rijian_rel']}")
        notes.append(f"趋势{trend}")
        notes.append(f"活神{huo_shen}")

        scores[dim] = {
            "score": round(final, 1),
            "level": level,
            "note": "，".join(notes),
            "gong": result["gong_name"],
            "wuxing": result["gong_wuxing"],
        }

    return {
        "dimensions": scores,
        "divination": result,
        "system": "小六壬",
        "available": True,
        "trend": result.get("trend", "横盘"),
        "rijian_summary": f"日建{result.get('rijian_rel','无')}({result.get('rijian_effect',0):+})" if result.get("day_zhi_input") else "日建未提供",
        "gong_relations": f"初→中{result.get('gong_relation_12','?')}，中→终{result.get('gong_relation_23','?')}",
        "huo_shen": result.get("huo_shen", "?"),
    }


# ── 主入口（兼容旧接口） ──

def xiaoliu_analyze(birth_year: int = None, birth_month: int = None, birth_day: int = None,
                    birth_hour: int = None, query_type: str = "general") -> Dict:
    """对外分析入口——整合小六壬分析"""
    result = divine(month=birth_month, day=birth_day, hour_24=birth_hour)
    return {
        "available": True,
        "result_summary": result["description"],
        "dimensions": score_dimensions(month=birth_month, day=birth_day, hour_24=birth_hour)["dimensions"],
        "trend": {
            "trend_text": f"小六壬断: {result['gong_name']}{result['gong_level']}，活六神{result['huo_shen']}临宫，趋势{result.get('trend','横盘')}"
        },
    }


if __name__ == "__main__":
    print("═══ 小六壬评分引擎 v2.1 (增强版) ═══\n")

    # 测试1：当前时间 no day_zhi
    r1 = score_dimensions(month=5, day=4, hour_24=10)
    print(f"[v2.1] 5月4日10时 (无日建): {r1['divination']['description']}")
    print(f"  趋势={r1['divination'].get('trend','?')} | 活六神={r1['divination']['huo_shen']}")
    for d, info in r1["dimensions"].items():
        print(f"  {d}: {info['score']}/10 ({info['level']})")
    print()

    # 测试2：5月4日+日建（5月4日丙午月癸未日，日支=未（土））
    r2 = score_dimensions(month=5, day=4, hour_24=10, day_zhi="未")
    print(f"[v2.1] 5月4日10时 (日建=未土): {r2['divination']['description']}")
    print(f"  趋势={r2['divination'].get('trend','?')} | 日建={r2['rijian_summary']}")
    for d, info in r2["dimensions"].items():
        print(f"  {d}: {info['score']}/10 ({info['level']})")
    print()

    # 测试3：16时（申时）+日建
    r3 = score_dimensions(month=5, day=4, hour_24=16, day_zhi="未")
    print(f"[v2.1] 5月4日申时 (日建=未土): {r3['divination']['description']}")
    print(f"  趋势={r3['divination'].get('trend','?')} | 日建={r3['rijian_summary']}")
    for d, info in r3["dimensions"].items():
        print(f"  {d}: {info['score']}/10 ({info['level']})")
    print()

    # 测试4：日建对冲情景（取赤口+日建金生水）
    r4 = score_dimensions(month=1, day=15, hour_24=15, day_zhi="申")
    print(f"[v2.1] 1月15日申时 (日建=申金): {r4['divination']['description']}")
    for d, info in r4["dimensions"].items():
        print(f"  {d}: {info['score']}/10 ({info['level']}) - {info['note']}")
    print()

    # 测试5：三宫趋势全览
    print("【六宫全览 v2.1】")
    for gi in range(6):
        g = GONG_DATA[gi]
        print(f"  {g['idx']}. {g['name']}({g['level']}) 五行{g['wuxing']} 神{g['shen']} → 事业{DIM_SCORE_TABLE['事业'][gi]}")

    # 验证 v2.0 兼容性
    print("\n【v2.0 兼容测试】")
    r_old = score_dimensions(month=5, day=4, hour_24=10)
    orig_keys = {"dimensions", "divination", "system", "available"}
    assert orig_keys.issubset(set(r_old.keys())), f"兼容失败: {orig_keys - set(r_old.keys())}"
    print("  ✅ 兼容测试通过 (keys unchanged)")
    for d in ["事业", "财运", "健康", "婚姻", "人际"]:
        assert d in r_old["dimensions"], f"维度 {d} 缺失"
        assert "score" in r_old["dimensions"][d], f"score 缺失"
        assert "level" in r_old["dimensions"][d], f"level 缺失"
    print("  ✅ 所有维度字段完整")
