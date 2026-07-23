---
type: source
tags: [source-summary, AgentRL]
source_name: "EnvFactory: Scaling Tool-Use Agents via Executable Environments Synthesis"
author: "Minrui Xu, Zilin Wang, Mengyi Deng, et al."
url: "https://arxiv.org/abs/2605.18703"
created: 2026-07-23
updated: 2026-07-23
status: initialized
---

# Agent RL 论文 EnvFactory

## 来源信息

- **论文**: EnvFactory: Scaling Tool-Use Agents via Executable Environments Synthesis and Robust RL
- **arXiv**: 2605.18703
- **时间**: 2026.05

## 一句话摘要

自动构建可执行 tool 环境 + 合成自然多轮 trajectory 的全自动化框架。

## 解决的问题

Agent RL 面临两个瓶颈：缺乏可扩展的鲁棒执行环境，以及缺乏捕捉隐式人类推理的真实训练数据。

## 关键结构

1. 从真实资源自主探索和验证有状态、可执行工具环境
2. 拓扑感知采样，生成长链多步任务
3. 校准精炼，将指令序列转化为接近真实人类意图的自然查询

## 可沉淀知识点

- 仅用 85 个验证环境 × 7 个领域，生成 2575 条高质量轨迹
- 环境量是前人工作的 1/5，但效果更好
- Qwen3 在 BFCLv3 提升 +15%，MCP-Atlas 提升 +8.6%
- 解决了「训练环境从哪里来」的问题

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
