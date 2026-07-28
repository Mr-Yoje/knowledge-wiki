---
type: comparison
tags: [comparison, cognee, mem0, memory, ai-memory, framework-comparison]
created: 2026-07-28
updated: 2026-07-28
status: evolving
---

# Cognee 与 Mem0 对比

## 一句话结论

**Cognee 适合"需要关系推理和结构化知识"的场景**（知识图谱、因果分析、企业知识库）；**Mem0 适合"需要高精度事实召回和跨框架灵活性"的场景**（个性化助手、客服、多 Agent 系统）。两者在"向量 vs 图谱"的核心哲学上存在根本差异。

## 定义

### Cognee

开源 AI Agent 记忆平台，以知识图谱为核心存储范式（29.5k ⭐）。详情见 [[Knowledge/wiki/资料/Cognee]]。

### Mem0

AI Agent 的通用记忆层，以"多信号融合检索（语义+BM25+实体+时间）"为核心设计（25k+ ⭐）。详情见 [[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节]]。

## 全方位对比

| 维度 | Cognee | Mem0 |
|------|--------|------|
| **存储核心** | 知识图谱（图谱 > 向量） | 多信号融合（语义向量+BM25+实体+时间） |
| **检索方式** | 自动路由 → 图谱完成，向量是补充 | 语义 + BM25 + 实体 boost + 时间推理 并行融合 |
| **写入方式** | remember(永久/会话) → improve(丰富) | add(ADD-only) → 显式 update/delete |
| **会话记忆** | 缓存层（local fs / Redis），可由 improve 桥接为永久 | Session 级 user_id/run_id 隔离 |
| **去重机制** | 图谱构建时由实体提取和链接处理 | LLM 驱动的 ADD-only 模式（+ 显式 update/delete） |
| **自进化** | ✅ Improve 四阶段：反馈权重→持久化→蒸馏→丰富 | ⚠️ 显式 update + feedback 循环（Platform） |
| **Agent 学习** | 蒸馏（curator/writer/rejecter 三级评估） | LLM 提取事实（单次 ADD-only） |
| **关系推理** | ✅ 强（图谱原生） | ⚠️ 弱（实体 boost 辅助） |
| **时序推理** | ⚠️ 部分（auto-route 有 temporal 策略） | ✅ 强（时间感知检索，dated instance 排名） |
| **多模态输入** | ✅ 丰富（PDF/图片/音视频/URL/S3/文档） | ❌ 仅文本 |
| **本地运行** | ✅ Docker / pip 全本地可跑 | ✅ pip / npm 全本地 |
| **Postgres 全能** | ✅ 一张 Postgres 搞定关系+向量+图谱+缓存 | ❌ 需要独立向量库（Qdrant/PGVector 等） |
| **Agent 插件** | OpenClaw / Claude Code 官方插件 | Claude Code / Cursor 官方插件 |
| **MCP 支持** | ✅ 原生 MCP Server | ✅ 支持 |
| **框架集成** | OpenClaw + Claude Code + MCP | LangGraph + CrewAI + AutoGen + Claude Code + Cursor |
| **记忆可编辑性** | ⚠️ 通过 API 或图谱操作 | ⚠️ update/delete API |
| **研究论文** | 有（arXiv:2505.24478） | 有（arXiv:2504.19413） |
| **估值/背景** | 开源社区驱动 | YC 孵化，有商业版 |
| **语言** | Python（核心）+ TS + Rust 客户端 | Python + TypeScript |

## 什么时候选哪个

### ✅ 选 Cognee

- **你需要回答关系型问题**：如"A 和 B 之间有什么关系？"、"这个事件的根本原因是什么？"
- **你处理的是结构化知识**：企业文档库、研究论文集、代码库——内容之间有明确的关联关系
- **你需要多模态输入**：PDF + 图片 + 音视频等多种格式需要统一管理
- **你希望一张 Postgres 搞定所有存储**：不想维护多套数据库
- **你需要强化的自进化机制**：希望 Agent 能通过反馈和改进蒸馏持续优化

### ✅ 选 Mem0

- **你需要高精度的事实召回**：用户说了什么偏好、什么配置、什么事实——准确找到那条"对"的记忆
- **你需要跨框架灵活性**：同一套记忆可能同时服务 LangGraph Agent + CrewAI Agent + 纯 LLM 调用
- **你需要时间敏感检索**："最近发生了什么"、"用户以前喜欢什么"这类带时间语境的查询
- **你希望集成最简单**：`pip install mem0ai` + 几行代码即可，零配置
- **你主要处理对话/用户偏好/行为模式**：这些场景语义匹配比关系推理更重要

### 常见误区

- **误区：Cognee 的图谱检索比 Mem0 的向量检索"更高级"** → 两者解决不同问题。Cognee 擅长关系推理，但如果是"用户 A 之前说过什么偏好"这类纯事实召回，Mem0 的精度更高。
- **误区：Mem0 没有图谱能力** → Mem0 确实有实体链接和图谱 boost，但它以向量为主、图谱为辅；Cognee 反过来。
- **误区：两者只能二选一** → 技术上可以同时使用（Cognee 做结构化知识库，Mem0 做短期个性化偏好），但实际场景中重叠需求不多。

## 与知识库主线的关系

Agent Memory 框架全景中的"外挂记忆层"阵营开始分化出两条路线：
- **向量优先派**：Mem0、Supermemory、Honcho — 以语义匹配为核心
- **图谱优先派**：Cognee、m_flow — 以关系推理为核心

两条路线目前没有明显优劣之分，适用场景不同。但对于 Agent 长期记忆这个命题，"关系推理"的价值随着记忆量的增长而加速显现——单纯的"找相似"在大量记忆面前会退化。这是 Cognee 图谱优先路线的长期优势点。

## 相关来源

- Cognee GitHub：https://github.com/topoteretes/cognee
- Cognee 论文：https://arxiv.org/abs/2505.24478
- Mem0 GitHub：https://github.com/mem0ai/mem0
- Mem0 论文：https://mem0.ai/research

## 相关页面

- [[Knowledge/wiki/资料/Cognee]] — Cognee 详细资料页
- [[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节|Mem0 架构与知识图谱技术细节]]
- [[Knowledge/wiki/综合/Agent Memory框架全景|Agent Memory 框架全景]] — 三大框架全景
