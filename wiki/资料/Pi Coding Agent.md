---
type: source
tags: [source-summary, pi, coding-agent, agent-harness, pi-dev]
source_name: Pi Coding Agent — Minimal Agent Harness
author: Earendil Inc. (Mario Zechner / badlogic)
url: https://github.com/earendil-works/pi
created: 2026-07-28
updated: 2026-07-28
status: initialized
---

# Pi Coding Agent

## 一句话摘要

Pi 是一个**极简主义 Agent 框架**，遵循"原语而非功能"的设计哲学——核心只提供最基础的 Agent 循环、统一 LLM API、TUI 和会话管理，把子 Agent、计划模式、MCP 等功能都交给扩展系统去实现。

## 解决的问题

Pi 要解决的核心问题是：**现有 Agent 框架（Claude Code、Cursor 等）都是"密封产品"，用户被迫适应框架的预设工作流而无法按自己的方式调整**。Pi 的理念是"改造框架来适应你的工作流，而不是反过来"。

## 核心架构

### 四层架构

```
┌─────────────────────────────────────┐
│  pi-coding-agent (CLI / TUI)        │ ← 用户面向的交互层
├─────────────────────────────────────┤
│  pi-agent-core (Agent Runime)       │ ← Agent 循环 + 工具调用 + 状态管理
├─────────────────────────────────────┤
│  pi-ai (Unified LLM API)            │ ← 15+ 提供商的统一接口
├─────────────────────────────────────┤
│  pi-tui (Terminal UI)               │ ← 差分渲染 TUI 库
└─────────────────────────────────────┘
```

**四个 npm 包**：
- `@earendil-works/pi-ai` — 统一多提供商 LLM API（OpenAI/Anthropic/Google/...）
- `@earendil-works/pi-agent-core` — Agent 运行时，工具调用和状态管理
- `@earendil-works/pi-coding-agent` — 交互式编码 Agent CLI（用户直接用的）
- `@earendil-works/pi-tui` — 终端 UI 库，支持差分渲染

### 四种使用模式

| 模式 | 命令 | 用途 |
|------|------|------|
| **Interactive** | `pi` | 完整 TUI 体验 |
| **Print/JSON** | `pi -p "query"` / `--mode json` | 脚本/自动化调用 |
| **RPC** | stdin/stdout JSONL 协议 | 非 Node.js 集成 |
| **SDK** | 嵌入 Node.js 应用 | 构建自定义工具（OpenClaw 就用这个） |

## Agent 循环流程

```
用户输入 → 编译上下文（System Prompt + 历史 + 记忆）
  → LLM 调用（统一 pi-ai API）
  → 工具执行
  → 结果注入上下文
  → LLM 再次调用...（直到生成最终回复）
  → 输出 → 会话持久化（JSONL 文件，树形结构）
```

Pi 的 Agent 循环使用 **tool calling** 模式，LLM 生成工具调用 → 执行 → 结果反馈 → 继续，直到 LLM 选择直接回复。

## 关键设计特征

### 1. 极简系统提示

Pi 的 [system prompt](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/system-prompt.ts) 非常精简，留出大量上下文空间给用户。

- **AGENTS.md**：项目级指令，启动时从 `~/.pi/agent/`、父目录和当前目录加载
- **SYSTEM.md**：每个项目可替换或追加默认系统提示
- 可进可退——想用默认就用默认，想精调就写 AGENTS.md

### 2. 树形可共享会话

Pi 不把会话存为线性列表，而是**树结构存储**在每个会话 JSONL 文件中。

```
├─ user: "Hello"
│  └─ assistant: "Hi!"
│     ├─ user: "方案 A"        ← 旧分支（已被 tree 离开）
│     │  └─ assistant: "..."
│     └─ user: "方案 B"        ← 当前激活分支
│        └─ assistant: "..."
```

- `/tree` 命令：跳转到任何历史节点并从那里继续
- `/fork`：从某个历史用户消息创建新会话
- `/share`：导出为 GitHub Gist，生成可分享的 HTML
- 所有分支存在于单个文件中，不需要多个会话文件

### 3. Context Compaction（上下文紧凑）

当上下文即将超限时自动触发，或手动 `/compact` 执行：

```
触发条件: contextTokens > contextWindow - reserveTokens (默认 16K)
工作流程:
  1. 从最新消息反向遍历，累计直到 keepRecentTokens (默认 20K)
  2. 旧的 messages 被 LLM 总结为结构化摘要
  3. 摘要 + 最近消息 → 新的上下文窗口
  4. 多次紧凑时，摘要会基于上一次紧凑的边界累积

最终 LLM 看到的:
  [系统提示] [旧摘要] [最近N条消息]
```

完全可定制——Extension 可以接管 compaction 逻辑，实现主题式紧凑、代码感知总结等。

### 4. 扩展系统（Extension）

Extensions 是 **TypeScript 模块**，可以访问：工具注册、命令注册、快捷键、事件生命周期、自定义 UI。

