#!/usr/bin/env python3
"""
河图 · 盲派干支象法引擎 v1.0
═══════════════════════════════
核心方法论：
  1. "不见不象" —— 八字中显出的字才论象，藏干不直接论象
  2. "干支通变" —— 天干主外象、地支主内象、神煞加持
  3. "三合/六合/三会穿象" —— 合会联动产生新的象
  4. "穿刑破害的象" —— 冲穿刑破是"坏事"的直接表征
  5. "十神+五行+干支的复合象" —— 职业/性格/健康/六亲的具象化
"""

from typing import Dict, List, Optional, Tuple, Any
import sys, os

# 导入bazi_calc_v2的藏干数据（避免运行时依赖整个引擎）
_BAZI_PATH = os.path.expanduser("~/.agents/skills/bazi-mingli/scripts")
if _BAZI_PATH not in sys.path:
    sys.path.insert(0, _BAZI_PATH)

try:
    from bazi_calc_v2 import DIZHI_CANGGAN as _DC, DIZHI_WUXING as _DW
    DIZHI_CANGGAN = _DC
    DIZHI_WUXING = _DW
except ImportError:
    # 兜底数据
    DIZHI_CANGGAN = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
        "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
        "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
        "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
    }
    DIZHI_WUXING = ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"]

# ============================================================
# 1. 干支基本象意（盲派核心）
# ============================================================

# 天干象意（盲派精简版——看"字"说大象）
TIANGAN_BASE_IMAGE = {
    "甲": {
        "class": "阳木/大树",
        "images": ["参天大树", "栋梁", "领导", "阳刚", "成长", "首脑", "伟岸"],
        "personality": ["正直", "进取", "有担当", "好面子", "不易屈服"],
        "career": ["领导管理", "建筑", "林业", "教育", "经营"],
        "body": ["头", "胆", "神经", "筋脉"],
        "gods": "甲为青龙，主官贵、文书、权威",
    },
    "乙": {
        "class": "阴木/花草",
        "images": ["藤蔓", "花草", "柔软", "曲折", "机遇", "依附", "柔韧"],
        "personality": ["柔韧", "变通", "善交际", "易依赖", "敏感"],
        "career": ["艺术", "设计", "咨询", "中介", "教育"],
        "body": ["头发", "颈椎", "肩", "四肢"],
        "gods": "乙为朱雀，主文采、口舌、迁移",
    },
    "丙": {
        "class": "阳火/太阳",
        "images": ["太阳", "光明", "热情", "威严", "慷慨", "权力"],
        "personality": ["热情开朗", "大方", "急躁", "霸气", "爱面子"],
        "career": ["政治", "演艺", "餐饮", "能源", "时尚"],
        "body": ["眼", "心脏", "血液循环", "小肠"],
        "gods": "丙为朱雀，主权柄、文明、传媒",
    },
    "丁": {
        "class": "阴火/灯烛",
        "images": ["星火", "灯烛", "文明", "巧妙", "细腻", "持久", "神秘"],
        "personality": ["细腻", "文静", "执着", "内敛", "多思"],
        "career": ["文学", "科技", "研究", "香料", "文化"],
        "body": ["眼", "心脏", "血液", "神经末梢"],
        "gods": "丁为朱雀，主灵性、文昌、智慧",
    },
    "戊": {
        "class": "阳土/高岗",
        "images": ["高山", "城墙", "雄伟", "厚重", "信用", "稳定", "固执"],
        "personality": ["稳重", "诚信", "固执", "保守", "包容"],
        "career": ["建筑", "土建", "地产", "仓储", "金融"],
        "body": ["胃", "皮肤", "肌肉", "鼻"],
        "gods": "戊为勾陈，主财禄、稳定、忠诚",
    },
    "己": {
        "class": "阴土/田园",
        "images": ["田地", "平原", "柔顺", "谦卑", "农耕", "滋养"],
        "personality": ["谦虚", "包容", "内向", "务实", "柔和"],
        "career": ["农业", "教育", "服务", "设计", "营养"],
        "body": ["脾", "腹部", "肌肉", "唇"],
        "gods": "己为螣蛇，主口舌、虚惊、变动",
    },
    "庚": {
        "class": "阳金/刀剑",
        "images": ["刀剑", "金属", "变革", "刚毅", "决断", "肃杀"],
        "personality": ["刚强", "果断", "有魄力", "易伤人", "直率"],
        "career": ["军事", "制造", "五金", "外科", "法务"],
        "body": ["骨骼", "肺", "大肠", "牙齿"],
        "gods": "庚为白虎，主权柄、肃杀、手术",
    },
    "辛": {
        "class": "阴金/珠玉",
        "images": ["珠宝", "金银", "精致", "贵重", "锋利", "细腻"],
        "personality": ["精致", "秀气", "挑剔", "完美主义", "易脆"],
        "career": ["珠宝", "金融", "会计", "法律", "医疗"],
        "body": ["肺", "支气管", "牙齿", "骨骼"],
        "gods": "辛为白虎，主精细、变革、血光",
    },
    "壬": {
        "class": "阳水/江河",
        "images": ["江河", "大海", "流畅", "多变", "智慧", "远行"],
        "personality": ["豁达", "智慧", "多变", "不羁", "自由"],
        "career": ["水利", "航运", "贸易", "文化", "IT"],
        "body": ["肾", "膀胱", "血液", "淋巴"],
        "gods": "壬为玄武，主智慧、隐秘、远行",
    },
    "癸": {
        "class": "阴水/雨露",
        "images": ["雨露", "云雾", "雨水", "渗透", "细致", "滋润", "暗流"],
        "personality": ["细腻", "敏感", "直觉", "含蓄", "有计划"],
        "career": ["科研", "心理", "玄学", "药剂", "文学"],
        "body": ["肾", "精血", "内分泌", "耳"],
        "gods": "癸为玄武，主灵感、玄学、隐秘",
    },
}

