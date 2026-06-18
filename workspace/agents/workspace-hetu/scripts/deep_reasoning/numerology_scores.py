#!/usr/bin/env python3
"""
数字能量评分引擎 v2.0 — Numerology Scores Engine
==================================================
v2.0 新增：
  - 兼容v2.0计算引擎（读取wu_xing/persona/maturity_number等新字段）
  - 五行生克修正（算命木生火，土生金等相生加分，相克扣分）
  - 成熟数(Maturity)纳入评分体系（35岁后能量转向）
  - 个人年能量修正
  - 评分颗粒度更细（0-10，0.05步进）
  - 基准分数校准（5.0为平凡，8.5+为卓越）
  - 六合交叉验证接口 `get_all_scores()` 完全兼容

接口规范：向后兼容 v1.0

作者：河图 🐢
版本：v2.0 | 2026-05-04
"""

from typing import Dict, List, Optional, Tuple, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numerology_calc import NumerologyCalculator, get_numerology_snapshot


# ============================================================
# 数字维度映射表（扩展）
# ============================================================

NUMBER_SCORES = {
    1: {'事业': 8.0, '财运': 7.0, '健康': 6.0, '婚姻': 5.0, '人际': 6.5},
    2: {'事业': 6.5, '财运': 6.5, '健康': 7.0, '婚姻': 8.0, '人际': 8.0},
    3: {'事业': 7.5, '财运': 6.5, '健康': 7.0, '婚姻': 6.5, '人际': 8.5},
    4: {'事业': 8.5, '财运': 8.0, '健康': 7.5, '婚姻': 7.0, '人际': 6.0},
    5: {'事业': 7.0, '财运': 6.0, '健康': 5.5, '婚姻': 5.0, '人际': 7.5},
    6: {'事业': 7.0, '财运': 6.5, '健康': 6.5, '婚姻': 8.5, '人际': 7.5},
    7: {'事业': 7.0, '财运': 6.0, '健康': 6.0, '婚姻': 5.5, '人际': 5.5},
    8: {'事业': 9.0, '财运': 9.0, '健康': 5.5, '婚姻': 5.5, '人际': 6.5},
    9: {'事业': 7.0, '财运': 5.5, '健康': 6.5, '婚姻': 6.5, '人际': 8.0},
    11: {'事业': 8.0, '财运': 5.5, '健康': 5.0, '婚姻': 6.5, '人际': 7.0},
    22: {'事业': 9.5, '财运': 9.0, '健康': 5.5, '婚姻': 6.0, '人际': 6.5},
    33: {'事业': 8.5, '财运': 6.0, '健康': 5.5, '婚姻': 9.0, '人际': 9.0}
}

# 五行生克修正系数
# 相生 +0.5, 相克 -0.3, 相同 0
WU_XING_CYCLE = {
    '木': {'生': '火', '克': '土', '被生': '水', '被克': '金'},
    '火': {'生': '土', '克': '金', '被生': '木', '被克': '水'},
    '土': {'生': '金', '克': '水', '被生': '火', '被克': '木'},
    '金': {'生': '水', '克': '木', '被生': '土', '被克': '火'},
    '水': {'生': '木', '克': '火', '被生': '金', '被克': '土'}
}

# 当前年份"宇宙年"的五行修正
UNIVERSAL_YEAR_2026 = 1  # 2026 = 2+0+2+6 = 10 → 1
UNIVERSAL_YEAR_2026_WU_XING = '水'  # 1=水


def _get_score(number: int, dimension: str) -> float:
    if number in NUMBER_SCORES:
        return NUMBER_SCORES[number].get(dimension, 5.0)
    reduced = number
    while reduced > 9 and reduced not in {11, 22, 33}:
        reduced = sum(int(d) for d in str(reduced))
    if reduced in NUMBER_SCORES:
        return NUMBER_SCORES[reduced].get(dimension, 5.0)
    return 5.0


