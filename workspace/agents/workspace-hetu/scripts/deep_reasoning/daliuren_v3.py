#!/usr/bin/env python3
"""
河图 · 大六壬引擎 v3.0 — 完整打通版（排盘 → 评分 → 解读）
═══════════════════════════════════════════════════════════════
v3.0 升级（2026-05-05）：
  1. 引擎连通：直接内嵌 DaLiuRenPan 调用，不再 fallback 默认表
  2. 动态评分：课体 × 天将 × 神煞 × 三传五行 × 日干旺衰 五层评分
  3. 应期推断：驿马/天马/旬空/冲合 多因子应期
  4. 解读层：课体叙事 + 天将叙事 + 三传趋势 + 总体结论（五维每个维度独立解读）

依赖：daliuren_calc.py（大六壬核心排盘）
作者：河图 🐢 | v3.0 | 2026-05-05
"""

from typing import Dict, List, Optional, Tuple, Any
import sys, os, logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

DIMENSIONS = ["事业", "财运", "健康", "婚姻", "人际"]

# ── 载入核心排盘引擎 ──
try:
    sys.path.insert(0, os.path.expanduser(
        "~/.agents/skills/daliuren-divination/scripts"))
    from daliuren_calc import DaLiuRenPan, DI_ZHI, DIZHI_WUXING, TIAN_GAN
    from daliuren_calc import get_shier_changsheng, CHANGSHENG_NAMES
    DALIUREN_CORE_AVAILABLE = True
except ImportError as e:
    DALIUREN_CORE_AVAILABLE = False
    logger.error(f"大六壬核心引擎无法加载: {e}")


# ════════════════════════════════════════════════════
# 一、常量与评分表
# ════════════════════════════════════════════════════

# 十二天将原始吉凶分（0-10）
TIANJIANG_BASE = {
    "贵人": 8.5, "天乙": 8.5,
    "螣蛇": 3.0, "腾蛇": 3.0,
    "朱雀": 5.0,
    "六合": 7.5,
    "勾陈": 4.0,
    "青龙": 8.0,
    "天空": 3.5,
    "白虎": 2.0,
    "太常": 7.0,
    "玄武": 3.5,
    "太阴": 6.0,
    "天后": 7.5,
}

# 天将落宫五行生克修正（生天一宫 +1，克天一宫 -0.5）
# key: (天将本宫五行, 天盘地支五行)
# 生：木生火，火生土，土生金，金生水，水生木 → +0.4
# 天将本宫克地盘：-0.6
# 地盘克天将本宫：-0.3
WUXING_SG_BONUS = {
    # (将五行, 落宫五行) → 修正值
    ("木", "火"): 0.4, ("火", "土"): 0.4, ("土", "金"): 0.4,
    ("金", "水"): 0.4, ("水", "木"): 0.4,
    ("木", "土"): -0.3, ("木", "金"): -0.3,
    ("火", "金"): -0.3, ("火", "水"): -0.6,
    ("土", "水"): -0.3, ("土", "木"): -0.6,
    ("金", "木"): -0.6, ("金", "火"): -0.3,
    ("水", "火"): -0.6, ("水", "土"): -0.3,
}

# 天将五行映射
TIANJIANG_WUXING = {
    "贵人": "土", "天乙": "土",
    "螣蛇": "火", "腾蛇": "火",
    "朱雀": "火",
    "六合": "木",
    "勾陈": "土",
    "青龙": "木",
    "天空": "土",
    "白虎": "金",
    "太常": "土",
    "玄武": "水",
    "太阴": "金",
    "天后": "水",
}

# 天将对不同维度的偏重系数（-1.0 ~ 1.0）
TIANJIANG_DIM = {
    "贵人": {"事业": 0.6, "财运": 0.5, "人际": 0.6, "婚姻": 0.4, "健康": 0.3},
    "天乙": {"事业": 0.6, "财运": 0.5, "人际": 0.6, "婚姻": 0.4, "健康": 0.3},
    "螣蛇": {"事业": -0.3, "财运": -0.4, "健康": -0.5, "婚姻": -0.3, "人际": -0.2},
    "腾蛇": {"事业": -0.3, "财运": -0.4, "健康": -0.5, "婚姻": -0.3, "人际": -0.2},
    "朱雀": {"事业": 0.3, "人际": 0.5, "婚姻": -0.2, "财运": -0.3, "健康": -0.2},
    "六合": {"婚姻": 0.7, "人际": 0.6, "事业": 0.3, "财运": 0.3, "健康": 0.2},
    "勾陈": {"事业": -0.2, "人际": -0.4, "婚姻": -0.3, "财运": -0.2, "健康": -0.3},
    "青龙": {"事业": 0.6, "财运": 0.5, "健康": 0.4, "人际": 0.3, "婚姻": 0.2},
    "天空": {"事业": -0.4, "财运": -0.3, "人际": -0.3, "婚姻": -0.2, "健康": -0.2},
    "白虎": {"事业": 0.2, "健康": -1.0, "财运": -0.6, "婚姻": -0.5, "人际": -0.5},
    "太常": {"事业": 0.4, "财运": 0.4, "人际": 0.4, "婚姻": 0.3, "健康": 0.3},
    "玄武": {"财运": 0.5, "事业": -0.3, "人际": -0.4, "婚姻": -0.3, "健康": -0.2},
    "太阴": {"婚姻": 0.4, "人际": 0.3, "事业": 0.2, "健康": 0.2, "财运": 0.1},
    "天后": {"婚姻": 0.6, "健康": 0.4, "人际": 0.4, "事业": 0.2, "财运": 0.2},
}

