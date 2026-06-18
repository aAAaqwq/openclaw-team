# Knowledge Graph Curator — 外脑知识图谱构建与沉淀

> 版本：v1.0 | 分类：文化与组织运营 | 优先级：P1
> 作者：稷下 | 对标：Notion + Roam Research × Zettelkasten × 麦肯锡知识管理
> 触发场景：活动后24小时 / 项目复盘后 / 重要洞察产生时 / 定期知识梳理

---

## 核心价值

将俱乐部沙龙、项目复盘、外部情报等产生的认知成果，结构化沉淀到军团的"外脑知识图谱"中，供全员检索、复用、迭代，让军团的智慧持续积累而非流失。

---

## 知识管理最佳实践

### Zettelkasten（卢曼卡片盒）

尼尔斯·卢曼的卡片盒方法：
- 每条知识是一个独立的"卡片"
- 卡片之间通过链接形成网络
- 知识的价值在于链接，而非存储

稷下对齐：每条认知成果（Insight）必须包含"链接到其他知识"的连接，形成知识网络。

### 麦肯锡知识管理

麦肯锡的知识沉淀原则：
- 每次项目结束必须沉淀"经验教训"
- 知识库可供所有顾问检索
- 知识贡献是晋升考核的一部分

稷下对齐：每次活动/项目后，知识沉淀是强制流程。

---

## 知识图谱架构

```python
KNOWLEDGE_GRAPH = {
    "nodes": {
        "insight": "独立洞察（最小单元）",
        "person": "人物（碳基/硅基）",
        "project": "项目/任务",
        "event": "事件/活动",
        "concept": "概念/方法论"
    },
    "edges": {
        "relates_to": "相关洞察",
        "contributed_by": "贡献者",
        "applied_in": "应用场景",
        "derived_from": "来源",
        "supersedes": "替代旧知识"
    }
}
```

### 节点定义

| 节点类型 | 说明 | 示例 |
|---------|------|------|
| insight | 最小知识单元 | "顶级人才吸引的核心是使命，而非薪酬" |
| person | 人物档案 | 张博士、李总监 |
| project | 项目档案 | "烛龙量化2.0" |
| event | 活动档案 | "反共识沙龙#3" |
| concept | 概念定义 | "π型人才"、"蓝血文化" |

### 边关系定义

```python
RELATIONSHIP_TYPES = {
    "insight_to_insight": [
        "supports",      # A支持B
        "contradicts",   # A反对B
        "refines",       # A细化B
        "supersedes"     # A替代B
    ],
    "insight_to_person": [
        "authored",      # 某人创建
        "verified_by",   # 某人验证
        "applied_by"     # 某人应用
    ],
    "insight_to_project": [
        "applied_in",    # 在某项目应用
        "learned_from"   # 从某项目学到
    ]
}
```

---

## 知识沉淀流程

### 触发场景1：活动后24小时

```
反共识沙龙 / 失败复盘会 / 黑客松结束后
    ↓
稷下提取认知成果
    ├── 核心洞察（每条50字以内）
    ├── 关键引用（嘉宾/会员的原话）
    ├── 可执行建议（如果有）
    └── 无知区域（本次活动发现的新问题）
    ↓
创建insight节点 + 建立关系边
    ↓
同步到知识图谱
    ↓
通知相关Agent/会员（如果有关联）
```

### 触发场景2：项目复盘后

```
项目结束 → 天枢发起复盘 → 稷下协助沉淀
    ↓
提取：
    - 成功因素（为什么成功）
    - 失败教训（哪里做错）
    - 可复用方法（下次可用）
    - 认知盲区（我们不知道的）
    ↓
创建节点 + 建立项目关联
```

### 触发场景3：人才接触沉淀

```
每次与候选人接触后（无论成功与否）
    ↓
沉淀：
    - 候选人的关键洞察
    - 对军团有价值的信息
    - 接触学到的市场动态
    ↓
更新person节点 + 创建insight节点
```

---

## 输出格式

```yaml
insight_id: "INS-2026-0503-001"
content: "顶级人才的吸引，核心是'使命共鸣'而非'薪酬竞争'。候选人更看重'这件事是否有意义'。"
type: "recruiting_wisdom"
confidence: 0.88

source:
  type: "conversation"
  event_id: "沙龙#3"
  date: "2026-05-03"
  contributors: ["张博士", "李总监"]

relations:
  supports: ["INS-2026-0420-003"]  # 相关洞察
  related_people: ["张博士"]
  applied_in_projects: ["人才战略优化"]

tags:
  - talent_attraction
  - mission_driven
  - recruiting_wisdom

retrieval_hint: "想吸引顶级人才？先展示使命，而非薪酬"

next_review: "2026-08-03"  # 3个月后复看
```

---

## 检索接口

```python
def retrieve_knowledge(query, filters=None):
    """
    知识检索入口

    用法示例：
    retrieve_knowledge("人才吸引")
    retrieve_knowledge("量化", filters={"type": "insight", "min_confidence": 0.8})
    retrieve_knowledge("张博士相关洞察")
    """
    # 实现：基于关键词 + 向量相似度检索
    return ranked_results
```

### 检索结果示例

```
用户问：如何吸引量化领域的顶级人才？
稷下 → 知识图谱检索 → 返回：

相关洞察：
1. [INS-2026-0503-001] 顶级人才吸引核心是使命共鸣（置信度88%）
2. [INS-2026-0415-002] 量化人才更看重技术挑战深度（置信度82%）
3. [INS-2026-0401-008] Offer Package中AI副官是差异化价值（置信度91%）

相关人物：
- 张博士（量化专家，曾参与沙龙#2）

相关项目：
- 烛龙量化2.0（正在招聘量化PM）
```

---

## 踩坑记录

### 坑1：知识碎片化
- 问题：沉淀的知识太零散，无法形成系统
- 解决：每个insight必须包含"retrieval_hint"（用一句话能检索到）

### 坑2：沉淀延迟
- 问题：活动结束后没有及时沉淀，渐渐遗忘
- 解决：强制24小时沉淀流程，未完成则影响活动评分

### 坑3：检索效果差
- 问题：知识沉淀了，但检索不到
- 解决：每条insight必须有3个以上的标签，且有retrieval_hint

---

## 使用示例

```
用户：反共识沙龙#3结束，稷下进行知识沉淀
稷下：
1. 提取5条核心洞察
2. 记录3个关键引用
3. 提取2个可执行建议
4. 识别2个"无知区域"
5. 创建insight节点，建立关系边
6. 更新参与者person节点
7. 同步到知识图谱
8. 向相关Agent推送（如果有应用场景）
```