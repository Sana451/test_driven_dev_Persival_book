import pytest
from django.contrib import auth
from django.test import Client

from accounts.models import Token

User = auth.get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Тест модели пользователя."""

    def test_user_is_valid_with_email_only(self):
        """Тест: пользователь допустим только с электронной почтой."""
        user = User(email="a@c.com")
        user.full_clean()  # не должно поднять исключение

    def test_email_is_primary_key(self):
        """Тест: адрес электронной почты является первичным ключом."""
        user = User(email="a@c.com")
        assert user.pk == "a@c.com"

    def test_no_problem_with_auth_login(self, client: Client):
        """Тест: проблем с auth_login нет."""
        user = User.objects.create(email="edith@example.com")
        user.backend = ""
        request = client.request().wsgi_request
        auth.login(request, user)  # не должно поднять исключение


@pytest.mark.django_db
class TestTokenModel:
    """Тест модели маркера."""

    def test_links_user_with_auto_generated_uid(self):
        """Тест: соединяет пользователя с авто генерированным uid."""
        token1 = Token.objects.create(email="a@c.com")
        token2 = Token.objects.create(email="a@c.com")
        assert token1.uid != token2.uid
