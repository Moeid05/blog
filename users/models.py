from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name="user_groups",
        related_query_name="user",
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="user_permissions",
        related_query_name="user",
        blank=True
    )

    objects = CustomUserManager()