事件生命周期覆盖全面：
- **Startup**：startup/beforeModelReady/afterModelReady
- **Session**：session_before_turn/session_after_turn
- **Agent**：agent_before_turn/agent_after_turn
- **Tool**：tool_before_execution/tool_after_execution
- **Compaction**：session_before_compact/session_before_tree 等

**Dynamic Context**：Extension 可以在每轮交互前注入消息，实现 RAG、长期记忆等。

50+ 官方示例包括：sub-agent、plan-mode、SSH execution、sandboxing、MCP integration、permission gates 等。

### 5. Skills（Agent Skills 标准）

Pi 实现了 [Agent Skills 规范](https://agentskills.io/specification)，Skill 是带 `SKILL.md` 的自包含能力包。

- 采用 **progressive disclosure**：启动时只加载名称和描述到 System Prompt，完整指令按需加载
- 加载位置：`~/.pi/agent/skills/` / 项目 `.pi/skills/` / `.agents/skills/` 等
- 可复用其他框架的技能：Claude Code / OpenAI Codex 的技能目录可直接引用
- `/skill:name` 命令手动触发

### 6. 15+ LLM 提供商

一口气支持：Anthropic、OpenAI、Google、Azure、Bedrock、Mistral、Groq、Cerebras、xAI、Hugging Face、Kimi For Coding、MiniMax、NVIDIA、OpenRouter、Ollama、llama.cpp。

- `/model` 或 `Ctrl+L` 切换模型
- `Ctrl+P` 轮询收藏模型
- `models.json` 添加自定义模型
- Extensions 注册自定义提供商

## 核心技术特征总结

| 特征 | 描述 |
|------|------|
| **核心哲学** | 原语而非功能——极小内核 + 强力扩展 |
| **架构模式** | 四层 Monorepo（AI + Agent + CLI + TUI） |
| **会话存储** | 树结构 JSONL 文件（单文件多分支） |
| **上下文管理** | 自动 Compaction + 可定制 Extension |
| **扩展方式** | TypeScript 事件驱动 Extension |
| **技能系统** | Agent Skills 标准，progressive disclosure |
| **LLM 支持** | 15+ 提供商，统一 API |
| **输出模式** | Interactive / Print / JSON / RPC / SDK |
| **权限模型** | 无内置权限系统，建议容器化（Gondolin/Docker/OpenShell） |
| **语言** | TypeScript（Monorepo，npm 发布） |
| **许可证** | MIT |

## "我们故意没做"的设计选择

Pi 最反直觉的设计就是**明确不内置**一系列常见功能，而是让扩展系统去做：

| 不做的功能 | 替代方案 |
|-----------|---------|
| **No MCP** | 构建 CLI 工具+README，或用 Extension 添加 MCP |
| **No Sub-agents** | 用 tmux spawn，或用 Extension 构建 |
| **No Permission Popups** | 用容器隔离（Gondolin/Docker/OpenShell） |
| **No Plan Mode** | 写 Plan 到文件，或用 Extension 构建 |
| **No Built-in To-dos** | 用 TODO.md |
| **No Background Bash** | 用 tmux |

## 可沉淀的知识点

1. **"原语而非功能"的设计哲学**是 Pi 最区别于 Claude Code、Cursor 等产品的点。它假设开发者有能力构建自己需要的功能，而不是替开发者做所有决策。
2. **树形会话**是 Pi 的亮点——单文件多分支存储，让 Agent 可以在不丢失上下文的情况下探索多条路径。这在多次实验性编码场景中非常有用。
3. **Pi 的 Context Engineering 能力很强**：精简 System Prompt + 可定制 AGENTS.md/SYSTEM.md + 事件驱动的 Extension — 让真正想做 Context Engineering 的人有全套工具。
4. **Pi 与 OpenClaw 的关系**：OpenClaw 是用 SDK 模式嵌入 Pi 的真实案例——说明 Pi 不只是一个独立的编码 Agent，也可以作为嵌入式的 Agent 运行时。
5. **Pi 不做 MCP** 是一个鲜明的设计立场（参见官网博客 "What if you don't need MCP"），认为 CLI 工具 + README 本身就是天然的 MCP 接口。

## 相关来源

- 官方网站：https://pi.dev
- GitHub 主仓库：https://github.com/earendil-works/pi
- 文档：https://pi.dev/docs/latest
- 博客文章（设计理念）：https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
- 为什么不做 MCP：https://mariozechner.at/posts/2025-11-02-what-if-you-dont-need-mcp/
- Agent Skills 规范：https://agentskills.io/specification
- Pi Packages：https://pi.dev/packages
- OpenClaw（Pi SDK 集成案例）：https://github.com/OpenClaw/OpenClaw

## 相关页面

- [[Knowledge/wiki/综合/Agent Memory框架全景]] — 外挂记忆层中的不同哲学对比
