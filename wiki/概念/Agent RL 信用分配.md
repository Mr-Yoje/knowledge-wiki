---
type: concept
tags: [concept, AgentRL]
created: 2026-07-23
updated: 2026-07-23
status: evolving
---

# Agent RL 信用分配

多步工具使用中，中间某一步的 tool call 做对了还是做错了，很难从最终的 reward 反推。

## 问题描述

Agent 先调 API 获取数据，再调另一个 API 分析，最后算结果。如果最后结果错了，是数据获取错了还是分析错了？一步 reward 无法区分。

## 现有解法

- **ToolVerse 的 Turn-Aware Relative Advantage**：细粒度计算每一步的 advantage
- **TAO-RL 的熵引导奖励**：在 tool call 之后的 token 位置引入熵奖励，重塑 advantage

## 相关来源

- [[Knowledge/wiki/资料/Agent RL 论文 ToolVerse]]
- [[Knowledge/wiki/资料/Agent RL 论文 TAO-RL]]

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/Agent RL Collapse]]
