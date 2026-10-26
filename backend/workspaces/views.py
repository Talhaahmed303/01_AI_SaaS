from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Workspace, WorkspaceMembership
from .serializers import WorkspaceSerializer, WorkspaceCreateSerializer, WorkspaceMembershipSerializer, AddMemberSerializer
from .permissions import IsWorkspaceAdminOrOwner

User = get_user_model()

class WorkspaceListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkspaceCreateSerializer
        return WorkspaceSerializer

    def get_queryset(self):
        # Multi-tenant isolation: Only return workspaces where user is an active member
        return Workspace.objects.filter(memberships__user=self.request.user, is_active=True).distinct()

class WorkspaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(memberships__user=self.request.user)

    def perform_destroy(self, instance):
        # Only OWNER can delete workspace
        if instance.owner != self.request.user:
            return Response({'error': 'Only the workspace owner can delete this workspace.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()

class WorkspaceMembersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        workspace = get_object_or_404(Workspace, id=pk, memberships__user=request.user)
        memberships = workspace.memberships.select_related('user').all()
        serializer = WorkspaceMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        workspace = get_object_or_404(Workspace, id=pk)
        
        # Verify current user is Admin or Owner
        caller_membership = workspace.memberships.filter(user=request.user).first()
        if not caller_membership or caller_membership.role not in [WorkspaceMembership.RoleChoices.OWNER, WorkspaceMembership.RoleChoices.ADMIN]:
            return Response({'error': 'Only workspace Owners or Admins can invite new members.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        target_user = User.objects.get(email=serializer.validated_data['email'])
        role = serializer.validated_data['role']

        membership, created = WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=target_user,
            defaults={'role': role}
        )
        if not created:
            membership.role = role
            membership.save()

        return Response({
            'status': 'success',
            'message': f"User {target_user.email} added with role {role}",
            'membership': WorkspaceMembershipSerializer(membership).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class WorkspaceRemoveMemberView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, pk, user_id):
        workspace = get_object_or_404(Workspace, id=pk)
        caller_membership = workspace.memberships.filter(user=request.user).first()
        if not caller_membership or caller_membership.role not in [WorkspaceMembership.RoleChoices.OWNER, WorkspaceMembership.RoleChoices.ADMIN]:
            return Response({'error': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        if str(workspace.owner.id) == str(user_id):
            return Response({'error': 'Cannot remove workspace owner.'}, status=status.HTTP_400_BAD_REQUEST)

        membership = get_object_or_404(WorkspaceMembership, workspace=workspace, user_id=user_id)
        membership.delete()
        return Response({'status': 'success', 'message': 'Member removed.'}, status=status.HTTP_200_OK)