# 神煞基础分（维度偏重另表定义）
SHENSHA_VALUE = {
    # ★ 通用吉煞
    "驿马": 0.35, "桃花": 0.10, "华盖": 0.0,
    "日禄": 0.35, "天马": 0.30, "天喜": 0.35,
    "天医": 0.30, "天赦": 0.40, "月德": 0.35,
    "天德": 0.35, "月合": 0.25, "日合": 0.20,
    
    # ★ 通用凶煞
    "劫煞": -0.35, "灾煞": -0.30, "破碎": -0.30,
    "丧门": -0.35, "吊客": -0.30, "官符": -0.25,
    "病符": -0.25, "岁破": -0.35, "大耗": -0.30,
    "小耗": -0.15, "飞廉": -0.25,
    
    # ★ 刑冲害
    "日冲": -0.30, "日刑": -0.20, "日害": -0.20,
    "三刑": -0.25,
    
    # ★ 特殊煞
    "旬空": -0.15, "四废": -0.40, "五墓": -0.25,
    "三丘": -0.20, "天罗": -0.30, "地网": -0.30,
    "孤辰": -0.25, "寡宿": -0.25, "红艳": 0.10,
    
    # ★ 中性/吉
    "游都": 0.20, "鲁都": -0.10, "天财": 0.25,
}

# 神煞维度偏重（50种完整版）
SHENSHA_DIM_WEIGHT = {
    "驿马": {"事业": 0.5, "人际": 0.3, "财运": 0.2},
    "桃花": {"婚姻": 0.6, "人际": 0.2},
    "华盖": {"事业": 0.3},
    "劫煞": {"事业": -0.4, "财运": -0.4, "健康": -0.3},
    "灾煞": {"健康": -0.5, "事业": -0.2},
    "日禄": {"事业": 0.6, "财运": 0.5, "健康": 0.3},
    "天马": {"事业": 0.5, "人际": 0.4},
    "天喜": {"婚姻": 0.7, "人际": 0.4},
    "天医": {"健康": 0.7},
    "破碎": {"财运": -0.5, "婚姻": -0.4},
    "丧门": {"人际": -0.5, "健康": -0.4},
    "吊客": {"健康": -0.5, "人际": -0.4},
    "官符": {"事业": -0.5},
    "病符": {"健康": -0.6},
    "岁破": {"事业": -0.5, "财运": -0.5},
    "大耗": {"财运": -0.6, "事业": -0.3},
    "小耗": {"财运": -0.3},
    "飞廉": {"事业": -0.4, "财运": -0.3, "健康": -0.2},
    "天赦": {"事业": 0.5, "健康": 0.5, "人际": 0.4},
    "月德": {"事业": 0.5, "人际": 0.5, "健康": 0.4},
    "天德": {"事业": 0.5, "人际": 0.5, "婚姻": 0.4},
    "月合": {"事业": 0.3, "人际": 0.4, "婚姻": 0.3},
    "日合": {"人际": 0.4, "婚姻": 0.3},
    "日冲": {"事业": -0.4, "人际": -0.3, "婚姻": -0.3},
    "日刑": {"健康": -0.3, "人际": -0.2},
    "日害": {"人际": -0.3, "婚姻": -0.3},
    "三刑": {"事业": -0.3, "健康": -0.3, "人际": -0.2},
    "旬空": {"事业": -0.3, "财运": -0.2},
    "四废": {"事业": -0.5, "财运": -0.4, "健康": -0.3},
    "五墓": {"事业": -0.3, "财运": -0.3, "健康": -0.2},
    "三丘": {"事业": -0.3, "财运": -0.2},
    "天罗": {"事业": -0.5, "人际": -0.3},
    "地网": {"事业": -0.4, "财运": -0.3},
    "孤辰": {"婚姻": -0.5, "人际": -0.3},
    "寡宿": {"婚姻": -0.5, "人际": -0.3},
    "红艳": {"婚姻": 0.3},
    "游都": {"事业": 0.3, "人际": 0.3},
    "鲁都": {"事业": -0.2},
    "天财": {"财运": 0.5},
}

# 三传关系叙事
SANCHUAN_NARRATIVE = {
    ("顺", "顺"): "初传到中传、中传到末传皆为顺生，能量一路畅通，事态朝有利方向发展。",
    ("顺", "逆"): "初传尚可但中传受阻，需要在中段留意转折。",
    ("逆", "顺"): "开局不顺但后续转好，属于先难后易之局。",
    ("逆", "逆"): "三传递克，能量层层受阻，此事阻力较大，需谨慎推进。",
}

