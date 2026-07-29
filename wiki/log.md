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

## 2026-07-28｜Pi Coding Agent 深度调研

### Pi 架构与设计原理

- 新增资料页：
  - [[Knowledge/wiki/资料/Pi Coding Agent]] — 四层架构、Agent 循环、树形会话、Compaction、Extension 系统、极简主义设计哲学
- 更新：
  - [[Knowledge/wiki/index.md]] — 新增 Pi Coding Agent 资料页链接
- 关键结论：
  1. Pi 的核心理念是"原语而非功能"——极小内核 + TypeScript Extension 系统，与 Claude Code / Cursor 的"内置所有功能"形成鲜明对比
  2. 树形会话（单 JSONL 文件多分支）是 Pi 区别于所有其他 Agent 框架的独特设计
  3. Pi 是 OpenClaw 的 Agent 运行时内核（SDK 模式嵌入）

## 2026-07-29｜Pi Coding Agent 资料页补充

- 补充详情：
  - 补齐五种使用模式（新增 Ephemeral 模式）
  - 补充会话命令完整列表（/tree /fork /clone /share /export /resume /new /session /name）
  - 详细区分 tree/fork/clone 的差异对比表
  - 添加 resume 选择器快捷键和 tree 视图控制快捷键
  - 补充 Compaction 的可视化流程 ASCII 图
  - 扩展 Extension 系统细节（完整事件生命周期表 + Extension API 方法清单 + ExtensionContext 对象）
  - 补充 Skills 系统的完整加载位置和 SKILL.md 结构模板
  - 新增安装方式、安全与容器化、供应安全三个章节
  - 补充与其他 Agent 框架（Claude Code / Cursor）的详细对比表
  - 深入解读 No MCP 设计立场（CLI + README 就是天然 MCP）
  - 增加第 6 个可沉淀知识点：供应安全实践
  - 丰富相关来源链接（npm 包、Discord、pi-chat 等）
- 状态从 initialized 提升为 active

## 2026-07-29｜Agent Sandbox 技术全景调研

- 新增资料页：
  - [[Knowledge/wiki/资料/Agent Sandbox技术全景]] — 从容器隔离到 Agent 运行沙箱的完整技术脉络
- 更新：
  - [[Knowledge/wiki/index.md]] — 新增 Agent Sandbox 资料页链接
- 调研覆盖：
  1. 隔离技术三层次：Namespace（Docker）→ App Kernel（gVisor）→ microVM（Firecracker）对比
  2. 各层的逃逸难度、启动速度、资源开销、适用场景
  3. 专用 Agent 沙箱服务：E2B（基于 Firecracker，专为 Agent 设计）和 Modal Sandbox
  4. Agent 框架中的沙箱实践：OpenClaw/Gondolin、Pi 的三种容器化模式、Claude Code 内置权限弹窗
  5. 5 阶段演进脉络（2013→2025+）：传统容器→轻量VM/AppKernel→Agent工具安全→专用沙箱服务→Agent原生沙箱
  6. 10 个产品/技术的完整对比表
- 关键结论：
  1. 隔离等级与便捷性成反比
  2. Agent 沙箱正在从依赖 Agent 行为约束向基础设施层强制隔离演进
  3. 云沙箱（E2B）和本地沙箱（Gondolin）互补而非替代
  4. OpenClaw 的升级路径：Gondolin 提供最自然的逐步引入隔离方式

## 2026-07-29｜Cognee 技术原理深度调研

- 重写资料页：
  - [[Knowledge/wiki/资料/Cognee]] — 从概述页全面升级为技术原理深度文档
- 新增/大幅扩充内容：
  1. **核心架构**：三层存储（Relational/Vector/Graph）的职责分工和默认后端，Postgres 全能模式，Rust 端 crate 架构
  2. **四大核心操作**：remember（永久 vs 会话两种模式、Loader 生态）、recall（自动路由引擎+15 种 SearchType）、improve（9 阶段自改进链条）、forget（三级粒度）
  3. **图谱构建流水线**：cognify pipeline 完整步骤、Pipeline 运行机制（分层执行/串行化/可恢复/缓存控制）
  4. **检索策略体系**：15 种 SearchType 完整列表和说明
  5. **自改进机制**：反馈权重系统 + 会话蒸馏（curator/writer/rejecter 三级评估）+ Truth-Subspace Reranking（几何锚点+混合排序）
  6. **条件工程**：Global Context Index 机制（数据集级世界摘要）
  7. **多用户与权限体系**：Dataset/User/Tenant/Role/ACL + Dataset Database Handler 独立后端模式
- 更新可沉淀知识点为 6 条，新增 Truth-Subspace 和多架构洞察
- 状态从 initialized 提升为 active

## 2026-07-29｜Agent Sandbox 补充完整架构设计（五子系统）

- 新增章节：Agent Sandbox 完整架构设计（五子系统）
  - 包含 6 个核心子系统的完整设计（控制/文件/执行/网络/凭据/交付物）
- 补充内容：
  1. **控制子系统**：Agent 编排器、策略引擎、沙箱管理器、审计日志四个组件的职责定义 + 控制流示例
  2. **文件子系统**：架构图、文件操作分类表（只读/CoW/读写/不挂载四种模式）、CoW 实现细节（OverlayFS/virtio-fs）、建议的默认文件策略 JSON
  3. **执行子系统**：功能范围表、4 步执行控制层级、资源配额配置示例 JSON、命令白名单/黑名单/需审批三级控制
  4. **网络子系统**：网络模型架构图、5 种网络隔离策略表、网络策略配置示例 JSON、DNS 过滤和安全审计设计
  5. **凭据子系统**：单向注入架构、最小化/一次性/不可逆三大原则、凭据类型表
  6. **交付物子系统**：6 种交付物类型、完整交付物生命周期、4 级回写策略
  - 完整场景示例：Git clone → 修复 bug → PR → 清理的全链路六子系统协作
  - 配置总纲：完整的沙箱 JSON 配置示例
  - 五大维度一句话总结表
