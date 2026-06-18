# GEO Optimization Pro

## When to Apply
Use when optimizing content/brand for AI search engines (ChatGPT, Claude, Perplexity, Gemini), analyzing AI citation patterns, or improving brand mentions in LLM responses.

## Core Framework

### 1. AI Citation Optimization
Content must be structured so AI systems can easily parse, extract, and cite it.

**Content Structure for AI:**
```
Title: [Keyword-rich, clear, declarative]
Opening: "Here's what you need to know about X..."
Q&A Section: "Q: What is X? A: X is..."
Definitions: Bold key terms AI will extract
Data Points: Always cite sources for stats
Summary: "In conclusion, the key takeaway is..."
```

### 2. Authority Signal Matrix

| Signal | Weight | How to Build |
|--------|--------|-------------|
| Author Expertise | High | Bio + credentials + published works |
| Source Citations | High | Link to .edu/.gov/.org + peer-reviewed |
| Content Freshness | Medium | Regular updates + date stamps |
| Structured Data | Medium | JSON-LD (FAQPage, HowTo, Article) |
| Social Proof | Medium | LinkedIn endorsements, Twitter mentions |
| Backlink Quality | Medium | .edu/.gov backlinks > quantity |

### 3. GEO Scoring Checklist

```
□ 标题包含直接问题式回答 (e.g., "How to X in 2026")
□ 首段直接回答问题（AI提取答案的关键段）
□ 使用了FAQPage结构化数据（AI最常引用的Schema类型）
□ 每个数据点有权威引用来源
□ 内容中包含3-5个可引述的"金句"
□ 作者信息清晰（LinkedIn/出版物/资历）
□ 网页加载速度<2s（AI bot爬取效率）
□ 允许相关AI bot爬取（robots.txt白名单）
□ 内容定期更新（显示日期，保持时效性）
□ 有外部引用→被引用（增加AI的信任评分）
```

### AI Bot白名单配置

```txt
# robots.txt - 确保以下bot允许
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Applebot
Allow: /
```
