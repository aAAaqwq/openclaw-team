# DDD实践者

领域驱动设计（DDD）战略与战术模式实战指南。

## 战略设计

### Bounded Context（限界上下文）
```
核心原则：每个Bounded Context内保持统一的Ubiquitous Language。
上下文之间通过Context Map映射关系。

例子：
订单上下文：Order = 待付款/已付款/已发货
物流上下文：Order = 待揽件/运输中/已签收
库存上下文：Order = 预订/出库/退货
```

### Ubiquitous Language（统一语言）
- **团队共创**：业务+开发一起定义术语表
- **持续维护**：术语变化时同步更新
- **拒绝翻译**：代码中的类名/方法名使用统一语言
- **文档同步**：需求文档/PRD/代码注释用同一套术语

### 上下文类型识别
| 类型 | 特征 | 例子 |
|------|------|------|
| 核心域 | 核心竞争力，需自研 | 支付引擎/推荐系统 |
| 支撑子域 | 辅助业务，可外包 | 邮件通知/报表 |
| 通用子域 | 标准化，可买现成 | 认证/发票 |

## 战术设计

### Aggregate（聚合）
```
实体（Entity）和值对象（Value Object）的边界簇。
通过根实体（Aggregate Root）对外访问。

规则：
1. Aggregate Root保护内部一致性
2. 外部只能通过Root访问内部元素
3. 一次事务只修改一个Aggregate（最终一致性）
```

### 设计示例
```python
class Order(AggregateRoot):
    """订单聚合根"""
    def __init__(self):
        self.order_id: OrderId
        self.customer_id: CustomerId
        self._items: List[OrderItem] = []
        self._status: OrderStatus = OrderStatus.PENDING
        self._events: List[DomainEvent] = []
    
    def add_item(self, product_id: ProductId, quantity: int, price: Money):
        if self._status != OrderStatus.PENDING:
            raise DomainError("只能修改待处理订单")
        self._items.append(OrderItem(product_id, quantity, price))
        self._events.append(ItemAddedEvent(self.order_id, product_id))
    
    def submit(self):
        if not self._items:
            raise DomainError("空订单无法提交")
        self._status = OrderStatus.SUBMITTED
        self._events.append(OrderSubmittedEvent(self.order_id))
```

### Entity VS Value Object
| | Entity | Value Object |
|--|--------|--------------|
| 身份 | 有唯一ID | 无ID，靠属性值比较 |
| 可变性 | 可变 | 不可变 |
| 生命周期 | 有自己的生命周期 | 依附于Entity |
| 例子 | User/Order | Address/Money |

## Event Storming工作坊

### 工作坊流程
```
1. 混乱探索（1h）
→ 所有领域事件贴到墙上（浅橙）
→ 时间线排列

2. 触发事件（30min）
→ 什么导致领域事件发生？（命令 = 蓝色贴）

3. 约束条件（30min）
→ 哪些策略/规则影响流程？（政策 = 紫色贴）

4. 读取模型（20min）
→ 用户需要看什么数据？（读取模型 = 绿色贴）

5. 限界上下文（30min）
→ 按业务边界分组，定义上下文名称
```

### 必要材料
- 大量便利贴（4-6种颜色）
- 长墙或虚拟白板（Miro/Whimsical）
- 3-8人参与（必须含业务专家）
- 宽松的时间（半天到2天）

## 上下文映射（Context Map）

### 合作关系模式
| 模式 | 关系 | 团队协作 | 适用场景 |
|------|------|----------|----------|
| Partnership | 双向依赖 | 紧密协作 | 两个核心域 |
| Shared Kernel | 共享核心模型 | 联合开发 | 高度耦合 |
| Customer-Supplier | 上游→下游 | 下游驱动上游 | 典型上下游 |
| Conformist | 遵从上游 | 下游适应上游 | 通用子域 |
| Anticorruption Layer | 防腐层 | 下游隔离 | 适配遗留系统 |
| Open Host Service | 开放服务 | 发布API | 服务化上下文 |
| Published Language | 发布语言 | 标准协议 | 跨语言集成 |
| Separate Ways | 独立发展 | 无耦合 | 完全不相关的域 |

### 防腐层（ACL）设计
```python
class LegacySystemAdapter:
    """防腐层：适配旧系统模型→新领域模型"""
    
    def get_order(self, legacy_order_id):
        legacy_data = self.legacy_api.get_order(legacy_order_id)
        return Order(
            order_id=OrderId(legacy_data["order_no"]),
            customer_id=CustomerId(legacy_data["cust_code"]),
            total=Money(legacy_data["amt"], "CNY")
        )
```

## DDD实践Checklist

- [ ] Bounded Context划分清晰
- [ ] Ubiquitous Language文档化
- [ ] Aggregate Root设计正确
- [ ] 领域事件定义完整
- [ ] 上下文映射图维护
- [ ] 泛化与防腐层隔离外部系统
- [ ] Repository接口在领域层定义
- [ ] 应用服务只做编排，业务逻辑在领域层
- [ ] 领域服务处理跨Aggregate逻辑
- [ ] Event Storming定期（每季度）重访
