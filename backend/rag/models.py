import uuid
from django.db import models
from django.conf import settings
from workspaces.models import Workspace
from documents.models import DocumentChunk

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='chat_sessions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default='New Discussion')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.workspace.name})"

class ChatMessage(models.Model):
    class SenderChoices(models.TextChoices):
        USER = 'USER', 'User'
        ASSISTANT = 'ASSISTANT', 'AI Assistant'
        SYSTEM = 'SYSTEM', 'System'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SenderChoices.choices)
    content = models.TextField()
    model_used = models.CharField(max_length=80, default='gpt-4o-mini')
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)
    is_fallback = models.BooleanField(default=False, help_text='True if answer was ungrounded/unsupported or generated via fallback')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.sender}] {self.content[:40]}..."

class MessageCitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='citations')
    chunk = models.ForeignKey(DocumentChunk, on_delete=models.SET_NULL, null=True, blank=True, related_name='citations')
    document_title = models.CharField(max_length=255)
    page_number = models.IntegerField(null=True, blank=True)
    relevance_score = models.FloatField(help_text='Cosine similarity / semantic match score (0.0 to 1.0)')
    cited_text = models.TextField()

    class Meta:
        db_table = 'message_citations'
        ordering = ['-relevance_score']

    def __str__(self):
        return f"Citation from {self.document_title} (score: {self.relevance_score:.2f})"
