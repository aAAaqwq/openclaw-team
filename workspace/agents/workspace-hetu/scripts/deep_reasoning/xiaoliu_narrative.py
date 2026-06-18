#!/usr/bin/env python3
"""
小六壬 · 三宫叙事层 v1.0
═══════════════════════════════════════════════════════════════
把掌诀组合（大安→留连→速喜）翻译成可读的"情节叙事"
让用户直接理解：开头如何，中间卡在哪，最后怎么收尾

输入格式：xiaoliu_scores.score_dimensions() 的输出
  divination 中 need：first_gong, second_gong, final_gong, trend, huo_shen

作者：河图 🐢 | v1.0 | 2026-05-05
"""

from typing import Dict

# ── 六宫基本属性 ──

GONG_TRAITS = {
    "大安": {
        "wuxing": "木",
        "persona": "像一棵老树，根深蒂固，不慌不忙",
    },
    "留连": {
        "wuxing": "土",
        "persona": "像一脚踩进泥潭，拔出来费力",
    },
    "速喜": {
        "wuxing": "火",
        "persona": "像一团火，烧得快，但也容易灭",
    },
    "赤口": {
        "wuxing": "金",
        "persona": "像一把刀，伤人伤己",
    },
    "小吉": {
        "wuxing": "水",
        "persona": "像一条溪流，绕开石头也能流向远方",
    },
    "空亡": {
        "wuxing": "土",
        "persona": "像拳头打在棉花上，使不上力",
    },
}

# ── 两宫五行生克关系叙事 ──
WUXING_RELATION_NARRATIVE = {
    ("木", "木"): "同类相聚，事情延续性很强，但可能缺乏变数。",
    ("木", "火"): "木生火 — 前期的积累开始释放能量，有推动力。",
    ("木", "土"): "木克土 — 前期的想法受到现实的制约，执行力跟不上。",
    ("木", "金"): "金克木 — 外部规则或权威压制了前期的冲劲。",
    ("木", "水"): "水生木 — 前期的努力得到滋养，有后续潜力。",
    ("火", "火"): "双火叠加，能量爆发但容易过热，需控制节奏。",
    ("火", "土"): "火生土 — 热情转化为实质成果，事态渐稳。",
    ("火", "金"): "火克金 — 热情冲破障碍但消耗大，不可持久。",
    ("火", "水"): "水克火 — 势头被浇灭，外部冷水泼来。",
    ("火", "木"): "木生火 — 有基础支撑，局势进一步走高。",
    ("土", "土"): "双土堆积，稳中偏重，节奏慢但根基扎实。",
    ("土", "金"): "土生金 — 积累开始产出，踏实出结果。",
    ("土", "水"): "土克水 — 掌控力强但缺乏流动性，情感偏克制。",
    ("土", "木"): "木克土 — 想法冲击了稳定的状态，需要调整。",
    ("土", "火"): "火生土 — 外部推动让局面成势，渐入佳境。",
    ("金", "金"): "双金对冲，锐气过剩，容易产生摩擦。",
    ("金", "水"): "金生水 — 规则转化为流动，事情开始顺畅。",
    ("金", "木"): "金克木 — 硬性条件限制了灵活空间。",
    ("金", "火"): "火克金 — 热情打破了僵硬的框架，有突破。",
    ("金", "土"): "土生金 — 稳扎稳打，积累到一定量级会出结果。",
    ("水", "水"): "双水流动，顺势而行但方向感偏弱。",
    ("水", "木"): "水生木 — 潜力的种子开始生长，有后劲。",
    ("水", "火"): "水克火 — 冷静克制了冲动，适合刹车观望。",
    ("水", "土"): "土克水 — 现实约束限制自由流动，事有阻碍。",
    ("水", "金"): "金生水 — 有规则支撑，流动但不失控。",
}

# ── 三宫情节叙事模板 ──
GONG_STORY_INTRO = {
    "大安": "开头是平稳起势的。你带着足够的底气和安全感入场，不需要太慌张。",
    "留连": "开局就不是很顺。事情一上来就拖住了，像是在原地打转，迟迟看不到进展。",
    "速喜": "开局很猛，上手就有反应。事情以一种近乎冲动的方式启动了。",
    "赤口": "开局就有摩擦。你一开口对方就应激，或是条件一开始就不对等。",
    "小吉": "开局虽然没有爆点，但也顺风顺水。水到渠成，没有太大对抗。",
    "空亡": "开局就是冷的。一上来就有种'白费劲'的信号，好像这件事本身就不该开始。",
}

GONG_STORY_END = {
    "大安": "最终结果是稳的。虽然没有惊喜，但也踏实。不亏。",
    "留连": "最后收尾还是会拖。即使表面上结束，心里也放不下，需要回来收残。",
    "速喜": "最后是速战速决的。好事坏事都来得快，但需要注意后续会不会反复。",
    "赤口": "最后难免留点不愉快。口舌之争或资源分配上的不满意，大概率会留下点痕迹。",
    "小吉": "结局是小圆满。虽然没有大获全胜，但也够用了，是体面的收场。",
    "空亡": "结局是落空的。要么是白忙一场，要么是你自己主动放弃了。止损本身也是一种赢。",
}

