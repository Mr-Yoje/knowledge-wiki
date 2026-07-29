---
type: source
tags: [source-summary, agent-sandbox, security, isolation, container, microvm, coding-agent, pi-dev]
source_name: Agent Sandbox 技术全景 — 从容器隔离到 Agent 运行沙箱
author: Bruce X
url: ""
created: 2026-07-29
updated: 2026-07-29
status: active
---

# Agent Sandbox 技术全景

## 一句话摘要

Agent Sandbox 技术为 AI Agent 提供**安全的代码执行环境**，使其能够在不暴露宿主系统的情况下运行代码、操作文件、访问网络。技术路线从传统容器隔离，演进到轻量级 VM（microVM）和用户态内核（Application Kernel），再到面向 Agent 场景的专用沙箱服务和框架内嵌沙箱。

## 为什么 Agent 需要沙箱？

AI Agent 的核心能力之一是"执行代码"——无论是 LLM 生成的代码、用户提交的脚本，还是从网络获取的程序。这带来了严重的安全风险：

- **宿主逃逸**：Agent 生成的恶意代码可能突破容器限制，控制宿主系统
- **数据泄露**：Agent 可能访问不该看的文件（API Key、密钥、用户隐私）
- **资源滥用**：Agent 可能被诱导运行挖矿脚本、发起 DDoS 攻击
- **供应链攻击**：Agent 安装的依赖包可能含有恶意代码

这些风险在以下场景中尤为突出：
- **Coding Agent**（Claude Code / Pi / Cursor）执行代码和 Bash 命令
- **Browser Agent** 操作浏览器和网页内容
- **Agent 平台**（OpenClaw / AutoGPT）运行用户编写的 Agent
- **LLM 生成的代码**在沙箱中测试和执行

## 隔离技术的三个层次

### 第一层：软件隔离（Namespace + Cgroup）

**原理**：利用 Linux 内核的 namespace 和 cgroup 机制，在同一个内核上创建隔离的进程视图。

**代表技术**：
- **Docker / containerd** — 标准的 OCI 容器
- **Podman** — 无守护进程容器

**优点**：轻量、启动快（毫秒级）、与现有工具链无缝集成
**缺点**：共享宿主内核，容器逃逸风险大（内核漏洞可突破 namespace）

**Agent 场景**：Docker 是最广泛使用的 Agent 沙箱方案。但多数 Agent 框架**默认不使用完整的容器隔离**，而是依赖 Agent 自身的权限控制。

### 第二层：用户态内核隔离（Application Kernel / Sandbox Kernel）

**原理**：拦截应用程序的系统调用，在用户态实现一个虚拟内核来处理这些调用，而非直接透传到宿主内核。系统调用不再直接到达宿主内核，而是被一个用户态的"应用内核"捕获和处理。这相当于在应用程序和宿主内核之间加了一个"翻译层"。

**代表技术**：

#### gVisor（Google，2018）
- **架构**：用户态内核（Sentry）拦截系统调用，通过 KVM 或 ptrace 平台执行
- **工作方式**：提供一个 OCI 运行时 `runsc`，可直接替换 Docker/K8s 的 runc
- **语言**：Go 编写（内存安全）
- **性能**：接近原生容器的 80-90%，但 I/O 密集场景下降明显
- **安全模型**：Sentey 进程运行在用户态，即使被攻破也只是一个普通进程，不会危害宿主
- **适用**：多租户容器环境、Serverless 平台
- **用户**：Google Cloud Run、Google Cloud Functions 等

```
应用进程 → 系统调用 → Sentry（用户态内核）→ KVM/ptrace → 宿主内核
```
**关键设计区别**：
- 不是 syscall filter（如 seccomp），不是隔离原语包装（如 firejail/AppArmor）
- 不是传统 VM（如 VirtualBox/QEMU）——没有虚拟化硬件
- 相当于一个合并的 Guest Kernel + VMM，或者是"强化版 seccomp"

### 第三层：硬件虚拟化隔离（microVM / Lightweight VM）

**原理**：利用 KVM 硬件虚拟化技术，为每个沙箱启动一个独立的、极简的虚拟机，拥有完整的独立内核。每个沙箱有自己独立的 Linux 内核，即使内核被攻破也影响不到宿主。

**代表技术**：

#### Firecracker（AWS，2018）
- **起源**：AWS 为 Lambda 和 Fargate 开发的 VMM，源自 Chromium OS 的 crosvm（Rust 编写）
- **核心特性**：
  - 极简设备模型——去掉所有不必要的设备，减到最小攻击面
  - 启动时间：125ms 内启动用户空间代码
  - 创建速率：每台宿主机每秒钟 150 个 microVM
  - 内存开销：每个 microVM < 5 MiB
  - 内置 Rate Limiter：精细控制网络和存储资源
  - REST API 管理：配置 vCPU、启动机器
  - Jailer 组件：即使虚拟化层被突破，还有第二道防线
- **适用**：Serverless 函数、容器化微服务、多租户场景
- **CPU 支持**：64-bit Intel / AMD / Arm（需硬件虚拟化）
- **语言**：Rust
- **许可证**：Apache 2.0
- **集成方**：Fly.io、Kata Containers、Koyeb、Northflank、containerd（firecracker-containerd）

#### Kata Containers
- 结合 Firecracker（或 QEMU）为每个容器启动一个轻量 VM
- 兼容 OCI 规范，可作为 Docker/K8s 运行时

**安全等级对比**：

| 层次 | 逃逸难度 | 启动速度 | 资源开销 | 兼容性 | 典型场景 |
|------|---------|---------|---------|-------|---------|
| Namespace（Docker） | 容易 | 毫秒 | 极低 | 最高 | 开发环境、CI/CD |
| App Kernel（gVisor） | 中等 | 毫秒 | 低 | 高（Linux syscall） | Serverless、多租户 |
| microVM（Firecracker） | 最难 | ~125ms | <5MiB/个 | 高（完整内核） | Lambda、Fargate |

## Agent 专用沙箱服务

### E2B（e2b.dev）