# 地支象意（盲派——地支是"窝"，看窝藏什么东西）
DIZHI_BASE_IMAGE = {
    "子": {
        "class": "水/阳",
        "images": ["水池", "沟渠", "暗流", "深邃", "玄秘", "夜晚"],
        "personality": ["聪明", "外柔内刚", "善谋划", "隐秘"],
        "career": ["水利", "物流", "文化", "玄学", "娱乐"],
        "body": ["肾", "耳", "生殖", "泌尿"],
        "生肖": "鼠",
        "gods": "子为华盖星，主智慧、孤独、玄学",
    },
    "丑": {
        "class": "土/阴",
        "images": ["泥泞", "牛", "耕地", "仓库", "粪土", "基础"],
        "personality": ["坚韧", "保守", "踏实", "固执"],
        "career": ["农业", "矿业", "仓储", "建筑工程"],
        "body": ["脾", "腹", "肌肉"],
        "生肖": "牛",
        "gods": "丑为天乙贵人, 主观贵、提携、保险",
    },
    "寅": {
        "class": "木/阳",
        "images": ["虎", "山林", "权力", "威严", "开端", "创新"],
        "personality": ["勇敢", "创新", "好斗", "自信", "爱冒险"],
        "career": ["管理", "军警", "创业", "运动", "冒险"],
        "body": ["头部", "肝", "胆", "筋骨"],
        "生肖": "虎",
        "gods": "寅为功曹，主权贵、公门、诉讼",
    },
    "卯": {
        "class": "木/阴",
        "images": ["兔", "花", "门户", "木器", "桃花", "桥梁"],
        "personality": ["温和", "灵巧", "桃花旺", "善交际", "优柔"],
        "career": ["艺术", "设计", "公关", "婚介", "中介"],
        "body": ["肝", "目", "四肢"],
        "生肖": "兔",
        "gods": "卯为太冲，主门户、车辆、迁移、桃花",
    },
    "辰": {
        "class": "土/阳",
        "images": ["龙", "水库", "湿地", "堤坝", "变幻", "文明"],
        "personality": ["博大", "善变", "有理想", "好大喜功"],
        "career": ["文化", "教育", "水利", "政府", "地产"],
        "body": ["胃", "脾", "肩", "皮肤"],
        "生肖": "龙",
        "gods": "辰为天罡，主权贵、杀伐、官非",
    },
    "巳": {
        "class": "火/阴",
        "images": ["蛇", "火炉", "冶炼", "变化", "文采", "电器"],
        "personality": ["多变", "机敏", "有谋略", "善言辞"],
        "career": ["冶金", "电力", "文化", "科技", "安全"],
        "body": ["心", "咽喉", "面", "牙齿"],
        "生肖": "蛇",
        "gods": "巳为太乙，主文书、火灾、惊恐",
    },
    "午": {
        "class": "火/阳",
        "images": ["马", "太阳", "火光", "权力", "文明", "宴会"],
        "personality": ["热情", "奔放", "爱社交", "冲动", "不拘小节"],
        "career": ["文化", "传媒", "餐饮", "娱乐", "体育"],
        "body": ["心", "眼", "小肠", "血液"],
        "生肖": "马",
        "gods": "午为胜光，主权贵、文书、诉讼、迁移",
    },
    "未": {
        "class": "土/阴",
        "images": ["羊", "花园", "木库", "酒窖", "营养", "调味"],
        "personality": ["温和", "艺术感", "依赖", "情绪化"],
        "career": ["艺术", "餐饮", "农业", "旅游", "服务"],
        "body": ["脾", "胃", "口唇", "皮肤"],
        "生肖": "羊",
        "gods": "未为小吉，主酒食、祭祀、医药、喜事",
    },
    "申": {
        "class": "金/阳",
        "images": ["猴", "刀剑", "道路", "通信", "运输", "运动"],
        "personality": ["聪明", "灵活", "善变", "好动", "好奇"],
        "career": ["通信", "交通", "科技", "金融", "体育"],
        "body": ["骨骼", "肺", "大肠", "牙齿"],
        "生肖": "猴",
        "gods": "申为传送，主道路、迁移、行商、传信",
    },
    "酉": {
        "class": "金/阴",
        "images": ["鸡", "金银", "酒器", "精美", "乐器", "律令"],
        "personality": ["精致", "完美", "犀利", "善言", "见多识广"],
        "career": ["金融", "律法", "音乐", "珠宝", "仪表"],
        "body": ["肺", "口腔", "骨骼", "皮肤"],
        "生肖": "鸡",
        "gods": "酉为从魁，主酒食、才艺、尼僧、诉讼",
    },
    "戌": {
        "class": "土/阳",
        "images": ["狗", "火库", "城郭", "监狱", "庙宇", "文教"],
        "personality": ["忠诚", "正直", "稳重", "固执", "严谨"],
        "career": ["法律", "安保", "宗教", "教育", "建筑"],
        "body": ["胃", "心包", "膝", "命门"],
        "生肖": "狗",
        "gods": "戌为河魁，主狱讼、欺诈、印信、医药",
    },
    "亥": {
        "class": "水/阴",
        "images": ["猪", "江河", "大海", "深邃", "隐秘", "暗伏"],
        "personality": ["深沉", "包容", "善谋", "心软", "好色"],
        "career": ["水利", "物流", "金融", "慈善", "文化"],
        "body": ["肾", "血液", "生殖", "内分泌"],
        "生肖": "猪",
        "gods": "亥为登明，主暗昧、隐私、玄学、鬼神",
    },
}

