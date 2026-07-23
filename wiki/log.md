# 操作日志

## 2026-07-23｜Agent RL 专题导入

### Agent RL 全景调研

从 arXiv 收集 6 篇 2025-2026 最新论文 + 1 篇小红书 GRPO 踩坑笔记，完成 Agent RL 领域调研。

- 新增综合页：
  - [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
  - [[Knowledge/wiki/综合/Agent RL 实战经验]]
- 新增概念页：
  - [[Knowledge/wiki/概念/GRPO]]
  - [[Knowledge/wiki/概念/Agent RL 信用分配]]
  - [[Knowledge/wiki/概念/Agent RL Collapse]]
- 新增资料页：
  - [[Knowledge/wiki/资料/Agent RL 论文 Polar]]
  - [[Knowledge/wiki/资料/Agent RL 论文 EnvFactory]]
  - [[Knowledge/wiki/资料/Agent RL 论文 TAO-RL]]
  - [[Knowledge/wiki/资料/Agent RL 论文 ToolVerse]]
  - [[Knowledge/wiki/资料/Agent RL 论文 Collapse]]
  - [[Knowledge/wiki/资料/Agent RL 论文 DISA]]
  - [[Knowledge/wiki/资料/GRPO 踩坑合集]]

关键结论：Agent RL 核心挑战是信用分配、训练 collapse、环境可扩展性、样本稀疏和 log-prob 对齐。当前最新解法集中在解耦基础设施（Polar）、自动化环境（EnvFactory）、样本筛选+熵奖励（TAO-RL）、大规模环境（ToolVerse）、分布匹配（DISA）和交替训练（Collapse 论文）。

## 待办 / 后续方向

- [ ] 补充 PPO 概念页
- [ ] 补充 RLHF 和 Agent RL 的对比页

## 2026-07-23｜Ontology 本体论专题导入

### Palantir Ontology 调研

从 Palantir 官方文档（Overview、Why Ontology、Core Concepts）提取核心内容，完成 Ontology 本体论专题调研。

- 新增综合页：
  - [[Knowledge/wiki/综合/Ontology 本体论专题全景]]
- 新增概念页：
  - [[Knowledge/wiki/概念/Ontology 决策四要素]]
  - [[Knowledge/wiki/概念/Ontology 数据体系]]
  - [[Knowledge/wiki/概念/Ontology 与 AI Agent 的关系]]
- 新增资料页：
  - [[Knowledge/wiki/资料/Palantir Ontology Overview]]
  - [[Knowledge/wiki/资料/Palantir Why Ontology]]
  - [[Knowledge/wiki/资料/Palantir Core Concepts]]

关键结论：Palantir Ontology 是决策中心（decision-centric）的运营层，核心四要素为 Data、Logic、Action、Security。在 AI Agent 时代，Ontology 提供了比 RAG 更丰富的上下文，Agent 可以通过 Ontology 驱动的工具安全地查询、推理和行动。

## 待办 / 后续方向

- [ ] 对比 Ontology 与传统知识图谱
- [ ] Ontology 与 GraphRAG 的关系
