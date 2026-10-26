from django.urls import path
from .views import WorkspaceListCreateView, WorkspaceDetailView, WorkspaceMembersView, WorkspaceRemoveMemberView

urlpatterns = [
    path('', WorkspaceListCreateView.as_view(), name='workspace_list_create'),
    path('<uuid:pk>/', WorkspaceDetailView.as_view(), name='workspace_detail'),
    path('<uuid:pk>/members/', WorkspaceMembersView.as_view(), name='workspace_members'),
    path('<uuid:pk>/members/<uuid:user_id>/', WorkspaceRemoveMemberView.as_view(), name='workspace_remove_member'),
]
