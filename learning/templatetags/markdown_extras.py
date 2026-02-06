import re
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def _preprocess_markdown(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"(?<!<)(https?://[^\s>]+)", r"<\1>", text)


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(
        markdown.markdown(
            _preprocess_markdown(text),
            extensions=['fenced_code', 'codehilite', 'tables', 'sane_lists', 'smarty'],
        )
    )


@register.filter(name='get_item')
def get_item(dictionary, key):
    """从字典中获取指定 key 的值"""
    if dictionary is None:
        return None
    return dictionary.get(key)
