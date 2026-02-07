"""
公共工具函数 — 所有视图模块共享

- _get_llm_config / _call_llm: 统一 LLM 调用
- _get_memory_obj / _get_shared_user: 记忆管理
- _infer_provider_label / _apply_lab_meta / _ensure_lab_meta: 元数据工具
- _build_sidebar_context: 靶场侧栏构建
- get_sample_files: 跨平台示例文件路径
"""
import json
import os
import sys
import re
from pathlib import Path
from typing import Any, Dict, List

import requests as req_lib

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from ..models import AgentMemory, LLMConfig, LabCaseMeta, LabProgress, LabFavorite
from ..forms import LLMConfigForm
from ..memory_cases import LabGroup, LabItem, build_memory_poisoning_groups
from ..lab_principles import get_principle


# ============================================================
# 跨平台工具函数
# ============================================================

def get_platform_info() -> dict:
    """获取当前平台信息"""
    return {
        'system': sys.platform,  # 'win32', 'darwin', 'linux'
        'is_windows': sys.platform == 'win32',
        'is_macos': sys.platform == 'darwin',
        'is_linux': sys.platform.startswith('linux'),
    }


def get_sample_files() -> dict:
    """
    获取跨平台的示例文件路径
    用于靶场演示，确保 Windows/macOS/Linux 都能正常读取
    """
    base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent.parent))
    samples_dir = base_dir / 'static' / 'playground' / 'samples'
    
    return {
        'secret_config': str(samples_dir / 'secret_config.txt'),
        'employees': str(samples_dir / 'employees.txt'),
        'readme': str(samples_dir / 'README.txt'),
        'samples_dir': str(samples_dir),
    }


def get_sample_file_examples() -> list:
    """
    获取用于前端显示的示例文件列表
    返回跨平台兼容的路径
    """
    files = get_sample_files()
    platform = get_platform_info()
    
    # 根据平台提供不同的示例路径格式
    if platform['is_windows']:
        system_examples = [
            {'path': 'C:\\Windows\\System32\\drivers\\etc\\hosts', 'name': 'hosts 文件', 'dangerous': True},
            {'path': '%USERPROFILE%\\.ssh\\config', 'name': 'SSH 配置', 'dangerous': True},
        ]
    else:
        system_examples = [
            {'path': '/etc/passwd', 'name': '用户列表', 'dangerous': True},
            {'path': '/etc/hosts', 'name': 'hosts 文件', 'dangerous': True},
            {'path': '~/.ssh/config', 'name': 'SSH 配置', 'dangerous': True},
        ]
    
    return {
        'safe': [
            {'path': files['secret_config'], 'name': '示例配置文件', 'dangerous': False},
            {'path': files['employees'], 'name': '示例员工信息', 'dangerous': False},
        ],
        'dangerous': system_examples,
    }


# ============================================================
# LLM 配置与调用
# ============================================================

def _get_llm_config():
    """获取全局 LLM 配置，不存在或未启用时返回 None"""
    cfg = LLMConfig.objects.first()
    if cfg and cfg.enabled:
        return cfg
    return None


def _is_local_url(url: str) -> bool:
    """判断 URL 是否指向本机，本机请求需要绕过代理"""
    return any(h in url for h in ('://127.0.0.1', '://localhost', '://0.0.0.0'))


# 本机请求禁用代理，避免被 Clash 等代理工具劫持
_NO_PROXY = {'http': None, 'https': None}