# 盲派特有的"象"组合规则
#
# 1. 天干透出 + 地支本气 = "显象"
#    例：甲透+寅支 → "大树入山林" = 力量大、根基稳
#
# 2. 三合局（申子辰/亥卯未/寅午戌/巳酉丑）→ "化象"
#    例：申子辰合水 → "江河入海"象
#
# 3. 六合（子丑/寅亥/卯戌/辰酉/巳申/午未）→ "穿象"
#    例：寅亥合 → "虎落猪圈"/"豬入山林" — 互相借力
#
# 4. 三会（寅卯辰/巳午未/申酉戌/亥子丑）→ "会象" → 量变质变
#
# 5. 六冲（子午/丑未/寅申/卯酉/辰戌/巳亥）→ "冲象" → 变动/冲突/分散
#
# 6. 六穿（子未/丑午/寅巳/卯辰/申亥/酉戌）→ "穿象" → 暗伤/慢性矛盾
#
# 7. 六破（子酉/寅亥/辰丑/午卯/申巳/戌未）→ "破象" → 损耗/失常
#
# 8. 三刑（寅巳申/丑未戌/子卯/辰午酉亥自刑）→ "刑象" → 纠纷/受伤


def get_tiangan_image(gan: str) -> Dict:
    """获取天干象意"""
    return TIANGAN_BASE_IMAGE.get(gan, {"images": ["未知"], "personality": [""], "career": [""], "body": [""]})


