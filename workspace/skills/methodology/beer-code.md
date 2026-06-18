# BEER编码规则

Brevity（精简）+ Expressiveness（表达力）+ Efficiency（效率）+ Readability（可读性）编码规范。

## B — Brevity（精简）

### 原则
```
代码不是越短越好，而是没有冗余。
每行代码解决一个问题，不重复。
```

### 实践
```python
# ❌ 冗余
if condition == True:
    return True
else:
    return False

# ✅ 精简
return condition

# ❌ 冗余变量
temp_var = calculate_value(x, y)
result = process_value(temp_var)
return result

# ✅ 简洁链式
return process_value(calculate_value(x, y))

# ❌ 重复逻辑
def process_orders(orders):
    for o in orders:
        if o.status == 'active':
            o.discount = o.total * 0.1
            o.final = o.total - o.discount
    return orders

# ✅ 提取方法
def process_orders(orders):
    return [apply_discount(o) for o in orders if o.status == 'active']
```

## E — Expressiveness（表达力）

### 原则
```
代码传达意图，不解释实现。
命名即文档，类型即契约。
```

### 实践
```python
# ❌ 弱表达
def calc(a, b):
    return a * b * 0.9

# ✅ 强表达
def calculate_discounted_price(price: float, quantity: int) -> float:
    """计算折扣后总价（满×9折优惠）"""
    return price * quantity * 0.9

# ❌ 魔法数字
def is_valid_user(user):
    return user.score > 80 and user.reg_days > 30

# ✅ 命名常量
MIN_SCORE_FOR_ACTIVE_USER = 80
MIN_REG_DAYS_FOR_ACTIVE_USER = 30

def is_active_user(user) -> bool:
    return user.score > MIN_SCORE_FOR_ACTIVE_USER and \
           user.reg_days > MIN_REG_DAYS_FOR_ACTIVE_USER
```

## E — Efficiency（效率）

### 原则
```
选对数据结构和算法。
缓存计算结果，避免重复计算。
懒加载减少不必要开销。
```

### 实践
```python
# ❌ 低效
def find_duplicates(items):
    result = []
    for i in items:
        if items.count(i) > 1 and i not in result:
            result.append(i)
    return result  # O(n²)

# ✅ 高效
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)  # O(n)

# ❌ 重复计算
if expensive_check(user) and user.is_active:
    print("Start processing")

# ✅ 短路优化
if user.is_active and expensive_check(user):
    print("Start processing")

# 早返回 vs 嵌套条件
# ❌ 嵌套深
def process(data):
    if data:
        if validate(data):
            return transform(data)
        else:
            return None
    return None

# ✅ 早返回
def process(data):
    if not data:
        return None
    if not validate(data):
        return None
    return transform(data)
```

## R — Readability（可读性）

### 原则
```
代码被读的次数远多于写的次数。
一致性比个人喜好更重要。
层次分明，视觉引导。
```

### 实践
```python
# ❌ 可读性差
def f(x):return[x*2 if x%2==0 else x*3 for x in x if x>0]

# ✅ 可读性好
def transform_numbers(numbers):
    """偶数翻倍，奇数三倍"""
    return [n * 2 if n % 2 == 0 else n * 3 
            for n in numbers 
            if n > 0]

# ❌ 晦涩的链式
result = data.filter(lambda x: x>0).map(str).filter(lambda x: len(x) > 2).reduce(lambda a,b: a+b)

# ✅ 明确步骤
positive_only = data.filter(lambda x: x > 0)
as_strings = positive_only.map(str)
long_strings = as_strings.filter(lambda x: len(x) > 2)
result = long_strings.reduce(lambda a, b: a + b)
```

## BEER编码审查检查清单

### Brevity（精简）
- [ ] 是否有未使用的变量/函数
- [ ] 是否有重复代码（DRY）
- [ ] 是否有冗余的条件判断
- [ ] 注释是否解释了代码本身就能表达的意图

### Expressiveness（表达力）
- [ ] 函数名是否准确描述行为
- [ ] 变量名是否表明含义而非实现细节
- [ ] 类型注解是否完整
- [ ] 是否有魔法数字/字符串

### Efficiency（效率）
- [ ] 算法复杂度是否有优化空间（O(n²)→O(n)）
- [ ] 是否有不必要的数据复制
- [ ] 缓存是否利用得当
- [ ] 数据库查询是否N+1

### Readability（可读性）
- [ ] 缩进/格式一致
- [ ] 嵌套深度 ≤ 3层
- [ ] 函数行数 ≤ 50行（不含测试）
- [ ] 命名风格一致（camelCase/snake_case）
