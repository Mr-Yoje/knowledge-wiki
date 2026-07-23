---
type: source
tags: [source-summary, AgentRL]
source_name: "Polar: Agentic RL on Any Harness at Scale"
author: "Binfeng Xu, Hao Zhang, Shaokun Zhang, et al."
url: "https://arxiv.org/abs/2605.24220"
created: 2026-07-23
updated: 2026-07-23
status: initialized
---

# Agent RL 论文 Polar

## 来源信息

- **论文**: Polar: Agentic RL on Any Harness at Scale
- **arXiv**: 2605.24220
- **时间**: 2026.05

## 一句话摘要

把 Agent 的 rollout harness 和 RL trainer 解耦的规模化框架。

## 解决的问题

Agent RL 训练需要自定义 harness 来管理长上下文、多轮工具调用等，但把这些 harness 接入 RL 环境接口很困难，且容易丢失重要训练信号。

## 关键结构

- 将 Agent harness 当作黑盒，代理拦截 LLM API 调用
- 记录 token 级交互，重构保留 token fidelity 的训练轨迹
- 每个 rollout 节点并行管理：预热 → 执行 → 轨迹重构 → 评估
- 解耦架构：harness / trainer / RL 算法三者独立

## 可沉淀知识点

- Qwen3.5-4B 在 SWE-Bench Verified 上用不同 harness 提升 0.6~22.6 分
- 只需简单的 GRPO 就能看到显著提升
- 解决了「怎么组织训练基础设施」的问题

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/GRPO]]
