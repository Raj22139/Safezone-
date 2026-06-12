from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """A chatbot session per user (or anonymous)."""
    user        = models.ForeignKey(User, on_delete=models.CASCADE,
                                    null=True, blank=True, related_name='chat_sessions')
    session_key = models.CharField(max_length=64, blank=True, null=True)  # for anonymous
    started_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    page_context= models.CharField(max_length=20, default='public',
                                   choices=[('public','Public'),('dashboard','Dashboard'),('admin','Admin')])

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        who = self.user.username if self.user else f"anon({self.session_key[:8]})"
        return f"Session[{who}] @ {self.started_at:%Y-%m-%d %H:%M}"


class ChatMessage(models.Model):
    """Individual message in a chat session."""
    ROLE_CHOICES = [('user', 'User'), ('bot', 'Bot')]

    session   = models.ForeignKey(ChatSession, on_delete=models.CASCADE,
                                  related_name='messages')
    role      = models.CharField(max_length=5, choices=ROLE_CHOICES)
    content   = models.TextField()
    source    = models.CharField(max_length=10, default='rule',
                                 choices=[('rule','Rule-based'),('ai','AI'),('error','Error')])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"