def get_dizhi_image(zhi: str) -> Dict:
    """获取地支象意"""
    return DIZHI_BASE_IMAGE.get(zhi, {"images": ["未知"], "personality": [""], "career": [""], "body": [""], "gods": ""})


# ============================================================
# 2. 合冲刑害破 关系映射
# ============================================================

DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 六合
LIUHE = {  # 合化五行
    ("子","丑"): "土", ("丑","子"): "土",
    ("寅","亥"): "木", ("亥","寅"): "木",
    ("卯","戌"): "火", ("戌","卯"): "火",
    ("辰","酉"): "金", ("酉","辰"): "金",
    ("巳","申"): "水", ("申","巳"): "水",
    ("午","未"): "土", ("未","午"): "土",
}

LIUHE_IMAGE = {
    ("子","丑"): "寒冰入泥·暗合—幕后交易/暗中合作",
    ("寅","亥"): "虎落猪圈·志合—欲加之罪/被立约拖累",
    ("卯","戌"): "兔犬相合·淫合—桃花/暧昧/不正当关系",
    ("辰","酉"): "龙凤呈祥·正合—天作之合/合法契约",
    ("巳","申"): "蛇猴结盟·正合—智谋合作/互利双赢",
    ("午","未"): "马羊聚义·正合—忠诚信义/团队合作",
}

# 三合
SANHE = {
    ("申","子","辰"): "水局",
    ("亥","卯","未"): "木局",
    ("寅","午","戌"): "火局",
    ("巳","酉","丑"): "金局",
}

SANHE_IMAGE = {
    "水局": "江海汇流·大智若愚·流动性强",
    "木局": "森林参天·成长旺盛·扩散性",
    "火局": "炉火冲天·气势磅礴·影响力",
    "金局": "刀剑铸成·锋利决断·杀伐果断",
}

# 三会
SANHUI = {
    ("寅","卯","辰"): ("木", "春意盎然·百花齐放"),
    ("巳","午","未"): ("火", "炎炎夏日·气势冲天"),
    ("申","酉","戌"): ("金", "秋收肃杀·收获果实"),
    ("亥","子","丑"): ("水", "寒冬凛冽·潜藏积蓄"),
}

# 六冲
LIUCHONG = {
    ("子","午"): "正冲·水火不容·方向相反",
    ("午","子"): "正冲·水火不容·方向相反",
    ("丑","未"): "冲·土崩瓦解·同质冲突",
    ("未","丑"): "冲·土崩瓦解·同质冲突",
    ("寅","申"): "冲·动态冲突·道路相悖",
    ("申","寅"): "冲·动态冲突·道路相悖",
    ("卯","酉"): "冲·门户之争·正邪对立",
    ("酉","卯"): "冲·门户之争·正邪对立",
    ("辰","戌"): "冲·库门开启·新旧交替",
    ("戌","辰"): "冲·库门开启·新旧交替",
    ("巳","亥"): "冲·暗涌撞击·真假混淆",
    ("亥","巳"): "冲·暗涌撞击·真假混淆",
}

# 六穿（六害）
LIUCHUAN = {
    ("子","未"): "穿·鼠羊相害—暗合异心",
    ("未","子"): "穿·鼠羊相害—暗合异心",
    ("丑","午"): "穿·牛马相害—互不欣赏",
    ("午","丑"): "穿·牛马相害—互不欣赏",
    ("寅","巳"): "穿·虎蛇相害—金火相战",
    ("巳","寅"): "穿·虎蛇相害—金火相战",
    ("卯","辰"): "穿·兔龙相害—阴木破阳土",
    ("辰","卯"): "穿·兔龙相害—阴木破阳土",
    ("申","亥"): "穿·猴猪相害—金生水泄",
    ("亥","申"): "穿·猴猪相害—金生水泄",
    ("酉","戌"): "穿·鸡狗相害—口舌之争",
    ("戌","酉"): "穿·鸡狗相害—口舌之争",
}

