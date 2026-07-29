---
type: source
tags: [source-summary, cognee, memory, knowledge-graph, ai-memory]
source_name: Cognee — Open-Source AI Memory Platform for Agents
author: topoteretes
url: https://github.com/topoteretes/cognee
created: 2026-07-28
updated: 2026-07-29
status: active
---

# Cognee 技术原理

## 一句话摘要

Cognee 是一个开源 AI Agent 记忆平台，以**知识图谱为核心存储范式**，将任意格式的数据（文本/文件/PDF/图片/音视频/URL）通过**导入→图谱提取→图完善**三条流水线持续构建为可自托管的图谱记忆，使 Agent 拥有跨会话的持久长期记忆。

## 解决的问题

Cognee 解决的核心问题：**单一向量检索不足以支撑 Agent 记忆的关系推理需求。** 纯向量检索擅长找"语义相近"的内容，但无法回答"X 和 Y 之间有什么关系"或者"这个事件的完整因果链条是什么"这类关系型问题。Cognee 用知识图谱补上这个缺口。

## 核心架构：三层存储

```
[Agent/App] ←→ [Cognee API]
                    |
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    Relational   Vector      Graph
    (文档/溯源)  (语义嵌入)  (实体与关系)
```

| 存储层 | 角色 | 默认后端 | 生产可选 |
|-------|------|---------|---------|
| **Relational** | 追踪文档、chunks 和数据溯源（谁从哪里来） | SQLite | Postgres |
| **Vector** | 存放 embedding，做语义相似度搜索 | LanceDB（嵌入式 Arrow） | PGVector / Qdrant / Pinecone |
| **Graph** | 实体和关系的知识图谱，支持 Cypher 查询 | Ladybug（嵌入式图数据库） | Neo4j / Kuzu / FalkorDB |

三种存储各司其职，有重叠但分工明确：
- Relational：文档级元数据和溯源——**"这个数据从哪里来"**
- Vector：chunk 级别的语义指纹——**"哪些内容语义相近"**
- Graph：实体和关系的高层结构——**"这些概念之间怎么连接"**

### Postgres 全能模式

Cognee 1.0 的关键创新：**一张 Postgres 可以同时担任四个角色**：
- 关系表（元数据）：Postgres 原生表
- 向量搜索：PGVector 扩展
- 图谱关系：Cognee 的 Postgres 图谱后端（PgGraphAdapter）
- 会话缓存：SQL 缓存

对比传统方案需要 Neo4j（图）+ Qdrant（向量）+ Redis（会话）+ Postgres（元数据）四套服务。

### Rust 端架构（cognee-rs）

Rust 版是 Python 版的端口，针对边缘设备和本地场景优化。核心 crate 结构：

```
cognee-rust-oss/
├── crates/
│   ├── ingestion/     — 数据导入流水线（哈希去重、URL 爬取）
│   ├── chunking/      — 文本分块（word→sentence→paragraph）
│   ├── cognify/       — 知识图谱提取（实体/关系/摘要）
│   ├── search/        — 15 种检索策略的统一编排
│   ├── graph/         — 图数据库抽象（Ladybug/PG）
│   ├── vector/        — 向量数据库抽象（LanceDB/PGVector/BruteForce）
│   ├── embedding/     — 多 Provider 嵌入引擎（ONNX/OpenAI/Ollama/Mock）
│   ├── llm/           — LLM Provider 抽象（OpenAI 兼容 API）
│   ├── session/       — 会话管理（FS/Redis/SeaOrm 存储）
│   ├── ontology/      — 本体解析（RDF/JSON-LD）
│   └── lib/           — 统一的 public API（forget/recall/remember/improve）
```

## 四大核心操作（v1.0）

Cognee v1.0 用四个原语替代了传统 add/search 模式：

### remember（记忆存储）

两种模式：

