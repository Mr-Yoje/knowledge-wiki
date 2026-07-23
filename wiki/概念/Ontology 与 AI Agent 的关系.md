---
type: concept
tags: [concept, ontology]
created: 2026-07-23
updated: 2026-07-23
status: evolving
---

# Ontology 与 AI Agent 的关系

Palantir 文档清晰地阐述了 Ontology 如何为 AI Agent 服务。

## 核心论点

AI Agent 不能只基于检索增强生成（RAG）的数据限制，还需要与**互联的数据、逻辑和动作原语**进行交互。Ontology 通过可扩展的工具范式（tools paradigm）实现了这一点。

## Ontology 赋能的 Agent 能力

1. **丰富的上下文**：Agent 可以获取到比单纯 RAG 更密集、更结构化的上下文
2. **安全治理**：所有 Agent 行为受到与人类用户相同的安全策略约束
3. **权限渐进授予**：Agent 像新团队成员一样逐步获得更大范围的权限
4. **工具范式**：数据、逻辑、动作都可以作为 Agent 可调用的工具暴露
5. **场景化决策**：Agent 可以安全地在沙箱化场景中提出方案，交人类审核

## 关键优势

- Agent 可以跨企业数据源查询、推荐和行动
- 运维人员可以精确控制 LLM 可以查询、推荐和操作的范围
- 工具调用的安全性依赖于对 Ontology 中对象、属性、链接的访问权限

## 相关来源

- [[Knowledge/wiki/资料/Palantir Why Ontology]]

## 相关页面

- [[Knowledge/wiki/综合/Ontology 本体论专题全景]]
- [[Knowledge/wiki/概念/Ontology 决策四要素]]
