import uuid
from django.db import models
from django.conf import settings
from workspaces.models import Workspace

class Document(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending Ingestion'
        PROCESSING = 'PROCESSING', 'Processing & Chunking'
        INDEXED = 'INDEXED', 'Indexed & Ready'
        FAILED = 'FAILED', 'Ingestion Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    file = models.FileField(upload_to='documents/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50) # 'pdf', 'docx', 'txt', 'md'
    file_size = models.BigIntegerField(help_text='File size in bytes')
    file_hash = models.CharField(max_length=64, db_index=True, help_text='SHA-256 checksum for integrity & deduplication')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING, db_index=True)
    error_message = models.TextField(blank=True, null=True)
    chunk_count = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    summary = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['workspace', 'file_hash']),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.status}) in {self.workspace.name}"

class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    content = models.TextField()
    page_number = models.IntegerField(null=True, blank=True)
    token_count = models.IntegerField(default=0)
    embedding = models.JSONField(null=True, blank=True) # Normalized vector float array
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_chunks'
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]

    def __str__(self):
        return f"Chunk #{self.chunk_index} for Doc {self.document.file_name}"
