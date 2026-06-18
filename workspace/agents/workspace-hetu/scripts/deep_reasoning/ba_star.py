#!/usr/bin/env python3
"""
八星数字能量引擎 v2.0 — 河图 CMO

基于八极灵数(c1319.com) / 乾坤国学院 / 乔一数能 实战最佳实践。

v1.0→v2.0 进化：
  a) 三连/四连组合精编解读库（不再靠双连拼，逐条手写实战语义）
  b) 0/5处理增强（5种0/5场景：段落头、段落尾、夹心、长串、显隐共振）
  c) 全号段分析（对11位手机号的前3位号段也拆解，标记但不混入主能量区）
  d) 强凶/强吉的"化解建议"输出
  e) 评分公式重写：更贴近八星实战判断

Usage:
    from ba_star import BaStarEngine
    engine = BaStarEngine()
    result = engine.analyze_number("13912345678")
    print(result["summary"])
    scores = engine.get_scores_for_cross("13912345678")
"""

# ═══════════════════════════════════════════
# 一、八星核心数据
# ═══════════════════════════════════════════

# 格式: "数组": ("星名", 能量等级, "吉凶", "五行")
# 等级: 1=最强, 4=最弱
EIGHT_STARS_DATA = {
    # --- 四吉星 ---
    "13": ("天医", 1, "吉", "土"),
    "31": ("天医", 1, "吉", "土"),
    "68": ("天医", 2, "吉", "土"),
    "86": ("天医", 2, "吉", "土"),
    "49": ("天医", 3, "吉", "土"),
    "94": ("天医", 3, "吉", "土"),
    "27": ("天医", 4, "吉", "土"),
    "72": ("天医", 4, "吉", "土"),
    "19": ("延年", 1, "吉", "金"),
    "91": ("延年", 1, "吉", "金"),
    "78": ("延年", 2, "吉", "金"),
    "87": ("延年", 2, "吉", "金"),
    "34": ("延年", 3, "吉", "金"),
    "43": ("延年", 3, "吉", "金"),
    "26": ("延年", 4, "吉", "金"),
    "62": ("延年", 4, "吉", "金"),
    "14": ("生气", 1, "吉", "木"),
    "41": ("生气", 1, "吉", "木"),
    "67": ("生气", 2, "吉", "木"),
    "76": ("生气", 2, "吉", "木"),
    "93": ("生气", 3, "吉", "木"),
    "39": ("生气", 3, "吉", "木"),
    "82": ("生气", 4, "吉", "木"),
    "28": ("生气", 4, "吉", "木"),
    # 伏位（平）
    "11": ("伏位", 1, "平", "木"),
    "22": ("伏位", 1, "平", "木"),
    "88": ("伏位", 2, "平", "木"),
    "99": ("伏位", 2, "平", "木"),
    "77": ("伏位", 3, "平", "木"),
    "66": ("伏位", 3, "平", "木"),
    "44": ("伏位", 4, "平", "木"),
    "33": ("伏位", 4, "平", "木"),
    # --- 四凶星 ---
    "12": ("绝命", 1, "凶", "金"),
    "21": ("绝命", 1, "凶", "金"),
    "69": ("绝命", 2, "凶", "金"),
    "96": ("绝命", 2, "凶", "金"),
    "84": ("绝命", 3, "凶", "金"),
    "48": ("绝命", 3, "凶", "金"),
    "73": ("绝命", 4, "凶", "金"),
    "37": ("绝命", 4, "凶", "金"),
    "18": ("五鬼", 1, "凶", "火"),
    "81": ("五鬼", 1, "凶", "火"),
    "97": ("五鬼", 2, "凶", "火"),
    "79": ("五鬼", 2, "凶", "火"),
    "36": ("五鬼", 3, "凶", "火"),
    "63": ("五鬼", 3, "凶", "火"),
    "42": ("五鬼", 4, "凶", "火"),
    "24": ("五鬼", 4, "凶", "火"),
    "16": ("六煞", 1, "凶", "水"),
    "61": ("六煞", 1, "凶", "水"),
    "74": ("六煞", 2, "凶", "水"),
    "47": ("六煞", 2, "凶", "水"),
    "38": ("六煞", 3, "凶", "水"),
    "83": ("六煞", 3, "凶", "水"),
    "29": ("六煞", 4, "凶", "水"),
    "92": ("六煞", 4, "凶", "水"),
    "17": ("祸害", 1, "凶", "土"),
    "71": ("祸害", 1, "凶", "土"),
    "89": ("祸害", 2, "凶", "土"),
    "98": ("祸害", 2, "凶", "土"),
    "64": ("祸害", 3, "凶", "土"),
    "46": ("祸害", 3, "凶", "土"),
    "23": ("祸害", 4, "凶", "土"),
    "32": ("祸害", 4, "凶", "土"),
}

assert len(EIGHT_STARS_DATA) == 64, f"八星应有64数组, 实际{len(EIGHT_STARS_DATA)}"

# ── 五行生克 ──
WU_XING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WU_XING_KE   = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# ── 五行反向生/克（快速查找用） ──
WU_XING_SHENG_R = {v: k for k, v in WU_XING_SHENG.items()}
WU_XING_KE_R   = {v: k for k, v in WU_XING_KE.items()}

# ── 八星吉凶制化权重（基于乾坤国学院/立明堂实战经验） ──
# 凶星被吉星的克制关系（吉星可以化解凶星）
# 格式: (凶星五行, 吉星五行): 化解力度(0-1)
RESOLVE_WEIGHTS = {
    # 凶星金（绝命）→ 被吉星火克制（五鬼是火但五鬼本身是凶星，所以看吉星的火）
    # 实战中天医(土)、延年(金)、生气(木)都可以不同方式化解
    # 天医土：土生金→养绝命（不利），但土泄火（克制五鬼）
    # 延年金：金与金同气→助长绝命（不利）
    # 生气木：木生火→火克金→隔化解绝命
    # 核心原则（乾坤国学院教材）：
    #   1个天医 = 化解1个绝命 (土生金→让绝命的冲动有财可依)
    #   生气+延年 = 化解祸害
    #   五鬼（凶）需要天医+生气来化解
    "吉克凶": {
        ("土", "火"): 0.8,  # 天医土被火生→但愤怒之火克绝命金→隔山打牛
        ("金", "火"): 0.6,  # 延年金被火克→理论上克制绝命
        ("木", "火"): 0.3,  # 生气木引火→隔一层
        ("金", "土"): 0.2,  # 绝命金被天医土生→反而助长
        ("水", "土"): 0.7,  # 六煞水被天医土克→有效化解
        ("土", "木"): 0.5,  # 祸害土被生气木克→口舌被贵人化解
        ("火", "金"): 0.2,  # 五鬼火被延年金耗→弱化解
        ("火", "水"): 0.1,  # 五鬼火被六煞水克→但六煞本身凶，效果有限
    },
    # 凶星之间的加持关系（凶+凶更凶）
    "凶助凶": {
        ("金", "金"): 1.5,  # 绝命+延年（虽然延年是吉星，但同金气会引发绝命更强）
        ("火", "火"): 1.5,  # 双五鬼
        ("火", "金"): 1.3,  # 五鬼火烧绝命金→绝命变本加厉
        ("金", "火"): 1.3,  # 绝命金生五鬼火→冲动催生变数
        ("土", "土"): 1.2,  # 双祸害
        ("水", "水"): 1.2,  # 双六煞
        ("土", "金"): 1.1,  # 祸害土生绝命金→是非助长冲动
        ("金", "土"): 1.1,  # 绝命金被祸害土生→冲动被是非喂养
        ("火", "木"): 0.8,  # 五鬼火泄生气木→贵人被烧
        ("金", "木"): 0.7,  # 绝命金克生气木→贵人被冲动影响
        ("土", "水"): 1.0,  # 祸害土克六煞水→克制但消耗
    },
}

# ── 每条pair的能量流动方向判断 ──
# 相邻pair之间：前星能量流向判断
# 返回: "流通顺畅" / "流通受阻" / "耗散" / "助长" / "被泄" / "中继"
def get_flow_type(star_prev: str, star_next: str) -> str:
    """判断两颗星之间的能量流动类型"""
    if star_prev == star_next:
        return "中继"  # 同星=能量延续
    if star_prev == "伏位":
        return "中继"  # 伏位之后=能量延续
    if star_next == "伏位":
        return "蓄力"  # 到伏位=能量沉淀
    
    prev_attr = STAR_ATTRIBUTES.get(star_prev)
    next_attr = STAR_ATTRIBUTES.get(star_next)
    if not prev_attr or not next_attr:
        return "不明"
    
    px = prev_attr.get("wu_xing", "")
    nx = next_attr.get("wu_xing", "")
    if not px or not nx:
        return "不明"
    
    # 生克关系
    if WU_XING_SHENG.get(px) == nx:
        # 前生后 = 能量正向流动（前为后提供能量）
        pc = prev_attr.get("category", "")
        nc = next_attr.get("category", "")
        if pc == "吉" and nc == "吉":
            return "吉生吉·畅通"
        elif pc == "吉" and nc == "凶":
            return "吉养凶·被吸"  # 吉星养凶星，最差
        elif pc == "凶" and nc == "吉":
            return "凶生吉·转化"  # 凶生吉，好
        elif pc == "凶" and nc == "凶":
            return "凶生凶·加剧"  # 凶生凶，双凶
        return "相生"
    
    if WU_XING_KE.get(px) == nx:
        # 前克后 = 前压制后
        pc = prev_attr.get("category", "")
        nc = next_attr.get("category", "")
        if pc == "吉" and nc == "吉":
            return "吉克吉·内耗"  # 吉克吉，不好
        elif pc == "吉" and nc == "凶":
            return "吉制凶·化解"  # 吉星克制凶星，最好
        elif pc == "凶" and nc == "吉":
            return "凶克吉·压制"  # 凶星压制吉星，很差
        elif pc == "凶" and nc == "凶":
            return "凶克凶·制衡"  # 凶克凶，内部消耗
        return "相克"
    
    if WU_XING_SHENG.get(nx) == px:
        # 后生前 = 后滋养前（反向流动）
        return "反哺"
    
    if WU_XING_KE.get(nx) == px:
        # 后克前 = 后压制前（反向压制）
        return "反克"
    
    return "同气"


# ── 全号码能量流通检测 ──
def check_energy_flow(segments: list) -> dict:
    """检测整条号码的能量流通顺畅度"""
    stars = [s["star"] for s in segments if s["star"]]
    if len(stars) < 2:
        return {"flow_quality": "无法判断", "flow_score": 0}
    
    flows = []
    for i in range(len(stars) - 1):
        ft = get_flow_type(stars[i], stars[i+1])
        flows.append({"from": stars[i], "to": stars[i+1], "flow": ft, "position": i})
    
    # 统计流通质量
    good_flows = sum(1 for f in flows if f["flow"] in ("吉生吉·畅通", "凶生吉·转化", "吉制凶·化解", "中继", "蓄力", "凶克凶·制衡"))
    bad_flows = sum(1 for f in flows if f["flow"] in ("吉养凶·被吸", "凶克吉·压制", "吉克吉·内耗", "凶生凶·加剧"))
    total = len(flows)
    
    if total == 0:
        return {"flow_quality": "无法判断", "flow_score": 0}
    
    flow_ratio = (good_flows - bad_flows) / total
    
    # 查找阻塞点
    blockages = [f for f in flows if f["flow"] in ("吉养凶·被吸", "凶克吉·压制", "凶生凶·加剧")]
    
    if flow_ratio >= 0.6:
        quality = "流通顺畅"
        score = 80 + int(flow_ratio * 20)
    elif flow_ratio >= 0.2:
        quality = "基本通畅"
        score = 55 + int(flow_ratio * 30)
    elif flow_ratio >= -0.2:
        quality = "流通受阻"
        score = 35 + int((flow_ratio + 0.2) * 50)
    else:
        quality = "严重阻塞"
        score = max(0, 25 + int(flow_ratio * 30))
    
    return {
        "flow_quality": quality,
        "flow_score": score,
        "flow_count": total,
        "good_flow_count": good_flows,
        "bad_flow_count": bad_flows,
        "all_flows": flows,
        "blockages": blockages,
    }

