---
type: source
tags: [source-summary, AgentRL]
source_name: "ToolVerse: Unlocking Massive Environments for Agentic RL"
author: "Shuaiyu Zhou, Fengpeng Yue, Zengjie Hu, et al."
url: "https://arxiv.org/abs/2607.15660"
created: 2026-07-23
updated: 2026-07-23
status: initialized
---

# Agent RL 论文 ToolVerse

## 来源信息

- **论文**: ToolVerse: Unlocking Massive Environments and Long-Horizon Tasks for Agentic RL
- **arXiv**: 2607.15660
- **时间**: 2026.07

## 一句话摘要

基于约 400 个真实 MCP Server 构建的大规模 Agent RL 训练框架。

## 解决的问题

LLM Agent 在紧凑明确定义的场景中表现良好，但在大规模、多样化的真实环境中缺乏鲁棒性。

## 关键结构

1. 从约 400 个真实 MCP 服务自动构建可执行环境，涉及约 4500 个工具
2. Dynamic Unlocking Sampling 基于工具依赖图生成长链多步任务（GUST 数据集）
3. Turn-Aware Relative Advantage 算法解决长序列信用分配难题

## 可沉淀知识点

- 规模最大（400 MCP / 4500 tools）
- 工具依赖图 + 动态采样是创新点
- Turn-Aware Advantage 是信用分配的最新解法
- 解决了「环境规模和任务复杂度」的问题

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/Agent RL 信用分配]]
