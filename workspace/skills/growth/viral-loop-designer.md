# Viral Loop Designer

## When to Apply
Use when designing share mechanics, referral programs, or any social propagation mechanism.

## Framework

### 1. Viral Loop Anatomy

```
                 ┌─────────────────────┐
                 │  User experiences   │
                 │  core value         │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │  Trigger to share   │
                 │  (natural moment)   │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │  Share action       │
                 │  (1-click, low friction) │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │  New user lands     │
                 │  (same experience)  │
                 └─────────────────────┘
```

### 2. Design Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Value First** | Only ask to share AFTER user gets value | Dropbox: after file saved |
| **Shared Benefit** | Both sides get value from share | Uber: both get $5 |
| **Identity Signal** | Sharing reflects well on user | Strava: look how fit I am |
| **Low Friction** | 1-tap share, no typing | TikTok: share video in 1 tap |
| **Natural Timing** | Ask when user is happiest | After successful outcome |

### 3. K-factor Calculation

```
K-factor = i × c
  i = invitations sent per user
  c = conversion rate of invitations

K > 1.0  →  Exponential growth (viral)
K = 1.0  →  Linear growth (stable)
K < 1.0  →  Decay (need other channels)
```

### 4. Viral Coefficient Optimization

```
Target: i=2.0, c=50% → K=1.0

Levers to pull:
- Increase i: placement, timing, incentive
- Increase c: landing page, onboarding, incentive symmetry

Common K-factor benchmarks:
  B2B SaaS referral: 0.1-0.5
  Consumer app: 0.5-2.0
  Social platform: 1.0-3.0+
```
