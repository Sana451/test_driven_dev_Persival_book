from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from accounts.models import Token

User = get_user_model()


class PasswordlessAuthenticationBackend(BaseBackend):
    """Серверный процессор беспарольной аутентификации."""

    def authenticate(self, request, uid):
        """Авторизовать."""
        try:
            token = Token.objects.get(uid=uid)
            return User.objects.get(email=token.email)
        except User.DoesNotExist:
            return User.objects.create(email=token.email)
        except Token.DoesNotExist:
            return None

    def get_user(self, email):
        """Получить пользователя."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
