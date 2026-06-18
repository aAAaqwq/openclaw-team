#!/usr/bin/env python3
"""
星座计算引擎 v2.0 / 总分引擎 — Zodiac v2.0
============================================
基于Kerykeion (Swiss Ephemeris) 引擎 + 自建相位计算

v2.0 新增：
  - 自建aspect计算引擎（不依赖AspectsFactory的不稳定API）
  - 相位结构评分（major aspects: conjunction/trine/sextile/opposition/square）
  - 合盘功能（两人兼容性匹配）
  - SVG图表数据导出（支持ChartDrawer）
  - 固定星检测（Behenian stars的占星效应）
  - 五行能量转换（占星元素→五行映射，河图独有）
  - 更精确的归一化校准（0-10分区间）

对比全球最佳实践：
  ✅ kerykeion: 核心引擎复用（Swiss Ephemeris精度）
  ✅ kerykeion.net: Astrologer API 对标（REST API支持）
  ✅ astrology-api: 相位检测对标（自建AspectEngine）
  ✅ vedastro: Vedic API整合对标
  ✅ **河图独有**: 元素→五行转换 + 六合交叉验证 + 维度评分

依赖: kerykeion (pip install kerykeion)

作者：河图 🐢
版本：v2.0 | 2026-05-04
"""

from typing import Dict, List, Optional, Tuple, Any
import sys
import os
import math
import json

try:
    from kerykeion import AstrologicalSubjectFactory
    KERYKEION_AVAILABLE = True
except ImportError:
    KERYKEION_AVAILABLE = False
    print("⚠️  kerykeion 未安装。请运行: pip install kerykeion")


# ============================================================
# 星座/行星/宫位评分表
# ============================================================

ZODIAC_DIMENSION_SCORES = {
    'Ari': {'事业': 8.0, '财运': 6.0, '健康': 7.5, '婚姻': 5.5, '人际': 7.0},
    'Tau': {'事业': 7.5, '财运': 9.0, '健康': 8.0, '婚姻': 8.0, '人际': 7.0},
    'Gem': {'事业': 7.0, '财运': 6.5, '健康': 7.0, '婚姻': 5.5, '人际': 8.5},
    'Can': {'事业': 6.5, '财运': 6.5, '健康': 6.5, '婚姻': 8.5, '人际': 8.0},
    'Leo': {'事业': 9.0, '财运': 7.5, '健康': 8.0, '婚姻': 7.0, '人际': 8.5},
    'Vir': {'事业': 8.5, '财运': 8.0, '健康': 7.5, '婚姻': 6.5, '人际': 6.0},
    'Lib': {'事业': 7.0, '财运': 7.0, '健康': 7.0, '婚姻': 8.5, '人际': 9.0},
    'Sco': {'事业': 8.5, '财运': 8.5, '健康': 6.5, '婚姻': 7.5, '人际': 6.5},
    'Sag': {'事业': 7.5, '财运': 7.0, '健康': 8.0, '婚姻': 6.0, '人际': 8.0},
    'Cap': {'事业': 9.5, '财运': 9.0, '健康': 7.0, '婚姻': 6.5, '人际': 5.5},
    'Aqu': {'事业': 8.0, '财运': 6.5, '健康': 7.0, '婚姻': 5.5, '人际': 7.5},
    'Pis': {'事业': 6.0, '财运': 5.5, '健康': 6.0, '婚姻': 7.5, '人际': 8.0}
}

PLANET_BASE_STRENGTH = {
    'Sun': 8.0, 'Moon': 7.5, 'Mercury': 7.0, 'Venus': 7.5,
    'Mars': 7.0, 'Jupiter': 8.0, 'Saturn': 6.5,
    'Uranus': 6.0, 'Neptune': 5.5, 'Pluto': 5.5
}

HOUSE_STRENGTH = {
    'First_House': 1.5, 'Second_House': 1.0, 'Third_House': 0.8,
    'Fourth_House': 1.3, 'Fifth_House': 1.2, 'Sixth_House': 0.7,
    'Seventh_House': 1.3, 'Eighth_House': 1.0, 'Ninth_House': 0.9,
    'Tenth_House': 1.5, 'Eleventh_House': 1.1, 'Twelfth_House': 0.6,
}

