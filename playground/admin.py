from django.contrib import admin

from .models import Challenge, Attempt, LLMConfig, AgentMemory, RAGDocument, LabCaseMeta


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "difficulty", "points", "created_at")
    search_fields = ("title",)
    list_filter = ("difficulty",)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "challenge", "is_correct", "timestamp")
    list_filter = ("is_correct", "timestamp")
    search_fields = ("user__username", "challenge__title")


@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "provider", "default_model", "enabled", "updated_at")
    list_filter = ("provider", "enabled")


@admin.register(AgentMemory)
class AgentMemoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "scenario", "updated_at")
    list_filter = ("scenario", "updated_at")
    search_fields = ("user__username", "scenario")


@admin.register(RAGDocument)
class RAGDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "source", "is_poisoned", "created_at")
    list_filter = ("source", "is_poisoned")
    search_fields = ("title", "content")


@admin.register(LabCaseMeta)
class LabCaseMetaAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "updated_at")
    search_fields = ("slug", "title")
