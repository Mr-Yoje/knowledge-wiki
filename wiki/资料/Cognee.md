---
type: source
tags: [source-summary, cognee, memory, knowledge-graph, ai-memory]
source_name: Cognee — Open-Source AI Memory Platform for Agents
author: topoteretes
url: https://github.com/topoteretes/cognee
created: 2026-07-28
updated: 2026-07-28
status: initialized
---

# Cognee

## 一句话摘要

Cognee 是一个开源 AI Agent 记忆平台，以 **知识图谱为核心存储范式**，将任意格式的数据持续构建为可自托管的图谱记忆，使 Agent 拥有跨会话的持久长期记忆。

## 解决的问题

Cognee 解决的核心问题：**单一向量检索不足以支撑 Agent 记忆的关系推理需求**。纯向量检索擅长找"语义相近"的内容，但无法回答"X 和 Y 之间有什么关系"或者"这个事件的完整因果链条是什么"这类关系型问题。Cognee 用知识图谱补上这个缺口。

## 核心架构

### 三层存储架构

```
[Agent/App] ←→ [Cognee API]
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    Relational   Vector      Graph
    (文档/溯源)  (语义嵌入)  (实体与关系)
```

- **Relational Store**：追踪文档、chunks 和数据溯源（谁从哪里来）
- **Vector Store**：存放 embedding，做语义相似度搜索
- **Graph Store**：实体和关系的知识图谱，支持 Cypher 查询

### 独特优势：全跑在 Postgres 上

Cognee 1.0 的颠覆性设计——**整个记忆层可以只用一个 Postgres 实例**：
- 关系表（metadata）：Postgres
- 向量搜索：pgvector
- 图谱关系：Cognee 的 Postgres 图谱后端
- 会话缓存：SQL 缓存

对比传统方案：需要 Neo4j（图）+ Qdrant（向量）+ Redis（会话）+ Postgres（元数据）四套服务。

## 主要操作

Cognee v1.0 用四个原语替代了传统 add/search 模式：

### remember（记忆存储）
```
两种模式：
· 永久记忆：没有 session_id → 全程流水线——标准化→建图谱→嵌入→丰富
· 会话记忆：有 session_id → 写入缓存（快速），让 improve 后台同步
```

支持的输入格式丰富：纯文本、本地文件（含 PDF/图片/音视频）、URL、S3 路径、DataItem 对象。

### recall（记忆检索）
```
流程：
1. 检查会话作用域（session_id 存在则优先查缓存）
2. 自动路由选择检索策略（规则引擎匹配查询类型）
3. 执行图谱检索（非纯向量检索）
4. 返回带 source 标记的结果（session/graph/trace）

自动路由规则：
· "概述"类 → 摘要检索
· "X与Y的关系" → 图谱上下文扩展检索
· "时间"类 → 时间检索
· "编码规范" → 编码规则检索
· 精确引号 → 词汇 chunk 检索
```

### improve（记忆丰富）
```
不含 session_id：对已有数据集做图丰富（提取三元组等）
含 session_id：
  1. 反馈权重更新（thumbs up/down 影响图节点权重）
  2. 持久化会话 Q&A
  3. 持久化 Agent 工具调用追踪
  4. 提取会话上下文
  5. 蒸馏（distill）会话 → 经 curator/writer/rejecter 筛选后写入图谱
```

### forget（记忆删除）
按 item/dataset/user 范围删除记忆。

## 关键技术特征

| 特征 | 描述 |
|------|------|
| **存储核心** | 知识图谱（图谱检索 > 向量检索） |
| **检索方式** | 自动路由 + 图谱完成（GRAPH_COMPLETION 兜底） |
| **会话记忆** | 缓存层（默认 local filesystem / 可选 Redis） |
| **向量嵌入** | 作为图谱的补充（不是主要检索方式） |
| **自进化** | Improve 中的反馈权重 + 会话蒸馏 + 后训练一致性 |
| **去重** | 图谱构建时由实体提取和链接机制处理 |
| **多模态** | 支持图片/音频/视频/PDF/文档等多种输入格式 |
| **研究论文** | arXiv:2505.24478 — 知识图谱与 LLM 接口优化 |
| **多用户隔离** | 基于 Dataset 和 User 的完整权限模型 |
| **可观测性** | OTEL Collector 收集器支持 |

## 集成生态

| 平台/框架 | 方式 |
|-----------|------|
| **OpenClaw** | npm 插件 `@cognee/cognee-openclaw` |
| **Claude Code** | 官方 Claude Code 插件（marketplace 安装） |
| **Python SDK** | `pip install cognee` |
| **TypeScript SDK** | `@cognee/cognee-ts` |
| **Rust 客户端** | `cognee-rs` |
| **Docker** | `cognee/cognee`（API） + `cognee/cognee-mcp`（MCP Server） |
| **MCP** | 原生 MCP Server 支持 |

## 核心研究论文

《Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning》— Markovic et al., 2025, arXiv:2505.24478

核心论点：知识图谱 + LLM 的关键接口优化可以让 LLM 在复杂推理任务上超越纯端到端方案。

## 可沉淀的知识点

1. **Cognee 的核心哲学是"图谱优于向量"**：不只是把向量搜索作为主力，而是把知识图谱作为第一公民。这跟 Mem0 的"多信号融合"形成了鲜明对比——前者押注关系推理，后者押注多维度召回。
2. **Postgres 全能化**是 Cognee 1.0 的关键创新点：一张 Postgres 实例搞定关系+向量+图谱+缓存四个职能，大幅降低运维复杂度。
3. **Improve 的蒸馏机制**是 Cognee 区别于其他框架的关键差异：不只是简单地提取事实，而是让 curator/writer/rejecter 三级评估后决定什么值得持久化，类似 Letta 的 Dreaming 但更结构化。
4. **自动路由 + 图谱完成**的检索策略比纯向量检索更丰富——它能回答"X和Y的关系"、"发生了什么"这类结构性/情景性问题。

## 相关来源

- GitHub：https://github.com/topoteretes/cognee
- 官方文档：https://docs.cognee.ai
- 研究论文：https://arxiv.org/abs/2505.24478
- Cognee Cloud：https://cognee.ai
- Claude Code 插件：https://github.com/topoteretes/cognee-integrations

## 相关页面

- [[Knowledge/wiki/综合/Agent Memory框架全景]] — 三大框架对比
- [[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节|Mem0 架构与知识图谱技术细节]]
- [[Knowledge/wiki/对比/Cognee与Mem0对比|Cognee 与 Mem0 对比]]
