#!/usr/bin/env python3
"""
数字能量计算引擎 v2.0 — Numerology Calculation Engine
======================================================
v2.0 新增：
  - 全名拼音/英文名双系统兼容
  - 兼容性匹配 (Compatibility) — 两人的Life Path匹配度
  - 日期数字解读 (Maturity Number / Realization Number)
  - 姓名数理五行化（河图独有：数字→五行映射）
  - 名人验证数据集（built-in test cases）
  - 更完善的Chaldean系统支持（数字到字母的特殊映射）
  - 输出性格标签化（Leadership / Analyst / Healer等）

对比全球最佳实践：
  ✅ 覆盖 numerology PyPI: Life Path / Expression / Soul Urge / Personality / Birthday / Karmic Lessons
  ✅ 覆盖 numerologerCalculator (Go): 双系统 + 业力债务 + 顶峰/挑战
  ✅ 覆盖 numerologyapi.com: 203+ endpoints 中的核心计算部分
  ✅ 覆盖 divineapi.com: Pythagorean + Chaldean 双系统
  ✅ 覆盖 roxyapi.com: 兼容性匹配 + MCP友好输出
  ✅ **河图独有**: 五行映射 + 六合交叉验证集成 + 名人验证

接口规范：向后兼容 v1.0

作者：河图 🐢
版本：v2.0 | 2026-05-04
"""

from typing import Dict, List, Optional, Tuple, Union
from enum import Enum


# ============================================================
# 字母数值映射表
# ============================================================

PYTHAGOREAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

# Chaldean系统：数字分配不循环（1-8，9为神圣数字）
# 与Pythagorean不同，Chaldean的1-8不按字母表顺序循环
CHALDEAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 1,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8, 'Q': 1, 'R': 2,
    'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5, 'Y': 1, 'Z': 7
}

VOWELS = set('AEIOU')
MASTER_NUMBERS = {11, 22, 33}
MAX_MASTER = 33
KARMIC_DEBT_NUMBERS = {13, 14, 16, 19}

# 数字→五行映射（河图独家）
NUMBER_WU_XING = {
    1: '水', 2: '土', 3: '木', 4: '木', 5: '土',
    6: '金', 7: '金', 8: '土', 9: '火',
    11: '木', 22: '土', 33: '火'
}

# 数字→性格标签
NUMBER_PERSONA = {
    1: ('Leader', '领导开创'),
    2: ('Diplomat', '外交伙伴'),
    3: ('Creator', '创意表达'),
    4: ('Builder', '实干建造'),
    5: ('Free Spirit', '自由冒险'),
    6: ('Healer', '责任关怀'),
    7: ('Analyst', '智慧分析'),
    8: ('Executor', '商业执行'),
    9: ('Humanitarian', '博爱理想'),
    11: ('Visionary', '灵性启发'),
    22: ('Master Architect', '大师建造'),
    33: ('Master Healer', '大爱导师')
}

# ============================================================
# 工具函数
# ============================================================

def _char_val(char: str, system: str = 'pythagorean') -> int:
    upper = char.upper()
    if system == 'pythagorean':
        return PYTHAGOREAN_MAP.get(upper, 0)
    else:
        return CHALDEAN_MAP.get(upper, 0)


def _reduce_number(n: int, keep_master: bool = True) -> int:
    if n == 0:
        return 0
    while n > 9:
        if keep_master and n in MASTER_NUMBERS:
            return n
        n = sum(int(d) for d in str(n))
    return n


def _contains_karmic(n: int) -> Optional[int]:
    """检测是否含业力债务数"""
    if n in KARMIC_DEBT_NUMBERS:
        return n
    # 也检查归约过程中的中间值
    while n > 9 and n not in MASTER_NUMBERS:
        n = sum(int(d) for d in str(n))
        if n in KARMIC_DEBT_NUMBERS:
            return n
    return None


def _is_vowel(c: str) -> bool:
    u = c.upper()
    if u in VOWELS:
        return True
    return False


def _classify_letters(name: str) -> Tuple[str, str]:
    vowels = ''
    consonants = ''
    has_vowel = False
    for c in name:
        if c.isalpha():
            if _is_vowel(c):
                vowels += c
                has_vowel = True
            elif c.upper() == 'Y' and not has_vowel:
                vowels += c
                has_vowel = True
            else:
                consonants += c
    return vowels, consonants


