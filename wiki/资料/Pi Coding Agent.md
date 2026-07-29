---
type: source
tags: [source-summary, pi, coding-agent, agent-harness, pi-dev]
source_name: Pi Coding Agent — Minimal Agent Harness
author: Earendil Inc. (Mario Zechner / badlogic)
url: https://github.com/earendil-works/pi
created: 2026-07-28
updated: 2026-07-29
status: active
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
│  pi-agent-core (Agent Runtime)      │ ← Agent 循环 + 工具调用 + 状态管理
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

还有 Slack/聊天自动化用的 `@earendil-works/pi-chat`（https://github.com/earendil-works/pi-chat）。

### 五种使用模式

| 模式 | 命令/方式 | 用途 |
|------|----------|------|
| **Interactive** | `pi` | 完整 TUI 体验 |
| **Print/JSON** | `pi -p "query"` / `--mode json` | 脚本/自动化调用 |
| **RPC** | stdin/stdout JSONL 协议 | 非 Node.js 集成 |
| **SDK** | 嵌入 Node.js 应用 | 构建自定义工具（OpenClaw 就用这个） |
| **Ephemeral** | `pi --no-session` | 一次性查询，不保存会话 |

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

**会话相关命令**：

| 命令 | 作用 |
|------|------|
| `/tree` | 跳转到任何历史节点并从那里继续（同文件） |
| `/fork` | 从某个历史用户消息创建**新会话文件** |
| `/clone` | 复制当前激活分支到新会话文件 |
| `/share` | 导出为私有 GitHub Gist，生成可分享的 HTML 链接 |
| `/export` | 导出会话为 HTML |
| `/resume` | 交互式浏览和选择历史会话 |
| `/new` | 开始新会话 |
| `/session` | 查看当前会话信息（文件、ID、消息数、tokens、费用） |
| `/name` | 设置会话可读名称 |

**/tree vs /fork vs /clone 的区别**：

| 特性 | /tree | /fork | /clone |
|------|-------|-------|--------|
| 输出 | 同文件 | 新文件 | 新文件 |
| 视图 | 完整树 | 用户消息选择器 | 当前激活分支 |
| 典型用途 | 原地探索替代方案 | 从历史提示开始新会话 | 继续前先复制当前进度 |
| 摘要 | 可选分支摘要 | 无 | 无 |

**resume 选择器功能**：
- 搜索：输入文字搜索
- `Ctrl+P`：切换路径显示
- `Ctrl+S`：切换排序
- `Ctrl+N`：只显示有名字的会话
- `Ctrl+R`：重命令
- `Ctrl+D`：删除（优先用系统回收站）

**tree 视图控制**：
- `↑/↓`：导航可见条目
- `←/→`：翻页
- `Ctrl+←/→` 或 `Alt+←/→`：折叠/展开或跳转分支段
- `Shift+L`：设置/清除标签
- `Shift+T`：切换标签时间戳
- `Enter`：选择
- `Esc/Ctrl+C`：取消
- `Ctrl+O`：循环过滤模式（default/no-tools/user-only/labeled-only/all）

所有分支存在于单文件中，不需要多个会话文件。每当 `/tree` 离开一个分支时，Pi 可以自动总结被遗弃的分支并将摘要附加到新位置，保留关键上下文而不回放整个分支。

### 3. Context Compaction（上下文紧凑）

当上下文即将超限时自动触发，或手动 `/compact [instructions]` 执行：

```
触发条件: contextTokens > contextWindow - reserveTokens (默认 16K, 可在 settings.json 配置)
工作流程:
  1. 从最新消息反向遍历，累计直到 keepRecentTokens (默认 20K, 可配置)
  2. 旧的 messages 被 LLM 总结为结构化摘要
  3. 摘要 + 最近消息 → 新的上下文窗口
  4. 多次紧凑时，摘要会基于上一次紧凑的边界累积

最终 LLM 看到的:
  [系统提示] [旧摘要] [最近N条消息]
```

**Compaction 可视流程**：

