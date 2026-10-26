import uuid
from django.db import models
from django.conf import settings
from workspaces.models import Workspace

class UserQuota(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quota')
    tier = models.CharField(max_length=20, default='FREE')
    daily_query_limit = models.IntegerField(default=30)
    daily_token_limit = models.IntegerField(default=50000)
    max_upload_size_mb = models.IntegerField(default=10)
    max_documents = models.IntegerField(default=15)
    rate_limit_per_minute = models.IntegerField(default=20)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_quotas'

    def __str__(self):
        return f"Quota for {self.user.email}: {self.daily_query_limit} queries/day"

class DailyUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_usages')
    date = models.DateField(db_index=True)
    queries_used = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    documents_uploaded = models.IntegerField(default=0)
    last_request_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_usage_records'
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_user_daily_usage')
        ]
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.user.email} [{self.date}]: {self.queries_used} queries, {self.tokens_used} tokens"

class RequestLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='request_logs')
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True, blank=True, related_name='request_logs')
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latency_ms = models.IntegerField(default=0)
    tokens_consumed = models.IntegerField(default=0)
    error_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_request_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.latency_ms}ms)"
