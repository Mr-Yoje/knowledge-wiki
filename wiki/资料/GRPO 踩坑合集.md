---
type: source
tags: [source-summary, AgentRL]
source_name: "GRPO 训练会踩的坑合集"
source_file: "小红书笔记"
url: "https://www.xiaohongshu.com/discovery/item/6a4f7ea50000000008003c47"
created: 2026-07-23
updated: 2026-07-23
status: initialized
---

# GRPO 踩坑合集

## 来源信息

- **来源**: 小红书笔记，作者 Vincent ｜ AIGC
- **时间**: 2026.07

## 一句话摘要

GRPO 训练中的常见陷阱及排查经验。

## 解决的问题

跑 GRPO 出现 loss 一开始为 0、reward 半路掉、部分 batch 梯度为 0 等现象时，如何区分是代码 bug 还是算法本身的特性。

## 关键判断

- GRPO 的 loss 不是误差，而是策略移动方向信号，初始 loss≈0 是正常的
- 组内 reward 全对/全错 → advantage=0 → 白训
- Reward 半路崩不是 reward 先掉，是策略先漂坏
- 应该比 reward 更早盯 KL、entropy、长度分布、格式错误率、组内 reward 方差

## 可沉淀知识点

- Dr.GRPO 指出两个归一化副作用：按长度归一会让模型越写越长，除以 std 会让简单题和极难题权重过大
- 训练和推理 log-prob 不对齐（vLLM vs training forward）是一个隐蔽的工程问题
- 冒烟测试：ratio≈1、advantage 非零比例、verifier 体检、小步更新、holdout 对齐

## 相关页面

- [[Knowledge/wiki/综合/Agent RL 强化学习全景]]
- [[Knowledge/wiki/概念/GRPO]]
- [[Knowledge/wiki/综合/Agent RL 实战经验]]
- [[Knowledge/wiki/概念/Agent RL Collapse]]