```
压缩前:
 entry: 0  1  2  3  4  5  6  7  8  9
 ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
 │hdr │usr │ass │tool│usr │ass │tool│tool│ass │tool│
 └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
 └────────┬────────┘ └────────────┬────────────┘
  messagesToSummarize    kept messages
           ↑
  firstKeptEntryId (entry 4)

压缩后 (新增 cmp entry 10):
 ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
 │hdr │usr │ass │tool│usr │ass │tool│tool│ass │tool│cmp │
 └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
 └───┬───┘ └─────────────────┬──────────────────┘
 不发给 LLM             发给 LLM
                            ↑
                   从 firstKeptEntryId 开始
```

完全可定制——Extension 可以接管 compaction 逻辑，实现主题式紧凑、代码感知总结等。Compaction 和 branch summary 使用独立的 session ID 生成，且对支持 provider 的模型禁用 prompt-cache 写入（因为一次性提示不太可能被复用）。

### 4. 扩展系统（Extension）

Extensions 是 **TypeScript 模块**，可以访问：工具注册、命令注册、快捷键、事件生命周期、自定义 UI。

**事件生命周期（覆盖全面）**：

| 生命周期 | 事件 |
|----------|------|
| **Startup** | startup / beforeModelReady / afterModelReady |
| **Resource** | 资源加载事件 |
| **Session** | session_before_turn / session_after_turn |
| **Agent** | agent_before_turn / agent_after_turn |
| **Model** | 模型切换事件 |
| **Tool** | tool_before_execution / tool_after_execution |
| **Bash** | 用户 Bash 执行事件 |
| **Input** | 输入事件 |
| **Compaction** | session_before_compact / session_before_tree 等 |

**Extension API 核心能力**：

通过 `ExtensionAPI` 对象，Extension 可以：
- `pi.on(event, handler)` — 监听任意事件
- `pi.registerTool(definition)` — 注册自定义工具
- `pi.registerCommand(name, options)` — 注册自定义命令
- `pi.registerShortcut(shortcut, options)` — 注册快捷键
- `pi.registerFlag(name, options)` — 注册 CLI flag
- `pi.sendMessage(message, options)` — 向代理发送消息
- `pi.sendUserMessage(content, options)` — 模拟用户消息
- `pi.setModel(model)` — 切换模型
- `pi.setThinkingLevel(level)` — 设置思考级别
- `pi.registerMessageRenderer(customType, renderer)` — 自定义消息渲染
- `pi.registerEntryRenderer(customType, renderer)` — 自定义条目渲染
- `pi.exec(command, args, options)` — 内置 exec 工具

**Extension Context** — 通过 `ExtensionContext` 对象，Extension 可以获取：
- `ctx.ui` — 终端 UI 对象（TUI 模式下可用）
- `ctx.mode` — 当前模式（interactive/print/rpc）
- `ctx.sessionManager` — 会话管理器
- `ctx.modelRegistry / ctx.model` — 模型注册表/当前模型
- `ctx.cwd` — 当前工作目录
- `ctx.signal` — AbortSignal，监听关闭信号
- `ctx.compact()` — 触发上下文紧凑
- `ctx.getSystemPrompt()` — 获取系统提示
- `ctx.newSession()` / `ctx.fork()` / `ctx.navigateTree()` — 会话管理

**Dynamic Context**：Extension 可以在每轮交互前注入消息，实现 RAG、长期记忆等。

50+ 官方示例包括：sub-agent、plan-mode、SSH execution、sandboxing、MCP integration、permission gates、custom UI widgets 等。

### 5. Skills（Agent Skills 标准）