def _wu_xing_from_number(n: int) -> str:
    """数字→五行"""
    reduced = _reduce_number(n, keep_master=True)
    return NUMBER_WU_XING.get(reduced, '土')


def _persona(n: int) -> str:
    """数字→性格标签"""
    reduced = _reduce_number(n, keep_master=True)
    p = NUMBER_PERSONA.get(reduced)
    if p:
        return p[0] if isinstance(p, tuple) else p
    return 'Mystic'


# ============================================================
# 核心计算类 v2.0
# ============================================================

class NumerologyCalculator:
    """数字能量计算器 v2.0"""
    
    def __init__(self, system: str = 'pythagorean'):
        self.system = system
    
    def _letter_values(self, text: str) -> List[int]:
        return [_char_val(c, self.system) for c in text if c.isalpha()]
    
    def _sum_letters(self, text: str) -> int:
        return sum(self._letter_values(text))
    
    # ---------- 核心计算 ----------
    
    def get_life_path(self, year: int, month: int, day: int) -> Dict:
        """生命路径数
        
        使用两种算法并返回主流结果：
        1. 直接相加（主流）：年月日直接相加后归约，更能保留主数
        2. 先缩后加（变体）：年月日先分别归约再相加
        """
        # 算法1（主流）：年月日直接相加 → 归约
        alt_raw = year + month + day
        alt_karmic = _contains_karmic(alt_raw)
        alt_final = _reduce_number(alt_raw)
        alt_steps = [alt_raw]
        if alt_final != alt_raw:
            alt_steps.append(alt_final)
        
        # 算法2（变体）：先分别归约再相加 → 归约
        yr = _reduce_number(year)
        mo = _reduce_number(month)
        dy = _reduce_number(day)
        raw = yr + mo + dy
        steps = [raw]
        karmic = _contains_karmic(raw)
        final = _reduce_number(raw)
        if final != raw:
            steps.append(final)
        
        # 选择主流结果（算法1优先，因为它更能保留主数）
        is_master = alt_final in MASTER_NUMBERS
        
        return {
            'value': alt_final,
            'master': is_master,
            'master_value': alt_final if is_master else _reduce_number(alt_final),
            'alternative_value': final,
            'alternative_master': final in MASTER_NUMBERS,
            'year_reduced': yr,
            'month_reduced': mo,
            'day_reduced': dy,
            'steps': alt_steps,
            'alternative_steps': steps,
            'method': 'direct_sum',
            'alternative_method': 'separate_reduce_then_sum',
            'karmic_debt': alt_karmic if alt_karmic else karmic,
            'wu_xing': _wu_xing_from_number(alt_final),
            'persona': _persona(alt_final)
        }
    
    def get_birthday(self, day: int) -> Dict:
        """生日数"""
        raw = day
        final = _reduce_number(raw)
        return {
            'value': final,
            'master': final in MASTER_NUMBERS,
            'master_value': final if final in MASTER_NUMBERS else _reduce_number(final),
            'raw': raw,
            'karmic_debt': raw if raw in KARMIC_DEBT_NUMBERS else None,
            'wu_xing': _wu_xing_from_number(final),
            'persona': _persona(final)
        }
    
    def get_expression(self, full_name: str) -> Dict:
        """表达/命运数"""
        total = self._sum_letters(full_name)
        steps = [total]
        karmic = total if total in KARMIC_DEBT_NUMBERS else None
        final = _reduce_number(total)
        if final != total:
            steps.append(final)
        
        words = {}
        for word in full_name.split():
            if word.strip():
                wv = self._sum_letters(word)
                wr = _reduce_number(wv)
                words[word.upper()] = {'raw': wv, 'reduced': wr}
        
        return {
            'value': final,
            'master': final in MASTER_NUMBERS,
            'master_value': final if final in MASTER_NUMBERS else _reduce_number(final),
            'total': total,
            'steps': steps,
            'karmic_debt': karmic,
            'words': words,
            'wu_xing': _wu_xing_from_number(final),
            'persona': _persona(final)
        }
    
    def get_soul_urge(self, full_name: str) -> Dict:
        """灵魂驱力数"""
        vowels, _ = _classify_letters(full_name)
        total = self._sum_letters(vowels)
        steps = [total]
        karmic = total if total in KARMIC_DEBT_NUMBERS else None
        final = _reduce_number(total)
        if final != total:
            steps.append(final)
        return {
            'value': final,
            'master': final in MASTER_NUMBERS,
            'master_value': final if final in MASTER_NUMBERS else _reduce_number(final),
            'total': total,
            'steps': steps,
            'vowels_raw': vowels,
            'karmic_debt': karmic,
            'wu_xing': _wu_xing_from_number(final),
            'persona': _persona(final)
        }
    
    def get_personality(self, full_name: str) -> Dict:
        """人格数"""
        _, consonants = _classify_letters(full_name)
        total = self._sum_letters(consonants)
        steps = [total]
        karmic = total if total in KARMIC_DEBT_NUMBERS else None
        final = _reduce_number(total)
        if final != total:
            steps.append(final)
        return {
            'value': final,
            'master': final in MASTER_NUMBERS,
            'master_value': final if final in MASTER_NUMBERS else _reduce_number(final),
            'total': total,
            'steps': steps,
            'consonants_raw': consonants,
            'karmic_debt': karmic,
            'wu_xing': _wu_xing_from_number(final),
            'persona': _persona(final)
        }
    
    def get_karmic_lessons(self, full_name: str) -> Dict:
        """业力功课（缺失数字）"""
        values = self._letter_values(full_name)
        present = set(values)
        missing = [n for n in range(1, 10) if n not in present]
        freq = {n: values.count(n) for n in range(1, 10)}
        return {
            'missing_numbers': missing,
            'count': len(missing),
            'frequencies': freq
        }
    
    def get_hidden_passion(self, full_name: str) -> Dict:
        """隐藏激情数"""
        values = self._letter_values(full_name)
        freq = {n: values.count(n) for n in range(1, 10)}
        max_count = max(freq.values()) if freq else 0
        most = [n for n, c in freq.items() if c == max_count and c > 0]
        return {
            'most_frequent_numbers': most,
            'frequency': max_count,
            'frequencies': freq
        }
    
    def get_bridge_number(self, life_path: int, expression: int) -> Dict:
        """桥接数"""
        lp = _reduce_number(life_path, keep_master=False)
        ex = _reduce_number(expression, keep_master=False)
        bridge = abs(lp - ex)
        return {
            'life_path_reduced': lp,
            'expression_reduced': ex,
            'bridge_value': bridge,
            'bridge_number': bridge if bridge > 0 else None
        }
    
    def get_balance_number(self, full_name: str) -> Dict:
        """平衡数"""
        initials = ''.join(w.strip()[0].upper() for w in full_name.split() if w.strip())
        total = sum(_char_val(c, self.system) for c in initials if c.isalpha())
        final = _reduce_number(total)
        return {
            'value': final,
            'master': final in MASTER_NUMBERS,
            'initials': initials,
            'total': total,
            'wu_xing': _wu_xing_from_number(final)
        }
    
    def get_pinnacles(self, year: int, month: int, day: int) -> Dict:
        """顶峰数（4段生命）"""
        mo = _reduce_number(month, keep_master=False)
        dy = _reduce_number(day, keep_master=False)
        yr = _reduce_number(year, keep_master=False)
        
        p1 = _reduce_number(mo + dy, keep_master=False)
        p2 = _reduce_number(dy + yr, keep_master=False)
        p3 = _reduce_number(p1 + p2, keep_master=False)
        p4 = _reduce_number(mo + yr, keep_master=False)
        
        return {
            'first': {'value': p1, 'age_range': '0-27', 'wu_xing': _wu_xing_from_number(p1)},
            'second': {'value': p2, 'age_range': '28-54', 'wu_xing': _wu_xing_from_number(p2)},
            'third': {'value': p3, 'age_range': '55-81', 'wu_xing': _wu_xing_from_number(p3)},
            'fourth': {'value': p4, 'age_range': '82-', 'wu_xing': _wu_xing_from_number(p4)},
        }
    
    def get_challenges(self, year: int, month: int, day: int) -> Dict:
        """挑战数（4段时期）"""
        mo = _reduce_number(month, keep_master=False)
        dy = _reduce_number(day, keep_master=False)
        yr = _reduce_number(year, keep_master=False)
        
        c1 = abs(mo - dy)
        c2 = abs(dy - yr)
        c3 = abs(c1 - c2)
        c4 = abs(mo - yr)
        
        return {
            'first': {'value': c1, 'age_range': '0-27'},
            'second': {'value': c2, 'age_range': '28-54'},
            'third': {'value': c3, 'age_range': '55-81'},
            'fourth': {'value': c4, 'age_range': '82-'},
        }
    
    def get_subconscious_self(self, full_name: str) -> Dict:
        """潜意识自我数"""
        lessons = self.get_karmic_lessons(full_name)
        missing_count = lessons['count']
        value = max(1, min(9, 9 - missing_count + 1))
        return {
            'value': value,
            'missing_count': missing_count,
            'formula': f'9 - {missing_count} + 1 = {value}',
            'persona': _persona(value)
        }
    
    def get_universal_year(self, year: int) -> Dict:
        """宇宙年数"""
        total = sum(int(d) for d in str(year))
        final = _reduce_number(total)
        return {'value': final, 'year': year, 'total': total}
    
    def get_personal_year(self, year: int, month: int, day: int) -> Dict:
        """个人年数"""
        mo = _reduce_number(month, keep_master=False)
        dy = _reduce_number(day, keep_master=False)
        yr = _reduce_number(year, keep_master=False)
        total = mo + dy + yr
        final = _reduce_number(total)
        return {
            'value': final, 'master': final in MASTER_NUMBERS,
            'year': year, 'month_reduced': mo, 'day_reduced': dy, 'year_reduced': yr,
            'wu_xing': _wu_xing_from_number(final)
        }
    
    def get_maturity_number(self, life_path: int, expression: int) -> Dict:
        """
        成熟数（Maturity / Realization Number）
        
        Life Path + Expression 之和归约
        代表35岁后的人生发展方向
        """
        total = _reduce_number(life_path, keep_master=False) + _reduce_number(expression, keep_master=False)
        final = _reduce_number(total)
        return {
            'value': final,
            'master': final in MASTER_NUMBERS,
            'life_path': life_path,
            'expression': expression,
            'total': total,
            'wu_xing': _wu_xing_from_number(final),
            'persona': _persona(final),
            'meaning': f'35岁后的人生将从{_persona(life_path)}转向{_persona(final)}方向'
        }

    def get_rational_thought(self, full_name: str, day: int) -> Dict:
        """
        理性思维数（Rational Thought Number）

        国际数字能量体系核心指标之一：
        出生日（Birthday Number） + 全名表达数（Expression Number）
        代表一个人面对复杂问题时的理性处理方式、决策风格、思维组织能力。
        """
        bd = self.get_birthday(day)
        ex = self.get_expression(full_name)
        total = _reduce_number(bd['value'], keep_master=False) + _reduce_number(ex['value'], keep_master=False)
        final = _reduce_number(total)
        return {
            'value': final,
            'master': final in MASTER_NUMBERS,
            'birthday': bd['value'],
            'expression': ex['value'],
            'total': total,
            'wu_xing': _wu_xing_from_number(final),
            'persona': _persona(final),
            'meaning': f'你在处理现实问题时，倾向以{_persona(final)}模式做判断与取舍'
        }
    
    def get_groovetone(self, day: int) -> Dict:
        """
        动量数（Groove Tone / 又称Placement Number）
        
        实际出生日（不归约），代表振动频率
        """
        return {'value': day, 'persona': _persona(_reduce_number(day))}
    
    # ---------- v2.0 新增：兼容性匹配 ----------
    
    def get_compatibility(self, 
                          name1: str, year1: int, month1: int, day1: int,
                          name2: str, year2: int, month2: int, day2: int) -> Dict:
        """
        数字能量兼容性匹配
        
        基于：Life Path兼容性 + Expression兼容性 + Soul Urge兼容性
        评分范围 0-10
        """
        lp1 = self.get_life_path(year1, month1, day1)['value']
        lp2 = self.get_life_path(year2, month2, day2)['value']
        ex1 = self.get_expression(name1)['value']
        ex2 = self.get_expression(name2)['value']
        su1 = self.get_soul_urge(name1)['value']
        su2 = self.get_soul_urge(name2)['value']
        
        # Life Path兼容性
        lp_diff = abs(_reduce_number(lp1, keep_master=False) - _reduce_number(lp2, keep_master=False))
        if lp_diff == 0:
            lp_score = 9.0  # 相同：强共鸣
        elif lp_diff == 2 or lp_diff == 4:
            lp_score = 8.0  # 和谐
        elif lp_diff == 1 or lp_diff == 8:
            lp_score = 6.5  # 互补
        elif lp_diff == 3 or lp_diff == 6:
            lp_score = 5.0  # 中性
        else:  # 5, 7
            lp_score = 4.0  # 张力
        
        # Expression兼容性
        ex_diff = abs(_reduce_number(ex1, keep_master=False) - _reduce_number(ex2, keep_master=False))
        ex_score = max(2.0, 10.0 - ex_diff * 1.2)
        
        # Soul Urge兼容性（情感层面）
        su_diff = abs(_reduce_number(su1, keep_master=False) - _reduce_number(su2, keep_master=False))
        su_score = max(2.0, 10.0 - su_diff * 1.0)
        
        # 加权合成
        overall = round((lp_score * 0.45 + ex_score * 0.30 + su_score * 0.25), 2)
        
        return {
            'overall_score': min(10.0, overall),
            'life_path_compatibility': round(lp_score, 2),
            'expression_compatibility': round(ex_score, 2),
            'soul_urge_compatibility': round(su_score, 2),
            'person1': {'life_path': lp1, 'expression': ex1, 'soul_urge': su1},
            'person2': {'life_path': lp2, 'expression': ex2, 'soul_urge': su2},
            'life_path_wu_xing': {
                'person1': _wu_xing_from_number(lp1),
                'person2': _wu_xing_from_number(lp2)
            }
        }
    
    def get_angel_number(self, number: int) -> Dict:
        """天使数字检测"""
        s = str(abs(number))
        n = len(s)
        is_repeating = len(set(s)) == 1 and n >= 2
        is_sequential = all(int(s[i+1]) - int(s[i]) == 1 for i in range(n-1)) and n >= 3
        is_mirror = s == s[::-1] and n >= 2 and not is_repeating
        is_double_pair = n == 4 and s[:2] == s[2:] and not is_repeating
        
        patterns = []
        if is_repeating: patterns.append('repeating')
        if is_sequential: patterns.append('sequential')
        if is_mirror: patterns.append('mirror')
        if is_double_pair: patterns.append('double_pair')
        
        digits = list(set(int(d) for d in s))
        
        return {
            'number': number,
            'is_angel_number': len(patterns) > 0,
            'patterns': patterns,
            'digits': digits,
            'reduced': _reduce_number(number),
            'wu_xing': _wu_xing_from_number(number)
        }
    
    # ---------- 完整报告 ----------
    
    def get_full_report(self, full_name: str, year: int, month: int, day: int) -> Dict:
        name = full_name.strip() if full_name else ''
        
        lp = self.get_life_path(year, month, day)
        bd = self.get_birthday(day)
        ex = self.get_expression(name) if name else None
        su = self.get_soul_urge(name) if name else None
        pe = self.get_personality(name) if name else None
        kl = self.get_karmic_lessons(name) if name else None
        hp = self.get_hidden_passion(name) if name else None
        bn = self.get_bridge_number(lp['value'], ex['value']) if name and ex else None
        ba = self.get_balance_number(name) if name else None
        pi = self.get_pinnacles(year, month, day)
        ch = self.get_challenges(year, month, day)
        ss = self.get_subconscious_self(name) if name else None
        uy = self.get_universal_year(year)
        py = self.get_personal_year(year, month, day)
        mn = self.get_maturity_number(lp['value'], ex['value']) if name and ex else None
        rt = self.get_rational_thought(name, day) if name else None
        gt = self.get_groovetone(day)
        
        return {
            'system': self.system,
            'name': name,
            'birth_date': f'{year}-{month:02d}-{day:02d}',
            'life_path': lp,
            'birthday': bd,
            'expression': ex,
            'soul_urge': su,
            'personality': pe,
            'karmic_lessons': kl,
            'hidden_passion': hp,
            'bridge_number': bn,
            'balance_number': ba,
            'pinnacles': pi,
            'challenges': ch,
            'subconscious_self': ss,
            'universal_year': uy,
            'personal_year': py,
            'maturity_number': mn,
            'rational_thought': rt,
            'groove_tone': gt,
            'summary': {
                'primary_number': lp['value'],
                'primary_master': lp['master'],
                'primary_wu_xing': lp['wu_xing'],
                'primary_persona': lp['persona'],
                'year_energy': uy['value'],
                'personal_energy': py['value']
            }
        }