# 每颗星的属性
STAR_ATTRIBUTES = {
    "天医": {
        "category": "吉", "wu_xing": "土",
        "keywords": ["财富", "婚姻", "业绩", "健康"],
        "tags": ["正财", "正姻缘", "贵人", "治愈"],
        "persona": "善良单纯、善解人意、温柔多情、易被骗",
        "career": "医疗、金融、慈善、教育、美容",
        "health": "血压、血液、心脏（尤其低能量时）",
        "finance": "正财运好，但投资需谨慎，易被套牢",
    },
    "延年": {
        "category": "吉", "wu_xing": "金",
        "keywords": ["事业", "领导力", "能力", "压力"],
        "tags": ["大男子/女子主义", "专业能力", "管理者"],
        "persona": "能力强、有主见、大男子/女子主义、劳碌命",
        "career": "管理、自主创业、技术专家、军政",
        "health": "颈椎、腰椎、心脏压力（过强则劳损）",
        "finance": "能力带财，但劳碌所得，非横财",
    },
    "生气": {
        "category": "吉", "wu_xing": "木",
        "keywords": ["贵人", "人脉", "快乐", "随缘"],
        "tags": ["乐天派", "好人缘", "玩乐", "偏财"],
        "persona": "乐观开朗、随缘不争、乐善好施、花钱大方",
        "career": "公关、销售、中介、娱乐、旅游",
        "health": "肠胃消化问题",
        "finance": "偏财运好，意外之财，但无理财观念",
    },
    "伏位": {
        "category": "平", "wu_xing": "木",
        "keywords": ["保守", "等待", "延续", "积累"],
        "tags": ["被动", "忍耐", "固执", "等待时机"],
        "persona": "保守固执、谨慎细心、被动等待、内心矛盾",
        "career": "研究、分析、文职、等待型事业",
        "health": "心脏、脑部、血稠、隐性疾病",
        "finance": "稳定保守，靠积累，不宜投机",
    },
    "绝命": {
        "category": "凶", "wu_xing": "金",
        "keywords": ["破财", "冲动", "官司", "意外"],
        "tags": ["极致", "偏激", "冒险", "拼搏"],
        "persona": "敢于拼搏、极端性格、冲动易怒、不认输",
        "career": "投资、搏命行业、高风险创业",
        "health": "肝胆、肾、泌尿、突发性疾病",
        "finance": "财来财去，破财风险高",
    },
    "五鬼": {
        "category": "凶", "wu_xing": "火",
        "keywords": ["变动", "智慧", "偏门", "灵异"],
        "tags": ["聪明", "不稳定", "熬夜", "思维敏捷", "脑力"],
        "persona": "聪明伶俐、思维活跃、变化多端、不稳定",
        "career": "策划、设计、IT、宗教、口才",
        "health": "心脏、血光、失眠、熬夜、精神问题",
        "finance": "偏财运，但来去快，易破财",
    },
    "六煞": {
        "category": "凶", "wu_xing": "水",
        "keywords": ["桃花", "人际关系", "服务业", "口舌"],
        "tags": ["多情", "敏感", "纠结", "服务"],
        "persona": "敏感多情、心思细腻、优柔寡断、重感情",
        "career": "服务业、美容、酒店、公务员、中介",
        "health": "内分泌、乳腺、妇科、精神焦虑",
        "finance": "靠人际关系赚钱，波动大",
    },
    "祸害": {
        "category": "凶", "wu_xing": "土",
        "keywords": ["口舌", "是非", "欺骗", "官非"],
        "tags": ["嘴巴快", "刻薄", "是非多", "易被骗"],
        "persona": "口才好但刻薄、是非多、易被骗、易惹官司",
        "career": "销售、律师、歌手、主持、餐饮",
        "health": "咽喉、肺部、气管、免疫系统",
        "finance": "财难积聚，靠口赚钱也因口破财",
    },
}


# ═══════════════════════════════════════════
# 二、组合解读库（v2.0 精编版）
# ═══════════════════════════════════════════

# 2.1 双连组合（两相邻Pair之间的星）
DOUBLE_READINGS = {
    ("天医", "天医"): "双重财富，财运旺盛，但过强需防贪婪",
    ("天医", "延年"): "财富+事业，能力赚钱，富贵双全",
    ("天医", "生气"): "财富+贵人，贵人带财。最佳组合之一",
    ("天医", "伏位"): "财富在积累中，持续稳定收入",
    ("天医", "绝命"): "先赚后破。天医赚钱→绝命花，投资预警",
    ("天医", "五鬼"): "财富来源变动大，偏门赚钱，是非之财",
    ("天医", "六煞"): "通过人际关系/服务业赚钱",
    ("天医", "祸害"): "靠口才赚钱但也因口舌破财",
    ("延年", "天医"): "专业能力变现，事业带来财富",
    ("延年", "延年"): "事业心极强。双重压力，需注意健康透支",
    ("延年", "生气"): "贵人有助事业，人脉变商业",
    ("延年", "伏位"): "事业处于等待期，蓄势待发",
    ("延年", "绝命"): "事业型但冲动决策，风险极高",
    ("延年", "五鬼"): "智慧型事业，想法多变，脑力工作者",
    ("延年", "六煞"): "服务行业有成就",
    ("延年", "祸害"): "靠口才在职场发展，易有是非",
    ("生气", "天医"): "人脉变现，贵人带财。最佳组合之一",
    ("生气", "延年"): "人脉转化为事业，顺遂",
    ("生气", "生气"): "双重贵人，人缘极好，但缺赚钱动力",
    ("生气", "伏位"): "贵人待机，人脉靠谱但需时间培养",
    ("生气", "绝命"): "朋友带投资机会，风险不可控",
    ("生气", "五鬼"): "朋友介绍偏门生意，贵人+智慧组合",
    ("生气", "六煞"): "通过人际服务获利",
    ("生气", "祸害"): "口才好但朋友中有小人",
    ("伏位", "天医"): "等待后迎来财运",
    ("伏位", "延年"): "韬光养晦后事业起飞",
    ("伏位", "生气"): "慢热型的人际积累，贵人需要时间",
    ("伏位", "绝命"): "忍耐后的爆发，容易走极端",
    ("伏位", "五鬼"): "沉默中的变化，暗流涌动",
    ("伏位", "六煞"): "被动的人际困扰，情感压抑",
    ("伏位", "祸害"): "隐忍的口舌是非，背后闲话",
    ("绝命", "天医"): "破财后有补救，先难后易，但不可放松警惕",
    ("绝命", "延年"): "冒险事业，高风险高回报，赌徒命",
    ("绝命", "生气"): "破财后有贵人相助，朋友救场",
    ("绝命", "伏位"): "冲动后冷静，但隐患仍在",
    ("绝命", "绝命"): "双重破财，能量极凶。需极度警惕",
    ("绝命", "五鬼"): "极度不稳定，投资暴雷风险极高",
    ("绝命", "六煞"): "为情破财，桃花劫",
    ("绝命", "祸害"): "破财+是非，官司风险极高",
    ("五鬼", "天医"): "偏门变正财。转型成功，脑力赚钱",
    ("五鬼", "延年"): "智慧变事业，脑力工作者变管理者",
    ("五鬼", "生气"): "聪明人灵活交际，脑力+人脉",
    ("五鬼", "伏位"): "想法隐藏中，暗地里计划",
    ("五鬼", "绝命"): "想法+冲动=风险暴增。最危险的组合之一",
    ("五鬼", "五鬼"): "双重变动，极度不稳定。熬夜/失眠体质",
    ("五鬼", "六煞"): "因感情产生变动，心思不定",
    ("五鬼", "祸害"): "聪明反被聪明误，祸从口出",
    ("六煞", "天医"): "服务业/人际关系赚钱",
    ("六煞", "延年"): "服务业中成为管理者",
    ("六煞", "生气"): "人际关系好，左右逢源",
    ("六煞", "伏位"): "感情压抑，人际关系停滞",
    ("六煞", "绝命"): "感情破财，桃花劫",
    ("六煞", "五鬼"): "为情困扰，心神不宁",
    ("六煞", "六煞"): "多重感情纠葛，极度纠结",
    ("六煞", "祸害"): "感情口舌是非多",
    ("祸害", "天医"): "口才赚钱，业绩优秀",
    ("祸害", "延年"): "靠专业口才成为意见领袖",
    ("祸害", "生气"): "嘴巴甜、人缘好",
    ("祸害", "伏位"): "忍气吞声，心里委屈",
    ("祸害", "绝命"): "言辞激烈易惹官司",
    ("祸害", "五鬼"): "口舌+变动，祸从口出",
    ("祸害", "六煞"): "因感情产生是非，桃花口舌",
    ("祸害", "祸害"): "双倍是非。嘴欠惹祸，谨言慎行",
}