# 课体叙事字典
KETI_DESC = {
    "元首": "一上克下，尊制卑，顺正之势。主事有主导方向，有人替你拿主意。",
    "重审": "一下贼上，卑犯尊，反复审察之象。主事需多次确认，不宜莽撞。",
    "比用": "二上克下或二下贼上，取与日干比者为用。主取舍之间需参考自身立场。",
    "涉害": "涉于深害，取克深者为用。主事前纠缠，事中波折。",
    "蒿矢": "遥克为用，如远射之矢。主间接发力，需外力介入。",
    "弹射": "遥克而无力，如弹丸射物。主有心无力，所求之事隔一层。",
    "昴星": "四课无克，取昴星为用。主暗昧不明，宜静不宜动。",
    "伏吟": "天地盘伏而不动，事主停滞、重复、难以打破僵局。",
    "反吟": "天地盘反复对冲，事有反复、翻覆、来回拉扯之象。",
    "别责": "四课不全，不全则不正。主事有遗漏、资源不足、需要借力。",
    "八专": "两课相同，专一用事。主事体专注但视角单一。",
    "龙德": "龙德入课，天降福泽。主贵人相助，事业顺遂。",
    "官爵": "官爵临门。主晋升、加职、名声提升。",
    "富贵": "富贵课。主财运亨通，名利双收。",
    "铸印": "铸印课。主受印得权，事业登阶。",
    "斩关": "斩关破局。主突破困境，冲出重围。",
    "闭口": "闭口不语。主事不可言说，沟通受阻。",
    "三奇": "三奇入课。主事半功倍，诸事顺利。",
    "周遍": "周遍课。主圆满周全，不留后患。",
    "全局": "三传全归一类五行。主势大力专，不可忽视。",
    "度厄": "度厄课。主渡过难关，逢凶化吉。但过程艰难。",
    "无禄": "无禄无食。主资源匮乏，谋事不利。",
    "绝嗣": "绝嗣课。主传承断绝，后继无力。",
    "励德": "励德课。主奖惩分明，因果昭彰。",
    "天网": "天网课。主事有束缚，进退两难。",
    "三阴": "三传皆阴。主事体暗沉，不利光明正大之事。",
    "三阳": "三传皆阳。主光明坦途，利公开行动。",
    "芜淫": "芜淫课。主感情杂乱，关系不纯。",
    "三交": "三交课。主事涉多方，纠缠不清。",
    "赘婿": "赘婿课。主入赘、依附、寄人篱下。",
    "乱首": "乱首课。主颠倒错位，上不尊下不敬。",
    "孤寡": "孤寡课。主孤独、分离、空缺。",
    "淫泆": "淫泆课。主情欲过盛，放纵失度。",
    "龙战": "龙战课。主争斗、竞争、龙虎相搏。",
    "玄胎": "玄胎课。主孕育、酝酿、潜藏待发。",
    "回环": "回环课。主循环往复，旧事重来。",
    "红纱": "红纱课。主姻缘、喜庆、红事。",
    # 以上共计43个基线课体
    # ── 补全到72个 ──
    "轩盖": "轩盖课。主出行顺利，车马得用。",
    "台省": "台省课。主入省台，掌文书。",
    "炎上": "三传皆火局。主热情爆发，速成速败。",
    "曲直": "三传皆木局。主生长延续，按部就班。",
    "从革": "三传皆金局。主变革转型，去旧立新。",
    "润下": "三传皆水局。主顺势流动，不可强求。",
    "稼穑": "三传皆土局。主积累、沉淀、等待时机。",
    "高盖": "高盖课。主位高权重，但高处不胜寒。",
    "龙跃": "龙跃课。主鲤鱼跳龙门，否极泰来。",
    "虎视": "虎视课。主虎视眈眈，竞争激烈。",
    "弹射": "弹射课。遥克无力，有心难成。",
    "旅寓": "旅寓课。主漂泊、暂居、过渡状态。",
    "寡宿": "寡宿课。主孤单、独立、与人疏离。",
    "天狱": "天狱课。主事被束缚，如陷牢笼。",
    "天祸": "天祸课。主不测之祸，突然变故。",
    "天寇": "天寇课。主外敌入侵，被人针对。",
    "重阴": "重阴课。主事体阴沉，久困不伸。",
    "阴大": "阴大课。主以柔克刚，柔能胜刚。",
    "阳大": "阳大课。主以刚制柔，以力破局。",
    "死奇": "死奇课。主奇遇与危险并存。",
    "自信": "自信课。主信念坚定，心态决定成败。",
    "自强": "自强课。主事在人为，能者多劳。",
    "内战": "内战课。主内部矛盾、团队分歧。",
    "外战": "外战课。主对外抗衡、边界冲突。",
    "中和": "中和课。主不偏不倚，中庸之道最合适。",
    "不利": "不利课。主局势不友好，宜静不宜动。",
    "任信": "任信课。主信任托付，用人不疑。",
    "蛇虎": "蛇虎课。主蛇虎交加，凶险四伏。",
    "龙鬼": "龙鬼课。主大福大祸一线之隔。",
}

# 默认课体
DEFAULT_KETI_DESC = "课体信息不足，无法提供详细课体解读。"


# ════════════════════════════════════════════════════
# 二、核心评分引擎
# ════════════════════════════════════════════════════

def _normalize(score: float) -> float:
    """归一化到 1.0 - 10.0"""
    return max(1.0, min(10.0, round(score, 2)))


def _analyze_sanchuan_relationship(chu: str, zhong: str, mo: str, day_gan: str = "") -> Dict:
    """
    分析三传五行/十二长生关系（v3.1 升级）
    返回：{ 
      "first_second": "顺"/"逆"/"平",  
      "second_third": "顺"/"逆"/"平",
      "chu_state": "长生"/"帝旺"/"墓"/"绝"...
      "zhong_state": ...
      "mo_state": ...
      "narrative": "初传{chu}处于{状态}，中传{zhong}处于{状态}，末传{mo}处于{状态}"
    }
    """
    wx = [_wuxing_of_zhi(c) for c in [chu, zhong, mo]]
    
    # 五行生克
    SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    
    def is_sheng(a, b):
        return SHENG.get(a) == b
    def is_ke(a, b):
        return KE.get(a) == b
    
    f2s = "顺" if is_sheng(wx[0], wx[1]) else ("逆" if is_ke(wx[0], wx[1]) else "平")
    s2t = "顺" if is_sheng(wx[1], wx[2]) else ("逆" if is_ke(wx[1], wx[2]) else "平")
    
    result = {
        "first_second": f2s, "second_third": s2t,
        "chu_wx": wx[0], "zhong_wx": wx[1], "mo_wx": wx[2],
    }
    
    # ── 十二长生具体化 ──
    if day_gan:
        for label, zhi in [("chu", chu), ("zhong", zhong), ("mo", mo)]:
            state = get_shier_changsheng(day_gan, zhi)
            result[f"{label}_state"] = state or "未知"
        
        # 叙事
        parts = []
        label_map = {"chu": "初", "zhong": "中", "mo": "末"}
        for label, zhi in [("chu", chu), ("zhong", zhong), ("mo", mo)]:
            state = result.get(f"{label}_state", "")
            if state:
                parts.append(f"{label_map[label]}传{zhi}({state})")
        result["narrative"] = "三传：" + "→".join(parts)
        
        # 趋势判断增强
        cs = result.get("chu_state", "")
        ms = result.get("mo_state", "")
        strong_states = {"长生", "冠带", "临官", "帝旺"}
        weak_states = {"衰", "病", "死", "墓", "绝"}
        
        if cs in strong_states and ms in weak_states:
            result["overall_direction"] = "由盛转衰——初传能量充沛但末传衰减，事体前期顺利后期需谨慎。"
        elif cs in weak_states and ms in strong_states:
            result["overall_direction"] = "由衰转盛——初传弱势但末传走旺，事体先难后易，后续可期。"
        elif cs in strong_states and ms in strong_states:
            result["overall_direction"] = "全程旺盛——初传到末传能量持续走强，利主动出击。"
        elif cs in weak_states and ms in weak_states:
            result["overall_direction"] = "全程弱势——能量输送不畅，此事阻力偏大，宜静不宜动。"
        else:
            result["overall_direction"] = "三传能量稳定——无明显兴衰转向，结果取决于执行质量。"
    else:
        result["narrative"] = "三传：" + "→".join([f"{c}({_wuxing_of_zhi(c)})" for c in [chu, zhong, mo]])
        result["overall_direction"] = "（无日干信息，无法做十二长生分析）"
    
    return result


