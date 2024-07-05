from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class ListUserManager(BaseUserManager):
    """Менеджер пользователя списка."""

    def create_user(self, email):
        """Создать пользователя."""
        ListUser.objects.create(email=email)

    def create_superuser(self, email, password):
        """Создать суперпользователя."""
        self.create_user(email)


class Token(models.Model):
    """Маркер."""
    email = models.EmailField()
    uid = models.CharField(max_length=255)


class ListUser(AbstractBaseUser, PermissionsMixin):
    """Пользователь списка."""
    email = models.EmailField(primary_key=True)
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['email', 'height']
    objects = ListUserManager()

    @property
    def is_staff(self):
        return self.email == 'sana451@mail.ru'

    @property
    def is_active(self):
        return True