# 2.2 三连组合精编解读库（★ v2.0 核心进化）
# 格式: (星A, 星B, 星C): (吉凶预判, 解读正文)
# 精编120+条，覆盖实战高频+高危序列
TRIPLE_READINGS = {
    # ── 🏆 三吉串联（大好格局） ──
    ("天医", "天医", "天医"): ("吉", "三重天医，极旺财。但过强需防贪心招祸、钱多人盯"),
    ("天医", "天医", "延年"): ("吉", "强财+强事业。最典型的大老板能量"),
    ("天医", "天医", "生气"): ("吉", "强财+强贵人。人旺财旺"),
    ("天医", "天医", "伏位"): ("吉", "财富积累中，持续稳健"),
    ("天医", "延年", "天医"): ("吉", "能力变现→财富→再变现。事业良性循环"),
    ("天医", "延年", "生气"): ("吉", "财富+事业+贵人，三通格局，大吉"),
    ("天医", "延年", "延年"): ("吉", "财富+强事业心，富贵双全但需注意身心"),
    ("天医", "生气", "天医"): ("吉", "贵人带财→再带财，人际良性循环"),
    ("天医", "生气", "延年"): ("吉", "贵人引财→事业起飞，顺风顺水的富贵格局"),
    ("天医", "生气", "生气"): ("吉", "财富+双重人脉，社交幸福感强"),
    ("天医", "伏位", "天医"): ("吉", "财富积累→沉淀→再爆发"),
    ("天医", "伏位", "延年"): ("吉", "财富沉淀后再发力，厚积薄发"),
    ("天医", "伏位", "生气"): ("吉", "财富→等待→贵人，节奏稳健"),
    ("延年", "天医", "延年"): ("吉", "能力→财富→再提升，事业螺旋上升"),
    ("延年", "天医", "生气"): ("吉", "事业+财富+贵人，三吉串联，大吉"),
    ("延年", "延年", "天医"): ("吉", "强事业→财富，能力型富翁"),
    ("延年", "延年", "生气"): ("吉", "事业+事业+贵人，职场人气王"),
    ("延年", "延年", "延年"): ("凶", "三重延年，事业压力极大。易劳损/过劳"),
    ("延年", "生气", "天医"): ("吉", "事业+贵人+财富，通顺无比"),
    ("延年", "生气", "生气"): ("吉", "事业+双贵人，人脉助力事业"),
    ("延年", "伏位", "天医"): ("吉", "事业沉淀→财富，厚积薄发"),
    ("生气", "天医", "延年"): ("吉", "人脉→财富→事业，完美三通"),
    ("生气", "天医", "生气"): ("吉", "人脉变财→再变人脉，良性社交循环"),
    ("生气", "延年", "天医"): ("吉", "贵助事业→赚钱，格局极佳"),
    ("生气", "延年", "生气"): ("吉", "人脉+事业+人脉，左右逢源"),
    ("生气", "生气", "天医"): ("吉", "双重贵人带财，人脉价值变现"),
    ("生气", "生气", "延年"): ("吉", "双贵人助力事业，顺风顺水"),
    ("生气", "生气", "生气"): ("平", "三重贵人，人缘极好但缺乏赚钱驱动力"),
    ("生气", "伏位", "天医"): ("吉", "贵人→等待→财富，循序渐进"),
    ("伏位", "天医", "延年"): ("吉", "等待→财富→事业，厚积薄发"),
    ("伏位", "天医", "生气"): ("吉", "等待后财富与贵人齐来"),
    ("伏位", "延年", "天医"): ("吉", "蛰伏→事业→财富，完美翻盘"),
    ("伏位", "生气", "天医"): ("吉", "等待→贵人→财富，循序渐进"),

    # ── ⚠️ 吉凶混合（需要解读） ──
    ("天医", "绝命", "天医"): ("凶", "赚→破→赚。循环破财，需设资金防火墙"),
    ("天医", "绝命", "延年"): ("凶", "赚钱→冲动→事业受创，需冷静决策"),
    ("天医", "绝命", "五鬼"): ("凶", "赚钱→冲动→血本无归。高危投资序列"),
    ("天医", "绝命", "六煞"): ("凶", "赚钱→冲动破财→情色破财，三重预警"),
    ("天医", "绝命", "祸害"): ("凶", "赚钱→冲动→官司。经典破财组合"),
    ("天医", "绝命", "生气"): ("凶", "赚钱→破财→贵人救。可救但代价大"),
    ("天医", "绝命", "伏位"): ("平", "赚钱→破财→冷静。需重新规划"),
    ("天医", "五鬼", "天医"): ("平", "正财→偏财→正财，财路变动"),
    ("天医", "五鬼", "绝命"): ("凶", "正财变偏财→冲动破财。极易暴雷"),
    ("天医", "五鬼", "祸害"): ("凶", "赚钱→偏门→口舌官司。灰色地带风险"),
    ("天医", "六煞", "祸害"): ("凶", "服务业赚钱→情感纠葛→口舌是非"),
    ("天医", "六煞", "天医"): ("平", "通过人际赚钱→情感牵绊→再赚钱"),
    ("天医", "祸害", "天医"): ("吉", "靠嘴赚钱→再赚钱，口才变财"),
    ("天医", "祸害", "绝命"): ("凶", "口才赚钱→是非→破财，嘴财守不住"),
    ("天医", "祸害", "祸害"): ("凶", "赚钱→双口舌是非，赚多少赔多少"),
    ("延年", "天医", "绝命"): ("凶", "事业佼佼→赚钱→冲动失败。大运转坏预警"),
    ("延年", "绝命", "天医"): ("凶", "能力→冲动→弥补。走弯路"),
    ("延年", "绝命", "五鬼"): ("凶", "能力超强但走偏门，灰色地带"),
    ("延年", "绝命", "祸害"): ("凶", "事业型→冲动→官司。权力斗争"),
    ("延年", "五鬼", "天医"): ("平", "智慧→偏财→正财，职业转型期"),
    ("延年", "五鬼", "绝命"): ("凶", "事业用脑→偏门→暴雷。聪明反被误"),
    ("延年", "五鬼", "祸害"): ("凶", "事业变动→口舌官司。职场高危"),
    ("延年", "六煞", "五鬼"): ("凶", "服务业管理→感情困扰→心神不宁"),
    ("延年", "祸害", "天医"): ("平", "靠专业口才→赚钱，需防是非"),
    ("延年", "祸害", "绝命"): ("凶", "专业+口才→冲动官司。易得罪人"),
    ("生气", "绝命", "天医"): ("凶", "朋友→投资冲动→回本。惊险"),
    ("生气", "绝命", "五鬼"): ("凶", "朋友带门路→投资暴雷。交友不慎"),
    ("生气", "五鬼", "天医"): ("平", "朋友→偏门→赚钱。灰色路线"),
    ("生气", "五鬼", "绝命"): ("凶", "朋友引偏门→冲动暴雷。极度危险"),
    ("生气", "五鬼", "祸害"): ("凶", "朋友引偏门→聪明反误→是非"),
    ("生气", "六煞", "五鬼"): ("凶", "人际→桃花→心神不宁"),
    ("生气", "祸害", "天医"): ("平", "朋友有口才→赚钱，但需防小人在侧"),
    ("伏位", "绝命", "天医"): ("凶", "长期压抑→冲动破财→弥补。惊心"),
    ("伏位", "绝命", "五鬼"): ("凶", "沉默→爆发→偏执。情绪风险极大"),
    ("伏位", "五鬼", "绝命"): ("凶", "暗流→偏执→破财。连环凶"),
    ("伏位", "祸害", "绝命"): ("凶", "隐忍→爆发→官司。情绪管理差"),
    ("伏位", "祸害", "祸害"): ("凶", "隐忍→双是非。忍越久爆越大"),

    # ── 🔴 全凶串联（高危预警） ──
    ("绝命", "绝命", "绝命"): ("凶", "三重绝命，能量极凶。官司+破财+意外。强烈预警"),
    ("绝命", "绝命", "五鬼"): ("凶", "冲动+冲动+偏执。暴雷概率极高"),
    ("绝命", "绝命", "六煞"): ("凶", "冲动破财+感情纠葛，双杀"),
    ("绝命", "绝命", "祸害"): ("凶", "双冲动+是非。官司一触即发"),
    ("绝命", "五鬼", "绝命"): ("凶", "冲动→偏执→再冲动。魔鬼三角"),
    ("绝命", "五鬼", "五鬼"): ("凶", "冲动→双重变动。人生大动荡"),
    ("绝命", "五鬼", "祸害"): ("凶", "冲动→聪明沉沦→口舌官司。极度凶险"),
    ("绝命", "六煞", "绝命"): ("凶", "冲动→情伤→再冲动。恶性循环"),
    ("绝命", "六煞", "祸害"): ("凶", "破财→情伤→是非。三角危机"),
    ("绝命", "祸害", "绝命"): ("凶", "冲动→口舌→再冲动。官司连环"),
    ("绝命", "祸害", "五鬼"): ("凶", "冲动→是非→偏执。连环锁"),
    ("绝命", "祸害", "祸害"): ("凶", "冲动→双是非。嘴祸遇冲动"),
    ("五鬼", "五鬼", "五鬼"): ("凶", "三重变动，极度不稳定。健康堪忧（熬夜/失眠/心悸）"),
    ("五鬼", "五鬼", "绝命"): ("凶", "双变+冲动。人生暴风雨"),
    ("五鬼", "五鬼", "祸害"): ("凶", "双变+口舌。变动中惹是非"),
    ("五鬼", "五鬼", "六煞"): ("凶", "双变+情伤。感情生活动荡"),
    ("五鬼", "绝命", "祸害"): ("凶", "偏执+冲动+是非。经典三凶"),
    ("五鬼", "绝命", "绝命"): ("凶", "智慧+双冲动。聪明冲动更致命"),
    ("五鬼", "绝命", "六煞"): ("凶", "聪明→冲动→情伤。三重打击"),
    ("五鬼", "六煞", "祸害"): ("凶", "变动→情伤→口舌。一团乱"),
    ("五鬼", "祸害", "绝命"): ("凶", "变+是非+冲动。祸从口出"),
    ("六煞", "六煞", "绝命"): ("凶", "多重纠葛→为情破财"),
    ("六煞", "六煞", "五鬼"): ("凶", "双感情纠葛→心神不宁"),
    ("六煞", "五鬼", "祸害"): ("凶", "情感困惑→心神不宁→口舌是非"),

    # ── 🟡 伏位中继/过渡 ──
    ("伏位", "伏位", "绝命"): ("凶", "长期压抑→爆发式冲动。情绪风险"),
    ("伏位", "伏位", "五鬼"): ("凶", "沉默太久→暗流涌动"),
    ("伏位", "伏位", "祸害"): ("凶", "忍气吞声→最终爆发"),
    ("伏位", "伏位", "天医"): ("吉", "长期等待→财富来临"),
    ("伏位", "伏位", "延年"): ("吉", "多年沉淀→事业起飞"),
    ("伏位", "伏位", "天医"): ("吉", "厚积→薄发"),

    # ── 🔥 特殊组合（行业判断） ──
    ("绝命", "五鬼", "天医"): ("平", "高风险→偏门→回本。创业者/投资人常见"),
    ("绝命", "天医", "绝命"): ("凶", "破→赚→再破。循环破财人格"),
    ("天医", "绝命", "六煞"): ("凶", "赚钱→冲动→情色破财。三重预警"),
    ("祸害", "绝命", "五鬼"): ("凶", "口头官司+法律纠纷+阴谋诡计。三角雷"),
    ("祸害", "祸害", "祸害"): ("凶", "三重祸害，口舌是非不断。谨言慎行"),
    ("六煞", "六煞", "六煞"): ("凶", "三重六煞。感情纠葛极多，极度纠结"),
    ("天医", "延年", "绝命"): ("凶", "财富+能力→冲动决策。最危险的富贵组合"),
    ("生气", "生气", "绝命"): ("凶", "双贵人→投资暴雷。友情可能破裂"),
}

# 2.3 四连组合精编解读库（★ v2.0 新增）
# 四连预测整条号码的能量走势曲线
# 格式: (A, B, C, D): (走势, 解读)
QUAD_READINGS = {
    # ── 📈 上升曲线（后两吉 > 前两吉/平） ──
    ("绝命", "绝命", "天医", "延年"): ("上升", "大起格局：前期冲动破财，后期靠能力翻身"),
    ("绝命", "五鬼", "天医", "生气"): ("上升", "转型成功：从暴雷到贵人转运"),
    ("绝命", "天医", "延年", "生气"): ("上升", "先破后立：破财后事业+贵人双丰收"),
    ("祸害", "绝命", "天医", "延年"): ("上升", "涅槃重生：口舌官司后凭借能力东山再起"),
    ("祸害", "祸害", "天医", "生气"): ("上升", "由乱到治：是非过后贵人带财"),
    ("五鬼", "绝命", "天医", "延年"): ("上升", "变动中清醒：从暴雷到事业稳健"),
    ("绝命", "六煞", "天医", "生气"): ("上升", "情伤后翻盘：破财+感情伤后东山再起"),
    ("伏位", "绝命", "天医", "延年"): ("上升", "压抑→爆发→赚钱→事业，完整翻盘"),
    ("天医", "绝命", "延年", "天医"): ("上升", "财富流失后靠能力赚回，韧性极强"),

    # ── 📉 下降曲线（后两凶 > 前两吉/平） ──
    ("天医", "延年", "绝命", "五鬼"): ("下降", "盛极而衰：富裕→冲动→暴雷，需设防火墙"),
    ("天医", "生气", "绝命", "祸害"): ("下降", "好牌打烂：贵人带财后冲动+官司"),
    ("延年", "天医", "绝命", "五鬼"): ("下降", "巅峰坠落：事业财富双全后冲动暴雷"),
    ("延年", "生气", "绝命", "祸害"): ("下降", "人脉事业→冲动官司，大好变高危"),
    ("生气", "天医", "绝命", "绝命"): ("下降", "赚到钱后冲动连破，不留余地"),
    ("生气", "生气", "祸害", "绝命"): ("下降", "人缘好→小人→官司，交友不慎"),
    ("天医", "天医", "绝命", "五鬼"): ("下降", "富得快→败得快，暴发户心态"),
    ("天医", "伏位", "绝命", "祸害"): ("下降", "从稳到乱：财富积累后冲动惹祸"),
    ("天医", "延年", "六煞", "祸害"): ("下降", "富豪→情感纠葛→是非，后院起火"),
    ("生气", "延年", "五鬼", "绝命"): ("下降", "人人羡慕→偏执疯狂→一夜崩塌"),

    # ── ➡️ 平走/循环 ──
    ("天医", "绝命", "天医", "绝命"): ("循环", "赚-花-赚-花。天生留不住财"),
    ("绝命", "天医", "绝命", "天医"): ("循环", "破-赚-破-赚。交替轮回"),
    ("伏位", "伏位", "伏位", "伏位"): ("平走", "四连伏位，极度保守。多年原地踏步"),
    ("天医", "天医", "天医", "天医"): ("平走", "四连天医，极度富贵但也容易暴发心态"),
    ("绝命", "绝命", "绝命", "绝命"): ("下降", "四连绝命。极度凶险，建议立即更换号码"),
    ("祸害", "祸害", "祸害", "祸害"): ("下降", "四连祸害。是非官司不断"),
    ("五鬼", "五鬼", "五鬼", "五鬼"): ("下降", "四连五鬼。极度变动，健康堪忧"),
    ("六煞", "六煞", "六煞", "六煞"): ("下降", "四连六煞。感情极度纠结"),
    ("延年", "延年", "延年", "延年"): ("下降", "四连延年。事业压力极大，过劳高危"),
    ("生气", "生气", "生气", "生气"): ("平走", "四连生气。人缘极好但赚钱驱动力不足"),

    # ── 🌀 V字反转（凶→吉→凶→吉 波动） ──
    ("绝命", "天医", "绝命", "天医"): ("波动", "V字波动：破-赚-破-赚。过山车理财"),
    ("祸害", "天医", "祸害", "天医"): ("波动", "口舌-赚钱-口舌-赚钱。靠嘴的波动人生"),
    ("五鬼", "延年", "五鬼", "延年"): ("波动", "想法-事业-想法-事业。创意型创意工作"),
    ("六煞", "天医", "六煞", "天医"): ("波动", "情-钱-情-钱。靠人际吃饭的起伏"),
}


