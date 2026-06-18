#!/usr/bin/env python3
"""
河图八字排盘适配器 — 调用 bazi_calc_v2.py 的真实排盘
"""
import sys, os, json
from datetime import datetime
sys.path.insert(0, os.path.expanduser("~/.agents/skills/bazi-mingli/scripts"))

try:
    from bazi_calc_v2 import paipan_v2
    ENGINE_OK = True
except ImportError as e:
    print(f"❌ 引擎导入失败: {e}", file=sys.stderr)
    ENGINE_OK = False

def calc_bazi(year, month, day, hour=12, gender='男', liunian=None):
    """调用真实八字引擎排盘"""
    if not ENGINE_OK:
        return {"error": "引擎未加载", "engine_ok": False}
    if liunian is None:
        liunian = datetime.now().year
    
    try:
        result = paipan_v2(year, month, day, hour, gender, liunian)
        
        pillars = result.get("四柱八字", {})
        rizhu = result.get("日主分析", {})
        yongshen_data = result.get("用神喜忌", {})
        basic = result.get("基本資訊", {})
        shensha = result.get("神煞", {})
        dayun_list = result.get("大運排列", [])
        liunian_data = result.get("流年分析", {})
        
        yong_shen_text = yongshen_data.get("喜用神", yongshen_data.get("用神", "?"))
        ji_shen_text = yongshen_data.get("忌神", "?")
        
        bazi_str = f"{pillars['年柱']['干支']} {pillars['月柱']['干支']} {pillars['日柱']['干支']} {pillars['時柱']['干支']}" if '年柱' in pillars else "?"
        
        return {
            "bazi": bazi_str,
            "ri_zhu": rizhu.get("日主", "?") if isinstance(rizhu, dict) else "?",
            "ri_zhu_strength": rizhu.get("綜合判斷", "?") if isinstance(rizhu, dict) else "?",
            "score": rizhu.get("總評分", 50) if isinstance(rizhu, dict) else 50,
            "yong_shen": yong_shen_text,
            "ji_shen": ji_shen_text,
            "tiaohou": result.get("調候用神", {}),
            "shensha": {k: str(v)[:30] for k, v in (shensha or {}).items()},
            "wuxing": result.get("五行統計", {}),
            "dayun_count": len(dayun_list) if dayun_list else 0,
            "liunian": str(liunian_data)[:200] if liunian_data else "",
            "engine_ok": True
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc(), "engine_ok": False}

def calc_bazi_safe(year, month, day, hour=12, gender='男'):
    """安全版排盘——总是返回一个可用的字典"""
    result = calc_bazi(year, month, day, hour, gender)
    if result.get("engine_ok"):
        return result
    # 模拟兜底
    gan_list = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    zhi_list = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    return {
        "bazi": f"{gan_list[year%10]}{zhi_list[year%12]} ? ? ?",
        "ri_zhu": "?",
        "ri_zhu_strength": "中和",
        "score": 50,
        "yong_shen": "?",
        "ji_shen": "?",
        "engine_ok": False
    }

if __name__ == "__main__":
    year, month, day, hour = 1990, 11, 10, 10
    if len(sys.argv) >= 5:
        year, month, day, hour = map(int, sys.argv[1:5])
    gender = sys.argv[5] if len(sys.argv) >= 6 else '男'
    
    result = calc_bazi(year, month, day, hour, gender)
    if "error" not in result:
        print(f"八字: {result['bazi']}")
        print(f"日主: {result['ri_zhu']}")
        print(f"強弱: {result['ri_zhu_strength']} (评分: {result['score']})")
        print(f"用神: {result['yong_shen']}")
        print(f"忌神: {result['ji_shen']}")
    else:
        print(f"❌ {result['error']}")
