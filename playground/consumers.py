# -*- coding: utf-8 -*-
"""
CSWSH 靶场：故意不校验 Origin、不校验 CSRF 的 WebSocket 聊天消费者。
使用与记忆投毒相同的 LLM 配置，真实调用大模型并流式推送。
"""
from __future__ import annotations

import json
import asyncio
from typing import Any, List

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .agent import MemoryAgent


def _cswsh_stream_llm(user_msg: str) -> List[str]:
    """同步：用当前靶场配置调用大模型流式接口，返回内容块列表。"""
    agent = MemoryAgent(memory=[])
    messages = [
        {"role": "system", "content": "你是一个助手。请用简洁自然的语言回复用户。本靶场使用 WebSocket 流式推送。"},
        {"role": "user", "content": user_msg},
    ]
    return list(agent.call_llm_stream(messages))


class CswshChatConsumer(AsyncWebsocketConsumer):
    """脆弱 WebSocket 聊天：不检查 Origin，不校验连接级 CSRF；使用真实大模型。"""

    group_name: str = ""

    async def connect(self) -> None:
        # 故意不检查 Origin、不校验 CSRF token
        session = self.scope.get("session")
        if session and hasattr(session, "session_key") and session.session_key:
            self.group_name = f"cswsh_{session.session_key}"
        else:
            self.group_name = f"cswsh_{self.channel_name}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        msg = (data.get("message") or "").strip()
        if not msg:
            return
        chunks = await database_sync_to_async(_cswsh_stream_llm)(msg)
        full_reply = "".join(chunks)
        for c in chunks:
            await self.send(text_data=json.dumps({"type": "chunk", "text": c}))
            await asyncio.sleep(0.02)
        await self.send(text_data=json.dumps({"type": "done", "text": full_reply}))
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "cswsh.eavesdrop",
                "user": msg,
                "assistant": full_reply,
            },
        )

    async def cswsh_eavesdrop(self, event: dict[str, Any]) -> None:
        """接收广播的窃听消息；仅恶意页展示，正常聊天页可忽略。"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "eavesdrop",
                    "user": event.get("user", ""),
                    "assistant": event.get("assistant", ""),
                }
            )
        )


# DoS 靶场：仅接受连接并计数，不校验连接数上限（演示拒绝服务）
_dos_connection_count: int = 0


def get_dos_connection_count() -> int:
    """供 HTTP 视图读取当前 DoS 演示用的 WebSocket 连接数。"""
    return _dos_connection_count


class DosConsumer(AsyncWebsocketConsumer):
    """故意不限制单客户端连接数，用于演示 WebSocket DoS。仅 accept，不处理消息。"""

    async def connect(self) -> None:
        global _dos_connection_count
        await self.accept()
        _dos_connection_count += 1

    async def disconnect(self, close_code: int) -> None:
        global _dos_connection_count
        _dos_connection_count = max(0, _dos_connection_count - 1)
