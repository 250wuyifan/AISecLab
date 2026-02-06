# 🛡️ AI Security Playground (AI 安全靶场)

一个集学习与实战演练于一体的 **AI 安全攻防平台**，覆盖大模型安全的 8 大攻击面，30+ 交互式靶场。

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
| 🏴 **红队工具** | Garak 扫描器、越狱 Payload 测试 | 3 |

### 🔥 核心亮点

- **交互式攻防** — 不是纯文档，而是真正可操作的靶场
- **DVMCP 独创** — 国内首个 MCP 协议安全挑战靶场（10关）
- **即开即用** — SQLite 零配置，3 条命令启动
- **Docker 支持** — 一键 `docker-compose up` 部署
- **暗色主题** — 赛博朋克风格 UI，支持明暗切换

---

## 🚀 快速开始

### 方式一：本地运行（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/250wuyifan/AISecLab.git
cd AISecLab

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库并启动
python manage.py migrate
python manage.py runserver
```

打开浏览器访问 http://127.0.0.1:8000 即可。

### 方式二：Docker 部署

```bash
docker-compose up -d
```

访问 http://localhost:8000

### 方式三：使用 MySQL

如果你需要使用 MySQL 作为数据库：

```bash
# 1. 复制环境变量配置
cp .env.example .env

# 2. 编辑 .env，取消 MySQL 相关注释并填写信息
# DB_ENGINE=mysql
# DB_NAME=aisec_db
# DB_USER=root
# DB_PASSWORD=your_password

# 3. 初始化并启动
python manage.py migrate
python manage.py runserver
```

---

## 🏗️ 项目结构

```
ai-security-playground/
├── aisec_playground/      # Django 项目配置
│   ├── settings.py        # 配置（支持 SQLite/MySQL）
│   └── urls.py
├── learning/              # 学习模块（首页、知识管理）
│   ├── views.py
│   ├── models.py
│   └── templates/
├── playground/            # 靶场核心模块
│   ├── views/             # 所有靶场视图
│   ├── agent.py           # LLM Agent 逻辑
│   ├── dvmcp_challenges.py # DVMCP 10关挑战
│   ├── lab_principles.py  # 靶场原理说明
│   ├── solutions/         # 各关解题思路（Markdown）
│   └── templates/         # 40+ 靶场页面模板
├── templates/             # 全局模板（base.html）
├── static/                # 静态资源（CSS/JS）
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example           # 环境变量示例
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

**Damn Vulnerable MCP (DVMCP)** 是专为 MCP（Model Context Protocol）协议设计的 10 关安全挑战：

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
