---
type: concept
tags: [concept, mem0, memory, knowledge-graph]
created: 2026-07-22
updated: 2026-07-22
status: evolving
---

# Mem0 架构与知识图谱技术细节

Mem0 是一个面向 AI Agent 的通用记忆层基础设施，核心价值在于让 LLM 拥有跨会话的持久记忆能力。本文档从**整体架构、记忆流程、知识图谱（Graph Memory）、去重机制、更新策略**五大维度系统梳理。

## 整体架构

Mem0 采用三层存储 + 双阶段流水线架构：

### 三层存储

| 存储层 | 内容 | 用途 |
|--------|------|------|
| **SQL 数据库** | 事实（facts）与元数据（user_id, agent_id, timestamp 等） | 每个记忆的权威来源（source of truth） |
| **向量数据库** | 文本的 embedding 向量 | 语义相似度搜索（cosine similarity） |
| **图谱/实体存储** | 实体节点与关系 | 关系感知检索（Graph Memory 开启时生效） |

支持的向量存储：Qdrant、pgvector、Chroma、Pinecone、Redis、Weaviate、Milvus、Elasticsearch 等。

### 支持的内嵌(embedding)和 LLM

- **LLM**: OpenAI、Anthropic、Gemini、Groq、Ollama、AWS Bedrock、Azure OpenAI、LiteLLM 等
- **Embedder**: OpenAI、Gemini、Azure OpenAI、Ollama、HuggingFace、VertexAI、AWS Bedrock 等
- **Reranker**: Cohere 等（Python OSS 支持）

### 双阶段流水线

1. **提取阶段（Writing / `add`）**：用户传入 messages → LLM 提取事实 → embedding → 去重 → 写入 SQL + 向量库 + 图库
2. **检索阶段（Reading / `search`）**：查询 → embedding → 向量检索 → 关键词 BM25 → 实体图谱 boost → 排序 → 返回

## 记忆类型与层级

| 层级 | 生命周期 | 作用域 | 适用场景 |
|------|---------|--------|---------|
| **Conversation Memory** | 单次响应内 | 当前 turn | 工具调用、CoT 中间状态 |
| **Session Memory** | 分钟~小时 | run_id | 多步骤流程、debug 会话 |
| **User Memory** | 周~永久 | user_id | 用户偏好、账号信息 |
| **Organization Memory** | 全局配置 | 多 agent 共享 | FAQ、产品目录、策略 |

## 知识图谱（Graph Memory）: 创建、去重与更新

Mem0 在 Platform 中和 OSS 中的图谱实现方式**不同**。

### Platform 中的原生 Graph Memory

Platform 的 Graph Memory 是**内置的、零配置、始终开启**的，不需要外部图数据库。

#### 1. 实体提取 → 节点创建

- **spaCy NLP 引擎**做实体提取（在 OSS 源码 `mem0/utils/entity_extraction.py` 中看到具体实现）
- 提取三类实体：
  - **Proper Nouns**（专有名词）：人名、地名、品牌名，通过 spaCy NER（`PERSON`, `ORG`, `GPE`, `LOC`, `PRODUCT`, `EVENT` 等）和大小写识别
  - **Quoted Text**（引号内容）：书名、特定术语
  - **Noun Compounds**（名词复合短语）：如 "machine learning"、"knowledge graph"
- 大量去噪逻辑：排除通用词表（`_GENERIC_HEADS`、`_GENERIC_SINGLE_ENTITY_TERMS`、`_NON_SPECIFIC_ADJ` 等）
- 每个提取的独立实体成为一个**图节点（node）**，每个记忆为一个**记忆节点**
- 实体被嵌入为向量，以便不同表述的相同实体能被语义匹配

#### 2. 实体链接 → 关系建立

- 当**同一个实体出现在多个记忆中**，这些记忆通过该实体自动链接
- 关系是从**共现（co-occurrence）**推导的，不需要定义 schema
- 没有显式的类型化关系（如 "manages" 边），而是基于上下文的隐含连接
- **实体去重**：相同语义的实体通过 embedding 向量匹配，即使不同表述也能识别为同一实体

#### 3. 图谱在检索中的作用

- 检索时，Mem0 从查询中提取实体，在图谱中找到匹配的实体节点
- 连接到这些实体的记忆获得**排名提升（ranking boost）**，体现在 `score` 字段中
- 来自 **4 路信号**的综合排名：
  | 信号 | 原理 | 最佳场景 |
  |------|------|---------|
  | **Semantic** | 向量相似度（cosine） | 概念性问题 |
  | **Keyword** | BM25 关键词匹配 | 名称/ID/事实查找 |
  | **Entity** | 图谱实体 boost | 关于人/项目的查询 |
  | **Temporal** | 时间元数据 | "什么时候"、"最近" |

- OSS 中的实体 boost 权重通过 `ENTITY_BOOST_WEIGHT` 常量控制
- OSS 的 Qdrant 实现额外支持**混合搜索**：BM25 sparse vector + dense vector 同时查询

