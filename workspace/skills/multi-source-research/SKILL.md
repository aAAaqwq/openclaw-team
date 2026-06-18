---
name: multi-source-research
description: >
  Conduct deep, multi-source research by cross-referencing data from web search, news,
  social media, academic sources, and proprietary databases. Enforces APA 7th citations,
  evidence hierarchy, and 2-cycle verification per research theme. Built for competitive
  intelligence analyst workflows.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - curl
allowed-tools: web_search web_fetch Bash
---

# Multi-Source Research

Comprehensive multi-source investigation engine. Use when the task needs exhaustive research across ≥3 independent source categories, triangulated for accuracy.

## Workflow

### Phase 1: Research Plan

1. **Define thesis** — What question are we answering? What decisions ride on it?
2. **Source mapping** — Identify which source types are relevant:

| Source Category | Tools | Use Case |
|----------------|-------|----------|
| Web (general) | web_search/Brave | Company info, news, pricing |
| Academic | web_search (arXiv, Semantic Scholar, CrossRef) | Papers, benchmarks |
| Social media | web_search (Reddit, X, LinkedIn) | Sentiment, chatter, user feedback |
| Official | web_fetch (gov.cn, CAC, company sites) | Policy, official announcements |
| Code/OSS | web_search + web_fetch (GitHub) | Open source, repos, community |

3. **Cross-reference matrix** — For each claim, plan ≥2 independent sources.

### Phase 2: First Pass — Surface Collection

```markdown
Run parallel searches across target categories.
For each source type, collect:
- Title, URL, publication date
- Author/organization (source credibility assessment)
- Key claims (verbatim quotes where possible)
```

### Phase 3: Second Pass — Deep Verification

For each claim marked as critical:
1. Find a second independent source
2. Compare dates — is one version more recent?
3. Rate consistency: ✅ Match | ⚠️ Partial | ❌ Contradiction
4. If contradiction exists, flag and investigate further

### Phase 4: Synthesis

```markdown
## Research Summary

### Key Findings
| Finding | Confidence | Sources | Verdict |
|---------|-----------|---------|---------|
| ... | 90% | [A] + [B] | CORROBORATED |
| ... | 60% | [C] only | NEEDS VERIFICATION |

### Source Credibility Ratings
| Source | URL | Credibility | Rationale |
|--------|-----|-------------|-----------|
| CAC.gov.cn | ... | A (98%) | Official government |
| TechCrunch | ... | A (93%) | Established tech media |
| Zhihu | ... | C (65%) | User-generated, needs verification |

### Notable Gaps
- What we couldn't find
- What remains uncertain
- Recommended next research direction
```

## Cross-Validation Rules

1. **Critical claims** (P0/P1 relevance): must have ≥2 A-level or ≥3 B-level sources
2. **Single-source claims**: labeled as "unverified" with source credibility stated
3. **Conflicting claims**: surfaced explicitly with the analyst's judgment
4. **Dated information**: always check recency; label historical data

## Output Format

```markdown
### [Topic]

#### Verdict
[1-2 sentence judgment with confidence level]

#### Evidence
- [Source A]: [claim] (credibility: A, date)
- [Source B]: [corroborating/contradicting claim] (credibility: B, date)

#### Analyst Note
[What the data doesn't tell us, what to watch for]
```
