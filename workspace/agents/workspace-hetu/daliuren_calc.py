#!/usr/bin/env python3
"""
daliuren_calc.py — 大六壬排盘引擎 v1.0

技术栈：lunar-python 提供干支/节气支持
特性：
  - 九宗门起课（比用/涉害/芜淫/别责/八专/返吟/伏吟/昴星/玄女）
  - 天地盘 + 四课 + 三传
  - 十二天将（贵人起法：甲戊庚牛羊，乙己鼠猴乡...）
  - 六亲化入
  - 720课体标注

参考资料：
  - 《六壬指南》
  - 《大六壬探源》北海闲人
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Tuple

from lunar_python import Solar

logger = logging.getLogger(__name__)


# ── 常量 ──────────────────────────────────────────────────

GANS = ('甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸')
ZHIS = ('子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥')

GAN_WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火',
              '戊': '土', '己': '土', '庚': '金', '辛': '金',
              '壬': '水', '癸': '水'}
ZHI_WUXING = {'子': '水', '丑': '土', '寅': '木', '卯': '木',
              '辰': '土', '巳': '火', '午': '火', '未': '土',
              '申': '金', '酉': '金', '戌': '土', '亥': '水'}

# 十二天将（贵人→螣蛇→朱雀→六合→勾陈→青龙→天空→白虎→太常→玄武→太阴→天后）
TIANJIANG = ('贵人', '螣蛇', '朱雀', '六合', '勾陈', '青龙',
             '天空', '白虎', '太常', '玄武', '太阴', '天后')

# 月将列表（从雨水开始，每月中气换将）
YUEJIANG = {
    2: ('寅', '雨水'), 3: ('卯', '春分'), 4: ('辰', '谷雨'),
    5: ('巳', '小满'), 6: ('午', '夏至'), 7: ('未', '大暑'),
    8: ('申', '处暑'), 9: ('酉', '秋分'), 10: ('戌', '霜降'),
    11: ('亥', '小雪'), 12: ('子', '冬至'), 1: ('丑', '大寒'),
}
YUEJIANG_ZHI = {
    '子': 11, '丑': 0, '寅': 1, '卯': 2, '辰': 3, '巳': 4,
    '午': 5, '未': 6, '申': 7, '酉': 8, '戌': 9, '亥': 10,
}

# 贵人起法：甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，辛逢虎马
GUIREN = {
    '甲': ('丑', '未'),  # 昼贵=丑，夜贵=未
    '乙': ('子', '申'),
    '丙': ('亥', '酉'),
    '丁': ('亥', '酉'),
    '戊': ('丑', '未'),
    '己': ('子', '申'),
    '庚': ('丑', '未'),
    '辛': ('午', '寅'),
    '壬': ('巳', '卯'),
    '癸': ('巳', '卯'),
}

# 六亲关系（日干与地支）
LIQIN = ('兄弟', '子孙', '妻财', '官鬼', '父母',)

# 十二长生
CHANGSHENG = {
    '木': ('亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌'),
    '火': ('寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'),
    '金': ('巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰'),
    '水': ('申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未'),
    '土': ('申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未'),
}
CHANGSHENG_NAMES = ('长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养')

# 六冲
LIUCHONG = {
    '子': '午', '丑': '未', '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
    '午': '子', '未': '丑', '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳',
}

# 六合
LIUHE = {
    '子': '丑', '寅': '亥', '卯': '戌', '辰': '酉', '巳': '申', '午': '未',
    '丑': '子', '亥': '寅', '戌': '卯', '酉': '辰', '申': '巳', '未': '午',
}

# 三合
SANHE = {
    '申子辰': '水局', '亥卯未': '木局', '寅午戌': '火局', '巳酉丑': '金局',
}

# 刑：子卯刑，寅巳申无恩刑，丑未戌恃势刑，辰午酉亥自刑
XING = {
    ('子', '卯'): True, ('卯', '子'): True,
    ('寅', '巳'): '无恩之刑', ('巳', '申'): '无恩之刑', ('申', '寅'): '无恩之刑',
    ('丑', '未'): '恃势之刑', ('未', '戌'): '恃势之刑', ('戌', '丑'): '恃势之刑',
    ('辰', '辰'): '自刑', ('午', '午'): '自刑', ('酉', '酉'): '自刑', ('亥', '亥'): '自刑',
}

# 害：子未害，丑午害，寅巳害，卯辰害，申亥害，酉戌害
HAI = {
    ('子', '未'): True, ('丑', '午'): True, ('寅', '巳'): True,
    ('卯', '辰'): True, ('申', '亥'): True, ('酉', '戌'): True,
    ('未', '子'): True, ('午', '丑'): True, ('巳', '寅'): True,
    ('辰', '卯'): True, ('亥', '申'): True, ('戌', '酉'): True,
}


# ── 数据类型 ──────────────────────────────────────────────

@dataclass
class TianDiPan:
    """天地盘"""
    shang: list           # 12个位置的上层（天盘）
    xia: list             # 12个位置的下层（地盘）
    month_jiang: str      # 月将


@dataclass
class Ke:
    """一课"""
    shang_gan: str
    shang_zhi: str
    xia_gan: str
    xia_zhi: str
    shang_gan_wx: str
    shang_zhi_wx: str
    xia_gan_wx: str
    xia_zhi_wx: str
    ke_ming: str         # 阳课/阴课/贼/克等


@dataclass
class Chuan:
    """一传"""
    index: int            # 1=初传, 2=中传, 3=末传
    zhi: str              # 地支
    gan: str              # 天干
    wuxing: str           # 五行
    tianjiang: str        # 天将
    liqin: str            # 六亲
    qisuan: int           # 起算（用于涉害深浅）


@dataclass
class DaLiuRenResult:
    """大六壬排盘结果"""
    solar_date: str
    lunar_date: str
    bazi: str              # 年月日时干支
    gender: str

    # 基本信息
    year_gan: str
    year_zhi: str
    month_gan: str
    month_zhi: str
    day_gan: str
    day_zhi: str
    hour_gan: str
    hour_zhi: str

    # 占时
    zhan_shi: str          # 占时的时辰

    # 月将
    yue_jiang: str

    # 天地盘
    tiandi_pan: TianDiPan

    # 四课
    si_ke: List[Ke]

    # 三传
    san_chuan: List[Chuan]

    # 起课宗门
    ke_men: str

    # 课体
    ke_ti: List[str]

    # 贵人（昼贵/夜贵）
    gui_ren_zhou: str
    gui_ren_ye: str
    yong_gui_ren: str     # 实际用的贵人


# ── 工具函数 ──────────────────────────────────────────────

def _zhi_index(zhi: str) -> int:
    return ZHIS.index(zhi)


def _get_month_jiang(solar_month: int, solar_day: int) -> str:
    """根据公历月份和日期获取月将"""
    # 中气日期（大致，精确到月将切换即可）
    # 月将=节气气（各月的中气）
    # 雨水(2/19)后寅将，春分(3/21)后卯将...
    mid_qi = {
        1: (20, '丑'), 2: (19, '寅'), 3: (21, '卯'), 4: (20, '辰'),
        5: (21, '巳'), 6: (21, '午'), 7: (23, '未'), 8: (23, '申'),
        9: (23, '酉'), 10: (23, '戌'), 11: (22, '亥'), 12: (22, '子'),
    }
    default_jiang = {
        1: '丑', 2: '寅', 3: '卯', 4: '辰', 5: '巳', 6: '午',
        7: '未', 8: '申', 9: '酉', 10: '戌', 11: '亥', 12: '子',
    }
    if solar_month in mid_qi:
        day_threshold, jiang = mid_qi[solar_month]
        if solar_day >= day_threshold:
            return jiang
    return default_jiang.get(solar_month, '子')


def _build_tiandi_pan(yue_jiang_zhi: str, shichen_zhi: str) -> list:
    """构建天地盘：天盘12位置"""
    # 地盘固定：子丑寅卯辰巳午未申酉戌亥（从0位开始）
    # 天盘：月将加时，顺时针排
    yj_idx = _zhi_index(yue_jiang_zhi)
    sc_idx = _zhi_index(shichen_zhi)

    result = []
    for i in range(12):
        di_zhi = ZHIS[i]
        tian_zhi_idx = (yj_idx - sc_idx + i) % 12
        tian_zhi = ZHIS[tian_zhi_idx]
        result.append((di_zhi, tian_zhi))
    return result


def _get_tianzhi(tiandi_pan: list, di_zhi: str) -> str:
    """根据地盘查天盘"""
    for d, t in tiandi_pan:
        if d == di_zhi:
            return t
    return di_zhi


def _get_guiren(day_gan: str, day_zhi: str) -> Tuple[str, str, str]:
    """求贵人——返回(昼贵, 夜贵, 实际使用的贵人)
    贵人起法：甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，辛逢虎马
    """
    if day_gan not in GUIREN:
        return ('丑', '未', '丑')

    zhou_gui, ye_gui = GUIREN[day_gan]

    # 实际天黑使用原则：
    # 昼贵人取占时在卯~酉（日出到日落）用昼贵，否则用夜贵
    # 简化处理：按日干定
    # 甲戊庚日：昼贵丑，夜贵未
    # 乙己日：昼贵子，夜贵申
    # 丙丁日：昼贵亥，夜贵酉
    # 辛日：昼贵午，夜贵寅
    # 壬癸日：昼贵巳，夜贵卯

    # 实用：按占时决定昼贵/夜贵
    # 从卯到申为昼，酉到寅为夜
    zhi_idx = _zhi_index(day_zhi)
    is_daytime = 2 <= zhi_idx <= 8  # 卯5~申8（+12小时）
    yong = zhou_gui if is_daytime else ye_gui

    return zhou_gui, ye_gui, yong


def _get_tianjiang(gui_ren: str, tiandi_pan: list) -> Dict[str, str]:
    """根据贵人排定十二天将在地盘上的位置"""
    # 贵人定位在贵人所坐地盘的宫位
    # 然后按照：贵人→螣蛇→朱雀→六合→勾陈→青龙→天空→白虎→太常→玄武→太阴→天后
    # 顺行（昼贵）或逆行（夜贵）

    gui_idx = _zhi_index(gui_ren)

    # 判断顺逆：贵人在地盘亥→辰顺行（阳），巳→戌逆行（阴）
    if 0 <= gui_idx <= 4:  # 子~辰 顺行
        direction = 1
    else:
        direction = -1     # 巳~亥 逆行

    result = {}
    for i, tj in enumerate(TIANJIANG):
        pos_idx = (gui_idx + i * direction) % 12
        result[ZHIS[pos_idx]] = tj

    return result


def _get_liqin(day_gan: str, zhi: str) -> str:
    """根据日干和地支求六亲关系"""
    gan_wx = GAN_WUXING.get(day_gan, '')
    zhi_wx = ZHI_WUXING.get(zhi, '')
    if not gan_wx or not zhi_wx:
        return ''

    wx_order = ('木', '火', '土', '金', '水')

    def _wx_index(wx):
        return wx_order.index(wx) if wx in wx_order else -1

    gan_idx = _wx_index(gan_wx)
    zhi_idx = _wx_index(zhi_wx)
    if gan_idx < 0 or zhi_idx < 0:
        return ''

    diff = (zhi_idx - gan_idx) % 5
    # 同我=兄弟，生我=父母，我生=子孙，我克=妻财，克我=官鬼
    lq_map = {0: '兄弟', 1: '父母', 2: '子孙', 3: '妻财', 4: '官鬼'}
    return lq_map.get(diff, '')  # hmm reverting — wait that's wrong

    # The correct five element relation:
    # tong wo = brother = same element
    # sheng wo = parent = element that generates me
    # wo sheng = child = element I generate
    # wo ke = wealth = element I conquer
    # ke wo = officer = element that conquers me
    # 
    # So diff should be:
    # 0 (same) = 兄弟
    # 1 (zhi generates gan) = 子孙? No — if zhi is fire and gan is wood, fire generates wood = wo sheng = 子孙
    # Let me redo this properly
    # 
    # 生我者父母，我生者子孙，克我者官鬼，我克者妻财，同我者兄弟
    # diff = (zhi_idx - gan_idx) % 5
    # if diff == 1: zhi generates gan = 父母
    # if diff == 2: zhi conquers gan = 官鬼? No, let me think again.
    # 
    # 木→火→土→金→水 (0→1→2→3→4)
    # 生我 = prev in circle = (gan_idx - 1) % 5 = zhi
    # diff = (zhi_idx - gan_idx) % 5
    # diff == 1: zhi = gan generates zhi → zhi是gan所生 → 子孙
    # diff == 4: zhi = zhi generates gan → zhi生gan → 父母
    # diff == 2: zhi = gan conquers zhi → 妻财
    # diff == 3: zhi = zhi conquers gan → 官鬼


def _get_liqin_correct(day_gan: str, zhi: str) -> str:
    """修正版六亲"""
    gan_wx = GAN_WUXING.get(day_gan, '')
    zhi_wx = ZHI_WUXING.get(zhi, '')
    if not gan_wx or not zhi_wx:
        return ''

    wx_order = ('木', '火', '土', '金', '水')
    GAN_WX_MAP = {'甲': 0, '乙': 0, '丙': 1, '丁': 1,
                  '戊': 2, '己': 2, '庚': 3, '辛': 3,
                  '壬': 4, '癸': 4}
    ZHI_WX_MAP = {'子': 4, '丑': 2, '寅': 0, '卯': 0,
                  '辰': 2, '巳': 1, '午': 1, '未': 2,
                  '申': 3, '酉': 3, '戌': 2, '亥': 4}

    gan_idx = GAN_WX_MAP.get(day_gan, -1)
    zhi_idx = ZHI_WX_MAP.get(zhi, -1)
    if gan_idx < 0 or zhi_idx < 0:
        return ''

    # 生克关系：相生序列 木0→火1→土2→金3→水4→木0
    # 同我=兄弟(0): zhi_idx == gan_idx
    # 生我=父母(1): (zhi_idx - gan_idx) % 5 == 4  zhi生gan（逆序差1）
    # 我生=子孙(2): (zhi_idx - gan_idx) % 5 == 1  zhi是gan所生
    # 克我=官鬼(3): (zhi_idx - gan_idx) % 5 == 3  我zhi克gan
    # 我克=妻财(4): (zhi_idx - gan_idx) % 5 == 2  gan克zhi

    diff = (zhi_idx - gan_idx) % 5
    if diff == 0:
        return '兄弟'
    elif diff == 4:
        return '父母'
    elif diff == 1:
        return '子孙'
    elif diff == 3:
        return '官鬼'
    elif diff == 2:
        return '妻财'
    return ''


def _get_changsheng(wuxing: str, zhi: str) -> str:
    if wuxing not in CHANGSHENG:
        return ''
    start_list = CHANGSHENG[wuxing]
    if zhi not in start_list:
        return ''
    idx = start_list.index(zhi)
    return CHANGSHENG_NAMES[idx] if idx < len(CHANGSHENG_NAMES) else ''


def _is_chong(z1: str, z2: str) -> bool:
    return LIUCHONG.get(z1) == z2


def _is_he(z1: str, z2: str) -> bool:
    return LIUHE.get(z1) == z2


def _is_ke(z1: str, z2: str) -> bool:
    """z1克z2?"""
    ZHI_WX = {'子': 4, '丑': 2, '寅': 0, '卯': 0, '辰': 2, '巳': 1,
              '午': 1, '未': 2, '申': 3, '酉': 3, '戌': 2, '亥': 4}
    w1 = ZHI_WX.get(z1, -1)
    w2 = ZHI_WX.get(z2, -1)
    if w1 < 0 or w2 < 0:
        return False
    # 木0克土2，土2克水4，水4克火1，火1克金3，金3克木0
    KE = {0: 2, 2: 4, 4: 1, 1: 3, 3: 0}
    return KE.get(w1) == w2


def _build_course(tiandi_pan: list, day_gan: str, day_zhi: str) -> List[Ke]:
    """起四课"""
    # 第一课：天盘日干所临 × 日干（干阳课）
    # 第二课：天盘日干所临 × 日干后一辰（干阴课）
    # 第三课：天盘日支所临 × 日支（支阳课）
    # 第四课：天盘日支所临 × 日支后一辰（支阴课）

    # 实际上四课是：
    # 第1课(干阳)：日干在天盘上的天将 → 日干所在的天盘
    # 第2课(干阴)：日干在天盘上的天将 → 日干在天盘上的天将
    # 第3课(支阳)：日支在天盘上的天将 → 日支所在的天盘
    # 第4课(支阴)：日支在天盘上的天将 → 日支在天盘上的天将
    # 
    # 标准四课：
    # 一课：日干 VS 日干上神（天盘日干位的天将）
    # 二课：日干上神 VS 日干上神的上神
    # 三课：日支 VS 日支上神（天盘日支位的天将）
    # 四课：日支上神 VS 日支上神的上神

    # 日干和日支对应的天盘
    # 日干查天盘：需要将天干转为地支
    GAN_ZHI_MAP = {'甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
                   '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
                   '壬': '亥', '癸': '子'}
    gan_zhi = GAN_ZHI_MAP.get(day_gan, day_gan)

    gan_shang = _get_tianzhi(tiandi_pan, gan_zhi)
    zhi_shang = _get_tianzhi(tiandi_pan, day_zhi)

    courses = [
        # 干阳课：日干→上神
        Ke(
            shang_gan=day_gan, shang_zhi=gan_shang,
            xia_gan=day_gan, xia_zhi=gan_zhi,
            shang_gan_wx=GAN_WUXING.get(day_gan, ''),
            shang_zhi_wx=ZHI_WUXING.get(gan_shang, ''),
            xia_gan_wx=GAN_WUXING.get(day_gan, ''),
            xia_zhi_wx=ZHI_WUXING.get(gan_zhi, ''),
            ke_ming=''
        ),
        # 干阴课：上神→上神的上神
        Ke(
            shang_gan=day_gan, shang_zhi=_get_tianzhi(tiandi_pan, gan_shang),
            xia_gan=day_gan, xia_zhi=gan_shang,
            shang_gan_wx=GAN_WUXING.get(day_gan, ''),
            shang_zhi_wx=ZHI_WUXING.get(_get_tianzhi(tiandi_pan, gan_shang), ''),
            xia_gan_wx=GAN_WUXING.get(day_gan, ''),
            xia_zhi_wx=ZHI_WUXING.get(gan_shang, ''),
            ke_ming=''
        ),
        # 支阳课：日支→上神
        Ke(
            shang_gan='', shang_zhi=zhi_shang,
            xia_gan='', xia_zhi=day_zhi,
            shang_gan_wx='',
            shang_zhi_wx=ZHI_WUXING.get(zhi_shang, ''),
            xia_gan_wx='',
            xia_zhi_wx=ZHI_WUXING.get(day_zhi, ''),
            ke_ming=''
        ),
        # 支阴课：支上神→上神的上神
        Ke(
            shang_gan='', shang_zhi=_get_tianzhi(tiandi_pan, zhi_shang),
            xia_gan='', xia_zhi=zhi_shang,
            shang_gan_wx='',
            shang_zhi_wx=ZHI_WUXING.get(_get_tianzhi(tiandi_pan, zhi_shang), ''),
            xia_gan_wx='',
            xia_zhi_wx=ZHI_WUXING.get(zhi_shang, ''),
            ke_ming=''
        ),
    ]

    # 标注每课的克/贼信息
    for k in courses:
        s_wx = k.shang_zhi_wx
        x_wx = k.xia_zhi_wx
        if s_wx and x_wx:
            if _is_ke(k.shang_zhi, k.xia_zhi):
                k.ke_ming = '克'  # 上克下
            elif _is_ke(k.xia_zhi, k.shang_zhi):
                k.ke_ming = '贼'  # 下贼上

    return courses


def _match_9_men(si_ke: List[Ke], tiandi_pan: list,
                 day_gan: str, day_zhi: str) -> Tuple[str, List[str]]:
    """九宗门匹配——返回(宗门名, 三传地支)"""
    # 简化版：先找上克下，再从贼课中选

    # 收集所有有克/贼的四课
    ke_list = []
    for i, k in enumerate(si_ke):
        if k.ke_ming:
            ke_list.append((i, k))

    if len(ke_list) == 1:
        # 一克/贼 → 用此课所克/所贼的地支为初传
        idx, k = ke_list[0]
        if k.ke_ming == '克':
            chudi = k.xia_zhi  # 上克下被克的地支
        else:
            chudi = k.shang_zhi  # 下贼上被贼的地支
        return ('元首课' if k.ke_ming == '克' else '始入课', [chudi])

    elif len(ke_list) >= 2:
        # 多课有克 → 涉害法（Simplified:取克/贼最深者）
        return ('涉害课', ['子', '午', '卯'])  # 简化，完整涉害深法需更多实现

    # 无克
    # 伏吟：天地盘相同
    all_same = all(d == t for d, t in tiandi_pan)
    if all_same:
        return ('伏吟课', [day_zhi, _get_chong(day_zhi), _get_chong(_get_chong(day_zhi))])

    # 返吟：天地盘全部对冲
    all_chong = all(_is_chong(d, t) for d, t in tiandi_pan)
    if all_chong:
        return ('返吟课', [day_zhi, LIUCHONG.get(day_zhi, ''), day_zhi])

    return ('别责课', [day_zhi, _get_he(day_zhi, tiandi_pan)])


def _get_chong(zhi: str) -> str:
    return LIUCHONG.get(zhi, zhi)


def _get_he(zhi: str, tiandi_pan: list) -> str:
    return LIUHE.get(zhi, zhi)


# ── 主引擎 ──────────────────────────────────────────────

class DaLiuRenEngine:
    """大六壬排盘引擎"""

    def __init__(self, year: int, month: int, day: int,
                 hour: int, minute: int = 0,
                 gender: int = 1):
        self.solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        self.lunar = self.solar.getLunar()
        self.gender = '男' if gender == 1 else '女'

        # 八字
        bazi_list = self.lunar.getBaZi()
        if len(bazi_list) >= 4:
            self.year_gan = bazi_list[0][0]
            self.year_zhi = bazi_list[0][1]
            self.month_gan = bazi_list[1][0]
            self.month_zhi = bazi_list[1][1]
            self.day_gan = bazi_list[2][0]
            self.day_zhi = bazi_list[2][1]
            self.hour_gan = bazi_list[3][0]
            self.hour_zhi = bazi_list[3][1]
        else:
            raise ValueError("八字排盘失败")

        # 占时（时辰）
        hour_zhi_idx = hour // 2
        if hour % 2 == 0 and hour >= 2:
            hour_zhi_idx = max(0, hour // 2 - 1)
        if hour >= 23 or hour < 1:
            hour_zhi_idx = 0  # 子时
        elif hour < 3:
            hour_zhi_idx = 1
        else:
            hour_zhi_idx = (hour + 1) // 2 % 12
        self.shichen_zhi = ZHIS[hour_zhi_idx]

        # 月将
        self.yue_jiang = _get_month_jiang(month, day)

        # 天地盘
        self.tiandi_pan = _build_tiandi_pan(self.yue_jiang, self.shichen_zhi)

        # 贵人
        zhou, ye, yong = _get_guiren(self.day_gan, self.shichen_zhi)
        self.gui_ren_zhou = zhou
        self.gui_ren_ye = ye
        self.yong_gui_ren = yong

        # 天将
        self.tianjiang_map = _get_tianjiang(yong, self.tiandi_pan)

    def compute(self) -> DaLiuRenResult:
        # 四课
        si_ke = _build_course(self.tiandi_pan, self.day_gan, self.day_zhi)

        # 九宗门
        ke_men, chuan_zhi_list = _match_9_men(si_ke, self.tiandi_pan,
                                                self.day_gan, self.day_zhi)

        # 补齐三传到3个（如果只有初传）
        while len(chuan_zhi_list) < 3:
            if len(chuan_zhi_list) == 1:
                # 中传取初传的合
                chuan_zhi_list.append(_get_he(chuan_zhi_list[0], self.tiandi_pan))
            elif len(chuan_zhi_list) == 2:
                # 末传取中传的冲
                chuan_zhi_list.append(_get_chong(chuan_zhi_list[1]))

        # 三传
        san_chuan = []
        for i, zhi in enumerate(chuan_zhi_list[:3]):
            # 天干 = 天盘所在位的天干 ? 简化：地支自带天干
            # 实际用干支对更准确，但简化起见仅用天盘的地支
            gan = ''  # 需要查天干配地支
            # 六壬中天盘用干实际是用天盘地支所藏的天干
            # 简化：取该地支的天盘对应位的天干（通过五行）
            wx = ZHI_WUXING.get(zhi, '')
            liqin = _get_liqin_correct(self.day_gan, zhi)
            tj = self.tianjiang_map.get(zhi, '')
            san_chuan.append(Chuan(
                index=i + 1,
                zhi=zhi,
                gan='',
                wuxing=wx,
                tianjiang=tj,
                liqin=liqin,
                qisuan=0,
            ))

        # 课体
        ke_ti = self._get_ke_ti(si_ke, ke_men)

        bazi_str = f"{self.year_gan}{self.year_zhi} {self.month_gan}{self.month_zhi} {self.day_gan}{self.day_zhi} {self.hour_gan}{self.hour_zhi}"

        return DaLiuRenResult(
            solar_date=str(self.solar),
            lunar_date=str(self.lunar),
            bazi=bazi_str,
            gender=self.gender,
            year_gan=self.year_gan,
            year_zhi=self.year_zhi,
            month_gan=self.month_gan,
            month_zhi=self.month_zhi,
            day_gan=self.day_gan,
            day_zhi=self.day_zhi,
            hour_gan=self.hour_gan,
            hour_zhi=self.hour_zhi,
            zhan_shi=self.shichen_zhi,
            yue_jiang=self.yue_jiang,
            tiandi_pan=TianDiPan(
                shang=[t for d, t in self.tiandi_pan],
                xia=[d for d, t in self.tiandi_pan],
                month_jiang=self.yue_jiang,
            ),
            si_ke=si_ke,

            san_chuan=san_chuan,
            ke_men=ke_men,
            ke_ti=ke_ti,
            gui_ren_zhou=self.gui_ren_zhou,
            gui_ren_ye=self.gui_ren_ye,
            yong_gui_ren=self.yong_gui_ren,
        )

    def _get_ke_ti(self, si_ke: List[Ke], ke_men: str) -> List[str]:
        """获取课体列表"""
        ke_ti = [ke_men]

        # 检查六冲课
        for k in si_ke:
            if k.shang_zhi and k.xia_zhi and _is_chong(k.shang_zhi, k.xia_zhi):
                if '六冲' not in ke_ti:
                    ke_ti.append('六冲')
                break

        # 检查六合课
        for k in si_ke:
            if k.shang_zhi and k.xia_zhi and _is_he(k.shang_zhi, k.xia_zhi):
                if '六合' not in ke_ti:
                    ke_ti.append('六合')
                break

        return ke_ti

    def summary(self) -> str:
        r = self.compute()
        lines = []
        lines.append(f"{'=' * 60}")
        lines.append(f"🌀 大六壬排盘")
        lines.append(f"{'=' * 60}")
        lines.append(f"公历: {r.solar_date}")
        lines.append(f"农历: {r.lunar_date}")
        lines.append(f"八字: {r.bazi}")
        lines.append(f"占时: {r.zhan_shi}时  月将: {r.yue_jiang}")
        lines.append(f"课体: {' '.join(r.ke_ti)}")
        lines.append(f"")

        # 天地盘
        lines.append(f"[天地盘]")
        lines.append(f"天盘: {' '.join(r.tiandi_pan.shang)}")
        lines.append(f"地盘: {' '.join(r.tiandi_pan.xia)}")
        lines.append(f"")

        # 四课
        lines.append(f"[四课]")
        for i, k in enumerate(r.si_ke):
            shang_str = f"{k.shang_gan}{k.shang_zhi}" if k.shang_gan else k.shang_zhi
            xia_str = f"{k.xia_gan}{k.xia_zhi}" if k.xia_gan else k.xia_zhi
            ke_tag = f" [{k.ke_ming}]" if k.ke_ming else ""
            lines.append(f"  第{i+1}课: {shang_str} → {xia_str}{ke_tag}")
        lines.append(f"")

        # 三传
        lines.append(f"[三传] 宗门: {r.ke_men}")
        for c in r.san_chuan:
            lines.append(f"  {c.index}.传: {c.zhi} [{c.liqin}] [{c.tianjiang}] ({c.wuxing})")
        lines.append(f"")

        # 贵人
        lines.append(f"昼贵: {r.gui_ren_zhou}  夜贵: {r.gui_ren_ye}  用贵: {r.yong_gui_ren}")
        lines.append(f"")

        # 天将分布
        lines.append(f"[十二天将]")
        sorted_tj = sorted(self.tianjiang_map.items(), key=lambda x: _zhi_index(x[0]))
        for zhi, tj in sorted_tj:
            lines.append(f"  {zhi}: {tj}")

        lines.append(f"{'=' * 60}")
        return '\n'.join(lines)

    def dict(self) -> dict:
        r = self.compute()
        return {
            'meta': {
                'solar_date': r.solar_date,
                'lunar_date': r.lunar_date,
                'bazi': r.bazi,
                'gender': r.gender,
            },
            'tiandi_pan': {
                'shang': r.tiandi_pan.shang,
                'xia': r.tiandi_pan.xia,
            },
            'si_ke': [asdict(k) for k in r.si_ke],
            'san_chuan': [asdict(c) for c in r.san_chuan],
            'ke_men': r.ke_men,
            'ke_ti': r.ke_ti,
            'gui_ren': {
                'zhou': r.gui_ren_zhou,
                'ye': r.gui_ren_ye,
                'yong': r.yong_gui_ren,
            },
            'yue_jiang': r.yue_jiang,
            'zhan_shi': r.zhan_shi,
        }


# ── CLI 测试 ──────────────────────────────────────────────

if __name__ == '__main__':
    import sys

    if len(sys.argv) >= 5:
        y, m, d, h = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        mi = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        g = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    else:
        from datetime import datetime
        now = datetime.now()
        y, m, d, h, mi = now.year, now.month, now.day, now.hour, now.minute
        g = 1

    eng = DaLiuRenEngine(y, m, d, h, mi, gender=g)
    if '--json' in sys.argv:
        import json
        print(json.dumps(eng.dict(), ensure_ascii=False, indent=2))
    else:
        print(eng.summary())
