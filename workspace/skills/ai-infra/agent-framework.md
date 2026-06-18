# Agent框架

AI Agent架构设计、框架对比与工程实践。

## 主流框架对比

| 框架 | 特点 | 社区活跃度 | 部署难度 | 适用场景 |
|------|------|-----------|----------|----------|
| LangChain | 生态最大，灵活性高 | ⭐⭐⭐⭐⭐ | 低 | 通用Agent/RAG |
| CrewAI | 多Agent协作开箱即用 | ⭐⭐⭐⭐ | 低 | 多Agent编排 |
| AutoGen | Microsoft出品，对话式 | ⭐⭐⭐⭐ | 中 | 代码生成/研究 |
| Camel | 角色扮演式多Agent | ⭐⭐⭐ | 高 | 研究/模拟 |
| Semantic Kernel | Microsoft .NET原生 | ⭐⭐⭐ | 中 | 企业.NET应用 |
| Dify | 低代码平台 | ⭐⭐⭐⭐ | 低 | 业务人员使用 |
| Coze | 字节跳动，零代码 | ⭐⭐⭐⭐ | 最低 | 快速创建Bot |

### 选型决策
```
编程能力强的技术团队：
- 通用场景 → LangChain
- 多Agent协作 → CrewAI / AutoGen
- 研究探索 → Camel

非技术人员或快速验证：
- 可视化编排 → Dify / Coze
- 企业.NET → Semantic Kernel
```

## Tool-Use模式设计

### 工具定义规范
```python
# 函数式工具（推荐）
@tool
def search_weather(city: str) -> str:
    """查询城市天气
    Args:
        city: 城市名，如"北京"
    Returns:
        天气描述字符串
    """
    return f"{city}: 晴，25°C"

# JSON Schema工具（兼容OpenAI Function Calling）
weather_tool = {
    "type": "function",
    "function": {
        "name": "search_weather",
        "description": "查询城市天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名"}
            },
            "required": ["city"]
        }
    }
}
```

### 工具设计原则
1. **单一职责**：一个工具只做一件事
2. **描述清晰**：描述包含何时用、参数含义
3. **错误处理**：工具返回结构化错误，Agent决定重试/跳过
4. **权限分级**：只读/读写/管理级工具区分
5. **速率限制**：工具内部实现限流/重试

### 工具分类
| 类别 | 例子 | 安全等级 |
|------|------|----------|
| 检索 | 搜索/查数据库 | 只读 |
| 计算 | 数学/统计分析 | 只读 |
| 操作 | 创建/更新/删除 | 需审核 |
| 通信 | 发邮件/发消息 | 需审核 |
| 系统 | 执行命令/写文件 | 禁止 |

## 多Agent通信协议

### 通信模式
```
1. 广播模式：一Agent发，全体接收
2. 路由模式：指定接收者
3. 反馈模式：A询问B，B回复A
4. 编排模式：协调者分派任务
5. 辩论模式：多Agent讨论得出共识
```

### 消息格式
```python
@dataclass
class AgentMessage:
    sender: str
    receiver: str | None  # None = broadcast
    message_type: str     # query/response/action/result/error
    content: Any
    metadata: dict
    timestamp: float
    turn_id: int          # 对话轮次
```

### 实现策略
- **Synchronous**：等待回复，适用于简单链式任务
- **Asynchronous**：消息队列，适用于复杂协作
- **Hybrid**：同步超时+异步回调

## Memory/Persistence策略

### Agent记忆层级
```
短期记忆（Session）→ 对话上下文（可配窗口大小）
中期记忆（Conversation）→ 当前任务的完整历史
长期记忆（Profile/LongTerm）→ 用户偏好/领域知识/经验记录
```

### 存储实现
| 记忆类型 | 存储方案 | 检索方式 | TTL |
|----------|----------|----------|-----|
| 短期记忆 | 内存 List[Message] | 按序索引 | Session结束 |
| 中期记忆 | SQLite/Redis | 按ID/Session查询 | 24h |
| 长期记忆 | Vector DB | 语义相似度 | 永久 |

### 总结压缩策略
```
当上下文接近Token限制时：
1. 压缩早期对话（Summarization）
2. 提取关键信息（关键决策/用户偏好）
3. 保留最近N轮对话（滑动窗口）
4. 重置对话上下文
```

## Agent安全

- **越狱防护**：System Prompt注入检测
- **工具执行沙箱**：Docker/受限环境
- **权限最小化**：Agent只获得所需最低权限
- **审计日志**：所有Agent动作记录
- **人工确认**：高风险操作需审批

## Agent开发Checklist

- [ ] 框架选型（LangChain/CrewAI/AutoGen）
- [ ] 工具定义完成（描述准确）
- [ ] 权限分级设计
- [ ] 记忆策略确定（短/中/长期）
- [ ] 通信协议定义
- [ ] 推理预算控制（最大轮次/Token）
- [ ] 错误处理与重试
- [ ] 安全审计日志
- [ ] 监控指标配置
- [ ] 回退策略（Agent兜底）