HUO_SHEN_NOTE = {
    "青龙": "有贵人运加持",
    "白虎": "注意冲突和压制",
    "玄武": "信息不透明，多留个心眼",
    "腾蛇": "事情可能有变，不适合惯性操作",
    "朱雀": "注意言辞，容易引起争论",
    "勾陈": "稳中偏慢，适合守成",
}


def narrate_three_gongs(result: Dict) -> Dict:
    """
    对小六壬评分引擎的输出做三宫叙事翻译
    可用作独立工具，也可集成到评分引擎输出中。

    Args:
        result: score_dimensions() 的完整输出
    """
    div = result.get("divination", {})
    gong1 = div.get("first_gong", "")
    gong2 = div.get("second_gong", "")
    gong3_raw = div.get("final_gong", "")
    if isinstance(gong3_raw, dict):
        gong3 = gong3_raw.get("name", "")
    else:
        gong3 = str(gong3_raw) if gong3_raw else ""
    gong_name = div.get("gong_name", "")
    trend = div.get("trend", "横盘")
    huo_shen = div.get("huo_shen", "")

    if not gong1 and not gong2 and not gong3:
        return {"narrative": f"最终落于{gong_name}（无三宫递推数据）", "raw_gongs": gong_name}

    t1 = GONG_TRAITS.get(gong1, {})
    t2 = GONG_TRAITS.get(gong2, {})
    t3 = GONG_TRAITS.get(gong3, {})

    # 开头
    intro = GONG_STORY_INTRO.get(gong1, f"开局落在{gong1}")

    # 初→中过渡
    trans_12 = ""
    if gong1 and gong2:
        wx1 = t1.get("wuxing", "").replace("（虚）", "").strip()
        wx2 = t2.get("wuxing", "").replace("（虚）", "").strip()
        if wx1 and wx2:
            trans_12 = WUXING_RELATION_NARRATIVE.get((wx1, wx2), "")
        p2 = t2.get("persona", f"中间阶段呈{gong2}状态")
        process_story = f"然后进入了{gong2}阶段。{p2}。" + (trans_12 if trans_12 else "")
    else:
        process_story = ""

    # 中→终过渡
    final_part = ""
    if gong2 and gong3:
        wx2 = t2.get("wuxing", "").replace("（虚）", "").strip()
        wx3 = t3.get("wuxing", "").replace("（虚）", "").strip()
        trans_23 = WUXING_RELATION_NARRATIVE.get((wx2, wx3), "") if wx2 and wx3 else ""
        end_story = GONG_STORY_END.get(gong3, f"最终收于{gong3}。")
        p3 = t3.get("persona", "")
        final_part = f"最后来到了{gong3}。{p3}。" + (trans_23 if trans_23 else "")
        if end_story:
            final_part += end_story

    # 活六神提示
    shen_note = ""
    if huo_shen:
        note = HUO_SHEN_NOTE.get(huo_shen, "")
        shen_note = f"活六神{huo_shen}临宫" + (f"，{note}。" if note else "。")

    # 总体趋势
    if trend == "上升":
        overall = "整体趋势向上。初段到末端能量在增长，这是积极的信号。宜顺势推进，但不要冒进。"
    elif trend == "下降":
        overall = "整体趋势向下。初段到末端能量在衰减，说明阻力在变大。宜谨慎行事，降低预期。"
    else:
        overall = "整体呈现横盘格局。能量没有明显的升温或降温，主要看执行。事情有可成的概率，但需要自己推一把。"

    story_parts = [intro, process_story, final_part]
    if shen_note:
        story_parts.append(shen_note)
    story_parts.append(overall)

    return {
        "narrative": "\n".join(p for p in story_parts if p),
        "gong1_story": intro,
        "gong2_story": process_story,
        "gong3_story": final_part,
        "transition_12": trans_12,
        "huo_shen_note": shen_note,
        "overall": overall,
        "raw_gongs": f"{gong1} → {gong2} → {gong3}" if gong2 else gong1,
    }


if __name__ == "__main__":
    from xiaoliu_scores import score_dimensions

    print("═══ 小六壬三宫叙事层 v1.0 测试 ═══\n")

    for case_name, args in [
        ("5月5日11时（午时）", (5, 5, 11)),
        ("5月5日15时（申时）", (5, 5, 15)),
        ("5月5日19时（戌时）", (5, 5, 19)),
        ("6月1日8时（辰时）", (6, 1, 8)),
    ]:
        r = score_dimensions(month=args[0], day=args[1], hour_24=args[2])
        div = r["divination"]
        narr = narrate_three_gongs(r)
        print(f"【{case_name}】")
        print(f"  三宫：{narr['raw_gongs']} | 趋势{div.get('trend','?')} | {div.get('gong_name')}{div.get('gong_level','')}")
        print(f"  叙事：{narr['narrative'][:150]}...")
        print()