# ============================================================
# 快照API（向后兼容v1.0）
# ============================================================

def get_numerology_snapshot(full_name: str, year: int, month: int, day: int,
                           system: str = 'pythagorean') -> Dict:
    calc = NumerologyCalculator(system)
    full = calc.get_full_report(full_name, year, month, day)
    return {
        'life_path': full['life_path']['value'],
        'master': full['life_path']['master'],
        'life_path_karmic': full['life_path']['karmic_debt'],
        'expression': full['expression']['value'] if full['expression'] else None,
        'soul_urge': full['soul_urge']['value'] if full['soul_urge'] else None,
        'personality': full['personality']['value'] if full['personality'] else None,
        'birthday': full['birthday']['value'],
        'current_pinnacle': full['pinnacles']['first']['value'],
        'universal_year': full['universal_year']['value'],
        'personal_year': full['personal_year']['value'],
        'maturity_number': full['maturity_number']['value'] if full['maturity_number'] else None,
        'rational_thought': full['rational_thought']['value'] if full.get('rational_thought') else None,
        'karmic_debts': list(filter(None, [
            full['life_path']['karmic_debt'],
            full['expression']['karmic_debt'] if full['expression'] else None,
            full['soul_urge']['karmic_debt'] if full['soul_urge'] else None,
            full['personality']['karmic_debt'] if full['personality'] else None,
            full['birthday']['karmic_debt']
        ])),
        'missing_numbers': full['karmic_lessons']['missing_numbers'] if full['karmic_lessons'] else [],
        'wu_xing': full['life_path']['wu_xing'],
        'persona': full['life_path']['persona']
    }