**永久记忆（无 `session_id`）**：执行完整的三阶段流水线——
1. **Ingest**（ADD）— 数据标准化、去重、附加到数据集
2. **Cognify**（图谱构建）— 文档分块、LLM 提取实体和关系、生成 embedding
3. **Improve**（图完善）— 默认自动跟随，添加衍生检索结构

**会话记忆（有 `session_id`）**：
1. 写入会话缓存（快速，键=用户+会话）
2. `self_improvement=True`（默认）→ 立即在后台启动 Improve 将会话内容桥接至永久图谱
3. `self_improvement=False` → 内容只留在缓存，等待后续手动 improve

**支持的输入格式**：
- 纯文本字符串
- 本地文件路径（PDF/图片/音视频/Office 文档等，内置 Loader 自动识别）
- HTTP/HTTPS URL（永久模式下自动抓取）
- S3 路径
- `DataItem` 对象（带元数据包装）

**Loader 生态**：

| Loader | 格式 | 依赖 |
|--------|------|------|
| TextLoader | `.txt` `.md` `.json` `.xml` `.yaml` `.log` | 内置 |
| CsvLoader | `.csv` | 内置 |
| PyPdfLoader | `.pdf` | 内置 |
| ImageLoader | `.png` `.jpg` `.webp` 等 20+ 图片格式 | 内置 |
| AudioLoader | `.mp3` `.wav` `.flac` `.ogg` `.m4a` 等 | 内置 |
| UnstructuredLoader | `.docx` `.xlsx` `.pptx` `.html` `.eml` 等 | `cognee[docs]` |
| AdvancedPdfLoader | 布局感知 PDF | `cognee[docs]` |
| BeautifulSoupLoader | HTML 网页 | `cognee[scraping]` |
| DoclingDocument | Docling 预转换文档 | `cognee[docling]` |

### recall（记忆检索）

**核心流程**：

```
1. 检查会话作用域
   session_id 存在 → 优先查会话缓存
   缓存命中 → 返回 source="session" 的结果

2. 选择检索策略
   query_type 已指定 → 直接使用
   auto_route=True（默认）→ 规则引擎匹配（见下方自动路由表）
   auto_route=False → 用 GRAPH_COMPLETION 兜底

3. 执行图谱检索
   缓存未命中或请求图谱检索 → 查询永久知识图谱
   返回 source="graph" 的结果
```

**自动路由规则**（**规则引擎，不调 LLM 判断**）：

| 查询中的线索 | 路由到的搜索类型 | 返回内容 |
|------------|----------------|---------|
| "summarize"/"summary"/"overview"/"tl;dr"/"main points"/"key takeaways" | `GRAPH_SUMMARY_COMPLETION` | 生成的答案 |
| "why"/"explain"/"reasoning"/"step by step"/"chain of thought" | `GRAPH_COMPLETION_COT` | 生成的答案 |
| "how is X related to Y"/"what connects"/"path between"/"relationship"/"linked to" | `GRAPH_COMPLETION_CONTEXT_EXTENSION` | 生成的答案 |
| "when"/"before"/"after"/"timeline"/"between 1990 and 2000"/4 位年份 | `TEMPORAL` | 生成的答案 |
| 精确引号包裹的查询 / "exact"/"verbatim"/"literal"/"word for word" | `CHUNKS_LEXICAL` | 原始 chunk 数据 |
| "coding rules"/"code review"/"best practice"/"linter"/"refactoring" | `CODING_RULES` | 结构化数据 |
| 以 `MATCH `/`RETURN `/`CREATE `/`MERGE ` 开头或包含 `--(`/`)--` | `CYPHER` | 原始图谱行 |
| **无匹配** | `GRAPH_COMPLETION` | 生成的答案 |

