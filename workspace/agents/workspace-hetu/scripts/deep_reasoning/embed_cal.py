#!/usr/bin/env python3
"""
将校准后的参数嵌入到 triple_cross.py 中
并自动修正 cross_validate 函数以调用 apply_calibration
"""
import sys, os, re, json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep_reasoning"))

# 本轮校准的最佳偏移参数（基于45.9%一致性数据）
# 这些参数是剩余偏差的平均补偿
CAL_PARAMS = {
    "八字": {
        "事业": 1.7, "财运": -1.15, "健康": -2.4, "婚姻": -2.55, "人际": -1.15
    },
    "紫微": {
        "事业": 2.7, "财运": 1.0, "健康": 0, "婚姻": -0.7, "人际": 0.4
    },
    "奇门": {
        "事业": 2.75, "财运": 0.95, "健康": 0, "婚姻": -3.1, "人际": 0.75
    },
}

TC_PATH = os.path.expanduser("~/.openclaw/workspace/roles/hetu/scripts/deep_reasoning/triple_cross.py")

def embed_calibration():
    with open(TC_PATH, 'r') as f:
        content = f.read()
    
    cal_block = f"""
# ============================================================
# 【校准参数】自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}
# 校准案例：20个黄金案例（企业家/政治家/科学家/文学家/运动员/演艺）
# 校准后平均一致性：45.9%
# 使用方法：calibrated_score = min(10, max(1, raw + offset))
# 当某个体系不可用时，自动跳过其校准
# ============================================================

CALIBRATION_OFFSETS = {json.dumps(CAL_PARAMS, ensure_ascii=False, indent=4)}

def apply_calibration(system_dim_scores: dict) -> dict:
    \"\"\"应用校准偏移到原始评分上\"\"\"
    calibrated = {{}}
    for sys_name, dim_scores in system_dim_scores.items():
        cal = {{}}
        offsets = CALIBRATION_OFFSETS.get(sys_name, {{}})
        for dim, raw_val in dim_scores.items():
            if isinstance(raw_val, (int, float)):
                offset = offsets.get(dim, 0)
                cal[dim] = max(1, min(10, round(raw_val + offset, 1)))
            else:
                cal[dim] = raw_val
        calibrated[sys_name] = cal
    return calibrated

"""

    # 移除旧的校准参数（如果有）
    # 查找 # 【校准参数】 到下一个 # ========= 或 # ========= 之间的内容
    if "CALIBRATION_OFFSETS" in content:
        # 移除旧校准块
        content = re.sub(
            r'\n# ============================================================\n# 【校准参数】.*?# ============================================================\n\nCALIBRATION_OFFSETS[^#]*# ============================================================',
            '\n# ============================================================',
            content,
            flags=re.DOTALL
        )
        # 再处理一遍只移除参数区块
        content = re.sub(
            r'def apply_calibration[^#]*return calibrated\n\n',
            '',
            content,
            flags=re.DOTALL
        )
    
    # 在最终交叉验证前面插入
    insert_pos = content.find("# ============================================================\n# 最终交叉验证")
    if insert_pos == -1:
        # 找最后一组注释
        insert_pos = content.rfind("# ============================================================\n")
        if insert_pos > 0:
            insert_pos = content.index("\n", insert_pos) + 1
    
    new_content = content[:insert_pos] + cal_block + "\n" + content[insert_pos:]
    
    # 修改 cross_validate 函数以在最后应用校准
    # 找到 "return {" 那一段
    # 在 cross_validate 返回之前，插入校准
    old_return = '    return {\n        "name": person_name,'
    
    # 更精确：找 return 块的开始
    pat = r'(    # 6. 综合评分[\s\S]*?    return \{[\s\S]*?\})'
    
    if re.search(pat, new_content):
        new_content = re.sub(
            pat,
            r'    # 6. 综合评分\n    overall_score = round(sum(dim_results[d]["综合评分"] for d in DIMENSION_KEYS) / len(DIMENSION_KEYS), 1)\n\n    # 7. 校准偏移（基于20个黄金案例的偏差学习）\n    _raw_scores = {}\n    for sys_name in ["八字", "紫微", "奇门"]:\n        _raw_scores[sys_name] = {}\n        for dim in DIMENSION_KEYS:\n            for si in dim_results[dim]["各体系"]:\n                if si["system"] == sys_name:\n                    _raw_scores[sys_name][dim] = si["score"]\n    \n    try:\n        _calibrated = apply_calibration(_raw_scores)\n        # 更新 dim_results 中的综合评分\n        for dim in DIMENSION_KEYS:\n            _adj_scores = []\n            for si in dim_results[dim]["各体系"]:\n                sn = si["system"]\n                cal_val = _calibrated.get(sn, {}).get(dim)\n                if cal_val is not None:\n                    _adj_scores.append({"system": sn, "score": cal_val})\n            if _adj_scores:\n                _adj_weighted = sum(\n                    s["score"] * SYSTEM_WEIGHTS.get(s["system"], {}).get(dim, 0.33)\n                    for s in _adj_scores\n                )\n                _adj_wsum = sum(\n                    SYSTEM_WEIGHTS.get(s["system"], {}).get(dim, 0.33)\n                    for s in _adj_scores\n                )\n                if _adj_wsum > 0:\n                    dim_results[dim]["综合评分"] = round(_adj_weighted / _adj_wsum, 1)\n                    dim_results[dim]["等级"] = "高" if dim_results[dim]["综合评分"] >= 7 else ("中" if dim_results[dim]["综合评分"] >= 4 else "低")\n                    dim_results[dim]["各体系"] = _adj_scores\n        overall_score = round(sum(dim_results[d]["综合评分"] for d in DIMENSION_KEYS) / len(DIMENSION_KEYS), 1)\n        # 重新计算一致性\n        _all_cons = []\n        for dim in DIMENSION_KEYS:\n            svals = [s["score"] for s in dim_results[dim]["各体系"]]\n            if len(svals) >= 2:\n                _all_cons.append(max(0, 100 - (max(svals) - min(svals)) * 20))\n        overall_consistency = round(sum(_all_cons) / len(_all_cons), 1) if _all_cons else 0\n        consistency_str = f"{overall_consistency:.0f}%"\n    except Exception:\n        pass\n\n    return {',
            new_content
        )
    
    with open(TC_PATH, 'w') as f:
        f.write(new_content)
    
    print(f"✅ 校准参数已嵌入: {TC_PATH}")
    
    # 验证语法
    try:
        compile(new_content, TC_PATH, 'exec')
        print("✅ 语法检查通过")
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")

if __name__ == "__main__":
    embed_calibration()