def _call_llm(messages: list, *, timeout: int = 60, max_tokens: int | None = None) -> str:
    """
    统一 LLM 调用入口。
    - 自动从 LLMConfig 读取 api_base / api_key / default_model
    - 自动兼容 OpenAI chat/completions 和 Ollama /api/chat 两种返回格式
    - 本机地址自动绕过系统代理
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

    kwargs: dict = dict(json=payload, headers=headers, timeout=timeout)
    if _is_local_url(cfg.api_base):
        kwargs['proxies'] = _NO_PROXY

    resp = req_lib.post(cfg.api_base, **kwargs)
    resp.raise_for_status()
    data = resp.json()

    # 兼容 OpenAI chat/completions 格式
    choices = data.get('choices', [])
    if choices:
        return choices[0].get('message', {}).get('content', '')
    # 兼容 Ollama /api/chat 格式
    return data.get('message', {}).get('content', '')


def _call_multimodal_llm(
    messages: list,
    *,
    model_override: str | None = None,
    timeout: int = 120,
    max_tokens: int | None = None,
) -> str:
    """
    多模态 LLM 调用入口 — 支持在 messages 中包含图片。

    messages 格式示例（OpenAI vision 兼容）：
    [
        {"role": "system", "content": "..."},
        {"role": "user", "content": [
            {"type": "text", "text": "描述这张图片"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBOR..."}}
        ]},
    ]

    model_override: 可指定模型名（如 qwen3-vl:32b），不指定则用全局配置。
    """
    cfg = _get_llm_config()
    if not cfg:
        raise ValueError('尚未配置或未启用大模型，请点击「配置 LLM」进行设置')

    headers = {'Content-Type': 'application/json'}
    if cfg.api_key:
        headers['Authorization'] = f'Bearer {cfg.api_key}'

    payload: dict = {
        'model': model_override or cfg.default_model,
        'messages': messages,
    }
    if max_tokens is not None:
        payload['max_tokens'] = max_tokens

    kwargs: dict = dict(json=payload, headers=headers, timeout=timeout)
    if _is_local_url(cfg.api_base):
        kwargs['proxies'] = _NO_PROXY

    resp = req_lib.post(cfg.api_base, **kwargs)
    resp.raise_for_status()
    data = resp.json()

    choices = data.get('choices', [])
    if choices:
        return choices[0].get('message', {}).get('content', '')
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
    构建靶场左侧侧栏 — 按攻击阶段的 6 大分类体系

    1. Prompt 安全 — 输入层攻击
    2. 记忆投毒   — 上下文层攻击
    3. RAG 安全   — 知识库攻击
    4. 工具与 MCP 安全 — Agent 层攻击（工具投毒 + MCP 协议）
    5. 多模态安全 — 视觉/跨模态攻击
    6. 输出与工具漏洞 — 输出层（XSS/SSTI/RCE + SSRF/SQLi/XXE/… + CSWSH）
    + DVMCP 实战靶场
    + 红队工具
    """

    groups = [
        LabGroup(
            id='prompt_security',
            title='1\ufe0f\u20e3 Prompt 安全',
            items=[
                LabItem(id='prompt_leak', title='System Prompt 泄露', subtitle='诱导 LLM 泄露系统提示词', kind='prompt', slug='system-prompt-leak', url=reverse('playground:system_prompt_leak')),
                LabItem(id='jailbreak', title='越狱攻击', subtitle='绕过安全限制的各种技巧', kind='prompt', slug='jailbreak', url=reverse('playground:jailbreak_payloads')),
                LabItem(id='hallucination', title='幻觉利用', subtitle='利用 LLM 生成虚假信息', kind='prompt', slug='hallucination', url=reverse('playground:hallucination_lab')),
                LabItem(id='adv_cot_hijack', title='CoT 推理链劫持', subtitle='注入伪造推理步骤劫持安全审核', kind='prompt', slug='cot-hijack', url=reverse('playground:advanced_lab', args=['cot-hijack'])),
                LabItem(id='adv_reasoning_leak', title='推理轨迹泄露', subtitle='诱导 Thinking 模型泄露敏感配置', kind='prompt', slug='reasoning-leak', url=reverse('playground:advanced_lab', args=['reasoning-leak'])),
                LabItem(id='adv_prompt_url', title='Prompt-as-URL 注入', subtitle='URL 参数一键注入 Agent 会话', kind='prompt', slug='prompt-url', url=reverse('playground:advanced_lab', args=['prompt-url'])),
                LabItem(id='adv_system_prompt_poison', title='系统提示投毒', subtitle='供应链上游篡改系统提示模板', kind='prompt', slug='system-prompt-poison', url=reverse('playground:advanced_lab', args=['system-prompt-poison'])),
                LabItem(id='adv_evaluator_hack', title='评估器操控', subtitle='操纵 ToT 多候选评估打分逻辑', kind='prompt', slug='evaluator-hack', url=reverse('playground:advanced_lab', args=['evaluator-hack'])),
                LabItem(id='adv_cot_dos', title='CoT 资源耗尽', subtitle='诱导无限递归推理消耗 Token', kind='prompt', slug='cot-dos', url=reverse('playground:advanced_lab', args=['cot-dos'])),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['prompt-security']),
        ),
        LabGroup(
            id='memory_security',
            title='2\ufe0f\u20e3 记忆投毒',
            items=[
                LabItem(id='mem_dialog', title='直接注入', subtitle='对话中直接注入恶意指令', kind='memory', slug='dialog', url=reverse('playground:memory_case', args=['dialog'])),
                LabItem(id='mem_drift', title='行为漂移', subtitle='多轮渐进式改变行为', kind='memory', slug='drift', url=reverse('playground:memory_case', args=['drift'])),
                LabItem(id='mem_progressive', title='渐进式污染', subtitle='建立信任→强化认知→激活恶意', kind='memory', slug='progressive', url=reverse('playground:memory_case', args=['progressive'])),
                LabItem(id='mem_replay', title='记忆回放', subtitle='历史记忆被检索时重新激活', kind='memory', slug='replay', url=reverse('playground:memory_case', args=['replay'])),
                LabItem(id='mem_cross_session', title='跨会话状态', subtitle='会话A设状态，后续会话触发', kind='memory', slug='cross-session', url=reverse('playground:memory_case', args=['cross-session'])),
                LabItem(id='mem_logic_bomb', title='逻辑炸弹', subtitle='条件满足时才激活的隐藏指令', kind='memory', slug='logic-bomb', url=reverse('playground:memory_case', args=['logic-bomb'])),
                LabItem(id='mem_trigger', title='触发器后门', subtitle='特定触发词激活隐藏指令', kind='memory', slug='trigger', url=reverse('playground:memory_case', args=['trigger'])),
                LabItem(id='mem_shared', title='跨用户污染', subtitle='共享记忆一人注入影响全体', kind='memory', slug='shared', url=reverse('playground:memory_case', args=['shared'])),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['memory-security']),
        ),
        LabGroup(
            id='rag_security',
            title='3\ufe0f\u20e3 RAG 安全',
            items=[
                LabItem(id='rag_basic', title='RAG 知识库投毒', subtitle='向量库被污染后回答被带偏', kind='rag', slug='rag-basic', url=reverse('playground:rag_poisoning')),
                LabItem(id='rag_backdoor', title='RAG 后门触发', subtitle='特定查询激活隐藏指令', kind='rag', slug='rag-backdoor', url=reverse('playground:rag_poisoning_variant', args=['backdoor'])),
                LabItem(id='rag_doc_hidden', title='文档隐藏指令', subtitle='文档中混入对人不可见、模型可读的指令', kind='rag', slug='rag-doc-hidden', url=reverse('playground:rag_poisoning_variant', args=['doc-hidden'])),
                LabItem(id='adv_distributed_inject', title='分布式提示注入', subtitle='多文档片段分别无害、组合拼出恶意指令', kind='rag', slug='distributed-inject', url=reverse('playground:advanced_lab', args=['distributed-inject'])),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['rag-security']),
        ),
        LabGroup(
            id='tool_mcp_security',
            title='4\ufe0f\u20e3 工具与 MCP 安全',
            items=[
                LabItem(id='tool_basic', title='工具调用·基础投毒', subtitle='记忆指令劫持工具调用', kind='tool', slug='tool-basic', url=reverse('playground:tool_poisoning_variant', args=['basic'])),
                LabItem(id='tool_chain', title='工具调用·链式污染', subtitle='工具输出污染下一步决策', kind='tool', slug='tool-chain', url=reverse('playground:tool_poisoning_variant', args=['chain'])),
                LabItem(id='tool_return_poison', title='工具调用·返回污染', subtitle='接口返回值中隐藏指令被执行', kind='tool', slug='tool-return-poison', url=reverse('playground:tool_poisoning_variant', args=['return-poison'])),
                LabItem(id='tool_param_poison', title='工具调用·参数污染', subtitle='诱导 Agent 传递恶意参数值', kind='tool', slug='tool-param-poison', url=reverse('playground:tool_poisoning_variant', args=['param-poison'])),
                LabItem(id='mcp_indirect', title='MCP·间接注入', subtitle='恶意 Server 返回隐藏指令', kind='mcp', slug='mcp-indirect', url=reverse('playground:mcp_indirect_lab')),
                LabItem(id='mcp_ssrf', title='MCP·Server SSRF', subtitle='添加 Server 时 SSRF 攻击', kind='mcp', slug='mcp-ssrf', url=reverse('playground:mcp_ssrf_lab')),
                LabItem(id='mcp_cross', title='MCP·跨工具调用', subtitle='诱导执行其他高危工具', kind='mcp', slug='mcp-cross-tool', url=reverse('playground:mcp_cross_tool_lab')),
                LabItem(id='adv_context_confusion', title='上下文来源混淆', subtitle='伪造上下文标签让外部数据当系统指令', kind='tool', slug='context-confusion', url=reverse('playground:advanced_lab', args=['context-confusion'])),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['tool-mcp-security']),
        ),
        LabGroup(
            id='multimodal_security',
            title='5\ufe0f\u20e3 多模态安全',
            items=[
                LabItem(id='multimodal_steganography', title='图像隐写注入', subtitle='图片中嵌入人眼不可见的恶意指令', kind='multimodal', slug='multimodal-steganography', url=reverse('playground:multimodal_lab', args=['steganography'])),
                LabItem(id='multimodal_visual_mislead', title='视觉误导攻击', subtitle='伪造截图欺骗 LLM 做出错误判断', kind='multimodal', slug='multimodal-visual-mislead', url=reverse('playground:multimodal_lab', args=['visual_mislead'])),
                LabItem(id='multimodal_cross_modal', title='跨模态绕过', subtitle='将敏感文本做成图片绕过文本过滤', kind='multimodal', slug='multimodal-cross-modal', url=reverse('playground:multimodal_lab', args=['cross_modal'])),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['multimodal-security']),
        ),
        LabGroup(
            id='output_tool_security',
            title='6\ufe0f\u20e3 输出与工具漏洞',
            items=[
                # --- 输出处理漏洞 ---
                LabItem(id='output_xss', title='XSS（前端渲染）', subtitle='LLM 输出恶意 HTML 被前端渲染', kind='output', slug='output-xss', url=reverse('playground:xss_render_lab')),
                LabItem(id='output_ssti', title='SSTI（模板注入）', subtitle='用户输入进入 Jinja2 模板渲染', kind='output', slug='output-ssti', url=reverse('playground:ssti_jinja_lab')),
                LabItem(id='output_rce', title='RCE（eval/exec）', subtitle='后端 eval 执行 LLM 输出', kind='output', slug='output-rce', url=reverse('playground:rce_eval_lab')),
                # --- Agent 工具服务端漏洞 ---
                LabItem(id='tool_ssrf', title='SSRF（网页总结）', subtitle='Agent 访问内网/元数据', kind='tool_vuln', slug='tool-ssrf', url=reverse('playground:tool_ssrf_lab')),
                LabItem(id='tool_rce', title='RCE（代码执行）', subtitle='Agent eval 恶意代码', kind='tool_vuln', slug='tool-rce', url=reverse('playground:tool_rce_lab')),
                LabItem(id='tool_sqli', title='SQL 注入', subtitle='Agent 执行恶意 SQL', kind='tool_vuln', slug='tool-sqli', url=reverse('playground:tool_sqli_lab')),
                LabItem(id='tool_xxe', title='XXE/文件读取', subtitle='Agent 读取任意文件', kind='tool_vuln', slug='tool-xxe', url=reverse('playground:tool_xxe_lab')),
                LabItem(id='tool_yaml', title='反序列化', subtitle='unsafe_load 恶意 YAML', kind='tool_vuln', slug='tool-yaml', url=reverse('playground:tool_yaml_lab')),
                LabItem(id='tool_oauth', title='OAuth 凭证窃取', subtitle='Agent 持有过大权限被窃取', kind='tool_vuln', slug='tool-oauth', url=reverse('playground:tool_oauth_lab')),
                LabItem(id='tool_browser', title='浏览器操作', subtitle='Agent 打开恶意 URL', kind='tool_vuln', slug='tool-browser', url=reverse('playground:tool_browser_lab')),
                # --- 实时通信 ---
                LabItem(id='cswsh_basic', title='CSWSH 劫持', subtitle='WebSocket 未校验 Origin', kind='cswsh', slug='cswsh-basic', url=reverse('playground:cswsh_lab')),
                LabItem(id='cswsh_dos', title='DoS 拒绝服务', subtitle='大量连接耗尽资源', kind='cswsh', slug='cswsh-dos', url=reverse('playground:dos_lab')),
            ],
            expanded=True,
            intro_url=reverse('playground:lab_category_intro', args=['output-tool-security']),
        ),
        LabGroup(
            id='dvmcp',
            title='7\ufe0f\u20e3 DVMCP 实战靶场',
            items=[
                LabItem(id='dvmcp_challenges', title='MCP 安全挑战', subtitle='10 个递进式实战关卡', kind='dvmcp', slug='dvmcp', url=reverse('playground:dvmcp_index')),
            ],
            expanded=True,
        ),
        LabGroup(
            id='redteam',
            title='8\ufe0f\u20e3 红队工具',
            items=[
                LabItem(id='redteam_garak', title='Garak 扫描器', subtitle='自动化 LLM 漏洞扫描', kind='redteam', slug='garak', url=reverse('playground:garak_scanner')),
                LabItem(id='redteam_mcpscan', title='MCPScan', subtitle='MCP 协议多阶段安全扫描', kind='redteam', slug='mcpscan', url=reverse('playground:mcpscan_scanner')),
                LabItem(id='redteam_jailbreak', title='越狱 Payload 库', subtitle='收集整理的越狱提示词', kind='redteam', slug='jailbreak-payloads', url=reverse('playground:jailbreak_payloads')),
                LabItem(id='redteam_aiscan', title='AIScan 扫描器', subtitle='自研 AI 安全扫描器（模型+代码）', kind='redteam', slug='aiscan', url=reverse('playground:aiscan_scanner')),
                LabItem(id='redteam_advanced', title='高级红队工具', subtitle='对抗训练与评估工具', kind='redteam', slug='advanced-tools', url=reverse('playground:advanced_tools')),
            ],
            expanded=True,
        ),
    ]

    # 设置当前激活的项（LabItem 是 frozen dataclass，用 object.__setattr__ 绕过）
    for group in groups:
        for item in group.items:
            if item.id == active_item_id:
                object.__setattr__(item, 'active', True)

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
        'description': 'System Prompt 泄露、越狱攻击、幻觉利用、CoT 推理链劫持、推理轨迹泄露、'
                       'URL 参数注入、系统提示投毒、评估器操控、CoT 资源耗尽等 Prompt 层面的安全风险。',
        'principle_key': 'prompt_security',
        'group_id': 'prompt_security',
    },
    'memory-security': {
        'title': '记忆投毒',
        'icon': '2\ufe0f\u20e3',
        'description': '通过对话注入、行为漂移、逻辑炸弹等手段污染 Agent 记忆，实现持久化攻击。',
        'principle_key': 'memory_security',
        'group_id': 'memory_security',
    },
    'rag-security': {
        'title': 'RAG 安全',
        'icon': '3\ufe0f\u20e3',
        'description': '向量库/知识库投毒，利用 RAG 检索机制注入恶意内容。',
        'principle_key': 'rag_security',
        'group_id': 'rag_security',
    },
    'tool-mcp-security': {
        'title': '工具与 MCP 安全',
        'icon': '4\ufe0f\u20e3',
        'description': '工具调用投毒（基础/链式/返回/参数）及 MCP 协议安全（间接注入/SSRF/跨工具）。',
        'principle_key': 'tool_mcp_security',
        'group_id': 'tool_mcp_security',
    },
    'multimodal-security': {
        'title': '多模态安全',
        'icon': '5\ufe0f\u20e3',
        'description': '图像隐写、视觉误导、跨模态绕过等多模态 LLM 安全风险。',
        'principle_key': 'multimodal_security',
        'group_id': 'multimodal_security',
    },
    'output-tool-security': {
        'title': '输出与工具漏洞',
        'icon': '6\ufe0f\u20e3',
        'description': 'LLM 输出被不安全使用导致的 XSS/SSTI/RCE，以及 Agent 工具引发的 SSRF/SQLi/XXE 等服务端漏洞。',
        'principle_key': 'output_tool_security',
        'group_id': 'output_tool_security',
    },
    'redteam': {
        'title': '红队工具',
        'icon': '8\ufe0f\u20e3',
        'description': '自动化 LLM 安全扫描、越狱 Payload 库等红队实用工具。',
        'principle_key': 'redteam',
        'group_id': 'redteam',
    },
}