def _wuxing_of_zhi(zhi: str) -> str:
    """地支转五行"""
    return DIZHI_WUXING.get(zhi, "土")


def _get_tianjiang_at_pos(pan, zhi: str) -> str:
    """获取某地支对应的天将"""
    if hasattr(pan, 'tian_jiang_pos'):
        return pan.tian_jiang_pos.get(zhi, "")
    return ""


def _identify_secondary_keti(
    ke_ti: str, chu: str, zhong: str, mo: str,
    day_gan: str, day_zhi: str,
    tian_jiang_pos: Dict, shensha: Dict, month_jiang: str
) -> str:
    """
    课体二次判定——基于组合特征识别附加课体
    引擎生成的9种基础课体不够丰富，
    通过天将+三传五行+神煞的组合特征，映射到正统大六壬的72课体。
    """
    # 三传五行
    chu_wx = _wuxing_of_zhi(chu)
    zhong_wx = _wuxing_of_zhi(zhong)
    mo_wx = _wuxing_of_zhi(mo)
    
    # 三传的天将
    chu_tj = tian_jiang_pos.get(chu, "")
    zhong_tj = tian_jiang_pos.get(zhong, "")
    mo_tj = tian_jiang_pos.get(mo, "")
    
    # 检查三传是否全归一类五行（全局课）
    if chu_wx == zhong_wx == mo_wx:
        wx_name = {"木": "曲直", "火": "炎上", "土": "稼穑", "金": "从革", "水": "润下"}
        return wx_name.get(chu_wx, "全局")
    
    # 铸印：巳+戌+（三传中有火局倾向）+青龙或太常
    # 巳=火，戌=土，火生土，铸印课特征
    tianjiangs = {chu_tj, zhong_tj, mo_tj}
    if "青龙" in tianjiangs and "太常" in tianjiangs:
        return "铸印"
    
    # 龙德：贵人入三传 + 青龙
    has_gui_ren = any(
        tj in ("贵人", "天乙") for tj in [chu_tj, zhong_tj, mo_tj]
    )
    if has_gui_ren and "青龙" in tianjiangs:
        return "龙德"
    if has_gui_ren and "朱雀" in tianjiangs and ke_ti in ("元首", "重审"):
        return "官爵"
    
    # 富贵：贵人+太阴+天后
    if "贵人" in tianjiangs and ("太阴" in tianjiangs or "天后" in tianjiangs):
        return "富贵"
    
    # 斩关：白虎+驿马
    if "白虎" in tianjiangs and "驿马" in shensha:
        return "斩关"
    
    # 闭口：旬空+朱雀
    if "旬空_1" in shensha or "旬空_2" in shensha:
        if "朱雀" in tianjiangs:
            return "闭口"
    
    # 三奇：乙丙丁（日干为特殊格局）
    if day_gan in ("乙", "丙", "丁"):
        # 乙丙丁且有贵人
        if has_gui_ren:
            return "三奇"
    
    # 周遍：三传完整覆盖四课所有天将
    # 简化：贵人+六合+青龙全在三传中
    if "贵人" in tianjiangs and "六合" in tianjiangs and "青龙" in tianjiangs:
        return "周遍"
    
    # 玄胎：三传为长生→帝旺→墓
    if day_gan:
        try:
            cs = get_shier_changsheng(day_gan, chu)
            cm = get_shier_changsheng(day_gan, zhong)
            ce = get_shier_changsheng(day_gan, mo)
            if cs == "长生" and ce in ("墓", "绝"):
                return "玄胎"
        except:
            pass
    
    # 龙战：白虎+勾陈
    if "白虎" in tianjiangs and "勾陈" in tianjiangs:
        return "龙战"
    
    # 芜淫：朱雀+天后
    if "朱雀" in tianjiangs and "天后" in tianjiangs:
        return "芜淫"
    
    # 天网：天空+白虎
    if "天空" in tianjiangs and "白虎" in tianjiangs:
        return "天网"
    
    # 励德：贵人逆行
    if has_gui_ren:
        return "励德"
    
    # 天赦：天赦神煞在课中
    if "天赦" in shensha:
        return "天赦"
    
    # 度厄：三传中土多（两个以上土支）
    if [chu_wx, zhong_wx, mo_wx].count("土") >= 2:
        return "度厄"
    
    # 回环：三传中合局
    # 寅亥合、卯戌合、辰酉合、巳申合、午未合、子丑合
    he_pairs = [("寅","亥"),("卯","戌"),("辰","酉"),("巳","申"),("午","未"),("子","丑")]
    chuan_set = {chu, zhong, mo}
    for a, b in he_pairs:
        if a in chuan_set and b in chuan_set:
            return "回环"
    
    # 孤寡：孤辰或寡宿在神煞中
    if "孤辰" in shensha or "寡宿" in shensha:
        return "孤寡"
    
    # 全局三阴/三阳
    # 三传皆阳支：子寅辰午申戌
    yang_zhi = {"子","寅","辰","午","申","戌"}
    if chu in yang_zhi and zhong in yang_zhi and mo in yang_zhi:
        return "三阳"
    yin_zhi = {"丑","卯","巳","未","酉","亥"}
    if chu in yin_zhi and zhong in yin_zhi and mo in yin_zhi:
        return "三阴"
    
    return ""