**定位**：面向 AI Agent 的云端沙箱服务，专门为 Agent 运行 LLM 生成的代码而设计。

**核心能力**：
- **Sandbox**：按需创建的轻量 Linux VM（基于 Firecracker）
- **Template**：预配置沙箱环境（安装包、依赖、配置等），类似 Docker Image
- **SDK**：Python 和 JavaScript/TypeScript SDK，几行代码启动沙箱
- **文件管理**：上传/下载文件到沙箱
- **命令执行**：`sandbox.commands.run()` 在沙箱内执行 shell 命令
- **代码执行**：直接执行 Python/JS 代码
- **Desktop 沙箱**：提供虚拟 Linux 桌面，支持 Computer Use 场景
- **CI/CD 集成**：GitHub Actions 集成
- **暂停/恢复**：超时后自动暂停，保持状态可恢复（Pro 最长 24h 持续运行）
- **运行中修改超时**：`setTimeout` 动态延长沙箱生命周期

**使用场景**：
- 让 Agent 在隔离环境中运行生成的代码
- Browser Agent 控制虚拟桌面
- 安全运行不可信代码（用户提交的脚本）
- CI/CD 中跑 LLM 编写的测试

**商业模式**：云端服务（Free / Pro / Enterprise），非自托管。

### Modal Sandbox

**定位**：Modal 是一个 Serverless 云平台，其 Sandbox 功能用于安全运行不可信代码或 Agent 生成的任务。

**核心能力**：
- `modal.Sandbox.create()` 创建运行时容器
- 多语言 SDK：Python、JavaScript、Go
- 完整生命周期管理（Created → Scheduled → Started → Ready → Finished）
- 支持自定义 Image、Volume、GPU
- 默认 5 分钟超时（最大 24 小时）
- Idle Timeout + Filesystem Snapshot（超 24h 使用快照恢复）
- 生命周期事件（Event）支持自动化响应

**与 E2B 的区别**：Modal 是通用 Serverless 平台，Sandbox 是其功能之一；E2B 是专门为 Agent 设计的沙箱平台。

## Agent 框架中的沙箱实践

### OpenClaw

**沙箱模式**（参考 Pi 文档中的容器化章节）：

OpenClaw 的 Agent 运行在宿主机上（目前默认没有独立的沙箱），通过进程运行代码。从 Pi 的设计来看，OpenClaw 选择的容器化模式是**Gondolin**：

- **Gondolin Extension**: 在宿主上保留 OpenClaw 和 Provider 认证，将内置工具和 `!` 命令路由到本地 Linux 微 VM 中执行
- 这是一种"混合架构"——Agent 逻辑在宿主，工具执行在沙箱

**其他可选模式**（来自 Pi 的指南）：
- **Plain Docker**：整个 Pi/OpenClaw 进程运行在本地容器中
- **OpenShell**：运行在策略控制的沙箱中

### Pi（Pi.dev）

Pi 的设计哲学是**不做内置权限系统**。它的默认行为是"以启动用户的权限运行一切"。安全通过以下方式实现：

1. **完整的容器化文档** — 三种模式（Gondolin / Docker / OpenShell）
2. **依赖供应链安全** — 精确锁依赖、CI 定时审计、发布前隔离演练（包发布时在 repo 外创建隔离安装进行冒烟测试）
3. **项目信任机制** — 仅在受信任的项目目录下执行某些功能

Pi 的核心理念是：安全性是用户的责任，框架提供选项而非强制。这与 Claude Code 的内置权限弹窗形成了鲜明对比。

### Claude Code / Cursor

Claude Code 内置了**权限弹窗系统**——当 Agent 尝试执行危险操作（修改文件、执行命令、访问网络）时，会弹窗请求用户确认。这是一种"用户在场控制"模式。

Cursor 则没有独立的沙箱机制，依赖 Agent 本身的安全行为约束。

**关键问题**：这种模式假设用户始终在场且能判断风险。在 Agent 长时间自主运行时，这种模式失效。

## 技术路线图与演进脉络

```
2013年          2017年           2018年               2023年           2025年+
  │               │                │                    │                │
  │ Docker        │ Firecracker    │ Cursor/Claude Code  │ E2B            │ Gondolin
  │ (Namespace)   │ (microVM)      │ 内置权限控制        │ Agent 沙箱   │ OpenShell
  │               │                │                    │  (Firecracker) │
  │               │ gVisor         │ AutoGPT             │ Modal Sandbox  │ Agent-native
  │               │ (App Kernel)   │ Docker 包装         │                │ 沙箱模式
  │               │                │                    │                │
  └───────────────┴────────────────┴────────────────────┴────────────────┴──────────────

 传统容器化隔离 → 新一代轻量 VM/App Kernel → Agent 工具安全 → 专用 Agent 沙箱 → Agent 原生沙箱
```

### 阶段一：传统容器隔离（2013-2017）

Docker 普及了容器技术。Coding Agent 出现前，容器主要用于微服务部署和 CI/CD。Agent 场景中，容器被用作"跑代码的环境"。

**代表**：Docker、Kubernetes、containerd
**缺陷**：共享宿主内核，安全边界不够强

### 阶段二：新一代隔离技术（2018-2022）

Firecracker 和 gVisor 几乎同时出现（2018），代表了两种不同的思路：
- **Firecracker**：从硬件层面隔离（每个沙箱一个独立 kernel）
- **gVisor**：从系统调用层面隔离（用户态内核拦截 syscall）

两者都解决了容器的内核共享问题，但方式截然不同。

**代表**：Firecracker（AWS）、gVisor（Google）、Kata Containers
**催化剂**：Serverless 计算需求（Lambda / Cloud Run）

### 阶段三：Agent 工具安全（2023-2024）

随着 Claude Code、Cursor、AutoGPT 等 Coding Agent 的普及，Agent 执行代码的安全问题凸显。这一阶段的方案主要是：
- **内置权限弹窗**（用户确认）
- **Docker 手动包装**（AutoGPT 等社区实践）
- **LLM 自身的对齐行为**（希望 Agent 不产生恶意行为）

