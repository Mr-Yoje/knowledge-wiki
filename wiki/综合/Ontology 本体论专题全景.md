---
type: synthesis
tags: [synthesis, ontology]
created: 2026-07-23
updated: 2026-07-23
status: evolving
---

# Ontology 本体论专题全景

Ontology 是 Palantir Foundry 平台的核心概念，也是一个在知识工程、AI 和数据管理中越来越重要的思想。

## 两种语境下的 Ontology

### Palantir Ontology（工程语境）

Palantir 的 Ontology 是**组织的运营层（operational layer）**，它将数字资产（数据集、虚拟表、模型）与现实世界中的实体（设备、产品、订单等）连接起来，形成企业的**数字孪生**。

核心四要素：
- **Data（数据）**：全模态企业数据，包括结构化、流式、非结构化、地理空间等
- **Logic（逻辑）**：决定何时、如何做决策的推理和计算过程
- **Action（动作）**：决策的执行和编排，使系统从"分析型"变为"运营型"
- **Security（安全）**：贯穿数据、逻辑、动作的细粒度治理和权限控制

### 传统哲学 / 知识工程 Ontology

在哲学和计算机科学中，Ontology 是**对存在本质的形而上学研究**，在知识工程中则指**对概念、实体及其关系的显式规范**。

经典定义（Tom Gruber, 1993）："An ontology is a **formal, explicit specification of a shared conceptualization**."

## Palantir Ontology 的关键概念

- **Object types（对象类型）**：语义模型中的名词——设备、产品、订单等
- **Link types（链接类型）**：对象间的语义关系
- **Properties（属性）**：对象的特征描述
- **Action types（动作类型）**：语义模型中的动词——对对象执行的操作
- **Functions（函数）**：业务逻辑的编写和演化
- **Interfaces（接口）**：对象类型的多态抽象层
- **Scenarios（场景）**：安全的沙箱化决策环境

## 为什么 Ontology 在 AI 时代重要

Palantir 的 Why Ontology 文档指出：

1. 传统数据架构**不捕获决策背后的推理过程和后续行动**
2. Ontology 是决策中心的（decision-centric），而不是数据中心的
3. 它为 AI Agent 提供了**丰富、密集的上下文**，Agent 可以通过 Ontology 驱动的工具安全地查询、推理和行动
4. 安全治理在 Agent 场景下也适用——每个 Agent 可以像新团队成员一样，逐步获得权限

## 相关来源

- [[Knowledge/wiki/资料/Palantir Ontology Overview]]
- [[Knowledge/wiki/资料/Palantir Why Ontology]]
- [[Knowledge/wiki/资料/Palantir Core Concepts]]

## 相关页面

- [[Knowledge/wiki/概念/Ontology 数据体系]]
- [[Knowledge/wiki/概念/Ontology 决策四要素]]
- [[Knowledge/wiki/概念/Ontology 与 AI Agent 的关系]]
