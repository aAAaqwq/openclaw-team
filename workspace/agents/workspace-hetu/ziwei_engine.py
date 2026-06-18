#!/usr/bin/env python3
"""
ziwei_engine.py — 紫微斗数排盘引擎 v2.0

基于 iztro 2.5.8 (Node.js) 桥接。
替代原来数百行手写紫微排盘逻辑。

用法:
    from ziwei_engine import ZiweiEngine
    eng = ZiweiEngine(2026, 5, 2, 14, 0, gender=1)
    print(eng.summary())
"""

import json
import subprocess
import os
from dataclasses import dataclass, asdict
from typing import Optional


# ── 数据结构 ──────────────────────────────────────────────

@dataclass
class StarInfo:
    name: str
    type: str
    brightness: str
    mutagen: str

@dataclass
class Palace:
    index: int
    name: str
    earthly_branch: str
    heavenly_stem: str
    major_stars: list
    minor_stars: list
    adj_stars: list
    changsheng12: str
    boshi12: str
    jiangqian12: str
    suiqian12: str
    decadal: dict
    ages: list

@dataclass
class ZiweiResult:
    bazi: str
    gender: str
    lunar_date: str
    solar_date: str
    time: str
    time_range: str
    zodiac: str
    sign: str
    five_elements_class: str
    soul: str
    body: str
    soul_branch: str
    body_branch: str
    palaces: list
    transformations: list


SHI_ER_GONG = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄',
               '迁移', '交友', '官禄', '田宅', '福德', '父母']


# ── 引擎 ──────────────────────────────────────────────────

IZTRO_BIN = '/Users/peterqiu/.npm-global/lib/node_modules/iztro'

# 用脚本文件方式避免字符串转义麻烦
IZTRO_JS = os.path.join(os.path.dirname(__file__), '.iztro_bridge.js')


def _write_bridge():
    """写入桥接脚本文件"""
    js = r"""const { astro } = require('/Users/peterqiu/.npm-global/lib/node_modules/iztro');

function toTimeIndex(hour, minute) {
    const shichen = [
        [23, 1, 0], [1, 3, 1], [3, 5, 2], [5, 7, 3],
        [7, 9, 4], [9, 11, 5], [11, 13, 6], [13, 15, 7],
        [15, 17, 8], [17, 19, 9], [19, 21, 10], [21, 23, 11],
    ];
    for (const [start, end, idx] of shichen) {
        if (hour >= start && hour < end) return idx;
        if (start === 23 && (hour >= 23 || hour < 1)) return 0;
    }
    return Math.floor(hour / 2) % 12;
}

// 从 stdin 读取参数
const raw = require('fs').readFileSync('/dev/stdin', 'utf8').trim();
const args = JSON.parse(raw);
const hour = args.hour;
const minute = args.minute;
const timeIndex = toTimeIndex(hour, minute);

const star = astro.bySolar(args.date, timeIndex, args.gender);

const result = {
    bazi: star.chineseDate,
    gender: star.gender,
    lunarDate: star.lunarDate,
    solarDate: star.solarDate,
    time: star.time,
    timeRange: star.timeRange,
    zodiac: star.zodiac,
    sign: star.sign,
    fiveElementsClass: star.fiveElementsClass,
    soul: star.soul,
    body: star.body,
    soulBranch: star.earthlyBranchOfSoulPalace,
    bodyBranch: star.earthlyBranchOfBodyPalace,
    palaces: star.palaces.map(p => ({
        index: p.index,
        name: p.name,
        earthlyBranch: p.earthlyBranch,
        heavenlyStem: p.heavenlyStem,
        majorStars: (p.majorStars || []).map(s => ({
            name: s.name, type: s.type, brightness: s.brightness || '', mutagen: s.mutagen || ''
        })),
        minorStars: (p.minorStars || []).map(s => ({
            name: s.name, type: s.type, brightness: '', mutagen: ''
        })),
        adjStars: (p.adjectiveStars || []).map(s => ({
            name: s.name, type: s.type, brightness: '', mutagen: ''
        })),
        changsheng12: p.changsheng12 || '',
        boshi12: p.boshi12 || '',
        jiangqian12: p.jiangqian12 || '',
        suiqian12: p.suiqian12 || '',
        decadal: p.decadal,
        ages: p.ages || []
    })),
    transformations: []
};

for (const p of star.palaces) {
    for (const s of (p.majorStars || [])) {
        if (s.mutagen) {
            result.transformations.push({
                palace: p.name,
                star: s.name,
                mutagen: s.mutagen
            });
        }
    }
}

console.log(JSON.stringify(result));
"""
    with open(IZTRO_JS, 'w') as f:
        f.write(js)