**代表**：Claude Code、Cursor、AutoGPT、OpenInterpreter
**缺陷**：用户在场假设、安全依赖 Agent 自身行为、缺乏系统性隔离

### 阶段四：专用 Agent 沙箱服务（2024-2025）

E2B 和 Modal Sandbox 将 Serverless 容器/microVM 技术重新包装为 Agent 场景的专用产品：
- 几行 SDK 代码就能启动隔离环境
- 专门优化了 Agent 使用模式（动态超时、暂停恢复）
- 支持 Computer Use 等 Agent 特有场景

**代表**：E2B、Modal Sandbox
**特点**：云托管、SDK 优先、Agent-native 设计、商业服务

### 阶段五：Agent 原生沙箱（2025+）

最新的趋势是将沙箱内建于 Agent 框架本身：
- **Gondolin**：Pi/OpenClaw 的子集沙箱化（Agent 在宿主，工具执行在沙箱）
- **OpenShell**：策略驱动的沙箱，支持配置执行规则
- **平台级沙箱**：Agent 平台提供内建的代码执行隔离

**代表**：Gondolin、OpenShell、Pi 容器化模式
**特点**：本地运行、框架内嵌、按需隔离、混合架构

### Gondolin 模式详解

**Gondolin** 是 Pi/OpenClaw 采用的沙箱架构，核心思路是**混合架构**——Agent 在宿主，执行在沙箱。

```
              🏠 宿主（Host）
  ┌─────────────────────────────────────────┐
  │  Agent 进程（决策/编排/LLM调用）          │
  │  Provider 认证（API Key 管理）            │
  │  用户交互界面（TUI/CLI）                  │
  └────────────┬────────────────────────────┘
               │
        路由工具和 ! 命令
               │
  ┌────────────▼────────────────────────────┐
  │  🛡️ 本地 Linux 微 VM（Firecracker）       │
  │                                           │
  │  • 内置工具：bash / read / write          │
  │  • 文件系统：临时空间 + 挂载的宿主目录     │
  │  • 网络：NAT / 代理（可配置白名单）        │
  │  • 进程：沙箱内进程互不感知              │
  └─────────────────────────────────────────┘
```

**关键设计**：
- Provider 认证（API Key）留在宿主，沙箱只拿到执行需要的临时凭据
- 文件通过 `virtio-fs` 或 `9p` 共享，沙箱无法读取未显式挂载的宿主目录
- 网络通过 NAT/代理，出站可控制（白名单/黑名单）
- Agent 逻辑完整——沙箱进程崩溃不影响宿主上的 Agent 决策

**与纯容器方案（Docker wrap）的区别**：
| 维度 | Gondolin（混合架构） | Docker wrap（全容器） |
|------|-------------------|--------------------|
| Agent 位置 | 宿主机 | 容器内 |
| LLM 调用 | 宿主直连 | 容器内，需额外配置网络 |
| Provider 凭据 | 宿主管理，按需注入 | 全部传入容器 |
| 用户交互 | 宿主上的原生 TUI | 需映射或代理 |
| 启动速度 | 常驻 Agent + 按需创建微 VM | 每次启动完整容器 |
| 按需隔离 | 可精细到每个工具 | 要么全隔离要么全不隔离 |

**为什么这是更好的方案**：
1. Agent 的**决策核心**（LLM 调用、上下文管理、工具编排）不需要隔离——这是可控的本地逻辑
2. 真正需要隔离的是 Agent **执行的命令和代码**——这些是不可信的外部输入
3. 混合架构让你可以**逐步引入隔离**：先隔离文件写入，再隔离网络，最终全沙箱化
4. Agent 进程中断不会影响沙箱运行的长时间任务（编译/下载等）

## 当前格局总结

| 类别 | 产品/技术 | 隔离等级 | 部署方式 | 适用场景 |
|------|-----------|---------|---------|---------|
| **底层技术** | Docker | Namespace | 本地 | 通用容器 |
| | gVisor | App Kernel | 本地（OCI runtime） | 多租户容器 |
| | Firecracker | microVM | 本地（VMM） | Serverless |
| **云沙箱服务** | E2B | Firecracker microVM | 云端 | Agent 代码执行 |
| | Modal Sandbox | 容器（OCI） | 云端 | Serverless/Agent |
| **Agent 框架内** | Gondolin | microVM（Firecracker） | 本地混合 | OpenClaw / Pi |
| | OpenShell | 策略沙箱 | 本地 | Agent 安全执行 |
| | Claude Code 弹窗 | 软件控制 | 内嵌 | 用户在场控制 |
| **手动包装** | Docker wrap | Namespace | 本地 | 社区实践 |

## 什么进沙箱，什么留本地——Agent 沙箱的交互模式

**Agent 沙箱不是把 Agent 整个进程关进去**，而是**有选择性地把危险操作送进沙箱**，同时保持和本地环境的必要交互。

### 划分原则

| 进沙箱（隔离执行） | 不进沙箱（宿主机执行） |
|-------------------|----------------------|
| Agent 执行的 bash 命令 | Agent 本身的决策逻辑（思考/编排） |
| Agent 运行 LLM 生成的代码 | LLM API 调用（Anthropic/OpenAI/…） |
| `npm install` / `pip install` | 宿主敏感文件读取（`~/.ssh/`, `~/.aws/`） |
| 下载并执行外部脚本 | 用户确认的写文件操作（经同意后写入） |
| 浏览器自动化 / 爬虫 | Agent 日志持久化 |
| 处理用户上传的不可信文件 | Provider 认证凭据管理 |
| 连接外部服务（数据库/API） | 策略决策（哪些操作可信） |

### 四个交互通道

Agent 宿主机和沙箱之间通过**4 条明确定义的通道**进行交互：

