#!/usr/bin/env python3
"""
河图 · 铁板神数考刻引擎（精简版） v1.0
══════════════════════════════════════
核心方法论（铁板神数·已兼容现代应用）：
  1. "考刻" —— 出生时辰的微调确认（刻=2.5分钟，一个时辰=120分钟=8刻）
  2. "六亲定位" —— 按考刻后的八字定位父母/兄弟姐妹/子女情况
  3. "数理卦" —— 将八字转化为卦象，再还原为"数"
  4. "条文查对" —— 原始的6000条辞（我们这里"以理代数，用逻辑推理替代条文记忆"）
  
⚠️ 声明：铁板神数原始版本需要背6000条暗码，本引擎采用"逻辑铁板"方法：
  - 保留铁板的考刻+六亲+数理框架
  - 用现代八字推理替代晦涩条文
  - 达到"神数"的精准度，用AI推理补上
"""

from typing import Dict, List, Optional, Tuple, Any
import math
import sys, os

# 导入bazi_calc_v2的藏干数据
_BAZI_PATH = os.path.expanduser("~/.agents/skills/bazi-mingli/scripts")
if _BAZI_PATH not in sys.path:
    sys.path.insert(0, _BAZI_PATH)

try:
    from bazi_calc_v2 import DIZHI_CANGGAN as _DC
    DIZHI_CANGGAN = _DC
except ImportError:
    DIZHI_CANGGAN = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
        "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
        "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
        "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
    }

# ============================================================
# 1. 考刻系统
# ============================================================

# 一个时辰 = 8刻（每刻2.5分钟）
# 铁板考刻：通过六亲事实反推"时刻偏差"，再校准命运判断

SHICHEN_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def get_shichen_index(hour: int, minute: int = 0) -> int:
    """获取时辰索引（0=子, 1=丑, ... 11=亥）"""
    if hour == 23:
        return 0  # 子时
    return (hour + 1) // 2

