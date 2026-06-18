# Schema标记生成器 (Schema Markup Generator)

> 为企业站生成符合Schema.org标准的JSON-LD结构化数据标记，提升搜索引擎和AI引擎对页面内容的理解精度，是**GEO优化的基础设施层**。

## 核心方法

### 1. JSON-LD结构化数据模板

以下为常用Schema类型的JSON-LD模板：

#### Organization（组织）

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "企业全称",
  "alternateName": "品牌简称/别名",
  "url": "https://www.example.com",
  "logo": "https://www.example.com/logo.png",
  "description": "一句话企业描述",
  "foundingDate": "YYYY-MM-DD",
  "founders": [
    { "@type": "Person", "name": "创始人姓名" }
  ],
  "sameAs": [
    "https://linkedin.com/company/xxx",
    "https://twitter.com/xxx",
    "https://github.com/xxx"
  ]
}
```

#### FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "最常见的问题？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "清晰、简洁、包含核心关键词的答案"
      }
    }
  ]
}
```

#### Article

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "文章标题（包含核心关键词）",
  "description": "Meta描述或摘要",
  "author": {
    "@type": "Person",
    "name": "作者姓名",
    "url": "https://www.example.com/authors/xxx"
  },
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "publisher": {
    "@type": "Organization",
    "name": "发布组织"
  }
}
```

#### Product

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "产品名称",
  "description": "产品描述",
  "brand": {
    "@type": "Brand",
    "name": "品牌名称"
  },
  "offers": {
    "@type": "Offer",
    "priceCurrency": "CNY",
    "price": "99.99",
    "availability": "https://schema.org/InStock"
  },
  "category": "产品类别"
}
```

#### BreadcrumbList（面包屑导航）

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "首页",
      "item": "https://www.example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "分类名",
      "item": "https://www.example.com/category/"
    }
  ]
}
```

#### HowTo

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "操作指南标题",
  "description": "指南描述",
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "步骤1名称",
      "text": "步骤1详情"
    }
  ]
}
```

### 2. Schema与GEO引用的关联策略

| Schema类型 | GEO信号贡献 | 最佳实践 |
|-----------|------------|---------|
| Organization | 实体名称/属性/关系被AI引用 | 确保 alternateName 包含常用别名 |
| FAQPage | 问答对直接成为AI回答素材 | 每个FAQ回答200-500字，包含具体数据 |
| Article | 作者权威信号 | 作者页面含完整学术/职业背景 |
| Product | 产品属性结构化 | 含价格/版本/兼容性等精确数据 |
| BreadcrumbList | 网站结构清晰 | 帮助AI理解内容层级 |
| HowTo | 步骤式内容易被引用 | 每一步配简短描述 |

### 3. 测试工具

部署Schema标记后必须验证有效性：

| 工具 | 用途 | 链接 |
|------|------|------|
| **Google Rich Results Test** | 检查谷歌富媒体结果兼容性 | https://search.google.com/test/rich-results |
| **Schema.org Validator** | W3C标准验证 | https://validator.schema.org |
| **Google Merchant Center** | Product Schema专用 | GMC后台 |
| **Ahrefs/Raven Tools** | 批量页面Schema审计 | 付费工具 |

## 多页面Schema审计检查清单

- [ ] 首页：Organization + BreadcrumbList
- [ ] 关于页：Organization（含创始人/成立/团队信息）
- [ ] 产品/定价页：Product + Offer + BreadcrumbList
- [ ] 博客文章：Article + BreadcrumbList + Author
- [ ] FAQ页面：FAQPage
- [ ] 教程/指南：HowTo + BreadcrumbList
- [ ] 联系方式：Organization + LocalBusiness（如有线下）
- [ ] 案例：Article + ItemList + BreadcrumbList
- [ ] 所有页面：至少包含Organization基础标记
- [ ] 所有页面：BreadcrumbList

**质量检查：**
- [ ] 无重复/冲突的Schema声明
- [ ] JSON-LD格式正确（不使用Microdata）
- [ ] canonical标签指向正确
- [ ] 无占位文本或空白URL
- [ ] Schema内容与页面可见内容一致

## 相关技能

- [实体优化器](entity-optimizer.md) — 实体信号矩阵作为Schema内容素材
- [GEO内容优化器](../growth/geo-content-optimizer.md) — 内容级GEO优化
- [GEO优化大师](geo-optimization-pro.md) — Schema作为全面GEO审核的一部分
- [SEO+GEO内容写作](../growth/seo-content-writer.md) — 写作时预埋Schema友好内容
