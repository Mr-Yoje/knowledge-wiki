---
type: source
tags: [source-summary, AgentRL]
source_name: "Why Multi-Step Tool-Use Reinforcement Learning Collapses"
author: "Yupu Hao, Zhuoran Jin, Huanxuan Liao, et al."
url: "https://arxiv.org/abs/2606.26027"
created: 2026-07-23
updated: 2026-07-23
status: initialized
---

# Agent RL 论文 Collapse

## 来源信息

- **论文**: Why Multi-Step Tool-Use Reinforcement Learning Collapses and How Supervisory Signals Fix It
- **arXiv**: 2606.26027
- **时间**: 2026.06

## 一句话摘要

系统分析了 RL 在多步工具使用中为什么会 crash，以及如何用监督信号补救。

## 解决的问题

RL 单独训练多步工具使用时常导致 catastrophic collapse，性能突然彻底崩溃。

## 关键结构

**核心发现**：
- 崩溃不是 reward 先掉，而是策略先漂坏，reward 只是结果
- 根因是控制 token（如 tool call 格式标记）的概率出现意外 spike
- 底层工具使用能力还在，只是被错误的输出格式掩盖了

**解决方案**：
- 对比多种监督信号：Off-policy supervision、Hint-based guidance、Error example 等
- 最佳方案：SFT 和 RL 交替训练（Interleaving），大幅提升稳定性

## 可沉淀知识点

- SFT+RL 交替训练是最稳定的模式
- 但交替训练在 OOD 场景下会性能下降
- 理解了「为什么崩」的机理
- 先盯 KL/entropy/格式错误率比盯 reward 更早发现问题

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/Agent RL Collapse]]
- [[Knowledge/wiki/综合/Agent RL 实战经验]]