```
              ┌──────────────────────────────┐
              │         Agent 宿主机           │
              │  （决策 + LLM + 上下文管理）     │
              └──────────┬───────────────────┘
                         │
      ┌──────────────────┼──────────────────────┐
      │  ① 文件通道      │  ② 结果通道           │
      │  (volume mount)  │  (stdout/stderr)     │
      │                  │                      │
      │  ③ 回写通道      │  ④ 凭据通道(单向)     │
      │  (经确认后同步)   │  (Key→沙箱,不可逆)    │
      └──────────────────┴──────────────────────┘
                         │
              ┌──────────┴───────────────────┐
              │          沙箱                  │
              │  （隔离的代码/命令执行环境）     │
              └──────────────────────────────┘
```

#### ① 文件通道（File Mount）

**核心问题：直接挂载会不会破坏本地文件？**

会。如果简单地把宿主目录以读写方式挂载进沙箱，沙箱内的代码（不管是有 Bug 还是恶意）可以直接修改或删除项目文件，这就失去了沙箱的意义。

**正确做法：不要直接挂载读写，使用副本机制。**

宿主的项目目录通过 `virtio-fs`、`9p` 或 Docker volume 挂载进沙箱。根据挂载模式不同，安全等级也不同：

| 挂载模式 | 怎么工作 | 对本地文件的风险 | 适用场景 |
|---------|---------|---------------|---------|
| **只读（read-only）** | 沙箱可以读宿主文件但不能改 | ✅ 安全，但沙箱的输出没地方保存 | 只需读取配置/依赖的只读任务 |
| **写穿透（read-write）** | 沙箱直接修改宿主的原文件 | ❌ **危险** — 沙箱内的 Bug 或恶意代码会直接破坏项目文件 | 不推荐，除非完全信任沙箱 |
| **副本（copy-on-write）** | 沙箱启动时拿到一份快照副本，所有修改只影响副本，不影响原始文件 | ✅ **安全** — 沙箱随便折腾，宿主的文件毫发无伤 | **推荐给所有 Agent 场景** |

**Copy-on-Write 的完整流程**：

```
宿主文件（原始）
  │
  ▼
沙箱启动时创建快照副本 ─────── 沙箱内随意读写
  │                              │
  │                              ▼
  │                    改坏了 → 丢弃副本，宿主的文件完好
  │                              │
  │                    改好了 → diff 同步回宿主（经确认）
  │                              │
  ▼                              ▼
原始文件不受影响           用户/Agent 确认后合并
```

本质上就是 **Git 的工作方式**——Agent 在沙箱里随便改，不满意可以丢弃，满意了再 commit（同步回写）。沙箱就是给 Agent 开了一个**"随便改，错了就扔"**的暂存区。

**E2B 的实践**：E2B 的 Sandbox 默认就是 CoW——你通过 SDK 把文件上传到沙箱，沙箱内部随便改，关掉沙箱一切自动销毁。只有你显式调用下载接口的文件才会传回来。

**建议的挂载策略**：

| 目录 | 挂载模式 | 理由 |
|------|---------|------|
| 项目目录（`/project`） | **CoW 副本** | 安全保底，沙箱随便改，不怕项目被炸 |
| 输出目录（`/output`） | **读写** | 编译产物、下载内容直接写入宿主的指定位置 |
| 敏感目录（`~/.ssh/`、`~/.aws/`） | **不挂载** | 除非手动指定，否则不暴露 |
| 缓存目录（`~/.cache/`） | **只读或不挂载** | 不想让沙箱污染缓存 |

这样既安全又实用——Agent 可以放心跑代码，你不用担心本地文件被破坏。

#### ② 结果通道（Result Stream）
沙箱内命令的 stdout/stderr **原样流式返回**给 Agent。这是 Agent 感知沙箱工作的主要方式。

#### ③ 回写通道（Write-back）
沙箱内生成的文件（编译产物、下载的内容、爬虫抓取的数据）**经 Agent 确认后**同步回宿主。
- 直接信任的文件（如编译产物）自动回写
- 需要确认的文件（如修改了项目代码）先通知用户

#### ④ 凭据通道（Credential Injection）
单向通道：宿主将 API Key、Token 等凭据注入沙箱环境变量，但沙箱内的进程**无法反向读取**宿主的敏感文件（`~/.ssh/`、`~/.aws/` 等未挂载的目录）。

### 典型交互流程

以 OpenClaw / Pi 的 Gondolin 模式为例，一个完整的交互流程：

```
用户说: "帮我用 Python 爬这个网站的数据"
  │
  ▼
① Agent 在宿主机上决策:
   "好，写一个爬虫脚本"
  │
  ▼
② Agent 把爬虫脚本写入沙箱的文件系统
   (通过文件通道，copy-on-write 模式)
  │
  ▼
③ Agent 对沙箱下发命令:
   python /sandbox/crawler.py https://example.com
  │
  ▼
④ 沙箱执行爬虫:
   • 只能访问分配的临时目录
   • 网络出站受限（可配置白名单）
   • 无法访问 ~/.ssh/ 和其他宿主目录
  │
  ▼
⑤ 爬虫的 stdout（抓取结果）流回 Agent
   (通过结果通道)
  │
  ▼
⑥ Agent 检查结果，决定:
   • 写入项目文件 → 回写通道 + 用户确认
   • 丢弃（不合适）→ 沙箱自动清理
```

### Gondolin 混合架构的具体实现（OpenClaw / Pi）

**Gondolin** 是 Pi/OpenClaw 采用的沙箱架构，核心思路是**混合架构**——Agent 在宿主，执行在沙箱。

```
              🏠 宿主（Host）
  ┌─────────────────────────────────────────┐
  │  Agent 进程（决策/编排/LLM调用）          │
  │  Provider 认证（API Key 管理）            │
  │  用户交互界面（TUI/CLI）                  │
  └────────────┬────────────────────────────┘
               │
        路由工具和 ! 命令
               │
  ┌────────────▼────────────────────────────┐
  │  🛡️ 本地 Linux 微 VM（Firecracker）       │
  │                                           │
  │  • 内置工具：bash / read / write          │
  │  • 文件系统：临时空间 + 挂载的宿主目录     │
  │  • 网络：NAT / 代理（可配置白名单）        │
  │  • 进程：沙箱内进程互不感知              │
  └─────────────────────────────────────────┘
```

