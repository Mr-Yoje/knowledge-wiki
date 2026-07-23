---
type: source
tags: [source-summary, AgentRL]
source_name: "TAO-RL: Tool-Aware Optimization with Entropy Guidance"
author: "Hongye Cao, Nuo Yan, Haoyuan Deng, et al."
url: "https://arxiv.org/abs/2606.03762"
created: 2026-07-23
updated: 2026-07-23
status: initialized
---

# Agent RL 论文 TAO-RL

## 来源信息

- **论文**: Tool-Aware Optimization with Entropy Guidance for Efficient Agentic RL
- **arXiv**: 2606.03762
- **时间**: 2026.06

## 一句话摘要

从数据筛选和熵奖励两个维度解决 Agent RL 的样本效率和探索问题。

## 解决的问题

集成外部工具会破坏训练稳定性：过度依赖工具导致输入分布偏移，过于保守又限制了有效探索。

## 关键结构

**轨迹过滤**：
- 丢弃所有工具调用都失败的轨迹
- 丢弃所有 rollout 全部正确或全部错误的轨迹（advantage 退化为 0）
- 只保留既成功执行了工具、又有判别性信息的轨迹

**熵引导探索奖励**：
- 在 tool call 之后的 token 位置引入熵奖励
- 鼓励模型在关键决策点探索更多样化的推理路径

## 可沉淀知识点

- 7 个推理 benchmark × 3 种模型规模上超越现有方法
- 轨迹过滤和熵奖励两者互为强化
- 解决了「样本稀疏 + 探索不足」的问题

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/Agent RL 信用分配]]
