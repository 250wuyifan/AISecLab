"""
视图模块

结构：
- _common.py: 公共工具函数（_call_llm, _get_llm_config, _build_sidebar_context 等）
- _legacy.py: 所有视图函数（后续可逐步拆分到独立模块）
"""

# 公共工具函数
from ._common import (
    _get_llm_config,
    _call_llm,
    _build_sidebar_context,
    LAB_CATEGORIES,
)

# 从 _legacy.py 导入所有视图函数
from ._legacy import (
    
    # 配置
    llm_config_view,
    llm_test_api,
    
    # 靶场列表与分类
    lab_list_page,
    lab_category_intro_page,
    
    # 记忆投毒
    memory_poisoning_page,
    memory_case_page,
    memory_chat_api,
    memory_reset_api,
    memory_edit_api,
    
    # 工具调用投毒
    tool_poisoning_page,
    tool_poisoning_variant_page,
    tool_chat_api,
    
    # RAG 投毒
    rag_poisoning_page,
    rag_poisoning_variant_page,
    rag_poisoning_seed,
    rag_poisoning_seed_variant,
    rag_poisoning_clear,
    rag_chat_api,
    
    # CSWSH / DoS
    cswsh_lab_page,
    cswsh_malicious_page,
    ws_connection_count_api,
    dos_lab_page,
    
    # 输出安全
    rce_eval_lab_page,
    rce_eval_demo_api,
    ssti_jinja_lab_page,
    ssti_jinja_demo_api,
    xss_render_lab_page,
    xss_render_demo_api,
    
    # 工具安全
    tool_rce_lab_page,
    tool_rce_invoke_api,
    tool_ssrf_lab_page,
    tool_ssrf_fetch_api,
    tool_xxe_lab_page,
    tool_xxe_read_file_api,
    tool_sqli_lab_page,
    tool_sqli_query_api,
    tool_yaml_lab_page,
    tool_yaml_parse_api,
    tool_oauth_lab_page,
    tool_oauth_chat_api,
    tool_browser_lab_page,
    tool_browser_url_api,
    
    # MCP 安全
    mcp_indirect_lab_page,
    mcp_ssrf_lab_page,
    mcp_cross_tool_lab_page,
    mcp_query_with_resource_api,
    mcp_add_server_api,
    mcp_cross_tool_api,
    
    # 进度/提示/收藏 API
    lab_complete_api,
    lab_hint_api,
    lab_favorite_api,
    lab_stats_api,
    
    # DVMCP 实战靶场
    dvmcp_index_page,
    dvmcp_challenge_page,
    dvmcp_status_api,
    dvmcp_config_api,
    dvmcp_llm_status_api,
    dvmcp_chat_api,
    dvmcp_tools_api,
    dvmcp_tool_call_api,
    dvmcp_resource_read_api,
    
    # System Prompt 泄露
    system_prompt_leak_page,
    system_prompt_leak_api,
    
    # 红队工具
    redteam_index_page,
    garak_scanner_page,
    garak_ollama_status_api,
    garak_scan_api,
    garak_scan_poll_api,
    mcpscan_scanner_page,
    mcpscan_scan_api,
    mcpscan_scan_poll_api,
    mcpscan_status_api,
    jailbreak_payloads_page,
    jailbreak_test_api,
    advanced_tools_page,
    
    # AIScan
    aiscan_page,
    aiscan_scan_api,
    aiscan_scan_poll_api,
    
    # 幻觉利用
    hallucination_lab_page,
    hallucination_chat_api,
    
    # 多模态安全
    multimodal_lab_page,
    multimodal_chat_api,
    multimodal_inject_api,
    multimodal_reset_api,
)

# 高级安全靶场（基于前沿研究）
from ._advanced_labs import (
    advanced_lab_page,
    advanced_lab_chat_api,
)

__all__ = [
    '_build_sidebar_context',
    'llm_config_view',
    'llm_test_api',
    'lab_list_page',
    'lab_category_intro_page',
    'memory_poisoning_page',
    'memory_case_page',
    'memory_chat_api',
    'memory_reset_api',
    'memory_edit_api',
    'tool_poisoning_page',
    'tool_poisoning_variant_page',
    'tool_chat_api',
    'rag_poisoning_page',
    'rag_poisoning_variant_page',
    'rag_poisoning_seed',
    'rag_poisoning_seed_variant',
    'rag_poisoning_clear',
    'rag_chat_api',
    'cswsh_lab_page',
    'cswsh_malicious_page',
    'ws_connection_count_api',
    'dos_lab_page',
    'rce_eval_lab_page',
    'rce_eval_demo_api',
    'ssti_jinja_lab_page',
    'ssti_jinja_demo_api',
    'xss_render_lab_page',
    'xss_render_demo_api',
    'tool_rce_lab_page',
    'tool_rce_invoke_api',
    'tool_ssrf_lab_page',
    'tool_ssrf_fetch_api',
    'tool_xxe_lab_page',
    'tool_xxe_read_file_api',
    'tool_sqli_lab_page',
    'tool_sqli_query_api',
    'tool_yaml_lab_page',
    'tool_yaml_parse_api',
    'tool_oauth_lab_page',
    'tool_oauth_chat_api',
    'tool_browser_lab_page',
    'tool_browser_url_api',
    'mcp_indirect_lab_page',
    'mcp_ssrf_lab_page',
    'mcp_cross_tool_lab_page',
    'mcp_query_with_resource_api',
    'mcp_add_server_api',
    'mcp_cross_tool_api',
    'lab_complete_api',
    'lab_hint_api',
    'lab_favorite_api',
    'lab_stats_api',
    'dvmcp_index_page',
    'dvmcp_challenge_page',
    'dvmcp_status_api',
    'dvmcp_config_api',
    'dvmcp_llm_status_api',
    'dvmcp_chat_api',
    'dvmcp_tools_api',
    'dvmcp_tool_call_api',
    'dvmcp_resource_read_api',
    'system_prompt_leak_page',
    'system_prompt_leak_api',
    'redteam_index_page',
    'garak_scanner_page',
    'garak_ollama_status_api',
    'garak_scan_api',
    'jailbreak_payloads_page',
    'jailbreak_test_api',
    'advanced_tools_page',
    'hallucination_lab_page',
    'hallucination_chat_api',
    'multimodal_lab_page',
    'multimodal_chat_api',
    'multimodal_inject_api',
    'multimodal_reset_api',
    # 高级安全靶场
    'advanced_lab_page',
    'advanced_lab_chat_api',
    # AIScan
    'aiscan_page',
    'aiscan_scan_api',
    'aiscan_scan_poll_api',
]