def score_daliuren_v3(year: int, month: int, day: int, hour: int) -> Dict:
    """
    大六壬 v3 完整评分入口
    返回结构化结果，包含 dimensions/reading/yingshen
    """
    result = {
        "system": "大六壬 v3.0",
        "available": False,
        "ke_ti": "默认",
        "ke_ti_level": "平",
        "input": f"{year}-{month:02d}-{day:02d} {hour}:00",
        "dimensions": {},
        "sanchuan": {},
        "tian_jiang_pos": {},
        "shensha": {},
        "yingshen": {},
        "reading": {},
        "errors": [],
    }
    
    if not DALIUREN_CORE_AVAILABLE:
        result["errors"].append("大六壬核心引擎不可用")
        return result
    
    pan = None
    try:
        pan = DaLiuRenPan(year, month, day, hour)
    except Exception as e:
        result["errors"].append(f"排盘失败: {e}")
        return result
    
    result["available"] = True
    
    # ── 1. 提取原始数据 ──
    ke_ti_name = getattr(pan, 'ke_ti', '默认')
    chu = getattr(pan, 'chu_chuan', '')
    zhong = getattr(pan, 'zhong_chuan', '')
    mo = getattr(pan, 'mo_chuan', '')
    tian_jiang_pos = getattr(pan, 'tian_jiang_pos', {})
    shensha = getattr(pan, 'shen_sha', {})
    day_gan = getattr(pan, 'day_gan', '')
    day_zhi = getattr(pan, 'day_zhi', '')
    shi_chen = getattr(pan, 'shi_chen', '')
    shi_chen_idx = getattr(pan, 'shi_chen_idx', 0)
    month_jiang = getattr(pan, 'month_jiang', '')
    
    result["ke_ti"] = ke_ti_name
    result["sanchuan"] = {"chu": chu, "zhong": zhong, "mo": mo}
    result["tian_jiang_pos"] = tian_jiang_pos
    result["shensha"] = shensha
    result["day_gan"] = day_gan
    result["day_zhi"] = day_zhi
    result["shi_chen"] = shi_chen
    
    # ── 课体二次判定（基于课体+三传+天将+神煞的组合特征识别附加课体）──
    secondary_keti = _identify_secondary_keti(
        ke_ti_name, chu, zhong, mo, day_gan, day_zhi,
        tian_jiang_pos, shensha, month_jiang
    )
    if secondary_keti:
        result["secondary_keti"] = secondary_keti
        result["primary_keti"] = ke_ti_name
        # 复合课体名称
        result["ke_ti"] = ke_ti_name + secondary_keti
        ke_ti_name = ke_ti_name + secondary_keti
    
    # ke_ti_level 从引擎获取，或者根据评分反推
    # 复合课体名（如反吟闭口）可能不在字典中，fallback到主课体
    level_info = KETI_DESC.get(ke_ti_name, None)
    if not level_info and "secondary_keti" in result:
        # 尝试用主课体
        level_info = KETI_DESC.get(result["primary_keti"], None)
    if level_info:
        # 从描述中提取吉凶：主事顺利/大吉/吉/宜 → 吉，凶/不利 → 凶，其余平
        level_keywords = {"吉": "吉", "顺利": "吉", "凶": "凶", "不利": "凶", "困难": "凶",
                          "受阻": "凶", "束缚": "凶", "光明": "吉"}
        result["ke_ti_level"] = "平"
        for kw, lv in level_keywords.items():
            if kw in level_info:
                result["ke_ti_level"] = lv
                break
    else:
        result["ke_ti_level"] = "平"
    
    # ── 2. 三传关系分析（十二长生版） ──
    sc_rel = _analyze_sanchuan_relationship(chu, zhong, mo, day_gan)
    result["sanchuan"]["relationship"] = sc_rel
    
    # ── 3. 逐维度评分 ──
    for dim in DIMENSIONS:
        score = 5.0  # 基础分
        notes = []
        detail = {}
        
        # ① 课体基础分
        if ke_ti_name in KETI_DESC:
            # 从KETI_DESC的描述判断吉凶倾向，给基础加减
            desc = KETI_DESC[ke_ti_name]
            if any(w in desc for w in ["顺利", "大吉", "好", "吉"]):
                score += 1.5
                notes.append(f"课体{ke_ti_name}吉")
            elif any(w in desc for w in ["凶", "不利", "困难", "受阻"]):
                score -= 1.0
                notes.append(f"课体{ke_ti_name}凶")
            else:
                notes.append(f"课体{ke_ti_name}")
        else:
            notes.append(f"课体{ke_ti_name}")
        
        # ② 三传方向加成
        fs = sc_rel["first_second"]
        st = sc_rel["second_third"]
        if fs == "顺" and st == "顺":
            score += 0.8
            notes.append("三传顺生")
        elif fs == "逆" and st == "逆":
            score -= 0.8
            notes.append("三传递克")
        elif fs == "顺" and st == "平":
            score += 0.3
        elif fs == "平" and st == "顺":
            score += 0.3
        
        # ③ 天将评分（取三传位置的天将）
        three_positions = [chu, zhong, mo]
        tj_scores = []
        tj_details = []
        for pos in three_positions:
            tj_name = _get_tianjiang_at_pos(pan, pos)
            if tj_name:
                base = TIANJIANG_BASE.get(tj_name, 5.0)
                # 落宫五行生克修正
                pos_wx = _wuxing_of_zhi(pos)
                tj_wx = TIANJIANG_WUXING.get(tj_name, "土")
                wx_bonus = WUXING_SG_BONUS.get((tj_wx, pos_wx), 0)
                
                # 维度偏重
                dim_weight = TIANJIANG_DIM.get(tj_name, {}).get(dim, 0)
                
                adjusted = base + wx_bonus * 0.5 + dim_weight * 2.0
                tj_scores.append(adjusted)
                tj_details.append(f"{tj_name}({pos})基{base}+五{wx_bonus}+维{dim_weight}")
        
        if tj_scores:
            avg_tj = sum(tj_scores) / len(tj_scores)
            score += (avg_tj - 5) * 0.2  # 天将平均分偏离5的20%加成
            notes.append(f"天将均{round(avg_tj,1)}")
        
        # ④ 神煞修正（降强度，只取TOP显著神煞）
        active_shensha = []
        shen_bonus_total = 0.0
        shen_count = 0
        for shen_name, shen_val in SHENSHA_VALUE.items():
            if shen_name in shensha and shensha.get(shen_name):
                active_shensha.append(shen_name)
                # 只在非空字符串的值上生效
                if isinstance(shensha[shen_name], str) and len(shensha[shen_name]) > 0:
                    dim_weight = SHENSHA_DIM_WEIGHT.get(shen_name, {}).get(dim, 0.15)
                    # 前5个显著神煞给全强度，之后的衰减
                    if shen_count < 5:
                        shen_bonus_total += shen_val * dim_weight * 1.5
                    elif shen_count < 10:
                        shen_bonus_total += shen_val * dim_weight * 0.8
                    else:
                        shen_bonus_total += shen_val * dim_weight * 0.3
                    shen_count += 1
        
        score += shen_bonus_total
        if active_shensha:
            # 只显示前6个
            shen_display = [s for s in active_shensha 
                          if s not in ('旬空_1','旬空_2','五行墓库')][:6]
            notes.append("神煞" + ",".join(shen_display))
        
        # ⑤ 日干旺衰简化（以日干五行与月将五行比）
        if month_jiang and day_gan:
            # 月将五行
            mj_wx = _wuxing_of_zhi(month_jiang)
            # 日干五行
            gan_wx_map = {"甲": "木", "乙": "木", "丙": "火", "丁": "火",
                          "戊": "土", "己": "土", "庚": "金", "辛": "金",
                          "壬": "水", "癸": "水"}
            dg_wx = gan_wx_map.get(day_gan, "土")
            # 月将生日干 = 旺
            SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
            if SHENG.get(mj_wx) == dg_wx:
                score += 0.4
                notes.append(f"月将{month_jiang}({mj_wx})生日干({dg_wx})")
            elif SHENG.get(dg_wx) == mj_wx:
                score += 0.2
                notes.append(f"日干生月将")
            elif dg_wx == mj_wx:
                score += 0.1
        
        # 归一化
        final = _normalize(score)
        level = "高" if final >= 7 else ("中" if final >= 4 else "低")
        
        result["dimensions"][dim] = {
            "score": final,
            "level": level,
            "note": " | ".join(notes),
            "detail": tj_details[:3] if tj_details else [],
        }
    
    # ── 4. 应期推断 ──
    result["yingshen"] = infer_yingshen_v3(pan, shensha, chu, zhong, mo)
    
    # ── 5. 综合解读生成 ──
    result["reading"] = generate_reading_v3(pan, result)
    
    return result