**关键设计**：
- 线索带权重，累加计分，最高分胜出
- 线索前 20 字符内出现否定词（not/n't/no/never/without/lack）→ 跳过该线索
- Router 从**不**选择 SUMMARIES / CHUNKS / RAG_COMPLETION / HYBRID_COMPLETION / TRIPLET_COMPLETION 等——这些只有 `FEELING_LUCKY` 的 LLM 选择器可以到达
- 每条结果带 `source` 标记：`session` / `graph` / `trace` / `graph_context`

### improve（记忆丰富/自改进）

**无 session_id**——图丰富：
- 提取并索引 triplet datapoints（当 triplet embedding 启用时）
- 可选构建 Global Context Index（数据集级桶摘要和根摘要，供 GRAPH_COMPLETION 预置上下文）

**有 session_id**——完整自改进链条：

```
① 应用反馈权重（thumbs up/down 影响图节点/边的权重）
② 持久化会话 Q&A（标记为 user_sessions_from_cache）
③ 持久化 Agent 工具调用追踪（trace → 图节点）
④ 提取会话上下文（待处理的 trace 窗口 → 会话级 lessons）
⑤ 蒸馏会话（curator → writer/rejecter 三级评估）
    ↓
    curator 提出候选 lessons
    writer/rejecter 检查是否与已有 lessons/图谱实体冲突
    通过的 lessons → 写入 markdown 文档 → add + cognify → 图谱
    标记为 session_learnings 节点集
⑥ 可选构建 Truth Subspace（从 session_learnings 构建锚向量）
⑦ 图丰富（正常 enrichment pass）
⑧ 可选构建 Global Context Index
⑨ 新图谱关系同步回会话缓存
```

**蒸馏的筛选条件**（不是所有会话内容都进图谱）：
- 被标记为 harmful 的 guidance 被剔除
- 置信度过低的 guidance 被剔除
- 已有类似 lesson 或与图谱实体冲突的被拒绝

### forget（记忆删除）

按粒度支持：
- **item** 级：删除单条数据
- **dataset** 级：删除整个数据集
- **user** 级：删除指定用户的所有数据

## 图谱构建流水线（cognify pipeline）

Cognee 的核心流水线 `cognify()` 将原始数据转化为知识图谱，分以下步骤：

```
原始数据
  │
  ▼
文档分类（分类文档类型）
  │
  ▼
文本分块（word → sentence → paragraph，分层 chunking）
  │
  ▼
LLM 实体提取（识别命名实体）
  │
  ▼
LLM 关系提取（识别实体间关系）
  │
  ▼
摘要提取（每个文档/块的文本摘要）
  │
  ▼
存储到图数据库（节点+边）
  │
  ▼
生成 embedding（向量化）
  │
  ▼
存储到向量数据库
```

Pipeline 运行机制：
- **分层执行**：一个 `run_pipeline` 调用 = 多数据集处理 → 每文件处理 = 串联的任务序列
- **按数据集串行化**：同一数据集上的流水线互斥执行（`asyncio.Lock`），不同数据集并行
- **可恢复**：crash 后重建不会阻塞（内置的崩溃恢复逻辑）
- **缓存控制**：`use_pipeline_cache` 参数可让流水线跳过已处理的数据集

## 检索策略体系（15 种 SearchType）

| SearchType | 说明 | 返回 |
|-----------|------|------|
| `GRAPH_COMPLETION` | 默认兜底——图上下文+LLM 生成 | 答案 |
| `GRAPH_SUMMARY_COMPLETION` | 图总结检索 | 答案 |
| `GRAPH_COMPLETION_COT` | 图思维链检索 | 答案 |
| `GRAPH_COMPLETION_CONTEXT_EXTENSION` | 图上下文扩展（关系推理） | 答案 |
| `TEMPORAL` | 时间感知检索 | 答案 |
| `CYPHER` | 直接 Cypher 查询 | 原始图行 |
| `CHUNKS_LEXICAL` | 词汇匹配（精确匹配） | 原始 chunk |
| `CHUNKS` | 常规 chunk 检索 | 原始 chunk |
| `CODING_RULES` | 编码规则检索 | 结构化数据 |
| `RAG_COMPLETION` | 标准 RAG（向量+LLM） | 答案 |
| `HYBRID_COMPLETION` | 向量+图混合检索 | 答案 |
| `TRIPLET_COMPLETION` | 三元组嵌入检索 | 答案 |
| `SUMMARIES` | 摘要检索 | 摘要数据 |
| `FEELING_LUCKY` | LLM 自动选择策略 | 取决于 LLM |
| `NATURAL_LANGUAGE` | 自然语言转查询 | 答案 |

