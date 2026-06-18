# LLM训练优化

大语言模型分布式训练与显存优化全指南。

## 分布式训练策略

### 主要并行策略对比

| 策略 | 适用 | 通信开销 | 实现复杂度 |
|------|------|----------|------------|
| 数据并行（DDP/FSDP） | 模型单卡能放下 | 低 | 低 |
| 张量并行（TP） | 超大模型层内拆分 | 高 | 中 |
| 流水线并行（PP） | 超大模型跨层拆分 | 中 | 中 |
| 序列并行（SP） | 超长序列 | 中 | 高 |
| 上下文并行（CP） | 百万级Token训练 | 高 | 高 |

### 推荐组合
```
阶段性策略：
- < 13B参数：FSDP（Sharding策略）
- 13B-70B：FSDP + TP
- > 70B：FSDP + TP + PP（3D并行）
```

### FSDP Sharding策略选择
| 策略 | 显存 | 通信 | 速度 |
|------|------|------|------|
| NO_SHARD | 高 | 低 | 快 |
| SHARD_GRAD_OP | 中 | 中 | 中 |
| FULL_SHARD | 低 | 高 | 慢 |

> **建议**：小模型（<7B）用NO_SHARD；大模型用FULL_SHARD。
> 训练瓶颈在显存优先FULL_SHARD，在通信优先SHARD_GRAD_OP。

## 混合精度训练

### 精度对比
| 精度 | 位宽 | 范围 | 适用 |
|------|------|------|------|
| FP32 | 32 | 最宽 | Loss/Param累加 |
| FP16 | 16 | 窄（易溢出） | 前向/梯度 |
| BF16 | 16 | 宽（推荐） | 主流训练格式 |
| FP8 | 8 | 窄 | 新一代加速 |

### 推荐配置
```python
# PyTorch AMP
with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
    output = model(input)
    loss = loss_fn(output, target)

# DeepSpeed ZeRO + BF16
# ds_config.json
{
    "bf16": {"enabled": true},
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {"device": "cpu"}
    }
}
```

## 显存优化

### 激活检查点（Activation Checkpointing）
- **原理**：前向不存所有激活值，反向时重新计算
- **效果**：减少显存50-70%
- **代价**：增加30%计算时间
- **选择性使用**：只检查点特定Transformer Layer

### 梯度累积
```python
# batch = micro_batch_size * gradient_accumulation_steps
optimizer.zero_grad()
for micro_step in range(gradient_accumulation_steps):
    loss = model(micro_batch)
    loss = loss / gradient_accumulation_steps
    loss.backward()
optimizer.step()  # 每N步更新一次
```

### 显存节省速查表
| 技术 | 显存节省 | 速度影响 |
|------|----------|----------|
| BF16训练 | ~50% | +5% |
| 激活检查点 | ~60% | +30% |
| 梯度累积 | 不变（但模拟大Batch） | — |
| CPU Offload | ~80% | 极慢（仅适用单卡） |
| Flash Attention | ~30% | -10%（更快） |
| Paged Adam | ~50%优化器状态 | +5% |

## 数据并行/模型并行/流水线并行

### 数据并行（Data Parallelism）
```
每卡一份完整模型，分Batch训练 → AllReduce梯度
适用：模型单卡放得下
设配：DDP（同步）/ FSDP（分片）
```

### 模型并行（Tensor Parallelism）
```
单层操作拆分到多卡：
Attention头拆分 / FFN列拆分
适用：单层太大放不下
设配：Megatron-LM / vLLM
```

### 流水线并行（Pipeline Parallelism）
```
模型按Layer拆到不同GPU：
GPU0: Layer 1-10 → GPU1: Layer 11-20
调度：micro-batch交错执行
全局Batch需足够大
```

### 硬件配置推荐
| 模型规模 | GPU配置 | 并行策略 |
|----------|---------|----------|
| 7B | 1-4x A100 80G | FSDP |
| 13B | 8x A100 80G | FSDP stage 3 |
| 70B | 32x A100 80G | FSDP+TP+PP |
| 130B+ | 64+ H100 | Megatron-Core |

## 训练检查清单

- [ ] 模型架构确定（Dense/MoE/MLA）
- [ ] Batch Size与LR配套
- [ ] 学习率预热+衰减策略
- [ ] 分布式策略匹配硬件
- [ ] 激活检查点选层配置
- [ ] 混合精度（BF16/FP8）
- [ ] Loss曲线监控
- [ ] 梯度裁剪
- [ ] 数据Loader效率（num_workers）
- [ ] Checkpoint恢复测试
