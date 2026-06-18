# 归因模型深入指南

## 各模型JS/Python计算参考

### 马尔科夫链实现（Python伪代码）

```python
def markov_attribution(paths, channels):
    """paths: list of channel sequences, channels: all channel names"""
    
    # 1. 构建转移概率矩阵
    trans_matrix = build_transition_matrix(paths, channels)
    
    # 2. 计算基准转化率
    base_conversion = simulate_conversion(trans_matrix)
    
    # 3. 依次移除每个渠道，计算转化率下降
    attribution = {}
    for ch in channels:
        modified_matrix = remove_channel(trans_matrix, ch)
        removed_conversion = simulate_conversion(modified_matrix)
        removal_effect = (base_conversion - removed_conversion) / base_conversion
        attribution[ch] = removal_effect
    
    # 4. 归一化
    total = sum(attribution.values())
    return {ch: v/total for ch, v in attribution.items()}
```

## 归因误区

1. **用末次点击做所有决策** — 最普遍的致命错误
2. **归因模型一年不变** — 市场和用户行为在变化
3. **忽视离线渠道** — 如果用户在线下看到品牌，线上转化归因错误
4. **无增量测试** — 相关性≠因果关系
5. **过度优化一个渠道** — 渠道组合的协同效应 > 单一渠道最大化

## 工具集成

推荐工具链：GA4(免费) → Mixpanel/Amplitude(中) → Northbeam/Rockerbox(大)
跨渠道统一ID是归因的命脉，先解决这个再谈归因模型。