## 自改进与学习机制

### 反馈权重系统

- 会话反馈（thumbs up/down）→ 更新图谱中使用的节点/边的 `feedback_weight`
- 正面反馈 → 该节点/边在未来检索排序中更有影响力
- 负面反馈 → 影响力降低
- 通过 `DEFAULT_FEEDBACK_INFLUENCE` 环境变量控制影响程度（默认 0=关闭）

### 会话蒸馏（Session Distillation）

将会话中的 guidance（目标、规则、偏好、经验教训）转化为持久的图谱记忆：
1. 过滤：剔除 harmful 反馈或低置信度的 guidance
2. curate：LLM 提出持久的 lessons
3. writer/rejecter：检查与已有 lessons 和图谱实体的冲突
4. 写入：通过的 lessons 渲染为 markdown 文档，经 add+cognify 进入图谱
5. 标记：加入 `session_learnings` 节点集

### Truth-Subspace Reranking（实验性）

**将会话学到的"真理方向"作为向量锚点**，在检索排序中提升符合这些方向的 chunk：

1. **构建阶段**（post-session `improve`）：从 `session_learnings` 构建最多 8 个锚向量（TruthAnchor），将每个 chunk 投影到锚上得到对齐坐标
2. **查询阶段**（`use_truth_weight=True`）：计算查询与锚的匹配度 → 按匹配度权重调整 chunk 排序

**关键点**：
- 坐标存在**图节点上**（不是重新 embedding），成本只等于一次属性写入
- 对齐评分是**乘性**的：与查询关心的方向一致的 chunk 被提升，无坐标的 chunk 中性（不惩罚）
- 和 Feedback Weight 是互补信号（标量 vs 几何信号）
- 实验性、opt-in、默认关闭

## 条件工程机制

### 全局上下文索引（Global Context Index）

在 Improve 阶段可选构建：
1. 对所有已有 `TextSummary` 节点构建语义摘要桶（Bucket）
2. 为数据集创建紧凑的根摘要（Root Summary）——"数据集级世界总结"
3. 首次构建最昂贵，后续只处理新增摘要
4. 在 `GRAPH_COMPLETION` 和 `HYBRID_COMPLETION` 检索中，通过 `include_global_context_index=True` 使用

这一机制的作用类似于**检索时的全局上下文注入**——在回答涉及整个数据集的问题时，预置的概要信息可以提供更好的 orientation。

## 多用户与权限体系

| 概念 | 说明 |
|------|------|
| **Dataset** | 数据的基本组织单元，所有权和数据隔离的边界 |
| **Principal** | 统一抽象，可持有权限的实体 |
| **User** | 个人用户身份 |
| **Tenant** | 组织级访问控制和权限继承 |
| **Role** | 租户内的基于角色的访问控制 |
| **ACL** | 访问控制列表，存储和继承权限 |

### Dataset Database Handler 模式

多用户模式下，每个 dataset 可以拥有独立的图/向量存储后端实例（vs 共享后端），实现更强的数据隔离。支持的后端 Handler：
- PGVector
- LanceDB
- Kuzu
- Neo4j Aura
- FalkorDB
- Qdrant

## 技术特征总结

