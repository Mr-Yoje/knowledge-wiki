---
type: synthesis
tags: [synthesis, agent-memory, mem0, langgraph, letta, cognee, memory-framework]
created: 2026-07-28
updated: 2026-07-28
status: evolving
---

# Agent Memory 框架全景

AI Agent 的长期记忆能力是 Agent 从"一次性工具"进化为"持续学习伙伴"的核心瓶颈。当前 Agent Memory 领域形成了三大流派：以 [[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节|Mem0]] 为代表的**外挂记忆层**、以 LangGraph 为代表的**状态图引擎**、以 Letta Code（原 MemGPT）为代表的**自进化文件系统**。此外，以 [[Knowledge/wiki/资料/Cognee|Cognee]] 为代表的**知识图谱优先派**正在崛起，形成第四极。本文从架构、原理、流程三个维度深度分析各框架的设计取舍。

## 核心判断

1. **Agent Memory 的核心矛盾是"精度 vs 成本 vs 灵活性"的三角博弈**：Mem0 追求精度（多信号融合 + LLM 提取），Letta 追求灵活性（Agent 自主读写 Markdown 文件），LangGraph 追求可控性（显式的 State + Store 架构）。
2. **记忆写入策略正在从"LLM 实时决策写入"转向"后台独立学习"**：Letta 的 Dreaming 和 LangGraph 的 Background Memory 都证明，不阻塞主 Agent 响应流程的后台学习是更好的实践。
3. **ADD-only 优于 UPDATE 已成为共识**：Mem0 2026年4月新算法证明"只加不删"比 UPDATE/DELETE 效果好（LoCoMo 从 71.4→92.5），Letta 使用 Git 版本控制天然支持追加式记忆。
4. **多信号检索（语义 + BM25 + 实体 + 时间）正在替代纯向量检索**：单一 cosine similarity 不足以应对 Agent 记忆的各种查询类型（概念性、事实性、时序性）。
5. **记忆的可解释性和可编辑性正在成为新刚需**：Letta 用 Markdown 文件存储记忆，让人类可以直接阅读和编辑；LangGraph 的 Store 以 JSON 文档组织，天然可审查。

## 三大框架

### Mem0 — 记忆即服务

**定位**：AI Agent 的通用记忆层基础设施（YC 孵化）。

#### 核心架构

```
[Agent/LLM] ←→ [Mem0 Memory Layer]
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     VectorDB    GraphDB(可选)  SQL
     (语义)     (实体关联)     (事实元数据)
```

三层存储：SQL 存事实与元数据，向量库存 embedding 做语义搜索，图谱库存实体关系做关联提升。这三种存储并不是冗余备份，而是服务于不同的检索信号。

#### 2026 年 4 月新算法

2026 年 4 月 Mem0 发布了全新的记忆算法，在 LoCoMo、LongMemEval 等基准上取得显著提升：

| 基准 | 旧算法 | 新算法 | Token | 延迟 |
|------|--------|--------|-------|------|
| LoCoMo | 71.4 | **92.5** | 7.0K | 0.88s |
| LongMemEval | 67.8 | **94.4** | 6.8K | 1.09s |
| BEAM (1M) | — | **64.1** | 6.7K | 1.00s |
| BEAM (10M) | — | **48.6** | 6.9K | 1.05s |

**五项关键改进**：

1. **Single-pass ADD-only 提取** — 一次 LLM 调用完成记忆提取，不执行 UPDATE/DELETE 操作。记忆只增不减，避免 Agent 错误删除有用信息。
2. **Agent 生成事实优先级提升** — 当 Agent 确认某个动作完成后，产生的信息与用户提供的信息同等权重存入记忆。
3. **实体链接** — 提取实体、嵌入、跨记忆建立链接，检索时通过实体关联提升命中率。
4. **多信号融合检索** — semantic（向量相似度）、BM25（关键词）、entity（实体匹配）三种信号并行计算，分数融合后排名。
5. **时间推理** — 对包含时间信息（"现在/过去/计划"）的查询，时间感知的检索机制优先返回最合适的带时间戳记忆。

