from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "知识分类"
        verbose_name_plural = verbose_name

class Topic(models.Model):
    LEVEL_CHOICES = [
        (1, '入门'),
        (2, '进阶'),
        (3, '高阶'),
        (4, '专家'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics', verbose_name="所属分类")
    title = models.CharField(max_length=200, verbose_name="标题")
    level = models.IntegerField(choices=LEVEL_CHOICES, default=1, verbose_name="难度等级")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="作者")
    author_name = models.CharField(max_length=100, blank=True, verbose_name="作者姓名（可自填）")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "知识点"
        verbose_name_plural = verbose_name