# ============================================================
# 一级分类介绍页数据
# ============================================================

_CATEGORY_INTRO = {
    'prompt-security': {
        'group_id': 'prompt_security',
        'title': 'Prompt 安全',
        'subtitle': '输入层攻击 — 通过精心构造的提示词突破 LLM 安全边界',
        'what': 'Prompt 安全关注攻击者如何利用精心构造的提示词来泄露系统提示词、'
                '绕过安全限制（越狱）、诱导模型产生虚假信息（幻觉），'
                '以及利用推理链劫持（CoT Hijack）、推理轨迹泄露、URL 参数注入、'
                '系统提示投毒（供应链攻击）、评估器操控和 CoT 资源耗尽等前沿攻击手段。'
                '这是 LLM 安全中最基础、最广泛的攻击面。',
        'harms': [
            {'name': '信息泄露', 'desc': '系统提示词被提取，暴露业务逻辑与安全策略', 'severity': '🟡 中'},
            {'name': '安全绕过', 'desc': '越狱攻击使模型生成违规内容', 'severity': '🔴 高'},
            {'name': '错误引导', 'desc': '幻觉输出导致用户做出错误决策', 'severity': '🟡 中'},
            {'name': 'CoT 劫持', 'desc': '伪造推理步骤绕过安全审核', 'severity': '🔴 高'},
            {'name': '推理泄露', 'desc': 'Thinking 模型暴露敏感配置信息', 'severity': '🔴 高'},
            {'name': '供应链投毒', 'desc': '篡改系统提示模板影响所有下游会话', 'severity': '🔴 高'},
            {'name': '资源耗尽', 'desc': '诱导无限递归推理消耗 Token 和算力', 'severity': '🟡 中'},
        ],
        'causes': '根本原因在于 LLM 无法可靠区分"指令"与"数据"，用户输入与系统指令共享同一上下文窗口。'
                '推理链（CoT）可被续写劫持，系统提示模板处于信任边界之外却被无条件信任。',
    },
    'memory-security': {
        'group_id': 'memory_security',
        'title': '记忆投毒',
        'subtitle': '上下文层攻击 — 通过污染 Agent 记忆实现持久化攻击',
        'what': '记忆投毒攻击针对具有持久记忆的 AI Agent，通过在对话中注入恶意指令、'
                '渐进式改变模型行为、植入逻辑炸弹或跨会话/跨用户传播，'
                '使 Agent 的长期行为被攻击者控制。',
        'harms': [
            {'name': '行为劫持', 'desc': 'Agent 在后续交互中执行攻击者指令', 'severity': '🔴 高'},
            {'name': '持久后门', 'desc': '恶意指令存入记忆，重启后依然生效', 'severity': '🔴 高'},
            {'name': '横向扩散', 'desc': '共享记忆场景下一人注入影响全体用户', 'severity': '🔴 高'},
        ],
        'causes': '根本原因是 Agent 对记忆内容缺乏可信度分级，用户输入与系统指令在记忆中同等对待。',
    },
    'rag-security': {
        'group_id': 'rag_security',
        'title': 'RAG 安全',
        'subtitle': '知识库层攻击 — 通过污染外部知识库影响 LLM 输出',
        'what': 'RAG（检索增强生成）安全关注攻击者如何向向量库/知识库注入恶意文档，'
                '通过相似度检索被召回后影响 LLM 的回答。包括直接投毒、后门触发、'
                '文档隐藏指令和分布式提示注入（多文档片段分别无害、组合拼出恶意指令）。',
        'harms': [
            {'name': '知识污染', 'desc': '向量库被植入错误或恶意信息', 'severity': '🔴 高'},
            {'name': '隐蔽触发', 'desc': '特定查询激活隐藏在文档中的恶意指令', 'severity': '🔴 高'},
            {'name': '信任利用', 'desc': '用户信任基于知识库的回答，更易被误导', 'severity': '🟡 中'},
            {'name': '分布式注入', 'desc': '多个无害文档片段组合后形成恶意指令，绕过单文档审查', 'severity': '🔴 高'},
        ],
        'causes': 'LLM 将检索到的文档视为可信来源，无法区分正常知识与注入的恶意内容。'
                '安全审查仅针对单个文档，未考虑多文档组合后的语义变化。',
    },
    'tool-mcp-security': {
        'group_id': 'tool_mcp_security',
        'title': '工具与 MCP 安全',
        'subtitle': 'Agent 层攻击 — 通过工具投毒和 MCP 协议漏洞控制 Agent 行为',
        'what': '当 AI Agent 通过工具调用与外部系统交互时，攻击者可以通过投毒工具返回值、'
                '污染工具链、注入恶意参数来劫持 Agent 行为。MCP（Model Context Protocol）'
                '作为新兴的工具协议，也面临间接注入、SSRF 和跨工具调用等安全挑战。'
                '此外，上下文来源混淆攻击通过伪造上下文标签使外部数据被当作系统指令执行。',
        'harms': [
            {'name': '工具劫持', 'desc': '恶意指令通过记忆劫持工具调用', 'severity': '🔴 高'},
            {'name': '链式攻击', 'desc': '工具输出被污染后影响下游决策', 'severity': '🔴 高'},
            {'name': 'MCP 注入', 'desc': '恶意 MCP Server 返回隐藏指令', 'severity': '🔴 高'},
            {'name': '权限滥用', 'desc': '跨工具调用被诱导执行高危操作', 'severity': '🔴 高'},
            {'name': '上下文混淆', 'desc': '伪造上下文标签让外部数据被当作系统指令', 'severity': '🔴 高'},
        ],
        'causes': 'Agent 对工具返回值和 MCP 消息缺乏验证，盲目信任外部数据源。'
                '上下文标签是可预测的纯文本，LLM 无法区分真实标签和伪造标签。',
    },
    'multimodal-security': {
        'group_id': 'multimodal_security',
        'title': '多模态安全',
        'subtitle': '视觉/跨模态攻击 — 利用图像等非文本输入绕过安全检测',
        'what': '多模态 LLM 能理解图像、音频等非文本输入，这也带来了新的攻击面：'
                '在图像中隐写恶意指令、通过伪造截图误导模型判断、将敏感文本转为图片绕过文本过滤。',
        'harms': [
            {'name': '隐蔽注入', 'desc': '图像隐写的指令人眼不可见但模型可读', 'severity': '🟡 中'},
            {'name': '视觉欺骗', 'desc': '伪造截图让模型做出错误判断', 'severity': '🔴 高'},
            {'name': '过滤绕过', 'desc': '文本过滤器无法检测图像中的文本', 'severity': '🟡 中'},
        ],
        'causes': '多模态模型对图像内容的理解能力超越了传统安全检测手段的覆盖范围。',
    },
    'output-tool-security': {
        'group_id': 'output_tool_security',
        'title': '输出与工具漏洞',
        'subtitle': '输出层攻击 — LLM 输出被不安全使用导致的传统漏洞及 Agent 工具服务端漏洞',
        'what': '当 LLM 的输出被直接用于 HTML 渲染（XSS）、模板引擎（SSTI）、代码执行（RCE）时，'
                '传统 Web 安全漏洞在 AI 场景下被重新激活。同时，当 Agent 通过工具调用访问网络（SSRF）、'
                '数据库（SQLi）、文件系统（XXE）等后端资源时，也可能被诱导产生服务端漏洞。'
                '此外还包括 WebSocket 实时通信相关的安全风险。',
        'harms': [
            {'name': 'XSS', 'desc': '恶意 HTML/JS 在用户浏览器执行', 'severity': '🟡 中'},
            {'name': 'SSTI', 'desc': '模板注入导致服务端代码执行', 'severity': '🔴 高'},
            {'name': 'RCE', 'desc': 'eval/exec 执行恶意代码', 'severity': '🔴 高'},
            {'name': 'SSRF', 'desc': 'Agent 被诱导访问内网资源', 'severity': '🔴 高'},
            {'name': 'SQL 注入', 'desc': 'Agent 执行恶意 SQL 语句', 'severity': '🔴 高'},
            {'name': 'XXE/文件读取', 'desc': 'Agent 读取服务器敏感文件', 'severity': '🔴 高'},
            {'name': '反序列化', 'desc': 'YAML unsafe_load 导致代码执行', 'severity': '🔴 高'},
            {'name': 'CSWSH', 'desc': 'WebSocket 跨站劫持', 'severity': '🟡 中'},
        ],
        'causes': '根本原因是应用层未对 LLM 输出/工具调用参数进行充分的验证和过滤。',
    },
    'cswsh': {
        'group_id': 'output_tool_security',
        'title': 'CSWSH 实时通信安全',
        'subtitle': 'WebSocket 劫持与 DoS 攻击',
        'what': 'WebSocket 连接如果不校验 Origin，攻击者可通过恶意网页劫持用户的 WS 会话。',
        'harms': [
            {'name': 'CSWSH', 'desc': 'WebSocket 跨站劫持', 'severity': '🟡 中'},
            {'name': 'DoS', 'desc': '大量连接耗尽服务端资源', 'severity': '🟡 中'},
        ],
        'causes': 'WebSocket 握手未校验 Origin 头，连接数未做限制。',
    },
}