#### 写入流程

```
对话消息 → 上下文查找(查已有记忆) → LLM提取结构化事实
  → 去重与冲突检测 → embedding → 写入SQL+向量库+图谱库
```

#### 读取流程

```
查询 → embedding(语义) + BM25(关键词) + 实体匹配
  → 三种信号融合排序 → 时间推理重排 → 返回 top-k
```

#### 集成方式

- Python: `pip install mem0ai`
- TypeScript: `npm install mem0ai`
- CLI: `npm install -g @mem0/cli`
- 平台集成：LangGraph、CrewAI、AutoGen、Claude Code、Cursor 等

#### 适用场景

- 需要独立记忆服务的多 Agent 系统
- 记忆需要跨框架复用（Mem0 有多个框架的官方集成）
- 对记忆精度要求高、可以接受 ~1s 延迟的场景

---

### LangGraph — 状态即记忆

**定位**：有状态 Agent 的低级编排框架（LangChain 出品）。

#### 记忆分类体系

LangGraph 受 CoALA 论文启发，将 Agent 记忆分为三类：

| 类型 | 存储内容 | 人类类比 | Agent 类比 |
|------|---------|---------|-----------|
| **Semantic（语义记忆）** | 事实、概念 | 学校学的知识 | 用户的偏好和事实 |
| **Episodic（情景记忆）** | 经历、体验 | 做过的事 | Agent 过去的行为 |
| **Procedural（程序记忆）** | 规则、流程 | 本能或运动技能 | Agent 的 System Prompt |

其中 Semantic 又分两种组织形式：
- **Profile（档案模式）**：单文件持续更新，保持一个聚合的用户画像。优势是上下文完整，劣势是大 JSON 容易出错。
- **Collection（集合模式）**：多个独立记忆文档，每个记忆范围窄、生成容易。优势是召回率高，劣势是管理复杂度增加。

#### 短期记忆（Short-term / Thread-scoped）

- 作为 Agent State 的一部分，通过 Checkpointer 持久化
- 按 Thread（会话）隔离，同一线程内可恢复
- 面临长上下文挑战：LLM 在长上下文中性能下降、成本高
- 常用技术：消息过滤、摘要、滚动窗口

#### 长期记忆（Long-term / Cross-thread）

通过 **Store** 组件实现：

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore(index={"embed": embed_fn, "dims": 1536})
store.put(("user-123", "chitchat"), "preferences", 
          {"theme": "dark", "keybinding": "vim"})
results = store.search(("user-123",), query="preferences")
```

- 按 namespace 组织（类似文件夹层级）
- 支持语义搜索 + 内容过滤
- 跨 namespace 搜索可一次检索多个 scope

#### 记忆写入策略

**Hot Path（热路径）**：
```
Agent 响应过程中 → 调用 save_memories 工具 → 实时写入
优点：立即可用、用户可见
缺点：增加延迟、Agent 需分心
```

**Background（后台）**：
```
后台独立任务 → 定期回顾对话 → 提取/更新记忆
优点：不阻塞主流程、专注完成主任务
缺点：延迟更新、频率难定
```

#### Trustcall — 精确记忆更新

配套工具 [[Knowledge/wiki/资料/Trustcall]] 解决 LLM 更新大 JSON 不稳定的问题：LLM 只需生成 **JSON Patch（增量补丁）** 而非完整 JSON，精确修改部分字段。

#### 适用场景

- 需要精细控制 Agent 状态的复杂工作流
- 人类在环路（Human-in-the-loop）场景
- 需要 durable execution（崩溃后自动恢复）的生产系统

---

### Letta Code — 自我进化的记忆体

**定位**：有身份、能自我学习的状态 Agent 框架（原 MemGPT）。

**GitHub**: https://github.com/letta-ai/letta-code

#### 核心创新: MemFS（记忆文件系统）

MemFS 是一个 **Git 版本控制的 Markdown 文件系统**，作为 Agent 的长期记忆存储。所有记忆文件都存放在 `$MEMORY_DIR/` 下：

```
$MEMORY_DIR/
├── system/              ← 每次交互都加载进 System Prompt
│   ├── persona.md       ← Agent 的自我认知
│   └── human.md         ← 用户偏好、重要事实
├── reference/           ← 按需加载（不默认加载进 System Prompt）
│   └── project-notes.md
└── skills/              ← Agent 学习到的技能
    └── my-skill/
        └── SKILL.md
