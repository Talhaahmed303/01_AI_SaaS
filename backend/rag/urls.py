from django.urls import path
from .views import AskQuestionView, ChatSessionListCreateView, ChatSessionDetailView

urlpatterns = [
    path('ask/', AskQuestionView.as_view(), name='rag_ask_question'),
    path('sessions/', ChatSessionListCreateView.as_view(), name='rag_sessions_list_create'),
    path('sessions/<uuid:pk>/', ChatSessionDetailView.as_view(), name='rag_session_detail'),
]
