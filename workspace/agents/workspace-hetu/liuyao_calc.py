#!/usr/bin/env python3
"""
liuyao_calc.py — 六爻纳甲排盘引擎 v2.0

技术栈：lunar-python（干支/日历）+ najia 核心数据层（六十四卦/纳甲/六亲/六神/世应）
原则：不重复造轮子，复用社区最佳实践的数学层

支持的起卦方式：
  a) 手动掷币结果（6次，每次0~3阳面数）
  b) 随机起卦（引擎自动掷币）
  c) 特定卦象/变卦（用于学习/回测）

输出：完整的纳甲排盘+世应+六亲+六神+旺衰+旬空+伏神+飞神
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Tuple
from enum import Enum

from lunar_python import Solar, Lunar

logger = logging.getLogger(__name__)


# ── 核心数据层：从 najia.const 提取 ──────────────────────
# 避免依赖有bug的 najia 主库，直接用常量

GANS = ('甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸')
ZHIS = ('子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥')

# 五行：木1 火2 土3 金4 水5
XING5 = ('木', '火', '土', '金', '水')
ZHI5 = (4, 3, 1, 1, 3, 2, 2, 3, 4, 4, 3, 5)  # 子~亥 五行索引

# 六十四卦映射（二进制码→卦名）
GUA64 = {
    '111111': '乾为天', '011111': '天风姤', '001111': '天山遁', '000111': '天地否',
    '000011': '风地观', '000001': '山地剥', '000101': '火地晋', '111101': '火天大有',
    '110110': '兑为泽', '010110': '泽水困', '000110': '泽地萃', '001110': '泽山咸',
    '001010': '水山蹇', '001000': '地山谦', '001100': '雷山小过', '110100': '雷泽归妹',
    '101101': '离为火', '001101': '火山旅', '011101': '火风鼎', '010101': '火水未济',
    '010001': '山水蒙', '010011': '风水涣', '010111': '天水讼', '101111': '天火同人',
    '100100': '震为雷', '000100': '雷地豫', '010100': '雷水解', '011100': '雷风恒',
    '011000': '地风升', '011010': '水风井', '011110': '泽风大过', '100110': '泽雷随',
    '011011': '巽为风', '111011': '风天小畜', '101011': '风火家人', '100011': '风雷益',
    '100111': '天雷无妄', '100101': '火雷噬嗑', '100001': '山雷颐', '011001': '山风蛊',
    '010010': '坎为水', '110010': '水泽节', '100010': '水雷屯', '101010': '水火既济',
    '101110': '泽火革', '101100': '雷火丰', '101000': '地火明夷', '010000': '地水师',
    '001001': '艮为山', '101001': '山火贲', '111001': '山天大畜', '110001': '山泽损',
    '110101': '火泽睽', '110111': '天泽履', '110011': '风泽中孚', '001011': '风山渐',
    '000000': '坤为地', '100000': '地雷复', '110000': '地泽临', '111000': '地天泰',
    '111100': '雷天大壮', '111110': '泽天夬', '111010': '水天需', '000010': '水地比',
}

# 八宫
GONG8 = ('乾', '兑', '离', '震', '巽', '坎', '艮', '坤')
YAOS = ('111', '110', '101', '100', '011', '010', '001', '000')  # 八经卦二进制码

# 纳甲表：每宫(内卦干支, 外卦干支)
# 格式: (内卦天干+地支序列, 外卦天干+地支序列)
NAJIA = (
    ('甲子寅辰', '壬午申戌'),  # 乾
    ('丁巳卯丑', '丁亥酉未'),  # 兑
    ('己卯丑亥', '己酉未巳'),  # 离
    ('庚子寅辰', '庚午申戌'),  # 震
    ('辛丑亥酉', '辛未巳卯'),  # 巽
    ('戊寅辰午', '戊申戌子'),  # 坎
    ('丙辰午申', '丙戌子寅'),  # 艮
    ('乙未巳卯', '癸丑亥酉'),  # 坤
)

# 六亲：我克者妻财，克我者官鬼，生我者父母，我生者子孙，同我者兄弟
QING6 = ('妻财', '官鬼', '父母', '子孙', '兄弟')

# 六神：按日干起青龙→朱雀→勾陈→螣蛇→白虎→玄武
SHEN6 = ('青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武')

# 六合卦
LIUHE_GUA = ('地天泰', '雷天大壮', '泽天夬', '水天需', '水地比',
             '天地否', '风地观', '山地剥', '火地晋', '火天大有')

# 旬空表
KONG = ('子丑', '寅卯', '辰巳', '午未', '申酉', '戌亥')

# 十二长生：按五行分
CHANGSHENG = {
    '木': ('亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌'),
    '火': ('寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'),
    '金': ('巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰'),
    '水': ('申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未'),
    '土': ('申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未'),
}
CHANGSHENG_NAMES = ('长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养')

# 十二地支旺相休囚死
WANG_XIANG = {
    '寅': '旺', '卯': '旺',              # 春木
    '辰': '相',                           # 季春土相
    '巳': '旺', '午': '旺',              # 夏火
    '未': '相',                           # 季夏土相
    '申': '旺', '酉': '旺',              # 秋金
    '戌': '相',                           # 季秋土相
    '亥': '旺', '子': '旺',              # 冬水
    '丑': '相',                           # 季冬土相
}
# 更严谨的：月建旺相休囚死
WANG_XIANG_YUE = {  # 月地支 → (旺, 相, 休, 囚, 死) 的五行
    '寅': ('木', '火', '水', '金', '土'),
    '卯': ('木', '火', '水', '金', '土'),
    '辰': ('土', '金', '火', '水', '木'),
    '巳': ('火', '土', '木', '水', '金'),
    '午': ('火', '土', '木', '水', '金'),
    '未': ('土', '金', '火', '水', '木'),
    '申': ('金', '水', '土', '火', '木'),
    '酉': ('金', '水', '土', '火', '木'),
    '戌': ('土', '金', '火', '水', '木'),
    '亥': ('水', '木', '金', '土', '火'),
    '子': ('水', '木', '金', '土', '火'),
    '丑': ('土', '金', '火', '水', '木'),
}

GAN_WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火',
              '戊': '土', '己': '土', '庚': '金', '辛': '金',
              '壬': '水', '癸': '水'}
ZHI_WUXING = {'子': '水', '丑': '土', '寅': '木', '卯': '木',
              '辰': '土', '巳': '火', '午': '火', '未': '土',
              '申': '金', '酉': '金', '戌': '土', '亥': '水'}


# ── 数据类型 ──────────────────────────────────────────────

class CoinFace(Enum):
    """三枚硬币的面值总和"""
    SAN_YANG = 3      # 老阳（动爻）
    YI_YIN_ER_YANG = 2  # 少阴（静爻）
    YI_YANG_ER_YIN = 1  # 少阳（静爻）
    SAN_YIN = 0        # 老阴（动爻）


@dataclass
class YaoPosition:
    """单个爻位"""
    index: int           # 0~5，从下往上
    coin_sum: int        # 0~3
    yin_or_yang: str     # "—" 或 "--"
    is_moving: bool      # 是否动爻
    zhi: str             # 爻位地支（纳甲）
    gan: str             # 爻位天干（纳甲）
    wuxing: str          # 五行
    shishen: str         # 六亲
    she_ying: str        # 世应标记：'世'/'应'/空
    shen: str            # 六神
    biangong_zhi: str    # 变卦地支
    biangong_gan: str    # 变卦天干
    biangong_wuxing: str # 变卦五行


@dataclass
class LiuYaoResult:
    """六爻排盘结果"""
    # 元数据
    solar_date: str
    lunar_date: str
    bazi: str           # 月柱年柱日柱时柱

    # 本卦
    ben_gua_mark: str    # 二进制码
    ben_gua_name: str    # 卦名
    ben_gua_gong: str    # 卦宫
    ben_gua_type: str    # 卦象类型（六冲/六合/游魂/归魂/空）
    ben_gua_yaos: list   # 6个爻位

    # 变卦
    bian_gua_mark: Optional[str]
    bian_gua_name: Optional[str]
    bian_gua_gong: Optional[str]
    bian_gua_type: Optional[str]

    # 伏神
    fu_shen: Optional[list]

    # 日月建信息
    month_zhi: str       # 月建
    day_zhi: str         # 日建
    xunkong: str         # 旬空
    # 旺衰（每个爻位）
    yaos_wangshuai: list

    # 用神信息（起卦后填充）
    yong_shen: Optional[dict]


# ── 核心算法 ──────────────────────────────────────────────

def _get_najia_ganzhi(mark: str) -> list:
    """纳甲配干支"""
    wai = mark[3:]
    nei = mark[:3]
    wai_idx = YAOS.index(wai)
    nei_idx = YAOS.index(nei)

    # 内卦纳甲：天干+6个地支（只有前三个有效位）
    gan_nei = NAJIA[nei_idx][0][0]
    zhi_str = NAJIA[nei_idx][0][1:]
    # 对于乾/震/坎/艮（阳卦）：子寅辰
    # 对于坤/兑/离/巽（阴卦）：未巳卯 等
    # 内卦3爻对应前3个地支
    nei_zhi = [zhi_str[i] for i in range(3)]

    # 外卦纳甲
    gan_wai = NAJIA[wai_idx][1][0]
    zhi_str_wai = NAJIA[wai_idx][1][1:]
    wai_zhi = [zhi_str_wai[i] for i in range(3)]

    result = []
    # 从下往上（初爻到上爻）
    for i in range(3):
        result.append((gan_nei + nei_zhi[2 - i], nei_zhi[2 - i], gan_nei))
    for i in range(3):
        result.append((gan_wai + wai_zhi[2 - i], wai_zhi[2 - i], gan_wai))

    return result  # [(干支, 地支, 天干), ...] length=6


def _set_shi_yao(mark: str) -> Tuple[int, int, int]:
    """寻世应——返回(世爻, 应爻, 卦宫索引)"""
    wai = mark[3:]
    nei = mark[:3]

    def shi_ying(shi, index_val=None):
        ying = shi - 3 if shi > 3 else shi + 3
        index_val = shi if index_val is None else index_val
        return shi, ying, index_val

    # 天同二世天变五
    if wai[2] == nei[2]:
        if wai[1] != nei[1] and wai[0] != nei[0]:
            return shi_ying(2)
    else:
        if wai[1] == nei[1] and wai[0] == nei[0]:
            return shi_ying(5)

    # 人同游魂人变归
    if wai[1] == nei[1]:
        if wai[0] != nei[0] and wai[2] != nei[2]:
            return shi_ying(4, 6)  # 游魂
    else:
        if wai[0] == nei[0] and wai[2] == nei[2]:
            return shi_ying(3, 6)  # 归魂

    # 地同四世地变初
    if wai[0] == nei[0]:
        if wai[1] != nei[1] and wai[2] != nei[2]:
            return shi_ying(4)
    else:
        if wai[1] == nei[1] and wai[2] == nei[2]:
            return shi_ying(1)

    # 本宫六世
    if wai == nei:
        return shi_ying(6)

    # 三世异
    return shi_ying(3)


def _get_palace(mark: str, shi_index: int) -> int:
    """认卦宫——返回宫索引"""
    wai = mark[3:]
    nei = mark[:3]

    # 先判断游魂/归魂
    hun = ''
    if wai[1] == nei[1]:
        if wai[0] != nei[0] and wai[2] != nei[2]:
            hun = '游魂'
    else:
        if wai[0] == nei[0] and wai[2] == nei[2]:
            hun = '归魂'

    if hun == '归魂':
        return YAOS.index(nei)

    if shi_index in (1, 2, 3, 6):
        return YAOS.index(wai)

    # 四五游魂内变更
    if shi_index in (4, 5) or hun == '游魂':
        # 内卦取反
        symbol = ''.join(['1' if c == '0' else '0' for c in nei])
        return YAOS.index(symbol)

    return 0  # fallback


def _get_gua_type(mark: str) -> str:
    """卦象类型"""
    wai = mark[3:]
    nei = mark[:3]

    # 六冲：内外相同
    if wai == nei:
        return '六冲'

    # 游魂/归魂
    if wai[1] == nei[1]:
        if wai[0] != nei[0] and wai[2] != nei[2]:
            return '游魂'
    else:
        if wai[0] == nei[0] and wai[2] == nei[2]:
            return '归魂'

    return ''


def _get_god6_by_day(day_gan: str) -> list:
    """按日干取六神序列"""
    gan_idx = GANS.index(day_gan)
    # 六神起法：甲乙起青龙，丙丁起朱雀，戊日起勾陈，
    # 己日起螣蛇，庚辛起白虎，壬癸起玄武
    god_map = {
        0: 0, 1: 0,   # 甲乙→青龙
        2: 1, 3: 1,   # 丙丁→朱雀
        4: 2,         # 戊→勾陈
        5: 3,         # 己→螣蛇
        6: 4, 7: 4,   # 庚辛→白虎
        8: 5, 9: 5,   # 壬癸→玄武
    }
    start = god_map.get(gan_idx, 0)
    return SHEN6[start:] + SHEN6[:start]


def _get_qin6(gong_wuxing: int, zhi_wuxing: str) -> str:
    """根据宫五行和地支五行求六亲"""
    w2 = XING5.index(zhi_wuxing) if isinstance(zhi_wuxing, str) else zhi_wuxing
    ws = (gong_wuxing - w2) % 5
    return QING6[ws]


def _get_wangshuai(month_zhi: str, zhi: str) -> str:
    """根据月建判断爻的旺相休囚死"""
    if month_zhi not in WANG_XIANG_YUE:
        return '平'
    wx_list = WANG_XIANG_YUE[month_zhi]  # (旺, 相, 休, 囚, 死)
    zhi_wx = ZHI_WUXING.get(zhi, '')
    if zhi_wx == wx_list[0]:
        return '旺'
    elif zhi_wx == wx_list[1]:
        return '相'
    elif zhi_wx == wx_list[2]:
        return '休'
    elif zhi_wx == wx_list[3]:
        return '囚'
    else:
        return '死'


def _get_changsheng(wuxing: str, zhi: str) -> str:
    """求十二长生"""
    if wuxing not in CHANGSHENG:
        return ''
    start = CHANGSHENG[wuxing]
    if zhi not in start:
        return ''
    idx = start.index(zhi)
    return CHANGSHENG_NAMES[idx] if idx < len(CHANGSHENG_NAMES) else ''


def _get_xunkong(day_ganzhi: str) -> str:
    """根据日干支求旬空"""
    gan = day_ganzhi[0]
    zhi = day_ganzhi[1]
    gan_idx = GANS.index(gan)
    zhi_idx = ZHIS.index(zhi)

    # 旬空规则：甲子旬戌亥空，甲戌旬申酉空...
    xun_gap = (zhi_idx - gan_idx) % 12 // 2
    if 0 <= xun_gap < len(KONG):
        return KONG[xun_gap]
    return ''


def _get_bian_mark(params: list) -> Optional[str]:
    """根据动爻生成变卦二进制码"""
    if any(p in (0, 3) for p in params):
        mark = ''.join(['1' if p in (1, 4) else ('0' if p in (0, 3) else str(p % 2)) for p in params])
        # 修正：0=老阴（变阳1），3=老阳（变阴0）
        # 正确逻辑：
        mark_chars = []
        for p in params:
            if p == 0:     # 三阴→变阳
                mark_chars.append('1')
            elif p == 3:   # 三阳→变阴
                mark_chars.append('0')
            elif p == 1:   # 少阳
                mark_chars.append('1')
            elif p == 2:   # 少阴
                mark_chars.append('0')
            else:
                mark_chars.append(str(p % 2))
        return ''.join(mark_chars)
    return None  # 静卦


def _get_hidden_fushen(mark: str, gong_index: int, qin6_list: list) -> Optional[list]:
    """计算伏神"""
    # 如果六亲齐全（6种都有），无伏神
    unique_qin6 = set(qin6_list)
    if len(unique_qin6) >= 5:
        return None

    # 本宫卦的六个爻位
    gong_mark = YAOS[gong_index] * 2
    gong_gz = _get_najia_ganzhi(gong_mark)

    # 求本宫六亲
    gong_wx = (gong_index % 4) + 1  # 乾1兑2离3震4...
    gong_qin6 = []
    for gz in gong_gz:
        zhi = gz[1]
        wuxing = ZHI_WUXING.get(zhi, '')
        if wuxing:
            gong_qin6.append(_get_qin6(gong_wx, wuxing))
        else:
            gong_qin6.append('')

    missing = [q for q in QING6 if q not in unique_qin6]
    if not missing:
        return None

    fushen_list = []
    for miss_q in missing:
        for idx, gq in enumerate(gong_qin6):
            if gq == miss_q:
                fushen_list.append({
                    'shishen': miss_q,
                    'ganzhi': gong_gz[idx][0],
                    'zhi': gong_gz[idx][1],
                    'wuxing': ZHI_WUXING.get(gong_gz[idx][1], ''),
                    'position': idx,
                })
                break
    return fushen_list


# ── 主引擎 ────────────────────────────────────────────────

class LiuyaoEngine:
    """六爻纳甲排盘引擎"""

    def __init__(self, year: int, month: int, day: int,
                 hour: int = 12, minute: int = 0,
                 gender: int = 1):
        self.solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        self.lunar = self.solar.getLunar()
        self.gender = gender
        self.params = None  # 待设定

    def set_params_from_coins(self, coin_results: list):
        """
        从手工掷币结果设定参数

        coin_results: 6个数字，每次三枚硬币的正面（阳面）数
                      - 0 = 三阴（老阴X）
                      - 1 = 一阳（少阳—）
                      - 2 = 二阳（少阴--）
                      - 3 = 三阳（老阳O）
        顺序：从下往上（初爻到上爻）
        """
        assert len(coin_results) == 6, "需要6次掷币结果"
        assert all(0 <= c <= 3 for c in coin_results), "每次数值必须为0~3"
        self.params = coin_results

    def set_params_random(self):
        """随机起卦"""
        import random
        self.params = [random.randint(0, 3) for _ in range(6)]

    def set_params_from_gua(self, ben_gua_mark: str, dong_yaos: Optional[list] = None):
        """
        从特定卦象起卦（用于回测/学习）

        ben_gua_mark: 6位二进制字符串，从下往上
        dong_yaos: 动爻位置列表（如 [1, 3] 表示初爻和三爻动）
        """
        self.params = []
        for i, bit in enumerate(ben_gua_mark):
            if dong_yaos and (i + 1) in dong_yaos:
                self.params.append(3 if bit == '1' else 0)
            else:
                self.params.append(1 if bit == '1' else 2)
        # 注意：params是 (0=老阴, 1=少阳, 2=少阴, 3=老阳)
        # 当我们从二进制码反推时：
        # 二进制1（阳爻）→ 非要动爻则是少阳(1)，要动则是老阳(3)
        # 二进制0（阴爻）→ 非要动则是少阴(2)，要动则是老阴(0)

    def compute(self) -> LiuYaoResult:
        if not self.params:
            raise ValueError("请先设置起卦参数")

        params = self.params
        bazi_list = self.lunar.getBaZi()
        bazi_str = ' '.join(bazi_list) if bazi_list else ''

        # 本卦二进制码：1=阳爻(1或3)，0=阴爻(0或2)
        mark = ''.join(['1' if p in (1, 3) else '0' for p in params])
        ben_name = GUA64.get(mark, '未知卦')

        # 世应
        shi_idx, ying_idx, gong_idx = _set_shi_yao(mark)
        gong_name = GONG8[gong_idx] if 0 <= gong_idx < len(GONG8) else ''

        # 卦象类型
        gua_type = _get_gua_type(mark)

        # 日期信息
        month_zhi = bazi_list[1][1] if len(bazi_list) > 1 else self.lunar.getMonthZhiExact()
        day_ganzhi = bazi_list[2] if len(bazi_list) > 2 else ''
        day_gan = day_ganzhi[0] if day_ganzhi else ''
        day_zhi = day_ganzhi[1] if len(day_ganzhi) > 1 else ''
        if isinstance(month_zhi, str) and len(month_zhi) == 1:
            month_zhi_full = month_zhi
        else:
            month_zhi_full = bazi_list[1][1] if len(bazi_list) > 1 else ''

        # 纳甲
        gz_list = _get_najia_ganzhi(mark)

        # 宫五行（用于六亲判断）
        # 乾兑金(4) 离火(2) 震巽木(1) 坎水(5) 艮坤土(3)
        gong_wx_map = {0: 4, 1: 4, 2: 2, 3: 1, 4: 1, 5: 5, 6: 3, 7: 3}
        gong_wx = gong_wx_map.get(gong_idx, 4)

        # 六神
        shen_list = _get_god6_by_day(day_gan)

        # 旬空
        xunkong = _get_xunkong(day_ganzhi)

        # 动爻
        dong_list = [i for i, p in enumerate(params) if p in (0, 3)]

        # 构建每个爻位
        yaos = []
        for i in range(6):
            idx = 5 - i  # 从下往上，显示时上爻在上
            gz, zhi, gan = gz_list[i]
            yin_yang = '—' if mark[i] == '1' else '--'
            is_moving = i in dong_list
            zhi_wx = ZHI_WUXING.get(zhi, '')
            shishen = _get_qin6(gong_wx, zhi_wx) if zhi_wx else ''

            # 世应标记
            she_ying = ''
            yaos_from_bottom = 5 - i  # 显示顺序（上卦在上）
            if (5 - i + 1) == shi_idx:
                she_ying = '世'
            elif (5 - i + 1) == ying_idx:
                she_ying = '应'

            # 六神
            shen = shen_list[i] if i < len(shen_list) else ''

            # 变卦
            bian_mark = _get_bian_mark(params)
            bian_gz_list = _get_najia_ganzhi(bian_mark) if bian_mark else [('', '', '')] * 6
            b_gz, b_zhi, b_gan = bian_gz_list[i] if bian_mark else ('', '', '')
            b_wx = ZHI_WUXING.get(b_zhi, '')

            yaos.append(YaoPosition(
                index=yaos_from_bottom,
                coin_sum=params[i],
                yin_or_yang=yin_yang,
                is_moving=is_moving,
                zhi=zhi,
                gan=gan,
                wuxing=zhi_wx,
                shishen=shishen,
                she_ying=she_ying,
                shen=shen,
                biangong_zhi=b_zhi,
                biangong_gan=b_gan,
                biangong_wuxing=b_wx,
            ))

        # 变卦
        bian_mark = _get_bian_mark(params)
        bian_name = GUA64.get(bian_mark, '') if bian_mark else None
        if bian_mark:
            _, _, bian_gong_idx = _set_shi_yao(bian_mark)
            bian_gong = GONG8[bian_gong_idx] if 0 <= bian_gong_idx < len(GONG8) else ''
            bian_type = _get_gua_type(bian_mark)
        else:
            bian_gong = None
            bian_type = None

        # 伏神
        qin6_list = [y.shishen for y in yaos]
        fushen = _get_hidden_fushen(mark, gong_idx, qin6_list)

        # 旺衰
        wangshuai = []
        for y in yaos:
            ws = _get_wangshuai(month_zhi_full[:1] if isinstance(month_zhi_full, str) and len(month_zhi_full) > 0 else '', y.zhi)
            wangshuai.append(ws)

        return LiuYaoResult(
            solar_date=str(self.solar),
            lunar_date=str(self.lunar),
            bazi=bazi_str,
            ben_gua_mark=mark,
            ben_gua_name=ben_name,
            ben_gua_gong=gong_name,
            ben_gua_type=gua_type,
            ben_gua_yaos=yaos,
            bian_gua_mark=bian_mark,
            bian_gua_name=bian_name,
            bian_gua_gong=bian_gong,
            bian_gua_type=bian_type,
            fu_shen=fushen if fushen else None,
            month_zhi=month_zhi_full if isinstance(month_zhi_full, str) else str(month_zhi_full),
            day_zhi=day_zhi,
            xunkong=xunkong,
            yaos_wangshuai=wangshuai,
            yong_shen=None,
        )

    def summary(self) -> str:
        """输出可读的排盘结果"""
        r = self.compute()
        lines = []
        lines.append(f"{'=' * 60}")
        lines.append(f"🔮 六爻纳甲排盘")
        lines.append(f"{'=' * 60}")
        lines.append(f"公历: {self.solar}")
        lines.append(f"农历: {self.lunar}")
        lines.append(f"八字: {r.bazi}")
        lines.append(f"旬空: {r.xunkong}")
        lines.append(f"")

        # 变卦部分
        if r.bian_gua_name:
            lines.append(f"本卦: {r.ben_gua_name}[{r.ben_gua_gong}宫] ({r.ben_gua_type})")
            lines.append(f"变卦: {r.bian_gua_name}[{r.bian_gua_gong}宫] ({r.bian_gua_type})")
        else:
            lines.append(f"本卦: {r.ben_gua_name}[{r.ben_gua_gong}宫] ({r.ben_gua_type})【静卦】")
        lines.append(f"")

        # 爻位表格（从下往上，上卦在前）
        lines.append(f"{'爻位':<6} {'阴阳':<4} {'纳甲':<8} {'五行':<4} {'六亲':<6} {'世应':<4} {'六神':<6} {'旺衰':<4} {'动变':<8}")
        lines.append('-' * 60)

        yaos_display = list(reversed(r.ben_gua_yaos))
        for y in yaos_display:
            w_idx = 5 - y.index
            ws = r.yaos_wangshuai[w_idx] if w_idx < len(r.yaos_wangshuai) else ''
            dong_mark = '●' if y.is_moving else ' '
            b_gz = f"{y.biangong_gan}{y.biangong_zhi}" if y.biangong_zhi else ''
            line_str = f"{y.index}爻".ljust(6)
            line_str += f"{y.yin_or_yang:<4}"
            line_str += f"{y.gan}{y.zhi:<7}"
            line_str += f"{y.wuxing:<4}"
            line_str += f"{y.shishen:<6}"
            line_str += f"{y.she_ying:<4}"
            line_str += f"{y.shen:<6}"
            line_str += f"{ws:<4}"
            line_str += f"{dong_mark} {b_gz}" if b_gz else f"{dong_mark} {'':<5}"
            lines.append(line_str)

        lines.append(f"")
        if r.fu_shen:
            lines.append(f"伏神:")
            for fs in r.fu_shen:
                lines.append(f"  {fs['shishen']} {fs['ganzhi']} ({fs['wuxing']})")

        lines.append(f"{'=' * 60}")
        return '\n'.join(lines)

    def dict(self) -> dict:
        """输出JSON序列化结果"""
        r = self.compute()
        return {
            'meta': {
                'solar_date': r.solar_date,
                'lunar_date': r.lunar_date,
                'bazi': r.bazi,
                'gender': '男' if self.gender == 1 else '女',
            },
            'ben_gua': {
                'mark': r.ben_gua_mark,
                'name': r.ben_gua_name,
                'gong': r.ben_gua_gong,
                'type': r.ben_gua_type,
                'yaos': [asdict(y) for y in r.ben_gua_yaos],
            },
            'bian_gua': {
                'mark': r.bian_gua_mark,
                'name': r.bian_gua_name,
                'gong': r.bian_gua_gong,
                'type': r.bian_gua_type,
            } if r.bian_gua_name else None,
            'fu_shen': r.fu_shen,
            'month_zhi': r.month_zhi,
            'day_zhi': r.day_zhi,
            'xunkong': r.xunkong,
            'yaos_wangshuai': r.yaos_wangshuai,
        }


# ── CLI 测试 ──────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    import json

    # 默认随机起卦
    engine = LiuyaoEngine(2026, 5, 2, 14, 53, gender=1)

    if len(sys.argv) >= 7:
        # 手工掷币结果：python liuyao_calc.py 2 1 3 0 2 1
        coins = [int(a) for a in sys.argv[1:7]]
        engine.set_params_from_coins(coins)
    elif len(sys.argv) == 3:
        # 从卦象码起卦：python liuyao_calc.py 111000 1,4
        engine.set_params_from_gua(sys.argv[1], [int(x) for x in sys.argv[2].split(',')] if sys.argv[2] else None)
    else:
        # 随机
        engine.set_params_random()

    if '--json' in sys.argv:
        print(json.dumps(engine.dict(), ensure_ascii=False, indent=2))
    else:
        print(engine.summary())

