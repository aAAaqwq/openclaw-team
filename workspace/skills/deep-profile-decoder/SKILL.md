# Deep Profile Decoder — 超简历人才深度解码

> 版本：v1.0 | 分类：碳基人才猎取 | 优先级：P0
> 作者：稷下 | 对标：麦肯锡人才评估 × 字节"深层背景调查"
> 触发场景：候选人短名单确定后 / 深度接触前 / Offer设计前

---

## 核心价值

超越简历表面，深入分析目标人才的公开代码、论文、博客、演讲，解码其思维模式、技术品味与潜在诉求，为定制化接触和Offer设计提供精准依据。

---

## 解码框架：三维深度分析

### 维度一：技术思维模式

```python
def decode_technical_thinking(target):
    """
    通过代码和论文解码技术思维
    """
    analysis = {}

    # 代码风格分析
    code_samples = fetch_github_repos(target.github_handle)
    analysis['code_style'] = {
        'modularity': assess_modularity(code_samples),
        'naming_quality': assess_naming(code_samples),
        'documentation': assess_docs(code_samples),
        'testing_approach': assess_testing(code_samples),
        'architecture_taste': assess_architecture(code_samples)
    }

    # 技术选型偏好
    analysis['tech_preferences'] = {
        'paradigm': detect_paradigm(code_samples),  # OOP/FP/mixed
        'complexity_tolerance': detect_complexity(code_samples),
        'simplicity_versus_power': detect_simplicity(code_samples),
        'abstraction_level': detect_abstraction(code_samples)
    }

    # 论文/文章分析
    publications = fetch_publications(target.name)
    analysis['publications'] = {
        'depth': assess_depth(publications),
        'breadth': assess_breadth(publications),
        'novelty_style': detect_novelty_style(publications),  # 理论突破 vs 工程创新
        'collaboration_pattern': detect_collaboration(publications)
    }

    return analysis
```

### 维度二：商业洞察力

```
评估要素：
• 对用户需求的理解深度
• 对商业模式闭环的判断
• 对市场趋势的敏感度
• 对竞争格局的分析能力

评估来源：
• 演讲/访谈中的商业观点
• 博客中的行业分析
• 创业项目（如果有）的商业模式
• 对产品/市场的判断
```

### 维度三：心智成熟度

阿里"闻味道"方法论对齐：
```
• 面对挫折的反应：抱怨 vs 解决
• 面对成功的反应：自大 vs 感恩
• 面对冲突的反应：回避 vs 直面
• 面对批评的反应：防御 vs 吸收
• 面对权力诱惑的反应
```

Meta"心智成熟度"评估：
- 是否有"建设性冲突"能力
- 是否能接受不确定性
- 是否能在压力下保持判断力
- 是否有长期导向 vs 短期导向

---

## T型 → π型人才评估模型

稷下的独创模型：

```
T型人才：
  ─ 技术深度（1个领域顶尖）
  ─ 博雅贯通（多领域基础）

π型人才（稷下核心标准）：
  ═ 技术深度1（领域1顶尖）
  ═ 技术深度2（领域2顶尖）
  ─ 博雅贯通（跨领域连接）
```

```python
def assess_talent_type(target):
    deep_areas = detect_deep_expertise(target)
    breadth_score = assess_breadth(target)

    if len(deep_areas) >= 2 and breadth_score > 60:
        return "π型人才"
    elif len(deep_areas) == 1 and breadth_score > 60:
        return "T型人才"
    else:
        return "I型（深井型）"
```

---

## 输出格式

```yaml
target:
  name: "李博士"
  current_role: "字节跳动 Senior ML Engineer"
  target_position: "军团AI战略负责人"

decoding_results:

  technical_thinking:
    code_style_score: 88
    architecture_taste: "偏好简洁抽象，善于用简单方案解决复杂问题"
    paradigm: "FP为主，OO辅助"
    technical_depth: "LLM/PyTorch领域顶级"
    innovation_style: "工程创新型（非理论突破型）"

  business_insight:
    score: 76
    assessment: "对产品有敏锐直觉，能将技术与商业价值连接"
    gaps: "缺乏大规模团队管理经验"

  mental_maturity:
    score: 82
    strengths: ["直面冲突", "接受批评", "长期导向"]
    watch_outs: ["完美主义倾向", "对低效容忍度低"]

  talent_type: "π型人才"
    deep_area 1: "LLM训练与优化"
    deep area 2: "分布式系统"
    breadth: "跨AI/系统/产品三领域"

  risk_factors:
    - factor: "完美主义可能导致过度投入"
      mitigation: "设置清晰的工作边界"

contact_strategy:
  approach: "技术讨论入手，展示军团的技术挑战深度"
  first_contact_topic: "LLM推理优化系统工程问题"
  key_value_match: "超大模型分布式训练的技术使命"

offer_design_hints:
  primary_lever: "技术挑战深度（而非薪酬）"
  secondary_lever: "独立项目空间"
  watch_out: "需要明确汇报关系，避免政治摩擦"
```

---

## 华为"深层背景调查"对齐

华为的"深层背调"特点：
1. **不只听候选人说什么，而是追溯事实**
2. **找同事、上级、下级多维度了解**
3. **关注"关键时刻"的行为表现**

稷下的解码结果用于：
- 补充简历无法展示的维度
- 设计针对性面试问题
- 预测候选人可能的挑战

---

## 踩坑记录

### 坑1：数据不完整
- 问题：部分顶级人才GitHub/LinkedIn信息有限
- 解决：多源交叉验证 + 必要时通过熟人网络了解

### 坑2：推断主观性
- 问题：从公开信息推断性格可能有偏差
- 解决：将"推断"标注为"推断"而非"事实"，并提供置信度

### 坑3：过度分析
- 问题：对小人才花费过多时间分析
- 解决：设定投入上限（不超过2小时/人）

---

## 使用示例

```
用户：接触候选人张博士，需要深度解码
稷下：
1. 获取张博士GitHub/LinkedIn/论文/演讲
2. 执行deep-profile-decoder分析
3. 输出《张博士人才解码报告》
4. 稷下设计接触策略（stealth-engagement-protocol）
5. 为competitive-offer-architect提供精准依据
```