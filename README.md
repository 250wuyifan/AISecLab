# 🛡️ AI Security Playground (AI 安全靶场)

[![Release](https://img.shields.io/badge/Release-v1.0.0-blue?style=flat-square)](https://github.com/250wuyifan/AISecLab/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)

一个集学习与实战演练于一体的 **AI 安全攻防平台**，覆盖大模型安全的 8 大攻击面，40+ 交互式靶场。

> **Clone 下来就能用** — 使用 SQLite，无需安装数据库，3 条命令启动。

---

## ✨ 功能特色

### 🎯 8 大攻击面 × 40+ 靶场

| 分类 | 内容 | 靶场数 |
|------|------|--------|
| 💬 **Prompt 安全** | System Prompt 泄露、越狱攻击、幻觉利用 | 4 |
| 🤖 **Agent 安全** | 记忆投毒、工具链劫持、行为漂移 | 6 |
| 📚 **RAG 安全** | 知识库投毒、检索结果操纵 | 2 |
| 🖼️ **多模态安全** | 图像隐写注入、视觉提示注入 | 2 |
| ⚡ **输出安全** | RCE (eval)、SSTI、XSS、CSWSH、DoS | 5 |
| 🔧 **工具漏洞** | SSRF、SQLi、XXE、反序列化、OAuth、RCE | 7 |
| 🔌 **DVMCP 实战** | 10 关 MCP 协议安全挑战，从入门到进阶 | 10 |
| 🏴 **红队工具** | Garak 扫描器、越狱 Payload 测试、AIScan 安全扫描 | 4 |

### 🔥 核心亮点

- **交互式攻防** — 不是纯文档，而是真正可操作的靶场
- **DVMCP 独创** — 国内首个 MCP 协议安全挑战靶场（10关）
- **AIScan 内置** — 自研 AI 安全扫描器，支持模型测试 + 代码审计
- **即开即用** — SQLite 零配置，3 条命令启动
- **Docker 一键部署** — `docker compose up` 同时启动主平台 + DVMCP
- **明暗主题** — 简洁专业的 UI，支持明暗切换

---

## 🚀 快速开始

### 📋 系统要求

| 系统 | 版本要求 | 备注 |
|------|----------|------|
| **Windows** | Windows 10/11 | 推荐使用 PowerShell |
| **macOS** | 10.15+ | Intel / Apple Silicon 均支持 |
| **Linux** | Ubuntu 20.04+ / CentOS 8+ | 或其他主流发行版 |
| **Python** | 3.9+ | 推荐 3.10 或 3.11 |

### 方式一：Docker 一键部署（推荐）

**最简单的方式，自动启动主平台和 DVMCP 靶场：**

```bash
# 克隆项目
git clone https://github.com/250wuyifan/AISecLab.git
cd AISecLab

# 一键启动（主平台 + 10 个 DVMCP 挑战）
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f
```

> ⏱️ 首次启动需要几分钟下载依赖，请耐心等待。

**访问地址：**
- 主平台：http://localhost:8000
- DVMCP 服务：端口 9001-9010（自动启动，无需手动操作）

**默认账号：** `admin` / `admin`

<details>
<summary><b>🔧 Docker 模式连接本地 Ollama</b></summary>

Docker 容器与宿主机网络隔离，需要特殊配置才能连接本地的 Ollama：

1. 登录后点击右上角 **LLM 配置**
2. 将 **API 地址** 修改为：
   ```
   http://host.docker.internal:11434/v1/chat/completions
   ```
3. 点击保存

> `host.docker.internal` 是 Docker Desktop (macOS/Windows) 提供的特殊域名，用于从容器内访问宿主机。

</details>

### 方式二：一键安装脚本

**克隆项目：**
```bash
git clone https://github.com/250wuyifan/AISecLab.git
cd AISecLab
```

<details>
<summary><b>🪟 Windows 用户</b></summary>

```powershell
# 运行安装脚本
.\setup.bat

# 启动服务
.\start.bat
```
</details>

<details>
<summary><b>🍎 macOS / 🐧 Linux 用户</b></summary>

```bash
# 运行安装脚本
chmod +x setup.sh && ./setup.sh

# 启动服务
./start.sh
```
</details>

### 方式三：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/250wuyifan/AISecLab.git
cd AISecLab

# 2. 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python manage.py migrate

# 5. 创建管理员账号
python create_superuser.py

# 6. 启动服务
python manage.py runserver
```

打开浏览器访问 http://127.0.0.1:8000 ，使用 `admin / admin` 登录即可。

### ❓ 常见问题

<details>
<summary><b>Windows: 中文乱码</b></summary>

在 PowerShell 中运行：
```powershell
chcp 65001
```
</details>

<details>
<summary><b>macOS/Linux: 权限问题</b></summary>

```bash
chmod +x setup.sh start.sh
```
</details>

<details>
<summary><b>pip 安装依赖失败</b></summary>

尝试使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
</details>

<details>
<summary><b>端口 8000 被占用</b></summary>

使用其他端口：
```bash
python manage.py runserver 8080
```
</details>

---

## 🏗️ 项目结构

```
AISecLab/
├── aisec_playground/          # Django 项目配置
│   ├── settings.py            #   SQLite 数据库配置
│   ├── urls.py
│   └── asgi.py                #   WebSocket (Channels/Daphne)
├── learning/                  # 学习模块（首页、知识管理）
├── playground/                # 靶场核心模块
│   ├── views/                 #   视图函数
│   ├── dvmcp_challenges.py    #   DVMCP 10 关挑战定义
│   ├── dvmcp_client.py        #   MCP SSE 客户端
│   ├── consumers.py           #   WebSocket 消费者
│   ├── lab_principles.py      #   各靶场原理讲解
│   └── templates/             #   40+ 靶场页面模板
├── Dockerfile
├── docker-compose.yml         # 一键部署（主平台 + DVMCP）
└── requirements.txt
```

---

## ⚙️ LLM 配置

靶场中的交互式攻防需要连接大模型。支持所有 OpenAI 兼容 API：

| 方式 | 说明 |
|------|------|
| **Ollama（推荐）** | 本地运行，免费，`ollama run qwen2.5` |
| **OpenAI API** | 设置 `OPENAI_API_KEY` |
| **其他兼容 API** | 设置 `OPENAI_API_BASE` 指向你的服务 |

靶场内提供了 LLM 配置界面，可以在页面上直接切换模型。

---

## 🔌 DVMCP 靶场

**Damn Vulnerable MCP (DVMCP)** 是专为 MCP（Model Context Protocol）协议设计的 10 关安全挑战。

### 启动方式

| 方式 | 说明 |
|------|------|
| **Docker Compose（推荐）** | `docker compose up -d` 自动启动全部服务 |
| **手动启动** | 见下方说明 |

<details>
<summary><b>手动启动 DVMCP 服务（不使用 Docker 时）</b></summary>

```bash
# 克隆 DVMCP 项目（中文版）
git clone https://github.com/250wuyifan/damn-vulnerable-MCP-server-CN.git
cd damn-vulnerable-MCP-server-CN

# 安装依赖
pip install -r requirements.txt

# 启动全部 10 个挑战
./start_sse_servers.sh     # macOS/Linux
```
</details>

### 挑战列表

| 关卡 | 主题 | 难度 | 端口 |
|------|------|------|------|
| L1 | 基础信息获取 | ⭐ | 9001 |
| L2 | 工具描述注入 | ⭐ | 9002 |
| L3 | 文件系统穿越 | ⭐ | 9003 |
| L4 | 天气服务投毒 | ⭐⭐ | 9004 |
| L5 | 权限提升 | ⭐⭐ | 9005 |
| L6 | 文档上传投毒 | ⭐⭐ | 9006 |
| L7 | 令牌泄露 | ⭐⭐ | 9007 |
| L8 | 代码执行 | ⭐⭐⭐ | 9008 |
| L9 | 命令注入 | ⭐⭐⭐ | 9009 |
| L10 | 综合攻击链 | ⭐⭐⭐ | 9010 |

---

## 🛠️ 技术栈

- **后端**: Python + Django 4.x + Channels (WebSocket)
- **前端**: Bootstrap 5 + 原生 JS
- **数据库**: SQLite（轻量、零配置）
- **LLM**: 兼容 OpenAI API（Ollama / GPT / 通义千问等）
- **容器化**: Docker + Docker Compose

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的分支 (`git checkout -b feature/amazing-lab`)
3. 提交更改 (`git commit -m 'Add amazing lab'`)
4. 推送分支 (`git push origin feature/amazing-lab`)
5. 创建 Pull Request

---

## ⚠️ 免责声明

本项目仅用于 **安全学习和研究目的**。请勿将本项目中的攻击技术用于未授权的系统。使用者需自行承担因不当使用造成的法律责任。

---

## 📜 开源协议

[MIT License](LICENSE)

---

<div align="center">

**Made with ❤️ by [Changmen](https://github.com/250wuyifan)**

</div>
