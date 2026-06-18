# 因子挖掘集群

多因子挖掘与特征工程的核心skill，负责从海量数据中发现、验证和筛选有效Alpha因子。

## 核心能力

### 多因子挖掘方法论

| 因子类型 | 典型因子 | 数据源 |
|---------|---------|--------|
| **动量** | 时序动量/截面动量/残差动量 | 价格序列 |
| **价值** | PE/PB/PS/PCF分位数 | 财务数据 |
| **质量** | ROE/毛利率/资产负债率 | 财报数据 |
| **低波** | 历史波动率/贝塔/最大回撤 | 价格序列 |
| **成长** | 营收增速/利润增速/分析师预期 | 财报+一致预期 |
| **另类** | 搜索热度/新闻情绪/链上数据 | 非传统数据源 |

### 特征工程Pipeline

```
原始数据 → 清洗 → 标准化 → 异常处理 → 衍生特征 → 筛选
```

- **标准化方法**: Z-score / Min-Max / Rank / Quantile
- **归一化**: 截面排序 / 行业中性化 / 市值中性化
- **分箱**: 等宽分箱 / 等频分箱 / 聚类分箱
- **编码**: Label Encoding / Target Encoding / WOE

### 因子IC/IR计算

- **IC（Information Coefficient）**: Spearman秩相关系数（因子值与未来收益）
- **IR（Information Ratio）**: IC均值 / IC标准差
- **分位数IC**: 按因子值分组后做多空组合收益
- **累积IC**: 滚动窗口IC累计，检验因子稳定性

### 因子共线性检测

- **VIF（Variance Inflation Factor）**: VIF > 5 警示共线性，>10 需剔除
- **相关性矩阵**: Pearson/Spearman/Kendall
- **PCA降维**: 主成分提取正交因子
- **聚类分组**: 按因子相关性聚类，各组选代表

## 与回测系统的集成

通过 `backtesting-trading-strategies` skill 进行因子策略回测：

1. 因子挖掘 → 2. 因子检验（IC/IR） → 3. 合成多因子 → 4. 策略构建 → 5. 回测验证

## 相关技能

- [backtesting-trading-strategies](../skills/backtesting-trading-strategies/) — 回测引擎
- [alpha-factor-review](../skills/quant/alpha-factor-review.md) — 因子评审
- [out-of-sample-validator](../skills/quant/out-of-sample-validator.md) — 样本外验证