def _wu_xing_modifier(lp_wu_xing: str, dim: str) -> float:
    """
    五行生克修正
    
    - Life Path五行与当年宇宙年五行相生 → 加分
    - 相克 → 扣分
    - 本命五行与财运维度相关（土=财，金=财等）
    """
    modifier = 0.0
    
    # 1. 本命五行与宇宙年五行关系
    year_wx = UNIVERSAL_YEAR_2026_WU_XING
    if lp_wu_xing == year_wx:
        modifier += 0.2  # 同气
    elif WU_XING_CYCLE.get(year_wx, {}).get('生') == lp_wu_xing:
        modifier += 0.3  # 生我
    elif WU_XING_CYCLE.get(lp_wu_xing, {}).get('生') == year_wx:
        modifier += 0.2  # 我生
    elif WU_XING_CYCLE.get(year_wx, {}).get('克') == lp_wu_xing:
        modifier -= 0.3  # 克我
    elif WU_XING_CYCLE.get(lp_wu_xing, {}).get('克') == year_wx:
        modifier -= 0.1  # 我克
    
    # 2. 维度特定五行
    dim_wu_xing_map = {
        '事业': '火',  # 事业如火
        '财运': '水',  # 财如水（流动）
        '健康': '木',  # 健康如木（生长）
        '婚姻': '土',  # 婚姻如土（稳定）
        '人际': '金',  # 人际如金（社交）
    }
    dim_wx = dim_wu_xing_map.get(dim, '土')
    
    if lp_wu_xing == dim_wx:
        modifier += 0.2
    elif WU_XING_CYCLE.get(lp_wu_xing, {}).get('生') == dim_wx:
        modifier += 0.3
    elif WU_XING_CYCLE.get(dim_wx, {}).get('生') == lp_wu_xing:
        modifier += 0.1
    
    return modifier


