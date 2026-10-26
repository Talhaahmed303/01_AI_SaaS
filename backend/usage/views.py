from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import UserQuota, DailyUsage, RequestLog
from .serializers import UserQuotaSerializer, DailyUsageSerializer, RequestLogSerializer
from documents.models import Document

class UsageSummaryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        quota, _ = UserQuota.objects.get_or_create(user=user)
        today = timezone.now().date()
        daily_usage, _ = DailyUsage.objects.get_or_create(user=user, date=today)

        # Calculate percentages
        query_percent = min(100.0, round((daily_usage.queries_used / max(1, quota.daily_query_limit)) * 100, 1))
        token_percent = min(100.0, round((daily_usage.tokens_used / max(1, quota.daily_token_limit)) * 100, 1))

        # Recent 7-day usage trend
        past_week = today - timedelta(days=6)
        history_records = DailyUsage.objects.filter(user=user, date__gte=past_week).order_by('date')
        history_map = {r.date.isoformat(): r for r in history_records}

        daily_trend = []
        for i in range(7):
            d = (past_week + timedelta(days=i)).isoformat()
            rec = history_map.get(d)
            daily_trend.append({
                'date': d,
                'queries': rec.queries_used if rec else 0,
                'tokens': rec.tokens_used if rec else 0
            })

        total_docs = Document.objects.filter(uploaded_by=user).count()

        return Response({
            'tier': quota.tier,
            'quota': UserQuotaSerializer(quota).data,
            'today': {
                'date': today.isoformat(),
                'queries_used': daily_usage.queries_used,
                'queries_limit': quota.daily_query_limit,
                'queries_percent': query_percent,
                'queries_remaining': max(0, quota.daily_query_limit - daily_usage.queries_used),
                'tokens_used': daily_usage.tokens_used,
                'tokens_limit': quota.daily_token_limit,
                'tokens_percent': token_percent,
                'tokens_remaining': max(0, quota.daily_token_limit - daily_usage.tokens_used),
                'documents_uploaded_today': daily_usage.documents_uploaded,
                'total_documents': total_docs
            },
            'reset_time': '00:00:00 UTC',
            'daily_trend': daily_trend
        })

class RequestHistoryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        logs = RequestLog.objects.filter(user=request.user).order_by('-created_at')[:50]
        serializer = RequestLogSerializer(logs, many=True)
        return Response({
            'count': len(logs),
            'results': serializer.data
        })

class SimulateQuotaExhaustionView(APIView):
    """Developer test endpoint to toggle or simulate quota exhaustion for QA test cases."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        today = timezone.now().date()
        daily_usage, _ = DailyUsage.objects.get_or_create(user=request.user, date=today)
        quota, _ = UserQuota.objects.get_or_create(user=request.user)

        action = request.data.get('action', 'exhaust')
        if action == 'exhaust':
            daily_usage.queries_used = quota.daily_query_limit
            daily_usage.tokens_used = quota.daily_token_limit
            daily_usage.save()
            msg = "Daily quota marked as EXHAUSTED for testing."
        else:
            daily_usage.queries_used = 0
            daily_usage.tokens_used = 0
            daily_usage.save()
            msg = "Daily quota RESET to zero."

        return Response({
            'status': 'success',
            'message': msg,
            'queries_used': daily_usage.queries_used,
            'limit': quota.daily_query_limit
        })
