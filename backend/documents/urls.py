from django.urls import path
from .views import DocumentUploadView, DocumentListView, DocumentDetailDeleteView, DocumentChunksListView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('workspace/<uuid:workspace_id>/', DocumentListView.as_view(), name='document_list_workspace'),
    path('<uuid:pk>/', DocumentDetailDeleteView.as_view(), name='document_detail_delete'),
    path('<uuid:pk>/chunks/', DocumentChunksListView.as_view(), name='document_chunks'),
]
