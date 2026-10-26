from django.urls import path
from .views import UsageSummaryView, RequestHistoryView, SimulateQuotaExhaustionView

urlpatterns = [
    path('summary/', UsageSummaryView.as_view(), name='usage_summary'),
    path('history/', RequestHistoryView.as_view(), name='usage_request_history'),
    path('simulate-quota/', SimulateQuotaExhaustionView.as_view(), name='usage_simulate_quota'),
]