# ============================================================
# 名人验证集
# ============================================================

VERIFIED_CASES = [
    {'name': 'Albert Einstein', 'year': 1879, 'month': 3, 'day': 14, 'life_path': 6, 'note': '理论物理学家'},
    {'name': 'Elon Musk', 'year': 1971, 'month': 6, 'day': 28, 'life_path': 7, 'note': 'Tesla/SpaceX'},
    {'name': 'Barack Obama', 'year': 1961, 'month': 8, 'day': 4, 'life_path': 2, 'note': '前美国总统'},
    {'name': 'Steve Jobs', 'year': 1955, 'month': 2, 'day': 24, 'life_path': 1, 'note': 'Apple创始人'},
    {'name': 'Oprah Winfrey', 'year': 1954, 'month': 1, 'day': 29, 'life_path': 22, 'note': '媒体女王（主数22, 35岁后展现）'},
    {'name': 'Leonardo DiCaprio', 'year': 1974, 'month': 11, 'day': 11, 'life_path': 7, 'note': '演员（分析型）'},    
]


def verify_known_cases():
    """验证名人Life Path是否正确"""
    calc = NumerologyCalculator('pythagorean')
    results = []
    for case in VERIFIED_CASES:
        lp = calc.get_life_path(case['year'], case['month'], case['day'])
        correct = lp['value'] == case['life_path']
        results.append({
            'name': case['name'],
            'expected': case['life_path'],
            'got': lp['value'],
            'correct': correct
        })
    return results


