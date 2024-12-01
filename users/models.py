from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from .managers import CustomUserManager


class CustomUser (AbstractUser ):
    total_vote = models.IntegerField(default=0)
    followers = models.ManyToManyField(
        'self', 
        symmetrical=False,
        related_name='following',
    )

    # voted_postes = models.ManyToManyField(blog)
    # posted_bloges = models.ManyToManyField(blog)

    def __str__(self):
        return self.username
    
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