# Skill Evaluation 测试集模板

> 用途：测试 skill 的召回、误触发与结果质量。

## 一、测试维度
1. 召回测试（该触发时会不会触发）
2. 误触发测试（不该触发时会不会乱触发）
3. 边界测试（相邻任务是否区分得清）
4. 结果质量测试（触发后结果是否更稳）

## 二、最小样本结构
### A. 应触发样例（建议10条）
| id | user_request | expected_skill | 备注 |
|---|---|---|---|
| P1 | 帮我把这篇长文改成公众号风格 | wechat-article-pro | 公号改写 |
| P2 | 给我整理成会议纪要 | meeting-minutes-pro | 纪要类 |

### B. 不应触发样例（建议10条）
| id | user_request | should_not_trigger | 正确去向 |
|---|---|---|---|
| N1 | 帮我审一下合同风险 | wechat-article-pro | 合同/法务 skill |
| N2 | 修一下这个 TypeScript 报错 | meeting-minutes-pro | 开发 skill |

### C. 边界样例（建议5条）
| id | user_request | competing_skills | expected_winner | 说明 |
|---|---|---|---|---|
| B1 | 帮我把晨会内容整理成一条公众号文章 | meeting-minutes-pro / wechat-article-pro | 视上下文而定 | 纪要与内容改写边界 |

## 三、结果质量检查
- [ ] 输出结构是否符合预期
- [ ] 是否减少遗漏项
- [ ] 是否减少返工
- [ ] 是否显著降低 AI 味/格式漂移/流程漂移
- [ ] 是否引导模型读对了 references / 调对了 scripts

## 四、复盘记录
- 测试日期：
- skill 名称：
- 召回率：
- 误触发率：
- 主要失败原因：
- 下一轮修订建议：
