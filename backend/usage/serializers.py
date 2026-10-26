from rest_framework import serializers
from .models import UserQuota, DailyUsage, RequestLog

class UserQuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuota
        fields = ('tier', 'daily_query_limit', 'daily_token_limit', 'max_upload_size_mb', 'max_documents', 'rate_limit_per_minute')

class DailyUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyUsage
        fields = ('date', 'queries_used', 'tokens_used', 'documents_uploaded', 'last_request_at')

class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = ('id', 'endpoint', 'method', 'status_code', 'ip_address', 'latency_ms', 'tokens_consumed', 'error_details', 'created_at')
