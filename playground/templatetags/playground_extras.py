from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """从字典中获取指定 key 的值"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter(name='make_range')
def make_range(value):
    """生成 range 对象用于模板循环"""
    return range(value)
