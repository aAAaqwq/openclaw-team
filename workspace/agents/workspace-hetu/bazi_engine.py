#!/usr/bin/env python3
"""
bazi_engine.py — 八字排盘引擎 v2.0

基于 lunar-python 1.4.8 重构。
替代原来1173行手写代码，核心逻辑 ~100行。

用法:
    from bazi_engine import BaziEngine
    eng = BaziEngine(2026, 5, 2, 14, 0, gender=1)
    print(eng.summary())
"""

from lunar_python import Solar, Lunar, EightChar
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── 数据结构 ──────────────────────────────────────────────

@dataclass
class Pillar:
    ganzhi: str       # 干支
    nayin: str        # 纳音
    gan: str          # 天干
    zhi: str          # 地支
    gan_index: int    # 天干索引
    zhi_index: int    # 地支索引
    hide_gan: list    # 藏干
    shishen: str      # 十神
    wuxing: str       # 五行
    dishier: str      # 十二长生
    xunkong: str      # 旬空


@dataclass
class BaziResult:
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    day_gan: str               # 日干（元男/元女）
    gender: int                # 0=女, 1=男
    shengxiao: str             # 生肖
    yinyang: str               # 阴阳

    # 神煞
    tai_yuan: str              # 胎元
    tai_yuan_nayin: str        # 胎元纳音
    ming_gong: str             # 命宫
    ming_gong_nayin: str       # 命宫纳音
    shen_gong: str             # 身宫
    shen_gong_nayin: str       # 身宫纳音

    # 大运
    start_age: int             # 起运年龄
    start_year: int            # 起运年份
    forward: bool              # 顺排?
    dayun: list                # 大运列表 [(干支, 起始岁, 终止岁, 起始年, 终止年), ...]
    liunian: list              # 流年

    # 神煞/小数据
    yiyong: list               # 宜/忌
    zhi_xing: str              # 的值
    xiu: str                   # 星宿
    xiu_luck: str              # 星宿吉凶


SHI_SHEN_MAP = {
    ('比', '比'): '比肩', ('比', '劫'): '劫财', ('比', '食'): '食神', ('比', '伤'): '伤官',
    ('比', '才'): '正财', ('比', '财'): '偏财', ('比', '官'): '正官', ('比', '杀'): '七杀',
    ('比', '印'): '正印', ('比', '枭'): '偏印',
}

GAN_WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
ZHI_WUXING = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}


# ── 引擎 ──────────────────────────────────────────────────

