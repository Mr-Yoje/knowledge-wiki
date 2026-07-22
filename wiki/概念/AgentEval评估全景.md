---
type: concept
tags: [concept, agent-eval, benchmark, evaluation]
created: 2026-07-22
updated: 2026-07-22
status: evolving
---

# Agent Eval：AI Agent 评估全景

AI Agent 评估（Agent Eval）是衡量 LLM 作为自主 Agent 能力的关键环节。与传统 LLM 评测不同，Agent Eval 关注的是**多轮交互、工具调用、环境反馈、任务完成度**等动态能力，而非单纯的问答准确率。

---

## 一、框架与工具

### OpenAI Evals
- **定位**：通用的 LLM 与 LLM 系统评估框架
- **特点**：开源注册中心（registry of benchmarks）；支持自定义 eval
- **使用方式**：定义 YAML 配置文件 + Python 实现评测逻辑
- **适用**：通用 LLM 能力评测，非 Agent 专用但可扩展

### AgentBench（THUDM, ICLR'24）
- **定位**：首个系统化评估 LLM-as-Agent 的 benchmark
- **覆盖**：8 个环境（5 个全新 + 3 个重编）
- **最新版**：AgentBench FC（Function Calling 版），集成 AgentRL，支持 Docker 容器化部署
- **评估环境**：
  - **操作系统 (OS)** — Shell 命令执行
  - **数据库 (DB)** — SQL 查询与操作
  - **知识图谱 (KG)** — 图查询与推理
  - **数字卡牌 (DCG)** — 策略游戏
  - **横向思维谜题 (LTP)** — 逻辑推理
  - **家务 (HH)** — ALFWorld 环境中的指令执行
  - **网购 (WS)** — WebShop 商品搜索与购买
  - **网页浏览 (WB)** — Mind2Web 网页操作

### GAIA（Meta FAIR / Hugging Face）
- **定位**：通用 AI 助手能力的标杆级 benchmark
- **论文**：arXiv 2311.12983（Mialon et al., 2023）
- **核心理念**：提出"如果解决 GAIA 就代表 AI 研究的里程碑"
- **题目类型**：需要推理、多模态处理、网页浏览、工具调用等综合素质的真实世界问题
- **关键数据**：人类准确率 92% vs GPT-4+plugins 仅 15%
- **题量**：466 道题，300 道保留答案用于 leaderboard
- **意义**：Agent 能力（工具使用、多步推理）与人类水平间存在巨大鸿沟

### LangSmith（LangChain）
- **定位**：Agent & LLM 可观测性平台
- **核心能力**：Tracing（调用链追踪）+ Monitoring（实时监控）+ Evaluation（评测）+ Insights（自动分析）
- **评测方式**：LLM-as-judge、代码评估、在线评估
- **独特点**：SmithDB 专用数据库、OTel 集成支持、BYOC/自托管

### VisualAgentBench（THUDM）
- **定位**：评估和训练视觉基础 Agent
- **环境**：具身（OmniGibson, Minecraft）+ GUI（Mobile, WebArena-Lite）+ 视觉设计（CSS）

### OASIS（CAMEL-AI）
- **定位**：大规模社交 Agent 模拟评测
- **特点**：支持百万级 Agent 仿真

---

## 二、核心 Benchmark 对比

| Benchmark | 发布方 | 领域 | 任务数 | 评测维度 | 是否支持 FC | 特色 |
|-----------|--------|------|--------|----------|------------|------|
| **GAIA** | Meta FAIR | 通用助手 | 466 | 推理+多模态+工具+网页 | 是 | 人类92% vs GPT-4 15% |
| **AgentBench** | THUDM | 通用 Agent | 8 类环境 | OS/DB/KG/Game/Web/... | v2+支持 | 8个Docker化环境 |
| **WebArena** | 多校联合 | 网页操作 | 812 | 网页任务完成度 | 是 | 真实浏览器环境 |
| **SWE-bench** | Princeton | 代码工程 | 2,294 | GitHub Issue 解决率 | 是 | Agent写PR的能力 |
| **ToolBench** | 清华 | 工具调用 | 16k+ API | API调用准确率 | 是 | 覆盖数千真实API |
| **BFCL** | Berkeley | 函数调用 | 2,000+ | Function call 精准度 | 是 | 多语言/多轮FC |
| **MINT** | MSRA | 多轮交互 | 756 | 利用反馈改进能力 | 否 | Agent自我修正 |

---

## 三、Agent 评估的四大维度

### 1. 工具调用（Function Calling / Tool Use）
- **精准度**：API 参数匹配是否正确（名称、类型、必填/可选）
- **多样性**：是否能在多工具间切换/组合
- **错误恢复**：工具返回错误时能否正确重试或回退
- **代表 benchmark**：BFCL（Berkeley Function Calling Leaderboard）、ToolBench、Gorilla APIBench

### 2. 多步规划与推理（Multi-step Planning & Reasoning）
- **任务分解**：将复杂目标拆解为可执行的子步骤
- **回溯修正**：子步骤失败后能否调整后续计划
- **长程依赖**：多步操作之间能否保持状态一致性
- **代表 benchmark**：GAIA（多步推理）、AgentBench（OS/DB 环境）

### 3. 环境交互与反馈利用（Environment Interaction & Feedback）
- **状态感知**：能否正确理解环境返回的状态
- **反馈整合**：能否利用环境的正/负反馈调整行为
- **容错能力**：在部分失败的情况下能否继续完成任务
- **代表 benchmark**：MINT（利用反馈）、WebArena（浏览器状态）、ALFWorld（模拟环境）

