---
type: concept
tags: [concept, AgentRL]
created: 2026-07-23
updated: 2026-07-23
status: evolving
---

# GRPO

Group Relative Policy Optimization，DeepSeek 提出的 RL 训练 variant。

## 核心机制

- 每个 prompt 采样一组 response，组内计算 advantage
- 去掉 value model，用组内归一化替代 critic
- 训练更轻量，无需独立的价值网络

## 在 Agent RL 场景的挑战

- 组内 reward 全对/全错 → advantage=0 → 这批数据白训
- 模型越强，简单题越容易全对，有效样本越来越少
- **解法**：DAPO 的 dynamic sampling

## 与 PPO 的关系

PPO 是 RLHF 基础方法，维护参考策略做 KL 约束，用 clip 限制更新幅度。GRPO 是 PPO 的简化变体，去掉了 value model。

## 相关来源

- [[Knowledge/wiki/资料/Agent RL 论文 Polar]]
- [[Knowledge/wiki/资料/GRPO 踩坑合集]]

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/Agent RL Collapse]]
