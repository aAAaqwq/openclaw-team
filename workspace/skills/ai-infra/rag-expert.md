# RAG专家

检索增强生成（Retrieval-Augmented Generation）全栈实践。

## Chunking策略

### 主要策略对比
| 策略 | 方法 | 适合 | 缺点 |
|------|------|------|------|
| 固定大小 | 按字符/Token分割 | 通用文本 | 切断语义边界 |
| 语义分块 | LLM识别自然段落 | 文档/文章 | 成本高、延迟大 |
| 递归分割 | RecursiveCharacterTextSplitter | 代码/结构化文本 | 配置参数敏感 |
| 句级分块 | 按句号分割 | 新闻/规范文档 | 块可能过小 |
| 段落级 | Markdown Header分割 | 有结构的长文 | 块大小不一致 |

### 推荐配置
```python
# 通用文档：递归分割
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=128,  # 保持上下文连贯
    separators=["\n\n", "\n", ".", " ", ""],
)

# 代码文件：按函数分割 + 文件级摘要
# Markdown：按Header层级分割 + 保留标题元信息
```

### Chunking检查清单
- [ ] 分块后语义完整性如何？
- [ ] Overlap是否足够（至少128个字符/32个Token）？
- [ ] 是否保留了元数据（Source/Page/Header）？
- [ ] 小文档是否保留完整（不强制分块）？

## Embedding模型选型

| 模型 | 维度 | 特点 | 适用 |
|------|------|------|------|
| text-embedding-3-small | 1536 | 通用、性价比高 | 日常RAG |
| text-embedding-3-large | 3072 | 高精度 | 金融/法律 |
| bge-large-zh-v1.5 | 1024 | 中文优化 | 中文文档 |
| jina-embeddings-v3 | 1024 | 多语言、8192 token窗口 | 多语言长文 |
| E5-mistral-7b | 4096 | 高精度（贵） | 专业领域 |

> **建议**：先用 `text-embedding-3-small` 起步；中文场景主推 `bge-large-zh`。

## 检索增强生成Pipeline

### 核心流程
```
Query → Query Rewrite → Retriever → Reranker → LLM → Response
```

### Query Rewrite策略
- **HyDE**：假设文档生成（Query → 假想文档 → 搜索假想文档）
- **Sub-Query分解**：复杂问题拆多个子查询
- **Step-back Prompt**：退一步到抽象问题再具体搜索

### Retriever方法
- **Dense**：向量相似度（FAISS / Milvus / Pinecone）
- **Sparse**：BM25倒排索引（Elasticsearch）
- **Hybrid**：加权融合（推荐：dense:sparse = 7:3）

### Reranker
- **Cohere Rerank**：商业化，质量可靠
- **BGE-Reranker**：开源中文友好
- **Cross-Encoder**：速度快于再生成
- **LLM作为Reranker**：小模型排序（4%容量提示词）

## Hybrid Search（密集+稀疏）

### 实现方式
```python
# 加权融合
def hybrid_search(query, alpha=0.7):
    dense_results = vector_store.similarity_search(query, k=20)
    sparse_results = bm25_search(query, k=20)
    
    # Reciprocal Rank Fusion
    scores = {}
    for rank, doc in enumerate(dense_results + sparse_results):
        scores[doc.id] = scores.get(doc.id, 0) + 1 / (rank + 60)
    
    return sorted(scores.items(), key=lambda x: -x[1])[:10]
```

### 何时需要Hybrid
- 文档包含大量专有名词/代码
- 用户查询使用不同语言表达
- 短查询（2-3词）→ 密集检索
- 长查询/精确匹配 → 稀疏检索

## RAG评估

### 核心评估维度
| 维度 | 定义 | 测量方法 |
|------|------|----------|
| 忠实度 | 回答是否基于检索内容 | LLM Judge + Factual Consistency |
| 答案相关度 | 回答是否直接回应查询 | BERTScore / ROUGE-L |
| 上下文精度 | Top-K中相关文档比例 | 人工标注 + MRR/MAP |
| 上下文召回 | 相关文档是否都被检索 | Recall@K / NDCG@K |

### 常用评估框架
- **RAGAS**：Faithfulness + Answer Relevancy + Context Precision + Context Recall
- **TruLens**：RAG Triad（Answer Relevance / Context Relevance / Groundedness）
- **DeepEval**：内置RAG评估指标，支持CI集成

### 评估数据集构建
```python
# 测试集格式
test_questions = [
    {
        "question": "什么是RAG?",
        "ground_truth": "检索增强生成...",
        "relevant_docs": ["doc_1", "doc_3"]
    }
]
```

## RAG性能基线

| 指标 | 基线 | 目标 |
|------|------|------|
| 忠实度 | 0.85 | ≥ 0.92 |
| 答案相关度 | 0.80 | ≥ 0.90 |
| 上下文精度@5 | 0.75 | ≥ 0.85 |
| 上下文召回@5 | 0.70 | ≥ 0.85 |
| 端到端延迟 | 2s | ≤ 1s |
