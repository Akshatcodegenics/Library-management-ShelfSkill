from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    USER = 'USER', 'User'
    ADMIN = 'ADMIN', 'Admin'
    MEMBER = 'MEMBER', 'Member'
    AUTHOR = 'AUTHOR', 'Author'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER
    )
    name = models.CharField(max_length=255, blank=True)

    REQUIRED_FIELDS = ['email', 'role']

    def save(self, *args, **kwargs):
        if not self.name and (self.first_name or self.last_name):
            self.name = f"{self.first_name} {self.last_name}".strip()
        elif not self.name:
            self.name = self.username
        super().save(*args, **kwargs)

    @property
    def is_admin_user(self) -> bool:
        return self.role == UserRole.ADMIN or self.is_staff or self.is_superuser

    @property
    def is_author(self) -> bool:
        return self.role == UserRole.AUTHOR

    @property
    def is_normal_user(self) -> bool:
        return not self.is_admin_user

    def __str__(self):
        return f"{self.username} ({self.role})"
