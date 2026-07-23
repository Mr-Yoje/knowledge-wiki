---
type: source
tags: [source-summary, AgentRL]
source_name: "DISA: Offline Importance Sampling for Distribution-Matching LLM-RL"
author: "Shaobo Wang, Yujie Chen, Yafeng Sun, et al."
url: "https://arxiv.org/abs/2605.17295"
created: 2026-07-23
updated: 2026-07-23
status: initialized
---

# Agent RL 论文 DISA

## 来源信息

- **论文**: DISA: Offline Importance Sampling for Distribution-Matching LLM-RL
- **arXiv**: 2605.17295
- **时间**: 2026.05

## 一句话摘要

用 offline 重要性采样解耦 partition function 估计，避免 reward 坍塌到单一模式。

## 解决的问题

标准 reward-max RL 会把策略推向最容易获得高 reward 的单一路径，导致模式坍塌。Distribution-matching RL 追求在整个解空间上均匀分配概率，但传统方法把 partition function 估计和 policy 放在一起学，互相干扰。

## 关键结构

1. Offline 先采样 proposal 轨迹
2. 用重要性采样估计 partition function
3. 冻结 partition function 估计值，再开始 policy 优化
4. 数据和梯度完全分离，可独立诊断

## 可沉淀知识点

- 6 个数学 + 3 个代码 benchmark 匹配或超越 FlowRL
- 数学平均超越 GRPO/GSPO
- 超过 LoRASFT 蒸馏最多 13.8 Mean@8 分
- LLM 做 judge 评估发现 DISA 保留了更多的策略多样性
- 解决了「策略多样性丧失」的问题

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/GRPO]]
