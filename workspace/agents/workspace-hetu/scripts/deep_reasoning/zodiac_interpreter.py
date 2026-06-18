#!/usr/bin/env python3
"""
星座深度解读生成器 v3.0 — Zodiac Interpreter
===============================================
功能：
  - 从zodiac_scores的评分数据生成自然语言解读
  - 个人星盘多维度解读（太阳/月亮/上升/行星宫位+相位）
  - 合盘解读（两人兼容性的自然语言分析）
  - 周期运势（周运/月运/年运文本生成）
  - 对标：陶白白级的内容表达力 × 河图级量化评分

对比全球最佳实践：
  ✅ 对标陶白白：情感共鸣 × 案例深度 （我们的优势是有量化评分支撑）
  ✅ 对标Co-Star：每日推送 + 个人化解读 （我们多了五行化视角）
  ✅ 对标TimePassages：合盘深度解读
  ✅ 河图独有：五行能量转换 + 星座×能量评分交叉

商用Ready ⭐⭐⭐⭐⭐

作者：河图 🐢
版本：v3.0 | 2026-05-05

依赖: zodiac_scores.py (需kerykeion)
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from zodiac_scores import (
        get_all_scores, get_synastry_scores, AspectEngine,
        ZODIAC_DIMENSION_SCORES, PLANET_DIM_WEIGHTS,
        PLANET_BASE_STRENGTH, HOUSE_STRENGTH, ELEMENT_WU_XING
    )
    from zodiac_scores import KERYKEION_AVAILABLE
    from kerykeion import AstrologicalSubjectFactory
    ZODIAC_ENGINE_AVAILABLE = True
except ImportError as e:
    ZODIAC_ENGINE_AVAILABLE = False
    print(f"⚠️  Zodiac engine unavailable: {e}")


# ============================================================
# 一、星座人格解读库
# ============================================================

SUN_SIGN_PERSONALITY = {
    'Ari': {
        'name': '白羊座',
        'element': '火',
        'wu_xing': '火',
        'ruling_planet': '火星',
        'positive': ['勇敢', '直率', '行动力强', '热忱', '开拓精神'],
        'negative': ['冲动', '急躁', '自我', '没耐心', '不顾后果'],
        'personality': '白羊座是一团行动的火。你不需要完美的计划，你只需要第一个冲出去。你的直觉是"先做再说"，这让你在大多数人还在犹豫时已经拿到结果。但你的软肋也在这里——你常常因为行动太快而错过了本该注意的细节。',
        'love': '白羊座喜欢追逐的过程。你不需要对方太完美，但需要对方"有意思"。直接的表达方式有时候会伤人——不是因为你说错了，而是因为你没说那句话之前的沉默。',
        'career': '适合开创型、战斗型的工作。创业、销售、市场、户外、竞技。你受不了重复枯燥的办公室，你需要在行动中找到成就感。',
        'advice': '学会在冲出去之前深呼吸三次。真正的勇气不是永远向前冲，而是知道什么时候该停下来。'
    },
    'Tau': {
        'name': '金牛座',
        'element': '土',
        'wu_xing': '土',
        'ruling_planet': '金星',
        'positive': ['稳定', '务实', '有毅力', '品味好', '可靠'],
        'negative': ['固执', '懒惰', '占有欲强', '抗拒改变', '物质主义'],
        'personality': '金牛座是大地最忠实的子民。你相信看得见摸得着的东西——一顿好饭、一张舒服的床、一个可靠的账户余额。你不需要轰轰烈烈，你需要稳稳的幸福。但如果有人触碰你认定的"安全感"，你的固执程度超乎所有人的想象。',
        'love': '金牛座的爱是细水长流。你不会说太多漂亮话，但你会记得对方喜欢吃什么。你的占有欲不是不信任，而是你太怕失去好不容易建立起来的东西。',
        'career': '适合金融、会计、品酒/美食、设计、收藏、农业。你的耐心和务实让你在任何需要长期积累的领域都有优势。',
        'advice': '人生不是在储蓄，是在体验。偶尔花一笔"没有理由"的钱，做一件"没有计划"的事，你会发现另一片天地。'
    },
    'Gem': {
        'name': '双子座',
        'element': '风',
        'wu_xing': '金',
        'ruling_planet': '水星',
        'positive': ['聪明', '幽默', '适应力强', '好奇', '沟通高手'],
        'negative': ['善变', '肤浅', '说得多做得少', '缺乏耐心', '表里不一'],
        'personality': '双子座不是一个人在战斗。你的脑子里随时都有两个声音在对话——这就是你永远不无聊但也永远不安定的原因。你天生好奇，对各种话题都有话可说，但当别人以为你很"懂"的时候，你可能已经飞向下一个兴趣了。',
        'love': '双子座最吸引人的不是颜值不是财富，是那种"和你在一起永远不会无聊"的感觉。但问题也在这里——你太有趣了，以至于别人常常怀疑自己是不是你众多新鲜事物中的一个。',
        'career': '适合媒体、写作、演讲、销售、咨询、教育。任何需要"用语言创造价值"的领域都是你的舞台。',
        'advice': '深度比广度更能建立你的价值。选一个赛道深耕三年，你会发现自己比"什么都会"时更有说服力。'
    },
    'Can': {
        'name': '巨蟹座',
        'element': '水',
        'wu_xing': '水',
        'ruling_planet': '月亮',
        'positive': ['细腻', '温柔', '照顾他人', '直觉强', '记性好'],
        'negative': ['情绪化', '过度保护', '逃避冲突', '太过敏感'],
        'personality': '巨蟹座的内心是一个老房子——外面看起来不动声色，里面满满都是回忆。你太容易感知别人的情绪，也太容易被过去牵动。你的铠甲是对外人的冷漠，软肋是对自己在乎的人毫无底线。',
        'love': '巨蟹座的爱是"我用我的方式照顾你"。你会记得对方的喜好、忌讳、说过的话，但这有时候变成了一种压力——你以为的"关心"在对方看来可能是"过度介入"。',
        'career': '适合心理咨询、健康护理、教育、HR、餐饮、家政行业。你天生的共情力在任何需要"理解人"的领域都是王牌。',
        'advice': '你不需要为所有人的情绪负责。你的温柔是礼物，不是义务——学会说"不"，你才能更好地保护你的柔软。'
    },
    'Leo': {
        'name': '狮子座',
        'element': '火',
        'wu_xing': '火',
        'ruling_planet': '太阳',
        'positive': ['自信', '大方', '领导力', '热情', '慷慨'],
        'negative': ['自负', '爱面子', '控制欲', '听不进意见', '怕被忽视'],
        'personality': '狮子座天生站在舞台中央。你不需要向别人证明什么——你的存在本身就发出光芒。问题是，你也习惯了站在聚光灯下，当灯光移开的时候，你会感到一种说不出的恐慌。你对批评的抗拒不是骄傲，而是怕自己真的不够好。',
        'love': '狮子座的爱是阳光灿烂的。你会给对方最好的东西、最实在的支持。但你需要的回报是——对方要"看到你"。一句真诚的赞美能让你开心一整天。',
        'career': '适合管理、演艺、销售、演讲、品牌、创业。你的领导力是天生的，但你的真正弱点是一对一的耐心。',
        'advice': '真正的王者不需要时刻被承认。偶尔退到第二线，你会发现团队比你想象中更能干。'
    },
    'Vir': {
        'name': '处女座',
        'element': '土',
        'wu_xing': '土',
        'ruling_planet': '水星',
        'positive': ['细致', '靠谱', '分析力', '责任心', '完美主义'],
        'negative': ['挑剔', '焦虑', '过于苛刻', '唠叨', '不放过自己'],
        'personality': '处女座的大脑是一台精密的分析仪器。你能看到别人看不到的细节，能发现问题，能提前预判风险。这本是你的超能力——但如果一直开着这个开关，你会发现自己不仅挑剔别人，更挑剔自己，永远觉得"还不够完美"。',
        'love': '处女座的爱是用行动表达的。你不会说太多甜言蜜语，但你会默默地把对方的生活安排得井井有条。你的挑剔其实是你在意的表现——不在乎的人才懒得说。',
        'career': '适合数据分析、审计、医疗、编辑、行政、项目管理。你的系统化思维在任何需要"精确"的领域都是无价之宝。',
        'advice': '人生不是一场考试，不需要每道题都拿满分。接受"差不多"也是一种智慧。'
    },
    'Lib': {
        'name': '天秤座',
        'element': '风',
        'wu_xing': '金',
        'ruling_planet': '金星',
        'positive': ['优雅', '公平', '社交达人', '审美在线', '调解能力'],
        'negative': ['优柔寡断', '逃避冲突', '表面功夫', '依赖他人评价'],
        'personality': '天秤座是人际关系的艺术家。你天生知道如何在人群中保持优雅和平衡，你的社交技能写在基因里。但你的命门是——太在意别人的看法了。你害怕冲突、害怕做错选择，所以常常在"要不要说"和"要不要做"之间纠结到最后一刻。',
        'love': '天秤座的爱情是一场美丽的对话。你需要浪漫、需要仪式感、需要被欣赏。你的优柔寡断在感情里可能会让对方觉得你不够坚定——但事实上，你不是不坚定，只是你看到了一切可能。',
        'career': '适合法律、外交、公关、设计、时尚、演艺。你的审美和社交能力在任何需要"美和关系"的领域都是核心竞争力。',
        'advice': '不是所有事情都需要权衡。有时候闭着眼睛选一个，然后全力以赴去证明这个选择是对的——这本身就是一种优雅。'
    },
    'Sco': {
        'name': '天蝎座',
        'element': '水',
        'wu_xing': '水',
        'ruling_planet': '冥王星/火星',
        'positive': ['深邃', '忠诚', '直觉力强', '意志坚定', '洞察力'],
        'negative': ['占有欲强', '多疑', '复仇心', '极端', '喜欢控制'],
        'personality': '天蝎座的内心深处是一个巨大的谜。你不轻易向人敞开，因为你太清楚人性的复杂。你的直觉强烈到可以"闻"到别人的谎言。你的力量在于你的深度——大多数人活在水面，你活在海底。',
        'love': '天蝎座的爱不是恋爱——是信仰。你把自己全部投入、全部信任、全部付出。所以一旦被背叛，你的痛苦也不是伤心——是愤怒。你需要的是一个值得你托付全部的"一个人"，而不是无数个"还不错"的人。',
        'career': '适合侦探、调查记者、心理学、投资、科研、战略咨询。你的洞察力和韧性让你在任何需要"穿透表层"的领域无敌。',
        'advice': '不是所有秘密都需要揭开，不是所有伤口都需要追究。学会放下，是你这一生最重要的修行。'
    },
    'Sag': {
        'name': '射手座',
        'element': '火',
        'wu_xing': '火',
        'ruling_planet': '木星',
        'positive': ['乐观', '爱冒险', '诚实', '有远见', '热爱自由'],
        'negative': ['不靠谱', '口无遮拦', '缺乏耐心', '逃避责任', '过度乐观'],
        'personality': '射手座是永远在路上的人。你相信远方大于当下，相信可能性大过现实。你的乐观是真的乐观——不是因为你看不到困难，而是你觉得困难就是旅程的一部分。你不喜欢被任何东西束缚——工作、关系、城市，只要感觉"被关住"，你就会想要逃跑。',
        'love': '射手座的爱是自由的爱。你需要一个能跟你一起冒险的伴侣，而不是一个在家里等你回来的人。你的诚实有时候伤人——不是因为你有恶意，而是因为你懒得包装。',
        'career': '适合旅游、外派、教育、出版、体育、国际贸易。任何能让你"移动"和"增长见识"的领域都适合你。',
        'advice': '自由不是逃避的借口。你可以在一个地方扎根的同时保持对世界的好奇——稳定和自由从来不是对立面。'
    },
    'Cap': {
        'name': '摩羯座',
        'element': '土',
        'wu_xing': '土',
        'ruling_planet': '土星',
        'positive': ['责任感', '自律', '有目标', '务实', '坚忍'],
        'negative': ['冷漠', '悲观', '工作狂', '压抑情感', '太现实'],
        'personality': '摩羯座从小就像个小大人。你不相信运气，你相信计划、执行、坚持。你看似高冷的外表下藏着一颗焦虑的心——你太怕自己不够好，所以一直在努力证明自己。你的悲观看似消极，实际是风险管理——你永远在准备最坏的预案。',
        'love': '摩羯座的爱情像爬山——起步慢，过程辛苦，但到顶那一刻的风景值回票价。你不会甜言蜜语，但你会用行动证明"我在"。你不会轻易开始一段关系，但一旦确定了，你会负责到底。',
        'career': '适合CEO、金融、建筑、法律、公务员、传统行业。你的自律和持久力在每一个需要"坚持"的领域都是最大的护城河。',
        'advice': '人生不只有山顶的风光。偶尔停下来看看路边的花，你才会发现——你为之奋斗的一切，如果没有人分享，真的没太大意义。'
    },
    'Aqu': {
        'name': '水瓶座',
        'element': '风',
        'wu_xing': '金',
        'ruling_planet': '天王星/土星',
        'positive': ['独立', '创新', '理想主义', '社交网络', '前瞻思维'],
        'negative': ['叛逆', '疏离', '不按常理出牌', '情绪隔离'],
        'personality': '水瓶座活在未来。你现在的想法可能在五年后才会被主流接受。你的独立不是孤僻——是你太清楚自己和这个世界不在同一频率。你的叛逆不是青春期延迟——是你的判断标准不是"大家说什么"，而是"什么是对的"。',
        'love': '水瓶座的爱情是友情+革命友谊。你需要一个能跟你在思想上共振的人，一个能跟你讨论"未来"而不是只讨论"明天吃什么"的人。你的感情的表达方式是"非典型"的——你可能是在帮对方解决问题的时候，才意识到这是爱的一种形式。',
        'career': '适合科技、创新、公益、科研、艺术、互联网。你的超前思维在任何需要"变革"的领域都是核心竞争力。',
        'advice': '与世界不同频不代表你错了，也不代表你不需要连接。你需要的是找到那一群"和你一样"的人。'
    },
    'Pis': {
        'name': '双鱼座',
        'element': '水',
        'wu_xing': '水',
        'ruling_planet': '海王星/木星',
        'positive': ['艺术天赋', '共情力', '直觉', '浪漫', '灵性'],
        'negative': ['逃避现实', '过度敏感', '缺乏边界', '受害者心态'],
        'personality': '双鱼座的灵魂是没有边界的。你能感受到别人的情绪像感受自己的情绪一样真实——这是一种天赋，也是一种诅咒。你的创造力丰富到有时候连你自己都分不清现实和想象。你太容易"为了别人牺牲自己"，最后连自己在哪里都忘了。',
        'love': '双鱼座的爱像一首诗人还没写完的诗。你充满了浪漫的想象，你最会制造"氛围感"。但你的问题在于——你爱的可能是"爱情本身"而不是眼前那个人。当现实打破了幻想，你会感到幻灭。',
        'career': '适合艺术、音乐、设计、电影、心理治疗、公益。你的创造力和共情力在需要"感染别人"的领域无可替代。',
        'advice': '你的善良需要边界，你的浪漫需要现实。你不需要屏蔽自己的感受力，但至少学会分辨："这是我的情绪，还是别人的？"'
    }
}


# ============================================================
# 二、相位解读库
# ============================================================

ASPECT_INTERPRETATIONS = {
    'conjunction': {
        'name': '合相',
        'template': '{p1}与{p2}形成强烈的合相——两颗行星的能量在同一个频道上共振。这是一种"放大"的相位。',
        'note': '能量太集中可能变成过度或不平衡'
    },
    'opposition': {
        'name': '对分相',
        'template': '{p1}和{p2}在对立位置——这是一个人内在的拉锯战。你的一半渴望A，另一半渴望B。',
        'note': '整合对立面是成长的关键'
    },
    'trine': {
        'name': '三分相',
        'template': '{p1}与{p2}形成和谐的拱相位。这是天赋相位——能量流动顺畅，一切来得自然。',
        'note': '太顺畅反而容易忽视'
    },
    'square': {
        'name': '四分相',
        'template': '{p1}与{p2}形成紧张的刑相位。这是一种"不舒服但有用"的相位——压力让你必须行动。',
        'note': '压力是成长的催化剂'
    },
    'sextile': {
        'name': '六分相',
        'template': '{p1}与{p2}形成六合相位——机会相位。这不是天赋，但通过努力可以变成优势。',
        'note': '需要主动抓住机会'
    },
    'quincunx': {
        'name': '补十二分相',
        'template': '{p1}与{p2}形成不太舒适的150°相位。这是一股需要你调整和适应的能量流。',
        'note': '适应过程中可能会有困惑'
    },
    'semi-sextile': {
        'name': '半六分相',
        'template': '{p1}与{p2}形成30°相位——微小但有趣的影响。两颗行星在相邻星座，视角互补。',
        'note': '微调即可获益'
    }
}

PLANET_NAMES_CN = {
    'Sun': '太阳', 'Moon': '月亮', 'Mercury': '水星', 'Venus': '金星',
    'Mars': '火星', 'Jupiter': '木星', 'Saturn': '土星',
    'Uranus': '天王星', 'Neptune': '海王星', 'Pluto': '冥王星'
}

PLANET_MEANINGS = {
    'Sun': '自我核心、身份认同、生命力',
    'Moon': '情感、潜意识、安全感需求',
    'Mercury': '思维方式、沟通模式、学习风格',
    'Venus': '爱情、审美、价值观、亲密关系',
    'Mars': '行动力、欲望、竞争、原始驱动力',
    'Jupiter': '成长、运气、扩张、信念系统',
    'Saturn': '责任、限制、纪律、人生功课',
    'Uranus': '变革、独立、反叛、突然的变化',
    'Neptune': '梦想、幻想、灵性、消融边界',
    'Pluto': '转化、权力、掌控、深层心理'
}

TRANSIT_ASPECT_IMPACTS = {
    ('Jupiter', 'Sun'): '木星推动太阳，利扩张、自信提升、贵人运和公开表达。',
    ('Jupiter', 'Moon'): '木星照亮月亮，情绪更乐观，适合修复关系与家庭议题。',
    ('Saturn', 'Sun'): '土星压到太阳，责任变重、节奏变慢，但利于打基础与立规矩。',
    ('Saturn', 'Moon'): '土星碰月亮，容易感到孤独或情绪收缩，需要照顾心理韧性。',
    ('Uranus', 'Sun'): '天王星冲击太阳，适合破局、换赛道、升级身份，但变化突然。',
    ('Neptune', 'Sun'): '海王星影响太阳，灵感增强，但边界感下降，容易理想化。',
    ('Pluto', 'Sun'): '冥王星作用太阳，这是深层蜕变期，权力、掌控、自我定义会重组。',
    ('Jupiter', 'Venus'): '木星加持金星，利感情、合作、审美和财富机会。',
    ('Saturn', 'Venus'): '土星压金星，关系进入现实检验期，利长期承诺，不利轻松暧昧。',
    ('Jupiter', 'Mars'): '木星推火星，行动力和胆量提升，适合冲项目，但别过度冒进。',
    ('Saturn', 'Mars'): '土星压火星，行动受阻，需要耐心和方法，不适合硬刚。',
    ('Uranus', 'Mercury'): '天王星激活水星，想法突变、创意增加，适合创新但不宜草率。'
}

PROGRESSION_THEMES = {
    'Sun': '推运太阳代表人生主线正在转向新的身份主题。',
    'Moon': '推运月亮代表情绪节奏与生活重心正在移动。',
    'Mercury': '推运水星代表学习、表达和认知框架在升级。',
    'Venus': '推运金星代表价值观、关系偏好和审美结构在变化。',
    'Mars': '推运火星代表你正在重设行动方式与欲望表达。'
}

SOLAR_RETURN_THEMES = {
    'Fire': '返照太阳落火元素，全年适合主动进攻、扩大曝光、建立个人主导权。',
    'Earth': '返照太阳落土元素，全年主题偏务实落地、财务规划、系统建设。',
    'Air': '返照太阳落风元素，全年主题偏合作、传播、社交网络和认知升级。',
    'Water': '返照太阳落水元素，全年主题偏情感、内在修复、关系整合与感受力。'
}


# ============================================================
# 三、星座解读引擎
# ============================================================

class ZodiacInterpreter:
    """星座深度解读生成器 v3.0"""
    
    def __init__(self):
        self.aspect_engine = None
        if KERYKEION_AVAILABLE:
            from zodiac_scores import AspectEngine
            self.aspect_engine = AspectEngine()
    
    # ---------- 核心星盘解读 ----------
    
    def get_natal_reading(self, year: int, month: int, day: int,
                         hour: int = 12, minute: int = 0,
                         lng: float = 116.4, lat: float = 39.9,
                         tz_str: str = 'Asia/Shanghai') -> Dict:
        """本命盘深度解读"""
        if not ZODIAC_ENGINE_AVAILABLE:
            return self._get_fallback_reading(year, month, day)
        
        try:
            # 获取评分数据
            scores, detail = get_all_scores(
                year=year, month=month, day=day,
                hour=hour, minute=minute,
                lng=lng, lat=lat, tz_str=tz_str
            )
            
            raw = detail.get('raw_data', {})
            sun_sign = raw.get('sun_sign', '')
            moon_sign = raw.get('moon_sign', '')
            asc_sign = raw.get('ascendant_sign', '')
            
            # 太阳星座深度解读
            sun_reading = self._interpret_sun_sign(sun_sign) if sun_sign else None
            
            # 月亮星座解读
            moon_reading = self._interpret_sun_sign(moon_sign) if moon_sign else sun_reading
            
            # 上升星座
            asc_reading = self._interpret_sun_sign(asc_sign) if asc_sign else sun_reading
            
            # 相位解读
            aspects = detail.get('aspects', [])
            aspect_texts = self._interpret_aspects(aspects)
            
            # 行星解读
            planets_detail = raw.get('planets', [])
            planet_readings = self._interpret_planets(planets_detail) if planets_detail else []
            
            # 五维评分解读
            dim_texts = self._interpret_dimension_scores(scores)
            
            # 综合人格画像
            profile = self._build_profile(sun_reading, moon_reading, asc_reading, scores)
            transit_reading = self.get_transit_reading(year, month, day, hour, minute, lng, lat, tz_str)
            progression_reading = self.get_progression_reading(year, month, day, hour, minute, lng, lat, tz_str)
            solar_return_reading = self.get_solar_return_reading(year, month, day, hour, minute, lng, lat, tz_str)
            
            return {
                'engine': 'zodiac_interpreter_v3.0',
                'scores': scores,
                'profile': profile,
                'sun_sign': {'sign': sun_sign, **sun_reading} if sun_reading else {'sign': sun_sign},
                'moon_sign': {'sign': moon_sign, **moon_reading} if moon_reading else {'sign': moon_sign},
                'ascendant': {'sign': asc_sign, **asc_reading} if asc_reading else {'sign': asc_sign},
                'dimension_readings': dim_texts,
                'aspect_readings': aspect_texts,
                'planet_readings': planet_readings,
                'transit_reading': transit_reading,
                'progression_reading': progression_reading,
                'solar_return_reading': solar_return_reading,
                'raw_data': raw
            }
            
        except Exception as e:
            return {'error': str(e), **self._get_fallback_reading(year, month, day)}
    
    def get_transit_reading(self, year: int, month: int, day: int,
                           hour: int = 12, minute: int = 0,
                           lng: float = 116.4, lat: float = 39.9,
                           tz_str: str = 'Asia/Shanghai') -> Dict:
        """实时行星过运：当前天空行星 vs 本命盘"""
        if not ZODIAC_ENGINE_AVAILABLE:
            return {'summary': 'Transit 功能需要精确占星引擎支持。'}
        try:
            now = datetime.now()
            natal_subject = AstrologicalSubjectFactory.from_birth_data(
                'Natal', year, month, day, hour, minute, lng=lng, lat=lat, tz_str=tz_str
            )
            transit_subject = AstrologicalSubjectFactory.from_birth_data(
                'Transit', now.year, now.month, now.day, now.hour, now.minute, lng=lng, lat=lat, tz_str=tz_str
            )
            natal = natal_subject.model_dump()
            transit = transit_subject.model_dump()

            natal_pos = {}
            transit_pos = {}
            for p in ['sun','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto']:
                nd = natal.get(p)
                td = transit.get(p)
                if nd and isinstance(nd, dict):
                    natal_pos[p.capitalize()] = nd.get('abs_pos', 0)
                if td and isinstance(td, dict):
                    transit_pos[p.capitalize()] = td.get('abs_pos', 0)

            aspects = []
            if self.aspect_engine:
                for tp, tpos in transit_pos.items():
                    for np, npos in natal_pos.items():
                        angle = self.aspect_engine._angle_diff(tpos, npos)
                        result = self.aspect_engine._detect_aspect(angle)
                        if result:
                            a_name, strength = result
                            aspects.append({
                                'transit_planet': tp,
                                'natal_planet': np,
                                'aspect': a_name,
                                'strength': strength,
                                'angle': round(angle, 1)
                            })
            aspects = sorted(aspects, key=lambda x: x['strength'], reverse=True)[:8]

            focus = []
            for a in aspects[:4]:
                key = (a['transit_planet'], a['natal_planet'])
                text = TRANSIT_ASPECT_IMPACTS.get(key)
                if text:
                    focus.append(f"{PLANET_NAMES_CN.get(a['transit_planet'], a['transit_planet'])} {a['aspect']} 本命{PLANET_NAMES_CN.get(a['natal_planet'], a['natal_planet'])}：{text}")
                else:
                    focus.append(f"{PLANET_NAMES_CN.get(a['transit_planet'], a['transit_planet'])}正在以{a['aspect']}影响本命{PLANET_NAMES_CN.get(a['natal_planet'], a['natal_planet'])}。")

            return {
                'date': now.strftime('%Y-%m-%d %H:%M'),
                'top_aspects': aspects,
                'focus': focus,
                'summary': '当前过运显示：外部环境正在与你的本命结构发生实时互动，适合按重点相位做短中期判断。'
            }
        except Exception as e:
            return {'summary': f'Transit 计算失败：{e}'}

    def get_progression_reading(self, year: int, month: int, day: int,
                               hour: int = 12, minute: int = 0,
                               lng: float = 116.4, lat: float = 39.9,
                               tz_str: str = 'Asia/Shanghai') -> Dict:
        """简化次限推运：一岁一天法，抓主线变化"""
        if not ZODIAC_ENGINE_AVAILABLE:
            return {'summary': 'Progression 功能需要精确占星引擎支持。'}
        try:
            today = date.today()
            age = max(0, today.year - year - ((today.month, today.day) < (month, day)))
            from datetime import timedelta
            progressed_date = date(year, month, day) + timedelta(days=age)
            prog_subject = AstrologicalSubjectFactory.from_birth_data(
                'Progressed', progressed_date.year, progressed_date.month, progressed_date.day,
                hour, minute, lng=lng, lat=lat, tz_str=tz_str
            )
            prog = prog_subject.model_dump()
            themes = []
            for key in ['sun', 'moon', 'mercury', 'venus', 'mars']:
                pd = prog.get(key)
                if pd and isinstance(pd, dict):
                    planet_cn = PLANET_NAMES_CN.get(key.capitalize(), key)
                    sign = pd.get('sign', '')
                    themes.append(f"推运{planet_cn}落在{sign}：{PROGRESSION_THEMES.get(key.capitalize(), '你的内在节奏正在变化。')}")
            return {
                'progressed_date': progressed_date.isoformat(),
                'age_reference': age,
                'themes': themes[:5],
                'summary': '推运不是看外部事件，而是看你的内在成熟主题正在往哪里移动。'
            }
        except Exception as e:
            return {'summary': f'Progression 计算失败：{e}'}

    def get_solar_return_reading(self, year: int, month: int, day: int,
                               hour: int = 12, minute: int = 0,
                               lng: float = 116.4, lat: float = 39.9,
                               tz_str: str = 'Asia/Shanghai') -> Dict:
        """简化太阳返照：以生日当年返照日为年度主题入口"""
        if not ZODIAC_ENGINE_AVAILABLE:
            return {'summary': 'Solar Return 功能需要精确占星引擎支持。'}
        try:
            current_year = datetime.now().year
            sr_subject = AstrologicalSubjectFactory.from_birth_data(
                'SolarReturn', current_year, month, day, hour, minute,
                lng=lng, lat=lat, tz_str=tz_str
            )
            sr = sr_subject.model_dump()
            sun = sr.get('sun', {}) if isinstance(sr, dict) else {}
            sign = sun.get('sign', '')
            element = sun.get('element', '')
            house = sun.get('house', '')
            return {
                'solar_return_year': current_year,
                'sun_sign': sign,
                'sun_house': house,
                'element': element,
                'theme': SOLAR_RETURN_THEMES.get(element, '这一年主题偏综合，需要结合本命盘细看。'),
                'summary': f'返照太阳落在{sign} {house}，说明你这一年的主舞台会围绕该宫位主题展开。'
            }
        except Exception as e:
            return {'summary': f'Solar Return 计算失败：{e}'}

    def _interpret_sun_sign(self, sign: str) -> Dict:
        """太阳/月亮/上升星座文本解读"""
        info = SUN_SIGN_PERSONALITY.get(sign)
        if not info:
            return {}
        
        return {
            'name': info['name'],
            'element': info['element'],
            'wu_xing': info['wu_xing'],
            'ruling_planet': info['ruling_planet'],
            'positive_traits': info['positive'],
            'negative_traits': info['negative'],
            'personality': info['personality'],
            'love': info['love'],
            'career': info['career'],
            'advice': info['advice']
        }
    
    def _interpret_aspects(self, aspects: List[Dict]) -> List[str]:
        """相位解读"""
        texts = []
        for a in aspects[:5]:
            p1 = a.get('p1', '')
            p2 = a.get('p2', '')
            aspect_type = a.get('type', '')
            info = ASPECT_INTERPRETATIONS.get(aspect_type)
            if info:
                p1_cn = PLANET_NAMES_CN.get(p1, p1)
                p2_cn = PLANET_NAMES_CN.get(p2, p2)
                text = info['template'].replace('{p1}', p1_cn).replace('{p2}', p2_cn)
                texts.append(text)
        return texts

    def _interpret_planets(self, planets_data: List) -> List[Dict]:
        """行星落位解读"""
        readings = []
        if isinstance(planets_data, list) and planets_data:
            items = planets_data[0] if isinstance(planets_data[0], list) else planets_data
            for p in items:
                if isinstance(p, dict):
                    name = p.get('name', '')
                    sign = p.get('sign', '')
                    house = p.get('house', '')
                    wx = p.get('wu_xing', '')
                    retro = p.get('retrograde', False)
                    meaning = PLANET_MEANINGS.get(name, '')
                    readings.append({
                        'planet': name,
                        'planet_cn': PLANET_NAMES_CN.get(name, name),
                        'sign': sign,
                        'house': house,
                        'wu_xing': wx,
                        'retrograde': retro,
                        'meaning': meaning
                    })
        return readings
    
    def _interpret_dimension_scores(self, scores: Dict[str, float]) -> Dict[str, str]:
        """五维评分→自然语言"""
        texts = {}
        for dim, score in scores.items():
            if score >= 8.0:
                texts[dim] = '强势'
            elif score >= 6.5:
                texts[dim] = '良好'
            elif score >= 5.0:
                texts[dim] = '均衡'
            elif score >= 3.5:
                texts[dim] = '偏弱，需关注'
            else:
                texts[dim] = '薄弱，建议调整'
        return texts
    
    def _build_profile(self, sun, moon, asc, scores: Dict[str, float]) -> str:
        """综合人格画像"""
        parts = []
        
        if sun and asc:
            sun_name = sun.get('name', '')
            asc_name = asc.get('name', '')
            parts.append(f"你的太阳星座是{sun_name}（核心自我），上升星座是{asc_name}（外在表现）。")
            sun_elem = sun.get('element', '')
            asc_elem = asc.get('element', '')
            if sun_elem and asc_elem:
                if sun_elem == asc_elem:
                    parts.append(f'太阳和上升同为{sun_elem}元素，内外一致，你活得比较「表里如一」。')
                elif {sun_elem, asc_elem} in [{'火', '风'}, {'风', '火'}]:
                    parts.append('火象+风象组合，你充满活力且善于交际，但注意不要过度发散。')
                elif {sun_elem, asc_elem} in [{'土', '水'}, {'水', '土'}]:
                    parts.append('土象+水象组合，感性中有理智，稳重中有柔情。')
                else:
                    parts.append(f'不同元素的组合让你既有{sun_elem}象的底色，又有{asc_elem}象的外显。')
        
        if moon:
            moon_name = moon.get('name', '')
            parts.append(f"月亮落在{moon_name}，意味着你的情感安全感和潜意识模式带有{moon_name}特质。")
        
        strong = [k for k, v in scores.items() if v >= 7.0]
        weak = [k for k, v in scores.items() if v < 4.5]
        if strong:
            parts.append(f"星盘能量最强领域：{'、'.join(strong)}。")
        if weak:
            parts.append(f"需要关注的方向：{'、'.join(weak)}，这些方面可能给你带来挑战。")
        
        return ' '.join(parts)

    def get_transit_reading(self, year: int, month: int, day: int,
                           hour: int = 12, minute: int = 0,
                           lng: float = 116.4, lat: float = 39.9,
                           tz_str: str = 'Asia/Shanghai') -> Dict:
        """Transit：相位优先级 + 宫位影响层"""
        if not ZODIAC_ENGINE_AVAILABLE:
            return {'summary': 'Transit 功能需要精确占星引擎支持。'}
        try:
            now = datetime.now()
            natal_subject = AstrologicalSubjectFactory.from_birth_data(
                'Natal', year, month, day, hour, minute, lng=lng, lat=lat, tz_str=tz_str
            )
            transit_subject = AstrologicalSubjectFactory.from_birth_data(
                'Transit', now.year, now.month, now.day, now.hour, now.minute, lng=lng, lat=lat, tz_str=tz_str
            )
            natal = natal_subject.model_dump()
            transit = transit_subject.model_dump()

            natal_pos, transit_pos, natal_houses = {}, {}, {}
            for p in ['sun','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto']:
                nd = natal.get(p)
                td = transit.get(p)
                if nd and isinstance(nd, dict):
                    natal_pos[p.capitalize()] = nd.get('abs_pos', 0)
                    natal_houses[p.capitalize()] = nd.get('house', '')
                if td and isinstance(td, dict):
                    transit_pos[p.capitalize()] = td.get('abs_pos', 0)

            aspects = []
            if self.aspect_engine:
                for tp, tpos in transit_pos.items():
                    for np, npos in natal_pos.items():
                        angle = self.aspect_engine._angle_diff(tpos, npos)
                        result = self.aspect_engine._detect_aspect(angle)
                        if result:
                            a_name, strength = result
                            house = natal_houses.get(np, '')
                            priority = self._transit_priority(tp, np, a_name, house)
                            aspects.append({
                                'transit_planet': tp,
                                'natal_planet': np,
                                'aspect': a_name,
                                'strength': strength,
                                'angle': round(angle, 1),
                                'house': house,
                                'priority': priority
                            })
            aspects = sorted(aspects, key=lambda x: (x['priority'], x['strength']), reverse=True)[:8]

            focus = []
            for a in aspects[:4]:
                key = (a['transit_planet'], a['natal_planet'])
                text = TRANSIT_ASPECT_IMPACTS.get(key)
                house_note = self._house_theme(a.get('house', ''))
                if text:
                    focus.append(f"{PLANET_NAMES_CN.get(a['transit_planet'], a['transit_planet'])} {a['aspect']} 本命{PLANET_NAMES_CN.get(a['natal_planet'], a['natal_planet'])}（{a['house']}）：{text} {house_note}")
                else:
                    focus.append(f"{PLANET_NAMES_CN.get(a['transit_planet'], a['transit_planet'])}正以{a['aspect']}影响本命{PLANET_NAMES_CN.get(a['natal_planet'], a['natal_planet'])}（{a['house']}）。{house_note}")

            return {
                'date': now.strftime('%Y-%m-%d %H:%M'),
                'top_aspects': aspects,
                'focus': focus,
                'priority_summary': self._summarize_transit_priorities(aspects),
                'summary': '当前过运显示：外部环境正在与你的本命结构发生实时互动，适合按重点相位和宫位做短中期判断。'
            }
        except Exception as e:
            return {'summary': f'Transit 计算失败：{e}'}

    def _transit_priority(self, tp: str, np: str, aspect: str, house: str) -> int:
        score = 0
        if tp in ('Saturn', 'Pluto', 'Uranus', 'Jupiter'):
            score += 3
        if np in ('Sun', 'Moon', 'Ascendant'):
            score += 3
        if aspect in ('conjunction', 'opposition', 'square'):
            score += 2
        elif aspect in ('trine', 'sextile'):
            score += 1
        if house in ('Tenth_House', 'Seventh_House', 'Fourth_House', 'First_House'):
            score += 2
        elif house in ('Second_House', 'Eighth_House', 'Sixth_House'):
            score += 1
        return score

    def _house_theme(self, house: str) -> str:
        themes = {
            'First_House': '主题：自我、身体、身份',
            'Second_House': '主题：金钱、价值、资源',
            'Third_House': '主题：学习、沟通、短途移动',
            'Fourth_House': '主题：家庭、根基、内在安全',
            'Fifth_House': '主题：创造、恋爱、子女、表达',
            'Sixth_House': '主题：工作、健康、日常秩序',
            'Seventh_House': '主题：关系、合作、契约',
            'Eighth_House': '主题：共享资源、转化、深层绑定',
            'Ninth_House': '主题：远方、信念、学习、扩展',
            'Tenth_House': '主题：事业、名望、社会角色',
            'Eleventh_House': '主题：社群、朋友、愿景',
            'Twelfth_House': '主题：潜意识、隐退、疗愈、收尾'
        }
        return themes.get(house, '')

    def _summarize_transit_priorities(self, aspects: List[Dict]) -> str:
        if not aspects:
            return '当前没有特别强的过运触发点，适合稳扎稳打。'
        top = aspects[0]
        return f"最优先关注的是{PLANET_NAMES_CN.get(top['transit_planet'], top['transit_planet'])}对本命{PLANET_NAMES_CN.get(top['natal_planet'], top['natal_planet'])}的{top['aspect']}，因为它同时具备强度与现实议题。"

    def get_progression_reading(self, year: int, month: int, day: int,
                               hour: int = 12, minute: int = 0,
                               lng: float = 116.4, lat: float = 39.9,
                               tz_str: str = 'Asia/Shanghai') -> Dict:
        """Progression：完整双层比对（本命 vs 推运）"""
        if not ZODIAC_ENGINE_AVAILABLE:
            return {'summary': 'Progression 功能需要精确占星引擎支持。'}
        try:
            today = date.today()
            age = max(0, today.year - year - ((today.month, today.day) < (month, day)))
            from datetime import timedelta
            progressed_date = date(year, month, day) + timedelta(days=age)
            natal_subject = AstrologicalSubjectFactory.from_birth_data(
                'Natal', year, month, day, hour, minute, lng=lng, lat=lat, tz_str=tz_str
            )
            prog_subject = AstrologicalSubjectFactory.from_birth_data(
                'Progressed', progressed_date.year, progressed_date.month, progressed_date.day,
                hour, minute, lng=lng, lat=lat, tz_str=tz_str
            )
            natal = natal_subject.model_dump()
            prog = prog_subject.model_dump()

            pairs = []
            for key in ['sun', 'moon', 'mercury', 'venus', 'mars']:
                nd = natal.get(key)
                pd = prog.get(key)
                if nd and pd and isinstance(nd, dict) and isinstance(pd, dict):
                    nat_sign = nd.get('sign', '')
                    prog_sign = pd.get('sign', '')
                    nat_house = nd.get('house', '')
                    prog_house = pd.get('house', '')
                    planet_cn = PLANET_NAMES_CN.get(key.capitalize(), key)
                    direction = self._progression_direction(nat_sign, prog_sign)
                    pairs.append({
                        'planet': planet_cn,
                        'natal_sign': nat_sign,
                        'progressed_sign': prog_sign,
                        'natal_house': nat_house,
                        'progressed_house': prog_house,
                        'direction': direction,
                        'theme': PROGRESSION_THEMES.get(key.capitalize(), '你的内在节奏正在变化。')
                    })

            return {
                'progressed_date': progressed_date.isoformat(),
                'age_reference': age,
                'pairs': pairs,
                'summary': self._summarize_progression_pairs(pairs),
                'dual_view': '本命盘是你的底盘，推运盘是你此刻正在长成的样子。'
            }
        except Exception as e:
            return {'summary': f'Progression 计算失败：{e}'}

    def _progression_direction(self, natal_sign: str, prog_sign: str) -> str:
        if natal_sign == prog_sign:
            return '稳定'
        order = ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis']
        try:
            n = order.index(natal_sign)
            p = order.index(prog_sign)
            diff = (p - n) % 12
            if diff in (1, 2, 3):
                return '顺行推进'
            if diff in (4, 5, 6):
                return '结构性变化'
            return '周期转换'
        except ValueError:
            return '变化中'

    def _summarize_progression_pairs(self, pairs: List[Dict]) -> str:
        if not pairs:
            return '推运双层比对暂未抓到明显转折点。'
        head = pairs[0]
        return f"推运主线在{head['planet']}：从本命{head['natal_sign']}走向推运{head['progressed_sign']}，{head['theme']}"

    def get_solar_return_reading(self, year: int, month: int, day: int,
                               hour: int = 12, minute: int = 0,
                               lng: float = 116.4, lat: float = 39.9,
                               tz_str: str = 'Asia/Shanghai') -> Dict:
        """Solar Return：五维评分化 + 年度文本模板"""
        if not ZODIAC_ENGINE_AVAILABLE:
            return {'summary': 'Solar Return 功能需要精确占星引擎支持。'}
        try:
            current_year = datetime.now().year
            sr_subject = AstrologicalSubjectFactory.from_birth_data(
                'SolarReturn', current_year, month, day, hour, minute,
                lng=lng, lat=lat, tz_str=tz_str
            )
            sr = sr_subject.model_dump()
            sun = sr.get('sun', {}) if isinstance(sr, dict) else {}
            moon = sr.get('moon', {}) if isinstance(sr, dict) else {}
            asc = sr.get('ascendant', {}) if isinstance(sr, dict) else {}
            venus = sr.get('venus', {}) if isinstance(sr, dict) else {}
            mars = sr.get('mars', {}) if isinstance(sr, dict) else {}

            dimensions = self._solar_return_dimensions(sun, moon, asc, venus, mars)
            return {
                'solar_return_year': current_year,
                'sun_sign': sun.get('sign', ''),
                'sun_house': sun.get('house', ''),
                'moon_sign': moon.get('sign', ''),
                'ascendant_sign': asc.get('sign', ''),
                'dimension_scores': dimensions,
                'template': self._solar_return_template(dimensions),
                'summary': f"返照太阳落在{sun.get('sign', '')} {sun.get('house', '')}，这一年核心主题围绕{self._solar_return_focus(sun, asc)}展开。"
            }
        except Exception as e:
            return {'summary': f'Solar Return 计算失败：{e}'}

    def _solar_return_dimensions(self, sun: Dict, moon: Dict, asc: Dict, venus: Dict, mars: Dict) -> Dict[str, float]:
        def score_from(obj: Dict, base: float) -> float:
            if not obj:
                return base
            house = obj.get('house', '')
            house_bonus = {
                'First_House': 1.0, 'Fourth_House': 0.8, 'Seventh_House': 0.8, 'Tenth_House': 1.0,
                'Second_House': 0.7, 'Fifth_House': 0.7, 'Sixth_House': 0.6, 'Eighth_House': 0.7,
                'Eleventh_House': 0.7
            }.get(house, 0.4)
            return min(10.0, base + house_bonus)

        scores = {
            '事业': score_from(sun, 6.5) if sun else 6.0,
            '财运': score_from(venus, 6.0) if venus else 5.8,
            '健康': score_from(mars, 5.8) if mars else 5.6,
            '婚姻': score_from(moon, 6.0) if moon else 5.7,
            '人际': score_from(asc, 6.0) if asc else 5.8,
        }
        return {k: round(v, 2) for k, v in scores.items()}

    def _solar_return_focus(self, sun: Dict, asc: Dict) -> str:
        sign = sun.get('sign', '')
        house = sun.get('house', '')
        return f'返照太阳{sign}座与{house}宫'

    def _solar_return_template(self, dims: Dict[str, float]) -> str:
        top = max(dims, key=dims.get)
        return f"年度主题最强的是{top}，其次要看其余维度是否均衡。本年建议把精力优先投向{top}，其余维度做配套支撑。"
    
    # ---------- 合盘解读 ----------
    
    def get_synastry_reading(self, data1: Dict, data2: Dict) -> Dict:
        """合盘深度解读"""
        if not ZODIAC_ENGINE_AVAILABLE:
            return {'error': 'engine not available', 'overall_score': 5.0}
        
        try:
            syn = get_synastry_scores(data1, data2)
            
            overall = syn.get('overall_score', 5.0)
            
            # 文本评分
            if overall >= 8.0:
                quality = '高度匹配'
                summary = '你们之间存在强烈的能量共振。自然的默契度很高，很多事不需要说对方就懂了。'
            elif overall >= 6.5:
                quality = '良好匹配'
                summary = '大部分领域相互支持，少量的差异反而带来互补的乐趣。'
            elif overall >= 5.0:
                quality = '中规中矩'
                summary = '有契合的地方也有需要磨合的地方。关键是双方是否愿意为对方调整。'
            elif overall >= 3.5:
                quality = '需要努力'
                summary = '核心能量有差异，需要大量的理解和包容。不是不可能，但需要更多的投入。'
            else:
                quality = '挑战型'
                summary = '能量上存在显著的张力，可能更适合保持距离。'
            
            # 获取双方太阳星座
            s1 = self._get_sun_sign(data1.get('year',1990), data1.get('month',1), data1.get('day',1))
            s2 = self._get_sun_sign(data2.get('year',1990), data2.get('month',1), data2.get('day',1))
            
            # 星座配对评语
            pair_text = self._pair_comment(s1, s2)
            
            return {
                'overall_score': overall,
                'quality': quality,
                'summary': summary,
                'pair_comment': pair_text,
                'dimension_scores': syn.get('dimension_scores', {}),
                'auspicious_count': syn.get('auspicious_count', 0),
                'tension_count': syn.get('tension_count', 0),
                'total_aspects': syn.get('total_aspects', 0),
                'sun1': s1, 'sun2': s2
            }
        except Exception as e:
            return {'error': str(e), 'overall_score': 5.0}
    
    def _get_sun_sign(self, year: int, month: int, day: int) -> str:
        """快速判断太阳星座"""
        if (month == 3 and day >= 21) or (month == 4 and day <= 19): return 'Ari'
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20): return 'Tau'
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20): return 'Gem'
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22): return 'Can'
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22): return 'Leo'
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22): return 'Vir'
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22): return 'Lib'
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21): return 'Sco'
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21): return 'Sag'
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19): return 'Cap'
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18): return 'Aqu'
        else: return 'Pis'
    
    def _pair_comment(self, s1: str, s2: str) -> str:
        """星座配对评语"""
        astro_pairs = {
            ('Ari','Ari'): '两个白羊——能量爆炸级组合。一样的冲动、一样的热情，但谁先说对不起是个问题。',
            ('Ari','Tau'): '火+土——白羊的行动力和金牛的固执是天然冲突点，但如果互相欣赏对方的优点，可以形成保护与被保护的关系。',
            ('Ari','Gem'): '火+风——风助火势，一个行动一个策划，行动力加倍。最有趣的情侣档。',
            ('Ari','Can'): '火+水——白羊的直接和巨蟹的敏感需要极高的情商来平衡。巨蟹要的不是激情，是安全感。',
            ('Ari','Leo'): '火+火——爆炸级的热情组合，两个人都干脆直接，但要注意谁说了算。',
            ('Ari','Vir'): '火+土——白羊的试试看和处女的想清楚是天然冲突，但互补时一个负责开拓一个负责完善。',
            ('Ari','Lib'): '火+风——对宫星座，互相被对方吸引又觉得对方不可理喻。天秤的犹豫和冲动的白羊形成完美互补。',
            ('Ari','Sco'): '火+水——两个固定宫的火星守护者，要么天长地久要么你死我活。激情足够但需要极强的包容力。',
            ('Ari','Sag'): '火+火——冒险伴侣，一起闯世界，但别比谁更冲动。',
            ('Ari','Cap'): '火+土——白羊的冲动vs摩羯的谨慎，一个是先做再说，一个是算清楚再做。互相学习的最佳拍档。',
            ('Ari','Aqu'): '火+风——火星撞天王星，激情+创新的奇妙组合。看似不同频但能擦出最特别的火花。',
            ('Ari','Pis'): '火+水——白羊的直率会伤到双鱼的心，但双鱼的温柔也能融化白羊的倔强。需要大量的理解。',
            ('Tau','Tau'): '两个金牛——稳到极致的组合。生活会非常有品质感，但抵抗变化的固执也会加倍。',
            ('Tau','Gem'): '土+风——金牛要稳定，双子要变化。需要找到新鲜中的熟悉感才能维持。',
            ('Tau','Can'): '土+水——一个提供安全感，一个提供温暖，传统温馨的家庭组合。',
            ('Tau','Leo'): '土+火——金牛的品位和狮子的排场是天作之合，但金牛的慢节奏可能会让狮子不耐烦。',
            ('Tau','Vir'): '土+土——稳上加稳，现实主义的双人组合，生活品质感拉满。',
            ('Tau','Lib'): '土+风——都是金星守护的星座，审美在线。金牛务实，天秤理想主义，需要在花钱这件事上达成共识。',
            ('Tau','Sco'): '土+水——对宫星座。金牛和天蝎的吸引力是磁铁级别的，但占有欲的两倍也可能让关系窒息。',
            ('Tau','Sag'): '土+火——金牛要安全感，射手要自由。这是一场关于家的定义的长期谈判。',
            ('Tau','Cap'): '土+土——志同道合的建设者，共同目标让感情更牢固。',
            ('Tau','Aqu'): '土+风——金牛的务实和水瓶的叛逆看似不搭，但水瓶的稳定性和金牛的固执可能在坚持自我这件事上共鸣。',
            ('Tau','Pis'): '土+水——现实与浪漫的结合，需要互相理解对方的节奏。',
            ('Gem','Gem'): '两个双子——聊不完的天，说不完的八卦。但可能聊完了感情也消耗完了。谁先停下来谁就输了。',
            ('Gem','Can'): '风+水——双子需要新鲜感，巨蟹需要安全感。一个爱社交一个爱居家，需要找到中间的节奏。',
            ('Gem','Leo'): '风+火——狮子的光芒和双子的幽默是聚会上最耀眼的情侣。社交能力加倍，但深度话题可能需要练习。',
            ('Gem','Vir'): '风+土——双子天马行空，处女落地执行。完美的搭档，处女负责善后，双子负责开路。',
            ('Gem','Lib'): '风+风——社交届的天花板CP，聊不完的话题，但也可能聊完了感情。',
            ('Gem','Sco'): '风+水——双子觉得天蝎太沉重，天蝎觉得双子太肤浅。但如果天蝎愿意解释深度，双子愿意学习聆听，这是一场跨越维度的爱。',
            ('Gem','Sag'): '风+火——一半冒险一半理智，互补型的最佳典范。',
            ('Gem','Cap'): '风+土——双子喜欢变化，摩羯需要稳定。双子的跳跃思维在摩羯看来是不靠谱，摩羯的严肃在双子看来是无趣。需要极强的耐心。',
            ('Gem','Aqu'): '风+风——两个聪明人的碰撞，精神层面极度契合。',
            ('Gem','Pis'): '风+水——双子的理性和双鱼的感性互相需要但也互相不理解。双子觉得双鱼太情绪化，双鱼觉得双子不够走心。',
            ('Can','Can'): '两个巨蟹——敏感加敏感等于互相共情的完美组合，但也可能一起陷入情绪漩涡。需要一个更理性的人来平衡。',
            ('Can','Leo'): '水+火——巨蟹要家的温暖，狮子要舞台的光芒。巨蟹需要成为狮子的观众，狮子需要给巨蟹安全感。',
            ('Can','Vir'): '水+土——巨蟹提供情绪价值，处女提供实际支持。水象和土象的经典搭配，互相照顾得很舒服。',
            ('Can','Lib'): '水+风——巨蟹的情感深度和天秤的社交需求需要磨合。巨蟹觉得天秤不够深入，天秤觉得巨蟹太黏人。',
            ('Can','Sco'): '水+水——灵魂级别的深度连接，情感上的双向奔赴。',
            ('Can','Sag'): '水+火——巨蟹的守护和射手的冒险是一对经典矛盾。一个想保护，一个想探索。需要边界感。',
            ('Can','Cap'): '水+土——对宫星座。经典的角色互补，一个主内一个主外。巨蟹提供情绪港湾，摩羯提供物质保障。',
            ('Can','Aqu'): '水+风——巨蟹需要情感反馈，水瓶的情感表达方式是解决问题而不是共情。需要互相学对方的语言。',
            ('Can','Pis'): '水+水——温柔与温柔的相遇。互相理解对方不为人知的柔软角落，但也要注意别一起沉溺。',
            ('Leo','Leo'): '两个狮子——光芒四射但也容易争抢主角。如果学会了轮流站C位，这是最令人羡慕的情侣。',
            ('Leo','Vir'): '火+土——狮子的大气和处女的细节可以互相成就。处女帮狮子落地，狮子帮处女勇敢。',
            ('Leo','Lib'): '火+风——王者遇到社交艺术家，一个负责霸气一个负责优雅。',
            ('Leo','Sco'): '火+水——狮子要崇拜，天蝎要忠诚。两颗骄傲的心如果不愿低头，就是宫斗。如果愿意欣赏对方，就是传奇。',
            ('Leo','Sag'): '火+火——光芒四射的情侣，彼此欣赏，彼此鼓励。',
            ('Leo','Cap'): '火+土——狮子要掌声，摩羯要成绩。两个都要赢，但赢的方向不同。需要找到一个共同的目标。',
            ('Leo','Aqu'): '火+风——对宫星座。狮子的我和水瓶的我们需要找到平衡。互相欣赏但常常互相不服。',
            ('Leo','Pis'): '火+水——狮子的强势和双鱼的柔软可以是完美的保护与被保护关系。但狮子需要注意不要太自我，双鱼也不要太放弃自我。',
            ('Vir','Vir'): '两个处女——完美主义的平方。万事安排得井井有条，但可能过度分析了感情本身。',
            ('Vir','Lib'): '土+风——处女的实际和天秤的犹豫可能在决策上互相折磨。但处女帮天秤落地，天秤帮处女放松。',
            ('Vir','Sco'): '土+水——处女的分析力和天蝎的洞察力是顶级搭档。两个人都想要深度，都不满足于表面。',
            ('Vir','Sag'): '土+火——处女的想清楚再行动和射手的先试试再说。需要找到节奏的平衡。',
            ('Vir','Cap'): '土+土——两个责任感的化身，一起构建未来的最佳搭档。',
            ('Vir','Aqu'): '土+风——处女的分析力和水瓶的创新力可以做出很酷的事情。但处女需要秩序，水瓶需要自由。',
            ('Vir','Pis'): '土+水——对宫星座。处女的理性和双鱼的感性的完美互补。处女帮双鱼落地，双鱼帮处女柔软。',
            ('Lib','Lib'): '两个天秤——优雅的平方。做决定可能要花很长时间，但在一起的日子充满了美和仪式感。',
            ('Lib','Sco'): '风+水——天秤的社交表面和天蝎的情感深处需要桥梁。天蝎觉得天秤太浅，天秤觉得天蝎太沉。但这种互补产生最深的理解。',
            ('Lib','Sag'): '风+火——自由与平衡的协奏曲。天秤帮射手做决定，射手带天秤去冒险。',
            ('Lib','Cap'): '风+土——天秤的灵活性和摩羯的稳定性。摩羯觉得天秤不够认真，天秤觉得摩羯太过严肃。如果互相欣赏，就是最好的平衡。',
            ('Lib','Aqu'): '风+风——创新+美学的碰撞，灵魂伴侣的可能性。',
            ('Lib','Pis'): '风+水——天秤的社交和双鱼的梦幻。两个不喜欢冲突的星座在一起会很和谐，但也可能都逃避真正的问题。',
            ('Sco','Sco'): '两个天蝎——灵魂伴侣级别的深度连接。要么最懂彼此，要么最折磨彼此。没有中间地带。',
            ('Sco','Sag'): '水+火——天蝎的深度和射手的广度。一个要钻进去，一个要走出去。是天敌也是最有趣的组合。',
            ('Sco','Cap'): '水+土——天蝎的洞察力和摩羯的耐力。可以一起走向任何你们选择的方向。低调但强大。',
            ('Sco','Aqu'): '水+风——固定宫对固定宫。天蝎的情感绝对和水瓶的理性绝对需要在谁说了算这件事上达成协议。',
            ('Sco','Pis'): '水+水——深层次的情感共鸣，理解彼此不为人知的角落。',
            ('Sag','Sag'): '两个射手——一起环游世界的灵魂伴侣。问题是两个人都想自由，谁来管账单？',
            ('Sag','Cap'): '火+土——射手要自由vs摩羯要成功。射手帮摩羯放松，摩羯帮射手落地。真正的高手组合。',
            ('Sag','Aqu'): '风+火——一起探索世界的旅行伴侣。精神层面和行动层面都很一致。',
            ('Sag','Pis'): '火+水——射手要冒险，双鱼要浪漫。如果一起旅行，射手负责计划路线，双鱼负责把旅程变成故事。',
            ('Cap','Cap'): '两个摩羯——最强工作情侣。一起征服世界，但要注意别把对方当成项目来管理。',
            ('Cap','Aqu'): '土+风——摩羯要传统路线，水瓶要另辟蹊径。可以成为改变世界的搭档，甘蔗不能两头甜。',
            ('Cap','Pis'): '土+水——摩羯给双鱼安全感，双鱼给摩羯温柔。看似传统的组合，其实是深刻的需要与被需要。',
            ('Aqu','Aqu'): '两个水瓶——最酷的情侣。思想碰撞不断，但可能忘记了生活本身也是关系的一部分。',
            ('Aqu','Pis'): '风+水——水瓶的理想主义和双鱼的浪漫主义。一个想改变世界，一个想治愈世界。',
            ('Pis','Pis'): '两个双鱼——最浪漫的组合。活在两个人的梦里。问题是：梦醒了怎么办？需要一个人更接地气。',
        }
        
        pair = (s1, s2)
        reverse = (s2, s1)
        
        if pair in astro_pairs:
            return astro_pairs[pair]
        if reverse in astro_pairs:
            return astro_pairs[reverse]
        
        return f'{SUN_SIGN_PERSONALITY.get(s1, {}).get("name", "")}与{SUN_SIGN_PERSONALITY.get(s2, {}).get("name", "")}的组合，有吸引力也有差异性，关键看双方是否愿意为对方调整节奏。'
    
    # ---------- 周期运势文本 ----------
    
    def get_weekly_reading(self, sun_sign: str) -> str:
        """周运文本"""
        info = SUN_SIGN_PERSONALITY.get(sun_sign, {})
        name = info.get('name', '')
        elem = info.get('element', '')
        wx = info.get('wu_xing', '土')
        
        wx_energy = {
            '火': '行动力强的一周',
            '土': '落地执行的一周',
            '风': '思维活跃的一周',
            '水': '情绪敏感的一周'
        }
        
        return f"【{name}周运】本周能量关键词：{wx_energy.get(elem, '调整适应的一周')}。{name}的五行能量是{wx}，" + {
            '火': '适合推进新项目，但要注意冲动决策。周中可能出现一个让你兴奋的机会，先核实再行动。',
            '土': '适合处理积压的工作和财务。慢就是快，本周不适合冒险。感情方面，已有的关系会变得更稳固。',
            '金': '适合社交和表达。你可能在某些场合成为焦点，利用这个机会建立有价值的连接。周五后注意收敛。',
            '水': '情绪波动的一周。注意区分"真实的问题"和"过度敏感带来的想象"。适合创作而非决策。'
        }.get(wx, '量力而行，顺势而为。')
    
    def get_monthly_reading(self, sun_sign: str, month: int) -> str:
        """月运文本"""
        info = SUN_SIGN_PERSONALITY.get(sun_sign, {})
        name = info.get('name', '')
        
        # 月度生肖对应
        zodiac_animals = ['虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪', '鼠', '牛']
        month_name = ['摩羯月', '水瓶月', '双鱼月', '白羊月', '金牛月', '双子月', 
                     '巨蟹月', '狮子月', '处女月', '天秤月', '天蝎月', '射手月']
        
        mn = month_name[month - 1]
        za = zodiac_animals[month - 1]
        
        return f"【{name}·{mn}】进入{mn}，{name}的社交能量将迎来{['调整','激活','稳定','释放','变化','收获'][month % 6]}期。本月的核心议题：{['关系边界','财务规划','自我表达','职业突破','家庭平衡','健康管理','学习成长','社交拓展','情感深度','内在修行','合作谈判','完成放下'][month - 1]}。建议：本月的能量更适合{['收','放','稳','攻','守','修'][month % 6]}而非{['放','收','攻','稳','修','守'][(month + 3) % 6]}。"
    
    def get_daily_reading(self, sun_sign: str) -> str:
        """日常文本"""
        info = SUN_SIGN_PERSONALITY.get(sun_sign, {})
        name = info.get('name', '')
        
        import random
        advices = [
            f"今天{name}可以尝试做一件平时不会做的事——打破习惯就是最好的能量更新。",
            f'今天{name}的能量关键词是「平衡」——在工作和生活之间画一条清晰的线。',
            f'今天{name}要注意说话的分寸，你的直率有时候是一把双刃剑。',
            f'今天{name}适合独处一下，给自己一个安静的空间想清楚下一步。',
            f'今天{name}的直觉很准，相信第一反应。不要过度分析已经清晰的事情。',
            f'今天{name}社交运势不错，适合约朋友聊聊，可能有意外的信息和资源。',
            f'今天{name}的财运有波动，不适合大额投资，但适合整理财务。',
            f'今天{name}适合运动或者出门走走，身体动起来，思路也会跟着清晰。'
        ]
        
        # 基于星座的固定建议
        sign_advices = {
            'Ari': "今天白羊座的行动力特别强——但先把方向想清楚再冲。",
            'Tau': "今天金牛座适合处理财务相关的事项，但不适合冲动消费。",
            'Gem': "今天双子座的社交魅力值在线——但注意不要承诺太多。",
            'Can': "今天巨蟹座的情绪出口是你的创作力——写下来或画出来。",
            'Leo': "今天狮子座适合展示自己——让更多人看到你的价值。",
            'Vir': "今天处女座适合处理细节工作——你的专注力比平时更高。",
            'Lib': "今天天秤座的审美和判断力在线——适合做决策。",
            'Sco': '今天天蝎座的洞察力特别准——注意身边人的「没说的那句话」。',
            'Sag': "今天射手座适合探索新方向——但不适合在同一个问题上钻牛角尖。",
            'Cap': '今天摩羯座适合做长远规划——你的远见今天特别清晰。',
            'Aqu': '今天水瓶座适合创新和突破——别被「惯例」限制了想象力。',
            'Pis': '今天双鱼座的共情力特别强——帮助别人之前先照顾好自己。'
        }
        
        return sign_advices.get(sun_sign, advices[hash(f"{sun_sign}{datetime.now().strftime('%Y%m%d')}") % len(advices)])
    
    # ---------- 快照接口 ----------
    
    def _get_fallback_reading(self, year: int, month: int, day: int) -> Dict:
        """kerykeion不可用时的粗略解读"""
        sun = self._get_sun_sign(year, month, day)
        info = self._interpret_sun_sign(sun)
        scores = ZODIAC_DIMENSION_SCORES.get(sun, {})
        dim = ['事业', '财运', '健康', '婚姻', '人际']
        score_dict = {d: scores.get(d, 5.5) for d in dim}
        
        profile = f"你的太阳星座是{info.get('name', '')}（推算，无精确排盘）。{info.get('personality', '')}" if info else f"你的太阳星座是{sun}。"
        
        return {
            'engine': 'zodiac_interpreter_v3.0 (fallback)',
            'scores': score_dict,
            'profile': profile,
            'sun_sign': {'sign': sun, **info} if info else {'sign': sun},
            'note': '精度受限，安装kerykeion以获得完整排盘'
        }
    
    def get_for_cross(self, birth_data: Dict) -> Dict:
        """六合交叉验证接口"""
        reading = self.get_natal_reading(**birth_data)
        scores = reading.get('scores', {})
        avg = sum(scores.values()) / len(scores) if scores else 5.0
        
        return {
            'overall_score': round(avg, 2),
            'dimension_scores': scores,
            'profile': reading.get('profile', ''),
            'sun_sign': reading.get('sun_sign', {}).get('sign', ''),
            'element': reading.get('sun_sign', {}).get('element', ''),
            'wu_xing': reading.get('sun_sign', {}).get('wu_xing', '')
        }


# ============================================================
# 四、顶层API
# ============================================================

def get_zodiac_reading(year: int, month: int, day: int,
                       hour: int = 12, minute: int = 0,
                       lng: float = 116.4, lat: float = 39.9,
                       tz_str: str = 'Asia/Shanghai') -> Dict:
    """顶层解读API"""
    interpreter = ZodiacInterpreter()
    return interpreter.get_natal_reading(year, month, day, hour, minute, lng, lat, tz_str)


def get_sun_sign_daily(name: str, sign: str) -> str:
    """获取日常（纯文本，适合推送）"""
    interpreter = ZodiacInterpreter()
    return f"🐢 {name}今日星座({sign})\n━━━━━━━━━━\n{interpreter.get_daily_reading(sign)}"


def get_pair_reading(data1: Dict, data2: Dict) -> Dict:
    """合盘解读API"""
    interpreter = ZodiacInterpreter()
    return interpreter.get_synastry_reading(data1, data2)


# ============================================================
# 测试
# ============================================================

if __name__ == '__main__':
    print("=== 星座深度解读引擎 v3.0 — 测试 ===\n")
    
    interpreter = ZodiacInterpreter()
    
    # 丘总
    print("--- 丘总 (1990-11-10 10:00, 广东阳山) ---")
    reading = get_zodiac_reading(
        year=1990, month=11, day=10,
        hour=10, minute=0,
        lng=113.0, lat=24.5,
        tz_str='Asia/Shanghai'
    )
    
    print(f"太阳星座: {reading.get('sun_sign', {}).get('sign', '?')} {reading.get('sun_sign', {}).get('name', '')}")
    print(f"月亮星座: {reading.get('moon_sign', {}).get('sign', '?')} {reading.get('moon_sign', {}).get('name', '')}")
    print(f"上升星座: {reading.get('ascendant', {}).get('sign', '?')} {reading.get('ascendant', {}).get('name', '')}")
    print(f"\n人格画像:\n{reading.get('profile', '')}")
    print(f"\n评分:")
    for dim, score in reading.get('scores', {}).items():
        print(f"  {dim}: {score}/10 ({reading.get('dimension_readings', {}).get(dim, '')})")
    print(f"\n相位解读:")
    for a in reading.get('aspect_readings', []):
        print(f"  · {a}")
    
    if reading.get('planet_readings'):
        print(f"\n行星:")
        for p in reading['planet_readings'][:5]:
            retro = ' (R)' if p['retrograde'] else ''
            print(f"  {p['planet_cn']}在{p['sign']}第{p['house']}宫{retro}")
    
    print(f"\n--- 日常预览 ---")
    print(interpreter.get_daily_reading('Cap'))
    print(f"\n{interpreter.get_weekly_reading('Tau')}")
    
    print(f"\n\n✅ 星座解读引擎 v3.0 测试完毕")
