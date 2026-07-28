---
type: source
tags: [source-summary, trustcall, langgraph, memory, json-patch]
source_name: Trustcall — Tenacious tool calling built on LangGraph
author: hinthornw (LangChain)
url: https://github.com/hinthornw/trustcall
created: 2026-07-28
updated: 2026-07-28
status: initialized
---

# Trustcall

## 一句话摘要

Trustcall 是 LangChain 生态中的工具，通过让 LLM 输出 **JSON Patch（增量补丁）** 而非完整 JSON，解决 LLM 在更新大结构数据时的不稳定性问题，特别适用于 LangGraph 的记忆更新场景。

## 解决的问题

LLM 在要求一次性生成或修改大型 JSON 对象时，容易出现以下问题：
- 遗漏字段：部分已有字段在新输出中被误删
- 格式错误：嵌套结构中的语法错误
- 不相关修改：LLM 修改了不应修改的部分
- 幻觉填充：在不该改的位置填入新内容

这些问题在 Agent 长期记忆管理中尤其致命——错误地修改了已有的用户偏好记录可能导致糟糕的用户体验。

## 核心机制

Trustcall 的核心设计：LLM 不生成完整的 JSON，而是生成 **RFC 6902 JSON Patch**：

```
// 原始记忆
{ "name": "Alice", "preferences": { "theme": "dark", "lang": "en" } }

// Trustcall 生成的补丁
[
  { "op": "replace", "path": "/preferences/theme", "value": "light" }
]

// 应用补丁后
{ "name": "Alice", "preferences": { "theme": "light", "lang": "en" } }
```

**优势**：
- LLM 只需描述"变更"而非"全部"——准确率大幅提升
- 不改的部分完全不受影响——安全
- 支持批量原子更新——一次调用完成多个字段更新

## 可沉淀的知识点

1. **JSON Patch 比 JSON 重写更适合 LLM 记忆更新**：LLM 在"增量描述变化"任务上比"完整重写"任务表现好得多，这是 Trustcall 的核心理念。
2. **记忆更新的精度瓶颈不在检索，而在写入**：检索到正确记忆后，如果 LLM 不能精确修改，可能会导致信息丢失或污染。
3. **Trustcall 可视为 LangGraph Memory 栈中"精确写入"层的实现**：配合 LangGraph 的 Store（存储层）和 Hot Path/Background（触发策略），构成完整的记忆生命周期管理。

## 相关来源

- GitHub 仓库：https://github.com/hinthornw/trustcall

## 相关页面

- [[Knowledge/wiki/综合/Agent Memory框架全景|Agent Memory 框架全景]] — LangGraph 部分
