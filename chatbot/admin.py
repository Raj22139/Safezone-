from django.contrib import admin
from .models import ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['role', 'content', 'source', 'timestamp']
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'page_context', 'started_at', 'updated_at']
    list_filter   = ['page_context']
    inlines       = [ChatMessageInline]
    readonly_fields = ['started_at', 'updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ['session', 'role', 'source', 'content', 'timestamp']
    list_filter   = ['role', 'source']
    readonly_fields = ['timestamp']