**关键设计**：
- Provider 认证（API Key）留在宿主，沙箱只拿到执行需要的临时凭据
- 文件通过 `virtio-fs` 或 `9p` 共享，沙箱无法读取未显式挂载的宿主目录
- 网络通过 NAT/代理，出站可控制（白名单/黑名单）
- Agent 逻辑完整——沙箱进程崩溃不影响宿主上的 Agent 决策

**与纯容器方案（Docker wrap）的区别**：

| 维度 | Gondolin（混合架构） | Docker wrap（全容器） |
|------|-------------------|--------------------|
| Agent 位置 | 宿主机 | 容器内 |
| LLM 调用 | 宿主直连 | 容器内，需额外配置网络 |
| Provider 凭据 | 宿主管理，按需注入 | 全部传入容器 |
| 用户交互 | 宿主上的原生 TUI | 需映射或代理 |
| 启动速度 | 常驻 Agent + 按需创建微 VM | 每次启动完整容器 |
| 按需隔离 | 可精细到每个工具 | 要么全隔离要么全不隔离 |

**为什么这是更好的方案**：
1. Agent 的**决策核心**（LLM 调用、上下文管理、工具编排）不需要隔离——这是可控的本地逻辑
2. 真正需要隔离的是 Agent **执行的命令和代码**——这些是不可信的外部输入
3. 混合架构让你可以**逐步引入隔离**：先隔离文件写入，再隔离网络，最终全沙箱化
4. Agent 进程中断不会影响沙箱运行的长时间任务（编译/下载等）

## 关键洞察

1. **隔离等级与便捷性成反比** — Firecracker 最安全但需额外运维，Docker 最方便但安全最弱。多数 Agent 场景选择了 Docker（足够且简单）。

2. **Agent 沙箱正在"右移"** — 从依赖 Agent 自身行为约束，转向基础设施层强制隔离。类比编程语言的发展：从 Java 的 sandbox security（软件层）→ Docker（OS 层）→ Firecracker（硬件层）。

3. **云沙箱 vs 本地沙箱的取舍** — E2B 提供极致体验但有网络延迟和成本，Gondolin 提供本地运行的快速而隔离的环境。两者不是替代关系，而是适用不同场景。

4. **"不内置"的设计哲学正在被挑战** — Pi 的"安全是用户责任"和 Claude Code 的"弹窗审批"两种路线在 2025+ 开始融合。Gondolin 的出现表明即使是极简主义框架也需要一层基本的安全隔离。

5. **OpenClaw 的选择** — OpenClaw 目前默认在宿主机运行 Agent，没有强制沙箱。Gondolin 提供了最自然的升级路径：Agent 逻辑保持原样，工具执行路由到微 VM。这意味着可以逐步引入隔离——先隔离文件读写，再隔离网络，最终完全沙箱化。

6. **混合架构是当前最优解** — 纯容器方案（整 Agent 扔进去）太重、纯弹窗方案（靠用户确认）不可靠。混合架构（Agent 在宿主 + 工具执行在沙箱 + 4 条定义清晰的交互通道）在安全、性能、灵活性之间取得了最好的平衡。

7. **沙箱的"交互通道"设计比沙箱本身更重要** — 如何让沙箱里的代码与宿主环境通信（文件读写、凭据注入、结果回传），决定了沙箱方案是否可用。4 条通道（文件/结果/回写/凭据）的设计是区分好沙箱和勉强能用沙箱的关键。

## Agent Sandbox 完整架构设计（五子系统）

以下是从**控制、文件、执行、网络、交付物**五个维度对 Agent Sandbox 进行系统化的架构设计。这是混合架构（Agent 在宿主 + 执行在沙箱）的完整蓝图。

### 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    用户/开发者                            │
└──────────────────────────┬──────────────────────────────┘
                           │
                         指令
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    🏠 宿主层（Host）                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │        ① 控制子系统（Control Plane）               │   │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────┐  │   │
│  │  │ Agent 编排  │ │ 策略引擎     │ │ 审计日志 │  │   │
│  │  │ (决策/规划) │ │ (规则/白名单) │ │ (记录)   │  │   │
│  │  └──────┬──────┘ └──────┬───────┘ └──────────┘  │   │
│  │         │               │                        │   │
│  │  ┌──────▼──────────────▼────────────────────┐   │   │
│  │  │       沙箱管理器（Sandbox Manager）        │  │   │
│  │  │  生命周期 · 资源配额 · 策略下发 · 凭证注入 │   │   │
│  │  └──────────────────┬────────────────────────┘   │   │
│  └─────────────────────┼────────────────────────────┘   │
│                         │                                │
│  ┌─────────────────────┼────────────────────────────┐   │
│  │  ② 文件子系统       │   ③ 凭据子系统              │   │
│  │  (File Plane)       │   (Credential Plane)        │   │
│  │  ┌───────────────┐  │   ┌────────────────────┐   │   │
│  │  │ 文件路由/快照  │  │   │ Provider 认证管理  │   │   │
│  │  │ CoW 文件系统   │  │   │ API Key/Token 注入 │   │   │
│  │  │ Sandbox FS     │  │   │ (单向通道)         │   │   │
│  │  └───────┬───────┘  │   └────────────────────┘   │   │
│  └──────────┼──────────┘                            ┘   │
└─────────────┼────────────────────────────────────────────┘
              │
     ┌────────┼──────────┐──────────┐
     │        │          │          │
     ▼        ▼          ▼          ▼
┌────────────────────────────────────────────────┐
│               🛡️ 沙箱执行层                      │
│                                                  │
│  ┌────────────────┐  ┌──────────────────────┐   │
│  │ ④ 执行子系统   │  │ ⑤ 网络子系统         │   │
│  │ (Execute)      │  │ (Network)            │   │
│  │ ┌──────────┐   │  │ ┌───────────────┐    │   │
│  │ │ bash     │   │  │ │ NAT / 代理     │    │   │
│  │ │ python   │   │  │ │ 出站白名单     │    │   │
│  │ │ node/npm │   │  │ │ DNS 过滤       │    │   │
│  │ │ 编译器   │   │  │ │ 入站端口映射   │    │   │
│  │ │ git      │   │  │ └───────────────┘    │   │
│  │ └──────────┘   │  └──────────────────────┘   │
│  └────────────────┘                              │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ ⑥ 交付物子系统（Deliverable）              │   │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │ │ stdout/  │ │ 文件产物 │ │ 审计追溯 │   │   │
│  │ │ stderr   │ │ (编译物) │ │ (证据链) │   │   │
│  │ └──────────┘ └──────────┘ └──────────┘   │   │
│  └──────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