# 六破
LIUPO = {
    ("子","酉"): "破·鼠鸡相破·自泄",
    ("酉","子"): "破·鼠鸡相破·自泄",
    ("寅","亥"): "破·虎猪相破·合中带破",
    ("亥","寅"): "破·虎猪相破·合中带破",
    ("辰","丑"): "破·龙牛相破·破库",
    ("丑","辰"): "破·龙牛相破·破库",
    ("午","卯"): "破·马兔相破·破败",
    ("卯","午"): "破·马兔相破·破败",
    ("申","巳"): "破·猴蛇相破·合中带破",
    ("巳","申"): "破·猴蛇相破·合中带破",
    ("戌","未"): "破·狗羊相破·破库",
    ("未","戌"): "破·狗羊相破·破库",
}

# 三刑
SANXING = {
    "寅巳申": "无恩之刑—寅刑巳、巳刑申、申刑寅—忘恩负义、官非",
    "丑未戌": "恃势之刑—丑刑未、未刑戌、戌刑丑—恃强凌弱",
    "子卯": "无礼之刑—子刑卯、卯刑子—风流无德",
    "自刑": "辰/午/酉/亥自刑—自我攻击、抑郁",
}


def analyze_penetration(pillars: Dict[str, str]) -> Dict:
    """
    盲派:"透干为显象，藏支为伏象"
    检查每个天干是否在地支中有"本气根"或"余气根"。
    
    Args:
        pillars: {"year": "甲子", "month": "丙寅", "day": "庚午", "hour": "壬午"}
    
    Returns:
        透干分析
    """
    gan_list = [p[0] for p in pillars.values()]
    zhi_list = [p[1] for p in pillars.values()]
    
    result = {}
    for i, (gan, zhi, position) in enumerate(zip(gan_list, zhi_list, ["年", "月", "日", "时"])):
        tiangan = TIANGAN_BASE_IMAGE.get(gan, {})
        dizhi = DIZHI_BASE_IMAGE.get(zhi, {})
        
        # 找到在藏干中的位置
        hidden = DIZHI_CANGGAN.get(zhi, [])
        is_root = gan in hidden
        is_strong_root = False
        if is_root:
            # 检查是否为本气
            if hidden and hidden[0] == gan:
                is_strong_root = True
        
        result[f"{position}柱"] = {
            "天干": gan,
            "地支": zhi,
            "天干象": tiangan.get("images", [])[:3],
            "地支象": dizhi.get("images", [])[:3],
            "藏干": hidden,
            "是否透干": is_root,
            "是否本气根": is_strong_root,
            "根气强度": "强根" if is_strong_root else ("弱根" if is_root else "无根"),
        }
    return result


def analyze_relationships(zhi_list_str: str) -> List[str]:
    """
    分析地支之间的合冲刑害破关系
    
    Args:
        zhi_list_str: "子午卯申" 四个地支
    
    Returns:
        关系解读列表
    """
    # 将字符串转换成地支列表
    # 注意：地支是单个汉字，所以直接拆
    zhis = list(zhi_list_str)
    if len(zhis) < 2:
        return []
    
    results = []
    
    # 三合局
    for combo, image in SANHE.items():
        if all(zh in zhis for zh in combo):
            results.append(f"🌀 三合{image}：{SANHE_IMAGE[image]}")
    
    # 三会局
    for combo, (wx, desc) in SANHUI.items():
        if all(zh in zhis for zh in combo):
            results.append(f"🌿 三会{combo}：{desc}")
    
    # 六冲（一对对看）
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            key = (zhis[i], zhis[j])
            if key in LIUCHONG:
                results.append(f"⚡ 六冲{zhis[i]}{zhis[j]}：{LIUCHONG[key]}")
    
    # 六合
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            key = (zhis[i], zhis[j])
            if key in LIUHE:
                wx = LIUHE[key]
                img = LIUHE_IMAGE.get(key, f"{zhis[i]}{zhis[j]}合化{wx}")
                results.append(f"🔗 六合{zhis[i]}{zhis[j]}：{img} (合化{wx})")
    
    # 六穿
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            key = (zhis[i], zhis[j])
            if key in LIUCHUAN:
                results.append(f"💢 六穿{zhis[i]}{zhis[j]}：{LIUCHUAN[key]}")
    
    # 六破
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            key = (zhis[i], zhis[j])
            if key in LIUPO:
                results.append(f"💔 六破{zhis[i]}{zhis[j]}：{LIUPO[key]}")
    
    # 三刑
    # zi_set过滤掉可能带拼音的字符，只保留纯地支
    zhi_set = ''.join([c for c in zhis if c in "子丑寅卯辰巳午未申酉戌亥"])
    for combo, desc in SANXING.items():
        if combo == "自刑":
            for z in zhis:
                if z in "辰午酉亥" and zhi_set.count(z) >= 2:
                    results.append(f"🔥 {z}自刑：{desc}")
        else:
            if all(c in zhi_set for c in combo):
                results.append(f"🔥 三刑{combo}：{desc}")
    
    return results


