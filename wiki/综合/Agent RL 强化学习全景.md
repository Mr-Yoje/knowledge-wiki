---
type: synthesis
tags: [synthesis, AgentRL]
created: 2026-07-23
updated: 2026-07-23
status: evolving
---

# Agent RL 强化学习全景

Agent RL（Agentic Reinforcement Learning）是指将强化学习应用于 LLM Agent 在工具使用、多步推理、代码执行等场景中的训练方法。

## 核心思想

Agent 不再仅靠 SFT 模仿人类示范，而是通过「在环境中执行动作 → 获得反馈 → 更新策略」的闭环来学习。

## 与传统 RLHF 的对比

| 维度 | 传统 RLHF (PPO/GRPO) | Agent RL |
|---|---|---|
| 动作空间 | 下一个 token 生成 | tool call + code exec + multi-turn dialog |
| 奖励来源 | 人工/奖励模型打分 | 环境反馈（API 返回值、测试通过率） |
| rollout 长度 | 单次回答（数百 token） | 多轮交互（数千 token + 工具调用） |
| 信用分配 | 整段 reward → 每个 token | 需区分哪一步工具调用决定了成败 |
| 训练稳定性 | 相对成熟（有 KL 约束） | 容易 collapse，正在研究中 |

## 时间线

- **RLHF 时代**
  - PPO（带 value model）
  - GRPO（组内归一化，去 value model）
- **Agent RL 时代**
  - infra 层面：Polar（解耦 harness + trainer）
  - 数据/环境层面：EnvFactory（自动建环境）、ToolVerse（大规模 MCP）
  - 算法层面：TAO-RL（轨迹过滤+熵奖励）、DISA（分布匹配）

## 相关来源

- [[Knowledge/wiki/资料/Agent RL 论文 Polar]]
- [[Knowledge/wiki/资料/Agent RL 论文 EnvFactory]]
- [[Knowledge/wiki/资料/Agent RL 论文 TAO-RL]]
- [[Knowledge/wiki/资料/Agent RL 论文 ToolVerse]]
- [[Knowledge/wiki/资料/Agent RL 论文 Collapse]]
- [[Knowledge/wiki/资料/Agent RL 论文 DISA]]

## 相关页面

- [[Knowledge/wiki/概念/GRPO]]
- [[Knowledge/wiki/概念/Agent RL 信用分配]]
- [[Knowledge/wiki/概念/Agent RL Collapse]]
- [[Knowledge/wiki/综合/Agent RL 实战经验]]
