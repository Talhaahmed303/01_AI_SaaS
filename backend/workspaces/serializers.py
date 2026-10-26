from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Workspace, WorkspaceMembership

User = get_user_model()

class WorkspaceMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = WorkspaceMembership
        fields = ('id', 'user', 'user_email', 'user_name', 'role', 'joined_at')
        read_only_fields = ('id', 'joined_at')

class WorkspaceSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    members_count = serializers.IntegerField(source='memberships.count', read_only=True)
    documents_count = serializers.IntegerField(source='documents.count', read_only=True)
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ('id', 'name', 'slug', 'description', 'owner', 'owner_email', 'is_active', 'members_count', 'documents_count', 'user_role', 'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'owner', 'created_at', 'updated_at')

    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.memberships.filter(user=request.user).first()
            return membership.role if membership else None
        return None

class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ('id', 'name', 'description')

    def create(self, validated_data):
        user = self.context['request'].user
        workspace = Workspace.objects.create(owner=user, **validated_data)
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=user,
            role=WorkspaceMembership.RoleChoices.OWNER
        )
        return workspace

class AddMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=WorkspaceMembership.RoleChoices.choices, default=WorkspaceMembership.RoleChoices.MEMBER)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value
