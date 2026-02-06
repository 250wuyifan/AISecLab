"""
公共工具函数 — 所有视图模块共享

- _get_llm_config / _call_llm: 统一 LLM 调用
- _get_memory_obj / _get_shared_user: 记忆管理
- _infer_provider_label / _apply_lab_meta / _ensure_lab_meta: 元数据工具
- _build_sidebar_context: 靶场侧栏构建
"""
import json
import re
from typing import Any, Dict, List

import requests as req_lib

from django.contrib.auth.models import User
from django.urls import reverse

from ..models import AgentMemory, LLMConfig, LabCaseMeta, LabProgress, LabFavorite
from ..forms import LLMConfigForm
from ..memory_cases import LabGroup, LabItem, build_memory_poisoning_groups
from ..lab_principles import get_principle


# ============================================================
# LLM 配置与调用
# ============================================================

def _get_llm_config():
    """获取全局 LLM 配置，不存在或未启用时返回 None"""
    cfg = LLMConfig.objects.first()
    if cfg and cfg.enabled:
        return cfg
    return None


def _call_llm(messages: list, *, timeout: int = 60, max_tokens: int | None = None) -> str:
    """
    统一 LLM 调用入口。
    - 自动从 LLMConfig 读取 api_base / api_key / default_model
    - 自动兼容 OpenAI chat/completions 和 Ollama /api/chat 两种返回格式
    - 调用失败时抛出异常，由调用方捕获
    """
    cfg = _get_llm_config()
    if not cfg:
        raise ValueError('尚未配置或未启用大模型，请点击「配置 LLM」进行设置')

    headers = {'Content-Type': 'application/json'}
    if cfg.api_key:
        headers['Authorization'] = f'Bearer {cfg.api_key}'

    payload: dict = {
        'model': cfg.default_model,
        'messages': messages,
    }
    if max_tokens is not None:
        payload['max_tokens'] = max_tokens

    resp = req_lib.post(cfg.api_base, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    # 兼容 OpenAI chat/completions 格式
    choices = data.get('choices', [])
    if choices:
        return choices[0].get('message', {}).get('content', '')
    # 兼容 Ollama /api/chat 格式
    return data.get('message', {}).get('content', '')


# ============================================================
# 记忆管理
# ============================================================

def _get_memory_obj(user, scenario: str = 'memory_poisoning') -> AgentMemory:
    mem, _ = AgentMemory.objects.get_or_create(user=user, scenario=scenario)
    if mem.data is None:
        mem.data = []
    return mem


def _get_shared_user() -> User:
    '''用"系统用户"模拟跨用户/共享记忆场景。'''
    u, created = User.objects.get_or_create(username='_shared_memory')
    if created:
        u.set_unusable_password()
        u.is_active = True
        u.save()
    return u


# ============================================================
# 元数据工具
# ============================================================

def _infer_provider_label(cfg: LLMConfig) -> str:
    api_base = (cfg.api_base or '').lower()
    if '127.0.0.1:11434' in api_base or cfg.provider == 'ollama':
        return '本地（Ollama）'
    return '硅基流动（云端）'


def _apply_lab_meta(slug: str, base: Dict[str, Any]) -> Dict[str, Any]:
    '''如果数据库里为某个 slug 配置了 LabCaseMeta，就覆盖默认文案。'''
    try:
        meta = LabCaseMeta.objects.filter(slug=slug).first()
    except Exception:
        return base
    if not meta:
        return base
    merged = dict(base)
    if meta.title:
        merged['title'] = meta.title
    if meta.subtitle:
        merged['subtitle'] = meta.subtitle
    if meta.scenario:
        merged['scenario_story'] = meta.scenario
    if meta.real_world:
        merged['real_world_example'] = meta.real_world
        merged['real_world'] = meta.real_world
    return merged


def _ensure_lab_meta(slug: str, base: Dict[str, Any]) -> None:
    '''首次访问时，把默认文案"落库"成可编辑的 LabCaseMeta 记录。'''
    defaults = {
        'title': (base.get('title') or '').strip(),
        'subtitle': (base.get('subtitle') or '').strip(),
        'scenario': (base.get('scenario_story') or base.get('scenario') or '').strip(),
        'real_world': (base.get('real_world_example') or base.get('real_world') or '').strip(),
    }
    if not any(defaults.values()):
        return
    try:
        LabCaseMeta.objects.get_or_create(slug=slug, defaults=defaults)
    except Exception:
        return


# ============================================================
# 靶场侧栏构建
# ============================================================

def _build_sidebar_context(active_item_id: str) -> Dict[str, Any]:
    """
    构建靶场左侧侧栏 - 新的分类体系

    分类：
    1. Prompt 安全 - System Prompt 泄露、越狱、幻觉
    2. Agent 安全 - 记忆投毒、工具调用、MCP
    3. RAG 安全 - 知识库投毒
    4. 多模态安全 - 图像/音频攻击
    5. 输出安全 - RCE/SSTI/XSS
    6. 工具漏洞 - SSRF/SQLi/XXE 等
    7. 实战靶场 - DVMCP
    8. 红队工具 - Garak 等
    """

    groups = [
        LabGroup(
            id='prompt_security',
            title='1\ufe0f\u20e3 Prompt 安全',
            items=[
                LabItem(id='prompt_leak', title='System Prompt 泄露', subtitle='诱导 LLM 泄露系统提示词', kind='prompt', slug='system-prompt-leak', url=reverse('playground:system_prompt_leak')),
                LabItem(id='jailbreak', title='越狱攻击', subtitle='绕过安全限制的各种技巧', kind='prompt', slug='jailbreak', url=reverse('playground:jailbreak_payloads')),
                LabItem(id='hallucination', title='幻觉利用', subtitle='利用 LLM 生成虚假信息', kind='prompt', slug='hallucination', url=reverse('playground:hallucination_lab')),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['prompt-security']),
        ),
        LabGroup(
            id='agent_security',
            title='2\ufe0f\u20e3 Agent 安全',
            items=[
                LabItem(id='mem_dialog', title='记忆投毒·直接注入', subtitle='对话中直接注入恶意指令', kind='memory', slug='dialog', url=reverse('playground:memory_case', args=['dialog'])),
                LabItem(id='mem_drift', title='记忆投毒·行为漂移', subtitle='多轮渐进式改变行为', kind='memory', slug='drift', url=reverse('playground:memory_case', args=['drift'])),
                LabItem(id='mem_trigger', title='记忆投毒·触发器后门', subtitle='特定触发词激活隐藏指令', kind='memory', slug='trigger', url=reverse('playground:memory_case', args=['trigger'])),
                LabItem(id='mem_shared', title='记忆投毒·跨用户污染', subtitle='共享记忆一人注入影响全体', kind='memory', slug='shared', url=reverse('playground:memory_case', args=['shared'])),
                LabItem(id='tool_basic', title='工具调用·基础投毒', subtitle='记忆指令劫持工具调用', kind='tool', slug='tool-basic', url=reverse('playground:tool_poisoning_variant', args=['basic'])),
                LabItem(id='tool_chain', title='工具调用·链式污染', subtitle='工具输出污染下一步决策', kind='tool', slug='tool-chain', url=reverse('playground:tool_poisoning_variant', args=['chain'])),
                LabItem(id='mcp_indirect', title='MCP·间接注入', subtitle='恶意 Server 返回隐藏指令', kind='mcp', slug='mcp-indirect', url=reverse('playground:mcp_indirect_lab')),
                LabItem(id='mcp_ssrf', title='MCP·Server SSRF', subtitle='添加 Server 时 SSRF 攻击', kind='mcp', slug='mcp-ssrf', url=reverse('playground:mcp_ssrf_lab')),
                LabItem(id='mcp_cross', title='MCP·跨工具调用', subtitle='诱导执行其他高危工具', kind='mcp', slug='mcp-cross-tool', url=reverse('playground:mcp_cross_tool_lab')),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['agent-security']),
        ),
        LabGroup(
            id='rag_security',
            title='3\ufe0f\u20e3 RAG 安全',
            items=[
                LabItem(id='rag_basic', title='RAG 知识库投毒', subtitle='向量库被污染后回答被带偏', kind='rag', slug='rag-basic', url=reverse('playground:rag_poisoning')),
                LabItem(id='rag_backdoor', title='RAG 后门触发', subtitle='特定查询激活隐藏指令', kind='rag', slug='rag-backdoor', url=reverse('playground:rag_poisoning_variant', args=['backdoor'])),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['rag-security']),
        ),
        LabGroup(
            id='multimodal_security',
            title='4\ufe0f\u20e3 多模态安全',
            items=[
                LabItem(id='multimodal_steganography', title='图像隐写注入', subtitle='在图片中隐藏恶意指令', kind='multimodal', slug='multimodal-steganography', url=reverse('playground:multimodal_lab', args=['steganography'])),
                LabItem(id='multimodal_typography', title='排版攻击', subtitle='利用文字渲染欺骗视觉模型', kind='multimodal', slug='multimodal-typography', url=reverse('playground:multimodal_lab', args=['typography'])),
                LabItem(id='multimodal_adversarial', title='对抗性扰动', subtitle='微小像素修改改变模型输出', kind='multimodal', slug='multimodal-adversarial', url=reverse('playground:multimodal_lab', args=['adversarial'])),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['multimodal-security']),
        ),
        LabGroup(
            id='output_security',
            title='5\ufe0f\u20e3 输出安全',
            items=[
                LabItem(id='output_xss', title='XSS（前端渲染）', subtitle='LLM 输出恶意 HTML 被前端渲染', kind='output', slug='output-xss', url=reverse('playground:xss_render_lab')),
                LabItem(id='output_ssti', title='SSTI（模板注入）', subtitle='用户输入进入 Jinja2 模板渲染', kind='output', slug='output-ssti', url=reverse('playground:ssti_jinja_lab')),
                LabItem(id='output_rce', title='RCE（eval/exec）', subtitle='后端 eval 执行 LLM 输出', kind='output', slug='output-rce', url=reverse('playground:rce_eval_lab')),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['output-security']),
        ),
        LabGroup(
            id='tool_security',
            title='6\ufe0f\u20e3 工具漏洞',
            items=[
                LabItem(id='tool_ssrf', title='SSRF（网页总结）', subtitle='Agent 访问内网/元数据', kind='tool_vuln', slug='tool-ssrf', url=reverse('playground:tool_ssrf_lab')),
                LabItem(id='tool_rce', title='RCE（代码执行）', subtitle='Agent eval 恶意代码', kind='tool_vuln', slug='tool-rce', url=reverse('playground:tool_rce_lab')),
                LabItem(id='tool_sqli', title='SQL 注入', subtitle='Agent 执行恶意 SQL', kind='tool_vuln', slug='tool-sqli', url=reverse('playground:tool_sqli_lab')),
                LabItem(id='tool_xxe', title='XXE/文件读取', subtitle='Agent 读取任意文件', kind='tool_vuln', slug='tool-xxe', url=reverse('playground:tool_xxe_lab')),
                LabItem(id='tool_yaml', title='反序列化', subtitle='unsafe_load 恶意 YAML', kind='tool_vuln', slug='tool-yaml', url=reverse('playground:tool_yaml_lab')),
                LabItem(id='tool_oauth', title='OAuth 凭证窃取', subtitle='Agent 持有过大权限', kind='tool_vuln', slug='tool-oauth', url=reverse('playground:tool_oauth_lab')),
                LabItem(id='tool_browser', title='浏览器操作', subtitle='Agent 打开恶意 URL', kind='tool_vuln', slug='tool-browser', url=reverse('playground:tool_browser_lab')),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['tool-security']),
        ),
        LabGroup(
            id='cswsh_security',
            title='7\ufe0f\u20e3 实时通信安全',
            items=[
                LabItem(id='cswsh_basic', title='CSWSH 劫持', subtitle='WebSocket 未校验 Origin', kind='cswsh', slug='cswsh-basic', url=reverse('playground:cswsh_lab')),
                LabItem(id='cswsh_dos', title='DoS 拒绝服务', subtitle='大量连接耗尽资源', kind='cswsh', slug='cswsh-dos', url=reverse('playground:dos_lab')),
            ],
            expanded=True,
        ),
        LabGroup(
            id='dvmcp',
            title='8\ufe0f\u20e3 DVMCP 实战靶场',
            items=[
                LabItem(id='dvmcp_challenges', title='MCP 安全挑战', subtitle='10 个递进式实战关卡', kind='dvmcp', slug='dvmcp', url=reverse('playground:dvmcp_index')),
            ],
            expanded=True,
        ),
        LabGroup(
            id='redteam',
            title='9\ufe0f\u20e3 红队工具',
            items=[
                LabItem(id='redteam_garak', title='Garak 扫描器', subtitle='自动化 LLM 漏洞扫描', kind='redteam', slug='garak', url=reverse('playground:garak_scanner')),
                LabItem(id='redteam_jailbreak', title='越狱 Payload 库', subtitle='收集整理的越狱提示词', kind='redteam', slug='jailbreak-payloads', url=reverse('playground:jailbreak_payloads')),
                LabItem(id='redteam_advanced', title='高级红队工具', subtitle='对抗训练与评估工具', kind='redteam', slug='advanced-tools', url=reverse('playground:advanced_tools')),
            ],
            expanded=True,
        ),
    ]

    # 设置当前激活的项
    for group in groups:
        for item in group.items:
            if item.id == active_item_id:
                item.active = True

    return {
        'sidebar_groups': groups,
        'lab_groups': groups,  # 兼容 lab_list_page 中使用的键名
        'active_item_id': active_item_id,
    }


# ============================================================
# 靶场分类元数据（lab_list 页面用）
# ============================================================

LAB_CATEGORIES = {
    'prompt-security': {
        'title': 'Prompt 安全',
        'icon': '1\ufe0f\u20e3',
        'description': 'System Prompt 泄露、越狱攻击、幻觉利用等 Prompt 层面的安全风险。',
        'principle_key': 'prompt_security',
        'group_id': 'prompt_security',
    },
    'agent-security': {
        'title': 'Agent 安全',
        'icon': '2\ufe0f\u20e3',
        'description': '记忆投毒、工具调用劫持、MCP 协议安全等 Agent 架构层面的风险。',
        'principle_key': 'agent_security',
        'group_id': 'agent_security',
    },
    'rag-security': {
        'title': 'RAG 安全',
        'icon': '3\ufe0f\u20e3',
        'description': '向量库/知识库投毒，利用 RAG 检索机制注入恶意内容。',
        'principle_key': 'rag_security',
        'group_id': 'rag_security',
    },
    'multimodal-security': {
        'title': '多模态安全',
        'icon': '4\ufe0f\u20e3',
        'description': '图像隐写、排版攻击、对抗性扰动等视觉模型安全风险。',
        'principle_key': 'multimodal_security',
        'group_id': 'multimodal_security',
    },
    'output-security': {
        'title': '输出安全',
        'icon': '5\ufe0f\u20e3',
        'description': 'LLM 输出被不安全地使用导致 XSS、SSTI、RCE 等传统漏洞。',
        'principle_key': 'output_security',
        'group_id': 'output_security',
    },
    'tool-security': {
        'title': '工具漏洞',
        'icon': '6\ufe0f\u20e3',
        'description': 'Agent 工具调用引发的 SSRF、SQL 注入、RCE、XXE 等服务端漏洞。',
        'principle_key': 'tool_security',
        'group_id': 'tool_security',
    },
    'cswsh-security': {
        'title': '实时通信安全',
        'icon': '7\ufe0f\u20e3',
        'description': 'WebSocket 劫持、DoS 等实时通信相关安全风险。',
        'principle_key': 'cswsh_security',
        'group_id': 'cswsh_security',
    },
    'redteam': {
        'title': '红队工具',
        'icon': '9\ufe0f\u20e3',
        'description': '自动化 LLM 安全扫描、越狱 Payload 库等红队实用工具。',
        'principle_key': 'redteam',
        'group_id': 'redteam',
    },
}
