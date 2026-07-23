---
type: synthesis
tags: [synthesis, AgentRL]
created: 2026-07-23
updated: 2026-07-23
status: evolving
---

# Agent RL 实战经验

## 训练前冒烟检查清单

1. **Ratio ≈ 1** — 验证初始状态下策略和采样一致
2. **Advantage 非零比例** — 确保不是所有样本全对/全错
3. **Verifier 体检** — 奖励信号的可靠性和区分度
4. **小步更新测试** — 跑几 step 看是否有梯度异常
5. **Holdout 对齐** — 推理引擎和训练 forward 的 log-prob 是否一致

## 监控指标优先级

比 reward **更早变化**的预警指标：

- **KL divergence** — 策略漂移的早期信号
- **Entropy** — 探索/利用的平衡
- **输出长度分布** — 是否趋向于越写越长
- **格式错误率** — tool call 格式是否开始混乱
- **组内 reward 方差** — 样本信息量

等平均 reward 掉下来，往往已经晚了。

## 踩坑排查顺序

出问题时不要一次改多个超参：

1. 先查 **log-prob 对齐** — 训练和推理是否一致
2. 再查 **reward 信号** — reward 的分布和区分度
3. 最后调其他超参

## GRPO 特有的坑

- 组内 reward 全对/全错 → advantage=0 → 白训
- 按回答长度归一化 → 模型越写越长（Dr.GRPO 指出的副作用）
- 除以组内 std → 简单题和极难题在梯度中占过大权重
- 训练和推理 log-prob 不对齐 — vLLM 和训练 forward 的精度、tokenizer、mask 差异

## 相关来源

- [[Knowledge/wiki/资料/GRPO 踩坑合集]]

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/GRPO]]
- [[Knowledge/wiki/概念/Agent RL Collapse]]
