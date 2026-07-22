---
type: concept
tags: [concept, mem0, memory, add-mode, conflict-resolution]
created: 2026-07-22
updated: 2026-07-22
status: evolving
---

# Mem0 的 Add 模式与冲突处理机制

本文聚焦 Mem0 中最核心的问题：**什么时候用 `add()` 模式（默认的 ADD-only 增量提取），什么时候改用 `update()` 显式更新？两种模式的内在冲突是如何检测和处理的？**

---

## 一、Mem0 的两套记忆写入模式

Mem0 实际提供了两种本质不同的写入路径：

| 维度 | 默认 Add 模式（infer=True） | 显式 Update 模式 |
|------|---------------------------|-----------------|
| **调用方式** | `m.add(messages, ...)` | `m.update(memory_id, text=..., metadata=...)` |
| **写入策略** | 追加（ADD-only），从不覆盖已有记忆 | 直接替换指定 memory_id 的内容 |
| **去重位置** | LLM 提取阶段做语义去重 | 调用方自己负责 |
| **适用场景** | 持续积累用户偏好和事实 | 用户明确纠正或信息变更时 |
| **是否需要 memory_id** | 不需要（自动创建） | 必须（通过 search 先获取） |

此外还有第三个模式 **`infer=False`**——完全不经过 LLM 提取，原样逐字存储，此时完全没有去重。

---

## 二、默认 Add 模式的完整流程（含冲突避免）

当调用 `m.add(messages, user_id="alice")` 时，内部执行的是 **DEFAULT_UPDATE_MEMORY_PROMPT（来自源码 `mem0/configs/prompts.py`）** 中的智能记忆管理流程：

### 步骤 1：上下文查找（Context Lookup）

Mem0 先搜索同一 `user_id`/`agent_id`/`run_id` scope 下的**已有相关记忆**。

这一步的目的是：
- 获知用户已经存储了哪些事实
- 为下一步的冲突判断提供"旧记忆"输入

### 步骤 2：LLM 提取新事实（Fact Extraction）

LLM 从输入消息中提取**结构化的独立事实列表**（`{"facts": [...]}`）。提取 prompt（`FACT_RETRIEVAL_PROMPT`）定义了7大类要记住的信息：个人偏好、重要细节、计划和意图、活动偏好、健康偏好、职业信息、杂项。

### 步骤 3：冲突检测与操作决策

这是最关键的环节。LLM 拿到**旧记忆** + **新事实**，按以下规则逐一决策：

#### 规则 A：ADD — 新增（无冲突）
> 新事实中包含旧记忆中没有的信息 → 直接追加为新条目。

**例**：
- 旧记忆：`["用户是软件工程师"]`
- 新事实：`["名字是John"]`
- 结果：新增 `[名字是John]`，原有条目不动 → **无冲突**

#### 规则 B：UPDATE — 更新（丰富/替代）
> 新事实与旧记忆涉及同一件事，但新信息更丰富或表达不同 → 用新信息替换旧条目（保持相同 ID）。

**触发条件**：
- 新旧信息虽有重叠，但新信息**更具体、更详细**
- 新信息与旧信息**存在方向性差异但同主题**

**例 (a)**：
- 旧记忆：`"User likes to play cricket"`
- 新事实：`"Loves to play cricket with friends"`
- 结果：UPDATE → 保留 ID，text 替换为 `"Loves to play cricket with friends"`
- 本质：这是**同向增强**，不是冲突

**例 (b)**：
- 旧记忆：`"Likes cheese pizza"`
- 新事实：`"Loves cheese pizza"`
- 结果：NONE → 语义相同，不做变更

#### 规则 C：DELETE — 删除（矛盾冲突）
> 新事实与旧记忆**直接矛盾** → 删除旧条目。

**触发条件**：
- 新信息明确否定旧记忆（如 "喜欢"→"不喜欢"）
- 这是真正的"冲突"场景

**例**：
- 旧记忆：`"Loves cheese pizza"`
- 新事实：`"Dislikes cheese pizza"`
- 结果：DELETE → 旧条目被删除

#### 规则 D：NONE — 无变化（已存在）
> 新事实与旧记忆语义一致 → 什么都不做。

**触发条件**：
- 同义重复（"Name is John" vs 已有"Name is John"）

### 步骤 4：执行变更 + embedding + 写入三层存储

LLM 决策结果被解析为操作列表，依次执行：
1. SQL 库更新 facts 表
2. 新 facts 生成 embedding 写入向量库
3. 实体提取 → 写入图谱

---

## 三、那么"冲突"到底是怎么出来的？

### 3.1 真正的冲突类型

从源码来看，Mem0 承认两种冲突：

**① 语义矛盾（Significant Contradiction）**
- 被 `DEFAULT_UPDATE_MEMORY_PROMPT` 的 DELETE 规则处理
- 检测方式：LLM 判断新旧信息是否相互否定
- 例如："住在上海" vs "住在北京"