### OSS 中的图谱实现

在 OSS 版本中：
- **早期的 `enable_graph=True` + 外部图数据库（Neo4j/Memgraph/Kuzu/Neptune）**已被废弃
- 当前 OSS 的图谱依赖于**文本中的实体提取**和**检索时的实体 boost**
- 使用 spaCy + 规则引擎提取实体，在检索时对匹配实体相关记忆加分
- 没有持久化的图数据库，实体关系在查询时动态计算

### 去重机制（Deduplication）

#### 1. Add 阶段的去重

每次 `add` 时发生在**提取流程**中：

1. **上下文查找**：先从已有的记忆中查找与新消息相关的现有事实
2. **LLM 提取**：LLM 从输入消息中提取结构化的偏好、决策、计划等
3. **去重与嵌入**：冗余事实被移除（Redundant facts are removed），然后每条记忆才被嵌入向量
4. **实体链接**：当配置了图谱记忆时，执行实体链接

> 来自源码 `mem0/memory/main.py` 中的提取流程注释：
> - "Context lookup. Mem0 checks related existing memories so it can avoid storing the same fact again."
> - "Fact extraction. An LLM extracts preferences, decisions, plans..."
> - "Deduplication and embedding. Redundant facts are removed, then each memory is embedded."

#### 2. Add-only 模式 → 不自动覆盖

Mem0 默认是 **ADD-only（仅追加）** 模式：
- 新记忆不会覆盖或删除已有记忆。如果用户说"我从奥斯汀搬到了西雅图"，Mem0 存储新事实，但不自动抹去旧事实
- 要更正信息需要显式调用 `update()` 或 `delete()`
- 使用 `infer=False` 时跳过 LLM 提取和去重，原样存储

#### 3. 搜索排名去重

检索时使用**多信号融合排名**确保最相关的记忆排在前面，搜索引擎级别的去重由向量相似度 + BM25 + 图谱 boost 联合控制。

### 更新策略（Update）

#### 显式更新：`update()`

| 能力 | Platform | OSS |
|------|---------|-----|
| 单条更新 | `client.update(memory_id, text=..., metadata=...)` | `memory.update(memory_id, text=...)` |
| 批量更新 | `client.batch_update([...])`，最多 1000 条 | 需自行循环 |
| 不可变记忆 | 返回描述性错误 | 抛异常：需 delete 再 re-add |

`update()` 的参数：
- `memory_id`：目标记忆的 ID
- `text`：新的内容（替换存储值）
- `metadata`：可选的元数据更新
- `timestamp`：覆盖时间戳（Unix epoch 或 ISO 8601）
- `expiration_date`：可选，设置过期时间
- 可以只更新 `metadata` 而不改 `text`

**安全机制**：
- 身份字段（`user_id`, `agent_id`, `run_id`, `actor_id`）在创建后不可变
- `update()` 如果尝试通过 metadata 覆盖这些键，会被静默忽略并记录 warning

#### 隐式更新（Feedback Mechanism）

Platform 支持的反馈循环：
- 用户的 thumbs up/down 信号触发自动更正
- 配合 MCP Server，AI Agent 可以在用户指正时自动更新自己的记忆

#### 自动上下文（Automatic Conversation Context）

Platform 中 `add()` 的默认行为：
- 只发送新消息，Mem0 自动拉取相同 `user_id` + `run_id` 下的历史消息作为上下文
- 从而新消息中的代词（如"他"）能在前文语境中被正确理解
- 例如："我养了只金毛叫 Biscuit" → 下一句"他今天5岁了" 能正确解析为"Biscuit 今天5岁了"

## 关键技术特征总结

| 特征 | 描述 |
|------|------|
| **架构模式** | 三段式存储（SQL + Vector + Graph） |
| **提取机制** | LLM 驱动的结构化记忆提取，而非简单逐字存储 |
| **图谱模式** | 隐式共现图 vs 显式关系图（Platform 原生 vs OSS 轻量） |
| **去重策略** | Add 阶段的 LLM 上下文感知去重 + 检索阶段的交叉信号排名 |
| **更新方式** | 显式 update/batch_update + 隐式 feedback 循环 |
| **记忆作用域** | user_id / agent_id / app_id / run_id 四维隔离 |
| **多信号检索** | Semantic + BM25 Keyword + Entity Boost + Temporal |
| **检索排名** | 融合分数（score）输出，可调 explain 模式 |

## 相关来源

- Mem0 官方文档：https://docs.mem0.ai
- Mem0 GitHub 源码：https://github.com/mem0ai/mem0
- Mem0 Graph Memory 文档：https://docs.mem0.ai/platform/features/graph-memory

## 相关页面

- [[Knowledge/wiki/概念/LLM记忆层对比]]
- [[Knowledge/wiki/概念/知识图谱构建方法]]
