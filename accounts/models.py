import uuid

from django.contrib import auth
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)

# auth.signals.user_logged_in.disconnect(auth.models.update_last_login)


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
    uid = models.CharField(default=uuid.uuid4, max_length=40)


# class ListUser(AbstractBaseUser, PermissionsMixin):
#     """Пользователь списка."""
#     email = models.EmailField(primary_key=True)
#     USERNAME_FIELD = 'email'
# # REQUIRED_FIELDS = ['email', 'height']
# objects = ListUserManager()
#
# @property
# def is_staff(self):
#     return self.email == 'sana451@mail.ru'
#
# @property
# def is_active(self):
#     return True


class ListUser(models.Model):
    """Пользователь списка."""
    email = models.EmailField(primary_key=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    is_anonymous = False
    is_authenticated = True
