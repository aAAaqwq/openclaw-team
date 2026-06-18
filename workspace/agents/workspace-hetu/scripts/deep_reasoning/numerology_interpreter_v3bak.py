#!/usr/bin/env python3
"""
数字能量深度解读生成器 v3.0 — Numerology Interpreter
======================================================
功能：
  - 多维度联合解读（不单报数字，讲"你的生命路径X + 表达数Y"组合含义）
  - 周期运势生成（个人年→个人月→个人日三重滚动）
  - 自然语言输出（可商用、可推送、可生成内容）
  - 六合交叉验证接口兼容

对比全球最佳实践：
  ✅ 对标 numerology.com: 大师级文字解读 ≤ 我们新实现
  ✅ 对标 worldnumerology.com: 周期性分析 + 个人年解读覆盖
  ✅ 对标 divineapi.com: 详细解读文本 ≤ 我们新实现
  ✅ 河图独有：五行化解读 + 个人年五行映射

商用Ready ⭐⭐⭐⭐⭐

作者：河图 🐢
版本：v3.0 | 2026-05-05
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numerology_calc import NumerologyCalculator, get_numerology_snapshot, _reduce_number


# ============================================================
# 一、数字含义解读库
# ============================================================

NUMBER_MEANINGS = {
    1: {
        'name': '开创者',
        'positive': ['独立', '自信', '创新', '领导力', '原创思维'],
        'negative': ['固执', '独断', '急躁', '自我中心', '过度竞争'],
        'career': '适合创业、管理层、独立执业、创意总监',
        'relationship': '需要空间和尊重，恋人之间要给对方主权',
        'health': '注意头部和神经系统，偏头痛和过度压力',
        'advice': '学会授权，你不需要一个人扛全部',
        'year_theme': '重新定义自我身份的一年'
    },
    2: {
        'name': '外交家',
        'positive': ['合作', '敏感', '耐心', '包容', '协调能力'],
        'negative': ['被动', '依赖', '过度敏感', '逃避冲突'],
        'career': '适合公关、客户经理、心理咨询、HR、调解员',
        'relationship': '需要安全感，容易被情绪左右',
        'health': '注意免疫系统和消化系统，压力易引起胃病',
        'advice': '平衡他人需求和自己内心声音',
        'year_theme': '建立合作关系和深度链接的一年'
    },
    3: {
        'name': '创意家',
        'positive': ['表达力', '创造力', '社交', '乐观', '感染力'],
        'negative': ['散乱', '情绪化', '肤浅', '逃避责任'],
        'career': '适合写作、设计、营销、影视、自媒体',
        'relationship': '有趣但容易三分钟热度',
        'health': '注意喉咙和情绪波动，易咽喉问题',
        'advice': '把创意落地，不只是一个灵感收集者',
        'year_theme': '社交网络扩张和创意输出的一年'
    },
    4: {
        'name': '实干家',
        'positive': ['稳定', '务实', '执行力', '责任心', '系统思维'],
        'negative': ['固执', '死板', '焦虑', '不愿改变'],
        'career': '适合工程、管理、财务、建筑、项目管理',
        'relationship': '可靠但需要计划好的约会',
        'health': '注意消化系统和骨骼健康',
        'advice': '适当放下控制，拥抱不确定性',
        'year_theme': '打基础、建体系、夯实根基的一年'
    },
    5: {
        'name': '自由者',
        'positive': ['冒险', '适应力', '好奇心', '魅力', '多才多艺'],
        'negative': ['不负责任', '冲动', '浮躁', '缺乏毅力'],
        'career': '适合旅行、销售、媒体、自由职业、创业',
        'relationship': '需要自由，不喜欢被束缚',
        'health': '注意心脏和呼吸系统',
        'advice': '用自由做有价值的事，不是只享受自由本身',
        'year_theme': '开拓视野、拥抱变化的一年'
    },
    6: {
        'name': '关怀者',
        'positive': ['爱心', '责任感', '家庭', '服务', '审美'],
        'negative': ['过度付出', '控制欲', '挑剔', '牺牲自我'],
        'career': '适合教育、健康、家庭咨询、设计、心理',
        'relationship': '对家庭极度负责但容易让对方窒息',
        'health': '注意皮肤和血液循环',
        'advice': '先对自己负责，才能更好地对别人负责',
        'year_theme': '家庭责任和亲密关系的平衡之年'
    },
    7: {
        'name': '智者',
        'positive': ['分析力', '洞察', '深度思维', '心灵成长', '专业主义'],
        'negative': ['孤僻', '猜疑', '过度分析', '疏离社交'],
        'career': '适合研究、AI/数据、咨询、学术、哲学',
        'relationship': '需要智力共鸣，容易被神秘感吸引',
        'health': '注意神经紧张和失眠',
        'advice': '知识再多也需要与人连接',
        'year_theme': '深度学习和内在探索的一年'
    },
    8: {
        'name': '执行者',
        'positive': ['商业头脑', '执行力', '权威', '管理能力'],
        'negative': ['功利', '控制欲', '过度工作', '情感冷漠'],
        'career': '适合CEO、金融、投资、销售、地产',
        'relationship': '需要事业和感情的平衡',
        'health': '注意肝和脊椎，压力型疾病',
        'advice': '财富是工具不是目的，别忘了内心的丰盛',
        'year_theme': '事业爆发和财富积累的一年'
    },
    9: {
        'name': '博爱者',
        'positive': ['大爱', '包容', '理想主义', '艺术天赋', '智慧'],
        'negative': ['不切实际', '逃避责任', '过度理想化'],
        'career': '适合NGO、慈善、教育、艺术、咨询',
        'relationship': '爱所有人但很难爱具体一个人',
        'health': '注意免疫系统，情绪影响身体',
        'advice': '把理想变成现实，不只是发愿',
        'year_theme': '完成与放下的过渡之年'
    },
    11: {
        'name': '灵性启发者',
        'positive': ['直觉', '灵感', '理想主义', '领导力', '灵性'],
        'negative': ['焦虑', '不接地气', '情绪极端', '自我怀疑'],
        'career': '适合咨询、心理学、冥想、写作、教育',
        'relationship': '深刻但不稳定，需要精神层面的连接',
        'health': '注意神经系统和情绪管理',
        'advice': '你的天赋是启发别人，但要先稳住自己',
        'year_theme': '灵性觉醒和直觉放大的特殊之年'
    },
    22: {
        'name': '大师建造者',
        'positive': ['执行力', '远见', '战略', '资源整合', '建造能力'],
        'negative': ['压力过大', '不切实际', '独断专行'],
        'career': '适合大型项目管理、建筑、金融、政治',
        'relationship': '伴侣需要理解你的使命',
        'health': '注意压力累积和心血管',
        'advice': '你有能力改变世界，但先改变自己的节奏',
        'year_theme': '从蓝图到落地的大师级构建之年'
    },
    33: {
        'name': '大爱导师',
        'positive': ['慈悲', '智慧', '教学', '治愈', '无私奉献'],
        'negative': ['牺牲过度', '情绪负担', '疲惫'],
        'career': '适合教育、医疗、疗愈、心灵导师',
        'relationship': '爱是使命而不是占有',
        'health': '注意平衡付出和接收',
        'advice': '你的使命是照亮别人，但别忘了给自己充电',
        'year_theme': '大爱与服务的至高表达之年'
    }
}


# ============================================================
# 二、周期解读库
# ============================================================

PERSONAL_YEAR_MEANINGS = {
    1: '新开始之年。适合启动新项目、重塑个人品牌、重新定义方向。没有更好的开始时机。',
    2: '等待与合作之年。放慢脚步，建立关系，收集资源。不是行动年，是连接年。',
    3: '表达与创造之年。社交、内容创作、学习新技能。你的声音需要被听到。',
    4: '建设与实干之年。深耕现有项目，建立系统和流程。无聊但关键。',
    5: '变化与自由之年。打破常规、旅行、尝试新路径。保持灵活性。',
    6: '责任与家庭之年。关注伴侣、家人、亲密关系。平衡工作和家庭。',
    7: '反思与学习之年。向内看，减少社交，专注学习和研究。安静但丰收。',
    8: '收获与扩张之年。事业高速发展、财务机会增多。注意不要过度膨胀。',
    9: '完成与放下之年。结束旧周期，释放不再服务你的人和事。为下一个1做准备。',
    11: '直觉走强之年。相信直觉做决定，灵感层出不穷。',
    22: '大项目落地之年。你有能力把梦想变成现实，集中精力在最重要的事上。',
    33: '服务之年。利他带来最大的满足感，用你的爱去影响更多人。'
}

PERSONAL_MONTH_MEANINGS = {
    1: '适合新起点：这个月可以开始一个新习惯、新项目。',
    2: '适合合作：优先处理关系、谈判、团队协作。',
    3: '创意旺盛：适合写作、输出内容、社交活动。',
    4: '落地执行：埋头干活，把计划变成成果。',
    5: '变动频繁：可能有突如其来的人际或机会变化。',
    6: '家庭重心：家庭需求上升，平衡工作与陪伴。',
    7: '内省休息：减少应酬，适合独处和深度思考。',
    8: '财务窗口：收入机会或重大开销都可能出现。',
    9: '清理释放：不适合开始，适合结束和放手。',
    11: '灵光亮相：直觉特别准，多听听内心声音。',
    22: '效率狂升：做事特别顺，适合攻克难题。'
}

PERSONAL_DAY_MEANINGS = {
    1: '主动出击日。适合做决定、推进重要事项。',
    2: '协作沟通日。适合谈判、交流、合作。',
    3: '表达展示日。适合发表内容、社交聚会。',
    4: '执行落实日。适合完成待办、处理细节。',
    5: '灵活应变日。可能有意外信息或邀请，顺势而为。',
    6: '平衡关怀日。花时间陪家人或伴侣，修复关系。',
    7: '独处思考日。减少社交，适合读书和写东西。',
    8: '行动突破日。解决大问题、处理财务事项。',
    9: '结束归一日。不适合开始新事，适合理清收尾。'
}

WUXING_PERIOD_THEME = {
    '木': '成长生发之期。适合扩张、学习、创意项目。注意：木克土，不要做超出能力范围的承诺。',
    '火': '热情能量之期。适合社交、表达、市场活动。注意：火克金，避免冲动消费。',
    '土': '稳定沉淀之期。适合打基础、建立系统、深耕。注意：土克水，别太保守错失机会。',
    '金': '收割体现之期。适合变现、成交、成果落地。注意：金克木，小心过于功利损伤人脉。',
    '水': '流动智慧之期。适合学习、调整、内观。注意：水克火，情绪波动时不做重大决定。'
}


# ============================================================
# 三、联合解读引擎
# ============================================================

class NumerologyInterpreter:
    """数字能量深度解读生成器 v3.0"""
    
    def __init__(self, system: str = 'pythagorean'):
        self.calc = NumerologyCalculator(system)
        self.system = system
    
    # ---------- 核心解读 ----------
    
    def get_combined_reading(self, full_name: str, year: int, month: int, day: int,
                           target_year: int = 2026) -> Dict:
        """
        多维度联合解读
        
        输出不单报数字，告诉你组合含义。
        对标 numerology.com 的大师级解读。
        """
        report = self.calc.get_full_report(full_name, year, month, day)
        snap = get_numerology_snapshot(full_name, year, month, day, system=self.system)
        
        # 核心数字提取
        lp_val = report['life_path']['value']
        lp_wx = report['life_path']['wu_xing']
        lp_persona = report['life_path']['persona']
        
        ex_val = snap.get('expression')
        su_val = snap.get('soul_urge')
        pe_val = snap.get('personality')
        mn_val = snap.get('maturity_number')
        py_val = snap.get('personal_year')
        
        # 核心维度解读
        primary = self._interpret_number(lp_val, 'life_path')
        
        # 组合解读
        combo_text = self._build_combo_reading(lp_val, ex_val, su_val, pe_val)
        
        # 五维评分解读
        dim_text = self._interpret_dimensions(lp_val, lp_wx, py_val, mn_val)
        
        # 当前年份运势
        year_reading = self.get_personal_year_reading(full_name, year, month, day, target_year)
        
        # 当前月份运势
        month_reading = self.get_personal_month_reading(full_name, year, month, day, target_year)
        
        # 今日运势
        today = date.today()
        day_reading = self.get_personal_day_reading(full_name, year, month, day, 
                                                    target_year, today.month, today.day)
        
        return {
            'meta': {
                'name': full_name,
                'birth_date': f'{year}-{month:02d}-{day:02d}',
                'system': self.system,
                'generated': str(today)
            },
            'primary_number': {
                'value': lp_val,
                'name': primary['name'],
                'persona': lp_persona,
                'wu_xing': lp_wx,
                'is_master': report['life_path']['master']
            },
            'combined_reading': combo_text,
            'dimension_reading': dim_text,
            'annual_forecast': year_reading,
            'monthly_forecast': month_reading,
            'daily_forecast': day_reading,
            'numbers_detail': {
                'life_path': lp_val,
                'expression': ex_val,
                'soul_urge': su_val,
                'personality': pe_val,
                'maturity': mn_val,
                'personal_year': py_val,
                'karmic_debts': snap.get('karmic_debts', []),
                'missing_numbers': snap.get('missing_numbers', [])
            },
            'advice': self._generate_advice(lp_val, ex_val, su_val, snap.get('karmic_debts', []))
        }
    
    def _interpret_number(self, val: int, number_type: str) -> Dict:
        """单个数字含义解读"""
        v = val if val in NUMBER_MEANINGS else _reduce_number(val, keep_master=False)
        info = NUMBER_MEANINGS.get(v, NUMBER_MEANINGS.get(1))
        
        # 主数降级
        master_desc = ''
        if val in (11, 22, 33) and val != v:
            master_desc = f'（你拥有主数{val}的潜力，但目前稳定在{v}的表达层面）'
        
        return {
            'number': val,
            'reduced': v,
            'name': info['name'],
            'description': f'你是{val}号{info["name"]}{master_desc}',
            'positive_traits': info['positive'],
            'negative_traits': info['negative'],
            'career': info['career'],
            'relationship': info['relationship'],
            'health': info['health'],
            'advice': info['advice'],
            'year_theme': info['year_theme']
        }
    
    def _build_combo_reading(self, lp: int, ex: Optional[int], su: Optional[int], pe: Optional[int]) -> str:
        """构建多维度联合解读文字"""
        lp_name = NUMBER_MEANINGS.get(lp if lp in NUMBER_MEANINGS else _reduce_number(lp, False), {}).get('name', '探索者')
        ex_name = NUMBER_MEANINGS.get(ex if ex and ex in NUMBER_MEANINGS else _reduce_number(ex or 1, False), {}).get('name', '表达者')
        su_name = NUMBER_MEANINGS.get(su if su and su in NUMBER_MEANINGS else _reduce_number(su or 1, False), {}).get('name', '感受者')
        
        # 性格组合模式
        if ex and su:
            patterns = []
            ex_v = ex if ex in NUMBER_MEANINGS else _reduce_number(ex, False)
            su_v = su if su in NUMBER_MEANINGS else _reduce_number(su, False)
            
            if lp_v := (lp if lp in NUMBER_MEANINGS else _reduce_number(lp, False)):
                if lp_v == ex_v == su_v:
                    patterns.append(f'你的三重数字竟然都是{lp_v}号——这意味着你不是"有某种特质"，你几乎就是特质的化身。"{NUMBER_MEANINGS[lp_v]["name"]}"的气息浸透你人生的每一个角落。')
                elif lp_v == ex_v:
                    patterns.append(f'你的核心本质({lp_v})与外在表达({ex_v})一致。你是一个表里如一的人，不伪装、不迎合。')
                elif abs(lp_v - ex_v) <= 3:
                    patterns.append(f'你的本质({lp_v}号{lp_name})和外在表达({ex_v}号{ex_name})相近，内外基本一致，略有细微差异。')
                else:
                    patterns.append(f'你的本质({lp_v}号{lp_name})和外在表达({ex_v}号{ex_name})有较大差异——你看起来是一个{ex_name}，但内心深处是{lp_name}。这种张力是你的力量来源。')
                
                if su_v == lp_v:
                    patterns.append(f'你内心最深的驱动力({su_v}号)和你的人生方向({lp_v}号)高度一致，活得"自洽"——你的直觉往往为你做出正确的选择。')
                elif su_v == 7 and lp_v != 7:
                    patterns.append(f'你的灵魂渴望深度({su_v}号智者)，但人生道路({lp_v}号{lp_name})要求你更外向。这内在的拉扯是你成长的燃料。')
                elif su_v in (2, 6) and lp_v in (1, 8):
                    patterns.append(f'你内心渴望连接和温暖({su_v}号)，但外在的你必须强壮果断({lp_v}号)。你不是冷漠，只是还没学会让别人看到你的柔软。')
                elif lp_v in (3, 5, 9) and su_v in (4, 8):
                    patterns.append(f'你表现得自由洒脱({lp_v}号)，内心深处却渴望安全感和秩序({su_v}号)。"自由的斗士"与"安定的渴望者"都是你。')
            
            return '\n'.join(patterns) if patterns else f'你是{lp}号{lp_name}。'
        
        return f'你是{lp}号{lp_name}。'
    
    def _interpret_dimensions(self, lp: int, wx: str, py: int, mn: Optional[int]) -> str:
        """五维生活领域解读（自然语言版）"""
        info = NUMBER_MEANINGS.get(lp if lp in NUMBER_MEANINGS else _reduce_number(lp, False), {})
        mn_v = _reduce_number(mn or 1, False) if mn else None
        mn_info = NUMBER_MEANINGS.get(mn_v, {}) if mn_v else {}
        
        lines = []
        lines.append(f'【事业】{info.get("career", "适合你热爱的领域")}')
        lines.append(f'【感情】{info.get("relationship", "关系中允许你做自己最重要")}')
        lines.append(f'【健康】{info.get("health", "保持生活和工作的平衡")}')
        
        if mn:
            lines.append(f'【成熟方向】35岁后的人生将向{mn}号{mn_info.get("name","整合者")}过渡，{mn_info.get("advice","发挥后半生的潜力")}')
        
        lines.append(f'【当前能量】今年你处于个人年{py}，"{PERSONAL_YEAR_MEANINGS.get(py, "调整与过渡之年")}"')
        
        lines.append(f'【五行提示】你的生命路径能量属"{wx}"。' + {
            '木': '木性成长：今年适合扩张和学习，但注意土克木——在建立规则时不要过度消耗自己。',
            '火': '火性热烈：今年适合表达和营销，但注意水克火——情绪波动时不做重大决定。',
            '土': '土性厚重：今年适合打基础和变现，但注意木克土——不要被扩张欲推着走。',
            '金': '金性锐利：今年适合变现和收割，但注意火克金——过度激进会伤及人脉和健康。',
            '水': '水性流动：今年适合学习和内观，但注意土克水——犹豫观望会错失窗口。'
        }.get(wx, ''))
        
        return '\n'.join(lines)
    
    def _generate_advice(self, lp: int, ex: Optional[int], su: Optional[int], karmic_debts: List[int]) -> List[str]:
        """生成行动建议列表"""
        advices = []
        info = NUMBER_MEANINGS.get(lp if lp in NUMBER_MEANINGS else _reduce_number(lp, False), {})
        advices.append(info.get('advice', '保持真实'))
        
        # 业力债务
        for debt in karmic_debts:
            debt_advice = {
                13: '13号业力：注意不要走捷径，把基础工作做扎实。',
                14: '14号业力：不要为了自由牺牲责任，找到平衡才是解药。',
                16: '16号业力：学会在不失去自我的前提下重建关系。',
                19: '19号业力：你不需要一个人扛全部——你的力量在于影响他人，而不是替代他人。'
            }.get(debt, '')
            if debt_advice:
                advices.append(debt_advice)
        
        # 缺失数字->成长方向
        if su:
            su_v = su if su in NUMBER_MEANINGS else _reduce_number(su, False)
            if su_v:
                su_name = NUMBER_MEANINGS.get(su_v, {}).get('name', '感受者')
                advices.append(f'听从直觉（{su_v}号{su_name}）：你内心真正的渴望比你头脑中的计划更聪明。')
        
        return advices
    
    # ---------- 周期运势 ----------
    
    def get_personal_year_reading(self, full_name: str, year: int, month: int, day: int,
                                 target_year: int = 2026) -> Dict:
        """个人年深度解读"""
        py_data = self.calc.get_personal_year(target_year, month, day)
        py_val = py_data['value']
        py_wx = py_data['wu_xing']
        
        base = PERSONAL_YEAR_MEANINGS.get(py_val, '')
        wx_theme = WUXING_PERIOD_THEME.get(py_wx, '')
        
        # 个人年+生命路径交叉分析
        lp = self.calc.get_life_path(year, month, day)['value']
        lp_v = _reduce_number(lp, False)
        py_v = _reduce_number(py_val, False)
        
        cross_analysis = ''
        diff = min(abs(py_v - lp_v), abs(py_v - lp_v - 9), abs(py_v - lp_v + 9))
        if py_v == lp_v:
            cross_analysis = f'今年个人年{py_val}与你的生命路径{lp}共振——这是你的年份，能量高度对齐。'
        elif diff <= 2:
            cross_analysis = f'个人年{py_val}与生命路径{lp}接近，今年的趋势与你的人生大方向一致，顺势而为即可。'
        elif diff <= 4:
            cross_analysis = f'个人年{py_val}与生命路径{lp}有一定张力，今年不是你的舒适区，但挑战会带来最重要的成长。'
        else:
            cross_analysis = f'个人年{py_val}与生命路径{lp}差异较大，今年你可能感觉"不像是自己"——这正是你拓展边界的契机。'
        
        return {
            'year': target_year,
            'personal_year': py_val,
            'wu_xing': py_wx,
            'theme': base,
            'wu_xing_theme': wx_theme,
            'cross_analysis': cross_analysis,
            'raw_data': py_data
        }
    
    def get_personal_month_reading(self, full_name: str, year: int, month: int, day: int,
                                  target_year: int = 2026, target_month: Optional[int] = None) -> Dict:
        """个人月解读"""
        if target_month is None:
            target_month = datetime.now().month
        
        py = self.calc.get_personal_year(target_year, month, day)['value']
        py_r = _reduce_number(py, False)
        
        pm_raw = py_r + target_month
        pm_val = _reduce_number(pm_raw, False)
        pm_master = pm_val in {11, 22, 33}
        
        base = PERSONAL_MONTH_MEANINGS.get(pm_val, PERSONAL_MONTH_MEANINGS.get(
            pm_val if pm_val <= 9 else _reduce_number(pm_val, False), ''))
        
        # 月度五行
        month_wx_map = {1:'水', 2:'土', 3:'木', 4:'木', 5:'土', 6:'金', 7:'金', 8:'土', 9:'火',
                        11:'木', 22:'土', 33:'火'}
        pm_wx = month_wx_map.get(pm_val, '土')
        wx_theme = WUXING_PERIOD_THEME.get(pm_wx, '')
        
        return {
            'year_month': f'{target_year}-{target_month:02d}',
            'personal_month': pm_val,
            'wu_xing': pm_wx,
            'theme': base,
            'wu_xing_theme': wx_theme,
            'is_master': pm_master
        }
    
    def get_personal_day_reading(self, full_name: str, year: int, month: int, day: int,
                                target_year: int = 2026, target_month: Optional[int] = None,
                                target_day: Optional[int] = None) -> Dict:
        """个人日解读"""
        today = date.today()
        if target_month is None:
            target_month = today.month
        if target_day is None:
            target_day = today.day
        
        py = self.calc.get_personal_year(target_year, month, day)['value']
        py_r = _reduce_number(py, False)
        
        pm_raw = py_r + target_month
        pm_val = _reduce_number(pm_raw, False)
        
        pd_raw = pm_val + target_day
        pd_val = _reduce_number(pd_raw, False)
        
        base = PERSONAL_DAY_MEANINGS.get(pd_val if pd_val <= 9 else _reduce_number(pd_val, False),
                                         '听从内心的一天。')
        
        # 日五行
        day_wx_map = {1:'水', 2:'土', 3:'木', 4:'木', 5:'土', 6:'金', 7:'金', 8:'土', 9:'火'}
        pd_wx = day_wx_map.get(pd_val if pd_val <= 9 else _reduce_number(pd_val, False), '土')
        
        # 联合解读：今日重点
        signs = []
        if pd_val in (1, 8):
            signs.append('今天适合主动出击，推进重要事项')
        elif pd_val in (2, 6):
            signs.append('今天适合处理人际关系，修复或加强连接')
        elif pd_val == 5:
            signs.append('今天可能有意外惊喜，保持开放心态')
        elif pd_val == 7:
            signs.append('今天适合独处和思考，减少社交')
        elif pd_val == 9:
            signs.append('今天适合结束和放手，不适合开始新事')
        
        return {
            'date': f'{target_year}-{target_month:02d}-{target_day:02d}',
            'personal_day': pd_val,
            'wu_xing': pd_wx,
            'theme': base,
            'signs': signs,
            'advice': f'{base} 今日五行属{pd_wx}。',
            'raw_personal_year': py
        }
    
    # ---------- 快照接口（与六合兼容） ----------
    
    def get_for_cross(self, full_name: str, year: int, month: int, day: int,
                     target_year: int = 2026) -> Dict:
        """六合交叉验证接口"""
        reading = self.get_combined_reading(full_name, year, month, day, target_year)
        return {
            'primary_value': reading['primary_number']['value'],
            'primary_name': reading['primary_number']['name'],
            'primary_wu_xing': reading['primary_number']['wu_xing'],
            'is_master': reading['primary_number']['is_master'],
            'score': 8.0 if reading['primary_number']['is_master'] else 6.5,
            'combined_reading': reading['combined_reading'],
            'dimension_reading': reading['dimension_reading'],
            'annual_theme': reading['annual_forecast']['theme'],
            'daily_advice': reading['daily_forecast']['advice'],
            'advices': reading['advice']
        }


# ============================================================
# 四、顶层API（直接使用）
# ============================================================

def get_reading(full_name: str, year: int, month: int, day: int,
               target_year: int = 2026, system: str = 'pythagorean') -> Dict:
    """顶层解读API"""
    interpreter = NumerologyInterpreter(system)
    return interpreter.get_combined_reading(full_name, year, month, day, target_year)


def get_period_forecasts(full_name: str, year: int, month: int, day: int,
                        target_year: int = 2026, include_month: bool = True,
                        include_day: bool = True) -> Dict:
    """单独获取周期运势"""
    interpreter = NumerologyInterpreter()
    result = {'annual': interpreter.get_personal_year_reading(full_name, year, month, day, target_year)}
    
    if include_month:
        result['monthly'] = interpreter.get_personal_month_reading(full_name, year, month, day, target_year)
    
    if include_day:
        result['daily'] = interpreter.get_personal_day_reading(full_name, year, month, day, target_year)
    
    return result


def format_reading_for_push(reading: Dict) -> str:
    """格式化输出，适合Telegram/公众号推送"""
    meta = reading['meta']
    primary = reading['primary_number']
    
    lines = []
    lines.append(f"🐢 河图数字能量解读 · {meta['name']}")
    lines.append(f"━━━━━━━━━━━━━━━━")
    lines.append(f"")
    lines.append(f"【核心数字】{primary['value']}号 · {primary['name']} · {primary['wu_xing']}性")
    lines.append(f"")
    lines.append(f"📖 {reading['combined_reading']}")
    lines.append(f"")
    lines.append(f"━━━ 领域能量 ━━━")
    lines.append(f"{reading['dimension_reading']}")
    lines.append(f"")
    lines.append(f"━━━ 年度运势 ━━━")
    lines.append(f"个人年{reading['annual_forecast']['personal_year']}：{reading['annual_forecast']['theme']}")
    if reading['annual_forecast'].get('cross_analysis'):
        lines.append(f"{reading['annual_forecast']['cross_analysis']}")
    lines.append(f"")
    lines.append(f"━━━ 本月 ━━━")
    lines.append(f"个人月{reading['monthly_forecast']['personal_month']}：{reading['monthly_forecast']['theme']}")
    lines.append(f"")
    lines.append(f"━━━ 今日 ━━━")
    lines.append(f"个人日{reading['daily_forecast']['personal_day']}：{reading['daily_forecast']['theme']}")
    if reading['daily_forecast'].get('signs'):
        for s in reading['daily_forecast']['signs']:
            lines.append(f"  · {s}")
    lines.append(f"")
    lines.append(f"━━━ 河图建议 ━━━")
    for a in reading['advice']:
        lines.append(f"  ✓ {a}")
    lines.append(f"")
    lines.append(f"— 河图 🐢")
    
    return '\n'.join(lines)


# ============================================================
# 测试
# ============================================================

if __name__ == '__main__':
    print("=== 数字能量解读引擎 v3.0 — 测试 ===\n")
    
    interpreter = NumerologyInterpreter()
    
    # 创始人
    print("--- 创始人 (OpenClaw Founder, 1990-11-10) ---")
    reading = get_reading('OpenClaw Founder', 1990, 11, 10)
    print(f"核心数字: {reading['primary_number']['value']}号 · {reading['primary_number']['name']} · {reading['primary_number']['wu_xing']}性")
    print(f"\n联合解读:\n{reading['combined_reading']}")
    print(f"\n五维解读:\n{reading['dimension_reading']}")
    print(f"\n个人年: {reading['annual_forecast']['personal_year']} - {reading['annual_forecast']['theme']}")
    print(f"个人月: {reading['monthly_forecast']['personal_month']} - {reading['monthly_forecast']['theme']}")
    print(f"个人日: {reading['daily_forecast']['personal_day']} - {reading['daily_forecast']['theme']}")
    print(f"\n建议:")
    for a in reading['advice']:
        print(f"  · {a}")
    
    print("\n\n--- 格式化推送 ---")
    print(format_reading_for_push(reading))
    
    print("\n\n✅ 数字能量解读引擎 v3.0 测试完毕")