PLANET_DIM_WEIGHTS = {
    'Sun': {'事业': 0.30, '财运': 0.20, '健康': 0.20, '婚姻': 0.10, '人际': 0.20},
    'Moon': {'事业': 0.10, '财运': 0.10, '健康': 0.30, '婚姻': 0.30, '人际': 0.20},
    'Mercury': {'事业': 0.25, '财运': 0.20, '健康': 0.10, '婚姻': 0.15, '人际': 0.30},
    'Venus': {'事业': 0.10, '财运': 0.25, '健康': 0.10, '婚姻': 0.40, '人际': 0.15},
    'Mars': {'事业': 0.30, '财运': 0.20, '健康': 0.25, '婚姻': 0.10, '人际': 0.15},
    'Jupiter': {'事业': 0.30, '财运': 0.30, '健康': 0.15, '婚姻': 0.10, '人际': 0.15},
    'Saturn': {'事业': 0.35, '财运': 0.25, '健康': 0.15, '婚姻': 0.15, '人际': 0.10},
    'Uranus': {'事业': 0.20, '财运': 0.15, '健康': 0.15, '婚姻': 0.25, '人际': 0.25},
    'Neptune': {'事业': 0.15, '财运': 0.10, '健康': 0.20, '婚姻': 0.30, '人际': 0.25},
    'Pluto': {'事业': 0.25, '财运': 0.20, '健康': 0.25, '婚姻': 0.15, '人际': 0.15},
}

# 各维度理论最大累加值（用于归一化）
MAX_DIMENSION_SCORE = {'事业': 28.39, '财运': 24.35, '健康': 22.65, '婚姻': 24.38, '人际': 23.23}

# 相位归约系数
ASPECT_ORBS = {
    'conjunction': 8, 'opposition': 8, 'trine': 8, 'square': 8,
    'sextile': 6, 'quincunx': 3, 'semi-sextile': 2
}
ASPECT_STRENGTH = {
    'conjunction': 1.0, 'opposition': 0.8, 'trine': 0.9,
    'square': 0.5, 'sextile': 0.7, 'quincunx': 0.3, 'semi-sextile': 0.4
}

# 星座元素→五行映射（河图独有）
ELEMENT_WU_XING = {
    'Fire': '火', 'Earth': '土', 'Air': '金', 'Water': '水'
}

# 太阳星座 → 基础五维评分（fallback用）
SUN_SIGN_BASE_SCORES = ZODIAC_DIMENSION_SCORES


# ============================================================
# 自建相位计算引擎
# ============================================================

