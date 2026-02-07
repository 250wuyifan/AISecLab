# 🛡️ AI Security Playground (AI 安全靶场)

[![Release](https://img.shields.io/badge/Release-v1.0.0-blue?style=flat-square)](https://github.com/250wuyifan/AISecLab/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)

一个集学习与实战演练于一体的 **AI 安全攻防平台**，覆盖大模型安全的 8 大攻击面，40+ 交互式靶场。

> **Clone 下来就能用** — 默认使用 SQLite，无需安装数据库，3 条命令启动。

---

## ✨ 功能特色

### 🎯 8 大攻击面 × 30+ 靶场

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
- **Docker 支持** — 一键 `docker-compose up` 部署
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

### 方式一：一键安装脚本（推荐）

**克隆项目：**
```bash
git clone https://github.com/250wuyifan/AISecLab.git
cd AISecLab
```

<details>
<summary><b>🪟 Windows 用户</b></summary>

```powershell
# 方式 A：运行批处理脚本
.\setup.bat

# 方式 B：运行 Python 脚本
python scripts\setup.py

# 启动服务
.\start.bat
# 或
python manage.py runserver
```
</details>

<details>
<summary><b>🍎 macOS 用户</b></summary>

```bash
# 方式 A：运行 Shell 脚本
chmod +x setup.sh && ./setup.sh

# 方式 B：运行 Python 脚本
python3 scripts/setup.py

# 启动服务
./start.sh
# 或
python3 manage.py runserver
```
</details>

<details>
<summary><b>🐧 Linux 用户</b></summary>

```bash
# 方式 A：运行 Shell 脚本
chmod +x setup.sh && ./setup.sh

# 方式 B：运行 Python 脚本
python3 scripts/setup.py

# 启动服务
./start.sh
# 或
python3 manage.py runserver
```
</details>

### 方式二：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/250wuyifan/AISecLab.git
cd AISecLab

# 2. 创建虚拟环境（可选但推荐）
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python manage.py migrate

# 5. 创建管理员账号（默认 admin/admin）
python create_superuser.py

# 6. 启动服务
python manage.py runserver
```

打开浏览器访问 http://127.0.0.1:8000 ，使用 `admin / admin` 登录即可。

### 方式三：Docker 部署

```bash
# 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问 http://localhost:8000

### 方式四：使用 MySQL（可选）

如果你需要使用 MySQL 作为数据库：

```bash
# 1. 复制环境变量配置
cp .env.example .env  # Windows: copy .env.example .env

# 2. 编辑 .env，取消 MySQL 相关注释并填写信息
# DB_ENGINE=mysql
# DB_NAME=aisec_db
# DB_USER=root
# DB_PASSWORD=your_password

# 3. 安装 MySQL 驱动
pip install pymysql cryptography

# 4. 初始化并启动
python manage.py migrate
python manage.py runserver
```

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
│   ├── settings.py            #   支持 SQLite / MySQL
│   ├── urls.py
│   └── asgi.py                #   WebSocket (Channels/Daphne)
├── learning/                  # 学习模块（首页、知识管理）
│   ├── views.py
│   ├── models.py
│   └── templates/
├── playground/                # 靶场核心模块
│   ├── views/
│   │   ├── __init__.py        #   统一导出
│   │   ├── _common.py         #   公共工具：_call_llm / _build_sidebar 等
│   │   └── _legacy.py         #   所有靶场视图函数
│   ├── agent.py               #   LLM Agent（MemoryAgent / ToolAgent）
│   ├── dvmcp_challenges.py    #   DVMCP 10 关挑战定义
│   ├── dvmcp_client.py        #   MCP SSE 客户端
│   ├── consumers.py           #   WebSocket 消费者（CSWSH / DoS）
│   ├── lab_principles.py      #   各靶场原理讲解文案
│   ├── memory_cases.py        #   记忆投毒场景定义
│   ├── models.py              #   LLMConfig / AgentMemory / LabProgress 等
│   ├── forms.py
│   ├── tests.py               #   33 个测试用例
│   ├── solutions/             #   DVMCP 各关解题思路（Markdown）
│   └── templates/             #   40+ 靶场页面模板
│       └── playground/
│           ├── _lab_detail_header.html   # 统一头部组件
│           ├── _lab_tools.html           # 提示 / 完成按钮组件
│           ├── _llm_not_configured_alert.html  # 未配置 LLM 提醒
│           ├── _tool_lab_llm_config_modal.html # LLM 配置弹层
│           ├── system_prompt_leak.html   # ...各靶场页面
│           └── ...
├── templates/                 # 全局模板
│   └── base.html              #   含 navbar / LLM 弹层 / 主题切换
├── static/
│   ├── css/
│   │   ├── style.css          #   全局主题变量 & 样式
│   │   └── lab_detail.css     #   靶场详情页公共样式
│   └── js/
│       └── bg.js
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
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

> DVMCP 服务独立于主靶场运行，需要单独启动。源码位于 [damn-vulnerable-MCP-server-CN](https://github.com/250wuyifan/damn-vulnerable-MCP-server-CN)。

### 启动 DVMCP 服务

<details>
<summary><b>🐳 Docker 一键启动（推荐）</b></summary>

```bash
git clone https://github.com/250wuyifan/damn-vulnerable-MCP-server-CN.git
cd damn-vulnerable-MCP-server-CN
docker build -t dvmcp .
docker run -d --name dvmcp -p 9001-9010:9001-9010 dvmcp
```
</details>

<details>
<summary><b>🪟 Windows 手动启动</b></summary>

```powershell
git clone https://github.com/250wuyifan/damn-vulnerable-MCP-server-CN.git
cd damn-vulnerable-MCP-server-CN
pip install -r requirements.txt
python start_all_servers.py    # 一键启动全部 10 个挑战
```
</details>

<details>
<summary><b>🍎🐧 macOS/Linux 手动启动</b></summary>

```bash
git clone https://github.com/250wuyifan/damn-vulnerable-MCP-server-CN.git
cd damn-vulnerable-MCP-server-CN
pip install -r requirements.txt
./start_sse_servers.sh    # 一键启动全部 10 个挑战（端口 9001-9010）
```
</details>

启动后回到主靶场页面，进入「DVMCP 实战靶场」即可看到各挑战的运行状态。

### 挑战列表

| 关卡 | 主题 | 难度 |
|------|------|------|
| L1 | 基础信息获取 | ⭐ |
| L2 | 工具描述注入 | ⭐ |
| L3 | 文件系统穿越 | ⭐⭐ |
| L4 | 天气服务投毒 | ⭐⭐ |
| L5 | 权限提升 | ⭐⭐ |
| L6 | 文档上传投毒 | ⭐⭐⭐ |
| L7 | 令牌泄露 | ⭐⭐⭐ |
| L8 | 代码执行 | ⭐⭐⭐ |
| L9 | 命令注入 | ⭐⭐⭐⭐ |
| L10 | 综合攻击链 | ⭐⭐⭐⭐ |

---

## 🛠️ 技术栈

- **后端**: Python + Django 4.x + Channels (WebSocket)
- **前端**: Bootstrap 5 + 原生 JS
- **数据库**: SQLite（默认）/ MySQL（可选）
- **LLM**: 兼容 OpenAI API（Ollama / GPT / 通义千问等）

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
