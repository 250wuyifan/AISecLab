"""
DVMCP MCP 客户端 - 使用 SSE 连接 DVMCP Server

MCP SSE 协议流程：
1. GET /sse 建立 SSE 连接
2. 服务器发送 endpoint 事件，包含消息 URL（带 session_id）
3. POST 到该 URL 发送 JSON-RPC 请求
4. 服务器通过 SSE 返回响应
"""

import json
import httpx
import threading
import queue
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class MCPSSEClient:
    """MCP SSE 客户端 - 同步版本"""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.sse_url = f"{self.base_url}/sse"
        self.timeout = timeout
        self.session_id: Optional[str] = None
        self.message_url: Optional[str] = None
        self._request_id = 0
    
    def _get_next_id(self) -> int:
        self._request_id += 1
        return self._request_id
    
    def connect(self) -> bool:
        """
        连接到 MCP 服务器，获取 session_id 和 message_url
        
        MCP SSE 协议：服务器会在 SSE 流中发送 endpoint 事件
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                # 使用流式请求获取 SSE 事件
                with client.stream('GET', self.sse_url) as response:
                    if response.status_code != 200:
                        logger.error(f"SSE 连接失败: HTTP {response.status_code}")
                        return False
                    
                    # 读取 SSE 事件直到获得 endpoint
                    buffer = ""
                    for chunk in response.iter_text():
                        buffer += chunk
                        
                        # 解析 SSE 事件
                        while "\n\n" in buffer:
                            event_str, buffer = buffer.split("\n\n", 1)
                            
                            # 解析事件
                            event_type = None
                            event_data = None
                            
                            for line in event_str.split("\n"):
                                if line.startswith("event:"):
                                    event_type = line[6:].strip()
                                elif line.startswith("data:"):
                                    event_data = line[5:].strip()
                            
                            # 检查是否是 endpoint 事件
                            if event_type == "endpoint" and event_data:
                                # endpoint 数据格式: /messages/?session_id=xxx
                                self.message_url = f"{self.base_url}{event_data}"
                                # 提取 session_id
                                if "session_id=" in event_data:
                                    self.session_id = event_data.split("session_id=")[1].split("&")[0]
                                logger.info(f"获取到消息端点: {self.message_url}")
                                return True
                        
                        # 设置超时保护
                        if time.time() - response.elapsed.total_seconds() > 5:
                            break
                    
        except Exception as e:
            logger.error(f"连接 MCP 服务器失败: {e}")
        
        return False
    
    def _send_request(self, method: str, params: Dict = None) -> Optional[Dict]:
        """发送 JSON-RPC 请求"""
        if not self.message_url:
            # 尝试重新连接
            if not self.connect():
                return None
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or {}
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.message_url,
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    # MCP 通过 SSE 返回响应，这里可能收到 "Accepted"
                    text = response.text
                    if text and text != "Accepted":
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError:
                            pass
                    return {"status": "accepted"}
                elif response.status_code == 202:
                    return {"status": "accepted"}
                else:
                    logger.error(f"请求失败: HTTP {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"发送请求失败: {e}")
            return None
    
    def list_tools(self) -> List[Dict]:
        """获取工具列表"""
        result = self._send_request("tools/list")
        if result and "result" in result:
            return result["result"].get("tools", [])
        return []
    
    def list_resources(self) -> List[Dict]:
        """获取资源列表"""
        result = self._send_request("resources/list")
        if result and "result" in result:
            return result["result"].get("resources", [])
        return []
    
    def call_tool(self, name: str, arguments: Dict = None) -> Dict:
        """调用工具"""
        result = self._send_request("tools/call", {"name": name, "arguments": arguments or {}})
        if result and "result" in result:
            return {"success": True, "result": result["result"]}
        elif result and "error" in result:
            return {"success": False, "error": result["error"]}
        return {"success": False, "error": "请求失败"}
    
    def read_resource(self, uri: str) -> Dict:
        """读取资源"""
        result = self._send_request("resources/read", {"uri": uri})
        if result and "result" in result:
            return {"success": True, "result": result["result"]}
        elif result and "error" in result:
            return {"success": False, "error": result["error"]}
        return {"success": False, "error": "请求失败"}


def _fetch_tools_via_sse(port: int) -> Optional[Dict[str, Any]]:
    """通过完整 SSE 协议获取 MCP Server 的真实 tools/list 和 resources/list"""
    import threading, queue
    mcp_base = f'http://localhost:{port}'
    result_q: queue.Queue = queue.Queue()

    def _worker():
        """在独立线程中完成 SSE 连接 + 请求 + 读结果"""
        tools_result = None
        resources_result = None
        try:
            with httpx.Client(timeout=8.0) as http_client:
                with http_client.stream('GET', f'{mcp_base}/sse') as sse:
                    endpoint_url = None
                    current_event = None
                    n = 0
                    for line in sse.iter_lines():
                        n += 1
                        if line.startswith('event: '):
                            current_event = line[7:].strip()
                            continue
                        if line.startswith('data: '):
                            data_str = line[6:].strip()
                            if current_event == 'endpoint' and endpoint_url is None:
                                endpoint_url = f'{mcp_base}{data_str}' if data_str.startswith('/') else f'{mcp_base}/{data_str}'
                                # 立即在同一个线程中发送请求（避免线程竞争）
                                with httpx.Client(timeout=8.0) as pc:
                                    pc.post(endpoint_url, json={'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                                        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                                                   'clientInfo': {'name': 'AISecLab', 'version': '1.0'}}})
                                    pc.post(endpoint_url, json={'jsonrpc': '2.0', 'method': 'notifications/initialized'})
                                    pc.post(endpoint_url, json={'jsonrpc': '2.0', 'id': 10, 'method': 'tools/list', 'params': {}})
                                    pc.post(endpoint_url, json={'jsonrpc': '2.0', 'id': 11, 'method': 'resources/list', 'params': {}})
                                continue
                            if current_event == 'message' and endpoint_url:
                                try:
                                    msg = json.loads(data_str)
                                    mid = msg.get('id')
                                    if mid == 10 and 'result' in msg:
                                        tools_result = msg['result'].get('tools', [])
                                    elif mid == 11 and 'result' in msg:
                                        resources_result = msg['result'].get('resources', [])
                                except json.JSONDecodeError:
                                    pass
                                if tools_result is not None and resources_result is not None:
                                    break
                        if n > 80:
                            break
        except Exception:
            pass
        result_q.put({'tools': tools_result, 'resources': resources_result})

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=10)  # 最多等 10 秒

    if not result_q.empty():
        data = result_q.get_nowait()
        if data.get('tools') is not None:
            return {'tools': data['tools'], 'resources': data.get('resources') or []}
    return None


def get_mcp_tools_and_resources(challenge_id: int) -> Dict[str, Any]:
    """
    获取指定挑战的工具和资源列表。
    优先从 MCP Server 实时拉取（能看到完整的工具描述，包括隐藏指令）；
    失败时回退到静态定义。
    """
    port = 9000 + challenge_id

    # 尝试实时获取
    live_data = _fetch_tools_via_sse(port)
    if live_data and live_data.get('tools'):
        return live_data

    # 回退：静态定义（MCP Server 未运行时使用）
    base_url = f"http://localhost:{port}"
    challenge_tools = {
        1: {
            "tools": [
                {"name": "get_user_info", "description": "获取用户信息", "parameters": {"type": "object", "properties": {"username": {"type": "string", "description": "用户名"}}}}
            ],
            "resources": [
                {"uri": "notes://{user_id}", "name": "用户笔记", "description": "获取指定用户的笔记"},
                {"uri": "internal://credentials", "name": "内部凭据（隐藏）", "description": "系统内部凭据"}
            ]
        },
        2: {
            "tools": [
                {"name": "get_user_info", "description": "获取用户信息", "parameters": {}},
                {"name": "get_company_data", "description": "根据指定类型获取公司数据", "parameters": {"type": "object", "properties": {"data_type": {"type": "string"}}}},
                {"name": "search_company_database", "description": "在公司数据库中搜索信息", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}}
            ],
            "resources": [
                {"uri": "company://confidential", "name": "机密公司信息（隐藏）", "description": ""}
            ]
        },
        3: {
            "tools": [
                {"name": "read_file", "description": "从公共目录读取文件", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}}}},
                {"name": "search_files", "description": "在公共目录中搜索文件", "parameters": {"type": "object", "properties": {"keyword": {"type": "string"}}}}
            ],
            "resources": []
        },
        4: {
            "tools": [
                {"name": "get_weather_forecast", "description": "获取指定城市的天气预报", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}},
                {"name": "reset_challenge", "description": "重置挑战状态", "parameters": {}}
            ],
            "resources": []
        },
        5: {
            "tools": [
                {"name": "get_user_role", "description": "获取用户角色", "parameters": {"type": "object", "properties": {"username": {"type": "string"}}}},
                {"name": "get_user_roles", "description": "获取用户角色（可能被遮蔽）", "parameters": {"type": "object", "properties": {"username": {"type": "string"}}}}
            ],
            "resources": []
        },
        6: {
            "tools": [
                {"name": "read_document", "description": "从系统读取文档", "parameters": {"type": "object", "properties": {"document_name": {"type": "string"}}}},
                {"name": "read_upload", "description": "读取用户上传的文档", "parameters": {"type": "object", "properties": {"upload_name": {"type": "string"}}}},
                {"name": "upload_and_process_document", "description": "上传并处理文档", "parameters": {"type": "object", "properties": {"document_name": {"type": "string"}, "content": {"type": "string"}}}},
                {"name": "search_documents", "description": "搜索文档", "parameters": {"type": "object", "properties": {"keyword": {"type": "string"}}}}
            ],
            "resources": []
        },
        7: {
            "tools": [
                {"name": "check_email", "description": "检查邮件", "parameters": {"type": "object", "properties": {"folder": {"type": "string", "default": "inbox"}}}},
                {"name": "send_email", "description": "发送邮件", "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}}},
                {"name": "check_service_status", "description": "检查服务状态", "parameters": {"type": "object", "properties": {"service_id": {"type": "string"}}}},
                {"name": "view_system_logs", "description": "查看系统日志", "parameters": {"type": "object", "properties": {"log_type": {"type": "string", "default": "system"}}}}
            ],
            "resources": []
        },
        8: {
            "tools": [
                {"name": "execute_python_code", "description": "执行 Python 代码进行数据分析", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}}},
                {"name": "execute_shell_command", "description": "执行 shell 命令", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}}},
                {"name": "analyze_log_file", "description": "分析日志文件", "parameters": {"type": "object", "properties": {"log_path": {"type": "string"}}}}
            ],
            "resources": []
        },
        9: {
            "tools": [
                {"name": "ping_host", "description": "Ping 主机检查连接", "parameters": {"type": "object", "properties": {"host": {"type": "string"}, "count": {"type": "integer", "default": 4}}}},
                {"name": "traceroute", "description": "跟踪网络路由", "parameters": {"type": "object", "properties": {"host": {"type": "string"}}}},
                {"name": "port_scan", "description": "检查端口是否开放", "parameters": {"type": "object", "properties": {"host": {"type": "string"}, "port": {"type": "integer"}}}},
                {"name": "network_diagnostic", "description": "运行网络诊断", "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "options": {"type": "string", "default": ""}}}},
                {"name": "view_network_logs", "description": "查看网络日志", "parameters": {"type": "object", "properties": {"log_type": {"type": "string", "default": "ping"}}}}
            ],
            "resources": []
        },
        10: {
            "tools": [
                {"name": "authenticate", "description": "用户认证", "parameters": {"type": "object", "properties": {"username": {"type": "string"}, "password": {"type": "string"}}}},
                {"name": "get_user_profile", "description": "获取用户配置文件", "parameters": {"type": "object", "properties": {"username": {"type": "string"}}}},
                {"name": "run_system_diagnostic", "description": "运行系统诊断", "parameters": {"type": "object", "properties": {"component": {"type": "string", "default": "all"}}}},
                {"name": "check_system_status", "description": "检查系统状态", "parameters": {}},
                {"name": "analyze_log_file", "description": "分析日志文件", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}}}
            ],
            "resources": []
        }
    }
    
    return challenge_tools.get(challenge_id, {"tools": [], "resources": []})


def call_mcp_tool(challenge_id: int, tool_name: str, arguments: Dict = None) -> Dict[str, Any]:
    """
    调用 MCP 工具
    
    这里我们直接调用 Cursor 连接的 MCP 工具
    """
    port = 9000 + challenge_id
    
    # 由于 MCP SSE 协议的复杂性，我们这里提供工具信息
    # 实际的工具调用需要通过 Cursor/Claude 等 MCP 客户端进行
    
    return {
        "success": False,
        "error": "请使用页面上方的 MCP 工具直接调用，或在 Cursor 中连接 MCP 服务器",
        "hint": f"工具: {tool_name}, 参数: {arguments}, 端口: {port}"
    }


def check_mcp_server_running(challenge_id: int) -> bool:
    """检查 MCP 服务器是否运行"""
    import socket
    port = 9000 + challenge_id
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except Exception:
        return False