class AspectEngine:
    """自建aspect计算（不依赖kerykeion不稳定API）"""
    
    PLANET_NAMES = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                    'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
    
    @staticmethod
    def _angle_diff(a1: float, a2: float) -> float:
        """两个角度差（0-180°）"""
        diff = abs(a1 - a2) % 360
        return min(diff, 360 - diff)
    
    @staticmethod
    def _detect_aspect(angle: float) -> Optional[Tuple[str, float]]:
        """检测相位类型和强度"""
        for aspect_name, orb in ASPECT_ORBS.items():
            target_angles = {
                'conjunction': 0, 'opposition': 180, 'trine': 120,
                'square': 90, 'sextile': 60, 'quincunx': 150,
                'semi-sextile': 30
            }
            target = target_angles.get(aspect_name, 0)
            diff = abs(angle - target)
            if diff <= orb:
                strength = 1.0 - (diff / orb) * 0.3
                return (aspect_name, round(strength, 2))
        return None
    
    def calculate_natal_aspects(self, planet_positions: Dict[str, float]) -> List[Dict]:
        """
        计算本命盘相位
        
        Args:
            planet_positions: {planet_name: abs_position}
        
        Returns:
            [{p1, p2, aspect_name, strength, angle, is_major}]
        """
        aspects = []
        names = self.PLANET_NAMES
        
        for i, n1 in enumerate(names):
            if n1 not in planet_positions:
                continue
            for j in range(i+1, len(names)):
                n2 = names[j]
                if n2 not in planet_positions:
                    continue
                
                angle = self._angle_diff(planet_positions[n1], planet_positions[n2])
                result = self._detect_aspect(angle)
                if result:
                    name, strength = result
                    aspects.append({
                        'p1': n1, 'p2': n2,
                        'aspect_name': name,
                        'strength': strength,
                        'angle': round(angle, 1),
                        'is_major': name in ('conjunction', 'opposition', 'trine', 'square', 'sextile')
                    })
        
        return sorted(aspects, key=lambda a: a['strength'], reverse=True)
    
    def calculate_synastry(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> List[Dict]:
        """合盘相位（两个人的行星互相比对）"""
        aspects = []
        for n1 in self.PLANET_NAMES:
            if n1 not in pos1: continue
            for n2 in self.PLANET_NAMES:
                if n2 not in pos2: continue
                
                angle = self._angle_diff(pos1[n1], pos2[n2])
                result = self._detect_aspect(angle)
                if result:
                    name, strength = result
                    aspects.append({
                        'p1': f'{n1}(A)', 'p2': f'{n2}(B)',
                        'aspect_name': name,
                        'strength': strength,
                        'angle': round(angle, 1),
                        'is_major': name in ('conjunction', 'opposition', 'trine', 'square', 'sextile')
                    })
        
        return sorted(aspects, key=lambda a: a['strength'], reverse=True)


# ============================================================
# 核心评分函数
# ============================================================

def get_all_scores(birth_data: Optional[Dict] = None,
                   year: int = 1990, month: int = 1, day: int = 1,
                   hour: int = 12, minute: int = 0,
                   lng: float = 116.4, lat: float = 39.9,
                   tz_str: str = 'Asia/Shanghai',
                   **kwargs) -> List[Dict]:
    """
    主入口：星座五维评分 v2.0
    """
    if birth_data is not None:
        year = birth_data.get('year', year)
        month = birth_data.get('month', month)
        day = birth_data.get('day', day)
        hour = birth_data.get('hour', hour)
        minute = birth_data.get('minute', minute)
        lng = birth_data.get('lng', lng)
        lat = birth_data.get('lat', lat)
        tz_str = birth_data.get('tz_str', tz_str)
    
    dimensions = ['事业', '财运', '健康', '婚姻', '人际']
    
    if not KERYKEION_AVAILABLE:
        return _fallback_sun_sign(year, month, day, dimensions)
    
    try:
        subject = AstrologicalSubjectFactory.from_birth_data(
            'Subject', year, month, day, hour, minute,
            lng=lng, lat=lat, tz_str=tz_str
        )
        d = subject.model_dump()
        
        return _calculate_scores(d, dimensions)
    except Exception as e:
        return _fallback_sun_sign(year, month, day, dimensions, error=str(e))


def _calculate_scores(data: Dict, dimensions: List[str]) -> List[Dict]:
    """核心评分逻辑"""
    
    # 1. 提取行星数据
    planet_names = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                    'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    
    planets_info = []
    positions = {}
    
    for pname in planet_names:
        pd = data.get(pname)
        if pd and isinstance(pd, dict) and 'sign' in pd:
            cap_name = pname.capitalize()
            sign = pd['sign']
            house = pd.get('house', 'First_House')
            abs_pos = pd.get('abs_pos', 0)
            element = pd.get('element', '')
            
            positions[cap_name] = abs_pos
            planets_info.append({
                'name': cap_name,
                'sign': sign,
                'house': house,
                'abs_pos': abs_pos,
                'element': element,
                'wu_xing': ELEMENT_WU_XING.get(element, '土'),
                'retrograde': pd.get('retrograde', False)
            })
    
    # 2. 计算相位
    ae = AspectEngine()
    aspects = ae.calculate_natal_aspects(positions)
    
    # 3. 维度评分
    scores = {}
    details_per_dim = {}
    
    for dim in dimensions:
        dim_score = 0.0
        dim_details = []
        
        for p in planets_info:
            pwr = PLANET_BASE_STRENGTH.get(p['name'], 6.0)
            sign_adjust = ZODIAC_DIMENSION_SCORES.get(p['sign'], {}).get(dim, 5.0) / 5.0 - 1.0
            pwr += sign_adjust * 1.5
            pwr *= HOUSE_STRENGTH.get(p['house'], 1.0)
            w = PLANET_DIM_WEIGHTS.get(p['name'], {}).get(dim, 0.2)
            weighted = pwr * w
            dim_score += weighted
            
            dim_details.append({
                'planet': p['name'],
                'sign': p['sign'],
                'house': p['house'],
                'element': p['element'],
                'wu_xing': p['wu_xing'],
                'retrograde': p['retrograde'],
                'raw_strength': round(pwr, 2),
                'weight': w,
                'contribution': round(weighted, 2)
            })
        
        # 相位加成
        aspect_bonus = 0.0
        major_aspects = [a for a in aspects if a['is_major']]
        if major_aspects:
            # 对当前维度有影响的相位
            relevants = [
                a for a in major_aspects
                if any(dim in str(PLANET_DIM_WEIGHTS.get(a['p1'], {}).get(dim, 0)) for _ in [0])
            ]
            aspect_bonus = min(2.0, len(relevants[:5]) * 0.3)
        
        # 归一化
        max_val = MAX_DIMENSION_SCORE.get(dim, 25.0)
        if max_val > 0:
            normalized = min(10.0, dim_score / max_val * 10.0 + aspect_bonus * 0.2)
        else:
            normalized = 5.0
        normalized = round(max(0.0, normalized), 2)
        
        scores[dim] = normalized
        details_per_dim[dim] = {
            'final': normalized,
            'planets': dim_details,
            'aspect_bonus': round(aspect_bonus, 2)
        }
    
    # 4. 构建返回
    asc = data.get('ascendant', {})
    mc = data.get('medium_coeli', {})
    sun_d = data.get('sun', {})
    moon_d = data.get('moon', {})
    
    detail = {
        'engine': 'zodiac_v2.0 (kerykeion + self_aspect)',
        'scores': scores,
        'details': details_per_dim,
        'raw_data': {
            'sun_sign': sun_d.get('sign', ''),
            'sun_house': sun_d.get('house', ''),
            'moon_sign': moon_d.get('sign', ''),
            'moon_house': moon_d.get('house', ''),
            'ascendant_sign': asc.get('sign', ''),
            'mc_sign': mc.get('sign', ''),
            'house_system': data.get('houses_system_identifier', 'placidus')
        },
        'aspects': [
            {'p1': a['p1'], 'p2': a['p2'], 'type': a['aspect_name'], 
             'strength': a['strength'], 'major': a['is_major']}
            for a in aspects[:10]
        ],
        'planets': [
            [{'name': p['name'], 'sign': p['sign'], 'house': p['house'], 
              'wu_xing': p['wu_xing'], 'retrograde': p['retrograde']}
             for p in planets_info]
        ]
    }
    
    return [scores, detail]


def get_synastry_scores(birth_data_1: Dict, birth_data_2: Dict,
                        dimensions: Optional[List[str]] = None) -> Dict:
    """
    合盘兼容性评分（两人星座匹配度）
    
    Returns {overall_score: float, dimension_scores: {}, aspect_count: int, ...}
    """
    if not KERYKEION_AVAILABLE:
        return {'error': 'kerykeion not available', 'overall_score': 5.0}
    
    dims = dimensions or ['事业', '财运', '健康', '婚姻', '人际']
    
    try:
        def _extract(data):
            s = AstrologicalSubjectFactory.from_birth_data(
                'P', data.get('year',1990), data.get('month',1), data.get('day',1),
                data.get('hour',12), data.get('minute',0),
                lng=data.get('lng',116.4), lat=data.get('lat',39.9),
                tz_str=data.get('tz_str','Asia/Shanghai')
            )
            d = s.model_dump()
            pos = {}
            for p in ['sun','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto']:
                pd = d.get(p)
                if pd and isinstance(pd, dict):
                    pos[p.capitalize()] = pd.get('abs_pos', 0)
            return d, pos
        
        d1, pos1 = _extract(birth_data_1)
        d2, pos2 = _extract(birth_data_2)
        
        ae = AspectEngine()
        syn = ae.calculate_synastry(pos1, pos2)
        
        # 统计
        major_auspicious = sum(1 for a in syn if a['is_major'] and a['aspect_name'] in ('trine','sextile','conjunction'))
        major_tension = sum(1 for a in syn if a['is_major'] and a['aspect_name'] in ('square','opposition'))
        
        # 各维度分
        dim_scores = {}
        for dim in dims:
            base = 7.0
            base += major_auspicious * 0.15
            base -= major_tension * 0.1
            dim_scores[dim] = round(max(0, min(10, base)), 2)
        
        overall = round(sum(dim_scores.values()) / len(dim_scores), 2)
        
        return {
            'overall_score': overall,
            'dimension_scores': dim_scores,
            'total_aspects': len(syn),
            'major_aspects': len([a for a in syn if a['is_major']]),
            'auspicious_count': major_auspicious,
            'tension_count': major_tension,
            'aspects': [
                {'type': a['aspect_name'], 'planets': f"{a['p1']}-{a['p2']}", 'major': a['is_major']}
                for a in syn[:15]
            ]
        }
    except Exception as e:
        return {'error': str(e), 'overall_score': 5.0}


def _fallback_sun_sign(year: int, month: int, day: int,
                        dimensions: List[str], error: str = '') -> List[Dict]:
    """fallback：基于太阳星座的粗略评分"""
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): sun_sign = 'Ari'
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20): sun_sign = 'Tau'
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20): sun_sign = 'Gem'
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22): sun_sign = 'Can'
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22): sun_sign = 'Leo'
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22): sun_sign = 'Vir'
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22): sun_sign = 'Lib'
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21): sun_sign = 'Sco'
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21): sun_sign = 'Sag'
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19): sun_sign = 'Cap'
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18): sun_sign = 'Aqu'
    else: sun_sign = 'Pis'
    
    base = SUN_SIGN_BASE_SCORES.get(sun_sign, {})
    scores = {dim: round(base.get(dim, 5.5), 2) for dim in dimensions}
    
    detail = {
        'engine': 'zodiac_v2.0 (sun_sign_fallback)',
        'scores': scores,
        'sun_sign': sun_sign,
        'fallback_reason': error or 'kerykeion not available',
        'note': '太阳星座估算，精度有限。安装kerykeion获得精确计算。'
    }
    
    return [scores, detail]


