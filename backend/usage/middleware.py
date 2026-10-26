import time
import json
import logging
from django.utils import timezone
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)

class RequestLoggingAndRateLimitMiddleware:
    """
    Production-grade middleware providing:
    1. Sliding window IP/User rate limiting (HTTP 429 prevention of abusive requests)
    2. Comprehensive request auditing: latency, status codes, endpoints, and error tracking
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # In-memory sliding window fallback if redis/cache not configured
        self._memory_cache = {}

    def __call__(self, request):
        start_time = time.time()
        
        # Determine client identifier
        client_ip = self.get_client_ip(request)
        user_id = str(request.user.id) if request.user.is_authenticated else None
        rate_key = f"rl:{user_id or client_ip}"

        # Sliding window rate check (max 60 requests per minute by default for general endpoints)
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            now = time.time()
            timestamps = self._memory_cache.get(rate_key, [])
            # Keep only timestamps in the last 60 seconds
            timestamps = [t for t in timestamps if now - t < 60]
            
            # Rate limit check (e.g. 60 requests / minute)
            if len(timestamps) >= 60:
                return JsonResponse({
                    'status': 'error',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded: maximum 60 requests per minute allowed.',
                    'retry_after_seconds': int(60 - (now - timestamps[0]))
                }, status=429, headers={'Retry-After': '60'})

            timestamps.append(now)
            self._memory_cache[rate_key] = timestamps

        # Process the request
        response = self.get_response(request)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Asynchronously log or safely persist audit record for API requests
        if request.path.startswith('/api/'):
            self.record_log(request, response, latency_ms, client_ip)

        # Inject security and latency headers
        response['X-Response-Time-Ms'] = str(latency_ms)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '127.0.0.1')

    def record_log(self, request, response, latency_ms, client_ip):
        try:
            from usage.models import RequestLog
            workspace_id = request.headers.get('X-Workspace-ID') or request.GET.get('workspace_id')
            
            # Only record if database is ready
            RequestLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                endpoint=request.path[:250],
                method=request.method,
                status_code=response.status_code,
                ip_address=client_ip,
                latency_ms=latency_ms,
                tokens_consumed=getattr(request, 'tokens_consumed', 0),
                error_details=getattr(request, 'error_details', None)
            )
        except Exception as e:
            # Avoid breaking request lifecycle if log write fails
            logger.debug(f"Audit log write skipped: {str(e)}")