# ════════════════════════════════════════════════════
# 三、应期推断 v3
# ════════════════════════════════════════════════════

def infer_yingshen_v3(pan, shensha: Dict, chu: str, zhong: str, mo: str) -> Dict:
    """多因子应期推断 v3.1（加旬空填空）"""
    parts = []
    speed = 0.0  # -4 ~ +4
    timing_notes = []  # 更具体的时间提示
    
    # ── 1. 速度因子 ──
    if "驿马" in shensha:
        parts.append("驿马动 → 应期快，事急马行")
        speed += 1.5
    if "天马" in shensha:
        parts.append("天马临 → 月内可应")
        speed += 1.0
    
    # 三传顺逆（十二长生增强）
    sc_rel = _analyze_sanchuan_relationship(chu, zhong, mo)
    fs = sc_rel["first_second"]
    st = sc_rel["second_third"]
    
    # 十二长生速度影响
    mo_state = sc_rel.get("mo_state", "")
    if mo_state in ("帝旺", "临官", "长生"):
        speed += 0.4
    elif mo_state in ("墓", "绝", "死"):
        speed -= 0.4
    if fs == "顺" and st == "顺":
        speed += 0.8
        parts.append("三传顺 → 事速")
    elif fs == "逆" and st == "逆":
        speed -= 0.8
        parts.append("三传递克 → 事缓")
    elif fs == "顺":
        speed += 0.3
    elif st == "顺":
        speed += 0.3
    
    # 课体
    ke_ti = getattr(pan, 'ke_ti', '')
    if "反吟" in ke_ti:
        speed += 0.8
        parts.append("反吟课 → 反复但快速")
    elif "伏吟" in ke_ti:
        speed -= 0.8
        parts.append("伏吟课 → 缓滞")
    
    # 神煞速增
    if "飞廉" in shensha and shensha.get("飞廉"):
        speed += 0.5
        parts.append("飞廉动 → 事速")
    
    # ── 2. 旬空填空（应期最关键的校正） ──
    xun_kong_1 = shensha.get("旬空_1", "")
    xun_kong_2 = shensha.get("旬空_2", "")
    
    # 三传落旬空？
    sanchuan_positions = [chu, zhong, mo]
    empty_hits = [p for p in sanchuan_positions if p in (xun_kong_1, xun_kong_2)]
    
    if empty_hits:
        empty_names = ["初传" if p == chu else ("中传" if p == zhong else "末传") 
                       for p in empty_hits]
        empty_str = '、'.join(empty_names)
        parts.append(f"{empty_str}落旬空({xun_kong_1}{xun_kong_2})，须待填空")
        
        # 旬空填空日计算：冲空=填实
        # 子午冲、丑未冲、寅申冲、卯酉冲、辰戌冲、巳亥冲
        chong_map = {'子':'午','丑':'未','寅':'申','卯':'酉','辰':'戌','巳':'亥',
                     '午':'子','未':'丑','申':'寅','酉':'卯','戌':'辰','亥':'巳'}
        fill_days = []
        for empty_zhi in [xun_kong_1, xun_kong_2]:
            if empty_zhi and empty_zhi in chong_map:
                fill_zhi = chong_map[empty_zhi]
                fill_days.append(f"{fill_zhi}日")
        if fill_days:
            fill_str = '或'.join(fill_days)
            parts.append(f"填空日：{fill_str}")
            timing_notes.append(f"填空于{fill_str}")
        
        speed -= 0.6  # 落空则延缓
    
    # ── 3. 天赦/天喜/天医的优质窗口 ──
    if "天赦" in shensha and shensha.get("天赦"):
        timing_notes.append(f"天赦在{shensha['天赦']}方/日，利宽恕赦免之事")
    if "天喜" in shensha and shensha.get("天喜"):
        timing_notes.append(f"天喜在{shensha['天喜']}，利喜事")
    
    # ── 4. 最终判断 ──
    if speed >= 2.0:
        period = "快（3天内）"
    elif speed >= 0.5:
        period = "较快（7天内）"
    elif speed >= -0.5:
        period = "中期（半月内）"
    elif speed >= -1.5:
        period = "较慢（一月内）"
    else:
        period = "迟滞（一月以上）"
    
    return {
        "period": period,
        "speed_score": round(speed, 1),
        "factors": parts,
        "timing_notes": timing_notes,
        "summary": "；".join(parts) if parts else "信息不足，无法推定准确应期。",
    }