# ═══════════════════════════════════════════
# 三、0/5处理增强 (v2.0)
# ═══════════════════════════════════════════

# 0/5实战规则（基于八极灵数 2.0 + 乾坤国学院 实战教学）
# 
# 核心逻辑：
#   0 = 隐、空、藏、停、虚、被动延长、归零
#   5 = 显、强、桥、通、突然加速、突变/转折
#
# 五种实战场景：
#   1. 段落首 → X0 / X5（如 07→伏位, 37→伏位）
#      - 0在首：星被隐藏/延长，吉星变弱、凶星之凶也被压下
#      - 5在首：星的特性被加强/加速
#   2. 段落尾 → 0X / 5X（如 60, 65）
#      - 0在尾：能量走向归空/隐藏收尾
#      - 5在尾：能量突然显化/结束/突变
#   3. 夹心 → 0X0 / 5X5 / X0X（三连）
#      - 0X0：能量被双重隐藏，几乎不显
#      - 5X5：能量被双重加强，极旺（但可能过旺）
#   4. 长串 → 00 / 000 / 0000 / 55 / 555
#      - 00 / 000：超级伏位，极度的积累/等待/隐藏
#      - 55 / 555：突然爆发/转折信号
#   5. 显隐共振 → 050 / 505 / 0550
#      - 050：显→隐→显（波动）
#      - 505：隐→显→隐（波动）
#      - 0550：隐→显→显→隐（大波动/走完一圈）
#
# 实战用法（摘抄自八极灵数c1319）：
#   - 0是最后一个数字时（如...60）：该段能量归空，事业/财运停滞
#   - 5在中间通过（如...153）：天医+5延年 → 财富+事业的强化连接
#   - 连续000：长达3-5年的等待期/隐藏期
#   - 连续555：3年内必有重大转折


def classify_pair(pair: str) -> dict:
    """
    对单个两数字段分类（含高级0/5处理）

    Returns:
        dict with star, level, category, wu_xing, raw, zero_info
    """
    result = {
        "star": None, "level": 0, "category": None, "wu_xing": None,
        "raw": pair,
        "zero_info": {
            "has_zero": "0" in pair,
            "has_five": "5" in pair,
            "zero_five_rule": None,  # "head_votex" | "tail_votex" | "double_zero" | "double_five" | "none" | "fallback"
            "energy_effect": None,   # "hidden" | "amplified" | "vanishing" | "born_out" | "bridge" | "normal"
        },
        "is_duplicate": pair[0] == pair[1] if len(pair) == 2 else False,
        "note": "",
    }

    if len(pair) < 2:
        result["star"] = "伏位"
        result["level"] = 4
        result["category"] = "平"
        result["wu_xing"] = "木"
        result["zero_info"]["zero_five_rule"] = "fallback"
        result["note"] = "不足2位"
        return result

    # 特殊：00 / 000 系列 → 超级伏位
    if pair == "00":
        result["star"] = "伏位"
        result["level"] = 1
        result["category"] = "平"
        result["wu_xing"] = "木"
        result["zero_info"]["zero_five_rule"] = "double_zero"
        result["zero_info"]["energy_effect"] = "hidden"
        result["note"] = "双0伏位,极度隐藏/延长/归零"
        return result

    if pair == "55":
        result["star"] = "伏位"
        result["level"] = 1
        result["category"] = "平"
        result["wu_xing"] = "木"
        result["zero_info"]["zero_five_rule"] = "double_five"
        result["zero_info"]["energy_effect"] = "amplified"
        result["note"] = "双5伏位,强烈显化/突变信号"
        return result

    # 0在段首 → 伏位（隐藏/延长）
    if pair[0] == "0":
        result["star"] = "伏位"
        level_map = {"0": 1, "1": 2, "2": 3, "3": 3, "4": 3, "5": 2,
                     "6": 3, "7": 3, "8": 3, "9": 3}
        result["level"] = level_map.get(pair[1], 3)
        result["category"] = "平"
        result["wu_xing"] = "木"
        result["zero_info"]["zero_five_rule"] = "head_votex"
        result["zero_info"]["energy_effect"] = "hidden"
        result["note"] = f"0开头,原{pair[1]}星被隐藏/延长"
        return result

    # 5在段首 → 伏位（显性/加强/桥梁）
    if pair[0] == "5":
        result["star"] = "伏位"
        level_map = {"0": 2, "1": 1, "2": 2, "3": 2, "4": 2,
                     "5": 1, "6": 2, "7": 2, "8": 2, "9": 2}
        result["level"] = level_map.get(pair[1], 2)
        result["category"] = "平"
        result["wu_xing"] = "木"
        result["zero_info"]["zero_five_rule"] = "head_votex"
        result["zero_info"]["energy_effect"] = "amplified"
        result["note"] = f"5开头,原{pair[1]}星被显化/加强"
        return result

    # 0在段尾 → 伏位（归空/隐藏收尾）
    if pair[1] == "0":
        result["star"] = "伏位"
        level_map = {"0": 4, "1": 3, "2": 3, "3": 4, "4": 4,
                     "5": 2, "6": 3, "7": 4, "8": 3, "9": 3}
        result["level"] = level_map.get(pair[0], 3)
        result["category"] = "平"
        result["wu_xing"] = "木"
        result["zero_info"]["zero_five_rule"] = "tail_votex"
        result["zero_info"]["energy_effect"] = "vanishing"
        result["note"] = f"0结尾,原{pair[0]}星能量归空/隐藏收尾"
        return result

    # 5在段尾 → 伏位（显化收尾/突然结束）
    if pair[1] == "5":
        result["star"] = "伏位"
        level_map = {"0": 3, "1": 2, "2": 2, "3": 3, "4": 3,
                     "5": 1, "6": 2, "7": 3, "8": 2, "9": 2}
        result["level"] = level_map.get(pair[0], 2)
        result["category"] = "平"
        result["wu_xing"] = "木"
        result["zero_info"]["zero_five_rule"] = "tail_votex"
        result["zero_info"]["energy_effect"] = "born_out"
        result["note"] = f"5结尾,原{pair[0]}星能量显化收尾/突变转折"
        return result

    # 不含0/5 → 直接查表
    if pair in EIGHT_STARS_DATA:
        star, level, cat, wx = EIGHT_STARS_DATA[pair]
        result["star"] = star
        result["level"] = level
        result["category"] = cat
        result["wu_xing"] = wx
        result["zero_info"]["zero_five_rule"] = "none"
        result["zero_info"]["energy_effect"] = "normal"
        if result["is_duplicate"]:
            result["note"] = "重叠数字"
    else:
        # fallback → 伏位
        result["star"] = "伏位"
        result["level"] = 2
        result["category"] = "平"
        result["wu_xing"] = "木"
        result["zero_info"]["zero_five_rule"] = "fallback"
        result["zero_info"]["energy_effect"] = "normal"
        result["note"] = "未识别,按伏位"

    return result


def detect_zero_five_chain(digits: str, segments: list) -> list:
    """
    检测号码中的0/5长串和显隐共振模式

    在segment上添加额外标记：
    1. "zero_five_chain": 连续0/5的段索引
    2. "resonance_chain": 显隐共振（050/505/0550等）
    """
    extras = []

    # 查找连续0/5（三连及以上）
    i = 0
    while i < len(segments):
        seg = segments[i]
        if seg["zero_info"].get("has_zero") or seg["zero_info"].get("has_five"):
            chain_start = i
            # 向前看是否连续0/5
            while i < len(segments) and (
                segments[i]["zero_info"].get("has_zero") or
                segments[i]["zero_info"].get("has_five")
            ):
                i += 1
            chain_len = i - chain_start
            if chain_len >= 2:
                # 长串检测
                chain_pairs = [segments[j]["raw"] for j in range(chain_start, i)]
                chain_str = "".join(chain_pairs)

                # 判断类型
                all_zero = all("0" in p for p in chain_pairs)
                all_five = all("5" in p for p in chain_pairs)

                if all_zero:
                    reading = f"位置{chain_start}-{i-1}: {chain_len}段连续含0, 极度隐藏/归零/等待期, 约{chain_len*2}年能量停滞"
                elif all_five:
                    reading = f"位置{chain_start}-{i-1}: {chain_len}段连续含5, 强烈显化/突变信号, 人生重大转折期"
                else:
                    reading = f"位置{chain_start}-{i-1}: {chain_len}段0/5交替, 显隐共振, 能量波动极大"

                extras.append({
                    "type": "zero_five_chain",
                    "start": chain_start,
                    "end": i - 1,
                    "chain_length": chain_len,
                    "chain_pairs": chain_pairs,
                    "reading": reading,
                })

                # 0515 / 0505 等混合共振检测
                has_zero = any("0" in p for p in chain_pairs)
                has_five = any("5" in p for p in chain_pairs)
                if has_zero and has_five and chain_len >= 3:
                    extras.append({
                        "type": "resonance_chain",
                        "start": chain_start,
                        "end": i - 1,
                        "chain_length": chain_len,
                        "chain_pairs": chain_pairs,
                        "reading": "0/5混合共振: 藏→显→藏→显交替, 人生阶段性爆发与隐退",
                    })
        else:
            i += 1

    return extras


# ═══════════════════════════════════════════
# 四、核心引擎
# ═══════════════════════════════════════════

