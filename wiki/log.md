# 操作日志

## 2026-07-22｜初始化 + 首次资料导入

### 知识库初始化

- 创建 Knowledge Wiki 目录结构（source/、wiki/、schema/）
- 创建 wiki/index.md、wiki/README.md、wiki/log.md
- 创建 wiki/ 子目录：资料/、实体/、概念/、综合/、对比/、查询/
- 安装 schema 文件（SKILL.md、verify_wiki.py）
- 初始化 git 仓库，创建 GitHub 远程仓库 `Mr-Yoje/knowledge-wiki` 并推送
- 保存 GitHub PAT 到 secrets.json

### 首次资料导入

- 调研 Mem0 架构、Graph Memory 创建/去重/更新机制
- **新增概念页**：[[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节|Mem0 架构与知识图谱技术细节]]
- **新增资料页**：[[Knowledge/wiki/资料/原始资料层说明]]
- 更新 wiki/index.md 添加概念页入口
- 修复断链：README.md 中的示例链接、概念页中的待创建页面引用
- 运行体检脚本 verify_wiki.py：问题已全部修复（0 broken links, 0 missing index）

### 深入 Mem0 Add 模式与冲突处理

- 调研 Mem0 的 add() 默认 ADD-only 模式 vs update() 显式更新模式的选择问题
- 深入分析 DEFAULT_UPDATE_MEMORY_PROMPT 的 ADD/UPDATE/DELETE/NONE 四选一决策逻辑
- 从源码确认：LLM 驱动的语义去重是唯一的冲突检测手段，无独立规则引擎
- 确认 Platform 和 OSS 的冲突处理逻辑相同
- **新增概念页**：[[Knowledge/wiki/概念/Mem0的Add模式与冲突处理机制|Mem0 的 Add 模式与冲突处理机制]]
- 更新 wiki/index.md

### Agent Eval 评估体系调研

- 系统调研 Agent 评估的 Benchmark、框架、通用指标和评测流程
- 覆盖：GAIA、AgentBench、SWE-bench、BFCL、ToolBench、WebArena、MINT 等核心 Benchmark
- 梳理四大评测维度：工具调用、多步规划、环境交互、安全鲁棒
- 总结标准评测流程（定义→运行→评分→报告）和通用指标
- 收录 LangSmith、OpenAI Evals 等评测平台信息
- 分析当前趋势（FC 标准化、动态环境、安全评测崛起）与挑战（成本高、复现难、数据污染）
- **新增概念页**：[[Knowledge/wiki/概念/AgentEval评估全景|Agent Eval 评估全景]]

### 补充参考文章 + searxng 修复

- 发现 searxng 实际运行在 **127.0.0.1:8080**（而非 4000），已定位并确认可用
- 根据参考文章（warm3snow《Agent Eval 最佳实践》），提取核心三层架构体系、DeepEval 代码实践、pass@k 指标选择策略、生产采样与成本控制方案
- **新增资料页**：[[Knowledge/wiki/资料/AgentEval最佳实践|Agent Eval 最佳实践指南]]
- 更新概念页：新增 DeepEval 框架介绍和参考资料链接
- 更新 wiki/index.md