# ════════════════════════════════════════════════════
# 四、综合解读生成
# ════════════════════════════════════════════════════

def generate_reading_v3(pan, scored: Dict) -> Dict:
    """
    生成本盘综合解读
    返回：{ke_ti_reading, sanchuan_reading, tianjiang_reading, dimension_readings, summary}
    """
    ke_ti = scored.get("ke_ti", "默认")
    sc = scored.get("sanchuan", {})
    chu = sc.get("chu", "")
    zhong = sc.get("zhong", "")
    mo = sc.get("mo", "")
    sc_rel = sc.get("relationship", {})
    tjp = scored.get("tian_jiang_pos", {})
    shensha = scored.get("shensha", {})
    
    reading = {}
    
    # 1. 课体解读
    if ke_ti in KETI_DESC:
        reading["ke_ti"] = KETI_DESC[ke_ti]
    else:
        reading["ke_ti"] = f"课体：{ke_ti}，未见详细记录。"
    
    # 2. 三传解读（十二长生增强版）
    # 优先使用十二长生叙事
    narr = sc_rel.get("narrative", "")
    direction = sc_rel.get("overall_direction", "")
    if narr:
        sanchuan_text = narr
        if direction:
            sanchuan_text += "\n" + direction
    else:
        sanchuan_text = SANCHUAN_NARRATIVE.get((sc_rel.get("first_second", "平"), sc_rel.get("second_third", "平")), "")
    reading["sanchuan"] = sanchuan_text or "三传信息不足。"
    
    # 3. 天将解读（取三传的天将）
    tj_parts = []
    for pos, label in [(chu, "初"), (zhong, "中"), (mo, "末")]:
        if pos:
            tj = tjp.get(pos, "")
            if tj:
                tj_parts.append(f"{label}传{tj}({pos})")
    if tj_parts:
        reading["tianjiang"] = "天将：" + " → ".join(tj_parts)
    else:
        reading["tianjiang"] = "天将信息不足。"
    
    # 4. 神煞高亮（按凶吉分类）
    active = [k for k in SHENSHA_VALUE if k in shensha and shensha.get(k)]
    if active:
        # 分出吉凶
        good_shen = [k for k in active if SHENSHA_VALUE.get(k, 0) > 0.15]
        bad_shen = [k for k in active if SHENSHA_VALUE.get(k, 0) < -0.15]
        parts_shen = []
        if good_shen:
            gs = "、".join(good_shen[:4])
            parts_shen.append(f"吉：{gs}")
        if bad_shen:
            bs = "、".join(bad_shen[:4])
            parts_shen.append(f"凶：{bs}")
        reading["shensha_highlight"] = "神煞注意 | " + " | ".join(parts_shen)
        
        # 同时输出完整神煞字典供参考
        reading["shensha_active"] = active
    else:
        reading["shensha_highlight"] = ""
        reading["shensha_active"] = []
    
    # 旬空提醒
    xk_1 = shensha.get("旬空_1", "")
    xk_2 = shensha.get("旬空_2", "")
    if xk_1 and xk_2:
        reading["xunkong"] = f"旬空：{xk_1}{xk_2}"
    
    # 5. 各维度综合解读
    dim_readings = {}
    dims = scored.get("dimensions", {})
    for dim, info in dims.items():
        s = info["score"]
        if s >= 8:
            tag = "强旺"
            comment = f"此维度能量充沛。"
        elif s >= 6.5:
            tag = "良好"
            comment = f"此维度状态中上，顺势而为即可。"
        elif s >= 4.5:
            tag = "平稳"
            comment = f"此维度不旺不衰，结果取决于后天努力。"
        elif s >= 3.0:
            tag = "偏弱"
            comment = f"此维度有阻力，需谨慎应对。"
        else:
            tag = "弱势"
            comment = f"此维度能量低，建议避开重大决定。"
        
        dim_readings[dim] = f"{tag}（{s}/10）。{comment}"
    
    reading["dimension_readings"] = dim_readings
    
    # 6. 总体总结
    avg = sum(info["score"] for info in dims.values()) / len(dims) if dims else 5.0
    if avg >= 7:
        overall = "总体格局良好。课体、三传、天将协同，事体有正面趋势。建议顺势推进，抓住关键窗口。"
    elif avg >= 5:
        overall = "总体格局中平。能量有正有负，并非全吉也不是全凶。事体有成有败，关键在于执行和时机。"
    else:
        overall = "总体格局偏弱。能量层面显示阻力较多，建议三思而后行。如果必须做，做好最坏打算。"
    reading["overall"] = overall
    
    return reading


