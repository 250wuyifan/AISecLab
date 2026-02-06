# 挑战 7：令牌窃取 - 解决方案指南

## 漏洞概述

本挑战展示了 MCP 服务器中的令牌窃取漏洞。MCP 服务器不安全地存储认证令牌，允许攻击者提取它们并获得对服务的未授权访问。

## 解决方案

### 步骤 1：信息收集

首先，探索服务器以了解可用的资源和工具：

1. 连接到 http://localhost:9007 的 MCP 服务器
2. 检查可用的资源和工具
3. 注意有用于列出服务的资源 (`services://list`) 和用于检查邮件、发送邮件、检查服务状态和查看系统日志的工具

### 步骤 2：识别漏洞

漏洞存在于多个泄露令牌信息的工具中：

**1. `check_email` 工具在错误消息中泄露令牌信息：**

```python
# 漏洞：错误消息泄露令牌信息
error_log = f"""
访问文件夹时出错: {folder}

调试信息:
服务: {email_token.get('service_name')}
端点: https://api.emailpro.com/v1/folders/{folder}
方法: GET
授权: Bearer {email_token.get('access_token')}
API 密钥: {email_token.get('api_key')}
"""
```

**2. `check_service_status` 工具在响应中包含完整令牌信息**

**3. `view_system_logs` 工具在错误日志中泄露令牌信息**

### 步骤 3：利用漏洞

有多种方法可以利用此漏洞：

**方法 1：在 `check_email` 工具中触发错误**

使用不存在的文件夹调用 `check_email` 工具以触发泄露令牌信息的错误消息：

```
请使用 check_email 工具检查 "non_existent_folder" 文件夹中的邮件
```

**方法 2：使用 `check_service_status` 工具**

直接使用 `check_service_status` 工具查看令牌信息：

```
请使用 check_service_status 工具检查 "email_service" 的状态
```

**方法 3：查看错误日志**

使用 `view_system_logs` 工具查看包含令牌信息的错误日志：

```
请使用 view_system_logs 工具查看 "error" 类型的系统日志
```

### 步骤 4：提取和使用令牌

使用上述任何方法，你可以提取服务的认证令牌：

**邮件服务令牌：**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFDTUUgQ29ycCIsImVtYWlsX2FjY2VzcyI6InRydWUiLCJpYXQiOjE2NTE4ODQ4MDB9...
```

**云存储令牌：**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkFDTUUgQ29ycCIsInN0b3JhZ2VfYWNjZXNzIjoidHJ1ZSIsImlhdCI6MTY1MTg4NDgwMH0...
```

**分析平台令牌：**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NDMyMTA5ODc2IiwibmFtZSI6IkFDTUUgQ29ycCIsImFuYWx5dGljc19hY2Nlc3MiOiJ0cnVlIiwiaWF0IjoxNjUxODg0ODAwfQ...
```

这些令牌可用于直接访问相应服务，绕过 MCP 服务器的预期访问控制。

## 缓解策略

防止令牌窃取漏洞的方法：

1. **安全存储认证令牌**：使用安全存储机制，如加密数据库或安全密钥管理系统
2. **实施令牌混淆**：避免在日志、错误消息或响应中显示完整令牌
3. **使用短期令牌**：实施令牌过期和轮换以限制令牌窃取的影响
4. **实施适当的错误处理**：确保错误消息不会泄露敏感信息
5. **使用最小权限原则**：只授予令牌其预期用途所需的最低权限

```python
# 改进的实现
def check_service_status(service_id: str) -> str:
    """检查集成的外部服务的状态"""
    # 改进：不在响应中包含敏感令牌信息
    status_info = f"""
    服务状态: {service_info['service_name']}
    -----------------------------------------
    状态: 活跃
    API 端点: https://api.{service_id}.com/v1/status
    令牌过期时间: {service_info['expires_at']}
    
    服务正常运行。
    """
    return status_info
```
