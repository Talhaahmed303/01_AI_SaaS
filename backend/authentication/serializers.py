from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from workspaces.models import Workspace, WorkspaceMembership
from usage.models import UserQuota

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name', 'password', 'password_confirm', 'tier', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # 1. Auto-provision default Personal Workspace
        workspace = Workspace.objects.create(
            name=f"{user.username.capitalize()}'s Workspace",
            description=f"Primary default workspace for {user.email}",
            owner=user
        )
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=user,
            role=WorkspaceMembership.RoleChoices.OWNER
        )

        # 2. Auto-provision User Quota
        UserQuota.objects.create(
            user=user,
            tier=user.tier,
            daily_query_limit=30 if user.tier == 'FREE' else 500,
            daily_token_limit=50000 if user.tier == 'FREE' else 500000
        )

        return user

class UserSerializer(serializers.ModelSerializer):
    workspaces = serializers.SerializerMethodField()
    quota_summary = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name', 'tier', 'avatar_url', 'workspaces', 'quota_summary', 'created_at')

    def get_workspaces(self, obj):
        memberships = obj.workspace_memberships.select_related('workspace')
        return [
            {
                'id': str(m.workspace.id),
                'name': m.workspace.name,
                'slug': m.workspace.slug,
                'role': m.role,
                'is_owner': m.workspace.owner_id == obj.id
            }
            for m in memberships
        ]

    def get_quota_summary(self, obj):
        if hasattr(obj, 'quota'):
            return {
                'tier': obj.quota.tier,
                'daily_query_limit': obj.quota.daily_query_limit,
                'daily_token_limit': obj.quota.daily_token_limit,
                'rate_limit_per_minute': obj.quota.rate_limit_per_minute,
            }
        return None

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
