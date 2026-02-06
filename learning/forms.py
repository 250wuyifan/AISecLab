from django import forms
from .models import Topic
from .models import Category

class TopicForm(forms.ModelForm):
    markdown_file = forms.FileField(
        label="导入 Markdown/Typora 文件",
        required=False,
        help_text="上传 .md 文件，内容将覆盖下方编辑框的内容。"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 允许“只上传 md 文件而不手填 content”，最终 content 会在 view 里用文件内容覆盖
        self.fields["content"].required = False
        # 作者姓名可自填
        self.fields["author_name"].required = False

    def clean(self):
        cleaned = super().clean()
        content = (cleaned.get("content") or "").strip()
        md = cleaned.get("markdown_file")

        # 允许两种方式之一：
        # - 直接填写 content
        # - 上传 markdown_file（内容由 view 读取覆盖）
        if not content and not md:
            self.add_error("content", "请填写内容，或上传一个 Markdown 文件。")

        return cleaned

    class Meta:
        model = Topic
        fields = ['title', 'category', 'level', 'author_name', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '可自填作者姓名，不填则用当前登录用户'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '分类名称'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '描述（可选）'}),
        }
