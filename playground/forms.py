from django import forms
from .models import LLMConfig


class LLMConfigForm(forms.ModelForm):
    class Meta:
        model = LLMConfig
        fields = ["provider", "api_base", "api_key", "default_model", "enabled"]
        widgets = {
            "provider": forms.Select(attrs={
                "class": "form-select",
            }),
            "api_base": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "例如：http://127.0.0.1:11434/v1/chat/completions",
            }),
            "api_key": forms.TextInput(attrs={
                "class": "form-control font-monospace",
                "placeholder": "sk-xxxxxxxxxxxxxxxx",
                "autocomplete": "off",
                "spellcheck": "false",
                "style": "font-size: 0.85rem;",
            }),
            "default_model": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "例如：qwen2.5、gpt-4o-mini",
            }),
            "enabled": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }
        labels = {
            "provider": "服务提供方",
            "api_base": "API 地址",
            "api_key": "API Key",
            "default_model": "默认模型",
            "enabled": "启用",
        }