class BaziEngine:
    """八字排盘引擎"""

    def __init__(self, year: int, month: int, day: int, hour: int, minute: int = 0,
                 gender: int = 1, tz: int = 8):
        self.solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        self.lunar = Lunar.fromSolar(self.solar)
        self.gender = gender  # 0=女, 1=男
        self.ec = EightChar(self.lunar)

    def _make_pillar(self, gan_fn, zhi_fn, nayin_fn, hide_fn, shishen_gan_fn, shishen_zhi_fn,
                     dishier_fn, xunkong_fn) -> Pillar:
        gan = gan_fn()
        zhi = zhi_fn()
        gz = gan + zhi
        gan_idx = {'甲': 0, '乙': 1, '丙': 2, '丁': 3, '戊': 4, '己': 5, '庚': 6, '辛': 7, '壬': 8, '癸': 9}[gan]
        zhi_idx = {'子': 0, '丑': 1, '寅': 2, '卯': 3, '辰': 4, '巳': 5, '午': 6, '未': 7, '申': 8, '酉': 9, '戌': 10, '亥': 11}[zhi]
        hide = hide_fn()
        shishen_gan = shishen_gan_fn()
        shishen_zhi = shishen_zhi_fn()
        # 取天干十神作为柱的十神
        if isinstance(shishen_gan, str) and shishen_gan.strip():
            shishen = shishen_gan
        else:
            shishen = shishen_zhi[0] if isinstance(shishen_zhi, list) and len(shishen_zhi) > 0 and isinstance(shishen_zhi[0], str) else str(shishen_zhi)
        dishier = dishier_fn()
        xunkong = xunkong_fn()
        nayin = nayin_fn()
        # 五行
        wuxing = GAN_WUXING.get(gan, '')

        return Pillar(
            ganzhi=gz, nayin=nayin, gan=gan, zhi=zhi,
            gan_index=gan_idx, zhi_index=zhi_idx,
            hide_gan=hide if isinstance(hide, list) else [],
            shishen=shishen, wuxing=wuxing,
            dishier=dishier, xunkong=xunkong
        )

    def compute(self) -> BaziResult:
        ec = self.ec

        year = self._make_pillar(
            self.lunar.getYearGanExact, self.lunar.getYearZhiExact,
            ec.getYearNaYin, ec.getYearHideGan,
            ec.getYearShiShenGan, ec.getYearShiShenZhi,
            ec.getYearDiShi, ec.getYearXunKong
        )
        month = self._make_pillar(
            self.lunar.getMonthGanExact, self.lunar.getMonthZhiExact,
            ec.getMonthNaYin, ec.getMonthHideGan,
            ec.getMonthShiShenGan, ec.getMonthShiShenZhi,
            ec.getMonthDiShi, ec.getMonthXunKong
        )
        day = self._make_pillar(
            self.lunar.getDayGanExact, self.lunar.getDayZhiExact,
            ec.getDayNaYin, ec.getDayHideGan,
            # 日柱自身用日支十神
            ec.getDayShiShenGan, ec.getDayShiShenZhi,
            ec.getDayDiShi, ec.getDayXunKong
        )
        hour = self._make_pillar(
            self.lunar.getTimeGan, self.lunar.getTimeZhi,
            ec.getTimeNaYin, ec.getTimeHideGan,
            ec.getTimeShiShenGan, ec.getTimeShiShenZhi,
            ec.getTimeDiShi, ec.getTimeXunKong
        )

        # 大运
        yun = ec.getYun(self.gender)
        dayun_list = []
        for d in yun.getDaYun():
            dayun_list.append((
                d.getGanZhi(),
                d.getStartAge(), d.getEndAge(),
                d.getStartYear(), d.getEndYear()
            ))

        liunian_list = None  # 延迟计算，需要时调用 _compute_liunian()

        # 取日建宜忌
        yiyong = self.lunar.getDayYi()
        if not yiyong:
            yiyong = self.lunar.getDayJi()

        return BaziResult(
            year=year, month=month, day=day, hour=hour,
            day_gan=ec.getDayGan(),
            gender=self.gender,
            shengxiao=self.lunar.getYearShengXiao(),
            yinyang=self.lunar.getYinYang() if hasattr(self.lunar, 'getYinYang') else '阳',
            tai_yuan=ec.getTaiYuan(),
            tai_yuan_nayin=ec.getTaiYuanNaYin(),
            ming_gong=ec.getMingGong(),
            ming_gong_nayin=ec.getMingGongNaYin(),
            shen_gong=ec.getShenGong(),
            shen_gong_nayin=ec.getShenGongNaYin(),
            start_age=yun.getStartYear(),
            start_year=yun.getStartSolar().getYear() if yun.getStartSolar() else 0,
            forward=yun.isForward(),
            dayun=dayun_list,
            liunian=liunian_list,
            yiyong=yiyong if yiyong else [],
            zhi_xing=self.lunar.getZhiXing(),
            xiu=self.lunar.getXiu(),
            xiu_luck=self.lunar.getXiuLuck()
        )

    def summary(self) -> str:
        r = self.compute()
        lines = []
        lines.append(f"八字: {r.year.ganzhi} {r.month.ganzhi} {r.day.ganzhi} {r.hour.ganzhi}")
        lines.append(f"纳音: {r.year.nayin} {r.month.nayin} {r.day.nayin} {r.hour.nayin}")
        lines.append(f"日干: {r.day_gan} 生肖: {r.shengxiao}")
        lines.append(f"")
        for label, p in [('年柱', r.year), ('月柱', r.month), ('日柱', r.day), ('时柱', r.hour)]:
            lines.append(f"{label}: {p.ganzhi} 纳音={p.nayin} 十神={p.shishen} 藏干={''.join(p.hide_gan)} 长生={p.dishier} 空亡={p.xunkong}")
        lines.append(f"")
        lines.append(f"胎元: {r.tai_yuan}({r.tai_yuan_nayin})  命宫: {r.ming_gong}({r.ming_gong_nayin})  身宫: {r.shen_gong}({r.shen_gong_nayin})")
        lines.append(f"起运: {r.start_age}岁({r.start_year}年)  {'顺' if r.forward else '逆'}排")
        lines.append(f"大运:")
        for gz, sa, ea, sy, ey in r.dayun:
            lines.append(f"  {gz}: {sa}~{ea}岁 ({sy}~{ey})")
        lines.append(f"星宿: {r.xiu}({r.xiu_luck})  的值: {r.zhi_xing}")
        return '\n'.join(lines)

    def _compute_liunian(self) -> list:
        """延迟计算流年"""
        yun = self.ec.getYun(self.gender)
        result = []
        for d in yun.getDaYun():
            for ln in d.getLiuNian():
                result.append({
                    'year': ln.getYear(),
                    'ganzhi': ln.getGanZhi(),
                    'age': ln.getAge()
                })
        return result

    def dict(self) -> dict:
        r = self.compute()
        return {
            'bazi': f"{r.year.ganzhi} {r.month.ganzhi} {r.day.ganzhi} {r.hour.ganzhi}",
            'pillars': {
                'year': asdict(r.year),
                'month': asdict(r.month),
                'day': asdict(r.day),
                'hour': asdict(r.hour),
            },
            'day_gan': r.day_gan,
            'gender': '男' if r.gender == 1 else '女',
            'shengxiao': r.shengxiao,
            'tai_yuan': f"{r.tai_yuan}({r.tai_yuan_nayin})",
            'ming_gong': f"{r.ming_gong}({r.ming_gong_nayin})",
            'shen_gong': f"{r.shen_gong}({r.shen_gong_nayin})",
            'start_age': r.start_age,
            'start_year': r.start_year,
            'forward': r.forward,
            'dayun': [{'ganzhi': gz, 'start_age': sa, 'end_age': ea, 'start_year': sy, 'end_year': ey}
                      for gz, sa, ea, sy, ey in r.dayun],
            'liunian': self._compute_liunian(),
            'xiu': f"{r.xiu}({r.xiu_luck})",
            'zhi_xing': r.zhi_xing,
        }


# ── CLI Test ──────────────────────────────────────────────

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

    eng = BaziEngine(y, m, d, h, mi, gender=g)
    print(eng.summary())