---

### ① 控制子系统（Control Plane）

**位置**：全部在宿主层。这是沙箱的大脑，不进入沙箱。

| 组件 | 职责 | 关键能力 |
|------|------|---------|
| **Agent 编排器** | 决策、规划、工具调用编排 | LLM 调用、上下文管理、工具选择、多步规划 |
| **策略引擎** | 定义什么操作进沙箱、执行策略 | 操作分类（read-only/read-write/exec）、白名单/黑名单规则、资源配额 |
| **沙箱管理器** | 沙箱生命周期管理 | 创建/销毁/暂停/恢复沙箱、凭证注入、策略下发、状态监控 |
| **审计日志** | 所有跨沙箱操作的记录 | 操作时间戳、来源（Agent/User）、目标路径、操作结果、凭证使用记录 |

**控制流示例**：

```
Agent 决定执行: npm install axios
  → Agent 编排器判断：这是"安装依赖"操作
  → 策略引擎查规则：npm install → 需要网络出站 + 文件写入
  → 沙箱管理器：
     1. 检查沙箱是否存在，不存在则创建
     2. 注入临时 npm token（凭据子系统）
     3. 将项目目录以 CoW 模式挂载
     4. 下发网络策略：允许 registry.npmjs.org
     5. 下发资源配额：最大 30s，1GB 内存
  → 执行子系统: npm install axios
  → 交付物子系统: stdout + node_modules/ 产物
  → 审计日志: 记录操作全过程
```

---

### ② 文件子系统（File Plane）

**位置**：横跨宿主层和沙箱执行层。宿主端负责策略控制和快照管理，沙箱端负责实际 I/O。

**架构**：

```
      宿主文件系统
           │
           ▼
  ┌──────────────────┐
  │  文件路由/策略层  │ ← 决定哪些路径可访问、什么模式
  └──────┬───────────┘
         │
    ┌────┴────┬──────┐
    │         │      │
    ▼         ▼      ▼
  只读挂载   CoW副本  不挂载
           │
           ▼
    沙箱内文件系统
    (tmpfs / 挂载点)
```

**文件操作分类**：

| 操作类型 | 沙箱行为 | 对宿主影响 | 安全等级 |
|---------|---------|-----------|---------|
| **读取配置文件**（只读挂载） | 直接读宿主文件 | 无影响 | ✅ 安全 |
| **读取并修改项目文件**（CoW） | 读宿主 → 写副本 | 不影响原始文件 | ✅ 安全 |
| **生成新文件到输出目录**（读写挂载） | 直接写宿主指定目录 | 只影响 `/output/` | ⚠️ 需控制路径 |
| **下载外部文件** | 写入沙箱 tmpfs | 不落盘，随沙箱销毁 | ✅ 安全 |
| **删除文件**（CoW） | 标记副本删除 | 不影响原始文件 | ✅ 安全 |

**CoW 实现细节**：
- **存储**：OverlayFS（Linux）/ virtio-fs + 快照（Firecracker）
- **写入策略**：沙箱的每次写入实际发生在上层（upperdir），下层（lowerdir）保持不变
- **回滚**：丢弃 upperdir 即可，原始 lowerdir 不受影响
- **回写**：`rsync` diff 或逐层合并，仅将修改部分同步回宿主
- **粒度**：可配置到文件级别或目录级别

**建议的默认文件策略**：

```json
{
  "files": {
    "mounts": [
      {"host": "/project", "sandbox": "/workspace", "mode": "copy-on-write"},
      {"host": "/project/output", "sandbox": "/workspace/output", "mode": "read-write"},
      {"host": "/project/node_modules", "sandbox": "/workspace/node_modules", "mode": "read-only"}
    ],
    "blocklist": [
      "/root/.ssh",
      "/home/*/.ssh",
      "/etc/kubernetes",
      "**/*.pem",
      "**/secrets.*"
    ]
  }
}
```

---

### ③ 执行子系统（Execution Plane）

**位置**：全部在沙箱执行层。本质是一个受限制的 shell 环境。

**功能范围**：

| 能力 | 说明 | 限制方式 |
|------|------|---------|
| **bash/sh 执行** | 任意 shell 命令 | 白名单命令、超时、cgroup 资源上限 |
| **语言运行时** | Python/Node.js/Rust/Go 等 | 环境变量隔离、module 访问限制 |
| **包管理器** | npm/pip/cargo/go 等 | 限制文件写入范围、registry 白名单 |
| **git 操作** | clone/pull/checkout | 限制远程仓库、禁止修改 git config |
| **编译器** | gcc/rustc/typescript | 限制输出路径 |
| **后台进程** | 长服务、watcher | 限制进程数、内存、运行时间 |

**执行控制层级**：

```
Agent 决定执行命令
  │
  ▼
策略引擎检查（白名单/黑名单/正则）
  │  禁止的命令: rm -rf /, dd, :(){ :|:& };:
  │  受限的命令: curl/wget（只能出站不能入站）
  │  无条件允许: ls, cat, echo, python, node
  │
  ▼
沙箱管理器注入环境变量
  │  注入: API_KEY, TEMP_DIR, WORKSPACE
  │  覆盖: HOME=/sandbox/home, PATH=/sandbox/bin
  │
  ▼
cgroup 资源限制
  │  CPU 配额、内存上限、磁盘 IOPS、进程数
  │
  ▼
超时控制
  │  默认超时、最大超时、idle 超时
  │
  ▼
执行 → stdout/stderr 流回宿主
```

