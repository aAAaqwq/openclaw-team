# 推理优化

LLM推理加速技术与部署优化全指南。

## 推理框架对比

| 框架 | 特点 | 适用场景 | 延迟 | 吞吐 |
|------|------|----------|------|------|
| vLLM | PagedAttention，生态最好 | 通用在线服务 | 低 | 高 |
| TGI | HuggingFace官方 | HF模型生态 | 中 | 中 |
| TensorRT-LLM | NVIDIA官方 | 生产级高性能 | 最低 | 最高 |
| SGLang | 结构化LLM | 复杂推理/Agent | 低 | 高 |
| Ollama | 本地使用 | 个人/开发 | 中 | 低 |
| llama.cpp | 本地+量化 | 边缘设备 | 中 | 低 |

### 选型建议
```
生产环境：
- 通用服务 → vLLM
- 极致性能 → TensorRT-LLM
- Agent/Function Calling → SGLang

开发环境：
- 快速验证 → Ollama / TGI
- 本地部署 → Ollama / llama.cpp
```

## KV Cache优化

### 核心问题
```
Transformer推理中，每个Token产生KV向量。
序列越长，KV Cache显存越大。
Batch越大，KV Cache显存消耗越严重。
```

### 主要优化技术

| 技术 | 原理 | 效果 | 实现框架 |
|------|------|------|----------|
| PagedAttention | 分页管理KV Cache | 消除碎片，提升2-4x吞吐 | vLLM |
| Multi-Query Attention | 多Query共享KV | KV显存降80% | MQA模型 |
| Grouped-Query Attention | Q组共享KV | 折中MQA与MHA | GQA模型（LLaMA2-3） |
| KV Cache量化 | INT8/FP8存KV | KV缓存减半 | TensorRT-LLM |
| Prefix Caching | 共享Prompt前缀Cache | 重复Prompt降低延迟 | vLLM/SGLang |

### KV Cache共享策略
```
互动场景：
- System Prompt共享 → Prefix Cache
- 多轮对话 → 增量续算Cache
- 批量相同Prompt → 共享前缀

实现：vLLM enable_prefix_caching=True
```

## 连续批处理

### 工作原理
```
传统批处理：Batch一起请求 → 等最慢的完成 → 返回
连续批处理：动态加入/退出Batch，类似操作系统调度

处理流程：
1. 收集等待请求
2. 调度器决定哪些请求参与本次Decode
3. Prefill新请求 + Decode旧请求
4. 完成请求移出，新请求加入
```

### 调度策略
| 策略 | 优先级 | 公平性 | 适用 |
|------|--------|--------|------|
| FCFS | 先来先服务 | 低 | 简单场景 |
| SJF | 短作业优先 | 中 | 低延迟要求 |
| Max Throughput | 吞吐优先 | 低 | 流式批量 |
| 混合 | 延迟+吞吐平衡 | 高 | 生产推荐 |

## Streaming/Speculative Decoding

### Streaming输出
```
Server-Sent Events（SSE）逐Token输出
避免用户等待完整响应
```

### Speculative Decoding（投机解码）
```
原理：用小模型（Draft Model）快速生成K个Token，
再用大模型（Target Model）一次性验证纠正。

加速：1.5-3x（理想），取决于draft接受率
适用：自回归生成瓶颈场景
代价：需要匹配的Draft Model
```

### 实现方式
```python
# vLLM speculative decoding
from vllm import LLM
llm = LLM(
    model="target-model",
    speculative_model="draft-model",  # 小模型通常1/3参数
    num_speculative_tokens=5,
)
```

## 推理优化Checklist

- [ ] 选对推理框架（vLLM/SGLang/TRT-LLM）
- [ ] KV Cache策略（量化/共享）
- [ ] 连续批处理开启
- [ ] 模型Batch Size匹配负载
- [ ] 量化策略选择（INT4/INT8/FP8）
- [ ] PagedAttention开启（vLLM默认）
- [ ] Prefix Caching启用（重复Prompt场景）
- [ ] Speculative Decoding评估加速比
- [ ] GPU利用率 > 80%
- [ ] 端到端延迟达标（P50/P99）
- [ ] 最大并发用户估测
