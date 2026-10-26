import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class ServiceFailureException(Exception):
    """Custom exception raised when upstream AI or external service experiences a failure."""
    def __init__(self, message="External AI provider service temporarily unavailable", details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class QuotaExceededException(Exception):
    """Custom exception raised when a user exceeds their daily usage quota."""
    def __init__(self, message="Daily usage quota exceeded. Upgrade your tier to continue.", details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

def custom_exception_handler(exc, context):
    """
    Standardized API Exception Handler across all AI SaaS endpoints.
    Ensures unified error structure, proper HTTP status codes, and security sanitization.
    """
    response = exception_handler(exc, context)

    if isinstance(exc, QuotaExceededException):
        return Response({
            'status': 'error',
            'code': 'QUOTA_EXCEEDED',
            'message': exc.message,
            'details': exc.details or {},
            'retry_after': 'Reset at 00:00 UTC'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS, headers={'Retry-After': '3600'})

    if isinstance(exc, ServiceFailureException):
        logger.error(f"Service Failure: {exc.message}", exc_info=True)
        return Response({
            'status': 'error',
            'code': 'SERVICE_FAILURE',
            'message': exc.message,
            'details': exc.details or {},
            'recommendation': 'Please retry your request shortly or switch to local deterministic fallback.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE, headers={'Retry-After': '30'})

    if response is not None:
        custom_data = {
            'status': 'error',
            'code': response.status_text.upper().replace(' ', '_') if hasattr(response, 'status_text') else 'API_ERROR',
            'status_code': response.status_code,
            'message': 'An error occurred processing your request',
            'details': response.data
        }

        # Humanize common DRF detail strings
        if isinstance(response.data, dict) and 'detail' in response.data:
            custom_data['message'] = str(response.data['detail'])

        response.data = custom_data
        return response

    # Unhandled unexpected exceptions (500)
    logger.critical(f"Unhandled Server Error: {str(exc)}", exc_info=True)
    return Response({
        'status': 'error',
        'code': 'INTERNAL_SERVER_ERROR',
        'status_code': 500,
        'message': 'An internal server error occurred. Our engineering team has been notified.',
        'details': str(exc) if context.get('request') and context['request'].user.is_staff else None
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
