from rest_framework import permissions
from .models import WorkspaceMembership

class IsWorkspaceMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        workspace = getattr(obj, 'workspace', obj)
        return WorkspaceMembership.objects.filter(workspace=workspace, user=request.user).exists()

class IsWorkspaceAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        workspace = getattr(obj, 'workspace', obj)
        return WorkspaceMembership.objects.filter(
            workspace=workspace,
            user=request.user,
            role__in=[WorkspaceMembership.RoleChoices.OWNER, WorkspaceMembership.RoleChoices.ADMIN]
        ).exists()
