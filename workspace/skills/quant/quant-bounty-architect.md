# 量化悬赏架构师

设计和管理量化策略竞赛（赏金赛），参考Kaggle竞赛模式，驱动社区创新。

## 悬赏赛设计模板

### 标准模板

```markdown
# 悬赏赛: [标题]

## 问题背景
[描述量化交易问题，如:"预测BTC未来1小时3%以上波动"]

## 数据描述
- **训练集**: 2024-01-01 至 2024-06-30 (1分钟K线)
- **验证集**: 2024-07-01 至 2024-07-31
- **测试集**: 2024-08-01 至 2024-08-31
- **字段**: open/high/low/close/volume/vwap

## 评估指标
- 主要: Rank IC (Spearman)
- 次要: Sharpe Ratio, Max Drawdown
- 权重: IC 60% + Sharpe 30% + DD 10%

## 基线
- 简单动量策略: Rank IC = 0.015
- 随机猜测: Rank IC = 0.0

## 赏金
| 排名 | 奖励 |
|------|------|
| 🥇 第1名 | $5,000 |
| 🥈 第2名 | $2,000 |
| 🥉 第3名 | $1,000 |
| 特别奖(新因子) | $500 |

## 提交要求
- 提交格式: 预测CSV (timestamp, asset, prediction)
- 代码可选提交（加分项）
- 不允许使用未来数据
```

## 数据脱敏流程

### 加密数据安全

```
原始数据 → 脱敏处理 → 参赛数据
                ↓
        1. 时间戳偏移（随机日偏移）
        2. 价格缩放（统一除以因子）
        3. 资产名称Hash
        4. 删除敏感元数据
```

| 处理 | 方法 | 可逆性 |
|------|------|--------|
| 时间偏移 | ±random(1-7)天 | 不可逆 |
| 价格缩放 | 统一除以初始价格 | 可校准 |
| 资产Hash | SHA256(name) | 不可逆 |
| 量缩放 | 除以成交量中位数 | 不可逆 |

## 样本内/样本外分割协议

### 时间序列分割

```
训练集: [======70%======]
验证集:         [=15%=]
测试集:               [=15%=]
```

- **训练集**: 用于因子挖掘和模型训练
- **验证集**: 用于超参数调优和模型选择
- **测试集**: 最终评估，**仅使用一次**

### 滚动窗口验证

```
Fold 1: [===train===][val]
Fold 2:  [===train===][val]
Fold 3:   [===train===][val]
```

## 自动评分脚本模板

```python
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

def evaluate_ic(submission, ground_truth):
    """计算Rank IC"""
    merged = submission.merge(ground_truth, on=['timestamp', 'asset'])
    ic, p_value = spearmanr(merged['prediction'], merged['actual_return'])
    return ic

def evaluate_sharpe(submission, ground_truth):
    """计算夏普比率"""
    merged = submission.merge(ground_truth, on=['timestamp', 'asset'])
    # 假设按信号方向交易
    daily_returns = merged['prediction'].sign() * merged['actual_return']
    sharpe = daily_returns.mean() / daily_returns.std() * np.sqrt(365)
    return sharpe

def score_submission(submission_path, truth_path):
    sub = pd.read_csv(submission_path)
    truth = pd.read_csv(truth_path)
    
    ic = evaluate_ic(sub, truth)
    sharpe = evaluate_sharpe(sub, truth)
    
    total_score = 0.6 * ic/0.015 + 0.3 * min(sharpe/2, 1) + 0.1 * 1
    return {'ic': ic, 'sharpe': sharpe, 'score': total_score}
```

## 相关技能

- [alpha-factor-review](../skills/quant/alpha-factor-review.md) — 因子评审
- [out-of-sample-validator](../skills/quant/out-of-sample-validator.md) — 样本外验证
- [factor-mining-cluster](../skills/quant/factor-mining-cluster.md) — 因子挖掘