class BaStarEngine:
    """八星数字能量引擎 v2.0"""

    def __init__(self):
        self._double = DOUBLE_READINGS
        self._triple = TRIPLE_READINGS
        self._quad = QUAD_READINGS

    def analyze_number(self, number: str) -> dict:
        """全号段分析主入口"""
        digits = self._clean(number)
        if len(digits) < 2:
            return {"error": "号码太短，至少2位"}

        is_phone = len(digits) == 11
        prefix = digits[:3] if is_phone else None
        main_part = digits

        # 1. 两两相邻分组（从第0位开始）
        pairs = self._make_pairs(main_part)

        # 2. 每对分类（含0/5高级处理）
        segments = [classify_pair(p) for p in pairs]

        # 3. 0/5长串检测
        zero_five_chains = detect_zero_five_chain(digits, segments)

        # 4. 号段标记
        prefix_info = None
        if is_phone:
            prefix_pairs_raw = [digits[i:i+2] for i in range(2)]  # 0-1, 1-2
            prefix_stars = [classify_pair(pp) for pp in prefix_pairs_raw]
            prefix_info = {
                "prefix": prefix,
                "prefix_pairs": prefix_stars,
            }

        # 5. 统计
        stats = self._build_stats(segments)

        # 6. 组合分析
        combos = self._analyze_combos(segments)
        triples = self._analyze_triples(segments)
        quads = self._analyze_quads(segments)

        # 7. 连接分析（v2.1 实战核心）
        connections = self._analyze_connections(segments)

        # 8. 五行
        wx = self._analyze_wuxing(stats["wu_xing_counts"])

        # 9. 评分（基于连接的实战评分）
        score = self._calc_score(stats, segments, connections, triples)

        # 10. 人话摘要（尾4位优先）
        summary = self._gen_summary(stats, score, combos, triples, quads,
                                     zero_five_chains, wx, is_phone, prefix_info,
                                     connections)

        return {
            "version": "2.1",
            "number": number,
            "clean_digits": digits,
            "is_phone": is_phone,
            "prefix_info": prefix_info,
            "pairs_count": len(pairs),
            "segments": segments,
            "zero_five_chains": zero_five_chains,
            "star_counts": stats["star_counts"],
            "refined_levels": stats["refined_levels"],
            "ji_ping_xiong": stats["ji_ping_xiong"],
            "ratio": stats["ratio"],
            "wu_xing": stats["wu_xing_counts"],
            "wu_xing_shengke": wx,
            "combinations": combos,
            "triples": triples,
            "quads": quads,
            "connections": connections,
            "score": score,
            "summary": summary,
        }

    def analyze_phone(self, phone: str) -> dict:
        return self.analyze_number(phone)

    def ask(self, number: str) -> str:
        r = self.analyze_number(number)
        score = r["score"]
        s = r["summary"]
        first = s.split("\n")[0] if s else ""
        return f"评分{score}分 | {first}"

    def get_scores_for_cross(self, number: str) -> dict:
        r = self.analyze_number(number)
        # v3.0 新增：能量流动+制化
        flow = self._analyze_energy_flow(r["segments"])
        resolve = self._analyze_resolve_chain(r["segments"])
        return {
            "available": True,
            "score": r["score"],
            "result_summary": (
                f"八星数字能量: {r['ratio']['ji_percent']}%吉 "
                f"{r['ratio']['xiong_percent']}%凶"
            ),
            "star_counts": r["star_counts"],
            "combinations": r["combinations"],
            "triples": r["triples"],
            "quads": r["quads"],
            "connections": r.get("connections"),
            "zero_five_chains": r["zero_five_chains"],
            "wu_xing": r["wu_xing_shengke"],
            "energy_flow": flow,
            "resolve_chain": resolve,
        }

    # ── 内部方法 ──

    def _clean(self, s: str) -> str:
        return "".join(c for c in s if c.isdigit())

    def _make_pairs(self, digits: str) -> list:
        """两两相邻分组，全号段不分跳过"""
        return [digits[i:i+2] for i in range(len(digits) - 1)]

    def _build_stats(self, segments: list) -> dict:
        """构建统计信息"""
        star_counts = {}
        star_levels = {}
        wx_counts = {}
        ji = ping = xiong = 0

        for seg in segments:
            star = seg["star"]
            if star:
                star_counts[star] = star_counts.get(star, 0) + 1
                if star not in star_levels:
                    star_levels[star] = []
                star_levels[star].append(seg["level"])
            if seg["wu_xing"]:
                wx_counts[seg["wu_xing"]] = wx_counts.get(seg["wu_xing"], 0) + 1
            cat = seg.get("category")
            if cat == "吉":
                ji += 1
            elif cat == "凶":
                xiong += 1
            else:
                ping += 1

        total = ji + ping + xiong
        refined = {}
        for star, levels in star_levels.items():
            refined[star] = {
                "min_level": min(levels),
                "max_level": max(levels),
                "avg_level": round(sum(levels) / len(levels), 1),
                "count": len(levels),
            }

        return {
            "star_counts": star_counts,
            "refined_levels": refined,
            "wu_xing_counts": wx_counts,
            "ji_ping_xiong": {"吉": ji, "平": ping, "凶": xiong},
            "ratio": {
                "ji_percent": round(ji / total * 100, 1) if total else 0,
                "xiong_percent": round(xiong / total * 100, 1) if total else 0,
            },
            "total": total,
        }

    def _analyze_combos(self, segments: list) -> list:
        """双连组合"""
        combos = []
        for i in range(len(segments) - 1):
            a, b = segments[i], segments[i+1]
            if a["star"] and b["star"]:
                key = (a["star"], b["star"])
                reading = self._double.get(
                    key,
                    f"{a['star']}+{b['star']}"
                )
                combos.append({
                    "pair": f"{a['raw']}+{b['raw']}",
                    "stars": key,
                    "reading": reading,
                    "position": i,
                })
        return combos

    def _analyze_triples(self, segments: list) -> list:
        """三连组合"""
        triples = []
        for i in range(len(segments) - 2):
            a, b, c = segments[i], segments[i+1], segments[i+2]
            if a["star"] and b["star"] and c["star"]:
                key = (a["star"], b["star"], c["star"])
                entry = self._triple.get(key)
                if entry:
                    pred, reading = entry
                else:
                    pred, reading = self._gen_triple(key)
                triples.append({
                    "pairs": f"{a['raw']}{b['raw']}{c['raw']}",
                    "stars": key,
                    "prediction": pred,
                    "reading": reading,
                    "position": i,
                })
        return triples

    def _analyze_quads(self, segments: list) -> list:
        """四连组合"""
        quads = []
        for i in range(len(segments) - 3):
            items = [segments[i+j] for j in range(4)]
            stars = tuple(s["star"] for s in items)
            if all(stars):
                entry = self._quad.get(stars)
                if entry:
                    trend, reading = entry
                else:
                    trend, reading = self._gen_quad(stars)
                quads.append({
                    "pairs": "".join(s["raw"] for s in items),
                    "stars": list(stars),
                    "trend": trend,
                    "reading": reading,
                    "position": i,
                })
        return quads

    def _gen_triple(self, key: tuple) -> tuple:
        """自动生成三连解读（未命中精编库时的fallback）"""
        a, b, c = key
        cats = [
            STAR_ATTRIBUTES.get(s, {}).get("category", "平")
            for s in key
        ]

        ji_count = cats.count("吉")
        xiong_count = cats.count("凶")

        if ji_count >= 2 and xiong_count == 0:
            return ("吉", f"{a}+{b}+{c}: 吉星为主导，能量正向流通")
        elif xiong_count >= 2 and ji_count == 0:
            return ("凶", f"{a}+{b}+{c}: 凶星串联，需警惕能量负向累积")
        elif ji_count >= xiong_count:
            return ("平", f"{a}+{b}+{c}: 吉凶参半，吉略占优")
        elif xiong_count > ji_count:
            return ("平", f"{a}+{b}+{c}: 凶星偏重，需谨慎")
        else:
            return ("平", f"{a}+{b}+{c}: 伏位中继，能量待发")

    def _gen_quad(self, key: tuple) -> tuple:
        """自动生成四连走势"""
        a, b, c, d = key
        cats = [
            STAR_ATTRIBUTES.get(s, {}).get("category", "平")
            for s in key
        ]

        front_ji = sum(1 for x in cats[:2] if x == "吉")
        front_xiong = sum(1 for x in cats[:2] if x == "凶")
        back_ji = sum(1 for x in cats[2:] if x == "吉")
        back_xiong = sum(1 for x in cats[2:] if x == "凶")

        ji_trend = back_ji - front_ji
        xiong_trend = back_xiong - front_xiong

        net = back_ji - back_xiong - (front_ji - front_xiong)

        if net > 0:
            return ("上升", f"{a}+{b}→{c}+{d}: 能量上升趋势，后面比前面好")
        elif net < 0:
            return ("下降", f"{a}+{b}→{c}+{d}: 能量下降曲线，需注意后半段凶星")
        else:
            return ("平走", f"{a}+{b}→{c}+{d}: 能量平稳，前后基本持平")

    def _analyze_wuxing(self, wx_counts: dict) -> dict:
        """五行生克分析"""
        active = [wx for wx, c in wx_counts.items() if c > 0]
        sheng = []
        ke = []

        for wx in active:
            st = WU_XING_SHENG.get(wx)
            kt = WU_XING_KE.get(wx)
            if st and st in active:
                sheng.append(f"{wx}生{st}")
            if kt and kt in active:
                ke.append(f"{wx}克{kt}")

        if not active:
            return {"sheng": [], "ke": [], "pattern": "无数据"}

        sorted_wx = sorted(wx_counts.items(), key=lambda x: -x[1])
        main_wx = sorted_wx[0][0] if sorted_wx else "?"

        if len(active) == 1:
            pattern = f"单一{main_wx}局，能量纯粹"
        elif len(active) == 2:
            w1, w2 = active
            if WU_XING_SHENG.get(w1) == w2:
                pattern = f"{w1}生{w2}局，能量顺生"
            elif WU_XING_SHENG.get(w2) == w1:
                pattern = f"{w2}生{w1}局，能量顺生"
            elif WU_XING_KE.get(w1) == w2:
                pattern = f"{w1}克{w2}局，能量相克"
            elif WU_XING_KE.get(w2) == w1:
                pattern = f"{w2}克{w1}局，能量相克"
            else:
                pattern = f"{w1}/{w2}局，不相生克"
        else:
            pattern = f"多行局({','.join(active)})，{main_wx}为最旺"

        return {
            "counts": wx_counts,
            "main": main_wx,
            "sheng": sheng,
            "ke": ke,
            "pattern": pattern,
        }

    # ───────────────────────────────────────
    # 实战连接分析（v2.1 核心进化）
    # ───────────────────────────────────────

    def _analyze_connections(self, segments: list) -> dict:
        """
        实战连接分析 v2.2 — 开-中-尾三段式 + 整体能量曲线

        核心原则（基于八极灵数2.0/实战派解读）：
        1. 号码三段论：开头(0-3位)=天赋/贵人/开局，中间(4-6位)=过程/经历，尾部(7-9位)=结局/收束
        2. 尾数整体格局：最后3组pair不是各自独立，而是构成一个完整格局
        3. 能量连接链：去掉伏位中继，只看纯七星链
        4. 好号码=开头好+尾巴好成格局，中间可以有波折
        5. 2134=绝命→天医→延年 是"破而后立"的圆满收束格局

        Returns:
            {
                "chains": 全号能量链,
                "triplet_segments": 开-中-尾能量分段,
                "tail_pattern": 尾数完整格局解读,
                "curve_type": 能量曲线类型(上升/下降/V字/倒V/平走/波动),
            }
        """
        CAT_ORDER = {"吉": 1, "平": 0, "凶": -1}

        # ── 段1：七星序列（去掉伏位）──
        star_sequence = []  # (star, category, raw, level, pos)
        for i, seg in enumerate(segments):
            star = seg["star"]
            if star and star != "伏位":
                cat = seg["category"] or "平"
                star_sequence.append((star, cat, seg["raw"], seg["level"], i))

        # ── 段2：能量链分析 ──
        chains = []
        if star_sequence:
            current_chain = [star_sequence[0]]
            for item in star_sequence[1:]:
                prev_cat = CAT_ORDER.get(current_chain[-1][1], 0)
                cur_cat = CAT_ORDER.get(item[1], 0)
                if prev_cat == cur_cat and cur_cat != 0:
                    current_chain.append(item)
                else:
                    if len(current_chain) >= 2:
                        cat_label = current_chain[0][1]
                        chains.append({
                            "stars": [x[0] for x in current_chain],
                            "pairs": [x[2] for x in current_chain],
                            "length": len(current_chain),
                            "energy": cat_label,
                            "positions": [x[4] for x in current_chain],
                        })
                    current_chain = [item]
            if len(current_chain) >= 2:
                cat_label = current_chain[0][1]
                chains.append({
                    "stars": [x[0] for x in current_chain],
                    "pairs": [x[2] for x in current_chain],
                    "length": len(current_chain),
                    "energy": cat_label,
                    "positions": [x[4] for x in current_chain],
                })

        # ── 段3：开-中-尾三段能量（未去掉伏位，看原始能量分布）──
        n = len(segments)
        head = segments[:3] if n >= 3 else segments
        middle = segments[3:7] if n >= 7 else segments[3:]
        tail = segments[7:] if n >= 10 else segments[-3:] if n >= 3 else segments

        def _segment_score(segs):
            """一段的净能量得分（吉+，凶-，考虑等级）"""
            s = 0
            for seg in segs:
                cat = seg.get("category", "平")
                lv = seg.get("level", 3)
                w = min(4, 5 - lv)
                if cat == "吉":
                    s += w
                elif cat == "凶":
                    s -= w * 1.5
            return s

        head_score = _segment_score(head)
        mid_score = _segment_score(middle)
        tail_score_seg = _segment_score(tail)

        # ── 段4：能量曲线类型（八星实战派三段论）──
        # 实战派的核心理念：V型/谷型/上升是最好的曲线形态
        # 倒V/下降/高位平稳要看使用场景
        
        def _trend_score(segs):
            s = 0
            for seg in segs:
                cat = seg.get("category", "平")
                lv = seg.get("level", 3)
                w = min(4, 5 - lv)
                if cat == "吉":
                    s += w * 1.2
                elif cat == "凶":
                    s -= w * 1.0
            return s
        
        head_trend = _trend_score(head)
        mid_trend = _trend_score(middle)
        tail_trend = _trend_score(tail)
        
        if head_trend - mid_trend > 2 and tail_trend - mid_trend > 2 and tail_trend > 0:
            if head_trend < 0 and tail_trend >= tail_score_seg:
                curve_type = "V型"
            elif head_trend > 0 and tail_trend > 0:
                curve_type = "谷型"
            else:
                curve_type = "V型"
        elif head_trend < -2 and tail_trend >= 3:
            curve_type = "V型反转"
        elif tail_trend > head_trend and tail_trend > 0:
            curve_type = "上升"
        elif head_trend > tail_trend and head_trend > 0 and tail_trend < 0:
            curve_type = "下降"
        elif mid_trend > head_trend and mid_trend > tail_trend and tail_trend < 0:
            curve_type = "倒V"
        elif head_trend >= 0 and mid_trend >= 0 and tail_trend >= 0:
            curve_type = "高位稳定"
        else:
            curve_type = "平走"

        # ── 段5：尾数完整格局（最重要！）──
        # 取最后3组pair的完整七星序列作为一个整体格局
        tail_pairs_raw = [s["raw"] for s in tail]
        tail_stars = [s["star"] for s in tail if s["star"] and s["star"] != "伏位"]
        tail_stars_full = [s["star"] for s in tail]  # 含伏位

        # 七星链（去掉伏位）的尾数格局
        tail_seq = tail_stars  # 已去伏位

        # 尾数格局分类
        # 经典格局库（相比单一pair的评分，格局才是实战派判断）
        TAIL_PATTERNS = {
            # 🟢 吉格收束
            "天医_天医": ("吉", "双天医收尾，财库双开"),
            "天医_延年": ("吉", "财富收束于事业，富贵双全"),
            "延年_生气": ("吉", "事业得贵人助，名利双收"),
            "天医_生气": ("吉", "财富与贵人同至，人财两旺"),
            "生气_天医": ("吉", "贵人带财收官"),
            "延年_天医": ("吉", "事业致富，有能力守住财富"),
            "延年_延年": ("吉", "双延年收局，事业稳健，能力强"),
            "天医_伏位": ("平", "财富沉淀待发"),
            "生气_延年": ("吉", "人脉转化事业，贵人成事"),
            "生气_生气": ("平", "贵人环绕但不聚财"),
            # 🟡 中性收束
            "伏位_天医": ("平", "等待后财富"),
            "伏位_延年": ("平", "等待后事业"),
            "伏位_生气": ("平", "人脉待开发"),
            "绝命_天医": ("平", "破而后立，但过程折腾—创业格局"),
            "绝命_天医_延年": ("吉", "破而后立终成事业！大起大落的完美结局，创业/销售的顶级尾数"),
            "绝命_延年": ("平", "冲动后成事"),
            "祸害_天医": ("平", "靠口才赚钱"),
            "五鬼_天医": ("平", "偏财收尾"),
            "六煞_天医": ("平", "人际生财"),
            # 🔴 凶格收束
            "绝命_绝命": ("凶", "双绝命收束，破财不止"),
            "绝命_祸害": ("凶", "冲动+全非收局，官司预警"),
            "绝命_五鬼": ("凶", "冲动+偏执，暴雷收尾"),
            "祸害_祸害": ("凶", "是非不断收束"),
            "五鬼_五鬼": ("凶", "变动不止收束"),
            "六煞_六煞": ("凶", "情感纠葛收束"),
            "五鬼_祸害": ("凶", "聪明反被误收束"),
            "绝命_六煞": ("凶", "为情破财收束"),
        }

        # 匹配尾数格局（按最长匹配）
        tail_seq_str = "_".join(tail_seq) if tail_seq else ""
        if not tail_seq_str:
            tail_pattern = ("平", "伏位收尾，能量中立")
        else:
            # 从长到短匹配
            matched = None
            for pat_len in [5, 4, 3, 2, 1]:
                parts = tail_seq_str.split("_")
                for start in range(len(parts) - pat_len + 1):
                    candidate = "_".join(parts[start:start+pat_len])
                    if candidate in TAIL_PATTERNS:
                        matched = candidate
                        break
                if matched:
                    break
            if matched:
                tail_pattern = TAIL_PATTERNS[matched]
            else:
                # fallback: 八星实战派启发式判断（比last_two更智能）
                # 核心：2+吉尾无凶=吉，2+凶尾无吉=凶，末位吉=吉，末位凶=凶
                cat_order = {"吉": 1, "凶": -1, "平": 0}
                tail_ji = sum(1 for s in tail_seq if cat_order.get(
                    STAR_ATTRIBUTES.get(s, {}).get("category", ""), 0) > 0)
                tail_xiong = sum(1 for s in tail_seq if cat_order.get(
                    STAR_ATTRIBUTES.get(s, {}).get("category", ""), 0) < 0)
                last_cat = STAR_ATTRIBUTES.get(tail_seq[-1], {}).get("category", "平") if tail_seq else "平"
                
                if tail_ji >= 2 and tail_xiong == 0:
                    tail_pattern = ("吉", f"尾序{tail_seq_str}: {tail_ji}吉串联收束，格局优秀")
                elif tail_xiong >= 2 and tail_ji == 0:
                    tail_pattern = ("凶", f"尾序{tail_seq_str}: {tail_xiong}凶串联收束，需警惕")
                elif tail_ji >= 2 and tail_xiong == 1:
                    # 两吉一凶，末位凶=偏凶，末位吉=大吉
                    if last_cat == "吉":
                        tail_pattern = ("吉", f"尾序{tail_seq_str}: 两吉一凶但末位吉星收束，大局吉")
                    else:
                        tail_pattern = ("凶", f"尾序{tail_seq_str}: 两吉一凶但末位凶星盖顶，中段好晚年需防")
                elif last_cat == "吉":
                    tail_pattern = ("吉", f"尾序{tail_seq_str}: 末位吉星收束，能量向好")
                elif tail_ji >= 1 and tail_xiong <= 1:
                    # 吉凶参半，如天医_祸害
                    if last_cat == "凶":
                        tail_pattern = ("平", f"尾序{tail_seq_str}: 吉凶参半，末位凶待观察")
                    else:
                        tail_pattern = ("平", f"尾序{tail_seq_str}: 吉凶参半，中性格局")
                elif last_cat == "凶":
                    tail_pattern = ("凶", f"尾序{tail_seq_str}: 末位凶星收束，需谨慎")
                else:
                    tail_pattern = ("平", f"尾序{tail_seq_str}: 中性格局收束")

        # ── 段6：整号综合判断（八星实战派）──
        # 核心原则：
        # a) 尾数格局决定结局（最重要）
        # b) 能量曲线决定人生节奏
        # c) 中段凶星看用途——绝命=冲劲/五鬼=脑力/六煞=人际/祸害=口才
        # d) 伏位=蓄力等待，不是空洞
        # e) 吉凶pair计数≠号码品质，格局决定一切

        # 开头两对吉凶
        head_cats = [s.get("category") for s in head[:2] if s.get("category")]
        head_has_ji = "吉" in head_cats
        head_has_xiong = "凶" in head_cats

        # 中段凶星用途分析
        mid_stars = [s["star"] for s in middle if s.get("star") and s.get("category") == "凶"]
        mid_xiong_map = {
            "绝命": "拼搏/冒险",
            "五鬼": "智慧/变化",
            "六煞": "人际/情感",
            "祸害": "口才/是非",
        }
        mid_xiong_purpose = []
        for s in mid_stars:
            if s in mid_xiong_map:
                mid_xiong_purpose.append(mid_xiong_map[s])

        # 整体号码类型判断
        tail_pat_cat, _ = tail_pattern
        
        if tail_pat_cat == "吉" and curve_type in ("V型", "谷型", "V型反转", "上升"):
            number_category = "能量上升"
            # 尾数有"破而后立"或"绝命"等关键词→更偏向大格局
            tail_text = tail_pattern[1]
            if "破而后立" in tail_text or "顶级" in tail_text or "创业" in tail_text:
                number_subtype = "先难后成大格局号"
            else:
                number_subtype = "稳中向好潜力号"
        elif tail_pat_cat == "吉" and curve_type == "高位稳定":
            if mid_xiong_purpose:
                number_category = "能量上升"
                number_subtype = "小波折但格局稳"
            else:
                number_category = "全吉平稳"
                number_subtype = "财官双美平安号"
        elif tail_pat_cat == "吉" and curve_type == "倒V":
            number_category = "高开走低"
            number_subtype = "中段需关注"
        elif tail_pat_cat == "凶":
            number_category = "尾数预警"
            number_subtype = "收束不佳"
        elif tail_pat_cat == "平":
            number_category = "中性格局"
            number_subtype = "需结合使用者八字判断"
        else:
            number_category = "普通"
            number_subtype = "无明显指向"

        return {
            "chains": chains,
            "star_sequence": [(x[0], x[1], x[4]) for x in star_sequence],
            "segments_score": {
                "head": head_score,
                "middle": mid_score,
                "tail": tail_score_seg,
            },
            "curve_type": curve_type,
            "tail_pattern": tail_pattern,
            "tail_stars_raw": tail_pairs_raw,
            "tail_stars": tail_stars_full,
            "head_has_ji": head_has_ji,
            "head_has_xiong": head_has_xiong,
            "mid_xiong_purpose": mid_xiong_purpose,
            "number_category": number_category,
            "number_subtype": number_subtype,
        }

    def _calc_score(self, stats: dict, segments: list,
                    connections: dict, triples: list) -> int:
        """
        v3.0 八星实战派评分公式

        不再做机械权重配比，而是按号码类型设定分数区间：
        - 能量上升 + 尾巴收吉 = 70-95（最好的号码）
        - 全吉平稳 = 65-85（好号码，但不如有波折的）
        - 尾凶 = 0-40
        - 中性 = 40-65
        
        在区间内，用链长/曲线做微调。
        """
        if stats["total"] == 0:
            return 50

        tail_pat, _ = connections["tail_pattern"]
        curve = connections["curve_type"]
        chains = connections["chains"]
        ncat = connections["number_category"]
        mid_xiong = connections["mid_xiong_purpose"]

        total_ji_chain = sum(c["length"] for c in chains if c["energy"] == "吉")
        total_xiong_chain = sum(c["length"] for c in chains if c["energy"] == "凶")
        max_ji = max([c["length"] for c in chains if c["energy"] == "吉"], default=0)
        max_xiong = max([c["length"] for c in chains if c["energy"] == "凶"], default=0)

        # ── 基准分（由号码类型决定）──
        if ncat == "能量上升":
            # 最佳类型：尾巴收吉 + 曲线朝上
            base = 72
            if curve in ("V型", "V型反转"):
                base += 8  # 先难后成，加分
            if curve == "谷型":
                base += 6  # 开端好→中波折→尾更好
            # 长吉链奖励
            base += min(10, total_ji_chain * 0.5)
            # 中段有凶星但有意义 = 加分（奋斗者）
            if mid_xiong:
                base += min(4, len(mid_xiong) * 2)
            # 大长链惩罚——凶链太长
            base -= min(15, total_xiong_chain * 2.5)
            # cap
            base = max(60, min(95, base))
        elif ncat == "全吉平稳":
            base = 68
            # 长吉链加分
            base += min(12, total_ji_chain * 0.6)
            # 全吉平稳 = 无明显波折
            base += 5 if not mid_xiong else 0
            # cap
            base = max(55, min(88, base))
        elif ncat == "高开走低":
            base = 45
            base -= min(15, total_xiong_chain * 3)
            base += min(8, total_ji_chain * 0.4)
            base = max(25, min(65, base))
        elif tail_pat == "凶":
            base = 30
            base -= min(20, total_xiong_chain * 3)
            base = max(0, min(50, base))
        else:
            base = 48
            base += min(8, total_ji_chain * 0.3)
            base -= min(12, total_xiong_chain * 2)
            base = max(20, min(70, base))

        return int(round(base))

    def _gen_summary(self, stats: dict, score: int,
                     combos: list, triples: list, quads: list,
                     zero_five_chains: list, wx: dict,
                     is_phone: bool, prefix_info: dict,
                     connections: dict) -> str:
        """v3.0 八星实战派摘要 — 号码类型 + 三段能量流 + 实战建议"""
        lines = []
        ji = stats["ji_ping_xiong"]["吉"]
        xiong = stats["ji_ping_xiong"]["凶"]
        seg_scores = connections["segments_score"]

        # ── 总体评价 ──
        if score >= 80:
            level = "优"
        elif score >= 65:
            level = "良"
        elif score >= 50:
            level = "中"
        elif score >= 35:
            level = "低"
        else:
            level = "差"
        lines.append(f"【综合评分】{score}/100（{level}）")
        ncat = connections["number_category"]
        nsub = connections["number_subtype"]
        ncat_emoji = {"能量上升": "📈", "全吉平稳": "🏔️", "高开走低": "📉", "尾数预警": "🚨", "中性格局": "⚪", "普通": "➡️"}
        lines.append(f"{ncat_emoji.get(ncat, '')} 号码类型: {ncat} — {nsub}")

        # ── 能量曲线 ──
        curve = connections["curve_type"]
        curve_emoji = {"上升": "📈", "V型": "📈", "V型反转": "📈", "下降": "📉",
                       "高位稳定": "🏔️",
                       "倒V": "📉", "平走": "➡️", "峰型": "🔝", "谷型": "🕳️"}
        lines.append(f"{curve_emoji.get(curve, '')} 能量曲线: {curve}")
        lines.append(f"  开头{seg_scores['head']:.0f} → 中间{seg_scores['middle']:.0f} → 尾部{seg_scores['tail']:.0f}")

        # ── 尾数格局 ──
        lines.append("━" * 30)
        tail_pat, tail_reading = connections["tail_pattern"]
        pat_emoji = {"吉": "🟢", "凶": "🔴", "平": "⚪"}.get(tail_pat, "")
        lines.append(f"{pat_emoji} 尾数格局: {tail_reading}")

        tail_stars = connections["tail_stars"]
        if tail_stars:
            line_parts = []
            for s in tail_stars:
                attr = STAR_ATTRIBUTES.get(s, {})
                cat = attr.get("category", "平")
                emoji = {"吉": "🟢", "凶": "🔴", "平": "⚪"}.get(cat, "")
                line_parts.append(f"{emoji}{s}")
            lines.append(f"  {' → '.join(line_parts)}")

        tail_pairs = connections["tail_stars_raw"]
        if tail_pairs:
            lines.append(f"  (数组: {' '.join(tail_pairs)})")

        # ── 开中尾三段 ──
        lines.append("━" * 30)
        lines.append("【开·中·尾三段】")

        # 主要吉凶星
        good = sorted(
            [(s, c) for s, c in stats["star_counts"].items()
             if STAR_ATTRIBUTES.get(s, {}).get("category") == "吉"],
            key=lambda x: -x[1]
        )
        bad = sorted(
            [(s, c) for s, c in stats["star_counts"].items()
             if STAR_ATTRIBUTES.get(s, {}).get("category") == "凶"],
            key=lambda x: -x[1]
        )
        if good:
            lines.append(f"🟢 吉星: {' '.join(f'{s}×{c}' for s,c in good)}")
        if bad:
            lines.append(f"🔴 凶星: {' '.join(f'{s}×{c}' for s,c in bad)}")

        # 全号能量链
        chains = connections["chains"]
        if chains:
            for c in chains:
                sym = "🟢" if c["energy"] == "吉" else "🔴"
                lines.append(f"  {sym} {c['length']}星链: {'→'.join(c['stars'])}")
        else:
            lines.append("  无有效能量链")

        # 中段凶星用途
        mid_xiong = connections.get("mid_xiong_purpose", [])
        if mid_xiong:
            lines.append(f"  ⚡中段凶星用途: {' + '.join(mid_xiong)}")

        # ── 三连亮点/预警（只看尾部位置） ──
        good_triples = [t for t in triples if t.get("prediction") == "吉"]
        bad_triples = [t for t in triples if t.get("prediction") == "凶"]
        tail_bad = [t for t in bad_triples if t["position"] >= 5]
        tail_good = [t for t in good_triples if t["position"] >= 5]
        if tail_good:
            for t in tail_good[:1]:
                lines.append(f"✅ 尾部亮点: {t['pairs']} → {t['reading']}")
        if tail_bad:
            for t in tail_bad[:1]:
                lines.append(f"🚨 尾部预警: {t['pairs']} → {t['reading']}")

        # 0/5
        if zero_five_chains:
            for z in zero_five_chains:
                lines.append(f"💧 {z['reading']}")

        # ── 八星实战派综合判断 ──
        lines.append("━" * 30)
        lines.append("【八星实战派诊断】")
        
        if ncat == "能量上升":
            lines.append("✅ 尾数格局收吉 + 能量曲线朝上 = 号码能量向好")
            if curve in ("V型", "V型反转"):
                lines.append("  📈 先难后成格局，适合创业/奋斗型人士")
            else:
                lines.append("  📈 稳中向上格局，适合持续发展的各类人士")
            if mid_xiong:
                lines.append(f"  ⚡ 中段有凶星({' + '.join(mid_xiong)})，是奋斗过程的助燃剂，") 
                lines.append(f"     不是先天缺陷。正是这类凶星造就了人生阅历。")
        elif ncat == "全吉平稳":
            lines.append("🏔️ 全吉平稳格局，能量稳定、少波折")
            lines.append("  🌟 适合求稳、管理、传承类人士")
            lines.append('  📝 八星实战派认为：全吉号虽好，但缺少凶星的"打磨力"。')
            lines.append("     若有绝命/五鬼在号码中段，反而更有奋斗精神。")
        elif ncat == "高开走低":
            lines.append("📉 能量趋势向下，需注意结尾凶星累积")
            lines.append("  ⚠️ 前半段好但收束不理想，建议结合使用者八字判断")
        elif tail_pat == "凶":
            lines.append("🔴 尾数收凶，建议谨慎")
            if curve in ("上升", "V型"):
                lines.append("  ⚠️ 但曲线向上，说明过程向好，尾凶影响可化解")
        else:
            lines.append("⚪ 中性格局，无明显指向，建议结合使用者八字综合判断")

        return "\n".join(lines)

    # ═══════════════════════════════════════
    # v3.0 新增：五行生克能量流动分析
    # ═══════════════════════════════════════

    def _analyze_energy_flow(self, segments: list) -> dict:
        """五行生克驱动的能量流动分析"""
        return check_energy_flow(segments)

    def _analyze_resolve_chain(self, segments: list) -> dict:
        """吉凶制化分析（乾坤国学院实战法）
        1个天医可化解1个绝命（天医在绝命后）
        生气+延年可化解祸害
        吉星在凶星后面=化解，在前=被拖累"""
        stars_chain = [s["star"] for s in segments if s["star"]]
        results = {"resolved_pairs": [], "unresolved_threats": [], "resolve_score": 50}

        # 找凶星位置
        threat_stars = {"绝命": 0, "五鬼": 0, "祸害": 0, "六煞": 0}
        
        for i, star in enumerate(stars_chain):
            if star in threat_stars:
                threat_stars[star] += 1
            
            # 凶星后面有吉星=化解判断
            if star in threat_stars:
                lookahead = stars_chain[i+1:i+4]
                for ls in lookahead:
                    if ls == "天医" and star in ("绝命", "祸害"):
                        results["resolved_pairs"].append({
                            "threat": star, "position": i,
                            "resolver": ls, "type": "天医化解"
                        })
                        results["resolve_score"] = min(100, results["resolve_score"] + 15)
                        break
                    elif ls in ("生气", "延年") and star == "祸害":
                        results["resolved_pairs"].append({
                            "threat": star, "position": i,
                            "resolver": f"{ls}", "type": "生气/延年化解"
                        })
                        results["resolve_score"] = min(100, results["resolve_score"] + 10)
                        break
                    elif ls == "生气" and star == "六煞":
                        results["resolved_pairs"].append({
                            "threat": star, "position": i,
                            "resolver": ls, "type": "生气化解"
                        })
                        results["resolve_score"] = min(100, results["resolve_score"] + 8)
                        break
                else:
                    results["unresolved_threats"].append({
                        "star": star, "position": i
                    })
                    results["resolve_score"] = max(0, results["resolve_score"] - 10)
        
        return results

    def synastry_with_bazi(self, number: str, bazi_wuxi: dict, bazi_xiji: dict) -> dict:
        """八星数字能量 × 八字五行合盘分析（v3.1 — 三维融合引擎）

        不再只是五行数量占比统计，而是三维综合评估:
        维度1: 喜用/忌神五行占比 (基础)
        维度2: 八星星性对八字的影响 (金克官杀=好, 水土混=差, 等等)
        维度3: 位置权重 (尾段收局>开头>中间)
        """
        # 边界保护: 空号码/短号
        if not number or len(number) < 2:
            return {
                "number_wuxing": {},
                "bazi_wuxi": bazi_wuxi,
                "xi_wuxing": [],
                "ji_wuxing": [],
                "xi_match": 0,
                "ji_match": 0,
                "xi_ratio": 0,
                "ji_ratio": 0,
                "base_score": 25,
                "star_effect_score": 0,
                "position_score": 0,
                "compatibility": "中性",
                "synastry_score": 25,
                "synastry_version": "v3.1三维融合引擎",
            }

        result = self.analyze_number(number)
        segments = result["segments"]

        # ── 维度1: 五行占比基础分 ──
        num_wx = {}
        for seg in segments:
            wx = seg.get("wu_xing")
            if wx:
                num_wx[wx] = num_wx.get(wx, 0) + 1

        total = sum(num_wx.values()) or 1

        xi_wuxing = bazi_xiji.get("xi", []) + bazi_xiji.get("yong", [])
        ji_wuxing = bazi_xiji.get("ji", [])

        xi_match = sum(num_wx.get(wx, 0) for wx in xi_wuxing)
        ji_match = sum(num_wx.get(wx, 0) for wx in ji_wuxing)
        xi_ratio = xi_match / total
        ji_ratio = ji_match / total

        # 基础分: 喜用占比越高越好
        base_score = round(max(0, min(100, (xi_ratio - ji_ratio + 1) * 50)))

        # ── 维度2: 八星星性效应分 ──
        star_effect_score = 0

        # 2a: 延年(金)的"制裁官杀"效应
        if "木" in ji_wuxing:
            yannian_count = sum(1 for seg in segments if seg["star"] == "延年" and seg.get("wu_xing") == "金")
            if yannian_count > 0:
                star_effect_score += yannian_count * 10

        # 2b: 天医(土)的"补土"效应
        if "土" in xi_wuxing or "土" in (bazi_xiji.get("yong", [])):
            tianyi_count = sum(1 for seg in segments if seg["star"] == "天医" and seg.get("wu_xing") == "土")
            if tianyi_count > 0:
                star_effect_score += tianyi_count * 8  # 每段天医土补用神

        # 2c: 生气(木)的"木为用神"效应
        if "木" in xi_wuxing or "木" in (bazi_xiji.get("yong", [])):
            shengqi_count = sum(1 for seg in segments if seg["star"] == "生气")
            if shengqi_count > 0:
                star_effect_score += shengqi_count * 6

        # 2d: 绝命(金)的冲击效应
        if "水" in ji_wuxing:
            jueming_count = sum(1 for seg in segments if seg["star"] == "绝命")
            jueming_gold = sum(1 for seg in segments if seg["star"] == "绝命" and seg.get("wu_xing") == "金")
            if jueming_gold > 0 and "水" in ji_wuxing:
                star_effect_score -= jueming_gold * 5
            if jueming_gold > 0 and "木" in ji_wuxing:
                star_effect_score += jueming_gold * 3

        # 2e: 六煞(水)加重水忌
        if "水" in ji_wuxing:
            liusha_count = sum(1 for seg in segments if seg["star"] == "六煞")
            if liusha_count > 0:
                star_effect_score -= liusha_count * 6

        # 2f: 五鬼(火)的效应
        wugui_count = sum(1 for seg in segments if seg["star"] == "五鬼")
        if wugui_count > 0:
            wugui_fire = sum(1 for seg in segments if seg["star"] == "五鬼" and seg.get("wu_xing") == "火")
            if wugui_fire > 0:
                if "火" in xi_wuxing:
                    star_effect_score += wugui_fire * 4
                if "火" in ji_wuxing:
                    star_effect_score -= wugui_fire * 5

        # 2g: 祸害(土)的效应
        huohai_count = sum(1 for seg in segments if seg["star"] == "祸害")
        if huohai_count > 0:
            if "土" in xi_wuxing:
                star_effect_score += huohai_count * 3
            if "土" in ji_wuxing:
                star_effect_score -= huohai_count * 4

        # ── 维度3: 位置权重 (v3.1 — 五行+星性双轴评估) ──
        position_score = 0
        for idx, seg in enumerate(segments):
            wx = seg.get("wu_xing", "")
            star = seg["star"]
            is_ji = seg["category"] == "吉"
            is_xiong = seg["category"] == "凶"

            # 位置权重: 尾段(最后2个pair)权重最高, 开头次之, 中间最低
            if idx >= len(segments) - 2:
                pos_weight = 2.0
            elif idx == 0:
                pos_weight = 1.5
            else:
                pos_weight = 1.0

            # ── 三维评分: 五行符合度 + 星性效应 + 位置 ──

            # A. 五行维度: 喜用加分, 忌神扣分
            wx_score = 0
            if wx in xi_wuxing:
                wx_score = 3
            elif wx in ji_wuxing:
                wx_score = -3
            else:
                wx_score = 0

            # B. 星性维度: 吉星加分(尤其延年/天医), 凶星扣分(尤其位置差)
            star_score = 0
            if star == "延年":
                star_score = 5  # 事业能力星, 在哪都是加分
            elif star == "天医":
                star_score = 5  # 财富星
            elif star == "生气":
                star_score = 4  # 贵人星
            elif star == "伏位":
                star_score = 2  # 中继星, 轻微正面
            elif star == "绝命" or star == "五鬼" or star == "六煞" or star == "祸害":
                star_score = -3

            # C. 星性+五行交叉: 修正项
            cross_bonus = 0
            if star == "延年" and wx == "金" and "木" in ji_wuxing:
                cross_bonus = 6  # 延年金制官杀木=额外加分
            if star == "天医" and wx == "土" and "土" in xi_wuxing:
                cross_bonus = 4  # 天医土补用神=额外加分
            if star == "绝命" and wx == "金" and "水" in ji_wuxing:
                cross_bonus = -4  # 绝命金生水忌神=额外扣分
            if star == "六煞" and wx == "水" and "水" in ji_wuxing:
                cross_bonus = -4  # 六煞水加重水忌

            # 单段总位置分
            seg_total = (wx_score + star_score + cross_bonus) * pos_weight
            position_score += seg_total

        # 尾段额外加权: 最后2个pair如果都是吉星, 额外+6
        tail_ji_stars = sum(1 for idx in range(max(0, len(segments)-2), len(segments))
                            if segments[idx]["category"] == "吉" or segments[idx]["category"] == "平")
        if tail_ji_stars >= 2:
            position_score += 5
        # 尾段全是凶星, 额外-8
        tail_xiong_stars = sum(1 for idx in range(max(0, len(segments)-2), len(segments))
                               if segments[idx]["category"] == "凶")
        if tail_xiong_stars >= 2:
            position_score -= 8

        # ── 综合得分 ──
        combined = base_score * 0.20 + star_effect_score * 0.50 + position_score * 0.30
        final_score = min(100, max(0, round(combined)))

        if final_score >= 75:
            compatibility = "强烈适配"
        elif final_score >= 60:
            compatibility = "基本适配"
        elif final_score >= 40:
            compatibility = "中性"
        elif final_score >= 25:
            compatibility = "略有不配"
        else:
            compatibility = "不匹配"

        return {
            "number_wuxing": num_wx,
            "bazi_wuxi": bazi_wuxi,
            "xi_wuxing": xi_wuxing,
            "ji_wuxing": ji_wuxing,
            "xi_match": xi_match,
            "ji_match": ji_match,
            "xi_ratio": round(xi_ratio, 2),
            "ji_ratio": round(ji_ratio, 2),
            "base_score": base_score,
            "star_effect_score": star_effect_score,
            "position_score": position_score,
            "compatibility": compatibility,
            "synastry_score": final_score,
            "synastry_version": "v3.1三维融合引擎",
        }


