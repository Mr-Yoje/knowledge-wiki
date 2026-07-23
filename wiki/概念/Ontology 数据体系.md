---
type: concept
tags: [concept, ontology]
created: 2026-07-23
updated: 2026-07-23
status: evolving
---

# Ontology 数据体系

## 对象类型（Object Types）

对象是 Ontology 的基本语义单元，对应现实世界中的实体——设备、产品、供应商、订单等。每个对象类型包含一组属性和链接。

## 链接类型（Link Types）

对象之间的语义关系。通过链接可以在 Ontology 中导航——例如从"订单"导航到"供应商"再导航到"生产工厂"。

## 属性（Properties）

对象的特征描述，支持丰富的元数据配置：
- 值格式化（value formatting）
- 条件格式化（conditional formatting）
- 派生属性（derived properties）
- 共享属性（shared properties）

## 值类型（Value Types）

用于定义可复用的数据类型约束，支持版本管理和权限控制。

## 接口（Interfaces）

接口提供了对象类型的多态抽象——允许多个对象类型共享相同的"形状"和"能力"。是 Ontology 实现类型多态的关键机制。

## 相关来源

- [[Knowledge/wiki/资料/Palantir Ontology Overview]]

## 相关页面

- [[Knowledge/wiki/综合/Ontology 本体论专题全景]]
- [[Knowledge/wiki/概念/Ontology 决策四要素]]