**资源配额示例**：

```json
{
  "execution": {
    "default_timeout_ms": 30000,
    "max_timeout_ms": 3600000,
    "idle_timeout_ms": 600000,
    "resources": {
      "cpu_quota": 2.0,
      "memory_mb": 2048,
      "disk_mb": 10240,
      "max_processes": 50,
      "max_open_files": 1024
    },
    "command_policies": {
      "allow": ["^python ", "^node ", "^npm ", "^git clone ", "^ls ", "^cat ", "^echo "],
      "deny": ["rm -rf /", "dd if=", ":(){ "],
      "require_approval": ["^curl ", "^wget ", "^sudo ", "^chmod 777"]
    }
  }
}
```

---

### ④ 网络子系统（Network Plane）

**位置**：宿主端有网络策略网关，沙箱端的网络通过 NAT/代理/隧道 实现。

**网络模型**：

```
        宿主网络
           │
    ┌──────┴──────┐
    │ 网络策略网关  │ ← 出站白名单、DNS 过滤、流量审计
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │  NAT / 代理  │ ← 通常走 NAT（沙箱无独立 IP）
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │  沙箱网络    │ ← 受限的出站访问，入站需显式端口映射
    └─────────────┘
```

**网络隔离策略**：

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **无网络** | 完全断开，沙箱内无法访问任何外部地址 | 分析本地代码、执行已下载的脚本 |
| **出站白名单** | 只允许访问指定的域名/IP | npm install（只 allow registry.npmjs.org） |
| **出站代理** | 所有出站流量经过代理，可审计和过滤 | 爬虫、API 调用 |
| **入站端口映射** | 沙箱内服务通过宿主端口暴露 | 启动临时 HTTP 服务做测试 |
| **VPN/隧道** | 沙箱通过安全隧道连接外部资源 | 连接内部数据库、VPC |

**网络策略配置示例**：

```json
{
  "network": {
    "outbound": {
      "mode": "whitelist",
      "rules": [
        {"domain": "registry.npmjs.org", "ports": [443], "description": "npm packages"},
        {"domain": "pypi.org", "ports": [443], "description": "pip packages"},
        {"domain": "github.com", "ports": [443], "description": "git clone"},
        {"domain": "*.docker.com", "ports": [443], "description": "docker pull"},
        {"domain": "api.openai.com", "ports": [443], "description": "LLM API"}
      ],
      "block": [
        {"domain": "*.miner.*", "reason": "crypto mining"},
        {"domain": "pastebin.com", "reason": "data exfiltration"}
      ],
      "dns_filter": true,
      "audit_log": true
    },
    "inbound": {
      "enabled": false,
      "port_mapping": []
    }
  }
}
```

**关键安全设计**：
- DNS 过滤：防止沙箱内恶意代码通过 DNS 隧道外传数据
- 流量审计：记录所有出站连接（目标 IP、端口、流量大小）
- 默认拒绝入站：沙箱不可被外部访问，除非显式配置端口映射
- 出站代理模式：可在代理层注入身份认证或做内容过滤

---

### ⑤ 凭据子系统（Credential Plane）

**位置**：宿主层负责管理和注入，沙箱层只读使用。

**架构**：

```
        宿主凭据存储
  (环境变量 / Secrets Manager / Keychain)
           │
           ▼
    ┌──────────────┐
    │  凭据管理器    │ ← 策略控制：哪些沙箱/哪些操作可获取哪些凭据
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  单向注入      │ ← 环境变量 / 临时文件（沙箱销毁时自动清除）
    └──────┬───────┘
           │
           ▼
      沙箱进程
  （只能读取，不可反向回传）
```

**安全设计原则**：
- **最小化原则**：只注入当前任务需要的凭据，不注入无关的
- **一次性原则**：每次沙箱创建注入一次，销毁时清除
- **不可逆原则**：凭据从宿主到沙箱单向流动，沙箱内不可获取宿主凭据存储的访问权
- **按需注入**：不是所有沙箱启动都注入凭据，只有涉及外部服务调用的操作才注入

**凭据类型**：

| 类型 | 示例 | 注入方式 | 安全级别 |
|------|------|---------|---------|
| **Provider 认证** | `ANTHROPIC_API_KEY` | 环境变量 | ⚠️ 敏感，限时间范围 |
| **包管理器 Token** | `NPM_TOKEN` | 临时文件 + 环境变量 | ✅ 低敏感，作用域限 registry |
| **Git 访问 Token** | `GITHUB_TOKEN` | 环境变量 | ⚠️ 敏感，按 repo 限权 |
| **云服务凭证** | `AWS_ACCESS_KEY_ID` | 环境变量 | 🔴 高敏感，需显式用户确认 |
| **数据库连接串** | `DATABASE_URL` | 环境变量 | 🔴 高敏感，限连接白名单 |

---

### ⑥ 交付物子系统（Deliverable Plane）

**位置**：横跨宿主和沙箱，负责将沙箱执行结果转化为宿主可用的形式。

**交付物类型**：

| 类型 | 传输方式 | 持久化策略 | 典型用途 |
|------|---------|-----------|---------|
| **stdout/stderr 流** | 实时流式通道 | 写入审计日志 + 传递给 Agent | Agent 感知执行结果 |
| **exit code** | 同步返回 | 审计日志 | 判断执行成败 |
| **文件产物** | CoW→回写通道 | 经确认后同步回宿主 | 编译产物、生成代码、爬取数据 |
| **日志/追溯** | 写审计日志 | 持久化到宿主日志系统 | 调试、审计、回放 |
| **图表/可视化** | 文件通道回写 | 同文件产物 | Agent 生成的可视化输出 |
| **网络响应** | 网络通道捕获 | 随沙箱销毁 | API 调用响应、爬虫结果 |

**交付物生命周期**：