# ═══════════════════════════════════════════
# v3.0 综合解读函数（整合五行+制化+流动+合盘）
# ═══════════════════════════════════════════

def deep_analyze(number: str, bazi_info: dict = None) -> dict:
    """八星数字能量深度解读 v3.1 — 双轨制

    主轨: 纯八星评分（独立于八字，行业标准）
    辅轨: 八字合盘评分（需提供八字信息，增值功能）

    输出结构:
      ba_star_score    — 纯八星评分 (0-100)
      ba_star_summary  — 纯八星摘要
      [synastry]       — 八字合盘(仅当bazi_info提供时)
      [synastry_score] — 合盘评分(仅当bazi_info提供时)
      energy_flow      — 能量流通检测
      resolve_chain    — 吉凶制化分析
    """
    engine = BaStarEngine()
    base = engine.analyze_number(number)
    flow = engine._analyze_energy_flow(base["segments"])
    resolve = engine._analyze_resolve_chain(base["segments"])

    result = {
        **base,
        "energy_flow": flow,
        "resolve_chain": resolve,
        "ba_star_score": base["score"],
        "ba_star_summary": base["summary"],
    }

    if bazi_info:
        syn = engine.synastry_with_bazi(
            number, bazi_info.get("wuxi", {}), bazi_info.get("xiji", {})
        )
        result["synastry"] = syn
        result["synastry_score"] = syn["synastry_score"]

    return result


