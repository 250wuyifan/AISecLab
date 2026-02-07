from django.db import models
from django.contrib.auth.models import User


class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]

    title = models.CharField(max_length=200, verbose_name="题目名称")
    description = models.TextField(verbose_name="题目描述")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy', verbose_name="难度")
    flag = models.CharField(max_length=100, verbose_name="Flag")
    points = models.IntegerField(default=10, verbose_name="积分")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "靶场题目"
        verbose_name_plural = verbose_name


class Attempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, verbose_name="题目")
    submitted_flag = models.CharField(max_length=100, verbose_name="提交的Flag")
    is_correct = models.BooleanField(default=False, verbose_name="是否正确")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.challenge.title}"

    class Meta:
        verbose_name = "解题记录"
        verbose_name_plural = verbose_name


class LLMConfig(models.Model):
    """
    全局大模型配置（当前版本先做成全局一份，后续需要可以扩展为按用户配置）。
    """

    PROVIDER_CHOICES = [
        ("openai", "OpenAI / 兼容 API"),
        ("ollama", "Ollama（本地）"),
        ("siliconflow", "硅基流动"),
        ("deepseek", "DeepSeek"),
        ("other", "其他"),
    ]

    provider = models.CharField(
        max_length=32,
        choices=PROVIDER_CHOICES,
        default="ollama",
        verbose_name="服务提供方",
    )
    api_base = models.URLField(
        max_length=255,
        default="http://127.0.0.1:11434/v1/chat/completions",
        verbose_name="API 地址",
    )
    api_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="API Key（仅存本地，勿提交到代码仓库）",
    )
    default_model = models.CharField(
        max_length=128,
        default="qwen2.5:32b",
        verbose_name="默认模型",
    )
    extra_headers = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="额外 HTTP Header（可选，高级配置）",
    )
    enabled = models.BooleanField(default=True, verbose_name="启用")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "大模型配置"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.get_provider_display()} - {self.default_model}"


class AgentMemory(models.Model):
    """
    记忆投毒靶场使用的 Agent 记忆。

    为了方便演示，这里按 user + scenario 存一条 JSON，
    JSON 里是若干条记忆对象：
      {"type": "user_memory" / "conversation" / "poison", "content": "..."}
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    scenario = models.CharField(max_length=64, default="memory_poisoning", verbose_name="场景标识")
    data = models.JSONField(default=list, verbose_name="记忆内容（JSON 数组）")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "scenario")
        verbose_name = "Agent 记忆"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.user.username} - {self.scenario}"


class RAGDocument(models.Model):
    """
    向量库 / RAG 知识库中的文档，用于演示“向量库记忆投毒”。

    为了简化演示，这里不接真实向量数据库，而是将内容存入关系型数据库，
    在视图中用简单的关键字重叠度来模拟“相似度检索”。
    """

    SOURCE_CHOICES = [
        ("internal", "内部文档"),
        ("external", "外部来源"),
        ("user_upload", "用户上传"),
    ]

    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容（作为 RAG 知识）")
    source = models.CharField(
        max_length=32, choices=SOURCE_CHOICES, default="internal", verbose_name="来源"
    )
    is_poisoned = models.BooleanField(default=False, verbose_name="是否疑似恶意/投毒文档")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "RAG 知识文档"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.title


class LabCaseMeta(models.Model):
    """
    靶场文案元数据：
    - slug 统一标识一个 case/变体，例如：
      - memory:dialog / memory:drift / ...
      - tool:basic / tool:chain / ...
      - rag:basic / rag:backdoor / ...
    - 允许在后台或页面上覆盖默认的标题/说明/真实世界示例。
    """

    slug = models.CharField(max_length=128, unique=True, verbose_name="靶场标识（slug）")
    title = models.CharField(max_length=200, blank=True, verbose_name="标题（可选覆盖）")
    subtitle = models.TextField(blank=True, verbose_name="靶场简介（可选覆盖）")
    scenario = models.TextField(blank=True, verbose_name="场景设定（可选覆盖）")
    real_world = models.TextField(blank=True, verbose_name="真实世界示例（可选覆盖）")
    # Hint 提示系统
    hint1 = models.TextField(blank=True, verbose_name="提示1（轻度提示）")
    hint2 = models.TextField(blank=True, verbose_name="提示2（中度提示）")
    hint3 = models.TextField(blank=True, verbose_name="提示3（答案提示）")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "靶场文案配置"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.slug


class LabProgress(models.Model):
    """
    用户靶场完成进度：记录用户完成了哪些靶场。
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    lab_slug = models.CharField(max_length=128, verbose_name="靶场标识")
    completed = models.BooleanField(default=False, verbose_name="是否完成")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    hints_used = models.IntegerField(default=0, verbose_name="使用的提示数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "lab_slug")
        verbose_name = "靶场进度"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"{self.user.username} - {self.lab_slug} [{status}]"


class LabFavorite(models.Model):
    """
    用户收藏的靶场。
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    lab_slug = models.CharField(max_length=128, verbose_name="靶场标识")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "lab_slug")
        verbose_name = "靶场收藏"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.user.username} ♥ {self.lab_slug}"