def blind_school_profiling(bazi: str, 
                           ri_zhu: str, 
                           yong_shen: str,
                           ji_shen: str,
                           pillars_dict: Dict[str, str],
                           shensha: Dict[str, str]) -> Dict:
    """
    盲派简判法 — 基于干支象意和十神定位
    Args:
        bazi: "庚午 丁亥 己卯 己巳"
        ri_zhu: "己"
        yong_shen: 用神文本
        ji_shen: 忌神文本
        pillars_dict: 四柱字典
        shensha: 神煞字典
    Returns:
        Dict: 盲派解析
    """
    gans = [p[0] for p in pillars_dict.values()]
    zhis = [p[1] for p in pillars_dict.values()]
    
    # 1. 日主象
    ri_image = TIANGAN_BASE_IMAGE.get(ri_zhu, {})
    ri_ele = "己土"
    rizhu_images = ri_image.get("images", [])
    rizhu_careers = ri_image.get("career", [])
    
    # 2. 每个天干的象
    gan_images = []
    for i, (gan, pos) in enumerate(zip(gans, ["年", "月", "日", "时"])):
        img_data = TIANGAN_BASE_IMAGE.get(gan, {})
        gan_images.append(f"{pos}干{gan}: {', '.join(img_data.get('images', ['?'])[:3])}")
    
    # 3. 每个地支的象
    zhi_images = []
    for i, (zhi, pos) in enumerate(zip(zhis, ["年", "月", "日", "时"])):
        img_data = DIZHI_BASE_IMAGE.get(zhi, {})
        zhi_images.append(f"{pos}支{zhi}: {', '.join(img_data.get('images', ['?'])[:3])}")
    
    # 4. 关系分析
    relationships = analyze_relationships(''.join(zhis))
    
    # 5. 透干分析
    penetration = generate_penetration_text(pillars_dict)
    
    # 6. 十神分析（简版，从bazi字符串提取）
    # 日主五行
    # 7. 整体论断
    # 基于日主强弱和用神忌神给出盲派形象的职业/性格/运势判断
    conclusions = _generate_blind_conclusions(ri_zhu, rizhu_images, rizhu_careers, 
                                              yong_shen, ji_shen, relationships)
    
    return {
        "日主象": f"{ri_zhu}为{ri_ele}，{', '.join(rizhu_images[:4])}",
        "天干象": gan_images,
        "地支象": zhi_images,
        "关系分析": relationships,
        "透干分析": penetration,
        "整体论断": conclusions,
    }


def generate_penetration_text(pillars_dict: Dict[str, str]) -> List[str]:
    """简化透干分析文本"""
    
    results = []
    for pos, gan_zhi in pillars_dict.items():
        if len(gan_zhi) < 2:
            continue
        gan = gan_zhi[0]
        zhi = gan_zhi[1]
        hidden = DIZHI_CANGGAN.get(zhi, [])
        is_root = gan in hidden
        strong = is_root and hidden and hidden[0] == gan
        root_desc = "【强根·本气】" if strong else ("【弱根·余气】" if is_root else "【无根·虚浮】")
        hidden_str = ' '.join(hidden)
        results.append(f"{pos}: {gan}坐{zhi}(藏{hidden_str}) {root_desc}")
    return results