class ZiweiEngine:
    """紫微斗数排盘引擎"""

    def __init__(self, year: int, month: int, day: int,
                 hour: int, minute: int = 0,
                 gender: int = 1):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.gender = 'male' if gender == 1 else 'female'
        self._result: Optional[ZiweiResult] = None

        if not os.path.exists(IZTRO_JS):
            _write_bridge()

    def _gender_cn(self):
        return '男' if self.gender == 'male' else '女'

    def compute(self) -> ZiweiResult:
        if self._result:
            return self._result

        args_json = json.dumps({
            'date': f'{self.year}-{self.month}-{self.day}',
            'hour': self.hour,
            'minute': self.minute,
            'gender': self.gender,
        })

        proc = subprocess.run(
            ['node', IZTRO_JS],
            input=args_json,
            capture_output=True, text=True, timeout=30
        )

        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            raise RuntimeError(f"iztro 失败: {stderr or '未知错误'}")

        data = json.loads(proc.stdout.strip())

        palaces = []
        for p in data['palaces']:
            palaces.append(Palace(
                index=p['index'],
                name=p['name'],
                earthly_branch=p['earthlyBranch'],
                heavenly_stem=p['heavenlyStem'],
                major_stars=[StarInfo(**s) for s in p['majorStars']],
                minor_stars=[StarInfo(**s) for s in p['minorStars']],
                adj_stars=[StarInfo(**s) for s in p['adjStars']],
                changsheng12=p['changsheng12'],
                boshi12=p['boshi12'],
                jiangqian12=p['jiangqian12'],
                suiqian12=p['suiqian12'],
                decadal=p['decadal'],
                ages=p['ages'],
            ))

        self._result = ZiweiResult(
            bazi=data['bazi'],
            gender=self._gender_cn(),
            lunar_date=data['lunarDate'],
            solar_date=data['solarDate'],
            time=data['time'],
            time_range=data['timeRange'],
            zodiac=data['zodiac'],
            sign=data['sign'],
            five_elements_class=data['fiveElementsClass'],
            soul=data['soul'],
            body=data['body'],
            soul_branch=data['soulBranch'],
            body_branch=data['bodyBranch'],
            palaces=palaces,
            transformations=data['transformations'],
        )
        return self._result

    def summary(self) -> str:
        r = self.compute()
        lines = []
        lines.append(f"紫微斗数 · {r.solar_date} {r.time}")
        lines.append(f"八字: {r.bazi}")
        lines.append(f"生肖: {r.zodiac}  星座: {r.sign}  五行局: {r.five_elements_class}")
        lines.append(f"命主: {r.soul}({r.soul_branch})  身主: {r.body}({r.body_branch})")
        lines.append("")

        for p in r.palaces:
            name = SHI_ER_GONG[p.index] if p.index < len(SHI_ER_GONG) else p.name
            major_list = [f"{s.name}({s.brightness})" for s in p.major_stars] if p.major_stars else ['-']
            minor_list = [s.name for s in p.minor_stars] if p.minor_stars else ['-']
            adj_list = [s.name for s in p.adj_stars] if p.adj_stars else ['-']
            dr = p.decadal['range']
            lines.append(f"{name}[{p.earthly_branch}]: 主[{', '.join(major_list)}] 辅[{', '.join(minor_list)}] 杂[{', '.join(adj_list)}]")
            lines.append(f"  大限: {dr[0]}~{dr[1]}岁  长生: {p.changsheng12}")

        if r.transformations:
            lines.append("")
            hua_strs = [f'{h["palace"]}: {h["star"]}({h["mutagen"]})' for h in r.transformations]
            lines.append(f"四化: {' | '.join(hua_strs)}")

        return '\n'.join(lines)

    def dict(self) -> dict:
        r = self.compute()
        return {
            'bazi': r.bazi,
            'gender': r.gender,
            'lunar_date': r.lunar_date,
            'solar_date': r.solar_date,
            'time': r.time,
            'time_range': r.time_range,
            'zodiac': r.zodiac,
            'sign': r.sign,
            'five_elements_class': r.five_elements_class,
            'soul': f"{r.soul}({r.soul_branch})",
            'body': f"{r.body}({r.body_branch})",
            'palaces': [asdict(p) for p in r.palaces],
            'transformations': r.transformations,
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

    eng = ZiweiEngine(y, m, d, h, mi, gender=g)
    print(eng.summary())
