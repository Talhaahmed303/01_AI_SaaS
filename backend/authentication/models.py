import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is mandatory')
        if not username:
            raise ValueError('Username is mandatory')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('tier', 'ENTERPRISE')
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    class TierChoices(models.TextChoices):
        FREE = 'FREE', 'Free Tier'
        PRO = 'PRO', 'Pro Tier'
        ENTERPRISE = 'ENTERPRISE', 'Enterprise Tier'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255, blank=True)
    tier = models.CharField(max_length=20, choices=TierChoices.choices, default=TierChoices.FREE)
    avatar_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.tier})"