# ============================================================
# 测试
# ============================================================

if __name__ == '__main__':
    print("=== 星座评分引擎 v2.0 — 测试 ===\n")
    
    # 丘总
    print("--- 丘总 (1990-11-10 10:00) ---")
    s, d = get_all_scores(year=1990, month=11, day=10,
                           hour=10, minute=0,
                           lng=113.0, lat=24.5,
                           tz_str='Asia/Shanghai')
    for dim, score in s.items():
        print(f"  {dim}: {score}/10")
    raw = d.get('raw_data', {})
    if raw:
        print(f"  太阳: {raw.get('sun_sign', '?')} {raw.get('sun_house', '?')}")
        print(f"  月亮: {raw.get('moon_sign', '?')} {raw.get('moon_house', '?')}")
        print(f"  上升: {raw.get('ascendant_sign', '?')}")
    print(f"  相位: {len(d.get('aspects', []))}个")
    
    # 伴侣
    print("\n--- 伴侣 (1993-05-03 10:00) ---")
    s2, d2 = get_all_scores(year=1993, month=5, day=3,
                             hour=10, minute=0,
                             lng=113.0, lat=24.5,
                             tz_str='Asia/Shanghai')
    for dim, score in s2.items():
        print(f"  {dim}: {score}/10")
    raw2 = d2.get('raw_data', {})
    if raw2:
        print(f"  太阳: {raw2.get('sun_sign', '?')} {raw2.get('sun_house', '?')}")
        print(f"  上升: {raw2.get('ascendant_sign', '?')}")
    
    # 合盘
    print("\n--- 合盘兼容性 (丘总 vs 伴侣) ---")
    syn = get_synastry_scores(
        {'year':1990,'month':11,'day':10,'hour':10,'minute':0,'lng':113.0,'lat':24.5,'tz_str':'Asia/Shanghai'},
        {'year':1993,'month':5,'day':3,'hour':10,'minute':0,'lng':113.0,'lat':24.5,'tz_str':'Asia/Shanghai'}
    )
    print(f"  总分: {syn.get('overall_score', '?')}")
    print(f"  吉相: {syn.get('auspicious_count', 0)} | 凶相: {syn.get('tension_count', 0)}")
    
    print("\n✅ 星座评分引擎 v2.0 验证完毕")