```
沙箱执行
  │
  ├─ stdout/stderr → 实时流回 Agent → 决策参考
  │
  ├─ exit code → Agent 判断成功/失败
  │
  ├─ 文件写入（CoW）
  │     │
  │     ├─ 产物: 编译/build 输出 → 自动回写（受信任路径）
  │     ├─ 代码: Agent 生成的源文件 → 提示用户确认后回写
  │     └─ 临时: 中间文件 → 沙箱销毁时自动清除
  │
  ├─ 网络响应
  │     │
  │     ├─ 捕获的 HTTP 响应 → Agent 处理
  │     └─ 下载的文件 → 暂存沙箱，按需回写
  │
  └─ 审计日志
        │
        ├─ 操作记录 → 宿主日志持久化
        ├─ 凭据使用记录 → 安全审计
        └─ 异常记录 → 告警
```

**回写策略**：

| 回写策略 | 行为 | 安全等级 |
|---------|------|---------|
| **自动回写**（受信任路径） | 产物自动同步回宿主 | ✅ 适用：编译输出、测试报告 |
| **提示确认**（代码修改） | 通知用户后回写 | ⚠️ 适用：代码生成、配置修改 |
| **差异展示**（修改现有文件） | 只展示 diff，用户选择合并与否 | ⚠️ 适用：代码重构、Bug 修复 |
| **审核后回写**（高危操作） | 需要人工 review 确认 | 🔴 适用：涉及生产环境、安全配置的修改 |

---

### 六子系统协作示例

以一个完整场景说明六个子系统如何协作：

**场景**：Agent 从 GitHub clone 一个项目 → 分析代码 → 修复 bug → 提交 PR

```
Step 1: git clone https://github.com/user/repo
  │
  ├─ 控制子系统：Agent 决策 → 策略引擎检查 git 操作是否允许
  │               → 沙箱管理器创建沙箱（如果不存在）
  ├─ 文件子系统：创建 CoW workspace，不关联宿主项目目录
  ├─ 执行子系统：执行 git clone → stdout 流回 Agent
  ├─ 网络子系统：允许出站到 github.com:443
  ├─ 凭据子系统：注入 GITHUB_TOKEN（只读 scope）
  └─ 交付物子系统：git clone 的 stdout + 下载到沙箱的 repo

Step 2: 分析代码并修复 bug
  │
  ├─ 控制子系统：Agent 分析代码 → 决定修改 src/main.ts
  ├─ 文件子系统：CoW 模式下创建 src/main.ts 的副本
  ├─ 执行子系统：Agent 执行 sed 或写文件命令修改副本
  ├─ 网络子系统：不涉及
  ├─ 凭据子系统：不涉及
  └─ 交付物子系统：修改的 diff 展示给用户确认

Step 3: git push + create PR
  │
  ├─ 控制子系统：Agent 决定提交 → 用户确认后执行
  ├─ 文件子系统：CoW→diff 合并回沙箱文件系统
  ├─ 执行子系统：git commit + git push
  ├─ 网络子系统：允许出站到 github.com:443
  ├─ 凭据子系统：注入 GITHUB_TOKEN（写 scope）
  └─ 交付物子系统：git push 输出 + PR 链接

Step 4: 清理
  │
  └─ 控制子系统：沙箱管理器标记沙箱可回收
                   → 沙箱销毁，所有临时数据清除
                   → 审计日志持久化（供追溯）
```

---

### 配置总纲

一个完整的沙箱配置 JSON 示例：

```json
{
  "sandbox_name": "agent-sandbox",
  "version": "1.0",

  "control": {
    "strategy": "primitives_in_sandbox",
    "lifecycle": "per-task",
    "max_concurrent_commands": 10
  },

  "files": {
    "mounts": [
      {"host": "/project", "sandbox": "/workspace", "mode": "copy-on-write"},
      {"host": "/project/output", "sandbox": "/workspace/output", "mode": "read-write"}
    ],
    "blocklist": ["/root/.ssh", "/home/*/.ssh", "**/secrets.*"]
  },

  "execution": {
    "default_timeout_ms": 30000,
    "max_timeout_ms": 3600000,
    "resources": {
      "cpu_quota": 2.0,
      "memory_mb": 2048,
      "disk_mb": 10240,
      "max_processes": 50
    },
    "command_policies": {
      "allow_patterns": ["^python ", "^node ", "^npm ", "^git ", "^ls"],
      "deny_patterns": ["rm -rf /", "dd if="]
    }
  },

  "network": {
    "outbound": {
      "mode": "whitelist",
      "allowed_domains": ["github.com", "registry.npmjs.org", "pypi.org"],
      "dns_filter": true,
      "audit": true
    },
    "inbound": {
      "enabled": false
    }
  },

  "credentials": {
    "inject_on_demand": true,
    "max_lifetime_ms": 300000,
    "clear_on_destroy": true
  },

  "deliverables": {
    "auto_sync_paths": ["/workspace/output", "/workspace/dist", "/workspace/build"],
    "confirm_sync_paths": ["/workspace/src"],
    "audit_log_path": "/var/log/agent-sandbox/"
  }
}
```

---

### 总结：五大维度一句话

| 子系统 | 一句话 |
|--------|--------|
| **控制** | 决策什么做、怎么做，在宿主上执行，不进沙箱 |
| **文件** | 只读/CoW/读写三种模式，默认用 CoW 保护本地文件 |
| **执行** | 命令在沙箱内受限执行，cgroup 控制资源，策略控制命令 |
| **网络** | 默认切断，出站白名单可控，入站需显式映射 |
| **交付物** | stdout/产物/日志三类，按安全等级自动/提示/审核后回写 |

## 相关来源

- Firecracker: https://firecracker-microvm.github.io/ | https://github.com/firecracker-microvm/firecracker
- gVisor: https://gvisor.dev | https://github.com/google/gvisor
- E2B: https://e2b.dev
- Modal Sandbox: https://modal.com/docs/guide/sandboxes
- Pi 容器化文档: https://pi.dev/docs/latest/containerization
- OpenClaw: https://github.com/OpenClaw/OpenClaw
- Docker: https://www.docker.com
- Kata Containers: https://katacontainers.io

## 相关页面

- [[Knowledge/wiki/资料/Pi Coding Agent]] — Pi 的容器化三模式和 No MCP 设计哲学
