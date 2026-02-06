from django import forms
from .models import LLMConfig


class LLMConfigForm(forms.ModelForm):
    class Meta:
        model = LLMConfig
        fields = ["provider", "api_base", "api_key", "default_model", "enabled"]
        widgets = {
            "api_key": forms.PasswordInput(render_value=True, attrs={"autocomplete": "off"}),
        }
        labels = {
            "provider": "服务提供方",
            "api_base": "API 地址",
            "api_key": "API Key（仅保存在本机数据库）",
            "default_model": "默认模型名称",
            "enabled": "启用",
        }

