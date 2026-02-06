"""
靶场基础测试 — 确保所有页面可以正常渲染，API 接口可以正确响应。

运行: python manage.py test playground
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import LLMConfig


class LabPageResponseTest(TestCase):
    """测试所有靶场页面返回 200"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        # 创建一个 LLM 配置
        LLMConfig.objects.create(
            pk=1,
            provider='ollama',
            api_base='http://127.0.0.1:11434/v1/chat/completions',
            api_key='test-key',
            default_model='qwen2.5',
            enabled=True,
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    # ---- 靶场列表与配置 ----

    def test_lab_list_page(self):
        resp = self.client.get(reverse('playground:lab_list'))
        self.assertEqual(resp.status_code, 200)

    def test_llm_config_page(self):
        resp = self.client.get(reverse('playground:llm_config'))
        self.assertEqual(resp.status_code, 200)

    # ---- Prompt 安全 ----

    def test_system_prompt_leak_page(self):
        resp = self.client.get(reverse('playground:system_prompt_leak'))
        self.assertEqual(resp.status_code, 200)

    def test_jailbreak_payloads_page(self):
        resp = self.client.get(reverse('playground:jailbreak_payloads'))
        self.assertEqual(resp.status_code, 200)

    def test_hallucination_lab_page(self):
        resp = self.client.get(reverse('playground:hallucination_lab'))
        self.assertEqual(resp.status_code, 200)

    # ---- Agent 安全 ----

    def test_memory_poisoning_page(self):
        resp = self.client.get(reverse('playground:memory_poisoning'))
        self.assertIn(resp.status_code, [200, 302])  # 可能重定向到默认 case

    def test_memory_case_dialog_page(self):
        resp = self.client.get(reverse('playground:memory_case', args=['dialog']))
        self.assertEqual(resp.status_code, 200)

    def test_tool_poisoning_page(self):
        resp = self.client.get(reverse('playground:tool_poisoning'))
        self.assertIn(resp.status_code, [200, 302])  # 可能重定向到默认变体

    # ---- RAG ----

    def test_rag_poisoning_page(self):
        resp = self.client.get(reverse('playground:rag_poisoning'))
        self.assertIn(resp.status_code, [200, 302])  # 可能重定向到默认变体

    # ---- 工具安全 ----

    def test_tool_ssrf_lab_page(self):
        resp = self.client.get(reverse('playground:tool_ssrf_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_tool_rce_lab_page(self):
        resp = self.client.get(reverse('playground:tool_rce_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_tool_xxe_lab_page(self):
        resp = self.client.get(reverse('playground:tool_xxe_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_tool_sqli_lab_page(self):
        resp = self.client.get(reverse('playground:tool_sqli_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_tool_yaml_lab_page(self):
        resp = self.client.get(reverse('playground:tool_yaml_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_tool_oauth_lab_page(self):
        resp = self.client.get(reverse('playground:tool_oauth_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_tool_browser_lab_page(self):
        resp = self.client.get(reverse('playground:tool_browser_lab'))
        self.assertEqual(resp.status_code, 200)

    # ---- MCP 安全 ----

    def test_mcp_indirect_lab_page(self):
        resp = self.client.get(reverse('playground:mcp_indirect_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_mcp_ssrf_lab_page(self):
        resp = self.client.get(reverse('playground:mcp_ssrf_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_mcp_cross_tool_lab_page(self):
        resp = self.client.get(reverse('playground:mcp_cross_tool_lab'))
        self.assertEqual(resp.status_code, 200)

    # ---- 输出安全 ----

    def test_rce_eval_lab_page(self):
        resp = self.client.get(reverse('playground:rce_eval_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_ssti_jinja_lab_page(self):
        resp = self.client.get(reverse('playground:ssti_jinja_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_xss_render_lab_page(self):
        resp = self.client.get(reverse('playground:xss_render_lab'))
        self.assertEqual(resp.status_code, 200)

    # ---- CSWSH ----

    def test_cswsh_lab_page(self):
        resp = self.client.get(reverse('playground:cswsh_lab'))
        self.assertEqual(resp.status_code, 200)

    def test_dos_lab_page(self):
        resp = self.client.get(reverse('playground:dos_lab'))
        self.assertEqual(resp.status_code, 200)

    # ---- 红队工具 ----

    def test_redteam_index_page(self):
        resp = self.client.get(reverse('playground:redteam_index'))
        self.assertEqual(resp.status_code, 200)

    def test_garak_scanner_page(self):
        resp = self.client.get(reverse('playground:garak_scanner'))
        self.assertEqual(resp.status_code, 200)

    # ---- DVMCP ----

    def test_dvmcp_index_page(self):
        resp = self.client.get(reverse('playground:dvmcp_index'))
        self.assertEqual(resp.status_code, 200)

    # ---- 多模态 ----

    def test_multimodal_lab_page(self):
        resp = self.client.get(reverse('playground:multimodal_lab_default'))
        self.assertEqual(resp.status_code, 200)


class LLMApiMockTest(TestCase):
    """测试 LLM API 接口（使用 mock 避免真实调用）"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        LLMConfig.objects.create(
            pk=1,
            provider='ollama',
            api_base='http://127.0.0.1:11434/v1/chat/completions',
            api_key='test-key',
            default_model='qwen2.5',
            enabled=True,
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    @patch('playground.views._common.req_lib.post')
    def test_jailbreak_test_api(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'choices': [{'message': {'content': 'I am a safe AI.'}}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        resp = self.client.post(
            reverse('playground:jailbreak_test_api'),
            data='{"payload": "hello"}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertIn('response', data)

    @patch('playground.views._common.req_lib.post')
    def test_system_prompt_leak_api(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'choices': [{'message': {'content': 'Hello! How can I help?'}}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        resp = self.client.post(
            reverse('playground:system_prompt_leak_api'),
            data='{"message": "hello", "history": []}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    @patch('playground.views._common.req_lib.post')
    def test_hallucination_chat_api(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'choices': [{'message': {'content': 'This is a test response.'}}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        resp = self.client.post(
            reverse('playground:hallucination_chat_api'),
            data='{"message": "tell me about fake history", "history": []}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_api_without_config(self):
        """未配置 LLM 时 API 应该返回错误而非 500"""
        LLMConfig.objects.all().delete()
        resp = self.client.post(
            reverse('playground:jailbreak_test_api'),
            data='{"payload": "test"}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)


class CsrfProtectionTest(TestCase):
    """验证 API 接口的 CSRF 保护"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_api_rejects_without_csrf(self):
        """不带 CSRF token 的 POST 应被拒绝"""
        client = Client(enforce_csrf_checks=True)
        client.login(username='testuser', password='testpass123')
        resp = client.post(
            reverse('playground:jailbreak_test_api'),
            data='{"payload": "test"}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)