**② 信息过时（Stale Information）**
- Mem0 采用 **ADD-only 默认策略**来处理：不自动覆盖旧信息
- 官方文档明确指出：
  > "If a user says 'I moved from Austin to Seattle,' Mem0 stores the new fact **without silently rewriting the old one.** Use explicit `update` or `delete` operations when your application needs to correct or remove a memory."
- 这意味着**两座城市共存**（Austin 和 Seattle都会出现在记忆中），搜索引擎通过 ranking 决定哪条更相关

### 3.2 为什么即使有 DEFAULT_UPDATE_MEMORY_PROMPT 还是会出现冲突？

关键在于 **DEFAULT_UPDATE_MEMORY_PROMPT 是 OSS 的「记忆更新」Prompt**，但对 `m.add()` 而言，这个 prompt 只是在**写入时做去重和冲突检测**。它处理的逻辑颗粒度是：

- 同一条事实是否已存在 → NONE
- 同一条事实是否需丰富 → UPDATE
- 同一条事实是否被否定 → DELETE

但它**没有处理**的场景：

1. **跨 session 的隐式矛盾**：用户在不同 session 说了矛盾的话，两个 session 的 `add()` 独立执行，各自没有对方的完整上下文
2. **代词的泛指解析**："他"可能在不同上下文中指不同人
3. **时序相关的冲突**：旧偏好 vs 新偏好（如 "喜欢咖啡" → "戒咖啡了"），`add()` 默认是增量保留两条

---

## 四、什么时候用 add 模式 vs update 模式

### ✅ 用默认 Add 模式（`infer=True`）

| 场景 | 举例 | 原因 |
|------|------|------|
| 持续积累偏好 | "我喜欢科幻片"、"我不吃辣" | 新事实自然追加 |
| 对话中的隐式知识 | "我的狗叫Biscuit"→"他今天5岁了" | 自动上下文解析代词 |
| 在已有知识上加料 | "我爱跑步"→"我每天跑5公里" | UPDATE 规则自动丰富已有记录 |
| 多轮对话积累 | 正常聊天中逐步透露信息 | 去重和冲突检测由 LLM 兜底 |

### ⚠️ 用显式 Update 模式（`m.update()`）

| 场景 | 举例 | 原因 |
|------|------|------|
| 用户明确指正 | "不对，我不住上海了，现在在北京" | add() 会保留两条记录，需要 update 替换 |
| 信息完全变更 | 改密码、改地址、换工作 | 旧信息应被替换而非保留两条矛盾记录 |
| 业务数据同步 | CRM 中用户资料更新了 | 需精确覆盖指定 memory_id |
| 需要批量更正 | 批量修正一批记忆 | `batch_update` 支持最多 1000 条 |

### ❌ 用 `infer=False`（原始存储）

| 场景 | 举例 |
|------|------|
| 需要逐字记录对话历史 | 审计日志、合规场景 |
| 不想经过 LLM 提取 | 节省 token、需要原样存储 |

---

## 五、Mem0 不擅长的冲突场景

| 场景 | 问题 | 建议 |
|------|------|------|
| **长时段的偏好演变** | "喜欢咖啡"→3个月后"戒了咖啡" → 两条共存 | 应用层维护版本号，用 update 覆盖过时记录 |
| **多用户的矛盾事实** | 同一 user_id 下两个人使用 | 改用不同的 user_id 或 run_id |
| **事实否定 vs 新事实** | "我不喜欢喝咖啡了" → add() 可能新增一条而非替代 | 显式调用 update() 或 delete() |
| **infer=False 混用** | 与 infer=True 混合存储同一事实 → 产生重复 | 保持一致模式，不要混用 |

---

## 六、总结：核心判断

1. **Add 模式（infer=True）的"冲突处理"本质是 LLM 驱动的「去重 + 语义合并」**，不是真正的冲突解决——它偏向于保守（ADD-only），避免错误地抹去旧信息。
2. **真正的冲突解决需要显式 Update**：add() 故意设计为不自动覆盖，确保安全但需要应用层配合。
3. **Platform 和 OSS 的冲突处理逻辑相同**，都依赖 `DEFAULT_UPDATE_MEMORY_PROMPT` 的 ADD/UPDATE/DELETE/NONE 四选一决策。
4. **关键矛盾检测由 LLM 自身做**，没有独立的规则引擎或矛盾检测算法——这是 Mem0 的取舍：用 LLM 的语义理解能力换取灵活性。

## 相关来源

- Mem0 源码 `mem0/configs/prompts.py` — FACT_RETRIEVAL_PROMPT 和 DEFAULT_UPDATE_MEMORY_PROMPT
- Mem0 官方文档 How It Works：https://docs.mem0.ai/core-concepts/how-it-works

## 相关页面

- [[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节|Mem0 架构与知识图谱技术细节]]
- 待创建：Mem0 与 LLM Wiki 知识库对比
