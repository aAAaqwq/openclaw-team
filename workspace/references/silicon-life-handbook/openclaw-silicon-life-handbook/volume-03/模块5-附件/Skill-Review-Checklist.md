# Skill Review 审核清单

> 用途：防止低质量 skill 污染能力生态。

## A. 路由层（召回）
- [ ] `name` 与目录名一致
- [ ] `description` 清晰说明“做什么”
- [ ] `description` 写明“什么时候用”
- [ ] `description` 写明“什么时候别用”
- [ ] 包含典型触发表达
- [ ] 不与现有 skill 高度重叠

## B. 指挥层（SKILL.md）
- [ ] 主流程是 SOP，不是散文
- [ ] 有编号步骤
- [ ] 有条件分支
- [ ] 有输出合同（output contract）
- [ ] 有 references 读取时机
- [ ] 有 scripts 调用时机（若存在）

## C. 资源层（references / scripts / assets）
- [ ] references 扁平、可定位
- [ ] scripts 小而专
- [ ] assets 仅放最终产物脚手架
- [ ] 不存在无关 README/CHANGELOG/INSTALL 类噪音文件

## D. 安全与治理
- [ ] 写明 negative triggers
- [ ] 高风险动作是否需要确认/审批
- [ ] 是否依赖 exec / secrets / 外部 API
- [ ] 是否需要 metadata gating（bins/env/config/os）
- [ ] 是否已记录 owner
- [ ] 是否已记录进 registry

## E. 质量与评估
- [ ] 至少 5 条应触发样例
- [ ] 至少 5 条不应触发样例
- [ ] 至少 3 条边界样例
- [ ] 至少一次 transcript 回放
- [ ] 明确 maturity level
- [ ] 明确 review 周期

## 审核结论
- 通过 / 退回 / 限定试运行
- 退回原因：
- 需补项：
- 下一次复审日期：
