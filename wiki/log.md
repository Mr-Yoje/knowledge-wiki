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

## 2026-07-24｜AgentEval 页面位置修正

将 [[Knowledge/wiki/概念/AgentEval评估全景]] 移至 [[Knowledge/wiki/综合/AgentEval评估全景]]（实操指南型内容，放在概念不合适）

- 修改元数据：type: concept → type: guide
- 更新 index.md：综合下新增条目，资料下新增 AgentEval最佳实践 链接
- 配套页面 [[Knowledge/wiki/资料/AgentEval最佳实践]] 已在资料目录

## 2026-07-28｜Agent Memory 框架调研

### Agent Memory 框架全景

完成三大 Agent Memory 框架（Mem0 / LangGraph / Letta Code）的深度调研。

- 新增综合页：
  - [[Knowledge/wiki/综合/Agent Memory框架全景]] — 三框架架构/原理/流程/对比矩阵
- 新增资料页：
  - [[Knowledge/wiki/资料/Trustcall]] — LangGraph 生态的 JSON Patch 精确记忆更新工具
- 更新概念页：
  - [[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节]] — 补充 2026年4月新算法信息，增加与综合页的链接
  - [[Knowledge/wiki/概念/Mem0的Add模式与冲突处理机制]] — 增加与综合页的链接
- 关键结论：
  1. ADD-only 优于 UPDATE 已成共识（Mem0 新算法 LoCoMo 92.5）
  2. Letta Dreaming + LangGraph Background 表明后台学习是正确方向
  3. 多信号检索（语义+BM25+实体+时间）正在替代纯向量检索
  4. 记忆的可编辑性和版本化正在成为新刚需

### 当前待办 / 后续方向

- [ ] Agent Memory 框架对比页（在综合页基础上提取为独立对比页）
- [ ] Mem0 新算法的原理更深挖（研究论文阅读）
- [ ] Letta Code MemFS 的 git 操作层面深入分析

## 2026-07-28｜Cognee 深入调研与 Mem0 对比

### Cognee 调研与对比页

- 新增资料页：
  - [[Knowledge/wiki/资料/Cognee]] — 三层架构、四大操作、Postgres 全能化、Improve 蒸馏机制
- 新增对比页：
  - [[Knowledge/wiki/对比/Cognee与Mem0对比]] — 8 维度对比表 + 选型指南 + 常见误区
- 更新：
  - [[Knowledge/wiki/综合/Agent Memory框架全景]] — 加入 Cognee 引用
  - [[Knowledge/wiki/index.md]] — 新增对比分类、Cognee 资料页链接
- 关键结论：
  1. Cognee 以图谱为第一存储范式，与 Mem0 的多信号融合形成根本性路线差异
  2. Postgres 全能化（关系+向量+图谱+缓存在一张 PG 上）是 Cognee 1.0 的关键差异化
  3. Cognee 适合关系推理场景，Mem0 适合精准事实召回场景
  4. 向量优先派（Mem0） vs 图谱优先派（Cognee）的分化正在加速
