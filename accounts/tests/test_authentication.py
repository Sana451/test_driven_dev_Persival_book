import pytest
from django.contrib.auth import get_user_model

from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticate:
    """Тест аутентификации."""

    def test_returns_None_if_no_such_token(self, request):
        """Тест: возвращается None, если нет такого маркера."""
        result = PasswordlessAuthenticationBackend().authenticate(request, 'no-such-token')
        assert result is None

    def test_returns_new_user_with_correct_email_if_token_exists(self, request):
        """Тест: возвращается новый пользователь с правильной
        электронной почтой, если маркер существует."""
        email = "edith@example.com"
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(request, token.uid)
        new_user = User.objects.get(email=email)
        assert user == new_user

    def test_returns_existing_user_with_correct_email_if_token_exists(self, request):
        """Тест: возвращается существующий пользователь с правильной
        электронной почтой, если маркер существует."""
        email = "edith@example.com"
        existing_user = User.objects.create(email=email)
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(request, token.uid)
        assert user == existing_user


@pytest.mark.django_db
class TestGetUser:
    """Тест получения пользователя."""

    def test_gets_user_by_email(self):
        """Тест: получает пользователя по адресу электронной почты."""
        User.objects.create(email="another@example.com")
        desired_user = User.objects.create(email="edith@example.com")
        found_user = PasswordlessAuthenticationBackend().get_user("edith@example.com")
        assert found_user == desired_user

    def test_returns_None_if_no_user_with_that_email(self):
        """Тест: возвращается None, если нет пользователя с таким адресом электронной почты."""
        assert PasswordlessAuthenticationBackend().get_user("edith@example.com") is None
