"""
LLM Bridge — 支持多种 LLM 后端的统一调用层

支持的 Provider：
  - deepseek   : DeepSeek 官方 API (DEEPSEEK_API_KEY)
  - siliconflow : 硅基流动 SiliconFlow (SILICONFLOW_API_KEY)
  - ollama     : 本地 Ollama (无需 API Key)
  - openai     : OpenAI 官方 API (OPENAI_API_KEY)
  - custom     : 任意 OpenAI 兼容 API (LLM_API_KEY + LLM_BASE_URL)

配置方式（优先级从高到低）：
  1. 环境变量 LLM_PROVIDER + 对应 API Key
  2. CLI 参数 --llm-provider / --llm-model / --llm-api-key / --llm-base-url
  3. 回退到 DeepSeek（兼容原版行为）
"""

import os
import logging
from typing import List, Dict, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

# ── Provider 预设 ─────────────────────────────────────────
PROVIDER_PRESETS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
        "env_key": "SILICONFLOW_API_KEY",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "default_model": "qwen2.5:7b",
        "env_key": None,  # Ollama 无需 API Key
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
    },
    "custom": {
        "base_url": None,
        "default_model": None,
        "env_key": "LLM_API_KEY",
    },
}


def extract_after_think(text: str) -> str:
    """移除 <think>...</think> 标签内的推理内容"""
    parts = text.split("</think>")
    return parts[1].strip() if len(parts) > 1 else text


def _detect_provider() -> str:
    """根据环境变量自动检测可用的 Provider"""
    explicit = os.getenv("LLM_PROVIDER", "").strip().lower()
    if explicit and explicit in PROVIDER_PRESETS:
        return explicit

    # 按优先级自动检测
    if os.getenv("SILICONFLOW_API_KEY"):
        return "siliconflow"
    if os.getenv("DEEPSEEK_API_KEY"):
        return "deepseek"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("LLM_API_KEY") and os.getenv("LLM_BASE_URL"):
        return "custom"

    # 尝试检测本地 Ollama
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3):
            return "ollama"
    except Exception:
        pass

    return "deepseek"  # 兼容原版默认行为


class LLMClient:
    """统一 LLM 客户端，支持多种 Provider"""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        # 确定 provider
        self.provider = (provider or "").strip().lower() or _detect_provider()
        preset = PROVIDER_PRESETS.get(self.provider, PROVIDER_PRESETS["custom"])

        # 确定 base_url
        raw_url = base_url or os.getenv("LLM_BASE_URL") or preset["base_url"]
        if not raw_url:
            raise ValueError(
                f"Provider '{self.provider}' 需要设置 base_url。\n"
                f"请通过 --llm-base-url 参数或 LLM_BASE_URL 环境变量设置。"
            )
        # 清理 base_url：OpenAI SDK 会自动拼 /chat/completions，
        # 所以如果传入了完整 endpoint 需要去掉末尾
        raw_url = raw_url.rstrip("/")
        for suffix in ["/chat/completions", "/api/chat"]:
            if raw_url.endswith(suffix):
                raw_url = raw_url[: -len(suffix)]
                break
        self.base_url = raw_url

        # 确定 model
        self.model = model or os.getenv("LLM_MODEL") or preset["default_model"] or "default"

        # 确定 api_key
        env_key = preset.get("env_key")
        resolved_key = api_key or (os.getenv(env_key) if env_key else None) or os.getenv("LLM_API_KEY")

        # Ollama 不需要 API Key，给一个占位符
        if self.provider == "ollama" and not resolved_key:
            resolved_key = "ollama"

        if not resolved_key:
            env_hint = f"export {env_key}=your_key" if env_key else "export LLM_API_KEY=your_key"
            raise EnvironmentError(
                f"未找到 {self.provider} 的 API Key。\n"
                f"请设置环境变量: {env_hint}\n"
                f"或通过 --llm-api-key 参数传入。\n\n"
                f"支持的 Provider: {', '.join(PROVIDER_PRESETS.keys())}\n"
                f"也可设置 LLM_PROVIDER 环境变量切换 Provider。"
            )

        self.client = OpenAI(api_key=resolved_key, base_url=self.base_url)
        logger.info(f"LLM 客户端初始化: provider={self.provider}, model={self.model}, base_url={self.base_url}")

    def get_response(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        content = response.choices[0].message.content or ""
        return extract_after_think(content)

    def __repr__(self) -> str:
        return f"LLMClient(provider={self.provider!r}, model={self.model!r}, base_url={self.base_url!r})"
