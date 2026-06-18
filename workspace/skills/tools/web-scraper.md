# 网页抓取

网页数据抓取策略与反爬对抗全指南。

## 选择器策略

### 选择器对比
| 类型 | 语法 | 速度 | 准确性 | 适用 |
|------|------|------|--------|------|
| CSS选择器 | `.class #id div` | 快 | 中 | 静态HTML |
| XPath | `//div[@class="foo"]/text()` | 慢 | 高 | 复杂结构 |
| Regex | `/<title>(.*?)<\/title>/` | 快 | 低 | 文本提取 |
| 结合策略 | CSS + XPath混合 | 中 | 最高 | 推荐 |

### 选择器最佳实践
```python
# CSS选择器（推荐）
response.css('div.product-price::text').get()

# XPath选择器（复杂结构）
response.xpath('//div[contains(@class, "product")]//span[@data-price]/text()').get()

# 解析顺序：ID → Class → 属性 → 层级
# 1. ID最好：response.css('#main-price::text')
# 2. Class次之：response.css('.price-tag::text')
# 3. 属性最灵活：response.css('[data-testid="product-price"]::text')

# 避免脆弱的层级选择器
# ❌ 脆弱：response.css('div > div > span > span.price::text')
# ✅ 健壮：response.css('span.price::text')
```

### 动态选择器工厂
```python
def flexible_select(soup, selectors: list[str]) -> str | None:
    """多选择器回退策略"""
    for selector in selectors:
        result = soup.select_one(selector)
        if result:
            return result.get_text(strip=True)
    return None

# 使用
price = flexible_select(soup, [
    '[data-price]',
    '.price-tag',
    '.product-price',
    '#price',
])
```

## 动态内容抓取

### 渲染引擎方案
```python
# Playwright（推荐）
from playwright.async_api import async_playwright

async def scrape_dynamic(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        # 等待特定元素加载
        await page.wait_for_selector('.content-loaded')
        content = await page.content()
        await browser.close()
        return content

# Puppeteer（JS生态）
# const puppeteer = require('puppeteer');
# const browser = await puppeteer.launch();
# const page = await browser.newPage();
# await page.goto(url, { waitUntil: 'networkidle0' });
```

### 动态内容策略
```
1. 检测客户端渲染：查看HTML是否为空壳
2. 选择渲染引擎：Playwright（推荐）/ Puppeteer / Selenium
3. 等待策略：networkidle > 选择器等待 > 固定延迟
4. 滚动加载：模拟滚动到页面底部（瀑布流）
5. 无限滚动：循环滚动直到无新元素
```

### 检测方法
```python
def is_dynamic_content(html: str) -> bool:
    """检测是否需要JavaScript渲染"""
    indicators = [
        '<script>',
        'react-root',
        'id="app"',
        'ng-app',
        'vue-app',
        '<app-root>',
        'data-server-rendered="false"'
    ]
    return any(i in html.lower() for i in indicators)
```

## 反爬绕过策略

### 请求头伪装
```python
headers = {
    # 必须设置
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
    'Accept': 'text/html,application/xhtml+xml,...',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    
    # 可选设置
    'Referer': 'https://www.google.com/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
}

# User-Agent轮换池
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36...',
]
```

### 代理策略
```python
import random

proxies = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
]

def get_random_proxy():
    proxy = random.choice(proxies)
    return {'http': proxy, 'https': proxy}

# 代理轮换频率
# 低风险：每小时换一次
# 中风险：每10个请求换一次
# 高风险：每个请求都换
```

### 速率限制控制
```python
import asyncio
import time

class RateLimiter:
    def __init__(self, requests_per_second: float = 1.0):
        self.min_interval = 1.0 / requests_per_second
        self.last_request = 0
    
    async def wait(self):
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

# 指数退避重试
def fetch_with_retry(url, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            return response
        except (ConnectionError, Timeout) as e:
            wait = 2 ** i + random.random()  # 指数退避
            time.sleep(wait)
    raise Exception(f"Failed after {max_retries} retries")
```

## 数据清洗与结构化

### 清洗流程
```python
def clean_scraped_data(raw_text: str) -> dict:
    """清洗与结构化抓取结果"""
    # 1. 去除空白字符
    text = re.sub(r'\s+', ' ', raw_text).strip()
    
    # 2. 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. 规范化标点
    text = text.replace('，', ',').replace('。', '.')
    
    # 4. 提取结构化字段
    price_match = re.search(r'¥?(\d+\.?\d*)', text)
    data = {
        'price': float(price_match.group(1)) if price_match else None,
        # ... 其他字段
    }
    
    return data
```

## 抓取合法性检查清单

- [ ] 遵守robots.txt
- [ ] 设置合理的请求频率
- [ ] 不抓取个人隐私数据
- [ ] 不绕过登录墙（付费内容）
- [ ] 尊重版权（不重复发布）
- [ ] 缓存结果减少请求
- [ ] 公开数据不做商业化
- [ ] 留意API条款的限制