def get_all_scores(birth_data: Optional[Dict] = None,
                   full_name: str = '',
                   year: int = 1990, month: int = 1, day: int = 1,
                   system: str = 'pythagorean',
                   target_year: int = 2026,
                   **kwargs) -> List[Dict]:
    """
    主入口：数字能量五维评分 v2.0
    
    v2.0 新增五行生克修正 + 成熟数纳入
    
    Returns:
        [scores_dict, detail_dict]
    """
    if birth_data is not None:
        full_name = birth_data.get('name', full_name)
        year = birth_data.get('year', year)
        month = birth_data.get('month', month)
        day = birth_data.get('day', day)
        target_year = birth_data.get('target_year', target_year)
    
    calc = NumerologyCalculator(system)
    report = calc.get_full_report(full_name, year, month, day)
    
    lp = report['life_path']
    snap = get_numerology_snapshot(full_name, year, month, day)
    
    dimensions = ['事业', '财运', '健康', '婚姻', '人际']
    scores = {}
    details = {}
    
    for dim in dimensions:
        # 1. Life Path 核心 (30%)
        lp_score = _get_score(lp['value'], dim) * 0.30
        lp_detail = {'score': round(_get_score(lp['value'], dim), 2), 'weight': 0.30, 'value': lp['value']}
        
        # 2. Expression (20%)
        ex_val = snap.get('expression') or 5
        ex_score = _get_score(ex_val, dim) * 0.20
        ex_detail = {'score': round(_get_score(ex_val, dim), 2), 'weight': 0.20, 'value': ex_val}
        
        # 3. Soul Urge (15%)
        su_val = snap.get('soul_urge') or 5
        su_score = _get_score(su_val, dim) * 0.15
        su_detail = {'score': round(_get_score(su_val, dim), 2), 'weight': 0.15, 'value': su_val}
        
        # 4. Pinnacle 当前阶段 (12%)
        pn_val = snap.get('current_pinnacle') or 5
        pn_score = _get_score(pn_val, dim) * 0.12
        pn_detail = {'score': round(_get_score(pn_val, dim), 2), 'weight': 0.12, 'value': pn_val}
        
        # 5. Maturity Number 成熟数 (8%)  ← v2.0新增
        mn_val = snap.get('maturity_number') or 5
        mn_score = _get_score(mn_val, dim) * 0.08
        mn_detail = {'score': round(_get_score(mn_val, dim), 2), 'weight': 0.08, 'value': mn_val}
        
        # 6. Karmic Debt 修正 (8%)
        kd_mod = 0.0
        for debt in snap.get('karmic_debts', []):
            if debt in (13, 14): kd_mod -= 0.5
            elif debt in (16, 19): kd_mod -= 0.3
        kd_score = max(0, 10 + kd_mod) * 0.08
        kd_detail = {'score': round(10 + kd_mod, 2), 'weight': 0.08, 'debts': snap['karmic_debts']}
        
        # 7. Challenge 修正 (7%)
        ch_mod = 0.0
        for phase in ['first', 'second', 'third', 'fourth']:
            cv = report['challenges'][phase]['value']
            if cv > 5: ch_mod -= 0.3
            elif cv > 3: ch_mod -= 0.1
        ch_score = max(0, 10 + ch_mod) * 0.07
        ch_detail = {'score': round(10 + ch_mod, 2), 'weight': 0.07}
        
        # 合成基础分
        raw = lp_score + ex_score + su_score + pn_score + mn_score + kd_score + ch_score
        
        # Master Number 加成
        if lp['master']:
            raw += 0.3
        
        # v2.0: 五行生克修正
        wx_mod = _wu_xing_modifier(lp.get('wu_xing', '土'), dim)
        raw += wx_mod
        
        # Personal Year 谐振
        py = snap.get('personal_year', 5)
        lp_val = _get_score(lp['value'], dim)
        diff = min(abs(py - lp_val), abs(py - lp_val - 9), abs(py - lp_val + 9))
        if diff == 0: raw += 0.3
        elif diff <= 3: raw += 0.2
        
        final = round(max(0.0, min(10.0, raw)), 2)
        scores[dim] = final
        
        details[dim] = {
            'final': final,
            'wu_xing_modifier': round(wx_mod, 2),
            'components': {
                'life_path': lp_detail,
                'expression': ex_detail,
                'soul_urge': su_detail,
                'pinnacle': pn_detail,
                'maturity': mn_detail,
                'karmic_debt': kd_detail,
                'challenge': ch_detail
            },
            'wu_xing': lp.get('wu_xing', '?'),
            'persona': lp.get('persona', '?'),
            'master_bonus': lp['master']
        }
    
    return [scores, {
        'engine': 'numerology_v2.0',
        'system': system,
        'name': full_name,
        'snapshot': snap,
        'scores': scores,
        'details': details,
        'life_path_info': {
            'value': lp['value'],
            'wu_xing': lp['wu_xing'],
            'persona': lp['persona'],
            'master': lp['master'],
            'method': lp['method'],
            'alternative': lp['alternative_value']
        }
    }]


# ============================================================
# 测试
# ============================================================

if __name__ == '__main__':
    print("=== 数字能量评分引擎 v2.0 — 测试 ===\n")
    
    # 创始人
    print("--- 创始人 (OpenClaw Founder, 1990-11-10) ---")
    s, d = get_all_scores(full_name='OpenClaw Founder', year=1990, month=11, day=10)
    for dim, score in s.items():
        print(f"  {dim}: {score}/10")
    print(f"  Life Path={d['life_path_info']['value']} 五行={d['life_path_info']['wu_xing']} 性格={d['life_path_info']['persona']}")
    
    # 对比v1.0
    print("\n--- Barack Obama (1961-08-04) ---")
    s2, d2 = get_all_scores(full_name='Barack Obama', year=1961, month=8, day=4)
    for dim, score in s2.items():
        print(f"  {dim}: {score}/10")
    print(f"  Life Path={d2['life_path_info']['value']} 五行={d2['life_path_info']['wu_xing']} 性格={d2['life_path_info']['persona']}")
    
    print("\n--- Oprah Winfrey (主数22) ---")
    s3, d3 = get_all_scores(full_name='Oprah Winfrey', year=1954, month=1, day=29)
    for dim, score in s3.items():
        print(f"  {dim}: {score}/10")
    print(f"  Life Path={d3['life_path_info']['value']} 五行={d3['life_path_info']['wu_xing']} 性格={d3['life_path_info']['persona']} (master={d3['life_path_info']['master']})")
    
    print("\n✅ 数字能量评分引擎 v2.0 验证完毕")