| 特征 | 描述 |
|------|------|
| **存储核心** | 知识图谱（图谱检索 > 向量检索） |
| **检索方式** | 规则引擎自动路由 + 15 种 SearchType + GRAPH_COMPLETION 兜底 |
| **会话记忆** | 缓存层（默认 local filesystem / 可选 Redis） |
| **自改进** | 反馈权重 + 会话蒸馏（curator/writer/rejecter）+ Truth-Subspace |
| **去重** | 图谱构建时由实体提取 + ingestion 哈希去重 |
| **多模态** | 内置 Loader 支持文本/PDF/图片/音视频/Office/HTML/URL |
| **Pipeline 机制** | 模块化 Tasks + 可编排 Pipelines + 数据集级串行化 + 崩溃恢复 |
| **多用户隔离** | Dataset-Database Handler 模式，支持独立/共享后端 |
| **可观测性** | OTEL Collector 收集器 |
| **Postgres 全能** | 一张 Postgres 搞定关系+向量+图谱+缓存 |
| **研究论文** | arXiv:2505.24478 — 知识图谱与 LLM 接口优化 |

## 集成生态

| 平台/框架 | 方式 |
|-----------|------|
| **OpenClaw** | npm 插件 `@cognee/cognee-openclaw` |
| **Claude Code** | Claude Code 插件（marketplace） |
| **Python SDK** | `pip install cognee` |
| **TypeScript SDK** | `@cognee/cognee-ts` |
| **Rust client** | `cognee-rs` |
| **Docker** | `cognee/cognee`（API）+ `cognee/cognee-mcp`（MCP Server） |
| **MCP** | 原生 MCP Server（HTTP/SSE/stdio 三种传输模式） |
| **COGX 格式** | 标准化的记忆导入/导出格式，可迁移 Mem0/LangMem/Letta/Zep/Graphiti |

## 核心研究论文

《Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning》— Markovic et al., 2025, arXiv:2505.24478

核心论点：知识图谱 + LLM 的关键接口优化可以让 LLM 在复杂推理任务上超越纯端到端方案。

## 可沉淀的知识点

1. **Cognee 的核心哲学是"图谱优于向量"**——不只是把向量搜索作为主力，而是把知识图谱作为第一公民。从 15 种 SearchType 可以看出，绝大部分检索策略是图谱驱动的（GRAPH_*），向量/混合只是补充。

2. **Postgres 全能化**是 Cognee 1.0 的关键创新点：一张 Postgres 实例搞定关系+向量+图谱+缓存四个职能，大幅降低运维复杂度。

3. **检索策略的自动路由是规则引擎，不是 LLM 判断**——这是务实且高效的设计。用加权正则匹配替代每次查询调一次 LLM，既省钱又确定。

4. **会话蒸馏的三级评估（curator/writer/rejecter）**是 Cognee 自改进机制的核心：不是所有会话内容都进图谱，而是经过筛选评估后只有高置信度的 lessons 被持久化。这与 Mem0 的 ADD-only 模式形成鲜明对比。

5. **Truth-Subspace Reranking 是独特的设计**——将学到的教训转化为几何锚点，在检索时不影响 embedding 的情况下重新排序。虽然实验性，但方向很有意思：让 Agent 记忆不仅是"存储和检索"，还能"学习和调整排序"。

6. **多语言/多平台架构**——Python 核心 + Rust 重写（cognee-rs）+ TypeScript SDK + 跨语言绑定，覆盖从边缘设备到云端完整场景。

## 相关来源

- GitHub：https://github.com/topoteretes/cognee
- 官方文档：https://docs.cognee.ai
- 研究论文：https://arxiv.org/abs/2505.24478
- Cognee Cloud：https://cognee.ai
- Claude Code 插件：https://github.com/topoteretes/cognee-integrations
- Rust 版：https://github.com/topoteretes/cognee-rs

## 相关页面

- [[Knowledge/wiki/综合/Agent Memory框架全景]] — 三大框架对比
- [[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节]]
- [[Knowledge/wiki/对比/Cognee与Mem0对比]]
