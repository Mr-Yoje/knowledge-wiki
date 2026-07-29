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
宿主的项目目录通过 `virtio-fs`、`9p` 或 Docker volume 挂载进沙箱。支持三种挂载模式：
- **只读**（read-only）— 沙箱可以读宿主文件但不能改
- **读写副本**（copy-on-write）— 沙箱修改不影响宿主的原始文件
- **指定目录读写** — 只有某个子目录（如 `/output/`）可写回

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