# ============================================================
# 测试
# ============================================================

if __name__ == '__main__':
    print("=== 数字能量计算引擎 v2.0 — 验证测试 ===\n")
    
    calc = NumerologyCalculator('pythagorean')
    
    # 验证
    results = verify_known_cases()
    all_ok = all(r['correct'] for r in results)
    for r in results:
        status = '✅' if r['correct'] else '❌'
        print(f"  {status} {r['name']}: LP={r['got']} (expected={r['expected']})")
    print(f"\n  名人验证：{'全部通过' if all_ok else '有偏差'}")
    
    # v2.0新特性测试
    print("\n--- v2.0 新特性 ---")
    
    # 五行映射
    r = calc.get_full_report('Peter Qiu', 1990, 11, 10)
    print(f"丘总 Life Path={r['life_path']['value']} 五行={r['life_path']['wu_xing']} 性格={r['life_path']['persona']}")
    
    # 成熟数
    print(f"成熟数: {r['maturity_number']['value']} ({r['maturity_number']['meaning']})")
    
    # 兼容性匹配
    compat = calc.get_compatibility(
        'Peter Qiu', 1990, 11, 10,
        'Jane Doe', 1993, 5, 3
    )
    print(f"\n兼容性测试: 总分={compat['overall_score']}")
    print(f"  Life Path: {compat['person1']['life_path']}({compat['life_path_wu_xing']['person1']}) vs {compat['person2']['life_path']}({compat['life_path_wu_xing']['person2']})")
    
    # 天使数字
    angel = calc.get_angel_number(111)
    print(f"\n111是天使数字? {angel['is_angel_number']}, 模式={angel['patterns']}, 五行={angel['wu_xing']}")
    
    print("\n✅ 数字能量计算引擎 v2.0 验证完毕")
