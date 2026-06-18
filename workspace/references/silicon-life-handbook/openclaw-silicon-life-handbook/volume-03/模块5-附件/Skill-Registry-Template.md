# Skill Registry 台账模板

> 用途：把 skill 从“目录存在”升级成“能力被治理”。

## 字段说明
- `skill_name`: skill 名称，必须与目录名一致
- `owner`: 负责人（agent/person）
- `layer`: 通用基础 / 角色专属 / 业务线 / 组织治理
- `location`: workspace/global/extraDir/plugin
- `status`: experimental / active / deprecated / archived
- `summary`: 一句话能力定义
- `trigger_summary`: 典型触发语义
- `negative_triggers`: 不适用边界
- `requires`: 依赖（bins/env/config）
- `assets`: 关键 references/scripts/assets 概览
- `maturity_level`: L0-L5
- `sample_tasks`: 代表任务
- `review_cycle`: 审核周期
- `last_reviewed_at`: 最近审核时间
- `notes`: 备注

## Markdown 表格版
| skill_name | owner | layer | location | status | maturity_level | summary | trigger_summary | negative_triggers | requires | review_cycle | last_reviewed_at | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| example-skill | kunlun | 组织治理 | workspace | experimental | L2 | 示例技能 | 用户提到XX时触发 | 不用于YY | bins:[] env:[] config:[] | monthly | 2026-03-29 | 待补测试 |

## YAML 版（适合后续程序化）
```yaml
- skill_name: example-skill
  owner: kunlun
  layer: 组织治理
  location: workspace
  status: experimental
  summary: 示例技能
  trigger_summary:
    - 用户提到XX
    - 用户要求YY
  negative_triggers:
    - 不用于ZZ
  requires:
    bins: []
    env: []
    config: []
  assets:
    references: []
    scripts: []
    assets: []
  maturity_level: L2
  sample_tasks:
    - 示例任务1
  review_cycle: monthly
  last_reviewed_at: 2026-03-29
  notes: 待补召回测试
```

## 最小治理规则
1. 没进台账 = 视为不存在
2. 没 owner = 不允许推广
3. 没 negative triggers = 不允许升为 active
4. 没有最近一次 review 日期 = 视为待审
5. 连续两轮 review 无价值增量 = 进入 deprecated 候选