def summarize_deep(number: str, bazi_info: dict = None) -> str:
    """v3.1 八星实战派综合诊断摘要 — 双轨制"""
    result = deep_analyze(number, bazi_info)
    lines = []

    lines.append(f"【八星能量深度诊断 v3.1 — 双轨制】 — {number}")
    lines.append("")

    # ── 主轨：纯八星评分（行业通用）──
    lines.append(f"⭐ 八星主评分: {result['ba_star_score']}/100")
    lines.append("")

    # ── 辅轨：八字合盘评分（如有）──
    syn_score = result.get("synastry_score")
    if syn_score is not None:
        syn = result["synastry"]
        lines.append(f"🎯 八字合盘评分: {syn_score}/100")
        lines.append(f"   兼容度: {syn['compatibility']}")
        lines.append(f"   号码五行: {syn['number_wuxing']}")
        lines.append(f"   喜用五行: {syn['xi_wuxing']} | 忌神: {syn['ji_wuxing']}")
        lines.append("")
        lines.append(f"   ├─ 基础匹配: {syn['base_score']}分 (喜用占比{syn['xi_ratio']}, 忌神占比{syn['ji_ratio']})")
        lines.append(f"   ├─ 星性效应: {syn['star_effect_score']}分 (延年制官杀/天医补用神等)")
        lines.append(f"   └─ 位置权重: {syn['position_score']}分 (尾段收局/开头切入)")
        lines.append("")

    # ── 能量流通 ──
    flow = result["energy_flow"]
    flow_emoji = {"流通顺畅": "🟢", "基本通畅": "🟡", "流通受阻": "🟠", "严重阻塞": "🔴"}
    lines.append(f"{flow_emoji.get(flow['flow_quality'], '⚪')} 能量流通: {flow['flow_quality']} (评分{flow['flow_score']})")
    if flow["blockages"]:
        lines.append(f"   阻塞点 {len(flow['blockages'])}处:")
        for b in flow["blockages"][:3]:
            lines.append(f"      🔴 {b['from']}→{b['to']} (位置{b['position']}) = {b['flow']}")
    lines.append("")

    # ── 吉凶制化 ──
    resolve = result["resolve_chain"]
    lines.append(f"⚔️ 吉凶制化分析 (化解评分{resolve['resolve_score']})")
    if resolve["resolved_pairs"]:
        for r in resolve["resolved_pairs"]:
            lines.append(f"  ✅ {r['threat']}@位置{r['position']} → 被 {r['resolver']} 化解")
    if resolve["unresolved_threats"]:
        lines.append(f"  ⚠️ 未被化解的凶星 {len(resolve['unresolved_threats'])}处:")
        for u in resolve["unresolved_threats"]:
            lines.append(f"    🔴 {u['star']}@位置{u['position']}")
    lines.append("")

    # ── 传统分析摘要 ──
    lines.append("━━━ 八星传统分析 ━━━")
    lines.append(result["ba_star_summary"])

    return "\n".join(lines)


# ═══════════════════════════════════════════
# 亲自测试
# ═══════════════════════════════════════════

if __name__ == "__main__":
    engine = BaStarEngine()

    print("═══ 八星数字能量引擎 v2.0 ═══\n")

    test_cases = [
        ("13912345678", "普通号码"),
        ("13640254561", "多0/5案例"),
        ("18888888888", "全豹子号"),
        ("13141913141", "天医+生气+延年经典"),
        ("15612345678", "新号段测试"),
        ("18123456789", "天医+延年"),
        ("13700000001", "多0测试号"),
        ("13719442134", "A号-2134破而后立"),
        ("13316276343", "B号-五鬼延年尾"),
    ]

    for num, desc in test_cases:
        print(f"── {desc}: {num} ──")
        result = engine.analyze_number(num)
        print(f"评分: {result['score']}")
        print(result['summary'])
        print()
