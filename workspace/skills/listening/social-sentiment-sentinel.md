# Social Sentiment Sentinel

## When to Apply
Use when monitoring brand sentiment, tracking competitor mentions, or identifying trend shifts across social platforms.

## Monitoring Framework

### Primary Channels

| Platform | Data Source | Key Signals |
|----------|------------|-------------|
| Reddit | Subreddits + posts | Product complaints, feature requests |
| Twitter/X | Search API + trends | Brand mentions, industry keywords |
| LinkedIn | Company page + groups | Competitive hiring, product launches |
| GitHub | Issues + Discussions | Technical trends, integration requests |
| Hacker News | Search + comments | Product reviews, industry news |

### Signal Categories

```
┌─ Positive ──────────────────────────────┐
│ • Product praise / recommendation       │
│ • Feature requests (high demand signal) │
│ • Comparison mentions (vs competitors)  │
└─────────────────────────────────────────┘

┌─ Negative ──────────────────────────────┐
│ • Bug reports / complaints              │
│ • Migration from our product            │
│ • Pricing complaints                    │
└─────────────────────────────────────────┘

┌─ Opportunity ───────────────────────────┐
│ • Unmet needs expressed                 │
│ • "Is there a tool that can..."         │
│ • Competitive weakness mentioned        │
└─────────────────────────────────────────┘
```

### Alert Rules

| Priority | Condition | Response |
|----------|-----------|----------|
| P0 | Brand crisis (+1000 negative mentions in 1h) | Immediate alert |
| P1 | Competitor launches major product | Growth team notify |
| P2 | Trending topic in our domain | Auto-create content brief |
| P3 | Feature request with >100 upvotes | Log as product input |
