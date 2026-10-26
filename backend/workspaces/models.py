import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, db_index=True)
    description = models.TextField(blank=True, default='')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_workspaces')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workspaces'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'workspace'
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.slug})"

class WorkspaceMembership(models.Model):
    class RoleChoices(models.TextChoices):
        OWNER = 'OWNER', 'Workspace Owner'
        ADMIN = 'ADMIN', 'Workspace Admin'
        MEMBER = 'MEMBER', 'Standard Member'
        VIEWER = 'VIEWER', 'Read-Only Viewer'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workspace_memberships'
        constraints = [
            models.UniqueConstraint(fields=['workspace', 'user'], name='unique_workspace_user_membership')
        ]
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.email} -> {self.workspace.name} as {self.role}"