### 4. 安全与鲁棒性（Safety & Robustness）
- **指令注入防御**：能否抵御 prompt injection
- **边界约束**：是否会在工具调用中做越权操作
- **幻觉控制**：是否会编造不存在的工具或 API
- **退路策略**：无法完成任务时是否给出合理的拒绝或降级

---

## 四、通用评估指标

### 任务级指标

| 指标 | 英文 | 含义 | 适用场景 |
|------|------|------|---------|
| **任务完成率** | Success Rate / Task Completion | Agent 完成任务的百分比 | 几乎所有 Benchmark |
| **部分进度** | Partial Progress Score | 步长式奖励（不完全成功也计分） | WebArena, ALFWorld |
| **平均步数** | Avg Steps / Turns | 完成任务所需的交互轮数 | AgentBench, MINT |
| **效率比** | Efficiency Ratio | 完成质量 / 步数 | SWE-bench |
| **Pass@k** | Pass@k | k 次尝试中至少成功 1 次 | 代码生成类 |

### 工具调用指标

| 指标 | 英文 | 含义 |
|------|------|------|
| **调用准确率** | Accuracy | 选择的工具和参数是否正确 |
| **参数匹配度** | Parameter Match Rate | FC 参数类型、格式的合规性 |
| **幻觉调用率** | Hallucination Rate | 调用了不存在工具的比例 |
| **调用多样性** | Tool Diversity | 在多工具场景下是否覆盖了必要的工具组合 |

### 质量类指标

| 指标 | 英文 | 含义 |
|------|------|------|
| **成本** | Cost | 每次任务调用的 token 消耗 |
| **延迟** | Latency | P50 / P95 / P99 响应时间 |
| **可重复性** | Reproducibility | 相同输入下输出的一致性 |
| **LLM-as-Judge 评分** | LLM Judge Score | 用 LLM 评估输出质量（1-10） |

---

## 五、评测流程（标准流水线）

### 步骤 1：定义评测集
- 选取/构造测试用例（黄金答案或预期行为）
- 每个用例包含：任务描述 + 初始环境状态 + 期望结果 + 评分规则
- 注意数据污染（data contamination）问题——测试集不应出现在训练数据中

### 步骤 2：运行 Agent
- Agent 通过 API 或本地环境执行任务
- 收集完整轨迹（trace）：每步思考 + 工具调用 + 环境返回
- 记录元数据：tokens 消耗、延迟、调用次数、错误状态

### 步骤 3：自动评分
- **精确匹配**：输出与预期答案精确匹配（简单任务）
- **LLM-as-Judge**：用强 LLM（如 GPT-4）评估回答质量
- **程序化评分**：根据任务特定逻辑自动判分（SQL 结果比较、文件存在检查）
- **语义等价**：用 embedding 余弦相似度判断语义等价性

### 步骤 4：报告与分析
- 聚合指标：成功率、平均步数、成本
- 分维度分析：按工具类型、难度、错误类型分类
- 失败分析：对失败 case 进行分类（规划错误、工具调用错误、幻觉、超时）
- 回归测试：与基线版本对比，检测能力变化

---

## 六、关键趋势与挑战

### 趋势
1. **从静态 QA 到动态环境**：AgentBench、WebArena 等采用真实交互环境替代纯文本评测
2. **函数调用（FC）成为标配**：BFCL、AgentBench FC 等专门聚焦 FC 能力
3. **从单轮到多轮**：MINT、GAIA 强调多轮交互和反馈利用
4. **评测平台化**：LangSmith、Arize、Weights & Biases 等提供完整的 trace + eval 基础设施
5. **安全评测崛起**：prompt injection、越权调用等安全维度的评估日益受重视

### 挑战
1. **评估成本高**：Agent 评测需要反复调用 LLM，token 消耗远大于纯文本评测
2. **环境一致性难保证**：Docker 化、随机种子、网络状态等因素影响复现
3. **评分主观性**：LLM-as-Judge 存在位置偏差、自我偏好等系统性偏差
4. **数据污染问题**：多数 Benchmark 的测试集已被 LLM 训练语料覆盖
5. **长尾任务覆盖不足**：现有 Benchmark 偏向编程和网页操作，专业领域（医疗、法律）评估不充分

---

## 七、评估框架选择建议

| 如果你的需求 | 推荐方案 |
|-------------|---------|
| 快速验证 LLM 的 Agent 基础能力 | GAIA + AgentBench |
| 深度评测函数调用能力 | BFCL + ToolBench |
| 评测代码类 Agent | SWE-bench + HumanEval |
| 评测网页操作 Agent | WebArena |
| 生产环境持续监控 | LangSmith（trace + monitor + eval） |
| 学术研究/发论文 | AgentBench FC + VisualAgentBench |
| 安全评测 | prompt injection test suite + 自定义红队 |

## 相关来源

- GAIA 论文（arXiv 2311.12983）— https://arxiv.org/abs/2311.12983
- AgentBench — https://github.com/THUDM/AgentBench
- OpenAI Evals — https://github.com/openai/evals
- LangSmith — https://www.langchain.com/langsmith
- Berkeley Function Calling Leaderboard (BFCL) — https://gorilla.cs.berkeley.edu/leaderboard.html
- SWE-bench — https://www.swebench.com
- WebArena — https://webarena.dev

## 相关页面

- 待创建：Agent 评估的 LLM-as-Judge 方法论
- 待创建：主流 LLM Agent 框架对比（LangGraph / AutoGen / CrewAI / OpenAI Assistants）