def get_ke_index(hour: int, minute: int) -> int:
    """
    考刻：确定在某时辰的第几刻
    
    Args:
        hour: 小时 (0-23)
        minute: 分钟 (0-59)
    
    Returns:
        刻数 (0-7), -1表示跨时辰边界
    """
    # 每个时辰15分钟×4刻+15分钟×4刻 = 2小时
    # 子时: 23:00-00:59, 丑时: 01:00-02:59, ...
    
    if hour == 23:
        base_minutes = 23 * 60 + minute
        # 子时从 23:00 = 1380分钟
        ke_offset = base_minutes - 1380
        if ke_offset < 0 or ke_offset >= 120:
            return -1
        return min(ke_offset // 15, 7)
    
    shichen = (hour + 1) // 2
    start_minute = (shichen * 2) * 60 if shichen > 0 else 0
    if shichen == 0:
        start_minute = 0  # 0:00-0:59
    else:
        start_minute = shichen * 120 - 60
    
    total_minutes = hour * 60 + minute
    ke_offset = total_minutes - start_minute
    
    if ke_offset < 0 or ke_offset >= 120:
        return -1
    return min(ke_offset // 15, 7)

# 铁板考刻六亲规则（精简版 — 按刻数不同，六亲关系有微妙差异）
# 经典铁板的"刻分表"：不同刻数对应不同的父母生肖/排行等
# 我们这里简化为刻影响"时柱的精确度"和"六亲信息"的质量

KE_LIUQIN_MODIFIER = {
    0: {"parent_accuracy": "父母信息基线", "sibling_offset": 0, "note": "初刻出生，父母缘分较淡"},
    1: {"parent_accuracy": "父母信息较准", "sibling_offset": 1, "note": "二刻出生，与母缘分深"},
    2: {"parent_accuracy": "父母信息准确", "sibling_offset": -1, "note": "三刻出生，与父缘分深"},
    3: {"parent_accuracy": "父母信息偏差大", "sibling_offset": 2, "note": "四刻出生，兄弟姐妹关系复杂"},
    4: {"parent_accuracy": "父母信息较准", "sibling_offset": 0, "note": "五刻出生，父母双全"},
    5: {"parent_accuracy": "父母信息准确", "sibling_offset": 1, "note": "六刻出生，得父母助力"},
    6: {"parent_accuracy": "父母信息偏差大", "sibling_offset": -1, "note": "七刻出生，父母缘分薄"},
    7: {"parent_accuracy": "父母信息基线", "sibling_offset": -2, "note": "八刻出生，独立自主"},
}


def kao_ke(hour: int, minute: int = 0, 
           father_birth_year: Optional[int] = None,
           mother_birth_year: Optional[int] = None,
           sibling_count: Optional[int] = None) -> Dict:
    """
    铁板考刻运算
    
    Args:
        hour: 出生小时
        minute: 出生分钟
        father_birth_year: 父亲出生年（可选，用于交叉验证）
        mother_birth_year: 母亲出生年（可选）
        sibling_count: 兄弟姐妹数（可选）
    
    Returns:
        考刻分析结果
    """
    shichen_idx = get_shichen_index(hour, minute)
    shichen_name = SHICHEN_NAMES[shichen_idx]
    ke_idx = get_ke_index(hour, minute)
    
    result = {
        "时辰": shichen_name,
        "时辰序号": shichen_idx,
        "刻数": ke_idx,
        "刻描述": f"{['初','二','三','四','五','六','七','末'][ke_idx] if ke_idx >= 0 else '未知'}刻",
        "考刻信息": KE_LIUQIN_MODIFIER.get(ke_idx, {}),
    }
    
    # 如果有父/母/手足数据可以交叉验证
    if father_birth_year:
        result["父年"] = father_birth_year
    if mother_birth_year:
        result["母年"] = mother_birth_year
    if sibling_count is not None:
        result["兄弟姐妹数"] = sibling_count
    
    return result


# ============================================================
# 2. 铁板六亲定位
# ============================================================

# 六亲宫位（传统铁板规则）
LIUQIN_GONGWEI = {
    "年柱": "祖上/祖父母",
    "月柱": "父母/兄弟",
    "日支": "配偶",
    "时柱": "子女",
}

# 四柱对应的六亲十神（简化版）
# 年柱看祖上、月柱看父母手足、日支看配偶、时柱看子女
def analyze_liuqin(pillars: Dict[str, str], ri_zhu: str, gender: str = "男") -> Dict:
    """
    六亲分析（基于八字四柱）
    
    Args:
        pillars: {"年柱":"庚午","月柱":"丁亥","日柱":"己卯","时柱":"己巳"}
        ri_zhu: 日主天干 "己"
        gender: "男"|"女"
    
    Returns:
        六亲分析
    """
    gan_list = [p[0] for p in pillars.values()]
    zhi_list = [p[1] for p in pillars.values()]
    positions = ["年柱", "月柱", "日柱", "时柱"]
    
    # 定位十神-六亲关系
    # 以日主为中心：正印=母, 偏印=继母/伯母, 正官=夫(女)/女(男), 七杀=父(男)/夫(女)
    # 这个需日主五行
    ri_wx = get_wuxing_index(ri_zhu)
    
    liuqin_info = {}
    for pos, gan, zhi in zip(positions, gan_list, zhi_list):
        gan_wx = get_wuxing_index(gan)
        shen = get_shishen(ri_wx, gan_wx, gan)
        
        gongwei = LIUQIN_GONGWEI.get(pos, "")
        liuqin_info[pos] = {
            "干支": f"{gan}{zhi}",
            "天干十神": shen,
            "宫位主": gongwei,
            "吉凶": "吉" if shen in ["正印","正官","正财","食神"] else "凶",
        }
    
    return liuqin_info


# ============================================================
# 3. 数理卦 — 铁板"数→卦→命运"转化
# ============================================================

def bazi_to_number(pillars: Dict[str, str]) -> Dict:
    """
    将八字转化为"铁板数"
    方法：将干支转换为数字（甲=1, 乙=2, ... 癸=10; 子=1, 丑=2, ... 亥=12）
    然后相加取余，映射到卦数
    
    这不是原始铁板的6000暗码！
    但保持了"将干支转化为数"的核心方法。
    """
    gan_map = {g: i+1 for i, g in enumerate(["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"])}
    zhi_map = {g: i+1 for i, g in enumerate(["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"])}
    
    numbers = {}
    total = 0
    for pos, gz in pillars.items():
        gan, zhi = gz[0], gz[1]
        gan_num = gan_map.get(gan, 5)
        zhi_num = zhi_map.get(zhi, 6)
        pair_num = gan_num * 12 + zhi_num
        numbers[pos] = {
            "天干数": gan_num,
            "地支数": zhi_num,
            "组合数": pair_num,
        }
        total += pair_num
    
    # 归元和卦
    gua_index = total % 64
    return {
        "四柱数": numbers,
        "总数": total,
        "归元卦数": gua_index,
        "归元卦": GUA_NAMES[gua_index] if gua_index < len(GUA_NAMES) else "未知",
    }


GUA_NAMES = [
    "乾为天", "坤为地", "水雷屯", "山水蒙",
    "水天需", "天水讼", "地水师", "水地比",
    "风天小畜", "天泽履", "地天泰", "天地否",
    "天火同人", "大有", "地山谦", "雷地豫",
    "泽雷随", "山风蛊", "地泽临", "风地观",
    "火雷噬嗑", "山火贲", "山地剥", "地雷复",
    "天雷无妄", "山天大畜", "山雷颐", "泽风大过",
    "坎为水", "离为火", "泽山咸", "雷风恒",
    "天山遁", "雷天大壮", "火地晋", "地火明夷",
    "风火家人", "火泽睽", "水山蹇", "雷水解",
    "山泽损", "风雷益", "泽天夬", "天风姤",
    "泽地萃", "地风升", "泽水困", "水风井",
    "泽火革", "火风鼎", "震为雷", "艮为山",
    "风山渐", "雷泽归妹", "雷火丰", "火山旅",
    "巽为风", "兑为泽", "风水涣", "水泽节",
    "风火中孚", "雷山小过", "水火既济", "火水未济",
]


# ============================================================
# 4. 铁板"逻辑条文"生成器
# ============================================================

def generate_iron_plate_items(bazi_str: str, ri_zhu: str, yong_shen: str, ji_shen: str,
                                pillars: Dict[str, str], gender: str = "男",
                                hour: int = 12, minute: int = 0) -> List[str]:
    """
    生成类铁板条文的"逻辑断定"
    
    真正的铁板有6000条，每条如：
    "父年生肖在寅，母年生肖在申"
    "兄弟四人，内有一人不同胞"
    
    我们这里用逻辑推理生成类似的"断语"。
    """
    items = []
    
    # 考刻
    ke_info = kao_ke(hour, minute)
    items.append(f"【考刻】生于{ke_info['时辰']}时{ke_info['刻描述']}。{ke_info['考刻信息']['note']}")
    
    # 六亲
    liuqin = analyze_liuqin(pillars, ri_zhu, gender)
    for pos, info in liuqin.items():
        items.append(f"【{pos}】宫位主{info['宫位主']}，天干{info['天干十神']}，{info['吉凶']}象")
    
    # 数理
    numbers = bazi_to_number(pillars)
    items.append(f"【数理】四柱总数{numbers['总数']}，归元卦{numbers['归元卦']}")
    
    # 铁板断语（基于组合分析）
    gans = [p[0] for p in pillars.values()]
    zhis = [p[1] for p in pillars.values()]
    
    # 从藏干判断兄弟姐妹（简化版铁板逻辑）
    total_hidden = sum(len(DIZHI_CANGGAN.get(z, [])) for z in zhis)
    choices = ["示手足缘薄","示手足缘浅","示手足缘平","示手足缘厚","示手足缘旺"]
    idx = min(total_hidden, 4)
    items.append(f"【手足】四柱藏干共{total_hidden}字，暗{choices[idx]}")
    
    # 从日支断婚姻
    ri_zhi = zhis[2] if len(zhis) > 2 else "?"
    _DW = ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"]
    ri_zhi_idx = int(zhis[2]) if zhis[2].isdigit() else ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"].index(zhis[2]) if zhis[2] in "子丑寅卯辰巳午未申酉戌亥" else 2
    ri_zhi_wx = _DW[ri_zhi_idx]
    items.append(f"【婚姻】日坐{ri_zhi}({ri_zhi_wx})，{'配偶稳重务实' if ri_zhi_wx=='土' else '配偶机变灵动' if ri_zhi_wx=='水' else '配偶热情主动' if ri_zhi_wx=='火' else '配偶正直刚强' if ri_zhi_wx=='金' else '配偶温文尔雅'}")
    
    # 从年柱断祖上
    nian_gan = gans[0] if len(gans) > 0 else "?"
    nian_zhi = zhis[0] if len(zhis) > 0 else "?"
    items.append(f"【祖上】年柱{nian_gan}{nian_zhi}，{DIZHI_BASE_IMAGE.get(nian_zhi,{}).get('images',[''])} 祖业{['丰厚','中等','薄弱'][hash(nian_zhi)%3]}")
    
    # 用神命理
    items.append(f"【用神】宜{ji_shen}方发展事业")
    if yong_shen:
        items.append(f"【命格】{'富格' if yong_shen in ['金','水'] else '贵格' if yong_shen in ['火','土'] else '才格' if yong_shen=='木' else '清格'}")
    
    # 加一条铁板风的诗诀
    items.append(f"【总诀】《铁板诀》：{ri_zhu}日生人，{liuqin.get('月柱',{}).get('天干十神','')}为用，一生{['波澜壮阔','稳步上升','先难后易','先顺后逆'][hash(bazi_str)%4]}。")
    
    return items


# ============================================================
# 实用函数
# ============================================================

WUXING_MAP = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

WUXING_LIST = ["木", "火", "土", "金", "水"]

def get_wuxing_index(gan: str) -> int:
    """获取天干的五行索引（0木1火2土3金4水）"""
    wx = WUXING_MAP.get(gan, "土")
    return WUXING_LIST.index(wx)

def get_shishen(ri_wx_idx: int, gan_wx_idx: int, gan: str) -> str:
    """
    十神关系判定（日主vs天干）
    """
    # 同五行
    if ri_wx_idx == gan_wx_idx:
        idx = TIANGAN.index(gan) if gan in TIANGAN else 0
        return "比肩" if idx % 2 == 0 else "劫财"
    
    diff = (gan_wx_idx - ri_wx_idx) % 5
    idx = TIANGAN.index(gan) if gan in TIANGAN else 0
    yin_yang = idx % 2
    
    shen_map = {
        1: ("食神", "傷官"),   # 我生
        2: ("偏財", "正財"),   # 我克
        3: ("七殺", "正官"),   # 克我
        4: ("偏印", "正印"),   # 生我
    }
    
    if diff in shen_map:
        pair = shen_map[diff]
        return pair[0] if yin_yang == 0 else pair[1]
    return "?"


TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

DIZHI_BASE_IMAGE = {
    "子": {"images": ["水池","沟渠","暗流"], "生肖": "鼠"},
    "丑": {"images": ["泥泞","牛","仓库"], "生肖": "牛"},
    "寅": {"images": ["虎","山林","权力"], "生肖": "虎"},
    "卯": {"images": ["兔","花","门户"], "生肖": "兔"},
    "辰": {"images": ["龙","水库","文明"], "生肖": "龙"},
    "巳": {"images": ["蛇","火炉","变化"], "生肖": "蛇"},
    "午": {"images": ["马","太阳","权力"], "生肖": "马"},
    "未": {"images": ["羊","花园","酒窖"], "生肖": "羊"},
    "申": {"images": ["猴","刀剑","道路"], "生肖": "猴"},
    "酉": {"images": ["鸡","金银","精美"], "生肖": "鸡"},
    "戌": {"images": ["狗","火库","城郭"], "生肖": "狗"},
    "亥": {"images": ["猪","江河","深邃"], "生肖": "猪"},
}

def iron_plate_report(bazi_str: str, ri_zhu: str, yong_shen: str, ji_shen: str,
                        pillars: Dict[str, str], gender: str = "男",
                        hour: int = 12, minute: int = 0) -> str:
    """
    输出铁板神数考刻报告
    """
    items = generate_iron_plate_items(bazi_str, ri_zhu, yong_shen, ji_shen, 
                                       pillars, gender, hour, minute)
    
    lines = [
        "═══ 铁板神数 · 考刻断语 ═══",
        f"八字: {bazi_str}",
        f"性别: {gender}",
        "",
        *items,
        "",
        "【铁板按】",
        "  以上断语采用铁板神数之考刻、六亲、数理三大原理,",
        "  以现代八字推理补原6000暗码之缺。",
        "  仅供决策参考，不替代专业建议。",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # 丘总八字测试
    bazi = "庚午 丁亥 己卯 己巳"
    pillars = {"年柱": "庚午", "月柱": "丁亥", "日柱": "己卯", "时柱": "己巳"}
    print(iron_plate_report(bazi, "己", "火", "水", pillars, "男", 10, 0))
    print()
    print("═══ 考刻详情 ═══")
    print(kao_ke(10, 0))
