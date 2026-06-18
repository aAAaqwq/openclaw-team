# RAG系统设计

端到端RAG架构设计、多模态支持与监控优化。

## 端到端RAG架构

### 核心Pipeline

```
┌─────────────────────┐
│   数据接入           │
│ (Documents/Crawl/API)│
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│   Ingestion          │
│ (解析/清洗/Chunking) │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│   Indexing           │
│ (Embedding/元数据)   │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│   Retrieval          │
│ (Dense+Sparse+Rerank)│
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│   Generation         │
│ (Prompt+Context+LLM) │
└─────────────────────┘
```

### 数据Ingestion流程
```python
def ingest_document(file_path):
    # 1. 文件解析
    text, metadata = parse_document(file_path)
    
    # 2. 文档清洗（去噪/去重）
    text = clean_text(text)
    
    # 3. 分块
    chunks = split_text(text, strategy="recursive", chunk_size=512)
    
    # 4. 元数据增强（时间戳/来源/页码）
    chunks = enrich_metadata(chunks, metadata)
    
    # 5. Embedding + 存储
    embeddings = model.encode(chunks)
    vector_store.add(embeddings, chunks)
```

### 检索Pipeline（延迟优化）
```python
async def retrieval_pipeline(query, k=5):
    # Step 1: Query理解（异步）
    query_task = asyncio.create_task(rewrite_query(query))
    rewrite_task = asyncio.create_task(decompose_query(query))
    
    # Step 2: 并行检索
    dense_task = asyncio.create_task(dense_search(query))
    sparse_task = asyncio.create_task(sparse_search(query))
    
    _, _, dense_results, sparse_results = await asyncio.gather(
        query_task, rewrite_task, dense_task, sparse_task
    )
    
    # Step 3: 融合+重排
    merged = fuse_results(dense_results, sparse_results)
    reranked = rerank(merged, query)
    
    return reranked[:k]
```

## 多模态RAG

### 支持的数据类型
| 类型 | 处理方式 | 存储策略 |
|------|----------|----------|
| 文本 | Chunking + Embedding | 向量库 |
| 图片 | 多模态Embedding / OCR文本 | 向量库 + 对象存储 |
| 表格 | 结构化解析 + Summary | 向量库 + 元数据 |
| 音频 | ASR转文字 | 向量库 |
| 视频 | 关键帧提取 + ASR | 向量库 + 对象存储 |

### 多模态检索策略
- **Late Fusion**：各模态独立检索后融合（推荐）
- **Early Fusion**：统一多模态Embedding（需要多模态模型）
- **分层检索**：先粗粒度（文档级），再细粒度（块级）

## 缓存策略

### 语义缓存（Semantic Cache）
```python
def semantic_cache_query(query, similarity_threshold=0.95):
    # 语义相似度匹配缓存
    cached = cache.search(query, top_k=1)
    if cached and cached.similarity > similarity_threshold:
        return cached.result
    return None
```

### 结果缓存
| 缓存类型 | TTL | 失效策略 | 适用场景 |
|----------|-----|----------|----------|
| 精确匹配 | 5min | LRU | 频繁相同查询 |
| 语义匹配 | 30min | LRU+时间 | 相似问题 |
| 前缀缓存 | 会话期 | Session | 多轮对话 |

### 缓存分层设计
```
L1: 内存缓存（Redis）— 毫秒级，容量小
L2: 本地缓存（LRU）— 微秒级，容量有限
L3: 分布式缓存 — 毫秒级，容量大
```

## 监控体系

### 核心监控指标

| 分类 | 指标 | 告警阈值 | 说明 |
|------|------|----------|------|
| 延迟 | P50检索 | > 200ms | 检索慢 → 检查索引 |
| 延迟 | P50生成 | > 2s | 生成慢 → 检查模型 |
| 质量 | Recall@5 | < 0.8 | 召回下降 → 检查Embedding |
| 质量 | MRR | < 0.75 | 排序差 → 检查Reranker |
| 系统 | QPS | — | 容量规划 |
| 系统 | 命中率 | — | 缓存与检索比例 |

### 端到端链路追踪
```python
# 使用 OpenTelemetry
from opentelemetry import trace
tracer = trace.get_tracer("rag-service")

with tracer.start_as_current_span("rag_query") as span:
    span.set_attribute("query", query)
    
    with tracer.start_as_current_span("retrieval") as child:
        results = retrieve(query)
        child.set_attribute("results_count", len(results))
    
    span.set_attribute("total_latency_ms", latency)
```

## 架构模式选择

### 适用场景
| 场景 | 推荐架构 | 理由 |
|------|----------|------|
| 通用问答 | Simple RAG | 少依赖，快速上线 |
| 代码问答 | 层级RAG | 代码+文档分层 |
| 金融分析 | Agent RAG | 需要多步推理 |
| 客服系统 | 多轮RAG | 需要对话历史 |
| 知识库 | 图RAG（GraphRAG） | 实体关系复杂 |

## RAG系统Checklist

- [ ] Ingestion流程自动化
- [ ] 文档版本管理
- [ ] 增量更新机制
- [ ] 检索延迟 < 200ms P50
- [ ] 端到端延迟 < 2s P50
- [ ] 缓存策略配置
- [ ] 监控告警配置
- [ ] A/B测试框架
- [ ] 回滚方案
- [ ] 数据质量控制
