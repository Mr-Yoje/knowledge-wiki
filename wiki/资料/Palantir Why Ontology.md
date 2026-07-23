---
type: source
tags: [source-summary, ontology]
source_name: "Palantir Why Ontology"
author: "Palantir Technologies"
url: "https://palantir.com/docs/foundry/ontology/why-ontology/"
created: 2026-07-23
updated: 2026-07-23
status: initialized
---

# Palantir Why Ontology

## 来源信息

- **来源**: Palantir Foundry 官方文档
- **URL**: https://palantir.com/docs/foundry/ontology/why-ontology/

## 一句话摘要

Ontology 是决策中心（decision-centric）而非数据中心（data-centric）的系统，将数据、逻辑、动作、安全四要素统一。

## 解决的问题

传统数据架构不捕获决策背后的推理过程和后续行动，限制了学习和 AI 的整合。分析型架构没有将计算置于真实环境中，与运营脱节。

## 关键结构

**决策四要素**：
1. Data（数据）—— 用于决策的信息，包括决策过程中产生的"决策数据"
2. Logic（逻辑）—— 评估决策的启发式和计算过程
3. Action（动作）—— 决策的编排和执行
4. Security（安全）—— 决策符合运营策略的保障

**虚构案例**：Onyx Incorporated 医疗设备制造商经历供应链中断 → Ontology 驱动的 Agent（Disruption Bot）提出原料重新分配方案 → 交人类审核 → 执行并学习

## 可沉淀知识点

- LLM Agent 需要在 Ontology 提供的丰富密集上下文中工作，而不仅仅是 RAG
- Agent 的行为受与人类相同的安全策略约束
- 每个 Agent 可像新团队成员一样逐步获得更大的权限范围
- 决策数据（decision data）是传统架构忽视的重要资产——包含了上下文、可选方案和后续影响
- End-to-end 决策血统（decision lineage）自动捕获，可作为 Agent 微调的训练数据

## 相关页面

- [[Knowledge/wiki/综合/Ontology 本体论专题全景]]
- [[Knowledge/wiki/概念/Ontology 决策四要素]]
- [[Knowledge/wiki/概念/Ontology 与 AI Agent 的关系]]