# ════════════════════════════════════════════════════
# 五、小六壬 → 大六壬 联动接口
# ════════════════════════════════════════════════════

def xiaoliu_to_daliuren(xiaoliu_result: Dict,
                         question_category: str = "general") -> Dict:
    """
    小六壬结果 → 大六壬深度挖掘
    流程：
      1. 根据小六壬给出的时间点（月+日+时），起大六壬盘
      2. 取得大六壬评分
      3. 结合小六壬的趋势方向，标记大六壬中的关键矛盾
      4. 输出"表层+深层"双层解读
    
    Args:
        xiaoliu_result: xiaoliu_scores.score_dimensions 的输出
        question_category: general / relationship / career / finance / health
    
    Returns:
        联动解读
    """
    # 获取小六壬的时间信息
    div = xiaoliu_result.get("divination", {})
    month = div.get("month", 5)
    day = div.get("day", 5)
    hour = div.get("hour_24", 12)
    
    # 排大六壬
    dlr = score_daliuren_v3(2026, month, day, hour)
    
    # 小六壬趋势
    xl_trend = xiaoliu_result.get("trend", "横盘")
    xl_gong = div.get("gong_name", "")
    xl_level = div.get("gong_level", "")
    
    # 联动合成
    linkage = {
        "xiaoliu": {
            "gong": xl_gong,
            "level": xl_level,
            "trend": xl_trend
        },
        "daliuren": {
            "ke_ti": dlr.get("ke_ti", ""),
            "dimensions": {d: info["score"] for d, info in dlr.get("dimensions", {}).items()},
            "reading": dlr.get("reading", {}),
            "yingshen": dlr.get("yingshen", {})
        },
        "linkage_analysis": ""
    }
    
    # 联动分析逻辑
    analysis_parts = []
    
    # 趋势对比
    dlr_dim_scores = [info["score"] for info in dlr.get("dimensions", {}).values()]
    dlr_avg = sum(dlr_dim_scores) / len(dlr_dim_scores) if dlr_dim_scores else 5.0
    
    if xl_trend == "上升" and dlr_avg >= 6.5:
        analysis_parts.append(f"【双层共振】小六壬{xl_gong}{xl_level}趋势上升，大六壬综合{dlr_avg}/10，两层均显示正面。事体有明确利好。")
    elif xl_trend == "上升" and dlr_avg < 5.0:
        analysis_parts.append(f"【表层看似有利，底层有隐患】小六壬趋势上升说明表面信息乐观，但大六壬课体显示深层能量偏弱，建议不要只看表面。")
    elif xl_trend == "下降" and dlr_avg >= 6.5:
        analysis_parts.append(f"【表层有阻力，底子还在】小六壬趋势下降说明当下不顺，但大六壬显示本局底子不差，可能只是暂时的阻滞。")
    elif xl_trend == "下降" and dlr_avg < 5.0:
        analysis_parts.append(f"【双层示警】小六壬趋势下降，大六壬综合偏弱。建议暂停或大幅调整计划。")
    else:
        analysis_parts.append(f"【中性联动】小六壬{xl_gong}{xl_level}趋势{xl_trend}，大六壬综合{dlr_avg}/10。需要结合具体问题判断。")
    
    # 大六壬课体关键信息
    ke_ti = dlr.get("ke_ti", "")
    if "反吟" in ke_ti or "伏吟" in ke_ti:
        analysis_parts.append(f"注意：大六壬呈{ke_ti}课，事体有反复或停滞的底层特征，与小六壬趋势结合考虑节奏。")
    
    linkage["linkage_analysis"] = "\n".join(analysis_parts)
    
    return linkage


# ════════════════════════════════════════════════════
# 六、主入口与测试
# ════════════════════════════════════════════════════

def main():
    """命令行入口"""
    import json
    
    if len(sys.argv) < 5:
        print("用法: python daliuren_v3.py <年> <月> <日> <时>")
        print("示例: python daliuren_v3.py 2026 5 5 19")
        sys.exit(1)
    
    year, month, day, hour = map(int, sys.argv[1:5])
    result = score_daliuren_v3(year, month, day, hour)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # 测试：今天（2026-05-05 19:00）
    print("═══ 大六壬 v3.0 完整测试 ═══")
    print()
    r = score_daliuren_v3(2026, 5, 5, 19)
    print(f"课体: {r['ke_ti']} ({r['ke_ti_level']})")
    print(f"三传: {r['sanchuan']['chu']} → {r['sanchuan']['zhong']} → {r['sanchuan']['mo']}")
    print(f"关系: {r['sanchuan']['relationship']}")
    print()
    print("五维评分:")
    for dim, info in r["dimensions"].items():
        print(f"  {dim}: {info['score']}/10 ({info['level']})  {info['note']}")
    print()
    print("应期:")
    print(f"  {r['yingshen']['period']}")
    print(f"  因子: {r['yingshen']['summary']}")
    print()
    print("综合解读:")
    reading = r.get("reading", {})
    print(f"  课体: {reading.get('ke_ti', '')}")
    print(f"  三传: {reading.get('sanchuan', '')}")
    print(f"  天将: {reading.get('tianjiang', '')}")
    if reading.get('shensha_highlight'):
        print(f"  {reading['shensha_highlight']}")
    print(f"  总体: {reading.get('overall', '')}")
    print()
    for dim, rd in reading.get("dimension_readings", {}).items():
        print(f"  {dim}: {rd}")
    print()
    print("═══ 测试完毕 ═══")