```

**每个文件都是 Markdown + YAML frontmatter**，Agent 可以用文件读写工具直接打开、阅读、修改。这意味着：
- 人类也可以直接阅读和编辑 Agent 的记忆
- Agent 不需要特定 API 就能读写——只是操作文件
- Git 提供完整的版本历史和回滚能力

#### 记忆生命周期

```
① 初始化 (/init)
   → Agent 扫描项目、了解工作风格、回顾之前的编码会话
   
② 交互中学习 (/remember)
   → 用户显式告诉 Agent 某个规则或事实
   → Agent 自行决定存储到哪个文件、什么位置

③ 🛌 Dreaming（做梦）
   → 后台用子 Agent 审查最近的对话记录
   → 提取"可持久化的教训" → 写入 MemFS
   → 通过 /sleeptime 配置触发间隔

④ 整理重组 (/doctor)
   → 检查记忆层级是否过大或漂移
   → 审计放置位置、去重、检查 System Prompt token 使用
```

#### Dreaming 机制的独特价值

Dreaming 是 Letta Code 区别其他框架的关键创新：
- **不打断主 Agent**：子 Agent 在后台工作，不影响主 Agent 的响应速度
- **自省式学习**：子 Agent 审查对话记录，发现"值得记住的东西"
- **并发安全**：使用 Git worktree 实现多个内存子 Agent 并发更新
- **可配置频率**：支持按用户消息数或上下文窗口紧凑时触发

#### 版本化与共享

- **Git 提交**：每次记忆修改都 commit，提供完整版本历史
- **云同步**：云端备份后，记忆和技能随 Agent 迁移
- **共享内存**：多 Agent 可挂载同一 Git 仓库，共享上下文和记忆

#### 适用场景

- 需要长期持续进化的个人助理 Agent
- Agent 需要在多平台（Slack、Telegram、Discord、CLI、Web）一致运作
- Agent 需要自主学习和优化自身行为
- 需要可审计、可回滚的记忆系统

---

## 横向对比

| 维度 | Mem0 | LangGraph | Letta Code |
|------|------|-----------|------------|
| **记忆粒度** | 事实级（LLM 提取的结构化文本） | State + JSON Doc | Markdown 文件段落级 |
| **存储媒介** | SQL + Vector + Graph | JSON Doc (Store) | Git 版本控制文件系统 |
| **写入触发** | API 调用（add/update） | 热路径 or 后台任务 | 主动 + Dreaming（后台） |
| **检索方式** | 语义+BM25+实体融合+时间 | 语义搜索+内容过滤 | 文件系统读取+子Agent搜索 |
| **更新策略** | ADD-only 默认，可显式 update | JSON Patch / 全文替换 | Git commit（追加式） |
| **并发安全** | 服务端原子操作 | Store 原子操作 | Git worktree |
| **延迟** | ~1s（含 LLM 提取） | 可控（热路径可选） | 低（文件直读写） |
| **跨会话记忆** | ✅ 原生支持 | ✅ Store 跨 Thread | ✅ MemFS 持久化 |
| **记忆可读性** | ⚠️ API 返回文本 | ⚠️ JSON 文档 | ✅ Markdown 文件直接可读 |
| **记忆可编辑性** | ⚠️ 需 API 调用 update/delete | ⚠️ 需 Store API | ✅ 直接修改文件 |
| **记忆版本管理** | ❌ 不支持 | ❌ 不支持 | ✅ Git 完整版本历史 |
| **Agent 自我学习** | ⚠️ 被动提取 | ✅ 可配置 | ✅ 主动 Dreaming |
| **人类在回路** | ⚠️ 反馈机制 | ✅ 原生支持 | ✅ 直接编辑记忆 |
| **框架依赖** | 独立服务，可接入任意框架 | 深度绑定 LangChain 生态 | 独立框架 |
| **生产就绪度** | ✅ YC 孵化，商业版 + OSS | ✅ LangSmith 生态成熟 | ✅ npm 全球安装，桌面端 |
| **语言** | Python + TypeScript | Python + TypeScript | TypeScript (Node/Bun) |

## 使用场景矩阵

| 需求 | 推荐框架 | 理由 |
|------|---------|------|
| 快速为已有 Agent 添加记忆 | Mem0 | 最少侵入，API 调用即可 |
| 构建复杂多步 Agent 工作流 | LangGraph | 细粒度 State 控制 + durable execution |
| 构建长期自我进化的个人助手 | Letta Code | Dreaming + MemFS + 多平台支持 |
| 多 Agent 共享同一记忆系统 | Mem0 / Letta Code | Mem0 的 Organization Memory / Letta 的 Shared Memory |
| 记忆需要人工审核和编辑 | Letta Code | Markdown 文件，人类可直接阅读和修改 |
| 高精度、低延迟的事实检索 | Mem0 | 多信号融合检索 + 时间推理 |
| 需要完整记���审计日志 | Letta Code | Git 版本控制，每次修改可回溯 |

## 设计趋势总结

1. **ADD-only 优于 UPDATE**：Mem0 2026年4月新算法证明"只加不删"比 UPDATE/DELETE 效果好，减少 LLM 决策错误概率。
2. **多信号检索成标配**：纯向量检索不够，BM25 + 实体链接 + 时间推理成为标配。
3. **后台学习不阻塞主流程**：Letta 的 Dreaming 和 LangGraph 的 Background 写入——Agent 不需要在每次响应时额外花时间决定"该记住什么"。
4. **文件即记忆**：Letta 用 Markdown 文件存储记忆，Agent 天然能读写，降低系统耦合。
5. **记忆版本化**：Git 做记忆版本管理，支持回滚、审计、多 Agent 同步。
6. **人类可读可写**：记忆不再是黑盒，人类可以直接审查和修正 Agent 的记忆。

## 相关来源

- Mem0 官方文档：https://docs.mem0.ai
- Mem0 GitHub：https://github.com/mem0ai/mem0
- Mem0 研究论文：https://mem0.ai/research
- LangGraph Memory 文档：https://docs.langchain.com/oss/python/langgraph/add-memory
- LangGraph GitHub：https://github.com/langchain-ai/langgraph
- Letta Code GitHub：https://github.com/letta-ai/letta-code
- Letta Docs Memory：https://docs.letta.com/configuration/memory
- Letta MemFS 概念：https://docs.letta.com/concepts/memfs
- Trustcall GitHub：https://github.com/hinthornw/trustcall
- langchain-ai/memory-template：https://github.com/langchain-ai/memory-template

## 相关页面

- [[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节|Mem0 架构与知识图谱技术细节]]
- [[Knowledge/wiki/概念/Mem0的Add模式与冲突处理机制|Mem0 的 Add 模式与冲突处理机制]]
- [[Knowledge/wiki/资料/Trustcall]] — 用于 LangGraph 精确记忆更新的 JSON Patch 工具
- [[Knowledge/wiki/资料/Cognee]] — Cognee 详细资料页 
