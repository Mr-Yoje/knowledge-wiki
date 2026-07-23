---
type: concept
tags: [concept, AgentRL]
created: 2026-07-23
updated: 2026-07-23
status: evolving
---

# Agent RL Collapse

Agent RL 训练中的灾难性崩溃现象。

## 现象描述

RL 单独训练多步工具使用时，模型会突然性能崩溃（catastrophic collapse），tool-invocation 结构和格式彻底损坏。

## 根因

- **不是 reward 先掉，而是策略先漂坏**，reward 只是结果
- 控制 token（如 tool call 格式标记）的概率出现意外 spike
- 底层工具使用能力并未丢失，只是被错误的输出格式掩盖了

## 现有解法

- **SFT+RL 交替训练**（Interleaving）：最稳定的方案，大幅提升稳定性
- **代价**：交替训练在格式和内容 OOD 场景下性能下降

## 与 GRPO 踩坑的关系

GRPO 特有的组内 reward 全对/全错导致 advantage 退化为 0 的问题，也是 collapse 的一种表现形式。

## 相关来源

- [[Knowledge/wiki/资料/Agent RL 论文 Collapse]]
- [[Knowledge/wiki/资料/GRPO 踩坑合集]]

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/GRPO]]
- [[Knowledge/wiki/综合/Agent RL 实战经验]]