Pi 实现了 [Agent Skills 规范](https://agentskills.io/specification)，Skill 是带 `SKILL.md` 的自包含能力包。

- 采用 **progressive disclosure**：启动时只加载名称和描述到 System Prompt（XML 格式），完整指令按需加载
- 加载位置：
  - 全局：`~/.pi/agent/skills/`、`~/.agents/skills/`
  - 项目（仅受信任）：`.pi/skills/`、`.agents/skills/`（递归查找祖先目录）
  - Packages：`skills/` 目录或 `pi.skills` 字段
  - Settings：`skills` 数组
  - CLI：`--skill` 参数
- 可复用其他框架的技能：Claude Code / OpenAI Codex 的技能目录可直接引用（settings.json 中添加 `"skills": ["~/.claude/skills"]`）
- `/skill:name` 命令手动触发，支持传参
- `--no-skills` 禁用发现（显式 `--skill` 仍有效）

**SKILL.md 结构**：
```
---
name: my-skill
description: 1-1024 字符，描述功能和适用场景
license: MIT
compatibility: 环境要求（可选）
metadata: 任意键值
allowed-tools: 预批准工具列表（实验性）
disable-model-invocation: true  # 从 system prompt 隐藏，需手动 /skill:name 触发
---

# My Skill

## Setup
安装/初始化步骤

## Usage
具体使用说明，相对路径引用脚本和资源
```

**Skill 命名规则**：a-z、0-9、连字符，1-64 字符。Pi 允许名称与目录名不同（规范要求一致，但 Pi 认为共享目录时不合理）。

### 6. 15+ LLM 提供商

一口气支持：Anthropic、OpenAI、Google、Azure、Bedrock、Mistral、Groq、Cerebras、xAI、Hugging Face、Kimi For Coding、MiniMax、NVIDIA、OpenRouter、Ollama、llama.cpp。

Pi 还支持内置的 llama.cpp 路由器，可通过 `/llama` 管理本地模型。

- `/model` 或 `Ctrl+L` 切换模型
- `Ctrl+P` 轮询收藏模型
- `models.json` 添加自定义模型
- Extensions 注册自定义提供商和 OAuth 流程

## 安装方式

```bash
# npm 全局安装
npm install -g --ignore-scripts @earendil-works/pi-coding-agent

# Linux/macOS 一键脚本
curl -fsSL https://pi.dev/install.sh | sh
```

`--ignore-scripts` 表示 Pi 的正常 npm 安装不需要运行生命周期脚本。

## 安全与容器化

Pi **不内置权限系统**（不限制文件系统、进程、网络或凭据访问），默认以启动用户/进程的权限运行。

有三种容器化模式：
1. **Gondolin Extension**：宿主上保留 pi 和 provider 认证，将内置工具和 `!` 命令路由到本地 Linux 微 VM 中执行
2. **Plain Docker**：整个 pi 进程运行在本地容器中
3. **OpenShell**：整个 pi 进程运行在策略控制的沙箱中

完整容器化指南：https://pi.dev/docs/latest/containerization

## 供应安全（Supply-chain Hardening）

Pi 对依赖管理有严格的策略：
- 外部直接依赖**锁定精确版本**（`save-exact=true`）
- `min-release-age=2`：npm 解析时避免使用当天发布的依赖
- `package-lock.json` 是依赖的事实基准，pre-commit 阻止意外的 lockfile 提交（除非设 `PI_ALLOW_LOCKFILE_CHANGE=1`）
- `npm run check` 验证锁定直接依赖、TypeScript 导入兼容性和 shrinkwrap
- 发布前做本地发布演练（`npm run release:local`），在 repo 外创建隔离的 npm 和 Bun 安装
- CI 使用 `npm ci --ignore-scripts`，定时运行 `npm audit`
- shrinkwrap 生成有显式的生命周期脚本批准名单，新引入的脚本依赖会被检查阻止

## 与其他 Agent 框架的核心差异

| 维度 | Pi | Claude Code / Cursor |
|------|-----|---------------------|
| **设计哲学** | 原语而非功能，极小内核 | 密封产品，预设工作流 |
| **扩展性** | TypeScript Extension + Skills | 有限的扩展机制 |
| **会话模型** | 树结构 JSONL（单文件多分支） | 线性会话列表 |
| **MCP** | 不内置，用 Extension 或 CLI + README | 原生支持 MCP |
| **权限模型** | 无内置，建议容器隔离 | 内置权限弹窗 |
| **上下文管理** | 自动紧凑 + 可定制 Extension hooks | 内置紧凑，有限定制 |
| **SDK 模式** | 一等支持，OpenClaw 就是集成案例 | 通常不自带 SDK |

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
| **输出模式** | Interactive / Print / JSON / RPC / SDK / Ephemeral |
| **权限模型** | 无内置权限系统，建议容器化（Gondolin/Docker/OpenShell） |
| **语言** | TypeScript（Monorepo，npm 发布） |
| **许可证** | MIT |
| **组织** | Earendil Inc.（Mario Zechner / badlogic） |
| **首页** | https://pi.dev |
| **Discord** | https://discord.com/invite/3cU7Bz4UPx |
| **npm** | `@earendil-works/pi-coding-agent` |

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

### 深入："No MCP" 的设计立场

Mario Zechner 专门写了一篇博客 [What if you don't need MCP at all?](https://mariozechner.at/posts/2025-11-02-what-if-you-dont-need-mcp/) 阐述了核心观点：

1. **MCP Server 太臃肿** — 以 Playwright MCP 为例，21 个工具消耗 13.7K tokens（Claude 上下文的 6.8%）；Chrome DevTools MCP 26 个工具消耗 18K tokens（9%）。这么多工具会混淆 Agent。
2. **可组合性问题** — MCP 返回的结果必须通过 Agent 的上下文层才能持久化或与其他结果组合，缺乏直接组合能力。
3. **难以扩展** — 要修改已有 MCP Server 需要理解整个代码库。
4. **替代方案** — CLI 工具 + README 就是天然的 MCP 接口。Agent 可以运行 Bash、写代码，而 Bash 和代码本身就是可组合的。

他用**浏览器 DevTools** 举例，展示了如何用 4 个极简 Node.js 脚本（start.js / nav.js / eval.js / screenshot.js）+ 一个 README 就实现了 Playwright MCP 的浏览器控制功能，代码量极少、上下文消耗极低、且 Agent 可以按需修改。

## 可沉淀的知识点

1. **"原语而非功能"的设计哲学**是 Pi 最区别于 Claude Code、Cursor 等产品的点。它假设开发者有能力构建自己需要的功能，而不是替开发者做所有决策。这种哲学在 AI Agent 框架中是独特而有力的。
2. **树形会话**是 Pi 的亮点——单文件多分支存储，让 Agent 可以在不丢失上下文的情况下探索多条路径。这在多次实验性编码场景中非常有用。`/fork`、`/clone` 和 `/tree` 的三者配合覆盖了不同的分支使用场景。
3. **Pi 的 Context Engineering 能力很强**：精简 System Prompt + 可定制 AGENTS.md/SYSTEM.md + 事件驱动的 Extension（可注入 Dynamic Context）+ 智能 Compaction — 让真正想做 Context Engineering 的人有全套工具。
4. **Pi 与 OpenClaw 的关系**：OpenClaw 是 Pi SDK 模式嵌入的真实案例——说明 Pi 不只是一个独立的编码 Agent CLI，也可以作为嵌入式的 Agent 运行时。
5. **Pi 不做 MCP 是一个鲜明的设计立场**，核心论点是 CLI 工具 + README 本身就是天然的 MCP 接口，更轻量、更可组合、更容易修改。这不仅是技术选择，也是设计哲学的自然延伸。
6. **供应安全是 Pi 的一个隐藏亮点**：从精确锁依赖、shrinkwrap 生成、CI 审计到发布前隔离演练，Pi 在供应链安全上做了大量的工业级实践，这对依赖依赖的 Agent 框架来说尤为重要。

## 相关来源

- 官方网站：https://pi.dev
- GitHub 主仓库：https://github.com/earendil-works/pi
- 文档：https://pi.dev/docs/latest
- 博客文章（设计理念）：https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
- 为什么不做 MCP：https://mariozechner.at/posts/2025-11-02-what-if-you-dont-need-mcp/
- Agent Skills 规范：https://agentskills.io/specification
- Pi Packages：https://pi.dev/packages
- npm 包：https://www.npmjs.com/package/@earendil-works/pi-coding-agent
- OpenClaw（Pi SDK 集成案例）：https://github.com/OpenClaw/OpenClaw
- Slack 聊天自动化的 pi-chat：https://github.com/earendil-works/pi-chat
- Discord 社区：https://discord.com/invite/