def _generate_blind_conclusions(ri_zhu: str, 
                                  ri_images: List[str],
                                  ri_careers: List[str],
                                  yong_shen: str,
                                  ji_shen: str,
                                  relationships: List[str]) -> Dict:
    """基于盲派象意生成整体论断"""
    # 性格判断（基于日主）
    ri_god = TIANGAN_BASE_IMAGE.get(ri_zhu, {})
    personality = ri_god.get("personality", [])
    career_hints = ri_god.get("career", [])
    
    # 看是否有六冲或三刑（影响性格）
    has_chong = any("六冲" in r for r in relationships)
    has_xing = any("三刑" in r for r in relationships)
    has_chuan = any("六穿" in r for r in relationships)
    
    personality_modifiers = []
    if has_chong:
        personality_modifiers.append("生涯多变动，性格中带有冲突张力")
    if has_xing:
        personality_modifiers.append("内心常有纠结，易自我攻击")
    if has_chuan:
        personality_modifiers.append("人际关系中有暗伤或慢性困扰")
    
    return {
        "性格特征": personality[:4],
        "性格修饰": personality_modifiers,
        "职业倾向": career_hints[:3],
        "用神形象": f"喜用{ji_shen}能量的人物/事物更助运势" if ji_shen else "",
        "整体评价": f"{ri_zhu}日主，{', '.join(personality[:3])}。{personality_modifiers[0] if personality_modifiers else ''}",
    }


# ============================================================
# 简化调用接口
# ============================================================

def blind_school_analyze(bazi_str: str, ri_zhu: str, yong_shen: str, ji_shen: str,
                          pillars: Dict[str, str], shensha: Dict[str, str]) -> str:
    """
    将盲派分析结果输出为结构化的中文报告
    
    Args:
        bazi_str: "庚午 丁亥 己卯 己巳"
        ri_zhu: "己"  
        yong_shen: "火"
        ji_shen: "水"
        pillars: {"年柱": "庚午", ...}
        shensha: {"年柱": "天乙贵人", ...}
    
    Returns:
        可读性好的文本报告
    """
    result = blind_school_profiling(bazi_str, ri_zhu, yong_shen, ji_shen, pillars, shensha)
    
    lines = ["── 盲派象法解析 ──", ""]
    
    lines.append(f"【日主】{result['日主象']}")
    lines.append("")
    
    lines.append("【四柱象意】")
    for g in result["天干象"]:
        lines.append(f"  {g}")
    for z in result["地支象"]:
        lines.append(f"  {z}")
    
    if result["透干分析"]:
        lines.append("")
        lines.append("【根气分析】")
        for p in result["透干分析"]:
            lines.append(f"  {p}")
    
    if result["关系分析"]:
        lines.append("")
        lines.append("【地支关系】")
        for r in result["关系分析"]:
            lines.append(f"  {r}")
    
    lines.append("")
    lines.append("【整体论断】")
    concl = result["整体论断"]
    lines.append(f"  · 性格：{', '.join(concl['性格特征'])}")
    if concl["性格修饰"]:
        for m in concl["性格修饰"]:
            lines.append(f"  · 注意：{m}")
    lines.append(f"  · 职业倾向：{', '.join(concl['职业倾向'])}")
    lines.append(f"  · {concl['整体评价']}")
    
    lines.append("")
    lines.append("【盲派简评】")
    lines.append(f"  {ri_zhu}日主，看其四柱字字皆象，")
    lines.append(f"  盲派重字不重理——日主身上所坐、千支所透、合冲所显，皆是此人命运之象。")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试创始人八字
    test_bazi = "庚午 丁亥 己卯 己巳"
    pillars = {"年柱": "庚午", "月柱": "丁亥", "日柱": "己卯", "时柱": "己巳"}
    shensha = {"年柱": "将星", "月柱": "天乙贵人", "日柱": "文昌贵人"}
    
    print(blind_school_analyze(test_bazi, "己", "火", "水", pillars, shensha))
